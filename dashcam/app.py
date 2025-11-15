#!/usr/bin/env python3
"""
Dash Cam Recorder Service
Continuous front/rear recording with cloud backup and incident detection
Port: 10100
"""

import os
import sys
import uuid
import threading
import time
import requests
from pathlib import Path
from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.dashcam.database import DashcamDatabase
from services.dashcam.recorder import LoopRecorder
from services.dashcam.incidents import IncidentDetector
from services.dashcam.cloud import CloudBackupService

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dashcam-recorder-secret-key')
CORS(app)

db = DashcamDatabase()

recordings_dir = ROOT / 'services' / 'dashcam' / 'recordings'
recordings_dir.mkdir(parents=True, exist_ok=True)

recorder = LoopRecorder(output_dir=recordings_dir, max_storage_gb=128)

def incident_callback(incident):
    """Callback when incident is detected."""
    print(f"\n🚨 INCIDENT DETECTED: {incident['incident_type'].upper()}")
    print(f"   Severity: {incident['severity']}")
    print(f"   G-Force: {incident['g_force_value']:.3f}g\n")
    
    try:
        camera_system = get_camera_system()
        gps_tracker = get_gps_tracker()
        
        clip_result = recorder.record_incident_clip(
            camera_system=camera_system,
            incident_id=incident['incident_id'],
            duration_seconds=30,
            gps_tracker=gps_tracker
        )
        
        if clip_result.get('ok'):
            location = incident.get('location', {})
            
            incident_db_id = db.create_incident(
                incident_id=incident['incident_id'],
                incident_type=incident['incident_type'],
                severity=incident['severity'],
                g_force_value=incident['g_force_value'],
                speed_kmh=incident.get('speed_kmh'),
                location_lat=location.get('latitude'),
                location_lng=location.get('longitude'),
                video_clip_path=clip_result['video_path'],
                metadata=incident
            )
            
            if cloud_backup.enabled:
                cloud_backup.queue_upload(
                    incident_id=incident['incident_id'],
                    file_path=clip_result['video_path'],
                    file_size_mb=clip_result['file_size_mb'],
                    priority=True
                )
    
    except Exception as e:
        print(f"Error processing incident: {e}")

incident_detector = IncidentDetector(callback=incident_callback)

def cloud_upload_callback(upload_result):
    """Callback when cloud upload completes."""
    if upload_result['status'] == 'completed':
        print(f"✓ Cloud upload completed: {upload_result['incident_id']}")
        
        if upload_result.get('incident_id'):
            db.mark_incident_uploaded(
                incident_id=upload_result['incident_id'],
                cloud_url=upload_result.get('cloud_url')
            )

cloud_backup = CloudBackupService(callback=cloud_upload_callback)

monitoring_active = False
monitoring_thread = None

battery_state = {
    'voltage': 12.6,
    'temperature': 25.0,
    'charging': False,
    'low_voltage_cutoff': 11.8
}

parking_mode_state = {
    'active': False,
    'motion_sensitivity': 0.7,
    'time_lapse': False,
    'triggered_at': None
}


def get_camera_system():
    """Get camera system from camera service."""
    try:
        camera_url = "http://localhost:7300"
        response = requests.get(f"{camera_url}/health", timeout=2)
        if response.status_code == 200:
            from services.cameras.camera import CameraSystem
            return CameraSystem()
    except:
        pass
    
    from services.cameras.camera import CameraSystem
    return CameraSystem()


def get_gps_tracker():
    """Get GPS tracker from security service."""
    try:
        security_url = "http://localhost:9300"
        response = requests.get(f"{security_url}/health", timeout=2)
        if response.status_code == 200:
            from services.security.gps import GPSTracker
            return GPSTracker()
    except:
        pass
    
    from services.security.gps import GPSTracker
    return GPSTracker()


