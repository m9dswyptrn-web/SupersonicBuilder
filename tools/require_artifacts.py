#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from pathlib import Path
from glob import glob

def any_match(pattern: str) -> bool:
    return any(Path(p).is_file() for p in glob(pattern, recursive=True))

def main():
    ap = argparse.ArgumentParser(description="Ensure required release artifacts exist.")
    ap.add_argument("--require", required=True, help="newline-separated glob patterns that must match at least one file each")
    args = ap.parse_args()

    reqs = [s.strip() for s in args.require.splitlines() if s.strip()]
    missing = [r for r in reqs if not any_match(r)]
    if missing:
        print("❌ Missing required artifacts:")
        for r in missing:
            print(" -", r)
        sys.exit(43)
    print("✅ All required artifact patterns are present.")
    sys.exit(0)

if __name__ == "__main__":
    main()
