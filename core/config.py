import os
import importlib.util
from typing import Any, Dict, Optional
from core.registry import registry
from core.interfaces import IService
from dotenv import load_dotenv

class ConfigService(IService):
    """
    Central Configuration Service.
    Loads settings from 'config.py' and environment variables.
    Allows runtime updates and type-safe access.
    """
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self.load_dotenv()
        self.load_legacy_config()

    def get_name(self):
        return "config"

    def load_dotenv(self):
        load_dotenv()

    def load_legacy_config(self):
        """Loads variable from the root config.py file."""
        try:
            # Dynamic import of the config.py file
            spec = importlib.util.spec_from_file_location("legacy_config", "config.py")
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Copy uppercase variables to our internal dict
                for key, value in vars(module).items():
                    if key.isupper():
                        self._config[key] = value
                # print(f"✅ Loaded {len(self._config)} keys from legacy config.")
        except Exception as e:
            print(f"⚠️ Failed to load legacy config.py: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        # 1. Check Env Var first (highest priority for secrets)
        env_val = os.getenv(key)
        if env_val is not None:
            # Attempt type conversion if default is bool/int
            if isinstance(default, bool):
                return env_val.lower() in ('true', '1', 'yes')
            if isinstance(default, int):
                try: return int(env_val)
                except: pass
            return env_val
            
        # 2. Check Internal Config
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Runtime update of config."""
        self._config[key] = value
        # Optional: trigger event 'config_changed'

# Global Instance (for easy access in existing code if needed)
config_service = ConfigService()
registry.register("config", config_service)
