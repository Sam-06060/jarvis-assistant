from .base import Skill
import subprocess
import re

# ============================================================
# WORD-TO-NUMBER MAP (Handles misheard / spoken numbers)
# ============================================================
WORD_TO_NUMBER = {
    # Core numbers
    "zero": 0, "one": 1, "uno": 1,
    "two": 2, "tu": 2,
    "three": 3, "tree": 3,
    "four": 4,
    "five": 5, "fife": 5,
    "six": 6, "sex": 6, "sics": 6,
    "seven": 7,
    "eight": 8, "ate": 8,
    "nine": 9, "nein": 9,
    "ten": 10, "tin": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19,
    # Tens
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    # Special
    "hundred": 100, "full": 100, "max": 100, "maximum": 100,
    "half": 50, "quarter": 25,
    # Descriptive levels
    "low": 20, "medium": 50, "med": 50, "mid": 50,
    "high": 80, "loud": 90, "louder": 80,
    "quiet": 15, "silent": 0, "mute": 0, "soft": 20,
}

# ============================================================
# LOCK SCREEN NLP PATTERNS
# ============================================================
LOCK_DIRECT_TRIGGERS = [
    "lock", "lock screen", "lock device", "lock computer", "lock my computer",
    "lock my screen", "lock the screen", "screen off", "display off",
    "turn off screen", "turn off display", "turn off the screen",
]

LOCK_NLP_PATTERNS = [
    r"\bi\s*(?:am|'m)\s+going\b",           # "i am going", "i'm going"
    r"\bgoing\s+away\b",                     # "going away"
    r"\bstepping\s+away\b",                  # "stepping away"
    r"\b(?:brb|be\s+right\s+back)\b",        # "brb", "be right back"
    r"\bi'?ll\s+be\s+back\b",               # "i'll be back"
    r"\bleaving\s+(?:now|for)\b",            # "leaving now", "leaving for"
    r"\bwalk(?:ing)?\s+away\b",              # "walk away", "walking away"
    r"\btake\s+a\s+break\b",                 # "take a break"
    r"\baway\s+for\s+(?:a\s+)?(?:minute|bit|moment|while|sec)\b",  # "away for a minute"
    r"\bneed\s+to\s+(?:go|leave|step\s+out)\b",  # "need to go"
]

# ============================================================
# VOLUME NLP PATTERNS (intent-based, no "volume" keyword needed)
# ============================================================
VOLUME_NLP_PATTERNS = [
    r"\bmake\s+it\s+(?:louder|quieter|softer|silent|loud)\b",
    r"\bturn\s+(?:it\s+)?(?:up|down)\b",
    r"\b(?:louder|quieter)\b",
    r"\b(?:full|max|maximum)\s+volume\b",
    r"\bunmute\b",
]


def _parse_number_from_text(text):
    """
    Extract a number from text using digits first, then word-to-number mapping.
    Handles compound numbers like "twenty five" → 25, "one hundred" → 100.
    Returns int or None.
    """
    # 1. Try raw digits first
    nums = re.findall(r'\d+', text)
    if nums:
        return int(nums[0])

    # 2. Word-to-number parsing
    words = text.lower().split()
    result = None
    for word in words:
        clean_word = word.strip(".,!?")
        if clean_word in WORD_TO_NUMBER:
            val = WORD_TO_NUMBER[clean_word]
            if result is None:
                result = val
            elif val >= 100:
                # "one hundred" → 1 * 100 = 100
                result = result * val if result > 0 else val
            elif val >= 10 and result < 10:
                # "twenty" after nothing OR "twenty five" pattern
                result = val
            elif val < 10 and result is not None and result % 10 == 0:
                # "twenty" + "five" → 25
                result += val
            else:
                result = val
    return result


