# SonicBuilder Complete Integration Guide
## SB_REPO_URL Workflow System with Build Tools

This guide covers the complete integration of the SB_REPO_URL system including CoA generation, manual builds, two-up raster, and QR gallery tools.

---

## 📦 What's Integrated

### 1. **URL Management System**
- Reusable workflow: `.github/workflows/repo-url-setup.yml`
- Auto-detects GitHub vs Replit environment
- Provides `SB_REPO_URL` to all workflows

### 2. **CoA Generator** (Certificate of Authenticity)
- Auto-increment serial numbers
- QR code integration
- Dark-themed professional certificates
- CSV audit logging
- Workflow: `.github/workflows/coa-on-release.yml`

### 3. **Manual Build Workflow**
- Workflow: `.github/workflows/manual-build.yml`
- Builds PDF manuals with SB_REPO_URL metadata
- Runs on push to main or manual dispatch

### 4. **Two-Up Rasterizer**
- Script: `scripts/two_up_raster.py`
- Creates 2-up laminated field cards
- Adds footer with SB_REPO_URL
- Optional QR code in corner

### 5. **QR Gallery Generator**
- Script: `scripts/qr_gallery.py`
- Generates printable QR code sheet
- Links to manuals, parts, wiring, firmware
- Uses SB_REPO_URL as base

### 6. **Makefile Integration**
- Fragment: `make_patches/MAKEFRAG.urls`
- Fragment: `make_patches/MAKEFRAG.two_up_qr`
- Exposes SB_REPO_URL to all build targets

---

## 🌐 URL Resolution Chain

```
1. CLI --qr flag               [Highest Priority]
   ↓
2. Environment: SB_REPO_URL
   ↓
3. Environment: GITHUB_REPOSITORY → https://github.com/<owner>/<repo>
   ↓
4. Replit Domain (current)
   08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev
   ↓
5. Default: https://example.com/sonicbuilder
```

---

## 🚀 Quick Start

### Check SB_REPO_URL
```bash
make echo-url
# Output: Using SB_REPO_URL=https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev
```

### Generate CoA
```bash
cd tools/CoA_Generator
python generate_coa.py --auto-increment --version v2.5.0
```

### Build Two-Up Field Card
```bash
make two_up
# Output: dist/two_up_field_card.pdf (with QR code)
```

### Generate QR Gallery
```bash
make qr_gallery
# Output: Parts_Index/QR_Gallery.pdf
```

---

## 📁 File Structure

```
SonicBuilder/
├── .github/workflows/
│   ├── repo-url-setup.yml      ← Reusable URL detection
│   ├── coa-on-release.yml      ← Auto-mint CoA on release
│   ├── manual-build.yml        ← Build manuals with SB_REPO_URL
│   ├── release.yml
│   ├── sonicbuilder-ci.yml
│   └── ...
│
├── config/
│   └── repo_urls.json          ← URL configuration
│
├── docs/
│   ├── GITHUB_WORKFLOWS.md           ← Workflow reference
│   ├── USING_SB_REPO_URL.md          ← URL usage guide
│   ├── WIRE_SB_REPO_URL_MANUAL.md    ← Manual build integration
│   ├── TWOUP_QRGALLERY_SBURL.md      ← Two-up & QR gallery
│   └── COMPLETE_INTEGRATION_GUIDE.md ← This file
│
├── make_patches/
│   ├── MAKEFRAG.urls           ← URL exposure
│   └── MAKEFRAG.two_up_qr      ← Two-up & QR gallery targets
│
├── scripts/
│   ├── two_up_raster.py        ← 2-up field card generator
│   ├── qr_gallery.py           ← QR code gallery
│   └── ...
│
├── tools/CoA_Generator/
│   ├── generate_coa.py         ← QR-ready CoA generator
│   ├── CoA_Log.csv             ← Audit trail
│   ├── README_QR_PATCH.md      ← QR configuration
│   └── output/                 ← Generated certificates
│
└── Makefile                    ← Includes MAKEFRAG.urls & MAKEFRAG.two_up_qr
```

