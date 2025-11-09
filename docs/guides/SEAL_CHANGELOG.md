# SonicBuilder Official Seal - Changelog

## v2.5.0 (2025-10-28) - Initial Release

### Created
- **SonicBuilder Official Seal** graphics package
- Circular badge design with:
  - "SONICBUILDER" top arc text
  - "OFFICIAL SEAL" bottom arc text
  - "CE" center monogram (Christopher Elgin)
  - "FOUNDER" label
  - Auto-updating version badge (reads from VERSION.txt)
  - Decorative ⭕ symbols

### File Formats
- `SonicBuilder_Seal.svg` - Vector format (2 KB)
  - Scales infinitely for print/laser cutting
  - Editable in vector software
  
- `SonicBuilder_Seal.png` - High-res PNG (2000x2000px, 317 KB)
  - Transparent background
  - For light backgrounds
  - 300 DPI print-ready
  
- `SonicBuilder_Seal_white.png` - Inverted PNG (2000x2000px, 269 KB)
  - Transparent background
  - For dark backgrounds
  - 300 DPI print-ready

### Documentation
- `README_Seal_Usage.txt` (8.3 KB)
  - Complete usage guidelines
  - Placement specifications
  - Opacity settings
  - Printing specifications
  - Design element descriptions
  
- `SEAL_PREVIEW.txt` (5.4 KB)
  - ASCII art preview
  - Quick usage examples
  - Seal design overview
  
- `INTEGRATION_EXAMPLES.md` (11 KB)
  - Code examples for PDF (ReportLab)
  - HTML integration examples
  - Markdown usage
  - LaTeX examples
  - Python/PIL image editing
  - Sizing reference table

### Build System Integration
- Added `make seal` command to Makefile
- Created `scripts/gen_seal.py` generator script
- Auto-reads version from VERSION.txt
- Generates all 3 file formats

### Usage Guidelines
**Opacity Settings:**
- Cover pages: 100% (full visibility)
- Headers/footers: 60-80%
- Watermarks: 25-40% (translucent)
- Background patterns: 15-20% (subtle)

**Size Recommendations:**
- Cover pages: 4-5 inches diameter
- Headers: 1-1.5 inches diameter
- Footers: 1-1.5 inches diameter
- Watermarks: 3-4 inches diameter
- Signature blocks: 0.75-1 inch diameter

**Positioning:**
- Cover: Center or top-right corner
- Headers: Top-right, 0.5" from edge
- Footers: Bottom-right, 0.5" from edge
- Watermark: Center of page
- Signature: Left of signature line

### Design Specifications
**Colors:**
- Primary: #1a1a1a (near-black)
- Background: #f5f5f5 (light gray)
- Text: #333333 (dark gray)
- Accent: #ffffff (white)

**Fonts:**
- Headings: Arial Bold
- Monogram: Georgia Bold
- Body: Arial Regular

### Future Enhancements
- [ ] Add signature block PDF generator
- [ ] Create branded contributor manual template
- [ ] Integrate seal into main manual PDFs
- [ ] Create field card with seal
- [ ] Add watermark option to builder.py

### Attribution
**Founder:** Christopher Elgin  
**Project:** SonicBuilder - Professional PDF Manual Generator  
**Vehicle:** 2014 Chevy Sonic LTZ  
**Integration:** EOENKK Android 15 + Maestro RR2 GM5

---

For current seal assets, run: `make seal`
For usage details, see: `Founder_Seal/README_Seal_Usage.txt`
