#!/usr/bin/env python3
"""Split oversize non-PDF artifacts into ~180 MB parts."""
import os, math
from pathlib import Path

LIMIT_MB = int(os.environ.get("SB_SPLIT_LIMIT_MB", "200"))
PART_MB  = int(os.environ.get("SB_SPLIT_PART_MB",  "180"))
LIMIT    = LIMIT_MB * 1024 * 1024
PARTSIZE = PART_MB  * 1024 * 1024

def human(n):
    u=['B','KB','MB','GB','TB']; i=0; x=float(n)
    while x>=1024 and i<len(u)-1: x/=1024; i+=1
    return f"{x:.2f} {u[i]}"

def split_file(p: Path):
    """Split file into parts of PARTSIZE bytes."""
    size = p.stat().st_size
    if size <= LIMIT:
        return False, []
    
    parts = math.ceil(size / PARTSIZE)
    part_paths = []
    
    with p.open('rb') as src:
        for i in range(parts):
            chunk = src.read(PARTSIZE)
            if not chunk:
                break
            out = p.with_name(f"{p.name}.part{str(i+1).zfill(2)}")
            with out.open('wb') as dst:
                dst.write(chunk)
            part_paths.append(out)
    
    print(f"   ↳ split {p.name} → {len(part_paths)} parts (<~{PART_MB} MB each)")
    return True, part_paths

def main():
    root = Path("release_assets")
    if not root.exists():
        print("release_assets not found; nothing to split.")
        return
    
    overs = []
    for f in root.rglob("*"):
        if f.is_file() and f.suffix.lower() != ".pdf" and ".part" not in f.name and f.stat().st_size > LIMIT:
            overs.append(f)
    
    if not overs:
        print(f"No oversize non-PDF artifacts (> {LIMIT_MB} MB) to split.")
        return
    
    for f in overs:
        print(f"- {f.name} ({human(f.stat().st_size)}) exceeds {LIMIT_MB} MB; splitting…")
        try:
            _, parts = split_file(f)
            for p in parts:
                print(f"   • {p.name} ({human(p.stat().st_size)})")
        except Exception as e:
            print(f"   ! split error: {e}")

    # Write reassembly instructions
    man = root / "SPLIT_MANIFEST.txt"
    with man.open("w") as w:
        w.write(f"# Split artifacts (limit {LIMIT_MB} MB, part size ~{PART_MB} MB)\n\n")
        w.write("## Reassemble on Linux/Mac:\n")
        w.write("cat <file>.zip.part* > <file>.zip\n\n")
        w.write("## Reassemble on Windows PowerShell:\n")
        w.write("Get-ChildItem <file>.zip.part* | Get-Content -Encoding Byte -ReadCount 0 | Set-Content -Encoding Byte <file>.zip\n")
    print(f"Wrote {man}")
    print("Done.")

if __name__ == "__main__":
    main()
