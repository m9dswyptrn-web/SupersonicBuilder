#!/usr/bin/env python3
"""
Supersonic_Health_Extension.py
Health + Sync endpoints for FastAPI or Flask, with boot banner & boot log rotation.

Endpoints:
  GET  /api/ping    → JSON: uptime, git (branch/remote/head/dirty), last sync
  GET  /api/status  → JSON: raw sync state
  GET  /api/ready   → "OK" (200) if healthy or never-run; "ERROR: ..." (503) if last sync failed
  POST /api/sync    → starts background sync (commit unstaged -> fetch -> ff/rebase/merge -> push)

Usage:
  from Supersonic_Health_Extension import attach
  app = FastAPI() or Flask(__name__)
  attach(app)

Env (optional):
  GH_TOKEN, GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL, GITHUB_REPOSITORY
  BOOT_MAX_SIZE_BYTES, BOOT_KEEP_FILES, BOOT_MAX_TOTAL_MB   (boot banner rotation controls)
"""
import os, subprocess, hashlib, threading, time, socket, gzip, shutil
from pathlib import Path
from datetime import datetime

BOOT_TIME = time.time()
STATE = {"last_started": None, "last_finished": None, "last_ok": None,
         "last_msg": "never run", "last_commit": None}

def sh(cmd: str, check: bool = True) -> str:
    p = subprocess.run(cmd, shell=True, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if check and p.returncode != 0:
        raise RuntimeError(f"$ {cmd}\n{p.stdout}")
    return p.stdout

def _ensure_git_identity():
    name  = os.getenv("GIT_AUTHOR_NAME",  "SonicBuilder Bot")
    email = os.getenv("GIT_AUTHOR_EMAIL", "bot@sonicbuilder.local")
    sh(f'git config user.name "{name}"')
    sh(f'git config user.email "{email}"')

def _detect_default_branch() -> str:
    out = sh("git symbolic-ref refs/remotes/origin/HEAD", check=False).strip()
    if out and "/" in out: return out.split("/")[-1]
    for b in ("main","master"):
        if sh(f"git rev-parse --verify {b}", check=False).strip(): return b
    return "main"

def _commit_any_changes():
    sh("git add -A")
    status = sh("git status --porcelain").strip()
    if status:
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        tree = sh("git write-tree").strip()
        digest = hashlib.sha1(tree.encode()).hexdigest()[:8]
        msg = f"[sync] Replit auto-sync @ {ts} (tree {digest})"
        sh(f'git commit -m "{msg}"')
        STATE["last_commit"] = msg
    else:
        STATE["last_commit"] = "(no local changes)"

def _pull_reconcile_push(branch: str):
    sh("git fetch --prune")
    sh(f"git checkout -B {branch}")
    out = sh(f"git merge --ff-only origin/{branch}", check=False)
    if "fatal:" in out or "not something we can merge" in out:
        rebase = sh(f"git rebase origin/{branch}", check=False)
        if "CONFLICT" in rebase:
            sh("git rebase --abort", check=False)
            sh(f"git merge --no-edit origin/{branch}", check=True)
    sh(f"git push --set-upstream origin {branch}")

def _run_sync():
    _ensure_git_identity()
    branch = _detect_default_branch()
    _commit_any_changes()
    _pull_reconcile_push(branch)

def _sync_job():
    try:
        STATE["last_started"]  = datetime.utcnow().isoformat()+"Z"
        _run_sync()
        STATE["last_ok"]  = True
        STATE["last_msg"] = "sync completed"
    except Exception as e:
        STATE["last_ok"]  = False
        STATE["last_msg"] = str(e)
    finally:
        STATE["last_finished"] = datetime.utcnow().isoformat()+"Z"

# ---------- Boot banner + rotation ----------
BOOT_LOG_PATH = Path("logs/boot.log")
BOOT_ARCHIVE_DIR = Path("logs/archive")
BOOT_MAX_SIZE_BYTES = int(os.getenv("BOOT_MAX_SIZE_BYTES", str(512 * 1024)))
BOOT_KEEP_FILES = int(os.getenv("BOOT_KEEP_FILES", "5"))
BOOT_MAX_TOTAL_MB = int(os.getenv("BOOT_MAX_TOTAL_MB", "10"))

def _guess_base_url() -> str:
    for k in ("REPLIT_WEB_URL","REPLIT_APP_URL","WEB_URL"):
        v=os.getenv(k); 
        if v and v.startswith("http"): return v.rstrip("/")
    host = os.getenv("HOST","localhost"); port=os.getenv("PORT","8000")
    return f"http://{host}:{port}"

def _rotate_boot_logs_if_needed():
    try:
        BOOT_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        if not BOOT_LOG_PATH.exists(): return
        if BOOT_LOG_PATH.stat().st_size < BOOT_MAX_SIZE_BYTES: return
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        raw = BOOT_ARCHIVE_DIR / f"boot.{ts}.log"
        gz  = BOOT_ARCHIVE_DIR / f"boot.{ts}.log.gz"
        shutil.move(str(BOOT_LOG_PATH), raw)
        with open(raw,"rb") as fin, gzip.open(gz,"wb",compresslevel=6) as fout:
            shutil.copyfileobj(fin,fout)
        raw.unlink(missing_ok=True)
        # keep last N
        archives = sorted(BOOT_ARCHIVE_DIR.glob("boot.*.log.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in archives[BOOT_KEEP_FILES:]:
            old.unlink(missing_ok=True)
        # cap total size
        def total_mb():
            return sum(p.stat().st_size for p in BOOT_ARCHIVE_DIR.glob("boot.*.log.gz"))/(1024*1024)
        archives = sorted(BOOT_ARCHIVE_DIR.glob("boot.*.log.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
        while total_mb() > BOOT_MAX_TOTAL_MB and len(archives) > 1:
            victim = archives.pop(); victim.unlink(missing_ok=True)
    except Exception as e:
        print(f"[WARN] log rotation failed: {e}")

def _log_banner_to_file(text: str):
    try:
        BOOT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(BOOT_LOG_PATH,"a",encoding="utf-8") as f:
            ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            f.write(f"\n[{ts}] Boot Banner\n{text}\n")
    except Exception as e:
        print(f"[WARN] Could not write boot log: {e}")
    _rotate_boot_logs_if_needed()

def _print_banner():
    base = _guess_base_url()
    try:
        branch = sh("git symbolic-ref --short HEAD", check=False).strip() or "main"
        remote = sh("git remote get-url origin", check=False).strip() or "(no remote)"
    except Exception:
        branch, remote = "main", "(unknown)"
    repo = os.getenv("GITHUB_REPOSITORY","(unset)")
    banner = (
        "\n"+"="*64+"\n"
        " Supersonic Health & Sync online 🚀\n"
        + "-"*64 + "\n"
        + f" Host        : {socket.gethostname()}\n"
        + f" Base URL    : {base}\n"
        + f" Repo        : {repo}\n"
        + f" Git branch  : {branch}\n"
        + f" Git remote  : {remote}\n"
        + "-"*64 + "\n"
        + f" GET  {base}/api/ping\n"
        + f" GET  {base}/api/ready\n"
        + f" GET  {base}/api/status\n"
        + f" POST {base}/api/sync\n"
        + "="*64 + "\n"
    )
    print(banner); _log_banner_to_file(banner)

# ---------- FastAPI adapter ----------
def _attach_fastapi(app):
    from fastapi import APIRouter
    from pydantic import BaseModel
    from fastapi.responses import PlainTextResponse
    router = APIRouter(prefix="/api", tags=["sync"])
    class SyncQueued(BaseModel):
        queued: bool; message: str
    @router.post("/sync", response_model=SyncQueued, status_code=202)
    def api_sync_now():
        t = threading.Thread(target=_sync_job, daemon=True); t.start()
        return SyncQueued(queued=True, message="Sync started")
    @router.get("/status")
    def api_status(): return STATE
    @router.get("/ping")
    def api_ping():
        def safe(cmd, default=""):
            try: return sh(cmd, check=False).strip()
            except Exception: return default
        branch=_detect_default_branch()
        remote=safe("git remote get-url origin"); head=safe("git rev-parse --short HEAD")
        dirty=bool(safe("git status --porcelain")); last=safe("git log -1 --pretty=%cI || true")
        if STATE["last_ok"] is True: status,ok="green",True
        elif STATE["last_ok"] is False: status,ok="red",False
        else: status,ok="yellow",True
        return {
            "ok": ok, "status": status, "ts": datetime.utcnow().isoformat()+"Z",
            "uptime_sec": int(time.time()-BOOT_TIME), "host": socket.gethostname(),
            "git": {"branch":branch,"remote":remote,"head":head,"dirty":dirty,"last_commit_time":last},
            "sync": STATE,
            "env": {"repo":os.getenv("GITHUB_REPOSITORY",""),
                    "gh_token":"present" if (os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")) else "missing",
                    "port":os.getenv("PORT",""), "mode":os.getenv("APP_MODE","prod")}
        }
    @router.get("/ready", response_class=PlainTextResponse)
    def api_ready():
        ok = STATE.get("last_ok")
        if ok is True or STATE["last_msg"] == "never run":
            return PlainTextResponse("OK", status_code=200)
        return PlainTextResponse(f"ERROR: {STATE.get('last_msg','unknown')}", status_code=503)
    app.include_router(router)

# ---------- Flask adapter ----------
def _attach_flask(app):
    from flask import Blueprint, jsonify
    from flask import Response as FlaskResponse
    bp = Blueprint("sync_bp", __name__, url_prefix="/api")
    @bp.route("/sync", methods=["POST"])
    def api_sync_now():
        t = threading.Thread(target=_sync_job, daemon=True); t.start()
        return jsonify({"queued":True,"message":"Sync started"}), 202
    @bp.route("/status", methods=["GET"])
    def api_status(): return jsonify(STATE), 200
    @bp.route("/ping", methods=["GET"])
    def api_ping():
        def safe(cmd, default=""):
            try: return sh(cmd, check=False).strip()
            except Exception: return default
        branch=_detect_default_branch()
        remote=safe("git remote get-url origin"); head=safe("git rev-parse --short HEAD")
        dirty=bool(safe("git status --porcelain")); last=safe("git log -1 --pretty=%cI || true")
        if STATE["last_ok"] is True: status,ok="green",True
        elif STATE["last_ok"] is False: status,ok="red",False
        else: status,ok="yellow",True
        return jsonify({
            "ok":ok,"status":status,"ts":datetime.utcnow().isoformat()+"Z",
            "uptime_sec":int(time.time()-BOOT_TIME),"host":socket.gethostname(),
            "git":{"branch":branch,"remote":remote,"head":head,"dirty":dirty,"last_commit_time":last},
            "sync":STATE,
            "env":{"repo":os.getenv("GITHUB_REPOSITORY",""),
                   "gh_token":"present" if (os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")) else "missing",
                   "port":os.getenv("PORT",""),"mode":os.getenv("APP_MODE","prod")}
        }), 200
    @bp.route("/ready", methods=["GET"])
    def api_ready():
        ok = STATE.get("last_ok")
        if ok is True or STATE["last_msg"] == "never run":
            return FlaskResponse("OK", status=200, mimetype="text/plain")
        return FlaskResponse(f"ERROR: {STATE.get('last_msg','unknown')}", status=503, mimetype="text/plain")
    app.register_blueprint(bp)

def attach(app):
    """Detect framework and mount endpoints; print banner."""
    mod = type(app).__module__.lower(); name = type(app).__name__.lower()
    if "fastapi" in mod or "fastapi" in name: _attach_fastapi(app)
    elif "flask" in mod or "flask" in name: _attach_flask(app)
    else: raise RuntimeError("Unsupported app type. Use FastAPI or Flask app instance.")
    try: _print_banner()
    except Exception: pass
