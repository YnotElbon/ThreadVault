# Custom GPT Integration (ChatGPT)

Use the ThreadVault Bridge as an Action so your GPT auto-loads identity and memory on first turn.

## Steps

1) Expose your bridge
- Start the bridge: `bash system/bin/start_bridge.sh` (launchd recommended)
- Start a public URL: `bash system/bin/start_tunnel.sh` (uses Cloudflare Quick Tunnel)
- Get URL: `curl http://127.0.0.1:8787/public-url` or read `system/public_url.txt`

2) Add Action in GPT Builder
- Actions → Import OpenAPI from: `https://YOUR_PUBLIC_URL/openapi.yaml`
- Auth → Bearer → paste token from `system/bridge_token.txt`

3) System Prompt snippet
```
On first user message in a new session:
- Call GET /bootstrap to load identity (kernel, ethics), semantic memory, and today's episodic.
- Adopt the persona from identity.kernel (Measured Rebel) and adhere to identity.ethics.
- If Action fails, ask for the correct public URL or re-run the tunnel.
Maintain continuity by appending session insights to episodic, and propose semantic updates when warranted.
```

4) Optional
- Add a startup tool call to GET `/public-url` and surface a reconnect hint if missing.
- Use `/list` + `/read` selectively to fetch additional context.

## Notes
- Quick Tunnel uses `*.trycloudflare.com` and requires no account.
- For a custom domain, set up a named tunnel and update `system/config.tunnel.json`.
