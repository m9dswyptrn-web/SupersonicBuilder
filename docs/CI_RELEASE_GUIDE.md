# Appendix C Release Workflow Guide

## Overview

The `release-appendixC.yml` workflow automatically builds and uploads Appendix C documentation to GitHub releases when you create a new tag or publish a release.

---

## 🚀 How to Trigger

### Method 1: Create and Push Tag
```bash
# Create tag
git tag v2.0.9

# Push tag to GitHub
git push origin v2.0.9
```

### Method 2: Publish Release on GitHub
1. Go to your repository on GitHub
2. Click "Releases" → "Draft a new release"
3. Choose or create a tag (e.g., `v2.0.9`)
4. Add release notes
5. Click "Publish release"

Both methods automatically trigger the workflow!

---

## 📦 What Gets Uploaded

The workflow uploads to your GitHub release:

### Individual PDFs
1. **QR_Index.pdf** - Dark mode QR gallery
2. **QR_Index_2UP.pdf** - 2-up laminated sheet for printing
3. **Appendix_C_I2S_Index.pdf** - Professional dark-mode index

### Complete Package
4. **AppendixC_v2.0.9.zip** - ZIP containing:
   - All PDFs above
   - 03_Photo_Index.csv
   - metadata.json

---

## 🔄 Complete Workflow

### Step 1: Prepare Release
```bash
# Ensure everything is committed
git status

# Optional: Update version locally first
make bump FROM=v2.0.8 TO=v2.0.9

# Optional: Build locally to verify
make all VERSION=v2.0.9
```

### Step 2: Create Tag
```bash
# Create annotated tag with message
git tag -a v2.0.9 -m "Release v2.0.9: Complete Appendix C integration"

# Or create lightweight tag
git tag v2.0.9
```

### Step 3: Push Tag
```bash
# Push the tag
git push origin v2.0.9
```

### Step 4: Watch Workflow
1. Go to your repository's "Actions" tab
2. See "Release Appendix C" workflow running
3. Wait ~2-3 minutes for completion
4. Check "Releases" page for uploaded files

---

## 📥 Download Release Files

After workflow completes:
1. Go to repository "Releases" page
2. Find your release (e.g., v2.0.9)
3. Download files from "Assets" section:
   - Individual PDFs for specific needs
   - Complete ZIP for full package

---

## 🌐 URL Management

The workflow uses `repo-url-setup.yml` to set canonical URL:
- **On GitHub:** `https://github.com/<owner>/<repo>`
- All QR codes point to GitHub repository
- All metadata contains GitHub URL
- Professional, permanent links

---

## 📊 Workflow Details

### Triggers
```yaml
on:
  release:
    types: [published]  # When you publish a release
  push:
    tags:
      - 'v*'            # When you push a version tag
```

### Build Steps
1. **Setup URL** - Gets canonical repository URL
2. **Install Dependencies** - Python, reportlab, qrcode, poppler
3. **Extract Version** - From tag or VERSION file
4. **Build Appendix C** - Runs all indexing and generation
5. **Create Package** - ZIPs all files
6. **Upload to Release** - Attaches files to GitHub release
7. **Create Summary** - Shows build results

### Version Detection
Priority order:
1. Git tag (if pushed via `git push --tags`)
2. Release tag name (if published via GitHub UI)
3. VERSION file in repository
4. Default: v2.0.9

---

## 🎯 Example Release Process

### Complete v2.0.9 Release
```bash
# 1. Bump version locally
make bump FROM=v2.0.8 TO=v2.0.9

# 2. Build and verify locally
make all VERSION=v2.0.9
ls -lh Appendix/C_I2S_Integration/*.pdf

# 3. Commit version bump
git add -A
git commit -m "chore: bump to v2.0.9"
git push

# 4. Create and push tag
git tag -a v2.0.9 -m "Release v2.0.9: Appendix C complete"
git push origin v2.0.9

# 5. Workflow runs automatically!
# - Builds Appendix C with v2.0.9
# - Creates ZIP package
# - Uploads to GitHub release

# 6. Go to Releases page on GitHub
# - Download AppendixC_v2.0.9.zip
# - Or individual PDFs
```

---

## 📝 Release Notes Template

When creating a release on GitHub, use this template:

```markdown
# SonicBuilder v2.0.9 - Appendix C Integration

## What's New
- Complete I²S integration documentation
- Auto-indexed PCB photos and tap diagrams
- Professional dark-mode index PDFs
- QR galleries for installer reference

## Appendix C Contents
- **QR_Index.pdf** - QR gallery for quick access
- **QR_Index_2UP.pdf** - Printable laminated cards
- **Appendix_C_I2S_Index.pdf** - Complete index
- **AppendixC_v2.0.9.zip** - Full package

## Installation
Download and extract `AppendixC_v2.0.9.zip` for all documentation.

## Documentation
See repository README for complete integration guide.
```

---

## 🔍 Verify Upload

After workflow completes:

### Check Release Page
```bash
# Open release page
open https://github.com/<owner>/<repo>/releases/tag/v2.0.9
```

### Verify Files
Expected files in release assets:
- ✅ AppendixC_v2.0.9.zip (~100 KB)
- ✅ QR_Index.pdf (~7 KB)
- ✅ QR_Index_2UP.pdf (~500 KB)
- ✅ Appendix_C_I2S_Index.pdf (~2 KB)

