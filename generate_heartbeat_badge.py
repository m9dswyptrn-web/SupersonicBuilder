#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 HARMONY HEARTBEAT BADGE GENERATOR
-----------------------------------------------------
Generates Harmony status badge based on last GitHub Actions heartbeat.

Updates:
  - badges/heartbeat.json - Badge metadata
  - Used by update_badges.py for README injection

Status Detection:
  - Active (green) - Last heartbeat < 1.5 hours
  - Desync (red) - Last heartbeat >= 1.5 hours
"""

import json
import os
import time
import datetime

BADGE_PATH = "badges/heartbeat.json"
LAST_HEARTBEAT_FILE = "last_heartbeat.txt"
MAX_INTERVAL = 5400  # 1.5 hours
COLOR_ACTIVE = "brightgreen"
COLOR_DESYNC = "red"

def make_badge(label, message, color):
    """Generate Shields.io badge URL"""
    safe_label = label.replace(" ", "%20")
    safe_message = message.replace(" ", "%20")
    return f"https://img.shields.io/badge/{safe_label}-{safe_message}-{color}.svg"

def heartbeat_status():
    """Determine current heartbeat status"""
    now = time.time()
    last = 0
    
    if os.path.exists(LAST_HEARTBEAT_FILE):
        try:
            with open(LAST_HEARTBEAT_FILE) as f:
                last = float(f.read().strip())
        except Exception:
            pass
    
    delta = now - last
    
    if delta < MAX_INTERVAL:
        status = "Active"
        color = COLOR_ACTIVE
    else:
        status = "Desync"
        color = COLOR_DESYNC
    
    return status, color, delta

def generate_badge():
    """Generate and save Harmony badge"""
    status, color, delta = heartbeat_status()
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    badge_url = make_badge("Harmony", f"{status}", color)
    
    data = {
        "status": status,
        "color": color,
        "badge": badge_url,
        "last_check": timestamp,
        "delta_seconds": delta
    }
    
    os.makedirs(os.path.dirname(BADGE_PATH), exist_ok=True)
    with open(BADGE_PATH, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"💓 Harmony badge updated → {status} ({round(delta/60)}m since last ping)")
    print(f"🏷️ Badge URL: {badge_url}")

if __name__ == "__main__":
    generate_badge()
