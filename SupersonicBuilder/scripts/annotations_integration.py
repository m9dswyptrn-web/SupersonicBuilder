#!/usr/bin/env python3
"""
Sonic Builder - Annotations Integration Module
==============================================
Provides three levels of annotation rendering:
1. Basic: Simple arrows, boxes, and labels
2. Styled: Per-annotation custom colors and sizes
3. Themed: Automatic styling based on label keywords

Usage in main.py or other rendering scripts:
    from scripts.annotations_integration import draw_annotations_on_page
    
    # In your page rendering function:
    draw_annotations_on_page(
        canvas_obj=c,
        annotations_json="templates/annotations.sonic.json",
        theme_json="templates/theme.sonic.json",  # optional
        page_width=W,
        page_height=H,
        margin=0.8*inch,
        mode="themed"  # "basic", "styled", or "themed"
    )
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# Import annotation renderers
from scripts.render_pages_annotations_patch import draw_annotations as draw_annotations_basic
from scripts.render_pages_annotations_patch_v2 import draw_annotations_styled
from scripts.annotation_theme import apply_theme, load_theme


def draw_annotations_on_page(
    canvas_obj,
    annotations_json: str,
    page_width: float,
    page_height: float,
    margin: float = 0.8 * inch,
    theme_json: Optional[str] = None,
    mode: str = "themed",
    default_accent: tuple = (0.95, 0.65, 0.20)
):
    """
    Draw annotations on a canvas page.
    
    Args:
        canvas_obj: ReportLab canvas object
        annotations_json: Path to annotations JSON file
        page_width: Page width in points
        page_height: Page height in points
        margin: Margin size in points (default 0.8 inch)
        theme_json: Path to theme JSON file (optional, for themed mode)
        mode: Rendering mode - "basic", "styled", or "themed" (default)
        default_accent: Default accent color as RGB tuple (0-1 range)
    
    Returns:
        bool: True if annotations were drawn, False otherwise
    """
    # Load annotations
    if not annotations_json or not Path(annotations_json).exists():
        return False
    
    with open(annotations_json, "r", encoding="utf-8") as f:
        ann_data = json.load(f)
    
    # Apply theming if requested and theme file exists
    if mode == "themed" and theme_json and Path(theme_json).exists():
        theme = load_theme(theme_json)
        ann_data = apply_theme(ann_data, theme)
    
    # Draw using appropriate renderer
    if mode == "basic":
        draw_annotations_basic(canvas_obj, ann_data, margin, page_width, page_height)
    else:  # styled or themed (both use styled renderer)
        draw_annotations_styled(canvas_obj, ann_data, margin, page_width, page_height, default_accent)
    
    return True


def render_annotated_photo_page(
    canvas_obj,
    page_title: str,
    photo_paths: list,
    annotations_json: str,
    theme_json: Optional[str] = None,
    page_num: int = 1,
    total_pages: int = 1,
    dark_mode: bool = True,
    margin: float = 0.8 * inch
):
    """
    Render a complete annotated photo page with frame, photos, and annotations.
    
    Args:
        canvas_obj: ReportLab canvas object
        page_title: Title for the page header
        photo_paths: List of 1-2 photo file paths to display
        annotations_json: Path to annotations JSON file
        theme_json: Path to theme JSON file (optional)
        page_num: Current page number
        total_pages: Total number of pages
        dark_mode: Use dark theme (default True)
        margin: Page margin in points
    
    Example:
        render_annotated_photo_page(
            c,
            "Harness Connections",
            ["assets/photo1.jpg", "assets/photo2.jpg"],
            "templates/annotations.sonic.json",
            theme_json="templates/theme.sonic.json",
            page_num=5,
            total_pages=15
        )
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader
    from reportlab.lib import colors
    
    W, H = letter
    
    # Draw page frame (dark or light)
    bg_color = colors.HexColor("#1c1c1e") if dark_mode else colors.white
    text_color = colors.white if dark_mode else colors.black
    accent_color = colors.HexColor("#f2a527")
    
    canvas_obj.setFillColor(bg_color)
    canvas_obj.rect(0, 0, W, H, fill=1, stroke=0)
    
    # Header
    canvas_obj.setStrokeColor(accent_color)
    canvas_obj.setLineWidth(2)
    canvas_obj.line(margin, H - margin + 10, W - margin, H - margin + 10)
    
    canvas_obj.setFillColor(text_color)
    canvas_obj.setFont("Helvetica-Bold", 14)
    canvas_obj.drawString(margin, H - margin + 20, page_title)
    
    # Footer with page number
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.drawRightString(W - margin, margin - 20, f"Page {page_num} of {total_pages}")
    
    # Calculate photo layout
    content_h = H - 2 * margin - 40
    
    if len(photo_paths) == 1:
        # Single photo - full width
        box_w = W - 2 * margin
        box_h = content_h
        _draw_photo_box(canvas_obj, photo_paths[0], margin, margin + 20, box_w, box_h)
    elif len(photo_paths) == 2:
        # Two photos - top and bottom
        box_w = W - 2 * margin
        box_h = content_h * 0.45
        gap = content_h * 0.10
        
        _draw_photo_box(canvas_obj, photo_paths[0], margin, H - margin - box_h, box_w, box_h)
        _draw_photo_box(canvas_obj, photo_paths[1], margin, margin + 20, box_w, box_h)
    
    # Draw annotations
    draw_annotations_on_page(
        canvas_obj,
        annotations_json,
        W, H,
        margin=margin,
        theme_json=theme_json,
        mode="themed"
    )


