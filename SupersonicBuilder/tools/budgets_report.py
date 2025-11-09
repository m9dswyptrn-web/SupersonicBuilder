#!/usr/bin/env python3
from __future__ import annotations
import os, json, fnmatch, urllib.request, urllib.error, html, datetime, base64
from pathlib import Path
from glob import glob

ROOT = Path(__file__).resolve().parents[1]
BUDGETS = ROOT / ".github" / "artifact_budgets.json"
DOCS   = ROOT / "docs"
OUT    = DOCS / "budgets.html"
SPARK = DOCS / "budgets_sparkline.svg"
ASSET_HISTORY = DOCS / "budgets_asset_history.json"
HIST_TAGS_JSON = DOCS / "budgets_history.json"

def human(n:int)->str:
    u=["B","KB","MB","GB","TB"]; i=0; f=float(n)
    while f>=1024 and i<len(u)-1: f/=1024; i+=1
    return f"{f:.2f} "+u[i]

def expand_globs(globs):
    inc, exc = [], []
    for g in globs:
        g = g.strip()
        if not g: continue
        (exc if g.startswith("!") else inc).append(g[1:] if g.startswith("!") else g)
    files=set()
    for p in inc:
        for m in glob(p, recursive=True):
            q=Path(m)
            if q.is_file(): files.add(q.resolve())
    ex=set()
    for p in exc:
        for m in glob(p, recursive=True):
            q=Path(m)
            if q.is_file(): ex.add(q.resolve())
    return sorted([p for p in files if p not in ex])

