#!/usr/bin/env python3
"""
Security System Integration Service
Motion detection, theft alerts, GPS tracking, and stolen vehicle recovery
Port: 9300
"""

import os
import sys
import uuid
import threading
import time
import requests
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.security.database import SecurityDatabase
from services.security.motion import MotionDetector
from services.security.alerts import AlertSystem
from services.security.gps import GPSTracker

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'security-system-secret-key')
CORS(app)

db = SecurityDatabase()
motion_detector = MotionDetector()
alert_system = AlertSystem()
gps_tracker = GPSTracker()

snapshots_dir = ROOT / 'services' / 'security' / 'snapshots'
snapshots_dir.mkdir(parents=True, exist_ok=True)

monitoring_active = False
monitoring_thread = None

door_states = {
    'driver': {'open': False, 'authorized': True},
    'passenger': {'open': False, 'authorized': True},
    'rear_left': {'open': False, 'authorized': True},
    'rear_right': {'open': False, 'authorized': True}
}

battery_state = {
    'voltage': 12.6,
    'connected': True,
    'temperature': 25.0
}


def alert_callback(alert):
    """Callback for when alerts are triggered."""
    print(f"\n🚨 [{alert['severity'].upper()}] {alert['title']}")
    print(f"   {alert['message']}\n")
    
    db.create_alert(
        alert_id=alert['alert_id'],
        alert_type=alert['alert_type'],
        title=alert['title'],
        message=alert['message'],
        severity=alert['severity'],
        triggered_by=alert.get('triggered_by')
    )
    
    event_id = f"event_{uuid.uuid4().hex[:12]}"
    db.log_event(
        event_id=event_id,
        event_type=alert['alert_type'],
        severity=alert['severity'],
        description=alert['message'],
        metadata=alert.get('metadata')
    )
    
    if alert['severity'] == 'critical' and motion_detector.armed:
        _trigger_camera_recording(alert)


def _trigger_camera_recording(alert):
    """Trigger camera recording for security events."""
    try:
        camera_url = "http://localhost:7300"
        response = requests.post(
            f"{camera_url}/api/recordings/start",
            json={
                'camera_layout': 'quad',
                'recording_type': 'security_trigger',
                'trigger_event': alert['alert_type']
            },
            timeout=2
        )
        if response.status_code == 200:
            print(f"✓ Camera recording started for {alert['alert_type']}")
    except Exception as e:
        print(f"Camera recording trigger failed: {e}")


alert_system.register_callback(alert_callback)


def monitoring_loop():
    """Background monitoring thread."""
    global monitoring_active
    
    while monitoring_active:
        try:
            if motion_detector.armed:
                detections = motion_detector.detect_motion_all_cameras()
                
                for detection in detections:
                    db.log_motion_detection(
                        detection_id=detection['detection_id'],
                        camera_position=detection['camera_position'],
                        detection_type=detection.get('detection_type', 'motion'),
                        confidence=detection['confidence'],
                        person_detected=detection.get('person_detected', False),
                        bounding_boxes=detection.get('bounding_boxes'),
                        system_armed=True,
                        alert_triggered=True
                    )
                    
                    alert_system.motion_alert(
                        camera_position=detection['camera_position'],
                        person_detected=detection.get('person_detected', False),
                        person_count=detection.get('person_count', 0),
                        confidence=detection['confidence']
                    )
            
            location = gps_tracker.get_current_location()
            db.log_gps_location(
                track_id=gps_tracker.track_id,
                latitude=location['latitude'],
                longitude=location['longitude'],
                altitude=location.get('altitude'),
                speed_kmh=location.get('speed_kmh'),
                heading=location.get('heading'),
                accuracy_meters=location.get('accuracy_meters')
            )
            
            geofence_violations = gps_tracker.check_geofences(location)
            for violation in geofence_violations:
                alert_system.geofence_alert(
                    fence_name=violation['fence_name'],
                    event_type=violation['event_type'],
                    location=violation['location']
                )
            
            if battery_state['connected']:
                db.log_battery_status(
                    voltage=battery_state['voltage'],
                    temperature_celsius=battery_state['temperature'],
                    status='normal' if battery_state['voltage'] > 12.0 else 'low'
                )
                
                alert_system.battery_alert(
                    voltage=battery_state['voltage'],
                    disconnected=False
                )
            
        except Exception as e:
            print(f"Monitoring error: {e}")
        
        time.sleep(3)


