# SonicBuilder Deployment Checklist

Complete checklist for deploying your enhanced SonicBuilder platform to GitHub.

---

## ✅ Option 1: Commit & Push Everything

### Files to Commit

**New Workflows (3):**
```bash
.github/workflows/pr-docs-ready-command.yml
.github/workflows/pr-docs-reset-command.yml
.github/workflows/pr-docs-ready-autoreset.yml
```

**Updated Workflows (1):**
```bash
.github/workflows/pr-merge-guard.yml
```

**New Toolkits (2 directories, 48 files):**
```bash
tools/pdf_composer/          # 7 PDF tools
tools/image_suite/           # 41 image generators
```

**New Documentation (4):**
```bash
docs/PR_AUTOMATION.md        # Updated with slash commands
docs/TOOLS_REFERENCE.md      # Complete tool reference
tools/README.md              # Toolkit overview
OPTION_4_COMPLETE.md         # Integration summary
DEPLOYMENT_CHECKLIST.md      # This file
```

**Updated Templates (1):**
```bash
.github/pull_request_template.md
```

**Example Assets (5):**
```bash
output/examples/cover_example.png
output/examples/qr_repo_example.png
output/examples/callout_tip.png
output/examples/callout_warn.png
output/examples/callout_danger.png
```

---

### Commit Commands

```bash
# Stage all new files
git add .github/workflows/pr-docs-ready-command.yml \
        .github/workflows/pr-docs-reset-command.yml \
        .github/workflows/pr-docs-ready-autoreset.yml \
        .github/workflows/pr-merge-guard.yml \
        .github/pull_request_template.md \
        tools/ \
        docs/PR_AUTOMATION.md \
        docs/TOOLS_REFERENCE.md \
        output/examples/ \
        OPTION_4_COMPLETE.md \
        DEPLOYMENT_CHECKLIST.md

# Commit with descriptive message
git commit -m "feat: complete PR automation + PDF/Image toolkits

PR Automation Enhancements:
- Add /docs-ready maintainer command for manual label override
- Add /docs-reset maintainer command to remove label
- Auto-reset docs:ready label on new commits
- Enhanced merge guard with better user feedback

Toolkit Integration:
- PDF Composer (7 tools): compose, stamp, two-up, appendix, footer, watermark, verify
- ImageSuite (41 generators): covers, callouts, field cards, technical blocks, labels

Documentation:
- Updated PR_AUTOMATION.md with slash command reference
- Added TOOLS_REFERENCE.md with complete tool documentation
- Added tools/README.md for quick start
- Generated example assets demonstrating toolkit capabilities

Statistics:
- 24 GitHub Actions workflows total
- 150+ Python scripts and tools
- 35+ documentation files
- Complete CI/CD pipeline with dual badges, CHANGELOG automation, and release enrichment"

# Push to GitHub
git push origin main
```

---

## ✅ Option 2: Test Features

### Test 1: PR Slash Commands (Manual Test)

**Setup:**
1. Push all changes to GitHub (see Option 1)
2. Create a test PR with docs changes

**Test `/docs-ready` command:**
```
1. Open a PR that changes docs/
2. Wait for docs-build to run
3. Comment on PR: /docs-ready
4. Expected result:
   - 🚀 reaction appears on your comment
   - 'docs:ready' label applied to PR
   - Merge guard passes
```

**Test `/docs-reset` command:**
```
1. On same PR (now has docs:ready label)
2. Comment on PR: /docs-reset
3. Expected result:
   - 'docs:ready' label removed
   - Merge guard blocks merge again
```

**Test auto-reset:**
```
1. Re-apply label with /docs-ready
2. Push new commit to PR
3. Expected result:
   - Label automatically removed
   - Comment posted explaining auto-reset
   - Next docs-build will re-apply label
```

---

### Test 2: Merge Guard Smart Detection

**Test Case A: Docs changes**
```
1. Create PR changing: docs/RELEASE_AUTOMATION.md
2. Expected: Merge guard requires docs:ready label
3. Status: ❌ Blocked until label applied
```

**Test Case B: Non-docs changes**
```
1. Create PR changing: scripts/builder.py
2. Expected: Merge guard posts "no docs changes" comment
3. Status: ✅ Passes automatically
```

**Test Case C: Mixed changes**
```
1. Create PR changing: scripts/builder.py + README.md
2. Expected: Merge guard detects README (docs-related)
3. Status: ❌ Requires docs:ready label
```

