#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   scripts/release/bump_and_tag_auto.sh [--level patch|minor|major] [--explicit vX.Y.Z]
#   If NEXT_VERSION file exists, it overrides both.

LEVEL="patch"
EXPLICIT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --level) LEVEL="${2:-patch}"; shift 2;;
    --explicit) EXPLICIT="${2:-}"; shift 2;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

# Compute new version
if [ -n "$EXPLICIT" ]; then
  NEW_TAG="$EXPLICIT"
else
  NEW_TAG="$(python3 scripts/release/next_version.py --level "$LEVEL" ${EXPLICIT:+--explicit "$EXPLICIT"})"
fi

echo "==> Auto-bumping to ${NEW_TAG}"

# Write VERSION
echo "${NEW_TAG}" > VERSION

# Refresh badges
if [ -f scripts/update_readme_docs_badges.py ]; then
  python3 scripts/update_readme_docs_badges.py || true
elif [ -f scripts/badges/update_readme_badges.py ]; then
  SB_OWNER="${OWNER:-m9dswyptrn-web}" SB_REPO="${REPO:-SonicBuilder}" \
  python3 scripts/badges/update_readme_badges.py || true
fi

# Generate release notes for the upcoming tag
python3 scripts/release/gen_changelog.py || true

# Commit & push
git add -A
git commit -m "release: ${NEW_TAG} (auto-bump ${LEVEL}) + badges/changelog" || echo "No changes to commit."
git push || true

# Tag if needed and push tag
if git rev-parse -q --verify "refs/tags/${NEW_TAG}" >/dev/null; then
  echo "Tag ${NEW_TAG} already exists. Skipping tag creation."
else
  git tag "${NEW_TAG}"
fi
git push --tags

echo "==> Done. Actions will build and release ${NEW_TAG}."
