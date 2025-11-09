#!/usr/bin/env bash
set -euo pipefail
[[ -n "${GH_PAT:-}" ]] || { echo "❌ GH_PAT missing (add in Replit → Secrets)"; exit 1; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "❌ Not a git repo"; exit 1; }
echo "✅ GH_PAT present (${#GH_PAT} chars), repo OK"
git remote -v