---

### Test 3: Local Workflow Testing

**Test docs-build locally:**
```bash
# Simulate what docs-build does
make verify
make build_dark
make build_light

# Check output
ls -lh output/*.pdf
```

**Expected output:**
```
✅ Preflight checks passed
✅ Built: output/supersonic_manual_dark.pdf
✅ Built: output/supersonic_manual_light.pdf
```

---

## ✅ Option 3: Generate Example Assets

### Test PDF Composer Tools

**Example 1: Compose Images to PDF**
```bash
# Create test images directory
mkdir -p test_images
# Add some PNGs to test_images/

python tools/pdf_composer/compose_images_to_pdf.py \
  --in test_images/*.png \
  --out output/test_manual.pdf \
  --page Letter \
  --margin 24

echo "✅ Check: output/test_manual.pdf"
```

---

**Example 2: Stamp Metadata**
```bash
python tools/pdf_composer/pdf_stamp_metadata.py \
  --in output/test_manual.pdf \
  --out output/test_manual_meta.pdf \
  --title "SonicBuilder Test Manual" \
  --author "Christopher Elgin" \
  --subject "Testing PDF Tools" \
  --keywords "Test,SonicBuilder,PDF"

echo "✅ Check: output/test_manual_meta.pdf"
```

---

**Example 3: Two-Up Layout**
```bash
python tools/pdf_composer/pdf_two_up.py \
  --in output/test_manual_meta.pdf \
  --out output/test_manual_twoup.pdf \
  --rasterize

echo "✅ Check: output/test_manual_twoup.pdf"
```

---

**Example 4: Add Footer**
```bash
python tools/pdf_composer/pdf_footer_stamp_dark.py \
  --in output/test_manual_twoup.pdf \
  --out output/test_manual_final.pdf \
  --left "SonicBuilder Test" \
  --center "v2.1.0" \
  --right "© 2025"

echo "✅ Check: output/test_manual_final.pdf"
```

---

**Example 5: Verify Metadata**
```bash
python tools/pdf_composer/pdf_verify_metadata.py \
  --in output/test_manual_final.pdf

# Expected output:
# ✅ Title: SonicBuilder Test Manual
# ✅ Author: Christopher Elgin
# ✅ Subject: Testing PDF Tools
# ✅ Keywords: Test,SonicBuilder,PDF
```

---

### Test ImageSuite Generators

**Already Generated Examples (see output/examples/):**
- ✅ `cover_example.png` - Dark-themed cover
- ✅ `qr_repo_example.png` - QR code with label
- ✅ `callout_tip.png` - Blue tip callout
- ✅ `callout_warn.png` - Yellow warning callout
- ✅ `callout_danger.png` - Red danger callout

**View examples:**
```bash
ls -lh output/examples/
```

---

## 🎯 Post-Deployment Verification

### After pushing to GitHub, verify:

**1. Workflows appear in Actions tab**
```
✅ pr-docs-ready-command
✅ pr-docs-reset-command  
✅ pr-docs-ready-autoreset
✅ pr-merge-guard (updated)
```

**2. Test on a real PR**
```
✅ Create test PR
✅ Try /docs-ready command
✅ Verify label applied
✅ Try /docs-reset command
✅ Verify label removed
```

**3. Check documentation renders**
```
✅ docs/PR_AUTOMATION.md shows slash commands
✅ docs/TOOLS_REFERENCE.md complete
✅ tools/README.md accessible
```

---

## 🚀 Next Steps

After successful deployment:

1. **Update README badges** (if not already done)
   - Point to m9dswyptrn-web/SonicBuilder

2. **Test complete release workflow**
   ```bash
   make release_checklist VERSION=v2.1.0
   make release_tag VERSION=v2.1.0
   git push --tags
   ```

3. **Monitor first automated release**
   - Check badges update
   - Verify release notes enriched
   - Confirm checklist appended

4. **Try the new tools**
   - Generate custom assets with ImageSuite
   - Compose PDFs with PDF Composer
   - Build complete documentation packages

---

## 📊 Success Metrics

**You'll know deployment succeeded when:**
- ✅ 24 workflows show in GitHub Actions
- ✅ Slash commands work on PRs
- ✅ Auto-reset triggers on new commits
- ✅ Merge guard posts helpful comments
- ✅ Example assets generated successfully
- ✅ All documentation renders correctly

---

**Ready to deploy!** 🚀

Follow this checklist step by step for a smooth deployment.
