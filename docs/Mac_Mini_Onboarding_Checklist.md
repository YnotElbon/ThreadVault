# Mac Mini Onboarding Checklist (ThreadVault)

This is a one‑shot, copy‑friendly checklist to bring a new Mac mini online with ThreadVault, fast. Quick Tunnel is enabled for rapid ChatGPT integration; evaluate longer‑term options (named tunnel or VPS) after the Mini is stable.

## 0) Prep
- macOS: Finish Setup Assistant, sign in Apple ID, run System Settings → General → Software Update.
- Dev tools: Run in Terminal: `xcode-select --install` (accept CLT install).
- Dropbox (optional): Install and sign in if using `~/Dropbox/Apps/Threadsaves`.

## 1) Core Install
- Homebrew:
  - `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
  - `eval "$(/opt/homebrew/bin/brew shellenv)"` (add to `~/.zshrc` for persistence)
- Clone + bootstrap:
  - `git clone https://github.com/YnotElbon/ThreadVault ~/ThreadVault`
  - `bash ~/ThreadVault/system/bin/bootstrap_mini.sh`

What this does:
- Installs: git, python, jq, cloudflared, ollama
- Repo: ~/ThreadVault with Git hooks installed
- Python venv + FastAPI/uvicorn
- Services (launchd): bridge (autostart), maintenance (daily backup/prune/push), consult self‑test (daily 03:05, notifications on FAIL)
- Quick Tunnel: enabled (public URL written to `system/public_url.txt`)
- Threadsaves import: pulls anchors/bundles from `~/Dropbox/Apps/Threadsaves` if present
- Ollama: pulls `mistral` and `llama3:8b` models

## 2) Provider Keys (Consult CLI)
- Edit `~/.threadvault.env` (bootstrap offers to create it):
  - `export ANTHROPIC_API_KEY=...` (Claude)
  - `export MISTRAL_API_KEY=...`
  - `export OPENAI_API_KEY=...`
  - `export GOOGLE_API_KEY=...`
  - `export OLLAMA_MODEL=mistral`
- Note: consult self‑test and launch agents source this automatically.

## 3) Verify Services
- Bridge health: `curl http://127.0.0.1:8787/health` → `ok`
- Public URL (Quick Tunnel): `curl http://127.0.0.1:8787/public-url`
- Self‑test: `~/ThreadVault/system/bin/consult-selftest` (PASS for configured providers; SKIP for unset; Ollama PASS if daemon running)
- Ollama: `ollama serve &; ollama pull mistral` (already pulled by bootstrap)

## 4) GitHub Auth (push from Mini)
- `brew install gh && gh auth login` (HTTPS + browser)
- Verify: `cd ~/ThreadVault && git fetch && git push`

## 5) Consult CLI (Cross‑Platform)
- Tool: `~/ThreadVault/system/bin/consult` (THE consult tool)
- Auto-pick: Claude → Mistral → OpenAI → Gemini → Ollama
- Examples:
  - `./system/bin/consult "sanity check"`
  - `./system/bin/consult -p anthropic "deep reasoning"`
  - `./system/bin/consult -p ollama -m mistral "offline check"`
- Continuity: Consults append to `memory/episodic/<today>.md`.

## 6) Mobile + ChatGPT Action
- Quick Tunnel URL: `curl http://127.0.0.1:8787/public-url`
- In ChatGPT Builder:
  - Actions → Import: `<PUBLIC_URL>/openapi.yaml`
  - Auth → Bearer → token in `~/ThreadVault/system/bridge_token.txt`
  - First‑turn instruction: call `GET /bootstrap` to load identity + memory
- Obsidian (Git‑based):
  - iOS: Working Copy → clone repo → Share as folder to Obsidian
  - Android: GitJournal/MGit → clone repo → open in Obsidian

## 7) Daily Ops
- Maintenance (02:15): backup/prune/push (launchd)
- Consult self‑test (03:05): logs PASS/FAIL to episodic, macOS notification on FAIL
- Bridge/Tunnel: autostart at login

## 8) Security & Next Steps
- Sep 8: Security reminder due (rotate token, ensure secrets untracked, consider history purge)
- Evaluate long‑term exposure:
  - Option A: Named Cloudflare Tunnel (stable domain)
  - Option B: VPS + HTTPS reverse proxy (Git‑synced vault, public OpenAPI)
  - Option C: Keep Quick Tunnel for convenience (be aware it’s public)

## 9) Troubleshooting
- Logs:
  - Bridge: `system/bridge_launchd.{out,err}.log`
  - Self‑test: `system/consultselftest.out.log`
- Episodic tail: `tail -n 80 memory/episodic/$(date +%F).md`
- Restart agents:
  - `launchctl unload -w ~/Library/LaunchAgents/com.threadvault.*.plist && launchctl load -w ~/Library/LaunchAgents/com.threadvault.*.plist`

---

Keep Quick Tunnel for fast start. After the Mini is stable for a day, evaluate and migrate to a named tunnel or VPS per Thread’s recommendation.