def load_json(p:Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def gh_get(url:str, token:str):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept":"application/vnd.github+json",
        "User-Agent":"budgets-report"
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def find_prev_release(owner_repo:str, token:str, current_tag:str|None):
    rels = gh_get(f"https://api.github.com/repos/{owner_repo}/releases?per_page=100", token)
    rels.sort(key=lambda r:r.get("created_at",""), reverse=True)
    seen = False
    if current_tag:
        for r in rels:
            if r.get("tag_name")==current_tag:
                seen=True; continue
            if seen and not r.get("draft") and not r.get("prerelease"):
                return r
    for r in rels:
        if not r.get("draft") and not r.get("prerelease"):
            return r
    return None

def match_budget(budgets:list[dict], name:str):
    exact = [b for b in budgets if b.get("pattern")==name]
    if exact: return exact[0]
    for b in budgets:
        if fnmatch.fnmatch(name, b.get("pattern","*")):
            return b
    return {}

def color_status(ok_size, ok_delta):
    if ok_size and ok_delta: return "var(--ok)", "🟢 OK"
    if not ok_size and not ok_delta: return "var(--bad)", "🔴 over size & delta"
    if not ok_size: return "var(--warn)", "🟠 over size cap"
    return "var(--warn)", "🟡 over delta cap"

def build_inline_spark(points: list[int], labels: list[str] | None = None, width=160, height=36, pad=4) -> str:
    """Render a tiny sparkline with per-point <title> tooltips.
    points: list of sizes in BYTES, oldest -> newest.
    labels: parallel list of release tags (oldest -> newest); optional.
    """
    if not points:
        points = [0]
    n = len(points)
    if not labels:
        labels = [f"#{i+1}" for i in range(n)]
    else:
        # keep only the last N labels to match points length
        if len(labels) > n:
            labels = labels[-n:]
        elif len(labels) < n:
            # left-pad with blanks if labels shorter
            labels = ([""] * (n - len(labels))) + labels

    lo, hi = min(points), max(points)
    span = max(1, hi - lo)

    xs = [pad + (width - 2*pad) * (i / max(1, n-1)) for i in range(n)]
    ys = [height - pad - (p - lo) * (height - 2*pad) / span for p in points]
    path_d = " ".join([f"{'M' if i==0 else 'L'}{xs[i]:.2f},{ys[i]:.2f}" for i in range(n)])
    area_d = f"M{xs[0]:.2f},{height-pad:.2f} " + " ".join([f"L{xs[i]:.2f},{ys[i]:.2f}" for i in range(n)]) + f" L{xs[-1]:.2f},{height-pad:.2f} Z"

    # Circles with per-point <title> tooltips
    circles = []
    for i,(x,y) in enumerate(zip(xs, ys)):
        size_txt = "not present" if points[i] == 0 else human(points[i])
        tag = labels[i] or f"#{i+1}"
        title = f"{tag} — {size_txt}"
        circles.append(
            f'<g><circle cx="{x:.2f}" cy="{y:.2f}" r="2.8" fill="#86c5ff" stroke="#e6eef8" stroke-width="1">'
            f'<title>{title}</title></circle></g>'
        )

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
  xmlns="http://www.w3.org/2000/svg" role="img" aria-label="artifact history">
  <defs>
    <linearGradient id="ga" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#4ea8ff" stop-opacity="0.36"/>
      <stop offset="100%" stop-color="#4ea8ff" stop-opacity="0.06"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="{width}" height="{height}" fill="transparent"/>
  <path d="{area_d}" fill="url(#ga)"/>
  <path d="{path_d}" fill="none" stroke="#86c5ff" stroke-width="2"/>
  {''.join(circles)}
</svg>'''
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img alt="history" src="data:image/svg+xml;base64,{encoded}" style="display:block;opacity:.95"/>'

def main():
    globs = os.getenv("ARTIFACT_GLOBS", "dist/**\nbuild/**\n**/*.zip\n**/*.tar.gz\n**/*.whl\n!**/node_modules/**\n!**/.venv/**\n!**/__pycache__/**").splitlines()
    repo  = os.getenv("GITHUB_REPOSITORY","")
    token = os.getenv("GITHUB_TOKEN","") or os.getenv("GH_TOKEN","")
    current_tag = os.getenv("VERSION","") or os.getenv("GITHUB_REF_NAME","")

    files = expand_globs(globs)
    artifacts = { p.name: p.stat().st_size for p in files }

    budgets = load_json(BUDGETS, [])
    prev_tag, prev_assets = "", {}
    if repo and token:
        try:
            prev = find_prev_release(repo, token, current_tag or None)
            if prev:
                prev_tag = prev.get("tag_name","")
                prev_assets = { a["name"]: int(a.get("size",0)) for a in prev.get("assets",[]) }
        except Exception:
            pass
    
    # Load per-asset history
    asset_hist = {}
    if ASSET_HISTORY.exists():
        try:
            asset_hist = json.loads(ASSET_HISTORY.read_text(encoding="utf-8"))
        except Exception:
            asset_hist = {}
    
    # Load tags (oldest→newest) from budgets_history.json for tooltips
    tags_order = []
    if HIST_TAGS_JSON.exists():
        try:
            tag_map = json.loads(HIST_TAGS_JSON.read_text(encoding="utf-8"))
            tags_order = list(tag_map.keys())
        except Exception:
            tags_order = []

    rows = []
    total = sum(artifacts.values())
    total_prev = sum(prev_assets.values()) if prev_assets else 0
    for name, size in sorted(artifacts.items()):
        b = match_budget(budgets, name)
        max_mb = float(b.get("max_mb", 9e9))
        max_delta_mb = float(b.get("max_delta_mb", 9e9))
        prev = prev_assets.get(name, 0)
        delta = size - prev
        ok_size = size <= max_mb*1024*1024
        ok_delta = abs(delta) <= max_delta_mb*1024*1024
        color, label = color_status(ok_size, ok_delta)
        # Build inline sparkline for this asset with tag labels
        hist_html = ""
        hist_series = asset_hist.get(name)
        if isinstance(hist_series, list) and len(hist_series) > 0:
            # Align labels with the series length (trim from right if tags list is longer)
            labels = tags_order[-len(hist_series):] if tags_order else None
            hist_html = build_inline_spark(hist_series, labels=labels, width=160, height=36)
        else:
            hist_html = '<span style="color:var(--muted)">—</span>'
        
        rows.append({
            "name": name,
            "size": size,
            "prev": prev,
            "delta": delta,
            "max_mb": None if max_mb>=9e9 else int(max_mb),
            "max_delta_mb": None if max_delta_mb>=9e9 else int(max_delta_mb),
            "color": color,
            "label": label,
            "history": hist_html
        })

    DOCS.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.utcnow().isoformat(timespec="seconds")+"Z"
    
    # Build sparkline card if exists
    spark_html = ""
    if SPARK.exists():
        history_count = os.getenv("HISTORY_COUNT", "20")
        spark_html = f'<div class="card" style="margin:16px 0;"><div class="kv"><div class="chip">Release totals (last {history_count})</div></div><img src="budgets_sparkline.svg" alt="Release size sparkline" style="width:100%;max-width:860px;border-radius:10px;border:1px solid var(--line)"/></div>'
    
    with OUT.open("w", encoding="utf-8") as f:
        f.write(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Artifact Budgets • {html.escape(current_tag or '(unreleased)')}</title>
<style>
:root {{
  --bg:#0b0f14; --panel:#121822; --ink:#e6eef8; --muted:#9db0c6;
  --ok:#1f8b4c; --warn:#d4a21f; --bad:#c53939; --chip:#1b2635; --line:#203044;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, Apple Color Emoji, Segoe UI Emoji;
}}
* {{ box-sizing:border-box }}
body {{ margin:0; background:var(--bg); color:var(--ink); }}
.wrap {{ max-width:1100px; margin:32px auto; padding:0 16px; }}
h1 {{ margin:0 0 12px; font-size:24px; }}
.meta {{ color:var(--muted); margin-bottom:18px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th, td {{ padding:10px 8px; border-bottom:1px solid var(--line); vertical-align:middle; }}
th {{ text-align:left; color:var(--muted); font-weight:600; }}
td.size, td.delta, td.prev, td.budget {{ text-align:right; font-variant-numeric: tabular-nums; }}
td.hist {{ width: 170px; }}
.badge {{ display:inline-block; padding:3px 8px; border-radius:999px; background:var(--chip); color:#fff; font-size:12px; }}
.status {{ font-weight:700; }}
tfoot td {{ color:var(--muted); font-weight:600; }}
.kv {{ display:flex; gap:8px; flex-wrap:wrap; margin:0 0 14px; }}
.kv .chip {{ background:var(--chip); padding:6px 10px; border-radius:999px; }}
a {{ color:#86c5ff; text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Artifact Budgets <span class="badge">{html.escape(current_tag or "Unreleased")}</span></h1>
  <div class="meta">Generated {html.escape(now)} · Repo: {html.escape(repo or "(local)")}{(" · Compared to "+html.escape(prev_tag)) if prev_tag else ""}</div>

  {spark_html}
  <div class="card">
    <div class="kv">
      <div class="chip">Current total: <b>{html.escape(human(total))}</b></div>
      <div class="chip">Previous total: <b>{html.escape(human(total_prev))}</b></div>
      <div class="chip">Δ total: <b>{'+' if total-total_prev>=0 else ''}{html.escape(human(abs(total-total_prev)))}</b></div>
    </div>

    <table>
      <thead>
        <tr>
          <th>File</th>
          <th class="size">Size</th>
          <th class="prev">Prev</th>
          <th class="delta">Δ</th>
          <th class="budget">Budget</th>
          <th class="budget">Δ Budget</th>
          <th>History</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
""")
        for r in rows:
            f.write(f"""        <tr>
          <td>{html.escape(r['name'])}</td>
          <td class="size">{html.escape(human(r['size']))}</td>
          <td class="prev">{html.escape(human(r['prev'])) if r['prev'] else "—"}</td>
          <td class="delta">{'+' if r['delta']>=0 else '-'}{html.escape(human(abs(r['delta'])))}{' ' if r['prev'] else ' (new)'}
          </td>
          <td class="budget">{(str(r['max_mb'])+' MB') if r['max_mb'] is not None else '∞'}</td>
          <td class="budget">{(str(r['max_delta_mb'])+' MB') if r['max_delta_mb'] is not None else '∞'}</td>
          <td class="hist">{r['history']}</td>
          <td class="status" style="color:{r['color']}">{r['label']}</td>
        </tr>
""")
        f.write("""      </tbody>
      <tfoot>
        <tr>
          <td>Total</td>
          <td class="size">{total}</td>
          <td class="prev">{total_prev}</td>
          <td class="delta">{delta}</td>
          <td class="budget">—</td>
          <td class="budget">—</td>
          <td class="hist">—</td>
          <td>—</td>
        </tr>
      </tfoot>
    </table>
  </div>
</div>
<script>
  document.querySelectorAll('tfoot td.size')[0].textContent = "{total_h}";
  document.querySelectorAll('tfoot td.prev')[0].textContent = "{prev_h}";
  document.querySelectorAll('tfoot td.delta')[0].textContent = "{sign}{delta_h}";
</script>
</body>
</html>""".format(
            total_h=human(total),
            prev_h=human(total_prev),
            delta_h=human(abs(total-total_prev)),
            sign=("+" if total-total_prev>=0 else "-")
        ))
    print(f"✅ Wrote {OUT}")

if __name__ == "__main__":
    main()
