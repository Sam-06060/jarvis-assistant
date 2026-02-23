from core.registry import registry
from core.interfaces import IService
import threading
import time

class ServiceProxy(IService):
    """
    A smart proxy that sits in the registry while the real service loads in background.
    If accessed, it tells the user to wait.
    Once real service is ready, it swaps itself out.
    """
    def __init__(self, service_name, human_name, factory_func):
        self.name = service_name
        self.human_name = human_name
        self.factory = factory_func
        self.real_service = None
        self.is_loading = True
        self.load_thread = threading.Thread(target=self._background_load, daemon=True)
        self.load_thread.start()

    def get_name(self):
        return self.name

    def _background_load(self):
        # print(f"⏳ Background Load Started: {self.human_name}")
        try:
            instance = self.factory()
            self.real_service = instance
            self.is_loading = False
            
            # Hot Swap in Registry
            registry.register(self.name, instance)
            # print(f"✅ Background Load Complete: {self.human_name}")
            
        except Exception as e:
            print(f"❌ Failed to load {self.human_name}: {e}")
            self.is_loading = False # Stop loading state even if failed

    def __getattr__(self, name):
        """Intercept all calls to the service."""
        # If accessing the real_service attribute itself, return it (handled by object but just in case)
        if name == 'real_service':
            return self.__dict__.get('real_service')

        if self.real_service:
            return getattr(self.real_service, name)
        
        # If we are here, service is not ready
        def proxy_method(*args, **kwargs):
            try:
                # Late import to minimize top-level imports
                from core.registry import registry
                speech = registry.get("speech")
                if speech:
                    speech.speak(f"One moment sir, the {self.human_name} module is still loading.")
            except: pass
            return False # Fail gracefully
            
        return proxy_method
