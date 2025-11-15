#!/usr/bin/env python3
"""
Advanced DSP Control Center
Professional-grade audio tuning for EOENKK Android 15 head unit
Port: 8100
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.dsp.equalizer import ParametricEqualizer
from services.dsp.crossover import ActiveCrossover
from services.dsp.time_align import TimeAlignment
from services.dsp.analyzer import SpectrumAnalyzer
from services.dsp.presets import PresetManager
from services.dsp.database import DSPDatabase

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

eq = ParametricEqualizer()
crossover = ActiveCrossover()
time_align = TimeAlignment()
analyzer = SpectrumAnalyzer()
preset_manager = PresetManager()
db = DSPDatabase()

current_settings = {
    'eq': None,
    'crossover': None,
    'time_alignment': None,
    'bass': {
        'level_db': 0.0,
        'subsonic_filter_hz': 25,
        'boost_db': 0.0,
        'phase_degrees': 0
    },
    'loudness': {
        'enabled': False,
        'reference_level_db': -20.0,
        'compensation_curve': 'iso226'
    }
}


@app.route('/')
def index():
    """Serve the DSP control interface."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('DSP_PORT', 8100))
    return jsonify({
        'ok': True,
        'service': 'advanced_dsp_control_center',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'features': [
            '31-band parametric EQ',
            'Per-channel EQ control',
            'Active crossover (2/3/4-way)',
            'Time alignment',
            'Bass management',
            'Loudness compensation',
            'Spectrum analyzer',
            'Preset management',
            'EOENKK Android integration'
        ]
    })


