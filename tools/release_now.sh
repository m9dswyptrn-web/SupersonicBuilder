#!/usr/bin/env bash
set -euo pipefail

BRANCH="${BRANCH:-main}"
PUSH_BRANCH=0
BUMP="patch"
EXPLICIT_TAG=""
PRE_ID=""

latest_tag() {
  git fetch --tags >/dev/null 2>&1 || true
  git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0"
}

parse_base() {
  local base="${1#v}"; base="${base%%-*}"
  IFS='.' read -r MA MI PA <<<"${base:-0.0.0}"
  echo "${MA:-0} ${MI:-0} ${PA:-0}"
}

bump() {
  local ma="$1" mi="$2" pa="$3" kind="$4"
  case "$kind" in
    major) echo "$((ma+1)).0.0" ;;
    minor) echo "$ma.$((mi+1)).0" ;;
    patch) echo "$ma.$mi.$((pa+1))" ;;
    *) echo "$ma.$mi.$pa" ;;
  esac
}

usage() {
  cat <<EOF
Usage:
  tools/release_now.sh [--patch|--minor|--major] [--pre rc.1] [--tag vX.Y.Z] [--push-branch]

Examples:
  tools/release_now.sh --patch
  tools/release_now.sh --minor --push-branch
  tools/release_now.sh --tag v2.4.0
Env:
  GH_PAT   fine-grained token (Read/Write to repo)
  BRANCH   branch to push (default: main)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --patch) BUMP="patch"; shift ;;
    --minor) BUMP="minor"; shift ;;
    --major) BUMP="major"; shift ;;
    --pre)   PRE_ID="${2:-}"; shift 2 ;;
    --tag)   EXPLICIT_TAG="${2:-}"; shift 2 ;;
    --push-branch) PUSH_BRANCH=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

LATEST="$(latest_tag)"
read -r MA MI PA <<<"$(parse_base "$LATEST")"

if [[ -n "$EXPLICIT_TAG" ]]; then
  NEXT="${EXPLICIT_TAG#v}"
else
  NEXT="$(bump "$MA" "$MI" "$PA" "$BUMP")"
fi

[[ -n "$PRE_ID" ]] && NEXT="${NEXT}-${PRE_ID}"
NEXT_TAG="v${NEXT}"

if git rev-parse "$NEXT_TAG" >/dev/null 2>&1; then
  echo "✅ ${NEXT_TAG} already exists. Nothing to do."
  exit 0
fi

git fetch --tags >/dev/null 2>&1 || true
git tag -a "$NEXT_TAG" -m "SupersonicBuilder $NEXT_TAG"

source "$(dirname "$0")/gh.sh"
with_auth_remote bash -c "
  git push origin '${NEXT_TAG}'
  [[ ${PUSH_BRANCH} -eq 1 ]] && git push origin '${BRANCH}:${BRANCH}' || true
"

echo "🎉 Released ${NEXT_TAG}"
