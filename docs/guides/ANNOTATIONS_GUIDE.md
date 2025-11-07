# Sonic Builder - Annotations System Guide

Complete guide to using the advanced annotation system in your Sonic manual builder.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Annotation Types](#annotation-types)
- [Rendering Modes](#rendering-modes)
- [Theme System](#theme-system)
- [Integration Guide](#integration-guide)
- [Examples](#examples)

---

## Overview

The annotation system provides three levels of sophistication:

1. **Basic** - Simple arrows, boxes, and labels
2. **Styled** - Per-annotation custom colors and sizes
3. **Themed** - Automatic styling based on label keywords

### Key Files

```
scripts/
├── annotations_integration.py           # Main integration module
├── render_pages_annotations_patch.py    # Basic renderer
├── render_pages_annotations_patch_v2.py # Styled renderer
├── render_pages_annotations_themed.py   # Themed renderer
└── annotation_theme.py                  # Theme engine

templates/
├── annotations.sonic.json               # Basic annotations
├── annotations.sonic.styled.json        # Styled annotations
└── theme.sonic.json                     # Theme rules

examples/
└── annotation_usage_example.py          # Usage examples
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.extras.txt
```

### 2. Basic Usage

```python
from scripts.annotations_integration import draw_annotations_on_page
from reportlab.lib.units import inch

# In your PDF rendering code:
draw_annotations_on_page(
    canvas_obj=c,
    annotations_json="templates/annotations.sonic.json",
    page_width=612,
    page_height=792,
    margin=0.8*inch,
    mode="basic"
)
```

### 3. Test Examples

```bash
python3 examples/annotation_usage_example.py
# Creates 4 example PDFs in output/
```

---

## Annotation Types

### Label (Simple Text Point)

```json
{
  "type": "label",
  "x": 0.5,
  "y": 0.5,
  "label": "Connection Point"
}
```

**Coordinates**: Normalized 0.0-1.0 (0,0 = bottom-left, 1,1 = top-right)

### Box (Rounded Rectangle with Text)

```json
{
  "type": "box",
  "x": 0.2,
  "y": 0.7,
  "w": 150,
  "h": 25,
  "label": "Power Input"
}
```

**Properties**:
- `x`, `y`: Bottom-left corner (normalized 0-1)
- `w`, `h`: Width and height in points
- `label`: Text to display inside box

### Arrow (Directional Leader Line)

```json
{
  "type": "arrow",
  "from_x": 0.3,
  "from_y": 0.4,
  "to_x": 0.5,
  "to_y": 0.6,
  "label": "Signal Flow"
}
```

**Properties**:
- `from_x`, `from_y`: Arrow tail position (normalized 0-1)
- `to_x`, `to_y`: Arrow head position (normalized 0-1)
- `label`: Text near arrow head

---

## Rendering Modes

### Basic Mode

Simple rendering with default colors:

```python
draw_annotations_on_page(
    canvas_obj=c,
    annotations_json="templates/annotations.sonic.json",
    page_width=W,
    page_height=H,
    mode="basic"
)
```

**Default Colors**:
- Accent: Warm gold/orange (0.95, 0.65, 0.20)
- Text: White (1, 1, 1)
- Box fill: Semi-transparent black

### Styled Mode

Per-annotation custom styling:

```json
{
  "type": "arrow",
  "from_x": 0.2,
  "from_y": 0.5,
  "to_x": 0.4,
  "to_y": 0.7,
  "label": "GMLAN Bus",
  "arrow_color": "#34c759",
  "line_width": 1.6,
  "font_size": 10,
  "text_color": "#ffffff"
}
```

**Styling Options**:
- `arrow_color`, `box_stroke`, `text_color`: Hex "#RRGGBB" or RGB array [0-1]
- `box_fill`: Hex with alpha "#RRGGBBAA" or RGBA array
- `line_width`: Float (default 1.2)
- `font_size`: Integer (default 9)
- `label_dx`, `label_dy`: Label offset from arrow tip
- `arrow_size`: Arrowhead size in points
- `w`, `h`: Box dimensions

### Themed Mode

Automatic styling based on label keywords:

```python
draw_annotations_on_page(
    canvas_obj=c,
    annotations_json="templates/annotations.sonic.json",
    theme_json="templates/theme.sonic.json",
    page_width=W,
    page_height=H,
    mode="themed"
)
```

**Auto-Applied Colors** (from theme.sonic.json):
- **Power** (12V, B+): Red `#ff3b30`
- **Ground** (GND, chassis): Gray `#8e8e93`
- **GMLAN** (CAN): Green `#34c759`
- **RCA** (line-level): Blue `#0a84ff`
- **Mic** (microphone): Light gray `#d1d1d6`
- **Reverse**: Yellow `#ffd60a`
- **Camera**: Yellow `#ffd60a`
- **Trigger**: Orange `#ff9f0a`

---

## Theme System

### Theme File Structure

`templates/theme.sonic.json`:

```json
{
  "priority": ["power", "ground", "gmlan", "rca"],
  "rules": {
    "power": {
      "any": ["power", "12v", "b+"],
      "arrow_color": "#ff3b30",
      "box_stroke": "#ff3b30"
    },
    "ground": {
      "any": ["ground", "gnd", "chassis"],
      "arrow_color": "#8e8e93"
    }
  },
  "defaults": {
    "arrow_color": "#f2a527",
    "box_stroke": "#f2a527",
    "box_fill": "#00000099",
    "text_color": "#ffffff",
    "line_width": 1.2,
    "font_size": 9
  }
}
```

### Rule Matching

**Keyword Matching**:
- `"any"`: Match if ANY keyword is in label (case-insensitive)
- `"all"`: Match if ALL keywords are in label
- `"none"`: Match if NONE of the keywords are in label

**Priority**: First matching rule in `priority` list wins

**Example**:
- Label: "GMLAN Low (Green)" → Matches `"gmlan"` rule → Green color
- Label: "+12V Battery" → Matches `"power"` rule → Red color
- Label: "Star Ground Node" → Matches `"ground"` rule → Gray color

### Creating Custom Themes

1. Copy `templates/theme.sonic.json`
2. Modify `rules` for your project
3. Adjust `defaults` for fallback styling
4. Use in your build:

```python
draw_annotations_on_page(
    c, "my_annotations.json",
    W, H,
    theme_json="my_custom_theme.json",
    mode="themed"
)
```

---

## Integration Guide

### Method 1: Direct Integration

Add to your existing page rendering function:

```python
def render_my_page(c, page_num, total_pages):
    # Your existing page content
    draw_header(c, "My Page Title")
    draw_photo(c, "assets/photo.jpg")
    
    # Add annotations
    from scripts.annotations_integration import draw_annotations_on_page
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    
    W, H = letter
    draw_annotations_on_page(
        c, "templates/annotations.sonic.json",
        W, H,
        margin=0.8*inch,
        theme_json="templates/theme.sonic.json",
        mode="themed"
    )
```

### Method 2: Full Page Renderer

Use the complete page renderer:

```python
from scripts.annotations_integration import render_annotated_photo_page

render_annotated_photo_page(
    canvas_obj=c,
    page_title="Harness Connections",
    photo_paths=["assets/photo1.jpg", "assets/photo2.jpg"],
    annotations_json="templates/annotations.sonic.json",
    theme_json="templates/theme.sonic.json",
    page_num=5,
    total_pages=15,
    dark_mode=True
)
```

### Method 3: Makefile Integration

Add annotation build target to `Makefile`:

```makefile
build_annotated:
	python3 -c "from scripts.annotations_integration import render_annotated_photo_page; \
	            from reportlab.pdfgen import canvas; \
	            c = canvas.Canvas('output/annotated.pdf'); \
	            render_annotated_photo_page(c, 'Photos', ['assets/p1.jpg', 'assets/p2.jpg'], \
	                'templates/annotations.sonic.json', 'templates/theme.sonic.json', 1, 1); \
	            c.save()"
```

---

## Examples

### Example 1: Power Connection

```json
{
  "type": "arrow",
  "from_x": 0.15,
  "from_y": 0.65,
  "to_x": 0.25,
  "to_y": 0.80,
  "label": "+12V Battery to HU"
}
```

**With Theming**: Auto-colored red (matches "power" rule)

### Example 2: GMLAN Bus

```json
{
  "type": "arrow",
  "from_x": 0.18,
  "from_y": 0.62,
  "to_x": 0.11,
  "to_y": 0.80,
  "label": "GMLAN Low (Green) → BCM"
}
```

**With Theming**: Auto-colored green (matches "gmlan" rule)

### Example 3: Ground Point

```json
{
  "type": "box",
  "x": 0.18,
  "y": 0.16,
  "w": 180,
  "h": 22,
  "label": "Trigger/Ground Star Point"
}
```

**With Theming**: Auto-colored gray (matches "ground" rule)

### Example 4: Custom Styled

```json
{
  "type": "box",
  "x": 0.76,
  "y": 0.66,
  "w": 156,
  "h": 22,
  "label": "Custom Component",
  "box_fill": "#1e3a8a99",
  "box_stroke": "#3b82f6",
  "text_color": "#ffffff",
  "font_size": 11
}
```

**Manual Styling**: Overrides theme with custom blue colors

---

## Coordinate Helper

Convert pixel coordinates to normalized values:

```bash
python scripts/annotation_coords_helper.py --x_px 350 --y_px 420
# → Normalized: x=0.5230, y=0.6056
```

**With panel bounds**:

```bash
python scripts/annotation_coords_helper.py \
  --x_px 350 --y_px 420 \
  --panel_left 72 --panel_bottom 72 \
  --panel_width 468 --panel_height 648
```

---

## Build Workflow

### Complete Build Process

```bash
# 1. Edit annotations
vim templates/annotations.sonic.json

# 2. Test with helper
python scripts/annotation_coords_helper.py --x_px 400 --y_px 500

# 3. Run examples
python3 examples/annotation_usage_example.py

# 4. Build manual with annotations
make clean
make build
make post

# 5. Check output
open output/sonic_manual_dark.pdf
```

### Live Development

Use grid overlays for positioning:

1. Open `overlays/*_grid.jpg` images
2. Identify pixel coordinates
3. Convert using helper script
4. Add to annotations JSON
5. Rebuild and verify

---

## Troubleshooting

### Annotations Not Visible

1. Check file paths exist:
   ```bash
   ls -la templates/annotations.sonic.json
   ```

2. Verify JSON syntax:
   ```bash
   python3 -m json.tool templates/annotations.sonic.json
   ```

3. Check coordinates (must be 0-1):
   ```json
   "x": 0.5,  // ✓ Valid
   "x": 350,  // ✗ Invalid (use helper to convert)
   ```

### Colors Not Applied

1. Ensure theme file exists:
   ```bash
   ls -la templates/theme.sonic.json
   ```

2. Check rule matching (case-insensitive):
   ```json
   "label": "GMLAN Bus"  // Matches "gmlan" rule ✓
   "label": "Data Bus"   // No match, uses default ✓
   ```

3. Verify mode is "themed":
   ```python
   mode="themed"  # ✓ Uses theme
   mode="styled"  # ✗ Ignores theme
   ```

### Import Errors

```bash
# Ensure all dependencies installed
pip install -r requirements.extras.txt

# Check Python path
python3 -c "import scripts.annotations_integration; print('✓ OK')"
```

---

## Advanced Usage

### Multiple Annotation Sets

```python
# Render different annotations per page
annotations_map = {
    1: "templates/annotations.page1.json",
    2: "templates/annotations.page2.json",
    3: "templates/annotations.page3.json"
}

for page_num in range(1, 4):
    draw_annotations_on_page(
        c,
        annotations_map[page_num],
        W, H,
        theme_json="templates/theme.sonic.json",
        mode="themed"
    )
    c.showPage()
```

### Dynamic Annotation Generation

```python
import json

# Generate annotations programmatically
annotations = {
    "annotations": [
        {
            "type": "arrow",
            "from_x": 0.2 + i * 0.15,
            "from_y": 0.5,
            "to_x": 0.25 + i * 0.15,
            "to_y": 0.7,
            "label": f"Connection {i+1}"
        }
        for i in range(5)
    ]
}

# Save to temp file
with open("temp_annotations.json", "w") as f:
    json.dump(annotations, f, indent=2)

# Render
draw_annotations_on_page(c, "temp_annotations.json", W, H, mode="basic")
```

---

## Best Practices

1. **Use Normalized Coordinates** (0-1 range) for portability
2. **Test on Grid Overlays** before final positioning
3. **Group Related Annotations** in separate JSON files per page
4. **Use Theming** for consistency across manual
5. **Override Theme** only when necessary for specific highlights
6. **Keep Labels Concise** - Long labels may overflow boxes
7. **Test Both Modes** - Print vs screen display
8. **Version Control** annotation files separately

---

## Reference

### Color Palette (Sonic Default)

```
Power:    #ff3b30 (Red)
Ground:   #8e8e93 (Gray)
GMLAN:    #34c759 (Green)
RCA:      #0a84ff (Blue)
Mic:      #d1d1d6 (Light Gray)
Reverse:  #ffd60a (Yellow)
Camera:   #ffd60a (Yellow)
Trigger:  #ff9f0a (Orange)
Default:  #f2a527 (Warm Gold)
```

### Coordinate System

```
(0,1) ────────────── (1,1)
  │                    │
  │    Page Area       │
  │                    │
(0,0) ────────────── (1,0)
```

Origin: Bottom-left
Units: Normalized (0.0 to 1.0)

---

## Support

For questions or issues:

1. Check `examples/annotation_usage_example.py`
2. Review grid overlays in `overlays/`
3. Test with coordinate helper script
4. Verify JSON syntax with `json.tool`

Happy annotating! 🎨
