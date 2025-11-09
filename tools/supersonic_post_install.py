#!/usr/bin/env python3
"""
supersonic_post_install.py
- Copy Supersonic pack files into your project
- Patch main.py (FastAPI/Flask) to attach endpoints + logging
- NEW: `--zip [OUT]` bundles a full project snapshot (all files) into a zip
       (excludes .git, __pycache__, node_modules by default; override with env)

Usage:
  python3 supersonic_post_install.py
  python3 supersonic_post_install.py --zip                # writes project_snapshot_<ts>.zip
  python3 supersonic_post_install.py --zip my_snapshot.zip
"""
import os, sys, zipfile, shutil, re
from pathlib import Path
from datetime import datetime

ROOT = Path(".").resolve()
DEFAULT_ZIP = ROOT/"Supersonic_Health_and_Sync_Pack.zip"
DEFAULT_DIR = ROOT/"Supersonic_Health_and_Sync_Pack"
PACK_PATH = Path(os.getenv("PACK_PATH") or (DEFAULT_ZIP if DEFAULT_ZIP.exists() else DEFAULT_DIR))

DEST_FILES = [
    "Supersonic_Health_Extension.py",
    "rotating_logger.py",
    "snippets/control_panel_sync.html",
]

DEFAULT_EXCLUDES = {".git", "__pycache__", "node_modules", ".mypy_cache", ".pytest_cache", ".DS_Store"}
MORE_EXCLUDES = set(filter(None, os.getenv("ZIP_EXCLUDES","").split(",")))  # comma sep
EXCLUDES = DEFAULT_EXCLUDES | MORE_EXCLUDES

def info(m): print(f"[INFO] {m}")
def die(m, code=1): print(f"[ERROR] {m}", file=sys.stderr) or sys.exit(code)

