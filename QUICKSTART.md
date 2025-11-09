# 🚀 Supersonic Edition — Quick Start Guide

**Get started with SonicBuilder Supersonic in 5 minutes!**

---

## ⚡ 3-Step Installation

### 1. Clone Repository
```bash
git clone https://github.com/ChristopherElgin/SonicBuilderSupersonic.git
cd SonicBuilderSupersonic
```

### 2. Install Dependencies
```bash
pip install -r supersonic_requirements.txt
```

### 3. Build Everything
```bash
python builders/supersonic_build_secure_all.py
```

**Done!** 🎉 Check `SonicBuilder/docs/` for all generated files.

---

## 🎯 Common Workflows

### Generate Complete Build
```bash
# One command to build everything
python builders/supersonic_build_secure_all.py

# View results
open Supersonic_Dashboard.html
open SonicBuilder/docs/
```

### Live Development (Smart-Diff)
```bash
# Auto-rebuild only what changed
python builders/supersonic_watch_smartdiff.py

# Edit any file and save → Auto-rebuilds in 3-5 seconds!
```

### System Tray Commander
```bash
# Background development with visual + audio feedback
pip install pystray Pillow plyer playsound
python builders/supersonic_tray_commander_audio.py

# Right-click tray icon for menu:
# - Run Full Secure Build
# - Run Smart-Diff Build
# - Pause / Resume Watcher
# - Quit Commander
```

---

## 🧪 Test Individual Tools

### AI Build Analysis
```bash
python builders/supersonic_reasoner_pro.py
# Creates TXT+JSON+HTML reports in SonicBuilder/reports/
```

### Auto-Diagram Generation
```bash
python builders/supersonic_sketcher.py examples/diagram_specs.json
# Creates diagrams in SonicBuilder/docs/diagrams/
```

### Badge & Branding
```bash
python builders/supersonic_branding.py
# Creates badges in SonicBuilder/branding/badges/
```

### SBOM Generation
```bash
python builders/supersonic_sbom.py
# Creates manifest in SonicBuilder/release/
```

### Commander Dashboard
```bash
python builders/make_commander_dashboard.py
# Creates Supersonic_Dashboard_Commander.html
```

### Badge Sheet
```bash
python builders/make_commander_badge_sheet.py
# Creates SonicBuilder/docs/Supersonic_Badge_Sheet.pdf
```

### Release Bundle
```bash
python builders/make_supersonic_release_bundle.py
# Creates versioned ZIP in SonicBuilder/docs/
```

---

## 📋 What Gets Created?

After running the complete build:

```
✅ PDFs:
  • Verification cards (single + double-sided)
  • Badge sheet (printable)
  • Demo manuals (dark + light)

✅ Images:
  • Banners (dark, light, animated GIF)
  • Badges (4 PNG files)
  • Commander seal (256×256 PNG)
  • QR codes (dashboard, releases)

✅ Diagrams:
  • Block diagram (audio stack)
  • Wiring diagram (simplified)
  • Pipeline diagram (build flow)

✅ Dashboards:
  • Main dashboard (Supersonic_Dashboard.html)
  • Commander dashboard (aggregated view)

✅ Release Assets:
  • SBOM manifest (JSON)
  • SHA-256 hashes (TXT)
  • Versioned release bundle (ZIP)

✅ Reports:
  • Build summaries (TXT/JSON/HTML)
```

---

## 🎨 Directory Structure

```
SonicBuilderSupersonic/
├─ SonicBuilder/docs/          ← Your generated files
│  ├─ *.pdf                    ← Verification cards
│  ├─ diagrams/                ← Auto-generated diagrams
│  └─ Supersonic_*.zip         ← Release bundles
├─ SonicBuilder/branding/
│  └─ badges/                  ← PNG badges
├─ SonicBuilder/reports/       ← Build analysis
├─ SonicBuilder/release/       ← SBOM & manifests
├─ Supersonic_Dashboard*.html  ← Dashboards
└─ Supersonic_Banner_*.png     ← Banners
```

---

## 🛠️ Optional: Install Graphviz

For auto-diagram generation:

**macOS:**
```bash
brew install graphviz
```

**Ubuntu/Debian:**
```bash
sudo apt-get install graphviz
```

**Windows:**
Download from https://graphviz.org/download/

---

## 🔍 Troubleshooting

### Missing Dependencies
```bash
# Full install
pip install -r supersonic_requirements.txt

# Minimal (core only)
pip install reportlab pikepdf Pillow segno requests
```

### Graphviz Not Found
```bash
# macOS
brew install graphviz

# Linux
sudo apt-get install graphviz

# Verify
which dot
```

### Audio Not Working
```bash
# Install audio support
pip install playsound

# Add sound files to sounds/ directory
# (See sounds/README.md for file names)
```

---

## 🚀 Next Steps

### Read Full Documentation
```bash
ls docs/SUPERSONIC*.md
# 10 comprehensive guides available
```

### Try Live Development
```bash
# Smart watcher (fast)
python builders/supersonic_watch_smartdiff.py

# System tray (visual)
python builders/supersonic_tray_commander_audio.py
```

### Set Up CI/CD
See `.github/workflows/supersonic_build.yml` for GitHub Actions setup

---

## 📞 Need Help?

- **Documentation:** `docs/` directory (4,350+ lines)
- **Examples:** All tools have `if __name__ == "__main__"` blocks
- **Issues:** https://github.com/ChristopherElgin/SonicBuilderSupersonic/issues

---

**Happy Building!** 🎉
