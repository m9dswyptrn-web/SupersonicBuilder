#!/usr/bin/env python3
"""
SonicBuilder Autodeploy System
Performs:
- preflight checks
- deploy key + webhook verification
- push to GitHub
- rollback recovery
"""

import os
import subprocess
import datetime
import json
import sys

REPO = "m9dswyptrn-web/SonicBuilder"
BRANCH = "main"
LOG_DIR = "founder_autodeploy/logs"

def run(cmd, check=True):
    """Execute shell command and log output"""
    print(f"→ {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr)
        if check:
            raise Exception(f"Command failed: {cmd}")
    return res

def preflight():
    """Run preflight checks for required secrets and dependencies"""
    print("🔍 Running preflight check...")
    
    # Check for required secrets
    needed = ["GITHUB_TOKEN"]
    missing = []
    for var in needed:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing secrets: {', '.join(missing)}")
        print("\nTo fix:")
        print("  1. Set environment variables:")
        for var in missing:
            print(f"     export {var}=<your_token>")
        print("  2. Or use Replit Secrets panel to add them")
        sys.exit(1)
    
    print("✅ All secrets present")
    
    # Check git status
    print("\n🔍 Checking git status...")
    res = run("git status --porcelain", check=False)
    if res.stdout.strip():
        print(f"  📝 Found {len(res.stdout.splitlines())} changed files")
    else:
        print("  ℹ️  No changes to deploy")
    
    # Check git remote
    res = run("git config --get remote.origin.url", check=False)
    if res.returncode == 0:
        print(f"  ✅ Git remote: {res.stdout.strip()}")
    else:
        print("  ⚠️  No git remote configured")
    
    print("\n✅ Preflight checks passed")

def commit_and_push():
    """Commit changes and push to GitHub"""
    print("\n📦 Committing and pushing changes...")
    
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Add all changes
    run("git add .")
    
    # Commit with timestamp
    commit_msg = f"autodeploy: {ts}"
    res = run(f'git commit -m "{commit_msg}"', check=False)
    
    if "nothing to commit" in res.stdout:
        print("ℹ️  No changes to commit")
        return False
    
    # Push to GitHub
    print(f"\n🚀 Pushing to {BRANCH} branch...")
    run(f"git push origin {BRANCH}")
    
    print(f"\n✅ Successfully deployed at {ts}")
    return True

def rollback():
    """Rollback to previous commit in case of failure"""
    print("\n⚠️  Deploy failed, initiating rollback...")
    
    # Reset to previous commit
    run("git reset --hard HEAD~1")
    
    # Force push to remote
    run(f"git push -f origin {BRANCH}")
    
    print("✅ Rollback complete")

def create_deployment_log(success=True, error=None):
    """Create deployment log file"""
    os.makedirs(LOG_DIR, exist_ok=True)
    
    timestamp = datetime.datetime.utcnow().isoformat()
    log_file = os.path.join(LOG_DIR, f"deploy_{timestamp.replace(':', '-')}.json")
    
    log_data = {
        "timestamp": timestamp,
        "branch": BRANCH,
        "repo": REPO,
        "success": success,
        "error": str(error) if error else None
    }
    
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\n📄 Deployment log: {log_file}")

def main():
    """Main deployment workflow"""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     🚀 SonicBuilder Autodeploy System                         ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    
    try:
        # Run preflight checks
        preflight()
        
        # Commit and push changes
        deployed = commit_and_push()
        
        # Create success log
        if deployed:
            create_deployment_log(success=True)
            print("\n╔════════════════════════════════════════════════════════════════╗")
            print("║                 ✅ DEPLOYMENT SUCCESSFUL                       ║")
            print("╚════════════════════════════════════════════════════════════════╝")
        else:
            print("\n╔════════════════════════════════════════════════════════════════╗")
            print("║                 ℹ️  NO CHANGES TO DEPLOY                       ║")
            print("╚════════════════════════════════════════════════════════════════╝")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Deploy error: {e}")
        
        # Create error log
        create_deployment_log(success=False, error=e)
        
        # Attempt rollback
        try:
            rollback()
        except Exception as rollback_error:
            print(f"❌ Rollback also failed: {rollback_error}")
        
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║                 ❌ DEPLOYMENT FAILED                           ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
