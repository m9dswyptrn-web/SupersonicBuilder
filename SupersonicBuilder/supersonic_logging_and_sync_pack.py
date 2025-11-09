#!/usr/bin/env python3
# supersonic_logging_and_sync_pack.py
# One-and-done installer for health + sync endpoints and rotating logs.

from __future__ import annotations
import os, re, sys, stat, textwrap
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "logs"
ARCH = LOGS / "archive"
SNIPS = ROOT / "snippets"
TOOLS = ROOT / "tools"

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    new = content.rstrip() + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == new:
        print(f"= {path} (unchanged)")
        return False
    path.write_text(new, encoding="utf-8")
    print(f"+ wrote {path}")
    return True

def chmod_exec(path: Path):
    try:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except Exception:
        pass

def append_make_targets():
    mk = ROOT/"Makefile"
    add = textwrap.dedent(r"""
    # --- Supersonic health/sync/log helpers ---
    .PHONY: ping ready log-tail log-size log-archives
    ping:
    	@curl -s ${BASE:-http://localhost:$(PORT)}/api/ping | jq -r . || curl -s ${BASE:-http://localhost:$(PORT)}/api/ping

    ready:
    	@curl -s -o /dev/null -w "%{http_code}\n" ${BASE:-http://localhost:$(PORT)}/api/ready

    log-tail:
    	@tail -n 200 logs/app.log 2>/dev/null || echo "(no logs/app.log yet)"

    log-size:
    	@python3 - <<'PY'
    from pathlib import Path
    p=Path('logs')
    size=sum(f.stat().st_size for f in p.rglob('*') if f.is_file()) if p.exists() else 0
    print(f'Total logs size: {size/1024:.1f} KB')
    PY

    log-archives:
    	@ls -lh logs/archive/*.gz 2>/dev/null || echo "(no archives yet)"
    """).strip()+"\n"

    if not mk.exists():
        mk.write_text(add, encoding="utf-8")
        print("+ created Makefile with supersonic targets")
        return True

    txt = mk.read_text(encoding="utf-8")
    if "Supersonic health/sync/log helpers" in txt:
        print("= Makefile targets already present")
        return False
    with mk.open("a", encoding="utf-8") as f:
        f.write("\n\n"+add)
    print("+ appended supersonic targets to Makefile")
    return True

# --- File contents ---

SUPERSONIC_HEALTH_EXTENSION = r'''#!/usr/bin/env python3
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
'''

