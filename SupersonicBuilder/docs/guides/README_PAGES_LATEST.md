# GitHub Pages • Latest PDF Workflow

## 🎯 **Streamlined PDF Publishing**

This is a **simplified** GitHub Pages workflow that publishes **only the latest PDF** to your GitHub Pages site.

---

## 📦 **What's Included**

### **Workflow Files:**
1. `.github/workflows/pages-latest.yml` - Publishes latest PDF to GitHub Pages
2. `.github/workflows/pages-smoke.yml` - Smoke test to verify deployment

### **Makefile Target:**
```bash
make pages-latest  # Trigger Pages workflow manually
```

### **README Badge:**
```markdown
[![Latest Download](https://img.shields.io/badge/download-latest.pdf-2b6fff?logo=adobeacrobatreader&logoColor=white)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
```

---

## 🚀 **How It Works**

### **Pages • Latest PDF Workflow:**

**Triggers:**
- ✅ Push to `main` when PDFs change (`build/**/*.pdf` or `dist/**/*.pdf`)
- ✅ Release published or edited
- ✅ Manual workflow dispatch

**What It Does:**
1. Finds newest PDF in `build/` (or `dist/` as fallback)
2. Copies it to `__site/downloads/` with original filename
3. Creates `latest.pdf` symlink pointing to newest
4. Generates minimal `index.html` with download button
5. Deploys to GitHub Pages
6. Posts summary with URLs

**Output:**
- `https://m9dswyptrn-web.github.io/SonicBuilder/` - Minimal index page
- `https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf` - Always newest PDF
- `https://m9dswyptrn-web.github.io/SonicBuilder/downloads/<filename>.pdf` - Specific PDF

---

## 🧪 **Smoke Test Workflow**

### **Pages • Smoke:**

**Triggers:**
- ✅ After "Pages • Latest PDF" workflow completes
- ✅ Manual workflow dispatch

**What It Does:**
1. Checks if `latest.pdf` is reachable (HTTP 200)
2. Fails if not reachable
3. Logs "OK" if successful

**Purpose:**
Automatically verifies your deployment worked correctly.

---

## 📋 **Setup Instructions**

### **Step 1: Enable GitHub Pages**
1. Go to: https://github.com/m9dswyptrn-web/SonicBuilder/settings/pages
2. Build and deployment → Source: **GitHub Actions**
3. Save

### **Step 2: Commit Workflows**
```bash
git add .github/workflows/pages-latest.yml .github/workflows/pages-smoke.yml Makefile
git commit -m "ci: add streamlined Pages workflow for latest PDF"
git push
```

### **Step 3: Trigger Deployment**

**Option A: Push PDFs (Auto-trigger):**
```bash
# Build PDFs
make build_dark
make release_local

# Commit and push
git add dist/*.pdf
git commit -m "docs: update PDFs"
git push  # Workflow runs automatically
```

**Option B: Manual Trigger:**
```bash
make pages-latest
# Or via GitHub UI: Actions → Pages • Latest PDF → Run workflow
```

### **Step 4: Wait for Deployment**
- Check Actions tab: https://github.com/m9dswyptrn-web/SonicBuilder/actions
- Wait ~1-2 minutes
- Smoke test runs automatically after deployment

### **Step 5: Verify**
```bash
curl -I https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf
# Should return: HTTP/2 200
```

---

## 🌐 **Published URLs**

After deployment:

**Index Page:**
```
https://m9dswyptrn-web.github.io/SonicBuilder/
```
Simple page with download button.

**Latest PDF (Symlink):**
```
https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf
```
Always points to newest PDF.

**Specific PDF:**
```
https://m9dswyptrn-web.github.io/SonicBuilder/downloads/supersonic_manual_dark.pdf
```
Direct link to specific file.

---

## 🎨 **Minimal Index Page**

The workflow creates a simple index.html:

```html
<!doctype html><meta charset="utf-8">
<title>SonicBuilder Downloads</title>
<style>
  html{color-scheme:dark light} 
  body{font:16px/1.5 system-ui;margin:40px;max-width:880px}
  a.btn{display:inline-block;padding:.6rem 1rem;border:1px solid #3a6df0;border-radius:8px;text-decoration:none}
</style>
<h1>SonicBuilder — Latest Manual</h1>
<p><a class="btn" href="./downloads/latest.pdf">⬇️ Download latest.pdf</a></p>
<p>All files are under <code>/downloads/</code>.</p>
```

**Features:**
- ✅ Dark/light theme support
- ✅ Clean, minimal design
- ✅ One-click download button
- ✅ No JavaScript required

---

## 🔧 **Configuration**

### **Environment Variables (in workflow):**

