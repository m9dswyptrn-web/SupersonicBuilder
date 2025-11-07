
#!/usr/bin/env python3
import argparse, re, yaml
from pathlib import Path

CANDIDATES = [
    "main_panelshot.py",
    "main_sub_svgpaired.py",
    "main_usbhdmi_svgpaired.py",
    "main_svg_injected.py",
    "main_patched_helpers.py",
    "main.py",
]

OVERLAYS = {
    "A": "diagrams/panel_labels_compact_overlay.svg",
    "B": "diagrams/panel_labels_expanded_overlay.svg",
}

def find_target():
    for name in CANDIDATES:
        p = Path(name)
        if p.exists():
            return p
    raise SystemExit("❌ No main generator file found among: " + ", ".join(CANDIDATES))

def ensure_imports(lines):
    txt = "\n".join(lines)
    ins = []
    if "draw_svg_fit" not in txt or "draw_image_fit" not in txt:
        ins.append("from tools.canvas_draw_helpers import AssetResolver, draw_image_fit, draw_svg_fit")
    if "RES = AssetResolver('assets')" not in txt:
        ins.append("RES = AssetResolver('assets')")
    if ins:
        idx = 0
        for i, ln in enumerate(lines):
            if ln.startswith(("import ", "from ")):
                idx = i + 1
        lines[idx:idx] = ins + [""]
    return lines

def parse_panel_snapshot_coords(lines):
    # Expect a line like:
    # draw_image_fit(c, RES, 'diagrams/panel_snapshot.png', x=468, y=72, width=200, height=200)
    pat = re.compile(r"draw_image_fit\(\s*c\s*,\s*RES\s*,\s*['\"]diagrams/panel_snapshot\.png['\"]\s*,\s*x=(?P<x>\d+)\s*,\s*y=(?P<y>\d+)\s*,\s*width=(?P<w>\d+)\s*,\s*height=(?P<h>\d+)\s*\)")
    for i, ln in enumerate(lines):
        m = pat.search(ln)
        if m:
            return i, int(m.group('x')), int(m.group('y')), int(m.group('w')), int(m.group('h'))
    return -1, None, None, None, None

def load_yaml_nudges():
    cfg = Path("assets/config/panel_labels.yaml")
    if cfg.exists():
        try:
            data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
            return int(data.get("dx", 0) or 0), int(data.get("dy", 0) or 0)
        except Exception:
            return 0, 0
    return 0, 0

def inject_overlay(lines, variant="A"):
    idx, x, y, w, h = parse_panel_snapshot_coords(lines)
    dx, dy = load_yaml_nudges()
    overlay = OVERLAYS.get(variant.upper(), OVERLAYS["A"])

    banner = [
        "",
        "# === AUTO-INSERT: Panel Labels Overlay ===",
        "try:",
        f"    draw_svg_fit(c, RES, '{overlay}', x={x}+{dx}, y={y}+{dy}, max_w={w}, max_h={h})",
        "except Exception as _err_labels:",
        "    pass",
        "",
    ]

    if idx == -1:
        # fallback before first showPage
        insert_at = len(lines) - 1
        for i, ln in enumerate(lines):
            if 'showPage()' in ln:
                insert_at = i
                break
        lines[insert_at:insert_at] = banner
    else:
        # place right after the panel snapshot draw
        lines[idx+1:idx+1] = banner
    return lines

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="A", help="A=compact_overlay, B=expanded_overlay")
    args = ap.parse_args()

    t = find_target()
    lines = t.read_text(encoding='utf-8').splitlines()
    if "AUTO-INSERT: Panel Labels Overlay" in "\n".join(lines):
        print("✅ Overlay already present."); return

    lines = ensure_imports(lines)
    lines = inject_overlay(lines, args.variant)
    out = Path("main_panel_labels.py")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Wrote {out} (variant={args.variant})")

if __name__ == "__main__":
    main()
