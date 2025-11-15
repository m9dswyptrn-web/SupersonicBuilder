#!/usr/bin/env python3
"""
Advanced Climate Control UI Service
Beautiful HVAC control for QLED display with Maestro RR2 integration
Port: 8800
"""

import os
import sys
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, request, render_template
from flask_cors import CORS
from datetime import datetime
import logging

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.climate.hvac import HVACController
from services.climate.maestro_bridge import MaestroBridge
from services.climate.database import ClimateDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

TEMPLATE_DIR = Path(__file__).parent / 'templates'
STATIC_DIR = Path(__file__).parent / 'static'

hvac = HVACController(multi_zone=True, rear_zone=False)
maestro = MaestroBridge()
db = ClimateDatabase()


@app.route('/')
def index():
    """Serve the climate control UI."""
    return render_template('index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory(STATIC_DIR, filename)


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'ok': True,
        'service': 'Climate Control UI',
        'port': 8800,
        'maestro_connected': maestro.connected,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/status')
def api_status():
    """Get current climate status."""
    state = hvac.get_state()
    
    if maestro.connected:
        vehicle_data = maestro.get_vehicle_data()
        if vehicle_data and 'outside_temp' in vehicle_data:
            hvac.update_outside_temp(vehicle_data['outside_temp'], 'C')
            state = hvac.get_state()
    
    return jsonify({
        'ok': True,
        'state': state,
        'maestro_connected': maestro.connected
    })


@app.route('/api/temperature', methods=['POST'])
def api_set_temperature():
    """Set temperature for a zone."""
    try:
        data = request.json
        temp = float(data.get('temperature'))
        zone = data.get('zone', 'driver')
        unit = data.get('unit', 'C')
        
        state = hvac.set_temperature(temp, zone, unit)
        
        if maestro.connected and zone == 'driver':
            if unit == 'F':
                temp_c = (temp - 32) * 5/9
            else:
                temp_c = temp
            maestro.send_temperature_command(temp_c, zone)
        
        return jsonify({
            'ok': True,
            'state': state
        })
    except Exception as e:
        logger.error(f"Error setting temperature: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/fan', methods=['POST'])
def api_set_fan():
    """Set fan speed."""
    try:
        data = request.json
        speed = int(data.get('speed'))
        zone = data.get('zone', 'driver')
        
        state = hvac.set_fan_speed(speed, zone)
        
        if maestro.connected and zone == 'driver':
            maestro.send_fan_command(speed)
        
        return jsonify({
            'ok': True,
            'state': state
        })
    except Exception as e:
        logger.error(f"Error setting fan speed: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/mode', methods=['POST'])
def api_set_mode():
    """Set HVAC mode."""
    try:
        data = request.json
        mode = data.get('mode')
        
        state = hvac.set_mode(mode)
        
        return jsonify({
            'ok': True,
            'state': state
        })
    except Exception as e:
        logger.error(f"Error setting mode: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/ac', methods=['POST'])
def api_toggle_ac():
    """Toggle AC on/off."""
    state = hvac.toggle_ac()
    
    if maestro.connected:
        maestro.send_ac_command(state['ac_enabled'])
    
    return jsonify({
        'ok': True,
        'state': state
    })


@app.route('/api/max-ac', methods=['POST'])
def api_set_max_ac():
    """Set max AC mode."""
    try:
        data = request.json
        enabled = data.get('enabled', True)
        
        state = hvac.set_max_ac(enabled)
        
        return jsonify({
            'ok': True,
            'state': state
        })
    except Exception as e:
        logger.error(f"Error setting max AC: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/recirculation', methods=['POST'])
def api_toggle_recirculation():
    """Toggle recirculation mode."""
    state = hvac.toggle_recirculation()
    
    if maestro.connected:
        maestro.send_recirculation_command(state['recirculation'])
    
    return jsonify({
        'ok': True,
        'state': state
    })


@app.route('/api/defrost', methods=['POST'])
def api_toggle_defrost():
    """Toggle defrost."""
    try:
        data = request.json
        location = data.get('location', 'front')
        
        state = hvac.toggle_defrost(location)
        
        if maestro.connected:
            maestro.send_defrost_command(location, state[f'defrost_{location}'])
        
        return jsonify({
            'ok': True,
            'state': state
        })
    except Exception as e:
        logger.error(f"Error toggling defrost: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/heated-mirrors', methods=['POST'])
def api_toggle_heated_mirrors():
    """Toggle heated mirrors."""
    state = hvac.toggle_heated_mirrors()
    
    return jsonify({
        'ok': True,
        'state': state
    })


@app.route('/api/auto', methods=['POST'])
def api_set_auto():
    """Set auto climate mode."""
    try:
        data = request.json
        enabled = data.get('enabled', True)
        
        state = hvac.set_auto_mode(enabled)
        
        if maestro.connected:
            maestro.send_auto_command(enabled)
        
        return jsonify({
            'ok': True,
            'state': state
        })
    except Exception as e:
        logger.error(f"Error setting auto mode: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/heated-seat', methods=['POST'])
def api_set_heated_seat():
    """Set heated seat level."""
    try:
        data = request.json
        level = int(data.get('level'))
        seat = data.get('seat', 'driver')
        
        state = hvac.set_heated_seat(level, seat)
        
        return jsonify({
            'ok': True,
            'state': state
        })
    except Exception as e:
        logger.error(f"Error setting heated seat: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/presets')
def api_list_presets():
    """List all climate presets."""
    presets = db.list_presets()
    
    return jsonify({
        'ok': True,
        'presets': presets
    })


@app.route('/api/preset/<preset_name>')
def api_load_preset(preset_name):
    """Load a specific preset."""
    preset = db.load_preset(preset_name)
    
    if not preset:
        return jsonify({'ok': False, 'error': 'Preset not found'}), 404
    
    return jsonify({
        'ok': True,
        'preset': preset
    })


@app.route('/api/preset/apply/<preset_name>', methods=['POST'])
def api_apply_preset(preset_name):
    """Apply a climate preset."""
    try:
        preset = db.load_preset(preset_name)
        
        if not preset:
            return jsonify({'ok': False, 'error': 'Preset not found'}), 404
        
        state = hvac.apply_preset(preset)
        
        if maestro.connected:
            if preset.get('temp_driver'):
                maestro.send_temperature_command(preset['temp_driver'], 'driver')
            if preset.get('fan_speed') is not None:
                maestro.send_fan_command(preset['fan_speed'])
            if preset.get('ac_enabled') is not None:
                maestro.send_ac_command(preset['ac_enabled'])
            if preset.get('auto_mode') is not None:
                maestro.send_auto_command(preset['auto_mode'])
        
        return jsonify({
            'ok': True,
            'preset_name': preset_name,
            'state': state
        })
    except Exception as e:
        logger.error(f"Error applying preset: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/preset/save', methods=['POST'])
def api_save_preset():
    """Save current state as a preset."""
    try:
        data = request.json
        preset_name = data.get('preset_name')
        description = data.get('description', '')
        
        if not preset_name:
            return jsonify({'ok': False, 'error': 'preset_name required'}), 400
        
        state = hvac.get_state()
        
        preset_data = {
            'preset_name': preset_name,
            'temp_driver': state['driver_zone']['temperature'],
            'temp_passenger': state['passenger_zone']['temperature'] if state['passenger_zone'] else None,
            'temp_rear': state['rear_zone']['temperature'] if state['rear_zone'] else None,
            'fan_speed': state['driver_zone']['fan_speed'],
            'mode': state['mode'],
            'ac_enabled': state['ac_enabled'],
            'recirculation': state['recirculation'],
            'defrost_front': state['defrost_front'],
            'defrost_rear': state['defrost_rear'],
            'auto_mode': state['auto_mode'],
            'heated_seat_driver': state['driver_zone']['heated_seat_level'],
            'heated_seat_passenger': state['passenger_zone']['heated_seat_level'] if state['passenger_zone'] else 0,
            'description': description
        }
        
        preset_id = db.save_preset(preset_data)
        
        return jsonify({
            'ok': True,
            'preset_id': preset_id,
            'message': f'Preset "{preset_name}" saved'
        })
    except Exception as e:
        logger.error(f"Error saving preset: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/preset/delete/<preset_name>', methods=['DELETE'])
def api_delete_preset(preset_name):
    """Delete a preset."""
    success = db.delete_preset(preset_name)
    
    if success:
        return jsonify({
            'ok': True,
            'message': f'Preset "{preset_name}" deleted'
        })
    else:
        return jsonify({'ok': False, 'error': 'Preset not found'}), 404


@app.route('/api/sync', methods=['POST'])
def api_sync_from_vehicle():
    """Sync climate state from vehicle via Maestro."""
    if not maestro.connected:
        return jsonify({
            'ok': False,
            'error': 'Maestro RR2 not connected'
        }), 503
    
    vehicle_climate = maestro.sync_state_from_vehicle()
    
    if vehicle_climate:
        if 'temperature' in vehicle_climate:
            temp_data = vehicle_climate['temperature']
            if 'driver' in temp_data:
                hvac.set_temperature(temp_data['driver'], 'driver', 'C')
        
        if 'fan' in vehicle_climate:
            fan_data = vehicle_climate['fan']
            if 'speed' in fan_data:
                hvac.set_fan_speed(fan_data['speed'], 'driver')
        
        if 'modes' in vehicle_climate:
            modes = vehicle_climate['modes']
            hvac.state.ac_enabled = modes.get('ac', False)
            hvac.state.recirculation = modes.get('recirculation', False)
            hvac.state.defrost_front = modes.get('defrost_front', False)
            hvac.state.auto_mode = modes.get('auto', False)
    
    state = hvac.get_state()
    
    return jsonify({
        'ok': True,
        'state': state,
        'synced': True
    })


@app.route('/api/history')
def api_get_history():
    """Get climate history."""
    hours = int(request.args.get('hours', 24))
    limit = int(request.args.get('limit', 1000))
    
    history = db.get_history(hours, limit)
    
    return jsonify({
        'ok': True,
        'history': history
    })


@app.route('/api/maestro/status')
def api_maestro_status():
    """Get Maestro RR2 connection status."""
    maestro._check_connection()
    
    return jsonify({
        'ok': True,
        'connected': maestro.connected,
        'url': maestro.maestro_url
    })


if __name__ == '__main__':
    logger.info("Starting Advanced Climate Control UI on port 8800")
    logger.info(f"Maestro RR2 connection: {'Connected' if maestro.connected else 'Not connected'}")
    
    app.run(
        host='0.0.0.0',
        port=8800,
        debug=False,
        threaded=True
    )