---

## 🔧 Makefile Targets

### Core Targets
```bash
make echo-url          # Show current SB_REPO_URL
make build_dark        # Build dark manual
make build_light       # Build light manual
make release_local     # Full release build
```

### New Targets (from MAKEFRAG.two_up_qr)
```bash
make two_up           # Generate 2-up field card with QR
make qr_gallery       # Generate QR code gallery sheet
```

### CoA Targets
```bash
cd tools/CoA_Generator
python generate_coa.py --auto-increment        # Auto serial
python generate_coa.py --serial 0042           # Manual serial
```

---

## 🎯 Development Workflow

### On Replit (Current)
```bash
# 1. Check URL
make echo-url
# Using SB_REPO_URL=https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev

# 2. Generate CoA
cd tools/CoA_Generator
python generate_coa.py --auto-increment --version v2.5.0
# QR code points to Replit domain

# 3. Build two-up card
cd ../..
make two_up
# Footer shows Replit URL, QR code included

# 4. Generate QR gallery
make qr_gallery
# All QR codes use Replit domain as base
```

### On GitHub (After Push)
```bash
# 1. Push to GitHub
git push origin main

# 2. Workflows run automatically
# - repo-url-setup.yml detects GitHub repository
# - SB_REPO_URL = https://github.com/<owner>/<repo>

# 3. Create release
git tag v2.5.1
git push origin v2.5.1
# - coa-on-release.yml auto-generates CoA
# - QR code points to GitHub repository

# 4. Manual build triggered
# - manual-build.yml builds PDFs
# - All metadata uses GitHub URL
```

### Custom Domain (Production)
```bash
# Set environment variable
export SB_REPO_URL="https://sonicbuilder.io"

# All tools use custom domain
make echo-url           # → https://sonicbuilder.io
make two_up             # → Footer: sonicbuilder.io
make qr_gallery         # → Base: sonicbuilder.io
```

---

## 📊 Example Outputs

### CoA Certificate (#0006)
```
Serial:   #0006
Version:  v2.5.0
Customer: SB_REPO_URL Test Build
Installer: Christopher Elgin
QR URL:   https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev
File:     tools/CoA_Generator/output/SonicBuilder_CoA_#0006.pdf
```

### Two-Up Field Card
```
Input:  QuickStart_Field_Card.pdf
Output: dist/two_up_field_card.pdf
Layout: 2 cards stacked vertically on Letter page
Footer: SonicBuilder • https://08abbd3d.../
QR:     Bottom-right corner (optional)
```

### QR Gallery
```
Output:     Parts_Index/QR_Gallery.pdf
Layout:     3x3 grid of QR codes
Base URL:   https://08abbd3d.../
Links:      manuals, latest, parts, wiring, firmware
QR Codes:   9 printable codes with labels
```

---

## 🔄 GitHub Workflows

### repo-url-setup.yml (Reusable)
**Purpose:** Detects and exports SB_REPO_URL

**Usage:**
```yaml
jobs:
  setup-url:
    uses: ./.github/workflows/repo-url-setup.yml
  
  your-job:
    needs: [setup-url]
    env:
      SB_REPO_URL: ${{ needs.setup-url.outputs.SB_REPO_URL }}
```

### coa-on-release.yml
**Trigger:** Release published  
**Actions:**
1. Calls repo-url-setup.yml
2. Reads VERSION.txt
3. Generates CoA with auto-increment
4. Commits to repository
5. Uploads PDF to release assets

### manual-build.yml
**Trigger:** Push to main, manual dispatch  
**Actions:**
1. Calls repo-url-setup.yml
2. Installs Python dependencies
3. Runs `make build_dark` with SB_REPO_URL
4. Uploads artifacts

---

## 🛠️ Advanced Usage

### Override URL Per-Command
```bash
SB_REPO_URL="https://custom.url" make two_up
SB_REPO_URL="https://custom.url" make qr_gallery
SB_REPO_URL="https://custom.url" python generate_coa.py --auto-increment
```

