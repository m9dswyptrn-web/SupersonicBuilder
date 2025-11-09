# "Last Updated" Badge Integration

## Overview

The "last updated" badge shows when the latest PDF was built, displaying human-readable relative time (e.g., "2h ago", "3d ago") with color coding based on recency.

## Features

### 1. **Human-Readable Time Format**

Uses intelligent relative time formatting:
- **"just now"** - Less than 1 minute ago
- **"5m ago"** - Minutes (under 1 hour)
- **"3h ago"** - Hours (under 24 hours)
- **"5d ago"** - Days (24+ hours)
- **"never"** - No PDFs available

### 2. **Smart Color Coding**

Badge color changes based on recency:
- **🟢 Bright Green** - "just now" or recent minutes
- **🟡 Yellow** - Hours old (under 24h)
- **🟠 Orange** - Days old (24h+)
- **⚪ Light Grey** - "never" (no PDFs)

### 3. **Dual Badge Options**

**Live Badge (Replit Server):**
```markdown
[![Last updated](https://img.shields.io/endpoint?url=YOUR_REPL_URL/badge/updated.json)](YOUR_REPL_URL/)
```

**Static Badge (GitHub Pages):**
```markdown
[![Last updated](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/updated.json)](https://m9dswyptrn-web.github.io/SonicBuilder/)
```

---

## Implementation Details

### Flask Endpoint: `/badge/updated.json`

```python
@app.route("/badge/updated.json")
def badge_updated():
    idx = get_index()
    latest = (idx.get("items") or [{}])[0]
    mtime = latest.get("mtime", 0)
    human = _fmt_human(mtime)
    
    # Color by recency
    color = "brightgreen"
    if human.endswith("h ago") or human.endswith("d ago"):
        color = "yellow" if ("h" in human and not human.startswith("24")) else "orange"
    if human == "never":
        color = "lightgrey"
    
    payload = {
        "schemaVersion": 1,
        "label": "last updated",
        "message": human,
        "color": color
    }
    return Response(json.dumps(payload), mimetype="application/json")
```

### Time Formatting Function

```python
from datetime import datetime, timezone

def _fmt_human(ts):
    """Format timestamp as human-readable relative time."""
    if not ts:
        return "never"
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    delta = now - dt
    mins = int(delta.total_seconds() // 60)
    if mins < 1:
        return "just now"
    if mins < 60:
        return f"{mins}m ago"
    hrs = mins // 60
    if hrs < 24:
        return f"{hrs}h ago"
    days = hrs // 24
    return f"{days}d ago"
```

### Workflow Integration

The `.github/workflows/badge-update.yml` workflow now generates a static `updated.json` badge file:

```python
# last updated badge
mtime = latest.get("mtime", 0)

def human(ts):
    if not ts:
        return "never"
    now = time.time()
    mins = int((now - ts)//60)
    if mins < 1: return "just now"
    if mins < 60: return f"{mins}m ago"
    hrs = mins//60
    if hrs < 24: return f"{hrs}h ago"
    days = hrs//24
    return f"{days}d ago"

msg = human(mtime)
color = "brightgreen"
if msg.endswith("h ago") or msg.endswith("d ago"):
    color = "yellow" if ("h" in msg and not msg.startswith("24")) else "orange"
if msg == "never":
    color = "lightgrey"

(docs/"updated.json").write_text(json.dumps({
    "schemaVersion": 1,
    "label": "last updated",
    "message": msg,
    "color": color
}), "utf-8")
```

---

## UI Enhancement

### Exact Build Time Display

The dashboard now shows the exact UTC build timestamp:

```javascript
// Exact build time display
const summary = await fetchJSON('/api/summary.json');
const ts = summary.latest_mtime ? new Date(summary.latest_mtime*1000) : null;
document.getElementById('exactTime').textContent =
    ts ? `Exact build time (UTC): ${ts.toISOString()}` : 'No builds yet';
```

**Displays:**
```
Exact build time (UTC): 2025-10-30T14:04:00.000Z
```

---

## Badge Examples

### Time-Based Badge Evolution

