from core.registry import registry
from core.interfaces import IService
from typing import Any, Dict, Optional
import threading

class ContextService(IService):
    """
    Manages Shared Application State.
    Replaces ad-hoc passing of 'context_manager' and global variables.
    """
    def __init__(self):
        self._state: Dict[str, Any] = {
            "current_app": None,
            "last_command": None,
            "clipboard_content": None,
            "is_speaking": False,
            "user_presence": False
        }
        self._lock = threading.RLock()

    def get_name(self):
        return "context"

    def update(self, key: str, value: Any):
        """Update a context variable thread-safely."""
        with self._lock:
            self._state[key] = value
            # Future: trigger event 'context_changed'

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._state.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        with self._lock:
            return self._state.copy()

# Global Instance
context_service = ContextService()
registry.register("context_service", context_service)
