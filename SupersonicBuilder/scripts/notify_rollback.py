#!/usr/bin/env python3
"""
Rollback Notification Script
Sends Discord/Slack notifications for deployment events
"""

import os
import requests
from datetime import datetime

def notify(message, level="info"):
    """Send a formatted message to Discord/Slack webhook"""
    webhook_url = os.getenv("ROLLBACK_WEBHOOK_URL")
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    
    # Use Discord or Slack webhook (Discord takes priority)
    target_webhook = webhook_url or slack_webhook
    
    if not target_webhook:
        print("⚠️  No webhook URL configured — skipping notification")
        return

    timestamp = datetime.utcnow().isoformat()
    emoji = {"info": "🟢", "warn": "🟡", "error": "🔴"}.get(level, "ℹ️")

    # Discord webhook format
    payload = {
        "username": "SonicBuilder Monitor",
        "embeds": [
            {
                "title": f"{emoji} SonicBuilder Deployment Update",
                "description": message,
                "color": 65280 if level == "info" else 16776960 if level == "warn" else 16711680,
                "footer": {"text": f"UTC {timestamp}"},
            }
        ],
    }

    try:
        resp = requests.post(target_webhook, json=payload, timeout=10)
        if resp.status_code == 204 or resp.status_code == 200:
            print("📡 Notification sent successfully")
        else:
            print(f"⚠️  Notification response: {resp.status_code}")
    except Exception as e:
        print(f"❌ Notification failed: {e}")

def main():
    event = os.getenv("ROLLBACK_EVENT", "manual_test")
    status = os.getenv("ROLLBACK_STATUS", "ok")

    if status == "rollback":
        notify(
            f"⚠️ **Rollback Executed**\n\n"
            f"Reason: Failed commit or system.json corruption\n"
            f"Event: `{event}`\n"
            f"Action: Reverted to last known good state",
            "error"
        )
    elif status == "success":
        notify(
            f"✅ **Deployment Successful**\n\n"
            f"System.json successfully deployed to GitHub Pages\n"
            f"Event: `{event}`\n"
            f"Status: All systems operational",
            "info"
        )
    else:
        notify(f"ℹ️ Unknown event: {event}", "warn")

if __name__ == "__main__":
    main()
