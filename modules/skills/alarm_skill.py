
from .base import Skill
import re

class AlarmSkill(Skill):
    def __init__(self, app_context):
        super().__init__(app_context)
        # Do NOT cache alarm_manager here — it is registered AFTER skills load
        # (startup race condition). Store the registry for lazy lookup at call time.
        self._registry = app_context.get('registry')

    def _get_alarm_manager(self):
        """Lazy lookup — always fetches the real registered AlarmManager instance."""
        if self._registry:
            return self._registry.get('alarms')
        return None

    def can_handle(self, command: str) -> bool:
        cmd = command.lower()
        triggers = ["set alarm", "set an alarm", "wake me up"]
        return any(t in cmd for t in triggers)

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        
        # Extract Time and Label
        # Patterns:
        # 1. "Set alarm for [TIME] called [LABEL]"
        # 2. "Set alarm for [TIME]"
        # 3. "Wake me up in [TIME]" hiding "alarm" keyword
        
        # Regex to capture content after "for" or "at"
        # Be careful not to capture "for" if it's part of "set alarm for"
        
        time_part = None
        label_part = None
        
        # Check for label first (at the end)
        label_match = re.search(r'(called|named|labeled|with label)\s+(.+)$', cmd)
        if label_match:
            label_part = label_match.group(2).strip()
            # Remove label part from command for time parsing
            cmd = cmd[:label_match.start()].strip()
            
        # Extract Time
        # "Set alarm FOR 5 minutes"
        # "Wake me up AT 7am"
        # "Set alarm 5 minutes" (implied for)
        
        # Strategy: Remove the trigger words, then look for "for" or "at" or just take the rest
        clean_cmd = cmd
        for trigger in ["set an alarm", "set alarm", "wake me up"]:
            if trigger in clean_cmd:
                clean_cmd = clean_cmd.replace(trigger, "").strip()
                break
        
        # Remove leading "for" or "at"
        if clean_cmd.startswith("for "):
            clean_cmd = clean_cmd[4:].strip()
        elif clean_cmd.startswith("at "):
            clean_cmd = clean_cmd[3:].strip()
            
        time_part = clean_cmd
        
        if not time_part:
            self.speech.speak("What time should I set the alarm for?")
            return True
            
        alarm_manager = self._get_alarm_manager()
        if alarm_manager:
            success, message = alarm_manager.set_alarm(time_part, label_part)
            self.speech.speak(message)
        else:
            self.speech.speak("Alarm system is not available yet, please try again in a moment.")
            
        return True
