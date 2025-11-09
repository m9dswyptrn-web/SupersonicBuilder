# CI/CD Troubleshooting Guide

Complete troubleshooting guide for SonicBuilder CI/CD workflows, covering common issues and solutions.

---

## 🔍 Quick Diagnosis

### Workflow Won't Start
- ✅ Check file paths in workflow triggers
- ✅ Verify workflow YAML syntax
- ✅ Check repository permissions

### Workflow Fails
- ✅ Check workflow logs in Actions tab
- ✅ Verify secrets are configured
- ✅ Check dependency installation

### Files Not Generated
- ✅ Verify input files exist
- ✅ Check script permissions
- ✅ Review script output logs

---

## 📦 Common Issues & Solutions

### 1. Poppler Utils / pdf2image Issues

#### Error: `pdf2image requires poppler-utils`
```
ERROR: pdf2image.exceptions.PDFInfoNotInstalledError: 
Unable to get page count. Is poppler installed and in PATH?
```

**Cause:** Poppler not installed in CI environment

**Solution (GitHub Actions):**
```yaml
- name: Install dependencies
  run: |
    pip install reportlab pypdf pillow qrcode pdf2image
    sudo apt-get update
    sudo apt-get install -y poppler-utils
```

**Solution (Local):**
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Test
pdftoppm -v
```

**Note:** `poppler-utils` is only needed for 2-up PDF rasterization. Other features work without it.

---

### 2. Makefile Include Errors

#### Error: `makefile:X: MAKEFRAG.*: No such file or directory`
```
Makefile:10: MAKEFRAG.urls: No such file or directory
make: *** No rule to make target 'MAKEFRAG.urls'. Stop.
```

**Cause:** Fragment files missing or wrong path

**Solution 1: Use `-include` (silent failure)**
```makefile
# Use dash prefix to suppress errors if file doesn't exist
-include make_patches/MAKEFRAG.urls
-include make_patches/MAKEFRAG.repo
-include make_patches/MAKEFRAG.two_up_qr
-include make_patches/MAKEFRAG.onebutton
```

**Solution 2: Create missing files**
```bash
mkdir -p make_patches
touch make_patches/MAKEFRAG.urls
touch make_patches/MAKEFRAG.repo
touch make_patches/MAKEFRAG.two_up_qr
touch make_patches/MAKEFRAG.onebutton
```

**Solution 3: Verify paths**
```bash
# Check files exist
ls -lh make_patches/MAKEFRAG.*

# Check from Makefile location
cat Makefile | grep include
```

---

### 3. GitHub Secrets Not Found

#### Error: `secrets.SB_NOTIFY_WEBHOOK is not set`
```
Error: Secret "SB_NOTIFY_WEBHOOK" not found
```

**Cause:** Secret not configured in repository

**Solution:**
1. Go to repository Settings
2. Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `SB_NOTIFY_WEBHOOK` (exact match, case-sensitive)
5. Value: Your webhook URL
6. Save

**Verify:**
```yaml
# In workflow
- name: Check secret
  run: |
    if [ -z "${{ secrets.SB_NOTIFY_WEBHOOK }}" ]; then
      echo "Secret not configured"
      exit 1
    fi
```

**Debug:**
```yaml
# Show if secret exists (not value!)
- name: Debug
  run: |
    echo "Secret exists: ${{ secrets.SB_NOTIFY_WEBHOOK != '' }}"
```

---

### 4. URL Canonicalization Issues

#### Problem: QR codes show wrong URL
```
Expected: https://github.com/owner/repo
Actual:   https://replit.dev/...
```

**Cause:** `SB_REPO_URL` not propagating to subprocesses

**Solution: Add `env=os.environ.copy()` to subprocess calls**

**Before (wrong):**
```python
subprocess.check_call(cmd)
```

**After (correct):**
```python
import os
subprocess.check_call(cmd, env=os.environ.copy())
```

**Workflow usage:**
```yaml
jobs:
  setup-url:
    uses: ./.github/workflows/repo-url-setup.yml

  build:
    needs: [setup-url]
    env:
      SB_REPO_URL: ${{ needs.setup-url.outputs.SB_REPO_URL }}
    steps:
      - run: python scripts/i2s_index.py  # Now has SB_REPO_URL
