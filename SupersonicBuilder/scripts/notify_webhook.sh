#!/usr/bin/env bash
set -euo pipefail

EVENT_TITLE="${1:-SonicBuilder}"
EVENT_TEXT="${2:-Notification}"
EVENT_URL="${3:-}"
COLOR="${4:-#36a64f}"   # Slack color; ignored by Discord

# JSON builders
slack_payload() {
  jq -n --arg t "$EVENT_TITLE" --arg m "$EVENT_TEXT" --arg u "$EVENT_URL" --arg c "$COLOR" '
  {
    "attachments":[
      {
        "fallback": $t,
        "color": $c,
        "title": $t,
        "title_link": ($u|length>0 ? $u : null),
        "text": $m
      }
    ]
  }'
}

discord_payload() {
  jq -n --arg t "$EVENT_TITLE" --arg m "$EVENT_TEXT" --arg u "$EVENT_URL" '
  {
    "embeds":[
      {
        "title": $t,
        "url": ($u|length>0 ? $u : null),
        "description": $m
      }
    ]
  }'
}

notify_slack() {
  [[ -z "${SLACK_WEBHOOK_URL:-}" ]] && return 0
  slack_payload | curl -fsSL -X POST -H 'Content-Type: application/json' -d @- "$SLACK_WEBHOOK_URL" >/dev/null || true
}

notify_discord() {
  [[ -z "${DISCORD_WEBHOOK_URL:-}" ]] && return 0
  discord_payload | curl -fsSL -X POST -H 'Content-Type: application/json' -d @- "$DISCORD_WEBHOOK_URL" >/dev/null || true
}

notify_slack
notify_discord
