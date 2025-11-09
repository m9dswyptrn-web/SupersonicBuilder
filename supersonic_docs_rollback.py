#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
supersonic_docs_rollback.py
------------------------------------------------------------
Restore docs/ HTML from a chosen backup folder created by
supersonic_promote_preview.py (docs/_backup_YYYYMMDD_HHMMSS).

Usage:
  python supersonic_docs_rollback.py --list
  python supersonic_docs_rollback.py --use _backup_20251031_213012 [--yes]
Exit 0 on success, 1 on fatal error.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import shutil, sys, argparse, re

DOCS = Path("docs")
BACKUP_PREFIX = "_backup_"

def list_backups():
    if not DOCS.exists(): return []
    return sorted([p for p in DOCS.iterdir() if p.is_dir() and p.name.startswith(BACKUP_PREFIX)])

def copy_tree(src: Path, dst_root: Path):
    for p in src.rglob("*"):
        if p.is_file():
            rel = p.relative_to(src)
            dst = dst_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="List available backups")
    ap.add_argument("--use", type=str, help="Backup folder name to restore (e.g., _backup_20251031_213012)")
    ap.add_argument("--yes", action="store_true", help="Skip confirmation")
    args = ap.parse_args()

    if not DOCS.exists():
        print("❌ docs/ not found")
        return 1

    backups = list_backups()

    if args.list or not args.use:
        if not backups:
            print("ℹ️ No backups found in docs/")
            return 0 if args.list else 1
        print("Available backups:")
        for b in backups:
            print("  -", b.name)
        if args.list: return 0
        print("❌ --use <backup_name> required")
        return 1

    # Validate backup name (security: prevent path traversal)
    if not args.use.startswith(BACKUP_PREFIX):
        print(f"❌ Invalid backup name: must start with {BACKUP_PREFIX}")
        return 1
    
    if "/" in args.use or "\\" in args.use or ".." in args.use:
        print(f"❌ Invalid backup name: path traversal detected")
        return 1
    
    # Verify backup exists in the list of known backups
    valid_backups = [b.name for b in list_backups()]
    if args.use not in valid_backups:
        print(f"❌ Backup not found: {args.use}")
        print(f"Available backups: {', '.join(valid_backups) if valid_backups else '(none)'}")
        return 1
    
    # find target backup
    target = DOCS / args.use
    if not target.exists() or not target.is_dir():
        print(f"❌ Backup directory missing: {args.use}")
        return 1

    # confirmation
    if not args.yes:
        print(f"About to restore files from {target} into docs/")
        print("This will overwrite files that exist in the backup.")
        resp = input("Proceed? [y/N]: ").strip().lower()
        if resp not in ("y", "yes"): 
            print("Canceled.")
            return 1

    # make pre-rollback backup of current docs HTML
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    pre = DOCS / f"_backup_{ts}_pre_rollback"
    pre.mkdir(parents=True, exist_ok=True)
    print(f"🛟 Creating pre-rollback backup: {pre.name}")
    copy_tree(DOCS, pre)

    # restore
    print(f"⏪ Restoring from {target.name} …")
    copy_tree(target, DOCS)

    print("✅ Rollback complete.")
    print(f"↩️  Previous state saved at {pre.name}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
