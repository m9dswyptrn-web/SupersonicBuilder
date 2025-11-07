# GitHub Pages Badge Snippet

## 🎯 Dynamic Badge (Shows Latest PDF Name + Version)

Add this to your `README.md` to show a dynamic badge that displays the latest PDF filename and version:

```markdown
[![Latest Download](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
```

**Live Example:**
[![Latest Download](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)

**Features:**
- ✅ Shows actual filename of latest PDF
- ✅ Includes version number (from VERSION file)
- ✅ Updates automatically on each push
- ✅ Click to download latest PDF directly
- ✅ Shows "not available" if no PDFs exist yet

---

## 📌 Static Badge (Simple Alternative)

If you prefer a simpler static badge that still links to the latest PDF:

```markdown
[![Latest Download](https://img.shields.io/badge/Download-Latest-blue)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
```

**Live Example:**
[![Latest Download](https://img.shields.io/badge/Download-Latest-blue)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)

---

## 🔧 How It Works

### **Dynamic Badge (`badge.json` endpoint):**

1. GitHub Pages workflow runs on push/release
2. Finds newest PDF in `dist/` directory
3. Copies it to `public/downloads/latest.pdf`
4. Creates `public/downloads/badge.json` with:
   ```json
   {
     "schemaVersion": 1,
     "label": "Latest Download",
     "message": "supersonic_manual_dark.pdf (v2.0.9)",
     "color": "blue"
   }
   ```
5. Shields.io reads this endpoint and renders the badge
6. Badge updates automatically on next deployment

### **Static Badge:**
- Always shows "Download Latest" text
- Links to `latest.pdf` which is updated by workflow
- Simpler but less informative

---

## 📋 What Gets Published

After workflow runs successfully:

**Files:**
- `https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf` → Newest PDF
- `https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json` → Badge endpoint
- `https://m9dswyptrn-web.github.io/SonicBuilder/downloads/<filename>.pdf` → All PDFs

**Badge Endpoint:**
- URL: `https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json`
- Used by: Shields.io to render dynamic badge
- Updates: Automatically on each push/release

---

## 🎨 Badge Customization

### **Change Badge Color:**
Edit `.github/workflows/pages.yml` and change `"color": "blue"` to:
- `green` - Success/stable builds
- `orange` - Beta/testing builds
- `red` - Unstable/experimental builds
- `yellow` - Warning/attention needed
- `lightgrey` - Not available/disabled

### **Change Badge Label:**
Edit workflow and change `"label": "Latest Download"` to:
- `"Manual"`
- `"Documentation"`
- `"PDF"`
- Your custom text

### **Add Multiple Badges:**

**Dark Theme PDF:**
```markdown
[![Dark Manual](https://img.shields.io/badge/Download-Dark%20Manual-blue)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/supersonic_manual_dark.pdf)
```

**Light Theme PDF:**
```markdown
[![Light Manual](https://img.shields.io/badge/Download-Light%20Manual-lightgrey)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/supersonic_manual_light.pdf)
```

---

## 🧪 Testing the Badge

### **After first deployment:**

1. **Check badge endpoint directly:**
   ```bash
   curl https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json
   ```
   
   Should return:
   ```json
   {
     "schemaVersion": 1,
     "label": "Latest Download",
     "message": "supersonic_manual_dark.pdf (v2.0.9)",
     "color": "blue"
   }
   ```

2. **Test latest.pdf link:**
   ```bash
   curl -I https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf
   ```
   
   Should return `200 OK`

3. **View badge in README:**
   - Add badge snippet to README.md
   - Commit and push
   - View on GitHub - badge should render

---

## 🐛 Troubleshooting

### **Badge shows "not available":**
**Causes:**
- No PDFs in `dist/` directory
- Workflow hasn't run yet
- Build failed

**Solutions:**
1. Ensure PDFs are built and copied to `dist/`
2. Wait for workflow to complete (check Actions tab)
3. Check workflow logs for errors

### **Badge not updating:**
**Solutions:**
1. Shields.io caches badges - wait a few minutes
2. Force refresh badge by appending `?v=timestamp` to badge URL
3. Clear your browser cache

### **Badge shows old filename:**
**Solutions:**
1. Verify workflow ran successfully (Actions tab)
2. Check `badge.json` endpoint directly in browser
3. Wait for Shields.io cache to expire (~5 minutes)

---

## 📚 Related Files

- `.github/workflows/pages.yml` - GitHub Pages workflow (creates badge.json)
- `VERSION` - Version file (included in badge message)
- `dist/` - PDFs to publish (source for latest.pdf)
- `GITHUB_PAGES_INTEGRATION.md` - Complete Pages setup guide

---

## 🎊 Summary

**Dynamic Badge:**
```markdown
[![Latest Download](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/downloads/badge.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
```

**Features:**
- ✅ Shows actual filename + version
- ✅ Auto-updates on push/release
- ✅ One-click download
- ✅ Professional appearance

**Add this to your README.md and you're done!** 🎉
