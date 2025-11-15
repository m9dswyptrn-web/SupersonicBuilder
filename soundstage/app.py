#!/usr/bin/env python3
"""
Sound Stage Optimizer
Perfect acoustic positioning and AI-powered tuning for 2014 Chevy Sonic
Port: 8200
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.soundstage.database import SoundStageDatabase
from services.soundstage.acoustics import CabinAcoustics
from services.soundstage.positioning import SpeakerPositioning
from services.soundstage.measurement import MeasurementTools
from services.soundstage.ai_tuner import AITuner

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

db = SoundStageDatabase()
acoustics = CabinAcoustics()
positioning = SpeakerPositioning()
measurement = MeasurementTools()
ai_tuner = AITuner()

DSP_SERVICE_URL = os.getenv('DSP_SERVICE_URL', 'http://localhost:8100')

current_state = {
    'listening_position': 'driver',
    'speaker_positions': positioning.SONIC_SPEAKER_DEFAULTS.copy(),
    'balance_db': 0.0,
    'fader_db': 0.0,
    'time_alignment': {},
    'center_image_settings': {}
}


@app.route('/')
def index():
    """Serve the Sound Stage Optimizer interface."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('PORT', 8200))
    stats = db.get_stats()
    
    return jsonify({
        'ok': True,
        'service': 'sound_stage_optimizer',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'features': [
            '3D speaker positioning',
            'Chevy Sonic acoustic modeling',
            'Time alignment calculation',
            'Balance/fader optimization',
            'Center image focus',
            'AI-powered tuning (Claude)',
            'REW measurement import',
            'Sweep tone generation',
            'DSP integration',
            'Preset management'
        ],
        'ai_available': ai_tuner.has_api_key,
        'database': stats
    })


