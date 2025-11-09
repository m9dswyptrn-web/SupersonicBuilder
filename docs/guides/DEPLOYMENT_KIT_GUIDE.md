# 📦 SonicBuilder Deployment Kit & Advanced Features

**Complete deployment packaging, theme switching, and automated badge updates**

---

## ✅ What's Been Added

### **1. DeployKit Packaging** 📦

**Purpose:** Package entire project into a self-contained deployment ZIP

**Features:**
- ✅ Full source code (excluding build artifacts)
- ✅ Environment template for secrets
- ✅ Quick start instructions
- ✅ Ready for local or Replit deployment

**Command:**
```bash
make package_deploykit
```

**Output:**
```
dist/SonicBuilder_Complete_DeployKit_v1_20250130T183522Z.zip
```

**Files:**
- `scripts/pack_deploykit.sh` - DeployKit packaging script
- `scripts/git_auto_commit.sh` - Auto-commit helper

---

### **2. Theme Switch & PDF Previews** 🎨

**Purpose:** Generate preview PDFs with limited pages for quick review

**Features:**
- ✅ Build dark or light theme previews
- ✅ Configurable page limit (default: 6 pages)
- ✅ Preserves full PDF builds
- ✅ Fast iteration for design changes

**Commands:**
```bash
# Build dark theme preview (first 6 pages)
make build_dark_preview

# Build light theme preview (first 6 pages)
make build_light_preview

# Custom page count
make build_dark_preview PREVIEW_PAGES=10
```

**Output:**
```
dist/preview/SonicBuilder_Manual_v2.2.3_g12ab34cd_dark_preview.pdf
```

**Files:**
- `scripts/tools/pdf_slice.py` - PDF page slicer

---

### **3. README Badge Auto-Updater** 📛

**Purpose:** Automatically update README badges with latest version and commit

**Features:**
- ✅ Updates version-specific download links
- ✅ Updates commit hashes
- ✅ Updates GitHub Pages URLs
- ✅ Preserves badge formatting

**Command:**
```bash
make badges
```

**What it updates:**
```markdown
<!-- DOCS-BADGES:BEGIN -->
<p align="center">
  <a href="https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/docs-build.yml">
    <img alt="Docs Build" src="https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/docs-build.yml?label=Docs%20Build&logo=github">
  </a>
  <a href="https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/docs-release.yml">
    <img alt="Docs Release" src="https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/docs-release.yml?label=Docs%20Release&logo=github">
  </a>
  <a href="https://github.com/m9dswyptrn-web/SonicBuilder/releases/latest">
    <img alt="Latest Release" src="https://img.shields.io/github/v/release/m9dswyptrn-web/SonicBuilder?display_name=tag&logo=github">
  </a>
</p>
<p align="center">
  <a href="https://m9dswyptrn-web.github.io/SonicBuilder/?theme=dark">
    <img alt="Open Docs (Dark)" src="https://img.shields.io/badge/docs-dark-111111?logo=readthedocs&logoColor=white">
  </a>
  <a href="https://m9dswyptrn-web.github.io/SonicBuilder/?theme=light">
    <img alt="Open Docs (Light)" src="https://img.shields.io/badge/docs-light-f6f8fa?logo=readthedocs&logoColor=000">
  </a>
  <a href="https://github.com/m9dswyptrn-web/SonicBuilder/releases/download/v2.2.3/SonicBuilder_Manual_v2.2.3_g12ab34cd.zip">
    <img alt="Download PDF Bundle" src="https://img.shields.io/badge/download-PDF_bundle-4c9aff?logo=adobeacrobatreader">
  </a>
</p>
<!-- DOCS-BADGES:END -->
```

**Files:**
- `scripts/update_readme_docs_badges.py` - Badge updater script

---

### **4. Docs Bundle Status Badge** 🎯

**Purpose:** Monitor whether releases contain expected PDF bundle

**Features:**
- ✅ Checks latest release for PDF bundle
- ✅ Validates filename pattern
- ✅ Auto-updates via GitHub Actions
- ✅ Daily refresh

