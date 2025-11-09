# GitHub Pages Dynamic Content Integration

## Overview

The GitHub Pages workflow now automatically injects dynamic content into `index.html`:

1. **Latest Download Badge** - Always points to newest PDF
2. **Recent PDFs List** - Last 5 PDFs with size and timestamp
3. **Footer Stamp** - Version, commit, build time, and latest.pdf link

## How It Works

### Workflow: `.github/workflows/pages.yml`

**Triggers:**
- Push to `main` (when `dist/`, `docs/`, workflows, or scripts change)
- Release published
- Manual workflow dispatch

**Steps:**
1. Copies `docs/` → `public/` (preserves your custom front page)
2. Copies `dist/*.pdf` → `public/downloads/`
3. Creates `latest.pdf` (copy of newest PDF)
4. Runs Python script to inject dynamic content
5. Deploys to GitHub Pages

### Script: `scripts/pages/build_pages_index.py`

**What it does:**
- Finds `index.html` in `public/` (creates minimal one if missing)
- Scans `downloads/` for PDFs
- Injects content between HTML markers:
  - `<!--BEGIN:LATEST_BADGE-->...<!--END:LATEST_BADGE-->`
  - `<!--BEGIN:RECENT_PDFS-->...<!--END:RECENT_PDFS-->`
  - `<!--BEGIN:FOOTER_STAMP-->...<!--END:FOOTER_STAMP-->`

## Content Injected

### 1. Latest Badge

```html
<!--BEGIN:LATEST_BADGE-->
<div class="badge">
<a href='./downloads/latest.pdf'>
<img alt='Latest Download' src='https://img.shields.io/badge/download-latest.pdf-2b6fff?style=for-the-badge&logo=adobeacrobatreader&logoColor=white'>
</a>
</div>
<!--END:LATEST_BADGE-->
```

### 2. Recent PDFs List

```html
<!--BEGIN:RECENT_PDFS-->
<section id='recent-pdfs'>
<h2>📄 Recent PDFs</h2>
<ul>
<li><a href='./downloads/file1.pdf'>file1.pdf</a> <span>— 2.5 MB — 2025-10-30 14:05 UTC</span></li>
<li><a href='./downloads/file2.pdf'>file2.pdf</a> <span>— 2.3 MB — 2025-10-30 12:30 UTC</span></li>
...
</ul>
</section>
<!--END:RECENT_PDFS-->
```

### 3. Footer Stamp

```html
<!--BEGIN:FOOTER_STAMP-->
<footer>
<p><small>Version: <strong>v2.0.9</strong> • Commit: <code>abc1234</code> • Built: 2025-10-30 14:05 UTC • <a href='./downloads/latest.pdf'>latest.pdf</a></small></p>
</footer>
<!--END:FOOTER_STAMP-->
```

## Using With Custom index.html

### Option 1: Let Script Create Minimal Index

If `docs/index.html` doesn't exist, the script creates a dark-themed minimal page with all markers.

### Option 2: Add Markers to Existing Index

Add these markers anywhere in your existing `docs/index.html`:

```html
<!doctype html>
<html>
<head>
  <title>Your Custom Title</title>
  <!-- your styles -->
</head>
<body>
  <h1>Your Custom Header</h1>
  
  <!-- Latest badge will be injected here -->
  <!--BEGIN:LATEST_BADGE--><!--END:LATEST_BADGE-->
  
  <p>Your custom content...</p>
  
  <!-- Recent PDFs list will be injected here -->
  <!--BEGIN:RECENT_PDFS--><!--END:RECENT_PDFS-->
  
  <!-- Footer will be injected here -->
  <!--BEGIN:FOOTER_STAMP--><!--END:FOOTER_STAMP-->
</body>
</html>
```

The script will populate content between the markers on every deployment.

## Customization

### Change Number of Recent PDFs

Edit `scripts/pages/build_pages_index.py`:

```python
items = list_pdfs(5)  # Change 5 to any number
```

### Change Badge Style

Edit the badge URL in the script:

```python
# Current: for-the-badge (large)
style=for-the-badge

# Other options:
style=flat-square    # Compact squares
style=flat           # Standard flat
style=plastic        # Glossy
```

### Customize Styling

The minimal index includes basic dark theme styling. To customize:

1. Copy `docs/index.html` from first deployment
2. Add your custom CSS
3. Keep the marker comments
4. Push changes

## Testing Locally

```bash
# Simulate the workflow locally
mkdir -p public/downloads
cp dist/*.pdf public/downloads/
cp -f "$(ls -1t public/downloads/*.pdf | head -n1)" public/downloads/latest.pdf
cd public && python ../scripts/pages/build_pages_index.py
# View public/index.html
```

## Deployment

### Manual Trigger:
```bash
make pages
# Or: gh workflow run pages.yml
```

### Automatic Trigger:
```bash
# Update PDFs
make build_dark
make release_local

# Commit and push
git add dist/*.pdf
git commit -m "docs: update PDFs"
git push  # Workflow auto-triggers
```

## Published URLs

After deployment:

- **Website:** https://m9dswyptrn-web.github.io/SonicBuilder/
- **Latest PDF:** https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf
- **Specific PDF:** https://m9dswyptrn-web.github.io/SonicBuilder/downloads/<filename>.pdf

## Troubleshooting

### Issue: Markers not replaced

**Cause:** Markers missing or malformed in index.html

**Solution:** Ensure exact marker format:
```html
<!--BEGIN:MARKER_NAME--><!--END:MARKER_NAME-->
```

### Issue: PDFs not showing

**Cause:** No PDFs in `dist/` when workflow runs

**Solution:** Build PDFs first, commit to `dist/`, then push

### Issue: Version shows "dev"

**Cause:** Not running from release or tagged commit

**Solution:** Create release or tag to get proper version number

---

**Your Pages site now has dynamic, auto-updating content! 🚀**
