#!/usr/bin/env bash
# Setup labels using GitHub CLI (gh). Requires 'gh auth login' first.
# Usage: ./scripts/setup_labels_gh.sh your-org/your-repo
set -euo pipefail
REPO="${1:-}"
if [[ -z "$REPO" ]]; then
  echo "Usage: $0 owner/repo"
  exit 1
fi
FILE=".github/labels.yml"
if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI 'gh' not found. Install from https://cli.github.com/"
  exit 1
fi

while IFS= read -r line; do
  if [[ "$line" =~ ^-\ name:\ (.*)$ ]]; then
    name="${BASH_REMATCH[1]}"
    read -r line; color="${line#*color: }"
    read -r line; description="${line#*description: }"
    gh label create "$name" --color "${color#\#}" --description "$description" --repo "$REPO" 2>/dev/null ||     gh label edit "$name" --color "${color#\#}" --description "$description" --repo "$REPO"
  fi
done < "$FILE"

echo "✅ Labels synced to $REPO"
