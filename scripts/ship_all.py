#!/usr/bin/env python3
"""
scripts/ship_all.py
One-button release + deploy for SupersonicBuilder.

Usage:
  python3 scripts/ship_all.py --version v0.1.4
  # or just:
  python3 scripts/ship_all.py
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone

PAGES_URL = "https://m9dswyptrn-web.github.io/SupersonicBuilder/"
GIT_NAME = "Supersonic Builder"
GIT_EMAIL = "supersonic-builder@users.noreply.github.com"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(cmd, env=None, check=True, cwd=ROOT):
    print(f"\n$ {' '.join(cmd)}")
    try:
        return subprocess.run(cmd, cwd=cwd, env=env or os.environ, check=check)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        sys.exit(e.returncode)

def git_config():
    run(["git", "config", "user.name", GIT_NAME], check=False)
    run(["git", "config", "user.email", GIT_EMAIL], check=False)

def ensure_token_in_env():
    # Make ship flow happy: prefer GH_TOKEN, fall back to GH_PAT if present
    env = os.environ.copy()
    if not env.get("GH_TOKEN") and env.get("GH_PAT"):
        env["GH_TOKEN"] = env["GH_PAT"]
        print("🔑 Using GH_PAT as GH_TOKEN for this session.")
    elif env.get("GH_TOKEN"):
        print("🔑 GH_TOKEN detected.")
    else:
        print("⚠️  No GH_TOKEN/GH_PAT in environment. Push may prompt or fail.")
    return env

def sync_main(env):
    # Ensure remote exists and sync local main
    res = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, env=env)
    if res.returncode != 0:
        print("❌ No 'origin' remote configured. Add it, then re-run.")
        sys.exit(2)

    run(["git", "fetch", "origin", "main"], env=env)
    run(["git", "checkout", "-B", "main"], env=env)
    run(["git", "reset", "--hard", "origin/main"], env=env)
    print("✅ Workspace is aligned with origin/main.")

def maybe_bump(version: str, env):
    if not version:
        print("⏭️  No version bump requested.")
        return
    # Expect explicit semantic version like v0.1.4
    print(f"📦 Bumping version to {version} …")
    run(["make", "bump", f"VERSION={version}"], env=env)
    # Add the VERSION file (or whatever the bump changed) just in case:
    run(["git", "add", "-A"], env=env, check=False)
    run(["git", "commit", "-m", f"release: bump {version} [ci skip]"], env=env, check=False)
    run(["git", "push", "origin", "main"], env=env, check=False)
    # Tag if not already present
    run(["git", "tag", "-f", version], env=env, check=False)
    run(["git", "push", "origin", "--tags"], env=env, check=False)

def build_release(env):
    print("🛠️  Building PDFs & artifacts …")
    run(["make", "supersonic-release"], env=env)

def deploy_pages(env):
    print("🚀 Deploying to GitHub Pages (/docs) …")
    # Use the working deploy script your make target calls
    run(["python3", "supersonic_deploy_pages.py"], env=env)

    # Commit/push docs
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    run(["git", "add", "docs/"], env=env, check=False)
    # If nothing to commit, this will fail—so ignore failures gracefully
    run(["git", "commit", "-m", f"docs: publish {ts}"], env=env, check=False)
    run(["git", "push", "origin", "main"], env=env, check=False)

def main():
    parser = argparse.ArgumentParser(description="Ship SupersonicBuilder: bump, build, deploy.")
    parser.add_argument("--version", help="Explicit version tag to bump (e.g. v0.1.4). Optional.")
    args = parser.parse_args()

    os.chdir(ROOT)
    env = ensure_token_in_env()
    git_config()
    sync_main(env)
    if args.version:
        maybe_bump(args.version, env)
        # re-sync after bump to be safe
        sync_main(env)

    # quick dry-run print (optional)
    run(["make", "-n", "supersonic-release"], env=env, check=False)

    build_release(env)
    deploy_pages(env)

    print("\n✅ Release complete.")
    print(f"🌐 Live hub: {PAGES_URL}")

if __name__ == "__main__":
    main()