### Custom QR Gallery Links
```bash
python scripts/qr_gallery.py \
  --out dist/custom_qr.pdf \
  --base "https://sonicbuilder.io" \
  --links \
    "docs=/docs" \
    "support=/support" \
    "shop=/shop"
```

### Two-Up Without QR
```bash
python scripts/two_up_raster.py \
  --in QuickStart_Field_Card.pdf \
  --out dist/two_up_no_qr.pdf
# No --qr flag = no QR code
```

---

## 📝 Configuration

### config/repo_urls.json
```json
{
  "preferred": "env:SB_REPO_URL",
  "fallbacks": [
    "env:GITHUB_REPOSITORY_URL",
    "https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev"
  ],
  "notes": "Edit SB_REPO_URL when you move to GitHub."
}
```

### Makefile Fragments
**make_patches/MAKEFRAG.urls:**
- Defines SB_REPO_URL with Replit default
- Provides `echo-url` target

**make_patches/MAKEFRAG.two_up_qr:**
- Defines `two_up` target
- Defines `qr_gallery` target
- Uses SB_REPO_URL automatically

---

## 🔍 Troubleshooting

### Wrong URL in QR Codes
**Problem:** QR shows Replit domain instead of GitHub  
**Solution:** Ensure GitHub workflow includes repo-url-setup:
```yaml
jobs:
  setup-url:
    uses: ./.github/workflows/repo-url-setup.yml
```

### Makefile Syntax Errors
**Problem:** `Makefile:X: *** missing separator`  
**Solution:** Makefiles require TABS, not spaces. Check MAKEFRAG files.

### Missing Dependencies
**Problem:** `ModuleNotFoundError: No module named 'qrcode'`  
**Solution:** Install dependencies:
```bash
pip install reportlab qrcode pillow pdf2image
```

### Two-Up Fails
**Problem:** `convert_from_path` fails  
**Solution:** Install poppler-utils:
```bash
# On Replit, already installed
# Locally: apt-get install poppler-utils
```

---

## ✅ Verification Checklist

### Local Development
- [ ] `make echo-url` shows Replit domain
- [ ] CoA generates with Replit QR code
- [ ] Two-up builds successfully
- [ ] QR gallery creates PDF

### GitHub Integration
- [ ] Push to GitHub repository
- [ ] `repo-url-setup.yml` workflow exists
- [ ] Create test release
- [ ] Verify CoA auto-generated
- [ ] Check QR code uses GitHub URL

### Production Ready
- [ ] Set SB_REPO_URL to custom domain
- [ ] Test all make targets
- [ ] Verify QR codes point to production
- [ ] Update documentation

---

## 📚 Related Documentation

- `docs/GITHUB_WORKFLOWS.md` - Complete workflow reference
- `docs/USING_SB_REPO_URL.md` - URL usage patterns
- `docs/WIRE_SB_REPO_URL_MANUAL.md` - Manual build integration
- `docs/TWOUP_QRGALLERY_SBURL.md` - Two-up & QR gallery details
- `tools/CoA_Generator/README_QR_PATCH.md` - CoA QR configuration

---

## 🎉 Summary

Your SonicBuilder platform now has:

✅ **URL Management**
- Auto-detection: GitHub → Replit → Custom
- Consistent across all tools

✅ **CoA System**
- Auto-increment serial numbers
- QR codes with smart URLs
- CSV audit logging
- GitHub workflow automation

✅ **Build Tools**
- Manual builds with metadata
- Two-up field cards
- QR gallery sheets
- Makefile integration

✅ **Documentation**
- Complete workflow guides
- Usage examples
- Troubleshooting help

**Current Status:**
- Replit Domain: ✅ Configured
- GitHub Ready: ✅ Workflows installed
- Production Ready: ⏳ Set SB_REPO_URL when deployed

**Next Steps:**
1. Keep developing on Replit (Replit domain)
2. Push to GitHub (auto-switches to GitHub URLs)
3. Set custom domain for production (sonicbuilder.io)

---

**The entire system works seamlessly across all environments!** 🚀
