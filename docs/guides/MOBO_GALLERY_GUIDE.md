# 📸 SonicBuilder Motherboard Gallery Guide

**Your Gallery URL:**
```
https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html
```

---

## ✅ What's Installed

### Files
- **scripts/mobo_gallery_build_web.py** - Gallery generator script
- **docs/styles/gallery_dark.css** - Dark theme styles  
- **docs/web_gallery/lightbox.css** - Lightbox styles
- **docs/web_gallery/lightbox.js** - Lightbox JavaScript
- **docs/images/mobo_back/gallery.html** - Generated gallery page

### Makefile Target
```makefile
web-gallery:
    @python3 scripts/mobo_gallery_build_web.py
    @echo "✅ Web gallery rendered at docs/images/mobo_back/gallery.html"
```

---

## 🚀 Usage

### Step 1: Add Images

Organize your motherboard images by date:

```bash
docs/images/mobo_back/
├── 2025-10-01/
│   ├── mobo_back_angle1.jpg
│   ├── mobo_back_angle2.jpg
│   └── mobo_back_ports.jpg
├── 2025-10-15/
│   ├── mobo_back_overview.jpg
│   └── mobo_back_detail.jpg
└── gallery.html (auto-generated)
```

**Supported formats:** `.jpg`, `.jpeg`, `.png`, `.webp`

---

### Step 2: Generate Gallery

```bash
make web-gallery
```

**Output:**
```
✅ Web gallery rendered at docs/images/mobo_back/gallery.html
```

---

### Step 3: Deploy to GitHub Pages

```bash
# Commit changes
git add docs/
git commit -m "docs: add motherboard gallery images"

# Deploy
make ship
```

Or manually:
```bash
git push
```

---

### Step 4: Enable GitHub Pages

1. Go to **GitHub Repository Settings**
2. Click **Pages** (left sidebar)
3. **Source:** Select `main` branch
4. **Folder:** Select `/ (root)`
5. **Save**

GitHub Pages will be available at:
```
https://m9dswyptrn-web.github.io/SonicBuilder/
```

---

## 🎨 Gallery Features

### Dark Theme
- Professional dark background
- High contrast for image viewing
- Responsive grid layout

### Lightbox
- Click any image to view fullscreen
- Navigate with arrow keys
- Close with ESC or ✕ button
- Image captions from filenames

### Auto-Grouping
Images are automatically grouped by their subdirectory (date):

```
Motherboard Backside Gallery
  
📅 2025-10-01
[img] [img] [img]

📅 2025-10-15  
[img] [img]
```

---

## 📱 Responsive Design

The gallery adapts to all screen sizes:
- **Desktop:** 4 columns grid
- **Tablet:** 2-3 columns
- **Mobile:** 1-2 columns

---

## 🔧 Optional: Thumbnails

For faster loading, generate thumbnails:

```bash
# Create thumbnails directory
mkdir -p docs/images/mobo_back/.thumbs

# Use ImageMagick to create thumbnails
for img in docs/images/mobo_back/*/*.jpg; do
  thumb="docs/images/mobo_back/.thumbs/$(basename "$img")"
  convert "$img" -resize 400x400 "$thumb"
done

# Regenerate gallery
make web-gallery
```

The script will automatically use thumbnails if `.thumbs/` directory exists.

---

## 📊 Example Gallery Structure

```html
<!doctype html>
<html lang="en">
<head>
  <title>Mobo Backside Gallery</title>
  <link rel="stylesheet" href="/styles/gallery_dark.css"/>
  <link rel="stylesheet" href="/web_gallery/lightbox.css"/>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="title">Motherboard Backside Gallery</div>
      <div>
        <span class="badge">Dark</span>
        <span class="badge">2025-10-29 23:22 UTC</span>
      </div>
    </div>
    
    <!-- Images grouped by date -->
    <div class="group">
      <h2>2025-10-01</h2>
      <div class="grid">
        <a class="card" href="/images/mobo_back/2025-10-01/image1.jpg">
          <img src="/images/mobo_back/2025-10-01/image1.jpg"/>
          <div class="meta">Image 1</div>
        </a>
        <!-- More images... -->
      </div>
    </div>
    
    <div class="footer">
      Generated automatically by SonicBuilder
    </div>
  </div>
  
  <!-- Lightbox overlay -->
  <div class="lightbox-backdrop">
    <div class="lightbox-close">✕</div>
    <div class="lightbox-stage"></div>
    <div class="lightbox-caption"></div>
  </div>
  
  <script src="/web_gallery/lightbox.js"></script>
</body>
</html>
```

---

## 🎯 Integration with Build System

### Auto-build with docs

Add to your Makefile:

```makefile
docs: web-gallery build_dark
    @echo "📚 Building docs with gallery..."
    @$(MAKE) deploy verify notify
```

Now `make docs` will automatically rebuild the gallery.

---

## ✨ Customization

### Change Gallery Title

Edit `scripts/mobo_gallery_build_web.py`:

```python
<div class="title">Motherboard Backside Gallery</div>
```

### Add Custom Styles

Edit `docs/styles/gallery_dark.css` to customize colors, spacing, etc.

### Modify Lightbox Behavior

Edit `docs/web_gallery/lightbox.js` for custom interactions.

---

## 🔍 Troubleshooting

### Gallery is empty

**Check:**
1. Images exist in `docs/images/mobo_back/<date>/`
2. Images have valid extensions (`.jpg`, `.png`, `.webp`)
3. No `.thumbs` in image paths

**Fix:**
```bash
ls docs/images/mobo_back/*/
make web-gallery
```

### CSS/JS not loading

**Check paths in `gallery.html`:**
```html
<link rel="stylesheet" href="/styles/gallery_dark.css"/>
<link rel="stylesheet" href="/web_gallery/lightbox.css"/>
<script src="/web_gallery/lightbox.js"></script>
```

For local testing, use relative paths:
```html
<link rel="stylesheet" href="../../styles/gallery_dark.css"/>
```

### Lightbox not working

**Check browser console:**
1. Open DevTools (F12)
2. Look for JavaScript errors
3. Verify `lightbox.js` loaded

### Images don't group by date

**Directory structure must be:**
```
docs/images/mobo_back/
  YYYY-MM-DD/
    image1.jpg
    image2.jpg
```

---

## 📚 Quick Reference

```bash
# Generate gallery
make web-gallery

# Test locally (if you have Python SimpleHTTPServer)
cd docs && python3 -m http.server 8000
# Open: http://localhost:8000/images/mobo_back/gallery.html

# Deploy to GitHub Pages
make ship
```

---

## 🎉 You're All Set!

Your motherboard gallery will be live at:
```
https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html
```

Just add images and run `make web-gallery` to rebuild!

---

**Generated:** October 29, 2025  
**Version:** SonicBuilder MoboGallery v1  
**Status:** ✅ Production Ready