**Badge States:**
- 🟢 **Green:** Bundle present (`v2.2.3 ✓`)
- 🔴 **Red:** Bundle missing (`v2.2.3 missing`)

**Badge URL:**
```markdown
<a href="https://github.com/m9dswyptrn-web/SonicBuilder/releases/latest">
  <img alt="Docs Bundle Status"
       src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/docs_bundle_status.json">
</a>
```

**Files:**
- `scripts/check_release_bundle.py` - Bundle checker script
- `.github/workflows/docs-bundle-badge.yml` - Auto-update workflow

---

## 🚀 Complete Workflow

### **Development Workflow**

```bash
# 1. Make changes to documentation

# 2. Build preview PDFs (fast iteration)
make build_dark_preview PREVIEW_PAGES=6

# 3. Review preview
open dist/preview/*.pdf

# 4. Build full PDFs
make build_dark
make build_light

# 5. Update README badges
make badges

# 6. Package DeployKit
make package_deploykit

# 7. Deploy everything
make ship
```

---

### **Release Workflow**

```bash
# 1. Bump version
echo "v2.3.0" > VERSION

# 2. Build all artifacts
make build_dark
make build_light

# 3. Update badges
make badges

# 4. Commit and tag
git add -A
git commit -m "release: v2.3.0"
git tag v2.3.0

# 5. Deploy
make ship

# This triggers:
# - GitHub Actions builds PDFs
# - Creates release with bundles
# - Updates all badges
# - Deploys to GitHub Pages
# - Runs smoke tests
```

---

## 📦 DeployKit Usage

### **Creating a DeployKit**

```bash
make package_deploykit
```

**Output:**
```
dist/SonicBuilder_Complete_DeployKit_v1_20250130T183522Z.zip
```

**Contents:**
```
SonicBuilder_Complete_DeployKit_v1_20250130T183522Z.zip
├── src/                    # Full project source
├── ENV_TEMPLATE            # Environment variables template
└── DEPLOYKIT_README.md     # Quick start guide
```

---

### **Using DeployKit (Local)**

```bash
# 1. Extract ZIP
unzip SonicBuilder_Complete_DeployKit_v1_*.zip
cd src/

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp ../ENV_TEMPLATE .env
# Edit .env and add:
#   GIT_USER_NAME=your-name
#   GIT_USER_EMAIL=your@email.com
#   GH_TOKEN=your-github-token

# 5. Initialize
make init

# 6. Deploy
make ship
```

---

### **Using DeployKit (Replit)**

```bash
# 1. Upload ZIP to Replit
# 2. Extract in shell:
unzip SonicBuilder_Complete_DeployKit_v1_*.zip

# 3. Add GH_TOKEN to Replit Secrets

# 4. Deploy
make ship
```

---

## 🎨 PDF Preview System

### **Why Use Previews?**

- ✅ **Fast iteration** - Build only first 6 pages
- ✅ **Quick review** - Check styling without full build
- ✅ **Save time** - Preview builds in seconds vs minutes
- ✅ **Theme testing** - Compare dark/light themes quickly

---

### **Preview Commands**

```bash
# Dark theme preview
make build_dark_preview

# Light theme preview  
make build_light_preview

# Custom page count
make build_dark_preview PREVIEW_PAGES=3
make build_light_preview PREVIEW_PAGES=10

# Just slice existing PDFs
make slice_preview PREVIEW_PAGES=5
```

---

### **Preview Output**

```
dist/preview/
├── SonicBuilder_Manual_v2.2.3_g12ab34cd_dark_preview.pdf (6 pages)
└── SonicBuilder_Manual_v2.2.3_g12ab34cd_light_preview.pdf (6 pages)
```

Compare to full builds:
```
dist/
├── SonicBuilder_Manual_v2.2.3_g12ab34cd_dark.pdf (150 pages)
└── SonicBuilder_Manual_v2.2.3_g12ab34cd_light.pdf (150 pages)
```

---

## 📛 Automatic Badge Updates

### **How It Works**

1. **Script runs** - `update_readme_docs_badges.py`
2. **Reads current state** - VERSION file + git commit
3. **Updates README** - Rewrites DOCS-BADGES block
4. **Stages changes** - `git add README.md`