def monitoring_loop():
    """Background monitoring for incidents and battery."""
    global monitoring_active
    
    while monitoring_active:
        try:
            if incident_detector.enabled:
                gps_tracker = get_gps_tracker()
                location = gps_tracker.get_current_location()
                
                incident = incident_detector.detect_incident(
                    speed_kmh=location.get('speed_kmh', 0),
                    location=location
                )
                
                incident_detector.detect_honk()
            
            if parking_mode_state['active']:
                motion_detected = (os.urandom(1)[0] / 255.0) < parking_mode_state['motion_sensitivity']
                if motion_detected:
                    incident_detector.simulate_parking_mode_event(motion_detected=True)
            
            if battery_state['voltage'] < battery_state['low_voltage_cutoff']:
                print(f"⚠️ Low battery: {battery_state['voltage']}V - Stopping recording")
                if recorder.is_recording():
                    recorder.stop_continuous_recording()
        
        except Exception as e:
            print(f"Monitoring error: {e}")
        
        time.sleep(2)


def start_monitoring():
    """Start background monitoring."""
    global monitoring_active, monitoring_thread
    
    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        print("✓ Dashcam monitoring started")


def stop_monitoring():
    """Stop background monitoring."""
    global monitoring_active
    monitoring_active = False
    print("✓ Dashcam monitoring stopped")


