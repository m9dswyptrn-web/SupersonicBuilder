#!/usr/bin/env python3
"""
Wireless Charger Monitor Service
Real-time monitoring of phone charging on EOENKK wireless charging pad
Port: 10000
"""

import os
import sys
import threading
import time
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.wireless.database import WirelessChargerDatabase
from services.wireless.monitor import WirelessChargerMonitor
from services.wireless.battery import BatteryHealthTracker

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'wireless-charger-secret-key')
CORS(app)

db = WirelessChargerDatabase()
monitor = WirelessChargerMonitor()
battery_tracker = BatteryHealthTracker()

monitoring_active = False
monitoring_thread = None
current_session_id = None


def monitoring_loop():
    """Background thread for continuous monitoring."""
    global monitoring_active, current_session_id
    
    while monitoring_active:
        try:
            monitor.update_charging_status()
            
            if monitor.phone_on_pad:
                if current_session_id is None:
                    current_session_id = db.start_charging_session(
                        phone_model=monitor.phone_model,
                        qi_compatible=monitor.qi_compatible,
                        start_battery_percent=int(monitor.battery_percent)
                    )
                    print(f"✓ Started charging session: {current_session_id}")
                
                battery_tracker.update_from_charging_metrics(
                    int(monitor.battery_percent),
                    monitor.charging_power_w,
                    monitor.phone_temp_c
                )
                
                db.record_charging_metric(
                    session_id=current_session_id,
                    phone_detected=True,
                    charging_active=monitor.charging_active,
                    battery_percent=int(monitor.battery_percent),
                    charging_power_w=monitor.charging_power_w,
                    input_power_w=monitor.input_power_w,
                    output_power_w=monitor.output_power_w,
                    efficiency_percent=monitor.get_efficiency_percent(),
                    pad_temp_c=monitor.pad_temp_c,
                    phone_temp_c=monitor.phone_temp_c,
                    alignment_score=monitor.alignment_score
                )
                
                db.record_pad_health('pad_temperature', monitor.pad_temp_c, '°C', 
                                    'critical' if monitor.pad_temp_c > 50 else 'normal')
                db.record_pad_health('coil_health', monitor.coil_health_percent, '%', 'normal')
                
                alerts = monitor.check_alerts()
                for alert in alerts:
                    if alert['severity'] in ['warning', 'critical']:
                        db.record_alert(
                            session_id=current_session_id,
                            alert_type=alert['type'],
                            severity=alert['severity'],
                            message=alert['message']
                        )
            else:
                if current_session_id is not None:
                    db.end_charging_session(
                        session_id=current_session_id,
                        end_battery_percent=int(monitor.battery_percent)
                    )
                    print(f"✓ Ended charging session: {current_session_id}")
                    
                    session = db.get_active_session()
                    if session and session['completed']:
                        db.update_charging_cycles(
                            session['total_power_wh'],
                            monitor.coil_health_percent
                        )
                    
                    current_session_id = None
            
        except Exception as e:
            print(f"Monitoring error: {e}")
        
        time.sleep(2)


def start_monitoring():
    """Start the monitoring background thread."""
    global monitoring_active, monitoring_thread
    
    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        print("✓ Wireless charger monitoring started")


def stop_monitoring():
    """Stop the monitoring background thread."""
    global monitoring_active
    monitoring_active = False
    print("✓ Wireless charger monitoring stopped")


