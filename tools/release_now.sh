#!/usr/bin/env bash
set -euo pipefail

REL="${1:-v2.1.1}"

# Safety: delete existing tag locally & on remote if it exists
git tag -d "$REL" >/dev/null 2>&1 || true
git push origin :refs/tags/"$REL" || true

# Tag the current commit and push the tag (this triggers the workflow)
git tag -a "$REL" -m "SupersonicBuilder $REL"
git push origin "$REL"
