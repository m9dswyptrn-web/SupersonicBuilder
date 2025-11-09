#!/usr/bin/env python3
"""Appends a "Download Assets" section and verification report link to GitHub Release body."""
import argparse, requests

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True)
    ap.add_argument("--repo", required=True, help="owner/repo")
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    headers = {
        "Authorization": f"token {args.token}",
        "Accept": "application/vnd.github+json",
    }

    # Fetch release by tag
    r = requests.get(f"https://api.github.com/repos/{args.repo}/releases/tags/{args.tag}", headers=headers)
    r.raise_for_status()
    release = r.json()
    release_id = release["id"]
    upload_url_base = release["html_url"].replace("/tag/", "/download/")

    assets = release.get("assets", [])
    if not assets:
        print("[warn] No assets found on release", args.tag)
        return

    # Check if download section already exists
    current_body = release.get("body") or ""
    if "## 📥 Download Assets" in current_body:
        print("[info] Download Assets section already exists, skipping")
        return

    lines = ["\n## 📥 Download Assets"]
    has_report = False
    report_name = "RELEASE_ASSET_REPORT.md"
    
    for asset in assets:
        name = asset["name"]
        icon = "📄"
        lname = name.lower()
        
        if name == report_name:
            has_report = True
            continue  # Don't list report in main assets
            
        if "two_up" in lname:
            icon = "🖨️"
        elif "sha256" in lname:
            icon = "🔐"
            
        lines.append(f"- [{icon} {name}]({upload_url_base}/{name})")

    body = current_body + "\n" + "\n".join(lines)
    body += "\n\n🧾 *Printing tip: Print `*_two_up_raster.pdf` for field cards and shop binders.*"

    if has_report:
        body += f"\n\n🔎 **Verification Report:** [{report_name}]({upload_url_base}/{report_name})"

    r2 = requests.patch(
        f"https://api.github.com/repos/{args.repo}/releases/{release_id}",
        headers=headers,
        json={"body": body}
    )
    r2.raise_for_status()
    print("[ok] Appended asset links to release", args.tag)

if __name__ == "__main__":
    main()
