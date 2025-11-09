#!/usr/bin/env python3
"""
tools/bump_version.py
Auto-bumps the patch version number in VERSION file and build/VERSION.txt
Usage:
  python3 tools/bump_version.py --auto
"""
import argparse
from pathlib import Path

def parse_version(v: str) -> tuple[int, int, int]:
    """Parse vX.Y.Z to (X,Y,Z)"""
    v = v.strip().lstrip('v')
    parts = v.split('.')
    return (int(parts[0] or 0), int(parts[1] or 0), int(parts[2] or 0) if len(parts)>2 else 0)

def format_version(major: int, minor: int, patch: int) -> str:
    return f"v{major}.{minor}.{patch}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto", action="store_true", help="Auto-bump patch version")
    args = ap.parse_args()
    
    root = Path(".")
    version_file = root / "VERSION"
    build_version = root / "build" / "VERSION.txt"
    
    # Read current version
    current = "v0.0.0"
    if version_file.exists():
        try:
            current = version_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    elif build_version.exists():
        try:
            current = build_version.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    
    if args.auto:
        major, minor, patch = parse_version(current)
        patch += 1
        new_ver = format_version(major, minor, patch)
        
        # Write to both locations
        version_file.write_text(new_ver + "\n", encoding="utf-8")
        build_version.parent.mkdir(exist_ok=True)
        build_version.write_text(new_ver + "\n", encoding="utf-8")
        
        print(f"Bumped version from {current} to {new_ver}")
    else:
        print(f"Current version: {current}")
        print("Use --auto to bump")

if __name__ == "__main__":
    main()
