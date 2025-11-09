# 📛 SonicBuilder Badges MegaPack - Complete Guide

**Automated badge system with README integration and CI/CD workflows**

---

## ✅ What's Installed

The Badges MegaPack provides a complete automated badge system:

### **Components**

1. **Badge Scripts** (`scripts/badges/`)
   - `update_readme_badges.py` - Auto-updates README badge block

2. **Badge JSONs** (`docs/badges/`)
   - `pages_smoke.json` - GitHub Pages availability status
   - `docs_coverage.json` - PDF documentation coverage

3. **Makefile Fragment** (`Makefrag.badges`)
   - `make install_badges` - Install/refresh badges in README
   - `make update_readme_badges` - Update badges with current repo info
   - `make verify_badges` - Verify badge JSON files exist

4. **GitHub Actions Workflows** (`.github/workflows/`)
   - `pages-smoke.yml` - Monitor Pages availability (every 30 min)
   - `docs-coverage.yml` - Monitor PDF coverage (every 6 hours)

---

## 🚀 Quick Start

### **1. Install Badges in README**

```bash
make install_badges
```

This adds the badge block to your `README.md`:

```markdown
<!-- SONICBUILDER:DOCS-BADGES:START -->
<p align="center">

<a href="https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/docs-release.yml">
  <img alt="Docs Release" src="https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/docs-release.yml?label=Docs%20Release&logo=github">
</a>
&nbsp;
<a href="https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/docs-build.yml">
  <img alt="Docs Build" src="https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/docs-build.yml?label=Docs%20Build&logo=github">
</a>
&nbsp;
<a href="https://m9dswyptrn-web.github.io/SonicBuilder">
  <img alt="Pages Smoke" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fm9dswyptrn-web%2FSonicBuilder%2Fmain%2Fdocs%2Fbadges%2Fpages_smoke.json">
</a>
&nbsp;
<a href="https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/docs-coverage.yml">
  <img alt="Docs Coverage" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fm9dswyptrn-web%2FSonicBuilder%2Fmain%2Fdocs%2Fbadges%2Fdocs_coverage.json">
</a>

</p>

**Latest Docs:**  
- Release: [Releases](https://github.com/m9dswyptrn-web/SonicBuilder/releases)  
- Pages: [https://m9dswyptrn-web.github.io/SonicBuilder](https://m9dswyptrn-web.github.io/SonicBuilder)
<!-- SONICBUILDER:DOCS-BADGES:END -->
```

---

### **2. Update Badge URLs**

If you change owner/repo or want to refresh:

```bash
make update_readme_badges
```

This automatically detects your GitHub owner and repo from git config.

---

### **3. Verify Installation**

```bash
make verify_badges
```

Output:
```
[SB] Badge JSONs present.
```

---

## 📊 Badge System

### **Pages Smoke Badge** 🧪

**Purpose:** Monitor GitHub Pages availability

**Workflow:** `.github/workflows/pages-smoke.yml`

**Update Schedule:**
- Every 30 minutes (cron: `*/30 * * * *`)
- Manual dispatch

**Badge States:**
- 🟢 **online** - Pages returned HTTP 200
- 🟠 **timeout** - Request timed out
- 🔴 **error:XXX** - HTTP error code XXX

**JSON Location:** `docs/badges/pages_smoke.json`

**Example:**
```json
{"schemaVersion":1,"label":"pages","message":"online","color":"brightgreen"}
```

---

### **Docs Coverage Badge** 📚

**Purpose:** Monitor PDF documentation coverage

**Workflow:** `.github/workflows/docs-coverage.yml`

**Update Schedule:**
- Every 6 hours (cron: `0 */6 * * *`)
- Manual dispatch

**Badge States:**
- 🟢 **N pdf(s)** - Found N PDFs in dist/
- 🔴 **no pdfs** - No PDFs found

**JSON Location:** `docs/badges/docs_coverage.json`

**Example:**
```json
{"schemaVersion":1,"label":"docs","message":"2 pdf(s)","color":"brightgreen"}
```

---

## 🎯 Makefile Targets

### **install_badges**

```bash
make install_badges
```

**What it does:**
1. Detects owner/repo from git remote
2. Generates badge block with correct URLs
3. Injects or updates badge block in README.md
4. Preserves existing content

**Use when:**
- First time setup
- After cloning to new repo
- After changing repository name

---

### **update_readme_badges**

```bash
make update_readme_badges
```

**What it does:**
1. Re-reads current git remote
2. Updates all badge URLs
3. Refreshes README badge block

**Use when:**
- After changing GitHub owner
- After renaming repository
- Periodic maintenance

---

### **verify_badges**

```bash
make verify_badges
```

**What it does:**
- Checks `docs/badges/pages_smoke.json` exists
- Checks `docs/badges/docs_coverage.json` exists
- Exits with error if missing

**Use when:**
- Before deployment
- In CI/CD preflight checks
- Debugging badge issues

---

## 🤖 GitHub Actions Integration

### **Pages Smoke Workflow**

**File:** `.github/workflows/pages-smoke.yml`

**Triggers:**
```yaml
on:
  schedule:
    - cron: "*/30 * * * *"  # Every 30 minutes
  workflow_dispatch:         # Manual run
```

