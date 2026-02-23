from typing import Any, Dict, Optional, Type
import threading
from .interfaces import IService

class ServiceRegistry:
    """
    Central Service Registry.
    Replaces "God Object" passing. Components ask for what they need.
    """
    _instance = None
    _services: Dict[str, Any] = {}
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ServiceRegistry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, name: str, service: Any):
        """Register a service implementation."""
        with cls._lock:
            cls._services[name] = service
            # print(f"✅ Service Registered: {name}")

    @classmethod
    def get(cls, name: str) -> Optional[Any]:
        """Get a service by name. Returns None if not found."""
        with cls._lock:
            return cls._services.get(name)

    @classmethod
    def list_services(cls) -> list[str]:
        with cls._lock:
            return list(cls._services.keys())

# Global Accessor
registry = ServiceRegistry()
