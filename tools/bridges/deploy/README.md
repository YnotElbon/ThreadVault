# VPS Deployment (Public Bridge)

This deploy runs the ThreadVault Bridge on a VPS and serves a public HTTPS URL (via your reverse proxy). The bridge reads/writes a Git clone of your vault, and (optionally) auto-commits/pushes changes.

## Option A: Docker Compose + Reverse Proxy

Prereqs:
- VPS with Docker + Docker Compose
- A domain or subdomain (e.g., `vault.yourdomain.com`)
- Reverse proxy (Caddy or Nginx) pointing to `localhost:8787`

Steps:
1. SSH to VPS and clone your repo:
   ```bash
   git clone https://github.com/YnotElbon/ThreadVault /opt/threadvault
   cd /opt/threadvault/tools/bridges/deploy
   ```
2. Prepare data volume with your vault content:
   ```bash
   mkdir -p data
   rsync -a --exclude='.git' ../../../../ /opt/threadvault/tools/bridges/deploy/data/
   cd /opt/threadvault/tools/bridges/deploy/data
   git init && git remote add origin https://github.com/YnotElbon/ThreadVault
   git fetch origin && git checkout -b main origin/main
   ```
3. Set API token and start:
   ```bash
   export API_TOKEN="<long-secret>"
   docker compose up -d --build
   curl -fsS http://127.0.0.1:8787/health
   ```
4. Reverse proxy (Caddy example):
   ```
   vault.yourdomain.com {
     reverse_proxy 127.0.0.1:8787
   }
   ```
   Or Nginx:
   ```
   server {
     listen 80; server_name vault.yourdomain.com;
     location / { proxy_pass http://127.0.0.1:8787; }
   }
   ```
5. Point ChatGPT Action at `https://vault.yourdomain.com/openapi.yaml` and use your token.

## Option B: Systemd (no Docker)

1. Install Python 3.11 and git
2. Clone repo to `/opt/threadvault` and create a venv
3. `pip install fastapi uvicorn`
4. `THREADVAULT_BASE=/opt/threadvault GIT_AUTO_COMMIT=true API_TOKEN=... uvicorn tools.bridges.fastapi_app:app --host 0.0.0.0 --port 8787`
5. Put it behind your reverse proxy as above.

## Sync Strategy
- Auto-commit/push: set `GIT_AUTO_COMMIT=true`. Every write/append/insert will: `git add -A && git commit && git push origin main`.
- Pull latest: call `POST /sync` (bearer auth) from your CI or webhook to fetch/reset to `origin/main`.

## Security
- Keep the Action token secret (set via VPS environment, not in repo).
- Restrict reverse proxy to HTTPS and, if possible, IP allowlists or an auth layer in front of the bridge.

## Notes
- The bridge filters file listings and blocks path traversal. It only edits under `THREADVAULT_BASE`.
- Health: `GET /health` should return `ok`.
