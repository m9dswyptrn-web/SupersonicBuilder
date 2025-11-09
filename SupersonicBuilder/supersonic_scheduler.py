#!/usr/bin/env python3
"""
SonicBuilder v2.0.9-SB-ULTRA : Autonomous Scheduler
Runs supersonic_autodeploy_silent.py every 12 hours automatically
Usage: nohup python3 supersonic_scheduler.py &
"""

import os
import time
import datetime
import subprocess
import sys

LOG = "scheduler.log"
SILENT_SCRIPT = "supersonic_autodeploy_silent.py"
INTERVAL_HOURS = 12

def log(msg):
    """Log to both console and file"""
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{timestamp}] {msg}"
    print(line)
    sys.stdout.flush()
    
    with open(LOG, "a") as f:
        f.write(line + "\n")

def check_github_reachable():
    """Check if GitHub is reachable via git"""
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

def run_silent_deploy():
    """Execute silent autodeploy script"""
    log("Triggering silent auto-deploy...")
    
    try:
        result = subprocess.run(
            f"python3 {SILENT_SCRIPT}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        log(f"Silent deploy exit code: {result.returncode}")
        
        if result.returncode == 0:
            log("✅ Deploy cycle completed successfully")
        else:
            log("⚠️  Deploy cycle completed with errors")
            if result.stderr:
                log(f"Stderr: {result.stderr[:200]}")
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        log("❌ Deploy cycle timed out (5 min)")
        return 1
    except Exception as e:
        log(f"❌ Deploy cycle failed: {e}")
        return 1

def main():
    log("╔════════════════════════════════════════════════════════════════╗")
    log("║     🚀 SonicBuilder Autonomous Scheduler Started              ║")
    log("╚════════════════════════════════════════════════════════════════╝")
    log(f"Interval: {INTERVAL_HOURS} hours")
    log(f"Silent script: {SILENT_SCRIPT}")
    log(f"Log file: {LOG}")
    log("")
    
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            log(f"═══ Cycle #{cycle_count} ═══")
            
            # Check GitHub availability
            if check_github_reachable():
                log("✅ GitHub reachable, starting deploy cycle")
                run_silent_deploy()
            else:
                log("⚠️  GitHub not reachable, skipping this cycle")
            
            # Sleep until next cycle
            next_run = datetime.datetime.utcnow() + datetime.timedelta(hours=INTERVAL_HOURS)
            log(f"Next deploy cycle: {next_run.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            log(f"Sleeping for {INTERVAL_HOURS} hours...")
            log("")
            
            time.sleep(INTERVAL_HOURS * 3600)
    
    except KeyboardInterrupt:
        log("\n⚠️  Scheduler stopped by user (KeyboardInterrupt)")
        log("╔════════════════════════════════════════════════════════════════╗")
        log("║     🛑 SonicBuilder Autonomous Scheduler Stopped              ║")
        log("╚════════════════════════════════════════════════════════════════╝")
        return 0
    
    except Exception as e:
        log(f"\n❌ Scheduler crashed: {e}")
        import traceback
        log(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
