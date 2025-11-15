#!/usr/bin/env python3
"""
Real-Time Performance Dashboard Service
Monitoring for Qualcomm Snapdragon processor performance
Port: 8700
"""

import os
import sys
import threading
import time
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.performance.database import PerformanceDatabase
from services.performance.monitor import SnapdragonMonitor
from services.performance.optimizer import PerformanceOptimizer

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'performance-dashboard-secret-key')
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

db = PerformanceDatabase()
monitor = SnapdragonMonitor()
optimizer = PerformanceOptimizer()

monitoring_active = False
monitoring_thread = None
alert_thresholds = {
    'cpu_usage': 80,
    'gpu_usage': 80,
    'memory_usage': 85,
    'storage_free_gb': 20,
    'temperature_c': 75,
    'battery_percent': 20
}


def check_alerts(metrics: dict):
    """Check metrics and trigger alerts if thresholds are exceeded."""
    alerts = []
    
    cpu_usage = metrics['cpu']['total_usage']
    if cpu_usage > alert_thresholds['cpu_usage']:
        alert = {
            'alert_type': 'cpu',
            'severity': 'high' if cpu_usage > 90 else 'warning',
            'message': f'High CPU usage: {cpu_usage}%',
            'metric_name': 'cpu_total_usage',
            'metric_value': cpu_usage,
            'threshold_value': alert_thresholds['cpu_usage']
        }
        alerts.append(alert)
        db.record_alert(**alert)
    
    gpu_usage = metrics['gpu']['usage_percent']
    if gpu_usage > alert_thresholds['gpu_usage']:
        alert = {
            'alert_type': 'gpu',
            'severity': 'high' if gpu_usage > 90 else 'warning',
            'message': f'High GPU usage: {gpu_usage}%',
            'metric_name': 'gpu_usage',
            'metric_value': gpu_usage,
            'threshold_value': alert_thresholds['gpu_usage']
        }
        alerts.append(alert)
        db.record_alert(**alert)
    
    memory_usage = metrics['memory']['usage_percent']
    if memory_usage > alert_thresholds['memory_usage']:
        alert = {
            'alert_type': 'memory',
            'severity': 'critical' if memory_usage > 95 else 'warning',
            'message': f'High memory usage: {memory_usage}%',
            'metric_name': 'memory_usage',
            'metric_value': memory_usage,
            'threshold_value': alert_thresholds['memory_usage']
        }
        alerts.append(alert)
        db.record_alert(**alert)
    
    storage_free = metrics['storage']['free_gb']
    if storage_free < alert_thresholds['storage_free_gb']:
        alert = {
            'alert_type': 'storage',
            'severity': 'critical' if storage_free < 10 else 'warning',
            'message': f'Low storage space: {storage_free}GB free',
            'metric_name': 'storage_free',
            'metric_value': storage_free,
            'threshold_value': alert_thresholds['storage_free_gb']
        }
        alerts.append(alert)
        db.record_alert(**alert)
    
    soc_temp = metrics['temperature']['soc_temp_c']
    if soc_temp > alert_thresholds['temperature_c']:
        alert = {
            'alert_type': 'temperature',
            'severity': 'critical' if soc_temp > 85 else 'warning',
            'message': f'High SoC temperature: {soc_temp}°C',
            'metric_name': 'soc_temperature',
            'metric_value': soc_temp,
            'threshold_value': alert_thresholds['temperature_c']
        }
        alerts.append(alert)
        db.record_alert(**alert)
    
    if metrics['temperature']['thermal_throttling']:
        alert = {
            'alert_type': 'thermal_throttling',
            'severity': 'critical',
            'message': 'Thermal throttling active - performance reduced',
            'metric_name': 'thermal_throttling',
            'metric_value': 1,
            'threshold_value': 0
        }
        alerts.append(alert)
        db.record_alert(**alert)
    
    battery_percent = metrics['battery']['battery_percent']
    if battery_percent < alert_thresholds['battery_percent']:
        alert = {
            'alert_type': 'battery',
            'severity': 'critical' if battery_percent < 10 else 'warning',
            'message': f'Low battery: {battery_percent}%',
            'metric_name': 'battery_percent',
            'metric_value': battery_percent,
            'threshold_value': alert_thresholds['battery_percent']
        }
        alerts.append(alert)
        db.record_alert(**alert)
    
    if alerts:
        socketio.emit('alerts', alerts, namespace='/')
    
    return alerts


