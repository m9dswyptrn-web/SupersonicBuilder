#!/usr/bin/env python3
"""
Real-Time Audio Visualizer Service
Stunning visual effects for QLED 2000×1200 display
Port: 8300
"""

import os
import sys
import json
import time
import numpy as np
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, render_template, request, Response
from flask_cors import CORS

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.visualizer_audio.database import VisualizerDatabase
from services.visualizer_audio.fft import FFTAnalyzer
from services.visualizer_audio.beatdetect import BeatDetector
from services.visualizer_audio.effects import EffectsEngine
from services.visualizer_audio.themes import ThemeManager

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

db = VisualizerDatabase()
fft_analyzer = FFTAnalyzer()
beat_detector = BeatDetector()
effects_engine = EffectsEngine()
theme_manager = ThemeManager()

current_audio_data = None
last_analysis = None


@app.route('/')
def index():
    """Serve the main visualizer dashboard."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('VISUALIZER_AUDIO_PORT', 8300))
    return jsonify({
        'ok': True,
        'service': 'real_time_audio_visualizer',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'features': [
            'Spectrum analyzer (31/64-band)',
            'Waveform display',
            'VU meters',
            'Beat detection',
            'Music-reactive effects',
            'RGB lighting integration',
            'Multiple themes',
            'Full-screen mode'
        ],
        'display': {
            'target_resolution': '2000x1200',
            'target_fps': 60
        }
    })


@app.route('/api/analyze', methods=['POST'])
def api_analyze_audio():
    """Analyze audio data and return visualization parameters."""
    global current_audio_data, last_analysis
    
    try:
        data = request.json or {}
        
        if 'audio_data' in data:
            audio_samples = np.array(data['audio_data'])
        else:
            audio_samples = fft_analyzer.generate_test_signal(duration=0.1)
        
        num_bands = data.get('num_bands', 31)
        
        fft_result = fft_analyzer.analyze_audio(audio_samples, num_bands)
        
        beat_result = beat_detector.detect_beat(
            audio_samples,
            fft_result['bass_level'],
            fft_result['mid_level'],
            fft_result['treble_level']
        )
        
        particles = effects_engine.generate_particles(
            fft_result['bass_level'],
            beat_result['beat_detected'],
            num_particles=20
        )
        effects_engine.add_particles(particles)
        
        active_particles = effects_engine.update_particles(1/60)
        
        color_pulse = effects_engine.generate_color_pulse(
            beat_result['beat_detected'],
            beat_result['beat_strength'],
            beat_result['bpm']
        )
        
        waveform_distortion = effects_engine.generate_waveform_distortion(
            fft_result['bass_level'],
            fft_result['mid_level'],
            fft_result['treble_level']
        )
        
        spectrum_glow = effects_engine.generate_spectrum_glow(fft_result['band_levels'])
        
        rgb_data = effects_engine.get_rgb_lighting_data(
            fft_result['bass_level'],
            fft_result['mid_level'],
            fft_result['treble_level'],
            beat_result['beat_detected']
        )
        
        # Convert numpy types to Python types for JSON serialization
        def sanitize_for_json(obj):
            """Convert numpy types to Python native types."""
            if isinstance(obj, dict):
                return {k: sanitize_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize_for_json(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, (np.bool_)):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj
        
        analysis = {
            'timestamp': time.time(),
            'fft': sanitize_for_json(fft_result),
            'beat': sanitize_for_json(beat_result),
            'effects': {
                'particles': sanitize_for_json(active_particles[:100]),
                'color_pulse': sanitize_for_json(color_pulse),
                'waveform_distortion': sanitize_for_json(waveform_distortion),
                'spectrum_glow': sanitize_for_json(spectrum_glow)
            },
            'rgb_lighting': sanitize_for_json(rgb_data)
        }
        
        last_analysis = analysis
        current_audio_data = audio_samples
        
        snapshot_id = f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        db.save_audio_snapshot(
            snapshot_id,
            fft_result['band_levels'],
            bool(beat_result['beat_detected']),
            float(beat_result['bpm']),
            float(fft_result['bass_level']),
            float(fft_result['mid_level']),
            float(fft_result['treble_level'])
        )
        
        return jsonify({
            'ok': True,
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/stream')
def api_stream_analysis():
    """Server-Sent Events stream for real-time updates."""
    def generate():
        """Generate SSE stream."""
        while True:
            if last_analysis:
                yield f"data: {json.dumps(last_analysis)}\n\n"
            time.sleep(1/60)
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/test/generate/<signal_type>')
def api_generate_test_signal(signal_type):
    """Generate test audio signals for visualization testing."""
    try:
        duration = float(request.args.get('duration', 1.0))
        
        if signal_type == 'tone':
            freq = float(request.args.get('frequency', 440))
            signal = fft_analyzer.generate_test_signal(duration, [freq])
        elif signal_type == 'multitone':
            signal = fft_analyzer.generate_test_signal(duration, [100, 440, 1000, 5000])
        elif signal_type == 'white_noise':
            signal = fft_analyzer.generate_white_noise(duration)
        elif signal_type == 'pink_noise':
            signal = fft_analyzer.generate_pink_noise(duration)
        elif signal_type == 'sweep':
            signal = fft_analyzer.generate_sweep(duration)
        else:
            return jsonify({'ok': False, 'error': 'Invalid signal type'}), 400
        
        return jsonify({
            'ok': True,
            'signal_type': signal_type,
            'samples': signal.tolist()[:1000],
            'duration': duration,
            'sample_rate': fft_analyzer.sample_rate
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes')
def api_get_themes():
    """Get all available themes."""
    try:
        builtin_themes = theme_manager.get_all_themes()
        custom_themes = db.get_all_themes()
        
        return jsonify({
            'ok': True,
            'builtin_themes': builtin_themes,
            'custom_themes': custom_themes,
            'current_theme': theme_manager.current_theme
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/<theme_name>')
def api_get_theme(theme_name):
    """Get specific theme details."""
    try:
        theme = theme_manager.get_theme(theme_name)
        
        if not theme:
            theme = db.get_theme(theme_name)
        
        if theme:
            return jsonify({
                'ok': True,
                'theme': theme
            })
        else:
            return jsonify({'ok': False, 'error': 'Theme not found'}), 404
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/current', methods=['POST'])
def api_set_current_theme():
    """Set the current active theme."""
    try:
        data = request.json or {}
        theme_name = data.get('theme_name')
        
        if not theme_name:
            return jsonify({'ok': False, 'error': 'theme_name required'}), 400
        
        theme_manager.set_current_theme(theme_name)
        db.save_setting('current_theme', theme_name)
        
        return jsonify({
            'ok': True,
            'current_theme': theme_name
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/custom', methods=['POST'])
def api_save_custom_theme():
    """Save a custom theme."""
    try:
        data = request.json or {}
        theme_name = data.get('theme_name')
        theme_data = data.get('theme_data')
        is_favorite = data.get('is_favorite', False)
        
        if not theme_name or not theme_data:
            return jsonify({'ok': False, 'error': 'theme_name and theme_data required'}), 400
        
        db.save_theme(theme_name, theme_data, is_favorite)
        theme_manager.add_custom_theme(theme_name, theme_data)
        
        return jsonify({
            'ok': True,
            'message': 'Theme saved successfully',
            'theme_name': theme_name
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/settings')
def api_get_settings():
    """Get all visualizer settings."""
    try:
        settings = {
            'visualization_mode': db.get_setting('visualization_mode', 'spectrum_bars'),
            'num_bands': db.get_setting('num_bands', 31),
            'show_waveform': db.get_setting('show_waveform', True),
            'show_vu_meters': db.get_setting('show_vu_meters', True),
            'show_particles': db.get_setting('show_particles', True),
            'effect_intensity': db.get_setting('effect_intensity', 0.8),
            'fullscreen': db.get_setting('fullscreen', False),
            'current_theme': db.get_setting('current_theme', 'dark'),
            'rgb_lighting_enabled': db.get_setting('rgb_lighting_enabled', True)
        }
        
        return jsonify({
            'ok': True,
            'settings': settings
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/settings', methods=['POST'])
def api_save_settings():
    """Save visualizer settings."""
    try:
        data = request.json or {}
        
        for key, value in data.items():
            db.save_setting(key, value)
            
            if key == 'effect_intensity':
                effects_engine.set_intensity(value)
        
        return jsonify({
            'ok': True,
            'message': 'Settings saved successfully'
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/rgb/send', methods=['POST'])
def api_send_rgb_data():
    """Send RGB lighting data to external controller (port 8500)."""
    try:
        data = request.json or {}
        
        import requests
        rgb_controller_url = 'http://localhost:8500/api/lighting/update'
        
        response = requests.post(rgb_controller_url, json=data, timeout=0.1)
        
        return jsonify({
            'ok': True,
            'message': 'RGB data sent to controller',
            'controller_response': response.json() if response.ok else None
        })
    
    except requests.exceptions.Timeout:
        return jsonify({'ok': True, 'message': 'RGB controller not responding (timeout)'})
    except requests.exceptions.ConnectionError:
        return jsonify({'ok': True, 'message': 'RGB controller not available'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/beat/reset', methods=['POST'])
def api_reset_beat_detector():
    """Reset beat detection state."""
    try:
        beat_detector.reset()
        
        return jsonify({
            'ok': True,
            'message': 'Beat detector reset'
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/effects/clear', methods=['POST'])
def api_clear_effects():
    """Clear all visual effects."""
    try:
        effects_engine.clear_particles()
        
        return jsonify({
            'ok': True,
            'message': 'Effects cleared'
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/snapshots/recent')
def api_recent_snapshots():
    """Get recent audio analysis snapshots."""
    try:
        limit = int(request.args.get('limit', 100))
        snapshots = db.get_recent_snapshots(limit)
        
        return jsonify({
            'ok': True,
            'snapshots': snapshots,
            'count': len(snapshots)
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/performance/stats')
def api_performance_stats():
    """Get performance statistics."""
    try:
        stats = {
            'target_fps': 60,
            'active_particles': len(effects_engine.particles),
            'max_particles': effects_engine.max_particles,
            'effect_intensity': effects_engine.effect_intensity,
            'fft_size': fft_analyzer.fft_size,
            'sample_rate': fft_analyzer.sample_rate,
            'display_resolution': '2000x1200'
        }
        
        return jsonify({
            'ok': True,
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('VISUALIZER_AUDIO_PORT', 8300))
    
    print(f"🎵 Real-Time Audio Visualizer starting on port {port}")
    print(f"📺 Optimized for 2000×1200 QLED display @ 60 FPS")
    print(f"🌈 Dashboard: http://localhost:{port}")
    print(f"💓 Health Check: http://localhost:{port}/health")
    print(f"🎨 Themes: http://localhost:{port}/api/themes")
    print(f"📊 FFT Analysis: POST http://localhost:{port}/api/analyze")
    print(f"🎛️  Settings: http://localhost:{port}/api/settings")
    print(f"💡 RGB Integration: POST http://localhost:{port}/api/rgb/send")
    print(f"🧪 Test Signals: http://localhost:{port}/api/test/generate/tone")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
