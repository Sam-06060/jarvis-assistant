#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${JARVIS_PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT_DIR"

PYTHON_BIN="${JARVIS_PYTHON_BIN:-${ROOT_DIR}/.venv/bin/python3}"
SCRIPT_PATH="${JARVIS_SCRIPT_PATH:-${ROOT_DIR}/jarvis.py}"
BACKEND_PORT="${JARVIS_BACKEND_PORT:-8492}"
DOTENV_PATH="${ROOT_DIR}/.env"

log() {
  printf '%s\n' "$1"
}

load_dotenv() {
  if [[ ! -f "$DOTENV_PATH" ]]; then
    return
  fi

  while IFS= read -r line || [[ -n "$line" ]]; do
    local trimmed="$line"
    trimmed="${trimmed#"${trimmed%%[![:space:]]*}"}"
    [[ -z "$trimmed" || "${trimmed:0:1}" == "#" ]] && continue
    [[ "$trimmed" != *=* ]] && continue

    local key="${trimmed%%=*}"
    local value="${trimmed#*=}"

    key="${key%"${key##*[![:space:]]}"}"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"

    if [[ ${#value} -ge 2 ]]; then
      if [[ "${value:0:1}" == "\"" && "${value: -1}" == "\"" ]]; then
        value="${value:1:${#value}-2}"
      elif [[ "${value:0:1}" == "'" && "${value: -1}" == "'" ]]; then
        value="${value:1:${#value}-2}"
      fi
    fi

    export "$key=$value"
  done < "$DOTENV_PATH"
}

backend_is_listening() {
  /usr/bin/lsof -nP -iTCP:"$BACKEND_PORT" -sTCP:LISTEN >/dev/null 2>&1
}

linked_python_framework_bin() {
  /usr/bin/otool -L "$PYTHON_BIN" 2>/dev/null | /usr/bin/awk '/Python\.framework/ { print $1; exit }'
}

repair_python_signature_if_needed() {
  local stamp_file="${ROOT_DIR}/.codesign_ok"
  local framework_bin
  framework_bin="$(linked_python_framework_bin)"

  if [[ -z "$framework_bin" ]]; then
    log "⚠️ Could not resolve linked Python.framework for $PYTHON_BIN"
    return 0
  fi

  # FAST PATH: skip codesign if binary hasn't changed since last successful check
  local current_mtime
  current_mtime="$(/usr/bin/stat -f '%m' "$framework_bin" 2>/dev/null || echo 0)"
  if [[ -f "$stamp_file" ]] && [[ "$(cat "$stamp_file" 2>/dev/null)" == "$current_mtime" ]]; then
    return 0
  fi

  local framework_root
  framework_root="$(cd "$(dirname "$framework_bin")/../../.." && pwd)"

  if /usr/bin/codesign --verify --verbose=2 "$framework_bin" >/dev/null 2>&1; then
    echo "$current_mtime" > "$stamp_file"
    return 0
  fi

  log "⚠️ Python runtime signature is invalid. Repairing Homebrew framework..."
  /usr/bin/codesign --force --deep --sign - "$framework_root"

  while IFS= read -r stub; do
    /usr/bin/codesign --force --sign - "$stub"
  done < <(/usr/bin/find "${ROOT_DIR}/.venv/bin" -maxdepth 1 -type f -name 'python*' | /usr/bin/sort)

  if ! /usr/bin/codesign --verify --verbose=2 "$framework_bin" >/dev/null 2>&1; then
    log "❌ Python runtime signature repair failed for $framework_root"
    exit 1
  fi

  # Cache successful verification
  current_mtime="$(/usr/bin/stat -f '%m' "$framework_bin" 2>/dev/null || echo 0)"
  echo "$current_mtime" > "$stamp_file"
  log "✅ Python runtime signature repaired."
}

mkdir -p "${ROOT_DIR}/logs"
load_dotenv

if [[ ! -x "$PYTHON_BIN" ]]; then
  log "❌ Missing virtualenv python: $PYTHON_BIN"
  log "Run: ./scripts/bootstrap_macos.sh"
  exit 1
fi

if [[ ! -f "$SCRIPT_PATH" ]]; then
  log "❌ Missing backend entrypoint: $SCRIPT_PATH"
  exit 1
fi

if backend_is_listening; then
  log "ℹ️ Backend already listening on port $BACKEND_PORT. Reusing existing process."
  exit 0
fi

repair_python_signature_if_needed

exec "$PYTHON_BIN" -u "$SCRIPT_PATH" --api
