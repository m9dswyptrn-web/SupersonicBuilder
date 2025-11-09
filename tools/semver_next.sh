#!/usr/bin/env bash
set -euo pipefail
bump="${1:-patch}"

# Find latest v*-style tag, default to v0.1.0 if none
latest="$(git tag --list 'v*' --sort=-v:refname | head -n1 || true)"
if [[ -z "${latest}" ]]; then latest="v0.1.0"; fi

# Strip leading v and split
ver="${latest#v}"
IFS='.' read -r major minor patch <<< "$ver"

case "$bump" in
  major) major=$((major+1)); minor=0; patch=0 ;;
  minor) minor=$((minor+1)); patch=0 ;;
  patch|*) patch=$((patch+1)) ;;
esac

echo "v${major}.${minor}.${patch}"