@app.route('/api/positioning/speakers', methods=['GET', 'POST'])
def api_positioning_speakers():
    """Get or update speaker positions."""
    try:
        if request.method == 'POST':
            data = request.json or {}
            
            for speaker_name, position in data.items():
                if isinstance(position, dict):
                    positioning.set_speaker_position(
                        speaker_name,
                        position.get('x', 0),
                        position.get('y', 0),
                        position.get('z', 0),
                        position.get('angle_horizontal'),
                        position.get('angle_vertical')
                    )
                    current_state['speaker_positions'][speaker_name] = position
        
        return jsonify({
            'ok': True,
            'speaker_positions': positioning.speaker_positions,
            'listening_positions': positioning.listening_positions
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/positioning/distances/<listening_position>')
def api_positioning_distances(listening_position):
    """Calculate distances from all speakers to listening position."""
    try:
        distances = positioning.calculate_all_distances(listening_position)
        
        return jsonify({
            'ok': True,
            'listening_position': listening_position,
            'distances_inches': distances,
            'distances_cm': {k: v * 2.54 for k, v in distances.items()}
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/positioning/time-alignment/<listening_position>')
def api_positioning_time_alignment(listening_position):
    """Calculate time alignment delays."""
    try:
        reference_speaker = request.args.get('reference_speaker')
        delays = positioning.calculate_time_delays(listening_position, reference_speaker)
        
        current_state['time_alignment'] = delays
        current_state['listening_position'] = listening_position
        
        return jsonify({
            'ok': True,
            'listening_position': listening_position,
            'time_delays_ms': delays,
            'reference_speaker': reference_speaker or 'furthest'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/positioning/balance/<listening_position>')
def api_positioning_balance(listening_position):
    """Calculate balance corrections."""
    try:
        corrections = positioning.calculate_balance_correction(listening_position)
        
        return jsonify({
            'ok': True,
            'listening_position': listening_position,
            'balance_corrections_db': corrections
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/positioning/fader/<listening_position>')
def api_positioning_fader(listening_position):
    """Calculate optimal fader settings."""
    try:
        fader_settings = positioning.calculate_fader_settings(listening_position)
        
        current_state['fader_db'] = fader_settings['fader_db']
        
        return jsonify({
            'ok': True,
            'listening_position': listening_position,
            'fader_settings': fader_settings
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/positioning/center-image/<listening_position>')
def api_positioning_center_image(listening_position):
    """Calculate center image settings."""
    try:
        center_settings = positioning.calculate_center_image(listening_position)
        
        current_state['center_image_settings'] = center_settings
        
        return jsonify({
            'ok': True,
            'listening_position': listening_position,
            'center_image': center_settings
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/positioning/visualize/<listening_position>')
def api_positioning_visualize(listening_position):
    """Get 3D visualization data."""
    try:
        visualization = positioning.create_soundstage_visualization(listening_position)
        
        return jsonify({
            'ok': True,
            'visualization': visualization
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/acoustics/cabin-info')
def api_acoustics_cabin_info():
    """Get complete cabin acoustic information."""
    try:
        cabin_info = acoustics.get_cabin_info()
        
        return jsonify({
            'ok': True,
            'cabin_acoustics': cabin_info,
            'vehicle': '2014 Chevy Sonic LTZ'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/acoustics/room-modes')
def api_acoustics_room_modes():
    """Calculate room modes."""
    try:
        modes = acoustics.calculate_room_modes()
        
        return jsonify({
            'ok': True,
            'room_modes': modes,
            'note': 'These frequencies may cause acoustic resonances'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/acoustics/rt60')
def api_acoustics_rt60():
    """Calculate RT60 values."""
    try:
        frequency_band = request.args.get('frequency', '1000Hz')
        rt60 = acoustics.calculate_rt60(frequency_band)
        
        all_rt60 = {
            freq: acoustics.calculate_rt60(freq)
            for freq in ['125Hz', '250Hz', '500Hz', '1000Hz', '2000Hz', '4000Hz']
        }
        
        return jsonify({
            'ok': True,
            'rt60_seconds': rt60,
            'frequency_band': frequency_band,
            'all_bands': all_rt60
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/acoustics/eq-correction')
def api_acoustics_eq_correction():
    """Get EQ correction recommendations."""
    try:
        corrections = acoustics.recommend_eq_correction()
        
        return jsonify({
            'ok': True,
            'eq_corrections': corrections,
            'note': 'Apply these corrections to compensate for cabin acoustics'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/acoustics/early-reflections', methods=['POST'])
def api_acoustics_early_reflections():
    """Calculate early reflections."""
    try:
        data = request.json or {}
        speaker_pos = tuple(data.get('speaker_position', [12, 8, 24]))
        listener_pos = tuple(data.get('listener_position', [32, 12, 20]))
        
        reflections = acoustics.calculate_early_reflections(speaker_pos, listener_pos)
        
        return jsonify({
            'ok': True,
            'early_reflections': reflections
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/measurement/sweep-tone')
def api_measurement_sweep_tone():
    """Generate sweep tone parameters."""
    try:
        start_freq = float(request.args.get('start_freq', 20))
        end_freq = float(request.args.get('end_freq', 20000))
        duration = float(request.args.get('duration', 10))
        
        sweep = measurement.generate_sweep_tone(start_freq, end_freq, duration)
        
        return jsonify({
            'ok': True,
            'sweep_tone': sweep
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/measurement/import-rew', methods=['POST'])
def api_measurement_import_rew():
    """Import REW measurement data."""
    try:
        data = request.json or {}
        rew_data = data.get('rew_data', {})
        
        imported = measurement.import_rew_measurement(rew_data)
        
        measurement_id = imported.get('measurement_id', f"meas_{int(datetime.now().timestamp())}")
        db.save_measurement(
            measurement_id=measurement_id,
            measurement_type='rew_import',
            frequency_response=imported.get('data', {}).get('frequency_response'),
            impulse_response=imported.get('data', {}).get('impulse_response'),
            rew_import_data=rew_data
        )
        
        return jsonify({
            'ok': True,
            'imported_data': imported,
            'saved_to_database': True
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/measurement/test-signals')
def api_measurement_test_signals():
    """Get test signal configurations."""
    try:
        signals = measurement.generate_test_signals()
        
        return jsonify({
            'ok': True,
            'test_signals': signals
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/measurement/calibrate')
def api_measurement_calibrate():
    """Get microphone calibration info."""
    try:
        sensitivity = float(request.args.get('sensitivity', 10.0))
        reference = float(request.args.get('reference', 94.0))
        
        calibration = measurement.calibrate_microphone(sensitivity, reference)
        
        return jsonify({
            'ok': True,
            'calibration': calibration
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/measurement/guide')
def api_measurement_guide():
    """Get measurement procedure guide."""
    try:
        guide = measurement.get_measurement_guide()
        
        return jsonify({
            'ok': True,
            'measurement_guide': guide
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/measurement/phase-analysis', methods=['POST'])
def api_measurement_phase_analysis():
    """Analyze phase correlation between channels."""
    try:
        data = request.json or {}
        left = data.get('left_channel', [])
        right = data.get('right_channel', [])
        
        analysis = measurement.analyze_phase_response(left, right)
        
        return jsonify({
            'ok': True,
            'phase_analysis': analysis
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ai/analyze', methods=['POST'])
def api_ai_analyze():
    """AI-powered analysis of current setup."""
    try:
        data = request.json or {}
        listening_pos = data.get('listening_position', 'driver')
        
        speaker_pos = positioning.speaker_positions
        acoustic_data = acoustics.get_cabin_info()
        current_settings = data.get('current_settings', current_state)
        
        analysis = ai_tuner.analyze_setup(
            speaker_pos,
            acoustic_data,
            listening_pos,
            current_settings
        )
        
        tuning_id = f"tune_{int(datetime.now().timestamp())}"
        if 'recommendations' in analysis:
            db.save_ai_tuning(
                tuning_id=tuning_id,
                analysis=analysis.get('analysis', ''),
                recommendations=analysis.get('recommendations', {}),
                model=analysis.get('model', 'rule_based'),
                tokens_used=analysis.get('tokens_used'),
                confidence_score=analysis.get('confidence_score')
            )
        
        return jsonify({
            'ok': True,
            'tuning_id': tuning_id,
            **analysis
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ai/auto-tune', methods=['POST'])
def api_ai_auto_tune():
    """Generate one-click auto-tune settings."""
    try:
        data = request.json or {}
        listening_pos = data.get('listening_position', 'driver')
        
        speaker_pos = positioning.speaker_positions
        acoustic_data = acoustics.get_cabin_info()
        
        auto_tune = ai_tuner.suggest_auto_tune(speaker_pos, acoustic_data, listening_pos)
        
        return jsonify({
            'ok': True,
            **auto_tune
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ai/tips')
def api_ai_tips():
    """Get tuning tips."""
    try:
        listening_pos = request.args.get('listening_position', 'driver')
        tips = ai_tuner.get_tuning_tips(listening_pos)
        
        return jsonify({
            'ok': True,
            'tuning_tips': tips
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/presets')
def api_presets_list():
    """List all presets."""
    try:
        presets = db.list_presets()
        
        builtin_presets = [
            {
                'preset_name': 'driver_optimal',
                'description': 'Optimized for driver seat',
                'listening_position': 'driver',
                'builtin': True
            },
            {
                'preset_name': 'all_seats_balanced',
                'description': 'Balanced for all passengers',
                'listening_position': 'center',
                'builtin': True
            },
            {
                'preset_name': 'front_row_focus',
                'description': 'Optimized for front row',
                'listening_position': 'driver',
                'builtin': True
            },
            {
                'preset_name': 'rear_passengers',
                'description': 'Optimized for rear seats',
                'listening_position': 'rear_left',
                'builtin': True
            }
        ]
        
        return jsonify({
            'ok': True,
            'custom_presets': presets,
            'builtin_presets': builtin_presets,
            'total': len(presets) + len(builtin_presets)
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/presets/<preset_name>')
def api_presets_get(preset_name):
    """Get specific preset."""
    try:
        preset = db.get_preset(preset_name)
        
        if not preset:
            builtin = _get_builtin_preset(preset_name)
            if builtin:
                return jsonify({'ok': True, 'preset': builtin, 'builtin': True})
            return jsonify({'ok': False, 'error': 'Preset not found'}), 404
        
        return jsonify({'ok': True, 'preset': preset, 'builtin': False})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/presets/save', methods=['POST'])
def api_presets_save():
    """Save preset."""
    try:
        data = request.json or {}
        
        preset_name = data.get('preset_name', f"custom_{int(datetime.now().timestamp())}")
        description = data.get('description', '')
        listening_pos = data.get('listening_position', 'driver')
        
        speaker_pos = data.get('speaker_positions', positioning.speaker_positions)
        balance = data.get('balance_settings', {'balance_db': current_state.get('balance_db', 0)})
        fader = data.get('fader_settings', {'fader_db': current_state.get('fader_db', 0)})
        acoustic_corr = data.get('acoustic_corrections')
        time_align = data.get('time_alignment', current_state.get('time_alignment'))
        center_image = data.get('center_image_settings', current_state.get('center_image_settings'))
        
        db.save_preset(
            preset_name=preset_name,
            speaker_positions=speaker_pos,
            balance_settings=balance,
            fader_settings=fader,
            description=description,
            acoustic_corrections=acoustic_corr,
            time_alignment=time_align,
            center_image_settings=center_image,
            listening_position=listening_pos
        )
        
        return jsonify({
            'ok': True,
            'preset_name': preset_name,
            'message': 'Preset saved successfully'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/presets/delete/<preset_name>', methods=['DELETE'])
def api_presets_delete(preset_name):
    """Delete preset."""
    try:
        db.delete_preset(preset_name)
        
        return jsonify({
            'ok': True,
            'message': f'Preset {preset_name} deleted'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/dsp/apply', methods=['POST'])
def api_dsp_apply():
    """Apply soundstage settings to DSP service."""
    try:
        data = request.json or {}
        listening_pos = data.get('listening_position', 'driver')
        
        export_data = positioning.export_to_dsp(listening_pos)
        
        dsp_response = _send_to_dsp(export_data)
        
        return jsonify({
            'ok': True,
            'applied_to_dsp': dsp_response.get('ok', False),
            'dsp_response': dsp_response,
            'settings_applied': export_data
        })
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e),
            'note': 'DSP service may not be available'
        }), 500


@app.route('/api/state')
def api_state_get():
    """Get current state."""
    return jsonify({
        'ok': True,
        'current_state': current_state
    })


@app.route('/api/state', methods=['POST'])
def api_state_update():
    """Update current state."""
    try:
        data = request.json or {}
        current_state.update(data)
        
        return jsonify({
            'ok': True,
            'current_state': current_state
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


def _get_builtin_preset(preset_name):
    """Get builtin preset configuration."""
    presets = {
        'driver_optimal': {
            'preset_name': 'driver_optimal',
            'description': 'Optimized for driver seat listening',
            'listening_position': 'driver',
            'speaker_positions': positioning.SONIC_SPEAKER_DEFAULTS,
            'balance_settings': {'balance_db': -1.5},
            'fader_settings': {'fader_db': 3.0},
            'time_alignment': positioning.calculate_time_delays('driver')
        },
        'all_seats_balanced': {
            'preset_name': 'all_seats_balanced',
            'description': 'Balanced sound for all passengers',
            'listening_position': 'center',
            'speaker_positions': positioning.SONIC_SPEAKER_DEFAULTS,
            'balance_settings': {'balance_db': 0.0},
            'fader_settings': {'fader_db': 0.0},
            'time_alignment': positioning.calculate_time_delays('center')
        },
        'front_row_focus': {
            'preset_name': 'front_row_focus',
            'description': 'Focus on front row passengers',
            'listening_position': 'driver',
            'speaker_positions': positioning.SONIC_SPEAKER_DEFAULTS,
            'balance_settings': {'balance_db': 0.0},
            'fader_settings': {'fader_db': 4.0},
            'time_alignment': positioning.calculate_time_delays('driver')
        },
        'rear_passengers': {
            'preset_name': 'rear_passengers',
            'description': 'Optimized for rear seat passengers',
            'listening_position': 'rear_left',
            'speaker_positions': positioning.SONIC_SPEAKER_DEFAULTS,
            'balance_settings': {'balance_db': 0.0},
            'fader_settings': {'fader_db': -3.0},
            'time_alignment': positioning.calculate_time_delays('rear_left')
        }
    }
    
    return presets.get(preset_name)


def _send_to_dsp(settings):
    """Send settings to DSP service on port 8100."""
    try:
        response = requests.post(
            f"{DSP_SERVICE_URL}/api/time-alignment/calculate",
            json={'speaker_delays': settings.get('time_delays_ms', {})},
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {'ok': False, 'error': str(e)}


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8200))
    app.run(host='0.0.0.0', port=port, debug=False)
