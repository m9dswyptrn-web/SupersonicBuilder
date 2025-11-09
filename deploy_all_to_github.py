#!/usr/bin/env python3
"""
Deploy EVERYTHING from Replit to GitHub and tag a release.

- Reads VERSION if present; else makes tag vYYYY.MM.DD.HHMM.
- Commits only when there are changes.
- Pushes main + tags.
"""

import os, subprocess, sys, time, pathlib, re

OWNER = os.getenv("GITHUB_USER", "m9dswyptrn-web")
REPO  = os.getenv("REPO_SLUG", "SonicBuilder")

def sh(cmd: str):
    print("➜", cmd, flush=True)
    return subprocess.run(cmd, shell=True, check=True)

def sh_out(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True, text=True).strip()

def read_version() -> str:
    p = pathlib.Path("VERSION")
    if p.exists():
        v = p.read_text().strip()
        v = re.sub(r"\s+", "", v)
        if v:
            return v
    return time.strftime("v%Y.%m.%d.%H%M")

def ensure_git_identity():
    def get(cfg):
        try:
            return sh_out(f"git config {cfg} || true").strip()
        except Exception:
            return ""
    name  = get("user.name")
    email = get("user.email")
    if not name:
        sh('git config user.name "SonicBuilder AutoDeploy"')
    if not email:
        sh('git config user.email "autodeploy@users.noreply.github.com"')

def main():
    ensure_git_identity()

    # init if needed
    if not pathlib.Path(".git").exists():
        sh("git init")
        sh("git add .")
        sh('git commit -m "chore(init): initial import" || true')

    sh("git branch -M main || true")

    # add/commit only if anything changed
    sh("git add -A")
    status = sh_out("git status --porcelain")
    if status.strip():
        msg = f'chore(deploy): auto-commit from Replit at {time.strftime("%Y-%m-%d %H:%M:%S")}'
        sh(f'git commit -m "{msg}"')
    else:
        print("ℹ️  No file changes to commit.")

    # remote
    remotes = sh_out("git remote -v || true")
    if "origin" not in remotes:
        sh(f"git remote add origin https://github.com/{OWNER}/{REPO}.git")

    # push main
    sh("git push -u origin main")

    # tag
    version = read_version()
    existing = sh_out("git tag --points-at HEAD")
    if version in existing.split():
        print(f"ℹ️  Tag {version} already at HEAD.")
    else:
        sh(f"git tag {version}")

    sh("git push --tags")

    print("\n✅ Deploy complete.")
    print(f"   Repo:    https://github.com/{OWNER}/{REPO}")
    print(f"   Actions: https://github.com/{OWNER}/{REPO}/actions")

if __name__ == "__main__":
    main()
