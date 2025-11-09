#!/usr/bin/env python3
"""
Supersonic Flask Control Panel Installer (with logging & key checks)
Targets: Flask app in serve_pdfs.py
"""
import os, shutil, datetime
from pathlib import Path

ROOT = Path(os.getcwd())
SERVER_FILE = ROOT / "serve_pdfs.py"
TEMPLATES_DIR = ROOT / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)
BACKUP_FILE = SERVER_FILE.with_suffix(f".bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")

PANEL_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Supersonic Control Panel</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="doctor-key" content="{{ doctor_key|default('') }}">
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; background:#0f1115; color:#eaeaea; padding:24px; }
    .btn { appearance:none; border:0; border-radius:10px; padding:10px 14px; cursor:pointer; background:#1e90ff; color:white; font-weight:600; margin-right:10px; }
    .toast { position:fixed; right:16px; bottom:16px; background:#111; color:#fff; padding:12px 14px; border-radius:8px; box-shadow:0 6px 20px rgba(0,0,0,.35); display:none; z-index:9999; }
    .toast.show { display:block; }
    pre { background:#0b0d11; border:1px solid #232734; padding:12px; border-radius:8px; overflow:auto; margin-top:16px; }
  </style>
</head>
<body>
  <h1>Supersonic Control Panel</h1>
  <button id="btnStatus" class="btn" style="background:#5865f2;">📊 Status</button>
  <button id="btnRestart" class="btn">⟳ Restart</button>
  <button id="btnHealth" class="btn" style="background:#2ea043;">❤️ Health</button>
  <pre id="out"></pre>
  <div id="toast" class="toast"></div>
<script>
(function(){
  const k = document.querySelector('meta[name="doctor-key"]').content;
  const h = k ? {'X-Doctor-Key':k} : {};
  const out=document.getElementById('out');const toast=document.getElementById('toast');
  function show(t,m=4200){toast.textContent=t;toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),m);}
  async function call(p,m='GET'){
    try{
      const r=await fetch(p,{method:m,headers:Object.assign({'Content-Type':'application/json'},h)});
      let d;try{d=await r.json();}catch{d={error:'Non-JSON'}};
      out.textContent=JSON.stringify(d,null,2);
      show((r.ok?'✅ ':'⚠️ ')+p);
    }catch(e){out.textContent=String(e);show('❌ '+p);}
  }
  document.getElementById('btnStatus').onclick=()=>call('/sync/status');
  document.getElementById('btnRestart').onclick=()=>call('/sync/restart','POST');
  document.getElementById('btnHealth').onclick=()=>call('/health');
})();
</script>
</body></html>
"""

ROUTES = r"""
# --- Supersonic Control Panel & Health Endpoints (auto-injected) ---
from flask import render_template, jsonify, request
import os, sys, subprocess, logging, datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("supersonic")

def _client_ip():
    fwd = request.headers.get("X-Forwarded-For")
    return (fwd.split(",")[0].strip() if fwd else request.remote_addr) or "unknown"

def _require_key():
    want = os.getenv("DOCTOR_KEY", "")
    got = request.headers.get("X-Doctor-Key", "")
    if want:
        ok = (got == want)
        if not ok:
            log.warning("KEY MISMATCH ip=%s path=%s", _client_ip(), request.path)
        return ok
    return True

@app.route("/panel")
def supersonic_panel():
    ip = _client_ip()
    log.info("OPEN_PANEL ip=%s ua=%s", ip, request.headers.get("User-Agent",""))
    return render_template("panel.html", doctor_key=os.getenv("DOCTOR_KEY", ""))

@app.route("/health")
def supersonic_health():
    ip = _client_ip()
    data = {"ok": True, "pid": os.getpid(), "cwd": os.getcwd(), "python": sys.version}
    log.info("HEALTH ip=%s -> ok", ip)
    return jsonify(data)

@app.route("/sync/status")
def supersonic_status():
    ip = _client_ip()
    now = datetime.datetime.now().isoformat()
    files = len(list(Path('.').rglob('*.*')))
    log.info("STATUS ip=%s files=%s", ip, files)
    return jsonify({"ok": True, "cwd": os.getcwd(), "time": now, "files": files})

@app.route("/sync/restart", methods=["POST"])
def supersonic_restart():
    ip = _client_ip()
    if not _require_key():
        return jsonify({"ok": False, "error": "invalid key"}), 401
    log.info("RESTART_REQUEST ip=%s", ip)
    try:
        if "REPLIT" in os.environ:
            log.info("RESTART_MODE=replit kill 1")
            subprocess.Popen(["kill", "1"])
        else:
            log.info("RESTART_MODE=os.execv")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        log.info("RESTART_ISSUED ip=%s", ip)
        return jsonify({"ok": True, "issued": True})
    except Exception as e:
        log.exception("RESTART_FAILED ip=%s err=%s", ip, e)
        return jsonify({"ok": False, "error": str(e)}), 500
# --- end Supersonic ---
"""

def main():
    if not SERVER_FILE.exists():
        print(f"❌ Error: {SERVER_FILE.name} not found.")
        return
    shutil.copy2(SERVER_FILE, BACKUP_FILE)
    print(f"🧾 Backed up original to {BACKUP_FILE.name}")

    content = SERVER_FILE.read_text(encoding="utf-8")
    if "/panel" in content and "Supersonic Control Panel" in content:
        print("✅ Panel routes already present; skipping inject.")
    else:
        insert_where = None
        if "app = Flask" in content:
            i = content.find("app = Flask")
            insert_where = content.find("\n", i)
        patched = (content[:insert_where] + "\n" + ROUTES + "\n" + content[insert_where:]) if insert_where else (content + "\n" + ROUTES)
        SERVER_FILE.write_text(patched, encoding="utf-8")
        print(f"✅ Patched routes into {SERVER_FILE.name}")

    panel_path = TEMPLATES_DIR / "panel.html"
    if not panel_path.exists():
        panel_path.write_text(PANEL_HTML, encoding="utf-8")
        print(f"✅ Created {panel_path}")
    else:
        print("⚠️ templates/panel.html already exists; left unchanged.")

    print("\n🎉 Done! Open `/panel` in your webview.")
    print("• Action endpoints require header X-Doctor-Key when DOCTOR_KEY is set in Replit Secrets.")
    print("• View logs in the Replit console (look for OPEN_PANEL / HEALTH / STATUS / RESTART_* lines).")
    print(f"• To undo: replace {SERVER_FILE.name} with {BACKUP_FILE.name}")

if __name__ == "__main__":
    main()
