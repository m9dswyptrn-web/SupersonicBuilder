# Appendix C CI/CD Workflow Guide

## Overview

The `build-appendixC.yml` workflow automatically builds Appendix C documentation when you push changes to PCB photos or tap diagrams.

---

## 🚀 How It Works

### Automatic Triggers
The workflow runs automatically when you push to:
- `Appendix/C_I2S_Integration/PCB_Photos/**`
- `Appendix/C_I2S_Integration/Tap_Diagrams/**`
- `scripts/i2s_*.py`
- `scripts/appendix_c_*.py`
- `make_patches/MAKEFRAG.onebutton`

### Manual Trigger
You can also run it manually:
1. Go to Actions tab on GitHub
2. Select "Build Appendix C"
3. Click "Run workflow"
4. Optionally specify version (default: v2.0.9)

---

## 📦 What It Builds

The workflow generates:
1. **03_Photo_Index.csv** - Complete file inventory
2. **QR_Index.pdf** - Dark mode QR gallery
3. **QR_Index_2UP.pdf** - 2-up laminated QR sheet
4. **Appendix_C_I2S_Index.pdf** - Professional dark-mode index
5. **metadata.json** - Build metadata with URL
6. **Auto_Notes.txt** - Build log

---

## 🔧 Workflow Steps

1. **Setup URL** - Calls `repo-url-setup.yml` for canonical URL
2. **Install Dependencies** - Python, reportlab, pypdf, qrcode, poppler-utils
3. **Determine Version** - Reads from VERSION file or uses input
4. **Index Files** - Runs `i2s_index.py`
5. **Generate QR Gallery** - Runs `i2s_qr.py`
6. **Generate 2-Up Sheet** - Runs `i2s_qr_2up.py`
7. **Generate Index PDF** - Runs `appendix_c_index_pdf.py`
8. **Upload Artifacts** - All files uploaded with 90-day retention

---

## 📥 Download Artifacts

After workflow completes:
1. Go to workflow run page
2. Scroll to "Artifacts" section
3. Download `appendix-c-v2.0.9` (or your version)
4. Extract ZIP to get all PDFs, CSV, and metadata

---

## 🌐 URL Management

The workflow uses the reusable `repo-url-setup.yml` workflow to set `SB_REPO_URL`:
- On GitHub: `https://github.com/<owner>/<repo>`
- Auto-detected from `GITHUB_REPOSITORY` environment variable
- Used in all QR codes, PDFs, and metadata

---

## 🔄 Example Workflow

### Add PCB Photo
```bash
# 1. Add photo to local repository
cp new_installation.jpg Appendix/C_I2S_Integration/PCB_Photos/

# 2. Commit and push
git add Appendix/C_I2S_Integration/PCB_Photos/new_installation.jpg
git commit -m "docs: add PCB installation photo"
git push

# 3. Workflow runs automatically!
# - Indexes new file
# - Regenerates QR gallery
# - Updates index PDF
# - Uploads all artifacts
```

### Check Workflow Status
```bash
# Go to your repository on GitHub
# Click "Actions" tab
# See "Build Appendix C" workflow running
# Wait for completion (usually ~2 minutes)
# Download artifacts from workflow run page
```

---

## 📊 Workflow Output Example

**GitHub Actions Summary:**
```
## Appendix C Build Complete 🎉

Version: v2.0.9
Base URL: https://github.com/<owner>/<repo>

### Generated Files
- 03_Photo_Index.csv
- QR_Index.pdf (dark mode QR gallery)
- QR_Index_2UP.pdf (2-up laminated sheet)
- Appendix_C_I2S_Index.pdf (professional index)
- metadata.json
- Auto_Notes.txt

Files Indexed: 4

Artifacts uploaded and ready for download!
```

---

## 🛠️ Customization

### Change Version
Edit the workflow file or use manual dispatch:
```yaml
workflow_dispatch:
  inputs:
    version:
      default: 'v2.0.9'  # Change this
```

