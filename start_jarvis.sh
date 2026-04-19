#!/usr/bin/env bash
set -euo pipefail

# --- JARVIS LAUNCHER (v4.6) ---
# This script is triggered by the cmd+option+j shortcut.
# Start the backend first so the app has a socket to connect to immediately.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

exec /bin/bash "${ROOT_DIR}/start_backend_only.sh"
