#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 HARMONY AUTO-HEALER
----------------------------------------
Silent background service that monitors and auto-heals:
  - Harmony feed staleness (harmony_feed.json)
  - PDF documentation builds
  - GitHub Pages heartbeat
  - Auto-healer status badge

Runs every 15 minutes and triggers GitHub Actions or local rebuilds as needed.
"""

import os
import time
import json
import subprocess
import requests
from datetime import datetime, timedelta

# === CONFIGURATION ===
FEED_PATH = "harmony_feed.json"
FALLBACK_FEED_PATH = "docs/status/feed.json"
PDF_PATH = "docs_build/latest.pdf"
HEARTBEAT_FILE = "docs/status/heartbeat.json"
BADGE_FILE = "badges/auto_healer_status.json"
UPTIME_LOG = "docs/status/uptime_log.json"

CHECK_INTERVAL = 900  # 15 minutes in seconds
MAX_AGE_HOURS = 24
HEARTBEAT_INTERVAL = 3600  # 1 hour
MAX_UPTIME_DAYS = 7  # Rolling window for uptime log

GITHUB_REPO = os.getenv("GITHUB_REPO", "m9dswyptrn-web/SonicBuilder")
GH_TOKEN = os.getenv("GITHUB_TOKEN")

# Track last heartbeat time
last_heartbeat_time = 0

# === LOGGING ===
def log(msg):
    """Log message with timestamp"""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{timestamp}] {msg}")

# === HELPER FUNCTIONS ===
def file_age_hours(path):
    """Get file age in hours, returns 999 if doesn't exist"""
    if not os.path.exists(path):
        return 999
    return (time.time() - os.path.getmtime(path)) / 3600

def get_feed_timestamp():
    """Get timestamp of last feed entry"""
    # Try primary feed first
    feed_path = FEED_PATH if os.path.exists(FEED_PATH) else FALLBACK_FEED_PATH
    
    if not os.path.exists(feed_path):
        return None
    
    try:
        with open(feed_path) as f:
            data = json.load(f)
        
        if not data:
            return None
        
        last_entry = data[-1]["timestamp"] if data else None
        if last_entry:
            return datetime.strptime(last_entry, "%Y-%m-%d %H:%M:%S UTC")
    except Exception as e:
        log(f"⚠️  Error parsing feed: {e}")
    
    return None

def trigger_github_action(reason="autoheal"):
    """Trigger GitHub Actions workflow via repository dispatch"""
    if not GH_TOKEN:
        log("❌ Missing GITHUB_TOKEN, cannot trigger GitHub Action")
        return False
    
    headers = {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "event_type": "feed_badge_refresh",
        "client_payload": {
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "Replit Auto-Healer"
        }
    }
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 204:
            log(f"✅ Triggered GitHub Action: {reason}")
            return True
        else:
            log(f"⚠️  GitHub Action trigger failed: {resp.status_code}")
            return False
    except Exception as e:
        log(f"❌ Failed to trigger GitHub Action: {e}")
        return False

def rebuild_pdf():
    """Attempt to rebuild PDF documentation locally"""
    log("🛠️  Attempting local PDF rebuild...")
    
    build_scripts = ["supersonic_autodeploy.py", "supersonic_autodeploy_silent.py"]
    
    for script in build_scripts:
        if os.path.exists(script):
            try:
                log(f"📄 Running {script}...")
                result = subprocess.run(
                    ["python3", script],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=300  # 5 minute timeout
                )
                log("✅ PDF rebuild completed successfully")
                return True
            except subprocess.TimeoutExpired:
                log(f"⚠️  {script} timed out")
            except subprocess.CalledProcessError as e:
                log(f"⚠️  {script} failed: {e.stderr.decode()[:200]}")
            except Exception as e:
                log(f"⚠️  Error running {script}: {e}")
    
    log("❌ All PDF rebuild attempts failed")
    return False

def load_uptime_log():
    """Load uptime log from disk"""
    if os.path.exists(UPTIME_LOG):
        try:
            with open(UPTIME_LOG) as f:
                return json.load(f)
        except Exception as e:
            log(f"⚠️  Uptime log parse error: {e}")
    return []

def save_uptime_log(data):
    """Save uptime log to disk"""
    os.makedirs(os.path.dirname(UPTIME_LOG), exist_ok=True)
    try:
        with open(UPTIME_LOG, "w") as f:
            json.dump(data, f, indent=2)
        log("📈 Uptime log updated")
    except Exception as e:
        log(f"⚠️  Failed to write uptime log: {e}")

