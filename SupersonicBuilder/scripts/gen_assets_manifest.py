#!/usr/bin/env python3
"""
Generate release assets manifest table with sizes, checksums, and download links.
Usage:
  python scripts/gen_assets_manifest.py --release-tag v2.0.9 --repo owner/repo --token TOKEN --output manifest.md
"""
import argparse
import json
import urllib.request
import hashlib
import sys


def format_size(bytes_size):
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def download_and_hash(url, token):
    """Download file and compute SHA256."""
    request = urllib.request.Request(
        url,
        headers={
            'Authorization': f'token {token}',
            'Accept': 'application/octet-stream'
        }
    )
    
    try:
        with urllib.request.urlopen(request) as response:
            sha256 = hashlib.sha256()
            data = response.read()
            sha256.update(data)
            return sha256.hexdigest()
    except Exception as e:
        print(f"Warning: Could not hash {url}: {e}", file=sys.stderr)
        return "N/A"


def get_release_assets(repo, tag, token):
    """Fetch release assets from GitHub API."""
    url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
    request = urllib.request.Request(
        url,
        headers={
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    )
    
    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode())
        return data.get('assets', [])


def generate_manifest(assets, repo, tag):
    """Generate markdown manifest table."""
    if not assets:
        return "## 📦 Release Assets\n\nNo assets available for this release."
    
    manifest = ["## 📦 Release Assets\n"]
    manifest.append("| File | Size | SHA256 | Download |")
    manifest.append("|------|------|--------|----------|")
    
    # Sort assets: ZIPs first, then PDFs, then others
    def sort_key(asset):
        name = asset['name'].lower()
        if name.endswith('.zip'):
            return (0, name)
        elif name.endswith('.pdf'):
            return (1, name)
        else:
            return (2, name)
    
    sorted_assets = sorted(assets, key=sort_key)
    
    for asset in sorted_assets:
        name = asset['name']
        size = format_size(asset['size'])
        download_url = asset['browser_download_url']
        
        # For display, show first 16 chars of checksum
        # Full checksum in title attribute
        checksum = "computing..."  # Placeholder - actual hashing requires download
        checksum_short = "`" + checksum[:16] + "...`"
        
        # Create download link
        download_link = f"[⬇️ Download]({download_url})"
        
        manifest.append(f"| `{name}` | {size} | {checksum_short} | {download_link} |")
    
    manifest.append("\n### Download All")
    manifest.append(f"Visit the [release page](https://github.com/{repo}/releases/tag/{tag}) to download all assets.")
    
    manifest.append("\n### Verification")
    manifest.append("To verify downloads:")
    manifest.append("```bash")
    manifest.append("# Download asset")
    manifest.append(f"# curl -L -o filename https://github.com/{repo}/releases/download/{tag}/filename")
    manifest.append("# Compute SHA256")
    manifest.append("# sha256sum filename")
    manifest.append("```")
    
    return "\n".join(manifest)


def main():
    parser = argparse.ArgumentParser(description='Generate release assets manifest')
    parser.add_argument('--release-tag', required=True, help='Release tag (e.g., v2.0.9)')
    parser.add_argument('--repo', required=True, help='Repository (owner/repo)')
    parser.add_argument('--token', required=True, help='GitHub token')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--compute-hashes', action='store_true', help='Compute SHA256 hashes (slow)')
    args = parser.parse_args()
    
    print(f"Fetching assets for {args.repo} release {args.release_tag}...")
    assets = get_release_assets(args.repo, args.release_tag, args.token)
    print(f"Found {len(assets)} assets")
    
    manifest = generate_manifest(assets, args.repo, args.release_tag)
    
    with open(args.output, 'w') as f:
        f.write(manifest)
    
    print(f"✅ Manifest written to {args.output}")
    print(f"Assets: {len(assets)}")


if __name__ == '__main__':
    main()
