# Jarvis × Samsung SmartThings AC Integration
## Master Implementation Plan — Full Technical Specification

---

## 0. CONTEXT & OBJECTIVES

This document is the canonical implementation specification for integrating Samsung SmartThings AC control natively into the Jarvis voice assistant. It is written to be executed by an AI coding agent with zero additional ambiguity. Every file path, class name, method signature, error code, config key, and data shape is specified explicitly.

**Primary goals:**
1. Sub-100ms AC command execution via a dedicated Skill layer (bypassing the LLM round-trip entirely for simple voice commands).
2. Full agentic LLM integration for complex, compound requests (e.g., "I feel hot, cool down the room and play lofi").
3. Secrets stored exclusively in environment variables — never committed to source control.
4. Graceful degradation if the SmartThings API is unreachable — Jarvis must not crash or hang.
5. Comprehensive logging at every layer so failures are instantly diagnosable.

---

## 1. REPOSITORY LAYOUT — FILES TO CREATE OR MODIFY

```
jarvis/
├── config.py                          ← MODIFY
├── modules/
│   ├── smartthings.py                 ← CREATE (new)
│   ├── commands.py                    ← MODIFY
│   └── skills/
│       └── smartthings_skill.py       ← CREATE (new)
├── tests/
│   └── test_smartthings.py            ← CREATE (new)
└── scripts/
    └── verify_smartthings.py          ← CREATE (new) — standalone ping script
```

> **Do NOT touch** any other existing file unless explicitly stated below.

---

## 2. SECRETS & ENVIRONMENT SETUP

### 2.1 Environment Variables Required

| Variable Name | Description | Example Value |
|---|---|---|
| `SMARTTHINGS_PAT` | Samsung Personal Access Token | `00000000-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `SMARTTHINGS_DEVICE_ID` | Target AC device UUID | `ee2f1cab-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |

### 2.2 Where to Define Them

Create or append to a `.env` file in the project root (this file MUST be in `.gitignore`):

```env
# .env — never commit this file
SMARTTHINGS_PAT=your_pat_here
SMARTTHINGS_DEVICE_ID=your_device_id_here
```

Verify `.gitignore` contains:
```
.env
*.env
```

### 2.3 Loading Strategy

Jarvis must load these via `python-dotenv` at startup. In `config.py`, add:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env into os.environ

SMARTTHINGS_PAT = os.environ.get("SMARTTHINGS_PAT")
SMARTTHINGS_DEVICE_ID = os.environ.get("SMARTTHINGS_DEVICE_ID")

# Validate at boot — hard fail early, not at runtime inside a voice command
if not SMARTTHINGS_PAT:
    raise EnvironmentError(
        "[Jarvis/Config] SMARTTHINGS_PAT is not set. "
        "Add it to your .env file or export it in your shell."
    )
if not SMARTTHINGS_DEVICE_ID:
    raise EnvironmentError(
        "[Jarvis/Config] SMARTTHINGS_DEVICE_ID is not set. "
        "Add it to your .env file or export it in your shell."
    )
```

---

## 3. FILE: `modules/smartthings.py` — THE HARDWARE MANAGER

This is the lowest layer. It owns all HTTP communication with the SmartThings REST API. Nothing else in Jarvis talks to the API directly — everything goes through this class.

### 3.1 Full Source Code

```python
"""
modules/smartthings.py
─────────────────────
Native Python SmartThings hardware manager for Jarvis.
Wraps the Samsung SmartThings REST API v1.
All methods are synchronous (requests-based) to match Jarvis's architecture.
"""

import logging
import requests
from config import SMARTTHINGS_PAT, SMARTTHINGS_DEVICE_ID

logger = logging.getLogger("jarvis.smartthings")

# ── Constants ────────────────────────────────────────────────────────────────

BASE_URL = "https://api.smartthings.com/v1"
DEFAULT_TIMEOUT_SECONDS = 8

VALID_MODES = {"cool", "heat", "auto", "dry", "wind", "fanOnly"}
TEMP_MIN_C = 16
TEMP_MAX_C = 30

# ── Exception Types ───────────────────────────────────────────────────────────

class SmartThingsError(Exception):
    """Base exception for all SmartThings failures."""
    pass

class SmartThingsAuthError(SmartThingsError):
    """Raised on 401/403 responses — bad or expired PAT."""
    pass

class SmartThingsDeviceError(SmartThingsError):
    """Raised on 404 — device not found or wrong DEVICE_ID."""
    pass

class SmartThingsAPIError(SmartThingsError):
    """Raised on 5xx or unexpected non-2xx responses."""
    pass


# ── Manager Class ─────────────────────────────────────────────────────────────