@app.route('/')
def index():
    """Serve the main dashboard."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('WIRELESS_PORT', 10000))
    return jsonify({
        'ok': True,
        'service': 'wireless_charger_monitor',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'monitoring_active': monitoring_active,
        'phone_on_pad': monitor.phone_on_pad,
        'charging_active': monitor.charging_active
    })


@app.route('/api/status')
def api_status():
    """Get current charging status."""
    try:
        status = monitor.get_charging_status()
        return jsonify({
            'ok': True,
            'status': status
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/metrics/current')
def api_current_metrics():
    """Get all current metrics."""
    try:
        metrics = monitor.get_all_metrics()
        battery_info = battery_tracker.get_battery_info()
        
        return jsonify({
            'ok': True,
            'metrics': metrics,
            'battery': battery_info
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/efficiency')
def api_efficiency():
    """Get charging efficiency metrics."""
    try:
        efficiency = monitor.get_efficiency_metrics()
        return jsonify({
            'ok': True,
            'efficiency': efficiency
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/compatibility')
def api_compatibility():
    """Get phone compatibility information."""
    try:
        compatibility = monitor.get_phone_compatibility()
        return jsonify({
            'ok': True,
            'compatibility': compatibility
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/pad/health')
def api_pad_health():
    """Get wireless charging pad health."""
    try:
        health = monitor.get_pad_health()
        cycles = db.get_latest_charging_cycles()
        
        return jsonify({
            'ok': True,
            'health': health,
            'cycles': cycles
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/alerts')
def api_alerts():
    """Get current alerts."""
    try:
        alerts = monitor.check_alerts()
        recent_alerts = db.get_recent_alerts(limit=10, unresolved_only=True)
        
        return jsonify({
            'ok': True,
            'current_alerts': alerts,
            'recent_alerts': recent_alerts
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/alerts/resolve', methods=['POST'])
def api_resolve_alerts():
    """Resolve alerts."""
    try:
        data = request.json or {}
        alert_type = data.get('alert_type')
        
        db.resolve_alerts(alert_type)
        
        return jsonify({
            'ok': True,
            'message': f'Alerts resolved{" for " + alert_type if alert_type else ""}'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/battery/info')
def api_battery_info():
    """Get battery information."""
    try:
        battery_info = battery_tracker.get_battery_info()
        optimal_range = battery_tracker.get_optimal_range_status()
        
        return jsonify({
            'ok': True,
            'battery': battery_info,
            'optimal_range': optimal_range
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/battery/recommendations')
def api_battery_recommendations():
    """Get battery care recommendations."""
    try:
        recommendations = battery_tracker.get_care_recommendations()
        profile = battery_tracker.get_charging_profile()
        lifespan = battery_tracker.predict_battery_lifespan()
        
        return jsonify({
            'ok': True,
            'recommendations': recommendations,
            'charging_profile': profile,
            'lifespan_prediction': lifespan
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/battery/impact')
def api_battery_impact():
    """Analyze charging impact on battery health."""
    try:
        if not monitor.charging_active:
            return jsonify({
                'ok': True,
                'impact': None,
                'message': 'Not currently charging'
            })
        
        session = db.get_active_session()
        duration_minutes = 0
        if session:
            start_time = datetime.fromisoformat(session['start_time'])
            duration_minutes = int((datetime.now() - start_time).total_seconds() / 60)
        
        impact = battery_tracker.analyze_charging_impact(
            monitor.charging_power_w,
            monitor.pad_temp_c,
            duration_minutes
        )
        
        return jsonify({
            'ok': True,
            'impact': impact
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/battery/tips')
def api_battery_tips():
    """Get battery care tips."""
    try:
        daily_tips = battery_tracker.get_daily_tips()
        all_tips = db.get_all_battery_care_tips()
        
        return jsonify({
            'ok': True,
            'daily_tips': daily_tips,
            'all_tips': all_tips
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/sessions')
def api_sessions():
    """Get charging session history."""
    try:
        limit = int(request.args.get('limit', 20))
        completed_only = request.args.get('completed_only', 'true').lower() == 'true'
        
        sessions = db.get_charging_sessions(limit, completed_only)
        
        return jsonify({
            'ok': True,
            'sessions': sessions
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/sessions/<session_id>')
def api_session_details(session_id):
    """Get details for a specific charging session."""
    try:
        metrics = db.get_session_metrics(session_id)
        
        return jsonify({
            'ok': True,
            'session_id': session_id,
            'metrics': metrics
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/sessions/active')
def api_active_session():
    """Get current active session."""
    try:
        session = db.get_active_session()
        
        return jsonify({
            'ok': True,
            'session': session,
            'session_id': current_session_id
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/statistics')
def api_statistics():
    """Get overall charging statistics."""
    try:
        stats = db.get_charging_statistics()
        
        return jsonify({
            'ok': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/history/pad-health')
def api_pad_health_history():
    """Get pad health history."""
    try:
        metric_name = request.args.get('metric')
        hours = int(request.args.get('hours', 24))
        limit = int(request.args.get('limit', 500))
        
        history = db.get_pad_health_history(metric_name, hours, limit)
        
        return jsonify({
            'ok': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/simulate/place-phone', methods=['POST'])
def api_simulate_place_phone():
    """Simulate placing a phone on the charging pad."""
    try:
        data = request.json or {}
        alignment = data.get('alignment', 'good')
        
        monitor.simulate_phone_placement(alignment)
        
        return jsonify({
            'ok': True,
            'message': 'Phone placed on charging pad',
            'status': monitor.get_charging_status()
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/simulate/remove-phone', methods=['POST'])
def api_simulate_remove_phone():
    """Simulate removing the phone from the charging pad."""
    try:
        monitor.simulate_phone_removal()
        
        return jsonify({
            'ok': True,
            'message': 'Phone removed from charging pad',
            'status': monitor.get_charging_status()
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/monitoring/start', methods=['POST'])
def api_start_monitoring():
    """Start monitoring."""
    try:
        start_monitoring()
        return jsonify({
            'ok': True,
            'message': 'Monitoring started'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/monitoring/stop', methods=['POST'])
def api_stop_monitoring():
    """Stop monitoring."""
    try:
        stop_monitoring()
        return jsonify({
            'ok': True,
            'message': 'Monitoring stopped'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/stats/database')
def api_database_stats():
    """Get database statistics."""
    try:
        stats = db.get_stats()
        
        return jsonify({
            'ok': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('WIRELESS_PORT', 10000))
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║     Wireless Charger Monitor Service                     ║
║     Port: {port}                                         ║
║     Status: Starting...                                   ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    start_monitoring()
    
    print(f"✓ Service ready at http://0.0.0.0:{port}")
    print(f"✓ Health check: http://0.0.0.0:{port}/health")
    print(f"✓ Web UI: http://0.0.0.0:{port}/")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
