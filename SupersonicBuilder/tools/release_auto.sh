#!/usr/bin/env bash
set -euo pipefail

# Usage: tools/release_auto.sh [--major|--minor|--patch]
# Default: --patch

bump="patch"
case "${1:-}" in
  --major) bump="major" ;;
  --minor) bump="minor" ;;
  ""|--patch) bump="patch" ;;
  *) echo "Unknown option: $1 (use --major | --minor | --patch)"; exit 1 ;;
esac

# Make sure we're up to date
git pull --rebase origin main >/dev/null || true

# Find latest tag like v1.2.3 (if none, seed v0.1.0)
latest="$(git tag -l 'v[0-9]*.[0-9]*.[0-9]*' --sort=-v:refname | head -n1 || true)"
if [[ -z "$latest" ]]; then
  major=0; minor=1; patch=0
else
  ver="${latest#v}"
  IFS='.' read -r major minor patch <<<"$ver"
fi

case "$bump" in
  major) major=$((major+1)); minor=0; patch=0 ;;
  minor) minor=$((minor+1)); patch=0 ;;
  patch) patch=$((patch+1)) ;;
esac

new="v${major}.${minor}.${patch}"

echo "Latest tag: ${latest:-<none>}"
echo "Bump: $bump  →  New tag: $new"

# Re-tag safely (delete if exists locally/remote)
git tag -d "$new" >/dev/null 2>&1 || true
git push origin ":refs/tags/$new" >/dev/null 2>&1 || true

# Create annotated tag and push (triggers Actions)
git tag -a "$new" -m "SupersonicBuilder $new"
git push origin "$new"

echo "✅ Pushed tag $new. GitHub Actions release should start shortly."
echo "Open: https://github.com/m9dswyptn-web/SupersonicBuilder/actions"
