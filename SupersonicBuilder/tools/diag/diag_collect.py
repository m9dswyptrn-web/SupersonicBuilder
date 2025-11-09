#!/usr/bin/env python3

# SonicBuilder Diagnostics Bundle Collector v1.0.0
# Creates a sanitized ZIP of project state to share for troubleshooting.
#
# What it collects (if present):
# - Makefile, .replit, requirements*.txt, pyproject.toml, setup.cfg
# - scripts/**/*.py (small files under 500 KB)
# - .github/workflows/*.yml
# - docs/**/*.md (under 500 KB)
# - out/*.log, out/*.pdf (filenames only logged, PDFs not included unless --include-pdf)
# - environment info (python --version, pip freeze), uname, timezone
#
# Excludes: .git/, node_modules/, venvs, __pycache__, exports/, large binaries
#
# Usage:
#   python tools/diag/diag_collect.py --out diag/diag_bundle.zip [--include-pdf]
import os, sys, json, subprocess, platform, time
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

def safe_write(z, base, p):
    try:
        rel = p.relative_to(base)
    except Exception:
        rel = p.name
    z.write(p, rel.as_posix())

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="diag/diag_bundle.zip")
    ap.add_argument("--include-pdf", action="store_true", help="include PDFs from out/ (may be large)")
    A = ap.parse_args()

    base = Path(".").resolve()
    outp = base / A.out
    outp.parent.mkdir(parents=True, exist_ok=True)

    excludes = {".git", "node_modules", ".venv", "venv", "__pycache__", "exports"}
    small = 500*1024

    with ZipFile(outp, "w", ZIP_DEFLATED) as z:
        # Top files
        for name in ["Makefile",".replit","requirements.txt","requirements-dev.txt","pyproject.toml","setup.cfg","README.md"]:
            p = base / name
            if p.exists() and p.is_file():
                safe_write(z, base, p)

        # scripts/**/*.py
        for p in base.rglob("scripts/*.py"):
            if any(x in p.parts for x in excludes): continue
            if p.is_file() and p.stat().st_size <= small:
                safe_write(z, base, p)

        # workflows
        for p in (base / ".github" / "workflows").glob("*.yml"):
            if p.is_file(): safe_write(z, base, p)

        # docs md
        for p in base.rglob("docs/*.md"):
            if any(x in p.parts for x in excludes): continue
            if p.is_file() and p.stat().st_size <= small:
                safe_write(z, base, p)

        # out logs
        out_dir = base / "out"
        if out_dir.exists():
            for p in out_dir.glob("*.log"):
                if p.is_file() and p.stat().st_size <= small:
                    safe_write(z, base, p)
            # PDFs: names only unless include flag
            for p in out_dir.glob("*.pdf"):
                if A.include_pdf and p.is_file():
                    safe_write(z, base, p)

        # environment info
        info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "uname": platform.uname()._asdict() if hasattr(platform.uname(), "_asdict") else str(platform.uname()),
            "timezone": time.tzname,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())
        }
        # pip freeze
        try:
            frz = subprocess.check_output([sys.executable,"-m","pip","freeze"], timeout=20).decode().splitlines()
        except Exception as e:
            frz = [f"pip freeze failed: {e!r}"]
        info["pip_freeze"] = frz

        z.writestr("diag/env_info.json", json.dumps(info, indent=2))

    print(f"✅ Diagnostics bundle created: {outp}")

if __name__ == "__main__":
    main()
