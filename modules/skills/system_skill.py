from .base import Skill
import subprocess
import re

class SystemSkill(Skill):
    def can_handle(self, command: str) -> bool:
        triggers = [
            "volume", "brightness", "screen", "voice feedback", "vad", "voice detection",
            "battery", "memory", "disk", "cpu", "system status", "uptime", "system info", "ram", "storage"
        ]
        return any(t in command for t in triggers)

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        
        # --- VOLUME CONTROL ---
        if "volume" in cmd:
            if "set volume" in cmd or "volume to" in cmd:
                # Extract number
                nums = re.findall(r'\d+', cmd)
                if nums:
                    return self._set_volume(nums[0])
            
            elif "up" in cmd or "raise" in cmd or "increase" in cmd:
                return self._adjust_volume("up")
            elif "down" in cmd or "lower" in cmd or "decrease" in cmd:
                return self._adjust_volume("down")
                
        # --- BRIGHTNESS CONTROL ---
        if "brightness" in cmd or ("screen" in cmd and ("dim" in cmd or "bright" in cmd)):
            if "set brightness" in cmd or "brightness to" in cmd:
                nums = re.findall(r'\d+', cmd)
                if nums:
                    return self._set_brightness(nums[0])
            
            elif "up" in cmd or "raise" in cmd or "increase" in cmd or "brighter" in cmd:
                return self._adjust_brightness("up")
            elif "down" in cmd or "lower" in cmd or "decrease" in cmd or "dim" in cmd:
                return self._adjust_brightness("down")
                
        # --- VOICE FEEDBACK ---
        if "voice feedback" in cmd:
            if "verbose" in cmd: self.speech.tts.set_feedback_level("verbose")
            elif "brief" in cmd: self.speech.tts.set_feedback_level("brief")
            elif "normal" in cmd: self.speech.tts.set_feedback_level("normal")
            elif "silent" in cmd: self.speech.tts.set_feedback_level("silent")
            else:
                 self.speech.speak("Say: voice feedback verbose, brief, normal, or silent")
                 return True
            self.speech.speak(f"Voice feedback set to {self.speech.tts.voice_feedback_level}")
            return True

        # --- VAD TOGGLE (MIC) ---
        if "toggle vad" in cmd or "toggle voice detection" in cmd:
             if hasattr(self.speech, "wake_word_active"):
                 self.speech.wake_word_active = not self.speech.wake_word_active
                 status = "enabled" if self.speech.wake_word_active else "disabled"
                 # Only update HUD, keep silent
                 if self.speech.hud_queue:
                      self.speech.hud_queue.put(("IDLE", f"Mic {status.title()}"))
             return True
        
        # --- SYSTEM INFO ---
        system = self.app.get('system')
        if system:
            # Battery - just percentage
            if "battery" in cmd and "status" not in cmd:
                battery_info = system.get_battery()
                # Extract just the percentage
                match = re.search(r'(\d+)%', battery_info)
                if match:
                    percent = match.group(1)
                    self.speech.speak(f"Battery is at {percent} percent")
                else:
                    self.speech.speak(battery_info)
                return True
            
            # Battery status - full details
            if "battery status" in cmd:
                self.speech.speak(system.get_battery())
                return True
            
            # Memory/RAM
            if "memory" in cmd or "ram" in cmd:
                self.speech.speak(system.get_memory())
                return True
            
            # Disk/Storage
            if "disk" in cmd or "storage" in cmd:
                self.speech.speak(system.get_disk())
                return True
            
            # CPU/Processor
            if "cpu" in cmd or "processor" in cmd:
                self.speech.speak(system.get_cpu())
                return True
            
            # System status - comprehensive overview
            if "system status" in cmd or "system info" in cmd:
                self.speech.speak(system.get_detailed_status())
                return True
            
            # Uptime
            if "uptime" in cmd:
                self.speech.speak(system.get_uptime())
                return True
              
        return False

    # --- HELPERS ---
    def _set_volume(self, level):
        try:
            target = int(level)
            subprocess.run(["osascript", "-e", f"set volume output volume {target}"], check=False)
            self.speech.speak(f"Volume set to {target} percent.")
            return True
        except Exception:
            self.speech.speak("I couldn't adjust the volume.")
            return True

    def _adjust_volume(self, direction):
        try:
            result = subprocess.run(
                ["osascript", "-e", "output volume of (get volume settings)"],
                capture_output=True, text=True
            )
            current = int(result.stdout.strip())
            
            if direction == "up":
                new_vol = min(100, current + 10)
            else:
                new_vol = max(0, current - 10)
            
            subprocess.run(["osascript", "-e", f"set volume output volume {new_vol}"], check=False)
            self.speech.speak(f"Volume set to {new_vol} percent.")
            return True
        except:
             return True

    def _set_brightness(self, level):
        try:
            # Need to convert 0-100 to 0.0-1.0 if using `shortcuts`, or use CLI tool
            # Original code used shortcuts: ["shortcuts", "run", "Set Brightness", "-i", target]
            val = int(level) / 100
            target = str(val)
            result = subprocess.run(
                ["shortcuts", "run", "Set Brightness", "-i", target], 
                capture_output=True, text=True
            )
            if result.returncode != 0:
                self.speech.speak("I couldn't set the brightness. Do you have the shortcut installed?")
                return True
            self.speech.speak(f"Screen brightness set to {level} percent.")
            return True
        except Exception:
            return True

    def _adjust_brightness(self, direction):
        if direction == "up":
            return self._set_brightness(80) # Simple toggle logic from original
        else:
            return self._set_brightness(30)
