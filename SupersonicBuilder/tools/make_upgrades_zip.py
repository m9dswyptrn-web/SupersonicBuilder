#!/usr/bin/env python3
"""Create upgrades ZIP with tools and scripts"""
from pathlib import Path
import zipfile
import time

root = Path(".")
build = Path("build")
build.mkdir(exist_ok=True)

# Read version
ver = "v0.0.0"
for candidate in (root/"VERSION", build/"VERSION.txt"):
    if candidate.exists():
        try:
            ver = candidate.read_text(encoding="utf-8").strip() or ver
            break
        except Exception:
            pass

# Create ZIP
out = build / f"Sonic_Builder_Upgrades_{ver}_{time.strftime('%Y%m%d_%H%M')}.zip"
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for rel in ('scripts', 'tools', 'utils'):
        p = root / rel
        if p.exists():
            for path in p.rglob('*'):
                if path.is_file() and '__pycache__' not in str(path):
                    z.write(path, str(path))
    
    # Add key files
    for item in ('Makefile', 'VERSION', 'README.md', 'CHANGELOG.md'):
        p = root / item
        if p.exists():
            z.write(p, str(p))

print(f"📦 Created {out}")
