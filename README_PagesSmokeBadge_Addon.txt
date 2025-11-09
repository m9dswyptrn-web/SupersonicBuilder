SonicBuilder — Pages Smoke Badge
Generated: 2025-10-30 00:09:52 UTC

Purpose
- Badge shows **green** if both dark and light gallery URLs return HTTP 200.
- **Orange** if only one is up, **red** if both are down.

Install
  unzip -o SonicBuilder_PagesSmokeBadge_Addon_v1.zip
  cat Makefile.pages.smokebadge.addon >> Makefile
  git add scripts/pages_smoke_badge.py .github/workflows/pages-smoke-badge.yml Makefile
  git commit -m "ci(badge): add pages smoke badge"
  git push

README badge
  <a href="https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html">
    <img alt="Pages Smoke"
         src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/pages_smoke_status.json">
  </a>
