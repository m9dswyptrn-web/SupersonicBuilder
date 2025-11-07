#!/bin/bash
set -euo pipefail
LARGE_FILE_MB=25
REPO_WARN_GIB=2
red(){ printf "\e[31m%s\e[0m\n" "$*"; }
grn(){ printf "\e[32m%s\e[0m\n" "$*"; }
ylw(){ printf "\e[33m%s\e[0m\n" "$*"; }
hdr(){ printf "\n\e[36m== %s ==\e[0m\n" "$*"; }
ISSUES=0
hdr "Repository & branch"
git rev-parse --is-inside-work-tree >/dev/null || { red "Not a git repo."; exit 2; }
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Branch: $BRANCH"
hdr "Remote origin"; git remote -v | sed 's/^/  /' || { ylw "No origin remote"; ISSUES=$((ISSUES+1)); }
hdr "Working tree"; git status -s || true
hdr "Sync vs origin/main"
git fetch origin main >/dev/null 2>&1 || ylw "Could not fetch origin/main (ok if first push)"
AHEAD=$(git rev-list --left-right --count HEAD...origin/main 2>/dev/null | awk '{print $1}')
BEHIND=$(git rev-list --left-right --count HEAD...origin/main 2>/dev/null | awk '{print $2}')
echo "Ahead: ${AHEAD:-N/A}  Behind: ${BEHIND:-N/A}"
[[ "${BEHIND:-0}" -gt 0 ]] && { ylw "Local is behind remote"; ISSUES=$((ISSUES+1)); }
hdr "Recent commits (local/remote)"
echo "-- local --";  git log --oneline -n 3 || true
echo "-- remote --"; git log origin/main --oneline -n 3 2>/dev/null || true
hdr "Tracked file size scan (> ${LARGE_FILE_MB} MB)"
FOUND_LARGE=0
while IFS= read -r f; do
  [[ -f "$f" ]] || continue
  sz=$(du -m "$f" | cut -f1)
  if [[ "$sz" -gt "$LARGE_FILE_MB" ]]; then
    echo "🚨 $f (${sz} MB)"; FOUND_LARGE=1
  fi
done < <(git ls-files)
[[ $FOUND_LARGE -eq 0 ]] && grn "No oversized tracked files" || ISSUES=$((ISSUES+1))
hdr ".git storage"
git count-objects -vH
PACK_DIR=".git/objects/pack"
if [[ -d "$PACK_DIR" ]]; then
  PACK_GIB=$(find "$PACK_DIR" -name '*.pack' -printf '%s\n' 2>/dev/null | awk '{s+=$1} END{printf "%.2f", s/1024/1024/1024}')
  echo "Pack size total: ${PACK_GIB:-0} GiB"
  if awk "BEGIN{exit !(${PACK_GIB:-0} > $REPO_WARN_GIB)}"; then ylw "Pack size > ${REPO_WARN_GIB} GiB"; ISSUES=$((ISSUES+1)); fi
fi
hdr "Result"
[[ $ISSUES -eq 0 ]] && { grn "✅ Git health looks good."; exit 0; } || { red "⚠️  Found $ISSUES issue(s)."; exit 1; }
