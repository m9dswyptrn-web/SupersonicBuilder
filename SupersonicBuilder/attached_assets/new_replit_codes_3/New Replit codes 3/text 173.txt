#!/usr/bin/env python3
# pages_bootstrap.py — add a minimal GitHub Pages site + workflow

import os, stat, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def write(path: Path, content: str, exe=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if exe:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"→ wrote {path}")

INDEX_HTML = """<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SonicBuilder • Supersonic</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
<header class="container">
  <h1>⚡ SonicBuilder</h1>
  <p class="muted">Android head unit project • DSP configs • wiring PDFs • ZIP packaging</p>
  <nav>
    <a href="#quickstart">Quickstart</a>
    <a href="#features">Features</a>
    <a href="#downloads">Downloads</a>
    <a href="https://github.com/OWNER/REPO" target="_blank" rel="noopener">GitHub ↗</a>
  </nav>
</header>

<main class="container">
<section id="quickstart">
  <h2>Quickstart</h2>
  <ol>
    <li><code>git clone https://github.com/OWNER/REPO</code></li>
    <li><code>cd REPO</code></li>
    <li><code>make vendor</code>  <span class="muted"># pulls PDF.js + JSZip</span></li>
    <li><code>make run</code>     <span class="muted"># dev server (fast cache)</span></li>
  </ol>
  <p class="tip">Tip: Set <code>CATALOG_TTL_HOURS</code> (dev ≈10m by default, prod 24h).</p>
</section>

<section id="features">
  <h2>Highlights</h2>
  <ul class="grid">
    <li>🎚️ DSP configs + wiring PDFs</li>
    <li>🧩 Diagram picker with PNG/PDF/ZIP export</li>
    <li>⏱️ Env-aware catalog cache (TTL + version)</li>
    <li>🌙 Theme toggle, settings modal, restart-last preview</li>
    <li>🚀 GitHub CI + Release (zip on tag)</li>
  </ul>
</section>

<section id="downloads">
  <h2>Downloads</h2>
  <p>Artifacts from CI appear on each commit in <em>Actions → artifacts</em>. Release bundles land on the <em>Releases</em> page when you push a tag like <code>v1.0.0</code>.</p>
  <div class="cards">
    <a class="card" href="https://github.com/OWNER/REPO/actions" target="_blank" rel="noopener">
      <strong>CI Artifacts</strong><span class="muted">static/vendor & docs</span>
    </a>
    <a class="card" href="https://github.com/OWNER/REPO/releases" target="_blank" rel="noopener">
      <strong>Releases</strong><span class="muted">SonicBuilder_&lt;tag&gt;.zip</span>
    </a>
  </div>
</section>

<section>
  <h2>Notes</h2>
  <ul>
    <li>This site is static documentation (no Flask backend here).</li>
    <li>Your runtime app still serves API + preview locally/hosted.</li>
  </ul>
</section>
</main>

<footer class="container muted small">
  <p>© SonicBuilder. Built with ❤️ and supersonic caffeine.</p>
</footer>
</body>
</html>
"""

STYLES = """*{box-sizing:border-box}html,body{margin:0;padding:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Helvetica,Arial,sans-serif}
:root{--bg:#0b0f14;--fg:#e5e7eb;--muted:#9aa3af;--card:#121822;--border:#1f2937;--link:#8efcff}
body{background:var(--bg);color:var(--fg)}
.container{max-width:1000px;margin:0 auto;padding:1.25rem}
header h1{margin:.25rem 0 0}
header .muted{margin:.25rem 0 1rem;color:var(--muted)}
nav a{margin-right:.9rem;color:var(--link);text-decoration:none}
nav a:hover{text-decoration:underline}
h2{margin-top:2rem}
.muted{color:var(--muted)}
.small{font-size:.9rem}
.tip{background:var(--card);border:1px solid var(--border);padding:.6rem .8rem;border-radius:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:.6rem;padding-left:1rem}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:.8rem}
.card{display:block;background:var(--card);border:1px solid var(--border);padding:1rem;border-radius:10px;color:var(--fg);text-decoration:none}
.card:hover{border-color:#334155;box-shadow:0 10px 30px rgba(0,0,0,.25)}
code{background:#0e1420;border:1px solid #18202e;padding:.1rem .35rem;border-radius:6px}
ol{padding-left:1.25rem}
"""

PAGES_YML = """name: Deploy Docs (GitHub Pages)

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
      - '.github/workflows/pages.yml'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: 'pages'
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Prepare site
        run: |
          mkdir -p ./dist
          cp -R docs/* dist/
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
"""

def main():
    # Write docs
    write(ROOT / "docs" / "index.html", INDEX_HTML)
    write(ROOT / "docs" / "styles.css", STYLES)

    # Write workflow
    write(ROOT / ".github" / "workflows" / "pages.yml", PAGES_YML)

    print("\n✅ Pages bootstrap complete.")
    print("Next:")
    print("  1) Search/replace OWNER/REPO in docs/index.html with your GitHub owner & repo.")
    print("  2) Commit & push to main. The 'Deploy Docs (GitHub Pages)' workflow will publish.")
    print("  3) First time only: Settings → Pages → Source = GitHub Actions (it auto-detects).")

if __name__ == '__main__':
    main()