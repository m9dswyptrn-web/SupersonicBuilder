# 🚀 SonicBuilder Supersonic Edition Tools

**Advanced utilities for automated build, documentation, and deployment**

---

## 📋 Overview

The Supersonic Edition includes enterprise-grade tools for:
- ✅ **Automated demo PDF generation** (dark + light themes)
- ✅ **CHANGELOG to HTML diff rendering** with theme toggle
- ✅ **Complete build automation** with verification
- ✅ **Lean installer** for standalone deployments

---

## 🛠️ Available Tools

### 1. Demo PDF Generators

Generate laminated-style demo PDFs for field documentation.

#### Dark Theme PDF
```bash
python3 builders/make_demo_dark_pdf.py
```

**Output:** `SonicBuilder/docs/demo_dark.pdf`

**Features:**
- Dark background (#121212) for shop lighting
- Cyan accent lines
- Professional laminated style
- Ready for real wiring diagrams

#### Light Theme PDF
```bash
python3 builders/make_demo_light_pdf.py
```

**Output:** `SonicBuilder/docs/demo_light.pdf`

**Features:**
- White background for print distribution
- Blue accent lines
- Professional laminated style
- Bright-room optimized

#### Quick Generate Both
```bash
make supersonic-demos
```

**Requirements:**
```bash
pip install reportlab
```

---

### 2. Diff Renderer (CHANGELOG → HTML)

Convert your CHANGELOG.md to styled HTML with dark/light theme toggle.

#### Usage
```bash
python3 SonicBuilder/tools/diff_render_html.py \
  --md CHANGELOG.md \
  --out diff.html \
  --title "SonicBuilder Changelog"
```

**Or use Makefile:**
```bash
make supersonic-diff
```

#### Features
- **Dark/Light Toggle** - Switch themes with localStorage memory
- **Print-Friendly** - Optimized stylesheet for printing
- **Copy to Clipboard** - One-click GitHub release notes
- **Anchored Headers** - Easy navigation
- **Responsive Design** - Mobile-friendly

#### Output
Opens a styled HTML page with:
- 🌓 Theme toggle button
- 📋 Copy notes button
- Syntax-highlighted code blocks
- Professional typography

---

### 3. Full Build Automation

Complete verification + build + optional GitHub publishing.

#### Basic Build
```bash
python3 builders/supersonic_build_all.py
```

**What it does:**
1. ✅ Checks folder structure
2. ✅ Verifies Python environment
3. ✅ Generates demo PDFs (dark + light)
4. ✅ Renders CHANGELOG to HTML
5. ✅ Runs full Supersonic pack build
6. ✅ Verifies output ZIPs

#### With GitHub Publishing
```bash
python3 builders/supersonic_build_all.py --publish
```

**Additional steps:**
7. ✅ Creates GitHub release with tag
8. ✅ Uploads all ZIPs from dist/
9. ✅ Includes RELEASE_NOTES.md if available

**Or use Makefile:**
```bash
# Build only
make supersonic-build-all

# Build + publish to GitHub
make supersonic-build-all-publish
```

#### Requirements for Publishing
```bash
# Install GitHub CLI
gh auth login
```

---

### 4. Lean Installer (Basic)

Create a minimal standalone Supersonic environment.

```bash
python3 builders/make_supersonic_lean.py
```

**Output:** `supersonic_lean/` directory with:
- ✅ Supersonic builder
- ✅ Demo PDF generators
- ✅ Diff renderer
- ✅ Build automation script
- ✅ Configuration templates
- ✅ Folder skeleton

### 5. Lean Auto Installer (Trace-Enabled)

Advanced installer with build traceability and GitHub integration.

```bash
python3 builders/make_supersonic_lean_auto.py
```

**Or use Makefile:**
```bash
make supersonic-lean-auto
```

**Features:**
- ✅ **Build tracing** - Embeds GitHub tag/commit
- ✅ **BUILD_REPORT.md** - Complete environment snapshot
- ✅ **Dual mode** - GitHub or local file sources
- ✅ **Version tracking** - Know exactly what you're running

**Perfect for:**
- Team collaboration
- Version tracking
- Build auditing
- Deployment verification
- Offline distribution

**See:** `docs/SUPERSONIC_LEAN_AUTO.md` for complete guide

### 6. Preflight Verification

Verify build integrity before publishing.

```bash
python3 builders/supersonic_verify.py
```

**Or use Makefile:**
```bash
make supersonic-verify
```

**Checks:**
- ✅ Required files exist
- ✅ Config tag matches GitHub tag
- ✅ BUILD_REPORT.md contains trace
- ✅ Complete environment validation

**Output:**
- ✅ ALL SYSTEMS GO — Ready to publish
- ⚠️ Warnings — Review before publishing
- ❌ Errors — Fix required files

### 7. Mission Summary Cards

Generate professional reference cards with embedded build trace.

```bash
python3 builders/make_supersonic_cards_autoattach.py
```

**Or use Makefile:**
```bash
# Generate cards
make supersonic-mission-cards

# Generate + auto-open folder
make supersonic-mission-cards-open
```

**Output:**
- `SonicBuilder/docs/Mission_Summary_Card.pdf` (dark shop edition)
- `SonicBuilder/docs/Mission_Summary_Card_Light.pdf` (light print edition)
- `SonicBuilder/docs/Mission_Cards_Supersonic_v3.2.1.zip` (both cards)

**Features:**
- Embedded build tag/commit in footer
- Primary command reference
- Status indicator legend
- Traceability chain diagram
- Dual-theme support (dark/light)
- Auto-ZIP packaging

**Perfect for:**
- Field reference cards
- Team distribution
- Quick command lookup
- Laminated shop manuals

---

## 🎯 Makefile Quick Reference

### All Supersonic Commands
```bash
make supersonic-help
```

### Individual Commands

| Command | Description |
|---------|-------------|
| `make supersonic-demos` | Generate demo PDFs (dark + light) |
| `make supersonic-diff` | Render CHANGELOG to HTML |
| `make supersonic-build-all` | Full build automation |
| `make supersonic-build-all-publish` | Build + GitHub publish |
| `make supersonic-lean` | Create basic lean installer |
| `make supersonic-lean-auto` | Create trace-enabled lean installer |
| `make supersonic-verify` | Run preflight verification |
| `make supersonic-mission-cards` | Generate mission summary cards |
| `make supersonic-mission-cards-open` | Generate cards + open folder |

---

## 📁 File Locations

### Tools
```
SonicBuilder/tools/
└── diff_render_html.py         # CHANGELOG → HTML converter
```

### Builders
```
builders/
├── make_demo_dark_pdf.py        # Dark PDF generator
├── make_demo_light_pdf.py       # Light PDF generator
├── supersonic_build_all.py      # Full automation
└── make_supersonic_lean.py      # Lean installer
```

### Generated Output
```
SonicBuilder/docs/
├── demo_dark.pdf                # Dark demo
└── demo_light.pdf               # Light demo

diff.html                        # Rendered CHANGELOG

builders/dist/
├── SonicBuilder_..._dark.zip    # Dark build
└── SonicBuilder_..._light.zip   # Light build
```

---

## 🔧 Configuration

### sonicbuilder.config.json
```json
{
  "project_name": "SonicBuilder",
  "vehicle": "Chevy Sonic LTZ (T300)",
  "version": "v3.2.1",
  "profile": "dark",
  "profiles_matrix": ["dark", "light"],
  "changelog_md": "CHANGELOG.md",
  "diff_renderer": "SonicBuilder/tools/diff_render_html.py"
}
```

---

## 📊 Complete Workflow Example

### Daily Build Workflow
```bash
# 1. Generate demo PDFs
make supersonic-demos

# 2. Update CHANGELOG.md
# (edit your changes)

# 3. Render to HTML for review
make supersonic-diff

# 4. Run full build
make supersonic-build-all

# 5. Verify output
ls -lh builders/dist/
```

### Release Workflow
```bash
# 1. Update version in sonicbuilder.config.json
# (edit version to v3.2.2)

# 2. Update CHANGELOG.md with release notes
# (add release notes)

# 3. Generate everything and publish
make supersonic-build-all-publish

# GitHub release created automatically!
```

---

## 🎨 Diff Renderer Features

### Theme Toggle
The diff renderer includes persistent dark/light theme switching:
- **Dark:** Cyan (#00ffff) + Amber (#ffb000) accents
- **Light:** Blue (#007acc) + Orange (#ff5500) accents
- **Memory:** Uses localStorage to remember preference

### Print Mode
Optimized for printing:
- Removes header/buttons
- Forces white background
- Black text for clarity
- Underlined links

### Copy to Clipboard
One-click copy of entire CHANGELOG for GitHub release notes.

---

## ⚙️ Requirements

### Python Packages
```bash
pip install reportlab        # PDF generation
pip install segno            # QR codes (optional)
pip install qrcode[pil]      # QR codes (optional)
pip install pikepdf          # PDF manipulation (optional)
```

### External Tools
```bash
gh --version                 # GitHub CLI for publishing
```

---

## 🐛 Troubleshooting

### PDF Generation Fails
```
ImportError: No module named 'reportlab'
```

**Solution:**
```bash
pip install reportlab
```

### Diff Render Fails
```
FileNotFoundError: CHANGELOG.md not found
```

**Solution:** Create a CHANGELOG.md in your project root.

### GitHub Publishing Fails
```
gh: command not found
```

**Solution:** Install GitHub CLI from https://cli.github.com/

---

## 📚 Examples

### Custom Diff Render
```bash
python3 SonicBuilder/tools/diff_render_html.py \
  --md RELEASE_NOTES.md \
  --out release.html \
  --title "Release v3.2.1"
```

### Custom PDF Output
```python
from make_demo_dark_pdf import make_demo_dark_pdf
make_demo_dark_pdf("custom_output/my_manual.pdf")
```

### Programmatic Build
```python
import subprocess
subprocess.run(["python3", "builders/supersonic_build_all.py"])
```

---

## 🎉 Summary

The Supersonic Edition provides:
- ✅ **7 automation tools** (demos, diff, build, lean, verify, cards)
- ✅ **9 Makefile targets** (complete automation suite)
- ✅ **Complete build automation** (verify + build + publish)
- ✅ **GitHub integration** (tag tracking + releases)
- ✅ **Professional documentation** (mission cards + HTML renders)
- ✅ **Build traceability** (full version tracking)

Perfect for enterprise deployments and team workflows!

---

**Documentation:** `docs/SUPERSONIC_TOOLS.md`  
**Main Builder:** `builders/sonicbuilder_supersonic.py`  
**Help:** `make supersonic-help`