### Add More Triggers
Add paths to the `on.push.paths` section:
```yaml
on:
  push:
    paths:
      - 'Appendix/C_I2S_Integration/PCB_Photos/**'
      - 'Appendix/C_I2S_Integration/Tap_Diagrams/**'
      - 'your/custom/path/**'  # Add here
```

### Extend Artifact Retention
Change retention days (default: 90):
```yaml
retention-days: 180  # 6 months
```

---

## ✅ Verification

### Check Workflow File
```bash
cat .github/workflows/build-appendixC.yml
```

### Test Locally First
```bash
# Before pushing, test locally
make i2s_index i2s_qr i2s_qr_2up
make appendix_pdf VERSION=v2.0.9

# Verify outputs
ls -lh Appendix/C_I2S_Integration/*.pdf
```

### Monitor Workflow
1. Push changes
2. Go to Actions tab immediately
3. Click on running workflow
4. Watch real-time logs
5. Download artifacts when complete

---

## 🔍 Troubleshooting

### Workflow Doesn't Trigger
**Problem:** Pushed to PCB_Photos/ but workflow didn't run  
**Solution:** Check paths match exactly:
```bash
git status
# Should show: Appendix/C_I2S_Integration/PCB_Photos/file.jpg
```

### Build Fails on Index Step
**Problem:** "No such file or directory"  
**Solution:** Ensure directory structure exists:
```bash
mkdir -p Appendix/C_I2S_Integration/{PCB_Photos,Tap_Diagrams}
```

### Artifacts Not Available
**Problem:** Workflow completed but no artifacts  
**Solution:** Check upload step succeeded in logs. Files must exist:
```bash
# In workflow logs, look for:
# ✅ Generated QR gallery
# ✅ Generated 2-up QR sheet
# ✅ Generated index PDF
```

### Wrong Version in Output
**Problem:** PDF shows v2.0.8 instead of v2.0.9  
**Solution:** Update VERSION file or use manual dispatch with version input

---

## 📚 Related Workflows

- `.github/workflows/repo-url-setup.yml` - Reusable URL detection
- `.github/workflows/version-bump-on-appendix.yml` - Auto-bump version
- `.github/workflows/coa-on-release.yml` - Auto-mint CoA
- `.github/workflows/manual-build.yml` - Build manuals

---

## 🎯 Best Practices

### 1. Test Locally First
Always run `make all VERSION=v2.0.9` locally before pushing to catch errors early.

### 2. Meaningful Commit Messages
Use clear messages for automatic triggers:
```bash
git commit -m "docs: add PCB solder joint closeup"
git commit -m "docs: update I²S tap wiring diagram"
```

### 3. Batch Updates
If adding multiple files, add them all in one commit to trigger workflow once:
```bash
git add Appendix/C_I2S_Integration/PCB_Photos/*.jpg
git commit -m "docs: add 5 PCB installation photos"
git push
```

### 4. Monitor First Run
Watch the first workflow run completely to ensure everything works correctly.

### 5. Download Artifacts Regularly
Artifacts expire after 90 days. Download important builds for archival.

---

## 🔄 Integration with Version Bumping

When `version-bump-on-appendix.yml` bumps to v2.0.9:
1. VERSION file updated
2. Both workflows may trigger
3. `build-appendixC.yml` uses new version automatically
4. All outputs show v2.0.9

---

## 📈 Workflow Performance

**Typical Runtime:** ~2-3 minutes
- Checkout: ~10 seconds
- Python setup: ~15 seconds
- Dependencies: ~45 seconds
- Index generation: ~5 seconds
- QR generation: ~10 seconds
- 2-up generation: ~30 seconds
- Index PDF: ~5 seconds
- Upload: ~10 seconds

**Total:** Usually completes in under 3 minutes.

---

## 🎉 Summary

Your Appendix C CI/CD workflow:
- ✅ Triggers automatically on file changes
- ✅ Uses canonical URL from repo-url-setup
- ✅ Generates all indexes and PDFs
- ✅ Uploads artifacts for download
- ✅ Provides build summary
- ✅ Integrates with version management

**Just push your PCB photos and diagrams — GitHub Actions does the rest!** 🚀