---

### **When Badges Update**

**Automatically:**
- After release creation (via GitHub Actions)
- When you run `make badges`
- Integrated into deployment workflow

**Manual:**
```bash
make badges
git commit -m "docs: update badges"
git push
```

---

### **Badge Block Format**

Add this to your `README.md`:

```markdown
<!-- DOCS-BADGES:BEGIN -->
<!-- Content auto-generated by scripts/update_readme_docs_badges.py -->
<!-- DOCS-BADGES:END -->
```

The script will populate the content between markers.

---

## 🎯 Bundle Status Monitoring

### **What It Checks**

The bundle checker validates:
- ✅ Latest release exists
- ✅ Contains ZIP file matching pattern: `SonicBuilder_Manual_v*.*.* _g<commit>.zip`
- ✅ Filename includes version tag
- ✅ Filename includes git commit hash

---

### **Workflow Triggers**

- On release publish/edit
- Daily at 3:17 AM UTC (cron)
- Manual dispatch

---

### **Integration Example**

Add validation to your release workflow:

```yaml
- name: Validate release contains bundle
  env:
    OWNER: ${{ github.repository_owner }}
    REPO:  ${{ github.event.repository.name }}
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python3 scripts/check_release_bundle.py
    jq -e '.color == "brightgreen"' docs/status/docs_bundle_status.json >/dev/null || {
      echo "::error title=Bundle Missing::Release missing docs bundle"
      exit 1
    }
```

---

## 📊 Complete Badge Suite

You now have **5 status badges**:

1. **Docs Coverage Badge** 📚 - Dark/Light PDF presence
2. **Pages Smoke Badge** 🧪 - Gallery availability
3. **Docs Smoke Test Badge** ✅ - Workflow status
4. **Docs Bundle Badge** 🎯 - Release bundle validation
5. **Dynamic README Badges** 📛 - Version/commit-specific

---

## 🗂️ Updated File Structure

```
SonicBuilder/
├── scripts/
│   ├── pack_deploykit.sh              # NEW: DeployKit packager
│   ├── git_auto_commit.sh             # NEW: Auto-commit helper
│   ├── update_readme_docs_badges.py   # NEW: Badge updater
│   ├── check_release_bundle.py        # NEW: Bundle checker
│   └── tools/
│       └── pdf_slice.py               # NEW: PDF page slicer
├── .github/workflows/
│   └── docs-bundle-badge.yml          # NEW: Bundle badge workflow
├── Makefile                            # Updated with new targets
└── dist/
    ├── preview/                        # Generated previews
    └── SonicBuilder_Complete_DeployKit_v1_*.zip  # Generated kit
```

---

## 🎯 New Makefile Targets

```bash
# DeployKit
make package_deploykit          # Create deployment package

# PDF Previews
make build_dark_preview         # Build dark preview (6 pages)
make build_light_preview        # Build light preview (6 pages)
make slice_preview              # Slice existing PDFs

# Badges
make badges                     # Update README badges
```

---

## ✅ Verification

Test all new features:

```bash
# 1. Test PDF preview
make build_dark_preview
ls dist/preview/

# 2. Test badge updater
make badges
git diff README.md

# 3. Test DeployKit packaging
make package_deploykit
ls dist/*.zip

# 4. Test bundle checker (requires GitHub token)
export GITHUB_TOKEN=your-token
python3 scripts/check_release_bundle.py
cat docs/status/docs_bundle_status.json
```

---

## 🚀 Ready to Deploy

Your complete infrastructure now includes:

✅ **4 Addons** - Gallery, Smoke Test, Coverage Badge, Smoke Badge  
✅ **DeployKit** - Self-contained deployment package  
✅ **PDF Previews** - Fast iteration workflow  
✅ **Auto Badges** - README always up-to-date  
✅ **Bundle Validation** - Release quality assurance  

Everything production-ready! 🎉

---

**Generated:** October 30, 2025  
**Version:** SonicBuilder Deployment Kit v1  
**Status:** ✅ Production Ready
