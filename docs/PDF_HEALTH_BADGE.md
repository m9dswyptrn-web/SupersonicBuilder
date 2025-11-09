# "PDF Health" Badge Integration

## Overview

The "PDF Health" badge monitors GitHub Pages availability by checking that the latest PDF is accessible. It provides real-time health status of your documentation hosting with clear OK/ERR indicators.

## Features

### 1. **Health Status Monitoring**

Checks if GitHub Pages is serving PDFs:
- **"OK"** (🟢 Bright Green) - PDF accessible on Pages
- **"ERR 404"** (🔴 Red) - PDF not found
- **"ERR 500"** (🔴 Red) - Server error
- **"ERR down"** (🔴 Red) - Site unreachable

### 2. **Dual Check Options**

**Live Badge (Replit Server):**
- Real-time check when badge loads
- Instant verification from Flask

**Static Badge (GitHub Pages via Workflow):**
- Automated checks every 20 minutes
- Committed to `docs/badges/pdf-health.json`
- Historical status tracking

### 3. **HTTP Status Reporting**

Shows specific error codes:
- `200-299` → OK (success)
- `404` → ERR 404 (not found)
- `500-599` → ERR 5xx (server error)
- `000` → ERR down (timeout/unreachable)

---

## Implementation

### Flask Endpoint: `/badge/pdf-health.json`

```python
import urllib.request, urllib.error
from flask import Response

@app.route("/badge/pdf-health.json")
def badge_pdf_health():
    owner = "m9dswyptrn-web"
    repo  = "SonicBuilder"
    url = f"https://{owner}.github.io/{repo}/downloads/latest.pdf"
    code = 0
    ok = False
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=8) as r:
            code = r.getcode() or 0
            ok = (200 <= code < 300)
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception:
        pass
    payload = {
        "schemaVersion": 1,
        "label": "pdf health",
        "message": "OK" if ok else f"ERR {code or 'down'}",
        "color": "brightgreen" if ok else "red"
    }
    return Response(json.dumps(payload), mimetype="application/json")
```

### Workflow: `pages-health-badge.yml`

```yaml
name: Badges • PDF Health (Pages)

on:
  workflow_dispatch:
  schedule:
    - cron: "*/20 * * * *"    # every 20 min
  push:
    paths:
      - ".github/workflows/pages-health-badge.yml"
      - "downloads/**"

permissions:
  contents: write

jobs:
  probe:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Ensure docs/badges exists
        run: mkdir -p docs/badges

      - name: Check Pages latest.pdf
        id: check
        env:
          OWNER: ${{ github.repository_owner }}
          REPO:  ${{ github.event.repository.name }}
        run: |
          set -e
          URL="https://${OWNER}.github.io/${REPO}/downloads/latest.pdf"
          CODE=$(curl -L -s -o /dev/null -w "%{http_code}" --max-time 10 "$URL" || echo "000")
          echo "url=$URL"   >> $GITHUB_OUTPUT
          echo "code=$CODE" >> $GITHUB_OUTPUT

      - name: Write health badge JSON
        run: |
          CODE="${{ steps.check.outputs.code }}"
          if [[ "$CODE" =~ ^2[0-9][0-9]$ ]]; then
            COLOR="brightgreen"; MSG="OK"
          else
            COLOR="red"; MSG="ERR ${CODE}"
          fi
          cat > docs/badges/pdf-health.json <<EOF
          { "schemaVersion": 1, "label": "pdf health", "message": "${MSG}", "color": "${COLOR}" }
          EOF

      - name: Commit badge
        run: |
          git config user.name  "actions-bot"
          git config user.email "actions@users.noreply.github.com"
          git add docs/badges/pdf-health.json
          git commit -m "chore(badges): update PDF health badge (${{ steps.check.outputs.code }})" || echo "No changes"
          git push
```

---

## Badge Usage

### Live Badge (Real-time)

```markdown
[![PDF Health (live)](https://img.shields.io/endpoint?url=REPL_URL/badge/pdf-health.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
```

### Static Badge (Periodic)

```markdown
[![PDF Health](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/pdf-health.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
```

---

## Complete Badge Set

**Recommended layout with all badges:**

```markdown
[![Latest PDF](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/latest.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
[![Last updated](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/updated.json)](https://m9dswyptrn-web.github.io/SonicBuilder/)
[![Latest size](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/size.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
[![PDF Health](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/pdf-health.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
```

**Result shows:**
- 📄 Latest PDF filename
- ⏰ When last updated
- 📏 File size  
- 🟢 Health status

---

## Badge Examples

### Success

```json
{
  "schemaVersion": 1,
  "label": "pdf health",
  "message": "OK",
  "color": "brightgreen"
}
```
![OK](https://img.shields.io/badge/pdf%20health-OK-brightgreen)

### Error 404

```json
{
  "schemaVersion": 1,
  "label": "pdf health",
  "message": "ERR 404",
  "color": "red"
}
```
![ERR 404](https://img.shields.io/badge/pdf%20health-ERR%20404-red)

### Error Down

```json
{
  "schemaVersion": 1,
  "label": "pdf health",
  "message": "ERR down",
  "color": "red"
}
```
![ERR down](https://img.shields.io/badge/pdf%20health-ERR%20down-red)

---

## Use Cases

1. **Uptime Monitoring** - Track GitHub Pages availability
2. **Deployment Verification** - Confirm Pages is serving files
3. **Quick Status** - Instant visibility of documentation health
4. **Alert System** - Red badge alerts to problems immediately
5. **Historical Tracking** - Git commits show status changes

---

## Testing

### Test Endpoint:
```bash
curl http://localhost:5000/badge/pdf-health.json
```

### Manual Workflow:
```bash
gh workflow run pages-health-badge.yml
gh run list --workflow=pages-health-badge.yml --limit 1
```

---

## API Reference

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/badge/pdf-health.json` | GET | PDF health check | Shields.io JSON |

### Response Format

```json
{
  "schemaVersion": 1,
  "label": "pdf health",
  "message": "OK" | "ERR {code}" | "ERR down",
  "color": "brightgreen" | "red"
}
```

---

## All Badge Endpoints

1. `/badge/latest.json` - Latest filename
2. `/badge/downloads.json` - Total downloads  
3. `/badge/updated.json` - Last updated time
4. `/badge/size.json` - File size
5. `/badge/pdf-health.json` - Health check

---

**Your documentation now has comprehensive health monitoring! 🎉**
