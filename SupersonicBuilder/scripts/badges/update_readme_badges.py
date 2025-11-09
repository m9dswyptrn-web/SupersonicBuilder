import re, os, json, pathlib

owner = os.environ.get("SB_OWNER","m9dswyptrn-web")
repo  = os.environ.get("SB_REPO","SonicBuilder")
pages = f"https://{owner}.github.io/{repo}"

BADGE_BLOCK_START = "<!-- SONICBUILDER:DOCS-BADGES:START -->"
BADGE_BLOCK_END   = "<!-- SONICBUILDER:DOCS-BADGES:END -->"

block = f"""{BADGE_BLOCK_START}
<p align="center">

<a href="https://github.com/{owner}/{repo}/actions/workflows/docs-release.yml">
  <img alt="Docs Release" src="https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/docs-release.yml?label=Docs%20Release&logo=github">
</a>
&nbsp;
<a href="https://github.com/{owner}/{repo}/actions/workflows/docs-build.yml">
  <img alt="Docs Build" src="https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/docs-build.yml?label=Docs%20Build&logo=github">
</a>
&nbsp;
<a href="{pages}">
  <img alt="Pages Smoke" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2F{owner}%2F{repo}%2Fmain%2Fdocs%2Fbadges%2Fpages_smoke.json">
</a>
&nbsp;
<a href="https://github.com/{owner}/{repo}/actions/workflows/docs-coverage.yml">
  <img alt="Docs Coverage" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2F{owner}%2F{repo}%2Fmain%2Fdocs%2Fbadges%2Fdocs_coverage.json">
</a>

</p>

**Latest Docs:**  
- Release: [Releases](https://github.com/{owner}/{repo}/releases)  
- Pages: [{pages}]({pages})
{BADGE_BLOCK_END}
"""

readme = pathlib.Path("README.md")
text = readme.read_text(encoding="utf-8") if readme.exists() else "# SonicBuilder\n\n"

if BADGE_BLOCK_START in text and BADGE_BLOCK_END in text:
    text = re.sub(
        f"{BADGE_BLOCK_START}[\\s\\S]*?{BADGE_BLOCK_END}",
        block.strip(),
        text,
        flags=re.M
    )
else:
    # insert near top (after first header)
    parts = text.splitlines()
    if parts and parts[0].startswith("# "):
        parts.insert(1, "\n" + block.strip() + "\n")
        text = "\n".join(parts)
    else:
        text = block.strip() + "\n\n" + text

readme.write_text(text, encoding="utf-8")
print("README badges block updated.")
