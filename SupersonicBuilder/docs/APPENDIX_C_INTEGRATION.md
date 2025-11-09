# Appendix C Integration — I²S Documentation System
**Date:** October 28, 2025  
**Version:** v2.0.9  
**One-Button Build Ready**

---

## 🎉 Complete Appendix C System

Your SonicBuilder platform now has a complete Appendix C system for professional I²S integration documentation with auto-indexing, QR galleries, and one-button builds!

---

## 📦 What's Been Added

### 1. **New Scripts** (4)
- `scripts/i2s_index.py` - Scans PCB_Photos/ and Tap_Diagrams/, generates index
- `scripts/appendix_c_index_pdf.py` - Creates dark-mode index PDF
- `scripts/i2s_qr.py` - Generates QR gallery for Appendix C
- `scripts/i2s_qr_2up.py` - Creates 2-up laminated QR card sheet

### 2. **New Makefile Fragment**
- `make_patches/MAKEFRAG.onebutton` - One-button build pipeline

### 3. **New Make Targets**
```bash
make i2s_index          # Index PCB & I²S files
make i2s_qr             # Generate QR gallery
make i2s_qr_2up         # Generate 2-up QR sheet
make appendix_pdf       # Generate dark-mode index PDF
make all VERSION=v2.0.9 # ONE-BUTTON BUILD (runs everything!)
```

### 4. **Directory Structure**
```
Appendix/
└─ C_I2S_Integration/
   ├─ 00_Overview.md              ← Introduction
   ├─ README.md                   ← Complete guide (NEW)
   ├─ PCB_Photos/                 ← Drop PCB photos here
   │   ├─ DEMO_Main_Board_Top.jpg
   │   └─ DEMO_Main_Board_Bottom.jpg
   ├─ Tap_Diagrams/               ← Drop I²S tap diagrams here
   │   └─ DEMO_I2S_Tap_Map.png
   ├─ 03_Photo_Index.csv          ← Auto-generated index
   ├─ QR_Index.pdf                ← QR gallery (dark mode)
   ├─ QR_Index_2UP.pdf            ← 2-up laminated QR sheet
   ├─ Appendix_C_I2S_Index.pdf    ← Dark-mode index PDF
   ├─ metadata.json               ← Build metadata
   └─ Auto_Notes.txt              ← Build log
```

### 5. **Documentation**
- `docs/ONE_BUTTON_BUILD.md` - Quick start guide
- `docs/APPENDIX_C_INTEGRATION.md` - This file
- `Appendix/C_I2S_Integration/README.md` - Complete workflow guide

---

## 🚀 Quick Start

### One-Button Build
```bash
make all VERSION=v2.0.9
```

**This single command:**
1. ✅ Indexes all PCB photos and tap diagrams
2. ✅ Generates QR gallery (dark mode)
3. ✅ Creates 2-up laminated QR sheet
4. ✅ Builds Appendix C index PDF
5. ✅ Stamps metadata if dist/manual.pdf exists

**Done!** All Appendix C documentation generated.

---

## 🔧 Individual Make Targets

### Index Files
```bash
make i2s_index
```
**Output:**
- `Appendix/C_I2S_Integration/03_Photo_Index.csv` - File inventory
- `Appendix/C_I2S_Integration/metadata.json` - Build metadata with URL
- `Appendix/C_I2S_Integration/Auto_Notes.txt` - Build log

**CSV Format:**
```csv
type,file,name,ext,bytes
pcb,PCB_Photos/DEMO_Main_Board_Top.jpg,DEMO Main Board Top,.jpg,71234
pcb,PCB_Photos/DEMO_Main_Board_Bottom.jpg,DEMO Main Board Bottom,.jpg,73456
tap,Tap_Diagrams/DEMO_I2S_Tap_Map.png,DEMO I2S Tap Map,.png,25678
```

### Generate QR Gallery
```bash
make i2s_qr
```
**Output:** `Appendix/C_I2S_Integration/QR_Index.pdf`

**QR Codes Link To:**
- Manuals (/releases)
- Latest Release (/releases/latest)
- Appendix C folder (/tree/main/Appendix/C_I2S_Integration)
- PCB Photos folder
- Tap Diagrams folder

### Generate 2-Up QR Sheet
```bash
make i2s_qr_2up
```
**Output:** `Appendix/C_I2S_Integration/QR_Index_2UP.pdf`

Laminated 2-up card sheet with:
- 2 QR gallery copies on one Letter page
- Footer with SB_REPO_URL
- QR code in corner
- Ready to print and laminate

### Generate Index PDF
```bash
make appendix_pdf VERSION=v2.0.9
```
**Output:** `Appendix/C_I2S_Integration/Appendix_C_I2S_Index.pdf`

