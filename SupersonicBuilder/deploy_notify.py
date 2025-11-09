#!/usr/bin/env python3
"""
Optional Slack/Discord ping after success.
Set one of:
  SLACK_WEBHOOK_URL or DISCORD_WEBHOOK_URL
Optional:
  SB_NOTIFY_TEXT
"""
import os, sys, requests

text = os.getenv("SB_NOTIFY_TEXT") or "🚀 SonicBuilder deploy complete! All workflows succeeded."
url  = os.getenv("SLACK_WEBHOOK_URL") or os.getenv("DISCORD_WEBHOOK_URL")

if not url:
    print("ℹ️ No webhook provided; skipping notification.")
    sys.exit(0)

r = requests.post(url, json={"text": text}, timeout=20)
print("📣 Notification sent.", r.status_code)
