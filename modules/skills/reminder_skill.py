from .base import Skill

class ReminderSkill(Skill):
    def can_handle(self, command: str) -> bool:
        triggers = ["remind", "reminder", "set a reminder"]
        return any(t in command.lower() for t in triggers)
    
    def handle(self, command: str) -> bool:
        cmd = command.lower()
        reminders = self.app.get('reminders')
        
        if not reminders:
            return False
        
        # List reminders
        if "list" in cmd or "show" in cmd or "what are" in cmd:
            result = reminders.get_active_reminders()
            self.speech.speak(result)
            return True
        
        # Set reminder: "remind me to X at/in Y"
        if "remind me to" in cmd or "set a reminder" in cmd:
            # Parse: "remind me to [message] at/in [time]"
            import re
            
            # Try "remind me to X at Y"
            match = re.search(r'remind me to (.+?) (?:at|in) (.+)', cmd)
            if not match:
                # Try "set a reminder to X at Y"
                match = re.search(r'set (?:a )?reminder (?:to )?(.+?) (?:at|in) (.+)', cmd)
            
            if match:
                message = match.group(1).strip()
                when = match.group(2).strip()
                result = reminders.add_reminder(message, when)
                self.speech.speak(result)
                return True
            else:
                self.speech.speak("Say: remind me to [task] at [time]")
                return True
        
        # Clear reminders
        if "clear" in cmd and "reminder" in cmd:
            if "all" in cmd:
                result = reminders.clear_all_reminders()
                self.speech.speak(result)
                return True
        
        return False
