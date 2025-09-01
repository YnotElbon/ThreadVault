#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
cd "$ROOT_DIR"

CFG="system/config.tunnel.json"
PORT="${PORT:-$(python3 - <<'PY'
import json;print(json.load(open('system/config.tunnel.json')).get('port',8787))
PY
)}"

BIN_CF="$ROOT_DIR/system/bin/cloudflared"

log_file="system/cloudflared.log"
url_file="system/public_url.txt"

ensure_cloudflared() {
  if command -v cloudflared >/dev/null 2>&1; then
    echo "cloudflared found in PATH" >&2
    echo "cloudflared"
    return 0
  fi
  if [ -x "$BIN_CF" ]; then
    echo "$BIN_CF"
    return 0
  fi
  echo "Downloading cloudflared quick binary..." >&2
  OS="darwin"; ARCH="arm64"
  URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-${OS}-${ARCH}.tgz"
  TMP=$(mktemp -d)
  (cd "$TMP" && curl -fsSL "$URL" -o cf.tgz && tar xzf cf.tgz && mv cloudflared "$BIN_CF" && chmod +x "$BIN_CF")
  rm -rf "$TMP"
  echo "$BIN_CF"
}

start_quick_tunnel() {
  CF_BIN=$(ensure_cloudflared)
  echo "Starting quick tunnel on port $PORT... logs: $log_file" >&2
  # Start in background
  nohup "$CF_BIN" tunnel --url "http://127.0.0.1:${PORT}" --no-autoupdate > "$log_file" 2>&1 &
  echo $! > system/cloudflared.pid
  # Wait for URL
  for i in {1..30}; do
    if grep -Eo 'https://[A-Za-z0-9.-]+\.trycloudflare\.com' "$log_file" | head -n1 > "$url_file"; then
      if [ -s "$url_file" ]; then
        echo "Public URL: $(cat "$url_file")" >&2
        return 0
      fi
    fi
    sleep 1
  done
  echo "Failed to obtain public URL (timeout)" >&2
  return 1
}

start_quick_tunnel

