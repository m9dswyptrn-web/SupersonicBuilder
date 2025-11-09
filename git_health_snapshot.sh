#!/usr/bin/env bash
set -euo pipefail

LARGE_FILE_MB=25
REPO_WARN_GIB=0.75

cyn(){ printf "\033[36m%s\033[0m\n" "$*"; }
grn(){ printf "\033[32m%s\033[0m\n" "$*"; }
ylw(){ printf "\033[33m%s\033[0m\n" "$*"; }
red(){ printf "\033[31m%s\033[0m\n" "$*"; }

cyn "== Working tree =="
git status --short || true

cyn "== Sync vs origin/main =="
git fetch --quiet origin main || true
git --no-pager log --oneline -n 2 --decorate --all | sed 's/^/  /'

cyn "== Tracked file size scan (> ${LARGE_FILE_MB} MB) =="
ISSUES=0
FOUND_LARGE=0
while IFS= read -r f; do
  [[ -f "$f" ]] || continue
  sz=$(du -m "$f" | cut -f1)
  if [[ "$sz" -gt "$LARGE_FILE_MB" ]]; then
    echo "  🚨 $f (${sz} MB)"; FOUND_LARGE=1
  fi
done < <(git ls-files)
[[ $FOUND_LARGE -eq 0 ]] && grn "No oversized tracked files" || ISSUES=$((ISSUES+1))

cyn "== git storage =="
git count-objects -vH

PACK_DIR=".git/objects/pack"
PACK_GiB=0
if [[ -d "$PACK_DIR" ]]; then
  PACK_GiB=$(find "$PACK_DIR" -name '*.pack' -printf '%s\n' 2>/dev/null | \
             awk 'BEGIN{s=0}{s+=$1}END{printf "%.2f", s/1024/1024/1024}')
fi
echo "Pack size total: ${PACK_GiB} GiB"
awk "BEGIN{exit !(${PACK_GiB:-0} > ${REPO_WARN_GIB})}" && {
  ylw "Pack size > ${REPO_WARN_GiB} GiB"; ISSUES=$((ISSUES+1));
} || true

cyn "== Result =="
if [[ $ISSUES -eq 0 ]]; then grn "✅ Git health looks good."
else red "⚠️  Found $ISSUES issue(s)."
fi