```yaml
env:
  REPO: m9dswyptrn-web/SonicBuilder
  OUTDIR: __site   # staging directory
  PDF_GLOB_PRIMARY: build/**/*.pdf
  PDF_GLOB_FALLBACK: dist/**/*.pdf
```

**To customize:**
- Change `PDF_GLOB_PRIMARY` to search different directories
- Change `OUTDIR` to use different staging directory
- Add more PDF globs if needed

### **Trigger on Different Files:**

Edit `pages-latest.yml`:
```yaml
on:
  push:
    branches: [ main ]
    paths:
      - 'build/**/*.pdf'
      - 'dist/**/*.pdf'
      - 'output/**/*.pdf'  # Add custom paths
```

---

## 📊 **Comparison: Full Pages vs Latest-Only**

| Feature | Full Pages (pages.yml) | Latest-Only (pages-latest.yml) |
|---------|------------------------|--------------------------------|
| **What's Published** | Entire `docs/` + PDFs | Latest PDF only |
| **Index Page** | Full dark-themed front page | Minimal download page |
| **File Size** | ~10MB (all docs + assets) | ~5MB (one PDF) |
| **Build Time** | ~2 minutes | ~1 minute |
| **Use Case** | Documentation hub | Simple PDF hosting |
| **Assets** | All docs/images/ | None |
| **Complexity** | Full static site | Minimal |

**Recommendation:**
- Use **pages-latest.yml** for simple PDF distribution
- Use **pages.yml** if you need the full documentation site

---

## 🛠️ **Makefile Helpers**

### **Trigger Deployment:**
```bash
make pages-latest
```
Runs `gh workflow run pages-latest.yml`

### **Check Status:**
```bash
gh run list --workflow=pages-latest.yml --limit 5
```
Shows recent workflow runs.

### **View Logs:**
```bash
gh run view --log
```
View logs from most recent run.

---

## 🐛 **Troubleshooting**

### **Issue: No PDFs found**
**Error:** `No PDFs found in build/ or dist/.`

**Solution:**
1. Ensure PDFs exist in `build/` or `dist/`
2. Build PDFs first:
   ```bash
   make build_dark
   make release_local
   ```
3. Commit and push PDFs to trigger workflow

### **Issue: Workflow doesn't trigger on push**
**Solution:**
1. Verify you're pushing to `main` branch
2. Check that PDFs are in watched paths (`build/` or `dist/`)
3. Ensure workflow file is committed to `.github/workflows/`

### **Issue: Smoke test fails**
**Error:** `latest.pdf not reachable (HTTP 404)`

**Solutions:**
1. Wait a few minutes for DNS propagation
2. Check if deployment succeeded (Actions tab)
3. Verify GitHub Pages is enabled
4. Clear CDN cache (wait ~5-10 minutes)

### **Issue: 404 on GitHub Pages**
**Solutions:**
1. Verify Pages is enabled in Settings
2. Check source is set to "GitHub Actions"
3. Wait for first deployment to complete
4. Check Actions tab for deployment status

---

## 📚 **Related Documentation**

- **GITHUB_PAGES_INTEGRATION.md** - Full Pages setup (docs/)
- **PAGES_BADGE_INTEGRATION.md** - Badge endpoint details
- **README_BADGE_SNIPPET.md** - Badge examples
- **README_PAGES_LATEST.md** - This file

---

## 🎯 **README Badge Options**

### **Option 1: Adobe Acrobat Style (Recommended):**
```markdown
[![Latest Download](https://img.shields.io/badge/download-latest.pdf-2b6fff?logo=adobeacrobatreader&logoColor=white)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
```

**Result:**  
Blue badge with Adobe PDF icon → "download | latest.pdf"

### **Option 2: Simple Style:**
```markdown
[![Latest Download](https://img.shields.io/badge/Download-Latest%20PDF-blue)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
```

**Result:**  
Blue badge → "Download | Latest PDF"

### **Option 3: Direct Link:**
```markdown
**Direct link:** https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf
```

---

## 🎊 **Summary**

**This workflow provides:**
- ✅ Streamlined PDF publishing (latest only)
- ✅ Auto-deployment on PDF changes
- ✅ Minimal index page with download button
- ✅ Automatic smoke testing
- ✅ Makefile helper (`make pages-latest`)
- ✅ Simple, fast deployments (~1 minute)

**Perfect for:**
- Projects that just need to host the latest PDF
- Simple download pages
- Fast deployments without heavy docs

**Not ideal for:**
- Full documentation sites (use pages.yml instead)
- Multiple PDFs with descriptions
- Complex navigation

---

**Your streamlined Pages workflow is ready! 🚀**

Commit, push, and your latest PDF will be published automatically!
