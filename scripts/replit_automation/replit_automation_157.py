#!/usr/bin/env python3
"""
deploy_github.py  —  One-and-done GitHub push for your Supersonic project.

Features:
- Works with either GitHub CLI (`gh`) or a Personal Access Token (`GITHUB_TOKEN`).
- Initializes git repo, sets author, default branch, adds .gitignore and (optional) LFS.
- Creates remote repo if missing, commits all, pushes (optionally force-with-lease).
- Drops a minimal GitHub Actions workflow to sanity-check the project.

Usage:
  python3 deploy_github.py

Environment (set before running OR edit defaults below):
  GITHUB_OWNER         : your GitHub username or org (e.g. "christopherelgin")
  GITHUB_REPO          : repository name to create/push (e.g. "SonicBuilder")
  GITHUB_TOKEN         : classic or fine-grained PAT (only required if not using `gh`)
  GIT_AUTHOR_NAME      : commit author name
  GIT_AUTHOR_EMAIL     : commit author email
  GIT_DEFAULT_BRANCH   : default branch (default: "main")
  COMMIT_MSG           : commit message (default: "Supersonic: initial import")
  PUSH_FORCE           : "1" to --force-with-lease (default: "0")
  ADD_LFS              : "1" to enable Git LFS for large binaries (default: "1")
  ADD_WORKFLOW         : "1" to add CI workflow (default: "1")
  VISIBILITY           : "private" | "public" (default: "private")
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# --------- Config (env with sane defaults) ----------
OWNER   = os.getenv("GITHUB_OWNER",   "your-username-or-org")
REPO    = os.getenv("GITHUB_REPO",    "SonicBuilder")
TOKEN   = os.getenv("GITHUB_TOKEN",   "")
AUTHOR  = os.getenv("GIT_AUTHOR_NAME","Supersonic Bot")
EMAIL   = os.getenv("GIT_AUTHOR_EMAIL","bot@example.com")
BRANCH  = os.getenv("GIT_DEFAULT_BRANCH","main")
MSG     = os.getenv("COMMIT_MSG","Supersonic: initial import")
PUSH_FORCE = os.getenv("PUSH_FORCE","0") == "1"
ADD_LFS    = os.getenv("ADD_LFS","1") == "1"
ADD_WORKFLOW = os.getenv("ADD_WORKFLOW","1") == "1"
VISIBILITY = os.getenv("VISIBILITY","private").lower().strip()  # private|public

REMOTE_URL = f"https://github.com/{OWNER}/{REPO}.git"

# LFS patterns that suit this project (tweak freely)
LFS_PATTERNS = [
    "*.zip", "*.7z", "*.rar",
    "assets/audio/*.wav", "assets/audio/*.mp3",
    "static/vendor/**",
    "docs/**/*.pdf", "assets/**/*.pdf",
    "*.png", "*.jpg", "*.jpeg",
]

GITIGNORE = """# Supersonic/Flask/Node/Python common ignores
__pycache__/
*.pyc
.env
.env.*
.venv/
venv/
dist/
build/
node_modules/
*.log
.DS_Store
.replit
replit.nix
.idea/
.vscode/
# Caches
.cache/
*.cache/
pip-wheel-metadata/
# Artifacts
*.zip
*.7z
*.tar
*.tar.gz
*.egg-info/
# Local data
tmp/
local/
"""

WORKFLOW_YML = """name: Supersonic CI

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  sanity:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install basics
        run: |
          python -m pip install --upgrade pip
          # Optional: add your runtime deps here, e.g. Flask if you want to smoke-test app import
          pip install flask
      - name: Smoke test app import
        run: |
          python - <<'PY'
          try:
              import app
              print("✅ app.py import OK")
          except Exception as e:
              print("❌ app.py import failed:", e)
              raise
          PY