class SmartThingsManager:
    """
    Controls a Samsung AC unit via the SmartThings REST API.

    Usage:
        st = SmartThingsManager()
        st.turn_on()
        st.set_temperature(22)
        st.set_mode("cool")
        st.turn_off()
    """

    def __init__(self, pat: str = None, device_id: str = None):
        self.pat = pat or SMARTTHINGS_PAT
        self.device_id = device_id or SMARTTHINGS_DEVICE_ID
        self.base_headers = {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json",
        }
        self.device_url = f"{BASE_URL}/devices/{self.device_id}/commands"
        self.status_url = f"{BASE_URL}/devices/{self.device_id}/status"
        logger.info(
            "[SmartThings] Manager initialised. Device: %s",
            self.device_id[:8] + "..." if self.device_id else "UNSET",
        )

    # ── Private HTTP Helpers ─────────────────────────────────────────────────

    def _post_command(self, commands: list) -> dict:
        """
        POST a list of SmartThings command objects to the device endpoint.
        Returns the parsed JSON response body.
        Raises SmartThingsError subclasses on failure.
        """
        payload = {"commands": commands}
        logger.debug("[SmartThings] POST %s | payload: %s", self.device_url, payload)
        try:
            response = requests.post(
                self.device_url,
                json=payload,
                headers=self.base_headers,
                timeout=DEFAULT_TIMEOUT_SECONDS,
            )
        except requests.exceptions.Timeout:
            raise SmartThingsError(
                f"[SmartThings] Request timed out after {DEFAULT_TIMEOUT_SECONDS}s. "
                "Check your internet connection."
            )
        except requests.exceptions.ConnectionError as e:
            raise SmartThingsError(
                f"[SmartThings] Connection failed: {e}. "
                "SmartThings API may be unreachable."
            )

        self._raise_for_status(response)
        logger.info("[SmartThings] Command succeeded. HTTP %s", response.status_code)
        return response.json()

    def _raise_for_status(self, response: requests.Response) -> None:
        """Map HTTP error codes to typed exceptions."""
        code = response.status_code
        if 200 <= code < 300:
            return
        if code == 401:
            raise SmartThingsAuthError(
                "[SmartThings] HTTP 401 — PAT is invalid or expired. "
                "Regenerate it at https://account.smartthings.com/tokens"
            )
        if code == 403:
            raise SmartThingsAuthError(
                "[SmartThings] HTTP 403 — PAT does not have permission for this device."
            )
        if code == 404:
            raise SmartThingsDeviceError(
                f"[SmartThings] HTTP 404 — Device '{self.device_id}' not found. "
                "Verify SMARTTHINGS_DEVICE_ID is correct."
            )
        if code == 429:
            raise SmartThingsAPIError(
                "[SmartThings] HTTP 429 — Rate limited. Wait 60 seconds and retry."
            )
        raise SmartThingsAPIError(
            f"[SmartThings] HTTP {code} — Unexpected error. Body: {response.text[:200]}"
        )

    # ── Public API ───────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """
        Fetch and return the full device status dict from SmartThings.
        Useful for verification scripts and debug logging.
        Returns a dict like:
            {
              "switch": "on",
              "temperature": 24,
              "coolingSetpoint": 22,
              "airConditionerMode": "cool",
              "fanMode": "auto"
            }
        """
        logger.debug("[SmartThings] GET device status: %s", self.status_url)
        try:
            response = requests.get(
                self.status_url,
                headers=self.base_headers,
                timeout=DEFAULT_TIMEOUT_SECONDS,
            )
        except requests.exceptions.Timeout:
            raise SmartThingsError("[SmartThings] Status request timed out.")
        except requests.exceptions.ConnectionError as e:
            raise SmartThingsError(f"[SmartThings] Connection failed: {e}")

        self._raise_for_status(response)
        raw = response.json()

        # Parse the nested SmartThings status structure into a flat dict
        components = raw.get("components", {}).get("main", {})
        status = {
            "switch": components.get("switch", {}).get("switch", {}).get("value", "unknown"),
            "temperature": components.get("temperatureMeasurement", {})
                                      .get("temperature", {}).get("value"),
            "coolingSetpoint": components.get("thermostatCoolingSetpoint", {})
                                          .get("coolingSetpoint", {}).get("value"),
            "airConditionerMode": components.get("airConditionerMode", {})
                                             .get("airConditionerMode", {}).get("value"),
        }
        logger.info("[SmartThings] Status: %s", status)
        return status

    def turn_on(self) -> dict:
        """
        Power on the AC unit.
        SmartThings capability: switch → on
        """
        logger.info("[SmartThings] Turning AC ON.")
        return self._post_command([
            {
                "component": "main",
                "capability": "switch",
                "command": "on",
            }
        ])

    def turn_off(self) -> dict:
        """
        Power off the AC unit.
        SmartThings capability: switch → off
        """
        logger.info("[SmartThings] Turning AC OFF.")
        return self._post_command([
            {
                "component": "main",
                "capability": "switch",
                "command": "off",
            }
        ])

    def set_temperature(self, celsius: float) -> dict:
        """
        Set the cooling setpoint in degrees Celsius.
        Valid range: TEMP_MIN_C (16) to TEMP_MAX_C (30).
        Raises ValueError for out-of-range values.
        SmartThings capability: thermostatCoolingSetpoint → setCoolingSetpoint
        """
        celsius = float(celsius)
        if not (TEMP_MIN_C <= celsius <= TEMP_MAX_C):
            raise ValueError(
                f"[SmartThings] Temperature {celsius}°C is out of valid range "
                f"[{TEMP_MIN_C}, {TEMP_MAX_C}]."
            )
        logger.info("[SmartThings] Setting temperature to %.1f°C.", celsius)
        return self._post_command([
            {
                "component": "main",
                "capability": "thermostatCoolingSetpoint",
                "command": "setCoolingSetpoint",
                "arguments": [celsius],
            }
        ])

    def set_mode(self, mode: str) -> dict:
        """
        Set the AC operating mode.
        Valid modes: cool, heat, auto, dry, wind, fanOnly
        SmartThings capability: airConditionerMode → setAirConditionerMode
        """
        mode = mode.lower().strip()
        if mode not in VALID_MODES:
            raise ValueError(
                f"[SmartThings] Invalid mode '{mode}'. "
                f"Valid options are: {', '.join(sorted(VALID_MODES))}"
            )
        logger.info("[SmartThings] Setting AC mode to '%s'.", mode)
        return self._post_command([
            {
                "component": "main",
                "capability": "airConditionerMode",
                "command": "setAirConditionerMode",
                "arguments": [mode],
            }
        ])

    def set_fan_mode(self, fan_mode: str) -> dict:
        """
        Set the fan speed/mode.
        Common values: auto, low, medium, high, turbo
        SmartThings capability: airConditionerFanMode → setFanMode
        """
        fan_mode = fan_mode.lower().strip()
        logger.info("[SmartThings] Setting fan mode to '%s'.", fan_mode)
        return self._post_command([
            {
                "component": "main",
                "capability": "airConditionerFanMode",
                "command": "setFanMode",
                "arguments": [fan_mode],
            }
        ])
```

---

## 4. FILE: `modules/skills/smartthings_skill.py` — ZERO-LATENCY VOICE SKILL

This skill layer sits in the priority chain **before** anything is sent to the Groq LLM. If user input matches a registered phrase, Jarvis executes immediately without an LLM round-trip.

### 4.1 Design Philosophy

- **Pattern matching is fuzzy.** The user might say "AC on", "turn on the ac", "switch on ac". All should match.
- **Temperature extraction is regex-based.** "set it to 22", "make it 22 degrees", "22 celsius" — all must extract `22`.
- **Each pattern has a canonical intent.** The skill normalises to one of five intents: `AC_ON`, `AC_OFF`, `SET_TEMP`, `SET_MODE`, `AC_STATUS`.
- **Logging is mandatory.** Every match and every execution must be logged so the routing chain is traceable.

### 4.2 Full Source Code

```python
"""
modules/skills/smartthings_skill.py
────────────────────────────────────
Zero-latency SmartThings AC skill for Jarvis.
Registered as a high-priority pre-LLM skill.

