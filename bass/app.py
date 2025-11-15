#!/usr/bin/env python3
"""
Bass Management System
Professional subwoofer integration and bass optimization
Port: 8400
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.bass.subwoofer import SubwooferController
from services.bass.filters import BassFilters
from services.bass.phase import PhaseAlignment
from services.bass.testtones import TestToneGenerator
from services.bass.database import BassDatabase

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

sub_controller = SubwooferController()
filters = BassFilters()
phase_align = PhaseAlignment()
tone_gen = TestToneGenerator()
db = BassDatabase()

current_session = {
    'subwoofers': [],
    'subsonic_filter': None,
    'lowpass_crossover': None,
    'bass_boost': None,
    'phase_config': None,
    'delay_config': None
}


@app.route('/')
def index():
    """Serve the Bass Management interface."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('BASS_PORT', 8400))
    db_stats = db.get_stats()
    
    return jsonify({
        'ok': True,
        'service': 'bass_management_system',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'features': [
            'Multiple subwoofer support (up to 4)',
            'Subsonic filter protection',
            'Low-pass crossover with Linkwitz-Riley',
            'Bass boost (shelf and peak)',
            'Phase alignment tools',
            'Group delay compensation',
            'Test tone generation',
            'SPL meter integration',
            'Preset management',
            'DSP integration (port 8100)'
        ],
        'database': db_stats
    })


