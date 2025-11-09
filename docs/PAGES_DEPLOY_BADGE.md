# "Pages Deploy" Badge Integration

## Overview

The "Pages Deploy" badge monitors your GitHub Pages deployment status by querying GitHub's Pages API. It shows whether your latest deployment is built, building, queued, or errored.

## Features

### 1. **Deployment Status Monitoring**

Shows the current state of GitHub Pages:
- **"built"** (🟢 Bright Green) - Successfully deployed
- **"building"** (🔵 Blue) - Currently deploying
- **"queued"** (🔵 Blue) - Waiting to deploy
- **"errored"** (🔴 Red) - Deployment failed
- **"unknown"** (⚪ Grey) - Status unavailable

### 2. **Automatic Updates**

**After Pages Workflow:**
- Triggers automatically when Pages workflow completes
- Instant status update after deployment

**Periodic Checks:**
- Runs every 20 minutes via cron schedule
- Ensures status stays current

### 3. **GitHub API Integration**

Uses GitHub's official Pages API:
```bash
GET /repos/{owner}/{repo}/pages/builds/latest
```

Returns deployment status, timestamps, and build info.

---

## Implementation

### Workflow: `pages-deploy-badge.yml`

```yaml
name: Badges • Pages Deploy Status

on:
  workflow_dispatch:
  schedule:
    - cron: "*/20 * * * *"        # every 20 min
  workflow_run:                   # refresh right after Pages workflow
    workflows:
      - "pages"
    types: [completed]

permissions:
  contents: write

jobs:
  deploy-badge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Ensure docs/badges
        run: mkdir -p docs/badges

      - name: Query latest Pages build
        id: pages
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          set -e
          API="https://api.github.com/repos/${{ github.repository }}/pages/builds/latest"
          JSON=$(curl -sSL -H "Accept: application/vnd.github+json" \
                       -H "Authorization: Bearer $GH_TOKEN" "$API")
          echo "$JSON" > /tmp/latest_pages_build.json
          STATUS=$(jq -r '.status // "unknown"' /tmp/latest_pages_build.json)
          CREATED=$(jq -r '.created_at // ""' /tmp/latest_pages_build.json)
          UPDATED=$(jq -r '.updated_at // ""' /tmp/latest_pages_build.json)
          echo "status=$STATUS"  >> $GITHUB_OUTPUT
          echo "created=$CREATED" >> $GITHUB_OUTPUT
          echo "updated=$UPDATED" >> $GITHUB_OUTPUT

      - name: Write Pages deploy badge JSON
        run: |
          STATUS="${{ steps.pages.outputs.status }}"
          case "$STATUS" in
            built)     COLOR="brightgreen"; MSG="built"     ;;
            building)  COLOR="blue";        MSG="building"  ;;
            queued)    COLOR="blue";        MSG="queued"    ;;
            errored)   COLOR="red";         MSG="errored"   ;;
            *)         COLOR="lightgrey";   MSG="${STATUS:-unknown}" ;;
          esac
          cat > docs/badges/pages-deploy.json <<EOF
          { "schemaVersion": 1, "label": "pages deploy", "message": "${MSG}", "color": "${COLOR}" }
          EOF

      - name: Commit badge
        run: |
          git config user.name  "actions-bot"
          git config user.email "actions@users.noreply.github.com"
          git add docs/badges/pages-deploy.json
          git commit -m "chore(badges): refresh Pages deploy status (${{ steps.pages.outputs.status }})" || echo "No changes"
          git push
```

---

## Badge Usage

```markdown
[![Pages Deploy](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/pages-deploy.json)](https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/pages.yml)
```

---

## Complete 6-Badge Set

**All badges together:**

```markdown
[![Latest PDF](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/latest.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
[![Last updated](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/updated.json)](https://m9dswyptrn-web.github.io/SonicBuilder/)
[![Latest size](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/size.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
[![Downloads](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/downloads.json)](https://m9dswyptrn-web.github.io/SonicBuilder/)
[![PDF Health](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/pdf-health.json)](https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf)
[![Pages Deploy](https://img.shields.io/endpoint?url=https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/pages-deploy.json)](https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/pages.yml)
```

**Result shows:**
- 📄 Latest PDF filename
- ⏰ When last updated
- 📏 File size
- ⬇️ Total downloads
- 🟢 PDF health status
- ✅ Pages deployment status

---

## Badge Examples

### Built (Success)

