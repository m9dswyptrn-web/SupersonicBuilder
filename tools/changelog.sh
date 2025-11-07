#!/usr/bin/env bash
set -euo pipefail

VER="${1:-}"
if [[ -z "$VER" ]]; then
  echo "Usage: $0 vMAJOR.MINOR.PATCH" >&2
  exit 2
fi

# Previous tag (if any)
PREV_TAG="$(git describe --tags --abbrev=0 --match 'v*' 2>/dev/null || true)"
RANGE=""
if [[ -n "$PREV_TAG" ]]; then
  RANGE="${PREV_TAG}..HEAD"
else
  ROOT="$(git rev-list --max-parents=0 HEAD | tail -n1)"
  RANGE="${ROOT}..HEAD"
fi

DATE="$(date -u +'%Y-%m-%d')"

# Collect commits (subject line only)
COMMITS="$(git log --pretty=format:'- %s (%h)' $RANGE || true)"

# Fallback if empty (e.g., tag only)
if [[ -z "$COMMITS" ]]; then
  COMMITS="- Version bump and maintenance"
fi

# Prepend new section to CHANGELOG.md
TMP="$(mktemp)"
{
  echo "# Changelog"
  echo
  echo "## ${VER} — ${DATE}"
  echo
  echo "${COMMITS}"
  echo
  if [[ -f CHANGELOG.md ]]; then
    # Skip existing top header if present to avoid duplicates
    awk 'NR>1{print prev} {prev=$0}' CHANGELOG.md || true
  fi
} > "$TMP"

mv "$TMP" CHANGELOG.md
echo "CHANGELOG.md updated for ${VER}"
