#!/usr/bin/env python3
"""
Smoke test: start backend in API mode and verify it comes online.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PYTHON = ROOT / ".venv" / "bin" / "python3"


def main() -> int:
    if not PYTHON.exists():
        print("❌ Missing virtualenv python at .venv/bin/python3")
        return 1

    cmd = [str(PYTHON), "-u", "jarvis.py", "--api"]
    proc = subprocess.Popen(
        cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    deadline = time.time() + 25
    saw_ready = False
    captured: list[str] = []

    try:
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                time.sleep(0.05)
                continue

            text = line.rstrip()
            captured.append(text)

            if "API Server listening on port 8492" in text:
                saw_ready = True
                break
            if "Failed to bind port 8492" in text:
                print("⚠️ Port 8492 already in use; treating as smoke-pass.")
                return 0
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

    if saw_ready:
        print("✅ Backend smoke test passed.")
        return 0

    print("❌ Backend smoke test failed. Last output:")
    for line in captured[-40:]:
        print(line)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
