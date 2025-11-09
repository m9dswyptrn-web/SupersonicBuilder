#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
supersonic_deploy_pages.py
------------------------------------------------------------
Copies Commander Dashboard + assets to /docs for GitHub Pages.
Safe to run repeatedly; only copies files that exist.

Default layout (served at https://<user>.github.io/<repo>/):
  docs/
    Supersonic_Dashboard.html
    SonicBuilder/branding/**
    SonicBuilder/docs/diagrams/**
    SonicBuilder/release/**
    SonicBuilder/reports/**   (telemetry, changelog cards)
"""

from __future__ import annotations
from pathlib import Path
import shutil, sys

ROOT = Path(".")
SRC_DASH = ROOT / "Supersonic_Dashboard.html"
SRC_SB = ROOT / "SonicBuilder"
DEST = ROOT / "docs"

INCLUDE = [
    "branding",
    "docs/diagrams",
    "release",
    "reports",
]

def copy_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

def copy_tree(src: Path, dst: Path):
    if not src.exists(): return
    for p in src.rglob("*"):
        if p.is_file():
            rel = p.relative_to(src)
            copy_file(p, dst / rel)

def deploy():
    print("🚀 Deploying to /docs …")
    DEST.mkdir(parents=True, exist_ok=True)

    if SRC_DASH.exists():
        copy_file(SRC_DASH, DEST / "Supersonic_Dashboard.html")
        print("  • Dashboard copied")
    else:
        print("  • Dashboard missing (skip)")

    for sub in INCLUDE:
        src = SRC_SB / sub
        dst = DEST / "SonicBuilder" / sub
        if src.exists():
            copy_tree(src, dst)
            print(f"  • Copied {sub}/")
        else:
            print(f"  • Missing {sub}/ (skip)")

    print("✅ Deploy copy complete → docs/")
    print("ℹ️ Commit & push to publish (Pages must be set to /docs).")

if __name__ == "__main__":
    try:
        deploy()
        sys.exit(0)
    except Exception as e:
        print("❌ Deploy error:", e)
        sys.exit(1)
