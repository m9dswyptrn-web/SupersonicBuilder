#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
supersonic_telemetry.py
------------------------------------------------------------
Collects system metrics and build stats for the Supersonic Dashboard.
Outputs:
  SonicBuilder/reports/telemetry.json
  SonicBuilder/reports/telemetry_card.html
  SonicBuilder/reports/telemetry_spark.svg    (24-point sparkline)
  SonicBuilder/reports/telemetry_log.jsonl    (rolling time series)

Run:
  python supersonic_telemetry.py
"""

from __future__ import annotations
import json, time, os
from datetime import datetime
from pathlib import Path

try:
    import psutil
except Exception:
    psutil = None

ROOT = Path(".")
OUT = ROOT / "SonicBuilder" / "reports"
OUT.mkdir(parents=True, exist_ok=True)

TELEM_JSON = OUT / "telemetry.json"
TELEM_CARD = OUT / "telemetry_card.html"
TELEM_SPARK = OUT / "telemetry_spark.svg"
TELEM_LOG = OUT / "telemetry_log.jsonl"
STATE = ROOT / ".supersonic_state.json"

SPARK_LEN = 24

def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            pass
    return {
        "rebuild_count": 0,
        "last_build_status": "unknown",
        "last_build_time": ""
    }

def save_state(state):
    STATE.write_text(json.dumps(state, indent=2))

def get_metrics():
    m = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"),
        "cpu_pct": None,
        "mem_pct": None,
        "disk_pct": None,
        "temps_c": None,
        "proc_count": None
    }
    if psutil is None:
        return m

    try:
        m["cpu_pct"] = psutil.cpu_percent(interval=0.20)
        m["mem_pct"] = psutil.virtual_memory().percent
        m["disk_pct"] = psutil.disk_usage("/").percent
        m["proc_count"] = len(psutil.pids())
        temps = getattr(psutil, "sensors_temperatures", lambda: {})()
        if temps:
            for _, lst in temps.items():
                if lst:
                    m["temps_c"] = lst[0].current
                    break
    except Exception:
        pass
    return m

def append_log(sample):
    try:
        with TELEM_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(sample) + "\n")
    except Exception:
        pass

def last_n_series():
    if not TELEM_LOG.exists():
        return []
    lines = TELEM_LOG.read_text(encoding="utf-8").strip().splitlines()[-SPARK_LEN:]
    series = []
    for L in lines:
        try:
            series.append(json.loads(L))
        except Exception:
            continue
    return series

def make_spark_svg(series, key="cpu_pct"):
    values = [s.get(key) for s in series if s.get(key) is not None]
    if not values:
        TELEM_SPARK.write_text("<svg width='320' height='64' xmlns='http://www.w3.org/2000/svg'></svg>", encoding="utf-8")
        return
    w, h = 320, 64
    vmin, vmax = min(values), max(values)
    rng = max(1e-6, vmax - vmin)
    pts = []
    for i, v in enumerate(values):
        x = int(i * (w-8) / max(1, len(values)-1)) + 4
        y = int(h - 6 - ((v - vmin) / rng) * (h - 12))
        pts.append(f"{x},{y}")
    svg = f"""<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="{w}" height="{h}" fill="#0d0d0d" />
  <polyline fill="none" stroke="#00ffff" stroke-width="2" points="{' '.join(pts)}" />
  <text x="8" y="{h-10}" fill="#88ffff" font-family="Segoe UI,Arial" font-size="10">CPU% ({values[-1]:.0f})</text>
</svg>"""
    TELEM_SPARK.write_text(svg, encoding="utf-8")

def write_card(state, sample):
    temps = sample.get("temps_c")
    temps_str = f"{temps:.0f}°C" if isinstance(temps, (int, float)) else "n/a"
    html = f"""<!doctype html><meta charset="utf-8">
<style>
body{{background:#0d0d0d;color:#e0e0e0;font-family:Segoe UI,Roboto,Arial,sans-serif;padding:12px}}
.card{{background:#1b1b1b;border:1px solid #00ffff44;border-radius:10px;padding:14px;max-width:920px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-top:8px}}
.kv{{background:#121212;border:1px solid #00ffff22;border-radius:8px;padding:8px}}
.kv b{{color:#00ffff}}
img.spark{{width:100%;max-width:320px;border:1px solid #00ffff33;border-radius:8px;margin-top:8px}}
small{{color:#aaa}}
</style>
<div class="card">
  <h3>Supersonic Telemetry</h3>
  <small>{sample.get('timestamp','')}</small>
  <div class="grid">
    <div class="kv"><b>CPU</b><br>{sample.get('cpu_pct','n/a')}%</div>
    <div class="kv"><b>Memory</b><br>{sample.get('mem_pct','n/a')}%</div>
    <div class="kv"><b>Disk</b><br>{sample.get('disk_pct','n/a')}%</div>
    <div class="kv"><b>Temp</b><br>{temps_str}</div>
    <div class="kv"><b>Processes</b><br>{sample.get('proc_count','n/a')}</div>
    <div class="kv"><b>Rebuild Count</b><br>{state.get('rebuild_count',0)}</div>
    <div class="kv"><b>Last Build Status</b><br>{state.get('last_build_status','unknown')}</div>
  </div>
  <img class="spark" src="{TELEM_SPARK.as_posix()}" alt="CPU sparkline">
</div>"""
    TELEM_CARD.write_text(html, encoding="utf-8")

def main():
    state = load_state()
    sample = get_metrics()
    payload = {
        "state": state,
        "metrics": sample,
        "generated_at": sample.get("timestamp")
    }
    TELEM_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    append_log(sample)
    series = last_n_series()
    make_spark_svg(series, "cpu_pct")
    write_card(state, sample)
    print(f"📊 Telemetry updated → {TELEM_JSON.name}, {TELEM_CARD.name}, {TELEM_SPARK.name}")

if __name__ == "__main__":
    main()
