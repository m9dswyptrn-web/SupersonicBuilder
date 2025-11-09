#!/usr/bin/env bash
set -euo pipefail
MSG="${1:-chore: update}"
git add -A
if ! git diff --cached --quiet; then
  git commit -m "$MSG"
else
  echo "No changes to commit."
fi
