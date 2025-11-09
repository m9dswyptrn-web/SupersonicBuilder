#!/usr/bin/env python3
"""
supersonic_preflight.py
Preflight checks before snapshot/push/deploy (Replit-friendly).

What it does
------------
- Verifies: git installed, inside a repo, current branch, remote "origin"
- Shows: pending changes, last commit, default branch guess
- Checks env: GH_TOKEN/GITHUB_TOKEN, GITHUB_REPOSITORY, git user.name/email
- Prints EXACT commands to run for safe push
- Optional --fix: set user.name/email if missing; add origin if GIT_REMOTE_URL is provided
- Optional --push: add/commit/push with a standardized message

Usage
-----
  python3 supersonic_preflight.py           # read-only checks
  python3 supersonic_preflight.py --fix     # applies minor fixes (idempotent)
  python3 supersonic_preflight.py --push    # commits and pushes (uses existing remote)
Env (optional)
-------------
  GIT_AUTHOR_NAME   (fallback: SonicBuilder Bot)
  GIT_AUTHOR_EMAIL  (fallback: bot@sonicbuilder.local)
  GIT_REMOTE_URL    (used by --fix to create 'origin' if missing)
"""

import os, sys, subprocess, shlex
from pathlib import Path
from datetime import datetime

def sh(cmd, check=True):
    p = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if check and p.returncode != 0:
        raise RuntimeError(f"$ {cmd}\n{p.stdout}")
    return p.stdout.strip()

def safe(cmd):
    try: return sh(cmd, check=False).strip()
    except Exception as e: return f"(error: {e})"

def header(title):
    print("\n" + "="*64)
    print(title)
    print("="*64)

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="apply minor fixes (git user, origin if env provided)")
    ap.add_argument("--push", action="store_true", help="git add/commit/push to origin/<branch>")
    args = ap.parse_args()

    # Section: system & repo
    header("Preflight: System & Repo")
    git_ver = safe("git --version")
    print(f"git: {git_ver}")
    inside = safe("git rev-parse --is-inside-work-tree")
    print(f"inside git repo: {inside}")
    if "true" not in inside:
        print("NOT inside a git repo. Run: git init")
        if args.push or args.fix:
            print("Aborting due to missing repo.")
            sys.exit(2)

    # Current branch & last commit
    branch = safe("git symbolic-ref --short HEAD") or "(detached?)"
    last   = safe("git log -1 --pretty=%h %s (%cI) || true")
    print(f"current branch: {branch}")
    print(f"last commit   : {last}")

    # Remote
    origin = safe("git remote get-url origin")
    print(f"remote origin : {origin}")
    if "error" in origin or not origin or origin.startswith("fatal:"):
        print("No remote 'origin' configured. Set GIT_REMOTE_URL and use --fix to add it.")
    else:
        print("Remote 'origin' looks set.")

    # Default branch guess
    origin_head = safe("git symbolic-ref refs/remotes/origin/HEAD | sed 's#.*/##'")
    guess_def = origin_head or ("main" if safe("git rev-parse --verify main") else "master")
    print(f"default branch guess: {guess_def if guess_def else '(unknown)'}")

    # Pending changes
    status = safe("git status --porcelain")
    print("pending changes:", "yes" if status else "no")
    if status:
        print("\n--- git status --porcelain ---")
        print(status)

    # Env & identity
    header("Preflight: Identity & Tokens")
    user = safe("git config user.name")
    email = safe("git config user.email")
    gh_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    gh_repo  = os.getenv("GITHUB_REPOSITORY","")
    print(f"git user.name      : {user or '(not set)'}")
    print(f"git user.email     : {email or '(not set)'}")
    print(f"GITHUB_REPOSITORY  : {gh_repo or '(unset; format: owner/repo)'}")
    print(f"GH_TOKEN present   : {'yes' if gh_token else 'no'}")

    if args.fix:
        print("\nApplying minor fixes…")
        if not user:
            name = os.getenv("GIT_AUTHOR_NAME","SonicBuilder Bot")
            print(f"  - Setting git user.name to '{name}'")
            print(safe(shlex.quote(f'git config user.name "{name}"')))
            sh(f'git config user.name "{name}"', check=False)
        if not email:
            mail = os.getenv("GIT_AUTHOR_EMAIL","bot@sonicbuilder.local")
            print(f"  - Setting git user.email to '{mail}'")
            sh(f'git config user.email "{mail}"', check=False)
        if ("error" in origin or not origin or origin.startswith("fatal:")) and os.getenv("GIT_REMOTE_URL"):
            remote_url = os.getenv("GIT_REMOTE_URL")
            print(f"  - Adding remote origin: {remote_url}")
            sh(f"git remote add origin {shlex.quote(remote_url)}", check=False)
        print("Fixes applied (if any).")

    # Recommended commands
    header("Recommended Commands")
    cmds = []
    cmds.append("git add -A")
    cmds.append('git status --porcelain')
    commit = '[sync] preflight snapshot ' + datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    cmds.append(f'git commit -m "{commit}" || true')
    if origin and not origin.startswith("fatal:"):
        cmds.append("git fetch --prune")
        cmds.append("git pull --rebase --autostash || git merge --no-edit")
        cmds.append(f"git push --set-upstream origin {branch}")
    else:
        cmds.append("# No origin set. Set GIT_REMOTE_URL and run with --fix, or run:")
        cmds.append("#   git remote add origin https://github.com/<owner>/<repo>.git")
        cmds.append(f"#   git push --set-upstream origin {branch}")

    print("\n".join(f"$ {c}" for c in cmds))

    if args.push:
        print("\nExecuting push sequence…")
        for c in cmds:
            if c.startswith("#"): 
                print(c); continue
            sh(c, check=False)
        print("Push sequence complete.")

if __name__ == "__main__":
    main()
