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
