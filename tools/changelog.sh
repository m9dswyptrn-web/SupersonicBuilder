#!/usr/bin/env bash
set -euo pipefail

VER="${1:-}"
if [[ -z "$VER" ]]; then
  echo "Usage: $0 vMAJOR.MINOR.PATCH" >&2
  exit 2
fi

# Find previous tag (vX.Y.Z). If none, use repo root.
PREV_TAG="$(git describe --tags --abbrev=0 --match 'v*' 2>/dev/null || true)"
if [[ -n "$PREV_TAG" ]]; then
  RANGE="${PREV_TAG}..HEAD"
else
  ROOT="$(git rev-list --max-parents=0 HEAD | tail -n1)"
  RANGE="${ROOT}..HEAD"
fi

DATE="$(date -u +'%Y-%m-%d')"
TMP="$(mktemp)"

# Buckets
declare -A SECT
SECT["feat"]=""
SECT["fix"]=""
SECT["perf"]=""
SECT["refactor"]=""
SECT["docs"]=""
SECT["test"]=""
SECT["build"]=""
SECT["ci"]=""
SECT["chore"]=""
SECT["revert"]=""
OTHER=""

# Collect commits
# Conventional format: type(scope)!: subject
# Example lines we’ll parse: "feat(ui): add dark card (#123) abc123"
git log --no-merges --pretty=format:'%h%x09%s' $RANGE | while IFS=$'\t' read -r HASH SUBJ; do
  # Strip PR refs like "(#123)" and trailing hashes
  CLEAN="$(echo "$SUBJ" | sed -E 's/\s*\(#([0-9]+)\)//g' | sed -E 's/\s+[a-f0-9]{7,}$//')"

  # Extract type, (optional) scope, breaking "!" flag, and title
  if [[ "$CLEAN" =~ ^([a-zA-Z]+)(\([^\)]+\))?(!)?:[[:space:]]*(.*)$ ]]; then
    TYPE="$(echo "${BASH_REMATCH[1]}" | tr '[:upper:]' '[:lower:]')"
    SCOPE="${BASH_REMATCH[2]}"
    BANG="${BASH_REMATCH[3]:-}"
    TITLE="${BASH_REMATCH[4]}"

    # Pretty scope
    if [[ -n "${SCOPE}" ]]; then
      SCOPE_STR="**${SCOPE:1:-1}:** "
    else
      SCOPE_STR=""
    fi

    LINE="- ${SCOPE_STR}${TITLE} (${HASH})"
    [[ -n "$BANG" ]] && LINE="${LINE} **[BREAKING]**"

    if [[ -n "${SECT[$TYPE]+x}" ]]; then
      SECT["$TYPE"]+="${LINE}"$'\n'
    else
      OTHER+="${LINE}"$'\n'
    fi
  else
    OTHER+="- ${CLEAN} (${HASH})"$'\n'
  fi
done

# Write file
{
  echo "# Changelog"
  echo
  echo "## ${VER} — ${DATE}"
  echo

  print_section() {
    local title="$1"; local key="$2"
    local body="${SECT[$key]}"
    if [[ -n "${body}" ]]; then
      echo "### ${title}"
      echo
      printf "%s" "${body}"
      echo
    fi
  }

  print_section "Features" "feat"
  print_section "Fixes" "fix"
  print_section "Performance" "perf"
  print_section "Refactors" "refactor"
  print_section "Documentation" "docs"
  print_section "Tests" "test"
  print_section "Build" "build"
  print_section "CI" "ci"
  print_section "Chores" "chore"
  print_section "Reverts" "revert"

  if [[ -n "${OTHER}" ]]; then
    echo "### Other"
    echo
    printf "%s" "${OTHER}"
    echo
  fi

  # Append the old changelog (skip its top title line if present)
  if [[ -f CHANGELOG.md ]]; then
    awk 'NR>1{print prev} {prev=$0}' CHANGELOG.md || true
  fi
} > "$TMP"

mv "$TMP" CHANGELOG.md
echo "CHANGELOG.md updated for ${VER}"
