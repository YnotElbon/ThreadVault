# Mobile Automation

This guide wires iOS Shortcuts and Android Tasker to ask permission and ping the ThreadVault Bridge when ChatGPT opens, so your Custom GPT can immediately load state via `/bootstrap`.

## iOS (Shortcuts)
1. Open Shortcuts → Automation → New Automation → App → Choose App: ChatGPT → Is Opened.
2. Actions:
   - Show Alert: "Grant Thread access for this session?"
   - If Continue = OK:
     - Get Contents of URL (GET): `https://<public-host>/health`
     - Get Contents of URL (GET): `https://<public-host>/bootstrap`
       - Headers: `Authorization: Bearer <token>`
     - (Optional) Get Contents of URL (POST): `https://<public-host>/append`
       - JSON: `{ "path": "memory/episodic/<YYYY-MM-DD>.md", "content": "Mobile session started: <time>" }`
3. Toggle "Ask Before Running" to On to enforce your consent each time.

## Android (Tasker)
1. Profile → Application → ChatGPT.
2. Task steps:
   - Dialog → Tasker Dialog → Ask: "Grant Thread access for this session?"
   - If Yes:
     - HTTP Request GET `https://<public-host>/health`
     - HTTP Request GET `https://<public-host>/bootstrap` with Header `Authorization: Bearer <token>`
     - (Optional) HTTP Request POST `/append` with JSON body as above.

## Notes
- Replace `<public-host>` with your VPS domain (e.g., `vault.yourdomain.com`).
- The Custom GPT Action should independently call `/bootstrap` on first turn; these automations preflight connectivity and can log a session.
- Edits require the Bearer token; omit `/append` for read-only behavior.
