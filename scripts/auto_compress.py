#!/usr/bin/env python3
"""Re-compress non-PDF artifacts in release_assets (ZIPs & folders)."""
import os, subprocess, shutil
from pathlib import Path

MAX_MB = 200
MAX_BYTES = MAX_MB * 1024 * 1024

def human(n):
    u=['B','KB','MB','GB','TB']; i=0; x=float(n)
    while x>=1024 and i<len(u)-1: x/=1024; i+=1
    return f"{x:.2f} {u[i]}"

def zip_dir(src: Path, out_zip: Path):
    """Compress directory with maximum compression."""
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(["zip","-r9q", str(out_zip), "."], cwd=str(src))

def rezip_file(src_zip: Path, out_zip: Path):
    """Recompress existing ZIP with maximum compression."""
    tmp = out_zip.with_suffix(".repack")
    subprocess.check_call(["unzip","-q","-o", str(src_zip), "-d", str(tmp)])
    zip_dir(tmp, out_zip)
    shutil.rmtree(tmp, ignore_errors=True)

def main():
    root = Path("release_assets")
    if not root.exists():
        print("release_assets not found; nothing to compress.")
        return

    # Collect offenders: non-PDF files/dirs > 200 MB
    offenders = []
    for p in root.iterdir():
        if p.is_dir():
            size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
            if size > MAX_BYTES:
                offenders.append((p, size, "dir"))
        elif p.is_file():
            if p.suffix.lower() != ".pdf" and p.stat().st_size > MAX_BYTES:
                offenders.append((p, p.stat().st_size, "file"))

    if not offenders:
        print("No oversize non-PDF artifacts detected.")
        return

    print(f"Found {len(offenders)} oversize artifacts > {MAX_MB} MB (non-PDF). Attempting compression...")
    success = []
    still_big = []

    for path, size, kind in offenders:
        print(f" - {path.name}: {human(size)} ({kind})")
        try:
            if kind == "dir":
                out_zip = path.with_suffix(".zip")
                if out_zip.exists():
                    out_zip.unlink()
                zip_dir(path, out_zip)
                new_size = out_zip.stat().st_size
                print(f"   ↳ zipped → {out_zip.name} ({human(new_size)})")
                if new_size <= MAX_BYTES:
                    success.append((out_zip, new_size))
                else:
                    still_big.append((out_zip, new_size))
            else:
                if path.suffix.lower() == ".zip":
                    out_zip = path.with_suffix(".repacked.zip")
                    rezip_file(path, out_zip)
                    new_size = out_zip.stat().st_size
                    print(f"   ↳ repacked → {out_zip.name} ({human(new_size)})")
                    if new_size <= MAX_BYTES:
                        path.unlink()
                        out_zip.rename(path)
                        success.append((path, new_size))
                    else:
                        if new_size < path.stat().st_size:
                            path.unlink()
                            out_zip.rename(path)
                            print("   ↳ kept repacked (still > limit but smaller)")
                            still_big.append((path, new_size))
                        else:
                            out_zip.unlink()
                            still_big.append((path, path.stat().st_size))
                else:
                    print("   ↳ not a ZIP; cannot recompress generically.")
                    still_big.append((path, size))
        except Exception as e:
            print(f"   ! compression error: {e}")
            still_big.append((path, size))

    print("\nCompression summary:")
    for p,s in success:
        print(f" ✅ {p.name}: {human(s)}")
    for p,s in still_big:
        print(f" ⚠️  {p.name}: {human(s)} (still over {MAX_MB} MB)")

    # Write manifest
    man = root / "COMPRESSION_MANIFEST.txt"
    with man.open("w") as f:
        print("Compressed OK:", file=f)
        for p,s in success:
            print(f"  - {p.name}  {s} bytes", file=f)
        print("\nStill oversize:", file=f)
        for p,s in still_big:
            print(f"  - {p.name}  {s} bytes", file=f)
    print(f"\nWrote {man}")

if __name__ == "__main__":
    main()