def monitoring_loop():
    """Background thread for continuous monitoring."""
    global monitoring_active
    
    while monitoring_active:
        try:
            metrics = monitor.get_all_metrics()
            
            db.record_metric('cpu', 'cpu_total_usage', metrics['cpu']['total_usage'], '%', metrics['cpu']['status'])
            db.record_metric('cpu', 'cpu_frequency', metrics['cpu']['frequency_ghz'], 'GHz', metrics['cpu']['status'])
            db.record_metric('gpu', 'gpu_usage', metrics['gpu']['usage_percent'], '%', metrics['gpu']['status'])
            db.record_metric('gpu', 'gpu_frequency', metrics['gpu']['frequency_mhz'], 'MHz', metrics['gpu']['status'])
            db.record_metric('gpu', 'gpu_temperature', metrics['gpu']['temperature_c'], '°C', metrics['gpu']['status'])
            db.record_metric('memory', 'memory_usage', metrics['memory']['usage_percent'], '%', metrics['memory']['status'])
            db.record_metric('memory', 'memory_used', metrics['memory']['used_gb'], 'GB', metrics['memory']['status'])
            db.record_metric('storage', 'storage_usage', metrics['storage']['usage_percent'], '%', metrics['storage']['status'])
            db.record_metric('storage', 'storage_free', metrics['storage']['free_gb'], 'GB', metrics['storage']['status'])
            db.record_metric('temperature', 'soc_temperature', metrics['temperature']['soc_temp_c'], '°C', metrics['temperature']['status'])
            db.record_metric('temperature', 'battery_temperature', metrics['temperature']['battery_temp_c'], '°C', metrics['temperature']['status'])
            db.record_metric('battery', 'battery_percent', metrics['battery']['battery_percent'], '%', metrics['battery']['status'])
            db.record_metric('battery', 'battery_voltage', metrics['battery']['voltage_v'], 'V', metrics['battery']['status'])
            db.record_metric('battery', 'battery_current', metrics['battery']['current_ma'], 'mA', metrics['battery']['status'])
            
            for i, core_usage in enumerate(metrics['cpu']['core_usage']):
                db.record_metric('cpu', f'cpu_core_{i}', core_usage, '%', 'normal')
            
            check_alerts(metrics)
            
            socketio.emit('metrics_update', metrics, namespace='/')
            
            health = monitor.get_system_health()
            socketio.emit('health_update', health, namespace='/')
            
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
        print("✓ Performance monitoring started")


def stop_monitoring():
    """Stop the monitoring background thread."""
    global monitoring_active
    monitoring_active = False
    print("✓ Performance monitoring stopped")


