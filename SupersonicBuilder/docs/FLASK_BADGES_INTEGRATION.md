# Flask Badge Endpoints & Download Analytics

## Overview

Enhanced Flask server (`serve_pdfs.py`) with download statistics tracking, Shields.io-compatible badge endpoints, and live analytics dashboard.

## Features

### 1. **Download Statistics Tracking**

Automatically tracks every PDF download:

```json
// downloads/stats.json
{
  "updated": 1730291040,
  "counts": {
    "supersonic_manual_dark.pdf": 42,
    "supersonic_manual_light.pdf": 38,
    "latest.pdf": 125
  },
  "last_download": {
    "supersonic_manual_dark.pdf": 1730291040,
    "supersonic_manual_light.pdf": 1730290580
  }
}
```

**Features:**
- Increments counter on every download
- Tracks last download timestamp per file
- Persists to JSON atomically (no data loss)
- Thread-safe with temp file + replace pattern

### 2. **Shields.io Badge Endpoints**

#### `/badge/latest.json` - Latest PDF Badge

Returns current latest PDF name in Shields.io format:

```json
{
  "schemaVersion": 1,
  "label": "latest",
  "message": "supersonic_manual_dark.pdf",
  "color": "blue"
}
```

**Usage:**
```markdown
[![Latest PDF](https://img.shields.io/endpoint?url=YOUR_REPL_URL/badge/latest.json)](YOUR_REPL_URL/downloads/latest.pdf)
```

#### `/badge/downloads.json` - Total Downloads Badge

Returns total download count:

```json
{
  "schemaVersion": 1,
  "label": "downloads",
  "message": "205",
  "color": "success"
}
```

**Usage:**
```markdown
[![Downloads](https://img.shields.io/endpoint?url=YOUR_REPL_URL/badge/downloads.json)](YOUR_REPL_URL/)
```

### 3. **Enhanced Web UI**

Professional dashboard with:
- **Theme toggle** (dark/light with system preference)
- **Total downloads counter** (live updating)
- **Per-file download counts**
- **Auto-refresh** (60 seconds)
- **MD5 hashes** (first 8 chars)
- **Responsive layout**

**UI Elements:**
```html
<!-- Total downloads display -->
<span id="totalBox">
  ⬇️ total downloads: <strong id="totalCnt">205</strong>
</span>

<!-- Per-file counts in table -->
<td>42</td>  <!-- Download count column -->
```

### 4. **JSON API Endpoints**

