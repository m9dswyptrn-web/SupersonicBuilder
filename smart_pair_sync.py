#!/usr/bin/env python3
"""
SonicBuilder Smart Pair Sync Add-On
v2.0.9 — Continuous mirror between Replit and GitHub
"""

import os, time, subprocess, datetime

SYNC_INTERVAL = 180  # seconds between sync checks (3 minutes)

def log(msg):
    print(f"[{datetime.datetime.utcnow().isoformat()}] {msg}")

def run(cmd, check=False):
    try:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=check)
        if result.stdout: log(result.stdout.strip())
        if result.stderr: log(result.stderr.strip())
        return result.returncode == 0
    except Exception as e:
        log(f"⚠️ Command failed: {e}")
        return False

def ensure_remote():
    log("🔍 Checking Git remote...")
    remotes = subprocess.run("git remote -v", shell=True, text=True, capture_output=True).stdout
    if "origin" not in remotes:
        run(f"git remote add origin https://github.com/m9dswyptrn-web/SonicBuilder.git")
        log("✅ Added GitHub remote origin.")
    else:
        log("✅ Remote origin already configured.")

def pull_updates():
    log("⬇️ Pulling latest changes from GitHub...")
    run("git fetch origin main")
    run("git pull origin main --rebase")

def push_updates():
    log("⬆️ Pushing local Replit changes to GitHub...")
    run("git add -A")
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    run(f'git commit -m "🌀 Smart Pair Sync auto-commit ({ts})" || echo "Nothing to commit"')
    run("git push origin main")

def sync_loop():
    ensure_remote()
    while True:
        log("🔁 Starting sync cycle...")
        pull_updates()
        push_updates()
        log(f"⏳ Waiting {SYNC_INTERVAL//60} minutes for next cycle...\n")
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    log("🚀 SonicBuilder Smart Pair Sync engaged.")
    sync_loop()