#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import os

STATE = (os.getenv("STATE","success") or "success").lower()

LKG_TAG        = os.getenv("LKG_TAG", "") or ""
LKG_RELEASE_URL= os.getenv("LKG_RELEASE_URL", "") or ""
LKG_PAGES_URL  = os.getenv("LKG_PAGES_URL", "") or ""

MAP = {
  "success":   ("assets/led_online.gif", "SYSTEM ONLINE",   "assets/system_online.gif"),
  "failure":   ("assets/led_fail.gif",   "SYSTEM FAILURE",  "assets/system_online.gif"),
  "cancelled": ("assets/led_warn.gif",   "SYSTEM STANDBY",  "assets/system_online.gif"),
}
led_img, label, hero = MAP.get(STATE, MAP["success"])
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

recovery_html = ""
if LKG_TAG:
    pages_link = f'<a href="{LKG_PAGES_URL}" target="_blank">Pages</a>' if LKG_PAGES_URL else ""
    rel_link   = f'<a href="{LKG_RELEASE_URL}" target="_blank">Release</a>' if LKG_RELEASE_URL else ""
    sep = " · " if (pages_link and rel_link) else ""
    links = f"{pages_link}{sep}{rel_link}"
    recovery_html = f'\n<sub>Last known good: <b>{LKG_TAG}</b> — {links}</sub>\n'

out = Path("docs/status_banner.md")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(
f"""<div align="center">

<img src="docs/{hero}" height="28" alt="{label}"/><br/>
<img src="docs/{led_img}" width="14" alt="LED"> <b>{label}</b><br/>
<sub>Last pipeline: <code>{ts}</code></sub>{recovery_html}

</div>
""", encoding="utf-8")
print(f"[OK] Wrote {out} ({STATE}) with LKG={LKG_TAG or 'n/a'}")
