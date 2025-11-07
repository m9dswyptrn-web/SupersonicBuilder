#!/usr/bin/env python3
"""
embed_doctor_panel.py
- Copies snippets/doctor_panel.html into templates/ (or creates it)
- Injects a "Doctor" button/link into an existing control panel HTML if found
- Adds a /panel/doctor route for FastAPI or Flask by patching main.py safely
Safe to run multiple times (idempotent).
"""
import re, sys, shutil
from pathlib import Path

ROOT = Path(".").resolve()
SNIPPET_SRC = ROOT / "snippets" / "doctor_panel.html"
TEMPLATES_DIR = ROOT / "templates"
PANEL_TARGET = TEMPLATES_DIR / "doctor_panel.html"
MAIN = ROOT / "main.py"

CONTROL_PANEL_CANDIDATES = [
    ROOT / "templates" / "control_panel.html",
    ROOT / "templates" / "dashboard.html",
    ROOT / "templates" / "index.html",
    ROOT / "control_panel.html",
    ROOT / "dashboard.html",
    ROOT / "index.html",
]

def ensure_templates_dir():
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

def install_panel():
    ensure_templates_dir()
    if SNIPPET_SRC.exists():
        shutil.copy2(SNIPPET_SRC, PANEL_TARGET)
        return "[OK] Installed doctor_panel.html from snippets/ to templates/"
    else:
        # If snippet missing, create minimal file
        PANEL_TARGET.write_text("<!doctype html><title>Doctor</title><h1>Doctor Panel</h1>", encoding="utf-8")
        return "[WARN] snippets/doctor_panel.html missing. Wrote minimal templates/doctor_panel.html instead."

def detect_framework():
    if not MAIN.exists():
        return "unknown"
    txt = MAIN.read_text(encoding="utf-8", errors="ignore")
    if "from fastapi" in txt or "import FastAPI" in txt:
        return "fastapi"
    if "from flask" in txt or "import Flask" in txt:
        return "flask"
    return "unknown"

def patch_main_fastapi():
    txt = MAIN.read_text(encoding="utf-8")
    if "/panel/doctor" in txt and "FileResponse" in txt:
        return "[OK] FastAPI route appears already present."
    inject = """
# --- Supersonic Doctor route (auto-injected) ---
try:
    from fastapi.responses import FileResponse
    from pathlib import Path as _Path
    DOC_PANEL = _Path("templates") / "doctor_panel.html"
    if DOC_PANEL.exists():
        @app.get("/panel/doctor")
        def panel_doctor():
            return FileResponse(str(DOC_PANEL))
except Exception as _e:
    print("[embed] WARN: could not wire FastAPI /panel/doctor:", _e)
# --- end doctor route ---
"""
    m = re.search(r"app\s*=\s*FastAPI\(.*?\)\s*", txt, flags=re.S)
    if m:
        idx = m.end()
        new = txt[:idx] + "\n" + inject + "\n" + txt[idx:]
    else:
        new = txt + "\n" + inject
    MAIN.write_text(new, encoding="utf-8")
    return "[OK] Patched main.py with FastAPI /panel/doctor route."

def patch_main_flask():
    txt = MAIN.read_text(encoding="utf-8")
    if "@app.route('/panel/doctor'" in txt and "send_from_directory" in txt:
        return "[OK] Flask route appears already present."
    inject = """
# --- Supersonic Doctor route (auto-injected) ---
try:
    from flask import send_from_directory
    import os as _os
    @app.route('/panel/doctor')
    def panel_doctor():
        return send_from_directory('templates', 'doctor_panel.html')
except Exception as _e:
    print("[embed] WARN: could not wire Flask /panel/doctor:", _e)
# --- end doctor route ---
"""
    m = re.search(r"app\s*=\s*Flask\(.*?\)\s*", txt, flags=re.S)
    if m:
        idx = m.end()
        new = txt[:idx] + "\n" + inject + "\n" + txt[idx:]
    else:
        new = txt + "\n" + inject
    MAIN.write_text(new, encoding="utf-8")
    return "[OK] Patched main.py with Flask /panel/doctor route."

def patch_main_unknown():
    if not MAIN.exists():
        MAIN.write_text(\"\"\"from fastapi import FastAPI
app = FastAPI()

from fastapi.responses import FileResponse
from pathlib import Path as _Path
DOC_PANEL = _Path("templates") / "doctor_panel.html"
@app.get("/panel/doctor")
def panel_doctor():
    return FileResponse(str(DOC_PANEL))
\"\"\", encoding="utf-8")
        return "[OK] Created minimal FastAPI main.py with /panel/doctor route."
    else:
        txt = MAIN.read_text(encoding="utf-8")
        if "/panel/doctor" in txt:
            return "[OK] /panel/doctor route already detected."
        inject = """
# --- Supersonic Doctor route (auto-injected; generic) ---
try:
    from fastapi import FastAPI
    from fastapi.responses import FileResponse
    from pathlib import Path as _Path
    if 'app' not in globals():
        app = FastAPI()
    DOC_PANEL = _Path("templates") / "doctor_panel.html"
    @app.get("/panel/doctor")
    def panel_doctor():
        return FileResponse(str(DOC_PANEL))
except Exception as _e:
    print("[embed] WARN: generic route add failed:", _e)
# --- end doctor route ---
"""
        MAIN.write_text(txt + "\n" + inject, encoding="utf-8")
        return "[OK] Appended generic FastAPI /panel/doctor route to existing main.py."

def inject_link_into_control_panel():
    link_html = '<a href="/panel/doctor" class="btn">Doctor</a>'
    for candidate in CONTROL_PANEL_CANDIDATES:
        if candidate.exists():
            txt = candidate.read_text(encoding="utf-8", errors="ignore")
            if "/panel/doctor" in txt or "Doctor</a>" in txt:
                return f"[OK] Doctor link already present in {candidate.name}"
            if "</body>" in txt:
                new = txt.replace("</body>", "\\n<!-- auto-added doctor link -->\\n"+link_html+"\\n</body>")
            else:
                new = txt + "\\n" + link_html + "\\n"
            candidate.write_text(new, encoding="utf-8")
            return f"[OK] Added Doctor link to {candidate}"
    return "[WARN] No control panel HTML found to inject link; panel still available at /panel/doctor"

def main():
    msgs = []
    msgs.append(install_panel())
    framework = detect_framework()
    if framework == "fastapi":
        msgs.append(patch_main_fastapi())
    elif framework == "flask":
        msgs.append(patch_main_flask())
    else:
        msgs.append(patch_main_unknown())
    msgs.append(inject_link_into_control_panel())
    print("\\n".join(msgs))

if __name__ == "__main__":
    main()
