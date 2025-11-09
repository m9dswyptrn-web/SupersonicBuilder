#!/usr/bin/env bash
set -euo pipefail
# tools/snapshot_all.sh — convenience wrapper around the installer --zip flag.

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
