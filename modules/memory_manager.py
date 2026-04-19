"""
memory_manager.py — Unified 4-tier memory system for Jarvis.

Replaces the ad-hoc memory_vault + ConversationHistory patchwork with
a single, coherent interface across four memory scopes:

  Tier 1 — Step Output Cache  (task-scoped, in-memory)
            Stores raw tool outputs keyed by (task_id, step_id).
            Wiped when a new AgentCore.run() call begins.

  Tier 2 — Session Memory     (session-scoped, in-memory)
            Stores named facts with optional TTL.
            Wiped when Jarvis exits (or on explicit clear).

  Tier 3 — Conversation Window (disk-persisted, delegated to ConversationHistory)
            Provides get_context_window() for LLM system prompt injection.

  Tier 4 — Long-Term Knowledge (disk-persisted, survives restarts)
            User preferences, contact aliases, frequently used paths, etc.
            Written to data/knowledge.json.
"""

import os
import json
import time
import threading
import logging
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Unified memory interface for the Jarvis agent.

    Usage (from AgentCore):
        memory = registry.get("memory")
        memory.set_step_output(task_id, step_id=1, data="Django, Flask, FastAPI...")
        data = memory.get_step_output(task_id, step_id=1)
        memory.remember("last_contact", "John", ttl_seconds=3600)
        name = memory.recall("last_contact")
        memory.know("user_city", "Bengaluru")
        city = memory.lookup("user_city")
    """

    def __init__(
        self,
        history_component=None,
        knowledge_file: str = "data/knowledge.json",
    ):
        self._lock = threading.RLock()

        # Tier 1: {task_id: {step_id: str}}
        self._step_cache: Dict[str, Dict[int, str]] = {}

        # Tier 2: {key: {"value": Any, "timestamp": float, "ttl": Optional[float]}}
        self._session: Dict[str, Dict] = {}

        # Tier 3: Delegated to ConversationHistory
        self._history = history_component

        # Tier 4: Persistent key-value knowledge store
        self._knowledge_file = knowledge_file
        self._knowledge: Dict[str, Any] = self._load_knowledge()

        logger.info("🧠 MemoryManager initialised (4-tier).")

    # ─────────────────────────────────────────────────────────────────────────
    # TIER 1 — Step Output Cache
    # ─────────────────────────────────────────────────────────────────────────

    def set_step_output(self, task_id: str, step_id: int, data: str):
        """Store a tool's raw output, keyed by task + step."""
        with self._lock:
            if task_id not in self._step_cache:
                self._step_cache[task_id] = {}
            self._step_cache[task_id][step_id] = data
        logger.debug(f"🧠 [T1] set_step_output task={task_id} step={step_id} ({len(data)} chars)")

    def get_step_output(self, task_id: str, step_id: int) -> Optional[str]:
        """Retrieve a stored step output. Returns None if not found."""
        with self._lock:
            return self._step_cache.get(task_id, {}).get(step_id)

    def clear_task(self, task_id: str):
        """Discard all step outputs for a completed task (optional housekeeping)."""
        with self._lock:
            self._step_cache.pop(task_id, None)

    # ─────────────────────────────────────────────────────────────────────────
    # TIER 2 — Session Memory
    # ─────────────────────────────────────────────────────────────────────────

    def remember(self, key: str, value: Any, ttl_seconds: Optional[float] = None):
        """
        Store a named fact in session memory.

        Args:
            key:         Unique string key.
            value:       Any serialisable value.
            ttl_seconds: Optional time-to-live in seconds. None = no expiry.
        """
        with self._lock:
            self._session[key] = {
                "value": value,
                "timestamp": time.time(),
                "ttl": ttl_seconds,
            }
        logger.debug(f"🧠 [T2] remember: {key} = {str(value)[:60]}")

    def recall(self, key: str) -> Optional[Any]:
        """Retrieve a session memory value. Returns None if missing or expired."""
        self._evict_expired()
        with self._lock:
            entry = self._session.get(key)
            if entry is None:
                return None
            return entry["value"]

    def recall_all(self) -> Dict[str, Any]:
        """Return all non-expired session memory entries as a flat dict."""
        self._evict_expired()
        with self._lock:
            return {k: v["value"] for k, v in self._session.items()}

    def _evict_expired(self):
        """Remove TTL-expired session entries. Called on every recall."""
        now = time.time()
        with self._lock:
            expired = [
                k for k, v in self._session.items()
                if v["ttl"] is not None and now - v["timestamp"] > v["ttl"]
            ]
            for k in expired:
                del self._session[k]
                logger.debug(f"🧠 [T2] expired: {k}")

    def clear_session(self):
        """Wipe all session memory (call on Jarvis exit)."""
        with self._lock:
            self._session.clear()
        logger.info("🧠 [T2] Session memory cleared.")

    # ─────────────────────────────────────────────────────────────────────────
    # TIER 3 — Conversation History (delegated)
    # ─────────────────────────────────────────────────────────────────────────

    def get_context_window(self, limit: int = 5) -> str:
        """
        Returns the last N conversation exchanges formatted for LLM injection.
        Delegates to ConversationHistory if available, otherwise returns empty.
        """
        if self._history and hasattr(self._history, "get_context_window"):
            return self._history.get_context_window(limit=limit)
        return ""

    def log_exchange(self, user_text: str, ai_text: str, exchange_type: str = "general"):
        """Log a completed conversation exchange to persistent history."""
        if self._history and hasattr(self._history, "log_exchange"):
            self._history.log_exchange(user_text, ai_text, exchange_type)

    # ─────────────────────────────────────────────────────────────────────────
    # TIER 4 — Long-Term Knowledge
    # ─────────────────────────────────────────────────────────────────────────

    def know(self, key: str, value: Any):
        """
        Persist a fact to long-term knowledge (survives restarts).
        Example: memory.know("user_city", "Bengaluru")
        """
        with self._lock:
            self._knowledge[key] = {
                "value": value,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        self._save_knowledge()
        logger.info(f"🧠 [T4] know: {key} = {str(value)[:60]}")

    def lookup(self, key: str) -> Optional[Any]:
        """
        Retrieve a long-term knowledge value.
        Returns None if the key has never been stored.
        """
        with self._lock:
            entry = self._knowledge.get(key)
            return entry["value"] if entry else None

    def forget(self, key: str):
        """Remove a specific key from long-term knowledge."""
        with self._lock:
            self._knowledge.pop(key, None)
        self._save_knowledge()
        logger.info(f"🧠 [T4] forget: {key}")

    def knowledge_summary(self) -> str:
        """Return a compact readable summary of all known facts (for context injection)."""
        with self._lock:
            if not self._knowledge:
                return ""
            lines = [f"  {k}: {v['value']}" for k, v in self._knowledge.items()]
        return "Known facts (long-term memory):\n" + "\n".join(lines)

    def _load_knowledge(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self._knowledge_file):
                with open(self._knowledge_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"🧠 [T4] Loaded {len(data)} long-term knowledge entries.")
                    return data
        except Exception as e:
            logger.warning(f"⚠️ MemoryManager: could not load knowledge file: {e}")
        return {}

    def _save_knowledge(self):
        try:
            os.makedirs(os.path.dirname(self._knowledge_file), exist_ok=True)
            with self._lock:
                data_copy = dict(self._knowledge)
            with open(self._knowledge_file, "w", encoding="utf-8") as f:
                json.dump(data_copy, f, indent=2)
        except Exception as e:
            logger.error(f"❌ MemoryManager: could not save knowledge file: {e}")
