# tools/doctor_endpoints_secure.py
from __future__ import annotations
import os, time, psutil, sys, json
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

def mount_health_endpoints(app, url_prefix: str = ""):
    """Mount /health and /metrics endpoints"""
    from flask import jsonify, request, abort
    
    prefix = ("/" + url_prefix.strip("/")) if url_prefix else ""
    
    @app.get(prefix + "/health")
    def health():
        if not _check_admin(request):
            abort(401)
        
        proc = psutil.Process()
        mem = proc.memory_info()
        disk = psutil.disk_usage('.')
        load = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
        cpu_count = os.cpu_count() or 1
        
        payload = {
            "ok": True,
            "status": "ok",
            "uptime_sec": round(time.time() - START_TS, 2),
            "python": sys.version,
            "cwd": os.getcwd(),
            "cpu_count": cpu_count,
            "loadavg": {
                "raw": list(load),
                "per_cpu": [round(l / cpu_count, 4) for l in load]
            },
            "memory": {
                "rss_mb": round(mem.rss / 1024 / 1024, 3),
                "vms_mb": round(mem.vms / 1024 / 1024, 3),
                "rss_bytes": mem.rss,
                "vms_bytes": mem.vms,
                "source": "psutil"
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free
            },
            "checks": {
                "git_present": os.path.isdir(".git"),
                "make_present": os.path.exists("Makefile")
            }
        }
        return jsonify(payload)
    
    @app.get(prefix + "/metrics")
    def metrics():
        if not _check_admin(request):
            abort(401)
        
        proc = psutil.Process()
        mem = proc.memory_info()
        disk = psutil.disk_usage('.')
        load = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
        cpu_count = os.cpu_count() or 1
        
        data = {
            "ok": True,
            "uptime_sec": round(time.time() - START_TS, 2),
            "loadavg": {
                "raw": list(load),
                "per_cpu": [round(l / cpu_count, 4) for l in load]
            },
            "memory": {
                "rss_mb": round(mem.rss / 1024 / 1024, 3),
                "vms_mb": round(mem.vms / 1024 / 1024, 3)
            },
            "disk": {
                "total_gb": round(disk.total / 1024**3, 2),
                "used_gb": round(disk.used / 1024**3, 2),
                "free_gb": round(disk.free / 1024**3, 2)
            },
            "errors_last_5m": 0,
            "http_5xx": {"count": 0, "window_sec": 600}
        }
        
        fmt = request.args.get("format", "json")
        if fmt == "prom":
            lines = [
                "# HELP app_uptime_seconds Application uptime in seconds",
                f"app_uptime_seconds {data['uptime_sec']}",
                "# HELP app_disk_bytes Disk usage in bytes",
                f"app_disk_bytes{{type=\"total\"}} {disk.total}",
                f"app_disk_bytes{{type=\"used\"}} {disk.used}",
                f"app_disk_bytes{{type=\"free\"}} {disk.free}",
            ]
            return "\n".join(lines) + "\n", 200, {"Content-Type": "text/plain; version=0.0.4"}
        
        return jsonify(data)

def mount_sync_endpoints(app, url_prefix: str = ""):
    """Mount /sync/* endpoints with ADMIN_TOKEN protection"""
    from flask import jsonify, request, abort
    import threading
    
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
    
    @app.post(prefix + "/snapshot")
    def create_snapshot():
        if not _check_admin(request):
            abort(401)
        
        import subprocess
        try:
            result = subprocess.run(
                ["python3", "scripts/snapshot_full.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return jsonify({"ok": True, "output": result.stdout})
            else:
                return jsonify({"ok": False, "error": result.stderr}), 500
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500
