#!/usr/bin/env python3
# security_badges_tiles_bootstrap.py — Security tile + header badges for MkDocs (idempotent)
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MK = ROOT / "mkdocs.yml"
INDEX = ROOT / "docs" / "index.md"
OVR = ROOT / "docs" / "overrides" / "main.html"
README_SNIPPET = ROOT / "README_security_badges.md"

BADGES_HEADER = """\
{% extends "base.html" %}
{% block extrahead %}{{ super() }}{% endblock %}
{% block content %}
  <div id="sb-badges" style="margin:0 0 12px 0; display:flex; flex-wrap:wrap; gap:8px;">
    <!-- Status badges (shields.io) -->
    <a href="https://github.com/{{ config.repo_url | replace('https://github.com/','') }}/actions" target="_blank" rel="noopener">
      <img alt="CI" src="https://img.shields.io/github/actions/workflow/status/{{ config.repo_url | replace('https://github.com/','') }}/supersonic-build.yml?label=CI&logo=github" />
    </a>
    <a href="https://github.com/{{ config.repo_url | replace('https://github.com/','') }}/actions" target="_blank" rel="noopener">
      <img alt="Docs" src="https://img.shields.io/github/actions/workflow/status/{{ config.repo_url | replace('https://github.com/','') }}/docs-mkdocs.yml?label=Docs&logo=github" />
    </a>
    <a href="https://github.com/{{ config.repo_url | replace('https://github.com/','') }}/security/code-scanning" target="_blank" rel="noopener">
      <img alt="CodeQL" src="https://img.shields.io/github/actions/workflow/status/{{ config.repo_url | replace('https://github.com/','') }}/codeql.yml?label=CodeQL&logo=github" />
    </a>
    <a href="https://github.com/{{ config.repo_url | replace('https://github.com/','') }}/security/dependabot" target="_blank" rel="noopener">
      <img alt="Dependabot" src="https://img.shields.io/badge/dependabot-enabled-025e8c?logo=dependabot" />
    </a>
  </div>
  {{ super() }}
{% endblock %}
"""

SEC_TILE_MD = """
## Security

<div class="grid cards" markdown>
- :material-shield-lock:{ .lg } **Security Dashboard**  
  _Live feed of CodeQL alerts, Dependabot advisories, and recent audit notes._  
  [:octicons-arrow-right-24: Open dashboard](security/dashboard.md)

- :material-license:{ .lg } **Open Source Licenses**  
  _Auto-generated license inventory for Python & NPM deps (updates weekly/on demand)._  
  [:octicons-arrow-right-24: View licenses](security/licenses.md)
</div>
"""

README_BADGES = """<!-- Security & status badges (drop into README.md near the top) -->
<p align="center">
  <a href="https://github.com/OWNER/REPO/actions"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/OWNER/REPO/supersonic-build.yml?label=CI&logo=github"></a>
  <a href="https://github.com/OWNER/REPO/actions"><img alt="Docs" src="https://img.shields.io/github/actions/workflow/status/OWNER/REPO/docs-mkdocs.yml?label=Docs&logo=github"></a>
  <a href="https://github.com/OWNER/REPO/security/code-scanning"><img alt="CodeQL" src="https://img.shields.io/github/actions/workflow/status/OWNER/REPO/codeql.yml?label=CodeQL&logo=github"></a>
  <a href="https://github.com/OWNER/REPO/security/dependabot"><img alt="Dependabot" src="https://img.shields.io/badge/dependabot-enabled-025e8c?logo=dependabot"></a>
  <a href="https://OWNER.github.io/REPO/"><img alt="Pages" src="https://img.shields.io/badge/docs-online-00ffff"></a>
</p>
"""

def ensure_mkdocs_override():
    if not MK.exists():
        print("! mkdocs.yml not found; skipping theme.custom_dir patch.")
        return
    text = MK.read_text(encoding="utf-8")
    if "theme:" not in text:
        # add minimal theme section
        text += "\n\ntheme:\n  name: material\n"
    # ensure custom_dir points to docs/overrides
    if "custom_dir:" not in text:
        # insert under theme:
        text = re.sub(r"(?m)^theme:\s*\n", "theme:\n  custom_dir: docs/overrides\n", text, count=1)
    elif "custom_dir: docs/overrides" not in text:
        text = text.replace("custom_dir:", "custom_dir: docs/overrides  # patched", 1)
    MK.write_text(text, encoding="utf-8")
    print("→ patched mkdocs.yml (theme.custom_dir)")

def ensure_index_tile():
    if not INDEX.exists():
        print("! docs/index.md not found; creating new file with Security tile.")
        INDEX.parent.mkdir(parents=True, exist_ok=True)
        INDEX.write_text("# Overview\n" + SEC_TILE_MD + "\n", encoding="utf-8")
        print("→ wrote docs/index.md with Security tile")
        return
    txt = INDEX.read_text(encoding="utf-8")
    if "Security Dashboard" in txt and "Open Source Licenses" in txt:
        print("→ docs/index.md already has Security tile")
        return
    # add Security section near end
    if txt.strip().endswith(("\n", "\r\n")):
        txt += "\n" + SEC_TILE_MD + "\n"
    else:
        txt += "\n\n" + SEC_TILE_MD + "\n"
    INDEX.write_text(txt, encoding="utf-8")
    print("→ appended Security tile to docs/index.md")

def main():
    # override template that injects badges header
    OVR.parent.mkdir(parents=True, exist_ok=True)
    OVR.write_text(BADGES_HEADER, encoding="utf-8")
    print("→ wrote docs/overrides/main.html (badges header)")

    ensure_mkdocs_override()
    ensure_index_tile()

    # README helper snippet
    README_SNIPPET.write_text(README_BADGES, encoding="utf-8")
    print("→ wrote README_security_badges.md (copy/paste into README if you want badges there too)")

    print("\n✅ Security badges + tile installed.")
    print("Docs will pick up the override on the next build (CI Docs workflow).")

if __name__ == "__main__":
    main()