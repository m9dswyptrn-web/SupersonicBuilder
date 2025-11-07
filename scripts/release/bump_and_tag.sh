#!/usr/bin/env bash
set -euo pipefail

NEW_TAG="${1:-v2.0.10}"
echo "==> Bumping to $NEW_TAG"

# 1) set VERSION
echo "$NEW_TAG" > VERSION

# 2) regenerate README badges if available
if [ -f scripts/update_readme_docs_badges.py ]; then
  python3 scripts/update_readme_docs_badges.py || true
elif [ -f scripts/badges/update_readme_badges.py ]; then
  SB_OWNER="${OWNER:-m9dswyptrn-web}" SB_REPO="${REPO:-SonicBuilder}" \
  python3 scripts/badges/update_readme_badges.py || true
fi

# 3) generate release notes
python3 scripts/release/gen_changelog.py || true

# 4) commit changes
git add -A
git commit -m "release: ${NEW_TAG} + badges/changelog" || echo "No changes to commit."

# 5) push main
git push || true

# 6) create tag if not exists
if git rev-parse -q --verify "refs/tags/${NEW_TAG}" >/dev/null; then
  echo "Tag ${NEW_TAG} already exists. Skipping tag creation."
else
  git tag "${NEW_TAG}"
fi

# 7) push tags
git push --tags

echo "==> Done. Actions will build + release docs and attach bundles."
echo "Open Actions: https://github.com/m9dswyptrn-web/SonicBuilder/actions"
