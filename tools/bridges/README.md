# ThreadVault Bridge (FastAPI)

Give a GPT Action **safe edit permissions** to a *restricted* portion of your Obsidian vault.

## Install

1. Ensure Python 3.10+.
2. `pip install fastapi uvicorn pydantic[dotenv] python-multipart` (or create a venv).
3. Copy `.env.example` to `.env` (or export env vars) and set:
   - `THREADVAULT_BASE` → absolute path to your `ThreadVault/`
   - `API_TOKEN` → long random secret
4. Run: `uvicorn fastapi_app:app --host 0.0.0.0 --port 8787`

> **Tip:** Keep it private. If you need remote access for GPT Actions, put this behind a secure tunnel (Cloudflare Tunnel / Tailscale Funnel) and require the bearer token.

## Endpoints

- `GET /health` – check service
- `GET /list?subdir=anchors` – list files under a subfolder
- `GET /read?path=anchors/continuity_manifest.md` – read markdown
- `POST /write` – replace/create markdown (`{"path":"anchors/file.md","content":"..."}`)
- `POST /append` – append markdown
- `POST /insert-under-heading` – add content under a specific heading
- `POST /backup` – zip the entire ThreadVault into `Backups/`

## Connect as a GPT Action

- Host `openapi.yaml` at `https://YOUR_PUBLIC_HOSTNAME/openapi.yaml` (same server or static hosting).
- In the GPT builder, add an Action and point it at the OpenAPI URL.
- Choose **Bearer** auth and paste the `API_TOKEN`.

## Safety Defaults

- Path traversal is blocked.
- Only files under `THREADVAULT_BASE` are touched.
- All writes are logged at `ThreadVault/_bridge_logs/actions.log`.
- PDFs are ignored on write; this is a markdown-first bridge.

