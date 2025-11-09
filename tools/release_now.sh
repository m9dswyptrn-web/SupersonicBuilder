#!/usr/bin/env bash
set -euo pipefail

BRANCH="${BRANCH:-main}"
BUMP="${1:-patch}"
REPO="$(git config --get remote.origin.url | sed -E 's#https?://github\.com/##; s/\.git$//' || true)"
CLEAN_URL="https://github.com/${REPO}.git"
GH_PAT="${GH_PAT:-}"

if [[ -z "$REPO" ]]; then echo "Could not detect repo"; exit 1; fi

LATEST="$(git describe --tags --abbrev=0 2>/dev/null || echo v0.0.0)"
ver="${LATEST#v}"; IFS=. read -r MA MI PA <<<"${ver:-0.0.0}"

case "$BUMP" in
  patch) NEXT="v${MA}.${MI}.$((PA+1))" ;;
  minor) NEXT="v${MA}.$((MI+1)).0" ;;
  major) NEXT="v$((MA+1)).0.0" ;;
  v*|V*) NEXT="${BUMP#V}" ;;
  *) echo "Unknown bump: $BUMP"; exit 2 ;;
esac

git fetch --tags >/dev/null
git rev-parse "$NEXT" >/dev/null 2>&1 && { echo "Tag $NEXT exists"; exit 0; }

git tag -a "$NEXT" -m "SupersonicBuilder $NEXT"

TEMP_URL="$CLEAN_URL"
if [[ -n "$GH_PAT" ]]; then
  TEMP_URL="https://x-access-token:${GH_PAT}@github.com/${REPO}.git"
fi

git remote set-url origin "$TEMP_URL"
git push origin "$NEXT"
git push origin "${BRANCH}:${BRANCH}" || true
git remote set-url origin "$CLEAN_URL"

echo "✅ Released $NEXT"