```

**Verify:**
```bash
# Check metadata.json for correct URL
cat Appendix/C_I2S_Integration/metadata.json | jq .base_url
```

---

### 5. Workflow Doesn't Trigger

#### Problem: Pushed changes but workflow didn't run

**Check trigger paths:**
```yaml
on:
  push:
    paths:
      - 'Appendix/C_I2S_Integration/PCB_Photos/**'  # Must match exactly
```

**Common mistakes:**
- Trailing slashes
- Wrong case
- Missing `**` for subdirectories

**Debug:**
```bash
# Check what was committed
git diff HEAD~1 --name-only

# Should show path matching workflow trigger
Appendix/C_I2S_Integration/PCB_Photos/file.jpg
```

**Solution:**
```bash
# Ensure exact path match
git add Appendix/C_I2S_Integration/PCB_Photos/file.jpg
git commit -m "docs: trigger workflow"
git push
```

---

### 6. Version Detection Fails

#### Error: `VERSION file not found`
```
cat: VERSION: No such file or directory
```

**Solution 1: Create VERSION file**
```bash
echo "2.0.9" > VERSION
git add VERSION
git commit -m "chore: add VERSION file"
```

**Solution 2: Fallback in workflow**
```yaml
- name: Determine version
  id: version
  run: |
    if [ -f VERSION ]; then
      VERSION=$(cat VERSION | tr -d '\n' | sed 's/^/v/')
    elif [ -n "${{ github.ref_name }}" ]; then
      VERSION=${{ github.ref_name }}
    else
      VERSION="v2.0.9"  # Fallback
    fi
    echo "VERSION=$VERSION" >> $GITHUB_OUTPUT
```

---

### 7. Python Import Errors

#### Error: `ModuleNotFoundError: No module named 'reportlab'`

**Cause:** Dependencies not installed

**Solution:**
```yaml
- name: Install Python dependencies
  run: |
    pip install --upgrade pip
    pip install reportlab pypdf pillow qrcode pdf2image
```

**For scripts/repo_url.py:**
```python
# Add path for imports
import sys
sys.path.insert(0, 'scripts')
from repo_url import resolve_repo_url
```

---

### 8. File Permissions Errors

#### Error: `Permission denied: ./scripts/notify.py`

**Cause:** Script not executable

**Solution:**
```bash
# Make executable
chmod +x scripts/notify.py
git add scripts/notify.py
git commit -m "fix: make script executable"
```

**Or in workflow:**
```yaml
- name: Run script
  run: python scripts/notify.py  # Use python instead of ./
```

---

### 9. Artifact Upload Fails

#### Error: `No files found matching pattern`

**Cause:** Files not generated or wrong path

**Debug:**
```yaml
- name: List files before upload
  run: |
    echo "=== Generated files ==="
    ls -lhR Appendix/C_I2S_Integration/
