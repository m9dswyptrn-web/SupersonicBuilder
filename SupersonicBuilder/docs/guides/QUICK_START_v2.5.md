# SuperSonic Manual v2.5.0 - Quick Start Guide

## 🚀 One-Command Release Build

```bash
make release_local
```

**That's it!** This single command:
1. ✅ Builds both manual themes (dark + light)
2. ✅ Generates parts lists (dark + light)
3. ✅ Copies all PDFs to `dist/`
4. ✅ Creates SHA256 checksums
5. ✅ **Auto-generates RELEASE_NOTES.md**

**Time:** ~35 seconds  
**Output:** 6 files in `dist/` ready for GitHub release

---

## 📦 What You Get

```
dist/
├── supersonic_manual_dark.pdf    (65 MB) - Main manual (screen)
├── supersonic_manual_light.pdf   (65 MB) - Main manual (print)
├── parts_tools_dark.pdf          (2.4 KB) - Parts list (screen)
├── parts_tools_light.pdf         (2.4 KB) - Parts list (print)
├── SHA256SUMS.txt                - Checksums for verification
├── RELEASE_NOTES.md              - Auto-generated release notes
└── README.txt                    - Package description
```

---

## ✅ Verify Release

```bash
cd dist
sha256sum -c SHA256SUMS.txt
```

**Expected:**
```
supersonic_manual_dark.pdf: OK
supersonic_manual_light.pdf: OK
parts_tools_dark.pdf: OK
parts_tools_light.pdf: OK
```

---

## 🌐 GitHub Release (3 Steps)

### 1. Create Tag
```bash
git tag v2.5.0
git push origin v2.5.0
```

### 2. Upload Files
- Go to GitHub → Releases → Draft new release
- Upload all 4 PDFs from `dist/`

### 3. Add Description
- Copy/paste content from `dist/RELEASE_NOTES.md`
- Publish release

**Done!** Your release is live with clickable PDF links and SHA256 checksums.

---

## 🛠️ Individual Build Commands

```bash
# Manual only
make build_dark          # Dark theme manual (15s)
make build_light         # Light theme manual (15s)

# Parts list only
make parts_tools         # Dark theme (<1s)
make parts_tools_light   # Light theme (<1s)

# Content updates
make ingest_schematics   # Import new diagrams
make verify              # Check dependencies
```

---

## 📝 Update Parts List

### Edit Configuration
```bash
nano parts_tools.yaml
```

### Example: Add a Tool
```yaml
sections:
  - title: Tools
    items:
      - name: Panel Removal Tool Set
        sku: TOOL-KIT-5PC
        url: https://example.com/tools
        notes: 5-piece nylon trim removal set
```

### Rebuild
```bash
make parts_tools
make parts_tools_light
```

**Time:** <1 second per theme

---

## 🖼️ Add Wiring Diagrams

### Drop In Files
```bash
# Put PNG/JPG/SVG/PDF files here:
assets/schematics_drop_here/
  ├── AUDIO_Speaker_Layout.png
  ├── CAN_Bus_Wiring.png
  └── POWER_Distribution.pdf
```

### Import & Build
```bash
make ingest_schematics   # Import to manual
make build_dark          # Rebuild with new diagrams
```

**Auto-generated:**
- ✅ Index with page numbers
- ✅ QR codes on each diagram
- ✅ Back-to-Index navigation
- ✅ QR glyph indicators

---

## ⚡ Super Quick Reference

```bash
# Complete release (one command)
make release_local              # → dist/ with 6 files

# Verify
cd dist && sha256sum -c SHA256SUMS.txt

# View release notes
cat dist/RELEASE_NOTES.md

# Check all PDFs
ls -lh output/*.pdf             # Source PDFs
ls -lh dist/*.pdf               # Release PDFs
```

---

## 📊 System Performance

| Task | Time | Output |
|------|------|--------|
| `make build_dark` | ~15s | 65 MB manual |
| `make parts_tools` | <1s | 2.4 KB parts list |
| `make release_local` | ~35s | Complete release package |

---

## ✨ Key Features

**Manual (108 pages):**
- 93 camera installation photos
- 69 wiring diagrams with QR codes
- Auto-generated index
- Dark & Light themes

**Parts List (1 page):**
- QR codes for supplier URLs
- YAML configuration
- Professional styling

**Release Automation:**
- One-command full release
- Auto-generated release notes
- SHA256 verification
- GitHub-ready markdown

---

**🎯 SuperSonic Manual v2.5.0** - Complete PDF documentation system  
**One Command:** `make release_local` | **Time:** 35s | **Output:** Production-ready release
