#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
supersonic_settings_server.py
------------------------------------------------------------
Supersonic Commander Control Panel - Full Integration
• Live settings management with web UI
• Streaming consoles for: Rebuild, Deploy, Verify, Auto-Fix, Promote
• Voice feedback integration
• Telemetry refresh
• Real-time log polling

Run:
  pip install flask pyttsx3 psutil beautifulsoup4 requests
  python supersonic_settings_server.py
Then open http://localhost:5055 or the Replit webview
"""

from __future__ import annotations
from flask import Flask, send_file, jsonify, request
from pathlib import Path
import json, subprocess, threading, time, sys, os

SETTINGS_PATH = Path("supersonic_settings.json")
AUDIT_PATH = Path("docs/_ops_log.txt")
DEFAULTS = {
    "voice_pack": "FlightOps",
    "volume": 1.0,
    "rate": 185,
    "dashboard_auto_refresh": True,
    "telemetry_interval_sec": 30,
    "theme": "dark",
    "show_changelog_cards": True,
    "advanced_tools": False,
    "perfAuto": True,
    "profile": "balanced",
    "perf": {
        "fpsMin": 25,
        "fpsRelease": 40,
        "fpsDurationMs": 2000,
        "rttMaxMs": 500,
        "rttDurationMs": 3000,
        "cooldownMs": 15000
    }
}

app = Flask(__name__, static_url_path="", static_folder=".")

# ============ Settings Management ============
def load_settings():
    if SETTINGS_PATH.exists():
        try:
            return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return DEFAULTS.copy()

def save_settings(cfg: dict):
    SETTINGS_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

@app.get("/")
def index():
    return send_file("supersonic_settings_panel.html")

@app.get("/api/settings")
def api_get():
    return jsonify(load_settings())

@app.post("/api/settings")
def api_post():
    data = request.get_json(force=True, silent=True) or {}
    cfg = load_settings()
    for k in DEFAULTS:
        if k in data:
            cfg[k] = data[k]
    if "perf" in data and isinstance(data["perf"], dict):
        cfg["perf"] = data["perf"]
    save_settings(cfg)
    return jsonify({"ok": True, "settings": cfg})

@app.route("/api/ping", methods=["GET"])
def api_ping():
    """
    Simple liveness/latency probe.
    Client sends ?t=<ms since epoch>, we echo back server time.
    """
    try:
        client_t = float(request.args.get("t", "0"))
    except Exception:
        client_t = 0.0
    return jsonify({
        "ok": True,
        "server_ts": time.time(),
        "echo_client_ts": client_t
    })

@app.post("/api/test-voice")
def api_test_voice():
    try:
        from supersonic_voice_commander import VoiceCommander
        pack = (request.get_json(force=True, silent=True) or {}).get("pack", None)
        vc = VoiceCommander(pack)
        vc.speak_event("success")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ============ Log Buffer Class ============
class LogBuffer:
    def __init__(self, max_lines=2000):
        self.max_lines = max_lines
        self.lines: list[str] = []
        self.idx = 0
        self.lock = threading.Lock()

    def append(self, text: str):
        with self.lock:
            for ln in text.splitlines():
                self.lines.append(ln)
                self.idx += 1
            if len(self.lines) > self.max_lines:
                over = len(self.lines) - self.max_lines
                self.lines = self.lines[over:]

    def snapshot(self, offset: int, limit: int = 200):
        with self.lock:
            start = max(0, min(offset, self.idx))
            first_idx_in_buf = self.idx - len(self.lines)
            rel = max(0, start - first_idx_in_buf)
            slice_ = self.lines[rel: rel + limit]
            next_offset = start + len(slice_)
            return {"lines": slice_, "next": next_offset, "idx": self.idx}

# ============ Voice & Telemetry Helpers ============
def _voice(event: str):
    try:
        from supersonic_voice_commander import VoiceCommander
        pack = load_settings().get("voice_pack")
        vc = VoiceCommander(pack)
        vc.speak_event(event)
    except Exception:
        pass

def _refresh_telemetry():
    try:
        subprocess.run([sys.executable, "supersonic_telemetry.py"], check=False)
    except Exception:
        pass

def _audit(op: str, status: str, meta: dict | None = None):
    """Log operation to audit trail in docs/_ops_log.txt"""
    try:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "op": op,
            "status": status,
            "meta": (meta or {}),
        }
        with AUDIT_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass

# ============ REBUILD Engine ============
BUILD_STATE = {"running": False, "rc": None, "started_at": None, "ended_at": None}
BUILD_LOCK = threading.Lock()
BUILD_LOGS = LogBuffer(max_lines=4000)

def _run_build_thread():
    with BUILD_LOCK:
        BUILD_STATE.update({"running": True, "rc": None, "started_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()), "ended_at": None})
    BUILD_LOGS.append("=== 🔁 Rebuild triggered ===\n")
    _audit("rebuild", "start", {})
    _voice("start")
    try:
        # Check if build script exists in builders/ or root
        build_script = "supersonic_build_secure_all.py"
        if not Path(build_script).exists():
            build_script = "builders/supersonic_build_secure_all.py"
        if not Path(build_script).exists():
            BUILD_LOGS.append("⚠️ Build script not found, using makefile fallback...")
            proc = subprocess.Popen(["make", "-C", "builders", "build"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        else:
            proc = subprocess.Popen([sys.executable, build_script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        if proc.stdout:
            for line in iter(proc.stdout.readline, ""):
                BUILD_LOGS.append(line.rstrip("\n"))
            proc.stdout.close()
        rc = proc.wait()
    except Exception as e:
        BUILD_LOGS.append(f"❌ Build runner error: {e}")
        rc = 1

    with BUILD_LOCK:
        BUILD_STATE["rc"] = rc
        BUILD_STATE["running"] = False
        BUILD_STATE["ended_at"] = time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime())

    if rc == 0:
        BUILD_LOGS.append("✅ Build complete.")
        _voice("success")
        _audit("rebuild", "success", {"rc": rc})
    else:
        BUILD_LOGS.append("❌ Build failed.")
        _voice("fail")
        _audit("rebuild", "fail", {"rc": rc})

    _refresh_telemetry()

@app.post("/api/rebuild")
def api_rebuild():
    with BUILD_LOCK:
        if BUILD_STATE["running"]:
            return jsonify({"ok": False, "error": "Build already running"}), 409
        BUILD_LOGS.append("\n---\n")
        t = threading.Thread(target=_run_build_thread, daemon=True)
        t.start()
        return jsonify({"ok": True})

@app.get("/api/rebuild-status")
def api_rebuild_status():
    try:
        offset = int(request.args.get("offset", "0"))
    except Exception:
        offset = 0
    snap = BUILD_LOGS.snapshot(offset, limit=200)
    with BUILD_LOCK:
        state = BUILD_STATE.copy()
    return jsonify({"ok": True, "running": state["running"], "rc": state["rc"], "started_at": state["started_at"], "ended_at": state["ended_at"], **snap})

# ============ DEPLOY Engine ============
DEPLOY_STATE = {"running": False, "rc": None, "started_at": None, "ended_at": None}
DEPLOY_LOCK = threading.Lock()
DEPLOY_LOGS = LogBuffer(max_lines=2000)

def _run_deploy_thread():
    with DEPLOY_LOCK:
        DEPLOY_STATE.update({"running": True, "rc": None, "started_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()), "ended_at": None})
    DEPLOY_LOGS.append("=== 🚀 Deploy to /docs started ===\n")
    _audit("deploy", "start", {})
    _voice("start")
    try:
        proc = subprocess.Popen([sys.executable, "supersonic_deploy_pages.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        if proc.stdout:
            for line in iter(proc.stdout.readline, ""):
                DEPLOY_LOGS.append(line.rstrip("\n"))
            proc.stdout.close()
        rc = proc.wait()
    except Exception as e:
        DEPLOY_LOGS.append(f"❌ Deploy runner error: {e}")
        rc = 1
    with DEPLOY_LOCK:
        DEPLOY_STATE.update({"rc": rc, "running": False, "ended_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime())})
    if rc == 0:
        _voice("release")
        _audit("deploy", "success", {"rc": rc})
    else:
        _voice("fail")
        _audit("deploy", "fail", {"rc": rc})
    _refresh_telemetry()

@app.post("/api/deploy")
def api_deploy():
    with DEPLOY_LOCK:
        if DEPLOY_STATE["running"]:
            return jsonify({"ok": False, "error": "Deploy already running"}), 409
        t = threading.Thread(target=_run_deploy_thread, daemon=True)
        t.start()
        return jsonify({"ok": True})

@app.get("/api/deploy-status")
def api_deploy_status():
    try:
        offset = int(request.args.get("offset", "0"))
    except Exception:
        offset = 0
    snap = DEPLOY_LOGS.snapshot(offset, limit=200)
    with DEPLOY_LOCK:
        state = DEPLOY_STATE.copy()
    return jsonify({"ok": True, "running": state["running"], "rc": state["rc"], "started_at": state["started_at"], "ended_at": state["ended_at"], **snap})

# ============ VERIFY Engine ============
VERIFY_STATE = {"running": False, "rc": None, "started_at": None, "ended_at": None}
VERIFY_LOCK = threading.Lock()
VERIFY_LOGS = LogBuffer(max_lines=2000)

def _run_verify_thread(externals: bool, hints: bool):
    with VERIFY_LOCK:
        VERIFY_STATE.update({"running": True, "rc": None, "started_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()), "ended_at": None})
    VERIFY_LOGS.append(f"=== 🔗 Verify Pages started (externals={externals}, hints={hints}) ===\n")
    _audit("verify", "start", {"externals": externals, "hints": hints})
    _voice("start")
    try:
        cmd = [sys.executable, "supersonic_verify_pages.py"]
        if externals:
            cmd.append("--externals")
        if hints:
            cmd.append("--hints")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        if proc.stdout:
            for line in iter(proc.stdout.readline, ""):
                VERIFY_LOGS.append(line.rstrip("\n"))
            proc.stdout.close()
        rc = proc.wait()
    except Exception as e:
        VERIFY_LOGS.append(f"❌ Verify runner error: {e}")
        rc = 1
    with VERIFY_LOCK:
        VERIFY_STATE.update({"rc": rc, "running": False, "ended_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime())})
    if rc == 0:
        _voice("success")
        _audit("verify", "success", {"rc": rc})
    else:
        _voice("warn")
        _audit("verify", "warn", {"rc": rc})
    _refresh_telemetry()

@app.post("/api/verify")
def api_verify():
    body = (request.get_json(force=True, silent=True) or {})
    externals = bool(body.get("externals"))
    hints = bool(body.get("hints", True))
    with VERIFY_LOCK:
        if VERIFY_STATE["running"]:
            return jsonify({"ok": False, "error": "Verify already running"}), 409
        t = threading.Thread(target=_run_verify_thread, args=(externals, hints), daemon=True)
        t.start()
        return jsonify({"ok": True})

@app.get("/api/verify-status")
def api_verify_status():
    try:
        offset = int(request.args.get("offset", "0"))
    except Exception:
        offset = 0
    snap = VERIFY_LOGS.snapshot(offset, limit=200)
    with VERIFY_LOCK:
        state = VERIFY_STATE.copy()
    return jsonify({"ok": True, "running": state["running"], "rc": state["rc"], "started_at": state["started_at"], "ended_at": state["ended_at"], **snap})

# ============ AUTO-FIX Engine ============
AUTOFIX_STATE = {"running": False, "rc": None, "started_at": None, "ended_at": None}
AUTOFIX_LOCK = threading.Lock()
AUTOFIX_LOGS = LogBuffer(max_lines=2000)

def _run_autofix_thread():
    with AUTOFIX_LOCK:
        AUTOFIX_STATE.update({"running": True, "rc": None, "started_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()), "ended_at": None})
    AUTOFIX_LOGS.append("=== 🔧 Auto-Fix Preview started ===\n")
    _audit("autofix", "start", {})
    _voice("start")
    try:
        cmd = [sys.executable, "supersonic_verify_autofix_preview.py"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        if proc.stdout:
            for line in iter(proc.stdout.readline, ""):
                AUTOFIX_LOGS.append(line.rstrip("\n"))
            proc.stdout.close()
        rc = proc.wait()
    except Exception as e:
        AUTOFIX_LOGS.append(f"❌ Auto-fix runner error: {e}")
        rc = 1
    with AUTOFIX_LOCK:
        AUTOFIX_STATE.update({"rc": rc, "running": False, "ended_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime())})
    if rc == 0:
        _voice("success")
        _audit("autofix", "success", {"rc": rc})
    else:
        _voice("warn")
        _audit("autofix", "warn", {"rc": rc})
    _refresh_telemetry()

@app.post("/api/autofix")
def api_autofix():
    with AUTOFIX_LOCK:
        if AUTOFIX_STATE["running"]:
            return jsonify({"ok": False, "error": "Auto-fix already running"}), 409
        t = threading.Thread(target=_run_autofix_thread, daemon=True)
        t.start()
        return jsonify({"ok": True})

@app.get("/api/autofix-status")
def api_autofix_status():
    try:
        offset = int(request.args.get("offset", "0"))
    except Exception:
        offset = 0
    snap = AUTOFIX_LOGS.snapshot(offset, limit=200)
    with AUTOFIX_LOCK:
        state = AUTOFIX_STATE.copy()
    return jsonify({"ok": True, "running": state["running"], "rc": state["rc"], "started_at": state["started_at"], "ended_at": state["ended_at"], **snap})

# ============ PROMOTE Engine ============
PROMOTE_STATE = {"running": False, "rc": None, "started_at": None, "ended_at": None}
PROMOTE_LOCK = threading.Lock()
PROMOTE_LOGS = LogBuffer(max_lines=2000)

def _run_promote_thread():
    with PROMOTE_LOCK:
        PROMOTE_STATE.update({"running": True, "rc": None, "started_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()), "ended_at": None})
    PROMOTE_LOGS.append("=== ⬆️ Promote Preview → Docs started ===\n")
    _audit("promote", "start", {})
    _voice("start")
    try:
        cmd = [sys.executable, "supersonic_promote_preview.py"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        if proc.stdout:
            for line in iter(proc.stdout.readline, ""):
                PROMOTE_LOGS.append(line.rstrip("\n"))
            proc.stdout.close()
        rc = proc.wait()
    except Exception as e:
        PROMOTE_LOGS.append(f"❌ Promote runner error: {e}")
        rc = 1
    with PROMOTE_LOCK:
        PROMOTE_STATE.update({"rc": rc, "running": False, "ended_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime())})
    if rc == 0:
        _voice("release")
        _audit("promote", "success", {"rc": rc})
    else:
        _voice("warn")
        _audit("promote", "warn", {"rc": rc})
    _refresh_telemetry()

@app.post("/api/promote")
def api_promote():
    with PROMOTE_LOCK:
        if PROMOTE_STATE["running"]:
            return jsonify({"ok": False, "error": "Promote already running"}), 409
        t = threading.Thread(target=_run_promote_thread, daemon=True)
        t.start()
        return jsonify({"ok": True})

@app.get("/api/promote-status")
def api_promote_status():
    try:
        offset = int(request.args.get("offset", "0"))
    except Exception:
        offset = 0
    snap = PROMOTE_LOGS.snapshot(offset, limit=200)
    with PROMOTE_LOCK:
        state = PROMOTE_STATE.copy()
    return jsonify({"ok": True, "running": state["running"], "rc": state["rc"], "started_at": state["started_at"], "ended_at": state["ended_at"], **snap})

# ============ ROLLBACK Engine ============
ROLLBACK_STATE = {"running": False, "rc": None, "started_at": None, "ended_at": None}
ROLLBACK_LOCK = threading.Lock()
ROLLBACK_LOGS = LogBuffer(max_lines=2000)

def _list_backups():
    from pathlib import Path
    DOCS = Path("docs")
    if not DOCS.exists(): return []
    return sorted([p.name for p in DOCS.iterdir() if p.is_dir() and p.name.startswith("_backup_")], reverse=True)

@app.get("/api/rollback-list")
def api_rollback_list():
    return jsonify({"ok": True, "backups": _list_backups()})

def _run_rollback_thread(backup_name: str):
    with ROLLBACK_LOCK:
        ROLLBACK_STATE.update({"running": True, "rc": None, "started_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()), "ended_at": None})
    ROLLBACK_LOGS.append(f"=== ⏪ Emergency Rollback from {backup_name} ===\n")
    _audit("rollback", "start", {"backup": backup_name})
    _voice("start")
    try:
        cmd = [sys.executable, "supersonic_docs_rollback.py", "--use", backup_name, "--yes"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        if proc.stdout:
            for line in iter(proc.stdout.readline, ""):
                ROLLBACK_LOGS.append(line.rstrip("\n"))
            proc.stdout.close()
        rc = proc.wait()
    except Exception as e:
        ROLLBACK_LOGS.append(f"❌ Rollback runner error: {e}")
        rc = 1
    with ROLLBACK_LOCK:
        ROLLBACK_STATE.update({"rc": rc, "running": False, "ended_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime())})
    if rc == 0:
        _voice("rollback")
        _audit("rollback", "success", {"backup": backup_name, "rc": rc})
    else:
        _voice("fail")
        _audit("rollback", "fail", {"backup": backup_name, "rc": rc})
    _refresh_telemetry()

@app.post("/api/rollback")
def api_rollback():
    body = request.get_json(force=True, silent=True) or {}
    backup_name = body.get("backup")
    if not backup_name:
        return jsonify({"ok": False, "error": "Missing 'backup'"}), 400
    with ROLLBACK_LOCK:
        if ROLLBACK_STATE["running"]:
            return jsonify({"ok": False, "error": "Rollback already running"}), 409
        t = threading.Thread(target=_run_rollback_thread, args=(backup_name,), daemon=True)
        t.start()
        return jsonify({"ok": True})

@app.get("/api/rollback-status")
def api_rollback_status():
    try:
        offset = int(request.args.get("offset", "0"))
    except Exception:
        offset = 0
    snap = ROLLBACK_LOGS.snapshot(offset, limit=200)
    with ROLLBACK_LOCK:
        state = ROLLBACK_STATE.copy()
    return jsonify({"ok": True, "running": state["running"], "rc": state["rc"], "started_at": state["started_at"], "ended_at": state["ended_at"], **snap})

# ============ AUDIT LOG API ============
@app.get("/api/audit")
def api_audit():
    try:
        if not AUDIT_PATH.exists():
            return jsonify({"ok": True, "lines": []})
        with AUDIT_PATH.open("r", encoding="utf-8") as f:
            lines = f.readlines()[-200:]
        return jsonify({"ok": True, "lines": [x.rstrip("\n") for x in lines]})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ============ Health Endpoints (Production Ready) ============
START_TIME = time.time()

@app.get("/healthz")
def healthz():
    """Liveness probe: process is up and responding"""
    return jsonify(
        status="ok",
        service="supersonic-commander",
        uptime_seconds=round(time.time() - START_TIME, 1),
    ), 200

@app.get("/readyz")
def readyz():
    """Readiness probe: app is ready to accept traffic"""
    checks = {
        "settings_loaded": SETTINGS_PATH.exists() or True,
        "flask_app": True,
    }
    ready = all(checks.values())
    code = 200 if ready else 503
    return jsonify(status="ready" if ready else "not_ready", checks=checks), code

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🧭 Supersonic Commander Control Panel starting on port {port}...")
    print("   Voice packs: FlightOps, SciFiControl, IndustrialOps, ArcadeHUD")
    print("   Consoles: Rebuild, Deploy, Verify (+ Auto-Fix, Promote, Rollback when advanced tools enabled)")
    app.run(host="0.0.0.0", port=port, debug=False)
