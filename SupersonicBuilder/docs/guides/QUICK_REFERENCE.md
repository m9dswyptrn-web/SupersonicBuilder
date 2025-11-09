# SuperSonic Manual v2.3.0 - Quick Reference

## 🚀 Build Commands

```bash
# Primary builds
make build_dark          # → output/supersonic_manual_dark.pdf (65 MB, 108 pages)
make build_light         # → output/supersonic_manual_light.pdf (65 MB, 108 pages)

# Content management
make ingest_schematics   # Import diagrams from assets/schematics_drop_here/
make index_diagrams      # Regenerate wiring index (auto-runs before builds)
make verify              # Check dependencies & environment

# Release packaging
make release_local       # Build both themes + create SHA256 checksums in dist/
```

## 📂 Add New Content

### Camera Photos
```bash
# 1. Drop JPGs into manual/01-Systems/Camera/img/
# 2. Run ingestion:
python scripts/ingest_images.py \
  --chapter-id camera \
  --target-dir manual/01-Systems/Camera/img \
  --pattern "*.jpg" \
  --caption "Camera installation"
# 3. Rebuild:
make build_dark
```

### Wiring Diagrams
```bash
# 1. Drop PNG/JPG/SVG/PDF into assets/schematics_drop_here/
# 2. Import + build:
make ingest_schematics
make build_dark
```

**Auto-magic happens:**
- Files copied to `manual/04-Appendix/Wiring_Diagrams/`
- Index auto-generated with page numbers, QR glyphs, grouped entries
- QR codes added to each diagram page
- "↩ Back to Index" navigation links added

## ✅ What's Included (v2.3.0)

**Content:**
- 108 pages professional documentation
- 93 camera installation photos
- 69 wiring diagrams

**Navigation Features:**
- QR glyph indicators (□) in index
- "↩ Back to Index" links on all diagram pages
- Bi-directional navigation workflow
- QR codes on each diagram (scan to see filename)
- Accurate page numbers throughout

**Themes:**
- Dark theme (screen-optimized)
- Light theme (print-optimized)

**Build System:**
- 2-minute quickstart workflow
- Automatic index generation
- Drop-in schematics system
- SHA256 release verification

## 📖 Navigation Workflow

**For installers using the manual:**

1. Open manual → Go to "Wiring Diagram Index" (Appendix)
2. Find diagram (e.g., "AUDIO Speaker Wiring" → page 85)
3. Click page 85 bookmark → jumps to diagram
4. View diagram, scan QR code if needed
5. Click "↩ Back to Index" → returns to index
6. Select next diagram → repeat

**Time saved:** 10-15 seconds per diagram lookup (no manual scrolling in 108-page PDF)

## 🔧 Key Files

```
SuperSonic Manual v2.3.0/
├── README.md                    ← Project overview & instructions
├── CHANGELOG.md                 ← Version history
├── QUICK_REFERENCE.md           ← This file
├── Makefile                     ← Build automation
├── requirements.txt             ← Python dependencies
├── outline.yml                  ← Book structure config
│
├── scripts/
│   ├── builder.py               ← PDF generator (w/ QR glyphs + back-links)
│   ├── gen_wiring_index.py      ← Auto-index generator
│   ├── ingest_images.py         ← Bulk image importer
│   ├── import_schematics.py     ← Schematics drop-in handler
│   └── verify_setup.py          ← Dependency checker
│
├── manual/                      ← Markdown content
│   ├── 01-Systems/
│   ├── 02-Steps/
│   ├── 03-Maestro_RR2_EOENKK/
│   └── 04-Appendix/
│       └── Wiring_Diagrams/     ← 69 diagrams + auto-generated index
│
├── assets/
│   ├── images/manifest.csv      ← Image metadata
│   ├── diagram_pages.csv        ← Diagram→page mapping (auto-generated)
│   └── schematics_drop_here/    ← Drop zone for new diagrams
│
└── output/
    ├── supersonic_manual_dark.pdf    ← Built manual (dark)
    └── supersonic_manual_light.pdf   ← Built manual (light)
```

## 📦 Dependencies

```bash
pip install -r requirements.txt
```

**Installed:**
- reportlab (PDF generation)
- Pillow (Image processing)
- pypdf (PDF manipulation)
- PyYAML (Config parsing)
- qrcode[pil] (QR code generation)
- svglib (SVG support)

## 🎯 Version Features Comparison

| Feature | v2.0.0 | v2.2.0 | v2.3.0 |
|---------|--------|--------|--------|
| Dark/Light themes | ✅ | ✅ | ✅ |
| Camera photos | 0 | 93 | 93 |
| Wiring diagrams | Basic | 69 | 69 |
| QR codes on diagrams | ❌ | ✅ | ✅ |
| Auto-generated index | ❌ | ✅ | ✅ |
| Page numbers in index | ❌ | ✅ | ✅ |
| QR glyphs in index | ❌ | ❌ | ✅ |
| Back-to-Index links | ❌ | ❌ | ✅ |
| Schematics drop-in | ❌ | ✅ | ✅ |
| Build time | ~10s | ~15s | ~15s |
| Page count | 60 | 108 | 108 |
| File size | 15 MB | 65 MB | 65 MB |

## 🚨 Troubleshooting

**Build fails?**
```bash
pip install -r requirements.txt
make verify
```

**Images not showing?**
- Check they're in correct `img/` directory
- Run `python scripts/ingest_images.py` to update manifest
- Verify `assets/images/manifest.csv` has correct `chapter_id`

**Diagrams missing from index?**
- Ensure files are in `manual/04-Appendix/Wiring_Diagrams/`
- Run `make index_diagrams` to regenerate
- Check `assets/diagram_pages.csv` for page mappings

**PDF Viewer not showing new build?**
- Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
- Check `output/` directory for latest PDF timestamps

## 🎓 Pro Tips

1. **Naming convention for diagrams:** Use `PREFIX_Description.png` format
   - `AUDIO_Speaker_Wiring.png` → Groups under "AUDIO"
   - `CAN_Bus_Layout.png` → Groups under "CAN"
   - `POWER_Distribution.png` → Groups under "POWER"

2. **Build time optimization:** Dark theme builds faster than both themes
   - Use `make build_dark` during development
   - Use `make release_local` for final packaging

3. **Image quality:** JPGs at 85% quality are sufficient
   - Keeps file size manageable
   - Maintains professional appearance

4. **PDF size:** 65 MB is acceptable for installer manuals
   - Optimized for quality over compression
   - Easy to distribute via USB/cloud

---

**🚀 SuperSonic Manual v2.3.0** - Professional PDF generation with enhanced navigation  
**Project:** 2014 Chevy Sonic LTZ Android Head Unit Installation  
**Build Time:** ~15 seconds | **Output:** 65 MB, 108 pages | **Themes:** Dark & Light
