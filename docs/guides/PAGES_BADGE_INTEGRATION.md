# ✅ GitHub Pages Badge Integration Complete

## 🎉 **Enhanced Workflow with Dynamic Badge Support**

Your GitHub Pages workflow now automatically creates:
1. **`latest.pdf`** - Symlink to newest PDF
2. **`badge.json`** - Shields.io endpoint for dynamic badges

---

## 🚀 **What's New**

### **Before (Basic Pages):**
- Published `docs/` to GitHub Pages
- Copied PDFs to `/downloads/`
- Basic static site hosting

### **After (Enhanced with Badges):**
- ✅ Published `docs/` to GitHub Pages
- ✅ Copied PDFs to `/downloads/`
- ✅ **Creates `latest.pdf` symlink** (always points to newest PDF)
- ✅ **Generates `badge.json`** (Shields.io endpoint)
- ✅ **Includes VERSION** in badge message
- ✅ **Dynamic README badge** support

---

## 📦 **Files Updated**

### **Modified:**
- `.github/workflows/pages.yml` - Enhanced with badge generation

### **Added:**
- `README_BADGE_SNIPPET.md` - Badge usage guide with examples

---

## 🎯 **How the Badge Works**

### **Workflow Steps:**

1. **Find Latest PDF:**
   ```bash
   LATEST_FILE="$(ls -1t public/downloads/*.pdf | head -n1)"
   ```

2. **Create Symlink:**
   ```bash
   cp -f "$LATEST_FILE" public/downloads/latest.pdf
   ```

3. **Generate Badge JSON:**
   ```bash
   cat > public/downloads/badge.json <<JSON
   {
     "schemaVersion": 1,
     "label": "Latest Download",
     "message": "supersonic_manual_dark.pdf (v2.0.9)",
     "color": "blue"
   }
   JSON
   ```

4. **Shields.io Renders Badge:**
   ```markdown
   ![Latest Download](https://img.shields.io/endpoint?url=https://owner.github.io/repo/downloads/badge.json)
   ```

---

## 📋 **Add Badge to README**

### **Option 1: Dynamic Badge (Recommended)**

Shows actual filename + version, updates automatically:

```markdown
[![Latest Download](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
```

**Result:**
- Badge text: `supersonic_manual_dark.pdf (v2.0.9)`
- Click to download: `latest.pdf`
- Auto-updates on each push/release

### **Option 2: Static Badge (Simple)**

Always shows "Download Latest":

```markdown
[![Latest Download](https://img.shields.io/badge/Download-Latest-blue)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
```

**Result:**
- Badge text: `Download Latest`
- Click to download: `latest.pdf`
- Simpler but less informative

---

## 🌐 **Published URLs**

After workflow runs, these URLs will be live:

### **Latest PDF (Symlink):**
```
https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf
```
Always points to newest PDF, updates automatically.

### **Badge Endpoint:**
```
https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json
```
JSON endpoint for Shields.io badge rendering.

### **Individual PDFs:**
```
https://m9dswyptrn-web.github.io/SonicBuilder/downloads/supersonic_manual_dark.pdf
https://m9dswyptrn-web.github.io/SonicBuilder/downloads/supersonic_manual_light.pdf
```
All PDFs from `dist/` directory.

---

## 🧪 **Testing After Deployment**

### **1. Check Badge Endpoint:**
```bash
curl https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json
```

**Expected output:**
```json
{
  "schemaVersion": 1,
  "label": "Latest Download",
  "message": "supersonic_manual_dark.pdf (v2.0.9)",
  "color": "blue"
}
```

### **2. Test Latest PDF Link:**
```bash
curl -I https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf
```

**Expected:** `200 OK` response

### **3. Verify Badge Renders:**
- Add badge snippet to README.md
- Commit and push
- View README on GitHub
- Badge should display with filename + version

---

## 🔧 **Badge Customization**

### **Change Badge Color:**
Edit `.github/workflows/pages.yml`, line with `"color":`:
- `blue` - Default (stable)
- `green` - Success/production
- `orange` - Beta/testing
- `red` - Experimental
- `lightgrey` - Not available

### **Change Badge Label:**
Edit `.github/workflows/pages.yml`, line with `"label":`:
```json
"label": "Manual Download"
"label": "Documentation"
"label": "PDF"
```

### **Version Format:**
Current format: `filename (v2.0.9)`

