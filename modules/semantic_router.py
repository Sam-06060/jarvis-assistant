"""
semantic_router.py — Lightweight Semantic Vector Router for Jarvis Playbook Vault

Architecture:
  - Indexes 1,618 expert playbook summaries using fastembed (BAAI/bge-small-en-v1.5)
  - Stores 384-dimensional vectors in a numpy matrix (~3.5 MB RAM)
  - Background thread initialization — Jarvis boots instantly, hot-swaps once ready
  - MD5-based cache invalidation to avoid redundant recomputation
  - Falls back to keyword search with a visible terminal warning when not ready

ONLY applies to the playbook vault. Built-in tools (37) use keyword scoring unchanged.
"""

import hashlib
import json
import logging
import os
import threading
import time
from typing import List, Optional, Tuple

import numpy as np

# --- WARP-SPEED IMPORTS ---
try:
    from fastembed import TextEmbedding
except ImportError:
    TextEmbedding = None

logger = logging.getLogger(__name__)

_CACHE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "data", "semantic_cache.npz"
)
_MODEL_NAME = "BAAI/bge-small-en-v1.5"


class SemanticRouter:
    """
    Singleton semantic router for the Jarvis playbook vault.

    Usage:
        router = SemanticRouter.instance()
        router.boot(registry_path)              # Call once at startup (non-blocking)

        results = router.search("SEO strategy") # Returns list of (playbook_id, score) tuples
        if results is None:                     # Not ready yet — use keyword fallback
            ...
    """
    _singleton: Optional["SemanticRouter"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._ready = False
        self._model = None
        self._matrix: Optional[np.ndarray] = None   # shape: (N, 384)
        self._ids: List[str] = []                    # playbook IDs, parallel to matrix rows
        self._registry_hash: str = ""
        self._init_thread: Optional[threading.Thread] = None

    @classmethod
    def instance(cls) -> "SemanticRouter":
        """Return the singleton instance, creating it if necessary."""
        if cls._singleton is None:
            with cls._lock:
                if cls._singleton is None:
                    cls._singleton = cls()
        return cls._singleton

    @property
    def ready(self) -> bool:
        return self._ready

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def boot(self, registry_path: str) -> None:
        """
        Non-blocking startup. Spins up a daemon thread that builds the vector index.
        Jarvis is responsive immediately on the keyword fallback.
        """
        if self._ready or (self._init_thread and self._init_thread.is_alive()):
            return  # Already booted or booting

        self._init_thread = threading.Thread(
            target=self._build_index,
            args=(registry_path,),
            daemon=True,
            name="SemanticRouter-Init"
        )
        self._init_thread.start()
        logger.info("🧠 [SemanticRouter] Background indexing started...")

    def search(self, query: str, top_k: int = 10, threshold: float = 0.65) -> Optional[List[Tuple[str, float]]]:
        """
        Search the playbook vault using cosine similarity.

        Returns:
            List of (playbook_id, score) sorted by score desc — or None if not ready.
        """
        if not self._ready:
            logger.warning("⚠️ [SemanticRouter] Not ready — falling back to keyword search")
            return None

        try:
            with np.errstate(all='ignore'):
                q_raw = self._embed([query])[0]                    # shape: (384,)
                # Normalize query vector (same as index normalization) + cast to float32 to prevent overflow
                q_raw = q_raw.astype(np.float32)
                q_norm = np.linalg.norm(q_raw)
                q_vec = q_raw / (q_norm if q_norm > 1e-9 else 1e-9)
                scores = self._matrix.astype(np.float32) @ q_vec    # shape: (N,) — cosine sim
                scores = np.nan_to_num(scores, nan=0.0, posinf=0.0, neginf=0.0)
            top_indices = np.argsort(scores)[::-1]              # descending order

            results = []
            for idx in top_indices[:top_k * 2]:                 # oversample then threshold
                score = float(scores[idx])
                if score < threshold:
                    break
                results.append((self._ids[idx], round(score, 4)))
                if len(results) >= top_k:
                    break

            return results if results else None

        except Exception as e:
            logger.error(f"❌ [SemanticRouter] Search failed: {e}")
            logger.warning("⚠️ [SemanticRouter] Search error — falling back to keyword search")
            return None

    # ──────────────────────────────────────────────────────────────────────────
    # Internal
    # ──────────────────────────────────────────────────────────────────────────

    def _build_index(self, registry_path: str) -> None:
        """Background worker: load model, build or restore cache, set ready flag."""
        t0 = time.time()
        try:
            # 1. Load registry
            with open(registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            playbooks = data.get("playbooks", {})
            if not playbooks:
                logger.error("❌ [SemanticRouter] No playbooks found in registry.")
                return

            # 2. Compute hash of registry content for cache invalidation
            current_hash = hashlib.md5(
                json.dumps(playbooks, sort_keys=True).encode()
            ).hexdigest()

            # 3. Try loading from cache
            cache_path = os.path.normpath(_CACHE_FILE)
            if self._try_load_cache(cache_path, current_hash):
                elapsed = time.time() - t0
                logger.info(f"✅ [SemanticRouter] Loaded from cache in {elapsed:.2f}s — {len(self._ids)} playbooks indexed.")
                self._ready = True
                return

            # 4. Cache miss — load model and embed
            logger.info(f"🧠 [SemanticRouter] Building new embedding index for {len(playbooks)} playbooks...")
            self._load_model()

            ids = list(playbooks.keys())
            texts = [
                f"{v.get('title', k)} — {v.get('summary', '')}"
                for k, v in playbooks.items()
            ]

            vectors = self._embed(texts)  # shape: (N, 384)

            # 5. L2-normalize for cosine similarity via dot product (always float32)
            vectors = vectors.astype(np.float32)
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1e-9, norms)           # prevent div-by-zero
            normalized = (vectors / norms).astype(np.float32)   # guarantee float32

            # 6. Save to cache
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            np.savez_compressed(cache_path, matrix=normalized, ids=np.array(ids), registry_hash=current_hash)
            logger.info(f"💾 [SemanticRouter] Cache saved to {cache_path}")

            # 7. Activate
            self._ids = ids
            self._matrix = normalized
            self._registry_hash = current_hash
            elapsed = time.time() - t0
            logger.info(f"✅ [SemanticRouter] Ready in {elapsed:.2f}s — {len(ids)} playbooks indexed.")
            self._ready = True

        except Exception as e:
            logger.error(f"❌ [SemanticRouter] Index build failed: {e}")
            logger.warning("⚠️ [SemanticRouter] Semantic routing unavailable — keyword fallback will be used.")

    def _try_load_cache(self, cache_path: str, current_hash: str) -> bool:
        """Attempt to restore index from disk cache. Returns True on success."""
        try:
            if not os.path.exists(cache_path):
                return False
            data = np.load(cache_path, allow_pickle=True)
            stored_hash = str(data["registry_hash"])
            if stored_hash != current_hash:
                logger.info("🔄 [SemanticRouter] Registry changed — rebuilding index.")
                return False
            self._matrix = data["matrix"]
            self._ids = list(data["ids"])
            self._registry_hash = current_hash
            return True
        except Exception as e:
            logger.warning(f"⚠️ [SemanticRouter] Cache load failed ({e}) — rebuilding.")
            return False

    def _load_model(self) -> None:
        """Lazy-load the fastembed model (downloads ~30MB ONNX file on first use)."""
        if self._model is not None:
            return
        if TextEmbedding is None:
            raise RuntimeError("FastEmbed library not found. Install it for semantic routing.")
        try:
            logger.info(f"📦 [SemanticRouter] Loading model: {_MODEL_NAME}")
            self._model = TextEmbedding(model_name=_MODEL_NAME)
            logger.info("✅ [SemanticRouter] Model loaded.")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize fastembed model: {e}")

    def _embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts. Returns numpy array."""
        self._load_model()
        embeddings = list(self._model.embed(texts))
        return np.array(embeddings, dtype=np.float32)
