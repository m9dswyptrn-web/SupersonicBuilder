#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 FOUNDER-INFINITY-MIRROR-SYNC
------------------------------------------------
Automated GitHub mirror synchronization service.

Every 60 minutes, commits the latest:
 • security_audit.json - Security audit trail
 • scheduler.log - Deployment history
 • banned_ips.json - IP ban list
 • pause.flag - Pause state (if present)

to GitHub branch: founder_mirror

This provides:
 - Off-site backup of critical logs
 - Historical audit trail
 - Compliance and forensics support
 - Real-time system state mirroring

Requires:
  - GITHUB_TOKEN - Personal access token with repo scope
  - GITHUB_REPO - Repository name (e.g., "username/repo")
"""

import os
import time
import base64
import requests
import json
from datetime import datetime

# Configuration
REPO = os.getenv("GITHUB_REPO", "m9dswyptrn-web/SonicBuilder")
TOKEN = os.getenv("GITHUB_TOKEN")
BRANCH = "founder_mirror"
SYNC_INTERVAL = 3600  # 60 minutes

# API Configuration
API_BASE = f"https://api.github.com/repos/{REPO}/contents"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Files to mirror
MIRROR_FILES = [
    "security_audit.json",
    "scheduler.log",
    "banned_ips.json",
    "pause.flag"
]

def upload_file_to_github(filepath):
    """Upload or update file in GitHub repository"""
    if not os.path.exists(filepath):
        print(f"  ⏩ Skipping {filepath} (not found)")
        return
    
    try:
        # Read file content
        with open(filepath, "rb") as f:
            content = f.read()
        
        # Encode to base64
        b64_content = base64.b64encode(content).decode()
        
        filename = os.path.basename(filepath)
        mirror_path = f"mirror/{filename}"
        url = f"{API_BASE}/{mirror_path}"
        
        # Check if file exists (to get SHA for update)
        try:
            existing = requests.get(url, headers=HEADERS, params={"ref": BRANCH})
            sha = existing.json().get("sha") if existing.status_code == 200 else None
        except Exception:
            sha = None
        
        # Prepare commit message
        timestamp = datetime.utcnow().isoformat()
        commit_msg = f"[Auto-Mirror] Update {filename} @ {timestamp}"
        
        # Upload file
        payload = {
            "message": commit_msg,
            "content": b64_content,
            "branch": BRANCH
        }
        
        if sha:
            payload["sha"] = sha
        
        response = requests.put(url, headers=HEADERS, json=payload)
        
        if response.status_code in [200, 201]:
            print(f"  ✅ {filename} → GitHub (HTTP {response.status_code})")
        else:
            print(f"  ❌ {filename} failed: HTTP {response.status_code}")
            if response.status_code == 409:
                print(f"     Conflict detected, retrying...")
    
    except Exception as e:
        print(f"  ⚠️  Error uploading {filepath}: {e}")

def sync_cycle():
    """Perform one synchronization cycle"""
    print(f"\n{'='*60}")
    print(f"🔄 Mirror Sync Cycle - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*60}")
    
    if not TOKEN:
        print("⚠️  GITHUB_TOKEN not configured! Skipping sync.")
        return
    
    for filepath in MIRROR_FILES:
        upload_file_to_github(filepath)
    
    print(f"\n✅ Sync cycle complete")

def main():
    """Main service loop"""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   🪞 SonicBuilder Mirror Sync Service v2.0.9                  ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"\nRepository: {REPO}")
    print(f"Branch: {BRANCH}")
    print(f"Interval: {SYNC_INTERVAL/60} minutes")
    print(f"Token configured: {'Yes' if TOKEN else 'No'}")
    
    if not TOKEN:
        print("\n⚠️  WARNING: GITHUB_TOKEN not set!")
        print("   Set GITHUB_TOKEN in Replit Secrets to enable mirror sync.\n")
        return
    
    print(f"\nMonitoring files:")
    for f in MIRROR_FILES:
        print(f"  • {f}")
    
    print(f"\nStarting continuous sync...\n")
    
    # Run initial sync
    sync_cycle()
    
    # Continuous sync loop
    while True:
        time.sleep(SYNC_INTERVAL)
        sync_cycle()

if __name__ == "__main__":
    main()
