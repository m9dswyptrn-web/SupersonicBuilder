#!/usr/bin/env python3
import os, re, subprocess, sys

def sh(cmd, check=True, capture=False):
    if capture:
        return subprocess.run(cmd, check=check, text=True, shell=True,
                              stdout=subprocess.PIPE).stdout.strip()
    subprocess.run(cmd, check=check, shell=True)

def repo_slug():
    url = sh("git config --get remote.origin.url", capture=True)
    if url:
        url = re.sub(r"\.git$", "", url)
    else:
        sys.exit("❌ Could not detect origin URL.")
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+)$", url)
    if not m:
        sys.exit("❌ Could not detect owner/repo from origin.")
    return f"{m.group(1)}/{m.group(2)}"

def latest_tag():
    try:
        t = sh("git describe --tags --abbrev=0 2>/dev/null || echo v0.0.0", capture=True)
        return t
    except subprocess.CalledProcessError:
        return "v0.0.0"

def bump(base, kind):
    base = base.lstrip("v").split("-")[0]
    try:
        major, minor, patch = [int(x) for x in base.split(".")]
    except Exception:
        major, minor, patch = 0,0,0
    if kind == "major": major, minor, patch = major+1, 0, 0
    elif kind == "minor": minor, patch = minor+1, 0
    else: patch += 1
    return f"v{major}.{minor}.{patch}"

def main():
    kind = "patch"
    explicit = None
    pre = None
    push_branch = False
    branch = os.environ.get("BRANCH", "main")

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--major": kind = "major"
        elif a == "--minor": kind = "minor"
        elif a == "--patch": kind = "patch"
        elif a == "--tag": i += 1; explicit = args[i]
        elif a == "--pre": i += 1; pre = args[i]
        elif a == "--push-branch": push_branch = True
        else:
            sys.exit(f"Unknown arg: {a}")
        i += 1

    if os.environ.get("CLEAN_OK","0") != "1":
        dirty = sh("git status --porcelain", capture=True)
        if dirty:
            sys.exit("❌ Working tree not clean. Commit or stash first.")

    repo = repo_slug()
    tag = explicit or bump(latest_tag(), kind)
    if pre: tag = f"{tag}-{pre}"

    # idempotent
    try:
        sh(f"git rev-parse {tag} >/dev/null 2>&1", check=True)
        print(f"✅ {tag} already exists. Nothing to do.")
        return
    except subprocess.CalledProcessError:
        pass

    sh("git fetch --tags >/dev/null")
    sh(f'git tag -a {tag} -m "SupersonicBuilder {tag}"')

    origin_clean = f"https://github.com/{repo}.git"
    gh_pat = os.environ.get("GH_PAT","")
    origin_temp = origin_clean if not gh_pat else f"https://x-access-token:{gh_pat}@github.com/{repo}.git"

    sh(f'git remote set-url origin "{origin_temp}"')
    sh(f"git push origin {tag}")
    if push_branch:
        sh(f"git push origin {branch}:{branch}")
    sh(f'git remote set-url origin "{origin_clean}"')

    print(f"🎉 Released {tag}")

if __name__ == "__main__":
    main()
