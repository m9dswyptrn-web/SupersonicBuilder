# SB_REPO_URL Workflow Patch

This patch guarantees your builds and releases have a stable `SB_REPO_URL` for QR codes
and PDF metadata. It prefers GitHub; if unavailable, it falls back to your Replit app URL.

## Files added

- `.github/workflows/repo-url-setup.yml` (reusable workflow)
- `.github/workflows/release.yml` (example release that consumes it; merge into yours)
- `docs/USING_SB_REPO_URL.md` (usage guide)

## Use in your existing workflows

Add a job that *uses* the reusable file:

```yaml
jobs:
  setup-url:
    uses: ./.github/workflows/repo-url-setup.yml
```

Then in any job that needs it:

```yaml
env:
  SB_REPO_URL: ${{ needs.setup-url.outputs.SB_REPO_URL }}
```

Now your CoA step (or any PDF generator) can omit `--qr`; the environment provides it.
