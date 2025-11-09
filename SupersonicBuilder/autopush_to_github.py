#!/usr/bin/env python3
import os, sys, json, subprocess, urllib.request, urllib.error
from pathlib import Path

# ==== Config (env overrides recommended) ====
TOKEN      = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or os.getenv("GIT_TOKEN")
OWNER      = os.getenv("GITHUB_OWNER", "").strip()     # e.g. "m9dswyptrn-web"; auto-detected if blank
REPO_NAME  = os.getenv("REPO_NAME", "SupersonicBuilder").strip()
BRANCH     = os.getenv("GIT_DEFAULT_BRANCH", "main").strip()
PRIVATE    = os.getenv("GITHUB_REPO_PRIVATE", "true").lower() in ("1","true","yes")
COMMIT_MSG = os.getenv("GIT_COMMIT_MESSAGE",
                       "Initial push: code only (ignore large artifacts)")
BIG_MB     = float(os.getenv("BIGFILE_MB", "95"))   # auto-untrack files >= BIG_MB

GITIGNORE_SNIPPET = """\
# --- Auto GitHub push defaults ---
# Large/binary artifacts
*.zip
*.tar
*.tar.gz
*.7z
*.rar
*.iso

# Build / output
build/
dist/
release/
exports/
downloads/

# General noise
__pycache__/
*.pyc
.DS_Store
.replit
*.log
"""

def sh(cmd, check=True, quiet=False):
    if not quiet:
        print("$", " ".join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if not quiet:
        print(p.stdout, end="")
    if check and p.returncode != 0:
        sys.exit(p.returncode)
    return p.stdout

# ---------- GitHub API helpers ----------
def gh(path, method="GET", data=None):
    if not TOKEN:
        print("❌ Missing GITHUB_TOKEN (classic token with `repo` scope) in Replit Secrets.")
        sys.exit(1)
    url = f"https://api.github.com{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": "push-via-shell",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        txt = e.read().decode()
        print(f"GitHub API error {e.code} on {path}:\n{txt}")
        sys.exit(1)

def ensure_repo_exists(owner):
    # Return True if existed already
    try:
        gh(f"/repos/{owner}/{REPO_NAME}")
        print("ℹ️ Repo exists on GitHub.")
        return True
    except SystemExit:
        # propagated, already printed
        raise
    except Exception:
        pass
    # try create
    payload = {"name": REPO_NAME, "private": PRIVATE, "auto_init": False}
    me = gh("/user")["login"]
    if me.lower() == owner.lower():
        gh("/user/repos", method="POST", data=payload)
    else:
        gh(f"/orgs/{owner}/repos", method="POST", data=payload)
    print("✅ Created repo on GitHub.")
    return False

# ---------- Repo prep ----------
def clear_git_lock():
    lock = Path(".git/index.lock")
    if lock.exists():
        print("🔓 Removing stale .git/index.lock")
        lock.unlink(missing_ok=True)

def ensure_repo_and_branch():
    if not Path(".git").is_dir():
        sh(["git", "init"])
    sh(["git", "checkout", "-B", BRANCH])
    sh(["git", "config", "user.name",  os.getenv("GIT_USER_NAME", "replit-bot")])
    sh(["git", "config", "user.email", os.getenv("GIT_USER_EMAIL","replit-bot@users.noreply.github.com")])

def update_gitignore():
    p = Path(".gitignore")
    text = p.read_text() if p.exists() else ""
    if "# --- Auto GitHub push defaults ---" not in text:
        if text and not text.endswith("\n"):
            text += "\n"
        p.write_text(text + GITIGNORE_SNIPPET)
        sh(["git", "add", ".gitignore"], check=False)

def list_big_files():
    threshold = BIG_MB * 1024 * 1024
    out = []
    for path in Path(".").rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        try:
            sz = path.stat().st_size
        except OSError:
            continue
        if sz >= threshold:
            out.append((sz, str(path)))
    out.sort(reverse=True)
    return out

def untrack_heavy_patterns():
    sh(["git", "rm", "--cached", "-r", "*.zip", "*.tar", "*.tar.gz", "*.7z", "*.rar",
        "build", "dist", "release", "exports", "downloads"], check=False)

def ensure_remote(owner):
    # Use tokened URL for first push (avoids auth prompts)
    url = f"https://{owner}:{TOKEN}@github.com/{owner}/{REPO_NAME}.git"
    remotes = sh(["git", "remote"], check=False, quiet=True).split()
    if "origin" not in remotes:
        sh(["git", "remote", "add", "origin", url], check=False)
    else:
        sh(["git", "remote", "set-url", "origin", url], check=False)
    # Make git tolerant on slow networks
    sh(["git", "config", "http.postBuffer", "524288000"], check=False)
    sh(["git", "config", "http.lowSpeedLimit", "0"], check=False)
    sh(["git", "config", "http.lowSpeedTime", "999999"], check=False)

def main():
    print("=== Push via Shell -> GitHub ===")

    if not TOKEN:
        print("❌ Set GITHUB_TOKEN in Replit Secrets (classic token with `repo` scope).")
        sys.exit(1)

    clear_git_lock()
    ensure_repo_and_branch()
    update_gitignore()
    untrack_heavy_patterns()

    # auto-detect owner if not provided
    owner = OWNER or gh("/user")["login"]
    print(f"Owner: {owner}\nRepo : {REPO_NAME} ({'private' if PRIVATE else 'public'})")

    ensure_repo_exists(owner)

    # remove any truly big files from tracking
    big = list_big_files()
    if big:
        print(f"🔎 Big files (>= {BIG_MB:.0f} MB) — untracking:")
        for sz, p in big[:20]:
            print(f"  {sz/1048576:7.2f} MB  {p}")
            sh(["git", "rm", "--cached", "-f", p], check=False)

    # stage + commit if needed
    sh(["git", "add", "-A"], check=False)
    status = sh(["git", "status", "--porcelain"], check=False, quiet=True)
    if status.strip():
        sh(["git", "commit", "-m", COMMIT_MSG], check=False)
    else:
        print("ℹ️ Nothing to commit.")

    ensure_remote(owner)
    print(f"🚀 Pushing to origin/{BRANCH} …")
    sh(["git", "push", "-u", "origin", BRANCH], check=False)

    # switch to clean remote (no token) after success
    clean = f"https://github.com/{owner}/{REPO_NAME}.git"
    sh(["git", "remote", "set-url", "origin", clean], check=False)
    print("\n✅ Done. View your repo:")
    print(f"   {clean}")

if __name__ == "__main__":
    main()