```json
{
  "schemaVersion": 1,
  "label": "pages deploy",
  "message": "built",
  "color": "brightgreen"
}
```
![built](https://img.shields.io/badge/pages%20deploy-built-brightgreen)

### Building (In Progress)

```json
{
  "schemaVersion": 1,
  "label": "pages deploy",
  "message": "building",
  "color": "blue"
}
```
![building](https://img.shields.io/badge/pages%20deploy-building-blue)

### Errored (Failed)

```json
{
  "schemaVersion": 1,
  "label": "pages deploy",
  "message": "errored",
  "color": "red"
}
```
![errored](https://img.shields.io/badge/pages%20deploy-errored-red)

---

## How It Works

### 1. **Triggered After Pages Workflow**

The `workflow_run` trigger automatically runs this badge workflow whenever your main Pages workflow completes:

```yaml
workflow_run:
  workflows:
    - "pages"
  types: [completed]
```

### 2. **Queries GitHub Pages API**

Uses GitHub's official API to get the latest build status:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://api.github.com/repos/m9dswyptrn-web/SonicBuilder/pages/builds/latest
```

**API Response includes:**
- `status`: built, building, queued, errored
- `created_at`: When build started
- `updated_at`: Last status update

### 3. **Color-Coded Status**

```bash
built     → brightgreen (success)
building  → blue (in progress)
queued    → blue (waiting)
errored   → red (failure)
unknown   → lightgrey (unavailable)
```

### 4. **Commits Badge JSON**

Writes to `docs/badges/pages-deploy.json` and commits to repo.

---

## Use Cases

### 1. **Deployment Monitoring**
Track Pages deployment status in real-time.

### 2. **Build Verification**
Confirm successful deployment after commits.

### 3. **Error Detection**
Red badge instantly alerts to deployment failures.

### 4. **Status Dashboard**
Combine with other badges for complete project health.

### 5. **CI/CD Integration**
Monitor deployment pipeline status.

---

## Testing

### Manual Trigger:
```bash
gh workflow run pages-deploy-badge.yml
gh run list --workflow=pages-deploy-badge.yml --limit 1
```

### Check Latest Status:
```bash
# View badge JSON
cat docs/badges/pages-deploy.json

# Query Pages API directly
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/m9dswyptrn-web/SonicBuilder/pages/builds/latest | jq .status
```

### Verify Badge:
```bash
# After commit, check on GitHub Pages
curl https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/pages-deploy.json
```

---

## Troubleshooting

### Issue: Badge shows "unknown"

**Cause:** Pages not enabled or API unavailable

**Solution:**
```bash
# Verify Pages is enabled
# Settings → Pages → Source should be set

# Check API access
gh api repos/m9dswyptrn-web/SonicBuilder/pages/builds/latest
```

### Issue: Workflow doesn't trigger after Pages

**Cause:** Workflow name mismatch

**Solution:**
Check your Pages workflow name matches:
```yaml
workflow_run:
  workflows:
    - "pages"  # Must match your Pages workflow name exactly
```

### Issue: Badge not updating

**Cause:** Workflow not running or commit failing

**Solution:**
```bash
# Check workflow runs
gh run list --workflow=pages-deploy-badge.yml --limit 5

# View logs
gh run view <run-id> --log

# Trigger manually
gh workflow run pages-deploy-badge.yml
```

---

## Advanced: Alert Integration

The megapack includes optional Discord/Email alerts for deployment failures. To enable:

### Add Discord Alerts

1. Create Discord webhook in your server
2. Add secret: `DISCORD_WEBHOOK_URL`
3. Use enhanced workflow with alerts

### Add Email Alerts

1. Configure SMTP settings
2. Add secrets: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
3. Add secrets: `NOTIFY_EMAIL_TO`, `NOTIFY_EMAIL_FROM`
4. Use enhanced workflow with alerts

**See:** `text 6_1761844469287.txt` for alert-enhanced version

---

## API Reference

### GitHub Pages API

**Endpoint:**
```
GET /repos/{owner}/{repo}/pages/builds/latest
```

**Response:**
```json
{
  "status": "built",
  "created_at": "2024-10-30T12:00:00Z",
  "updated_at": "2024-10-30T12:05:00Z",
  "url": "https://api.github.com/repos/.../pages/builds/12345"
}
```

**Status Values:**
- `built` - Deployment successful
- `building` - In progress
- `queued` - Waiting to start
- `errored` - Failed

---

## Complete Badge System

**All 6 Badges:**

| Badge | Shows | Color | Source | Update |
|-------|-------|-------|--------|--------|
| **Latest** | Filename | 🔵 Blue | Flask/Workflow | 30 min |
| **Updated** | Time ago | 🟢/🟡 Green/Yellow | Flask/Workflow | 30 min |
| **Size** | File size | 🔵 Blue | Flask/Workflow | 30 min |
| **Downloads** | Count | 🟢 Green | Flask/Workflow | 30 min |
| **Health** | PDF status | 🟢/🔴 Green/Red | Flask/Workflow | 20 min |
| **Deploy** | Build status | 🟢/🔵/🔴 | Workflow only | After deploy |

**Integration:**
- ✅ 5 Flask endpoints (live badges)
- ✅ 6 GitHub workflows (static badges)
- ✅ Auto-updates after deployments
- ✅ Complete documentation
- ✅ Professional monitoring

---

**Your documentation now has comprehensive deployment monitoring! 🎉**
