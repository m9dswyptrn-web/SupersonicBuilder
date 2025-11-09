
#!/usr/bin/env python3
import argparse
from pathlib import Path
from PIL import Image

def dpi_info(img: Image.Image):
    dpi = img.info.get("dpi", (72,72))
    if isinstance(dpi, tuple): return dpi
    try:
        return (int(dpi), int(dpi))
    except Exception:
        return (72,72)

def scan(root: Path):
    total = 0
    for p in root.rglob("*"):
        if p.suffix.lower() in {".png",".jpg",".jpeg"}:
            try:
                img = Image.open(p)
                w,h = img.size
                dx, dy = dpi_info(img)
                print(f"🖼️  {p}: {w}x{h}px @ {dx}x{dy} DPI")
                total += 1
            except Exception as e:
                print(f"⚠️  {p}: {e}")
    print(f"\nChecked {total} raster image(s).")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="assets")
    args = ap.parse_args()
    scan(Path(args.root))

if __name__ == "__main__":
    main()