ROTATING_LOGGER = r'''#!/usr/bin/env python3
"""
rotating_logger.py — size-rotating logger with gzip + pruning + request logging helpers.
Env:
  APP_LOG_PATH (default logs/app.log)
  APP_LOG_MAX_BYTES (default 1048576)
  APP_LOG_KEEP_FILES (default 7)
  APP_LOG_MAX_TOTAL_MB (default 50)
  APP_LOG_LEVEL (default INFO)
"""
import os, sys, gzip, shutil
from pathlib import Path
from datetime import datetime
import logging
from logging import Logger, Handler, LogRecord

APP_LOG_PATH       = Path(os.getenv("APP_LOG_PATH", "logs/app.log"))
APP_ARCHIVE_DIR    = APP_LOG_PATH.parent / "archive"
APP_LOG_MAX_BYTES  = int(os.getenv("APP_LOG_MAX_BYTES", str(1 * 1024 * 1024)))
APP_LOG_KEEP_FILES = int(os.getenv("APP_LOG_KEEP_FILES", "7"))
APP_LOG_MAX_TOTAL_MB = int(os.getenv("APP_LOG_MAX_TOTAL_MB", "50"))

def _ensure_dirs():
    APP_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    APP_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

def _rotate_if_needed():
    try:
        if not APP_LOG_PATH.exists() or APP_LOG_PATH.stat().st_size < APP_LOG_MAX_BYTES: return
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        raw = APP_ARCHIVE_DIR / f"app.{ts}.log"
        gz  = APP_ARCHIVE_DIR / f"app.{ts}.log.gz"
        shutil.move(str(APP_LOG_PATH), raw)
        with open(raw, "rb") as fin, gzip.open(gz, "wb", compresslevel=6) as fout:
            shutil.copyfileobj(fin, fout)
        raw.unlink(missing_ok=True)
        # keep last N
        archives = sorted(APP_ARCHIVE_DIR.glob("app.*.log.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in archives[APP_LOG_KEEP_FILES:]:
            old.unlink(missing_ok=True)
        # cap total
        def total_mb():
            return sum(p.stat().st_size for p in APP_ARCHIVE_DIR.glob("app.*.log.gz"))/(1024*1024)
        archives = sorted(APP_ARCHIVE_DIR.glob("app.*.log.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
        while total_mb() > APP_LOG_MAX_TOTAL_MB and len(archives) > 1:
            victim = archives.pop(); victim.unlink(missing_ok=True)
    except Exception as e:
        print(f"[WARN] app log rotation failed: {e}", file=sys.stderr)

class _RotatingFileHandler(Handler):
    def __init__(self):
        super().__init__(); _ensure_dirs()
        self._stream = open(APP_LOG_PATH, "a", encoding="utf-8")
    def emit(self, record: LogRecord):
        try:
            msg = self.format(record)
            self._stream.write(msg + "\n"); self._stream.flush()
            _rotate_if_needed()
        except Exception as e:
            try: self.handleError(record)
            except Exception: print(f"[WARN] logging error: {e}", file=sys.stderr)
    def close(self):
        try: self._stream.close()
        except Exception: pass
        super().close()

_formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
                               datefmt="%Y-%m-%d %H:%M:%S")

def get_logger(name: str = "app") -> Logger:
    level_name = os.getenv("APP_LOG_LEVEL","INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logger = logging.getLogger(name)
    if getattr(logger, "_supersonic_configured", False): return logger
    logger.setLevel(level)
    handler = _RotatingFileHandler(); handler.setFormatter(_formatter)
    logger.addHandler(handler)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console = logging.StreamHandler(sys.stdout); console.setLevel(level); console.setFormatter(_formatter)
        logger.addHandler(console)
    logger.propagate=False; logger._supersonic_configured=True
    logger.debug("Rotating logger initialized")
    return logger

class RequestLogMiddleware:
    """ASGI middleware (FastAPI/Starlette) to log method/path/status/time/client."""
    def __init__(self, app, logger: Logger | None = None):
        self.app = app; self.log = logger or get_logger("http")
    async def __call__(self, scope, receive, send):
        if scope["type"]!="http": return await self.app(scope, receive, send)
        method=scope.get("method"); path=scope.get("path"); client=scope.get("client")
        host=f"{client[0]}:{client[1]}" if client else "-"
        from time import perf_counter
        t0=perf_counter(); status_holder={"status":0}
        async def send_wrapper(event):
            if event["type"]=="http.response.start": status_holder["status"]=event["status"]
            await send(event)
        try: await self.app(scope, receive, send_wrapper)
        finally:
            ms=int((perf_counter()-t0)*1000); self.log.info("%s %s %s %dms", method, path, host, ms)

def wsgi_request_logger(app, logger: Logger | None = None):
    """WSGI wrapper (Flask) to log method/path/remote/time."""
    log = logger or get_logger("http")
    def middleware(environ, start_response):
        from time import perf_counter
        t0=perf_counter()
        def _start_response(status, headers, exc_info=None):
            ms=int((perf_counter()-t0)*1000)
            log.info("%s %s %s %dms",
                     environ.get("REQUEST_METHOD","-"),
                     environ.get("PATH_INFO","-"),
                     environ.get("REMOTE_ADDR","-"),
                     ms)
            return start_response(status, headers, exc_info)
        return app(environ, _start_response)
    return middleware
'''

