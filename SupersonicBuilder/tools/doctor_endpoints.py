"""
Doctor Endpoints (FastAPI / Flask auto-mount)
Routes:
  GET  /health         → live app/system health
  GET  /sync/status    → workspace + git status
  POST /sync/restart   → gentle refresh hook (make sync → fallback git pull)
  GET  /doctor         → tiny HTML panel linking the above

Security:
  - If DOCTOR_KEY is set (recommended), clients must send header:
      X-Doctor-Key: <value-of-DOCTOR_KEY>
"""

from __future__ import annotations
import os, json, subprocess, time, shutil, socket, hashlib, platform
from datetime import datetime, timezone
from typing import Dict, Any, Optional

BOOT_TS = time.time()
DOCTOR_KEY = os.getenv("DOCTOR_KEY", "").strip()

def _sec_ok(headers: Optional[Dict[str, str]] = None) -> bool:
    if not DOCTOR_KEY:
        return True
    try:
        key = (headers.get("X-Doctor-Key") or headers.get("x-doctor-key") or "").strip()
        return key == DOCTOR_KEY
    except Exception:
        return False

def _run(cmd: str) -> Dict[str, Any]:
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True, timeout=45)
        return {"ok": True, "cmd": cmd, "out": out.strip()}
    except subprocess.CalledProcessError as e:
        return {"ok": False, "cmd": cmd, "out": e.output.strip(), "code": e.returncode}
    except Exception as e:
        return {"ok": False, "cmd": cmd, "out": repr(e)}

def _git_root() -> str:
    r = _run("git rev-parse --show-toplevel")
    return r["out"] if r.get("ok") else os.getcwd()

def _disk() -> Dict[str, Any]:
    try:
        total, used, free = shutil.disk_usage("/")
        return {"total": total, "used": used, "free": free}
    except Exception as e:
        return {"error": repr(e)}

def _git_status() -> Dict[str, Any]:
    info = {}
    info["root"] = _git_root()
    info["branch"] = _run("git rev-parse --abbrev-ref HEAD")
    info["last_commit"] = _run("git log -1 --pretty='%h %s (%cr) <%an>'")
    info["dirty"] = _run("git status --porcelain")
    info["remotes"] = _run("git remote -v")
    return info

def _env_digest() -> str:
    src = "|".join([
        platform.platform(),
        platform.python_version(),
        socket.gethostname(),
        str(sorted([k for k in os.environ.keys() if k and k.isupper()][:50])),
    ])
    return hashlib.sha256(src.encode()).hexdigest()[:12]

def health_payload() -> Dict[str, Any]:
    py_ok = True
    try:
        import importlib, sys
        for m in ("json","subprocess","time"):
            importlib.import_module(m)
    except Exception:
        py_ok = False

    return {
        "status": "ok",
        "ts": datetime.now(timezone.utc).isoformat(),
        "uptime_sec": round(time.time() - BOOT_TS, 1),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "host": socket.gethostname(),
        "env_fingerprint": _env_digest(),
        "disk": _disk(),
        "checks": {
            "python_stdlib": py_ok,
            "git_present": _run("git --version").get("ok", False),
            "make_present": _run("make --version").get("ok", False),
        },
    }

def sync_status_payload() -> Dict[str, Any]:
    p = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "git": _git_status(),
    }
    if os.path.exists("Makefile"):
        p["make_targets"] = _run("grep -E '^(health|sync|doctor)[-:]' -n Makefile || true")
    return p

def sync_restart() -> Dict[str, Any]:
    tried = []
    for cmd in [
        "make sync",
        "make health-apply",
        "python3 supersonic_full_health_scan.py --apply",
        "git fetch --all -p && git pull --rebase --autostash || true",
    ]:
        tried.append(cmd)
        r = _run(cmd)
        if r.get("ok"):
            return {"ok": True, "used": cmd, "out": r.get("out", "")[:4000]}
    return {"ok": False, "tried": tried}

