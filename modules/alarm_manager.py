
import subprocess
import datetime
import re
from dateutil import parser
from modules.skills.base import Skill

class AlarmManager:
    """
    Manages setting alarms using the native macOS Clock app via Shortcuts.
    Requires a shortcut named 'Set Alarm' that accepts text input.
    """
    def __init__(self):
        pass

    def set_alarm(self, time_input, label=None):
        """
        Parses the time input and triggers the 'Set Alarm' shortcut.
        Returns a tuple: (success_bool, status_message)
        """
        try:
            target_time = self._parse_smart_time(time_input)
            if not target_time:
                return False, f"Could not understand the time '{time_input}'."

            # Format for Shortcut (e.g., "2023-10-27 14:30:00")
            # Full datetime string is more reliable for Shortcuts parsing
            time_str = target_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Construct the input string for the shortcut
            # Ideally the shortcut handles "Time"
            shortcut_input = time_str
            
            # Attempt to run shortcut
            # shortcuts run "Set Alarm" -i "time_str"
            result = subprocess.run(
                ["shortcuts", "run", "Set Alarm", "-i", shortcut_input],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Success
                # If label is provided, we can mention it in the success message
                msg = f"Alarm set for {time_str}"
                if label:
                    msg += f" labeled '{label}'"
                return True, msg
            else:
                # Failed
                error_msg = result.stderr.strip()
                if "not found" in error_msg.lower():
                     return False, "I couldn't find the 'Set Alarm' shortcut."
                return False, f"Failed to set alarm: {error_msg}"

        except Exception as e:
            return False, f"Error setting alarm: {e}"

    def _parse_smart_time(self, time_string):
        """
        Intelligently parses time strings like "11", "11pm", "20 mins", "tomorrow at 9".
        Returns a datetime object or None.
        """
        try:
            time_string = time_string.lower().strip()
            now = datetime.datetime.now()
            
            # 1. Relative Time (e.g. "in 20 minutes")
            # Reuse logic from ReminderManager or implementing simple regex here
            # Regex for "X minutes/hours"
            relative_match = re.search(r'(\d+)\s*(min|hour|hr)', time_string)
            if relative_match:
                amount = int(relative_match.group(1))
                unit = relative_match.group(2)
                
                delta = datetime.timedelta(minutes=0)
                if 'min' in unit:
                    delta = datetime.timedelta(minutes=amount)
                elif 'hour' in unit or 'hr' in unit:
                    delta = datetime.timedelta(hours=amount)
                
                return now + delta

            # 2. Absolute Time (Smart Inference)
            # Try dateutil parser
            parsed_time = parser.parse(time_string, fuzzy=True)
            
            # If no date info was parsed (defaulted to today's date), we need to infer
            # Check if user specified "tomorrow"
            is_tomorrow_explicit = "tomorrow" in time_string
            
            if is_tomorrow_explicit:
                # If parser didn't catch "tomorrow" correctly (sometimes fuzzy ignores it if it finds a time)
                # Ensure date is tomorrow
                if parsed_time.date() == now.date():
                    parsed_time = parsed_time + datetime.timedelta(days=1)
            
            # AM/PM Inference for bare numbers (e.g. "11", "5:30")
            # Check if AM/PM was explicit in string
            is_ampm_explicit = "am" in time_string or "pm" in time_string
            
            if not is_ampm_explicit and not is_tomorrow_explicit:
                # Logic: Find the next occurrence of this time
                # Example: It's 10 AM. User says "9". Parser gives 9 AM Today (Past).
                # We want either 9 PM Today OR 9 AM Tomorrow?
                # Usually "set alarm for 9" at 10am means 9 PM or 9 AM next day.
                # Let's assume standard 12-hour clock logic.
                
                # Case A: Parsed as AM (default) and it's in the past
                if parsed_time < now:
                    # Try PM
                    parsed_time_pm = parsed_time + datetime.timedelta(hours=12)
                    if parsed_time_pm > now:
                        parsed_time = parsed_time_pm
                    else:
                        # PM is also past (e.g. it's 11 PM, user says 9)
                        # Assume Tomorrow Morning
                        parsed_time = parsed_time + datetime.timedelta(days=1)
                
                # Case B: Parsed as AM and it's in future, but user might mean PM?
                # E.g. It's 2 AM. User says "5". Parser gives 5 AM. User likely means 5 AM. -> Good.
                # E.g. It's 2 PM. User says "5". Parser gives 5 AM (Tomorrow, maybe? or Today Past?). 
                # parser.parse("5") usually gives Today 5:00 AM.
                
                # Refined Logic:
                # 1. Get Today 5:00 AM and Today 5:00 PM.
                # 2. Pick the first one that is > Now.
                # 3. If both are past, pick Tomorrow 5:00 AM.
                
                # Re-parse strictly for hour/minute components to rebuild
                # This avoids dateutil's default behavior
                
                # Actually, simpler:
                target_am = parsed_time.replace(hour=parsed_time.hour % 12) # Force AM equivalent (0-11)
                if abs(target_am.hour - 12) < 0.1: target_am = target_am.replace(hour=0) # Handle 12 AM edge case if needed
                
                # Construct candidates
                candidates = []
                
                # Candidate 1: Today AM
                c1 = now.replace(hour=target_am.hour, minute=target_am.minute, second=0, microsecond=0)
                candidates.append(c1)
                
                # Candidate 2: Today PM
                c2 = c1 + datetime.timedelta(hours=12)
                candidates.append(c2)
                
                # Candidate 3: Tomorrow AM
                c3 = c1 + datetime.timedelta(days=1)
                candidates.append(c3)
                
                # Candidate 4: Tomorrow PM
                c4 = c2 + datetime.timedelta(days=1)
                candidates.append(c4)
                
                # Filter for future
                future_candidates = [c for c in candidates if c > now]
                
                if future_candidates:
                    parsed_time = future_candidates[0]

            return parsed_time

        except Exception as e:
            print(f"Time parse error: {e}")
            return None
