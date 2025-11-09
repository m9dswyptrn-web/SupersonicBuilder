# 📛 SonicBuilder Status Badges - Ready for README

Copy these badge snippets into your `README.md` to display live status indicators.

---

## 🎯 Complete Badge Suite

```markdown
<!-- SonicBuilder Status Badges -->
<p align="center">
  <!-- Docs Coverage Badge -->
  <a href="https://github.com/m9dswyptrn-web/SonicBuilder/releases/latest">
    <img alt="Docs Coverage"
         src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/docs_coverage_status.json">
  </a>
  
  <!-- Pages Smoke Badge -->
  <a href="https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html">
    <img alt="Pages Smoke"
         src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/pages_smoke_status.json">
  </a>
  
  <!-- Docs Smoke Test Workflow Badge -->
  <a href="https://github.com/m9dswyptrn-web/SonicBuilder/actions">
    <img alt="Docs Smoke Test"
         src="https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/docs-post-publish-smoketest.yml?label=docs%20smoke">
  </a>
</p>
```

---

## 📊 Individual Badges

### **1. Docs Coverage Badge** 📚

**Purpose:** Shows whether latest release has both Dark and Light PDF bundles

**HTML:**
```html
<a href="https://github.com/m9dswyptrn-web/SonicBuilder/releases/latest">
  <img alt="Docs Coverage"
       src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/docs_coverage_status.json">
</a>
```

**Markdown:**
```markdown
[![Docs Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/docs_coverage_status.json)](https://github.com/m9dswyptrn-web/SonicBuilder/releases/latest)
```

**Badge States:**
- 🟢 Green: Both Dark + Light PDFs present
- 🟠 Orange: Only one PDF variant
- 🔴 Red: No PDFs found

**Updates:**
- On release publish/edit
- Daily at 4:23 AM UTC
- Manual: `make coverage-badge`

---

### **2. Pages Smoke Badge** 🧪

**Purpose:** Monitors GitHub Pages gallery live status

**HTML:**
```html
<a href="https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html">
  <img alt="Pages Smoke"
       src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/pages_smoke_status.json">
</a>
```

**Markdown:**
```markdown
[![Pages Smoke](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/pages_smoke_status.json)](https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html)
```

**Badge States:**
- 🟢 Green: Both dark & light gallery accessible
- 🟠 Orange: Only one theme works
- 🔴 Red: Gallery down

**Updates:**
- Every 30 minutes automatically
- Manual: `make pages-smoke-badge`

---

### **3. Docs Smoke Test Badge** ✅

**Purpose:** Shows status of post-publish smoke test workflow

**HTML:**
```html
<a href="https://github.com/m9dswyptrn-web/SonicBuilder/actions">
  <img alt="Docs Smoke Test"
       src="https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/docs-post-publish-smoketest.yml?label=docs%20smoke">
</a>
```

**Markdown:**
```markdown
[![Docs Smoke Test](https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/docs-post-publish-smoketest.yml?label=docs%20smoke)](https://github.com/m9dswyptrn-web/SonicBuilder/actions)
```

**Badge States:**
- 🟢 Green: Last smoke test passed
- 🔴 Red: Last smoke test failed
- ⚪ Gray: No runs yet

**Updates:**
- After Pages deployment
- Manual: GitHub Actions "Run workflow"

---

## 🎨 Example README Layout

```markdown
# 🚗 SonicBuilder

**Professional PDF Manual Generator for 2014 Chevy Sonic LTZ Android Head Unit Installation**

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

---

## 📚 Features

- ✅ Comprehensive installer manuals (Dark + Light themes)
- ✅ CAN diagnostics platform with Teensy 4.1
- ✅ Web-based motherboard gallery
- ✅ Automated CI/CD pipeline
- ✅ One-command deployment

## 🚀 Quick Start

...your content here...

## 📸 Gallery

Visit the [Motherboard Gallery](https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html)

## 📦 Latest Release

Download the latest manuals from [Releases](https://github.com/m9dswyptrn-web/SonicBuilder/releases/latest)
```

---

## 🔧 Customization Options

### **Change Badge Style**

Shields.io supports various styles. Add `&style=` parameter:

```markdown
<!-- Flat style (default) -->
![Badge](https://img.shields.io/endpoint?url=...&style=flat)

<!-- Flat-square style -->
![Badge](https://img.shields.io/endpoint?url=...&style=flat-square)

<!-- For-the-badge style -->
![Badge](https://img.shields.io/endpoint?url=...&style=for-the-badge)

<!-- Plastic style -->
![Badge](https://img.shields.io/endpoint?url=...&style=plastic)

<!-- Social style -->
![Badge](https://img.shields.io/endpoint?url=...&style=social)
```

---

### **Add Custom Logo**

```markdown
<!-- With custom logo -->
![Badge](https://img.shields.io/endpoint?url=...&logo=github&logoColor=white)

<!-- Available logos: github, gitlab, bitbucket, etc. -->
<!-- See: https://simpleicons.org/ -->
```

---

### **Cache Busting**

Force refresh badge immediately:

```markdown
<!-- Add cache buster parameter -->
![Badge](https://img.shields.io/endpoint?url=...&cacheSeconds=300)
```

---

## 📋 Testing Badges

Before committing, test that badge JSON files are valid:

```bash
# Generate badges locally
make coverage-badge
make pages-smoke-badge

# Verify JSON is valid
cat docs/status/docs_coverage_status.json | python -m json.tool
cat docs/status/pages_smoke_status.json | python -m json.tool

# Expected output:
# {
#   "schemaVersion": 1,
#   "label": "...",
#   "message": "...",
#   "color": "...",
#   "labelColor": "..."
# }
```

---

## 🚀 Deployment

After adding badges to README:

```bash
# Commit all changes
git add README.md docs/status/

# Commit
git commit -m "docs: add status badges to README"

# Deploy
make ship
```

Badges will update automatically via GitHub Actions!

---

## 📊 Badge Monitoring

### **View Badge Update Logs**

```bash
# Check GitHub Actions runs
https://github.com/m9dswyptrn-web/SonicBuilder/actions

# Workflows to monitor:
# - Docs Coverage Badge (runs on release + daily)
# - Pages Smoke Badge (runs every 30 min)
# - Docs Smoke Test (runs after Pages deployment)
```

### **Manual Badge Updates**

Trigger workflows manually:

1. Go to: `https://github.com/m9dswyptrn-web/SonicBuilder/actions`
2. Select workflow (e.g., "Docs Coverage Badge")
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow"

Badge updates within 1-2 minutes!

---

## ✅ Complete Badge Infrastructure

Your repository now has:

1. **📚 Docs Coverage Badge** - Release asset tracking
2. **🧪 Pages Smoke Badge** - Live site monitoring
3. **✅ Docs Smoke Test Badge** - Workflow status

All automatically maintained via GitHub Actions! 🎉

---

**Generated:** October 30, 2025  
**Version:** SonicBuilder Badge Suite v1  
**Status:** ✅ Ready to Deploy
