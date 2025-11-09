#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 HARMONY FEED HEALTH BADGE GENERATOR
-------------------------------------------------------
Generates health badge for Harmony feed based on feed freshness.

Reads: docs/status/feed.json (or harmony_feed.json as fallback)
Writes: badges/feed_health.json (Shields.io endpoint format)

Status Logic:
  - healthy (green) - Last entry < 24 hours old
  - desync (red) - Last entry >= 24 hours old or missing
  - empty (red) - Feed exists but has no entries
  - missing (gray) - Feed file doesn't exist
  - invalid time (orange) - Cannot parse timestamp
"""

import os
import json
from datetime import datetime, timedelta

# Paths (check both locations)
FEED_PATHS = ["docs/status/feed.json", "harmony_feed.json"]
BADGE_PATH = "badges/feed_health.json"

def make_badge(label, message, color):
    """Generate Shields.io endpoint badge JSON"""
    return {
        "schemaVersion": 1,
        "label": label,
        "message": message,
        "color": color
    }

def main():
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   🎨 Harmony Feed Health Badge Generator v2.0.9               ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    # Find feed file
    feed_path = None
    for path in FEED_PATHS:
        if os.path.exists(path):
            feed_path = path
            print(f"✅ Found feed at: {feed_path}")
            break
    
    if not feed_path:
        print("⚠️  No feed file found, creating 'missing' badge")
        badge = make_badge("Feed", "missing", "lightgrey")
    else:
        try:
            with open(feed_path) as f:
                data = json.load(f)
            
            if not data:
                print("⚠️  Feed is empty, creating 'empty' badge")
                badge = make_badge("Feed", "empty", "red")
            else:
                last = data[-1]["timestamp"] if data else None
                print(f"📅 Last entry: {last}")
                
                if not last:
                    badge = make_badge("Feed", "empty", "red")
                else:
                    # Parse UTC timestamp
                    try:
                        ts = datetime.strptime(last, "%Y-%m-%d %H:%M:%S UTC")
                        delta = datetime.utcnow() - ts
                        hours = delta.total_seconds() / 3600
                        
                        print(f"⏰ Age: {hours:.1f} hours")
                        
                        if hours <= 24:
                            badge = make_badge("Feed", "healthy", "brightgreen")
                            print("✅ Status: healthy")
                        else:
                            badge = make_badge("Feed", f"desync {int(hours)}h", "red")
                            print(f"⚠️  Status: desync ({int(hours)}h)")
                    except Exception as e:
                        print(f"❌ Error parsing timestamp: {e}")
                        badge = make_badge("Feed", "invalid time", "orange")
        except Exception as e:
            print(f"❌ Error reading feed: {e}")
            badge = make_badge("Feed", "error", "red")
    
    # Save badge
    os.makedirs(os.path.dirname(BADGE_PATH), exist_ok=True)
    with open(BADGE_PATH, "w") as f:
        json.dump(badge, f, indent=2)
    
    print(f"\n✅ Feed badge written to {BADGE_PATH}")
    print(f"Badge: {badge['label']} - {badge['message']} ({badge['color']})\n")

if __name__ == "__main__":
    main()
