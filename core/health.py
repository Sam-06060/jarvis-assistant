from core.registry import registry
from core.interfaces import IService
import threading
import time

class HealthWatchdog(IService):
    """
    Monitors the health of critical systems.
    """
    def __init__(self):
        self._running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)

    def get_name(self):
        return "health_watchdog"

    def initialize(self):
        self.thread.start()
        return True

    def _monitor_loop(self):
        # Allow system to boot up
        time.sleep(10)
        
        while self._running:
            try:
                # Check all services
                for name, service in registry.get_all().items():
                    if name == "health": continue # Don't check self
                    
                    try:
                        is_alive = service.heartbeat()
                        if not is_alive:
                            print(f"⚠️ Service '{name}' failed heartbeat check!")
                            # Future: Trigger restart logic here if verified generic failure
                    except Exception as e:
                         print(f"⚠️ Error checking heartbeat for '{name}': {e}")
            except Exception: pass
            
            time.sleep(30) # Check every 30 seconds

    def shutdown(self):
        self._running = False

    def check_service(self, service_name: str) -> bool:
        """Manually check a service"""
        service = registry.get(service_name)
        if not service:
            return False
        # If service has a check_health method, call it
        if hasattr(service, 'check_health'):
            return service.check_health()
        return True

    def report_crash(self, service_name: str):
        """Called by components when they crash safely."""
        print(f"🚑 HealthWatchdog received crash report for: {service_name}")
        # Trigger Restart Strategy
        threading.Thread(target=self._attempt_recovery, args=(service_name,), daemon=True).start()

    def _attempt_recovery(self, service_name):
        """Try to restart the failed service via the App"""
        app = registry.get("app")
        if app and hasattr(app, 'restart_service'):
            print(f"🔄 Attempting to restart {service_name}...")
            try:
                success = app.restart_service(service_name)
                if success:
                    print(f"✅ Recovered {service_name} successfully!")
                else:
                    print(f"❌ Failed to recover {service_name}.")
            except Exception as e:
                print(f"❌ Recovery crashed: {e}")
