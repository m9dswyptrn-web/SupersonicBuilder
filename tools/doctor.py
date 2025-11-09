
#!/usr/bin/env python3

"""
tools/doctor.py
Quick environment checker for the Sonic Builder project.
- Verifies required files/dirs exist
- Checks Python libs
- Warns on common pitfalls (empty assets, missing YAMLs, etc.)
- Prints next-step guidance

Usage:
  python3 tools/doctor.py
"""
from __future__ import annotations
import sys, os, shutil, importlib.util
from pathlib import Path

OK = "✅"
WARN = "⚠️ "
ERR = "❌"

ROOT = Path(".")
REQUIRED_FILES = [
    ("main.py", "Core PDF generator"),
    ("serve_build.py", "Static file server"),
    ("VERSION", "Project version tag (created by bump)"),
]
REQUIRED_SCRIPTS = [
    ("scripts/validate_config.py", "YAML schema validator"),
    ("scripts/lint_assets.py", "Asset linter"),
]
REQUIRED_TOOLS = [
    ("tools/bump_version.py", "Version bumper"),
    ("tools/make_release_zip.py", "Release ZIP packer"),
    ("tools/write_release_notes.py", "Release notes generator"),
]
REQUIRED_DIRS = [
    ("assets", "Holds images/SVGs used in the manual"),
    ("config", "YAML configuration files (pinout, legends, etc.)"),
    ("build", "PDFs and ZIP artifacts are written here"),
]

PY_DEPS = [
    ("reportlab", "PDF generation"),
    ("PIL", "Image handling (Pillow)"),
]

def check_file(path: Path, desc: str) -> bool:
    if path.exists():
        print(f"{OK} {path} — {desc}")
        return True
    print(f"{ERR} {path} — MISSING ({desc})")
    return False

def check_dir(path: Path, desc: str) -> bool:
    if path.exists() and path.is_dir():
        contents = list(path.iterdir())
        if len(contents)==0:
            print(f"{WARN} {path}/ — exists but EMPTY ({desc})")
        else:
            print(f"{OK} {path}/ — {desc} ({len(contents)} items)")
        return True
    print(f"{ERR} {path}/ — MISSING ({desc})")
    return False

def check_pydep(modname: str, desc: str) -> bool:
    found = importlib.util.find_spec(modname) is not None
    if found:
        print(f"{OK} {modname} — {desc}")
        return True
    print(f"{ERR} {modname} — not installed ({desc})")
    return False

def main():
    print("🔎 Sonic Builder — Doctor\n")

    # Ensure base dirs
    for d,desc in REQUIRED_DIRS:
        check_dir(ROOT/d, desc)

    # Files & scripts
    for f,desc in REQUIRED_FILES:
        check_file(ROOT/f, desc)
    for s,desc in REQUIRED_SCRIPTS:
        check_file(ROOT/s, desc)
    for t,desc in REQUIRED_TOOLS:
        check_file(ROOT/t, desc)

    # Config sanity
    cfg = ROOT/"config"
    if cfg.exists():
        pin_yaml = cfg/"pinout_44pin.yaml"
        if pin_yaml.exists():
            print(f"{OK} {pin_yaml} — found")
        else:
            print(f"{WARN} {pin_yaml} — not found (manual may miss radio pin table)")
        # Count YAMLs
        ymls = list(cfg.glob("*.y*ml"))
        print(f"{OK if ymls else WARN} config/ — {len(ymls)} YAML file(s) detected")

    # Assets sanity
    assets = ROOT/"assets"
    if assets.exists():
        svgs = list(assets.glob("*.svg"))
        rasters = [p for p in assets.glob("*.*") if p.suffix.lower() in {".png",".jpg",".jpeg",".webp"}]
        if not svgs and not rasters:
            print(f"{WARN} assets/ — no images found (SVG or raster).")
        if svgs:
            print(f"{OK} assets/ — {len(svgs)} SVG(s) present (crisp diagrams ✅)")
        if rasters:
            print(f"{OK} assets/ — {len(rasters)} raster image(s) present")

    # Python deps
    print("\n📦 Python dependencies")
    ok_all = True
    for mod,desc in PY_DEPS:
        ok = check_pydep(mod, desc)
        ok_all = ok_all and ok

    # Final guidance
    print("\n🧭 Next steps")
    if not ok_all:
        print("- Install Python deps: pip install reportlab pillow")
    print("- Validate:        make preflight")
    print("- One-shot build:  make release-all")
    print("- Serve & fetch:   make serve-release  (then tap the globe icon)")
    print("\nDone.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
