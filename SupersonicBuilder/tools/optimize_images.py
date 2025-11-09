
#!/usr/bin/env python3
import argparse, io, os, sys
from pathlib import Path
from PIL import Image

EXTS = {".png", ".jpg", ".jpeg"}

def optimize_image(p: Path):
    try:
        img = Image.open(p)
        fmt = (img.format or "").upper()
        if p.suffix.lower() == ".png":
            # Try saving optimized PNG
            bio = io.BytesIO()
            img.save(bio, format="PNG", optimize=True)
            new = bio.getvalue()
            old = p.read_bytes()
            if len(new) < len(old):
                p.write_bytes(new)
                return len(old) - len(new)
        elif p.suffix.lower() in {".jpg",".jpeg"}:
            # Light lossy save @ quality 90 with optimize+progressive
            bio = io.BytesIO()
            img = img.convert("RGB")
            img.save(bio, format="JPEG", quality=90, optimize=True, progressive=True)
            new = bio.getvalue()
            old = p.read_bytes()
            if len(new) < len(old):
                p.write_bytes(new)
                return len(old) - len(new)
        return 0
    except Exception as e:
        print(f"⚠️  {p}: {e}")
        return 0

def walk(root: Path):
    saved = 0
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in EXTS:
            delta = optimize_image(p)
            if delta>0:
                print(f"🪶 {p}  -{delta/1024:.1f} KB")
                saved += delta
    print(f"\n✅ Optimization complete. Total saved: {saved/1024:.1f} KB")
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="assets")
    args = ap.parse_args()
    return walk(Path(args.root))

if __name__ == "__main__":
    raise SystemExit(main())