def extract_zip(zip_path: Path, tmp_dir: Path) -> Path:
    info(f"Extracting: {zip_path}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z: z.extractall(tmp_dir)
    return tmp_dir / "Supersonic_Health_and_Sync_Pack" if (tmp_dir/"Supersonic_Health_and_Sync_Pack").exists() else tmp_dir

def copy_from_pack(pack_root: Path, dest_root: Path):
    changed = []
    for rel in DEST_FILES:
        src = pack_root / rel
        if not src.exists():
            alt = pack_root / Path(rel).name
            if alt.exists(): src = alt
            else:
                info(f"Skipping missing in pack: {rel}")
                continue
        dst = dest_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        if dst.exists() and dst.read_bytes() == data:
            info(f"= {rel} (unchanged)"); continue
        shutil.copy2(src, dst)
        changed.append(rel); info(f"+ copied {rel}")
    (dest_root/"logs/archive").mkdir(parents=True, exist_ok=True)
    return changed

def detect_framework(main_text: str):
    fa = re.search(r'^\s*(\w+)\s*=\s*FastAPI\s*\(', main_text, flags=re.M)
    if fa: return "fastapi", fa.group(1)
    fl = re.search(r'^\s*(\w+)\s*=\s*Flask\s*\(', main_text, flags=re.M)
    if fl: return "flask", fl.group(1)
    return None, None

def already_patched(text: str) -> bool:
    return "from Supersonic_Health_Extension import attach" in text or "attach(app)" in text

def patch_main(main_path: Path):
    if not main_path.exists(): die(f"main.py not found at: {main_path}")
    original = main_path.read_text(encoding="utf-8")
    if already_patched(original):
        info("main.py already patched; backup saved for safety.")
        backup = main_path.with_name(f"main_backup_{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.py")
        backup.write_text(original, encoding="utf-8")
        return False

    fw, app_var = detect_framework(original)
    if not fw: die("Could not detect FastAPI or Flask app creation (app = FastAPI(...) / app = Flask(__name__))")
    app_line = re.search(rf'^\s*{re.escape(app_var)}\s*=\s*{("FastAPI" if fw=="fastapi" else "Flask")}\s*\(.*?\)\s*$', original, flags=re.M)
    insert_index = app_line.end() if app_line else len(original)

    if fw == "fastapi":
        imports = "from Supersonic_Health_Extension import attach\nfrom rotating_logger import get_logger, RequestLogMiddleware\n"
        attach_block = (f"\n# --- Supersonic health/sync wiring (auto-injected) ---\n"
                        f"log = get_logger('supersonic')\n"
                        f"{app_var}.add_middleware(RequestLogMiddleware, logger=log)\n"
                        f"attach({app_var})\n"
                        f"log.info('Supersonic Health & Sync attached (FastAPI)')\n")
    else:
        imports = "from Supersonic_Health_Extension import attach\nfrom rotating_logger import get_logger, wsgi_request_logger\n"
        attach_block = (f"\n# --- Supersonic health/sync wiring (auto-injected) ---\n"
                        f"log = get_logger('supersonic')\n"
                        f"{app_var}.wsgi_app = wsgi_request_logger({app_var}.wsgi_app, logger=log)\n"
                        f"attach({app_var})\n"
                        f"log.info('Supersonic Health & Sync attached (Flask)')\n")

    text = original
    if text.startswith("#!"):
        first_nl = text.find("\n")
        text = text[:first_nl+1] + imports + text[first_nl+1:]
        insert_index += len(imports)
    else:
        text = imports + text
        insert_index += len(imports)

    new_text = text[:insert_index] + attach_block + text[insert_index:]
    backup = main_path.with_name(f"main_backup_{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.py")
    backup.write_text(original, encoding="utf-8")
    main_path.write_text(new_text, encoding="utf-8")
    info(f"Patched main.py for {fw}; backup: {backup.name}")
    return True

def should_exclude(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDES: return True
    # exclude hidden top-level folders/files by default except .env
    if any(part.startswith(".") and part not in {".env"} for part in path.parts): return True
    return False

def make_snapshot_zip(out_path: Path):
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    if out_path is None:
        out_path = ROOT/f"project_snapshot_{ts}.zip"
    count = 0
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in ROOT.rglob("*"):
            if p.is_dir(): continue
            rel = p.relative_to(ROOT)
            if should_exclude(rel): continue
            z.write(p, rel)
            count += 1
    info(f"Snapshot written: {out_path} ({count} files)")
    return out_path

def main(argv=None):
    argv = argv or sys.argv[1:]
    if argv and argv[0] == "--zip":
        out = None if len(argv) == 1 else Path(argv[1])
        make_snapshot_zip(out)
        return

    print("=== Supersonic Post-Install ===")
    if not PACK_PATH.exists():
        die(f"Pack not found: {PACK_PATH}. Expected {DEFAULT_ZIP} or {DEFAULT_DIR}")
    tmp = ROOT/".supersonic_tmp"
    if tmp.exists(): shutil.rmtree(tmp, ignore_errors=True)
    if PACK_PATH.is_file() and PACK_PATH.suffix.lower()==".zip":
        with zipfile.ZipFile(PACK_PATH, "r") as z: z.extractall(tmp)
        pack_root = tmp/"Supersonic_Health_and_Sync_Pack" if (tmp/"Supersonic_Health_and_Sync_Pack").exists() else tmp
    else:
        pack_root = PACK_PATH
    info(f"Using pack root: {pack_root}")
    changed = copy_from_pack(pack_root, ROOT)
    patched = patch_main(ROOT/"main.py")
    shutil.rmtree(tmp, ignore_errors=True)

    print("\n=== Summary ===")
    if changed:
        for f in changed: print(f"  + updated: {f}")
    else:
        print("  = files already up to date")
    print(f"  * main.py {'patched' if patched else 'already patched'}")
    print("\nNext steps:\n  - Run your app and look for the Supersonic banner.\n  - Test: /api/ping, /api/ready, /api/status, POST /api/sync\n  - Add `snippets/control_panel_sync.html` to your control panel.\nDone. 🚀")

if __name__ == '__main__':
    main()
