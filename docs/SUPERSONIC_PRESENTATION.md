# 🎨 SonicBuilder Supersonic — Presentation & Verification Tools

**Complete suite of banner generators, dashboards, verification cards, and secure packaging**

---

## 📦 Tool Overview

The Supersonic Edition includes **15 new presentation and verification tools**:

### 🖼️ Banner Generators (3)
- `make_supersonic_banner_dark.py` — Dark GitHub banner
- `make_supersonic_banner_light.py` — Light GitHub banner
- `make_supersonic_banner_glow.py` — Animated glowing banner (GIF)

### 📊 Dashboard Generators (3)
- `make_supersonic_dashboard.py` — Basic HTML dashboard
- `make_supersonic_dashboard_v2.py` — Enhanced with live GitHub API
- `make_supersonic_dashboard_v3.py` — Complete with QR trace

### 🎴 Verification Cards (2)
- `make_supersonic_fieldcard.py` — Single-sided verification card
- `make_supersonic_fieldcard_double.py` — Double-sided with wiring reference

### 📦 Packaging & Release (3)
- `make_supersonic_fieldkit.py` — Bundles all assets
- `make_supersonic_release_secure.py` — Adds SHA-256 manifests & USB autorun
- `supersonic_build_secure_all.py` — Master build chain

### ⚙️ CI/CD Integration (2)
- `.github/workflows/supersonic_build.yml` — GitHub Actions workflow
- `buildspec.yml` — AWS CodeBuild configuration

---

## 🖼️ Banner Generators

### 1. Dark Banner

Generate a professional dark-mode GitHub banner.

```bash
python builders/make_supersonic_banner_dark.py
```

**Output:** `Supersonic_Banner_Dark.png` (1200×400)

