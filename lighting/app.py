#!/usr/bin/env python3
"""
RGB Ambient Lighting Controller
Music-reactive car interior lighting with zone control
Port: 8500
"""

import os
import sys
import json
import time
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.lighting.database import LightingDatabase
from services.lighting.led_controller import LEDController
from services.lighting.music_reactive import MusicReactiveEngine
from services.lighting.scenes import SceneManager

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'lighting-controller-secret-key')
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

db = LightingDatabase()
led_controller = LEDController()
music_engine = MusicReactiveEngine(led_controller)
scene_manager = SceneManager(led_controller, db)


@app.route('/')
def index():
    """Serve the main control UI."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('LIGHTING_PORT', 8500))
    return jsonify({
        'ok': True,
        'service': 'rgb_lighting_controller',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'zones_active': sum(1 for z in led_controller.zones.values() if z.enabled),
        'music_reactive': music_engine.running
    })


@app.route('/api/zones')
def api_get_zones():
    """Get status of all zones."""
    try:
        status = led_controller.get_all_zones_status()
        return jsonify({
            'ok': True,
            'status': status
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/zones/<zone_name>')
def api_get_zone(zone_name):
    """Get status of a specific zone."""
    try:
        status = led_controller.get_zone_status(zone_name)
        
        if not status:
            return jsonify({'ok': False, 'error': 'Zone not found'}), 404
        
        return jsonify({
            'ok': True,
            'zone': status
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/zones/<zone_name>/color', methods=['POST'])
def api_set_zone_color(zone_name):
    """Set color for a specific zone."""
    try:
        data = request.json or {}
        r = int(data.get('r', 0))
        g = int(data.get('g', 0))
        b = int(data.get('b', 0))
        
        success = led_controller.set_zone_color(zone_name, r, g, b)
        
        if not success:
            return jsonify({'ok': False, 'error': 'Zone not found'}), 404
        
        socketio.emit('zone_update', {
            'zone': zone_name,
            'color': {'r': r, 'g': g, 'b': b}
        })
        
        return jsonify({
            'ok': True,
            'zone': zone_name,
            'color': {'r': r, 'g': g, 'b': b}
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/zones/<zone_name>/brightness', methods=['POST'])
def api_set_zone_brightness(zone_name):
    """Set brightness for a specific zone."""
    try:
        data = request.json or {}
        brightness = int(data.get('brightness', 100))
        
        success = led_controller.set_zone_brightness(zone_name, brightness)
        
        if not success:
            return jsonify({'ok': False, 'error': 'Zone not found'}), 404
        
        socketio.emit('zone_update', {
            'zone': zone_name,
            'brightness': brightness
        })
        
        return jsonify({
            'ok': True,
            'zone': zone_name,
            'brightness': brightness
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/zones/<zone_name>/toggle', methods=['POST'])
def api_toggle_zone(zone_name):
    """Enable or disable a zone."""
    try:
        data = request.json or {}
        enabled = data.get('enabled', True)
        
        success = led_controller.enable_zone(zone_name, enabled)
        
        if not success:
            return jsonify({'ok': False, 'error': 'Zone not found'}), 404
        
        socketio.emit('zone_update', {
            'zone': zone_name,
            'enabled': enabled
        })
        
        return jsonify({
            'ok': True,
            'zone': zone_name,
            'enabled': enabled
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/zones/all/color', methods=['POST'])
def api_set_all_colors():
    """Set colors for all zones."""
    try:
        data = request.json or {}
        zone_colors = data.get('zone_colors', {})
        
        led_controller.set_all_colors(zone_colors)
        
        socketio.emit('zones_update', {
            'zone_colors': zone_colors
        })
        
        return jsonify({
            'ok': True,
            'zones_updated': len(zone_colors)
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/brightness', methods=['GET', 'POST'])
def api_global_brightness():
    """Get or set global brightness."""
    try:
        if request.method == 'POST':
            data = request.json or {}
            brightness = int(data.get('brightness', 100))
            
            led_controller.set_global_brightness(brightness)
            
            socketio.emit('brightness_update', {
                'brightness': brightness
            })
            
            return jsonify({
                'ok': True,
                'brightness': brightness
            })
        else:
            return jsonify({
                'ok': True,
                'brightness': led_controller.global_brightness
            })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/control/off', methods=['POST'])
def api_turn_off():
    """Turn off all zones."""
    try:
        led_controller.turn_off_all()
        
        socketio.emit('all_off', {})
        
        return jsonify({
            'ok': True,
            'message': 'All zones turned off'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/control/fade-in', methods=['POST'])
def api_fade_in():
    """Fade in all zones."""
    try:
        data = request.json or {}
        duration = float(data.get('duration', 2.0))
        
        led_controller.fade_in(duration)
        
        return jsonify({
            'ok': True,
            'message': f'Faded in over {duration}s'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/control/fade-out', methods=['POST'])
def api_fade_out():
    """Fade out all zones."""
    try:
        data = request.json or {}
        duration = float(data.get('duration', 2.0))
        
        led_controller.fade_out(duration)
        
        return jsonify({
            'ok': True,
            'message': f'Faded out over {duration}s'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/control/auto-dim', methods=['POST'])
def api_auto_dim():
    """Apply auto-dimming based on time of day."""
    try:
        dim_level = led_controller.apply_auto_dim()
        
        return jsonify({
            'ok': True,
            'brightness': dim_level,
            'message': f'Auto-dim applied: {dim_level}%'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/control/parking-brake', methods=['POST'])
def api_parking_brake():
    """Dim when parking brake engaged."""
    try:
        data = request.json or {}
        engaged = data.get('engaged', False)
        
        led_controller.apply_parking_brake_dim(engaged)
        
        return jsonify({
            'ok': True,
            'parking_brake': engaged,
            'brightness': led_controller.global_brightness
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/music/mode', methods=['GET', 'POST'])
def api_music_mode():
    """Get or set music reactive mode."""
    try:
        if request.method == 'POST':
            data = request.json or {}
            mode = data.get('mode', 'off')
            
            success = music_engine.set_mode(mode)
            
            if not success:
                return jsonify({'ok': False, 'error': 'Invalid mode'}), 400
            
            socketio.emit('music_mode_update', {
                'mode': mode,
                'running': music_engine.running
            })
            
            return jsonify({
                'ok': True,
                'mode': mode,
                'running': music_engine.running
            })
        else:
            status = music_engine.get_status()
            return jsonify({
                'ok': True,
                'status': status
            })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/music/sensitivity', methods=['POST'])
def api_music_sensitivity():
    """Set music reactive sensitivity."""
    try:
        data = request.json or {}
        sensitivity = int(data.get('sensitivity', 50))
        
        music_engine.set_sensitivity(sensitivity)
        
        return jsonify({
            'ok': True,
            'sensitivity': sensitivity
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/music/test-connection')
def api_test_music_connection():
    """Test connection to audio visualizer."""
    try:
        connected = music_engine.test_connection()
        
        return jsonify({
            'ok': True,
            'connected': connected,
            'url': music_engine.audio_visualizer_url
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/scenes')
def api_get_scenes():
    """Get all scenes."""
    try:
        scenes = scene_manager.get_all_scenes()
        
        return jsonify({
            'ok': True,
            'scenes': scenes,
            'count': len(scenes)
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/scenes/<scene_name>')
def api_get_scene(scene_name):
    """Get a specific scene."""
    try:
        scene = db.get_scene(scene_name)
        
        if not scene:
            return jsonify({'ok': False, 'error': 'Scene not found'}), 404
        
        return jsonify({
            'ok': True,
            'scene': scene
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/scenes/<scene_name>/apply', methods=['POST'])
def api_apply_scene(scene_name):
    """Apply a scene."""
    try:
        success = scene_manager.apply_scene(scene_name)
        
        if not success:
            return jsonify({'ok': False, 'error': 'Scene not found'}), 404
        
        socketio.emit('scene_applied', {
            'scene_name': scene_name
        })
        
        return jsonify({
            'ok': True,
            'scene_name': scene_name,
            'message': f'Applied scene: {scene_name}'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/scenes', methods=['POST'])
def api_save_scene():
    """Save current state as a scene."""
    try:
        data = request.json or {}
        scene_name = data.get('scene_name', '')
        description = data.get('description', '')
        
        if not scene_name:
            return jsonify({'ok': False, 'error': 'scene_name required'}), 400
        
        success = scene_manager.save_current_as_scene(scene_name, description)
        
        socketio.emit('scene_saved', {
            'scene_name': scene_name
        })
        
        return jsonify({
            'ok': True,
            'scene_name': scene_name,
            'message': f'Saved scene: {scene_name}'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/scenes/<scene_name>', methods=['DELETE'])
def api_delete_scene(scene_name):
    """Delete a custom scene."""
    try:
        success = scene_manager.delete_scene(scene_name)
        
        if not success:
            return jsonify({'ok': False, 'error': 'Cannot delete scene'}), 400
        
        socketio.emit('scene_deleted', {
            'scene_name': scene_name
        })
        
        return jsonify({
            'ok': True,
            'scene_name': scene_name,
            'message': f'Deleted scene: {scene_name}'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/scenes/<scene_name>/favorite', methods=['POST'])
def api_set_favorite(scene_name):
    """Set scene as favorite."""
    try:
        data = request.json or {}
        is_favorite = data.get('is_favorite', True)
        
        success = scene_manager.set_favorite(scene_name, is_favorite)
        
        if not success:
            return jsonify({'ok': False, 'error': 'Scene not found'}), 404
        
        return jsonify({
            'ok': True,
            'scene_name': scene_name,
            'is_favorite': is_favorite
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/quick/solid/<color_name>', methods=['POST'])
def api_quick_solid_color(color_name):
    """Quick access to solid colors."""
    try:
        success = scene_manager.quick_access_solid_color(color_name)
        
        if not success:
            return jsonify({'ok': False, 'error': 'Invalid color'}), 400
        
        socketio.emit('quick_color_applied', {
            'color': color_name
        })
        
        return jsonify({
            'ok': True,
            'color': color_name,
            'message': f'Applied {color_name}'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/quick/two-tone', methods=['POST'])
def api_quick_two_tone():
    """Quick access to two-tone theme."""
    try:
        data = request.json or {}
        color1 = data.get('color1', 'red')
        color2 = data.get('color2', 'blue')
        
        success = scene_manager.two_tone_theme(color1, color2)
        
        if not success:
            return jsonify({'ok': False, 'error': 'Invalid colors'}), 400
        
        return jsonify({
            'ok': True,
            'colors': [color1, color2],
            'message': f'Applied two-tone: {color1} & {color2}'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/quick/rainbow', methods=['POST'])
def api_quick_rainbow():
    """Quick access to rainbow gradient."""
    try:
        success = scene_manager.rainbow_gradient()
        
        return jsonify({
            'ok': True,
            'message': 'Applied rainbow gradient'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/hardware/status')
def api_hardware_status():
    """Get hardware status."""
    try:
        status = led_controller.get_hardware_status()
        
        return jsonify({
            'ok': True,
            'hardware': status
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/hardware/serial/connect', methods=['POST'])
def api_serial_connect():
    """Simulate serial connection."""
    try:
        data = request.json or {}
        connected = data.get('connected', True)
        
        led_controller.simulate_serial_connect(connected)
        
        return jsonify({
            'ok': True,
            'connected': connected
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/preferences')
def api_get_preferences():
    """Get all preferences."""
    try:
        prefs = db.get_all_preferences()
        
        return jsonify({
            'ok': True,
            'preferences': prefs
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/preferences', methods=['POST'])
def api_set_preference():
    """Set a preference."""
    try:
        data = request.json or {}
        key = data.get('key', '')
        value = data.get('value')
        
        if not key:
            return jsonify({'ok': False, 'error': 'key required'}), 400
        
        db.set_preference(key, value)
        
        return jsonify({
            'ok': True,
            'key': key,
            'value': value
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/stats')
def api_stats():
    """Get overall statistics."""
    try:
        db_stats = db.get_stats()
        led_stats = led_controller.get_stats()
        music_stats = music_engine.get_stats()
        scene_stats = scene_manager.get_stats()
        
        return jsonify({
            'ok': True,
            'database': db_stats,
            'led_controller': led_stats,
            'music_reactive': music_stats,
            'scene_manager': scene_stats
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to RGB Lighting Controller'})
    
    status = led_controller.get_all_zones_status()
    emit('zones_status', status)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    print(f"Client disconnected: {request.sid}")


@socketio.on('request_update')
def handle_request_update():
    """Handle client request for immediate update."""
    status = led_controller.get_all_zones_status()
    emit('zones_status', status)


if __name__ == '__main__':
    port = int(os.environ.get('LIGHTING_PORT', 8500))
    
    print(f"🌈 RGB Ambient Lighting Controller starting on port {port}")
    print(f"🎨 Dashboard: http://localhost:{port}")
    print(f"💓 Health Check: http://localhost:{port}/health")
    print(f"🔌 WebSocket enabled for real-time updates")
    print(f"🎵 Music reactive engine ready")
    print(f"🎭 Pre-built scenes: Chill, Party, Drive, Night")
    print(f"💡 Total LED zones: {len(led_controller.zones)}")
    print(f"⚡ Total LEDs: {sum(z.led_count for z in led_controller.zones.values())}")
    
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
