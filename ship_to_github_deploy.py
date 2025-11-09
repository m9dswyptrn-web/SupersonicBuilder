#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supersonic v4 Ultimate Edition — Quick GitHub Deployment
Deploys existing project to GitHub with minimal changes
"""
import subprocess
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def run(cmd, check=True):
    print(" $", " ".join(cmd))
    return subprocess.run(cmd, check=check)

def check_gh_cli():
    """Verify GitHub CLI is available and authenticated"""
    try:
        result = subprocess.run(["gh", "auth", "status"], capture_output=True)
        if result.returncode != 0:
            print("❌ GitHub CLI not authenticated. Please run: gh auth login")
            return False
        print("✅ GitHub CLI authenticated")
        return True
    except FileNotFoundError:
        print("❌ GitHub CLI not found. Please install: https://cli.github.com/")
        return False

def deploy(repo_name, version, create_repo=True):
    """Deploy to GitHub"""
    print(f"\n🚀 Deploying Supersonic v4 Ultimate Edition to {repo_name}")
    print(f"📦 Version: {version}\n")
    
    # Check if git repo exists
    git_dir = ROOT / ".git"
    if not git_dir.exists():
        print("📝 Initializing git repository...")
        run(["git", "init"])
        run(["git", "branch", "-M", "main"])
    
    # Add all files
    print("📦 Staging files...")
    run(["git", "add", "."])
    
    # Commit
    print("💾 Creating commit...")
    run(["git", "commit", "-m", f"feat: Supersonic v4 Ultimate Edition - {version}"], check=False)
    
    # Create or set remote
    if create_repo:
        if not check_gh_cli():
            sys.exit(1)
        
        print(f"🏗️  Creating repository {repo_name}...")
        result = run(["gh", "repo", "create", repo_name, "--public", "--source=.", "--push"], check=False)
        
        if result.returncode != 0:
            print("⚠️  Repository might already exist. Trying to push to existing repo...")
            run(["git", "remote", "add", "origin", f"https://github.com/{repo_name}.git"], check=False)
            run(["git", "push", "-u", "origin", "main", "--force"])
    else:
        print("📤 Pushing to origin...")
        run(["git", "push", "-u", "origin", "main"])
    
    # Create tag
    print(f"🏷️  Creating tag {version}...")
    run(["git", "tag", "-a", version, "-m", f"Release {version}"], check=False)
    run(["git", "push", "origin", version], check=False)
    
    # Create release
    if check_gh_cli():
        print(f"🎉 Creating GitHub release {version}...")
        run([
            "gh", "release", "create", version,
            "--title", f"Supersonic v4 Ultimate Edition - {version}",
            "--notes", f"""# Supersonic v4 Ultimate Edition - {version}

## 🎯 Features

✅ **LED Status Banner System** - Animated GIF status indicators  
✅ **5 Professional Voice Packs** - Commander, AIOps, FlightOps, IndustrialOps, ArcadeHUD  
✅ **AI Mission Console** - Interactive TUI for workflow management  
✅ **Last Known Good Recovery** - Quick access to stable releases  
✅ **54 Make Targets** - Complete automation suite  
✅ **Self-Healing Assets** - Auto-generates missing badges & voice files  

## 📊 Integration Statistics

- Scripts Created: 10
- Voice Packs: 5 (35 WAV files total)
- LED Badges: 4 animated GIFs
- Make Targets: 54
- GitHub Workflows: Production-ready CI/CD

## 🚀 Quick Start

```bash
# Generate all voice packs
make -f make/ControlCore.mk ai-voicepacks

# Launch AI Mission Console
make -f make/ControlCore.mk ai-console

# View all available targets
make -f make/ControlCore.mk ai-help
```

**Documentation:** See `docs/LED_VOICE_AI_CONSOLE_INTEGRATION.md` for complete guide.

---

_© 2025 Supersonic Systems — "Fast is fine. Supersonic is better."_
"""
        ])
    
    print(f"\n✅ Deployment complete!")
    print(f"🌐 Repository: https://github.com/{repo_name}")
    print(f"📦 Release: https://github.com/{repo_name}/releases/tag/{version}")
    print(f"\n🎯 Next Steps:")
    print(f"   1. Enable GitHub Pages in repository settings")
    print(f"   2. Verify workflows in Actions tab")
    print(f"   3. Check status banner rendering")

def main():
    parser = argparse.ArgumentParser(description="Deploy Supersonic v4 to GitHub")
    parser.add_argument("--repo", required=True, help="Repository name (owner/repo)")
    parser.add_argument("--version", default="1.0.0", help="Version tag (default: 1.0.0)")
    parser.add_argument("--no-create", action="store_true", help="Don't create repo, just push")
    
    args = parser.parse_args()
    
    deploy(args.repo, args.version, create_repo=not args.no_create)

if __name__ == "__main__":
    main()
