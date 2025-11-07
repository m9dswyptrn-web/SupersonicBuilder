#!/usr/bin/env python3
"""
sync_metrics_api.py
FastAPI/Flask endpoints for sync metrics dashboard.

Provides /api/sync/metrics endpoint with aggregated stats.
"""

from typing import Dict, Any, List

def get_metrics_data() -> Dict[str, Any]:
    """
    Get all metrics data for dashboard.
    
    Returns:
        Dict with keys:
            - stats: Summary statistics
            - hourly: Hourly sync counts
            - recent: Recent sync history
            - throttle: Current throttle status
    """
    from tools.sync_config import get_config
    from tools.sync_history import get_history
    from tools.sync_throttle import get_throttle
    
    config = get_config()
    history = get_history(
        history_file=config.history_file,
        max_entries=config.history_max_entries
    )
    throttle = get_throttle(config)
    
    # Get stats for last 24 hours
    stats = history.get_stats(hours=24)
    
    # Get hourly counts for sparkline
    hourly = history.get_hourly_counts(hours=24)
    
    # Get recent entries (last 50)
    recent = history.load_all()[-50:]
    
    # Get throttle status
    throttle_status = throttle.get_status()
    
    return {
        "stats": stats,
        "hourly": hourly,
        "recent": recent,
        "throttle": throttle_status,
        "config": {
            "max_per_hour": config.max_per_hour,
            "backoff_enabled": config.backoff_enabled,
            "webhooks_enabled": config.webhooks_enabled,
        }
    }

# --- FastAPI Adapter ---

def add_fastapi_routes(router):
    """Add sync metrics endpoint to FastAPI router."""
    from fastapi.responses import HTMLResponse
    
    @router.get("/sync/metrics", response_model=None)
    def api_sync_metrics():
        """Get sync metrics data for dashboard."""
        return get_metrics_data()
    
    @router.get("/sync/dashboard", response_class=HTMLResponse)
    def api_sync_dashboard():
        """Serve sync metrics dashboard HTML."""
        try:
            with open("static/sync-metrics-dashboard.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)

# --- Flask Adapter ---

def add_flask_routes(app):
    """Add sync metrics endpoint to Flask app."""
    from flask import jsonify, send_file
    
    @app.route("/api/sync/metrics", methods=["GET"])
    def api_sync_metrics():
        """Get sync metrics data for dashboard."""
        return jsonify(get_metrics_data()), 200
    
    @app.route("/api/sync/dashboard", methods=["GET"])
    def api_sync_dashboard():
        """Serve sync metrics dashboard HTML."""
        try:
            return send_file("static/sync-metrics-dashboard.html")
        except FileNotFoundError:
            return "<h1>Dashboard not found</h1>", 404

# --- Standalone Server ---

if __name__ == "__main__":
    import sys
    from flask import Flask, jsonify, send_file
    
    app = Flask(__name__)
    add_flask_routes(app)
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8088
    print(f"📊 Sync Metrics Dashboard: http://localhost:{port}/api/sync/dashboard")
    app.run(host="0.0.0.0", port=port, debug=False)
