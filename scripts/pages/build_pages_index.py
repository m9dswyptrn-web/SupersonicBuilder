#!/usr/bin/env python3
import os, time, pathlib, html, re

# We're running from public/ directory
ROOT = pathlib.Path(".").resolve()
DL = ROOT / "downloads"
INDEX = ROOT / "index.html"

def list_pdfs(n=5):
    """List up to N most recent PDFs"""
    if not DL.exists(): 
        return []
    files = [p for p in DL.glob("*.pdf") if p.is_file() and p.name != "latest.pdf"]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for p in files[:n]:
        size = p.stat().st_size
        human = f"{size/1024/1024:.1f} MB"
        ts = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(p.stat().st_mtime))
        out.append({
            "name": p.name,
            "href": f"./downloads/{p.name}",
            "size": human,
            "ts": ts,
        })
    return out

def ensure_index():
    """Build or update index.html with dynamic content"""
    if INDEX.exists():
        html_in = INDEX.read_text(encoding="utf-8", errors="ignore")
    else:
        # Create minimal dark-themed index
        html_in = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SonicBuilder Documentation</title>
<style>
  :root { color-scheme: dark light; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    background: #0b0f14;
    color: #cfd7e3;
    line-height: 1.6;
  }
  h1 { color: #58a6ff; }
  h2 { color: #79c0ff; margin-top: 2rem; }
  a { color: #58a6ff; text-decoration: none; }
  a:hover { text-decoration: underline; }
  ul { list-style: none; padding-left: 0; }
  li { padding: 0.5rem 0; border-bottom: 1px solid #21262d; }
  footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #21262d; color: #8b949e; }
  .badge { margin: 1rem 0; }
</style>
</head>
<body>
<h1>🚗 SonicBuilder Documentation</h1>
<p>Professional PDF manuals for 2014 Chevy Sonic LTZ Android head unit installation.</p>

<!--BEGIN:LATEST_BADGE--><!--END:LATEST_BADGE-->

<!--BEGIN:RECENT_PDFS--><!--END:RECENT_PDFS-->

<!--BEGIN:FOOTER_STAMP--><!--END:FOOTER_STAMP-->

</body>
</html>"""

    # Build latest badge
    latest_href = "./downloads/latest.pdf"
    badge = f"""
<div class="badge">
<a href='{latest_href}'>
<img alt='Latest Download' src='https://img.shields.io/badge/download-latest.pdf-2b6fff?style=for-the-badge&logo=adobeacrobatreader&logoColor=white'>
</a>
</div>"""

    # Build recent PDFs list
    items = list_pdfs(5)
    block = ["\n<section id='recent-pdfs'>", "<h2>📄 Recent PDFs</h2>", "<ul>"]
    if items:
        for it in items:
            block.append(f"<li><a href='{html.escape(it['href'])}'>{html.escape(it['name'])}</a> <span style='color:#8b949e'>— {it['size']} — {it['ts']}</span></li>")
    else:
        block.append("<li style='color:#8b949e'>No PDFs found yet.</li>")
    block.append("</ul>")
    block.append("</section>")

    # Build footer stamp
    built = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    version = os.getenv('GITHUB_REF_NAME', 'dev')
    commit = os.getenv('GITHUB_SHA', 'unknown')[:7]
    footer = f"""
<footer>
<p><small>Version: <strong>{html.escape(version)}</strong> • Commit: <code>{html.escape(commit)}</code> • Built: {built} • <a href='{latest_href}'>latest.pdf</a></small></p>
</footer>"""

    # Helper: replace content between markers
    def replace_section(name, content, text):
        start = f"<!--BEGIN:{name}-->"
        end = f"<!--END:{name}-->"
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
        if pattern.search(text):
            return pattern.sub(start + content + end, text)
        else:
            # If markers don't exist, append at end (before </body> or </html>)
            if "</body>" in text:
                return text.replace("</body>", start + content + end + "\n</body>")
            elif "</html>" in text:
                return text.replace("</html>", start + content + end + "\n</html>")
            else:
                return text + start + content + end

    # Inject all sections
    html_out = html_in
    html_out = replace_section("LATEST_BADGE", badge, html_out)
    html_out = replace_section("RECENT_PDFS", "\n".join(block), html_out)
    html_out = replace_section("FOOTER_STAMP", footer, html_out)

    INDEX.write_text(html_out, encoding="utf-8")
    print(f"✅ {INDEX.name} updated with latest badge, recent PDFs list, and footer stamp")

if __name__ == "__main__":
    ensure_index()
