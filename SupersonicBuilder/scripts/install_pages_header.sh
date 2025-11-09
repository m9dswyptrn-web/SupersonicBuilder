#!/usr/bin/env bash
set -euo pipefail

OWNER_REPO="$(git remote get-url origin 2>/dev/null | sed -E 's#.*github.com[:/](.+)\.git#\1#' || true)"
OWNER="${OWNER_REPO%%/*}"; REPO="${OWNER_REPO##*/}"
: "${OWNER:=m9dswyptrn-web}"; : "${REPO:=SonicBuilder}"
README="README.md"

HEADER_FILE=".sb_header.tmp.md"
cat > "$HEADER_FILE" <<'HDR'
<!-- SB:HEADER-START -->
<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/main/docs/assets/logo_dark.png">
  <img alt="SonicBuilder" height="96" src="https://raw.githubusercontent.com/m9dswyptrn-web/SonicBuilder/main/docs/assets/logo_light.png">
</picture>

# SonicBuilder

**Android + RR2 + G-RZ-GM59 Builder Project**  
Enterprise-grade docs, CI/CD, diagnostics, and live gallery.

<a href="https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/Latest%20Download-latest.pdf-00d8ff?style=for-the-badge">
    <img alt="Latest Download" src="https://img.shields.io/badge/Latest%20Download-latest.pdf-1f6feb?style=for-the-badge">
  </picture>
</a>

<a href="https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/pages-publish.yml">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/pages-publish.yml?label=Pages%20Deploy&style=for-the-badge&logo=github">
    <img alt="Pages Deploy" src="https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/pages-publish.yml?label=Pages%20Deploy&style=for-the-badge&logo=github">
  </picture>
</a>
<a href="https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/pages-smoke.yml">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/pages-smoke.yml?label=Smoke%20Check&style=for-the-badge&logo=testcafe">
    <img alt="Smoke Check" src="https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/pages-smoke.yml?label=Smoke%20Check&style=for-the-badge&logo=testcafe">
  </picture>
</a>

<p>
  <a href="https://m9dswyptrn-web.github.io/SonicBuilder/">Website</a> ·
  <a href="https://m9dswyptrn-web.github.io/SonicBuilder/docs/">Docs</a> ·
  <a href="https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html">Motherboard Gallery</a> ·
  <a href="https://github.com/m9dswyptrn-web/SonicBuilder/releases">Releases</a>
</p>

</div>
<!-- SB:HEADER-END -->
HDR

if [[ ! -f "$README" ]]; then
  echo "# ${REPO}" > "$README"
fi

if grep -q '<!-- SB:HEADER-START -->' "$README"; then
  awk -v RS= -v ORS= '
    BEGIN{found=0}
    {
      gsub(/\r/,"")
      if ($0 ~ /<!-- SB:HEADER-START -->/ && $0 ~ /<!-- SB:HEADER-END -->/) {
        while ((getline line < "'$HEADER_FILE'") > 0) buf=buf line "\n";
        print buf; found=1
      } else print
    }' "$README" > "$README.tmp"
  mv "$README.tmp" "$README"
else
  cat "$HEADER_FILE" "$README" > "$README.tmp" && mv "$README.tmp" "$README"
fi

rm -f "$HEADER_FILE"

git add "$README"
git commit -m "docs(readme): theme-aware header + latest download & CI badges" || true
git push origin main
echo "✅ Header installed and pushed to https://github.com/${OWNER}/${REPO}"