CONTROL_PANEL_SNIPPET = r'''<!-- snippets/control_panel_sync.html -->
<section id="sync-panel" style="border:1px solid #223; border-radius:10px; padding:14px; background:#0b0f14; color:#e6eef8; font-family: ui-sans-serif, -apple-system, Segoe UI, Roboto, Helvetica, Arial;">
  <header style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
    <h3 style="margin:0;">🔄 Repo Sync</h3>
    <span id="sync-status-chip" style="font-size:12px; padding:2px 8px; border-radius:999px; background:#1b2635; border:1px solid #203044;">checking…</span>
    <span id="sync-last" style="font-size:12px; opacity:.8;"></span>
  </header>
  <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
    <button id="syncNowBtn" style="cursor:pointer; padding:10px 16px; border-radius:8px; border:1px solid #3a556f; background:#163148; color:#e6eef8; font-weight:600;">Run Sync Now</button>
    <span id="sync-cooldown" style="font-size:13px; opacity:.9;">…</span>
  </div>
  <details id="sync-log-wrap" style="margin-top:12px;">
    <summary style="cursor:pointer;">Show last run log</summary>
    <pre id="sync-log" style="background:#0f1720; border:1px solid #223; border-radius:8px; padding:10px; max-height:260px; overflow:auto; white-space:pre-wrap;"></pre>
  </details>
</section>
<script>
(function(){
  const btn = document.getElementById('syncNowBtn');
  const chip = document.getElementById('sync-status-chip');
  const cd = document.getElementById('sync-cooldown');
  const last = document.getElementById('sync-last');
  const logWrap = document.getElementById('sync-log-wrap');
  const logEl = document.getElementById('sync-log');

  const successAudio = new Audio('/assets/audio/notify_success.wav');
  const errorAudio = new Audio('/assets/audio/notify_error.wav');

  const fmt = (s)=> new Date(s).toLocaleString();
  const setChip = (txt, color) => { chip.textContent = txt; chip.style.background = color.bg; chip.style.borderColor = color.bd; };
  const COLORS = { running:{bg:'#2a3f25',bd:'#355a2e'}, ready:{bg:'#1b2635',bd:'#203044'}, wait:{bg:'#3a2e1b',bd:'#5a4a2e'}, error:{bg:'#3a1b1b',bd:'#5a2e2e'} };

  async function fetchStatus() {
    try {
      const r = await fetch('/api/ping', {cache:'no-store'});
      const s = await r.json();
      const running = false; // ping doesn't expose running; minimal UI
      const next = 0;
      if (running) { setChip('running…', COLORS.running); btn.disabled = true; cd.textContent = 'Sync running…'; }
      else if (next > 0) { setChip('cooldown', COLORS.wait); btn.disabled = true; cd.textContent = `Ready in ${next}s`; }
      else { setChip('ready', COLORS.ready); btn.disabled = false; cd.textContent = 'Ready'; }
      last.textContent = s.sync.last_finished ? `last run: ${fmt(s.sync.last_finished)}` : '';
    } catch (e) {
      setChip('status error', COLORS.error); cd.textContent = 'Unable to reach /api/ping'; btn.disabled = false;
    }
  }

  async function runSync() {
    btn.disabled = true; setChip('starting…', COLORS.running); cd.textContent = 'Sync running…';
    try {
      const r = await fetch('/api/sync', { method: 'POST' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const j = await r.json();
      logEl.textContent = (j.message || 'queued');
      if (!logWrap.open) logWrap.open = true;
      setTimeout(fetchStatus, 3500);
    } catch (e) {
      errorAudio.play().catch(()=>{});
      logEl.textContent = 'Request error: ' + e;
      setChip('error', COLORS.error);
    } finally {
      btn.disabled = false;
    }
  }

  btn.addEventListener('click', runSync);
  fetchStatus(); setInterval(fetchStatus, 5000);
})();
</script>
'''

def main():
    print("=== Supersonic Logging & Sync Pack ===")
    # Write files
    changed = False
    changed |= write(ROOT/"Supersonic_Health_Extension.py", SUPERSONIC_HEALTH_EXTENSION)
    changed |= write(ROOT/"rotating_logger.py", ROTATING_LOGGER)
    changed |= write(SNIPS/"control_panel_sync.html", CONTROL_PANEL_SNIPPET)

    # Ensure dirs exist
    LOGS.mkdir(exist_ok=True); ARCH.mkdir(exist_ok=True)

    # Makefile targets
    append_make_targets()

    # Friendly recap
    print("\n=== Done. Next steps:")
    print("1) Wire endpoints:")
    print("   - FastAPI:")
    print("       from fastapi import FastAPI")
    print("       from rotating_logger import get_logger, RequestLogMiddleware")
    print("       from Supersonic_Health_Extension import attach")
    print("       log = get_logger('supersonic')")
    print("       app = FastAPI()")
    print("       app.add_middleware(RequestLogMiddleware, logger=log)")
    print("       attach(app)")
    print("       log.info('FastAPI started')")
    print("   - Flask:")
    print("       from flask import Flask")
    print("       from rotating_logger import get_logger, wsgi_request_logger")
    print("       from Supersonic_Health_Extension import attach")
    print("       log = get_logger('supersonic')")
    print("       app = Flask(__name__)")
    print("       app.wsgi_app = wsgi_request_logger(app.wsgi_app, logger=log)")
    print("       attach(app)")
    print("       log.info('Flask started)')")
    print("2) Optional: drop `snippets/control_panel_sync.html` into your control panel page.")
    print("3) Secrets recommended in Replit:")
    print("   - GH_TOKEN (repo+workflow scopes), GITHUB_REPOSITORY=owner/repo")
    print("   - GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL")
    print("   - BOOT_MAX_SIZE_BYTES / BOOT_KEEP_FILES / BOOT_MAX_TOTAL_MB   (boot banner rotation)")
    print("   - APP_LOG_* variables to tune app log rotation (see rotating_logger.py)")
    print("4) Test:")
    print("   - make ping        # JSON health")
    print("   - make ready       # 200 means OK")
    print("   - open your panel and click 'Run Sync Now'")
    print("\nAll set. 🔥")

if __name__ == "__main__":
    main()