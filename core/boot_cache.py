"""
core/boot_cache.py — Persistent boot state cache for Jarvis.

Implements the "Instant Boot" mechanism:
  - Cold boot: full init runs, state is serialized and saved.
  - Warm boot: cached state is loaded, heavy init is skipped.

Cache invalidation is fingerprint-based — any change to source files
or config triggers a full cold boot automatically.

Cache location: data/.boot_cache/
  - boot_state.pkl   : serialized warm-bootable state
  - metadata.json    : fingerprint, version, timestamps

Security: HMAC-SHA256 integrity check on the pickle file prevents
          tampered caches from being loaded.
"""

import os
import json
import time
import pickle
import hashlib
import hmac
import logging
import threading
from typing import Optional, Any

from core.fingerprint import (
    compute_fingerprint,
    compute_all_component_fingerprints,
)

logger = logging.getLogger(__name__)

# Cache format version — increment this to auto-invalidate all existing caches
# when the cache schema changes.
_CACHE_VERSION = "1.0"

# HMAC key — derived from a constant + the project path so it's machine-specific.
# Not a security secret; just prevents accidental cache corruption from being loaded.
_HMAC_SECRET = b"jarvis_boot_cache_integrity_v1"


class BootCacheManager:
    """
    Manages the Jarvis persistent boot cache.

    Usage:
        cache = BootCacheManager(project_root=config.BASE_DIR)

        if cache.is_warm_boot():
            state = cache.load()
            apply_warm_state(state)
        else:
            run_full_cold_boot()
            cache.save(state)
    """

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.cache_dir = os.path.join(project_root, "data", ".boot_cache")
        self._state_path = os.path.join(self.cache_dir, "boot_state.pkl")
        self._meta_path = os.path.join(self.cache_dir, "metadata.json")
        self._current_fingerprint: Optional[str] = None
        self._cached_metadata: Optional[dict] = None
        self._lock = threading.Lock()

        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def is_warm_boot(self) -> bool:
        """
        Returns True if a valid, up-to-date cache exists and the codebase
        has not changed since the cache was written.

        This is the main gate call — invoke at startup before any init.
        """
        try:
            meta = self._load_metadata()
            if not meta:
                logger.info("🧊 Cold boot: no cache metadata found.")
                return False

            if meta.get("version") != _CACHE_VERSION:
                logger.info(f"🧊 Cold boot: cache version mismatch ({meta.get('version')} vs {_CACHE_VERSION}).")
                self.invalidate()
                return False

            cached_fp = meta.get("fingerprint")
            current_fp = self._get_fingerprint()

            if cached_fp != current_fp:
                logger.info("🧊 Cold boot: codebase has changed since last cache.")
                self.invalidate()
                return False

            if not os.path.exists(self._state_path):
                logger.info("🧊 Cold boot: state file missing.")
                return False

            logger.info(f"🔥 Warm boot eligible — cache from {self._format_age(meta.get('saved_at', 0))} ago.")
            return True

        except Exception as e:
            logger.warning(f"⚠️ Boot cache check failed: {e} — falling back to cold boot.")
            return False

    def load(self) -> Optional[dict]:
        """
        Load and return the cached boot state dict.
        Returns None if cache is corrupt or HMAC check fails (triggers cold boot).
        """
        try:
            t0 = time.time()
            with open(self._state_path, "rb") as f:
                raw = f.read()

            # Verify integrity
            meta = self._load_metadata()
            expected_hmac = meta.get("hmac") if meta else None
            if not self._verify_hmac(raw, expected_hmac):
                logger.warning("⚠️ Boot cache HMAC mismatch — cache may be corrupt. Cold boot.")
                self.invalidate()
                return None

            state = pickle.loads(raw)
            elapsed_ms = int((time.time() - t0) * 1000)
            logger.info(f"✅ Boot cache loaded in {elapsed_ms}ms")
            return state

        except Exception as e:
            logger.warning(f"⚠️ Failed to load boot cache: {e} — cold boot.")
            self.invalidate()
            return None

    def get_stale_components(self) -> list[str]:
        """
        Returns a list of component names whose files changed since the cache was saved.
        Used to decide which parts of the warm boot state to skip/refresh.

        Example return values:
          []              — nothing changed, full warm boot
          ['skills']      — only skills changed, reload them; keep GroqClient/SemanticRouter
          ['core', ...]   — core changed, treat as cold boot
        """
        try:
            meta = self._load_metadata()
            if not meta:
                return ["core", "skills", "semantic"]  # No meta — everything is stale

            cached_components = meta.get("component_fingerprints", {})
            if not cached_components:
                return []  # Old cache format — don’t penalize, just skip component check

            current_components = compute_all_component_fingerprints(self.project_root)
            stale = [
                name for name, fp in current_components.items()
                if cached_components.get(name) != fp
            ]
            if stale:
                logger.info(f"🔍 Stale components detected: {stale}")
            return stale
        except Exception as e:
            logger.debug(f"Component staleness check failed: {e}")
            return []

    def save(self, state: dict) -> bool:
        """
        Serialize and save the boot state to disk.
        Called at the end of a successful cold boot.

        Runs in a background thread to avoid blocking the main loop.
        """
        def _save_worker():
            try:
                with self._lock:
                    t0 = time.time()

                    # Serialize
                    raw = pickle.dumps(state, protocol=pickle.HIGHEST_PROTOCOL)

                    # Compute HMAC
                    mac = self._compute_hmac(raw)

                    # Atomic write: write to tmp then rename
                    tmp_path = self._state_path + ".tmp"
                    with open(tmp_path, "wb") as f:
                        f.write(raw)
                    os.replace(tmp_path, self._state_path)

                    # Write metadata — include component fingerprints for targeted invalidation
                    component_fps = compute_all_component_fingerprints(self.project_root)
                    meta = {
                        "version": _CACHE_VERSION,
                        "fingerprint": self._get_fingerprint(),
                        "component_fingerprints": component_fps,
                        "saved_at": time.time(),
                        "hmac": mac,
                        "state_keys": list(state.keys()),
                    }
                    tmp_meta = self._meta_path + ".tmp"
                    with open(tmp_meta, "w") as f:
                        json.dump(meta, f, indent=2)
                    os.replace(tmp_meta, self._meta_path)

                    elapsed_ms = int((time.time() - t0) * 1000)
                    size_kb = len(raw) // 1024
                    logger.info(f"💾 Boot cache saved in {elapsed_ms}ms ({size_kb}KB) — keys: {list(state.keys())}")

            except Exception as e:
                logger.warning(f"⚠️ Failed to save boot cache: {e}")

        t = threading.Thread(target=_save_worker, daemon=True, name="BootCacheSave")
        t.start()
        return True

    def invalidate(self) -> None:
        """Delete the cache files, forcing a cold boot next launch."""
        for path in (self._state_path, self._meta_path):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
        logger.debug("🗑️ Boot cache invalidated.")

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_fingerprint(self) -> str:
        """Compute and cache the fingerprint for this session."""
        if self._current_fingerprint is None:
            self._current_fingerprint = compute_fingerprint(self.project_root)
        return self._current_fingerprint

    def _load_metadata(self) -> Optional[dict]:
        """Load and parse the JSON metadata file."""
        if self._cached_metadata is not None:
            return self._cached_metadata
        try:
            with open(self._meta_path, "r") as f:
                self._cached_metadata = json.load(f)
            return self._cached_metadata
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _compute_hmac(self, data: bytes) -> str:
        return hmac.new(_HMAC_SECRET, data, hashlib.sha256).hexdigest()

    def _verify_hmac(self, data: bytes, expected: Optional[str]) -> bool:
        if not expected:
            return False
        actual = self._compute_hmac(data)
        return hmac.compare_digest(actual, expected)

    @staticmethod
    def _format_age(saved_at: float) -> str:
        """Human-readable age string for the cache."""
        if not saved_at:
            return "unknown time"
        age_s = time.time() - saved_at
        if age_s < 60:
            return f"{int(age_s)}s"
        if age_s < 3600:
            return f"{int(age_s / 60)}m"
        return f"{int(age_s / 3600)}h"