def start_monitoring():
    """Start background monitoring."""
    global monitoring_active, monitoring_thread
    
    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        print("✓ Security monitoring started")


def stop_monitoring():
    """Stop background monitoring."""
    global monitoring_active
    monitoring_active = False
    print("✓ Security monitoring stopped")


@app.route('/')
def index():
    """Serve the security dashboard."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('SECURITY_PORT', 9300))
    return jsonify({
        'ok': True,
        'service': 'security_system_integration',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'monitoring_active': monitoring_active,
        'system_armed': motion_detector.armed,
        'panic_mode': alert_system.panic_mode_active,
        'stolen_mode': gps_tracker.stolen_mode_active
    })


@app.route('/api/status')
def api_status():
    """Get complete security system status."""
    return jsonify({
        'ok': True,
        'system_armed': motion_detector.armed,
        'monitoring_active': monitoring_active,
        'motion_detection': motion_detector.get_detection_summary(),
        'alerts': alert_system.get_status(),
        'gps': gps_tracker.get_status(),
        'panic_mode': alert_system.panic_mode_active,
        'stolen_mode': gps_tracker.stolen_mode_active,
        'battery': battery_state,
        'doors': door_states
    })


@app.route('/api/arm', methods=['POST'])
def api_arm_system():
    """Arm the security system."""
    try:
        data = request.json or {}
        armed = data.get('armed', True)
        
        motion_detector.set_armed(armed)
        
        if armed:
            start_monitoring()
            db.set_setting('system_armed', 'true')
            message = "Security system ARMED - Motion detection active"
        else:
            db.set_setting('system_armed', 'false')
            message = "Security system DISARMED"
        
        event_id = f"event_{uuid.uuid4().hex[:12]}"
        db.log_event(
            event_id=event_id,
            event_type='system_arm_change',
            severity='info',
            description=message
        )
        
        return jsonify({
            'ok': True,
            'armed': armed,
            'message': message,
            'monitoring_active': monitoring_active
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/motion/detect', methods=['POST'])
def api_detect_motion():
    """Manually trigger motion detection."""
    try:
        data = request.json or {}
        camera_position = data.get('camera_position', 'all')
        
        if camera_position == 'all':
            detections = motion_detector.detect_motion_all_cameras()
        else:
            detection = motion_detector.detect_motion(camera_position)
            detections = [detection] if detection else []
        
        for detection in detections:
            db.log_motion_detection(
                detection_id=detection['detection_id'],
                camera_position=detection['camera_position'],
                detection_type=detection.get('detection_type', 'motion'),
                confidence=detection['confidence'],
                person_detected=detection.get('person_detected', False),
                bounding_boxes=detection.get('bounding_boxes'),
                system_armed=motion_detector.armed
            )
        
        return jsonify({
            'ok': True,
            'detections': detections,
            'count': len(detections)
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/motion/sensitivity', methods=['POST'])
def api_set_motion_sensitivity():
    """Set motion detection sensitivity."""
    try:
        data = request.json or {}
        sensitivity = float(data.get('sensitivity', 0.5))
        
        motion_detector.set_sensitivity(sensitivity)
        db.set_setting('motion_sensitivity', str(sensitivity))
        
        return jsonify({
            'ok': True,
            'sensitivity': sensitivity
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/alerts')
def api_get_alerts():
    """Get recent alerts."""
    try:
        limit = int(request.args.get('limit', 50))
        acknowledged = request.args.get('acknowledged')
        
        if acknowledged is not None:
            acknowledged = acknowledged.lower() == 'true'
        
        db_alerts = db.get_recent_alerts(limit, acknowledged)
        active_alerts = alert_system.get_active_alerts()
        
        return jsonify({
            'ok': True,
            'alerts': db_alerts,
            'active': active_alerts,
            'count': len(db_alerts)
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
def api_acknowledge_alert(alert_id):
    """Acknowledge an alert."""
    try:
        success = alert_system.acknowledge_alert(alert_id)
        
        if success:
            db.acknowledge_alert(alert_id)
        
        return jsonify({
            'ok': success,
            'alert_id': alert_id,
            'acknowledged': success
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/door', methods=['POST'])
def api_door_event():
    """Simulate door open/close event."""
    try:
        data = request.json or {}
        door_location = data.get('door_location', 'driver')
        is_open = data.get('open', True)
        authorized = data.get('authorized', False)
        
        if door_location in door_states:
            door_states[door_location]['open'] = is_open
            door_states[door_location]['authorized'] = authorized
        
        if is_open and motion_detector.armed:
            alert_system.door_alert(door_location, authorized)
        
        return jsonify({
            'ok': True,
            'door_location': door_location,
            'open': is_open,
            'authorized': authorized
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ignition', methods=['POST'])
def api_ignition_event():
    """Simulate ignition event."""
    try:
        data = request.json or {}
        ignition_on = data.get('ignition_on', True)
        key_present = data.get('key_present', False)
        
        if ignition_on and motion_detector.armed:
            alert_system.ignition_alert(key_present)
        
        return jsonify({
            'ok': True,
            'ignition_on': ignition_on,
            'key_present': key_present
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/tow', methods=['POST'])
def api_tow_detection():
    """Simulate tow-away detection."""
    try:
        data = request.json or {}
        acceleration = float(data.get('acceleration', 0.5))
        tilt_angle = float(data.get('tilt_angle', 15.0))
        
        if motion_detector.armed:
            alert_system.tow_away_alert(acceleration, tilt_angle)
        
        return jsonify({
            'ok': True,
            'acceleration': acceleration,
            'tilt_angle': tilt_angle,
            'alert_triggered': motion_detector.armed
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/battery', methods=['GET', 'POST'])
def api_battery():
    """Get or update battery status."""
    global battery_state
    
    try:
        if request.method == 'POST':
            data = request.json or {}
            
            if 'voltage' in data:
                battery_state['voltage'] = float(data['voltage'])
            if 'connected' in data:
                battery_state['connected'] = data['connected']
            if 'temperature' in data:
                battery_state['temperature'] = float(data['temperature'])
            
            db.log_battery_status(
                voltage=battery_state['voltage'],
                temperature_celsius=battery_state['temperature'],
                status='normal' if battery_state['connected'] else 'disconnected',
                alert_triggered=not battery_state['connected']
            )
            
            if not battery_state['connected'] and motion_detector.armed:
                alert_system.battery_alert(
                    voltage=battery_state['voltage'],
                    disconnected=True
                )
        
        history = db.get_battery_history(limit=100)
        
        return jsonify({
            'ok': True,
            'current': battery_state,
            'history': history
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/gps/location')
def api_get_location():
    """Get current GPS location."""
    try:
        location = gps_tracker.get_current_location()
        
        return jsonify({
            'ok': True,
            'location': location
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/gps/history')
def api_get_location_history():
    """Get GPS location history."""
    try:
        limit = int(request.args.get('limit', 100))
        
        history = gps_tracker.get_location_history(limit)
        route_summary = gps_tracker.get_route_summary()
        
        return jsonify({
            'ok': True,
            'history': history,
            'summary': route_summary,
            'count': len(history)
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/gps/geofences', methods=['GET', 'POST'])
def api_geofences():
    """Get or create geofences."""
    try:
        if request.method == 'POST':
            data = request.json or {}
            
            geofence = gps_tracker.create_geofence(
                fence_name=data['fence_name'],
                center_lat=float(data['center_lat']),
                center_lng=float(data['center_lng']),
                radius_meters=float(data.get('radius_meters', 1000)),
                alert_on_exit=data.get('alert_on_exit', True),
                alert_on_entry=data.get('alert_on_entry', False)
            )
            
            db.create_geofence(
                fence_id=geofence['fence_id'],
                fence_name=geofence['fence_name'],
                center_lat=geofence['center_lat'],
                center_lng=geofence['center_lng'],
                radius_meters=geofence['radius_meters'],
                alert_on_exit=geofence['alert_on_exit'],
                alert_on_entry=geofence['alert_on_entry']
            )
            
            return jsonify({
                'ok': True,
                'geofence': geofence
            })
        else:
            geofences = gps_tracker.get_geofences()
            
            return jsonify({
                'ok': True,
                'geofences': geofences,
                'count': len(geofences)
            })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/gps/geofences/<fence_id>', methods=['PUT', 'DELETE'])
def api_update_geofence(fence_id):
    """Update or delete a geofence."""
    try:
        if request.method == 'DELETE':
            success = gps_tracker.delete_geofence(fence_id)
            
            return jsonify({
                'ok': success,
                'fence_id': fence_id,
                'deleted': success
            })
        else:
            data = request.json or {}
            success = gps_tracker.update_geofence(fence_id, **data)
            
            if success:
                db.update_geofence(fence_id, **data)
            
            return jsonify({
                'ok': success,
                'fence_id': fence_id,
                'updated': success
            })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/stolen_mode', methods=['POST'])
def api_stolen_mode():
    """Enable/disable stolen vehicle recovery mode."""
    try:
        data = request.json or {}
        enabled = data.get('enabled', True)
        
        if enabled:
            result = gps_tracker.enable_stolen_mode()
            db.set_setting('stolen_mode', 'true')
            
            event_id = f"event_{uuid.uuid4().hex[:12]}"
            db.log_event(
                event_id=event_id,
                event_type='stolen_mode_activated',
                severity='critical',
                description='Stolen vehicle recovery mode activated'
            )
        else:
            result = gps_tracker.disable_stolen_mode()
            db.set_setting('stolen_mode', 'false')
        
        return jsonify({
            'ok': True,
            **result
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/panic', methods=['POST'])
def api_panic_mode():
    """Activate or deactivate panic mode."""
    try:
        data = request.json or {}
        activate = data.get('activate', True)
        
        if activate:
            alert = alert_system.activate_panic_mode(
                trigger_source=data.get('trigger_source', 'manual')
            )
            
            db.set_setting('panic_mode', 'true')
            
            return jsonify({
                'ok': True,
                'panic_mode_active': True,
                'alert': alert
            })
        else:
            result = alert_system.deactivate_panic_mode()
            db.set_setting('panic_mode', 'false')
            
            return jsonify({
                'ok': True,
                **result
            })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/events')
def api_get_events():
    """Get recent security events."""
    try:
        limit = int(request.args.get('limit', 50))
        event_type = request.args.get('event_type')
        
        events = db.get_recent_events(limit, event_type)
        
        return jsonify({
            'ok': True,
            'events': events,
            'count': len(events)
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/notifications/config', methods=['GET', 'POST'])
def api_notification_config():
    """Configure notification settings."""
    try:
        if request.method == 'POST':
            data = request.json or {}
            
            config = alert_system.configure_notifications(
                sms=data.get('sms_enabled', True),
                email=data.get('email_enabled', True),
                push=data.get('push_enabled', True)
            )
            
            return jsonify({
                'ok': True,
                'config': config
            })
        else:
            status = alert_system.get_status()
            
            return jsonify({
                'ok': True,
                'config': status['notifications']
            })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/monitoring/start', methods=['POST'])
def api_start_monitoring():
    """Start security monitoring."""
    try:
        start_monitoring()
        
        return jsonify({
            'ok': True,
            'monitoring_active': True
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/monitoring/stop', methods=['POST'])
def api_stop_monitoring():
    """Stop security monitoring."""
    try:
        stop_monitoring()
        
        return jsonify({
            'ok': True,
            'monitoring_active': False
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('SECURITY_PORT', 9300))
    
    print("=" * 60)
    print("Security System Integration Service")
    print("=" * 60)
    print(f"🔒 Starting on port {port}")
    print("✓ Motion detection ready")
    print("✓ Theft alert system ready")
    print("✓ GPS tracking ready")
    print("✓ Panic mode ready")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=True)
