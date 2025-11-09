#!/usr/bin/env python3

"""
tools/write_release_notes.py
Generates a RELEASE_NOTES.txt into ./build and (optionally) appends a change-log
section when version changes. It also prints the notes to stdout for visibility.

Inputs (env or args):
  --dpi <int>                DPI used for build (default: 450)
  --stamping <on|off>        Whether footer/title stamping was enabled
  --build-type <text>        e.g., "Full (Dark + Light)"
  --zip-name <filename>      Primary release zip filename
  --modules <csv>            Comma-separated list of included modules

Version resolution order:
  1) ./VERSION (project root)
  2) ./build/VERSION.txt

Writes:
  ./build/RELEASE_NOTES.txt

If an existing RELEASE_NOTES.txt exists with a different version header, a short
"Change Log" section is appended with the new version and timestamp.
"""
import os, sys, argparse, time
from pathlib import Path

def read_version():
    root = Path(".")
    for p in (root/"VERSION", root/"build"/"VERSION.txt"):
        if p.exists():
            try:
                v = p.read_text(encoding="utf-8").strip()
                if v: return v
            except Exception:
                pass
    return "v0.0.0"

def short_time_local():
    return time.strftime("%Y-%m-%d  %H:%M")

def load_existing_notes(path: Path):
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpi", default=os.environ.get("DPI","450"))
    ap.add_argument("--stamping", default=os.environ.get("STAMPING","on"))
    ap.add_argument("--build-type", default=os.environ.get("BUILD_TYPE","Full (Dark + Light)"))
    ap.add_argument("--zip-name", default=os.environ.get("ZIP_NAME","(not packaged yet)"))
    ap.add_argument("--modules", default=os.environ.get("MODULES","G-RZ-GM59 CAN Integration,iDatalink Maestro RR2 + GM2 T-Harness,DSP/AMP Tap Points + Subwoofer Routing,USB/HDMI Retrofit,Grounding Map + USB/AUX Vector Diagram,Auto TOC + Anchors"))
    args = ap.parse_args()

    build = Path("build")
    build.mkdir(exist_ok=True)

    version = read_version()
    ts = short_time_local()

    # Prepare body
    modules = [m.strip() for m in args.modules.split(",") if m.strip()]
    lines = []
    lines.append("Chevy Sonic LTZ Upgrade Manual")
    lines.append(f"Release: {version}")
    lines.append(f"Date: {ts}")
    lines.append(f"Build DPI: {args.dpi}")
    lines.append(f"Stamping: {'Enabled' if str(args.stamping).lower() in ('on','true','1','yes') else 'Disabled'}")
    lines.append(f"Build Type: {args.build_type}")
    lines.append("------------------------------------")
    lines.append("Modules Included:")
    for m in modules:
        lines.append(f"- {m}")
    lines.append("------------------------------------")
    lines.append("Build Status: ✅ Success")
    lines.append(f"ZIP File: {args.zip_name}")
    lines.append("------------------------------------")
    body = "\n".join(lines) + "\n"

    notes_path = build/"RELEASE_NOTES.txt"
    prev = load_existing_notes(notes_path)

    # Decide whether to append a Change Log entry
    add_changelog = False
    if prev:
        # Try to find previous "Release: vX.Y.Z"
        import re
        m = re.search(r"^Release:\s*(\S+)", prev, flags=re.MULTILINE)
        if m:
            prev_ver = m.group(1).strip()
            if prev_ver != version:
                add_changelog = True

    if add_changelog:
        changelog = []
        changelog.append("")
        changelog.append("CHANGE LOG")
        changelog.append("----------")
        changelog.append(f"{ts}  {version}:")
        changelog.append("  - Automated build with updated artifacts.")
        changelog.append("")
        updated = prev.rstrip() + "\n\n" + body + "\n" + "\n".join(changelog) + "\n"
        notes_path.write_text(updated, encoding="utf-8")
    else:
        notes_path.write_text(body, encoding="utf-8")

    # Echo to terminal for immediate visibility
    print("📜 RELEASE_NOTES.txt:\n" + ("-"*36) + "\n" + (notes_path.read_text(encoding="utf-8")))

if __name__ == "__main__":
    main()
