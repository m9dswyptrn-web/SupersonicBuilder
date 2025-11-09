#!/usr/bin/env python3
"""
Supersonic Voice Pack Switcher
Creates/updates an "active" pack pointer so all tools default to it.

Usage:
  python scripts/voicepack_switch.py list
  python scripts/voicepack_switch.py current
  python scripts/voicepack_switch.py use <packname>

Behavior:
- Active path: assets/audio/voicepacks/_active  (symlink; copies on Windows if needed)
- Packs live in: assets/audio/voicepacks/<packname>/
- Returns non-zero exit on error.
"""
from pathlib import Path
import os, sys, shutil

ROOT = Path(__file__).resolve().parents[1]
VP_ROOT = ROOT / "assets" / "audio" / "voicepacks"
ACTIVE = VP_ROOT / "_active"

def err(msg): print(f"ERROR: {msg}", file=sys.stderr); sys.exit(1)

def list_packs():
    if not VP_ROOT.exists():
        print("(no voicepacks found)"); return
    packs = sorted([p.name for p in VP_ROOT.iterdir() if p.is_dir() and not p.name.startswith("_")])
    for p in packs: print(p)

def current():
    if ACTIVE.is_symlink():
        print(ACTIVE.resolve().name); return
    if ACTIVE.exists() and ACTIVE.is_dir():
        meta = (ACTIVE / ".packname")
        if meta.exists():
            print(meta.read_text().strip()); return
        print("_active (copy)"); return
    print("(none)")

def use(pack: str):
    target = VP_ROOT / pack
    if not target.exists() or not target.is_dir():
        err(f"voicepack '{pack}' not found in {VP_ROOT}")

    VP_ROOT.mkdir(parents=True, exist_ok=True)

    if ACTIVE.is_symlink():
        ACTIVE.unlink()
    elif ACTIVE.exists():
        shutil.rmtree(ACTIVE, ignore_errors=True)

    try:
        os.symlink(target, ACTIVE, target_is_directory=True)
        print(f"[OK] Active voicepack → {pack} (symlink)")
        return
    except Exception:
        pass

    shutil.copytree(target, ACTIVE)
    try:
        (ACTIVE / ".packname").write_text(pack)
    except Exception:
        pass
    print(f"[OK] Active voicepack → {pack} (copied)")

def main():
    if len(sys.argv) < 2:
        print("Usage: voicepack_switch.py [list|current|use <pack>]"); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "list":
        list_packs()
    elif cmd == "current":
        current()
    elif cmd == "use":
        if len(sys.argv) < 3: err("missing <packname>")
        use(sys.argv[2])
    else:
        err(f"unknown command: {cmd}")

if __name__ == "__main__":
    main()
