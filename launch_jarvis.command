#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  launch_jarvis.command
#  Double-click this file from Finder to launch Jarvis with all
#  environment variables properly loaded from .env
# ─────────────────────────────────────────────────────────────

# Change to the project root (where this script lives)
cd "$(dirname "$0")" || exit 1

# Load credentials from .env
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
    echo "✅ .env loaded"
else
    echo "⚠️  No .env file found at $(pwd)/.env"
fi

# Run the release binary (built by: swift build -c release inside JarvisApp/)
BINARY="JarvisApp/.build/release/JarvisApp"

if [ ! -f "$BINARY" ]; then
    echo "🔨 Binary not found. Building release..."
    cd JarvisApp && swift build -c release
    cd ..
fi

echo "🚀 Launching Jarvis..."
exec "$BINARY"
