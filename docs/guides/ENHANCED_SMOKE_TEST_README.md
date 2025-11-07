# 🧪 Enhanced Smoke Test Addon v1 - Installation Complete

**Your Gallery URL:** `https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html`

---

## ✅ What's Installed

### Files
- ✅ `scripts/test_gallery_http_smoke.py` - Enhanced Python test script (5.4KB)
- ✅ `.github/workflows/docs-post-publish-smoketest.yml` - GitHub Actions workflow
- ✅ `Makefile.smoketest.addon` - Modular Makefile fragment
- ✅ `README_SmokeTest_Addon.txt` - Quick reference
- ✅ `Makefile` - Updated to include addon

---

## 🎯 Enhanced Features

### Multi-Theme Testing
```bash
make smoke         # Tests BOTH dark & light themes
make smoke:dark    # Dark theme only
make smoke:light   # Light theme only
```

### Auto-Discovery
- ✅ Automatically finds all CSS files in HTML
- ✅ Automatically finds all JS files in HTML
- ✅ Tests each asset (first 5 CSS, first 5 JS)
- ✅ Reports loading times for each

### Smart Validation
- ✅ Checks for required HTML snippets: `<title>`, `gallery`, `img`, `script`, `link`
- ✅ Verifies HTTP 200 status
- ✅ Measures latency in milliseconds
- ✅ Configurable retry logic with exponential backoff

### Webhook Notifications
- ✅ Discord webhook support
- ✅ Slack webhook support
- ✅ Email webhook support (generic inbound email services)
- ✅ Graceful fallback if not configured

### Detailed Diagnostics
- ✅ JSON output with full test results
- ✅ Separate diagnostics for each theme
- ✅ Asset-level status reporting
- ✅ Webhook delivery confirmation

---

## 🚀 Quick Start

### 1. Test Locally (Before Deployment)

```bash
# Install dependencies
pip install requests

# Run tests
make smoke
```

**Note:** This tests your live GitHub Pages site, not local files.

---

### 2. Configure (Optional)

Edit `Makefile.smoketest.addon` to customize:

```makefile
SMOKE_URL ?= https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html
SMOKE_TIMEOUT ?= 12           # Request timeout (seconds)
SMOKE_RETRIES ?= 3            # Number of retries
SMOKE_RETRY_SLEEP ?= 2.0      # Sleep between retries (seconds)
```

---

### 3. Add Webhook Notifications (Optional)

In **GitHub → Settings → Secrets → Actions**, add:

```
DISCORD_WEBHOOK_URL = https://discord.com/api/webhooks/...
SLACK_WEBHOOK_URL = https://hooks.slack.com/services/...
EMAIL_WEBHOOK_URL = https://your-email-webhook-service.com/...
```

**Benefits:**
- Get instant notifications when tests complete
- Know immediately if deployment succeeded/failed
- Share results with team automatically

---

## 📊 Example Output

### Success ✅

```json
{
  "title": "✅ Docs Smoke Test: PASS",
  "url": "https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html",
  "result": true,
  "themes": {
    "dark": {
      "ok": true,
      "status": 200,
      "latency_ms": 245
    },
    "light": {
      "ok": true,
      "status": 200,
      "latency_ms": 198
    }
  }
}
```

**Exit code:** 0

---

### Failure ❌

```json
{
  "title": "🛑 Docs Smoke Test: FAIL",
  "url": "https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html",
  "result": false,
  "themes": {
    "dark": {
      "ok": false,
      "status": 404,
      "latency_ms": 89
    },
    "light": {
      "ok": true,
      "status": 200,
      "latency_ms": 198
    }
  }
}
```

**Exit code:** 2 (triggers CI/CD failure alerts)

---

## 📋 Full Diagnostics

The complete `smoke_diagnostics.json` includes:

```json
{
  "target": "https://...",
  "timestamp": 1698612345,
  "themes": {
    "dark": {
      "url": "https://...?theme=dark",
      "status": 200,
      "latency_ms": 245,
      "required_snippets_ok": true,
      "assets": {
        "css": [
          "/styles/gallery_dark.css",
          "/web_gallery/lightbox.css"
        ],
        "js": [
          "/web_gallery/lightbox.js"
        ]
      },
      "asset_checks": [
        {
          "kind": "css",
          "asset": "https://.../styles/gallery_dark.css",
          "status": 200,
          "latency_ms": 89
        },
        {
          "kind": "css",
          "asset": "https://.../web_gallery/lightbox.css",
          "status": 200,
          "latency_ms": 76
        },
        {
          "kind": "js",
          "asset": "https://.../web_gallery/lightbox.js",
          "status": 200,
          "latency_ms": 82
        }
      ],
      "ok": true
    },
    "light": { /* similar structure */ }
  },
  "ok": true
}
```

