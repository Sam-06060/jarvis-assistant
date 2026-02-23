#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DEV_MODE=0
if [[ "${1:-}" == "--dev" ]]; then
  DEV_MODE=1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found. Install Python 3.11+ first."
  exit 1
fi

echo "🔧 Bootstrapping Jarvis in: $ROOT_DIR"
echo "🐍 Python: $(python3 --version)"

if [[ ! -d ".venv" ]]; then
  echo "📦 Creating virtual environment (.venv)"
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "⬆️ Upgrading pip/setuptools/wheel"
python -m pip install --upgrade pip setuptools wheel

echo "📚 Installing runtime dependencies"
python -m pip install -r requirements.txt

if [[ "$DEV_MODE" -eq 1 ]]; then
  echo "🧪 Installing development dependencies"
  python -m pip install -r requirements-dev.txt
fi

mkdir -p data logs macros

if [[ ! -f ".env" ]]; then
  if [[ -f ".env.example" ]]; then
    cp .env.example .env
    echo "📝 Created .env from .env.example"
  else
    echo "⚠️ .env.example not found. Create .env manually."
  fi
fi

echo
echo "✅ Bootstrap complete."
echo "Next:"
echo "  1) Edit .env with your API keys"
echo "  2) Run: .venv/bin/python scripts/doctor.py --strict"
echo "  3) Run: ./start_jarvis.sh"
