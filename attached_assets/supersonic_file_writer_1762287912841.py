#!/usr/bin/env python3
"""
supersonic_file_writer.py
One-shot installer that writes a Makefile and tools/snapshot_all.sh into your CURRENT directory.
- Backs up existing files as <name>.bak.<UTC timestamp>
- Creates tools/ (if missing)
- Makes snapshot script executable

Usage:
  python3 supersonic_file_writer.py        # writes/updates files safely
  TARGET_DIR=/path/to/repo python3 supersonic_file_writer.py   # optional different target
"""
from pathlib import Path
from datetime import datetime
import os, stat

TARGET = Path(os.getenv("TARGET_DIR") or ".").resolve()
TOOLS = TARGET / "tools"

MAKEFILE = """
# Supersonic Make Kit (installed by supersonic_file_writer.py)

PY ?= python3
ZIP_EXCLUDES ?= .git,__pycache__,node_modules,.mypy_cache,.pytest_cache,.DS_Store

snapshot:
	@ZIP_EXCLUDES="$(ZIP_EXCLUDES)" $(PY) supersonic_post_install.py --zip

snapshot-name:
	@test -n "$(OUT)" || (echo "Usage: make snapshot-name OUT=<filename.zip>"; exit 2)
	@ZIP_EXCLUDES="$(ZIP_EXCLUDES)" $(PY) supersonic_post_install.py --zip "$(OUT)"

postinstall:
	@$(PY) supersonic_post_install.py

ping:
	@curl -s http://localhost:8000/api/ping | jq . || curl -s http://localhost:8000/api/ping

ready:
	@curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/ready

status:
	@curl -s http://localhost:8000/api/status | jq . || curl -s http://localhost:8000/api/status

sync:
	@curl -s -X POST http://localhost:8000/api/sync | jq . || curl -s -X POST http://localhost:8000/api/sync

log-tail:
	@mkdir -p logs; touch logs/app.log; tail -n 100 -f logs/app.log

bootlog-tail:
	@mkdir -p logs; touch logs/boot.log; tail -n 100 -f logs/boot.log

git-sync:
	@git add -A && git status --porcelain && \	if [ -n "$$(git status --porcelain)" ]; then \	  git commit -m "[sync] manual snapshot $$(date -u +%Y-%m-%dT%H:%M:%SZ)"; \	fi; \	git fetch --prune && \	git pull --rebase --autostash || git merge --no-edit && \	git push

.PHONY: snapshot snapshot-name postinstall ping ready status sync log-tail bootlog-tail git-sync
"""

SNAPSHOT_SH = """#!/usr/bin/env bash
set -euo pipefail
# tools/snapshot_all.sh — wraps the installer --zip flag.
ZIP_EXCLUDES_DEFAULT=".git,__pycache__,node_modules,.mypy_cache,.pytest_cache,.DS_Store"
OUT="${1:-}"

if [[ -z "${ZIP_EXCLUDES:-}" ]]; then
  export ZIP_EXCLUDES="${ZIP_EXCLUDES_DEFAULT}"
fi

if [[ -z "${OUT}" ]]; then
  python3 supersonic_post_install.py --zip
else
  python3 supersonic_post_install.py --zip "${OUT}"
fi

echo "Snapshot complete."
"""

def backup_if_exists(path: Path):
    if path.exists():
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        bak = path.with_name(path.name + f".bak.{ts}")
        path.replace(bak)
        return bak
    return None

def main():
    print(f"[INFO] Target: {TARGET}")
    TOOLS.mkdir(parents=True, exist_ok=True)

    mf = TARGET / "Makefile"
    bak = backup_if_exists(mf)
    mf.write_text(MAKEFILE, encoding="utf-8")
    print(f"[OK] Wrote {mf.relative_to(TARGET)}" + (f" (backup: {bak.name})" if bak else ""))

    sh = TOOLS / "snapshot_all.sh"
    bak2 = backup_if_exists(sh)
    sh.write_text(SNAPSHOT_SH, encoding="utf-8")
    sh.chmod(sh.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"[OK] Wrote {sh.relative_to(TARGET)}" + (f" (backup: {bak2.name})" if bak2 else ""))

    print("\nNext:\n  - Place this script in your repo root and run it once.\n  - Then `make snapshot` or `make snapshot-name OUT=My.zip`.\n  - Ensure `supersonic_post_install.py` exists in the same root.")

if __name__ == "__main__":
    main()