def mount_on_fastapi(app, base_path: str = ""):
    from fastapi import APIRouter, Request
    from fastapi.responses import JSONResponse, HTMLResponse

    router = APIRouter()

    @router.get("/health")
    async def health(request: Request):
        if not _sec_ok(request.headers):
            return JSONResponse({"error": "forbidden"}, status_code=403)
        return JSONResponse(health_payload())

    @router.get("/sync/status")
    async def sync_status(request: Request):
        if not _sec_ok(request.headers):
            return JSONResponse({"error": "forbidden"}, status_code=403)
        return JSONResponse(sync_status_payload())

    @router.post("/sync/restart")
    async def sync_restart_ep(request: Request):
        if not _sec_ok(request.headers):
            return JSONResponse({"error": "forbidden"}, status_code=403)
        return JSONResponse(sync_restart())

    @router.get("/doctor")
    async def doctor_ui(request: Request):
        if not _sec_ok(request.headers):
            return HTMLResponse("<h3>Forbidden</h3>", status_code=403)
        html = """
        <html><head><title>Doctor</title>
        <style>body{font-family:system-ui;margin:32px} code{background:#111;color:#0f0;padding:2px 6px;border-radius:4px}</style>
        </head><body>
          <h2>Supersonic Doctor</h2>
          <p><a href="/health">/health</a> • <a href="/sync/status">/sync/status</a> •
             <form method="post" action="/sync/restart" style="display:inline">
               <button type="submit">POST /sync/restart</button>
             </form>
          </p>
          <p>Send header <code>X-Doctor-Key: $DOCTOR_KEY</code> if configured.</p>
          <pre id="out"></pre>
          <script>
            async function load() {
              const h = await fetch('/health', {headers: {'X-Doctor-Key': '%KEY%'}}).then(r=>r.json()).catch(()=>({error:'fetch failed'}));
              document.getElementById('out').textContent = JSON.stringify(h,null,2);
            }
            load();
          </script>
        </body></html>
        """.replace("%KEY%", DOCTOR_KEY)
        return HTMLResponse(html)

    app.include_router(router, prefix=base_path)

def mount_on_flask(app, url_prefix: str = ""):
    from flask import Blueprint, request, jsonify, Response

    bp = Blueprint("doctor", __name__, url_prefix=url_prefix or "")

    @bp.route("/health", methods=["GET"])
    def health():
        if not _sec_ok(request.headers):
            return jsonify({"error": "forbidden"}), 403
        return jsonify(health_payload())

    @bp.route("/sync/status", methods=["GET"])
    def sync_status():
        if not _sec_ok(request.headers):
            return jsonify({"error": "forbidden"}), 403
        return jsonify(sync_status_payload())

    @bp.route("/sync/restart", methods=["POST"])
    def sync_restart_ep():
        if not _sec_ok(request.headers):
            return jsonify({"error": "forbidden"}), 403
        return jsonify(sync_restart())

    @bp.route("/doctor", methods=["GET"])
    def doctor_ui():
        if not _sec_ok(request.headers):
            return Response("<h3>Forbidden</h3>", status=403, mimetype="text/html")
        html = """
        <html><head><title>Doctor</title>
        <style>body{font-family:system-ui;margin:32px} code{background:#111;color:#0f0;padding:2px 6px;border-radius:4px}</style>
        </head><body>
          <h2>Supersonic Doctor</h2>
          <p><a href="/health">/health</a> • <a href="/sync/status">/sync/status</a> •
             <form method="post" action="/sync/restart" style="display:inline">
               <button type="submit">POST /sync/restart</button>
             </form>
          </p>
          <p>Send header <code>X-Doctor-Key: $DOCTOR_KEY</code> if configured.</p>
        </body></html>
        """
        return Response(html, mimetype="text/html")

    app.register_blueprint(bp)

def _standalone():
    """Run a barebones HTTP server on :8080 exposing the same routes (FastAPI if available, else Flask)."""
    try:
        from fastapi import FastAPI
        import uvicorn
        app = FastAPI(title="Doctor")
        mount_on_fastapi(app)
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
    except Exception:
        from flask import Flask
        app = Flask(__name__)
        mount_on_flask(app)
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))

if __name__ == "__main__":
    _standalone()
