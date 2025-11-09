#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
supersonic_promote_preview.py
------------------------------------------------------------
Promotes patched HTML from docs/_fixed_preview/** into docs/**
• Makes a timestamped backup of changed originals under: docs/_backup_<ts>/
• Only promotes .html files (keeps assets untouched)
• Skips if preview missing

Usage:
  python supersonic_promote_preview.py
Exit 0 on success, 1 on fatal error.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import shutil, sys, filecmp

DOCS = Path("docs")
PREVIEW = DOCS / "_fixed_preview"

def main():
    if not DOCS.exists():
        print("❌ docs/ not found. Run deploy first.")
        return 1
    if not PREVIEW.exists():
        print("❌ docs/_fixed_preview/ not found. Run autofix preview first.")
        return 1

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_dir = DOCS / f"_backup_{ts}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    promoted = 0
    scanned = 0
    for p in PREVIEW.rglob("*.html"):
        rel = p.relative_to(PREVIEW)
        dst = DOCS / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        scanned += 1
        if dst.exists():
            try:
                if filecmp.cmp(p, dst, shallow=False):
                    print(f"• unchanged: {rel.as_posix()}")
                    continue
            except Exception:
                pass

            bkp = backup_dir / rel
            bkp.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, bkp)
            print(f"🛟 backup:   {rel.as_posix()} → {bkp.relative_to(DOCS).as_posix()}")

        shutil.copy2(p, dst)
        print(f"✅ promoted: {rel.as_posix()}")
        promoted += 1

    print(f"\nSummary: scanned {scanned} preview html → promoted {promoted}")
    if promoted:
        print(f"Backups in: {backup_dir.relative_to(DOCS).as_posix()}")
    else:
        print("No changes promoted (all identical).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