**What it does:**
1. Checks GitHub Pages URL with `curl`
2. Captures HTTP status code
3. Writes badge JSON based on result
4. Commits and pushes to repo (auto-update)

**Permissions needed:**
```yaml
permissions:
  contents: write  # To commit badge JSON
```

---

### **Docs Coverage Workflow**

**File:** `.github/workflows/docs-coverage.yml`

**Triggers:**
```yaml
on:
  schedule:
    - cron: "0 */6 * * *"  # Every 6 hours
  workflow_dispatch:        # Manual run
```

**What it does:**
1. Counts PDF files in `dist/` directory
2. Generates badge JSON with count
3. Commits and pushes to repo (auto-update)

**Permissions needed:**
```yaml
permissions:
  contents: write  # To commit badge JSON
```

---

## 📁 File Structure

```
SonicBuilder/
├── scripts/badges/
│   └── update_readme_badges.py      # Badge injector
├── docs/badges/
│   ├── pages_smoke.json             # Pages status (auto-updated)
│   └── docs_coverage.json           # Docs status (auto-updated)
├── .github/workflows/
│   ├── pages-smoke.yml              # Pages monitor
│   └── docs-coverage.yml            # Coverage monitor
├── Makefrag.badges                  # Makefile fragment
├── Makefile                         # Includes Makefrag.badges
└── README.md                        # Badge block injected
```

---

## 🔧 Customization

### **Change Badge Labels**

Edit `scripts/badges/update_readme_badges.py`:

```python
# Change badge labels
BADGE_BLOCK_START = "<!-- CUSTOM:BADGES:START -->"
BADGE_BLOCK_END   = "<!-- CUSTOM:BADGES:END -->"
```

---

### **Add Custom Badges**

Add to the `block` variable in `update_readme_badges.py`:

```python
block = f"""...
<a href="https://example.com">
  <img alt="Custom Badge" src="https://img.shields.io/badge/custom-badge-blue">
</a>
...
"""
```

---

### **Change Update Frequency**

Edit workflow cron schedules:

```yaml
# Update every hour instead of every 30 min
on:
  schedule:
    - cron: "0 * * * *"
```

---

## 🚀 Deployment Workflow

### **Typical Usage**

```bash
# 1. Install badges initially
make install_badges

# 2. Verify
make verify_badges

# 3. Commit
git add README.md docs/badges/ Makefrag.badges scripts/badges/
git commit -m "feat(badges): add badges megapack"
git push

# 4. Badges auto-update via GitHub Actions
# - Pages smoke: every 30 min
# - Docs coverage: every 6 hours
```

---

### **Integration with Ship Pipeline**

Add to your deployment workflow:

```bash
# Before ship
make verify_badges

# Update badges
make update_readme_badges

# Ship
make ship
```

Or in `Makefile`:

```makefile
ship: verify_badges
	@make update_readme_badges
	@./scripts/git_auto_commit.sh "chore(deploy): automated ship"
	@git push
	@echo "Shipped! Badges will auto-update."
```

---

## 🔍 Troubleshooting

### **Badge shows "unknown"**

**Cause:** Badge JSON not committed to repo

**Fix:**
```bash
# Check files exist
ls docs/badges/

# Commit them
git add docs/badges/
git commit -m "chore: add badge JSONs"
git push
```

---

### **Badge URLs broken after repo rename**

**Cause:** Badge URLs still use old owner/repo

**Fix:**
```bash
make update_readme_badges
git add README.md
git commit -m "chore: update badge URLs"
git push
```

---

### **Workflow not running**

**Cause:** Workflow permissions or schedule issues

**Fix:**
1. Check workflow permissions in repo settings
2. Enable Actions if disabled
3. Run manually via Actions tab → "Run workflow"

---

### **Badge shows stale data**

**Cause:** Shields.io caching or workflow not running

**Fix:**
1. Check last workflow run:
   ```
   https://github.com/m9dswyptrn-web/SonicBuilder/actions
   ```
2. Trigger manual run
3. Wait 5 minutes for Shields.io cache refresh

---

## ✅ Verification Checklist

- [ ] `scripts/badges/update_readme_badges.py` exists
- [ ] `docs/badges/pages_smoke.json` exists
- [ ] `docs/badges/docs_coverage.json` exists
- [ ] `Makefrag.badges` exists
- [ ] `Makefile` includes `Makefrag.badges`
- [ ] `.github/workflows/pages-smoke.yml` exists
- [ ] `.github/workflows/docs-coverage.yml` exists
- [ ] `make verify_badges` passes
- [ ] README.md contains badge block
- [ ] Badges display in README

---

## 📚 Complete Badge Suite

Combined with other addons, you now have:

1. **MegaPack Badges** (this guide)
   - Pages Smoke
   - Docs Coverage
   - Auto-updated via GitHub Actions

2. **Previous Badge Addons**
   - Docs Coverage Badge (release tracking)
   - Pages Smoke Badge (gallery monitoring)
   - Bundle Status Badge (release validation)

**Total:** 6+ live status badges! 🎉

---

**Generated:** October 30, 2025  
**Version:** SonicBuilder Badges MegaPack v1  
**Status:** ✅ Production Ready
