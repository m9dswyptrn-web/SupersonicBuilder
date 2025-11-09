#!/usr/bin/env python3
"""
SonicBuilder v2.0.9+ULTRA — Autonomous Scheduler
Full self-maintaining build agent with Discord notifications, pause flag,
adjustable intervals, and heartbeat monitoring.

Environment Variables:
  GITHUB_TOKEN          - GitHub personal access token (required for push)
  DISCORD_WEBHOOK       - Discord webhook URL (optional, for notifications)
  SB_INTERVAL_HOURS     - Deploy interval in hours (default: 12)

Usage:
  nohup python3 supersonic_scheduler_ultra.py &

Pause:
  touch pause.flag      - Pause scheduler
  rm pause.flag         - Resume scheduler
"""

import os
import time
import datetime
import subprocess
import sys

LOG = "scheduler.log"
SILENT_SCRIPT = "supersonic_autodeploy_silent.py"
DEFAULT_INTERVAL_HOURS = 12
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
INTERVAL_HOURS = float(os.getenv("SB_INTERVAL_HOURS", DEFAULT_INTERVAL_HOURS))
PAUSE_FLAG = "pause.flag"
REPO = "m9dswyptrn-web/SonicBuilder"

def log(msg):
    """Log to both console and file"""
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{timestamp}] {msg}"
    print(line)
    sys.stdout.flush()
    
    with open(LOG, "a") as f:
        f.write(line + "\n")

def send_discord_notification(msg, color=0x00FF00):
    """Send notification to Discord webhook"""
    if not DISCORD_WEBHOOK:
        return
    
    try:
        import requests
        
        payload = {
            "username": "SonicBuilderBot",
            "embeds": [{
                "title": "⚡ SonicBuilder Deployment Update",
                "description": msg,
                "color": color,
                "footer": {"text": f"SonicBuilder v2.0.9 • {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"},
                "timestamp": datetime.datetime.utcnow().isoformat()
            }]
        }
        
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        
        if response.status_code != 204:
            log(f"⚠️  Discord notification status: {response.status_code}")
    
    except ImportError:
        log("⚠️  Discord notifications require 'requests' package")
    except Exception as e:
        log(f"⚠️  Discord notification failed: {e}")

def check_github_reachable():
    """Check if GitHub is reachable"""
    try:
        import requests
        res = requests.get("https://github.com", timeout=5)
        return res.status_code == 200
    except ImportError:
        # Fallback to git if requests not available
        try:
            result = subprocess.run(
                "git ls-remote https://github.com/m9dswyptrn-web/SonicBuilder.git HEAD",
                shell=True,
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    except:
        return False

def run_silent_deploy():
    """Execute silent autodeploy and track metrics"""
    start = datetime.datetime.utcnow()
    log("🚀 Starting silent auto-deploy...")
    
    try:
        result = subprocess.run(
            f"python3 {SILENT_SCRIPT}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        duration = (datetime.datetime.utcnow() - start).total_seconds()
        code = result.returncode
        
        if code == 0:
            msg = f"✅ SonicBuilder deployment succeeded in {duration:.1f}s"
            log(msg)
            send_discord_notification(msg, color=0x00FF00)
            return True
        else:
            msg = f"❌ SonicBuilder deployment FAILED (exit code {code}) after {duration:.1f}s"
            log(msg)
            if result.stderr:
                log(f"   Error: {result.stderr[:200]}")
            send_discord_notification(msg, color=0xFF0000)
            return False
    
    except subprocess.TimeoutExpired:
        msg = "🔥 Deployment timed out (5 minutes)"
        log(msg)
        send_discord_notification(msg, color=0xFF0000)
        return False
    
    except Exception as e:
        msg = f"🔥 Exception during deploy: {e}"
        log(msg)
        send_discord_notification(msg, color=0xFF0000)
        return False

def check_pause_flag():
    """Check if pause flag exists"""
    return os.path.exists(PAUSE_FLAG)

def main():
    log("╔════════════════════════════════════════════════════════════════╗")
    log("║     🚀 SonicBuilder Autonomous Scheduler ULTRA                ║")
    log("╚════════════════════════════════════════════════════════════════╝")
    log(f"Interval: {INTERVAL_HOURS} hours")
    log(f"Silent script: {SILENT_SCRIPT}")
    log(f"Pause flag: {PAUSE_FLAG}")
    log(f"Discord notifications: {'Enabled' if DISCORD_WEBHOOK else 'Disabled'}")
    log(f"Log file: {LOG}")
    log("")
    
    send_discord_notification(
        f"🟢 Scheduler ULTRA online and standing by.\n"
        f"📊 Interval: {INTERVAL_HOURS} hours\n"
        f"⏸️ Pause: Create '{PAUSE_FLAG}' to pause",
        color=0x00AAFF
    )
    
    cycle_count = 0
    success_count = 0
    failure_count = 0
    
    try:
        while True:
            cycle_count += 1
            log(f"═══ Cycle #{cycle_count} ═══")
            
            # Check pause flag
            if check_pause_flag():
                log("⏸️  Pause flag detected — skipping this cycle")
                send_discord_notification(
                    f"⏸️ Scheduler paused by user ('{PAUSE_FLAG}' detected).\n"
                    f"Remove file to resume.",
                    color=0xAAAAAA
                )
                log(f"Sleeping for 10 minutes before checking again...")
                time.sleep(600)  # Check every 10 minutes when paused
                continue
            
            # Check GitHub availability
            if check_github_reachable():
                log("✅ GitHub reachable, starting deploy cycle")
                
                success = run_silent_deploy()
                
                if success:
                    success_count += 1
                else:
                    failure_count += 1
                
                log(f"📊 Stats: {success_count} successes, {failure_count} failures")
            else:
                log("⚠️  GitHub unreachable, skipping this cycle")
                send_discord_notification(
                    "⚠️ GitHub unreachable — cycle skipped.",
                    color=0xFFA500
                )
            
            # Sleep until next cycle
            next_run = datetime.datetime.utcnow() + datetime.timedelta(hours=INTERVAL_HOURS)
            log(f"Next deploy cycle: {next_run.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            log(f"💤 Sleeping for {INTERVAL_HOURS} hours...")
            log("")
            
            send_discord_notification(
                f"💤 Scheduler sleeping for {INTERVAL_HOURS} hours.\n"
                f"⏰ Next cycle: {next_run.strftime('%Y-%m-%d %H:%M UTC')}",
                color=0x6666FF
            )
            
            time.sleep(INTERVAL_HOURS * 3600)
    
    except KeyboardInterrupt:
        log("\n⚠️  Scheduler stopped by user (KeyboardInterrupt)")
        send_discord_notification(
            "🛑 Scheduler stopped by user.\n"
            f"📊 Final stats: {success_count} successes, {failure_count} failures",
            color=0xFF6600
        )
        log("╔════════════════════════════════════════════════════════════════╗")
        log("║     🛑 SonicBuilder Autonomous Scheduler ULTRA Stopped        ║")
        log("╚════════════════════════════════════════════════════════════════╝")
        return 0
    
    except Exception as e:
        log(f"\n❌ Scheduler crashed: {e}")
        import traceback
        log(traceback.format_exc())
        
        send_discord_notification(
            f"🔥 Scheduler crashed!\n"
            f"Error: {str(e)[:100]}",
            color=0xFF0000
        )
        return 1

if __name__ == "__main__":
    sys.exit(main())
