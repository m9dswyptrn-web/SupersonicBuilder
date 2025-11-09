# Version Bump & URL Management Integration
**Date:** October 28, 2025  
**Version:** v2.0.8 → v2.0.9 automation ready

---

## 🎉 Complete Automation Suite

Your SonicBuilder platform now has complete version bumping and URL management automation!

---

## 📦 New Components

### 1. **URL Management** (`scripts/repo_url.py`)
Single source of truth for repository URL resolution:

```python
from repo_url import resolve

url = resolve()  # Auto-detects GitHub > Replit > fallback
```

**Priority:**
1. CLI-provided URL (explicit argument)
2. `SB_REPO_URL` environment variable
3. `GITHUB_REPOSITORY` env → `https://github.com/<owner>/<repo>`
4. Replit fallback: `https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev`

### 2. **PDF Metadata Stamper** (`scripts/pdf_meta_stamp.py`)
Stamps PDFs with version, URL, and date metadata:

```bash
python scripts/pdf_meta_stamp.py \
  --in output/manual.pdf \
  --out output/manual_stamped.pdf \
  --version v2.0.9
```

**Metadata Added:**
- `/SonicBuilderURL` - Canonical repository URL
- `/SonicBuilderVersion` - Version string (e.g., v2.0.9)
- `/SonicBuilderDate` - ISO date (e.g., 2025-10-28)
- `/Subject` - "SonicBuilder — v2.0.9"
- `/Keywords` - "SonicBuilder,v2.0.9,<URL>"

### 3. **Version Bumper** (`scripts/version_bump.py`)
Bumps version strings across entire repository:

```bash
python scripts/version_bump.py \
  --from v2.0.8 \
  --to v2.0.9 \
  --root .
```

**What It Updates:**
- `VERSION` file
- `Founder_Seal/SonicBuilder_Seal.svg` (version text)
- All text files: `.md`, `.txt`, `.yml`, `.yaml`, `.json`, `.csv`, `.py`
- Replaces old version string with new version everywhere

### 4. **Makefile Targets** (`make_patches/MAKEFRAG.repo`)
New make targets for version and metadata operations:

```makefile
-include make_patches/MAKEFRAG.repo
```

**Available Targets:**
```bash
make bump FROM=v2.0.8 TO=v2.0.9
make stamp_meta VERSION=v2.0.9 IN=manual.pdf OUT=manual_stamped.pdf
```

### 5. **Auto-Bump Workflow** (`.github/workflows/version-bump-on-appendix.yml`)
Automatically bumps to v2.0.9 when files are added to:
- `Wiring_Diagrams/PCB_Photos/**`
- `Wiring_Diagrams/I2S_Taps/**`

**Workflow:**
1. Detects file changes in monitored directories
2. Runs `python scripts/version_bump.py --from v2.0.8 --to v2.0.9`
3. Updates `VERSION` file to `v2.0.9`
4. Commits changes to repository
5. Pushes to main branch

---

## 🚀 Quick Start

### Test URL Resolution
```bash
python3 -c "import sys; sys.path.insert(0, 'scripts'); from repo_url import resolve; print(resolve())"
# Output: https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev
```

### Bump Version
```bash
# Dry run first
make bump FROM=v2.0.8 TO=v2.0.9 --dry-run

# Actually bump
make bump FROM=v2.0.8 TO=v2.0.9
```

### Stamp PDF Metadata
```bash
make stamp_meta VERSION=v2.0.9 IN=output/manual.pdf OUT=output/manual_v2.0.9.pdf
```

### Trigger Auto-Bump (GitHub)
```bash
# Add a PCB photo
cp photo.jpg Wiring_Diagrams/PCB_Photos/
git add Wiring_Diagrams/PCB_Photos/photo.jpg
git commit -m "docs: add PCB installation photo"
git push
# Workflow automatically bumps to v2.0.9!
```

---

## 🔧 Integration with Existing Tools

### CoA Generator
```bash
cd tools/CoA_Generator
python generate_coa.py --auto-increment --version v2.0.9
# Automatically uses repo_url.resolve() for QR code
```

### Two-Up Raster
```bash
make two_up
# Footer uses SB_REPO_URL from repo_url.resolve()
```

### QR Gallery
```bash
make qr_gallery
# All QR codes use canonical URL from repo_url.resolve()
```

---

## 📁 Directory Structure

