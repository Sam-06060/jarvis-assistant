import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta
from dateutil import parser
import subprocess
import re

logger = logging.getLogger(__name__)

class ReminderManager:
    """Background reminder system"""
    
    def __init__(self, data_file="data/reminders.json"):
        self.data_file = data_file
        self.reminders = []
        self.running = False
        self.check_thread = None
        self.load_reminders()
    
    def load_reminders(self):
        """Load reminders from disk"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.reminders = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load reminders: {e}")
            self.reminders = []
    
    def save_reminders(self):
        """Atomically save reminders to disk (write to .tmp then rename)."""
        try:
            os.makedirs(os.path.dirname(self.data_file) or '.', exist_ok=True)
            tmp_path = self.data_file + ".tmp"
            with open(tmp_path, 'w') as f:
                json.dump(self.reminders, f, indent=2)
            os.replace(tmp_path, self.data_file)  # atomic on POSIX
        except Exception as e:
            logger.warning(f"Could not save reminders: {e}")
    
    def add_reminder(self, message, when_string):
        """Add a new reminder with Smart AM/PM inference"""
        try:
            # 1. Try relative time first (e.g., "in 5 mins")
            reminder_time = self._parse_relative_time(when_string)
            
            # 2. If not relative, parse absolute date/time
            if reminder_time is None:
                reminder_time = parser.parse(when_string, fuzzy=True)
                
                # --- SMART AM/PM LOGIC ---
                now = datetime.now()
                
                # If the parsed time is in the past (e.g., User says "10:15" at 11:00 AM)
                if reminder_time < now:
                    # Check if user explicitly said AM or PM
                    is_explicit = re.search(r'\b(am|pm)\b', when_string.lower())
                    
                    if not is_explicit:
                        # Ambiguous time: Try shifting to PM (add 12 hours)
                        # Example: 10:15 (AM) -> 22:15 (PM)
                        test_time = reminder_time + timedelta(hours=12)
                        
                        if test_time > now:
                            # If PM is in the future, assume user meant PM
                            reminder_time = test_time
                        else:
                            # If PM is also past (e.g. it's 11 PM and user says 9:00),
                            # assume they mean 9:00 AM tomorrow.
                            reminder_time = reminder_time + timedelta(days=1)
                    else:
                        # User was explicit (e.g. "9am") but it passed -> Set for tomorrow
                        reminder_time = reminder_time + timedelta(days=1)
            
            # 3. Clean up seconds (Snap to :00 for precision)
            reminder_time = reminder_time.replace(second=0, microsecond=0)
            
            reminder = {
                "id": len(self.reminders) + 1,
                "message": message,
                "time": reminder_time.isoformat(),
                "triggered": False,
                "created": datetime.now().isoformat()
            }
            
            self.reminders.append(reminder)
            self.save_reminders()
            
            time_str = reminder_time.strftime("%I:%M %p on %B %d")
            return f"Reminder set: '{message}' at {time_str}"
            
        except Exception as e:
            return f"Could not set reminder: {str(e)}"
    
    def _parse_relative_time(self, time_string):
        """Parse relative time and SNAP to the start of the minute"""
        time_string = time_string.lower()
        word_to_num = {
            'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
            'fifteen': '15', 'twenty': '20', 'thirty': '30',
            'a': '1', 'an': '1'
        }
        for word, digit in word_to_num.items():
            time_string = re.sub(r'\b' + word + r'\b', digit, time_string)
            
        pattern = r'(\d+)\s*(minutes?|mins?|hours?|hrs?|days?)'
        match = re.search(pattern, time_string)
        
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            
            now = datetime.now()
            target = now
            
            if 'min' in unit:
                target = now + timedelta(minutes=amount)
            elif 'hour' in unit or 'hr' in unit:
                target = now + timedelta(hours=amount)
            elif 'day' in unit:
                target = now + timedelta(days=amount)
            
            # Return time with 00 seconds
            return target.replace(second=0, microsecond=0)
            
        return None
    
    def get_active_reminders(self):
        active = [r for r in self.reminders if not r["triggered"]]
        if not active: return "No active reminders."
        result = "Active Reminders:\n"
        for reminder in active:
            time_obj = datetime.fromisoformat(reminder["time"])
            result += f"• {reminder['message']} - {time_obj.strftime('%I:%M %p')}\n"
        return result.strip()
    
    def start_background_check(self):
        """Start the independent background thread"""
        if self.running:
            return
        self.running = True
        self.check_thread = threading.Thread(target=self._check_reminders_loop, daemon=True)
        self.check_thread.start()
    
    def stop_background_check(self):
        """Stop the background thread"""
        self.running = False
        if self.check_thread:
            self.check_thread.join(timeout=1)
    
    def _check_reminders_loop(self):
        """The loop that runs in the background thread"""
        while self.running:
            try:
                now = datetime.now()
                is_dirty = False
                
                for reminder in self.reminders:
                    if reminder["triggered"]:
                        continue
                    
                    reminder_time = datetime.fromisoformat(reminder["time"])
                    
                    if now >= reminder_time:
                        self._trigger_reminder(reminder)
                        reminder["triggered"] = True
                        is_dirty = True
                
                if is_dirty:
                    self.save_reminders()
                
                # Check every 0.5 seconds for instant reaction
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Reminder check error: {e}")
                time.sleep(5)

    def _trigger_reminder(self, reminder):
        """Trigger a reminder notification (NON-BLOCKING)"""
        try:
            message = reminder["message"]
            logger.info(f"\U0001f514 REMINDER TRIGGERED: {message}")

            script = f'display notification "{message}" with title "JARVIS" sound name "Glass"'
            subprocess.Popen(["osascript", "-e", script])
            subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"])
            subprocess.Popen(["say", f"Reminder: {message}"])

        except Exception as e:
            logger.error(f"Error triggering reminder: {e}")
            
    def clear_old_reminders(self):
        cutoff = datetime.now() - timedelta(days=1)
        self.reminders = [r for r in self.reminders if not r["triggered"] or datetime.fromisoformat(r["time"]) > cutoff]
        self.save_reminders()
    
    def cancel_reminder(self, reminder_id):
        self.reminders = [r for r in self.reminders if r["id"] != reminder_id]
        self.save_reminders()
        return f"Reminder {reminder_id} cancelled."
    
    def clear_all_reminders(self):
        self.reminders = []
        self.save_reminders()
        return "All reminders cleared."