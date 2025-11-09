# "Latest Size" Badge Integration

## Overview

The "latest size" badge displays the file size of the most recent PDF in megabytes, making it easy for users to see the download size at a glance.

## Features

### 1. **Automatic Size Display**

Shows the size of the latest PDF:
- **"12.5 MB"** - Actual file size in megabytes
- **"n/a"** - No PDFs available

### 2. **Color Coding**

- **🔵 Blue** - Valid size available
- **⚪ Light Grey** - No PDFs (n/a)

### 3. **Dual Badge Options**

**Live Badge (Replit Server):**
```markdown
[![Latest size](https://img.shields.io/endpoint?url=YOUR_REPL_URL/badge/size.json)](YOUR_REPL_URL/downloads/latest.pdf)
```

**Static Badge (GitHub Pages):**
```markdown
[![Latest size](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/size.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
```

---

## Implementation Details

### Flask Endpoint: `/badge/size.json`

```python
@app.route("/badge/size.json")
def badge_size():
    idx = get_index()
    latest = (idx.get("items") or [{}])[0]
    mb = latest.get("mb", 0.0)
    msg = f"{mb:.1f} MB" if mb else "n/a"
    color = "blue" if mb else "lightgrey"
    payload = {
        "schemaVersion": 1,
        "label": "latest size",
        "message": msg,
        "color": color
    }
    return Response(json.dumps(payload), mimetype="application/json")
```

### Size Calculation

The size is calculated when the `index.json` is generated:

```python
# In make_downloads_json.py or similar
mb = bytes / (1024 * 1024)
item = {
    "name": filename,
    "bytes": bytes,
    "mb": round(mb, 1),  # Rounded to 1 decimal place
    # ... other fields
}
```

### Workflow Integration

The `.github/workflows/badge-update.yml` workflow generates `size.json`:

```python
# latest size badge
mb = latest.get("mb", 0.0)
size_msg = f"{mb:.1f} MB" if mb else "n/a"
size_color = "blue" if mb else "lightgrey"
(docs/"size.json").write_text(json.dumps({
    "schemaVersion": 1,
    "label": "latest size",
    "message": size_msg,
    "color": size_color
}), "utf-8")
```

---

## Complete Badge Set

Use all four badges together for comprehensive status:

```markdown
<!-- Badges: latest name • last updated • latest size • downloads -->
[![Latest PDF](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/latest.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
[![Last updated](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/updated.json)](https://m9dswyptrn-web.github.io/SonicBuilder/)
[![Latest size](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/size.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
[![Downloads](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/downloads.json)](https://m9dswyptrn-web.github.io/SonicBuilder/)
```

**Result shows:**
- 📄 Latest PDF filename
- ⏰ When last updated
- 📏 File size
- ⬇️ Total downloads

---

## Badge Examples

### With Valid PDF

