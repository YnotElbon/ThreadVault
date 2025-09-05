#!/usr/bin/env bash
set -euo pipefail

# One-shot bootstrap for a new Mac mini to run ThreadVault locally.
# - Installs Homebrew deps (git, python, jq, cloudflared optional, ollama)
# - Clones or updates the ThreadVault repo in ~/ThreadVault
# - Sets up venv, installs FastAPI/uvicorn, ensures bridge token
# - Installs and loads launchd agents (bridge, maintenance, tunnel optional, consult self-test)
# - Imports continuity bundles from Dropbox Threadsaves if present
# - Prompts to save API keys to ~/.threadvault.env for consult providers

: "${THREADVAULT_DIR:=$HOME/ThreadVault}"
REPO_URL="https://github.com/YnotElbon/ThreadVault"
WITH_TUNNEL=${WITH_TUNNEL:-1}
PULL_MODELS=${PULL_MODELS:-mistral}
THREADSAVES_DIR=${THREADSAVES_DIR:-"$HOME/Dropbox/Apps/Threadsaves"}

log() { echo "[bootstrap] $*"; }

need_cmd() { command -v "$1" >/dev/null 2>&1 || return 1; }

ensure_brew() {
  if ! need_cmd brew; then
    log "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$($(which brew) shellenv)"
  fi
}

install_deps() {
  log "Installing packages (git, python, jq, cloudflared, ollama)..."
  brew install git python jq cloudflared ollama || true
}

clone_or_update_repo() {
  if [ -d "$THREADVAULT_DIR/.git" ]; then
    log "Updating repo at $THREADVAULT_DIR"
    git -C "$THREADVAULT_DIR" fetch origin || true
    git -C "$THREADVAULT_DIR" reset --hard origin/main || true
  else
    log "Cloning repo to $THREADVAULT_DIR"
    git clone "$REPO_URL" "$THREADVAULT_DIR"
  fi
}

setup_python() {
  cd "$THREADVAULT_DIR"
  python3 -m venv .venv || true
  source .venv/bin/activate
  pip install --upgrade pip >/dev/null 2>&1 || true
  pip install fastapi uvicorn >/dev/null 2>&1
}

ensure_bridge_token() {
  cd "$THREADVAULT_DIR"
  if [ ! -s system/bridge_token.txt ]; then
    log "Generating bridge token"
    python3 - <<'PY'
import secrets, pathlib
pathlib.Path('system/bridge_token.txt').write_text(secrets.token_urlsafe(32))
PY
  fi
}

install_hooks() {
  cd "$THREADVAULT_DIR"
  bash system/install-hooks.sh || true
}

install_launch_agents() {
  cd "$THREADVAULT_DIR"
  mkdir -p "$HOME/Library/LaunchAgents"
  for pl in system/launchd/com.threadvault.bridge.plist \
             system/launchd/com.threadvault.maintenance.plist \
             system/launchd/com.threadvault.consultselftest.plist; do
    cp -f "$pl" "$HOME/Library/LaunchAgents/"
  done
  if [ "$WITH_TUNNEL" = "1" ]; then
    cp -f system/launchd/com.threadvault.tunnel.plist "$HOME/Library/LaunchAgents/"
  fi
  # Load
  launchctl unload "$HOME/Library/LaunchAgents/com.threadvault.bridge.plist" 2>/dev/null || true
  launchctl unload "$HOME/Library/LaunchAgents/com.threadvault.maintenance.plist" 2>/dev/null || true
  launchctl unload "$HOME/Library/LaunchAgents/com.threadvault.consultselftest.plist" 2>/dev/null || true
  [ "$WITH_TUNNEL" = "1" ] && launchctl unload "$HOME/Library/LaunchAgents/com.threadvault.tunnel.plist" 2>/dev/null || true

  launchctl load -w "$HOME/Library/LaunchAgents/com.threadvault.bridge.plist"
  [ "$WITH_TUNNEL" = "1" ] && launchctl load -w "$HOME/Library/LaunchAgents/com.threadvault.tunnel.plist"
  launchctl load -w "$HOME/Library/LaunchAgents/com.threadvault.maintenance.plist"
  launchctl load -w "$HOME/Library/LaunchAgents/com.threadvault.consultselftest.plist"
}

