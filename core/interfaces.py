from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class IService(ABC):
    """Base interface for all Jarvis Services."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the unique name of the service."""
        pass

    def heartbeat(self) -> bool:
        """
        Optional: Check if service is still responsive.
        Default is True (assuming if method call succeeds, thread is alive).
        Override for complex logic (e.g., checking internal queues).
        """
        return True

    def initialize(self) -> bool:
        """Initialize the service. Returns True if successful."""
        return True

    def shutdown(self) -> None:
        """Cleanup resources before shutdown."""
        pass

class IEventSubscriber(ABC):
    """Interface for components that listen to events."""
    
    @abstractmethod
    def handle_event(self, event_type: str, payload: Any) -> None:
        """Handle an incoming event."""
        pass
