#!/usr/bin/env python3
"""
Extract and install command snippets from uploaded text files
"""
import os
from pathlib import Path

TEXT_DIR = Path("uploaded_content/text_files")
UTIL_DIR = Path("scripts/util")
UTIL_DIR.mkdir(parents=True, exist_ok=True)

# Command snippet files (single-line executables)
SNIPPET_FILES = [
    "text 2.txt", "text 3.txt", "text 4.txt", "text 5.txt",
    "text 6.txt", "text 7.txt", "text 8.txt", "text 9.txt",
    "text 14.txt", "text 57.txt", "text 58.txt", "text 59.txt"
]

snippets = {}
for fname in SNIPPET_FILES:
    fpath = TEXT_DIR / fname
    if fpath.exists():
        content = fpath.read_text().strip()
        if content and len(content.splitlines()) <= 3:
            # Create sanitized filename
            num = fname.replace("text ", "").replace(".txt", "")
            snippets[f"snippet_{num}"] = content

# Generate executable scripts
for name, cmd in snippets.items():
    script_path = UTIL_DIR / f"{name}.sh"
    script_path.write_text(f"#!/bin/bash\n# Auto-generated from uploaded snippets\n{cmd}\n")
    os.chmod(script_path, 0o755)
    print(f"✅ Created: {script_path}")

print(f"\n📊 Total snippets installed: {len(snippets)}")
