#!/usr/bin/env python3
"""
bump_version.py — bump VERSION file (semver-ish) and optionally tag.

Usage:
  python scripts/bump_version.py --part patch|minor|major [--pre rc.1] [--no_tag]

Behavior:
- Reads VERSION (e.g., v2.0.7 or 2.0.7-rc.1)
- Bumps selected part; resets lower parts to 0
- Writes back to VERSION, prints the new version string
- If --no_tag not set, prints a suggested git tag (stdout) so Makefile can tag

Examples:
  python scripts/bump_version.py --part patch
  python scripts/bump_version.py --part minor --pre rc.1
"""
import re
import sys
import argparse
from pathlib import Path

SEMVER_RE = re.compile(r'^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z\.-]+))?$')

def parse_version(s: str):
    m = SEMVER_RE.match(s.strip())
    if not m:
        raise SystemExit(f"Invalid VERSION format: {s!r}. Expected vMAJOR.MINOR.PATCH[-PRERELEASE].")
    major, minor, patch = map(int, m.groups()[:3])
    pre = m.group(4)
    return major, minor, patch, pre

def format_version(major, minor, patch, pre=None, with_v=True):
    base = f"{major}.{minor}.{patch}"
    if pre:
        base += f"-{pre}"
    return f"v{base}" if with_v else base

def bump(major, minor, patch, pre, part, new_pre):
    if part == "major":
        major += 1; minor = 0; patch = 0
    elif part == "minor":
        minor += 1; patch = 0
    elif part == "patch":
        patch += 1
    else:
        raise SystemExit("--part must be major|minor|patch")
    pre = new_pre  # can be None
    return major, minor, patch, pre

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=["major","minor","patch"])
    ap.add_argument("--pre", default=None, help="optional prerelease identifier, e.g., rc.1")
    ap.add_argument("--no_tag", action="store_true", help="do not print the tag to stdout")
    ap.add_argument("--file", default="VERSION")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        raise SystemExit(f"VERSION file not found at {path}")

    cur = path.read_text(encoding="utf-8").strip()
    major, minor, patch, pre = parse_version(cur)
    major, minor, patch, pre = bump(major, minor, patch, pre, args.part, args.pre)

    newv = format_version(major, minor, patch, pre, with_v=True)
    path.write_text(newv + "\n", encoding="utf-8")
    print(newv)  # stdout for Makefile consumption
    if not args.no_tag:
        # Print a tag suggestion as a second line prefixed with TAG=
        print(f"TAG={newv}")

if __name__ == "__main__":
    main()
