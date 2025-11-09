# 🧪 SonicBuilder Docs Smoke Test Addon v1 (Enhanced)

**Purpose:** Comprehensive automated testing to verify your GitHub Pages gallery is accessible, with multi-theme support, asset validation, and webhook notifications

---

## ✅ What's Installed

### Files
- **scripts/test_gallery_http_smoke.py** - Smoke test script
- **.github/workflows/docs-post-publish-smoketest.yml** - Auto-test workflow
- **Makefile** - Added `smoke-test` target

### Tests Performed
1. ✅ Gallery HTML accessible (dark & light themes)
2. ✅ Required HTML snippets present
3. ✅ Auto-discovered CSS assets load
4. ✅ Auto-discovered JS assets load
5. ✅ Latency measurements
6. ✅ Retry logic with configurable timeouts
7. ✅ Webhook notifications on completion

---

## 🚀 Usage

### Manual Testing

Test your live GitHub Pages deployment:

```bash
# Test both themes
make smoke

# Test specific theme
make smoke:dark
make smoke:light
```

**Output:**
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

**Diagnostics saved to:** `smoke_diagnostics.json`

### Configuration

Environment variables (or set in `Makefile.smoketest.addon`):

```bash
SMOKE_URL="https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html"
SMOKE_TIMEOUT="12"           # seconds
SMOKE_RETRIES="3"            # retry attempts
SMOKE_RETRY_SLEEP="2.0"      # seconds between retries
```

---

## 🤖 Automated Testing

### GitHub Actions Workflow

The workflow automatically runs after GitHub Pages deployment:

**Trigger:** After `pages-build-deployment` completes successfully

**Steps:**
1. Wait 30 seconds for Pages to fully deploy
2. Run smoke tests
3. Report results

**View results:**
```
https://github.com/m9dswyptrn-web/SonicBuilder/actions
```

---

## 🔧 How It Works

### Test Flow

```python
base_url = "https://m9dswyptrn-web.github.io/SonicBuilder"

tests = [
    (f"{base_url}/docs/images/mobo_back/gallery.html", "Gallery HTML"),
    (f"{base_url}/docs/styles/gallery_dark.css", "Gallery CSS"),
    (f"{base_url}/docs/web_gallery/lightbox.css", "Lightbox CSS"),
    (f"{base_url}/docs/web_gallery/lightbox.js", "Lightbox JS"),
]
```

For each URL:
1. Send HTTP GET request
2. Check response status (expect 200 OK)
3. Report success/failure

---

## 📊 Example Output

### All Tests Pass ✅

```
🧪 SonicBuilder Docs Smoke Test
==================================================
Testing Gallery HTML... ✅ OK (200)
Testing Gallery CSS... ✅ OK (200)
Testing Lightbox CSS... ✅ OK (200)
Testing Lightbox JS... ✅ OK (200)
==================================================
Results: 4/4 tests passed
✅ All smoke tests passed!
```

**Exit code:** 0

---

### Some Tests Fail ❌

```
🧪 SonicBuilder Docs Smoke Test
==================================================
Testing Gallery HTML... ✅ OK (200)
Testing Gallery CSS... ❌ HTTP Error 404
Testing Lightbox CSS... ✅ OK (200)
Testing Lightbox JS... ✅ OK (200)
==================================================
Results: 3/4 tests passed
❌ Some smoke tests failed
```

**Exit code:** 1

---

## 🔍 Troubleshooting

### Test fails with 404

**Cause:** File not deployed to GitHub Pages

**Fix:**
1. Check file exists locally:
   ```bash
   ls docs/styles/gallery_dark.css
   ```

2. Verify committed and pushed:
   ```bash
   git status
   git add docs/
   git commit -m "docs: add gallery assets"
   git push
   ```

3. Wait for Pages rebuild (~1-2 minutes)

4. Re-run test:
   ```bash
   make smoke-test
   ```

---

### Test fails with timeout/connection error

**Cause:** GitHub Pages not enabled or still building

**Fix:**
1. Enable GitHub Pages:
   - Go to: https://github.com/m9dswyptrn-web/SonicBuilder/settings/pages
   - Source: `main` branch
   - Save

2. Wait for initial build (~2-5 minutes)

3. Check Pages status:
   - Go to: https://github.com/m9dswyptrn-web/SonicBuilder/actions
   - Look for "pages-build-deployment" workflow

4. Re-run test after build completes

---

### Workflow doesn't trigger

**Cause:** GitHub Actions not enabled or workflow file not committed

**Fix:**
1. Check Actions enabled:
   - Go to: https://github.com/m9dswyptrn-web/SonicBuilder/settings/actions
   - Enable "Allow all actions and reusable workflows"

2. Verify workflow committed:
   ```bash
   git add .github/workflows/docs-post-publish-smoketest.yml
   git commit -m "ci: add smoke test workflow"
   git push
   ```

3. Check workflow file syntax at:
   https://github.com/m9dswyptrn-web/SonicBuilder/actions

---

## 🎯 Integration with Deployment

### After Deploy

```bash
# Deploy everything
make ship

# Wait for GitHub Pages rebuild (~1-2 min)
sleep 120

# Run smoke test
make smoke-test
```

### In CI/CD Pipeline

The workflow automatically runs after Pages deployment, no manual intervention needed!

---

## 📝 Customizing Tests

### Add More URLs

Edit `scripts/test_gallery_http_smoke.py`:

```python
tests = [
    (f"{base_url}/docs/images/mobo_back/gallery.html", "Gallery HTML"),
    (f"{base_url}/docs/styles/gallery_dark.css", "Gallery CSS"),
    (f"{base_url}/docs/web_gallery/lightbox.css", "Lightbox CSS"),
    (f"{base_url}/docs/web_gallery/lightbox.js", "Lightbox JS"),
    # Add your custom tests:
    (f"{base_url}/docs/README.md", "README"),
    (f"{base_url}/index.html", "Home Page"),
]
```

### Change Wait Time

Edit `.github/workflows/docs-post-publish-smoketest.yml`:

```yaml
- name: Wait for Pages deployment
  run: sleep 60  # Wait 60 seconds instead of 30
```

---

## ✨ Benefits

### Automated Verification
- ✅ Catch deployment issues immediately
- ✅ Verify all assets loaded correctly
- ✅ No manual testing needed

### CI/CD Integration
- ✅ Runs automatically after Pages deployment
- ✅ GitHub Actions reports results
- ✅ Email notifications on failure

### Quick Local Testing
- ✅ Test before pushing: `make smoke-test`
- ✅ Verify production URLs
- ✅ Fast feedback loop

---

## 📚 Quick Reference

```bash
# Local smoke test
make smoke-test

# Direct script
python3 scripts/test_gallery_http_smoke.py

# View workflow results
# https://github.com/m9dswyptrn-web/SonicBuilder/actions

# Deploy and auto-test
make ship
# (workflow auto-runs after Pages deployment)
```

---

## 🎉 Summary

The smoke test addon provides:
- ✅ Automated verification of GitHub Pages deployment
- ✅ Tests gallery HTML, CSS, and JavaScript
- ✅ Local and CI/CD testing
- ✅ Fast feedback on deployment issues

**Your gallery deployment is now continuously verified!** 🚀

---

**Generated:** October 29, 2025  
**Version:** SonicBuilder DocsSmokeTest v1  
**Status:** ✅ Production Ready
