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

# Commit and push if there are changes
git add -A || true
if ! git diff --cached --quiet; then
  git commit -m "chore(memory): daily sync and backup" || true
  git push origin $(git rev-parse --abbrev-ref HEAD) || true
fi

exit 0

