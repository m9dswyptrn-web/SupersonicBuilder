# 📛 SonicBuilder Badge Addons - Complete Installation

**Status Badges for Your GitHub README**

---

## ✅ What's Been Installed

### **1. Docs Coverage Badge Addon** 📚

**Purpose:** Shows whether your latest release includes both Dark and Light PDF bundles

**Files:**
- ✅ `scripts/check_docs_coverage.py` - Badge generator script
- ✅ `.github/workflows/docs-coverage-badge.yml` - Auto-update workflow
- ✅ `README_DocsCoverageBadge_Addon.txt` - Quick reference
- ✅ `Makefile` - Added `coverage-badge` target

**Badge Logic:**
- 🟢 **Green:** Both Dark + Light PDFs present in latest release
- 🟠 **Orange:** Only one PDF variant present
- 🔴 **Red:** No PDFs found

**Makefile Target:**
```bash
make coverage-badge
```

**Workflow Triggers:**
- When a release is published/edited
- Daily at 4:23 AM UTC (cron)
- Manual dispatch

---

### **2. Pages Smoke Badge Addon** 🧪

**Purpose:** Monitors your GitHub Pages gallery availability

**Files:**
- ✅ `scripts/pages_smoke_badge.py` - Smoke test badge script
- ✅ `.github/workflows/pages-smoke-badge.yml` - Auto-update workflow
- ✅ `README_PagesSmokeBadge_Addon.txt` - Quick reference
- ✅ `Makefile` - Added `pages-smoke-badge` target

**Badge Logic:**
- 🟢 **Green:** Both dark & light gallery URLs return HTTP 200
- 🟠 **Orange:** Only one URL is accessible
- 🔴 **Red:** Both URLs down

**Makefile Target:**
```bash
make pages-smoke-badge
```

**Workflow Triggers:**
- Every 30 minutes (cron: `*/30 * * * *`)
- Manual dispatch

---

## 🎯 How It Works

### **Badge System Architecture**

Both addons use the **Shields.io Endpoint Badge** system:

1. **GitHub Actions workflow** runs periodically
2. **Python script** checks status (release assets or HTTP availability)
3. **JSON file** written to `docs/status/` directory
4. **Shields.io** reads JSON from your repo
5. **Badge** displays in your README

### **JSON Badge Format**

Both scripts output Shields.io endpoint JSON:

```json
{
  "schemaVersion": 1,
  "label": "docs coverage",
  "message": "v2.2.3 dark+light",
  "color": "brightgreen",
  "labelColor": "2f363d"
}
```

**Colors:**
- `brightgreen` - All good
- `orange` - Partial/warning
- `red` - Problem/down

---

## 📊 Badge URLs

### **Docs Coverage Badge**

```markdown
<a href="https://github.com/m9dswyptrn-web/SonicBuilder/releases/latest">
  <img alt="Docs Coverage"
       src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/docs_coverage_status.json">
</a>
```

**Example Display:**  
![Docs Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/docs_coverage_status.json)

---

### **Pages Smoke Badge**

```markdown
<a href="https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html">
  <img alt="Pages Smoke"
       src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/pages_smoke_status.json">
</a>
```

**Example Display:**  
![Pages Smoke](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/pages_smoke_status.json)

---

## 🚀 Usage

### **Local Testing**

Generate badges manually:

```bash
# Test docs coverage badge
make coverage-badge
cat docs/status/docs_coverage_status.json

# Test pages smoke badge
make pages-smoke-badge
cat docs/status/pages_smoke_status.json
```

**Output:**
```json
{
  "tag": "v2.2.3",
  "has_dark": true,
  "has_light": true,
  "assets": [
    "SonicBuilder_Manual_v2.2.3_g12ab34cd_dark.zip",
    "SonicBuilder_Manual_v2.2.3_g12ab34cd_light.zip"
  ]
}
```

---

### **Automated Updates**

Both badges auto-update via GitHub Actions:

