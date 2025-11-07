# GitHub Actions CI/CD Workflow Guide

**Workflow:** `.github/workflows/docs-release.yml`  
**Version:** v2.2.3 + Diagnostics/Support Bundle Integration  
**Last Updated:** October 29, 2025

---

## 🎯 Overview

The SonicBuilder CI/CD pipeline automatically builds documentation, creates diagnostics bundles, and publishes releases when you push a git tag.

---

## 📊 Workflow Structure

```
Tag Push (v*)
    ↓
┌──────────────────┐
│  release-docs    │ ← Builds PDFs and publishes to GitHub Release
└──────────────────┘
    ↓           ↓
    │           └─────────────┐
    ↓                         ↓
┌──────────────────┐   ┌──────────────────┐
│ diagnostic-run   │   │ support-bundle   │
└──────────────────┘   └──────────────────┘
Uploads CI artifact    Uploads to artifact + release
```

---

## 🔄 Jobs Reference

### 1️⃣ **release-docs** (Main Build)

**Triggers:** On git tag push (`v*`)  
**Dependencies:** None (runs first)  
**Runtime:** ~2-5 minutes

**Steps:**
1. Checkout code
2. Install Python 3.11 + dependencies
3. Build core manual (`supersonic_build_all.py`)
4. Build NextGen appendix (if present)
5. Merge PDFs with commit stamp
6. Upload to GitHub Release:
   - `SonicBuilder_Supersonic_Manual_<tag>.pdf`
   - `NextGen_Appendix_<tag>.pdf`
   - `SonicBuilder_Manual_with_Appendix_<sha>.pdf`

**Output:** Release assets available on GitHub Releases page

---

### 2️⃣ **diagnostic-run** (CI Diagnostics)

**Triggers:** After `release-docs` completes  
**Dependencies:** `release-docs`  
**Runtime:** ~30 seconds

**Steps:**
1. Checkout code
2. Install Python + dependencies
3. Collect project diagnostics (Makefile, scripts, configs, env info)
4. Upload as workflow artifact

**Output:** 
- Artifact: `diagnostics-<tag>` (~216 KB)
- Retention: 30 days

**Purpose:** 
- Validates build environment
- Captures CI state for troubleshooting
- Provides snapshot of project structure

---

### 3️⃣ **support-bundle** (Support Package)

**Triggers:** After `release-docs` completes  
**Dependencies:** `release-docs`  
**Runtime:** ~30 seconds

**Steps:**
1. Checkout code
2. Install Python + dependencies
3. Create support bundle (same as diagnostics)
4. Upload as workflow artifact
5. Attach to GitHub Release (optional, non-fatal)

**Output:**
- Artifact: `support-bundle-<tag>` (~216 KB)
- Release asset: `support_bundle.zip` (optional)
- Retention: 30 days

**Purpose:**
- Provides complete troubleshooting package
- Available for field support teams
- Includes environment info + project state

---

## 🚀 Usage

### Trigger a Release

```bash
# 1. Commit your changes
git add .
git commit -m "Release v2.2.3: Complete integration"

# 2. Create and push tag
git tag v2.2.3
git push && git push --tags

# 3. GitHub Actions automatically:
#    - Builds documentation PDFs
#    - Creates diagnostics bundle
#    - Creates support bundle
#    - Publishes release with assets
```

### Monitor Workflow

1. Go to GitHub repository → **Actions** tab
2. Find your tag workflow run
3. Monitor each job:
   - ✅ `release-docs` - Main build
   - ✅ `diagnostic-run` - Diagnostics collection
   - ✅ `support-bundle` - Support package

### Download Artifacts

**From Workflow:**
1. Actions tab → Select workflow run
2. Scroll to **Artifacts** section
3. Download:
   - `diagnostics-<tag>` - CI diagnostics
   - `support-bundle-<tag>` - Support bundle

**From Release:**
1. Releases page → Select release
2. Download:
   - Core manual PDF
   - NextGen appendix PDF
   - Merged manual PDF
   - `support_bundle.zip` (if attached)

---

## 📋 Environment Variables Available

| Variable | Example | Description |
|----------|---------|-------------|
| `github.ref_name` | `v2.2.3` | Tag name |
| `github.sha` | `abc123...` | Full commit SHA |
| `github.ref` | `refs/tags/v2.2.3` | Full git ref |

---

## 🔍 What Gets Collected

### Diagnostics Bundle Contents

**Configuration Files:**
- `Makefile`, `.replit`, `requirements*.txt`
- `pyproject.toml`, `setup.cfg`
- `README.md`

**Scripts:**
- `scripts/**/*.py` (under 500 KB)

**Workflows:**
- `.github/workflows/*.yml`

**Documentation:**
- `docs/**/*.md` (under 500 KB)

**Logs:**
- `out/*.log`