"""

def run(cmd, check=True, capture=False):
    if capture:
        return subprocess.run(cmd, check=check, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout
    subprocess.run(cmd, check=check)

def have_cmd(bin_name: str) -> bool:
    return shutil.which(bin_name) is not None

def git(*args, check=True, capture=False):
    return run(["git", *args], check=check, capture=capture)

def ensure_git_repo():
    if not (ROOT / ".git").exists():
        print("→ Initializing git repo")
        git("init", "-b", BRANCH)
    else:
        # ensure branch exists/checked out
        try:
            git("rev-parse", "--verify", BRANCH)
        except subprocess.CalledProcessError:
            git("checkout", "-b", BRANCH)
        else:
            git("checkout", BRANCH)

    print("→ Setting author")
    git("config", "user.name", AUTHOR)
    git("config", "user.email", EMAIL)

def ensure_gitignore():
    gi = ROOT / ".gitignore"
    if not gi.exists():
        gi.write_text(GITIGNORE)
        print("→ Wrote .gitignore")

def ensure_lfs():
    if not ADD_LFS:
        print("→ Skipping Git LFS setup (ADD_LFS=0)")
        return
    if not have_cmd("git"):
        raise SystemExit("git not found in PATH")
    print("→ Ensuring Git LFS")
    if not have_cmd("git-lfs"):
        print("  ! git-lfs not found; skipping LFS (install it to use).")
        return
    run(["git", "lfs", "install"])
    gattr = ROOT / ".gitattributes"
    existing = gattr.read_text() if gattr.exists() else ""
    lines = existing.splitlines()
    changed = False
    for pat in LFS_PATTERNS:
        rule = f"{pat} filter=lfs diff=lfs merge=lfs -text"
        if rule not in lines:
            lines.append(rule)
            changed = True
    if changed:
        gattr.write_text("\n".join(lines) + "\n")
        print(f"→ Updated .gitattributes with {len(LFS_PATTERNS)} LFS patterns")
    else:
        print("→ .gitattributes already contains LFS patterns")

def ensure_workflow():
    if not ADD_WORKFLOW:
        print("→ Skipping workflow (ADD_WORKFLOW=0)")
        return
    wf_dir = ROOT / ".github" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    wf = wf_dir / "supersonic-ci.yml"
    if not wf.exists():
        wf.write_text(WORKFLOW_YML)
        print("→ Added .github/workflows/supersonic-ci.yml")

def repo_exists_remote() -> bool:
    if have_cmd("gh"):
        try:
            out = run(["gh", "repo", "view", f"{OWNER}/{REPO}"], check=True, capture=True)
            return True
        except subprocess.CalledProcessError:
            return False
    # Fallback: unauthenticated HEAD may 401; prefer API if token present
    if TOKEN:
        import urllib.request, urllib.error
        req = urllib.request.Request(
            f"https://api.github.com/repos/{OWNER}/{REPO}",
            headers={"Authorization": f"Bearer {TOKEN}",
                     "Accept":"application/vnd.github+json",
                     "X-GitHub-Api-Version":"2022-11-28"}
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            # other codes → assume doesn't exist
            return False
    # No token and no gh; we’ll just try pushing and let it fail if missing.
    return True

def create_repo_if_needed():
    if repo_exists_remote():
        print(f"→ Remote repo {OWNER}/{REPO} already exists")
        return

    print(f"→ Creating repo {OWNER}/{REPO} ({VISIBILITY})")
    if have_cmd("gh"):
        vis_flag = "--private" if VISIBILITY == "private" else "--public"
        run(["gh", "repo", "create", f"{OWNER}/{REPO}", vis_flag, "--confirm"])
        return

    if not TOKEN:
        raise SystemExit("No gh and no GITHUB_TOKEN set; cannot create repo automatically.")

    import urllib.request
    payload = {
        "name": REPO,
        "private": (VISIBILITY == "private"),
        "has_issues": True,
        "has_projects": False,
        "has_wiki": False,
        "auto_init": False,
      # default_branch is ignored on create without auto_init; we set branch locally.
    }
    if "/" in OWNER:
        # unlikely: treat as org path; else default user
        api = f"https://api.github.com/orgs/{OWNER}/repos"
    else:
        api = "https://api.github.com/user/repos"

    req = urllib.request.Request(
        api,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Accept":"application/vnd.github+json",
                 "X-GitHub-Api-Version":"2022-11-28"}
    )
    with urllib.request.urlopen(req) as resp:
        if resp.status not in (200,201):
            raise SystemExit(f"GitHub API create repo failed: HTTP {resp.status}")
    print("→ Repo created via API")

def ensure_remote():
    remotes = git("remote", "-v", capture=True)
    if "origin" not in remotes:
        print(f"→ Adding remote origin {REMOTE_URL}")
        git("remote", "add", "origin", REMOTE_URL)
    else:
        print("→ Remote origin already set")

def commit_and_push():
    print("→ Adding files")
    git("add", "-A")

    has_commit = True
    try:
        git("rev-parse", "HEAD", capture=True)
    except subprocess.CalledProcessError:
        has_commit = False

    if has_commit:
        print(f"→ Committing: {MSG}")
        git("commit", "-m", MSG, check=False)  # allow no-op commit
    else:
        print(f"→ First commit: {MSG}")
        git("commit", "-m", MSG)

    print("→ Pushing to GitHub")
    if PUSH_FORCE:
        git("push", "-u", "origin", BRANCH, "--force-with-lease")
    else:
        git("push", "-u", "origin", BRANCH)

def main():
    print("=== Supersonic GitHub Deploy ===")
    if OWNER == "your-username-or-org":
        print("! Set GITHUB_OWNER to your username/org.")
        sys.exit(1)

    ensure_git_repo()
    ensure_gitignore()
    ensure_lfs()
    ensure_workflow()
    create_repo_if_needed()
    ensure_remote()
    commit_and_push()

    print("\n✅ Done.")
    print(f"Repo: https://github.com/{OWNER}/{REPO}")
    print(f"Branch: {BRANCH}")
    print("\nTips:")
    print(" - To change visibility: VISIBILITY=public (or private)")
    print(" - To skip LFS: ADD_LFS=0")
    print(" - To skip CI workflow: ADD_WORKFLOW=0")
    print(" - To force update: PUSH_FORCE=1")

if __name__ == "__main__":
    main()