**Docs Coverage:**
- Triggers on release publish/edit
- Daily cron at 4:23 AM UTC
- Manual dispatch anytime

**Pages Smoke:**
- Every 30 minutes automatically
- Manual dispatch anytime

---

## 📁 File Locations

```
SonicBuilder/
├── scripts/
│   ├── check_docs_coverage.py      # Docs badge script
│   └── pages_smoke_badge.py        # Smoke badge script
├── .github/workflows/
│   ├── docs-coverage-badge.yml     # Docs badge workflow
│   └── pages-smoke-badge.yml       # Smoke badge workflow
├── docs/status/
│   ├── docs_coverage_status.json   # Docs badge JSON (auto-generated)
│   └── pages_smoke_status.json     # Smoke badge JSON (auto-generated)
├── Makefile                         # Added targets
├── README_DocsCoverageBadge_Addon.txt
└── README_PagesSmokeBadge_Addon.txt
```

---

## 🔧 Customization

### **Docs Coverage Badge**

Customize PDF asset patterns via environment variables:

```yaml
# In .github/workflows/docs-coverage-badge.yml
env:
  DOCS_ASSET_REGEX_DARK: ".*dark.*\\.zip$"
  DOCS_ASSET_REGEX_LIGHT: ".*light.*\\.zip$"
```

Default patterns:
```python
PATTERN_DARK  = r"SonicBuilder_Manual_.*?_g[0-9a-fA-F]{7,8}.*(dark|DARK).*\.zip$"
PATTERN_LIGHT = r"SonicBuilder_Manual_.*?_g[0-9a-fA-F]{7,8}.*(light|LIGHT).*\.zip$"
```

---

### **Pages Smoke Badge**

Change the gallery URL:

```yaml
# In .github/workflows/pages-smoke-badge.yml
env:
  PAGES_GALLERY_URL: "https://your-custom-url.github.io/gallery.html"
  PAGES_SMOKE_TIMEOUT: "10"  # seconds
```

Or locally:
```bash
PAGES_GALLERY_URL="https://..." make pages-smoke-badge
```

---

## 🤖 GitHub Actions Workflows

### **Docs Coverage Badge Workflow**

```yaml
name: Docs Coverage Badge
on:
  release:
    types: [published, edited, released]
  workflow_dispatch: {}
  schedule:
    - cron: "23 4 * * *"
```

**What it does:**
1. Fetches latest release via GitHub API
2. Checks for dark/light PDF assets
3. Generates badge JSON
4. Commits to `docs/status/docs_coverage_status.json`
5. Badge auto-updates on Shields.io

---

### **Pages Smoke Badge Workflow**

```yaml
name: Pages Smoke Badge
on:
  schedule:
    - cron: "*/30 * * * *"  # Every 30 minutes
  workflow_dispatch: {}
```

**What it does:**
1. Tests gallery URL (dark theme)
2. Tests gallery URL (light theme)
3. Checks HTTP 200 + HTML content
4. Generates badge JSON
5. Commits to `docs/status/pages_smoke_status.json`
6. Badge auto-updates on Shields.io

---

## 📊 Add to README

Add these badges to your `README.md`:

```markdown
# SonicBuilder

<!-- Status Badges -->
<p align="center">
  <a href="https://github.com/m9dswyptrn-web/SonicBuilder/releases/latest">
    <img alt="Docs Coverage"
         src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/docs_coverage_status.json">
  </a>
  <a href="https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html">
    <img alt="Pages Smoke"
         src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/pages_smoke_status.json">
  </a>
  <a href="https://github.com/m9dswyptrn-web/SonicBuilder/actions">
    <img alt="Docs Smoke Test"
         src="https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/docs-post-publish-smoketest.yml?label=docs%20smoke">
  </a>
</p>

Your project description here...
```

---

## 🎯 Complete Badge Suite

You now have **3 status badge systems**:

