# SonicBuilder Tools Reference

Complete reference for the PDF Composer and ImageSuite toolkits.

---

## 📦 Tool Organization

```
tools/
├── pdf_composer/           # PDF manipulation & assembly
│   ├── compose_images_to_pdf.py
│   ├── pdf_stamp_metadata.py
│   ├── pdf_two_up.py
│   ├── pdf_appendix_index_dark.py
│   ├── pdf_footer_stamp_dark.py
│   ├── pdf_watermark_dark.py
│   └── pdf_verify_metadata.py
│
└── image_suite/            # Image asset generation
    ├── generate_cover.py
    ├── generate_titlepage.py
    ├── generate_parts_table_image.py
    ├── generate_qr_label.py
    └── [40+ more scripts...]
```

---

## 🔧 PDF Composer Tools

### compose_images_to_pdf.py

**Purpose:** Combine multiple images into a single PDF

**Usage:**
```bash
python tools/pdf_composer/compose_images_to_pdf.py \
  --in imgs/*.png \
  --out out/manual.pdf \
  --page Letter \
  --margin 24
```

**Options:**
- `--in` - Input images (glob pattern)
- `--out` - Output PDF file
- `--page` - Page size (Letter, A4, Legal)
- `--margin` - Margin in points (default: 24)

---

### pdf_stamp_metadata.py

**Purpose:** Stamp PDF metadata (title, author, subject, keywords)

**Usage:**
```bash
python tools/pdf_composer/pdf_stamp_metadata.py \
  --in manual.pdf \
  --out manual_stamped.pdf \
  --title "SonicBuilder Manual" \
  --author "Christopher Elgin" \
  --subject "EOENKK + Maestro RR2" \
  --keywords "Sonic,Maestro,EOENKK"
```

**Options:**
- `--in` - Input PDF
- `--out` - Output PDF with metadata
- `--title` - Document title
- `--author` - Author name
- `--subject` - Subject/description
- `--keywords` - Comma-separated keywords

---

### pdf_two_up.py

**Purpose:** Create two-up layout for printing

**Usage:**
```bash
python tools/pdf_composer/pdf_two_up.py \
  --in manual.pdf \
  --out manual_two_up.pdf \
  --rasterize
```

**Options:**
- `--in` - Input PDF
- `--out` - Output two-up PDF
- `--rasterize` - Convert to raster first (bulletproof rendering)

**Note:** Two-up layout places two pages side-by-side for booklet-style printing

---

### pdf_appendix_index_dark.py

**Purpose:** Generate dark-themed appendix index page with QR codes

**Usage:**
```bash
python tools/pdf_composer/pdf_appendix_index_dark.py \
  --index-out appendix_index.png \
  --entries "GM 44-pin:112:gm44pin.pdf" "Rear Cam:118:rear_cam.pdf" \
  --qr-prefix "https://github.com/owner/repo/releases/latest/download/"
```

**Options:**
- `--index-out` - Output PNG image
- `--entries` - List of "Label:Page:Filename" entries
- `--qr-prefix` - URL prefix for QR codes

**Output:** Dark-themed index page with QR codes linking to downloadable PDFs

---

### pdf_footer_stamp_dark.py

**Purpose:** Add dark-themed footers to PDF

**Usage:**
```bash
python tools/pdf_composer/pdf_footer_stamp_dark.py \
  --in manual.pdf \
  --out manual_footer.pdf \
  --left "SonicBuilder • CERT #0001" \
  --center "v2.0.9" \
  --right "© 2025"
```

**Options:**
- `--in` - Input PDF
- `--out` - Output PDF with footers
- `--left` - Left footer text
- `--center` - Center footer text
- `--right` - Right footer text

---

### pdf_watermark_dark.py

**Purpose:** Add dark watermark to PDF

**Usage:**
```bash
python tools/pdf_composer/pdf_watermark_dark.py \
  --in manual.pdf \
  --out manual_watermarked.pdf \
  --text "DRAFT"
```

**Options:**
- `--in` - Input PDF
- `--out` - Output watermarked PDF
- `--text` - Watermark text (e.g., "DRAFT", "CONFIDENTIAL")

---

### pdf_verify_metadata.py

**Purpose:** Verify PDF metadata correctness

**Usage:**
```bash
python tools/pdf_composer/pdf_verify_metadata.py --in manual.pdf
```

**Output:**
```
✅ Title: SonicBuilder Manual
✅ Author: Christopher Elgin
✅ Subject: EOENKK + Maestro RR2
✅ Keywords: Sonic,Maestro,EOENKK
```

---

## 🎨 ImageSuite Tools

### Core Generators

#### generate_cover.py

**Purpose:** Generate professional cover page

**Usage:**
```bash
python tools/image_suite/generate_cover.py \
  --title "Chevy Sonic LTZ" \
  --subtitle "Android 15 EOENKK + Maestro RR2" \
  --out out/cover.png
```

---

#### generate_titlepage.py

**Purpose:** Generate title page

**Usage:**
```bash
python tools/image_suite/generate_titlepage.py \
  --title "Installation Manual" \
  --version "v2.0.9" \
  --out out/titlepage.png
```

---

#### generate_parts_table_image.py

**Purpose:** Generate parts table graphic

**Usage:**
```bash
python tools/image_suite/generate_parts_table_image.py \
  --items "ADS-MRR2,HRN-RR-GM5,EOENKK HU,USB DAC,SPDIF TX" \
  --out out/parts.png
```

