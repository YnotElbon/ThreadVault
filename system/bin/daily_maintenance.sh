#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
cd "$ROOT_DIR"

# Run autorun validation (best-effort)
python3 system/autorun.py || true

# Create dated backup zip under Backups/
TS="$(date '+%Y-%m-%d_%H%M')"
BACKUPS_DIR="$ROOT_DIR/Backups"
mkdir -p "$BACKUPS_DIR"
ZIP_PATH="$BACKUPS_DIR/${TS}_ThreadVault.zip"

python3 - <<PY || true
import zipfile, pathlib, sys
base = pathlib.Path('.').resolve()
backups = base / 'Backups'
zip_path = pathlib.Path(sys.argv[1])
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for p in base.rglob('*'):
        if p.is_file():
            # Skip venv wheels, logs and existing backups
            if '.venv' in p.parts or '_bridge_logs' in p.parts or 'Backups' in p.parts:
                continue
            zf.write(p, p.relative_to(base))
print(str(zip_path))
PY
"$ZIP_PATH"

# Reminder: security follow-up after one week (2025-09-08)
TODAY="$(date '+%Y-%m-%d')"
DUE="2025-09-08"
if [[ "$TODAY" > "$DUE" || "$TODAY" == "$DUE" ]]; then
  echo "[REMINDER] Security follow-up due: rotate bridge token, ensure secrets untracked, consider history purge." | tee -a system/maintenance_launchd.out.log || true
  # Drop a marker file once (idempotent)
  mkdir -p system/reminders
  echo "$TODAY" > system/reminders/security_followup_due
fi

# Prune old backups (retain 30 days)
find "$BACKUPS_DIR" -type f -name "*_ThreadVault.zip" -mtime +30 -print -delete || true

# Commit and push if there are changes
git add -A || true
if ! git diff --cached --quiet; then
  git commit -m "chore(memory): daily sync and backup" || true
  git push origin $(git rev-parse --abbrev-ref HEAD) || true
fi

exit 0
