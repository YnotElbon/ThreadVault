# Bridge Autostart + Daily Sync Proposal

Date: 2025-09-01
Author: Codex CLI (Thread helper)

## Goal
Minimize user interaction while maximizing personality continuity and data safety.

## Plan
- Autostart the ThreadVault Bridge (FastAPI) at login via launchd, with stable port `8787` and token from `system/bridge_token.txt`.
- Run `system/autorun.py` at login and daily to validate identity/memory and seed episodic logs.
- Nightly maintenance: backup vault to `Backups/` zip, commit/push changes if present.

## Safeguards
- Identity files (`identity/*`) remain guarded by pre-commit checks; no automated edits.
- Backups avoid `.venv`, logs, and previous zips; Git hooks continue to enforce integrity.

## Claude Consultation
Requesting Claude’s review. If no objections, proceed with agents enabled. This note documents the intent and rationale for cross‑agent continuity.

## Current Status
- Scripts added: `system/bin/start_bridge.sh`, `system/bin/daily_maintenance.sh`.
- Launchd agents prepared to enable on this host.