To change, edit workflow:
```bash
# Show only filename (no version)
jq --arg msg "$LATEST_NAME" '.message = $msg' ...

# Show only version
jq --arg msg "$VERSION_STR" '.message = $msg' ...

# Custom format
jq --arg msg "v$VERSION_STR" '.message = $msg' ...
```

---

## 📊 **Workflow Logic**

### **When PDFs Exist:**
```bash
1. Find newest PDF: ls -1t public/downloads/*.pdf | head -n1
2. Copy to latest.pdf
3. Read VERSION file (if exists)
4. Generate badge.json:
   - message: "filename (version)"
   - color: blue
```

### **When No PDFs Exist:**
```bash
1. Generate badge.json:
   - message: "not available"
   - color: lightgrey
```

### **Example Badge Messages:**

**With PDFs + VERSION:**
```
supersonic_manual_dark.pdf (v2.0.9)
```

**With PDFs, no VERSION:**
```
supersonic_manual_dark.pdf
```

**No PDFs:**
```
not available
```

---

## 🎨 **Advanced: Multiple Badges**

### **Dark Theme Badge:**
```markdown
[![Dark Manual](https://img.shields.io/badge/Download-Dark%20Manual-blue)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/supersonic_manual_dark.pdf)
```

### **Light Theme Badge:**
```markdown
[![Light Manual](https://img.shields.io/badge/Download-Light%20Manual-lightgrey)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/supersonic_manual_light.pdf)
```

### **Version Badge:**
```markdown
[![Version](https://img.shields.io/badge/Version-v2.0.9-green)](https://github.com/m9dswyptrn-web/SonicBuilder)
```

---

## 🐛 **Troubleshooting**

### **Issue: Badge shows "not available"**

**Causes:**
- No PDFs in `dist/` directory when workflow ran
- Workflow failed before badge generation
- Build step didn't copy PDFs

**Solutions:**
1. Check `dist/` directory has PDFs:
   ```bash
   ls -la dist/*.pdf
   ```

2. Check workflow logs (Actions tab):
   - Did "Prepare site" step complete?
   - Were PDFs found and copied?

3. Run workflow again (manual dispatch)

### **Issue: Badge not updating**

**Causes:**
- Shields.io caching (5-10 minute cache)
- Browser caching
- Workflow hasn't run yet

**Solutions:**
1. Wait 5-10 minutes for Shields.io cache to expire
2. Force refresh: Add `?v=123` to badge URL temporarily
3. Clear browser cache
4. Check badge.json directly in browser

### **Issue: Badge shows old filename**

**Solution:**
1. Verify workflow ran successfully (Actions → latest run)
2. Check badge.json endpoint directly:
   ```
   https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json
   ```
3. If badge.json is correct, it's Shields.io caching - wait a few minutes

---

## 📚 **Complete Setup Steps**

### **Step 1: Enable GitHub Pages**
1. GitHub repo → Settings → Pages
2. Source: **GitHub Actions**
3. Save

### **Step 2: Commit Enhanced Workflow**
```bash
git add .github/workflows/pages.yml README_BADGE_SNIPPET.md
git commit -m "ci(pages): add badge endpoint + latest.pdf symlink"
git push
```

### **Step 3: Wait for Deployment**
- Check Actions tab
- Wait for "GitHub Pages (Docs Site + Latest Badge)" to complete
- ~2 minutes for first deployment

### **Step 4: Add Badge to README**
```bash
# Edit README.md and add:
[![Latest Download](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)

git add README.md
git commit -m "docs: add latest download badge"
git push
```

### **Step 5: Verify**
- Visit your README on GitHub
- Badge should display with filename + version
- Click badge to download latest PDF

---

## 🎊 **Summary**

**Enhanced Workflow Features:**
- ✅ Creates `latest.pdf` symlink
- ✅ Generates `badge.json` endpoint
- ✅ Includes VERSION in badge
- ✅ Dynamic Shields.io badge support
- ✅ Auto-updates on push/release
- ✅ Fallback for "not available" state

**Badge URLs:**
- Dynamic badge: `https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json`
- Latest PDF: `https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf`
- Badge endpoint: `https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json`

**Documentation:**
- `README_BADGE_SNIPPET.md` - Badge usage guide
- `GITHUB_PAGES_INTEGRATION.md` - Pages setup
- `PAGES_BADGE_INTEGRATION.md` - This file

---

**Your GitHub Pages now has professional dynamic badges! 🎉**

Add the badge to your README and you're all set!