Professional dark-mode index listing:
- All PCB photos
- All tap diagrams
- File metadata
- Version and URL footer

---

## 📁 Detailed File Descriptions

### Auto-Generated Files

#### 03_Photo_Index.csv
Complete inventory of all files in PCB_Photos/ and Tap_Diagrams/:
- `type` - "pcb" or "tap"
- `file` - Relative path from C_I2S_Integration/
- `name` - Human-readable name (underscores → spaces)
- `ext` - File extension (.jpg, .png, etc.)
- `bytes` - File size in bytes

#### metadata.json
Build metadata with URL and timestamp:
```json
{
  "count": 3,
  "generated_at": 1730144843,
  "base_url": "https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev"
}
```

#### Auto_Notes.txt
Simple build log:
```
Appendix C index regenerated.
```

#### QR_Index.pdf
Dark-mode 3x3 QR gallery grid:
- 9 QR codes maximum
- Links to manuals, parts, appendix, photos, diagrams
- Professional dark theme
- Version and URL footer

#### QR_Index_2UP.pdf
Laminated field card version:
- 2 QR galleries per page (stacked)
- Footer: "SonicBuilder • [URL]"
- Corner QR code
- Print on Letter, laminate, cut in half

#### Appendix_C_I2S_Index.pdf
Professional index document:
- Dark background (RGB 0.1, 0.1, 0.12)
- White text (whitesmoke)
- Numbered entries
- Multi-page support
- Version and URL on every page

---

## 🌊 Complete Workflow

### Step 1: Add Your Files
```bash
# Copy PCB installation photos
cp my_pcb_install_1.jpg Appendix/C_I2S_Integration/PCB_Photos/
cp my_pcb_install_2.jpg Appendix/C_I2S_Integration/PCB_Photos/

# Copy I²S tap diagrams
cp my_i2s_map.png Appendix/C_I2S_Integration/Tap_Diagrams/
cp my_wiring_diagram.jpg Appendix/C_I2S_Integration/Tap_Diagrams/
```

### Step 2: One-Button Build
```bash
make all VERSION=v2.0.9
```

**Output:**
```
Indexed 4 files into Appendix/C_I2S_Integration/03_Photo_Index.csv
Wrote Appendix/C_I2S_Integration/QR_Index.pdf
Wrote Appendix/C_I2S_Integration/QR_Index_2UP.pdf
Wrote Appendix/C_I2S_Integration/Appendix_C_I2S_Index.pdf
Stamped dist/manual.pdf with version=v2.0.9 url=https://08abbd3d.../
```

### Step 3: Done!
Your Appendix C is complete with:
- ✅ Indexed files
- ✅ QR gallery for installers
- ✅ Laminated QR cards
- ✅ Professional index PDF
- ✅ Metadata with canonical URL

---

## 🎯 Integration with Existing Tools

### URL Management
All Appendix C tools use `scripts/repo_url.py`:
```python
from repo_url import resolve
url = resolve()  # Auto-detects GitHub > Replit > custom
```

**Consistent URLs across:**
- QR galleries
- Index PDFs
- Metadata files
- CoA certificates
- Two-up cards

### Version Management
```bash
# Manual version bump
make bump FROM=v2.0.8 TO=v2.0.9

# Rebuild Appendix C with new version
make all VERSION=v2.0.9
```

### Complete Release
```bash
# 1. Bump version
make bump FROM=v2.0.8 TO=v2.0.9

# 2. Build Appendix C
make all VERSION=v2.0.9

# 3. Build manuals
make build_dark
make build_light

# 4. Generate CoA
cd tools/CoA_Generator
python generate_coa.py --auto-increment --version v2.0.9

# 5. Create distribution tools
make two_up
make qr_gallery

# 6. Package release
make release_local
```

---

## 🔍 Demo Files Included

Your installation includes demo files to test the system:

### PCB Photos (2)
- `DEMO_Main_Board_Top.jpg` (72 KB)
- `DEMO_Main_Board_Bottom.jpg` (73 KB)

### Tap Diagrams (1)
- `DEMO_I2S_Tap_Map.png` (26 KB)

**To replace with your own:**
```bash
# Remove demo files
rm Appendix/C_I2S_Integration/PCB_Photos/DEMO_*
rm Appendix/C_I2S_Integration/Tap_Diagrams/DEMO_*

# Add your files
cp your_files/* Appendix/C_I2S_Integration/PCB_Photos/
cp your_diagrams/* Appendix/C_I2S_Integration/Tap_Diagrams/

# Rebuild
make all VERSION=v2.0.9
```

---

