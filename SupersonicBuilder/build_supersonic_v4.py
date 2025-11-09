#!/usr/bin/env python3
"""
Supersonic Control Core v4 Builder
Creates Supersonic_ControlCore_Addons_v4.zip from make/, scripts/, docs/, and .github/workflows/
"""
import zipfile, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Supersonic_ControlCore_Addons_v4.zip"
SRC = ["make", "scripts", "docs", ".github/workflows"]

def build_zip():
    if OUT.exists(): OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for folder in SRC:
            p = ROOT / folder
            if not p.exists(): continue
            for f in p.rglob("*"):
                if f.is_file():
                    z.write(f, f.relative_to(ROOT))
    print(f"[OK] Supersonic_ControlCore_Addons_v4.zip created ({OUT.stat().st_size/1024:.1f} KB)")

if __name__ == "__main__":
    build_zip()
