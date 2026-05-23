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

FIX CHANGELOG (vs original):
  1. load_dotenv() is now called at module import time so saved tokens
     are always read back from .env after a restart.
  2. _ENV_PATH is computed once at module level and reused everywhere.
  3. _refresh_access_token() reloads .env from disk inside the lock so
     the "already refreshed by another thread/process" guard works correctly.
  4. get_status() 401-retry path uses self._headers (a @property that
     re-reads the freshly-updated self._access_token) — already correct,
     but now consistent with the fix in _post_command().
  5. Both _post_command() and get_status() also handle 403 as a trigger
     for a refresh attempt, because some SmartThings environments return
     403 instead of 401 for an expired token.
"""

import os
import logging
import requests
import base64
import threading

# ── FIX 1: load .env at import time ─────────────────────────────────────────
# Without this, tokens saved to .env by _refresh_access_token() are never
# read back into os.environ after a process restart, so the manager always
# starts with the original (expired) token from the shell environment.
from dotenv import load_dotenv, set_key

# ── FIX 2: single canonical path to the .env file ───────────────────────────
_ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=_ENV_PATH, override=True)

logger = logging.getLogger("jarvis.smartthings")

# ── Constants ────────────────────────────────────────────────────────────────

BASE_URL = "https://api.smartthings.com/v1"
TOKEN_URL = "https://api.smartthings.com/oauth/token"
DEFAULT_TIMEOUT_SECONDS = 8

_token_lock = threading.Lock()

def clean_env(key: str) -> str:
    """Read an environment variable and strip extraneous quotes."""
    value = os.getenv(key, "")
    return value.strip().strip('"').strip("'")

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
        # Because load_dotenv() ran at module import, os.environ now contains
        # the latest tokens from .env (including any refreshed tokens from a
        # previous run that were written back to disk).
        self._access_token  = clean_env("ST_ACCESS_TOKEN")
        self._refresh_token = clean_env("ST_REFRESH_TOKEN")
        self._client_id     = clean_env("ST_CLIENT_ID")
        self._client_secret = clean_env("ST_CLIENT_SECRET")

        # Device ID: env → explicit arg → legacy config fallback
        self.device_id = (
            clean_env("ST_DEVICE_ID")
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
        # Proactively validate token health at startup (non-blocking)
        import threading as _threading
        _threading.Thread(
            target=self._proactive_token_check,
            daemon=True,
            name="STTokenCheck",
        ).start()

    @property
    def _headers(self) -> dict:
        # Reads self._access_token every time it is accessed, so it always
        # reflects the latest token after a refresh.
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    def _proactive_token_check(self):
        """
        Called in a daemon thread at startup.
        Makes a lightweight status call to detect expired tokens early.
        If expired, attempts refresh. If refresh fails, checks if the
        SmartThings CLI has fresh tokens and adopts them automatically.
        """
        import time as _time
        _time.sleep(3)  # Let the rest of boot complete first
        try:
            resp = requests.get(
                self.status_url,
                headers=self._headers,
                timeout=5,
            )
            if resp.status_code in range(200, 300):
                logger.info("[SmartThings] ✅ Token healthy at startup.")
                return

            if resp.status_code == 401:
                logger.warning(
                    "[SmartThings] ⚠️  Access token expired at startup — attempting refresh..."
                )
                if self._refresh_access_token():
                    logger.info("[SmartThings] ✅ Token refreshed successfully at startup.")
                    return

                # Refresh failed — try adopting CLI tokens as fallback
                if self._adopt_cli_tokens():
                    logger.info("[SmartThings] ✅ Adopted fresh tokens from CLI.")
                    return

                logger.error(
                    "[SmartThings] ❌ Token expired and all recovery failed.\n"
                    "  FIX: Run this in Terminal to re-authenticate:\n"
                    "    python3 scripts/smartthings_reauth.py"
                )
        except Exception as e:
            logger.debug(f"[SmartThings] Startup token check skipped: {e}")

    def _adopt_cli_tokens(self) -> bool:
        """
        Try to read fresh OAuth tokens from the SmartThings CLI credentials file.
        If found and valid, adopt them into this process and save to .env.

        The CLI stores tokens at:
          ~/Library/Application Support/@smartthings/cli/credentials.json

        This allows auto-healing: if the user runs ANY `smartthings` CLI command
        (which triggers a login), Jarvis picks up the fresh tokens automatically.
        """
        import json
        cli_paths = [
            os.path.expanduser("~/Library/Application Support/@smartthings/cli/credentials.json"),
            os.path.expanduser("~/.config/@smartthings/cli/credentials.json"),
        ]
        for creds_path in cli_paths:
            try:
                if not os.path.exists(creds_path):
                    continue
                with open(creds_path) as f:
                    data = json.load(f)
                entry = data.get("default:api.smartthings.com", {})
                cli_access  = entry.get("accessToken", "")
                cli_refresh = entry.get("refreshToken", "")
                if not cli_access or cli_access == self._access_token:
                    continue  # Same token we already have, or empty

                # Test the CLI token
                test_resp = requests.get(
                    self.status_url,
                    headers={"Authorization": f"Bearer {cli_access}", "Content-Type": "application/json"},
                    timeout=5,
                )
                if test_resp.status_code not in range(200, 300):
                    logger.debug("[SmartThings] CLI token also expired.")
                    continue

                # CLI token works — adopt it
                self._access_token  = cli_access
                self._refresh_token = cli_refresh
                os.environ["ST_ACCESS_TOKEN"]  = cli_access
                os.environ["ST_REFRESH_TOKEN"] = cli_refresh
                try:
                    set_key(_ENV_PATH, "ST_ACCESS_TOKEN",  cli_access)
                    set_key(_ENV_PATH, "ST_REFRESH_TOKEN", cli_refresh)
                except Exception:
                    pass  # In-memory is enough for this session
                logger.info(
                    "[SmartThings] 🔄 Auto-adopted fresh tokens from CLI credentials (%s)",
                    creds_path,
                )
                return True
            except Exception as e:
                logger.debug(f"[SmartThings] CLI creds check failed ({creds_path}): {e}")
        return False

    def _refresh_access_token(self) -> bool:
        """
        Refresh the access token.  Two strategies, tried in order:

        1. CLI refresh (primary) — runs `smartthings devices -j` silently.
           The CLI has its own internal OAuth client credentials that match
           the tokens it issues, so this always works.  After the CLI runs,
           we read the updated credentials.json and adopt the new tokens.

        2. Manual OAuth POST (fallback) — uses ST_CLIENT_ID + ST_CLIENT_SECRET
           from .env.  Only works if the tokens were originally issued by the
           user's own OAuth app (not the CLI).

        Returns True on success, False on failure.
        """
        if not self._refresh_token:
            logger.error(
                "[SmartThings] ❌ No refresh token available.\n"
                "  FIX: Run in Terminal:  python3 scripts/smartthings_reauth.py"
            )
            return False

        with _token_lock:
            # ── Check if another thread/process already refreshed ────────────
            load_dotenv(dotenv_path=_ENV_PATH, override=True)
            current_access  = clean_env("ST_ACCESS_TOKEN")
            current_refresh = clean_env("ST_REFRESH_TOKEN")

            if current_access and current_access != self._access_token:
                logger.info(
                    "[SmartThings] Token already refreshed by another process/thread. "
                    "Adopting new token."
                )
                self._access_token  = current_access
                self._refresh_token = current_refresh
                return True

            # ── STRATEGY 1: CLI refresh (primary) ────────────────────────────
            # The SmartThings CLI stores its own OAuth client credentials
            # internally.  Running any CLI command triggers an auto-refresh
            # of its tokens using those matching credentials.
            if self._refresh_via_cli():
                return True

            # ── STRATEGY 2: Manual OAuth POST (fallback) ─────────────────────
            if self._client_id and self._client_secret:
                if self._refresh_via_oauth():
                    return True

            # ── STRATEGY 3: Adopt CLI credentials file if available ──────────
            if self._adopt_cli_tokens():
                return True

            logger.error(
                "[SmartThings] ❌ All token refresh strategies failed.\n"
                "  FIX: Run in Terminal:  python3 scripts/smartthings_reauth.py"
            )
            return False

    def _refresh_via_cli(self) -> bool:
        """
        Silently run the SmartThings CLI to trigger its internal token refresh.
        The CLI auto-refreshes its own tokens using its built-in client credentials.
        After running, we read the fresh tokens from credentials.json.
        """
        import subprocess
        import json

        try:
            # Quick silent command — just lists devices, triggers internal refresh
            result = subprocess.run(
                ["smartthings", "devices", "-j"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode != 0:
                logger.debug(
                    "[SmartThings] CLI refresh: command failed (rc=%d): %s",
                    result.returncode, result.stderr[:200],
                )
                return False

            # CLI succeeded — read the updated credentials
            cli_paths = [
                os.path.expanduser(
                    "~/Library/Application Support/@smartthings/cli/credentials.json"
                ),
                os.path.expanduser(
                    "~/.config/@smartthings/cli/credentials.json"
                ),
            ]
            for creds_path in cli_paths:
                try:
                    if not os.path.exists(creds_path):
                        continue
                    with open(creds_path) as f:
                        data = json.load(f)
                    entry = data.get("default:api.smartthings.com", {})
                    new_access  = entry.get("accessToken", "")
                    new_refresh = entry.get("refreshToken", "")
                    if not new_access:
                        continue

                    self._access_token  = new_access
                    self._refresh_token = new_refresh
                    os.environ["ST_ACCESS_TOKEN"]  = new_access
                    os.environ["ST_REFRESH_TOKEN"] = new_refresh
                    try:
                        set_key(_ENV_PATH, "ST_ACCESS_TOKEN",  new_access)
                        set_key(_ENV_PATH, "ST_REFRESH_TOKEN", new_refresh)
                    except Exception:
                        pass
                    logger.info(
                        "[SmartThings] ✅ Token refreshed via CLI (auto-refresh)"
                    )
                    return True
                except Exception:
                    continue

        except FileNotFoundError:
            logger.debug("[SmartThings] CLI refresh: smartthings CLI not installed")
        except subprocess.TimeoutExpired:
            logger.debug("[SmartThings] CLI refresh: timed out (15s)")
        except Exception as e:
            logger.debug("[SmartThings] CLI refresh failed: %s", e)

        return False

    def _refresh_via_oauth(self) -> bool:
        """
        Manual OAuth refresh using ST_CLIENT_ID + ST_CLIENT_SECRET from .env.
        Only works if tokens were originally issued by the user's own OAuth app.
        Retries once on 5xx (Samsung server outage).
        """
        import time as _time

        for attempt in range(1, 3):
            try:
                credentials = f"{self._client_id}:{self._client_secret}"
                encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

                resp = requests.post(
                    TOKEN_URL,
                    headers={
                        "Authorization": f"Basic {encoded}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data={
                        "grant_type":    "refresh_token",
                        "refresh_token": self._refresh_token,
                    },
                    timeout=5,
                )

                if resp.status_code == 200:
                    data = resp.json()
                    self._access_token  = data["access_token"]
                    self._refresh_token = data.get("refresh_token", self._refresh_token)
                    os.environ["ST_ACCESS_TOKEN"]  = self._access_token
                    os.environ["ST_REFRESH_TOKEN"] = self._refresh_token
                    try:
                        set_key(_ENV_PATH, "ST_ACCESS_TOKEN",  self._access_token)
                        set_key(_ENV_PATH, "ST_REFRESH_TOKEN", self._refresh_token)
                        logger.info("[SmartThings] ✅ Token refreshed via OAuth")
                    except Exception as e:
                        logger.warning(
                            "[SmartThings] ✅ Refreshed in memory, .env write failed: %s", e
                        )
                    return True

                if resp.status_code >= 500:
                    logger.warning(
                        "[SmartThings] OAuth refresh attempt %d/2: HTTP %s — retrying",
                        attempt, resp.status_code,
                    )
                    if attempt < 2:
                        _time.sleep(1)
                    continue

                # 4xx — credentials mismatch or revoked token, don't retry
                logger.debug(
                    "[SmartThings] OAuth refresh: HTTP %s (client/token mismatch)",
                    resp.status_code,
                )
                return False

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.debug("[SmartThings] OAuth refresh attempt %d/2 timeout: %s", attempt, e)
                if attempt < 2:
                    _time.sleep(1)
            except Exception as e:
                logger.debug("[SmartThings] OAuth refresh exception: %s", e)
                return False

        return False

    def _should_retry_after_refresh(self, status_code: int) -> bool:
        """
        Return True if the HTTP status code warrants a token-refresh attempt.

        FIX 5: Some SmartThings environments return 403 (not 401) for an
        expired token, so we attempt a refresh on both.
        """
        return status_code in (401, 403) and self._refresh_access_token()

    def _post_command(self, commands: list) -> dict:
        """
        POST a command list to the device.
        Automatically retries once after refreshing the token on 401 or 403.
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

        # Auto-refresh on 401/403 and retry once
        if self._should_retry_after_refresh(response.status_code):
            try:
                response = requests.post(
                    self.device_url,
                    json=payload,
                    headers=self._headers,   # @property re-reads updated token
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
        Returns: {"switch", "temperature", "coolingSetpoint", "airConditionerMode", "fanMode"}
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

        # Auto-refresh on 401/403 and retry once
        if self._should_retry_after_refresh(response.status_code):
            try:
                response = requests.get(
                    self.status_url,
                    headers=self._headers,   # @property re-reads updated token
                    timeout=DEFAULT_TIMEOUT_SECONDS,
                )
            except Exception as e:
                raise SmartThingsError(f"[SmartThings] Retry after refresh failed: {e}")

        self._raise_for_status(response)
        raw = response.json()
        status = {
            "switch":             raw.get("switch", {}).get("switch", {}).get("value", "unknown"),
            "temperature":        raw.get("temperatureMeasurement", {}).get("temperature", {}).get("value"),
            "coolingSetpoint":    raw.get("thermostatCoolingSetpoint", {}).get("coolingSetpoint", {}).get("value"),
            "airConditionerMode": raw.get("airConditionerMode", {}).get("airConditionerMode", {}).get("value"),
            "fanMode":            raw.get("airConditionerFanMode", {}).get("fanMode", {}).get("value"),
        }
        logger.info("[SmartThings] Status: %s", status)
        return status

    def turn_on(self) -> dict:
        """Power on the AC unit. (capability: switch → on)"""
        logger.info("[SmartThings] Turning AC ON.")
        return self._post_command([
            {"component": "main", "capability": "switch", "command": "on"}
        ])

    def turn_off(self) -> dict:
        """Power off the AC unit. (capability: switch → off)"""
        logger.info("[SmartThings] Turning AC OFF.")
        return self._post_command([
            {"component": "main", "capability": "switch", "command": "off"}
        ])

    def set_temperature(self, celsius: float) -> dict:
        """
        Set the cooling setpoint in °C.
        Valid range: 16 – 30.  Raises ValueError outside that range.
        (capability: thermostatCoolingSetpoint → setCoolingSetpoint)
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
                "component":  "main",
                "capability": "thermostatCoolingSetpoint",
                "command":    "setCoolingSetpoint",
                "arguments":  [celsius],
            }
        ])

    def set_mode(self, mode: str) -> dict:
        """
        Set the AC operating mode.
        Valid modes: cool, heat, auto, dry, wind, fanOnly
        (capability: airConditionerMode → setAirConditionerMode)
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
                "component":  "main",
                "capability": "airConditionerMode",
                "command":    "setAirConditionerMode",
                "arguments":  [mode],
            }
        ])

    def set_fan_mode(self, fan_mode: str) -> dict:
        """
        Set the fan speed/mode.
        Common values: auto, low, medium, high, turbo
        (capability: airConditionerFanMode → setFanMode)
        """
        fan_mode = fan_mode.lower().strip()
        logger.info("[SmartThings] Setting fan mode to '%s'.", fan_mode)
        return self._post_command([
            {
                "component":  "main",
                "capability": "airConditionerFanMode",
                "command":    "setFanMode",
                "arguments":  [fan_mode],
            }
        ])