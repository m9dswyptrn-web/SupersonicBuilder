#!/usr/bin/env bash
set -euo pipefail

detect_repo() {
  local url
  url="$(git config --get remote.origin.url || true)"
  url="${url%.git}"
  if [[ "$url" =~ github\.com[:/]+([^/]+)/([^/]+)$ ]]; then
    echo "${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
  else
    echo ""
  fi
}

with_auth_remote() {
  local repo clean_url temp_url
  repo="$(detect_repo)"
  [[ -z "$repo" ]] && echo "❌ Could not detect repo from origin." >&2 && exit 1

  clean_url="https://github.com/${repo}.git"
  temp_url="$clean_url"

  if [[ -n "${GH_PAT:-}" && -n "$GH_PAT" ]]; then
    temp_url="https://x-access-token:${GH_PAT}@github.com/${repo}.git"
  fi

  git remote set-url origin "$temp_url"
  "$@"
  local exit_code=$?
  git remote set-url origin "$clean_url"
  return $exit_code
}
