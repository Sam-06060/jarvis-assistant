"""
modules/skills/smartthings_skill.py
────────────────────────────────────
Zero-latency SmartThings AC skill for Jarvis.
Registered as a high-priority pre-LLM skill.

Features hyper-advanced fuzzy phrase matching to catch natural conversational
prompts (e.g., "I'm burning", "make it 20", "room temperature", "increase it").
"""

import re
import os
import logging
import time
import urllib.request
import json
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
        r"|\b(turn|switch)\s+(the\s+)?(ac|air\s*con)\s+(on|back\s+on)\b"  # 'turn the ac on'
        r"|\b(ac|air\s*con)\s+on\b"
        r"|\bcool.*room\s+down\b"
        r"|\b(it's|its|it is|i am|im|i'm).*(hot|warm|stuffy|burning|boiling|roasting)\b"
        r"|\b(could\s+you\s+please\s+turn\s+on\s+the\s+ac|turn\s+on\s+the\s+ac\s+god\s*dammit)\b",
        re.IGNORECASE
    )),

    # AC_OFF
    (INTENT_AC_OFF, re.compile(
        r"\b(turn\s+off|switch\s+off|power\s+off|stop|disable|shut\s+down).*(ac|air\s*con|hvac|cooling)\b"
        r"|\b(turn|switch)\s+(the\s+)?(ac|air\s*con)\s+off\b"  # 'turn the ac off'
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

    # Context window: bare "turn off/on" within this many seconds of an AC command = AC command
    CONTEXT_WINDOW_SECS = 180

    def __init__(self, app_context, manager: SmartThingsManager = None):
        super().__init__(app_context)
        self.last_ac_interaction = 0
        # Use provided manager (tests) or create one that reads from env
        self._manager = manager or SmartThingsManager()
        logger.info("[SmartThingsSkill] Initialised. AC commands route via Python → SmartThings API.")

    def _in_ac_context(self) -> bool:
        """Returns True if an AC command was used within the context window."""
        return (time.time() - self.last_ac_interaction) < self.CONTEXT_WINDOW_SECS

    def can_handle(self, user_input: str) -> bool:
        cleaned = user_input.strip().lower()

        # Guard: weather questions go elsewhere
        if ("weather" in cleaned or "outside" in cleaned) and "ac" not in cleaned:
            return False

        # Primary: regex intent matched
        intent, _ = self._detect_intent(cleaned)
        if intent:
            logger.debug("[SmartThingsSkill] Matched intent '%s' for: '%s'", intent, user_input[:60])
            return True

        # Context-aware: bare "turn off / switch off / turn on / switch on"
        # within CONTEXT_WINDOW after an AC command → AC command, not shutdown
        if self._in_ac_context():
            if re.match(r'^(turn|switch)\s+off\s*$', cleaned):
                logger.debug("[SmartThingsSkill] Context match: AC_OFF for bare '%s'", cleaned)
                return True
            if re.match(r'^(turn|switch)\s+on\s*$', cleaned):
                logger.debug("[SmartThingsSkill] Context match: AC_ON for bare '%s'", cleaned)
                return True

        return False

    def handle(self, user_input: str) -> str:
        cleaned = user_input.strip().lower()
        intent, match = self._detect_intent(cleaned)

        # Resolve context-based intents that didn't match a full regex
        if intent is None and self._in_ac_context():
            if re.match(r'^(turn|switch)\s+off\s*$', cleaned):
                intent = INTENT_AC_OFF
            elif re.match(r'^(turn|switch)\s+on\s*$', cleaned):
                intent = INTENT_AC_ON

        self.last_ac_interaction = time.time()
        logger.info("[SmartThingsSkill] Executing intent '%s'", intent)

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

    # ── Intent Detection ─────────────────────────────────────────────────────

    def _detect_intent(self, user_input: str):
        for intent, pattern in PATTERNS:
            match = pattern.search(user_input)
            if match:
                return intent, match
        return None, None

    # ── Intent Handlers — direct Python API calls ─────────────────────────────

    def _handle_on(self) -> str:
        try:
            self._manager.turn_on()
            return "Turning the AC on."
        except SmartThingsError as e:
            logger.error("[SmartThingsSkill] turn_on failed: %s", e)
            return f"I couldn't turn the AC on. {e}"

    def _handle_off(self) -> str:
        try:
            self._manager.turn_off()
            return "Turning the AC off."
        except SmartThingsError as e:
            logger.error("[SmartThingsSkill] turn_off failed: %s", e)
            return f"I couldn't turn the AC off. {e}"

    def _handle_set_temp(self, match) -> str:
        raw_temp = (
            match.group("temp") or
            match.group("temp2") or
            match.group("temp3") or
            match.group("temp4")
        )
        if not raw_temp:
            return "I couldn't determine the temperature you wanted."
        try:
            celsius = float(raw_temp)
            self._manager.set_temperature(celsius)
            return f"Setting the temperature to {int(celsius)} degrees."
        except ValueError as e:
            return f"That temperature is out of range. {e}"
        except SmartThingsError as e:
            return f"I couldn't set the temperature. {e}"

    def _handle_temp_up(self) -> str:
        try:
            status = self._manager.get_status()
            current = status.get("coolingSetpoint")
            if current is None:
                return "I couldn't read the current temperature to increase it."
            new_temp = int(current) + 1
            self._manager.set_temperature(new_temp)
            return f"Increasing the temperature to {new_temp} degrees."
        except SmartThingsError as e:
            return f"I couldn't increase the temperature. {e}"

    def _handle_temp_down(self) -> str:
        try:
            status = self._manager.get_status()
            current = status.get("coolingSetpoint")
            if current is None:
                return "I couldn't read the current temperature to decrease it."
            new_temp = int(current) - 1
            self._manager.set_temperature(new_temp)
            return f"Decreasing the temperature to {new_temp} degrees."
        except SmartThingsError as e:
            return f"I couldn't decrease the temperature. {e}"

    def _handle_set_mode(self, match) -> str:
        raw_mode = match.group("mode") or match.group("mode2")
        if not raw_mode:
            return "I couldn't determine which mode you wanted."
        mode = MODE_NORMALISE.get(raw_mode.lower().strip(), raw_mode.lower().strip())
        try:
            self._manager.set_mode(mode)
            return f"Setting AC to {mode} mode."
        except (SmartThingsError, ValueError) as e:
            return f"I couldn't set the AC mode. {e}"

    def _handle_status(self) -> str:
        try:
            s = self._manager.get_status()
            switch = s.get("switch", "unknown")
            temp   = s.get("temperature")
            setpt  = s.get("coolingSetpoint")
            mode   = s.get("airConditionerMode", "unknown")
            fan    = s.get("fanMode", "")

            parts = [f"The AC is currently {switch}."]
            if temp is not None:
                parts.append(f"Room temperature is {int(temp)} degrees Celsius.")
            if setpt is not None and switch == "on":
                parts.append(f"Set to {int(setpt)} degrees.")
            if switch == "on":
                parts.append(f"Running in {mode} mode" + (f" with {fan} fan." if fan else "."))
            return " ".join(parts)
        except SmartThingsError as e:
            return f"I couldn't fetch the AC status. {e}"