def _draw_photo_box(canvas_obj, photo_path: str, x: float, y: float, w: float, h: float):
    """Helper to draw a photo in a box with aspect-ratio fitting."""
    from reportlab.lib.utils import ImageReader
    from PIL import Image, ImageOps
    
    try:
        if not Path(photo_path).exists():
            # Draw placeholder box
            canvas_obj.setStrokeColorRGB(0.3, 0.3, 0.3)
            canvas_obj.setLineWidth(1)
            canvas_obj.rect(x, y, w, h, fill=0, stroke=1)
            return
        
        img = Image.open(photo_path)
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass
        
        img_reader = ImageReader(img)
        iw, ih = img_reader.getSize()
        img_aspect = iw / ih
        box_aspect = (w / h) if h else img_aspect
        
        if img_aspect > box_aspect:
            tw = w
            th = w / img_aspect
        else:
            th = h
            tw = h * img_aspect
        
        dx = x + (w - tw) / 2.0
        dy = y + (h - th) / 2.0
        canvas_obj.drawImage(img_reader, dx, dy, width=tw, height=th, mask='auto')
    except Exception as e:
        # Draw error placeholder
        canvas_obj.setStrokeColorRGB(0.8, 0.3, 0.3)
        canvas_obj.setLineWidth(1)
        canvas_obj.rect(x, y, w, h, fill=0, stroke=1)


# Convenience functions for quick integration

def get_annotation_examples():
    """Return example annotation structures for documentation."""
    return {
        "basic": {
            "annotations": [
                {"type": "label", "x": 0.5, "y": 0.5, "label": "Connection Point"},
                {"type": "box", "x": 0.2, "y": 0.7, "w": 150, "h": 25, "label": "Power Input"},
                {
                    "type": "arrow",
                    "from_x": 0.3, "from_y": 0.4,
                    "to_x": 0.5, "to_y": 0.6,
                    "label": "Signal Flow"
                }
            ]
        },
        "styled": {
            "annotations": [
                {
                    "type": "arrow",
                    "from_x": 0.2, "from_y": 0.5,
                    "to_x": 0.4, "to_y": 0.7,
                    "label": "GMLAN Bus",
                    "arrow_color": "#34c759",
                    "line_width": 1.6,
                    "font_size": 10
                },
                {
                    "type": "box",
                    "x": 0.6, "y": 0.3,
                    "w": 180, "h": 24,
                    "label": "Ground Point",
                    "box_stroke": "#8e8e93",
                    "box_fill": "#00000099",
                    "text_color": "#ffffff"
                }
            ]
        }
    }


if __name__ == "__main__":
    print("Sonic Builder - Annotations Integration Module")
    print("=" * 50)
    print("\nThis module provides annotation rendering capabilities.")
    print("\nExample usage:")
    print("""
    from scripts.annotations_integration import draw_annotations_on_page
    
    # In your PDF rendering code:
    draw_annotations_on_page(
        canvas_obj=c,
        annotations_json="templates/annotations.sonic.json",
        theme_json="templates/theme.sonic.json",
        page_width=612,
        page_height=792,
        margin=0.8*inch,
        mode="themed"
    )
    """)
