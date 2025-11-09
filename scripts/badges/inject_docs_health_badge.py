#!/usr/bin/env python3
"""
Inject a compact Docs Health badge into the README top badge row.

Rules:
- If a SONICBUILDER BADGES block exists, append the badge inside it.
- Else, if README starts with '# Title' and then a badge line, extend that line.
- Else, insert a new one-line badge row under the H1.
"""

import re, pathlib, os

OWNER = os.getenv("OWNER", "m9dswyptrn-web")
REPO  = os.getenv("REPO",  "SonicBuilder")

BADGE = f'![Docs Health](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/{OWNER}/{REPO}/HEAD/docs/badges/docs_health.json)'

readme = pathlib.Path("README.md")
text = readme.read_text(encoding="utf-8") if readme.exists() else "# SonicBuilder\n\n"

start = "<!-- SONICBUILDER:BADGES:START -->"
end   = "<!-- SONICBUILDER:BADGES:END -->"

changed = False

if start in text and end in text:
    # Append inside block if not present
    block = re.search(start + r"([\s\S]*?)" + end, text)
    if block and BADGE not in block.group(0):
        new_block = block.group(0).replace(end, " " + BADGE + "\n" + end)
        text = text.replace(block.group(0), new_block)
        changed = True
else:
    # Find H1, then a badge row (line with ](http or ![ )
    lines = text.splitlines()
    try:
        if lines and lines[0].startswith("# "):
            # search first 10 lines for badges
            inserted = False
            for i in range(1, min(len(lines), 10)):
                if ("![" in lines[i] and "](" in lines[i]) or ("shields.io" in lines[i]):
                    if BADGE not in lines[i]:
                        lines[i] = lines[i].strip() + " " + BADGE
                        inserted = True
                        changed = True
                    break
            if not inserted:
                # insert new line after H1
                lines.insert(1, BADGE)
                changed = True
            text = "\n".join(lines)
    except Exception:
        pass

if changed:
    readme.write_text(text, encoding="utf-8")
    print("README updated with mini Docs Health badge.")
else:
    print("No change (badge already present or README structure not matched).")
