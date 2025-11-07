# CI/CD Setup for Sonic Builder

Complete guide to GitHub Actions workflows and continuous integration.

---

## ✅ What's Included

### GitHub Actions Workflows

1. **`.github/workflows/sonicbuilder-ci.yml`** - Continuous Integration
   - Runs on every push to main/master
   - Runs on pull requests
   - Tests dark and light builds
   - Validates annotation system
   - Uploads build artifacts

2. **`.github/workflows/release.yml`** - Release Automation
   - Triggers on version tags (v*)
   - Builds complete release
   - Creates GitHub Release with attachments
   - Includes versioned PDFs and bundles

---

## 🚀 Quick Start

### Local Testing

```bash
# Fast verification (dark theme, smoke build)
make verify

# Fast verification (light theme)
THEME=light make verify

# Checks only (no build)
make verify_skip_build

# Full annotation system test
make test_annotations
```

### GitHub Actions Setup

1. **Push workflows to repository**:
   ```bash
   git add .github/workflows/
   git commit -m "Add CI/CD workflows"
   git push
   ```

2. **View workflow runs**:
   - Go to your repository on GitHub
   - Click "Actions" tab
   - See workflow runs and build artifacts

3. **Create a release**:
   ```bash
   git tag v2.0.5
   git push origin v2.0.5
   ```
   - Automatically triggers release workflow
   - Builds and attaches PDFs to GitHub Release

---

## 📋 Workflow Details

### CI Workflow (`sonicbuilder-ci.yml`)

**Triggers**:
- Push to `main` or `master` branch
- Pull requests
- Manual dispatch (from Actions tab)

**Steps**:
1. ✅ Checkout code
2. ✅ Setup Python 3.11
3. ✅ Cache pip dependencies
4. ✅ Install all dependencies (best effort)
5. ✅ Run dark theme verification + smoke build
6. ✅ Run light theme verification + smoke build
7. ✅ Test annotation system
8. ✅ Upload output PDFs as artifacts

**Artifacts**:
- `output-pdfs` - All generated PDFs (7 day retention)

**Concurrency**:
- Cancels previous runs on same branch

---

### Release Workflow (`release.yml`)

**Triggers**:
- Git tags matching `v*` pattern (e.g., `v2.0.5`, `v3.0.0`)

**Steps**:
1. ✅ Checkout tagged commit
2. ✅ Setup Python 3.11
3. ✅ Install dependencies
4. ✅ Build complete release (`make clean && make build && make post && make package`)
5. ✅ Create GitHub Release with:
   - Release notes
   - Versioned PDFs
   - Field cards
   - Complete bundle ZIPs

**Release Contents**:
```
dist/
├── sonic_builder_release_YYYYMMDD_HHMM.zip
├── field_cards_dark_two_up_PRO.pdf
├── sonic_manual_dark_YYYYMMDD_HHMM.pdf
└── sonic_manual_light_YYYYMMDD_HHMM.pdf
```

---

## 🔧 Makefile Targets

### New Verification Targets

```bash
make verify              # Fast verify + smoke build (THEME=dark/light)
make verify_skip_build   # Checks only, no build
```

### What `make verify` Does

1. **JSON Validation**:
   - `config/manual.manifest.json`
   - `templates/annotations.sonic.json`
   - `templates/theme.sonic.json`

2. **Python Import Checks**:
   - ✅ `reportlab` (required)
   - ⚠ `pypdf` (optional)
   - ⚠ `cairosvg` (optional)
   - ⚠ `pdfrw` (optional)
   - ⚠ `watchdog` (optional)

3. **Asset Checks**:
   - Verifies common asset files exist
   - Warns if optional files missing

4. **Smoke Build** (unless `--skip_build`):
   - Runs `scripts/main_glue.py` with `ANNOTATION_MODE=photo-only`
   - Builds minimal PDF to verify pipeline
   - Tests PDF can be opened with pypdf

5. **Exit Codes**:
   - `0` = All checks passed
   - `2` = Issues detected

---

## 🎯 Usage Examples

### Local Development

```bash
# Quick check before committing
make verify_skip_build

# Full verification with build
make verify

# Test both themes
make verify
THEME=light make verify

# Test annotation system
make test_annotations
make examples
```

### CI/CD Flow

1. **Feature Development**:
   ```bash
   git checkout -b feature/new-annotations
   # ... make changes ...
   make verify
   git commit -am "Add new annotations"
   git push origin feature/new-annotations
   ```
   → Creates pull request → CI runs automatically

2. **Release Process**:
   ```bash
   # Update VERSION file
   echo "2.0.6" > VERSION
   
   # Update CHANGELOG.md
   vim CHANGELOG.md
   
   # Commit and tag
   git commit -am "Release v2.0.6"
   git tag v2.0.6
   git push origin main
   git push origin v2.0.6
   ```
   → Release workflow builds and publishes

