#!/usr/bin/env python3
"""
System Health Summary Push Script
Commits and pushes system.json to GitHub Pages branch
"""

import os
import subprocess
from datetime import datetime

def git(*args):
    """Execute git command"""
    return subprocess.check_call(["git"] + list(args))

def main():
    print("🚀 Preparing to push system.json to GitHub Pages…")

    target_file = "docs/status/system.json"
    if not os.path.exists(target_file):
        raise FileNotFoundError("❌ system.json not found. Run gen_system_json.py first.")

    # Configure Git identity (safe defaults for CI)
    git("config", "--global", "user.name", "SonicBuilder AutoBot")
    git("config", "--global", "user.email", "autobot@sonicbuilder.local")

    # Add and commit changes
    git("add", target_file)
    
    try:
        git("commit", "-m", f"🤖 Auto-update system health summary — {datetime.utcnow().isoformat()} UTC")
    except subprocess.CalledProcessError:
        print("ℹ️  No changes to commit (system.json unchanged)")
        return

    # Push to the default Pages branch
    branch = os.getenv("PAGES_BRANCH", "gh-pages")
    remote = os.getenv("REMOTE_NAME", "origin")

    print(f"📤 Pushing to {remote}/{branch} …")
    git("push", remote, f"HEAD:{branch}")
    print("✅ system.json successfully updated and pushed!")

if __name__ == "__main__":
    main()
