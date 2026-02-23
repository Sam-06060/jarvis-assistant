from .base import Skill

class FocusSkill(Skill):
    def can_handle(self, command: str) -> bool:
        triggers = ["do not disturb", "dnd", "focus"]
        return any(t in command.lower() for t in triggers)

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        focus = self.app.get('focus')
        if not focus: return False

        if "do not disturb" in cmd or "dnd" in cmd:
            if "enable" in cmd or "on" in cmd:
                result = focus.enable_do_not_disturb()
            elif "disable" in cmd or "off" in cmd:
                result = focus.disable_do_not_disturb()
            else:
                result = "Say: enable do not disturb or disable do not disturb"
            
            self.speech.speak(result)
            return True
            
        return False
