
#!/usr/bin/env python3
from pathlib import Path
import re

CANDIDATES = ["main_svg_injected.py", "main_patched_helpers.py", "main.py"]

SVG_LINE = "draw_svg_fit(c, RES, 'diagrams/usb_hdmi_overview.svg', x=72, y=260, max_w=420, max_h=260)"
PNG_LINE = "draw_image_fit(c, RES, 'diagrams/usb_hdmi_overview.png', x=72, y=120, width=420, height=120)"

BANNER = [
"",
"# === AUTO-INSERT: USB/HDMI Retrofit (SVG + PNG) ===",
"try:",
f"    {SVG_LINE}",
f"    {PNG_LINE}",
"except Exception as _err_usb:",
"    pass",
"",
]

def find_target():
    for name in CANDIDATES:
        p = Path(name)
        if p.exists(): return p
    raise SystemExit("❌ No main file found.")

def ensure_imports(lines):
    txt = "\n".join(lines)
    ins = []
    if "draw_svg_fit" not in txt:
        ins.append("from tools.canvas_draw_helpers import AssetResolver, draw_image_fit, draw_svg_fit")
    if "RES = AssetResolver('assets')" not in txt:
        ins.append("RES = AssetResolver('assets')")
    if ins:
        # insert after imports
        idx = 0
        for i, ln in enumerate(lines):
            if ln.startswith(("import ","from ")): idx = i+1
        lines[idx:idx] = ins + [""]
    return lines

def inject_usb(lines):
    txt = "\n".join(lines).lower()
    # Best spot: look for "usb" or "hdmi" section
    idx = -1
    for i, ln in enumerate(lines):
        low = ln.lower()
        if "usb" in low or "hdmi" in low:
            idx = i; break
    # else before first showPage
    if idx == -1:
        for i, ln in enumerate(lines):
            if "showPage()" in ln: idx = i; break
    if idx == -1: idx = len(lines)-1
    for j, s in enumerate(BANNER, start=1):
        lines.insert(idx + j, s)
    return lines

def main():
    t = find_target()
    lines = t.read_text(encoding="utf-8").splitlines()
    if "usb_hdmi_overview.svg" in "\n".join(lines):
        print("✅ USB/HDMI block already present."); return
    lines = ensure_imports(lines)
    lines = inject_usb(lines)
    out = Path("main_usbhdmi_svgpaired.py")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Wrote {out}")

if __name__ == "__main__":
    main()
