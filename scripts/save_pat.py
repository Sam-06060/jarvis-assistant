#!/usr/bin/env python3
"""
Quick script to save a new SmartThings Personal Access Token to .env
Run: python3 scripts/save_pat.py
"""
import os, sys

_ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

from dotenv import load_dotenv, set_key
load_dotenv(dotenv_path=_ENV_PATH, override=True)

print()
print("═" * 60)
print("  SAVE SMARTTHINGS PERSONAL ACCESS TOKEN")
print("═" * 60)
print()
print("Paste the Personal Access Token you just generated")
print("from: https://account.smartthings.com/tokens")
print()
pat = input("  Token: ").strip().strip('"').strip("'")

if not pat or len(pat) < 20:
    print("❌ Token looks too short. Try again.")
    sys.exit(1)

# Test the token before saving
try:
    import requests
    env_device_id = os.getenv("ST_DEVICE_ID", "").strip().strip('"').strip("'")
    resp = requests.get(
        "https://api.smartthings.com/v1/devices",
        headers={"Authorization": f"Bearer {pat}"},
        timeout=8,
    )
    if resp.status_code == 200:
        devices = resp.json().get("items", [])
        print(f"\n✅ Token valid — {len(devices)} device(s) found on your account")
    else:
        print(f"\n⚠️  Token returned HTTP {resp.status_code} — saving anyway")
except Exception as e:
    print(f"\n⚠️  Could not verify token online ({e}) — saving anyway")

# Save — PAT is used as access token directly, no refresh needed
set_key(_ENV_PATH, "ST_ACCESS_TOKEN", pat)
# Clear old OAuth refresh token so we don't try to refresh a PAT
set_key(_ENV_PATH, "ST_REFRESH_TOKEN", "")
os.environ["ST_ACCESS_TOKEN"] = pat
os.environ["ST_REFRESH_TOKEN"] = ""

print()
print("═" * 60)
print("✅  Token saved to .env")
print("✅  Restart Jarvis — AC will work immediately")
print("═" * 60)
print()
print("Note: Personal Access Tokens don't expire automatically.")
print("You only need to regenerate one if you manually revoke it.")
print()
