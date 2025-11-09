#!/usr/bin/env bash
set -euo pipefail
BRANCH="${1:-main}"
source "$(dirname "$0")/gh.sh"
with_auth_remote bash -c "git push origin '${BRANCH}:${BRANCH}'"
echo "✅ Pushed ${BRANCH}"
