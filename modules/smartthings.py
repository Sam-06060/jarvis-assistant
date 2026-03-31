"""
modules/smartthings.py
─────────────────────
Native Python SmartThings hardware manager for Jarvis.
Wraps the Samsung SmartThings REST API v1.
All methods are synchronous (requests-based) to match Jarvis's architecture.

Auth: reads OAuth tokens from environment variables (set via .env file).
  ST_ACCESS_TOKEN   — current access token (expires in ~24h)
  ST_REFRESH_TOKEN  — used to get a new access token automatically
  ST_CLIENT_ID      — your SmartThings OAuth app client ID
  ST_CLIENT_SECRET  — your SmartThings OAuth app client secret
  ST_DEVICE_ID      — the Samsung AC device ID
"""

import os
import logging
import requests

logger = logging.getLogger("jarvis.smartthings")

# ── Constants ────────────────────────────────────────────────────────────────

BASE_URL = "https://api.smartthings.com/v1"
TOKEN_URL = "https://auth-global.api.smartthings.com/oauth/token"
DEFAULT_TIMEOUT_SECONDS = 8

VALID_MODES = {"cool", "heat", "auto", "dry", "wind", "fanOnly"}
TEMP_MIN_C = 16
TEMP_MAX_C = 30

# ── Exception Types ───────────────────────────────────────────────────────────

class SmartThingsError(Exception):
    """Base exception for all SmartThings failures."""
    pass

