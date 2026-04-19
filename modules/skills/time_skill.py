from .base import Skill
import datetime

class TimeSkill(Skill):
    # Domains that make this a compound query — yield to AgentCore so ALL parts get answered
    _COMPOUND_SIGNALS = [
        "weather", "temperature", "forecast", "humidity", "rain",
        "news", "headline", "stock", "price", "email", "message",
        "remind", "alarm", "schedule", "play", "search", "find", "open",
        "translate", "calculate", "convert",
    ]

    def can_handle(self, command: str) -> bool:
        cmd = command.lower()
        
        # Avoid conflict with Calculator ("5 times 5")
        if "times" in cmd or any(char.isdigit() for char in cmd):
            return False

        triggers = ["time", "date", "day is it"]
        if not any(t in cmd for t in triggers):
            return False

        # GUARD: If the query also asks about OTHER domains, let AgentCore handle the whole thing
        # so every part of the question gets answered, not just the time.
        if any(s in cmd for s in self._COMPOUND_SIGNALS):
            return False

        return True

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
