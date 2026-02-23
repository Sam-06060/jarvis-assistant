#!/usr/bin/env python3
"""
Jarvis preflight checker.
Runs non-destructive checks to verify a fresh clone is ready.
"""
from __future__ import annotations

import argparse
import importlib
import os
import platform
import socket
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()
    return data


def is_placeholder(value: str) -> bool:
    if not value:
        return True
    marker = value.upper()
    return (
        "YOUR_" in marker
        or marker.endswith("_HERE")
        or marker in {"CHANGEME", "PLACEHOLDER"}
    )


def check_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Jarvis environment doctor")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    print("🩺 Jarvis Doctor")
    print(f"📂 Root: {ROOT}")
    print(f"🖥️  OS: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {platform.python_version()}")

    if platform.system() != "Darwin":
        warnings.append("Jarvis is designed for macOS (Darwin).")

    if sys.version_info < (3, 10):
        errors.append("Python 3.10+ is required.")

    required_paths = [
        ROOT / "jarvis.py",
        ROOT / "config.py",
        ROOT / "modules",
        ROOT / "utils",
        ROOT / "JarvisApp",
        ROOT / ".env",
    ]
    for path in required_paths:
        if not path.exists():
            errors.append(f"Missing required path: {path}")

    for folder in ("data", "logs", "macros"):
        (ROOT / folder).mkdir(exist_ok=True)

    env = parse_env(ROOT / ".env")
    required_env = [
        "PICOVOICE_API_KEY",
        "OPENROUTER_API_KEY",
    ]
    for key in required_env:
        value = env.get(key, "")
        if is_placeholder(value):
            errors.append(f".env key not configured: {key}")

    optional_env = [
        "PHONE_MAC_ADDRESS",
        "REFERENCE_IMAGE_PATH",
    ]
    for key in optional_env:
        if not env.get(key):
            warnings.append(f"Optional .env key not set: {key}")

    import_checks = [
        "config",
        "utils.logger",
        "modules.speech",
        "modules.brain",
        "modules.commands",
        "modules.socket_server",
        "modules.web_search",
    ]
    for mod in import_checks:
        try:
            importlib.import_module(mod)
        except Exception as exc:  # pragma: no cover - diagnostic output
            errors.append(f"Import failed ({mod}): {exc}")

    if not check_port_free(8492):
        warnings.append("Port 8492 is already in use (backend may already be running).")

    print()
    if errors:
        print("❌ Errors:")
        for err in errors:
            print(f"  - {err}")
    else:
        print("✅ No blocking errors found.")

    if warnings:
        print("⚠️ Warnings:")
        for warn in warnings:
            print(f"  - {warn}")

    if errors:
        return 1
    if args.strict and warnings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