**Fresh build:**
```json
{
  "schemaVersion": 1,
  "label": "last updated",
  "message": "just now",
  "color": "brightgreen"
}
```
![Fresh](https://img.shields.io/badge/last%20updated-just%20now-brightgreen)

**30 minutes old:**
```json
{
  "schemaVersion": 1,
  "label": "last updated",
  "message": "30m ago",
  "color": "brightgreen"
}
```
![30m](https://img.shields.io/badge/last%20updated-30m%20ago-brightgreen)

**5 hours old:**
```json
{
  "schemaVersion": 1,
  "label": "last updated",
  "message": "5h ago",
  "color": "yellow"
}
```
![5h](https://img.shields.io/badge/last%20updated-5h%20ago-yellow)

**3 days old:**
```json
{
  "schemaVersion": 1,
  "label": "last updated",
  "message": "3d ago",
  "color": "orange"
}
```
![3d](https://img.shields.io/badge/last%20updated-3d%20ago-orange)

**No builds:**
```json
{
  "schemaVersion": 1,
  "label": "last updated",
  "message": "never",
  "color": "lightgrey"
}
```
![Never](https://img.shields.io/badge/last%20updated-never-lightgrey)

---

## Complete Badge Set

Use all three badges together for comprehensive status:

```markdown
[![Latest](https://img.shields.io/endpoint?url=YOUR_REPL_URL/badge/latest.json)](YOUR_REPL_URL/downloads/latest.pdf)
[![Downloads](https://img.shields.io/endpoint?url=YOUR_REPL_URL/badge/downloads.json)](YOUR_REPL_URL/)
[![Last updated](https://img.shields.io/endpoint?url=YOUR_REPL_URL/badge/updated.json)](YOUR_REPL_URL/)
```

**Result:**
- Shows latest filename
- Shows total download count
- Shows when last updated

---

## Testing

### Test Live Endpoint:
```bash
curl http://localhost:5000/badge/updated.json
```

**Expected output:**
```json
{
  "schemaVersion": 1,
  "label": "last updated",
  "message": "2h ago",
  "color": "yellow"
}
```

### Test with Different Times:

```bash
# Create test file with old timestamp
touch -t 202510291200 downloads/old.pdf

# Regenerate index
python scripts/pages/make_downloads_json.py

# Check badge
curl http://localhost:5000/badge/updated.json
# Should show: "24h ago" or similar
```

---

## Workflow Behavior

The `badge-update.yml` workflow:
1. **Runs every 30 minutes**
2. Reads `downloads/index.json`
3. Extracts latest PDF's `mtime`
4. Calculates human-readable time
5. Determines color based on age
6. Writes `docs/badges/updated.json`
7. Commits and pushes

**Result:** Static badge updates automatically every 30 minutes on GitHub Pages.

---

## Color Logic

```python
# Fresh (minutes)
if mins < 60:
    color = "brightgreen"

# Hours (yellow for <24h)
if hrs < 24:
    color = "yellow"

# Days (orange for 24h+)
if days >= 1:
    color = "orange"

# Never built
if message == "never":
    color = "lightgrey"
```

**Visual progression:**
```
Just built → 🟢 Bright Green
2h old     → 🟡 Yellow
2d old     → 🟠 Orange
Never      → ⚪ Light Grey
```

---

## Use Cases

### 1. **README Status**
```markdown
# My Project

[![Last updated](https://img.shields.io/endpoint?url=...)](...)

Shows visitors when docs were last built.
```

### 2. **CI/CD Monitoring**
Track how long since last successful build.

### 3. **Documentation Freshness**
Alert users to potentially outdated docs with orange badge.

### 4. **Multi-Project Dashboard**
Display update status for multiple documentation sets.

---

## Customization

### Change Time Thresholds

Edit `_fmt_human()`:
```python
def _fmt_human(ts):
    # ... existing code ...
    if mins < 120:  # 2 hours instead of 60 minutes
        return f"{mins}m ago"
```

### Change Colors

Edit `badge_updated()`:
```python
# Use different colors
color = "blue"  # Instead of brightgreen
color = "red"   # For very old builds
```

### Change Labels

```python
payload = {
    "label": "docs updated",  # Custom label
    "message": human,
    "color": color
}
```

---

## Troubleshooting

### Issue: Badge always shows "never"

**Cause:** No PDFs in `downloads/` or `index.json` is empty

**Solution:**
```bash
# Copy PDFs
cp dist/*.pdf downloads/

# Generate index
python scripts/pages/make_downloads_json.py

# Verify
cat downloads/index.json | grep mtime
```

### Issue: Badge shows wrong time

**Cause:** Server timezone mismatch

**Solution:** The function uses UTC explicitly:
```python
dt = datetime.fromtimestamp(ts, tz=timezone.utc)
now = datetime.now(tz=timezone.utc)
```

### Issue: Workflow badge not updating

**Cause:** Workflow not running or commit failing

**Solution:**
```bash
# Trigger manually
gh workflow run badge-update.yml

# Check logs
gh run list --workflow=badge-update.yml --limit 1
gh run view <run-id>
```

---

## API Reference

### New Endpoint

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/badge/updated.json` | GET | Last update badge | Shields.io JSON |

### Response Format

```json
{
  "schemaVersion": 1,
  "label": "last updated",
  "message": "2h ago",
  "color": "yellow"
}
```

### Dashboard Addition

New element on dashboard:
```html
<p class="small" id="exactTime" style="margin-top:8px;font-style:italic">
  Exact build time (UTC): 2025-10-30T14:04:00.000Z
</p>
```

---

## Integration Summary

**Complete badge system now includes:**

1. ✅ **Latest PDF** - Shows current filename
2. ✅ **Downloads** - Shows total count
3. ✅ **Last Updated** - Shows recency (NEW)

**All with:**
- Live endpoints (Replit server)
- Static endpoints (GitHub Pages)
- Auto-updating workflow (every 30 min)
- Smart color coding
- Human-readable formatting

---

**Your documentation now has comprehensive status badges! 🎉**
