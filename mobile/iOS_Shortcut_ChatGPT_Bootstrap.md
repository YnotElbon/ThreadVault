# iOS Shortcut: ChatGPT → ThreadVault Bootstrap (iPad)

This Shortcut runs when you open ChatGPT on iPad, asks permission, then calls the ThreadVault Bridge to preflight connectivity and optionally log the session.

## Prereqs
- Your Mac/Mini is running the bridge and tunnel (Quick Tunnel or VPS).
- You know the PUBLIC URL and have the Bearer token.

## Steps (Shortcuts app)
1) Automation → New Automation → App → Choose App: ChatGPT → Is Opened → Next → Add Action
2) Action: Show Alert
   - Title: “Grant Thread access for this session?”
   - Buttons: Continue / Cancel
3) Action: If [Alert Result] is Continue
   - Get Contents of URL
     - Method: GET
     - URL: `https://<PUBLIC_HOST>/health`
   - Get Contents of URL
     - Method: GET
     - URL: `https://<PUBLIC_HOST>/bootstrap`
     - Headers: `Authorization: Bearer <TOKEN>`
   - (Optional) Get Contents of URL
     - Method: POST
     - URL: `https://<PUBLIC_HOST>/append`
     - Headers: `Authorization: Bearer <TOKEN>`, `Content-Type: application/json`
     - Request Body (JSON):
       {
         "path": "memory/episodic/[[YYYY-MM-DD]].md",
         "content": "Mobile session started: [[HH:mm]]"
       }
4) Toggle “Ask Before Running” ON (so you consent each time).
5) Save.

Notes
- Replace `<PUBLIC_HOST>` with your current Quick Tunnel/VPS host.
- Use variables in Shortcuts for date/time or keep static.
- Your Custom GPT should still call /bootstrap on first turn; this shortcut preflights and can log the session.

Troubleshooting
- If /bootstrap fails, refresh the public URL on the Mac/Mini: `curl http://127.0.0.1:8787/public-url`.
- Confirm the token matches `~/ThreadVault/system/bridge_token.txt`.
