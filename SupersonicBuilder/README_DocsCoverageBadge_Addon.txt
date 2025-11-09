SonicBuilder — Docs Coverage Badge
Generated: 2025-10-30 00:09:52 UTC

Purpose
- Badge goes green if latest release has **both** Dark and Light PDF bundles.

Install
  unzip -o SonicBuilder_DocsCoverageBadge_Addon_v1.zip
  cat Makefile.docs.coverage.addon >> Makefile
  git add scripts/check_docs_coverage.py .github/workflows/docs-coverage-badge.yml Makefile
  git commit -m "ci(badge): add docs coverage badge"
  git push

README badge
  <a href="https://github.com/m9dswyptrn-web/SonicBuilder/releases/latest">
    <img alt="Docs Coverage"
         src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/HEAD/docs/status/docs_coverage_status.json">
  </a>

Customize patterns via env:
- DOCS_ASSET_REGEX_DARK
- DOCS_ASSET_REGEX_LIGHT
