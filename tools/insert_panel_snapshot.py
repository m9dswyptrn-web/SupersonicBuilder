
#!/usr/bin/env python3
import argparse
from pathlib import Path

CANDIDATES = [
    "main_sub_svgpaired.py",
    "main_usbhdmi_svgpaired.py",
    "main_svg_injected.py",
    "main_patched_helpers.py",
    "main.py",
]

BANNER_TMPL = '''
# === AUTO-INSERT: Panel Snapshot (corner) ===
try:
    # Corner placement: {corner} with size {size}px
    draw_image_fit(c, RES, 'diagrams/panel_snapshot.png', x={x}, y={y}, width={size}, height={size})
except Exception as _err_panel:
    pass

'''

def find_target():
    for name in CANDIDATES:
        p = Path(name)
        if p.exists():
            return p
    raise SystemExit("❌ No main entry file found among: " + ", ".join(CANDIDATES))

def ensure_imports(lines):
    txt = "\n".join(lines)
    ins = []
    if "draw_image_fit" not in txt:
        ins.append("from tools.canvas_draw_helpers import AssetResolver, draw_image_fit, draw_svg_fit")
    if "RES = AssetResolver('assets')" not in txt:
        ins.append("RES = AssetResolver('assets')")
    if ins:
        idx = 0
        for i, ln in enumerate(lines):
            if ln.startswith(("import ", "from ")):
                idx = i+1
        lines[idx:idx] = ins + [""]
    return lines

def inject_panel(lines, anchor="usb", corner="br", size=180):
    idx = -1
    for i, ln in enumerate(lines):
        if anchor.lower() in ln.lower():
            idx = i
            break

    if idx == -1:
        for i, ln in enumerate(lines):
            if "showPage()" in ln:
                idx = i
                break
    if idx == -1:
        idx = len(lines) - 1

    margin = 72
    coords = {
        "tl": (margin, 540),
        "tr": (468, 540),
        "bl": (margin, margin),
        "br": (468, margin),
    }
    x, y = coords.get(corner.lower(), coords["br"])
    banner = BANNER_TMPL.format(corner=corner, size=size, x=x, y=y).splitlines()

    for j, s in enumerate(banner, start=1):
        lines.insert(idx + j, s)
    return lines

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anchor", default="usb")
    ap.add_argument("--corner", default="br")
    ap.add_argument("--size", type=int, default=180)
    args = ap.parse_args()

    t = find_target()
    src = t.read_text(encoding="utf-8").splitlines()
    if "panel_snapshot.png" in "\n".join(src):
        print("✅ Panel snapshot already present.")
        return

    src = ensure_imports(src)
    src = inject_panel(src, anchor=args.anchor, corner=args.corner, size=args.size)
    out = Path("main_panelshot.py")
    out.write_text("\n".join(src), encoding="utf-8")
    print(f"✅ Wrote {out} (anchor='{args.anchor}', corner='{args.corner}', size={args.size})")

if __name__ == "__main__":
    main()
