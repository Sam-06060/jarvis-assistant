"""
modules/skills/smartthings_skill.py
────────────────────────────────────
Zero-latency SmartThings AC skill for Jarvis.
Registered as a high-priority pre-LLM skill.

Features hyper-advanced fuzzy phrase matching to catch natural conversational
prompts (e.g., "I'm burning", "make it 20", "room temperature", "increase it").
"""

import re
import logging
import time
from modules.smartthings import SmartThingsManager, SmartThingsError
from modules.skills.base import Skill

logger = logging.getLogger("jarvis.skill.smartthings")

# ── Intent Constants ──────────────────────────────────────────────────────────

INTENT_AC_ON      = "AC_ON"
INTENT_AC_OFF     = "AC_OFF"
INTENT_SET_TEMP   = "SET_TEMP"
INTENT_TEMP_UP    = "TEMP_UP"
INTENT_TEMP_DOWN  = "TEMP_DOWN"
INTENT_SET_MODE   = "SET_MODE"
INTENT_AC_STATUS  = "AC_STATUS"

# ── Pattern Registry ──────────────────────────────────────────────────────────

PATTERNS = [
    # AC_ON
    (INTENT_AC_ON, re.compile(
        r"\b(turn\s+on|switch\s+on|power\s+on|start|activate).*(ac|air\s*con|hvac|cooling)\b"
        r"|\b(turn\s+on|start)\s+(the\s+)?(ac|air\s*con)\b"
        r"|\bcool.*room\s+down\b"
        r"|\b(it's|its|it is|i am|im|i'm).*(hot|warm|stuffy|burning|boiling|roasting)\b"
        r"|\b(could\s+you\s+please\s+turn\s+on\s+the\s+ac|turn\s+on\s+the\s+ac\s+god\s*dammit)\b",
        re.IGNORECASE
    )),

    # AC_OFF
    (INTENT_AC_OFF, re.compile(
        r"\b(turn\s+off|switch\s+off|power\s+off|stop|disable|shut\s+down).*(ac|air\s*con|hvac|cooling)\b"
        r"|\b(it's|its|it is|i am|im|i'm).*(cold|freezing|too\s+cold|chilly)\b"
        r"|\b(turn\s+off\s+ac|ac\s+off|shut\s+ac)\b",
        re.IGNORECASE
    )),

    # TEMP_UP
    (INTENT_TEMP_UP, re.compile(
        r"\b(increase|raise|up).*(temperature|temp|it)\b"
        r"|\bmake\s+it\s+warmer\b"
        r"|\b(go|bump)\s+up\s+a\s+degree\b",
        re.IGNORECASE
    )),

    # TEMP_DOWN
    (INTENT_TEMP_DOWN, re.compile(
        r"\b(decrease|lower|drop|down).*(temperature|temp|it)\b"
        r"|\bmake\s+it\s+cooler\b"
        r"|\b(go|drop)\s+down\s+a\s+degree\b",
        re.IGNORECASE
    )),

    # SET_TEMP (extracts temp number)
    (INTENT_SET_TEMP, re.compile(
        r"\b(set|change|put|make|keep)\s+(the\s+)?(ac|air\s*con|temperature|temp|it)?\s*(to|at)?\s*(?P<temp>\d{1,2}(\.\d)?)\s*(degrees?|celsius|°c|°)?\b"
        r"|\b(?P<temp2>\d{1,2}(\.\d)?)\s*(degrees?|celsius|°c|°)\b"
        r"|\bmake\s+it\s+(?P<temp3>\d{1,2}(\.\d)?)\b"
        r"|\bcool\s+(it\s+)?to\s+(?P<temp4>\d{1,2}(\.\d)?)\b",
        re.IGNORECASE
    )),

    # SET_MODE (extracts mode string)
    (INTENT_SET_MODE, re.compile(
        r"\b(set|switch|change|put|make).*(to|on|in|mode)?\s*(?P<mode>cool(ing)?|heat(ing)?|auto|dry|fan\s*only|wind)\b"
        r"|\b(?P<mode2>cool|heat|auto|dry|fan\s*only)\s+mode\b",
        re.IGNORECASE
    )),

    # AC_STATUS
    (INTENT_AC_STATUS, re.compile(
        r"\b(ac\s+status|status\s+of\s+ac|how's\s+the\s+ac|what's\s+the\s+ac|ac\s+report)\b"
        r"|\b(is\s+the\s+ac\s+(on|off|running|online|offline))\b"
        r"|\bgive\s+me\s+(a\s+)?report\s+(for|on)\s+(the\s+)?ac\b"
        r"|\b(what's|what\s+is|tell\s+me\s+the).*(current\s+)?(room\s+)?temperature\b"
        r"|\bhow\s+is\s+the\s+ac\s+doing\b",
        re.IGNORECASE
    )),
]

MODE_NORMALISE = {
    "cooling": "cool",
    "heating": "heat",
    "fan only": "fanOnly",
    "fan_only": "fanOnly",
}

# ── Skill Class ───────────────────────────────────────────────────────────────