---

#### generate_qr_label.py

**Purpose:** Generate QR code labels

**Usage:**
```bash
python tools/image_suite/generate_qr_label.py \
  --text "https://github.com/owner/repo" \
  --label "Repo" \
  --out out/qr_repo.png
```

---

### Callout Tools

- `callout_tip.py` - Blue tip callouts
- `callout_warn.py` - Yellow warning callouts
- `callout_danger.py` - Red danger callouts

**Usage Pattern:**
```bash
python tools/image_suite/callout_tip.py \
  --text "Always disconnect battery before wiring" \
  --out out/tip_battery.png
```

---

### Field Card Tools

- `fieldcard_grid.py` - Grid layouts for field cards
- `two_up_cards.py` - Two-up card layouts
- `three_up_cards.py` - Three-up card layouts

**Usage:**
```bash
python tools/image_suite/fieldcard_grid.py \
  --entries "Step 1:Remove panel,Step 2:Connect harness" \
  --out out/fieldcard.png
```

---

### Chapter Elements

- `chapter_opener.py` - Chapter opening pages
- `divider_page.py` - Section dividers
- `section_label.py` - Section labels
- `figure_label.py` - Figure labels
- `appendix_tab.py` - Appendix tabs

---

### Technical Blocks

- `spec_block.py` - Specification blocks
- `pinout_block.py` - Pinout diagrams
- `connector_block.py` - Connector reference blocks

---

### System-Specific Labels

**Available:**
- `camera_overlay_label.py`
- `canbus_label.py`
- `power_label.py`
- `audio_label.py`
- `testing_label.py`
- `programming_label.py`
- `wiring_label.py`

**Usage Pattern:**
```bash
python tools/image_suite/canbus_label.py \
  --text "GMLAN MS-CAN @ 33.3 kbps" \
  --out out/canbus.png
```

---

### Utility Elements

- `note_card.py` - Note cards
- `step_card.py` - Step instruction cards
- `result_card.py` - Result/outcome cards
- `success_badge.py` - Success badges (green)
- `warning_badge.py` - Warning badges (yellow)
- `error_badge.py` - Error badges (red)
- `watermark_card.py` - Watermark overlays
- `qr_frame_label.py` - QR code frames
- `photo_frame.py` - Photo frames
- `diagram_canvas.py` - Diagram backgrounds

---

### Demo & Testing

#### demo_gallery.py

**Purpose:** Generate all example images in a gallery

**Usage:**
```bash
python tools/image_suite/demo_gallery.py
```

**Output:** Creates `out_gallery/` with examples of all generators

---

## 🔄 Complete Workflow Example

### Professional Manual from Images

```bash
#!/bin/bash
# Complete PDF composition workflow

# 1. Compose base PDF
python tools/pdf_composer/compose_images_to_pdf.py \
  --in imgs/*.png --out build/manual.pdf --page Letter --margin 24

# 2. Stamp metadata
python tools/pdf_composer/pdf_stamp_metadata.py \
  --in build/manual.pdf --out build/manual_meta.pdf \
  --title "SonicBuilder Manual v2.0.9" \
  --author "Christopher Elgin" \
  --subject "2014 Chevy Sonic LTZ EOENKK + Maestro RR2" \
  --keywords "Sonic,Android,EOENKK,Maestro,RR2,Installation"

# 3. Create two-up
python tools/pdf_composer/pdf_two_up.py \
  --in build/manual_meta.pdf --out build/manual_twoup.pdf --rasterize

# 4. Generate appendix index
python tools/pdf_composer/pdf_appendix_index_dark.py \
  --index-out build/appendix_index.png \
  --entries "Wiring Diagrams:15:wiring.pdf" "Pinouts:42:pinouts.pdf" \
  --qr-prefix "https://github.com/m9dswyptrn-web/SonicBuilder/releases/latest/download/"

# 5. Add footer
python tools/pdf_composer/pdf_footer_stamp_dark.py \
  --in build/manual_twoup.pdf --out build/manual_footer.pdf \
  --left "SonicBuilder • Professional Grade" \
  --center "v2.0.9" \
  --right "© 2025 CE"

# 6. Add watermark (optional for drafts)
# python tools/pdf_composer/pdf_watermark_dark.py \
#   --in build/manual_footer.pdf --out build/manual_draft.pdf --text "DRAFT"

# 7. Verify final output
python tools/pdf_composer/pdf_verify_metadata.py --in build/manual_footer.pdf

echo "✅ Manual complete: build/manual_footer.pdf"
```

---

## 📋 Dependencies

```bash
# Core requirements
pip install reportlab pypdf pillow qrcode pdf2image

# Or use main requirements
pip install -r requirements.txt
```

---

## 🎯 Integration Points

### With Main SonicBuilder System

```
Main builder.py output
    ↓
PDF Composer post-processing
    ↓
Two-up, metadata, footers
    ↓
Final release PDFs
```

### Standalone Usage

Tools work independently:
- Generate assets with ImageSuite
- Compose PDFs with PDF Composer
- No dependency on main SonicBuilder system

---

## 🔗 Related Documentation

- [Main Tools README](../tools/README.md) - Overview
- [Build System](../README.md) - Main documentation
- [PR Automation](PR_AUTOMATION.md) - CI/CD workflows

---

**Professional toolkit for automotive documentation** 🚗📄✨