**Environment Info:**
- Python version and executable path
- Platform info (OS, architecture)
- `pip freeze` output
- Timezone and timestamp

**Excluded:**
- `.git/`, `node_modules/`, `venv/`, `__pycache__/`
- `exports/` directory
- Large binaries
- Secrets and API keys

---

## ⚙️ Workflow Configuration

### Job Dependencies

```yaml
jobs:
  release-docs:           # Runs first
    # ... build and release
  
  diagnostic-run:         # Runs after release-docs
    needs: [release-docs]
  
  support-bundle:         # Runs after release-docs
    needs: [release-docs]
```

### Parallel Execution

- `diagnostic-run` and `support-bundle` run in **parallel** after `release-docs` completes
- This maximizes speed while ensuring PDFs are built first

### Error Handling

**Graceful Failures:**
- Appendix build failure → Continues (non-fatal)
- PDF merge failure → Continues with individual PDFs
- Support bundle attachment → Continues if fails
- Unmatched file upload → Does not fail workflow

**Fail-Fast:**
- Core manual build failure → Stops workflow
- Dependency installation failure → Stops workflow

---

## 🛠️ Customization

### Add More Artifacts to Release

Edit `.github/workflows/docs-release.yml`:

```yaml
- name: Upload release assets
  uses: softprops/action-gh-release@v2
  with:
    files: |
      out/SonicBuilder_Supersonic_Manual_${{ github.ref_name }}.pdf
      out/NextGen_Appendix_${{ github.ref_name }}.pdf
      out/SonicBuilder_Manual_with_Appendix_${{ github.sha }}.pdf
      out/field_cards_two_up.pdf              # NEW
      out/field_cards_four_up.pdf             # NEW
    fail_on_unmatched_files: false
```

### Change Artifact Retention

Default: 30 days

```yaml
- name: Upload diagnostics
  uses: actions/upload-artifact@v4
  with:
    name: diagnostics-${{ github.ref_name }}
    path: diag/diag_bundle.zip
    retention-days: 90  # Change to 90 days
```

### Add Pre-Release Validation

Add a new job before `release-docs`:

```yaml
jobs:
  validate-setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Run preflight checks
        run: make doctor || python scripts/verify_setup.py

  release-docs:
    needs: [validate-setup]  # Wait for validation
    # ... rest of build
```

---

## 🐛 Troubleshooting

### Workflow Fails on Build Step

**Check:**
1. Review Actions logs for error messages
2. Download `diagnostics-<tag>` artifact for environment info
3. Verify `scripts/supersonic_build_all.py` works locally
4. Check `requirements.txt` has all dependencies

**Fix:**
```bash
# Test locally first
make build-docs
python scripts/supersonic_build_all.py --version test --verify
```

### Missing Appendix Error

**Expected:** Workflow continues gracefully

**If it fails:**
```yaml
# Already configured with fallback:
if [ -f scripts/make_nextgen_appendix.py ]; then
  python scripts/make_nextgen_appendix.py ... || true
fi
```

### Support Bundle Not Attached to Release

**Check:**
- `support-bundle` job completed successfully
- Look in workflow artifacts (always uploaded there)
- Release attachment is optional (`continue-on-error: true`)

**Workaround:**
Download from workflow artifacts instead of release assets

### Diagnostics Bundle Missing Files

**Check bundle contents:**
```bash
# Download diagnostics-<tag>.zip
unzip -l diagnostics-<tag>.zip

# Verify expected files present
```

**Common issue:** Files over 500 KB are excluded

---

## 📊 Performance Metrics

| Job | Typical Runtime | Artifact Size |
|-----|----------------|---------------|
| release-docs | 2-5 min | 1-3 MB (PDFs) |
| diagnostic-run | 20-40 sec | ~216 KB |
| support-bundle | 20-40 sec | ~216 KB |
| **Total** | **~3-6 min** | **~1.5-3.5 MB** |

---

## ✅ Success Checklist

After workflow completes, verify:

- [ ] Release created on GitHub Releases page
- [ ] Core manual PDF uploaded
- [ ] NextGen appendix PDF uploaded (if applicable)
- [ ] Merged manual PDF with commit stamp uploaded
- [ ] `diagnostics-<tag>` artifact available (30 days)
- [ ] `support-bundle-<tag>` artifact available (30 days)
- [ ] All jobs show green checkmarks ✅

---

## 🔗 Related Documentation

- `RELEASE_v2.2.3_INTEGRATION.md` - v2.2.2/v2.2.3 pack integration
- `INTEGRATION_v2.2.3_IDS_WATCH_DIAGNOSTICS_SUPPORTFLOW.md` - Diagnostics/support guide
- `INTEGRATION_COMPLETE_ALL_PACKS.md` - Complete pack summary

---

**Last Updated:** October 29, 2025  
**Workflow Version:** v2.2.3 + Diagnostics  
**Status:** ✅ Production Ready