```json
{
  "schemaVersion": 1,
  "label": "latest size",
  "message": "12.5 MB",
  "color": "blue"
}
```
![12.5 MB](https://img.shields.io/badge/latest%20size-12.5%20MB-blue)

### No PDFs Available

```json
{
  "schemaVersion": 1,
  "label": "latest size",
  "message": "n/a",
  "color": "lightgrey"
}
```
![n/a](https://img.shields.io/badge/latest%20size-n%2Fa-lightgrey)

---

## API Response Format

### Endpoint: `/badge/size.json`

**Method:** GET

**Response:**
```json
{
  "schemaVersion": 1,
  "label": "latest size",
  "message": "12.5 MB",
  "color": "blue"
}
```

**Fields:**
- `schemaVersion` (number): Always 1 (Shields.io standard)
- `label` (string): Badge label ("latest size")
- `message` (string): File size or "n/a"
- `color` (string): "blue" or "lightgrey"

---

## Testing

### Test Live Endpoint:
```bash
curl http://localhost:5000/badge/size.json
```

**Expected output (with PDFs):**
```json
{
  "schemaVersion": 1,
  "label": "latest size",
  "message": "12.5 MB",
  "color": "blue"
}
```

**Expected output (no PDFs):**
```json
{
  "schemaVersion": 1,
  "label": "latest size",
  "message": "n/a",
  "color": "lightgrey"
}
```

### Test with Different Sizes:

```bash
# Create test PDFs of different sizes
dd if=/dev/zero of=downloads/small.pdf bs=1M count=5
dd if=/dev/zero of=downloads/large.pdf bs=1M count=50

# Regenerate index
python scripts/pages/make_downloads_json.py

# Check badges
curl http://localhost:5000/badge/size.json
# Should show size of latest PDF
```

---

## Workflow Behavior

The `badge-update.yml` workflow:
1. **Runs every 30 minutes** (or on push to `downloads/*.json`)
2. Reads `downloads/index.json`
3. Extracts latest PDF's `mb` field
4. Formats as "X.X MB" or "n/a"
5. Sets color to blue/lightgrey
6. Writes `docs/badges/size.json`
7. Commits and pushes

**Result:** Static badge updates automatically every 30 minutes on GitHub Pages.

---

## Use Cases

### 1. **Download Size Preview**
```markdown
# Installation Manual

[![Latest size](https://img.shields.io/endpoint?url=...)](...)

Users see file size before downloading.
```

### 2. **Bandwidth Awareness**
Show users the download size for planning on limited connections.

### 3. **Documentation Tracking**
Monitor how documentation size changes over time.

### 4. **Multi-Format Comparison**
```markdown
[![PDF size](https://img.shields.io/endpoint?url=.../size.json)](...)
[![HTML version](https://img.shields.io/badge/html-2.1%20MB-green)](...)
```

---

## Customization

### Change Size Format

Edit the badge endpoint:
```python
# Use different units
if mb < 1:
    msg = f"{mb * 1024:.0f} KB"
else:
    msg = f"{mb:.1f} MB"

# Or use binary units (MiB)
mib = bytes / (1024 * 1024)
msg = f"{mib:.1f} MiB"
```

### Change Precision

```python
# More decimal places
msg = f"{mb:.2f} MB"  # 12.45 MB

# No decimal places
msg = f"{int(mb)} MB"  # 12 MB
```

### Change Color Scheme

```python
# Color by size (green for small, orange for large)
if mb < 10:
    color = "brightgreen"
elif mb < 50:
    color = "yellow"
else:
    color = "orange"
```

### Custom Labels

```python
payload = {
    "label": "file size",     # Custom label
    "label": "download",      # Another option
    "label": "PDF size",      # Another option
    "message": msg,
    "color": color
}
```

---

## Troubleshooting

### Issue: Badge always shows "n/a"

**Cause:** No PDFs in `downloads/` or `index.json` missing `mb` field

**Solution:**
```bash
# Check index.json
cat downloads/index.json | grep mb

# Regenerate index with MB calculation
python scripts/pages/make_downloads_json.py

# Verify
cat downloads/index.json | grep -A5 '"mb"'
```

### Issue: Size is 0.0 MB

**Cause:** Empty file or calculation error

**Solution:**
```bash
# Check actual file size
ls -lh downloads/*.pdf

# Verify bytes field
cat downloads/index.json | grep bytes

# Recalculate
python scripts/pages/make_downloads_json.py
```

### Issue: Badge shows old size

**Cause:** Cache or workflow hasn't run

**Solution:**
```bash
# Force workflow run
gh workflow run badge-update.yml

# Or manually regenerate
python scripts/pages/make_downloads_json.py
cd .github/workflows
# Run Python script from badge-update.yml manually
```

---

## Integration with Analytics

### Track Size Over Time

Combined with download stats:
```python
@app.route("/api/size_history.json")
def size_history():
    idx = get_index()
    history = []
    for item in idx.get("items", [])[:10]:  # Last 10
        history.append({
            "name": item.get("name"),
            "mb": item.get("mb"),
            "mtime": item.get("mtime")
        })
    return Response(json.dumps(history), mimetype="application/json")
```

### Dashboard Display

Show size alongside downloads:
```javascript
const summary = await fetch('/api/summary.json').then(r => r.json());
console.log(`Latest: ${summary.latest_name} (${summary.latest_mb} MB)`);
```

---

## Complete Badge System Summary

**All Four Badges:**

| Badge | Shows | Color Logic |
|-------|-------|-------------|
| **Latest** | Filename | Blue (active) / Grey (none) |
| **Updated** | Time ago | Green→Yellow→Orange→Grey |
| **Size** | File size | Blue (active) / Grey (none) |
| **Downloads** | Count | Green (active) / Grey (0) |

**Integration:**
- ✅ Flask endpoints (live)
- ✅ GitHub Pages (static)
- ✅ Auto-updating workflow (30 min)
- ✅ Shields.io compatible
- ✅ Complete documentation

---

## Real-World Examples

### Minimal (Single Badge)
```markdown
[![Latest (12.5 MB)](https://img.shields.io/endpoint?url=...)](...)
```

### Standard (All Four Badges)
```markdown
[![Latest](https://img.shields.io/endpoint?url=.../latest.json)](...)
[![Updated](https://img.shields.io/endpoint?url=.../updated.json)](...)
[![Size](https://img.shields.io/endpoint?url=.../size.json)](...)
[![Downloads](https://img.shields.io/endpoint?url=.../downloads.json)](...)
```

### With Status (Including Build Status)
```markdown
[![Build](https://img.shields.io/github/actions/workflow/status/USER/REPO/build.yml)](...)
[![Latest](https://img.shields.io/endpoint?url=.../latest.json)](...)
[![Size](https://img.shields.io/endpoint?url=.../size.json)](...)
[![Downloads](https://img.shields.io/endpoint?url=.../downloads.json)](...)
```

---

## API Reference

### New Endpoint

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/badge/size.json` | GET | Latest size badge | Shields.io JSON |

### All Badge Endpoints

1. `/badge/latest.json` - Latest filename
2. `/badge/downloads.json` - Total downloads
3. `/badge/updated.json` - Last updated time
4. `/badge/size.json` - Latest file size (NEW)

---

## GitHub Pages Deployment

When you run `make pages` or the Pages workflow, all four badge JSONs are generated:

```
docs/badges/
├── latest.json      # Latest filename
├── downloads.json   # Total downloads
├── updated.json     # Last updated
└── size.json        # Latest size (NEW)
```

All badges update together every 30 minutes via the `badge-update.yml` workflow.

---

**Your complete badge system now includes file size information! 🎉**