@app.route('/api/subwoofer/configure', methods=['POST'])
def api_subwoofer_configure():
    """Configure individual subwoofer."""
    try:
        data = request.json or {}
        
        sub_id = data.get('sub_id', 1)
        level_percent = data.get('level_percent', 75.0)
        phase_degrees = data.get('phase_degrees', 0.0)
        delay_ms = data.get('delay_ms', 0.0)
        
        sub_config = sub_controller.configure_subwoofer(
            sub_id, level_percent, phase_degrees, delay_ms
        )
        
        current_session['subwoofers'] = [s for s in current_session['subwoofers'] 
                                         if s['subwoofer_id'] != sub_id]
        current_session['subwoofers'].append(sub_config)
        
        return jsonify({
            'ok': True,
            'subwoofer_config': sub_config,
            'active_subwoofers': len(current_session['subwoofers'])
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/subwoofer/configure-multiple', methods=['POST'])
def api_subwoofer_configure_multiple():
    """Configure multiple subwoofers."""
    try:
        data = request.json or {}
        sub_configs = data.get('subwoofers', [])
        
        multi_config = sub_controller.configure_multiple_subs(sub_configs)
        
        current_session['subwoofers'] = multi_config['subwoofers']
        
        return jsonify({
            'ok': True,
            'multi_subwoofer_config': multi_config
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/subwoofer/delay-from-distance', methods=['POST'])
def api_subwoofer_delay_from_distance():
    """Calculate delay from physical distance."""
    try:
        data = request.json or {}
        
        distance = data.get('distance', 0)
        unit = data.get('unit', 'inches')
        main_speaker_distance = data.get('main_speaker_distance')
        
        delay_calc = sub_controller.calculate_delay_from_distance(
            distance, unit, main_speaker_distance
        )
        
        return jsonify({
            'ok': True,
            'delay_calculation': delay_calc
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/subwoofer/optimize-dual-placement', methods=['POST'])
def api_subwoofer_optimize_dual_placement():
    """Get dual subwoofer placement recommendations."""
    try:
        data = request.json or {}
        
        room_dimensions = data.get('room_dimensions', {
            'length': 120, 'width': 80, 'height': 96
        })
        listening_position = data.get('listening_position', {
            'x': 40, 'y': 48
        })
        
        optimization = sub_controller.optimize_dual_sub_placement(
            room_dimensions, listening_position
        )
        
        return jsonify({
            'ok': True,
            'placement_optimization': optimization
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/subwoofer/group-output', methods=['POST'])
def api_subwoofer_group_output():
    """Calculate combined output of multiple subwoofers."""
    try:
        data = request.json or {}
        subwoofers = data.get('subwoofers', current_session.get('subwoofers', []))
        
        if not subwoofers:
            return jsonify({'ok': False, 'error': 'No subwoofers configured'}), 400
        
        group_output = sub_controller.calculate_group_output(subwoofers)
        
        return jsonify({
            'ok': True,
            'group_output': group_output
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/filters/subsonic', methods=['POST'])
def api_filters_subsonic():
    """Create subsonic filter."""
    try:
        data = request.json or {}
        
        frequency_hz = data.get('frequency_hz', 25)
        slope_db = data.get('slope_db', 24)
        
        subsonic = filters.create_subsonic_filter(frequency_hz, slope_db)
        
        current_session['subsonic_filter'] = subsonic
        
        return jsonify({
            'ok': True,
            'subsonic_filter': subsonic
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/filters/crossover', methods=['POST'])
def api_filters_crossover():
    """Create low-pass crossover."""
    try:
        data = request.json or {}
        
        frequency_hz = data.get('frequency_hz', 80)
        slope_db = data.get('slope_db', 24)
        alignment = data.get('alignment', 'linkwitz_riley')
        
        crossover = filters.create_lowpass_crossover(frequency_hz, slope_db, alignment)
        
        current_session['lowpass_crossover'] = crossover
        
        return jsonify({
            'ok': True,
            'lowpass_crossover': crossover
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/filters/recommend-crossover', methods=['POST'])
def api_filters_recommend_crossover():
    """Get crossover frequency recommendations."""
    try:
        data = request.json or {}
        
        subwoofer_spec = data.get('subwoofer_spec', {
            'max_frequency': 200,
            'recommended_range': (30, 150)
        })
        main_speakers = data.get('main_speakers', {
            'min_frequency': 80,
            'type': 'coax'
        })
        
        recommendation = filters.recommend_crossover_frequency(subwoofer_spec, main_speakers)
        
        return jsonify({
            'ok': True,
            'crossover_recommendation': recommendation
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/filters/bass-boost', methods=['POST'])
def api_filters_bass_boost():
    """Create bass boost curve."""
    try:
        data = request.json or {}
        
        boost_type = data.get('boost_type', 'shelf')
        frequency_hz = data.get('frequency_hz', 60)
        boost_db = data.get('boost_db', 3.0)
        q_factor = data.get('q_factor', 0.7)
        
        boost = filters.create_bass_boost(boost_type, frequency_hz, boost_db, q_factor)
        
        current_session['bass_boost'] = boost
        
        return jsonify({
            'ok': True,
            'bass_boost': boost
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/filters/preset/<preset_name>')
def api_filters_preset(preset_name):
    """Load filter preset."""
    try:
        preset = filters.create_preset_filters(preset_name)
        
        current_session['subsonic_filter'] = preset['subsonic_filter']
        current_session['lowpass_crossover'] = preset['lowpass_crossover']
        current_session['bass_boost'] = preset.get('bass_boost')
        
        return jsonify({
            'ok': True,
            'preset': preset
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/filters/analyze-interaction', methods=['POST'])
def api_filters_analyze_interaction():
    """Analyze filter interaction."""
    try:
        data = request.json or {}
        
        subsonic = data.get('subsonic', current_session.get('subsonic_filter'))
        crossover = data.get('crossover', current_session.get('lowpass_crossover'))
        boost = data.get('boost', current_session.get('bass_boost'))
        
        if not subsonic or not crossover:
            return jsonify({'ok': False, 'error': 'Subsonic and crossover filters required'}), 400
        
        analysis = filters.analyze_filter_interaction(subsonic, crossover, boost)
        
        return jsonify({
            'ok': True,
            'filter_interaction_analysis': analysis
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/phase/set', methods=['POST'])
def api_phase_set():
    """Set subwoofer phase."""
    try:
        data = request.json or {}
        
        phase_degrees = data.get('phase_degrees', 0)
        fine_adjust = data.get('fine_adjust', False)
        
        phase_config = phase_align.set_phase(phase_degrees, fine_adjust)
        
        current_session['phase_config'] = phase_config
        
        return jsonify({
            'ok': True,
            'phase_config': phase_config
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/phase/from-delay', methods=['POST'])
def api_phase_from_delay():
    """Calculate phase from time delay."""
    try:
        data = request.json or {}
        
        delay_ms = data.get('delay_ms', 0)
        frequency_hz = data.get('frequency_hz', 80)
        
        phase_calc = phase_align.calculate_phase_from_delay(delay_ms, frequency_hz)
        
        return jsonify({
            'ok': True,
            'phase_calculation': phase_calc
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/phase/measure-response', methods=['POST'])
def api_phase_measure_response():
    """Measure phase response at crossover region."""
    try:
        data = request.json or {}
        
        subwoofer_config = data.get('subwoofer_config', {
            'delay_ms': 0, 'phase_degrees': 0
        })
        main_speaker_config = data.get('main_speaker_config', {
            'delay_ms': 0
        })
        test_frequencies = data.get('test_frequencies')
        
        phase_response = phase_align.measure_phase_response(
            subwoofer_config, main_speaker_config, test_frequencies
        )
        
        return jsonify({
            'ok': True,
            'phase_response': phase_response
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/phase/optimize', methods=['POST'])
def api_phase_optimize():
    """Optimize phase and delay settings."""
    try:
        data = request.json or {}
        
        subwoofer_distance = data.get('subwoofer_distance', 0)
        main_speaker_distance = data.get('main_speaker_distance', 0)
        unit = data.get('unit', 'inches')
        crossover_frequency = data.get('crossover_frequency', 80)
        
        optimization = phase_align.optimize_phase_and_delay(
            subwoofer_distance, main_speaker_distance, unit, crossover_frequency
        )
        
        current_session['delay_config'] = optimization
        
        return jsonify({
            'ok': True,
            'phase_optimization': optimization
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/phase/visualize', methods=['POST'])
def api_phase_visualize():
    """Create phase response visualization."""
    try:
        data = request.json or {}
        phase_measurements = data.get('phase_measurements', [])
        
        if not phase_measurements:
            return jsonify({'ok': False, 'error': 'Phase measurements required'}), 400
        
        visualization = phase_align.create_phase_visualization(phase_measurements)
        
        return jsonify({
            'ok': True,
            'visualization': visualization
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/phase/group-delay', methods=['POST'])
def api_phase_group_delay():
    """Calculate group delay from filters."""
    try:
        data = request.json or {}
        
        filter_configs = data.get('filter_configs', [])
        if not filter_configs:
            if current_session.get('subsonic_filter'):
                filter_configs.append(current_session['subsonic_filter'])
            if current_session.get('lowpass_crossover'):
                filter_configs.append(current_session['lowpass_crossover'])
        
        if not filter_configs:
            return jsonify({'ok': False, 'error': 'Filter configurations required'}), 400
        
        group_delay = phase_align.calculate_group_delay(filter_configs)
        
        return jsonify({
            'ok': True,
            'group_delay': group_delay
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/testtones/sine', methods=['POST'])
def api_testtones_sine():
    """Generate sine wave test tone."""
    try:
        data = request.json or {}
        
        frequency_hz = data.get('frequency_hz', 40)
        duration_seconds = data.get('duration_seconds', 10.0)
        amplitude_db = data.get('amplitude_db', -20.0)
        
        sine_config = tone_gen.generate_sine_wave(frequency_hz, duration_seconds, amplitude_db)
        
        return jsonify({
            'ok': True,
            'sine_wave': sine_config,
            'instructions': 'Use for testing specific frequency response and room modes'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/testtones/sweep', methods=['POST'])
def api_testtones_sweep():
    """Generate frequency sweep."""
    try:
        data = request.json or {}
        
        start_hz = data.get('start_hz', 20)
        end_hz = data.get('end_hz', 200)
        duration_seconds = data.get('duration_seconds', 30.0)
        sweep_type = data.get('sweep_type', 'logarithmic')
        amplitude_db = data.get('amplitude_db', -20.0)
        
        sweep_config = tone_gen.generate_sweep_tone(
            start_hz, end_hz, duration_seconds, sweep_type, amplitude_db
        )
        
        return jsonify({
            'ok': True,
            'sweep_tone': sweep_config,
            'instructions': 'Listen for smooth response - variations indicate room modes'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/testtones/pink-noise', methods=['POST'])
def api_testtones_pink_noise():
    """Generate pink noise."""
    try:
        data = request.json or {}
        
        duration_seconds = data.get('duration_seconds', 30.0)
        amplitude_db = data.get('amplitude_db', -20.0)
        bass_weighted = data.get('bass_weighted', True)
        lowpass_hz = data.get('lowpass_hz', 200)
        
        noise_config = tone_gen.generate_pink_noise(
            duration_seconds, amplitude_db, bass_weighted, lowpass_hz
        )
        
        return jsonify({
            'ok': True,
            'pink_noise': noise_config,
            'instructions': 'Use with SPL meter for level calibration'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/testtones/burst', methods=['POST'])
def api_testtones_burst():
    """Generate tone burst."""
    try:
        data = request.json or {}
        
        frequency_hz = data.get('frequency_hz', 40)
        burst_duration_ms = data.get('burst_duration_ms', 100)
        silence_duration_ms = data.get('silence_duration_ms', 400)
        num_bursts = data.get('num_bursts', 10)
        amplitude_db = data.get('amplitude_db', -10.0)
        
        burst_config = tone_gen.generate_burst_tone(
            frequency_hz, burst_duration_ms, silence_duration_ms, num_bursts, amplitude_db
        )
        
        return jsonify({
            'ok': True,
            'burst_tone': burst_config,
            'instructions': 'Test transient response and port behavior'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/testtones/multitone', methods=['POST'])
def api_testtones_multitone():
    """Generate multi-frequency test signal."""
    try:
        data = request.json or {}
        
        frequencies = data.get('frequencies', [30, 40, 50, 63, 80])
        duration_seconds = data.get('duration_seconds', 10.0)
        amplitude_db_each = data.get('amplitude_db_each', -26.0)
        
        multitone_config = tone_gen.generate_multitone(frequencies, duration_seconds, amplitude_db_each)
        
        return jsonify({
            'ok': True,
            'multitone': multitone_config,
            'instructions': 'Test intermodulation distortion - listen for unwanted tones'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/testtones/calibration-sequence')
def api_testtones_calibration_sequence():
    """Get complete calibration sequence."""
    try:
        sequence = tone_gen.create_calibration_sequence()
        
        return jsonify({
            'ok': True,
            'calibration_sequence': sequence
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/spl/test-tones')
def api_spl_test_tones():
    """Get SPL test tone configurations."""
    try:
        spl_tones = tone_gen.create_spl_test_tones()
        
        return jsonify({
            'ok': True,
            'spl_test_tones': spl_tones
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/spl/measure', methods=['POST'])
def api_spl_measure():
    """Simulate SPL measurement."""
    try:
        data = request.json or {}
        
        frequency_hz = data.get('frequency_hz', 80)
        subwoofer_level = data.get('subwoofer_level', 75.0)
        room_acoustics = data.get('room_acoustics', 'average')
        
        measurement = tone_gen.simulate_spl_measurement(frequency_hz, subwoofer_level, room_acoustics)
        
        measurement_id = f"spl_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        db.save_measurement(
            measurement_id=measurement_id,
            measurement_type='spl',
            measurement_data=measurement,
            frequency_hz=frequency_hz,
            spl_db=measurement['measured_spl_db'],
            room_acoustics=room_acoustics
        )
        
        return jsonify({
            'ok': True,
            'spl_measurement': measurement,
            'measurement_id': measurement_id
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/config/current')
def api_config_current():
    """Get current session configuration."""
    return jsonify({
        'ok': True,
        'current_configuration': current_session
    })


@app.route('/api/config/save', methods=['POST'])
def api_config_save():
    """Save current configuration."""
    try:
        data = request.json or {}
        config_name = data.get('config_name', f"bass_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        notes = data.get('notes')
        
        if not current_session.get('subwoofers'):
            return jsonify({'ok': False, 'error': 'No subwoofer configuration to save'}), 400
        
        config_id = db.save_configuration(
            config_name=config_name,
            subwoofer_config=current_session['subwoofers'][0] if len(current_session['subwoofers']) == 1 else current_session['subwoofers'],
            subsonic_filter=current_session.get('subsonic_filter'),
            lowpass_crossover=current_session.get('lowpass_crossover'),
            bass_boost=current_session.get('bass_boost'),
            phase_config=current_session.get('phase_config'),
            delay_config=current_session.get('delay_config'),
            notes=notes
        )
        
        return jsonify({
            'ok': True,
            'config_id': config_id,
            'config_name': config_name,
            'message': 'Configuration saved successfully'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/config/load/<int:config_id>')
def api_config_load(config_id):
    """Load saved configuration."""
    try:
        config = db.get_configuration(config_id)
        
        if not config:
            return jsonify({'ok': False, 'error': 'Configuration not found'}), 404
        
        current_session['subwoofers'] = [config['subwoofer_config']] if isinstance(config['subwoofer_config'], dict) else config['subwoofer_config']
        current_session['subsonic_filter'] = config.get('subsonic_filter')
        current_session['lowpass_crossover'] = config.get('lowpass_crossover')
        current_session['bass_boost'] = config.get('bass_boost')
        current_session['phase_config'] = config.get('phase_config')
        current_session['delay_config'] = config.get('delay_config')
        
        return jsonify({
            'ok': True,
            'configuration': config,
            'message': 'Configuration loaded successfully'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/config/list')
def api_config_list():
    """List all saved configurations."""
    try:
        limit = int(request.args.get('limit', 50))
        configs = db.list_configurations(limit)
        
        return jsonify({
            'ok': True,
            'configurations': configs,
            'total': len(configs)
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/presets/list')
def api_presets_list():
    """List all presets."""
    try:
        preset_type = request.args.get('preset_type')
        presets = db.list_presets(preset_type)
        
        return jsonify({
            'ok': True,
            'presets': presets,
            'total': len(presets)
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/measurements/history')
def api_measurements_history():
    """Get measurement history."""
    try:
        measurement_type = request.args.get('type')
        limit = int(request.args.get('limit', 100))
        
        measurements = db.get_measurements(measurement_type, limit)
        
        return jsonify({
            'ok': True,
            'measurements': measurements,
            'total': len(measurements)
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/dsp/sync', methods=['POST'])
def api_dsp_sync():
    """Sync with main DSP service (port 8100)."""
    try:
        data = request.json or {}
        
        dsp_settings = {
            'bass_management': {
                'enabled': True,
                'subsonic_filter': current_session.get('subsonic_filter'),
                'lowpass_crossover': current_session.get('lowpass_crossover'),
                'bass_boost': current_session.get('bass_boost'),
                'subwoofer_level': current_session['subwoofers'][0].get('level_db', 0) if current_session.get('subwoofers') else 0,
                'phase': current_session.get('phase_config', {}).get('phase_degrees', 0),
                'delay_ms': current_session.get('delay_config', {}).get('recommended_delay_adjustment_ms', 0)
            },
            'sync_timestamp': datetime.now().isoformat(),
            'dsp_port': 8100,
            'bass_port': 8400
        }
        
        return jsonify({
            'ok': True,
            'dsp_sync': dsp_settings,
            'message': 'Configuration ready for DSP integration',
            'instructions': 'Apply these settings to DSP service at port 8100'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/export/android', methods=['POST'])
def api_export_android():
    """Export bass settings for EOENKK Android integration."""
    try:
        android_config = {
            'bass_management': {
                'version': '1.0',
                'subsonic_filter': current_session.get('subsonic_filter'),
                'lowpass_crossover': current_session.get('lowpass_crossover'),
                'bass_boost': current_session.get('bass_boost'),
                'subwoofers': current_session.get('subwoofers', []),
                'phase_config': current_session.get('phase_config'),
                'delay_config': current_session.get('delay_config')
            },
            'export_timestamp': datetime.now().isoformat(),
            'instructions': [
                '1. Copy this JSON configuration',
                '2. Open EOENKK Android 15 head unit settings',
                '3. Navigate to DSP → Bass Management',
                '4. Import configuration',
                '5. Verify all settings and apply'
            ]
        }
        
        return jsonify({
            'ok': True,
            'android_config': android_config
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('BASS_PORT', 8400))
    print(f"Starting Bass Management System on port {port}")
    print(f"Access at: http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