@app.route('/')
def index():
    """Serve the dashcam dashboard."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('DASHCAM_PORT', 10100))
    return jsonify({
        'ok': True,
        'service': 'dashcam_recorder',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'continuous_recording': recorder.is_recording(),
        'monitoring_active': monitoring_active,
        'parking_mode': parking_mode_state['active']
    })


@app.route('/api/status')
def api_status():
    """Get complete dashcam status."""
    return jsonify({
        'ok': True,
        'recorder': recorder.get_status(),
        'incident_detector': incident_detector.get_status(),
        'cloud_backup': cloud_backup.get_status(),
        'battery': battery_state,
        'parking_mode': parking_mode_state,
        'monitoring_active': monitoring_active,
        'stats': db.get_stats()
    })


@app.route('/api/recording/start', methods=['POST'])
def api_start_recording():
    """Start continuous recording."""
    try:
        data = request.json or {}
        camera_layout = data.get('camera_layout', 'dual')
        quality = data.get('quality', '1080p')
        
        if recorder.is_recording():
            return jsonify({'ok': False, 'error': 'Recording already active'}), 400
        
        camera_system = get_camera_system()
        gps_tracker = get_gps_tracker()
        
        result = recorder.start_continuous_recording(
            camera_system=camera_system,
            camera_layout=camera_layout,
            quality=quality,
            gps_tracker=gps_tracker
        )
        
        if result.get('ok'):
            start_monitoring()
            
            db.set_setting('continuous_recording', 'true')
            db.set_setting('recording_quality', quality)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/recording/stop', methods=['POST'])
def api_stop_recording():
    """Stop continuous recording."""
    try:
        result = recorder.stop_continuous_recording()
        
        if result.get('ok'):
            db.set_setting('continuous_recording', 'false')
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/recording/snapshot', methods=['POST'])
def api_capture_snapshot():
    """Capture manual snapshot."""
    try:
        data = request.json or {}
        reason = data.get('reason', 'manual')
        
        camera_system = get_camera_system()
        result = recorder.capture_snapshot(camera_system, reason=reason)
        
        if result.get('ok'):
            snapshot_event = incident_detector.trigger_manual_snapshot(reason=reason)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/incidents')
def api_get_incidents():
    """Get incident log."""
    try:
        limit = int(request.args.get('limit', 100))
        incident_type = request.args.get('type')
        
        incidents = db.get_incidents(limit=limit, incident_type=incident_type)
        
        return jsonify({
            'ok': True,
            'incidents': incidents,
            'count': len(incidents)
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/incidents/<incident_id>')
def api_get_incident(incident_id):
    """Get specific incident details."""
    try:
        incident = db.get_incident(incident_id)
        
        if not incident:
            return jsonify({'ok': False, 'error': 'Incident not found'}), 404
        
        return jsonify({
            'ok': True,
            'incident': incident
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/incidents/simulate', methods=['POST'])
def api_simulate_incident():
    """Simulate incident for testing."""
    try:
        data = request.json or {}
        incident_type = data.get('incident_type', 'hard_braking')
        g_force = data.get('g_force', 0.8)
        
        gps_tracker = get_gps_tracker()
        location = gps_tracker.get_current_location()
        
        g_force_vector = {
            'x': -g_force if incident_type == 'hard_braking' else g_force * 0.5,
            'y': g_force * 0.3 if incident_type == 'sharp_turn' else 0.2,
            'z': 1.0 + (g_force * 0.2)
        }
        
        incident = incident_detector.detect_incident(
            g_force=g_force_vector,
            speed_kmh=location.get('speed_kmh', 60),
            location=location
        )
        
        if incident:
            return jsonify({
                'ok': True,
                'incident': incident,
                'message': 'Incident simulated successfully'
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'Failed to trigger incident'
            }), 400
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/recordings')
def api_get_recordings():
    """Get recording list."""
    try:
        limit = int(request.args.get('limit', 100))
        protected_only = request.args.get('protected', 'false').lower() == 'true'
        
        recordings = db.get_recordings(limit=limit, protected_only=protected_only)
        
        return jsonify({
            'ok': True,
            'recordings': recordings,
            'count': len(recordings)
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/recordings/<recording_id>/protect', methods=['POST'])
def api_protect_recording(recording_id):
    """Mark recording as protected."""
    try:
        data = request.json or {}
        protected = data.get('protected', True)
        
        success = db.set_recording_protected(recording_id, protected)
        
        return jsonify({
            'ok': success,
            'recording_id': recording_id,
            'protected': protected
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/recordings/<recording_id>/delete', methods=['DELETE'])
def api_delete_recording(recording_id):
    """Delete unprotected recording."""
    try:
        success = db.delete_recording(recording_id)
        
        if success:
            return jsonify({'ok': True, 'recording_id': recording_id, 'deleted': True})
        else:
            return jsonify({
                'ok': False,
                'error': 'Cannot delete protected recording or recording not found'
            }), 400
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/storage')
def api_get_storage():
    """Get storage statistics."""
    try:
        storage_stats = recorder.get_storage_stats()
        db_stats = db.get_stats()
        
        return jsonify({
            'ok': True,
            'storage': storage_stats,
            'database': db_stats
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/storage/cleanup', methods=['POST'])
def api_cleanup_storage():
    """Cleanup old unprotected recordings."""
    try:
        data = request.json or {}
        keep_count = data.get('keep_count', 100)
        
        deleted_count = db.delete_old_recordings(keep_count=keep_count)
        
        return jsonify({
            'ok': True,
            'deleted_count': deleted_count,
            'message': f'Deleted {deleted_count} old recordings'
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/cloud/queue', methods=['POST'])
def api_queue_cloud_upload():
    """Queue file for cloud upload."""
    try:
        data = request.json or {}
        incident_id = data.get('incident_id')
        
        if not incident_id:
            return jsonify({'ok': False, 'error': 'incident_id required'}), 400
        
        incident = db.get_incident(incident_id)
        if not incident:
            return jsonify({'ok': False, 'error': 'Incident not found'}), 404
        
        file_path = incident['video_clip_path']
        file_size_mb = 5.0
        
        result = cloud_backup.queue_upload(
            incident_id=incident_id,
            file_path=file_path,
            file_size_mb=file_size_mb,
            priority=data.get('priority', False)
        )
        
        if result.get('ok'):
            upload_id = result['upload_id']
            db.create_cloud_upload(
                upload_id=upload_id,
                incident_id=incident_id,
                file_path=file_path,
                file_size_mb=file_size_mb,
                wifi_connected=cloud_backup.wifi_connected
            )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/cloud/status')
def api_cloud_status():
    """Get cloud backup status."""
    try:
        status = cloud_backup.get_status()
        queue = cloud_backup.get_queue()
        history = cloud_backup.get_upload_history(limit=20)
        
        return jsonify({
            'ok': True,
            'status': status,
            'queue': queue,
            'recent_uploads': history
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/cloud/wifi', methods=['POST'])
def api_set_wifi():
    """Set WiFi connection status."""
    try:
        data = request.json or {}
        connected = data.get('connected', False)
        
        cloud_backup.set_wifi_connected(connected)
        
        return jsonify({
            'ok': True,
            'wifi_connected': connected,
            'message': f"WiFi {'connected' if connected else 'disconnected'}"
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/parking_mode', methods=['POST'])
def api_set_parking_mode():
    """Enable/disable parking mode."""
    try:
        data = request.json or {}
        active = data.get('active', False)
        
        parking_mode_state['active'] = active
        parking_mode_state['motion_sensitivity'] = data.get('sensitivity', 0.7)
        parking_mode_state['time_lapse'] = data.get('time_lapse', False)
        
        if active:
            parking_mode_state['triggered_at'] = datetime.now().isoformat()
            db.set_setting('parking_mode_enabled', 'true')
            
            if not monitoring_active:
                start_monitoring()
        else:
            db.set_setting('parking_mode_enabled', 'false')
        
        return jsonify({
            'ok': True,
            'parking_mode': parking_mode_state
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/battery', methods=['POST'])
def api_update_battery():
    """Update battery status."""
    try:
        data = request.json or {}
        
        battery_state['voltage'] = data.get('voltage', battery_state['voltage'])
        battery_state['temperature'] = data.get('temperature', battery_state['temperature'])
        battery_state['charging'] = data.get('charging', battery_state['charging'])
        
        return jsonify({
            'ok': True,
            'battery': battery_state
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """Get or update settings."""
    try:
        if request.method == 'GET':
            settings = db.get_all_settings()
            return jsonify({
                'ok': True,
                'settings': settings
            })
        
        else:
            data = request.json or {}
            
            for key, value in data.items():
                db.set_setting(key, str(value))
            
            if 'g_sensor_sensitivity' in data:
                incident_detector.set_sensitivity(float(data['g_sensor_sensitivity']))
            
            if 'cloud_backup_enabled' in data:
                cloud_backup.set_enabled(data['cloud_backup_enabled'].lower() == 'true')
            
            if 'cloud_auto_upload_wifi' in data:
                cloud_backup.set_auto_upload_wifi(data['cloud_auto_upload_wifi'].lower() == 'true')
            
            if 'timestamp_overlay' in data:
                recorder.timestamp_overlay = data['timestamp_overlay'].lower() == 'true'
            
            if 'gps_overlay' in data:
                recorder.gps_overlay = data['gps_overlay'].lower() == 'true'
            
            return jsonify({
                'ok': True,
                'message': 'Settings updated successfully'
            })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/stats')
def api_get_stats():
    """Get comprehensive statistics."""
    try:
        db_stats = db.get_stats()
        storage_stats = recorder.get_storage_stats()
        cloud_stats = cloud_backup.get_cloud_storage_stats()
        
        return jsonify({
            'ok': True,
            'database': db_stats,
            'storage': storage_stats,
            'cloud': cloud_stats,
            'recorder': {
                'continuous_recording_active': recorder.is_recording(),
                'parking_mode_active': parking_mode_state['active']
            }
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('DASHCAM_PORT', 10100))
    
    print(f"""
╔════════════════════════════════════════════════╗
║      DASH CAM RECORDER SERVICE                 ║
║      Port: {port}                              ║
╚════════════════════════════════════════════════╝
    """)
    
    start_monitoring()
    
    app.run(host='0.0.0.0', port=port, debug=False)
