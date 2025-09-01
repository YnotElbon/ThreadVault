# Security Follow-up Reminder (Due: 2025-09-08)

Actions to address leaked/unstable secrets and hygiene:

- Rotate bridge API token and restart bridge
- Ensure token is not tracked; keep in `system/bridge_token.txt` (gitignored)
- Consider Keychain-backed secret retrieval in `start_bridge.sh`
- Optional: purge token from git history (BFG or git filter-repo)
- Review backups for sensitive data and retention policy

Context: User requested to defer fixes for one week. This is a scheduled reminder to complete them.
