#!/usr/bin/env bash
set -euo pipefail

# --- JARVIS LAUNCHER (v4.5) ---
# This script is triggered by the cmd+option+j shortcut.
# To prevent double-instancing, we only launch the Swift App (Jarvis.app).
# The app will automatically start the Python backend via ProcessManager.swift.

APP_BUNDLE="${JARVIS_APP_BUNDLE:-/Applications/Jarvis.app}"

if [[ -d "$APP_BUNDLE" ]]; then
  echo "🚀 Launching Jarvis..."
  open "$APP_BUNDLE"
else
  echo "❌ Error: Jarvis.app not found at $APP_BUNDLE"
  echo "Please build the app first: (cd JarvisApp && ./build_app.sh)"
  exit 1
fi

echo "✅ App trigger sent."
