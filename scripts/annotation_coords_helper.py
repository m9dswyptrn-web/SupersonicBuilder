
#!/usr/bin/env python3
"""
annotation_coords_helper.py
Usage:
  python scripts/annotation_coords_helper.py --x_px 350 --y_px 420 --panel_left 72 --panel_bottom 72 --panel_width 468 --panel_height 648
Returns normalized coords (x, y) for annotations.json
Notes:
  - panel_* are the inner panel bbox you use in render_pages.draw_dark_frame (in points)
  - If you don't know the exact inner panel, approximate: panel_left=0, panel_bottom=0, panel_width=page_w, panel_height=page_h
"""
import argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x_px", type=float, required=True)
    ap.add_argument("--y_px", type=float, required=True)
    ap.add_argument("--panel_left", type=float, default=0.0)
    ap.add_argument("--panel_bottom", type=float, default=0.0)
    ap.add_argument("--panel_width", type=float, default=612.0)   # Letter width in points
    ap.add_argument("--panel_height", type=float, default=792.0)  # Letter height in points
    args = ap.parse_args()

    nx = (args.x_px - args.panel_left) / args.panel_width
    ny = (args.y_px - args.panel_bottom) / args.panel_height
    print(f"Normalized: x={nx:.4f}, y={ny:.4f}")

if __name__ == "__main__":
    main()
