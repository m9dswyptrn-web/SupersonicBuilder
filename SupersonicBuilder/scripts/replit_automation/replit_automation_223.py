#!/usr/bin/env python3
# integrate_version_badge.py — merge the dynamic GitHub release badge into your MkDocs site
import os, re
from pathlib import Path

ROOT  = Path(__file__).resolve().parent
OWNER = os.environ.get("GITHUB_OWNER", "OWNER")
REPO  = os.environ.get("GITHUB_REPO", "REPO")

JS = r"""/* docs/assets/js/version_badge.js
 * Injects a floating badge with the latest GitHub release tag.
 * Works unauthenticated for public repos. Uses /releases/latest, falls back to /tags.
 */
(function () {
  const OWNER = "%OWNER%";
  const REPO  = "%REPO%";
  const releasesURL = `https://api.github.com/repos/${OWNER}/${REPO}/releases/latest`;
  const tagsURL     = `https://api.github.com/repos/${OWNER}/${REPO}/tags?per_page=1`;
  const relPage     = `https://github.com/${OWNER}/${REPO}/releases`;

  function insertBadge(text, href) {
    if (!text) return;
    const id = "sb-version-badge";
    if (document.getElementById(id)) return;
    const a = document.createElement("a");
    a.id = id;
    a.href = href || relPage;
    a.target = "_blank";
    a.rel = "noopener";
    a.setAttribute("aria-label", "Latest version");
    a.textContent = text;
    document.body.appendChild(a);
  }

  async function jget(url) {
    const r = await fetch(url, { headers: { "Accept": "application/vnd.github+json" }});
    if (!r.ok) throw new Error(url + " -> " + r.status);
    return await r.json();
  }

  async function main() {
    try {
      const rel = await jget(releasesURL);
      const tag = rel && (rel.tag_name || rel.name);
      insertBadge(tag || "latest", rel && rel.html_url || relPage);
    } catch (e) {
      // Fallback to tags if no releases yet
      try {
        const tags = await jget(tagsURL);
        const tag = (tags && tags.length && tags[0].name) || "latest";
        insertBadge(tag, relPage);
      } catch (e2) {
        insertBadge("latest", relPage);
      }
    }
  }

  if (document.readyState !== "loading") main();
  else document.addEventListener("DOMContentLoaded", main);
})();
""".replace("%OWNER%", OWNER).replace("%REPO%", REPO)

CSS = r"""/* docs/assets/css/version_badge.css */
:root{
  --sb-badge-bg:   #0b1220;
  --sb-badge-fg:   #dff7ff;
  --sb-badge-ring: #2a3b54;
}
#sb-version-badge{
  position: fixed;
  right: 14px;
  bottom: 14px;
  z-index: 9999;
  font: 600 12px/1.1 ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
  padding: 8px 10px;
  color: var(--sb-badge-fg);
  background: var(--sb-badge-bg);
  border: 1px solid var(--sb-badge-ring);
  border-radius: 10px;
  text-decoration: none;
  box-shadow: 0 10px 30px rgba(0,0,0,.25);
  opacity: .92;
  transition: transform .15s ease, opacity .15s ease, box-shadow .15s ease;
}
#sb-version-badge:hover{
  opacity: 1;
  transform: translateY(-1px);
  box-shadow: 0 14px 40px rgba(0,0,0,.35);
}
@media (max-width: 700px){
  #sb-version-badge{ bottom: 10px; right: 10px; padding: 7px 9px; }
}
"""

def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"→ wrote {path}")

def patch_mkdocs():
    mk = ROOT / "mkdocs.yml"
    if not mk.exists():
        print("! mkdocs.yml not found — add manually:\n  extra_javascript: [ docs/assets/js/version_badge.js ]\n  extra_css: [ docs/assets/css/version_badge.css ]")
        return
    text = mk.read_text(encoding="utf-8")

    # Ensure extra_javascript includes our JS (keep existing entries)
    if "extra_javascript:" not in text:
        text += "\nextra_javascript:\n  - docs/assets/js/version_badge.js\n"
    elif "docs/assets/js/version_badge.js" not in text:
        text = text.replace("extra_javascript:\n", "extra_javascript:\n  - docs/assets/js/version_badge.js\n")

    # Ensure extra_css includes our CSS
    if "extra_css:" not in text:
        text += "\nextra_css:\n  - docs/assets/css/version_badge.css\n"
    elif "docs/assets/css/version_badge.css" not in text:
        text = text.replace("extra_css:\n", "extra_css:\n  - docs/assets/css/version_badge.css\n")

    mk.write_text(text, encoding="utf-8")
    print("→ patched mkdocs.yml (added version badge JS/CSS)")

def main():
    write(ROOT / "docs" / "assets" / "js" / "version_badge.js", JS)
    write(ROOT / "docs" / "assets" / "css" / "version_badge.css", CSS)
    patch_mkdocs()
    print("\n✅ Version badge merged. Push and your docs will show the latest tag in the bottom-right.")

if __name__ == "__main__":
    main()