@app.route('/')
def index():
    """Serve the main dashboard."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('PERFORMANCE_PORT', 8700))
    return jsonify({
        'ok': True,
        'service': 'performance_dashboard',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'monitoring_active': monitoring_active,
        'performance_mode': monitor.performance_mode
    })


@app.route('/api/metrics/current')
def api_current_metrics():
    """Get current performance metrics."""
    try:
        metrics = monitor.get_all_metrics()
        return jsonify({
            'ok': True,
            'metrics': metrics
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/metrics/cpu')
def api_cpu_metrics():
    """Get CPU metrics."""
    try:
        cpu = monitor.get_cpu_metrics()
        return jsonify({
            'ok': True,
            'cpu': cpu
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/metrics/gpu')
def api_gpu_metrics():
    """Get GPU metrics."""
    try:
        gpu = monitor.get_gpu_metrics()
        return jsonify({
            'ok': True,
            'gpu': gpu
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/metrics/memory')
def api_memory_metrics():
    """Get memory metrics."""
    try:
        memory = monitor.get_memory_metrics()
        return jsonify({
            'ok': True,
            'memory': memory
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/metrics/storage')
def api_storage_metrics():
    """Get storage metrics."""
    try:
        storage = monitor.get_storage_metrics()
        return jsonify({
            'ok': True,
            'storage': storage
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/metrics/network')
def api_network_metrics():
    """Get network metrics."""
    try:
        network = monitor.get_network_metrics()
        return jsonify({
            'ok': True,
            'network': network
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/metrics/temperature')
def api_temperature_metrics():
    """Get temperature metrics."""
    try:
        temperature = monitor.get_temperature_metrics()
        return jsonify({
            'ok': True,
            'temperature': temperature
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/metrics/battery')
def api_battery_metrics():
    """Get battery metrics."""
    try:
        battery = monitor.get_battery_metrics()
        return jsonify({
            'ok': True,
            'battery': battery
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/processes')
def api_processes():
    """Get running processes."""
    try:
        processes = monitor.get_process_metrics()
        return jsonify({
            'ok': True,
            'processes': processes
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/health/system')
def api_system_health():
    """Get overall system health."""
    try:
        health = monitor.get_system_health()
        return jsonify({
            'ok': True,
            'health': health
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/performance/mode', methods=['GET', 'POST'])
def api_performance_mode():
    """Get or set performance mode."""
    try:
        if request.method == 'POST':
            data = request.json or {}
            mode = data.get('mode', 'balanced')
            
            before_metrics = monitor.get_all_metrics()
            success = monitor.set_performance_mode(mode)
            
            if success:
                after_metrics = monitor.get_all_metrics()
                
                db.record_optimization(
                    action_type='performance_mode_change',
                    details=f'Changed to {mode} mode',
                    before_state={'mode': before_metrics['performance_mode']},
                    after_state={'mode': mode},
                    success=True
                )
                
                return jsonify({
                    'ok': True,
                    'mode': mode,
                    'message': f'Performance mode set to {mode}'
                })
            else:
                return jsonify({
                    'ok': False,
                    'error': 'Invalid performance mode'
                }), 400
        else:
            return jsonify({
                'ok': True,
                'mode': monitor.performance_mode,
                'available_modes': ['high_performance', 'balanced', 'power_save']
            })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/optimize/cache', methods=['POST'])
def api_clear_cache():
    """Clear app cache."""
    try:
        data = request.json or {}
        app_name = data.get('app_name')
        
        result = optimizer.clear_cache(app_name)
        
        db.record_optimization(
            action_type='clear_cache',
            details=result['message'],
            after_state={'space_freed_mb': result['space_freed_mb']},
            success=result['success']
        )
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/optimize/background-apps', methods=['POST'])
def api_close_background_apps():
    """Close background applications."""
    try:
        data = request.json or {}
        app_names = data.get('app_names')
        
        result = optimizer.close_background_apps(app_names)
        
        db.record_optimization(
            action_type='close_background_apps',
            details=result['message'],
            after_state={
                'apps_closed': result['count'],
                'memory_freed_mb': result['memory_freed_mb']
            },
            success=result['success']
        )
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/optimize/process/kill', methods=['POST'])
def api_kill_process():
    """Kill a specific process."""
    try:
        data = request.json or {}
        process_name = data.get('process_name')
        pid = data.get('pid')
        
        if not process_name:
            return jsonify({'ok': False, 'error': 'process_name is required'}), 400
        
        result = optimizer.kill_process(process_name, pid)
        
        db.record_process_action(
            process_name=process_name,
            process_id=pid,
            action='killed' if result['success'] else 'kill_failed'
        )
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/optimize/memory', methods=['POST'])
def api_optimize_memory():
    """Optimize memory usage."""
    try:
        result = optimizer.optimize_memory()
        
        db.record_optimization(
            action_type='optimize_memory',
            details=result['message'],
            after_state={'total_freed_mb': result['total_freed_mb']},
            success=result['success']
        )
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/optimize/storage', methods=['POST'])
def api_optimize_storage():
    """Optimize storage usage."""
    try:
        result = optimizer.optimize_storage()
        
        db.record_optimization(
            action_type='optimize_storage',
            details=result['message'],
            after_state={'total_freed_gb': result['total_freed_gb']},
            success=result['success']
        )
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/optimize/cpu', methods=['POST'])
def api_optimize_cpu():
    """Optimize CPU usage."""
    try:
        result = optimizer.optimize_cpu()
        
        db.record_optimization(
            action_type='optimize_cpu',
            details=result['message'],
            after_state={'cpu_freed_percent': result['cpu_freed_percent']},
            success=result['success']
        )
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/optimize/gpu', methods=['POST'])
def api_optimize_gpu():
    """Optimize GPU usage."""
    try:
        result = optimizer.optimize_gpu()
        
        db.record_optimization(
            action_type='optimize_gpu',
            details=result['message'],
            after_state={'gpu_freed_percent': result['gpu_freed_percent']},
            success=result['success']
        )
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/optimize/battery', methods=['POST'])
def api_optimize_battery():
    """Optimize battery usage."""
    try:
        result = optimizer.optimize_battery()
        
        db.record_optimization(
            action_type='optimize_battery',
            details=result['message'],
            after_state={'estimated_runtime_increase_min': result['estimated_runtime_increase_min']},
            success=result['success']
        )
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/optimize/cooldown', methods=['POST'])
def api_cooldown():
    """Cool down overheating system."""
    try:
        result = optimizer.cool_down_system()
        
        db.record_optimization(
            action_type='cool_down_system',
            details=result['message'],
            after_state={'estimated_temp_reduction_c': result['estimated_temp_reduction_c']},
            success=result['success']
        )
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/optimize/full', methods=['POST'])
def api_full_optimization():
    """Run full system optimization."""
    try:
        result = optimizer.full_optimization()
        
        db.record_optimization(
            action_type='full_optimization',
            details=result['message'],
            after_state={'total_actions': result['total_actions']},
            success=result['success']
        )
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/suggestions')
def api_suggestions():
    """Get optimization suggestions."""
    try:
        metrics = monitor.get_all_metrics()
        suggestions = optimizer.get_optimization_suggestions(metrics)
        
        return jsonify({
            'ok': True,
            'suggestions': suggestions
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/alerts')
def api_get_alerts():
    """Get recent alerts."""
    try:
        limit = int(request.args.get('limit', 50))
        severity = request.args.get('severity')
        
        alerts = db.get_alerts(limit, severity)
        
        return jsonify({
            'ok': True,
            'alerts': alerts
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/history/metrics/<metric_name>')
def api_metric_history(metric_name):
    """Get historical data for a metric."""
    try:
        hours = int(request.args.get('hours', 1))
        limit = int(request.args.get('limit', 500))
        
        history = db.get_metric_history(metric_name, hours, limit)
        
        return jsonify({
            'ok': True,
            'metric_name': metric_name,
            'history': history
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/history/optimizations')
def api_optimization_history():
    """Get optimization history."""
    try:
        limit = int(request.args.get('limit', 50))
        
        history = db.get_optimization_history(limit)
        
        return jsonify({
            'ok': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/history/processes')
def api_process_history():
    """Get process monitoring history."""
    try:
        limit = int(request.args.get('limit', 100))
        
        history = db.get_process_history(limit)
        
        return jsonify({
            'ok': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/stats')
def api_stats():
    """Get database statistics."""
    try:
        stats = db.get_stats()
        
        return jsonify({
            'ok': True,
            'stats': stats
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
            'status': 'started',
            'monitoring_active': monitoring_active
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
            'status': 'stopped',
            'monitoring_active': monitoring_active
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to Performance Dashboard'})
    
    metrics = monitor.get_all_metrics()
    emit('metrics_update', metrics)
    
    health = monitor.get_system_health()
    emit('health_update', health)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    print(f"Client disconnected: {request.sid}")


@socketio.on('request_update')
def handle_request_update():
    """Handle client request for immediate update."""
    metrics = monitor.get_all_metrics()
    emit('metrics_update', metrics)
    
    health = monitor.get_system_health()
    emit('health_update', health)


if __name__ == '__main__':
    port = int(os.environ.get('PERFORMANCE_PORT', 8700))
    
    print(f"📊 Performance Dashboard starting on port {port}")
    print(f"🎯 Dashboard: http://localhost:{port}")
    print(f"💓 Health Check: http://localhost:{port}/health")
    print(f"🔌 WebSocket enabled for real-time updates")
    print(f"⚡ Monitoring: Auto-start enabled")
    print(f"🏁 Snapdragon 8-core @ 2.0GHz | 12GB RAM | 256GB Storage")
    
    start_monitoring()
    
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
