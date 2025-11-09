
"""
Wrapper renderer that applies theme to annotations before drawing.
Depends on v2 styled drawer: draw_annotations_styled(...)
"""
import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from scripts.render_pages_annotations_patch_v2 import draw_annotations_styled
from scripts.annotation_theme import apply_theme, load_theme

def page_photos_annotated_themed(c, assets_root, annotations_json, theme_json, page_num, total_pages):
    # Outer frame is handled by your existing draw_dark_frame
    draw_dark_frame(c, "Annotated Harness Photos", page_num, total_pages)
    W,H = letter
    margin = 0.8*inch
    box_w = W - 2*margin
    box_h = (H - 2*margin) * 0.40

    p1 = Path(assets_root) / "pinout_harness_closeup.jpg"
    p2 = Path(assets_root) / "rr2_gm2_primary_photo.jpg"
    draw_image_box(c, str(p1), margin, H - margin - box_h, box_w, box_h)
    draw_image_box(c, str(p2), margin, margin, box_w, box_h)

    if annotations_json and Path(annotations_json).exists():
        with open(annotations_json, "r", encoding="utf-8") as f:
            ann = json.load(f)
    else:
        ann = {"annotations": []}

    if theme_json and Path(theme_json).exists():
        theme = load_theme(theme_json)
        ann = apply_theme(ann, theme)

    draw_annotations_styled(c, ann, margin, W, H)
