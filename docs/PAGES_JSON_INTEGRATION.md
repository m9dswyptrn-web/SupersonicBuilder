# GitHub Pages JSON Index & Dynamic Loading

## Overview

Enhanced GitHub Pages deployment with JSON metadata index, dynamic JavaScript loading, and auto-updating README badges.

## Components

### 1. JSON Index Generator (`scripts/pages/make_downloads_json.py`)

Generates `/downloads/index.json` with complete PDF metadata:

```json
{
  "generated": 1730000000,
  "latest": "supersonic_manual_dark.pdf",
  "count": 16,
  "items": [
    {
      "name": "supersonic_manual_dark.pdf",
      "href": "/SonicBuilder/downloads/supersonic_manual_dark.pdf",
      "bytes": 68157440,
      "mb": 65.0,
      "mtime": 1730291040,
      "mtime_iso": "2025-10-30T14:04:00Z",
      "md5": "a1b2c3d4e5f6..."
    }
  ]
}
```

**Features:**
- MD5 hash for integrity verification
- File size in bytes and MB
- Modification timestamp (Unix + ISO format)
- Sorted by newest first
- Auto-excludes `latest.pdf` symlink

### 2. Dynamic JavaScript Loader (`docs/assets/js/downloads.js`)

Client-side JavaScript that fetches and renders PDF data:

**Features:**
- Fetches `/downloads/index.json` from Pages
- Renders latest download badge dynamically
- Builds PDF table with:
  - Filename (clickable link)
  - File size (human-readable MB)
  - Upload timestamp (localized)
  - MD5 hash (first 8 chars)
- No server required (pure client-side)
- Auto-refresh on page load

**Usage in HTML:**
```html
<!-- Mount points -->
<div id="latest-badge"></div>
<div id="recent-pdfs-table"></div>

<!-- Load script -->
<script src="/assets/js/downloads.js"></script>
```

### 3. README Badge Auto-Update (`.github/workflows/readme-badge.yml`)

Workflow that keeps README badge fresh:

**Triggers:**
- Weekly (Monday 12:00 UTC)
- Push to `downloads/`
- Manual workflow dispatch

**What it does:**
1. Reads `downloads/index.json`
2. Extracts latest filename
3. Updates `<!--BEGIN:PAGES_BADGES-->` markers in README
4. Commits with `[skip ci]` flag

**Example update:**
```markdown
<!--BEGIN:PAGES_BADGES-->
[![Latest Download](https://img.shields.io/badge/latest-download-blue?logo=adobeacrobatreader&logoColor=white)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
<!--END:PAGES_BADGES-->
```

### 4. Enhanced Deployment Workflow

Updated `pages.yml` now includes:

```yaml
- name: Build downloads index.json
  run: |
    cd public && python ../scripts/pages/make_downloads_json.py

- name: Generate dynamic content in index.html
  run: |
    cd public && python ../scripts/pages/build_pages_index.py
```

**Deployment flow:**
1. Copy `dist/` → `public/downloads/`
2. Create `latest.pdf` (newest)
3. **Generate `index.json`** (NEW)
4. Inject HTML content
5. Deploy to Pages

### 5. Smart Makefile Target

Enhanced `make pages` command:

```makefile
pages:
	@echo "📄 Deploying to GitHub Pages..."
	@git add -A 2>/dev/null || true
	@git diff-index --quiet HEAD || git commit -m "ci(pages): publish site w/ dynamic downloads & badges" || true
	@git push || true
	@gh workflow run pages.yml -R m9dswyptrn-web/SonicBuilder
	@echo "✅ Triggered Pages deployment. Watch: https://github.com/m9dswyptrn-web/SonicBuilder/actions"
```

**Features:**
- Auto-commits uncommitted changes
- Pushes to origin
- Triggers workflow
- Shows Actions URL

---

## Deployment

### Quick Deploy:
```bash
make pages
```

### Manual Deploy:
```bash
# Commit changes
git add -A
git commit -m "ci: update Pages"
git push

# Trigger workflow
gh workflow run pages.yml
```

### Local Testing:
```bash
# Test JSON generation
cd dist
python ../scripts/pages/make_downloads_json.py

# View generated JSON
cat downloads/index.json | jq
```

---

## Published URLs

After deployment:

**Main Site:**
```
https://m9dswyptrn-web.github.io/SonicBuilder/
```

**JSON Index:**
```
https://m9dswyptrn-web.github.io/SonicBuilder/downloads/index.json
```

**Latest PDF:**
```
https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf
```

**Specific PDF:**
```
https://m9dswyptrn-web.github.io/SonicBuilder/downloads/<filename>.pdf
```

