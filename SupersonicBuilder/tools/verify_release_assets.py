#!/usr/bin/env python3
"""
verify_release_assets.py
- Verifies SHA256 hashes listed in SHA256SUMS.txt against files in a directory.
- Fails (exit 46) on any mismatch or missing file.
Usage:
  python3 tools/verify_release_assets.py --dir verify
"""
from __future__ import annotations
import argparse, hashlib, sys
from pathlib import Path

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for ch in iter(lambda: f.read(1<<20), b""): h.update(ch)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="verify", help="directory containing downloaded assets")
    ap.add_argument("--sums", default="SHA256SUMS.txt", help="checksums file name inside --dir")
    args = ap.parse_args()

    root = Path(args.dir)
    sums_file = root / args.sums
    if not sums_file.exists():
        print(f"❌ Missing {sums_file}", file=sys.stderr)
        sys.exit(46)

    bad = []
    missing = []
    checked = 0

    for line in sums_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        try:
            digest, path = line.split(None, 1)
            rel = path.strip()
            if rel.startswith("*") or rel.startswith(" "):
                rel = rel.lstrip("* ").strip()
        except ValueError:
            continue

        target = (root / rel).resolve()
        if not target.exists():
            missing.append(rel); continue

        calc = sha256(target)
        if calc.lower() != digest.lower():
            bad.append((rel, digest, calc))
        checked += 1

    if missing or bad:
        if missing:
            print("❌ Missing files listed in SHA256SUMS.txt:")
            for m in missing: print("  -", m)
        if bad:
            print("❌ Hash mismatches:")
            for rel, exp, got in bad:
                print(f"  - {rel}: expected {exp[:12]}…, got {got[:12]}…")
        sys.exit(46)

    print(f"✅ All {checked} files match SHA256SUMS.txt")
    sys.exit(0)

if __name__ == "__main__":
    main()
