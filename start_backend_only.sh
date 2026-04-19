#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${ROOT_DIR}/.venv/bin/python3"
LAUNCHER="${ROOT_DIR}/scripts/launch_backend_from_app.sh"
APP_BUNDLE="${JARVIS_APP_BUNDLE:-/Applications/Jarvis.app}"
BACKEND_LOG="${ROOT_DIR}/logs/backend_console.log"
PID_FILE="${ROOT_DIR}/.jarvis_backend.pid"

mkdir -p "${ROOT_DIR}/logs"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "❌ Missing virtualenv python: $PYTHON_BIN"
  echo "Run: ./scripts/bootstrap_macos.sh"
  exit 1
fi

if [[ ! -f "$LAUNCHER" ]]; then
  echo "❌ Missing backend launcher: $LAUNCHER"
  exit 1
fi

echo "🚀 Starting Jarvis backend..."

if lsof -iTCP:8492 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "ℹ️ Port 8492 already in use. Reusing existing backend."
else
  /bin/bash "$LAUNCHER" >>"$BACKEND_LOG" 2>&1 &
  BACKEND_PID=$!
  echo "$BACKEND_PID" > "$PID_FILE"

  echo "⏳ Waiting for backend (port 8492)..."
  READY=0
  for _ in {1..40}; do
    if lsof -iTCP:8492 -sTCP:LISTEN >/dev/null 2>&1; then
      READY=1
      break
    fi
    sleep 0.5
  done

  if [[ "$READY" -ne 1 ]]; then
    echo "❌ Backend failed to start. See: $BACKEND_LOG"
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
    exit 1
  fi
fi

echo "✅ Backend online on port 8492"

if [[ -d "$APP_BUNDLE" ]]; then
  echo "🎨 Launching app: $APP_BUNDLE"
  open "$APP_BUNDLE"
else
  echo "⚠️ App bundle not found at $APP_BUNDLE"
  echo "Build it with: (cd JarvisApp && ./build_app.sh)"
fi

echo "✅ Jarvis start sequence complete."
