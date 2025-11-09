#!/usr/bin/env bash
set -euo pipefail
ORG="${1:-}"
NAME="${2:-Sonic Kanban}"
if [[ -z "$ORG" ]]; then
  echo "Usage: $0 <org> \"<project name>\""
  exit 1
fi
NUM=$(gh project create "$NAME" --owner "$ORG" --format json | jq -r '.number')
echo "Created project #$NUM"
echo "URL: https://github.com/orgs/$ORG/projects/$NUM"
echo "If needed, add Status options: Backlog, In Progress, Review, Done"
echo "Update .github/project_config.json with the URL above."