---

## 🤖 GitHub Actions Integration

### Automatic Trigger

The workflow runs automatically **after** your "Docs Release" workflow completes:

```yaml
on:
  workflow_run:
    workflows: ["Docs Release"]
    types: [completed]
```

**Flow:**
1. You push code → triggers "Docs Release"
2. Docs Release builds PDFs → deploys to GitHub Pages
3. Pages deployment completes
4. **Smoke test auto-runs** → verifies everything works
5. Results uploaded as artifact + job summary

---

### Manual Trigger

You can also run manually:

1. Go to: `https://github.com/m9dswyptrn-web/SonicBuilder/actions`
2. Select **"Docs Smoke Test (Pages)"**
3. Click **"Run workflow"**
4. Select branch (main)
5. Click **"Run workflow"**

---

### View Results

**GitHub Actions Summary:**
```
https://github.com/m9dswyptrn-web/SonicBuilder/actions
```

Each run shows:
- ✅/❌ Pass/Fail badge
- Job summary with JSON diagnostics
- Downloadable artifacts:
  - `smoke_diagnostics.json`
  - `smoke_webhook_results.json`

---

## 📊 Badge for README (Optional)

Add to your README.md:

```markdown
## 📡 Docs Smoke Test

- Target: https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html  
- Workflow: **Docs Smoke Test (Pages)**  
- Status: ![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/docs-post-publish-smoketest.yml?label=docs%20smoke)

Run locally:
```bash
make smoke              # both themes
make smoke:dark         # force dark
make smoke:light        # force light
```
```

---

## 🔧 Customization

### Change Tested Themes

Edit `scripts/test_gallery_http_smoke.py`:

```python
THEMES = ["dark", "light", "auto", "custom"]
```

### Add More Required Snippets

```python
REQUIRED_SNIPPETS = [
    "<title>", "gallery", "img", "script", "link",
    "Motherboard",  # Your custom snippet
    "SonicBuilder"
]
```

### Test More Assets

```python
# Change from first 5 to first 10
for kind, arr in (("css", css[:10]), ("js", js[:10])):
```

### Adjust Timeouts

In `Makefile.smoketest.addon`:

```makefile
SMOKE_TIMEOUT ?= 20        # Increase to 20 seconds
SMOKE_RETRIES ?= 5         # Try 5 times
SMOKE_RETRY_SLEEP ?= 3.0   # Wait 3 seconds between
```

---

## 🎯 Complete Workflow Example

```bash
# 1. Add images to gallery
mkdir -p docs/images/mobo_back/2025-10-29
cp ~/my-images/*.jpg docs/images/mobo_back/2025-10-29/

# 2. Generate gallery
make web-gallery

# 3. Deploy everything
make ship

# 4. Wait for GitHub Pages rebuild (~1-2 min)
# (GitHub Actions workflow auto-triggers)

# 5. Check Actions tab for results
# OR test manually:
make smoke

# 6. View diagnostics
cat smoke_diagnostics.json
```

---

## 📚 Integration Summary

You now have **3 complete addons** working together:

### 1. **MoboGallery Web Addon** 📸
- Professional image gallery
- Dark theme + lightbox
- Auto-grouped by date
- **Command:** `make web-gallery`

### 2. **Enhanced Smoke Test Addon** 🧪
- Multi-theme testing
- Asset auto-discovery
- Webhook notifications
- **Command:** `make smoke`

### 3. **Complete Deployment System** 🚀
- Preflight validation
- Automated deployment
- CI/CD workflows
- **Command:** `make ship`

---

## ✅ Verification Checklist

- [x] Smoke test script installed (`scripts/test_gallery_http_smoke.py`)
- [x] GitHub Actions workflow added (`.github/workflows/docs-post-publish-smoketest.yml`)
- [x] Makefile addon included (`Makefile.smoketest.addon`)
- [x] Main Makefile updated (`-include Makefile.smoketest.addon`)
- [x] Executable permissions set
- [x] Documentation complete

---

## 🚀 Ready to Deploy!

Your complete testing infrastructure is production-ready:

```bash
# Deploy with full automation
make ship

# After deployment, test manually
make smoke

# View results
cat smoke_diagnostics.json
```

**Everything auto-runs via GitHub Actions after deployment!** 🎉

---

**Generated:** October 29, 2025  
**Version:** SonicBuilder Enhanced Smoke Test Addon v1  
**Status:** ✅ Production Ready
