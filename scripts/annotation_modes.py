
import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from scripts.render_pages_annotations_patch_v2 import draw_annotations_styled
from scripts.annotation_theme import apply_theme, load_theme
from scripts.render_pages import draw_dark_frame, draw_image_box

def load_json(path: str):
    if not path or not Path(path).exists():
        return {"annotations": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _basic_to_styled(ann_obj):
    out = {"annotations": []}
    for a in ann_obj.get("annotations", []):
        if a.get("type") in ("box","arrow","label"):
            out["annotations"].append(a)
        else:
            out["annotations"].append({"type":"label", **a})
    return out

def render_photos_page_by_mode(c, title, assets_root, annotations_json, mode="themed", theme_json=None, page_num=1, total_pages=1):
    draw_dark_frame(c, title, page_num, total_pages)
    W,H = letter
    margin = 0.8*inch
    box_w = W - 2*margin
    box_h = (H - 2*margin) * 0.40

    from pathlib import Path as _P
    p1 = _P(assets_root) / "pinout_harness_closeup.jpg"
    p2 = _P(assets_root) / "rr2_gm2_primary_photo.jpg"
    draw_image_box(c, str(p1), margin, H - margin - box_h, box_w, box_h)
    draw_image_box(c, str(p2), margin, margin, box_w, box_h)

    if mode == "photo-only":
        return

    ann = load_json(annotations_json)
    ann = _basic_to_styled(ann)

    if mode == "themed":
        theme = load_theme(theme_json) if theme_json else None
        if theme:
            ann = apply_theme(ann, theme)

    draw_annotations_styled(c, ann, margin, W, H)
