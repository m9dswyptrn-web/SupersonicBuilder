#!/usr/bin/env python3
"""
SonicBuilder Rollback Helper
Provides manual rollback functionality to specific tags or commits
"""

import os
import subprocess
import sys
import argparse

def run(cmd, check=True):
    """Execute shell command"""
    print(f"→ {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0 and check:
        print(res.stderr)
        sys.exit(1)
    return res

def list_recent_commits(count=10):
    """List recent commits"""
    print(f"📋 Last {count} commits:\n")
    run(f"git log --oneline -n {count}")

def list_tags():
    """List available tags"""
    print("🏷️  Available tags:\n")
    run("git tag -l")

def rollback_to_commit(commit_hash):
    """Rollback to specific commit"""
    print(f"\n⚠️  Rolling back to commit: {commit_hash}")
    
    # Verify commit exists
    res = run(f"git cat-file -t {commit_hash}", check=False)
    if res.returncode != 0:
        print(f"❌ Commit {commit_hash} not found")
        sys.exit(1)
    
    # Checkout commit
    run(f"git checkout {commit_hash}")
    
    # Force push
    print("\n🚀 Pushing rollback to remote...")
    run("git push -f origin main")
    
    print(f"\n✅ Successfully rolled back to {commit_hash}")

def rollback_to_tag(tag):
    """Rollback to specific tag"""
    print(f"\n⚠️  Rolling back to tag: {tag}")
    
    # Verify tag exists
    res = run(f"git rev-parse {tag}", check=False)
    if res.returncode != 0:
        print(f"❌ Tag {tag} not found")
        sys.exit(1)
    
    # Checkout tag
    run(f"git checkout {tag}")
    
    # Force push
    print("\n🚀 Pushing rollback to remote...")
    run("git push -f origin main")
    
    print(f"\n✅ Successfully rolled back to tag {tag}")

def rollback_steps(steps=1):
    """Rollback N commits"""
    print(f"\n⚠️  Rolling back {steps} commit(s)...")
    
    # Reset HEAD
    run(f"git reset --hard HEAD~{steps}")
    
    # Force push
    print("\n🚀 Pushing rollback to remote...")
    run("git push -f origin main")
    
    print(f"\n✅ Successfully rolled back {steps} commit(s)")

def main():
    parser = argparse.ArgumentParser(description="SonicBuilder Rollback Helper")
    parser.add_argument("--list-commits", type=int, metavar="N", help="List last N commits")
    parser.add_argument("--list-tags", action="store_true", help="List available tags")
    parser.add_argument("--commit", metavar="HASH", help="Rollback to specific commit")
    parser.add_argument("--tag", metavar="TAG", help="Rollback to specific tag")
    parser.add_argument("--steps", type=int, metavar="N", help="Rollback N commits")
    
    args = parser.parse_args()
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     🔄 SonicBuilder Rollback Helper                           ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    
    if args.list_commits:
        list_recent_commits(args.list_commits)
    elif args.list_tags:
        list_tags()
    elif args.commit:
        rollback_to_commit(args.commit)
    elif args.tag:
        rollback_to_tag(args.tag)
    elif args.steps:
        rollback_steps(args.steps)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
