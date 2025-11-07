
#!/usr/bin/env python3
"""
main_glue.py — Drop-in build entrypoint with --theme switching and annotation modes.

Usage:
  python scripts/main_glue.py --theme dark --assets assets --output output --config config/manual.manifest.json

Notes:
- Uses the "modes" photos page (basic | styled | themed | photo-only) via ANNOTATION_MODE env var.
- Selects the correct theme JSON for annotations based on --theme (dark/light).
- Uses your existing page renderer helpers from scripts/render_pages.py
"""
import os, json, argparse, sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Import your page helpers
from scripts.render_pages import (
    draw_dark_frame, draw_image_box,
    page_cover, page_harness_vector, page_audio_map_table,
    page_can_triggers, page_field_cards, page_legend
)
from scripts.render_pages_modes import page_photos_with_modes

DARK_THEME_JSON  = "templates/theme.sonic.json"
LIGHT_THEME_JSON = "templates/theme.sonic.light.json"

def render_with_modes(pdf_path, manifest, assets_root="assets", theme="dark"):
    c = canvas.Canvas(pdf_path, pagesize=letter)
    pages = manifest.get("pages", [])
    total = len(pages)

    # Choose theme JSON for annotations
    theme_json = DARK_THEME_JSON if theme == "dark" else LIGHT_THEME_JSON

    for i, page in enumerate(pages, start=1):
        pid   = page.get("id", "")
        title = page.get("title", "Page")

        if pid == "cover":
            page_cover(c, manifest.get("title","Sonic Manual"))
        elif pid == "harness":
            page_harness_vector(c, assets_root, i, total)
        elif pid in ("photos", "photos_harness"):
            # Use the advanced, mode-aware photos page
            page_photos_with_modes(
                c,
                assets_root=assets_root,
                annotations_json=os.environ.get("ANNOTATIONS_JSON", "templates/annotations.sonic.json"),
                theme_json=theme_json,
                page_num=i,
                total_pages=total
            )
        elif pid == "audio_map":
            page_audio_map_table(c, assets_root, "tables/speakers.csv", i, total)
        elif pid == "can_triggers":
            page_can_triggers(c, assets_root, i, total)
        elif pid == "cards":
            page_field_cards(c, i, total)
        elif pid == "legend":
            page_legend(c, i, total)
        else:
            # Fallback: empty page with frame
            draw_dark_frame(c, title, i, total)
        c.showPage()
    c.save()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", default="dark", choices=["dark","light"])
    ap.add_argument("--assets", default="assets")
    ap.add_argument("--output", default="output")
    ap.add_argument("--config", default="config/manual.manifest.json")
    args = ap.parse_args()

    # Make sure dirs exist
    Path(args.output).mkdir(parents=True, exist_ok=True)

    # Load manifest
    with open(args.config, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Apply frame patch for light theme
    from scripts.main_glue_light_patch import patch_frame_for_theme
    patch_frame_for_theme(args.theme)

    # Apply watermark patch (controlled by env vars)
    from scripts.main_glue_watermark_patch import patch_watermark
    patch_watermark(
        text=os.getenv("WM_TEXT", "LTZ RR2 GRZ"),
        mode=os.getenv("WM_MODE", "footer"),
        opacity=float(os.getenv("WM_OPACITY", "0.55")),
        footer_pos=os.getenv("WM_FOOTER_POS", "right")
    )

    out_pdf = Path(args.output) / "sonic_manual_dark.pdf"
    if args.theme == "light":
        out_pdf = Path(args.output) / "sonic_manual_light.pdf"

    render_with_modes(str(out_pdf), manifest, assets_root=args.assets, theme=args.theme)
    print(f"[main_glue] wrote {out_pdf}")

if __name__ == "__main__":
    main()
