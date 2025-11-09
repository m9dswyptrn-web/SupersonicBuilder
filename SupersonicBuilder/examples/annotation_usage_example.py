#!/usr/bin/env python3
"""
Example: How to use annotations in your Sonic manual builder
=============================================================

This file shows three ways to use the annotation system:
1. Basic annotations (simple rendering)
2. Styled annotations (custom colors per annotation)
3. Themed annotations (automatic styling based on keywords)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from scripts.annotations_integration import (
    draw_annotations_on_page,
    render_annotated_photo_page
)

def example_1_basic_usage():
    """Example 1: Simple annotation drawing on existing page"""
    c = canvas.Canvas("output/example_basic_annotations.pdf", pagesize=letter)
    W, H = letter
    
    # Your existing page content here...
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 700, "My Manual Page with Annotations")
    
    # Add annotations (basic mode)
    draw_annotations_on_page(
        canvas_obj=c,
        annotations_json="templates/annotations.sonic.json",
        page_width=W,
        page_height=H,
        margin=0.8*inch,
        mode="basic"  # Simple rendering
    )
    
    c.showPage()
    c.save()
    print("✅ Created: output/example_basic_annotations.pdf")


def example_2_styled_usage():
    """Example 2: Styled annotations with custom colors"""
    c = canvas.Canvas("output/example_styled_annotations.pdf", pagesize=letter)
    W, H = letter
    
    # Your page content...
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 700, "Styled Annotations Example")
    
    # Add annotations with custom styling
    draw_annotations_on_page(
        canvas_obj=c,
        annotations_json="templates/annotations.sonic.styled.json",
        page_width=W,
        page_height=H,
        margin=0.8*inch,
        mode="styled"  # Respects per-annotation colors
    )
    
    c.showPage()
    c.save()
    print("✅ Created: output/example_styled_annotations.pdf")


def example_3_themed_usage():
    """Example 3: Automatic theming based on label keywords"""
    c = canvas.Canvas("output/example_themed_annotations.pdf", pagesize=letter)
    W, H = letter
    
    # Your page content...
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 700, "Auto-Themed Annotations")
    
    # Add annotations with automatic theming
    # Labels containing "power" → red, "ground" → gray, "gmlan" → green, etc.
    draw_annotations_on_page(
        canvas_obj=c,
        annotations_json="templates/annotations.sonic.json",
        theme_json="templates/theme.sonic.json",
        page_width=W,
        page_height=H,
        margin=0.8*inch,
        mode="themed"  # Auto-apply colors based on keywords
    )
    
    c.showPage()
    c.save()
    print("✅ Created: output/example_themed_annotations.pdf")


def example_4_full_page():
    """Example 4: Complete annotated photo page"""
    c = canvas.Canvas("output/example_full_page.pdf", pagesize=letter)
    
    # Render a complete annotated page with photos and annotations
    render_annotated_photo_page(
        canvas_obj=c,
        page_title="Harness Connections - Annotated",
        photo_paths=[
            "assets/pinout_harness_closeup.jpg",
            "assets/rr2_gm2_primary_photo.jpg"
        ],
        annotations_json="templates/annotations.sonic.json",
        theme_json="templates/theme.sonic.json",
        page_num=5,
        total_pages=15,
        dark_mode=True
    )
    
    c.showPage()
    c.save()
    print("✅ Created: output/example_full_page.pdf")


if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    
    print("🎨 Annotation System Examples")
    print("=" * 50)
    
    example_1_basic_usage()
    example_2_styled_usage()
    example_3_themed_usage()
    example_4_full_page()
    
    print("\n✅ All examples created in output/")
    print("\nNext steps:")
    print("1. Check the generated PDFs in output/")
    print("2. Edit templates/annotations.sonic.json to customize")
    print("3. Modify templates/theme.sonic.json for different color schemes")
    print("4. Integrate into your main.py build process")
