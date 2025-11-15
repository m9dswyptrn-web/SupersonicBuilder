#!/usr/bin/env python3
"""
TPMS Monitor Service
Tire Pressure Monitoring System with CAN bus integration
Port: 9700
"""

import os
import sys
import json
import requests
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
from threading import Thread, Lock
import time

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.tpms.database import TPMSDatabase
from services.tpms.monitor import TPMSMonitor
from services.tpms.alerts import TPMSAlertSystem

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

TEMPLATE_DIR = Path(__file__).parent / 'templates'
STATIC_DIR = Path(__file__).parent / 'static'

TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.template_folder = str(TEMPLATE_DIR)
app.static_folder = str(STATIC_DIR)

# Initialize components
db = TPMSDatabase()
monitor = TPMSMonitor(simulated=True)
alert_system = TPMSAlertSystem(db, monitor)

# CAN bus and maintenance service URLs
CAN_BUS_URL = os.environ.get('CAN_BUS_URL', 'http://localhost:7000')
MAINTENANCE_URL = os.environ.get('MAINTENANCE_URL', 'http://localhost:9800')

# Background monitoring
monitoring_active = False
monitor_lock = Lock()


def on_new_reading(position, pressure_psi, temperature_f, sensor_id, battery, signal):
    """Callback for new TPMS readings."""
    db.log_reading(
        tire_position=position,
        pressure_psi=pressure_psi,
        temperature_f=temperature_f,
        sensor_id=sensor_id,
        sensor_battery=battery,
        signal_strength=signal,
        source='simulated'
    )


def on_new_alert(alert_data):
    """Callback for new alerts."""
    print(f"TPMS Alert: {alert_data['message']}")


def monitoring_loop():
    """Background monitoring and alert checking."""
    global monitoring_active
    
    while monitoring_active:
        try:
            # Check for alerts
            alerts = alert_system.check_all_pressures()
            
            # Check for slow leaks every 5 minutes
            if int(time.time()) % 300 == 0:
                slow_leak_alerts = alert_system.check_slow_leaks()
                alerts.extend(slow_leak_alerts)
            
            # Check spare tire reminder
            spare_alert = alert_system.check_spare_tire()
            if spare_alert:
                alerts.append(spare_alert)
            
            # Update hourly summaries
            if datetime.now().minute == 0:
                db.update_hourly_summary()
        
        except Exception as e:
            print(f"Monitoring loop error: {e}")
        
        time.sleep(5)


