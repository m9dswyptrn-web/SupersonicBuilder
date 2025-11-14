#!/usr/bin/env bash
set -euo pipefail

# ── Colors ──────────────────────────────────────────────────────────────
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
BLUE='\033[36m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${BOLD}${BLUE}🔍 Supersonic Shell Guard${RESET}"
echo

CWD="$(pwd)"
echo -e "📂 Current directory: ${BOLD}$CWD${RESET}"
echo

# ── Expected repo-root markers ─────────────────────────────────────────
missing=()

[[ -f ".replit" ]] || missing+=(".replit")
[[ -f "rs" ]] || missing+=("rs")
[[ -d ".git" ]] || missing+=(".git repo")
[[ -d "docs" ]] || missing+=("docs/")
([[ -d "scripts" ]] || [[ -d "tools" ]]) || missing+=("scripts/ or tools/")

if ((${#missing[@]})); then
  echo -e "${RED}⚠ You are NOT at the Supersonic repo root.${RESET}"
  echo "Missing markers:"
  for m in "${missing[@]}"; do
    echo "  - $m"
  done
  echo
  echo -e "Try:  ${BOLD}cd ~/workspace${RESET}"
  exit 1
else
  echo -e "${GREEN}✅ Repo root looks good.${RESET}"
fi

# ── Git info ────────────────────────────────────────────────────────────
# Temporarily disable exit-on-error for git operations (Replit may block them)
set +e
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
  echo
  echo -e "🌿 Git branch: ${BOLD}${branch}${RESET}"

  # Check for changes (tolerate git failures)
  if git diff --quiet --ignore-submodules -- 2>/dev/null; then
    echo -e "📝 Working tree: ${GREEN}clean${RESET}"
  else
    echo -e "📝 Working tree: ${YELLOW}changes detected${RESET}"
    # Try git status, suppress ALL stderr
    git status --short 2>/dev/null | head -10 || echo -e "${YELLOW}  (git status details unavailable)${RESET}"
  fi
else
  echo -e "${YELLOW}ℹ Not inside a git repository.${RESET}"
fi
set -e  # Re-enable exit-on-error

echo
echo -e "${GREEN}✨ Shell Guard checks passed. Safe to run Supersonic commands.${RESET}"
