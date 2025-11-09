# SuperSonic Manual v2.4.0 - Parts & Tools Generator

## Overview

The **Parts & Tools Generator** creates professional PDF parts lists with **QR codes** for easy supplier sourcing. Scan any QR code with your phone to instantly access the supplier's product page.

---

## Quick Usage

### Generate Parts List

```bash
# Dark theme (screen-optimized)
make parts_tools

# Light theme (print-optimized)
make parts_tools_light
```

**Output:**
- `output/parts_tools_dark.pdf` (2.4 KB)
- `output/parts_tools_light.pdf` (2.4 KB)

---

## Configuration File: `parts_tools.yaml`

### Format

```yaml
sections:
  - title: Head Unit & Integration
    items:
      - name: EOENKK Android 15 DSP Head Unit
        sku: EOENKK-A15-DSP
        url: https://example.com/eoenkk-a15-dsp
        notes: 7" QLED, DSP, LTE, BT 5.4, CarPlay/Android Auto
      
      - name: iDatalink Maestro RR2 + HRN-RR-GM5
        sku: RR2 + HRN-RR-GM5
        url: https://example.com/idatalink-rr2
        notes: GM harness + steering controls + retention

  - title: Cameras
    items:
      - name: DVR Front + Rear Camera Kit
        sku: DVR-360
        url: https://example.com/dvr-360
        notes: Parking monitor, 1080p/60
```

### Fields

- **`title`**: Section heading (e.g., "Power & Wiring", "Tools")
- **`name`**: Part name/description
- **`sku`**: Part number or SKU
- **`url`**: Supplier product URL (converted to QR code)
- **`notes`**: Optional specifications or details (max 90 chars shown)

---

## PDF Layout

### Dark Theme
- Black background
- White text
- High contrast for screen viewing
- QR codes optimized for dark mode

### Light Theme
- White background
- Black text
- Print-optimized
- Standard QR codes

### Page Structure

```
╔════════════════════════════════════════════════════════╗
║  Parts & Tools — QR Sourcing                           ║
║                                                        ║
║  Head Unit & Integration                               ║
║  ┌────────────────────────────────────────┐           ║
║  │ EOENKK Android 15 DSP Head Unit    [QR]│           ║
║  │ SKU: EOENKK-A15-DSP                    │           ║
║  │ 7" QLED, DSP, LTE, BT 5.4, CarPlay...  │           ║
║  └────────────────────────────────────────┘           ║
║  ─────────────────────────────────────────            ║
║                                                        ║
║  Cameras                                               ║
║  ┌────────────────────────────────────────┐           ║
║  │ DVR Front + Rear Camera Kit        [QR]│           ║
║  │ SKU: DVR-360                           │           ║
║  │ Parking monitor, 1080p/60              │           ║
║  └────────────────────────────────────────┘           ║
╚════════════════════════════════════════════════════════╝
```

---

## Use Cases

### For Installers
1. **Scan QR codes** during parts ordering
2. **Print light theme** for shop reference
3. **Share dark theme** via tablet/phone to customers

### For Project Documentation
- Include parts list with installation manual
- Quick reference for replacement parts
- Sourcing documentation for future repairs

### For Budget Planning
- Complete parts inventory with SKUs
- Easy price checking via QR codes
- Notes field shows key specs

---

## Adding New Parts

### Example: Adding a Tool

Edit `parts_tools.yaml`:

```yaml
sections:
  - title: Tools
    items:
      - name: Panel Removal Tool Set
        sku: TOOL-PANEL-KIT
        url: https://example.com/panel-tools
        notes: Nylon trim removal tools, 5-piece set
      
      - name: Wire Stripper/Crimper
        sku: TOOL-WIRE-CRIMP
        url: https://example.com/wire-crimper
        notes: 18-22 AWG, ratcheting crimper
```

Rebuild:

```bash
make parts_tools
make parts_tools_light
```

---

## Features

✅ **QR Code Integration**
- Automatic QR generation from URLs
- Mobile-friendly scanning
- 0.9" × 0.9" QR code size

✅ **Theme Support**
- Dark theme for screens
- Light theme for printing
- Consistent styling with main manual

✅ **Auto-Pagination**
- Handles long parts lists
- Maintains consistent spacing
- Section headers on each page

✅ **Professional Styling**
- Clean layout
- Easy-to-scan format
- Consistent with SuperSonic Manual design

---

## Technical Details

### Dependencies
```bash
pip install -r requirements.txt
```

**Required:**
- reportlab (PDF generation)
- qrcode[pil] (QR code generation)
- PyYAML (YAML parsing)

### Generator Script
- `scripts/gen_parts_tools.py` - Main generator
- Command-line arguments: `--yaml`, `--out`, `--light`
- Default: Dark theme output

### File Size
- Typical parts list: 2-5 KB
- QR codes are vector-based (small file size)
- Scales well with 50+ parts

---

## Two-Up Raster (Optional)

### Purpose
Create two-page-per-sheet print layout from the main manual.

### Requirements
```bash
# System dependency (macOS)
brew install poppler

# System dependency (Linux)
sudo apt-get install poppler-utils

# Python dependency (already in requirements.txt)
pip install pdf2image
```

### Usage
```bash
make build_dark          # Must build manual first
make two_up_raster       # Creates two-up layout
```

**Output:** `output/supersonic_manual_two_up_dark.pdf`

### Notes
- Rasterizes manual at 300 DPI
- Combines 2 pages per Letter sheet
- Useful for compact printing
- **Requires poppler** to be installed on your system

---

## Troubleshooting

### QR Codes Not Generating?
- Check that URLs are valid in YAML
- Ensure `qrcode[pil]` is installed
- Verify YAML syntax is correct

### YAML Parse Error?
- Check indentation (use spaces, not tabs)
- Validate YAML syntax
- Ensure quotes around URLs with special characters

### PDF Not Generated?
```bash
# Check dependencies
pip install -r requirements.txt

# Verify YAML file exists
ls parts_tools.yaml

# Run generator directly
python scripts/gen_parts_tools.py --yaml parts_tools.yaml --out test.pdf
```

---

## Version History

**v2.4.0** (Current)
- Initial Parts & Tools generator
- QR code integration
- Dark & Light themes
- YAML configuration

---

**🛠️ Parts & Tools Generator** - Professional sourcing documentation with QR codes  
**Format:** Letter size (8.5" × 11") | **Themes:** Dark & Light | **Output:** 2-5 KB PDF