class SystemSkill(Skill):
    def can_handle(self, command: str) -> bool:
        cmd = command.lower().strip()
        
        # Standard keyword triggers
        triggers = [
            "volume", "brightness", "screen", "voice feedback", "vad", "voice detection",
            "battery", "memory", "disk", "cpu", "system status", "uptime", "system info",
            "ram", "storage", "lock", "mute", "unmute",
        ]
        if any(t in cmd for t in triggers):
            return True
        
        # NLP: Lock intent
        for pattern in LOCK_NLP_PATTERNS:
            if re.search(pattern, cmd):
                return True
        
        # NLP: Volume intent (no "volume" keyword)
        for pattern in VOLUME_NLP_PATTERNS:
            if re.search(pattern, cmd):
                return True
        
        return False

    def get_phrases(self) -> list[str]:
        return [
            # Volume
            "set volume", "volume up", "volume down", "mute", "unmute",
            "make it louder", "make it quieter", "turn it up", "turn it down",
            "full volume", "max volume", "louder", "quieter",
            # Brightness
            "set brightness", "brightness up", "brightness down", "brighter", "dimmer",
            "max brightness", "full brightness", "minimum brightness",
            # Lock
            "lock", "lock screen", "lock device", "screen off",
            "brb", "be right back", "stepping away", "going away",
            # System
            "battery", "system status", "system info", "cpu", "memory", "ram",
            "disk", "storage", "uptime",
            "voice feedback verbose", "voice feedback brief",
            "voice feedback normal", "voice feedback silent",
        ]

    def handle(self, command: str) -> bool:
        cmd = command.lower()

        # --- LOCK SCREEN ---
        if self._is_lock_intent(cmd):
            return self._lock_screen()

        # --- VOLUME CONTROL ---
        if self._is_volume_intent(cmd):
            return self._handle_volume(cmd)
                
        # --- BRIGHTNESS CONTROL ---
        if "brightness" in cmd or ("screen" in cmd and ("dim" in cmd or "bright" in cmd)):
            # Max / Full brightness
            if re.search(r"\b(?:max|full|maximum)\s*brightness\b", cmd):
                return self._set_brightness(100)
            # Min / Minimum brightness
            if re.search(r"\b(?:min|minimum|lowest)\s*brightness\b", cmd):
                return self._set_brightness(5)
            
            if "set brightness" in cmd or "brightness to" in cmd:
                level = _parse_number_from_text(cmd)
                if level is not None:
                    return self._set_brightness(level)
            
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
                 if self.speech.hud_queue:
                      self.speech.hud_queue.put(("IDLE", f"Mic {status.title()}"))
             return True
        
        # --- SYSTEM INFO ---
        system = self.app.get('system')
        if system:
            if "battery" in cmd and "status" not in cmd:
                battery_info = system.get_battery()
                match = re.search(r'(\d+)%', battery_info)
                if match:
                    percent = match.group(1)
                    self.speech.speak(f"Battery is at {percent} percent")
                else:
                    self.speech.speak(battery_info)
                return True
            
            if "battery status" in cmd:
                self.speech.speak(system.get_battery())
                return True
            
            if "memory" in cmd or "ram" in cmd:
                self.speech.speak(system.get_memory())
                return True
            
            if "disk" in cmd or "storage" in cmd:
                self.speech.speak(system.get_disk())
                return True
            
            if "cpu" in cmd or "processor" in cmd:
                self.speech.speak(system.get_cpu())
                return True
            
            if "system status" in cmd or "system info" in cmd:
                self.speech.speak(system.get_detailed_status())
                return True
            
            if "uptime" in cmd:
                self.speech.speak(system.get_uptime())
                return True
              
        return False

    # ============================================================
    # LOCK SCREEN
    # ============================================================
    def _is_lock_intent(self, cmd):
        """Check if command is a lock-screen intent."""
        # Direct triggers
        for trigger in LOCK_DIRECT_TRIGGERS:
            if trigger in cmd:
                return True
        # NLP patterns
        for pattern in LOCK_NLP_PATTERNS:
            if re.search(pattern, cmd):
                return True
        return False

    def _lock_screen(self):
        """Lock the Mac screen using pmset (puts display to sleep)."""
        try:
            self.speech.speak("Locking screen.")
            subprocess.run(["pmset", "displaysleepnow"], check=False)
            return True
        except Exception as e:
            self.speech.speak("I couldn't lock the screen.")
            return True

    # ============================================================
    # VOLUME (NLP-AWARE)
    # ============================================================
    def _is_volume_intent(self, cmd):
        """Check if command is a volume intent (keyword or NLP)."""
        if "volume" in cmd or "mute" in cmd or "unmute" in cmd:
            return True
        for pattern in VOLUME_NLP_PATTERNS:
            if re.search(pattern, cmd):
                return True
        return False

    def _handle_volume(self, cmd):
        """Smart volume handler with NLP word-to-number parsing."""
        # Mute / Unmute
        if "unmute" in cmd:
            subprocess.run(["osascript", "-e", "set volume without output muted"], check=False)
            self.speech.speak("Unmuted.")
            return True
        if cmd.strip() == "mute" or "mute" in cmd and "un" not in cmd:
            subprocess.run(["osascript", "-e", "set volume with output muted"], check=False)
            self.speech.speak("Muted.")
            return True

        # Set to specific level
        if "set volume" in cmd or "volume to" in cmd or "volume at" in cmd:
            level = _parse_number_from_text(cmd)
            if level is not None:
                return self._set_volume(level)
            else:
                self.speech.speak("I didn't catch the volume level. Try saying a number.")
                return True
        
        # Full / Max volume
        if re.search(r"\b(?:full|max|maximum)\s*(?:volume)?\b", cmd):
            return self._set_volume(100)

        # Direction: Up / Louder
        if any(w in cmd for w in ["up", "raise", "increase", "louder", "higher"]):
            return self._adjust_volume("up")
        
        # Direction: Down / Quieter
        if any(w in cmd for w in ["down", "lower", "decrease", "quieter", "softer", "quiet"]):
            return self._adjust_volume("down")

        # NLP catch-all: "make it louder" / "turn it up" etc.
        if re.search(r"\b(?:loud|louder|turn.*up)\b", cmd):
            return self._adjust_volume("up")
        if re.search(r"\b(?:quiet|quieter|softer|turn.*down)\b", cmd):
            return self._adjust_volume("down")

        # Volume with just a number: "volume fifty"
        level = _parse_number_from_text(cmd)
        if level is not None:
            return self._set_volume(level)

        self.speech.speak("I didn't understand the volume command.")
        return True

    def _set_volume(self, level):
        try:
            target = max(0, min(100, int(level)))
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

    # ============================================================
    # BRIGHTNESS (Native macOS API — no Shortcuts dependency)
    # ============================================================
    def _set_brightness(self, level):
        """Set display brightness using native macOS DisplayServices API."""
        try:
            target = max(0, min(100, int(level)))
            val = target / 100.0  # DisplayServices expects 0.0 - 1.0
            
            import ctypes
            # Load DisplayServices private framework (works on macOS 12+ / Apple Silicon)
            ds = ctypes.cdll.LoadLibrary(
                "/System/Library/PrivateFrameworks/DisplayServices.framework/DisplayServices"
            )
            # Get main display ID from CoreGraphics
            cg = ctypes.cdll.LoadLibrary(
                "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics"
            )
            cg.CGMainDisplayID.restype = ctypes.c_uint32
            main_display = cg.CGMainDisplayID()
            
            # Set brightness (0.0 to 1.0)
            ds.DisplayServicesSetBrightness.argtypes = [ctypes.c_uint32, ctypes.c_float]
            ds.DisplayServicesSetBrightness(main_display, ctypes.c_float(val))
            
            self.speech.speak(f"Brightness set to {target} percent.")
            return True
        except Exception as e:
            # Fallback: Try Shortcuts approach
            try:
                val_str = f"{target / 100.0:.2f}"
                result = subprocess.run(
                    ["shortcuts", "run", "Set Brightness", "-i", val_str],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    self.speech.speak(f"Brightness set to {target} percent.")
                    return True
            except Exception:
                pass
            self.speech.speak("I couldn't set the brightness.")
            return True

    def _adjust_brightness(self, direction):
        if direction == "up":
            return self._set_brightness(80)
        else:
            return self._set_brightness(30)
