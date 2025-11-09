#!/usr/bin/env bash
# deploy.sh — Supersonic one-shot deploy helper
# Chains: preflight -> (optional) postinstall -> snapshot (full project) -> push
# Safe to run on Replit. Requires git & Python available in shell.
#
# Environment overrides (optional):
#   GIT_REMOTE_URL="https://github.com/<owner>/<repo>.git"   # used by preflight --fix if missing origin
#   ZIP_EXCLUDES=".git,__pycache__,node_modules,build,dist"   # extra excludes for snapshot
#   SNAPSHOT_NAME="SonicBuilder_SUPERSONIC_SNAPSHOT.zip"      # custom snapshot name
#   SKIP_POSTINSTALL=1                                        # skip wiring health/sync/logging
#   PREFLIGHT_FIX=1                                           # allow preflight to apply fixes (git user/origin)
#   PREFLIGHT_PUSH=1                                          # use preflight to execute push sequence
#   QUIET=1                                                   # reduce output
set -euo pipefail

header(){ printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
note(){   if [[ -z "${QUIET:-}" ]]; then printf "  - %s\n" "$*"; fi; }
run(){    if [[ -z "${QUIET:-}" ]]; then printf "\033[2m$ %s\033[0m\n" "$*"; fi; bash -lc "$*"; }

# Sanity checks
if ! command -v python3 >/dev/null 2>&1; then echo "[ERROR] python3 not found"; exit 2; fi
if ! command -v git >/dev/null 2>&1; then echo "[ERROR] git not found"; exit 2; fi

# Ensure required scripts are present
for f in supersonic_preflight.py supersonic_post_install.py; do
  if [[ ! -f "$f" ]]; then
    echo "[ERROR] Missing $f in current directory."; exit 2
  fi
done

header "1) Preflight checks"
if [[ -n "${PREFLIGHT_FIX:-}" ]]; then
  note "Running preflight with --fix (may set git user/email and add origin)…"
  run 'python3 supersonic_preflight.py --fix'
else
  run 'python3 supersonic_preflight.py'
fi

if [[ -z "${SKIP_POSTINSTALL:-}" ]]; then
  header "2) Post-install wiring (health/sync/logging)"
  run 'python3 supersonic_post_install.py'
else
  header "2) Post-install wiring (skipped)"
fi

header "3) Full-project snapshot"
if [[ -n "${ZIP_EXCLUDES:-}" ]]; then
  export ZIP_EXCLUDES
fi
if [[ -n "${SNAPSHOT_NAME:-}" ]]; then
  run 'python3 supersonic_post_install.py --zip "${SNAPSHOT_NAME}"'
else
  run 'python3 supersonic_post_install.py --zip'
fi

header "4) Push to GitHub"
if [[ -n "${PREFLIGHT_PUSH:-}" ]]; then
  note "Using preflight --push sequence for commit/push…"
  run 'python3 supersonic_preflight.py --push'
else
  # Manual sequence mirrors preflight recommendations
  run 'git add -A'
  run 'git status --porcelain || true'
  run 'git commit -m "[sync] supersonic snapshot $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true'
  run 'git fetch --prune || true'
  run 'git pull --rebase --autostash || git merge --no-edit || true'
  CURRENT_BRANCH="$(git branch --show-current || echo main)"
  run 'git push --set-upstream origin '"$CURRENT_BRANCH"
fi

header "Done 🚀"
echo "Snapshot + push completed."
