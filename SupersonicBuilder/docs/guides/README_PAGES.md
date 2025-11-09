# GitHub Pages Bundle (Static Docs Hosting)

This bundle publishes your `docs/` front page and optional `/dist/*.pdf` downloads
to GitHub Pages using `actions/deploy-pages`.

## Files
- `.github/workflows/pages.yml` — CI to build and deploy a static site from `docs/` (+ optional `dist/*.pdf`).
- `README_PAGES.md` — this guide.
- `Makefile.append` — optional local helpers to build and open the site artifact.

## Setup
1) In your repo Settings → **Pages**:
   - Build and deployment: **GitHub Actions**
2) Commit this bundle, push to `main`.
3) The workflow deploys on every push to `main` and on Releases.

## What gets published
- `docs/` → becomes the site root.
  - Ensure you have `docs/index.html` (your front page).
- `dist/*.pdf` (if present) → copied to `downloads/` for easy links.

## URLs
- Site: `https://<owner>.github.io/<repo>/`
- Latest downloads (example): `https://<owner>.github.io/<repo>/downloads/<file>.pdf`

## Notes
- This is static-only (no Python server required). Works alongside your Replit server.
- You can keep both: Replit for APIs and health/status; Pages for public static docs.
- If you use a custom domain, configure it in Settings → Pages after first deploy.
