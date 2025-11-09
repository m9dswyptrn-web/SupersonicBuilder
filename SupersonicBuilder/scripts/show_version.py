#!/usr/bin/env python3
"""Show current version from VERSION file"""
from pathlib import Path

root = Path(".")
for p in (root/"VERSION", root/"build"/"VERSION.txt"):
    if p.exists():
        try:
            v = p.read_text(encoding="utf-8").strip()
            if v:
                print(f"{p.name}: {v}")
        except Exception:
            pass