---

## HTML Integration

### Option 1: Mount Points (Recommended)

Add mount points to your `docs/index.html`:

```html
<!doctype html>
<html>
<head>
  <title>SonicBuilder Docs</title>
  <style>
    /* Your custom styles */
  </style>
</head>
<body>
  <h1>SonicBuilder Documentation</h1>
  
  <!-- Latest badge mounts here -->
  <div id="latest-badge" style="margin:10px 0"></div>
  
  <p>Your custom content...</p>
  
  <!-- Recent PDFs table mounts here -->
  <div id="recent-pdfs-table" style="margin:10px 0"></div>
  
  <!-- Load renderer -->
  <script src="/assets/js/downloads.js"></script>
</body>
</html>
```

### Option 2: Static Markers

Use the Python script markers for static generation:

```html
<!--BEGIN:LATEST_BADGE-->
  <!-- Auto-injected by build_pages_index.py -->
<!--END:LATEST_BADGE-->

<!--BEGIN:RECENT_PDFS-->
  <!-- Auto-injected by build_pages_index.py -->
<!--END:RECENT_PDFS-->
```

---

## Benefits

### 1. Client-Side Rendering
- No server processing needed
- Fast page loads
- Works with static hosts

### 2. Metadata Rich
- MD5 hashes for verification
- Precise timestamps
- Accurate file sizes

### 3. Auto-Updates
- README badge stays fresh
- JSON rebuilds on every deploy
- No manual intervention

### 4. Flexible Integration
- Use JavaScript (dynamic)
- Use Python script (static)
- Mix both approaches

---

## Customization

### Change Number of PDFs:

**In Python script:**
```python
# scripts/pages/build_pages_index.py
items = list_pdfs(10)  # Show 10 instead of 5
```

**In JavaScript:**
```javascript
// docs/assets/js/downloads.js
const rows = data.items.slice(0, 20)  // Show 20 instead of 10
```

### Add More Metadata:

Edit `make_downloads_json.py`:
```python
items.append({
    "name": p.name,
    "href": f"/SonicBuilder/downloads/{p.name}",
    "bytes": st.st_size,
    "mb": round(st.st_size/1024/1024, 2),
    "mtime": int(st.st_mtime),
    "mtime_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
    "md5": md5(p),
    # Add custom fields:
    "version": extract_version(p.name),
    "theme": "dark" if "dark" in p.name else "light",
})
```

### Custom Badge Style:

Edit `readme-badge.yml`:
```yaml
BADGE_URL="https://img.shields.io/badge/latest-download-blue?style=flat-square&logo=adobeacrobatreader"
```

---

## Troubleshooting

### Issue: index.json not found

**Cause:** Script didn't run or failed

**Solution:**
```bash
# Check workflow logs
gh run list --workflow=pages.yml --limit 3

# Test locally
cd public && python ../scripts/pages/make_downloads_json.py
```

### Issue: JavaScript not loading data

**Cause:** CORS or wrong URL

**Solution:**
Check browser console:
```javascript
// Should see fetch request to:
// https://m9dswyptrn-web.github.io/SonicBuilder/downloads/index.json
```

### Issue: README badge not updating

**Cause:** Workflow not triggered or markers missing

**Solution:**
```bash
# Check markers exist
grep "BEGIN:PAGES_BADGES" README.md

# Trigger manually
gh workflow run readme-badge.yml
```

---

## File Structure

```
SonicBuilder/
├── .github/workflows/
│   ├── pages.yml           # Main deployment (enhanced)
│   └── readme-badge.yml    # Badge auto-update (NEW)
├── scripts/pages/
│   ├── build_pages_index.py       # HTML injection
│   └── make_downloads_json.py     # JSON generation (NEW)
├── docs/
│   ├── index.html          # Your front page
│   └── assets/js/
│       └── downloads.js    # Dynamic loader (NEW)
└── README.md               # With <!--BEGIN:PAGES_BADGES--> markers
```

---

## Summary

**Complete Pages Integration:**
1. ✅ JSON metadata index with MD5 hashes
2. ✅ Dynamic JavaScript rendering
3. ✅ Auto-updating README badge
4. ✅ Enhanced deployment workflow
5. ✅ Smart Makefile target
6. ✅ Client-side + server-side options

**Deploy with one command:**
```bash
make pages
```

**Your Pages site will have:**
- Complete PDF metadata (JSON API)
- Dynamic badge & table rendering
- Auto-updating README
- MD5 verification hashes
- Professional presentation

---

**Your GitHub Pages is now fully enterprise-grade! 🚀**
