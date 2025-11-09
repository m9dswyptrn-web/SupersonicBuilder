# tools/doctor_endpoints_simple.py
from __future__ import annotations
import os, time, json, hashlib, threading
from dataclasses import dataclass
from typing import Any, Dict

START_TS = time.time()
RELOAD_FLAG = ".reload"
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")

def _check_admin(req):
    """Check if request has valid admin token (if ADMIN_TOKEN is set)"""
    if not ADMIN_TOKEN:
        return True
    return req.headers.get("X-Admin-Token") == ADMIN_TOKEN

@dataclass
class Health:
    ok: bool = True
    uptime_sec: float = 0.0
    files: int = 0
    sha: str = ""

def _snapshot_sha(root: str=".") -> str:
    h = hashlib.sha256()
    for base, dirs, files in os.walk(root):
        if any(skip in base for skip in [".git", "__pycache__", ".mypy_cache", ".pytest_cache"]):
            continue
        for f in files:
            p = os.path.join(base, f)
            try:
                st = os.stat(p)
                h.update(f"{p}:{st.st_mtime_ns}:{st.st_size}".encode())
            except Exception:
                pass
    return h.hexdigest()[:16]

def _count_files(root: str=".") -> int:
    n = 0
    for base, _, files in os.walk(root):
        if ".git" in base or "__pycache__" in base:
            continue
        n += len(files)
    return n

def mount_sync_endpoints(app, url_prefix: str = ""):
    """Mount only the /sync/* endpoints (not /health which already exists)"""
    from flask import jsonify, request, abort
    
    prefix = ("/" + url_prefix.strip("/")) if url_prefix else ""

    @app.get(prefix + "/sync/status")
    def sync_status():
        if not _check_admin(request):
            abort(401)
        
        report_md = "docs/HEALTH_REPORT.md"
        found = os.path.exists(report_md)
        ts = None
        try:
            ts = os.path.getmtime(report_md) if found else None
        except Exception:
            pass
        payload: Dict[str, Any] = {
            "report_found": found,
            "report_mtime": ts,
            "uptime_sec": round(time.time() - START_TS, 2),
        }
        return jsonify(payload)

    @app.post(prefix + "/sync/restart")
    def sync_restart():
        if not _check_admin(request):
            abort(401)
        
        try:
            with open(RELOAD_FLAG, "w") as f:
                f.write(str(time.time()))
        except Exception:
            pass

        def _quit():
            time.sleep(0.5)
            os._exit(0)

        threading.Thread(target=_quit, daemon=True).start()
        return jsonify({"ok": True, "action": "restart"}), 202