Supports the following intents via fuzzy phrase matching:
  AC_ON      — "turn on the ac", "switch on ac", "ac on", etc.
  AC_OFF     — "turn off the ac", "ac off", etc.
  SET_TEMP   — "set ac to 22 degrees", "22 celsius", "make it 22", etc.
  SET_MODE   — "set ac to cool mode", "ac on heat mode", etc.
  AC_STATUS  — "ac status", "is the ac on", "what's the temperature", etc.
"""

import re
import logging
from modules.smartthings import SmartThingsManager, SmartThingsError

logger = logging.getLogger("jarvis.skill.smartthings")

# ── Intent Constants ──────────────────────────────────────────────────────────

INTENT_AC_ON     = "AC_ON"
INTENT_AC_OFF    = "AC_OFF"
INTENT_SET_TEMP  = "SET_TEMP"
INTENT_SET_MODE  = "SET_MODE"
INTENT_AC_STATUS = "AC_STATUS"

# ── Pattern Registry ──────────────────────────────────────────────────────────
# Each entry: (intent, compiled_regex_pattern)
# The patterns are checked in order. First match wins.
# NOTE: All patterns operate on lowercased, stripped input.

PATTERNS = [
    # AC_ON — must come before AC_OFF to avoid partial matches
    (INTENT_AC_ON, re.compile(
        r"\b(turn\s+on|switch\s+on|power\s+on|start|enable|activate)\s*(the\s+)?(ac|air\s*con(dition(er|ing)?)?|hvac|cooling)\b"
        r"|\b(ac|air\s*con(dition(er|ing)?)?)\s+(on|start)\b"
        r"|\b(it's|its|it is|its getting)\s+(hot|warm|stuffy)\b"
        r"|\bmake\s+it\s+cool(er)?\b",
        re.IGNORECASE
    )),

    # AC_OFF
    (INTENT_AC_OFF, re.compile(
        r"\b(turn\s+off|switch\s+off|power\s+off|stop|disable|shut\s+down)\s*(the\s+)?(ac|air\s*con(dition(er|ing)?)?|hvac|cooling)\b"
        r"|\b(ac|air\s*con(dition(er|ing)?)?)\s+(off|stop)\b"
        r"|\b(it's|its|it is)\s+(cold|freezing|too\s+cold)\b",
        re.IGNORECASE
    )),

    # SET_TEMP — extracts the degree value into group 'temp'
    (INTENT_SET_TEMP, re.compile(
        r"\b(set|change|put|make)\s*(the\s+)?(ac|air\s*con(dition(er|ing)?)?|temperature|temp|it)\s*(to|at)?\s*(?P<temp>\d{1,2}(\.\d)?)\s*(degrees?|celsius|°c|°)?\b"
        r"|\b(?P<temp2>\d{1,2}(\.\d)?)\s*(degrees?|celsius|°c|°)\b"
        r"|\bmake\s+it\s+(?P<temp3>\d{1,2}(\.\d)?)\b",
        re.IGNORECASE
    )),

    # SET_MODE — extracts mode into group 'mode'
    (INTENT_SET_MODE, re.compile(
        r"\b(set|switch|change|put)\s*(the\s+)?(ac|air\s*con(dition(er|ing)?)?)?\s*(to\s+|on\s+|in\s+)?(?P<mode>cool(ing)?|heat(ing)?|auto|dry|fan\s*only|wind)\s*(mode)?\b",
        re.IGNORECASE
    )),

    # AC_STATUS
    (INTENT_AC_STATUS, re.compile(
        r"\b(ac|air\s*con(dition(er|ing)?)?)\s*(status|state|on|off)?\b"
        r"|\b(is\s+the\s+(ac|air\s*con(dition(er|ing)?)?)\s+(on|off|running))\b"
        r"|\b(what('s|s| is)\s+the\s+(room\s+)?temperature)\b",
        re.IGNORECASE
    )),
]

# Mode normalisation table — maps user-facing variants to SmartThings API values
MODE_NORMALISE = {
    "cooling": "cool",
    "heating": "heat",
    "fan only": "fanOnly",
    "fan_only": "fanOnly",
}

# ── Skill Class ───────────────────────────────────────────────────────────────

class SmartThingsSkill:
    """
    Jarvis pre-LLM skill for SmartThings AC control.

    Lifecycle:
      1. Jarvis calls skill.matches(user_input) during routing.
      2. If True, Jarvis calls skill.execute(user_input) to run the command.
      3. execute() returns a plain-English response string for TTS.
    """

    SKILL_NAME = "SmartThingsSkill"
    PRIORITY = 10  # Lower number = higher priority in Jarvis skill chain

    def __init__(self, manager: SmartThingsManager = None):
        self._manager = manager or SmartThingsManager()
        logger.info("[SmartThingsSkill] Initialised with manager %s", self._manager)

    # ── Public Interface ─────────────────────────────────────────────────────

    def matches(self, user_input: str) -> bool:
        """
        Returns True if this skill can handle the given user input.
        Does NOT execute anything — purely a routing decision.
        """
        intent, _ = self._detect_intent(user_input)
        matched = intent is not None
        if matched:
            logger.debug("[SmartThingsSkill] Matched intent '%s' for input: '%s'", intent, user_input[:60])
        return matched

    def execute(self, user_input: str) -> str:
        """
        Execute the appropriate SmartThings command.
        Returns a plain-English string for Jarvis TTS output.
        Raises SmartThingsError if the API call fails.
        """
        intent, match = self._detect_intent(user_input)
        logger.info("[SmartThingsSkill] Executing intent '%s'", intent)

        try:
            if intent == INTENT_AC_ON:
                return self._handle_on()

            elif intent == INTENT_AC_OFF:
                return self._handle_off()

            elif intent == INTENT_SET_TEMP:
                return self._handle_set_temp(match)

            elif intent == INTENT_SET_MODE:
                return self._handle_set_mode(match)

            elif intent == INTENT_AC_STATUS:
                return self._handle_status()

            else:
                return "I couldn't determine what you wanted to do with the AC."

        except ValueError as e:
            logger.warning("[SmartThingsSkill] Validation error: %s", e)
            return f"I couldn't do that — {str(e)}"

        except SmartThingsError as e:
            logger.error("[SmartThingsSkill] SmartThings API error: %s", e)
            return f"There was a problem communicating with your AC. {str(e)}"

    # ── Intent Detection ─────────────────────────────────────────────────────

    def _detect_intent(self, user_input: str):
        """
        Scan all PATTERNS and return (intent_string, re.Match) for the first match.
        Returns (None, None) if nothing matches.
        """
        cleaned = user_input.strip().lower()
        for intent, pattern in PATTERNS:
            match = pattern.search(cleaned)
            if match:
                return intent, match
        return None, None

    # ── Intent Handlers ──────────────────────────────────────────────────────

    def _handle_on(self) -> str:
        self._manager.turn_on()
        logger.info("[SmartThingsSkill] AC turned ON.")
        return "Done. The AC is on."

    def _handle_off(self) -> str:
        self._manager.turn_off()
        logger.info("[SmartThingsSkill] AC turned OFF.")
        return "Done. The AC is off."

    def _handle_set_temp(self, match) -> str:
        # Try named groups in priority order
        raw_temp = (
            match.group("temp") or
            match.group("temp2") or
            match.group("temp3")
        )
        if not raw_temp:
            return "I heard a temperature command but couldn't extract the degrees. Please say something like 'set AC to 22 degrees'."

        celsius = float(raw_temp)
        self._manager.set_temperature(celsius)
        logger.info("[SmartThingsSkill] Set temperature to %.1f°C.", celsius)
        return f"Done. The AC is set to {celsius:.0f} degrees Celsius."

    def _handle_set_mode(self, match) -> str:
        raw_mode = match.group("mode")
        if not raw_mode:
            return "I heard a mode command but couldn't extract the mode. Try 'set AC to cool mode'."

        mode = raw_mode.lower().strip()
        mode = MODE_NORMALISE.get(mode, mode)  # normalise variants
        self._manager.set_mode(mode)
        logger.info("[SmartThingsSkill] Set mode to '%s'.", mode)
        return f"Done. The AC is now in {mode} mode."

    def _handle_status(self) -> str:
        status = self._manager.get_status()
        switch_state = status.get("switch", "unknown")
        temp = status.get("temperature")
        setpoint = status.get("coolingSetpoint")
        mode = status.get("airConditionerMode", "unknown")

        parts = [f"The AC is currently {switch_state}."]
        if temp is not None:
            parts.append(f"Room temperature is {temp} degrees.")
        if setpoint is not None:
            parts.append(f"The setpoint is {setpoint} degrees.")
        parts.append(f"Mode is {mode}.")
        return " ".join(parts)
```

---

## 5. FILE: `config.py` — MODIFICATIONS

Locate the existing `config.py`. Add the following block. If a `load_dotenv()` call already exists, do not add it again — just add the variable definitions.

### 5.1 Lines to Add

Find the imports section at the top of `config.py` and add (if not present):

```python
import os
from dotenv import load_dotenv

load_dotenv()
```

Then, in the configuration section (near other API key definitions), add:

```python
# ── SmartThings Configuration ─────────────────────────────────────────────────
SMARTTHINGS_PAT = os.environ.get("SMARTTHINGS_PAT")
SMARTTHINGS_DEVICE_ID = os.environ.get("SMARTTHINGS_DEVICE_ID")

# Boot validation — fail fast if secrets are missing
_missing = [k for k, v in {
    "SMARTTHINGS_PAT": SMARTTHINGS_PAT,
    "SMARTTHINGS_DEVICE_ID": SMARTTHINGS_DEVICE_ID,
}.items() if not v]

if _missing:
    import warnings
    warnings.warn(
        f"[Jarvis/Config] SmartThings secrets not set: {', '.join(_missing)}. "
        "AC control will be unavailable until these are configured.",
        RuntimeWarning,
        stacklevel=2,
    )
```

> **Note:** A `warnings.warn` is used instead of a hard `raise` so that Jarvis can still start if only some modules are missing — the hard `raise` pattern in Section 2.3 is for a fresh install with a dedicated `config.py`. Choose the approach that matches your existing architecture.

---

## 6. FILE: `modules/commands.py` — MODIFICATIONS

This section covers three modifications to `commands.py`:

### 6.1 Modification A — Import SmartThingsSkill and inject into the skill priority chain

Find the block at the top of `commands.py` where other skills are imported. Add:

```python
from modules.skills.smartthings_skill import SmartThingsSkill
```

Find where the skill chain / skill registry is assembled (look for a list like `SKILLS = [...]` or `skill_chain = [...]`). Add `SmartThingsSkill` at position 0 (or wherever PRIORITY=10 would rank it relative to existing skills):

```python
SKILLS = [
    SmartThingsSkill(),   # ← ADD THIS — priority 10, handles all AC commands
    # ... existing skills below ...
]
```

If Jarvis uses a different skill registration mechanism (e.g., `register_skill()`), call:

```python
skill_registry.register(SmartThingsSkill(), priority=10)
```

### 6.2 Modification B — Register ACControlTool in the Agentic ToolsRegistry

Find the section where LLM tools are defined (likely a list of tool dicts in the format expected by Groq). Add the following tool definition:

```python
AC_CONTROL_TOOL = {
    "type": "function",
    "function": {
        "name": "control_ac",
        "description": (
            "Controls the Samsung air conditioner in the user's room via SmartThings. "
            "Use this when the user wants to turn the AC on or off, change the temperature, "
            "change the AC mode, or check the AC status. "
            "Do NOT use this for general music, timers, or unrelated requests."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["turn_on", "turn_off", "set_temperature", "set_mode", "get_status"],
                    "description": "The AC action to perform.",
                },
                "temperature_celsius": {
                    "type": "number",
                    "description": "The target temperature in Celsius (16–30). Required only when action is 'set_temperature'.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["cool", "heat", "auto", "dry", "wind", "fanOnly"],
                    "description": "The AC mode. Required only when action is 'set_mode'.",
                },
            },
            "required": ["action"],
        },
    },
}
```

Find the list of tools passed to the Groq API call (e.g., `tools=[...]`) and add `AC_CONTROL_TOOL`:

```python
tools = [
    AC_CONTROL_TOOL,
    # ... existing tools ...
]
```

### 6.3 Modification C — Tool call execution handler

Find the section in `commands.py` that handles LLM tool call responses (the block that inspects `tool_calls` from the Groq response and dispatches to the correct function). Add a handler for `control_ac`:

```python
import json
from modules.smartthings import SmartThingsManager, SmartThingsError

_smartthings_manager = SmartThingsManager()  # singleton, instantiated once

def _execute_ac_tool(tool_args: dict) -> str:
    """
    Executes a SmartThings AC tool call dispatched from the Groq agentic loop.
    tool_args: parsed dict from the LLM tool_call arguments JSON.
    Returns a plain-English result string to be fed back into the conversation.
    """
    action = tool_args.get("action")
    logger.info("[commands] Executing AC tool: action='%s'", action)

    try:
        if action == "turn_on":
            _smartthings_manager.turn_on()
            return "The AC has been turned on."

        elif action == "turn_off":
            _smartthings_manager.turn_off()
            return "The AC has been turned off."

        elif action == "set_temperature":
            temp = tool_args.get("temperature_celsius")
            if temp is None:
                return "I needed a temperature value but didn't receive one."
            _smartthings_manager.set_temperature(float(temp))
            return f"The AC temperature has been set to {temp}°C."

        elif action == "set_mode":
            mode = tool_args.get("mode")
            if not mode:
                return "I needed a mode value but didn't receive one."
            _smartthings_manager.set_mode(mode)
            return f"The AC mode has been set to {mode}."

        elif action == "get_status":
            status = _smartthings_manager.get_status()
            return (
                f"AC is {status.get('switch', 'unknown')}. "
                f"Room temp: {status.get('temperature', 'N/A')}°C. "
                f"Setpoint: {status.get('coolingSetpoint', 'N/A')}°C. "
                f"Mode: {status.get('airConditionerMode', 'unknown')}."
            )

        else:
            return f"Unknown AC action: '{action}'."

    except ValueError as e:
        return f"Validation error: {e}"
    except SmartThingsError as e:
        return f"AC control failed: {e}"


# In your tool_call dispatch block, add:
# if tool_call.function.name == "control_ac":
#     args = json.loads(tool_call.function.arguments)
#     result = _execute_ac_tool(args)
```

### 6.4 Modification D — Regex pre-router for AC synonyms (if `_regex_pre_route` exists)

If `commands.py` has a function like `_regex_pre_route(text)` that maps input to intents before skills run, add these patterns:

```python
# AC synonyms for pre-router — these bridge informal phrasing to the skill layer
AC_REGEX_HOOKS = [
    (re.compile(r"\b(it'?s?\s+(hot|warm|stuffy)|make\s+it\s+cool(er)?)\b", re.I), "AC_ON"),
    (re.compile(r"\b(it'?s?\s+(cold|freezing|too\s+cold))\b", re.I), "AC_OFF"),
    (re.compile(r"\b(ac|air\s*con(dition(er|ing)?)?)\b", re.I), "AC_COMMAND"),
]
```

These hooks do not execute anything — they hint to the router that the SmartThingsSkill should be tried next.

---

## 7. FILE: `scripts/verify_smartthings.py` — STANDALONE VERIFICATION SCRIPT

This script is a standalone diagnostic. Run it directly to verify the credentials and device before testing Jarvis end-to-end.

### 7.1 Full Source Code

```python
"""
scripts/verify_smartthings.py
──────────────────────────────
Standalone SmartThings connectivity verification.
Run directly: python scripts/verify_smartthings.py

