# Thread Static API Starter (No Server)
**Goal:** publish a read-only `anchors.json` describing your Obsidian continuity anchors so Thread can fetch them.

## TL;DR
1) Put your anchor `.md` files in `anchors/` (or point to wherever they live).  
2) Run:
```bash
python build_manifest.py --src ./anchors --out ./anchors.json --vault "YOUR_VAULT_NAME" --html ./index.html
```
3) Host `anchors.json` (and optional `index.html`) on **GitHub Pages** or **Dropbox**.  
4) Give Thread the public URL (e.g., `https://YOUR.github.io/thread-vault/anchors.json`).  

## Files
- `build_manifest.py` – generates `anchors.json` + optional `index.html` from your `.md` anchors.
- `.github/workflows/publish.yml` – GitHub Action to auto-regenerate and publish on push.
- `anchors/` – put sample anchor files here or point the script to your actual folder.

## One-time GitHub setup (simplest)
1. Create a new repo named `thread-vault`.
2. Add files from this zip. Put your anchor `.md` files into `anchors/`.
3. Commit & push.
4. In repo **Settings → Pages**, set:
   - **Build and deployment:** GitHub Actions
   - Once you push, the provided workflow publishes Pages automatically.
5. After it runs, your files will be at: `https://<you>.github.io/thread-vault/anchors.json`

## Dropbox alternative
- Put `anchors.json` in Dropbox.
- Right-click → **Copy link** → change `?dl=0` to `?dl=1`.
- Share that URL with Thread.

## Notes
- Security: treat the link as public. If you need to rotate, move to a new URL.
- Vault name must match Obsidian’s vault name exactly for the `obsidian://` links.

— Generated 2025-08-27