### **1. Docs Coverage Badge** 📚
- **Shows:** Release PDF asset completeness
- **Updates:** On release + daily
- **Command:** `make coverage-badge`

### **2. Pages Smoke Badge** 🧪
- **Shows:** Gallery live status
- **Updates:** Every 30 minutes
- **Command:** `make pages-smoke-badge`

### **3. Docs Smoke Test Badge** (from previous addon) ✅
- **Shows:** Workflow status
- **Updates:** After each Pages deployment
- **Command:** `make smoke`

---

## 🔍 Troubleshooting

### Badge shows "invalid"

**Cause:** JSON file not accessible or malformed

**Fix:**
1. Check file exists:
   ```bash
   ls docs/status/*.json
   ```

2. Validate JSON:
   ```bash
   cat docs/status/docs_coverage_status.json | python -m json.tool
   ```

3. Ensure committed and pushed:
   ```bash
   git add docs/status/
   git commit -m "chore: add badge status files"
   git push
   ```

---

### Badge shows old data

**Cause:** Shields.io caching or workflow not running

**Fix:**
1. Trigger workflow manually:
   - Go to Actions tab
   - Select workflow
   - Click "Run workflow"

2. Clear Shields.io cache:
   - Add `?v=timestamp` to badge URL temporarily
   - Wait 5 minutes for cache refresh

3. Check workflow logs:
   ```
   https://github.com/m9dswyptrn-web/SonicBuilder/actions
   ```

---

### Docs coverage shows "none" but PDFs exist

**Cause:** Asset filename doesn't match regex pattern

**Fix:**
1. Check your PDF filenames:
   ```bash
   gh release view --json assets -q '.assets[].name'
   ```

2. Verify they match the pattern:
   ```
   SonicBuilder_Manual_v2.2.3_g12ab34cd_dark.zip
   SonicBuilder_Manual_v2.2.3_g12ab34cd_light.zip
   ```

3. Customize regex if needed (see Customization section)

---

### Pages smoke shows "down" but site works

**Cause:** Timeout too short or Pages still deploying

**Fix:**
1. Increase timeout:
   ```yaml
   env:
     PAGES_SMOKE_TIMEOUT: "20"  # Increase to 20 seconds
   ```

2. Check Pages deployment status:
   ```
   https://github.com/m9dswyptrn-web/SonicBuilder/deployments
   ```

3. Test manually:
   ```bash
   make pages-smoke-badge
   ```

---

## ✅ Verification Checklist

- [x] Scripts installed (`scripts/check_docs_coverage.py`, `scripts/pages_smoke_badge.py`)
- [x] Workflows added (`.github/workflows/docs-coverage-badge.yml`, `.github/workflows/pages-smoke-badge.yml`)
- [x] Makefile targets added (`coverage-badge`, `pages-smoke-badge`)
- [x] Status directory created (`docs/status/`)
- [x] README files available
- [ ] Test locally: `make coverage-badge`
- [ ] Test locally: `make pages-smoke-badge`
- [ ] Commit and push
- [ ] Verify badges in README
- [ ] Check GitHub Actions workflows

---

## 📦 Complete Addon Summary

You now have **4 complete addons**:

1. **MoboGallery Web Addon** 📸 - Professional image gallery
2. **Enhanced Smoke Test Addon** 🧪 - Multi-theme testing
3. **Docs Coverage Badge** 📚 - Release asset tracking
4. **Pages Smoke Badge** 🔍 - Live site monitoring

All integrated with your deployment pipeline! 🚀

---

## 🚀 Quick Start

```bash
# Test badges locally
make coverage-badge
make pages-smoke-badge

# View results
cat docs/status/docs_coverage_status.json
cat docs/status/pages_smoke_status.json

# Deploy everything
make ship

# Badges auto-update via GitHub Actions
```

---

**Generated:** October 30, 2025  
**Version:** SonicBuilder Badge Addons v1  
**Status:** ✅ Production Ready