class SmartThingsAuthError(SmartThingsError):
    """Raised on 401/403 responses — bad or expired token."""
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
    Reads credentials from environment variables automatically.

    Usage:
        st = SmartThingsManager()
        st.turn_on()
        st.set_temperature(22)
        st.set_mode("cool")
        status = st.get_status()
        st.turn_off()
    """

    def __init__(self, pat: str = None, device_id: str = None):
        # OAuth token from env (preferred)
        self._access_token  = os.getenv("ST_ACCESS_TOKEN", "")
        self._refresh_token = os.getenv("ST_REFRESH_TOKEN", "")
        self._client_id     = os.getenv("ST_CLIENT_ID", "")
        self._client_secret = os.getenv("ST_CLIENT_SECRET", "")

        # Device ID: env → explicit arg → legacy config fallback
        self.device_id = (
            os.getenv("ST_DEVICE_ID")
            or device_id
            or "ee2f1cab-7be3-3d30-895e-69af725c7291"
        )

        # Legacy PAT fallback — only used if no OAuth token is available
        if not self._access_token and pat:
            self._access_token = pat
            logger.warning("[SmartThings] No ST_ACCESS_TOKEN in env — using PAT fallback.")

        if not self._access_token:
            logger.error(
                "[SmartThings] No access token! Set ST_ACCESS_TOKEN in your .env file."
            )

        self.device_url = f"{BASE_URL}/devices/{self.device_id}/commands"
        self.status_url = f"{BASE_URL}/devices/{self.device_id}/components/main/status"
        logger.info(
            "[SmartThings] Manager initialised (OAuth). Device: %s",
            self.device_id[:8] + "..." if self.device_id else "UNSET",
        )

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    def _refresh_access_token(self) -> bool:
        """
        Use the refresh token to get a new access token.
        Updates self._access_token in-place.
        Returns True on success, False on failure.
        """
        if not all([self._refresh_token, self._client_id, self._client_secret]):
            logger.error(
                "[SmartThings] Cannot refresh — missing ST_REFRESH_TOKEN, "
                "ST_CLIENT_ID, or ST_CLIENT_SECRET in .env"
            )
            return False
        try:
            resp = requests.post(
                TOKEN_URL,
                data={
                    "grant_type":    "refresh_token",
                    "client_id":     self._client_id,
                    "client_secret": self._client_secret,
                    "refresh_token": self._refresh_token,
                },
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                self._access_token  = data["access_token"]
                self._refresh_token = data.get("refresh_token", self._refresh_token)
                # Write back to env so the rest of the process sees fresh tokens
                os.environ["ST_ACCESS_TOKEN"]  = self._access_token
                os.environ["ST_REFRESH_TOKEN"] = self._refresh_token
                
                # Persist to .env file so the tokens survive restarts
                try:
                    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
                    from dotenv import set_key
                    set_key(env_path, "ST_ACCESS_TOKEN", self._access_token)
                    set_key(env_path, "ST_REFRESH_TOKEN", self._refresh_token)
                    logger.info("[SmartThings] ✅ Token refreshed and saved successfully.")
                except Exception as e:
                    logger.warning(f"[SmartThings] ✅ Token refreshed but failed to update .env on disk: {e}")

                return True
            logger.error("[SmartThings] Token refresh failed: HTTP %s - %s", resp.status_code, resp.text)
        except Exception as e:
            logger.error("[SmartThings] Token refresh exception: %s", e)
        return False

    def _post_command(self, commands: list) -> dict:
        """
        POST a command. Automatically retries once after refreshing token on 401.
        """
        payload = {"commands": commands}
        logger.debug("[SmartThings] POST %s | payload: %s", self.device_url, payload)
        try:
            response = requests.post(
                self.device_url,
                json=payload,
                headers=self._headers,
                timeout=DEFAULT_TIMEOUT_SECONDS,
            )
        except requests.exceptions.Timeout:
            raise SmartThingsError(
                f"[SmartThings] Request timed out after {DEFAULT_TIMEOUT_SECONDS}s."
            )
        except requests.exceptions.ConnectionError as e:
            raise SmartThingsError(f"[SmartThings] Connection failed: {e}")

        # Auto-refresh on 401 and retry once
        if response.status_code == 401 and self._refresh_access_token():
            try:
                response = requests.post(
                    self.device_url,
                    json=payload,
                    headers=self._headers,
                    timeout=DEFAULT_TIMEOUT_SECONDS,
                )
            except Exception as e:
                raise SmartThingsError(f"[SmartThings] Retry after refresh failed: {e}")

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
                "[SmartThings] HTTP 401 — Token invalid or expired and refresh failed. "
                "Check ST_CLIENT_ID + ST_CLIENT_SECRET in .env"
            )
        if code == 403:
            raise SmartThingsAuthError(
                "[SmartThings] HTTP 403 — Token doesn't have permission for this device."
            )
        if code == 404:
            raise SmartThingsDeviceError(
                f"[SmartThings] HTTP 404 — Device '{self.device_id}' not found."
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
        Fetch and return a flat device status dict.
        Returns: {"switch", "temperature", "coolingSetpoint", "airConditionerMode"}
        """
        logger.debug("[SmartThings] GET device status: %s", self.status_url)
        try:
            response = requests.get(
                self.status_url,
                headers=self._headers,
                timeout=DEFAULT_TIMEOUT_SECONDS,
            )
        except requests.exceptions.Timeout:
            raise SmartThingsError("[SmartThings] Status request timed out.")
        except requests.exceptions.ConnectionError as e:
            raise SmartThingsError(f"[SmartThings] Connection failed: {e}")

        if response.status_code == 401 and self._refresh_access_token():
            response = requests.get(self.status_url, headers=self._headers,
                                    timeout=DEFAULT_TIMEOUT_SECONDS)

        self._raise_for_status(response)
        raw = response.json()  # /components/main/status returns the main component directly
        status = {
            "switch":              raw.get("switch", {}).get("switch", {}).get("value", "unknown"),
            "temperature":         raw.get("temperatureMeasurement", {}).get("temperature", {}).get("value"),
            "coolingSetpoint":     raw.get("thermostatCoolingSetpoint", {}).get("coolingSetpoint", {}).get("value"),
            "airConditionerMode":  raw.get("airConditionerMode", {}).get("airConditionerMode", {}).get("value"),
            "fanMode":             raw.get("airConditionerFanMode", {}).get("fanMode", {}).get("value"),
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
