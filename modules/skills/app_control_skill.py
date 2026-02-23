from .base import Skill
import subprocess
import time

class AppControlSkill(Skill):
    def can_handle(self, command: str) -> bool:
        return "open" in command.lower()

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        
        # 1. SPECIAL CASES (Hardcoded in original router)
        if "facetime" in cmd or "camera" in cmd:
             self.speech.speak("Opening FaceTime")
             subprocess.run(["open", "-a", "FaceTime"], check=False)
             return True
             
        if "whatsapp" in cmd:
             self.speech.speak("Opening WhatsApp")
             subprocess.run(["open", "-a", "WhatsApp"], check=False)
             return True

        if "chatgpt" in cmd or "open ai" in cmd:
             self.speech.speak("Opening ChatGPT")
             subprocess.run(["open", "https://chatgpt.com"], check=False)
             return True

        # 2. GENERIC APP OPENER
        app_name = cmd.replace("open", "").strip()
        if not app_name: return False

        config = self.app.get('config')
        fuzzy = self.app.get('speech') # Wait, fuzzy matcher was passed to CommandProcessor __init__...
        # We need to access fuzzy matcher. It was passed as `fuzzy_matcher` to __init__.
        # I stored it in `self.fuzzy` in CommandProcessor.
        # But `app_context` (CommandProcessor.app_context) didn't include it explicitly?
        # I need to update CommandProcessor to pass `fuzzy` in context.
        # For now, I'll access it safely.

        # ALIAS MATCHING
        if config and hasattr(config, "MAC_APPS"):
            for key, app_full_name in config.MAC_APPS.items():
                if key in cmd:
                    return self._open_app(app_full_name)
        
        # FUZZY MATCHING
        # Accessing fuzzy matcher from context if available
        # logic: self.fuzzy.match_app_name(app_name)
        # Note: I haven't updated CommandProcessor to pass 'fuzzy' yet. I will do that next.
        
        # BASIC OPEN
        return self._open_app(app_name)

    def _open_app(self, app_name):
        try:
            # Try open command
            result = subprocess.run(["open", "-a", app_name], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.speech.speak(f"Opening {app_name}")
                self.log_usage(f"open {app_name}")
                return True
            else:
                 # If exact match failed, try fuzzy if available
                 fuzzy = self.app.get('fuzzy')
                 if fuzzy:
                     best_match = fuzzy.match_app_name(app_name)
                     if best_match:
                         subprocess.run(["open", "-a", best_match])
                         self.speech.speak(f"Opening {best_match}")
                         self.log_usage(f"open {best_match}")
                         return True
                 
                 self.logger.warning(f"Failed to open {app_name}: {result.stderr}")
                 self.speech.speak(f"I couldn't find an app named {app_name}.")
                 return True # Handled (as failure)
                 
        except Exception as e:
            self.logger.error(f"App Control Error: {e}")
            self.speech.speak(f"An error occurred while trying to open {app_name}.")
            return True
        
        return False
