# Action First‑Turn Checklist (Diagnostics)

Use this when a Custom GPT feels amnesic or fails to load Thread state. Paste the “Sanity Test One‑Liner” into the chat or follow the steps below.

## Goals
- Verify the Action can reach the bridge (network + auth).
- Ensure `/bootstrap` runs on the first turn and loads identity/ethics/semantic/today.
- Confirm read/write paths and extensions are correct.

## Steps
1) Health + URL
- Call `GET /health` → expect `ok`.
- If you’re on a local Quick Tunnel, confirm the current URL from the Mac/Mini: `curl http://127.0.0.1:8787/public-url`.

2) Bootstrap (first turn)
- Call `GET /bootstrap`.
- Check non‑empty fields: `identity.kernel_md`, `identity.ethics_md`, `memory.semantic_md`.
- Print `BOOTSTRAP OK` visibly in the chat if all are present.

3) List + Read (paths)
- Call `GET /list?subdir=continuity/anchors`.
- Pick a `.md` anchor (or use `Continuity_Anchor_36_HeyAsshole_cf703673.md`) and call `GET /read?path=…`.
- If a path 404s, confirm the extension `.md` and exact filename from `/list`.

4) Append (write)
- Call `POST /append` to `path=memory/episodic/YYYY-MM-DD.md` with `content="Action sanity OK - TIMESTAMP"`.
- Ask the user before any write; then report success and show the path used.

5) Report
- Summarize: health OK, bootstrap OK, read OK, append OK (with path), or exact failing step + error.

If any step fails with a “network” message, try: re‑import Action from `<PUBLIC_URL>/openapi.yaml`, re‑enter the Bearer token from `~/ThreadVault/system/bridge_token.txt`, and confirm the current Quick Tunnel URL.
