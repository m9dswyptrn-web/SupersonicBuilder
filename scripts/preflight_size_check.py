#!/usr/bin/env python3
"""Preflight size check for non-PDF artifacts."""
import sys
from pathlib import Path

MAX_MB = 200
MAX_BYTES = MAX_MB * 1024 * 1024

def human(n):
    u=['B','KB','MB','GB','TB']; i=0; x=float(n)
    while x>=1024 and i<len(u)-1: x/=1024; i+=1
    return f"{x:.2f} {u[i]}"

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "release_assets")
    offenders = []
    for f in root.rglob("*"):
        if not f.is_file():
            continue
        size = f.stat().st_size
        # PDFs are allowed regardless of size; also skip .partNN files
        if f.suffix.lower() != ".pdf" and not ".part" in f.name and size > MAX_BYTES:
            offenders.append((f.name, size))
    
    if offenders:
        print(f"\n❌ Preflight check failed: {len(offenders)} offending file(s) exceed {MAX_MB} MB (non-PDF):")
        for name, size in offenders:
            print(f"   - {name} ({human(size)})")
        print(f"\n💡 Either compress/split these files or exclude them from release.")
        sys.exit(2)
    else:
        print("✅ Preflight size check passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
