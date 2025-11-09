#!/usr/bin/env python3
"""
SonicBuilder Alert Hooks System
v2.0.9 — watches health.json and triggers alerts to terminal + Discord
"""

import json, time, datetime, requests, os

# === USER CONFIGURATION ===
HEALTH_PATH = "docs/status/health.json"
DISCORD_WEBHOOK = os.getenv("ROLLBACK_WEBHOOK_URL") or os.getenv("DISCORD_WEBHOOK_URL")  # Replit Secrets
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")  # Optional Slack integration
CHECK_INTERVAL = 30  # seconds

def log(msg):
    print(f"[{datetime.datetime.utcnow().isoformat()}] {msg}")

def read_health():
    if not os.path.exists(HEALTH_PATH):
        return {"status": "missing"}
    try:
        with open(HEALTH_PATH) as f:
            return json.load(f)
    except Exception as e:
        return {"status": f"error: {e}"}

def send_discord_alert(status):
    if not DISCORD_WEBHOOK:
        log("⚠️ No Discord webhook set; skipping Discord alert.")
        return
    color = 0x00FF00 if status in ["ok", "patched", "success"] else 0xFF0000
    embed = {
        "title": "🚨 SonicBuilder Health Alert",
        "description": f"**Status:** `{status}`",
        "color": color,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "footer": {"text": "SonicBuilder Alert Hooks v2.0.9"}
    }
    payload = {"embeds": [embed]}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        log(f"📢 Sent Discord alert: {status}")
    except Exception as e:
        log(f"⚠️ Discord alert failed: {e}")

def send_slack_alert(status):
    if not SLACK_WEBHOOK:
        return
    emoji = "✅" if status in ["ok", "patched", "success"] else "🔴"
    text = f"{emoji} *SonicBuilder Health Alert*\nStatus: `{status}`"
    payload = {"text": text}
    try:
        requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
        log(f"📢 Sent Slack alert: {status}")
    except Exception as e:
        log(f"⚠️ Slack alert failed: {e}")

def monitor():
    last_status = None
    log("╔════════════════════════════════════════════════════════════════╗")
    log("║   🚨 SONICBUILDER ALERT HOOKS v2.0.9 ACTIVE                   ║")
    log("╚════════════════════════════════════════════════════════════════╝")
    log(f"📊 Monitoring: {HEALTH_PATH}")
    log(f"⏱️  Check Interval: {CHECK_INTERVAL}s")
    log(f"🔔 Discord: {'✅ Configured' if DISCORD_WEBHOOK else '❌ Not set'}")
    log(f"🔔 Slack: {'✅ Configured' if SLACK_WEBHOOK else '❌ Not set'}")
    log("")
    
    while True:
        data = read_health()
        current = data.get("status", "unknown")
        if current != last_status:
            log(f"🔄 Health status changed: {last_status or 'initial'} → {current}")
            send_discord_alert(current)
            send_slack_alert(current)
            last_status = current
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()