# =========================================================================
# WARM-BOOTABLE STATE BUILDERS
# Each function returns a serializable sub-dict for one subsystem.
# Called at the END of a cold boot to snapshot the warm state.
# =========================================================================

def build_semantic_router_state() -> Optional[dict]:
    """Snapshot SemanticRouter — just mark that cache exists so warm boot skips rebuild."""
    try:
        from modules.semantic_router import SemanticRouter
        sr = SemanticRouter.instance()
        if sr and sr._ready:
            return {
                "type": "semantic_router",
                "cache_path": sr._cache_path,
                "index_size": len(sr._index) if sr._index else 0,
            }
    except Exception as e:
        logger.debug(f"SemanticRouter state snapshot skipped: {e}")
    return None


def build_groq_client_state() -> Optional[dict]:
    """Snapshot GroqClient singleton config — skip re-detection on warm boot."""
    try:
        from modules.groq_client import GroqClient
        gc = GroqClient()
        return {
            "type": "groq_client",
            "groq_available": gc.groq_available,
            "openrouter_available": gc.openrouter_available,
            "gemini_available": gc.gemini_available,
            "detected_provider": getattr(__import__("config"), "AGENTIC_LLM_PROVIDER", None),
            "detected_model": getattr(__import__("config"), "AGENTIC_LLM_MODEL", None),
        }
    except Exception as e:
        logger.debug(f"GroqClient state snapshot skipped: {e}")
    return None


