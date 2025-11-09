#!/usr/bin/env bash
# pages_watch.sh — poll GitHub Pages + badge endpoints until green

set -euo pipefail

GH_USER="${GH_USER:-m9dswyptrn-web}"
GH_REPO="${GH_REPO:-SonicBuilder}"
BASE="https://${GH_USER}.github.io/${GH_REPO}"

URLS=(
  "$BASE/"
  "$BASE/downloads/latest.pdf"
  "$BASE/docs/badges/pdf-health.json"
  "$BASE/docs/badges/pages-deploy.json"
  "$BASE/docs/badges/updated.json"
  "$BASE/docs/badges/downloads.json"
)

status() {
  local u="$1"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$u" || true)
  size=$(curl -sI "$u" | awk '/Content-Length/ {print $2}' | tr -d '\r')
  echo "$code $size $u"
}

echo "Watching GitHub Pages for ${BASE}"
echo "Press Ctrl+C to stop."
echo

while true; do
  echo "---- $(date -u +"%F %T UTC") ----"
  ok=1
  for u in "${URLS[@]}"; do
    read -r code size url < <(status "$u")
    icon="🟡"
    [[ "$code" == "200" ]] && icon="🟢"
    # Require nonzero size for latest.pdf
    if [[ "$url" == *"latest.pdf" ]]; then
      if [[ "$code" != "200" || -z "$size" || "$size" == "0" ]]; then icon="🔴"; ok=0; fi
    else
      [[ "$code" != "200" ]] && ok=0
    fi
    printf "%s  %-3s  %8s  %s\n" "$icon" "$code" "${size:-"-"}" "$url"
  done

  if [[ $ok -eq 1 ]]; then
    echo "✅ All endpoints healthy!"
  else
    echo "⏳ Not ready yet—retrying..."
  fi
  echo
  sleep 20
done