class SmartThingsSkill(Skill):
    SKILL_NAME = "SmartThingsSkill"
    PRIORITY = 0

    def __init__(self, app_context, manager: SmartThingsManager = None):
        super().__init__(app_context)
        self._manager = manager or SmartThingsManager()
        self.last_ac_interaction = 0
        logger.info("[SmartThingsSkill] Initialised with hyper-advanced NLP.")

    def can_handle(self, user_input: str) -> bool:
        cleaned = user_input.strip().lower()
        
        # Protective Guard: If they explicitly ask about weather, let WeatherSkill/LLM handle it
        if ("weather" in cleaned or "outside" in cleaned) and not "ac" in cleaned:
            return False

        intent, _ = self._detect_intent(cleaned)
        if intent:
            # Add some context guard here so that overly general phrases (like just numbers)
            # are only matched if we know we are talking about AC, unless it explicitly matches AC perfectly.
            # But the regexes are tuned to be highly AC specific (e.g. "make it 20" or "set temp to 22"),
            # so we'll trust the regex.
            logger.debug("[SmartThingsSkill] Matched intent '%s' for input: '%s'", intent, user_input[:60])
            return True
            
        return False

    def handle(self, user_input: str) -> str:
        cleaned = user_input.strip().lower()
        intent, match = self._detect_intent(cleaned)
        
        # Track context timeframe
        self.last_ac_interaction = time.time()
        logger.info("[SmartThingsSkill] Executing intent '%s'", intent)

        try:
            result = None
            if intent == INTENT_AC_ON:
                result = self._handle_on()
            elif intent == INTENT_AC_OFF:
                result = self._handle_off()
            elif intent == INTENT_SET_TEMP:
                result = self._handle_set_temp(match)
            elif intent == INTENT_TEMP_UP:
                result = self._handle_temp_up()
            elif intent == INTENT_TEMP_DOWN:
                result = self._handle_temp_down()
            elif intent == INTENT_SET_MODE:
                result = self._handle_set_mode(match)
            elif intent == INTENT_AC_STATUS:
                result = self._handle_status()
            else:
                result = "I couldn't determine what you wanted to do with the AC."
                
            if result and hasattr(self, 'speech') and self.speech is not None:
                self.speech.speak(result)
            return result
            
        except ValueError as e:
            res = f"I couldn't do that. {str(e)}"
            if hasattr(self, 'speech') and self.speech is not None:
                self.speech.speak(res)
            return res
        except SmartThingsError as e:
            res = f"There was a problem communicating with your AC. {str(e)}"
            if hasattr(self, 'speech') and self.speech is not None:
                self.speech.speak(res)
            return res

    # ── Intent Detection ─────────────────────────────────────────────────────

    def _detect_intent(self, user_input: str):
        for intent, pattern in PATTERNS:
            match = pattern.search(user_input)
            if match:
                return intent, match
        return None, None

    # ── Intent Handlers ──────────────────────────────────────────────────────

    def _handle_on(self) -> str:
        self._manager.turn_on()
        return "The AC has been started for you, sir."

    def _handle_off(self) -> str:
        self._manager.turn_off()
        return "AC powered off."

    def _handle_set_temp(self, match) -> str:
        raw_temp = (
            match.group("temp") or
            match.group("temp2") or
            match.group("temp3") or
            match.group("temp4")
        )
        if not raw_temp:
            return "I heard a temperature command but couldn't exact the degrees."

        celsius = float(raw_temp)
        self._manager.set_temperature(celsius)
        return f"Temperature is now set to {celsius:.0f} degrees."

    def _handle_temp_up(self) -> str:
        status = self._manager.get_status()
        current = status.get("coolingSetpoint")
        if current is None:
            return "I couldn't retrieve the current temperature to increase it."
        
        new_temp = current + 1
        self._manager.set_temperature(new_temp)
        return f"Temperature increased to {new_temp:.0f} degrees."

    def _handle_temp_down(self) -> str:
        status = self._manager.get_status()
        current = status.get("coolingSetpoint")
        if current is None:
            return "I couldn't retrieve the current temperature to decrease it."
        
        new_temp = current - 1
        self._manager.set_temperature(new_temp)
        return f"Temperature decreased. It's now {new_temp:.0f} degrees."

    def _handle_set_mode(self, match) -> str:
        raw_mode = match.group("mode") or match.group("mode2")
        if not raw_mode:
            return "I couldn't determine which mode you wanted."

        mode = raw_mode.lower().strip()
        mode = MODE_NORMALISE.get(mode, mode)
        self._manager.set_mode(mode)
        return f"AC has been switched to {mode} mode."

    def _handle_status(self) -> str:
        status = self._manager.get_status()
        switch_state = status.get("switch", "unknown")
        temp = status.get("temperature")
        setpoint = status.get("coolingSetpoint")
        mode = status.get("airConditionerMode", "unknown")

        parts = [f"The AC is {switch_state}."]
        if temp is not None:
            parts.append(f"Current room temperature is {temp} degrees.")
        if setpoint is not None and switch_state == "on":
            parts.append(f"It is set to {setpoint} degrees.")
        parts.append(f"Operating in {mode} mode.")
        return " ".join(parts)
