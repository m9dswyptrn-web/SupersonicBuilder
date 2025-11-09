#!/usr/bin/env python3
# Wires a MkDocs footer + build metadata + JS that shows:
#  - last docs build time (UTC)
#  - commit short SHA
#  - latest GitHub release tag (live)
import re, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MK = ROOT / "mkdocs.yml"
FOOTER = ROOT / "docs" / "overrides" / "partials" / "footer.html"
JS = ROOT / "docs" / "assets" / "js" / "footer_meta.js"
BUILD_META = ROOT / ".github" / "scripts" / "write_docs_build_meta.py"
DOCS_WF = ROOT / ".github" / "workflows" / "docs-mkdocs.yml"

FOOTER_HTML = """{% set repo = config.repo_url | replace('https://github.com/','') %}
{% set page_footer %}
  <div class="md-footer-meta__inner">
    <div class="md-footer-copyright">
      <span>© {{ config.site_name }}</span>
    </div>
    <div class="md-footer-social">
      <span id="sb-footer-build" class="mdx-build">
        <strong>Build:</strong> <span id="sb-build-time">…</span>
        · <strong>Commit:</strong> <span id="sb-build-sha">…</span>
        · <strong>Latest:</strong> <span id="sb-latest-tag">…</span>
      </span>
    </div>
  </div>
{% endset %}

{% block footer %}
  {{ super() }}
  <div class="md-footer-meta md-typeset">
    {{ page_footer }}
  </div>
{% endblock %}
"""

FOOTER_JS = r"""/* docs/assets/js/footer_meta.js
 * Populates footer with docs build meta + latest release tag.
 * Build meta is written by CI to docs/assets/build.json.
 */
(function(){
  const OWNER_REPO = (document.querySelector('meta[name="repo"]')?.content || (window?.location?.host || '')).replace(/^https?:\/\/github\.com\//,'');
  const buildURL = new URL(document.baseURI).origin + (document.baseURI.includes('/site/') ? '/assets/build.json' : '/assets/build.json');

  function set(id, text){ const el = document.getElementById(id); if (el) el.textContent = text; }

  // Build meta (time + sha)
  fetch('assets/build.json', {cache: 'no-store'}).then(r => r.ok ? r.json() : null).then(j => {
    if (j){
      set('sb-build-time', (j.build_time_utc || '').replace('T',' ').replace('Z',' UTC'));
      set('sb-build-sha', (j.commit_short || '').slice(0,7));
    } else {
      set('sb-build-time', 'n/a');
      set('sb-build-sha', 'n/a');
    }
  }).catch(()=>{ set('sb-build-time','n/a'); set('sb-build-sha','n/a'); });

  // Latest release tag (live)
  (async ()=>{
    try{
      const repo = document.querySelector('a.md-source')?.getAttribute('href')?.replace('https://github.com/','') || OWNER_REPO;
      if (!repo) throw new Error('no repo');
      const url = `https://api.github.com/repos/${repo}/releases/latest`;
      const r = await fetch(url, { headers: { "Accept": "application/vnd.github+json" }});
      if (!r.ok) throw new Error('no latest');
      const j = await r.json();
      const tag = j.tag_name || j.name || 'latest';
      set('sb-latest-tag', tag);
    }catch(e){
      // fall back to tags
      try{
        const repo = document.querySelector('a.md-source')?.getAttribute('href')?.replace('https://github.com/','') || OWNER_REPO;
        const r = await fetch(`https://api.github.com/repos/${repo}/tags?per_page=1`);
        const tags = await r.json();
        set('sb-latest-tag', (tags && tags[0] && tags[0].name) || 'latest');
      }catch(e2){
        set('sb-latest-tag','latest');
      }
    }
  })();
})();
"""

WRITE_META = r"""# .github/scripts/write_docs_build_meta.py
# Writes docs/assets/build.json with build_time_utc + commit info (called from Docs workflow)
import json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "docs" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()

commit = os.environ.get("GITHUB_SHA") or git("rev-parse","HEAD")
short  = commit[:7]
ref    = os.environ.get("GITHUB_REF_NAME","")

payload = {
  "build_time_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "commit": commit,
  "commit_short": short,
  "ref": ref,
}

(ASSETS / "build.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print("→ wrote docs/assets/build.json")
"""

def patch_mkdocs():
    if not MK.exists():
        print("! mkdocs.yml not found; create it first.")
        return
    t = MK.read_text(encoding="utf-8")

    # ensure custom_dir for overrides
    if "theme:" not in t:
        t += "\n\ntheme:\n  name: material\n"
    if "custom_dir:" not in t:
        t = re.sub(r"(?m)^theme:\s*\n", "theme:\n  custom_dir: docs/overrides\n", t, count=1)

    # ensure extra_javascript includes footer_meta.js (idempotent)
    if "extra_javascript:" in t and "docs/assets/js/footer_meta.js" not in t:
        t = t.replace("extra_javascript:\n", "extra_javascript:\n  - docs/assets/js/footer_meta.js\n")
    elif "extra_javascript:" not in t:
        t += "\nextra_javascript:\n  - docs/assets/js/footer_meta.js\n"

    MK.write_text(t, encoding="utf-8")
    print("→ patched mkdocs.yml (custom_dir + footer_meta.js)")

def patch_docs_workflow():
    if not DOCS_WF.exists():
        print("! docs-mkdocs.yml not found; skipping workflow patch (create Docs workflow first).")
        return
    w = DOCS_WF.read_text(encoding="utf-8")
    if "write_docs_build_meta.py" in w:
        print("→ Docs workflow already writes build.json")
        return
    # Insert a step before "Build"
    w = w.replace(
        "      - name: Install MkDocs & plugins\n        run: |\n          python -m pip install --upgrade pip\n          pip install -r requirements.docs.txt\n      - name: Build",
        "      - name: Install MkDocs & plugins\n        run: |\n          python -m pip install --upgrade pip\n          pip install -r requirements.docs.txt\n      - name: Write build meta (time/commit)\n        run: |\n          python .github/scripts/write_docs_build_meta.py\n      - name: Build"
    )
    DOCS_WF.write_text(w, encoding="utf-8")
    print("→ patched Docs workflow to generate docs/assets/build.json")

def main():
    FOOTER.parent.mkdir(parents=True, exist_ok=True)
    FOOTER.write_text(FOOTER_HTML, encoding="utf-8")
    print("→ wrote", FOOTER)

    JS.parent.mkdir(parents=True, exist_ok=True)
    JS.write_text(FOOTER_JS, encoding="utf-8")
    print("→ wrote", JS)

    BUILD_META.parent.mkdir(parents=True, exist_ok=True)
    BUILD_META.write_text(WRITE_META, encoding="utf-8")
    print("→ wrote", BUILD_META)

    patch_mkdocs()
    patch_docs_workflow()
    print("\n✅ Docs footer wired. On the next Docs workflow run, the footer will show build time, commit, and latest tag.")

if __name__ == "__main__":
    main()