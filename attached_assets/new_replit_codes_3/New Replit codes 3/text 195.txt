#!/usr/bin/env python3
# live_artifacts_bootstrap.py — add a “Live Artifacts & Releases” panel to MkDocs

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

ARTIFACTS_MD = """# Live Artifacts & Releases

Below are the **latest Releases** and recent **CI Artifacts** for this project.

> **Note:** GitHub may require you to be logged in to download CI artifacts from Actions. Releases are public.

<div class="cards" id="sb-releases"></div>
<div class="cards" id="sb-artifacts"></div>

<script>
  window.SonicDocs = Object.assign({}, window.SonicDocs || {}, {
    owner: "{{OWNER}}",
    repo: "{{REPO}}",
    // OPTIONAL: provide a GitHub token to enable direct artifact downloads.
    // token: "ghp_xxx"
  });
</script>
"""

ARTIFACTS_JS = r"""/* docs/assets/js/artifacts.js
 * Renders latest Releases and recent Actions Artifacts into #sb-releases and #sb-artifacts.
 * Works unauthenticated for listing; direct artifact downloads may require auth.
 */
(function () {
  const cfg = (window.SonicDocs || {});
  const OWNER = cfg.owner || "OWNER";
  const REPO  = cfg.repo  || "REPO";
  const TOKEN = cfg.token || null;

  const $ = (sel) => document.querySelector(sel);
  const elRel = $("#sb-releases");
  const elArt = $("#sb-artifacts");

  const GH = "https://api.github.com";
  const headers = TOKEN ? { Authorization: "Bearer " + TOKEN, Accept: "application/vnd.github+json" }
                        : { Accept: "application/vnd.github+json" };

  async function jget(url) {
    const r = await fetch(url, { headers });
    if (!r.ok) throw new Error(url + " → " + r.status);
    return await r.json();
  }

  function card(href, title, subtitle, right=null) {
    const a = document.createElement("a");
    a.className = "card";
    a.href = href; a.target = "_blank"; a.rel = "noopener";
    a.innerHTML = `<strong>${title}</strong><span class="muted">${subtitle}</span>` + (right ? `<span class="right">${right}</span>` : "");
    return a;
  }
  function fmtBytes(n) {
    if (n == null) return "";
    const units = ["B","KB","MB","GB","TB"];
    let i=0, v=n;
    while (v>=1024 && i<units.length-1) { v/=1024; i++; }
    return v.toFixed(v>=10?0:1)+" "+units[i];
  }
  function timeAgo(iso) {
    if (!iso) return "";
    const then = new Date(iso).getTime();
    const now  = Date.now();
    const s = Math.max(1, Math.floor((now-then)/1000));
    const dict = [[31536000,"y"],[2592000,"mo"],[604800,"w"],[86400,"d"],[3600,"h"],[60,"m"],[1,"s"]];
    for (const [sec, label] of dict) if (s >= sec) return Math.floor(s/sec)+label+" ago";
    return "just now";
  }

  async function renderReleases() {
    if (!elRel) return;
    elRel.innerHTML = "";
    try {
      const releases = await jget(`${GH}/repos/${OWNER}/${REPO}/releases?per_page=5`);
      if (!releases.length) {
        elRel.innerHTML = "<div class='muted'>No releases yet.</div>";
        return;
      }
      for (const rel of releases) {
        const title = rel.name || rel.tag_name;
        const href  = rel.html_url;
        const when  = timeAgo(rel.published_at || rel.created_at);
        const assets = (rel.assets || []).map(a => `${a.name} (${fmtBytes(a.size)})`).join(" · ");
        const sub = assets ? `${when} • ${assets}` : `${when}`;
        elRel.appendChild(card(href, "🔖 " + title, sub));
      }
    } catch (e) {
      elRel.innerHTML = "<div class='muted'>Failed to load releases.</div>";
      console.error(e);
    }
  }

  async function renderArtifacts() {
    if (!elArt) return;
    elArt.innerHTML = "";
    try {
      // List artifacts (newest first)
      const arts = await jget(`${GH}/repos/${OWNER}/${REPO}/actions/artifacts?per_page=30`);
      if (!arts.artifacts || !arts.artifacts.length) {
        elArt.innerHTML = "<div class='muted'>No recent artifacts.</div>";
        return;
      }
      // Show a few non-expired, highlight familiar names
      const namesOrder = ["static-vendor","docs-pdfs"];
      const keep = arts.artifacts
        .filter(a => !a.expired)
        .sort((a,b) => {
          const ai = namesOrder.indexOf(a.name); const bi = namesOrder.indexOf(b.name);
          return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
        })
        .slice(0, 10);

      // Map workflow_run.id → html_url for nicer links
      const runIds = Array.from(new Set(keep.map(a => a.workflow_run && a.workflow_run.id).filter(Boolean)));
      const runHtml = {};
      if (runIds.length) {
        // We can’t bulk fetch; instead, build the web URL pattern:
        // https://github.com/OWNER/REPO/actions/runs/<run_id>
        for (const id of runIds) runHtml[id] = `https://github.com/${OWNER}/${REPO}/actions/runs/${id}`;
      }

      for (const a of keep) {
        const size = fmtBytes(a.size_in_bytes);
        const when = timeAgo(a.created_at);
        const label = `${a.name} • ${size} • ${when}`;
        // Artifact direct URL requires auth; link to the workflow run instead:
        const href = (a.workflow_run && runHtml[a.workflow_run.id]) || `https://github.com/${OWNER}/${REPO}/actions`;
        const suffix = TOKEN ? "download" : "open run";
        elArt.appendChild(card(href, "📦 " + a.name, label, suffix));
      }
    } catch (e) {
      elArt.innerHTML = "<div class='muted'>Failed to load artifacts.</div>";
      console.error(e);
    }
  }

  // Minimal styles if theme lacks .cards/.card
  const style = document.createElement("style");
  style.textContent = `
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:.8rem;margin:.8rem 0}
  .card{display:block;background:var(--md-default-bg-color, #11141a);border:1px solid var(--md-default-fg-color--lightest, #2a3340);
        padding:1rem;border-radius:10px;color:inherit;text-decoration:none;position:relative}
  .card:hover{border-color:#3a4658;box-shadow:0 10px 30px rgba(0,0,0,.25)}
  .card .muted{opacity:.75;display:block;margin-top:.35rem}
  .card .right{position:absolute;right:.9rem;top:.9rem;opacity:.8;font-size:.9rem}
  `;
  document.head.appendChild(style);

  renderReleases();
  renderArtifacts();
})();
"""

