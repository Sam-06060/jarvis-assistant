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