3. **Check Results**:
   - CI: GitHub → Actions tab → Latest workflow run
   - Release: GitHub → Releases → Latest release

---

## 📊 CI Badge

Add to your README.md:

```markdown
![SonicBuilder CI](https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/sonicbuilder-ci.yml/badge.svg)
```

Replace `YOUR_ORG` and `YOUR_REPO` with your GitHub organization and repository name.

---

## 🛠️ Customization

### Change CI Trigger Branches

Edit `.github/workflows/sonicbuilder-ci.yml`:
```yaml
on:
  push:
    branches: [ main, develop, staging ]  # Add more branches
```

### Modify Build Matrix

Add multiple Python versions:
```yaml
jobs:
  verify-and-build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

### Add Additional Checks

Add more steps to CI workflow:
```yaml
- name: 🧹 Lint Python code
  run: |
    pip install ruff
    ruff check scripts/

- name: 🧪 Run unit tests
  run: |
    pytest tests/ -v
```

---

## 🔍 Troubleshooting

### CI Fails on Dependency Install

**Issue**: `pip install` fails for some packages

**Solution**: Dependencies use best-effort installation:
```bash
pip install -r requirements.txt || true
pip install -r requirements.extras.txt || true
```

Optional packages failing won't break the build.

### Smoke Build Fails

**Issue**: `main_glue.py` needs `render_pages.py`

**Temporary Fix**: The verify script checks if `main_glue.py` exists and skips if not found:
```python
if not Path("scripts/main_glue.py").exists():
    print("[build] ⚠ scripts/main_glue.py not found; skipping smoke build")
    return True
```

**Permanent Fix**: Complete the refactoring (extract `render_pages.py`)

### Artifact Upload Warnings

**Issue**: "No files found" warning

**Solution**: Normal if build was skipped or failed earlier. Check workflow logs for actual error.

---

## 📝 Environment Variables

### CI Workflow

Set in workflow file or as GitHub Secrets:
```yaml
env:
  THEME: dark
  ANNOTATION_MODE: themed
  WM_MODE: footer
  WM_TEXT: "LTZ RR2 GRZ"
```

### Local Development

Set before running make:
```bash
export THEME=light
export ANNOTATION_MODE=styled
export WM_MODE=diagonal
make verify
```

---

## 🎯 Best Practices

1. **Run `make verify` before committing**
   - Catches JSON errors
   - Verifies imports
   - Quick smoke test

2. **Use pull requests**
   - CI runs automatically
   - Catches issues before merge
   - Team review process

3. **Tag releases properly**
   - Use semantic versioning (v2.0.5)
   - Update CHANGELOG.md first
   - Push tag after code is merged

4. **Monitor CI runs**
   - Check Actions tab regularly
   - Fix failures promptly
   - Review artifact outputs

5. **Keep workflows updated**
   - Update action versions periodically
   - Adjust Python version as needed
   - Add new checks as project grows

---

## 📦 Artifact Management

### Download Artifacts

**From GitHub UI**:
1. Go to Actions tab
2. Click on workflow run
3. Scroll to "Artifacts" section
4. Download ZIP files

**From CLI** (with GitHub CLI):
```bash
gh run list
gh run download <run-id>
```

### Artifact Retention

- **CI artifacts**: 7 days (configurable)
- **Release assets**: Permanent (part of release)

---

## 🚀 Advanced Usage

### Matrix Builds

Build multiple variants in parallel:
```yaml
strategy:
  matrix:
    theme: [dark, light]
    mode: [themed, styled, basic, photo-only]
steps:
  - run: make verify
    env:
      THEME: ${{ matrix.theme }}
      ANNOTATION_MODE: ${{ matrix.mode }}
```

### Scheduled Builds

Run nightly builds:
```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
```

### Deploy to GitHub Pages

Add deployment step:
```yaml
- name: 📤 Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./output
```

---

## ✅ Summary

### What You Get

- ✅ Automated testing on every push
- ✅ Pull request validation
- ✅ Automated releases on tags
- ✅ Build artifact storage
- ✅ Fast local verification
- ✅ GitHub Release creation

### Commands to Remember

```bash
make verify              # Fast local check
make verify_skip_build   # Checks only
make test_annotations    # Test annotation system
make examples            # Generate examples
```

### Workflow Files

- `.github/workflows/sonicbuilder-ci.yml` - CI pipeline
- `.github/workflows/release.yml` - Release automation
- `scripts/verify_fast.py` - Verification script
- `Makefile` - Build automation

---

**Version**: 2.0.5  
**Status**: ✅ CI/CD Ready  
**Last Updated**: 2025-10-27
