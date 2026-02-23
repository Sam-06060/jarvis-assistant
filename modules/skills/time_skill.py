from .base import Skill
import datetime

class TimeSkill(Skill):
    def can_handle(self, command: str) -> bool:
        cmd = command.lower()
        
        # Avoid conflict with Calculator ("5 times 5")
        if "times" in cmd or any(char.isdigit() for char in cmd):
            return False

        triggers = ["time", "date", "day is it"]
        return any(t in cmd for t in triggers)

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        
        # TIME
        if "time" in cmd:
            now = datetime.datetime.now().strftime('%I:%M %p')
            self.speech.speak(f"It's {now}")
            self.log_usage(command)
            return True
            
        # DATE
        if "date" in cmd or "day is it" in cmd:
            today = datetime.datetime.now().strftime('%A, %B %d, %Y')
            self.speech.speak(f"Today is {today}")
            self.log_usage(command)
            return True
            
        return False
