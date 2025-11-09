#!/usr/bin/env python3
"""
Supersonic — Voice Pack Preview
Auditions a voicepack by playing all standard events in order,
then restores the previously active pack.

Usage:
  python3 scripts/voicepack_preview.py PACKNAME
  # Options:
  #   --shuffle       play in random order
  #   --delay 0.7     seconds between clips (default 0.6)
  #   --keep-active   do NOT restore previous pack at the end
"""
import argparse, os, random, sys, time, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable or "python3"
VOICE_SWITCH = ROOT / "scripts" / "voicepack_switch.py"
VOICE_CONSOLE = ROOT / "helpers" / "supersonic_voice_console.py"
ACTIVE_DIR = ROOT / "assets" / "audio" / "voicepacks" / "_active"

EVENTS = [
    "build_start",
    "build_success",
    "build_fail",
    "deploy_start",
    "deploy_done",
    "doctor_ok",
    "doctor_warn",
]

def run(cmd, env=None):
    return subprocess.run(cmd, check=False, env=env or os.environ.copy())

def current_active_name() -> str:
    if ACTIVE_DIR.exists() and ACTIVE_DIR.is_dir():
        meta = ACTIVE_DIR / ".packname"
        if meta.exists():
            return meta.read_text().strip()
        try:
            return ACTIVE_DIR.resolve().name
        except Exception:
            return "_active"
    return ""

def set_active(pack: str):
    run([PY, str(VOICE_SWITCH), "use", pack])

def preview(pack: str, delay: float = 0.6, shuffle: bool = False, keep_active: bool = False):
    prev = current_active_name()
    if prev == pack:
        print(f"[info] '{pack}' is already active.")
    else:
        print(f"[switch] Active → {pack} (was: {prev or 'none'})")
        set_active(pack)

    order = EVENTS[:]
    if shuffle:
        random.shuffle(order)

    print(f"[preview] {pack} — {len(order)} events")
    for ev in order:
        print(f"  ▶ {ev}")
        run([PY, str(VOICE_CONSOLE), ev])
        time.sleep(delay)

    if not keep_active:
        if prev and prev != pack:
            print(f"[restore] Active → {prev}")
            set_active(prev)
        else:
            print("[restore] No change needed.")
    else:
        print("[keep] Leaving pack active:", pack)

def main():
    ap = argparse.ArgumentParser(description="Preview a Supersonic voice pack.")
    ap.add_argument("pack", help="voicepack name (e.g., commander, aiops)")
    ap.add_argument("--delay", type=float, default=0.6, help="seconds between clips")
    ap.add_argument("--shuffle", action="store_true", help="play in random order")
    ap.add_argument("--keep-active", action="store_true", help="do not restore previous pack")
    args = ap.parse_args()
    if not (ROOT / "assets" / "audio" / "voicepacks" / args.pack).exists():
        print(f"ERROR: voicepack '{args.pack}' not found under assets/audio/voicepacks/")
        sys.exit(1)
    preview(args.pack, delay=args.delay, shuffle=args.shuffle, keep_active=args.keep_active)

if __name__ == "__main__":
    main()