### Verify Content
Download ZIP and check contents:
```bash
unzip AppendixC_v2.0.9.zip
ls -lh
# Should show:
# - QR_Index.pdf
# - QR_Index_2UP.pdf
# - Appendix_C_I2S_Index.pdf
# - 03_Photo_Index.csv
# - metadata.json
```

---

## 🛠️ Advanced Usage

### Release from Branch
```bash
# Create release from specific branch
git checkout release-v2.0.9
git tag v2.0.9
git push origin v2.0.9
```

### Pre-release
When creating release on GitHub:
1. Check "This is a pre-release"
2. Workflow still runs
3. Files uploaded to pre-release

### Multiple Tags
```bash
# Create multiple tags
git tag v2.0.9
git tag v2.1.0-beta

# Push all tags
git push origin --tags

# Workflow runs for each tag!
```

---

## 🔧 Customization

### Change Package Name
Edit workflow file:
```yaml
zip -r ../AppendixC_Custom_${{ steps.version.outputs.VERSION }}.zip .
```

### Upload Additional Files
Add to upload section:
```yaml
files: |
  AppendixC_${{ steps.version.outputs.VERSION }}.zip
  Appendix/C_I2S_Integration/custom_file.pdf  # Add here
```

### Change Trigger Pattern
Modify tag pattern:
```yaml
push:
  tags:
    - 'release-*'  # Match release-v2.0.9
    - 'appendix-*' # Match appendix-v2.0.9
```

---

## 🐛 Troubleshooting

### Workflow Doesn't Trigger
**Problem:** Pushed tag but workflow didn't run  
**Solution:** Check tag format matches `v*` pattern:
```bash
# Good: v2.0.9, v1.0.0, v2.1.0-beta
# Bad: 2.0.9, version-2.0.9, release-2.0.9
```

### Files Not Uploaded
**Problem:** Workflow completed but no files in release  
**Solution:** Check workflow logs for upload step. Ensure release exists:
```bash
# For push tags, GitHub auto-creates release
# For manual tags, create release on GitHub first
```

### Wrong Version in Files
**Problem:** PDFs show v2.0.8 instead of v2.0.9  
**Solution:** Workflow uses tag version. Ensure tag is correct:
```bash
git tag -d v2.0.9           # Delete local tag
git push origin :v2.0.9     # Delete remote tag
git tag v2.0.9              # Create correct tag
git push origin v2.0.9      # Push correct tag
```

### Duplicate Uploads
**Problem:** Files uploaded twice to release  
**Solution:** Workflow triggers on both `release.published` and `push.tags`. Remove one:
```yaml
# Option 1: Only tag push
on:
  push:
    tags: ['v*']

# Option 2: Only release publish
on:
  release:
    types: [published]
```

---

## 📊 Workflow Performance

**Typical Runtime:** ~3-4 minutes
- Setup: ~20 seconds
- Dependencies: ~45 seconds
- Build Appendix C: ~30 seconds
- Create package: ~5 seconds
- Upload: ~15 seconds
- Summary: ~5 seconds

**File Sizes:**
- QR_Index.pdf: ~7 KB
- QR_Index_2UP.pdf: ~500 KB (rasterized)
- Appendix_C_I2S_Index.pdf: ~2 KB
- 03_Photo_Index.csv: ~300 bytes
- metadata.json: ~150 bytes
- **Total ZIP:** ~510 KB

---

## 🔄 Integration with Other Workflows

### With CoA Generation
When you create release:
1. `release-appendixC.yml` runs (uploads Appendix C)
2. `coa-on-release.yml` runs (auto-mints CoA)
3. Both upload to same release
4. Complete professional package!

### With Version Bump
When version bumped automatically:
1. `version-bump-on-appendix.yml` bumps to v2.0.9
2. Commit and tag manually
3. Push tag triggers `release-appendixC.yml`
4. Release created with v2.0.9 files

---

## 📚 Related Workflows

- `.github/workflows/build-appendixC.yml` - Build on push (artifacts)
- `.github/workflows/coa-on-release.yml` - Auto-mint CoA on release
- `.github/workflows/version-bump-on-appendix.yml` - Auto-bump version
- `.github/workflows/repo-url-setup.yml` - Reusable URL detection

---

## ✅ Best Practices

### 1. Test Locally First
Always build locally before tagging:
```bash
make all VERSION=v2.0.9
# Verify all PDFs look correct
```

### 2. Use Annotated Tags
Annotated tags include metadata:
```bash
git tag -a v2.0.9 -m "Release v2.0.9: Description"
# Better than: git tag v2.0.9
```

### 3. Write Release Notes
When publishing on GitHub, write clear release notes explaining what's new.

### 4. Verify Before Sharing
Download the ZIP from release and verify contents before sharing with installers.

### 5. Keep Versions Consistent
Make sure VERSION file, git tag, and Appendix C all show same version.

---

## 🎉 Summary

Your Appendix C release workflow:
- ✅ Triggers automatically on tags
- ✅ Builds all Appendix C documentation
- ✅ Creates professional ZIP package
- ✅ Uploads to GitHub releases
- ✅ Uses canonical repository URLs
- ✅ Provides build summaries

**Just tag and push — GitHub does the rest!** 🚀

---

## Quick Reference

```bash
# Complete release process
git tag -a v2.0.9 -m "Release v2.0.9"
git push origin v2.0.9
# ✅ Workflow runs automatically
# ✅ Files uploaded to release
# ✅ Ready to download and distribute!
```
