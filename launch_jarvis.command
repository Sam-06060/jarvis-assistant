#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  launch_jarvis.command
#  Double-click this file from Finder to launch Jarvis with all
#  environment variables properly loaded from .env
# ─────────────────────────────────────────────────────────────

# Change to the project root (where this script lives)
cd "$(dirname "$0")" || exit 1

echo "🚀 Launching Jarvis..."
exec /bin/bash "./start_backend_only.sh"