## 🛠️ Advanced Usage

### Custom QR Links
Edit `scripts/i2s_qr.py` to customize QR gallery links:
```python
cmd = [sys.executable, "scripts/qr_gallery.py", 
       "--out", out, 
       "--title", "Appendix C — QR Gallery",
       "--links", "custom1=/your/path",
       "--links", "custom2=/another/path"]
```

### Custom Index Title
```bash
python scripts/appendix_c_index_pdf.py \
  --csv Appendix/C_I2S_Integration/03_Photo_Index.csv \
  --out custom_index.pdf \
  --title "Custom Title Here" \
  --version v2.0.9
```

### Override URL
```bash
SB_REPO_URL="https://custom.domain" make all VERSION=v2.0.9
```

---

## 📊 File Size Estimates

**Typical Output Sizes:**
- `03_Photo_Index.csv` - ~1 KB (depends on file count)
- `metadata.json` - ~200 bytes
- `Auto_Notes.txt` - ~50 bytes
- `QR_Index.pdf` - ~50-100 KB (9 QR codes)
- `QR_Index_2UP.pdf` - ~500 KB (rasterized)
- `Appendix_C_I2S_Index.pdf` - ~20-50 KB (text-based)

**Total:** ~600 KB for complete Appendix C package

---

## ✅ Verification

### Test Complete Pipeline
```bash
# Clean previous builds
rm -f Appendix/C_I2S_Integration/*.{csv,pdf,json,txt}

# Run one-button build
make all VERSION=v2.0.9

# Verify outputs
ls -lh Appendix/C_I2S_Integration/
```

**Expected Files:**
```
-rw-r--r-- 03_Photo_Index.csv
-rw-r--r-- QR_Index.pdf
-rw-r--r-- QR_Index_2UP.pdf
-rw-r--r-- Appendix_C_I2S_Index.pdf
-rw-r--r-- metadata.json
-rw-r--r-- Auto_Notes.txt
```

### Test Individual Targets
```bash
make i2s_index          # Should create CSV and metadata
make i2s_qr             # Should create QR_Index.pdf
make i2s_qr_2up         # Should create QR_Index_2UP.pdf
make appendix_pdf VERSION=v2.0.9  # Should create Appendix_C_I2S_Index.pdf
```

---

## 🔧 Troubleshooting

### "No index CSV found"
**Problem:** Running `make appendix_pdf` before `make i2s_index`  
**Solution:** Run `make i2s_index` first or use `make all`

### "QR_Index.pdf not found"
**Problem:** Running `make i2s_qr_2up` before `make i2s_qr`  
**Solution:** Run `make i2s_qr` first or use `make all`

### Wrong URL in QR Codes
**Problem:** QR shows Replit domain instead of GitHub  
**Solution:** Set environment variable:
```bash
export SB_REPO_URL="https://github.com/<owner>/<repo>"
make all VERSION=v2.0.9
```

### Import Error: repo_url
**Problem:** `ModuleNotFoundError: No module named 'repo_url'`  
**Solution:** Scripts have been updated with correct imports. If error persists:
```bash
python3 -c "import sys; sys.path.insert(0, 'scripts'); from repo_url import resolve; print(resolve())"
```

---

## 📚 Related Documentation

- `docs/ONE_BUTTON_BUILD.md` - Quick start guide
- `docs/VERSION_BUMP_INTEGRATION.md` - Version management
- `docs/URL_MANAGEMENT.md` - URL resolution system
- `docs/COMPLETE_INTEGRATION_GUIDE.md` - Full system overview
- `Appendix/C_I2S_Integration/README.md` - Appendix C workflow

---

## 🎉 Summary

Your SonicBuilder platform now has:

✅ **Appendix C System**
- Auto-indexing of PCB photos and tap diagrams
- Dark-mode professional index PDFs
- QR galleries for installer reference
- 2-up laminated field cards

✅ **One-Button Build**
- `make all VERSION=v2.0.9` - Complete automation
- Generates all indexes, QR codes, and PDFs
- Stamps metadata automatically

✅ **URL Integration**
- All tools use canonical URL from repo_url.py
- Consistent across QR codes, PDFs, metadata
- Auto-detection: GitHub > Replit > custom

✅ **Complete Workflow**
- Drop files → Run `make all` → Done!
- Professional documentation in seconds
- Ready for installers and end users

---

**Current Status:**
- Demo Files: 3 files (2 PCB photos, 1 tap diagram)
- Scripts: 4 new Python tools
- Make Targets: 5 new commands
- Documentation: Complete

**Ready to Use:**
```bash
make all VERSION=v2.0.9
```

**Your Appendix C system is production-ready!** 🚀
