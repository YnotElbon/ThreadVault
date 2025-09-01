# Mobile Startup Automation Proposal (For Claude Review)

Date: 2025-09-01
Author: Codex CLI (Thread helper)

Goal: When the user opens ChatGPT on mobile, Thread’s state is fetched automatically (with an explicit permission prompt) so personality and context are loaded.

Summary:
- Use a Custom GPT Action that calls the public bridge `/bootstrap` on session start.
- On mobile, trigger a local OS automation that asks permission, then pings the bridge (optional) to log the session or pre-sync Git.
- Keep GitHub as the authoritative store for edits from Obsidian/Working Copy (iOS) or GitJournal (Android).

iOS (Shortcuts) flow:
1) Automation: “App Opened → ChatGPT” (Shortcuts)
2) Action chain:
   - Show Alert: “Grant Thread access for this session?” [Continue/Cancel]
   - If Continue: 
     - Get contents of URL: `GET https://<public-host>/health`
     - Get contents of URL: `GET https://<public-host>/bootstrap` with header `Authorization: Bearer <token>`
     - (Optional) POST a small note to episodic via `/append`
3) Result: The Custom GPT will also call `/bootstrap` on first turn; Shortcut preflight mainly verifies connectivity and can log the session.

Android (Tasker) flow:
1) Profile: Application → ChatGPT
2) Task:
   - Dialog → Ask: “Grant Thread access for this session?”
   - If Yes:
     - HTTP Request GET `https://<public-host>/health`
     - HTTP Request GET `https://<public-host>/bootstrap` with Bearer token
     - (Optional) HTTP Request POST `/append` to log the session

Consent mechanics:
- User explicitly taps Continue/Yes in the mobile automation.
- All API calls require the Bearer token.
- Edits (append/write) only happen if the automation includes them; otherwise read-only.

Open questions for Claude:
- Should we add an ephemeral, time‑boxed consent token to the bridge (accepted alongside the main token) to formalize “session consent”? 
- Do we want the bridge to create a minimal “mobile session started” entry automatically when `/bootstrap` is called with a `source=mobile` query param?
- Any concerns about calling `/bootstrap` twice (Shortcut preflight + GPT first turn)? Prefer a single source of truth?

If approved:
- I will add ready-to-import templates:
  - iOS Shortcuts: step-by-step import guide with screenshots and variables.
  - Android Tasker: XML export file in `mobile/templates/`.
- (Optional) Add `/mobile-session` endpoint to write an episodic entry with a standard format.

Current bridge endpoints used: `/health`, `/bootstrap`, `/append` (optional).
