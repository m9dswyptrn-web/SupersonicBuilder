# Supersonic CI/Docker Overlays (Additive-only)

These overlays are non-destructive: they add files with `-supersonic` names so your existing enterprise workflows remain untouched.

**Included:**
- `.github/workflows/docker-publish-supersonic.yml` — GHCR builds with cache
- `.github/workflows/docs-verify-supersonic.yml` — docs link checker
- `.github/workflows/pages-with-autofix-preview-supersonic.yml` — verify gate + auto-fix preview artifact
- `supersonic_verify_pages_supersonic.py` — verifier script
- `supersonic_verify_autofix_preview_supersonic.py` — preview generator

Rename later to promote these pipelines to primary names if desired.