@app.route('/api/eq/info')
def api_eq_info():
    """Get EQ band information."""
    try:
        band_info = eq.get_band_info()
        return jsonify({
            'ok': True,
            'bands': band_info,
            'total_bands': len(band_info),
            'channels': eq.channels
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/eq/create', methods=['POST'])
def api_eq_create():
    """Create 31-band EQ curve."""
    try:
        data = request.json or {}
        gains = data.get('gains', {})
        q_factor = data.get('q_factor', 1.41)
        channel = data.get('channel', 'all')
        
        gains_int = {int(k): float(v) for k, v in gains.items()}
        
        eq_curve = eq.create_31_band_eq(gains_int, q_factor, channel)
        
        valid, messages = eq.validate_eq_settings(eq_curve)
        headroom = eq.recommend_headroom(eq_curve)
        
        current_settings['eq'] = eq_curve
        
        return jsonify({
            'ok': True,
            'eq_curve': eq_curve,
            'validation': {
                'valid': valid,
                'messages': messages
            },
            'headroom_recommendation': headroom
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/eq/per-channel', methods=['POST'])
def api_eq_per_channel():
    """Create per-channel EQ curves."""
    try:
        data = request.json or {}
        channel_gains = data.get('channel_gains', {})
        
        per_channel_eq = eq.create_per_channel_eq(channel_gains)
        
        return jsonify({
            'ok': True,
            'per_channel_eq': per_channel_eq,
            'channels': list(per_channel_eq.keys())
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/eq/frequency-response', methods=['POST'])
def api_eq_frequency_response():
    """Calculate frequency response from EQ settings."""
    try:
        data = request.json or {}
        eq_curve = data.get('eq_curve', [])
        
        response = eq.calculate_frequency_response(eq_curve)
        
        return jsonify({
            'ok': True,
            'frequency_response': response,
            'num_points': len(response)
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/eq/cabin-correction', methods=['POST'])
def api_eq_cabin_correction():
    """Apply Chevy Sonic cabin acoustic correction."""
    try:
        data = request.json or {}
        eq_curve = data.get('eq_curve', [])
        
        corrected = eq.apply_sonic_cabin_correction(eq_curve)
        
        return jsonify({
            'ok': True,
            'corrected_eq': corrected,
            'note': 'Applied Chevy Sonic cabin acoustic correction'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/eq/export/android', methods=['POST'])
def api_eq_export_android():
    """Export EQ settings for EOENKK Android."""
    try:
        data = request.json or {}
        eq_curve = data.get('eq_curve', current_settings.get('eq', []))
        channel = data.get('channel', 'all')
        
        android_config = eq.export_to_android(eq_curve, channel)
        
        return jsonify({
            'ok': True,
            'android_config': android_config,
            'instructions': 'Copy this JSON to EOENKK head unit DSP settings'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/crossover/create/<config_type>', methods=['POST'])
def api_crossover_create(config_type):
    """Create crossover configuration (2-way, 3-way, or 4-way)."""
    try:
        data = request.json or {}
        slope_db = data.get('slope_db', 24)
        filter_type = data.get('filter_type', 'linkwitz_riley')
        
        if config_type == '2-way':
            frequency = data.get('frequency', 2500)
            crossover_config = crossover.create_2way_crossover(frequency, slope_db, filter_type)
        elif config_type == '3-way':
            low_mid_freq = data.get('low_mid_freq', 250)
            mid_high_freq = data.get('mid_high_freq', 2500)
            crossover_config = crossover.create_3way_crossover(low_mid_freq, mid_high_freq, slope_db, filter_type)
        elif config_type == '4-way':
            sub_low_freq = data.get('sub_low_freq', 80)
            low_mid_freq = data.get('low_mid_freq', 250)
            mid_high_freq = data.get('mid_high_freq', 2500)
            crossover_config = crossover.create_4way_crossover(sub_low_freq, low_mid_freq, mid_high_freq, slope_db, filter_type)
        else:
            return jsonify({'ok': False, 'error': 'Invalid config_type. Use 2-way, 3-way, or 4-way'}), 400
            
        current_settings['crossover'] = crossover_config
        
        return jsonify({
            'ok': True,
            'crossover_config': crossover_config
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/crossover/recommend/<speaker_config>')
def api_crossover_recommend(speaker_config):
    """Get recommended crossover frequencies for speaker configuration."""
    try:
        recommendations = crossover.recommend_crossover_frequencies(speaker_config)
        
        return jsonify({
            'ok': True,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/crossover/export/android', methods=['POST'])
def api_crossover_export_android():
    """Export crossover settings for EOENKK Android."""
    try:
        data = request.json or {}
        crossover_config = data.get('crossover_config', current_settings.get('crossover'))
        
        if not crossover_config:
            return jsonify({'ok': False, 'error': 'No crossover configuration available'}), 400
            
        android_config = crossover.export_to_android(crossover_config)
        
        return jsonify({
            'ok': True,
            'android_config': android_config,
            'instructions': 'Copy this JSON to EOENKK head unit crossover settings'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/time-alignment/calculate', methods=['POST'])
def api_time_alignment_calculate():
    """Calculate speaker delays from distances."""
    try:
        data = request.json or {}
        speaker_distances = data.get('speaker_distances', {})
        listening_position = data.get('listening_position', 'driver')
        distance_unit = data.get('distance_unit', 'inches')
        
        delays = time_align.calculate_speaker_delays(speaker_distances, listening_position, distance_unit)
        
        current_settings['time_alignment'] = delays
        
        return jsonify({
            'ok': True,
            'time_alignment': delays
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/time-alignment/sonic-defaults/<listening_position>')
def api_time_alignment_sonic_defaults(listening_position):
    """Get default time alignment for Chevy Sonic."""
    try:
        delays = time_align.calculate_sonic_defaults(listening_position)
        
        return jsonify({
            'ok': True,
            'time_alignment': delays,
            'note': 'Default speaker positions for Chevy Sonic LTZ'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/time-alignment/visualize', methods=['POST'])
def api_time_alignment_visualize():
    """Create soundstage visualization."""
    try:
        data = request.json or {}
        speaker_delays = data.get('speaker_delays', current_settings.get('time_alignment'))
        
        if not speaker_delays:
            return jsonify({'ok': False, 'error': 'No time alignment data available'}), 400
            
        visualization = time_align.create_soundstage_visualization(speaker_delays)
        
        return jsonify({
            'ok': True,
            'visualization': visualization
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/time-alignment/procedure')
def api_time_alignment_procedure():
    """Get measurement procedure recommendations."""
    try:
        procedure = time_align.recommend_measurement_procedure()
        
        return jsonify({
            'ok': True,
            'procedure': procedure
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/time-alignment/export/android', methods=['POST'])
def api_time_alignment_export_android():
    """Export time alignment for EOENKK Android."""
    try:
        data = request.json or {}
        speaker_delays = data.get('speaker_delays', current_settings.get('time_alignment'))
        
        if not speaker_delays:
            return jsonify({'ok': False, 'error': 'No time alignment data available'}), 400
            
        android_config = time_align.export_to_android(speaker_delays)
        
        return jsonify({
            'ok': True,
            'android_config': android_config,
            'instructions': 'Copy this JSON to EOENKK head unit time alignment settings'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/bass/settings', methods=['GET', 'POST'])
def api_bass_settings():
    """Get or update bass management settings."""
    try:
        if request.method == 'POST':
            data = request.json or {}
            
            current_settings['bass']['level_db'] = data.get('level_db', 0.0)
            current_settings['bass']['subsonic_filter_hz'] = data.get('subsonic_filter_hz', 25)
            current_settings['bass']['boost_db'] = data.get('boost_db', 0.0)
            current_settings['bass']['phase_degrees'] = data.get('phase_degrees', 0)
            
            current_settings['bass']['level_db'] = max(-12.0, min(12.0, current_settings['bass']['level_db']))
            current_settings['bass']['subsonic_filter_hz'] = max(10, min(50, current_settings['bass']['subsonic_filter_hz']))
            current_settings['bass']['boost_db'] = max(0.0, min(12.0, current_settings['bass']['boost_db']))
            current_settings['bass']['phase_degrees'] = max(0, min(180, current_settings['bass']['phase_degrees']))
            
        return jsonify({
            'ok': True,
            'bass_settings': current_settings['bass']
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/loudness/settings', methods=['GET', 'POST'])
def api_loudness_settings():
    """Get or update loudness compensation settings."""
    try:
        if request.method == 'POST':
            data = request.json or {}
            
            current_settings['loudness']['enabled'] = data.get('enabled', False)
            current_settings['loudness']['reference_level_db'] = data.get('reference_level_db', -20.0)
            current_settings['loudness']['compensation_curve'] = data.get('compensation_curve', 'iso226')
            
        return jsonify({
            'ok': True,
            'loudness_settings': current_settings['loudness'],
            'available_curves': ['iso226', 'flat', 'custom']
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/analyzer/spectrum')
def api_analyzer_spectrum():
    """Get real-time spectrum analyzer data."""
    try:
        signal_type = request.args.get('signal_type', 'music')
        include_peaks = request.args.get('include_peaks', 'true').lower() == 'true'
        
        spectrum = analyzer.generate_test_spectrum(signal_type, include_peaks)
        
        return jsonify({
            'ok': True,
            'spectrum': spectrum
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/analyzer/energy')
def api_analyzer_energy():
    """Calculate spectral energy distribution."""
    try:
        spectrum = analyzer.generate_test_spectrum()
        energy = analyzer.calculate_total_energy(spectrum['bands'])
        
        return jsonify({
            'ok': True,
            'energy': energy
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/analyzer/reset-peaks', methods=['POST'])
def api_analyzer_reset_peaks():
    """Reset peak hold values."""
    try:
        analyzer.reset_peak_hold()
        
        return jsonify({
            'ok': True,
            'message': 'Peak hold values reset'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/analyzer/settings')
def api_analyzer_settings():
    """Get analyzer settings."""
    try:
        settings = analyzer.get_analyzer_settings()
        
        return jsonify({
            'ok': True,
            'settings': settings
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/presets')
def api_presets_list():
    """List all available presets."""
    try:
        presets = preset_manager.list_presets()
        
        return jsonify({
            'ok': True,
            'presets': presets,
            'count': len(presets)
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/presets/<preset_name>')
def api_presets_get(preset_name):
    """Get specific preset."""
    try:
        preset = preset_manager.get_preset(preset_name)
        
        if preset:
            return jsonify({
                'ok': True,
                'preset': preset
            })
        else:
            return jsonify({'ok': False, 'error': 'Preset not found'}), 404
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/presets/save', methods=['POST'])
def api_presets_save():
    """Save current settings as preset."""
    try:
        data = request.json or {}
        preset_id = data.get('preset_id', f"preset_{int(datetime.now().timestamp())}")
        preset_name = data.get('name', 'Custom Preset')
        description = data.get('description', '')
        
        preset_data = {
            'name': preset_name,
            'description': description,
            'author': data.get('author', 'User'),
            'created': datetime.now().isoformat(),
            'eq': current_settings.get('eq'),
            'crossover': current_settings.get('crossover'),
            'time_alignment': current_settings.get('time_alignment'),
            'bass': current_settings.get('bass'),
            'loudness': current_settings.get('loudness')
        }
        
        result = preset_manager.save_preset(preset_id, preset_data, overwrite=data.get('overwrite', False))
        
        if result['ok']:
            db.save_preset(
                preset_id=preset_id,
                name=preset_name,
                eq_settings=current_settings.get('eq'),
                crossover_settings=current_settings.get('crossover'),
                time_alignment_settings=current_settings.get('time_alignment'),
                bass_settings=current_settings.get('bass'),
                loudness_settings=current_settings.get('loudness'),
                description=description
            )
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/presets/<preset_name>/load', methods=['POST'])
def api_presets_load(preset_name):
    """Load preset and apply to current settings."""
    try:
        preset = preset_manager.get_preset(preset_name)
        
        if not preset:
            return jsonify({'ok': False, 'error': 'Preset not found'}), 404
            
        if 'eq' in preset and preset['eq']:
            current_settings['eq'] = preset['eq'].get('bands', [])
        if 'crossover' in preset and preset['crossover']:
            current_settings['crossover'] = preset['crossover']
        if 'time_alignment' in preset and preset['time_alignment']:
            current_settings['time_alignment'] = preset['time_alignment']
        if 'bass' in preset and preset['bass']:
            current_settings['bass'] = preset['bass']
        if 'loudness' in preset and preset['loudness']:
            current_settings['loudness'] = preset['loudness']
            
        return jsonify({
            'ok': True,
            'preset_name': preset_name,
            'current_settings': current_settings
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/presets/<preset_name>/delete', methods=['DELETE'])
def api_presets_delete(preset_name):
    """Delete user preset."""
    try:
        result = preset_manager.delete_preset(preset_name)
        
        if result['ok']:
            db.delete_preset(preset_name)
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/presets/<preset_name>/export')
def api_presets_export(preset_name):
    """Export preset as JSON."""
    try:
        preset_json = preset_manager.export_preset(preset_name)
        
        if preset_json:
            return jsonify({
                'ok': True,
                'preset_name': preset_name,
                'preset_json': preset_json
            })
        else:
            return jsonify({'ok': False, 'error': 'Preset not found'}), 404
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/presets/import', methods=['POST'])
def api_presets_import():
    """Import preset from JSON."""
    try:
        data = request.json or {}
        preset_json = data.get('preset_json')
        preset_id = data.get('preset_id')
        
        if not preset_json:
            return jsonify({'ok': False, 'error': 'No preset_json provided'}), 400
            
        result = preset_manager.import_preset(preset_json, preset_id)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/export/android-full', methods=['POST'])
def api_export_android_full():
    """Export complete DSP configuration for EOENKK Android."""
    try:
        android_config = {
            'version': '1.0',
            'device': 'EOENKK_Android15',
            'exported_at': datetime.now().isoformat(),
            'dsp_configuration': {}
        }
        
        if current_settings.get('eq'):
            android_config['dsp_configuration']['eq'] = eq.export_to_android(
                current_settings['eq'], 'all'
            )
            
        if current_settings.get('crossover'):
            android_config['dsp_configuration']['crossover'] = crossover.export_to_android(
                current_settings['crossover']
            )
            
        if current_settings.get('time_alignment'):
            android_config['dsp_configuration']['time_alignment'] = time_align.export_to_android(
                current_settings['time_alignment']
            )
            
        android_config['dsp_configuration']['bass'] = current_settings.get('bass')
        android_config['dsp_configuration']['loudness'] = current_settings.get('loudness')
        
        return jsonify({
            'ok': True,
            'android_config': android_config,
            'instructions': 'Save this JSON and import into EOENKK DSP app'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/current-settings')
def api_current_settings():
    """Get all current DSP settings."""
    try:
        return jsonify({
            'ok': True,
            'settings': current_settings
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('DSP_PORT', 8100))
    print(f"🎚️  Advanced DSP Control Center starting on port {port}")
    print(f"🎧  Professional audio tuning for EOENKK Android 15")
    print(f"📊  31-band parametric EQ | Crossover | Time Alignment")
    app.run(host='0.0.0.0', port=port, debug=True)
