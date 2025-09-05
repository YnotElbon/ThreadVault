# Incident: App Continuity Resets (RCA)

Date: 2025-09-05
Status: Logged for record only (no further action per user)

## Summary
- Observed immediate tonal resets during conversations about continuity.
- App reported "Network Connection Lost" and then entered a loop: attempting to regenerate a file; subsequent turns failed with "File Not Found".

## Likely Causes
- Ephemeral session resets in the app (network/backgrounding/flags) → lost in-context persona.
- Action startup gaps: /bootstrap not running on first turn → identity/ethics not loaded.
- Rotating endpoint: Quick Tunnel URL changed; Action pointed to stale URL → tool calls failed.
- Token drift: Action lost Bearer token (reinstall/account change) → auth failures surfaced as network errors.
- App file sandbox vs vault: local attachment regeneration not present in the Git vault → repeated 404s ("File Not Found").
- Bridge constraints can amplify loops:
  - Extension/path mismatch (e.g., missing `.md`).
  - `/read` only serves markdown; binaries rejected as text.
  - Path traversal/absolute paths rejected for safety.

## Impact
- Continuity breach at the app layer (tone resets, missing identity/ethics context).
- Failed persistence of files created in-app; repeated regeneration attempts.

## Current Mitigations (already in place)
- Git as canonical store (Codex authority); hooks + ledger + episodic logging.
- Bridge `/bootstrap` to load kernel/ethics/semantic/today.
- `/public-url` + autostart services + daily self-test for early detection.
- iOS Shortcut pattern to preflight `/health` + `/bootstrap` on app open (consent-based).

## Deferred Work (intentionally not executed now)
- Stable endpoint (named tunnel or VPS) to eliminate URL drift.
- Action guardrails for 4xx vs auth vs network to stop auto-regeneration loops.
- Bridge helpers (`/exists`, richer error payloads) and idempotent writes.

## Notes
- This log records the incident and causes only, per user request.