CONFIG_JS = r"""/* docs/assets/js/config.js
 * Optional: set window.SonicDocs.token = "ghp_xxx" to allow direct artifact downloads.
 * CAUTION: Publicly exposing tokens is unsafe. Prefer leaving this file empty.
 */
window.SonicDocs = window.SonicDocs || {};
// window.SonicDocs.token = "ghp_xxx";
"""

def patch_mkdocs():
    mk = ROOT / "mkdocs.yml"
    if not mk.exists():
        print("! mkdocs.yml not found; skipping auto-patch (you can add entries manually).")
        return

    text = mk.read_text(encoding="utf-8")

    # Add nav entry if missing
    if "devops/artifacts.md" not in text:
        text = re.sub(r"(?ms)nav:\s*\n", "nav:\n  - DevOps:\n      - Live Artifacts: devops/artifacts.md\n", text, count=1) \
               if "DevOps:" not in text else text.replace("  - DevOps:\n", "  - DevOps:\n      - Live Artifacts: devops/artifacts.md\n", 1)

    # Add extra_javascript entries
    if "extra_javascript:" not in text:
        text += "\nextra_javascript:\n  - docs/assets/js/config.js\n  - docs/assets/js/artifacts.js\n"
    else:
        if "docs/assets/js/artifacts.js" not in text:
            text = text.replace("extra_javascript:\n", "extra_javascript:\n  - docs/assets/js/config.js\n  - docs/assets/js/artifacts.js\n")

    mk.write_text(text, encoding="utf-8")
    print("→ patched mkdocs.yml (nav + extra_javascript)")

def main():
    owner = os.environ.get("GITHUB_OWNER", "OWNER")
    repo  = os.environ.get("GITHUB_REPO", "REPO")

    # Write page
    (ROOT / "docs" / "devops").mkdir(parents=True, exist_ok=True)
    md = ARTIFACTS_MD.replace("{{OWNER}}", owner).replace("{{REPO}}", repo)
    (ROOT / "docs" / "devops" / "artifacts.md").write_text(md, encoding="utf-8")
    print("→ wrote docs/devops/artifacts.md")

    # Write JS
    (ROOT / "docs" / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs" / "assets" / "js" / "artifacts.js").write_text(ARTIFACTS_JS, encoding="utf-8")
    print("→ wrote docs/assets/js/artifacts.js")
    (ROOT / "docs" / "assets" / "js" / "config.js").write_text(CONFIG_JS, encoding="utf-8")
    print("→ wrote docs/assets/js/config.js (optional token placeholder)")

    # Patch mkdocs.yml
    patch_mkdocs()

    print("\n✅ Live Artifacts panel installed.")
    print("Next:")
    print("  1) Ensure mkdocs.yml contains your actual owner/repo, or set envs before building:")
    print('       export GITHUB_OWNER="YourUser"; export GITHUB_REPO="SonicBuilder"')
    print("  2) Commit & push. The Docs workflow will rebuild and the panel will populate.")
    print("  3) For public repos, Releases are downloadable; Actions artifacts may require login.")
    print("  4) (Optional) If you really need direct artifact downloads, add a token in docs/assets/js/config.js (not recommended for public repos).")

if __name__ == "__main__":
    main()