Verifies:
  1. Environment variables are set.
  2. API returns HTTP 200 for a status request.
  3. Device is reachable and returns a parseable state.

Does NOT turn the AC on or off — read-only.
"""

import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

import json
import requests

PAT = os.environ.get("SMARTTHINGS_PAT")
DEVICE_ID = os.environ.get("SMARTTHINGS_DEVICE_ID")

BASE_URL = "https://api.smartthings.com/v1"

def main():
    print("=" * 60)
    print("SmartThings Verification Script")
    print("=" * 60)

    # Step 1 — Check secrets
    print("\n[1] Checking environment variables...")
    errors = []
    if not PAT:
        errors.append("  ✗ SMARTTHINGS_PAT is not set.")
    else:
        print(f"  ✓ SMARTTHINGS_PAT found ({PAT[:8]}...)")
    if not DEVICE_ID:
        errors.append("  ✗ SMARTTHINGS_DEVICE_ID is not set.")
    else:
        print(f"  ✓ SMARTTHINGS_DEVICE_ID found ({DEVICE_ID[:8]}...)")

    if errors:
        for e in errors:
            print(e)
        print("\n[FAIL] Set missing secrets in your .env file and re-run.")
        sys.exit(1)

    # Step 2 — Ping device status endpoint
    print("\n[2] Pinging SmartThings API...")
    url = f"{BASE_URL}/devices/{DEVICE_ID}/status"
    headers = {"Authorization": f"Bearer {PAT}", "Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.ConnectionError:
        print("  ✗ Connection failed. Check your internet connection.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("  ✗ Request timed out after 10 seconds.")
        sys.exit(1)

    print(f"  HTTP Status: {response.status_code}")

    if response.status_code == 200:
        print("  ✓ HTTP 200 OK — API is reachable and credentials are valid.")
    elif response.status_code == 401:
        print("  ✗ HTTP 401 — Invalid PAT. Regenerate at https://account.smartthings.com/tokens")
        sys.exit(1)
    elif response.status_code == 403:
        print("  ✗ HTTP 403 — PAT lacks permission for this device.")
        sys.exit(1)
    elif response.status_code == 404:
        print("  ✗ HTTP 404 — Device not found. Verify SMARTTHINGS_DEVICE_ID.")
        sys.exit(1)
    else:
        print(f"  ✗ Unexpected HTTP {response.status_code}: {response.text[:200]}")
        sys.exit(1)

    # Step 3 — Parse and display device state
    print("\n[3] Parsing device state...")
    try:
        raw = response.json()
        components = raw.get("components", {}).get("main", {})
        switch = components.get("switch", {}).get("switch", {}).get("value", "unknown")
        temp = components.get("temperatureMeasurement", {}).get("temperature", {}).get("value", "N/A")
        setpoint = components.get("thermostatCoolingSetpoint", {}).get("coolingSetpoint", {}).get("value", "N/A")
        mode = components.get("airConditionerMode", {}).get("airConditionerMode", {}).get("value", "unknown")

        print(f"  AC Power   : {switch}")
        print(f"  Room Temp  : {temp}°C")
        print(f"  Setpoint   : {setpoint}°C")
        print(f"  Mode       : {mode}")
        print("\n[PASS] SmartThings is fully operational. Jarvis integration is ready.")

    except (KeyError, json.JSONDecodeError) as e:
        print(f"  ✗ Failed to parse response: {e}")
        print(f"  Raw body: {response.text[:300]}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 8. FILE: `tests/test_smartthings.py` — UNIT TESTS

```python
"""
tests/test_smartthings.py
──────────────────────────
Unit tests for SmartThingsManager and SmartThingsSkill.
Uses unittest.mock to avoid real HTTP calls.
Run with: python -m pytest tests/test_smartthings.py -v
"""

import pytest
from unittest.mock import MagicMock, patch
from modules.smartthings import (
    SmartThingsManager,
    SmartThingsAuthError,
    SmartThingsDeviceError,
    SmartThingsAPIError,
    SmartThingsError,
)
from modules.skills.smartthings_skill import SmartThingsSkill

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_manager():
    manager = MagicMock(spec=SmartThingsManager)
    manager.turn_on.return_value = {"results": [{"id": "main", "status": "ACCEPTED"}]}
    manager.turn_off.return_value = {"results": [{"id": "main", "status": "ACCEPTED"}]}
    manager.set_temperature.return_value = {"results": [{"id": "main", "status": "ACCEPTED"}]}
    manager.set_mode.return_value = {"results": [{"id": "main", "status": "ACCEPTED"}]}
    manager.get_status.return_value = {
        "switch": "on",
        "temperature": 27.0,
        "coolingSetpoint": 22.0,
        "airConditionerMode": "cool",
    }
    return manager

@pytest.fixture
def skill(mock_manager):
    return SmartThingsSkill(manager=mock_manager)

# ── SmartThingsSkill.matches() ────────────────────────────────────────────────

class TestSkillMatching:
    @pytest.mark.parametrize("phrase", [
        "turn on the ac",
        "turn on the air conditioner",
        "switch on AC",
        "ac on",
        "it's hot",
        "make it cooler",
        "its getting warm",
    ])
    def test_ac_on_matches(self, skill, phrase):
        assert skill.matches(phrase), f"Should match AC_ON for: '{phrase}'"

    @pytest.mark.parametrize("phrase", [
        "turn off the ac",
        "switch off ac",
        "ac off",
        "it's freezing",
        "it's too cold",
    ])
    def test_ac_off_matches(self, skill, phrase):
        assert skill.matches(phrase), f"Should match AC_OFF for: '{phrase}'"

    @pytest.mark.parametrize("phrase", [
        "set ac to 22 degrees",
        "set the temperature to 24",
        "make it 20 celsius",
        "22 degrees please",
    ])
    def test_set_temp_matches(self, skill, phrase):
        assert skill.matches(phrase), f"Should match SET_TEMP for: '{phrase}'"

    @pytest.mark.parametrize("phrase", [
        "set ac to cool mode",
        "switch to heat mode",
        "change to auto",
        "set ac to dry",
    ])
    def test_set_mode_matches(self, skill, phrase):
        assert skill.matches(phrase), f"Should match SET_MODE for: '{phrase}'"

    @pytest.mark.parametrize("phrase", [
        "what time is it",
        "play some music",
        "set a timer for 10 minutes",
        "hello jarvis",
    ])
    def test_non_ac_does_not_match(self, skill, phrase):
        assert not skill.matches(phrase), f"Should NOT match for: '{phrase}'"

# ── SmartThingsSkill.execute() ────────────────────────────────────────────────

class TestSkillExecution:
    def test_execute_ac_on(self, skill, mock_manager):
        result = skill.execute("turn on the ac")
        mock_manager.turn_on.assert_called_once()
        assert "on" in result.lower()

    def test_execute_ac_off(self, skill, mock_manager):
        result = skill.execute("turn off the ac")
        mock_manager.turn_off.assert_called_once()
        assert "off" in result.lower()

    def test_execute_set_temp(self, skill, mock_manager):
        result = skill.execute("set ac to 22 degrees")
        mock_manager.set_temperature.assert_called_once_with(22.0)
        assert "22" in result

    def test_execute_set_mode_cool(self, skill, mock_manager):
        result = skill.execute("set ac to cool mode")
        mock_manager.set_mode.assert_called_once_with("cool")
        assert "cool" in result.lower()

    def test_execute_status(self, skill, mock_manager):
        result = skill.execute("ac status")
        mock_manager.get_status.assert_called_once()
        assert "on" in result.lower()
        assert "27" in result or "22" in result

    def test_api_error_returns_graceful_message(self, skill, mock_manager):
        mock_manager.turn_on.side_effect = SmartThingsError("Connection failed")
        result = skill.execute("turn on the ac")
        assert "problem" in result.lower() or "failed" in result.lower()

# ── SmartThingsManager HTTP error mapping ─────────────────────────────────────

class TestManagerErrorMapping:
    @patch("modules.smartthings.requests.post")
    def test_401_raises_auth_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        manager = SmartThingsManager(pat="fake", device_id="fake-device")
        with pytest.raises(SmartThingsAuthError):
            manager.turn_on()

    @patch("modules.smartthings.requests.post")
    def test_404_raises_device_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response
        manager = SmartThingsManager(pat="fake", device_id="fake-device")
        with pytest.raises(SmartThingsDeviceError):
            manager.turn_on()

    @patch("modules.smartthings.requests.post")
    def test_temperature_out_of_range_raises_value_error(self, mock_post):
        manager = SmartThingsManager(pat="fake", device_id="fake-device")
        with pytest.raises(ValueError):
            manager.set_temperature(5)   # Below TEMP_MIN_C
        with pytest.raises(ValueError):
            manager.set_temperature(50)  # Above TEMP_MAX_C

    @patch("modules.smartthings.requests.post")
    def test_invalid_mode_raises_value_error(self, mock_post):
        manager = SmartThingsManager(pat="fake", device_id="fake-device")
        with pytest.raises(ValueError):
            manager.set_mode("turbo_nuclear_blast")
```

---

## 9. DEPENDENCY REQUIREMENTS

Add these to `requirements.txt` (or `pyproject.toml`) if not already present:

```
requests>=2.31.0
python-dotenv>=1.0.0
pytest>=7.4.0
```

Install:
```bash
pip install requests python-dotenv pytest
```

---

## 10. VERIFICATION PROTOCOL — STEP BY STEP

### Step 1 — Environment Setup
```bash
# Copy the template and fill in your credentials
cp .env.example .env
# Then open .env and set SMARTTHINGS_PAT and SMARTTHINGS_DEVICE_ID
```

### Step 2 — Run the Standalone Verification Script
```bash
python scripts/verify_smartthings.py
```
**Expected output:**
```
[1] Checking environment variables...
  ✓ SMARTTHINGS_PAT found (00000000...)
  ✓ SMARTTHINGS_DEVICE_ID found (ee2f1cab...)
[2] Pinging SmartThings API...
  HTTP Status: 200
  ✓ HTTP 200 OK — API is reachable and credentials are valid.
[3] Parsing device state...
  AC Power   : off
  Room Temp  : 28.5°C
  Setpoint   : 22.0°C
  Mode       : cool
[PASS] SmartThings is fully operational. Jarvis integration is ready.
```

### Step 3 — Run Unit Tests
```bash
python -m pytest tests/test_smartthings.py -v
```
All tests should pass with no real HTTP calls made.

### Step 4 — Live Integration Test via Jarvis Terminal
Start Jarvis in terminal input mode and issue the following commands one at a time. After each, observe the log output.

| Input | Expected Log | Expected TTS Response |
|---|---|---|
| `"turn on the ac"` | `[SmartThingsSkill] Executing intent 'AC_ON'` | "Done. The AC is on." |
| `"set ac to 22 degrees"` | `[SmartThingsSkill] Executing intent 'SET_TEMP'` | "Done. The AC is set to 22 degrees Celsius." |
| `"set ac to cool mode"` | `[SmartThingsSkill] Executing intent 'SET_MODE'` | "Done. The AC is now in cool mode." |
| `"ac status"` | `[SmartThingsSkill] Executing intent 'AC_STATUS'` | (reads back current device state) |
| `"turn off the ac"` | `[SmartThingsSkill] Executing intent 'AC_OFF'` | "Done. The AC is off." |

### Step 5 — Agentic Test (Multi-Intent LLM Path)
Input: `"I'm feeling hot and sad, play some upbeat music and cool down the room"`

Expected behaviour:
1. This input does NOT match the SmartThingsSkill directly (it contains both music and AC intents).
2. It falls through to the Groq LLM with `AC_CONTROL_TOOL` available.
3. The LLM issues two tool calls: one for music, one for `control_ac` with `action: "turn_on"`.
4. Log shows `[commands] Executing AC tool: action='turn_on'`.
5. Both music and AC execute.

---

## 11. LOGGING CONFIGURATION REFERENCE

To enable full debug logging for SmartThings in Jarvis, add to your logging config:

```python
import logging
logging.getLogger("jarvis.smartthings").setLevel(logging.DEBUG)
logging.getLogger("jarvis.skill.smartthings").setLevel(logging.DEBUG)
```

In production, set to `logging.INFO` to reduce verbosity.

---

## 12. SECURITY CHECKLIST

Before pushing to GitHub, verify:

- [ ] `.env` is listed in `.gitignore`
- [ ] No PAT or Device ID appears in any `.py` file as a string literal
- [ ] `SMARTTHINGS_PAT` and `SMARTTHINGS_DEVICE_ID` are loaded exclusively via `os.environ.get()`
- [ ] The verification script does not print the full PAT (only the first 8 characters)
- [ ] No credential appears in any test fixture — tests use `"fake"` placeholder strings

---

## 13. FUTURE EXTENSIONS (OUT OF SCOPE FOR THIS SPRINT)

These are intentionally deferred but the architecture above supports them without refactoring:

- **Scheduling:** "Turn off the AC in 2 hours" — add a `schedule_command(delay_seconds, fn)` utility to `SmartThingsManager`.
- **Multiple AC units:** `SmartThingsManager` already accepts `device_id` as a constructor arg — add a `device_registry` dict in `config.py` mapping room names to device IDs.
- **Temperature-based triggers:** "If the room goes above 28 degrees, turn on the AC" — requires a polling loop or SmartThings webhook; outside scope here.
- **Voice feedback with current temp:** `get_status()` is already implemented — wire it into the turn_on response: "Done. AC is on. Room is currently 28 degrees."

---

*End of specification. Every section above is immediately actionable.*