#### `/api/index.json` - PDF Metadata
```json
{
  "generated": 1730291040,
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

#### `/api/stats.json` - Download Statistics
```json
{
  "updated": 1730291040,
  "counts": {
    "supersonic_manual_dark.pdf": 42
  },
  "last_download": {
    "supersonic_manual_dark.pdf": 1730291040
  }
}
```

#### `/api/summary.json` - Combined Summary
```json
{
  "generated": 1730291040,
  "latest_name": "supersonic_manual_dark.pdf",
  "latest_bytes": 68157440,
  "latest_mtime": 1730291040,
  "total_downloads": 205,
  "counts": {
    "supersonic_manual_dark.pdf": 42,
    "latest.pdf": 125
  }
}
```

---

## Badge Update Workflow

**Workflow:** `.github/workflows/badge-update.yml`

Generates static badge JSON files for GitHub Pages hosting.

**Triggers:**
- Every 30 minutes (cron)
- Push to `downloads/index.json` or `downloads/stats.json`
- Manual workflow dispatch

**What it does:**
1. Reads `downloads/stats.json` and `downloads/index.json`
2. Generates static badge JSON files:
   - `docs/badges/downloads.json`
   - `docs/badges/latest.json`
3. Commits and pushes changes

**Output files:**
```
docs/badges/
├── downloads.json   # Total downloads badge
└── latest.json      # Latest PDF badge
```

**Usage (static badges on Pages):**
```markdown
[![Downloads](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/downloads.json)](https://m9dswyptrn-web.github.io/SonicBuilder/)
```

---

## Badge Deployment Options

### Option 1: Live Badges (Replit Server)

Use your Replit app URL for real-time badges:

```markdown
<!-- Always shows current stats -->
[![Latest](https://img.shields.io/endpoint?url=https://YOUR_REPL_URL/badge/latest.json)](https://YOUR_REPL_URL/downloads/latest.pdf)
[![Downloads](https://img.shields.io/endpoint?url=https://YOUR_REPL_URL/badge/downloads.json)](https://YOUR_REPL_URL/)
```

**Pros:**
- Real-time updates
- No delay
- Direct from source

**Cons:**
- Requires Replit server running
- Uses Replit bandwidth

### Option 2: Static Badges (GitHub Pages)

Use GitHub Pages URLs after workflow runs:

```markdown
<!-- Updates every 30 minutes -->
[![Latest](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/latest.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
[![Downloads](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/downloads.json)](https://m9dswyptrn-web.github.io/SonicBuilder/)
```

**Pros:**
- No Replit server required
- GitHub CDN (fast worldwide)
- Free hosting

**Cons:**
- 30-minute update delay
- Depends on workflow running

### Option 3: Hybrid (Recommended)

Use live badges in README, static badges in docs:

**README.md** (live):
```markdown
[![Latest](https://img.shields.io/endpoint?url=https://YOUR_REPL_URL/badge/latest.json)](...)
```

**GitHub Pages site** (static):
```markdown
[![Latest](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/latest.json)](...)
```

---

## Server Architecture

### Download Flow:
```
User clicks PDF link
  ↓
GET /downloads/supersonic_manual_dark.pdf
  ↓
bump_stat("supersonic_manual_dark.pdf")
  ↓
Increment counter in stats.json
  ↓
Save atomically (tmp file + replace)
  ↓
Serve file with send_from_directory()
```

### Badge Request Flow:
```
Shields.io requests badge
  ↓
GET /badge/downloads.json
  ↓
Load stats.json
  ↓
Calculate total downloads
  ↓
Return Shields.io JSON format
  ↓
Shields.io renders badge image
```

### Auto-Refresh Flow:
```
Browser loads page
  ↓
JavaScript fetches /api/index.json + /api/stats.json
  ↓
Renders table with data
  ↓
Calculates total downloads
  ↓
Updates UI elements
  ↓
Wait 60 seconds
  ↓
Repeat
```

---

## File Structure

```
SonicBuilder/
├── serve_pdfs.py           # Enhanced Flask server (UPDATED)
├── downloads/
│   ├── index.json          # PDF metadata (generated)
│   ├── stats.json          # Download statistics (auto-updated)
│   ├── latest.pdf          # Newest PDF (copy/symlink)
│   └── *.pdf               # Your PDFs
├── docs/badges/
│   ├── downloads.json      # Static badge (workflow-generated)
│   └── latest.json         # Static badge (workflow-generated)
└── .github/workflows/
    └── badge-update.yml    # Badge workflow (NEW)
```

---

## Usage Examples

### Start Server:
```bash
python3 serve_pdfs.py
# Server starts on http://0.0.0.0:5000
```

### View Dashboard:
```
http://localhost:5000/
```

### Test Badge Endpoints:
```bash
curl http://localhost:5000/badge/latest.json
curl http://localhost:5000/badge/downloads.json
curl http://localhost:5000/api/summary.json
```

### Check Statistics:
```bash
cat downloads/stats.json | jq
```

### Trigger Badge Update:
```bash
gh workflow run badge-update.yml
```

---

## Customization

### Change Auto-Refresh Interval:

Edit `serve_pdfs.py` HTML:
```javascript
setInterval(load, 120000); // 2 minutes instead of 60s
```

### Adjust Badge Update Frequency:

Edit `.github/workflows/badge-update.yml`:
```yaml
schedule:
  - cron: "*/15 * * * *"  # Every 15 minutes instead of 30
```

### Change Badge Colors:

Edit badge endpoint functions:
```python
@app.route("/badge/downloads.json")
def badge_downloads():
    # ...
    payload = {
        "color": "brightgreen"  # or: blue, green, yellow, red, orange
    }
```

### Add More Statistics:

Extend `bump_stat()`:
```python
def bump_stat(filename):
    s = get_stats()
    s["counts"][filename] = int(s["counts"].get(filename, 0)) + 1
    s["last_download"][filename] = time.time()
    # Add custom stats:
    s["daily_downloads"] = s.get("daily_downloads", 0) + 1
    s["updated"] = time.time()
    _save_json(STATS_JSON, s)
```

---

## Troubleshooting

### Issue: Stats not updating

**Cause:** File write permission or race condition

**Solution:**
```bash
# Check file exists and is writable
ls -la downloads/stats.json

# Reset if corrupted
echo '{"updated":0,"counts":{},"last_download":{}}' > downloads/stats.json
```

### Issue: Badge shows "no file"

**Cause:** No PDFs in downloads/ or index.json missing

**Solution:**
```bash
# Generate index.json
cd downloads && python ../scripts/pages/make_downloads_json.py

# Or copy PDFs
cp dist/*.pdf downloads/
```

### Issue: Badge workflow not running

**Cause:** Schedule trigger disabled or branch protection

**Solution:**
```bash
# Trigger manually
gh workflow run badge-update.yml

# Check workflow status
gh run list --workflow=badge-update.yml
```

---

## API Reference

### Endpoints Summary:

| Endpoint | Method | Description | Format |
|----------|--------|-------------|---------|
| `/` | GET | Web dashboard | HTML |
| `/api/index.json` | GET | PDF metadata | JSON |
| `/api/stats.json` | GET | Download stats | JSON |
| `/api/summary.json` | GET | Combined summary | JSON |
| `/badge/latest.json` | GET | Latest PDF badge | Shields.io JSON |
| `/badge/downloads.json` | GET | Downloads count badge | Shields.io JSON |
| `/downloads/<file>` | GET | Serve PDF (+ track) | PDF |
| `/health` | GET | Health check | Plain text |

---

## Benefits

### 1. **Complete Analytics**
- Track every download automatically
- Per-file and total statistics
- Timestamp tracking

### 2. **Professional Badges**
- Shields.io compatible
- Real-time or static options
- Customizable colors

### 3. **User-Friendly UI**
- Dark/light theme
- Auto-refresh
- Responsive design

### 4. **Developer-Friendly**
- JSON APIs for integration
- RESTful design
- Well-documented

---

## Next Steps

1. **Test Locally:**
   ```bash
   python3 serve_pdfs.py
   # Visit http://localhost:5000
   ```

2. **Add PDFs:**
   ```bash
   cp dist/*.pdf downloads/
   python scripts/pages/make_downloads_json.py
   ```

3. **Deploy to Replit:**
   - Server auto-starts via workflow
   - Badge endpoints live at your Replit URL

4. **Add Badges to README:**
   ```markdown
   [![Latest](https://img.shields.io/endpoint?url=YOUR_URL/badge/latest.json)](...)
   ```

5. **Enable Workflow:**
   ```bash
   git add .github/workflows/badge-update.yml
   git commit -m "ci: add badge update workflow"
   git push
   ```

---

**Your Flask server now has enterprise-grade analytics and badge support! 🎉**
