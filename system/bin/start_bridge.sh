#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
cd "$ROOT_DIR"

# Ensure token exists
TOKEN_FILE="system/bridge_token.txt"
if [ ! -f "$TOKEN_FILE" ] || [ ! -s "$TOKEN_FILE" ]; then
  python3 - <<'PY'
import secrets, pathlib
pathlib.Path('system/bridge_token.txt').write_text(secrets.token_urlsafe(32))
PY
fi
API_TOKEN="$(cat "$TOKEN_FILE" | tr -d '\n')"

# Ensure venv and dependencies
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null 2>&1 || true
pip install --disable-pip-version-check fastapi uvicorn >/dev/null 2>&1

export THREADVAULT_BASE="$ROOT_DIR"
export API_TOKEN="$API_TOKEN"

# Host/Port (override via env)
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8787}"
LOG_DIR="system"
mkdir -p "$LOG_DIR"

exec uvicorn tools.bridges.fastapi_app:app \
  --host "$HOST" \
  --port "$PORT"
