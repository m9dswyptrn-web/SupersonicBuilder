# 🚀 SonicBuilder Quick Start

**Essential commands for daily use**

---

## 📸 Gallery

```bash
# Add images
mkdir -p docs/images/mobo_back/$(date +%Y-%m-%d)
cp *.jpg docs/images/mobo_back/$(date +%Y-%m-%d)/

# Generate gallery
make web-gallery
```

**URL:** https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html

---

## 📄 PDF Building

```bash
# Preview (fast - 6 pages)
make build_dark_preview

# Full build
make build_dark
make build_light
```

---

## 🧪 Testing

```bash
# After deployment
make smoke
make coverage-badge
make pages-smoke-badge

# View results
cat smoke_diagnostics.json
cat docs/status/*.json
```

---

## 🚀 Deployment

```bash
# Update badges & deploy
make badges
make ship
```

---

## 📦 Release

```bash
# Version bump
echo "v2.3.0" > VERSION

# Build, badge, deploy
make build_dark
make build_light
make badges
make package_deploykit
make ship
```

---

## 📚 Documentation

- **COMPLETE_INFRASTRUCTURE_GUIDE.md** - Full system guide
- **DEPLOYMENT_KIT_GUIDE.md** - Advanced features
- **BADGES_FOR_README.md** - Badge URLs
- **MOBO_GALLERY_GUIDE.md** - Gallery guide

---

**Full guide:** COMPLETE_INFRASTRUCTURE_GUIDE.md