def record_uptime_entry():
    """Append a timestamped uptime entry and prune old records"""
    data = load_uptime_log()
    now = datetime.utcnow()
    entry = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": "up",
        "source": "Auto-Healer"
    }
    data.append(entry)

    # Prune entries older than MAX_UPTIME_DAYS
    cutoff = now - timedelta(days=MAX_UPTIME_DAYS)
    data = [d for d in data if datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S UTC") > cutoff]
    save_uptime_log(data)

def write_heartbeat():
    """Write heartbeat timestamp for GitHub Pages visibility"""
    os.makedirs(os.path.dirname(HEARTBEAT_FILE) if os.path.dirname(HEARTBEAT_FILE) else ".", exist_ok=True)
    
    heartbeat = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": "alive",
        "source": "Replit Auto-Healer",
        "version": "2.0.9"
    }
    
    try:
        with open(HEARTBEAT_FILE, "w") as f:
            json.dump(heartbeat, f, indent=2)
        log(f"💓 Heartbeat written: {heartbeat['timestamp']}")
        return True
    except Exception as e:
        log(f"⚠️  Heartbeat write failed: {e}")
        return False

def update_healer_badge(status="active"):
    """Update auto-healer status badge"""
    try:
        badge = {
            "schemaVersion": 1,
            "label": "Auto-Healer",
            "message": status,
            "color": "green" if status == "active" else "orange",
            "isError": False
        }
        
        os.makedirs(os.path.dirname(BADGE_FILE) if os.path.dirname(BADGE_FILE) else ".", exist_ok=True)
        
        with open(BADGE_FILE, "w") as f:
            json.dump(badge, f, indent=2)
        
        log(f"🏷️  Auto-healer badge updated → {status}")
        return True
    except Exception as e:
        log(f"⚠️  Badge update failed: {e}")
        return False

# === HEALING FUNCTIONS ===
def heal_feed():
    """Check and heal stale Harmony feed"""
    ts = get_feed_timestamp()
    
    if not ts:
        log("⚠️  Feed missing or invalid → triggering GitHub Action")
        trigger_github_action("missing_feed")
        return
    
    age_hours = (datetime.utcnow() - ts).total_seconds() / 3600
    
    if age_hours > MAX_AGE_HOURS:
        log(f"⚠️  Feed stale ({age_hours:.1f}h old) → triggering healing")
        trigger_github_action("stale_feed")
    else:
        log(f"✅ Feed healthy ({age_hours:.1f}h old)")

def heal_pdf():
    """Check and heal stale PDF documentation"""
    age = file_age_hours(PDF_PATH)
    
    if age > MAX_AGE_HOURS:
        log(f"⚠️  PDF stale ({age:.1f}h old) → triggering rebuild")
        
        # Try local rebuild first
        if rebuild_pdf():
            log("✅ PDF healed via local rebuild")
        else:
            # Fallback to GitHub Action
            log("⚠️  Local rebuild failed, triggering GitHub Action")
            trigger_github_action("stale_pdf")
    else:
        log(f"✅ PDF healthy ({age:.1f}h old)")

def periodic_heartbeat():
    """Write periodic heartbeat if enough time has passed"""
    global last_heartbeat_time
    
    current_time = time.time()
    
    if current_time - last_heartbeat_time >= HEARTBEAT_INTERVAL:
        write_heartbeat()
        record_uptime_entry()
        last_heartbeat_time = current_time

# === MAIN LOOP ===
def main():
    """Main auto-healer loop"""
    log("╔════════════════════════════════════════════════════════════════╗")
    log("║   🤖 SonicBuilder Auto-Healer v2.0.9 Started                  ║")
    log("╚════════════════════════════════════════════════════════════════╝")
    log("")
    log(f"📋 Configuration:")
    log(f"   Check Interval: {CHECK_INTERVAL/60:.0f} minutes")
    log(f"   Max Age: {MAX_AGE_HOURS} hours")
    log(f"   GitHub Repo: {GITHUB_REPO}")
    log(f"   GitHub Token: {'✅ Set' if GH_TOKEN else '❌ Missing'}")
    log("")
    
    # Initial badge update
    update_healer_badge("active")
    
    cycle = 0
    
    while True:
        cycle += 1
        log(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        log(f"🔄 Healing Cycle #{cycle}")
        log(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        try:
            # Update badge to show active status
            update_healer_badge("active")
            
            # Run healing checks
            heal_feed()
            heal_pdf()
            periodic_heartbeat()
            
            # Sleep until next check
            log(f"💤 Sleeping {CHECK_INTERVAL/60:.0f} minutes until next check")
            log("")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("")
            log("⚠️  Auto-healer stopped by user")
            update_healer_badge("paused")
            break
        except Exception as e:
            log(f"❌ Error in healing cycle: {e}")
            log(f"   Continuing after brief pause...")
            time.sleep(60)  # Brief pause before retry

if __name__ == "__main__":
    main()
