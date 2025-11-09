# GitHub Pages Workflow Cleanup Guide

## 📋 **Current Workflow Status**

You have **6 Pages-related workflows**. Here's what they do and which ones to keep:

---

## ✅ **Keep These (Active)**

### **1. `pages-publish.yml`** (NEW - Main workflow)
**Purpose:** Publish latest PDF to GitHub Pages  
**Triggers:** Push (PDFs), Release, Manual  
**Keep:** ✅ YES - This is your main Pages deployment  

### **2. `pages-smoke.yml`** (UPDATED - Smoke test)
**Purpose:** Verify latest.pdf is reachable after deployment  
**Triggers:** After pages-publish, Manual  
**Keep:** ✅ YES - Auto-tests your deployment  

### **3. `readme-stamp.yml`** (NEW - Auto-stamping)
**Purpose:** Auto-update README footer with version/commit/time  
**Triggers:** Push, Release, Manual  
**Keep:** ✅ YES - Keeps README metadata current  

---

## ❌ **Remove These (Duplicates/Old)**

### **4. `pages-latest.yml`** (OLD)
**Status:** ⚠️ REPLACED by `pages-publish.yml`  
**Action:** DELETE - Same functionality, different name  

### **5. `pages.yml`** (OLD - Full docs site)
**Status:** ⚠️ OPTIONAL - Full documentation site workflow  
**Action:** Keep if you want full docs site, DELETE if using minimal version  

### **6. `pages-smoke-badge.yml`** (DUPLICATE)
**Status:** ⚠️ DUPLICATE of `pages-smoke.yml`  
**Action:** DELETE - Use simplified `pages-smoke.yml` instead  

### **7. `pages-smoketest.yml`** (DUPLICATE)
**Status:** ⚠️ DUPLICATE of `pages-smoke.yml`  
**Action:** DELETE - Use simplified `pages-smoke.yml` instead  

---

## 🗑️ **Cleanup Commands**

### **Option 1: Remove All Duplicates (Recommended)**

```bash
git rm .github/workflows/pages-latest.yml
git rm .github/workflows/pages-smoke-badge.yml
git rm .github/workflows/pages-smoketest.yml
git rm .github/workflows/pages.yml  # If you don't need full docs site
git commit -m "ci: cleanup duplicate Pages workflows"
git push
```

**Result:** Keep only 3 workflows:
- `pages-publish.yml` (deployment)
- `pages-smoke.yml` (testing)
- `readme-stamp.yml` (auto-stamping)

### **Option 2: Keep Full Docs Site**

If you want to keep the full documentation site with dark theme:

```bash
git rm .github/workflows/pages-latest.yml
git rm .github/workflows/pages-smoke-badge.yml
git rm .github/workflows/pages-smoketest.yml
git commit -m "ci: cleanup duplicate Pages workflows, keep full docs"
git push
```

**Result:** Keep 4 workflows:
- `pages-publish.yml` (minimal PDF deployment)
- `pages.yml` (full docs site with dark theme)
- `pages-smoke.yml` (testing)
- `readme-stamp.yml` (auto-stamping)

**Note:** With both `pages-publish.yml` and `pages.yml`, you have TWO deployment options:
- Use `pages-publish.yml` for minimal fast deployment
- Use `pages.yml` for full featured docs site

---

## 📊 **Workflow Comparison**

| Workflow | Purpose | Size | Speed | Keep? |
|----------|---------|------|-------|-------|
| **pages-publish.yml** | Minimal PDF hosting | ~5MB | ~1 min | ✅ YES |
| **pages-smoke.yml** | Verify deployment | N/A | ~10 sec | ✅ YES |
| **readme-stamp.yml** | Auto-stamp README | N/A | ~10 sec | ✅ YES |
| pages-latest.yml | OLD minimal (duplicate) | ~5MB | ~1 min | ❌ DELETE |
| pages.yml | Full docs site | ~10MB | ~2 min | ⚠️ OPTIONAL |
| pages-smoke-badge.yml | OLD smoke (duplicate) | N/A | ~10 sec | ❌ DELETE |
| pages-smoketest.yml | OLD smoke (duplicate) | N/A | ~10 sec | ❌ DELETE |

---

## 🎯 **Recommended Setup**

### **For Simple PDF Distribution:**

**Keep 3 workflows:**
1. `pages-publish.yml` - Publish latest PDF
2. `pages-smoke.yml` - Verify deployment
3. `readme-stamp.yml` - Auto-stamp README

**Delete:**
- `pages-latest.yml`
- `pages.yml`
- `pages-smoke-badge.yml`
- `pages-smoketest.yml`

### **For Full Documentation Site:**

**Keep 4 workflows:**
1. `pages.yml` - Full docs site with dark theme
2. `pages-smoke.yml` - Verify deployment
3. `readme-stamp.yml` - Auto-stamp README
4. (Optional) `pages-publish.yml` - Quick minimal deployment

**Delete:**
- `pages-latest.yml` (duplicate of pages-publish.yml)
- `pages-smoke-badge.yml` (old version)
- `pages-smoketest.yml` (old version)

---

## 🔍 **How to Check What Each Does**

```bash
# View workflow file
cat .github/workflows/pages-publish.yml | head -20

# Check recent runs
gh run list --workflow=pages-publish.yml --limit 5

# View workflow triggers
grep -A5 "^on:" .github/workflows/pages-publish.yml
```

---

## ✅ **After Cleanup**

### **Verify Workflows:**
```bash
ls -1 .github/workflows/pages*.yml
# Should show only 2-3 files (depending on your choice)

ls -1 .github/workflows/readme*.yml
# Should show only 1 file (readme-stamp.yml)
```

### **Test Deployment:**
```bash
# Trigger main deployment
make pages
# Or: gh workflow run pages-publish.yml

# Check it worked
gh run list --limit 3
```

### **Update Makefile:**

If you deleted workflows, update Makefile target names:
```makefile
pages:
	gh workflow run pages-publish.yml -R m9dswyptrn-web/SonicBuilder
	@echo "Triggered Pages publish."
```

---

## 📝 **Summary**

**Current:** 6 Pages workflows (3 duplicates)  
**Recommended:** 3 workflows (publish + smoke + stamp)  
**Optional:** 4 workflows (if you want both minimal + full docs)

**Cleanup Command:**
```bash
git rm .github/workflows/pages-latest.yml \
       .github/workflows/pages-smoke-badge.yml \
       .github/workflows/pages-smoketest.yml
git commit -m "ci: cleanup duplicate Pages workflows"
git push
```

---

**Clean up whenever you're ready to simplify your CI/CD! 🧹**