```

**Solution:**
```yaml
- name: Upload artifacts
  uses: actions/upload-artifact@v4
  with:
    name: appendix-c
    path: |
      Appendix/C_I2S_Integration/*.pdf
      Appendix/C_I2S_Integration/*.csv
    if-no-files-found: warn  # Don't fail if missing
```

---

### 10. Release Not Created

#### Problem: Tag pushed but no release

**Check:**
1. Tag format matches trigger (`v*`)
2. Repository has releases enabled
3. Workflow has `contents: write` permission

**Solution:**
```yaml
permissions:
  contents: write  # Required for creating releases

on:
  push:
    tags:
      - 'v*'  # Only tags starting with 'v'
```

**Verify tag:**
```bash
# List tags
git tag -l

# Check tag format
git tag v2.0.9  # Good: starts with 'v'
git tag 2.0.9   # Bad: doesn't match 'v*'
```

---

### 11. Release Notes Not Enriched

#### Problem: Assets table not appearing

**Check:**
1. `release-notes-enricher.yml` ran (check Actions)
2. `release-appendixC.yml` completed first
3. Secrets configured

**Debug:**
```yaml
- name: Check release body
  run: |
    curl -s https://api.github.com/repos/${{ github.repository }}/releases/latest \
      | jq .body
```

**Solution:**
Re-run enricher workflow manually:
1. Go to Actions
2. Find "Enrich Release Notes"
3. Click "Re-run all jobs"

---

### 12. Idempotent Markers Not Working

#### Problem: Duplicate tables in release notes

**Cause:** Old enricher without HTML markers

**Solution: Update to marker-based enricher**
```yaml
# Check for markers
if echo "$CURRENT_BODY" | grep -q "<!-- SB_ASSETS_TABLE_BEGIN -->"; then
  # Update existing
else
  # Add new
fi
```

**Manual fix:**
1. Edit release on GitHub
2. Remove duplicate tables
3. Re-run enricher workflow

---

### 13. Build Takes Too Long

#### Problem: Workflow times out or takes >10 minutes

**Common causes:**
- Large PDF files
- Network slowness
- Unnecessary steps

**Solutions:**
```yaml
# Cache Python dependencies
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# Skip unnecessary installs
- name: Check if dependencies needed
  id: check
  run: echo "needs_install=${{ steps.cache.outputs.cache-hit != 'true' }}" >> $GITHUB_OUTPUT
  
- name: Install dependencies
  if: steps.check.outputs.needs_install == 'true'
  run: pip install -r requirements.txt
```

---

### 14. Notification Not Sent

#### Error: `Failed to send notification`

**Check:**
1. Webhook URL is valid
2. Secret is configured
3. Notification script has `requests` installed

**Debug:**
```bash
# Test webhook locally
curl -X POST "$SB_NOTIFY_WEBHOOK" \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test"}'
```

**Solution:**
```yaml
- name: Install requests (for notifications)
  run: pip install requests

- name: Send notification
  if: always()
  run: |
    python scripts/notify.py \
      --webhook "${{ secrets.SB_NOTIFY_WEBHOOK }}" \
      --message "Build complete"
```

---

## 🔧 Debugging Workflows

### Enable Debug Logging
```yaml
- name: Debug info
  run: |
    echo "::debug::Current directory: $(pwd)"
    echo "::debug::Files: $(ls -la)"
    echo "::debug::Environment: $(env | sort)"
```

### Add Step Summaries
```yaml
- name: Create summary
  run: |
    echo "## Build Summary" >> $GITHUB_STEP_SUMMARY
    echo "Version: $VERSION" >> $GITHUB_STEP_SUMMARY
    echo "Files generated: $(ls *.pdf | wc -l)" >> $GITHUB_STEP_SUMMARY
```

### Workflow Artifacts for Debugging
```yaml
- name: Upload logs on failure
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: debug-logs
    path: |
      **/*.log
      **/*.txt
```

---

## 📚 Quick Reference

### Workflow Logs
```bash
# View workflow logs
https://github.com/OWNER/REPO/actions

# Download logs
gh run view RUN_ID --log
```

### Common Commands
```bash
# Test locally
make all VERSION=v2.0.9

# Verify files
ls -lh Appendix/C_I2S_Integration/*.pdf

# Check secrets (don't show values!)
gh secret list

# Re-run workflow
gh run rerun RUN_ID
```

### File Checks
```bash
# Verify Makefile includes
grep "^-include" Makefile

# Check script permissions
ls -lh scripts/*.py

# Verify VERSION file
cat VERSION
```

---

## 🆘 Getting Help

### Check These First
1. Workflow logs in Actions tab
2. This troubleshooting guide
3. Related documentation (CI_APPENDIXC_GUIDE.md, etc.)

### Still Stuck?
1. Enable debug logging
2. Check each step's output
3. Test locally with same versions
4. Verify all files exist

### Report Issues
Include:
- Workflow name
- Error message
- Steps to reproduce
- Workflow logs (sanitized)

---

## ✅ Preventive Measures

### Before Committing
```bash
# Test locally
make all VERSION=v2.0.9

# Verify files generated
ls -lh Appendix/C_I2S_Integration/*.pdf

# Check Makefile syntax
make -n all
```

### Before Tagging
```bash
# Verify VERSION file
cat VERSION

# Check workflows are passing
gh run list --limit 5

# Test notification
source .env.local
python scripts/notify.py --message "Test"
```

### After Changes
1. Check workflow triggered
2. Monitor Actions tab
3. Verify outputs
4. Test downloads

---

**With these solutions, your CI/CD pipeline should run smoothly!** 🚀