def build_skill_registry_state() -> Optional[dict]:
    """Snapshot discovered skill + tool names so the filesystem scan is skipped."""
    try:
        from core.registry import ServiceRegistry
        cp = ServiceRegistry.get("commands")
        if cp and hasattr(cp, "command_phrases"):
            return {
                "type": "skill_registry",
                "command_phrases": list(cp.command_phrases) if cp.command_phrases else [],
                "skill_names": [s.__class__.__name__ for s in getattr(cp, "_skills", [])],
                "tool_count": len(getattr(cp, "tools", {})),
            }
    except Exception as e:
        logger.debug(f"SkillRegistry state snapshot skipped: {e}")
    return None


def capture_full_boot_state() -> dict:
    """
    Called once at the end of a successful cold boot.
    Snapshots all warm-bootable subsystem states into a single dict.
    """
    logger.info("📸 Capturing boot state for next launch cache...")
    state = {}

    sr_state = build_semantic_router_state()
    if sr_state:
        state["semantic_router"] = sr_state

    gc_state = build_groq_client_state()
    if gc_state:
        state["groq_client"] = gc_state

    sk_state = build_skill_registry_state()
    if sk_state:
        state["skill_registry"] = sk_state

    state["boot_timestamp"] = time.time()
    logger.info(f"📸 Boot state captured: {list(state.keys())}")
    return state


def apply_warm_boot_state(state: dict) -> None:
    """
    Apply cached subsystem states at the START of a warm boot.
    Each subsystem checks its own entry and skips heavy init if state exists.
    """
    logger.info(f"♻️  Applying warm boot state: {list(state.keys())}")

    # ── GroqClient: restore provider detection ────────────────────────────────
    gc_state = state.get("groq_client")
    if gc_state:
        try:
            import config
            if gc_state.get("detected_provider"):
                config.AGENTIC_LLM_PROVIDER = gc_state["detected_provider"]
            if gc_state.get("detected_model"):
                config.AGENTIC_LLM_MODEL = gc_state["detected_model"]
            logger.info(f"♻️  GroqClient: restored provider={config.AGENTIC_LLM_PROVIDER}")
        except Exception as e:
            logger.debug(f"GroqClient warm restore skipped: {e}")

    # ── SemanticRouter: signal that cache exists, skip rebuild ───────────────
    # (SemanticRouter._try_load_cache() will be called instead of _build_index)
    sr_state = state.get("semantic_router")
    if sr_state:
        try:
            import builtins
            # Set a module-level flag that SemanticRouter reads to skip rebuild
            builtins.__jarvis_semantic_cache_valid__ = True
            logger.info(f"♻️  SemanticRouter: skip rebuild ({sr_state.get('index_size', 0)} entries cached)")
        except Exception as e:
            logger.debug(f"SemanticRouter warm signal skipped: {e}")