import_threadsaves() {
  if [ -d "$THREADSAVES_DIR" ]; then
    log "Importing from Threadsaves at $THREADSAVES_DIR"
    python3 - <<PY
import os, re, shutil, pathlib
repo = pathlib.Path(os.environ['THREADVAULT_DIR'])
anc_dir = repo/'continuity'/'anchors'
zip_dir = repo/'archive'/'continuity_bundles'
anc_dir.mkdir(parents=True, exist_ok=True)
zip_dir.mkdir(parents=True, exist_ok=True)
root = os.environ['THREADSAVES_DIR']
anchor_re = re.compile(r'^Continuity_Anchor.*\.(md|pdf|txt|rtf)$', re.I)
zip_re    = re.compile(r'.*(thread|continuity).*\.zip$', re.I)
existing_anchors = { p.name.lower() for p in anc_dir.glob('*') if p.is_file() }
existing_zips    = { p.name.lower() for p in zip_dir.glob('*.zip') }
for r,_,fs in os.walk(root):
  for f in fs:
    if anchor_re.match(f) and f.lower() not in existing_anchors:
      shutil.copy2(os.path.join(r,f), anc_dir/f)
    if zip_re.match(f) and f.lower() not in existing_zips:
      shutil.copy2(os.path.join(r,f), zip_dir/f)
PY
    (cd "$THREADVAULT_DIR" && git add continuity/anchors archive/continuity_bundles && git commit -m "chore(import): threadsaves anchors/bundles" || true)
  else
    log "Threadsaves folder not found (skipping import)"
  fi
}

setup_keys_env() {
  local envfile="$HOME/.threadvault.env"
  if [ -f "$envfile" ]; then return 0; fi
  echo "Create provider keys file (~/.threadvault.env)? [y/N]"; read -r ans || true
  if [[ "$ans" =~ ^[Yy]$ ]]; then
    umask 077
    {
      echo "# ThreadVault provider keys"
      echo "# export ANTHROPIC_API_KEY=sk-ant-..."
      echo "# export MISTRAL_API_KEY=..."
      echo "# export OPENAI_API_KEY=sk-..."
      echo "# export GOOGLE_API_KEY=..."
      echo "# export OLLAMA_MODEL=mistral"
    } > "$envfile"
    log "Wrote $envfile (edit to add keys)"
  fi
}

setup_ollama() {
  if need_cmd ollama; then
    log "Ensuring Ollama daemon and local models..."
    if ! curl -sS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null; then
      nohup ollama serve >/tmp/ollama_serve.out 2>&1 &
      sleep 2
    fi
    IFS="," read -r -a models <<< "$PULL_MODELS"
    for m in "${models[@]}"; do
      ollama list | grep -q "^$m" || ollama pull "$m" || true
    done
  else
    log "Ollama not available (skipping local model setup)"
  fi
}

run_selftest() {
  cd "$THREADVAULT_DIR"
  SELFTEST_NOTIFY=1 system/bin/consult-selftest || true
}

main() {
  ensure_brew
  install_deps
  clone_or_update_repo
  setup_python
  ensure_bridge_token
  install_hooks
  install_launch_agents
  import_threadsaves
  setup_keys_env
  setup_ollama
  run_selftest
  log "Bootstrap complete."
  log "- Bridge health: curl http://127.0.0.1:8787/health"
  log "- Public URL (if tunnel enabled): curl http://127.0.0.1:8787/public-url"
  log "- Edit keys in ~/.threadvault.env for cloud providers"
}

main "$@"

