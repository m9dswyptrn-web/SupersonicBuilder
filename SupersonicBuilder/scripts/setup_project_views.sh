#!/usr/bin/env bash
# setup_project_views.sh — create/update saved views for a GitHub Project (beta)
# Requires: gh CLI logged in (gh auth login) and 'project' access.
# Usage:
#   ./scripts/setup_project_views.sh .github/project_views.json
set -euo pipefail

CFG_JSON="${1:-.github/project_views.json}"
if [[ ! -f "$CFG_JSON" ]]; then
  echo "Config JSON not found: $CFG_JSON"
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI 'gh' not found. Install from https://cli.github.com/"
  exit 1
fi

# Extract org and project number from URL
URL=$(jq -r '.project_url' "$CFG_JSON")
if [[ ! "$URL" =~ projects/([0-9]+)$ ]]; then
  echo "Invalid project_url in JSON; expected .../projects/<number>"
  exit 1
fi
NUM="${BASH_REMATCH[1]}"
ORG=$(echo "$URL" | sed -E 's#https://github.com/orgs/([^/]+)/projects/.*#\1#')

echo "Using org=$ORG project_number=$NUM"

# GraphQL helpers
read -r -d '' GET_PROJ <<'GQL' || true
query($org:String!,$number:Int!){
  organization(login:$org){
    projectV2(number:$number){
      id
      views(first:50){ nodes{ id name } }
    }
  }
}
GQL

read -r -d '' CREATE_VIEW <<'GQL' || true
mutation($projectId:ID!,$name:String!,$filter:String){
  createProjectV2View(input:{projectId:$projectId,name:$name,filter:$filter}){
    view{ id name }
  }
}
GQL

read -r -d '' UPDATE_VIEW <<'GQL' || true
mutation($viewId:ID!,$name:String,$filter:String){
  updateProjectV2View(input:{projectViewId:$viewId,name:$name,filter:$filter}){
    projectView{ id name }
  }
}
GQL

# Fetch project + existing views
PROJ_JSON=$(gh api graphql -f query="$GET_PROJ" -F org="$ORG" -F number="$NUM")
PROJ_ID=$(echo "$PROJ_JSON" | jq -r '.data.organization.projectV2.id')
echo "Project ID: $PROJ_ID"

# Iterate desired views from config
LEN=$(jq '.views | length' "$CFG_JSON")
for ((i=0; i<LEN; i++)); do
  NAME=$(jq -r ".views[$i].name" "$CFG_JSON")
  FILTER=$(jq -r ".views[$i].filter" "$CFG_JSON")

  EXIST_ID=$(echo "$PROJ_JSON" | jq -r --arg n "$NAME" '.data.organization.projectV2.views.nodes[] | select(.name==$n) | .id' || true)

  if [[ -z "$EXIST_ID" ]]; then
    echo "Creating view: $NAME"
    gh api graphql -f query="$CREATE_VIEW" -F projectId="$PROJ_ID" -F name="$NAME" -F filter="$FILTER" >/dev/null || {
      echo "⚠️  Create failed (API may change). You can create '$NAME' manually with filter: $FILTER"
    }
  else
    echo "Updating view: $NAME"
    gh api graphql -f query="$UPDATE_VIEW" -F viewId="$EXIST_ID" -F name="$NAME" -F filter="$FILTER" >/dev/null || {
      echo "⚠️  Update failed (API may change). You can edit '$NAME' manually with filter: $FILTER"
    }
  fi
done

echo "✅ Views processed. If some failed, open the Project UI and set filters manually."
