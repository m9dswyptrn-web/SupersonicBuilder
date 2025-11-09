#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
supersonic_verify_autofix_preview.py
------------------------------------------------------------
Generates a preview of automated link fixes in docs/_fixed_preview/
based on hints from supersonic_verify_pages.py.

This creates HTML files with corrected links that can be reviewed
before promoting to production via supersonic_promote_preview.py.

Usage:
  python supersonic_verify_autofix_preview.py
Exit 0 on success, 1 on fatal error.
"""
from __future__ import annotations
from pathlib import Path
from bs4 import BeautifulSoup
import shutil
import sys
import re

DOCS = Path("docs")
PREVIEW = DOCS / "_fixed_preview"

def main():
    print("=== 🔧 Auto-Fix Preview Generator ===")
    
    if not DOCS.exists():
        print("❌ docs/ folder not found")
        return 1
    
    # Clear and recreate preview directory
    if PREVIEW.exists():
        shutil.rmtree(PREVIEW)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created preview directory: {PREVIEW}")
    
    # Find all HTML files in docs/ (including subdirectories)
    html_files = list(DOCS.rglob("*.html"))
    if not html_files:
        print("ℹ️  No HTML files found in docs/")
        return 0
    
    print(f"🔍 Found {len(html_files)} HTML files to process (including subdirectories)")
    
    fixes_made = 0
    files_processed = 0
    
    for html_file in html_files:
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            
            file_fixes = 0
            
            # Fix common link issues
            for link in soup.find_all("a", href=True):
                href = str(link["href"])
                original_href = href
                
                # Fix: Remove duplicate docs/ prefix
                if href.startswith("docs/docs/"):
                    href = href.replace("docs/docs/", "docs/", 1)
                    file_fixes += 1
                
                # Fix: Ensure .html extension on local links
                if not href.startswith(("http://", "https://", "#", "mailto:")):
                    if not href.endswith(".html") and not href.endswith("/"):
                        # Check if target exists with .html
                        potential_target = DOCS / f"{href}.html"
                        if potential_target.exists():
                            href = f"{href}.html"
                            file_fixes += 1
                
                # Fix: Convert absolute paths to relative
                if href.startswith("/docs/"):
                    href = href.replace("/docs/", "", 1)
                    file_fixes += 1
                
                if href != original_href:
                    link["href"] = href
            
            # Only write if fixes were made
            if file_fixes > 0:
                # Preserve directory structure
                rel_path = html_file.relative_to(DOCS)
                preview_file = PREVIEW / rel_path
                preview_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(preview_file, "w", encoding="utf-8") as f:
                    f.write(str(soup))
                print(f"✓ {rel_path}: {file_fixes} fixes")
                fixes_made += file_fixes
                files_processed += 1
            else:
                rel_path = html_file.relative_to(DOCS)
                print(f"  {rel_path}: no fixes needed")
        
        except Exception as e:
            rel_path = html_file.relative_to(DOCS)
            print(f"⚠️  Error processing {rel_path}: {e}")
            continue
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {files_processed}/{len(html_files)}")
    print(f"   Total fixes: {fixes_made}")
    
    if files_processed > 0:
        print(f"\n✅ Preview ready in {PREVIEW}/")
        print("   Run supersonic_promote_preview.py to apply fixes")
        return 0
    else:
        print("\nℹ️  No fixes needed")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
