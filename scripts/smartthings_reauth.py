#!/usr/bin/env python3
"""
scripts/smartthings_reauth.py
──────────────────────────────────────────────────────────────────────────────
SmartThings OAuth Re-Authentication via CLI.

Run this when your refresh token is revoked (HTTP 400/401 on refresh).

How it works:
  1. Calls `smartthings devices` which triggers the CLI's built-in OAuth flow
  2. CLI opens a browser → you log in with your Samsung account
  3. CLI saves fresh access + refresh tokens to its credentials file
  4. This script reads those tokens and saves them to Jarvis's .env

Prerequisites:
  - SmartThings CLI installed: brew install smartthings
  - That's it. No developer workspace, no redirect URIs needed.

Usage:
    cd /Users/samsonganta/Desktop/jarvis-assistant
    python3 scripts/smartthings_reauth.py
"""

import json
import os
import subprocess
import sys

# ── Paths ─────────────────────────────────────────────────────────────────────
_SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_ENV_PATH     = os.path.join(_PROJECT_ROOT, ".env")
_CLI_CREDS    = os.path.expanduser(
    "~/Library/Application Support/@smartthings/cli/credentials.json"
)
_CLI_CREDS_ALT = os.path.expanduser("~/.config/@smartthings/cli/credentials.json")

if not os.path.exists(_ENV_PATH):
    print(f"❌ .env not found at: {_ENV_PATH}")
    sys.exit(1)

from dotenv import load_dotenv, set_key
load_dotenv(dotenv_path=_ENV_PATH, override=True)


def _find_creds_path() -> str:
    """Find the SmartThings CLI credentials file."""
    for p in [_CLI_CREDS, _CLI_CREDS_ALT]:
        if os.path.exists(p):
            return p
    return ""


def _read_cli_tokens() -> dict:
    """Read access + refresh tokens from the CLI's credentials.json."""
    creds_path = _find_creds_path()
    if not creds_path:
        return {}
    try:
        with open(creds_path) as f:
            data = json.load(f)
        # The CLI stores tokens under "default:api.smartthings.com"
        entry = data.get("default:api.smartthings.com", {})
        return {
            "access_token":  entry.get("accessToken", ""),
            "refresh_token": entry.get("refreshToken", ""),
            "expires":       entry.get("expires", ""),
            "scope":         entry.get("scope", ""),
        }
    except Exception as e:
        print(f"⚠️  Could not read CLI credentials: {e}")
        return {}


def _test_token(token: str) -> bool:
    """Quick test: can this token read devices?"""
    try:
        import requests
        resp = requests.get(
            "https://api.smartthings.com/v1/devices",
            headers={"Authorization": f"Bearer {token}"},
            timeout=8,
        )
        return resp.status_code == 200
    except Exception:
        return False


def main():
    print()
    print("═" * 65)
    print("   JARVIS × SMARTTHINGS RE-AUTHENTICATION (CLI)")
    print("═" * 65)
    print()

    # Step 1: Check if SmartThings CLI is installed
    try:
        result = subprocess.run(
            ["smartthings", "--version"],
            capture_output=True, text=True, timeout=5,
        )
        version = result.stdout.strip()
        print(f"  ✅ SmartThings CLI found: v{version}")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("  ❌ SmartThings CLI not found!")
        print("     Install it: brew install smartthings")
        sys.exit(1)

    # Step 2: Trigger CLI login (opens browser)
    print()
    print("  🌐 Opening Samsung login in your browser...")
    print("     → Log in with your Samsung account")
    print("     → The CLI will capture the token automatically")
    print()

    try:
        result = subprocess.run(
            ["smartthings", "devices", "-j"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            print(f"  ❌ CLI command failed: {result.stderr}")
            sys.exit(1)

        devices = json.loads(result.stdout) if result.stdout.strip() else []
        print(f"  ✅ Login successful — {len(devices)} device(s) found")
        for d in devices:
            label = d.get("label", "Unknown")
            did   = d.get("deviceId", "???")[:12]
            print(f"     • {label} ({did}...)")
    except subprocess.TimeoutExpired:
        print("  ❌ Login timed out (120s). Try again.")
        sys.exit(1)
    except Exception as e:
        print(f"  ❌ Error: {e}")
        sys.exit(1)

    # Step 3: Read the fresh tokens from CLI's credentials file
    print()
    tokens = _read_cli_tokens()
    if not tokens.get("access_token"):
        print("  ❌ Could not find tokens in CLI credentials file.")
        print(f"     Expected location: {_CLI_CREDS}")
        sys.exit(1)

    access_token  = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    expires       = tokens.get("expires", "unknown")

    print(f"  🔑 Access token:  {access_token[:16]}...")
    print(f"  🔑 Refresh token: {refresh_token[:16]}...")
    print(f"  ⏰ Expires:       {expires}")

    # Step 4: Verify the token works for device control
    if _test_token(access_token):
        print("  ✅ Token verified — device access confirmed")
    else:
        print("  ⚠️  Token could not be verified (network issue?) — saving anyway")

    # Step 5: Save to .env
    set_key(_ENV_PATH, "ST_ACCESS_TOKEN",  access_token)
    set_key(_ENV_PATH, "ST_REFRESH_TOKEN", refresh_token)
    os.environ["ST_ACCESS_TOKEN"]  = access_token
    os.environ["ST_REFRESH_TOKEN"] = refresh_token

    print()
    print("═" * 65)
    print("  ✅  SUCCESS — Fresh OAuth tokens saved to .env")
    print()
    print("  ✅  Restart Jarvis — AC will work immediately.")
    print("  ✅  Auto-refresh will keep tokens alive automatically.")
    print("═" * 65)
    print()


if __name__ == "__main__":
    main()
