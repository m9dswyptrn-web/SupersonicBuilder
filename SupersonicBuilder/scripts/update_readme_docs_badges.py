#!/usr/bin/env python3
import os, re, subprocess, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
VERSION_FILE = ROOT / "VERSION"

def sh(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()

def get_owner_repo():
    remote = sh("git remote get-url origin")
    m = re.search(r'github\.com[/:]([^/]+)/([^/.]+)', remote)
    if not m:
        raise SystemExit("Cannot parse origin remote to get owner/repo")
    return m.group(1), m.group(2)

def get_version():
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    try:
        return sh("git describe --tags --abbrev=0")
    except subprocess.CalledProcessError:
        return "v0.0.0"

def get_commit_short():
    return sh("git rev-parse --short=8 HEAD")

def rewrite_block(readme_text, owner, repo, version, commit):
    begin = r"<!-- DOCS-BADGES:BEGIN -->"
    end   = r"<!-- DOCS-BADGES:END -->"
    p = re.compile(f"{begin}.*?{end}", re.S)

    pages_base = f"https://{owner}.github.io/{repo}/"
    dark_url   = f"{pages_base}?theme=dark"
    light_url  = f"{pages_base}?theme=light"

    asset_zip  = f"SonicBuilder_Manual_{version}_g{commit}.zip"
    asset_url  = f"https://github.com/{owner}/{repo}/releases/download/{version}/{asset_zip}"

    new_block = f"""{begin}
<p align="center">
  <a href="https://github.com/{owner}/{repo}/actions/workflows/docs-build.yml">
    <img alt="Docs Build" src="https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/docs-build.yml?label=Docs%20Build&logo=github">
  </a>
  <a href="https://github.com/{owner}/{repo}/actions/workflows/docs-release.yml">
    <img alt="Docs Release" src="https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/docs-release.yml?label=Docs%20Release&logo=github">
  </a>
  <a href="https://github.com/{owner}/{repo}/releases/latest">
    <img alt="Latest Release" src="https://img.shields.io/github/v/release/{owner}/{repo}?display_name=tag&logo=github">
  </a>
</p>
<p align="center">
  <a href="{dark_url}">
    <img alt="Open Docs (Dark)" src="https://img.shields.io/badge/docs-dark-111111?logo=readthedocs&logoColor=white">
  </a>
  <a href="{light_url}">
    <img alt="Open Docs (Light)" src="https://img.shields.io/badge/docs-light-f6f8fa?logo=readthedocs&logoColor=000">
  </a>
  <a href="{asset_url}">
    <img alt="Download PDF Bundle" src="https://img.shields.io/badge/download-PDF_bundle-4c9aff?logo=adobeacrobatreader">
  </a>
</p>
{end}"""

    if p.search(readme_text):
        return p.sub(new_block, readme_text)
    else:
        return readme_text.rstrip() + "\n\n" + new_block + "\n"

def main():
    owner, repo = get_owner_repo()
    version = get_version()
    commit  = get_commit_short()

    text = README.read_text(encoding="utf-8")
    updated = rewrite_block(text, owner, repo, version, commit)
    if updated != text:
        README.write_text(updated, encoding="utf-8")
        print(f"[OK] README badges updated for {version} (g{commit})")
    else:
        print("[OK] README badges already up to date")

if __name__ == "__main__":
    main()