```
SonicBuilder/
├── .github/workflows/
│   ├── version-bump-on-appendix.yml  ← NEW: Auto-bump workflow
│   ├── repo-url-setup.yml            ← URL detection
│   ├── manual-build.yml              ← Manual builds
│   └── coa-on-release.yml            ← CoA generation
│
├── docs/
│   ├── URL_MANAGEMENT.md             ← NEW: URL resolution guide
│   ├── VERSIONING_AUTOMATION.md      ← NEW: Version bump guide
│   ├── VERSION_BUMP_INTEGRATION.md   ← NEW: This file
│   ├── COMPLETE_INTEGRATION_GUIDE.md
│   └── ...
│
├── make_patches/
│   ├── MAKEFRAG.urls                 ← URL exposure
│   ├── MAKEFRAG.repo                 ← NEW: bump & stamp_meta targets
│   └── MAKEFRAG.two_up_qr            ← Two-up & QR gallery
│
├── scripts/
│   ├── repo_url.py                   ← NEW: URL resolver (single source)
│   ├── pdf_meta_stamp.py             ← NEW: PDF metadata stamper
│   ├── version_bump.py               ← NEW: Version bumper
│   ├── two_up_raster.py              ← Two-up card generator
│   └── qr_gallery.py                 ← QR gallery generator
│
├── Wiring_Diagrams/
│   ├── PCB_Photos/                   ← NEW: Monitored directory
│   │   └── README.md                 ← Auto-bump trigger
│   └── I2S_Taps/                     ← NEW: Monitored directory
│       └── README.md                 ← Auto-bump trigger
│
├── Makefile                          ← Includes MAKEFRAG.repo
└── VERSION                           ← Current: v2.0.8
```

---

## 🌐 Complete URL Flow

### 1. Development (Replit)
```bash
make echo-url
# Using SB_REPO_URL=https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev

python3 -c "from scripts.repo_url import resolve; print(resolve())"
# https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev
```

### 2. GitHub Actions
```yaml
- name: Set URL
  run: |
    echo "GITHUB_REPOSITORY=${{ github.repository }}"
    # Sets SB_REPO_URL to https://github.com/<owner>/<repo>
```

### 3. Production
```bash
export SB_REPO_URL="https://sonicbuilder.io"
python3 -c "from scripts.repo_url import resolve; print(resolve())"
# https://sonicbuilder.io
```

---

## 🔄 Version Bump Workflow

### Manual Bump
```bash
# 1. Check current version
cat VERSION
# v2.0.8

# 2. Bump to v2.0.9
make bump FROM=v2.0.8 TO=v2.0.9

# 3. Verify changes
cat VERSION
# v2.0.9

git diff Founder_Seal/SonicBuilder_Seal.svg
# See version updated in SVG
```

### Automatic Bump (GitHub)
```bash
# 1. Add PCB photo or I²S tap documentation
cp new_pcb_photo.jpg Wiring_Diagrams/PCB_Photos/

# 2. Commit and push
git add Wiring_Diagrams/PCB_Photos/new_pcb_photo.jpg
git commit -m "docs: add new PCB installation photo"
git push

# 3. GitHub Actions workflow runs automatically:
#    - Detects file in PCB_Photos/
#    - Runs version_bump.py --from v2.0.8 --to v2.0.9
#    - Updates VERSION file
#    - Commits changes
#    - Pushes to repository

# 4. Your repository is now on v2.0.9!
```

---

## 📊 What Gets Updated During Bump

### Version Bump (v2.0.8 → v2.0.9)

**Files Updated:**
- `VERSION` - Updated to `v2.0.9`
- `Founder_Seal/SonicBuilder_Seal.svg` - Version text updated
- `README.md` - Any v2.0.8 references → v2.0.9
- `docs/*.md` - Documentation version references
- `.github/workflows/*.yml` - Workflow version references
- `tools/CoA_Generator/CoA_Log.csv` - Version references in log
- Any `.txt`, `.json`, `.yaml`, `.py`, `.md` files containing "v2.0.8"

**What's NOT Updated:**
- Binary files (PDFs, images)
- Large files (>10MB)
- Hidden files (unless explicitly matched)
- Git history

---

## 🎯 Common Workflows

### Release v2.0.9 with Full Automation
```bash
# 1. Bump version
make bump FROM=v2.0.8 TO=v2.0.9

# 2. Build manuals
make build_dark
make build_light

# 3. Stamp metadata
make stamp_meta VERSION=v2.0.9 IN=output/manual_dark.pdf OUT=output/manual_dark_v2.0.9.pdf
make stamp_meta VERSION=v2.0.9 IN=output/manual_light.pdf OUT=output/manual_light_v2.0.9.pdf

# 4. Generate CoA
cd tools/CoA_Generator
python generate_coa.py --auto-increment --version v2.0.9
cd ../..

# 5. Create two-up cards
make two_up

# 6. Generate QR gallery
make qr_gallery

# 7. Package release
make release_local

# 8. Commit and tag
git add -A
git commit -m "chore: release v2.0.9"
git tag v2.0.9
git push origin main v2.0.9
```

