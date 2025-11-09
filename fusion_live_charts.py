#!/usr/bin/env python3
"""
SonicBuilder Fusion Live Charts v3.5
Visualizes Replit ↔ GitHub ↔ Docs telemetry in real time.
"""

import os, json, datetime
from flask import Flask, render_template_string, jsonify

LOG_DIR = "logs/uptime"  # Use existing uptime logs from Auto-Healer
PORT = int(os.getenv("FUSION_CHARTS_PORT", 8092))

app = Flask(__name__)

def collect_metrics():
    """Collect metrics from Auto-Healer uptime logs."""
    records = []
    if not os.path.exists(LOG_DIR):
        return []
    
    for fname in sorted(os.listdir(LOG_DIR)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(LOG_DIR, fname)
        try:
            with open(path, "r") as f:
                data = json.load(f)
                # Convert Auto-Healer format to chart format
                records.append({
                    "timestamp": data.get("timestamp", ""),
                    "status": "green" if data.get("status") == "success" else "red",
                    "color": "#00e676" if data.get("status") == "success" else "#ff4444"
                })
        except Exception:
            continue
    return records[-500:]  # keep last 500 entries

def aggregate():
    records = collect_metrics()
    if not records:
        return {"uptime": 0, "failures": 0, "avg_delay": 0, "data": []}

    uptime = sum(1 for r in records if r["status"] == "green")
    total = len(records)
    failures = sum(1 for r in records if r["status"] == "red")
    uptime_percent = round((uptime / total) * 100, 2)
    avg_delay = 0  # placeholder if delay tracking is added

    data_points = [{
        "time": r["timestamp"],
        "status": r["status"],
        "color": r["color"]
    } for r in records]

    return {
        "uptime": uptime_percent,
        "failures": failures,
        "avg_delay": avg_delay,
        "data": data_points
    }

@app.route("/charts")
def charts_page():
    metrics = aggregate()
    html = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
      <meta charset='UTF-8'>
      <title>Fusion Live Charts</title>
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      <style>
        body {{
          background-color: #0d1117;
          color: #e6edf3;
          font-family: 'Consolas', monospace;
          margin: 30px;
        }}
        h1 {{ color: #fff; }}
        canvas {{ background: #1e1e1e; border-radius: 10px; padding: 10px; }}
      </style>
    </head>
    <body>
      <h1>🧠 Fusion Live Telemetry Charts</h1>
      <h3>Uptime: {metrics["uptime"]}% | Failures: {metrics["failures"]}</h3>
      <canvas id="chart" width="800" height="400"></canvas>
      <script>
        async function fetchData() {{
          const resp = await fetch('/telemetry/latest.json');
          const live = await resp.json();
          const histResp = await fetch('/charts/data.json');
          const hist = await histResp.json();
          renderChart(hist.data);
        }}

        function renderChart(data) {{
          const ctx = document.getElementById('chart').getContext('2d');
          const colors = data.map(d => d.color);
          const labels = data.map(d => d.time.split('T')[1].split('Z')[0]);
          const values = data.map(d => d.status === 'green' ? 1 : (d.status === 'yellow' ? 0.5 : 0));
          new Chart(ctx, {{
            type: 'line',
            data: {{
              labels: labels,
              datasets: [{{
                label: 'Health Index',
                data: values,
                borderColor: '#00e676',
                backgroundColor: 'rgba(0,230,118,0.2)',
                fill: true,
                tension: 0.3,
                pointRadius: 0
              }}]
            }},
            options: {{
              scales: {{
                y: {{
                  min: 0,
                  max: 1,
                  ticks: {{ stepSize: 0.25 }},
                  title: {{ display: true, text: 'Health Level' }}
                }},
                x: {{
                  display: true,
                  ticks: {{ maxTicksLimit: 10 }}
                }}
              }},
              plugins: {{
                legend: {{ display: false }},
              }}
            }}
          }});
        }}

        fetchData();
        setInterval(fetchData, 15000);
      </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/charts/data.json")
def chart_data():
    return jsonify(aggregate())

if __name__ == "__main__":
    os.makedirs(LOG_DIR, exist_ok=True)
    print(f"📈 Fusion Charts server running on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)