#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "🔍 Testing Jarvis Backend Launch..."

PYTHON_PATH="${ROOT_DIR}/.venv/bin/python3"
SCRIPT_PATH="${ROOT_DIR}/jarvis.py"

if [[ ! -x "$PYTHON_PATH" ]]; then
  echo "❌ Python not found at: $PYTHON_PATH"
  echo "Run: ./scripts/bootstrap_macos.sh"
  exit 1
fi

if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "❌ Script not found at: $SCRIPT_PATH"
  exit 1
fi

echo "✅ Python found: $PYTHON_PATH"
echo "✅ Script found: $SCRIPT_PATH"
echo
echo "🚀 Running backend smoke test..."
"$PYTHON_PATH" scripts/smoke_backend.py
