#!/usr/bin/env python3
"""
Compute local badge completeness by checking release_assets/ against
required asset patterns from .github/required-assets.txt
"""
import os, re, json, glob, sys
from pathlib import Path

def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "release_assets"
    
    # Get asset files
    assets = [Path(p).name for p in glob.glob(f"{output_dir}/*") if os.path.isfile(p)]
    
    # Load required patterns
    patterns_env = os.environ.get("SB_REQUIRED_ASSETS_PATTERNS", "").strip()
    if patterns_env:
        pats = [p.strip() for p in patterns_env.splitlines() if p.strip()]
    else:
        path = Path(".github/required-assets.txt")
        if path.exists():
            pats = [l.strip() for l in path.read_text().splitlines() 
                    if l.strip() and not l.strip().startswith("#")]
        else:
            pats = [
                r".*manual.*_g[0-9a-f]{7,12}\.pdf$",
                r".*appendix.*_g[0-9a-f]{7,12}\.pdf$"
            ]
    
    # Check which patterns are missing
    missing = []
    for pat in pats:
        rx = re.compile(pat, re.I)
        if not any(rx.search(a) for a in assets):
            missing.append(pat)
    
    has_all = not missing
    
    # Generate badge JSON
    badge = {
        "schemaVersion": 1,
        "label": "Docs Complete (local)",
        "message": "complete" if has_all else f"incomplete ({len(missing)})",
        "color": "brightgreen" if has_all else "yellow",
        "labelColor": "black"
    }
    
    # Write badge JSON
    status_dir = Path(".status")
    status_dir.mkdir(exist_ok=True)
    badge_file = status_dir / "docs-release-completeness.local.json"
    badge_file.write_text(json.dumps(badge))
    
    print(f"Wrote {badge_file}")
    
    if missing:
        print(f"Missing patterns (no matching asset names in {output_dir}/):")
        for m in missing:
            print(f" - {m}")
    
    # Also print the badge for preview
    print("\nPreview:")
    print(json.dumps(badge, indent=2))

if __name__ == "__main__":
    main()
