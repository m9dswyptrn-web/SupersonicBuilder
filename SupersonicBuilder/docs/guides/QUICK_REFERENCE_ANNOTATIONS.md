# Annotations Quick Reference

**One-page cheat sheet for the Sonic Builder Annotation System**

---

## 🚀 Quick Start (30 seconds)

```bash
# 1. Generate examples
make examples

# 2. View the PDFs
ls -lh output/example*.pdf

# 3. Read the guide
cat ANNOTATIONS_GUIDE.md
```

---

## 📋 3 Annotation Types

### 1. Label (Simple Text)
```json
{"type": "label", "x": 0.5, "y": 0.5, "label": "Point A"}
```

### 2. Box (Rectangle with Text)
```json
{"type": "box", "x": 0.2, "y": 0.7, "w": 150, "h": 25, "label": "Input"}
```

### 3. Arrow (Directional Line)
```json
{"type": "arrow", "from_x": 0.3, "from_y": 0.4, "to_x": 0.5, "to_y": 0.6, "label": "Flow"}
```

**Coordinates**: 0.0-1.0 range, origin = bottom-left

---

## 🎨 3 Rendering Modes

### Basic (Default Colors)
```python
draw_annotations_on_page(c, "annotations.json", W, H, mode="basic")
```

### Styled (Custom Colors)
```python
draw_annotations_on_page(c, "annotations.json", W, H, mode="styled")
```

### Themed (Auto-Color by Keywords)
```python
draw_annotations_on_page(c, "annotations.json", W, H, 
    theme_json="theme.json", mode="themed")
```

---

## 🌈 Auto-Theming Colors

| Keyword | Color | Hex |
|---------|-------|-----|
| Power/12V | 🔴 Red | `#ff3b30` |
| Ground/GND | ⚪ Gray | `#8e8e93` |
| GMLAN/CAN | 🟢 Green | `#34c759` |
| RCA | 🔵 Blue | `#0a84ff` |
| Reverse | 🟡 Yellow | `#ffd60a` |
| Trigger | 🟠 Orange | `#ff9f0a` |

---

## 🛠️ Helper Tools

### Coordinate Converter
```bash
python scripts/annotation_coords_helper.py --x_px 400 --y_px 500
# → x=0.6531, y=0.6313
```

### Make Commands
```bash
make examples          # Generate 4 example PDFs
make help_annotations  # Show annotation help
make annotations_demo  # Full demonstration
```

---

## 📁 Key Files

```
templates/
├── annotations.sonic.json         # Basic annotations
├── annotations.sonic.styled.json  # With custom styling
└── theme.sonic.json               # Auto-theming rules

scripts/
├── annotations_integration.py     # Main module (use this!)
└── annotation_coords_helper.py    # Coordinate converter

examples/
└── annotation_usage_example.py    # Working code examples
```

---

## 💻 Integration Code

### Method 1: Add to Existing Page
```python
from scripts.annotations_integration import draw_annotations_on_page
from reportlab.lib.units import inch

# In your page render function:
draw_annotations_on_page(
    canvas_obj=c,
    annotations_json="templates/annotations.sonic.json",
    page_width=W,
    page_height=H,
    margin=0.8*inch,
    theme_json="templates/theme.sonic.json",
    mode="themed"
)
```

### Method 2: Full Page Renderer
```python
from scripts.annotations_integration import render_annotated_photo_page

render_annotated_photo_page(
    c, "Title", ["photo1.jpg", "photo2.jpg"],
    "annotations.json", "theme.json", page_num=1, total_pages=10
)
```

---

## 🎯 Common Tasks

### Create New Annotation
1. Find pixel coords from grid overlay image
2. Convert: `python scripts/annotation_coords_helper.py --x_px 350 --y_px 420`
3. Add to `templates/annotations.sonic.json`:
   ```json
   {"type": "arrow", "from_x": 0.52, "from_y": 0.61, "to_x": 0.55, "to_y": 0.70, "label": "New"}
   ```
4. Test: `make examples`

### Custom Styling
```json
{
  "type": "box",
  "x": 0.5, "y": 0.5, "w": 180, "h": 24,
  "label": "Custom",
  "box_stroke": "#3b82f6",
  "box_fill": "#1e3a8a99",
  "text_color": "#ffffff",
  "font_size": 11,
  "line_width": 1.6
}
```

### Add Theme Rule
Edit `templates/theme.sonic.json`:
```json
{
  "priority": ["mytype", ...],
  "rules": {
    "mytype": {
      "any": ["keyword1", "keyword2"],
      "arrow_color": "#ff0000",
      "box_stroke": "#ff0000"
    }
  }
}
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Annotations not visible | Check JSON syntax: `python -m json.tool file.json` |
| Wrong position | Use grid overlays + coordinate helper |
| Colors not applied | Ensure `mode="themed"` and theme file exists |
| Import error | Run from project root: `cd /path/to/project` |

---

## 📖 Full Documentation

**Complete guide**: `ANNOTATIONS_GUIDE.md` (400+ lines)

**Examples**: `python3 examples/annotation_usage_example.py`

**Support**: Check examples first, then read guide

---

## ✨ Pro Tips

1. **Use normalized coords** (0-1) for portability
2. **Test on grid overlays** before finalizing
3. **Use theming** for consistency
4. **Keep labels short** to avoid overflow
5. **Version control** your annotation files

---

**Need more help?** Read `ANNOTATIONS_GUIDE.md` for comprehensive documentation.

**Ready to annotate!** 🎨 v2.0.4
