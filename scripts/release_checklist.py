#!/usr/bin/env python3
"""
Release checklist stamper — reads templates/RELEASE_CHECKLIST.md, 
stamps VERSION/COMMIT/DATE, writes docs/release-checklist.md
"""
import os, subprocess, sys
from pathlib import Path
from datetime import datetime

def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()

def main():
    template_path = Path("templates/RELEASE_CHECKLIST.md")
    output_path = Path("docs/release-checklist.md")
    
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    
    # Get metadata
    version = os.environ.get("VERSION", "")
    if not version:
        try:
            version = run("git describe --tags --abbrev=0 2>/dev/null || echo v0.0.0")
        except:
            version = "v0.0.0"
    
    try:
        commit = run("git rev-parse --short=12 HEAD 2>/dev/null || echo unknown")
    except:
        commit = "unknown"
    
    date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Read template
    template = template_path.read_text(encoding='utf-8')
    
    # Replace placeholders
    stamped = template.replace("{VERSION}", version)
    stamped = stamped.replace("{COMMIT}", commit)
    stamped = stamped.replace("{DATE}", date)
    stamped = stamped.replace("<TAG>", version)
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(stamped, encoding='utf-8')
    
    print(f"✅ Release checklist stamped for {version} @ {commit}")
    print(f"   Written to: {output_path}")

if __name__ == "__main__":
    main()
