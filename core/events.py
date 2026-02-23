from typing import Any, Callable, Dict, List
import threading
from .interfaces import IEventSubscriber

class EventManager:
    """
    Central Event Bus.
    Allows components to subscribe to events without knowing about the publisher.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EventManager, cls).__new__(cls)
                    cls._instance._subscribers: Dict[str, List[Callable]] = {}
        return cls._instance

    def subscribe(self, event_type: str, callback: Callable[[Any], None]):
        """Subscribe a callback function to an event type."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, payload: Any = None):
        """Publish an event to all subscribers."""
        # Copy list to avoid thread safety issues during iteration
        with self._lock:
            callbacks = self._subscribers.get(event_type, [])[:]
        
        for callback in callbacks:
            try:
                callback(payload)
            except Exception as e:
                print(f"❌ Event Handler Error ({event_type}): {e}")

# Global Accessor
events = EventManager()
