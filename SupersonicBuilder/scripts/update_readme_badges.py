#!/usr/bin/env python3
"""Insert or update badge block including workflow status and tag date."""
import argparse, os, re

DEFAULT_SNIPPET = '''<!-- SonicBuilder: Badges -->
<p align="center">
  <a href="https://github.com/OWNER/REPO/releases/latest">
    <img alt="Latest Release" src="https://img.shields.io/github/v/release/OWNER/REPO?display_name=tag&sort=semver">
  </a>
  <a href="https://github.com/OWNER/REPO/releases/latest">
    <img alt="Dark Manual (PDF)" src="https://img.shields.io/badge/download-dark_manual.pdf-0b7285?logo=adobeacrobatreader&logoColor=white">
  </a>
  <a href="https://github.com/OWNER/REPO/releases/latest">
    <img alt="Two‑Up Raster (PDF)" src="https://img.shields.io/badge/download-two_up_raster.pdf-5f3dc4?logo=adobeacrobatreader&logoColor=white">
  </a>
  <a href="https://github.com/OWNER/REPO/actions/workflows/release.yml">
    <img alt="Release Workflow Status" src="https://github.com/OWNER/REPO/actions/workflows/release.yml/badge.svg">
  </a>
  <a href="https://github.com/OWNER/REPO/releases/latest">
    <img alt="Tag Date" src="https://img.shields.io/github/release-date/OWNER/REPO">
  </a>
</p>
<!-- /SonicBuilder: Badges -->
'''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="owner/repo")
    ap.add_argument("--manual", default="sonic_manual_dark.pdf")
    ap.add_argument("--two_up", default="sonic_manual_dark_two_up_raster.pdf")
    ap.add_argument("--workflow", default="release.yml")
    ap.add_argument("--readme", default="README.md")
    args = ap.parse_args()

    if not os.path.exists(args.readme):
        print("[error] README not found at", args.readme)
        return 2

    snip = DEFAULT_SNIPPET.replace("OWNER/REPO", args.repo)
    snip = snip.replace("dark_manual.pdf", args.manual).replace("two_up_raster.pdf", args.two_up)
    snip = snip.replace("release.yml", args.workflow)

    with open(args.readme, "r", encoding="utf-8") as f:
        readme = f.read()

    start = "<!-- SonicBuilder: Badges -->"
    end = "<!-- /SonicBuilder: Badges -->"
    if start in readme and end in readme:
        new = re.sub(re.escape(start)+".*?"+re.escape(end), snip, readme, flags=re.S)
        act="updated"
    else:
        new = snip + "\n" + readme
        act="inserted"
    with open(args.readme,"w",encoding="utf-8") as f:
        f.write(new)
    print(f"[ok] badges {act}")

if __name__ == "__main__":
    main()
