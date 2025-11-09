#!/usr/bin/env python3
import os, sys, re, argparse, pathlib

VERSION_FILE = pathlib.Path("VERSION")
NEXT_FILE    = pathlib.Path("NEXT_VERSION")

SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(.*)?$")

def read_version(path: pathlib.Path):
    if not path.exists():
        return "v0.0.0"
    return path.read_text(encoding="utf-8").strip()

def bump(ver: str, level: str = "patch"):
    m = SEMVER_RE.match(ver or "v0.0.0")
    if not m:
        raise SystemExit(f"Unrecognized version format: {ver}")
    major, minor, patch = map(int, m.groups()[:3])
    suffix = m.group(4) or ""
    if level == "major":
        major += 1; minor = 0; patch = 0
    elif level == "minor":
        minor += 1; patch = 0
    else:
        patch += 1
    return f"v{major}.{minor}.{patch}{suffix}"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--level", choices=["major","minor","patch"], default="patch")
    p.add_argument("--explicit", help="Explicit version tag, e.g. v2.0.11")
    args = p.parse_args()

    # 1) explicit override
    if args.explicit:
        print(args.explicit.strip())
        return 0

    # 2) NEXT_VERSION file wins if present
    if NEXT_FILE.exists():
        nxt = NEXT_FILE.read_text(encoding="utf-8").strip()
        if nxt:
            print(nxt)
            return 0

    # 3) derive from VERSION (or default v0.0.0)
    cur = read_version(VERSION_FILE)
    print(bump(cur, args.level))
    return 0

if __name__ == "__main__":
    sys.exit(main())