**Features:**
- Deep gray background (#0A0A0F)
- Cyan accent (#00FFFF)
- Title: "SonicBuilder Supersonic"
- Tagline: "Build of Builds — Automated · Verified · Traceable"
- Footer: Version and author

**Use in GitHub:**
```markdown
<p align="center">
  <img src="Supersonic_Banner_Dark.png" alt="SonicBuilder Supersonic" width="100%">
</p>
```

### 2. Light Banner

Generate a light-theme banner for print/documentation.

```bash
python builders/make_supersonic_banner_light.py
```

**Output:** `Supersonic_Banner_Light.png` (1200×400)

**Features:**
- Soft white background (#F5F5FA)
- Blue accent (#007ACC)
- Same content as dark, optimized for printing

### 3. Glow Banner (Animated)

Generate an animated glowing banner for presentations.

```bash
python builders/make_supersonic_banner_glow.py
```

**Output:** `Supersonic_Banner_Glow.gif` (1200×400, 20 frames)

**Features:**
- Pulsing cyan glow effect
- Loop animation
- 120ms frame duration
- Perfect for slideshow headers

---

## 📊 Dashboard Generators

### Dashboard v1 (Basic)

Simple HTML dashboard with build metadata.

```bash
python builders/make_supersonic_dashboard.py
```

**Output:** `Supersonic_Dashboard.html`

**Features:**
- Build version display
- Repository link
- Banner previews
- Mission card links
- Package download links

### Dashboard v2 (Enhanced)

Adds theme toggle and live GitHub integration.

```bash
python builders/make_supersonic_dashboard_v2.py
```

**Features:**
- ✅ All v1 features
- ✅ Dark/Light theme toggle
- ✅ Live version fetch from GitHub API
- ✅ PDF preview embeds
- ✅ GitHub release launcher button

### Dashboard v3 (Complete)

Full-featured dashboard with QR trace.

```bash
python builders/make_supersonic_dashboard_v3.py
```

**Output:** `Supersonic_Dashboard.html` + `Supersonic_QR_Trace.png`

**Features:**
- ✅ All v2 features
- ✅ Embedded QR code trace
- ✅ JSON trace data in QR
- ✅ Auto-generated QR with build metadata

**QR Trace Data:**
```json
{
  "project": "SonicBuilder Supersonic",
  "tag": "v3.2.1",
  "timestamp": "2025-11-01T...",
  "repo": "https://github.com/...",
  "release": "https://github.com/.../releases/latest"
}
```

---

## 🎴 Verification Cards

### Single-Sided Card

Professional 5.5×8.5" verification card with QR trace.

```bash
python builders/make_supersonic_fieldcard.py
```

**Output:** `SonicBuilder/docs/Supersonic_Verification_Card.pdf`

**Layout:**
```
+-------------------------------------------+
| SONICBUILDER SUPERSONIC                   |
| Build of Builds — Field Verification Card |
|-------------------------------------------|
|     [ QR Code (centered, 2.5" square) ]   |
|                                           |
| Version: v3.2.1                           |
| Timestamp: 2025-11-01 18:42 UTC           |
| Repository: github.com/...                |
| Release: /releases/latest                 |
|                                           |
| Trace Legend:                             |
| • Scan QR to verify authenticity.         |
| • Confirms version, repo, and timestamp.  |
| • Use GitHub release for validation.      |
|-------------------------------------------|
| Built & Verified by SonicBuilder Supersonic|
| © 2025 Christopher Elgin                  |
+-------------------------------------------+
```

**Perfect for:**
- Laminated field reference cards
- Shop documentation
- Team distribution
- Build verification

### Double-Sided Card

Two-page card with verification + wiring reference.

```bash
python builders/make_supersonic_fieldcard_double.py
```

**Output:** `SonicBuilder/docs/Supersonic_Verification_Card_Double.pdf`

**Front:** Same as single-sided card

**Back — DSP & Wiring Reference:**
- Speaker/line wiring color codes
- DSP preset slot descriptions
- Quick diagnostic checklist
- Field troubleshooting guide

**Wiring Legend:**
```
Front Left (+)  → White
Front Left (–)  → White/Black
Front Right (+) → Gray
Front Right (–) → Gray/Black
Rear Left (+)   → Green
Rear Left (–)   → Green/Black
Rear Right (+)  → Purple
Rear Right (–)  → Purple/Black
```

**DSP Presets:**
- Preset 1: Flat (Factory Neutral)
- Preset 2: Daily Drive (Mild Bass Boost)
- Preset 3: Stage EQ (Front Focused)
- Preset 4: Custom / Project Tune

---

## 📦 Field Kit Packager

Bundle all presentation assets into a single ZIP.

```bash
python builders/make_supersonic_fieldkit.py
```

**Output:** `SonicBuilder/docs/Supersonic_FieldKit_v3.2.1.zip`

**Contents:**
```
Supersonic_FieldKit_v3.2.1.zip
 ├── Supersonic_Verification_Card.pdf
 ├── Supersonic_Verification_Card_Double.pdf
 ├── Supersonic_Dashboard.html
 ├── Supersonic_QR_Trace.png
 ├── Supersonic_Banner_Dark.png
 ├── Supersonic_Banner_Light.png
 ├── Supersonic_Banner_Glow.gif
 ├── Mission_Summary_Card.pdf
 ├── Mission_Summary_Card_Light.pdf
 └── Mission_Cards_Supersonic_v3.2.1.zip
```

---

## 🔐 Secure Release System

Add integrity verification and USB autorun.

```bash
python builders/make_supersonic_release_secure.py
```

**Output:** Enhanced Field Kit with:
- ✅ `MANIFEST.json` — SHA-256 checksums
- ✅ `readme.html` — USB autorun landing page
- ✅ `autorun.inf` — Windows autostart config

**MANIFEST.json Example:**
```json
{
  "project": "SonicBuilder Supersonic",
  "version": "v3.2.1",
  "timestamp": "2025-11-01_23-17-05Z",
  "files": [
    {
      "filename": "Supersonic_Verification_Card.pdf",
      "sha256": "9d24a8f0a..."
    },
    {
      "filename": "Supersonic_Dashboard.html",
      "sha256": "13b8d25c7..."
    }
  ]
}
```

**Auto-Upload to GitHub:**
If `GITHUB_TOKEN` environment variable is set, automatically uploads to GitHub release.

```bash
export GITHUB_TOKEN=ghp_...
python builders/make_supersonic_release_secure.py
```

---

## 🚀 Master Build Chain

Run the entire presentation build sequence.

```bash
python builders/supersonic_build_secure_all.py
```

**Executes in order:**
1. Banner Dark
2. Banner Light
3. Banner Glow
4. Dashboard v3 (with QR)
5. Verification Card (single)
6. Verification Card (double)
7. Field Kit Packaging
8. Secure Release (SHA-256 + manifests)

**Output:**
- All banners generated
- Dashboard with live trace
- Both verification cards
- Complete Field Kit ZIP
- SHA-256 integrity manifest
- USB autorun files
- Build log: `SonicBuilder/build_log.txt`

**Log Rotation:**
Previous logs are automatically archived with timestamps.

---

## ⚙️ CI/CD Integration

### GitHub Actions

Automated build on version tags.

**File:** `.github/workflows/supersonic_build.yml`

**Trigger:**
```bash
git tag v3.2.2
git push origin v3.2.2
```

**Actions:**
1. Checkout code
2. Setup Python 3.12
3. Install dependencies
4. Run lean environment setup
5. Execute full Supersonic build
6. Generate mission cards
7. Generate presentation assets
8. Upload artifacts
9. Create GitHub release

**Release Assets:**
- Mission_Cards_Supersonic_v3.2.2.zip
- Supersonic_FieldKit_v3.2.2.zip
- All build ZIPs from dist/
- BUILD_REPORT.md

### AWS CodeBuild

Cloud-based build automation.

**File:** `buildspec.yml`

**Phases:**
1. **Install:** Python 3.12 + dependencies
2. **Build:** Run full build chain
3. **Post-build:** Package artifacts

**Artifacts:**
- Mission Cards ZIP
- Field Kit ZIP
- BUILD_REPORT.md
- All dist/ packages

---

## 🎯 Complete Build Workflows

### Daily Development

```bash
# Generate presentation assets
python builders/supersonic_build_secure_all.py

# View dashboard locally
open Supersonic_Dashboard.html
```

### Release Preparation

```bash
# 1. Update version in config
# Edit sonicbuilder.config.json

# 2. Generate everything
python builders/supersonic_build_secure_all.py

# 3. Verify output
ls -lh SonicBuilder/docs/
```

### GitHub Release

```bash
# 1. Tag version
git tag v3.2.2
git push origin v3.2.2

# GitHub Actions automatically:
# - Builds all assets
# - Generates Field Kit
# - Creates GitHub release
# - Uploads all ZIPs
```

### Manual GitHub Upload

```bash
# Set token
export GITHUB_TOKEN=ghp_...

# Run secure release
python builders/make_supersonic_release_secure.py

# Field Kit uploaded automatically
```

---

## 📊 Complete Tool Summary

| Category | Tools | Output Files |
|----------|-------|--------------|
| **Banners** | 3 | PNG (2) + GIF (1) |
| **Dashboards** | 3 | HTML + QR PNG |
| **Cards** | 2 | PDF (single + double) |
| **Packaging** | 3 | ZIP + MANIFEST + autorun |
| **CI/CD** | 2 | GitHub Actions + CodeBuild |
| **Total** | **13** | **10+ assets** |

---

## 🎉 Output Summary

Running the complete build chain generates:

```
✅ BANNERS:
  • Supersonic_Banner_Dark.png
  • Supersonic_Banner_Light.png
  • Supersonic_Banner_Glow.gif

✅ DASHBOARDS:
  • Supersonic_Dashboard.html
  • Supersonic_QR_Trace.png

✅ VERIFICATION CARDS:
  • SonicBuilder/docs/Supersonic_Verification_Card.pdf
  • SonicBuilder/docs/Supersonic_Verification_Card_Double.pdf
  • SonicBuilder/docs/Supersonic_QR_Field.png

✅ FIELD KIT:
  • SonicBuilder/docs/Supersonic_FieldKit_v3.2.1.zip
  • SonicBuilder/docs/MANIFEST.json
  • SonicBuilder/docs/readme.html
  • SonicBuilder/docs/autorun.inf

✅ BUILD LOG:
  • SonicBuilder/build_log.txt
```

---

## 🔧 Dependencies

**Required:**
- Python 3.10+
- reportlab (PDFs)
- Pillow (Banners)
- segno (QR codes)

**Optional:**
- requests (GitHub API upload)
- PyGithub (Advanced GitHub integration)

**Install:**
```bash
pip install reportlab pillow segno requests PyGithub
```

Or use the requirements file:
```bash
pip install -r supersonic_requirements.txt
```

---

## 🎯 Use Cases

### Team Distribution
1. Generate Field Kit
2. Share ZIP with team
3. USB autorun provides instant access

### GitHub Repository
1. Add banners to README
2. Use dashboards for documentation
3. Automated releases with cards

### Field Operations
1. Laminate verification cards
2. Print double-sided wiring reference
3. QR trace for authenticity

### Presentations
1. Use animated glow banner
2. Display live dashboard
3. Show build traceability

---

**Complete documentation for all 13 presentation and verification tools!** 🚀

---

**See also:**
- `SUPERSONIC_TOOLS.md` — Main tool documentation
- `SUPERSONIC_GITHUB_SETUP.md` — Repository setup guide
- `SUPERSONIC_COMPLETE.md` — Full system overview
