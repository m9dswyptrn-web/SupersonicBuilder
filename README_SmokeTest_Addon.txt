SonicBuilder Docs Smoke Test Add-on v1
Generated: 2025-10-29

Files:
- scripts/test_gallery_http_smoke.py
- .github/workflows/docs-post-publish-smoketest.yml
- Makefile.smoketest.addon
- README_SmokeTest_Addon.txt

## Installation

1. Copy all files to your SonicBuilder repo
2. Add to your main Makefile (near the top):
   -include Makefile.smoketest.addon

3. (Optional) Add webhook secrets in GitHub:
   - DISCORD_WEBHOOK_URL
   - SLACK_WEBHOOK_URL
   - EMAIL_WEBHOOK_URL

## Usage

Local testing:
  make smoke              # test both themes
  make smoke:dark         # force dark theme
  make smoke:light        # force light theme

CI/CD:
  - Workflow auto-runs after "Docs Release" completes
  - Can also trigger manually via "Run workflow" button

## Features

✅ Tests both dark and light themes
✅ Verifies HTML content snippets
✅ Auto-discovers and tests CSS/JS assets
✅ Configurable retries and timeouts
✅ Webhook notifications (Discord, Slack, Email)
✅ Detailed JSON diagnostics output
✅ Exit code 2 on failure for CI/CD alerting

## Target URL

https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html

Configure in Makefile.smoketest.addon or via SMOKE_URL env variable.
