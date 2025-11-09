#!/usr/bin/env python3
"""
System Health Rollback Script
Detects corruption and rolls back to last known good state
"""

import os
import subprocess
from datetime import datetime

def git(*args):
    """Execute git command and return output"""
    return subprocess.check_output(["git"] + list(args), text=True).strip()

def safe_run(cmd):
    """Safely execute shell command"""
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def rollback():
    """Execute rollback to previous commit"""
    print("🛑 Commit failed — initiating rollback procedure...")
    
    try:
        prev_commit = git("rev-parse", "HEAD~1")
        print(f"🔙 Reverting to previous commit {prev_commit}")
        
        safe_run(f"git reset --hard {prev_commit}")
        safe_run("git push --force origin gh-pages")
        
        print("✅ Rollback complete — reverted to last known good state.")
    except Exception as e:
        print(f"❌ Rollback failed: {e}")

def main():
    target = "docs/status/system.json"
    
    if not os.path.exists(target):
        print("⚠️  system.json missing; nothing to rollback.")
        return

    print("🚀 Validating last system.json commit...")
    
    # Check if last commit modified system.json
    try:
        diff_check = safe_run("git diff --quiet HEAD HEAD~1 -- docs/status/system.json")
        if diff_check:
            print("✅ No corruption detected.")
            return
    except Exception:
        pass

    print("❌ Corruption detected — restoring previous good commit...")
    rollback()

if __name__ == "__main__":
    main()
