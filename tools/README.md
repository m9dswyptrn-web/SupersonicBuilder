# SonicBuilder Tools

This directory contains specialized toolkits for PDF composition and image generation.

---

## 📦 Tool Suites

### 1. `pdf_composer/` - PDF Composition Tools

Professional PDF manipulation and assembly tools for dark-themed manuals.

**Available Tools:**
- `compose_images_to_pdf.py` - Compose multiple images into a single PDF
- `pdf_stamp_metadata.py` - Stamp title, author, subject, keywords into PDF metadata
- `pdf_two_up.py` - Create two-up layouts (rasterized for reliability)
- `pdf_appendix_index_dark.py` - Generate dark-themed appendix index pages with QR codes
- `pdf_footer_stamp_dark.py` - Add dark footers with custom text
- `pdf_watermark_dark.py` - Apply dark watermarks (e.g., "DRAFT")
- `pdf_verify_metadata.py` - Verify PDF metadata correctness

**Example Workflow:**
```bash
# 1. Compose images to PDF
python tools/pdf_composer/compose_images_to_pdf.py \
  --in imgs/*.png --out out/manual.pdf --page Letter --margin 24

# 2. Stamp metadata
python tools/pdf_composer/pdf_stamp_metadata.py \
  --in out/manual.pdf --out out/manual.meta.pdf \
  --title "SonicBuilder v2.0.9" --author "Christopher Elgin" \
  --subject "EOENKK + Maestro RR2" --keywords "Sonic, EOENKK, Maestro RR2"

# 3. Create two-up
python tools/pdf_composer/pdf_two_up.py \
  --in out/manual.meta.pdf --out out/manual.two-up.pdf --rasterize

# 4. Add appendix index
python tools/pdf_composer/pdf_appendix_index_dark.py \
  --index-out out/appendix_index.png \
  --entries "GM 44-pin Main:112:gm44pin.pdf" "Rear Cam Power:118:rear_cam_power.pdf" \
  --qr-prefix "https://github.com/m9dswyptrn-web/SonicBuilder/releases/latest/download/"

# 5. Add footer
python tools/pdf_composer/pdf_footer_stamp_dark.py \
  --in out/manual.two-up.pdf --out out/manual.footer.pdf \
  --left "SonicBuilder • CERT #0001" --center "v2.0.9" --right "© 2025"

# 6. Add watermark (optional)
python tools/pdf_composer/pdf_watermark_dark.py \
  --in out/manual.footer.pdf --out out/manual.watermark.pdf --text "DRAFT"

# 7. Verify
python tools/pdf_composer/pdf_verify_metadata.py --in out/manual.watermark.pdf
```

---

### 2. `image_suite/` - Image Generation Suite

Generate professional graphics for manuals, field cards, and documentation.

**Available Generators (45+ scripts):**

#### **Headers & Covers**
- `generate_cover.py` - Main cover page
- `generate_titlepage.py` - Title page
- `header_strip.py` - Header strips
- `footer_strip.py` - Footer strips

#### **Information Cards**
- `generate_parts_table_image.py` - Parts table graphics
- `generate_qr_label.py` - QR code labels
- `fieldcard_grid.py` - Field card grid layouts
- `two_up_cards.py` - Two-up card layouts
- `three_up_cards.py` - Three-up card layouts

#### **Callouts & Notices**
- `callout_tip.py` - Tip callouts
- `callout_warn.py` - Warning callouts
- `callout_danger.py` - Danger callouts

#### **Chapter Elements**
- `chapter_opener.py` - Chapter opening pages
- `divider_page.py` - Section dividers
- `section_label.py` - Section labels
- `figure_label.py` - Figure labels
- `appendix_tab.py` - Appendix tabs
- `toc_card.py` - Table of contents cards

#### **Technical Blocks**
- `spec_block.py` - Specification blocks
- `pinout_block.py` - Pinout diagrams
- `connector_block.py` - Connector blocks

#### **System-Specific Labels**
- `camera_overlay_label.py` - Camera labels
- `canbus_label.py` - CAN bus labels
- `power_label.py` - Power labels
- `audio_label.py` - Audio labels
- `testing_label.py` - Testing labels
- `programming_label.py` - Programming labels
- `wiring_label.py` - Wiring labels

#### **Utility Elements**
- `legend_key.py` - Legend keys
- `note_card.py` - Note cards
- `step_card.py` - Step cards
- `result_card.py` - Result cards
- `success_badge.py` - Success badges
- `warning_badge.py` - Warning badges
- `error_badge.py` - Error badges
- `watermark_card.py` - Watermark cards
- `qr_frame_label.py` - QR frame labels
- `photo_frame.py` - Photo frames
- `diagram_canvas.py` - Diagram canvases

#### **Layouts**
- `grid_4x4.py` - 4x4 grid layouts
- `demo_gallery.py` - Demo gallery generator

**Example Usage:**
```bash
# Generate cover
python tools/image_suite/generate_cover.py \
  --title "Chevy Sonic LTZ" \
  --subtitle "Android 15 EOENKK + Maestro RR2" \
  --out out/cover.png

# Generate parts table
python tools/image_suite/generate_parts_table_image.py \
  --items "ADS-MRR2,HRN-RR-GM5,EOENKK HU,USB DAC,SPDIF TX" \
  --out out/parts.png

# Generate QR label
python tools/image_suite/generate_qr_label.py \
  --text "https://github.com/m9dswyptrn-web/SonicBuilder" \
  --label "Repo" \
  --out out/qr_repo.png

# Run demo gallery (generates all examples)
python tools/image_suite/demo_gallery.py
```

---

## 🚀 Integration with Main Build

These tools complement the main SonicBuilder system:

**Main System (`scripts/`):**
- `builder.py` - Core PDF builder (ReportLab-based)
- Processes YAML + Markdown → Full manual
- Integrated with CI/CD

**Tool Suites (`tools/`):**
- **PDF Composer** - Post-processing & assembly
- **Image Suite** - Asset generation
- Standalone utilities for custom workflows

**Workflow:**
```
Main Build (scripts/builder.py)
    ↓
Generate base manual PDF
    ↓
PDF Composer Tools
    ↓
Two-up, metadata, footers, watermarks
    ↓
Final release PDFs
```

---

## 📋 Requirements

Both tool suites require minimal dependencies:

```bash
# Install dependencies
pip install reportlab pypdf pillow qrcode pdf2image

# Or use main requirements.txt
pip install -r requirements.txt
```

---

## 🎯 Use Cases

### Standalone Manual Creation
Use PDF Composer to build manuals from raw images without the main SonicBuilder system.

### Custom Asset Generation
Use ImageSuite to generate branded graphics for any documentation project.

### Post-Processing Pipeline
Enhance SonicBuilder output with additional metadata, watermarks, and formatting.

### Field Card Production
Generate printable field cards for installers using the card layout tools.

---

## 🔗 Related Documentation

- [Main README](../README.md) - SonicBuilder overview
- [PR Automation](../docs/PR_AUTOMATION.md) - CI/CD workflows
- [Release Automation](../docs/RELEASE_AUTOMATION.md) - Release process

---

**Professional PDF tooling for automotive documentation** 🚗📄