@app.route('/')
def index():
    """Serve main dashboard."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('TPMS_PORT', 9700))
    
    readings = monitor.get_current_readings()
    active_alerts = len(db.get_active_alerts())
    
    return jsonify({
        'ok': True,
        'service': 'tpms_monitor',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'features': {
            'pressure_monitoring': True,
            'temperature_monitoring': True,
            'puncture_detection': True,
            'slow_leak_detection': True,
            'seasonal_adjustments': True,
            'tire_rotation_tracking': True,
            'can_bus_integration': True,
            'maintenance_integration': True,
            'sensor_calibration': True,
            'spare_tire_monitoring': True
        },
        'monitoring_active': monitoring_active,
        'active_alerts': active_alerts,
        'tire_count': len(readings)
    })


@app.route('/api/readings/current')
def api_current_readings():
    """Get current tire pressure readings."""
    try:
        readings = monitor.get_current_readings()
        
        # Add status for each tire
        seasonal = db.get_active_seasonal_setting()
        min_psi = seasonal['min_psi'] if seasonal else 28.0
        max_psi = seasonal['max_psi'] if seasonal else 36.0
        
        for position in readings:
            readings[position]['pressure_status'] = monitor.get_pressure_status(position, min_psi, max_psi)
            readings[position]['temperature_status'] = monitor.get_temperature_status(position)
            readings[position]['sensor'] = monitor.get_sensor_info(position)
        
        return jsonify({
            'ok': True,
            'readings': readings,
            'thresholds': {
                'min_psi': min_psi,
                'max_psi': max_psi,
                'recommended_psi': seasonal['recommended_psi'] if seasonal else 33.0
            }
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/readings/<tire_position>')
def api_get_reading(tire_position: str):
    """Get reading for specific tire."""
    try:
        reading = monitor.get_reading(tire_position)
        
        if not reading:
            return jsonify({
                'ok': False,
                'error': 'Invalid tire position'
            }), 404
        
        sensor = monitor.get_sensor_info(tire_position)
        pressure_status = monitor.get_pressure_status(tire_position)
        temp_status = monitor.get_temperature_status(tire_position)
        
        return jsonify({
            'ok': True,
            'tire_position': tire_position,
            'reading': reading,
            'sensor': sensor,
            'pressure_status': pressure_status,
            'temperature_status': temp_status
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/history/<tire_position>')
def api_pressure_history(tire_position: str):
    """Get pressure history for a tire."""
    try:
        hours = int(request.args.get('hours', 24))
        history = db.get_pressure_history(tire_position, hours)
        
        return jsonify({
            'ok': True,
            'tire_position': tire_position,
            'history': history,
            'count': len(history)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/history/all')
def api_all_pressure_history():
    """Get pressure history for all tires."""
    try:
        hours = int(request.args.get('hours', 24))
        history = db.get_all_pressure_history(hours)
        
        return jsonify({
            'ok': True,
            'history': history
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts')
def api_get_alerts():
    """Get active alerts."""
    try:
        alerts = alert_system.get_active_alerts()
        summary = alert_system.get_alert_summary()
        
        return jsonify({
            'ok': True,
            'alerts': alerts,
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts/<alert_id>/dismiss', methods=['POST'])
def api_dismiss_alert(alert_id: str):
    """Dismiss an alert."""
    try:
        alert_system.dismiss_alert(alert_id)
        
        return jsonify({
            'ok': True,
            'message': 'Alert dismissed'
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts/dismiss-all', methods=['POST'])
def api_dismiss_all_alerts():
    """Dismiss all alerts."""
    try:
        data = request.json or {}
        tire_position = data.get('tire_position')
        
        alert_system.dismiss_all_alerts(tire_position)
        
        return jsonify({
            'ok': True,
            'message': 'Alerts dismissed'
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts/check', methods=['POST'])
def api_check_alerts():
    """Manually trigger alert check."""
    try:
        alerts = alert_system.check_all_pressures()
        slow_leak_alerts = alert_system.check_slow_leaks()
        alerts.extend(slow_leak_alerts)
        
        spare_alert = alert_system.check_spare_tire()
        if spare_alert:
            alerts.append(spare_alert)
        
        return jsonify({
            'ok': True,
            'new_alerts': alerts,
            'count': len(alerts)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/seasonal/settings')
def api_seasonal_settings():
    """Get all seasonal settings."""
    try:
        settings = db.get_seasonal_settings()
        active = db.get_active_seasonal_setting()
        
        return jsonify({
            'ok': True,
            'settings': settings,
            'active': active
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/seasonal/activate', methods=['POST'])
def api_activate_season():
    """Activate a seasonal setting."""
    try:
        data = request.json or {}
        season = data.get('season')
        
        if not season:
            return jsonify({
                'ok': False,
                'error': 'Season is required'
            }), 400
        
        db.set_active_season(season)
        alert_system.update_thresholds_from_seasonal()
        
        return jsonify({
            'ok': True,
            'season': season,
            'message': f'{season.title()} settings activated'
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/seasonal/adjust-pressure', methods=['POST'])
def api_adjust_for_temperature():
    """Calculate recommended pressure for current temperature."""
    try:
        data = request.json or {}
        ambient_temp_f = float(data.get('ambient_temp_f', 68.0))
        
        seasonal = db.get_active_seasonal_setting()
        base_pressure = seasonal['recommended_psi'] if seasonal else 33.0
        
        adjusted_pressure = monitor.adjust_for_temperature(base_pressure, ambient_temp_f)
        
        return jsonify({
            'ok': True,
            'ambient_temp_f': ambient_temp_f,
            'base_pressure_psi': base_pressure,
            'recommended_pressure_psi': adjusted_pressure,
            'adjustment_psi': round(adjusted_pressure - base_pressure, 1)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/sensors')
def api_get_sensors():
    """Get all TPMS sensors."""
    try:
        sensors = db.get_sensors()
        
        # Add live sensor info from monitor
        for sensor in sensors:
            position = sensor['tire_position']
            live_sensor = monitor.get_sensor_info(position)
            if live_sensor:
                sensor['live_data'] = live_sensor
        
        return jsonify({
            'ok': True,
            'sensors': sensors
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/sensors/learn', methods=['POST'])
def api_learn_sensor():
    """Learn/register a TPMS sensor."""
    try:
        data = request.json or {}
        tire_position = data.get('tire_position')
        sensor_id = data.get('sensor_id')
        
        if not tire_position:
            return jsonify({
                'ok': False,
                'error': 'Tire position is required'
            }), 400
        
        success = monitor.learn_sensor(tire_position, sensor_id)
        
        if success:
            # Store in database
            sensor_info = monitor.get_sensor_info(tire_position)
            db.add_sensor(
                sensor_id=sensor_info['sensor_id'],
                tire_position=tire_position,
                battery_voltage=sensor_info['battery']
            )
        
        return jsonify({
            'ok': success,
            'tire_position': tire_position,
            'sensor': monitor.get_sensor_info(tire_position) if success else None
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/sensors/reset', methods=['POST'])
def api_reset_sensors():
    """Reset all TPMS sensors."""
    try:
        monitor.reset_sensors()
        db.reset_sensors()
        
        return jsonify({
            'ok': True,
            'message': 'All sensors reset'
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/rotations')
def api_get_rotations():
    """Get tire rotation history."""
    try:
        limit = int(request.args.get('limit', 10))
        rotations = db.get_rotations(limit)
        
        return jsonify({
            'ok': True,
            'rotations': rotations,
            'count': len(rotations)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/rotations/add', methods=['POST'])
def api_add_rotation():
    """Log a tire rotation."""
    try:
        data = request.json or {}
        rotation_date = data.get('rotation_date', datetime.now().strftime('%Y-%m-%d'))
        odometer_reading = int(data.get('odometer_reading', 0))
        rotation_pattern = data.get('rotation_pattern', 'front_to_back')
        notes = data.get('notes', '')
        
        if odometer_reading <= 0:
            return jsonify({
                'ok': False,
                'error': 'Valid odometer reading is required'
            }), 400
        
        rotation_id = db.log_rotation(rotation_date, odometer_reading, rotation_pattern, notes)
        
        return jsonify({
            'ok': True,
            'rotation_id': rotation_id
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/rotations/check-needed')
def api_check_rotation_needed():
    """Check if tire rotation is needed."""
    try:
        # Try to get current mileage from maintenance service
        current_mileage = 0
        
        try:
            response = requests.get(f'{MAINTENANCE_URL}/api/mileage/current', timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    current_mileage = data.get('odometer_reading', 0)
        except:
            pass
        
        if current_mileage == 0:
            return jsonify({
                'ok': True,
                'rotation_needed': False,
                'message': 'Unable to determine current mileage'
            })
        
        rotation_info = alert_system.check_rotation_needed(current_mileage)
        
        return jsonify({
            'ok': True,
            'rotation_needed': rotation_info is not None,
            'rotation_info': rotation_info,
            'current_mileage': current_mileage
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/monitoring/start', methods=['POST'])
def api_start_monitoring():
    """Start background monitoring."""
    try:
        global monitoring_active
        
        with monitor_lock:
            if monitoring_active:
                return jsonify({
                    'ok': False,
                    'error': 'Monitoring already active'
                }), 400
            
            # Set callbacks
            monitor.set_callbacks(on_reading=on_new_reading, on_alert=on_new_alert)
            
            # Start monitor
            monitor.start()
            
            # Start background alert checking
            monitoring_active = True
            Thread(target=monitoring_loop, daemon=True).start()
            
            return jsonify({
                'ok': True,
                'message': 'Monitoring started'
            })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/monitoring/stop', methods=['POST'])
def api_stop_monitoring():
    """Stop background monitoring."""
    try:
        global monitoring_active
        
        with monitor_lock:
            if not monitoring_active:
                return jsonify({
                    'ok': False,
                    'error': 'Monitoring not active'
                }), 400
            
            monitoring_active = False
            monitor.stop()
            
            return jsonify({
                'ok': True,
                'message': 'Monitoring stopped'
            })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/monitoring/status')
def api_monitoring_status():
    """Get monitoring status."""
    try:
        return jsonify({
            'ok': True,
            'monitoring_active': monitoring_active,
            'monitor_running': monitor.running
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/test/simulate-puncture', methods=['POST'])
def api_simulate_puncture():
    """Simulate a tire puncture for testing."""
    try:
        data = request.json or {}
        tire_position = data.get('tire_position', 'front_left')
        
        monitor.simulate_puncture(tire_position)
        
        return jsonify({
            'ok': True,
            'message': f'Puncture simulated for {tire_position}'
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/test/set-pressure', methods=['POST'])
def api_set_pressure():
    """Manually set tire pressure for testing."""
    try:
        data = request.json or {}
        tire_position = data.get('tire_position')
        pressure_psi = float(data.get('pressure_psi', 0))
        
        if not tire_position or pressure_psi < 0:
            return jsonify({
                'ok': False,
                'error': 'Valid tire position and pressure required'
            }), 400
        
        monitor.set_pressure(tire_position, pressure_psi)
        
        return jsonify({
            'ok': True,
            'tire_position': tire_position,
            'pressure_psi': pressure_psi
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/test/set-temperature', methods=['POST'])
def api_set_temperature():
    """Manually set tire temperature for testing."""
    try:
        data = request.json or {}
        tire_position = data.get('tire_position')
        temperature_f = float(data.get('temperature_f', 0))
        
        if not tire_position:
            return jsonify({
                'ok': False,
                'error': 'Tire position required'
            }), 400
        
        monitor.set_temperature(tire_position, temperature_f)
        
        return jsonify({
            'ok': True,
            'tire_position': tire_position,
            'temperature_f': temperature_f
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('TPMS_PORT', 9700))
    
    # Start monitoring automatically
    monitor.set_callbacks(on_reading=on_new_reading, on_alert=on_new_alert)
    monitor.start()
    monitoring_active = True
    Thread(target=monitoring_loop, daemon=True).start()
    
    print(f"TPMS Monitor Service starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