### Update Documentation, Trigger Auto-Bump
```bash
# 1. Add documentation to monitored directory
cp i2s_tap_diagram.png Wiring_Diagrams/I2S_Taps/

# 2. Commit and push
git add Wiring_Diagrams/I2S_Taps/i2s_tap_diagram.png
git commit -m "docs: add I²S tap point diagram"
git push

# 3. Workflow runs automatically:
#    ✅ Bumps to v2.0.9
#    ✅ Updates VERSION file
#    ✅ Updates Founder_Seal SVG
#    ✅ Commits changes
#    ✅ Pushes to repository

# Done! Your project is now v2.0.9
```

---

## 🛠️ Advanced Usage

### Custom URL Override
```bash
# Override URL for specific operation
SB_REPO_URL="https://custom.domain" python scripts/pdf_meta_stamp.py \
  --in manual.pdf \
  --out manual_custom.pdf \
  --version v2.0.9
```

### Stamp Multiple PDFs
```bash
for pdf in output/*.pdf; do
  make stamp_meta VERSION=v2.0.9 IN="$pdf" OUT="${pdf%.pdf}_v2.0.9.pdf"
done
```

### Conditional Bump (Only if Not Already v2.0.9)
```bash
current=$(cat VERSION)
if [ "$current" != "v2.0.9" ]; then
  make bump FROM="$current" TO=v2.0.9
else
  echo "Already on v2.0.9"
fi
```

---

## ✅ Verification

### Test URL Resolution
```bash
python3 -c "import sys; sys.path.insert(0, 'scripts'); from repo_url import resolve; print('URL:', resolve())"
# Expected: https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev
```

### Test Version Bump (Dry Run)
```bash
python scripts/version_bump.py --from v2.0.8 --to v2.0.9 --root . --dry-run
# Shows what would be changed without actually changing
```

### Test PDF Metadata Stamping
```bash
# Create a test PDF first
make build_dark

# Stamp it
make stamp_meta VERSION=v2.0.9 IN=output/manual_dark.pdf OUT=output/test_stamped.pdf

# Verify metadata
pdfinfo output/test_stamped.pdf | grep SonicBuilder
# Should show: SonicBuilderURL, SonicBuilderVersion, SonicBuilderDate
```

---

## 🔍 Troubleshooting

### Version Bump Doesn't Update Seal SVG
**Problem:** Founder seal still shows old version  
**Solution:** Check seal path in `scripts/version_bump.py`:
```python
SEAL_PATH = Path("Founder_Seal/SonicBuilder_Seal.svg")
```

### Auto-Bump Workflow Doesn't Trigger
**Problem:** Pushing to PCB_Photos/ doesn't trigger workflow  
**Solution:** 
1. Check workflow file exists: `.github/workflows/version-bump-on-appendix.yml`
2. Verify paths in workflow match your directory structure
3. Ensure workflow has `contents: write` permission

### PDF Metadata Missing
**Problem:** Stamped PDF doesn't show SonicBuilder metadata  
**Solution:** Verify pypdf installed:
```bash
pip install pypdf
python scripts/pdf_meta_stamp.py --in test.pdf --version v2.0.9
```

### Wrong URL in Metadata
**Problem:** PDF shows Replit URL instead of GitHub  
**Solution:** Set environment variable:
```bash
export SB_REPO_URL="https://github.com/<owner>/<repo>"
make stamp_meta VERSION=v2.0.9 IN=manual.pdf
```

---

## 📚 Related Documentation

- `docs/URL_MANAGEMENT.md` - URL resolution system
- `docs/VERSIONING_AUTOMATION.md` - Version bump automation
- `docs/COMPLETE_INTEGRATION_GUIDE.md` - Full integration overview
- `docs/GITHUB_WORKFLOWS.md` - GitHub Actions reference

---

## 🎉 Summary

Your SonicBuilder platform now has:

✅ **Single Source URL Management**
- `scripts/repo_url.py` resolves canonical URL
- All tools use same URL source
- Automatic GitHub/Replit detection

✅ **Version Bumping Automation**
- Manual: `make bump FROM=v2.0.8 TO=v2.0.9`
- Automatic: Push to PCB_Photos/ or I2S_Taps/
- Updates VERSION, SVG, and all text files

✅ **PDF Metadata Stamping**
- `make stamp_meta` adds version/URL/date
- Preserves existing metadata
- Professional document tracking

✅ **Complete Integration**
- Works with CoA generator
- Works with two-up rasterizer
- Works with QR gallery
- Works with all existing tools

---

**Your complete version management and URL resolution system is ready!** 🚀

Current version: **v2.0.8**  
Ready to bump to: **v2.0.9**

Use `make bump FROM=v2.0.8 TO=v2.0.9` to upgrade!
