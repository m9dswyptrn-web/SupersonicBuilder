import math
import json
from typing import Dict, List, Any, Optional, Tuple


class MeasurementTools:
    """
    Measurement microphone support and analysis tools.
    Handles REW import, sweep tones, impulse response analysis.
    """
    
    def __init__(self):
        self.sample_rate = 48000
        self.sweep_duration = 10.0
    
    def generate_sweep_tone(
        self,
        start_freq: float = 20.0,
        end_freq: float = 20000.0,
        duration: float = 10.0,
        sample_rate: int = 48000
    ) -> Dict[str, Any]:
        """
        Generate logarithmic sweep tone parameters for acoustic measurement.
        Returns sweep configuration data.
        """
        num_samples = int(duration * sample_rate)
        
        k = (end_freq / start_freq) ** (1 / duration)
        
        return {
            'type': 'logarithmic_sweep',
            'start_frequency_hz': start_freq,
            'end_frequency_hz': end_freq,
            'duration_seconds': duration,
            'sample_rate_hz': sample_rate,
            'num_samples': num_samples,
            'sweep_rate': k,
            'instructions': [
                '1. Play this sweep tone through the system',
                '2. Record the output with a calibrated measurement microphone',
                '3. Import the recording for impulse response analysis',
                '4. Position microphone at listening position'
            ],
            'format': {
                'bit_depth': 24,
                'channels': 1,
                'recommended_level_db': -6
            }
        }
    
    def import_rew_measurement(
        self,
        rew_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Import measurement data from REW (Room EQ Wizard).
        Processes frequency response and impulse response data.
        """
        imported = {
            'measurement_id': rew_data.get('measurement_id', 'rew_import'),
            'measurement_date': rew_data.get('date'),
            'microphone': rew_data.get('microphone', 'Unknown'),
            'calibration': rew_data.get('calibration'),
            'data': {}
        }
        
        if 'frequency_response' in rew_data:
            fr = rew_data['frequency_response']
            imported['data']['frequency_response'] = self._process_frequency_response(fr)
        
        if 'impulse_response' in rew_data:
            ir = rew_data['impulse_response']
            imported['data']['impulse_response'] = self._process_impulse_response(ir)
        
        if 'waterfall' in rew_data:
            imported['data']['waterfall'] = rew_data['waterfall']
        
        imported['analysis'] = self._analyze_measurement(imported['data'])
        
        return imported
    
    def _process_frequency_response(
        self,
        fr_data: List[Tuple[float, float]]
    ) -> Dict[str, Any]:
        """Process raw frequency response data."""
        frequencies = []
        magnitudes = []
        
        for freq, mag in fr_data:
            frequencies.append(freq)
            magnitudes.append(mag)
        
        avg_magnitude = sum(magnitudes) / len(magnitudes) if magnitudes else 0
        
        deviations = [abs(mag - avg_magnitude) for mag in magnitudes]
        max_deviation = max(deviations) if deviations else 0
        
        return {
            'frequencies': frequencies,
            'magnitudes_db': magnitudes,
            'average_magnitude_db': avg_magnitude,
            'max_deviation_db': max_deviation,
            'num_points': len(frequencies)
        }
    
    def _process_impulse_response(
        self,
        ir_data: List[float]
    ) -> Dict[str, Any]:
        """Process impulse response data."""
        peak_index = ir_data.index(max(ir_data, key=abs))
        peak_value = ir_data[peak_index]
        
        energy = sum(x**2 for x in ir_data)
        rms = math.sqrt(energy / len(ir_data)) if ir_data else 0
        
        rt60 = self._estimate_rt60(ir_data, peak_index)
        
        return {
            'samples': ir_data,
            'peak_index': peak_index,
            'peak_value': peak_value,
            'rms': rms,
            'total_energy': energy,
            'rt60_estimate_ms': rt60,
            'num_samples': len(ir_data)
        }
    
    def _estimate_rt60(
        self,
        ir_data: List[float],
        peak_index: int
    ) -> float:
        """Estimate RT60 from impulse response."""
        if peak_index >= len(ir_data):
            return 0.0
        
        decay_samples = ir_data[peak_index:]
        if not decay_samples:
            return 0.0
        
        energies = [x**2 for x in decay_samples]
        cumulative = []
        total = sum(energies)
        
        for i, e in enumerate(energies):
            cumulative.append(sum(energies[i:]) / total if total > 0 else 0)
        
        t60_point = None
        for i, level in enumerate(cumulative):
            if level <= 0.001:
                t60_point = i
                break
        
        if t60_point:
            rt60_ms = (t60_point / self.sample_rate) * 1000
        else:
            rt60_ms = 100.0
        
        return rt60_ms
    
    def _analyze_measurement(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze measurement data and provide insights."""
        analysis = {
            'issues_found': [],
            'recommendations': []
        }
        
        if 'frequency_response' in data:
            fr = data['frequency_response']
            
            if fr['max_deviation_db'] > 10.0:
                analysis['issues_found'].append({
                    'issue': 'Large frequency response variation',
                    'severity': 'high',
                    'value': f"{fr['max_deviation_db']:.1f} dB",
                    'description': 'Frequency response shows significant peaks and dips'
                })
                analysis['recommendations'].append({
                    'action': 'Apply parametric EQ corrections',
                    'priority': 'high',
                    'details': 'Use narrow Q filters to address specific problem frequencies'
                })
            
            if fr['average_magnitude_db'] < -10.0:
                analysis['issues_found'].append({
                    'issue': 'Low overall level',
                    'severity': 'medium',
                    'value': f"{fr['average_magnitude_db']:.1f} dB",
                    'description': 'System output level is lower than optimal'
                })
                analysis['recommendations'].append({
                    'action': 'Increase system gain',
                    'priority': 'medium',
                    'details': 'Adjust amplifier gain settings for better signal-to-noise ratio'
                })
        
        if 'impulse_response' in data:
            ir = data['impulse_response']
            
            if ir['rt60_estimate_ms'] > 150.0:
                analysis['issues_found'].append({
                    'issue': 'Excessive reverberation',
                    'severity': 'medium',
                    'value': f"{ir['rt60_estimate_ms']:.0f} ms",
                    'description': 'Cabin has long reverberation time'
                })
                analysis['recommendations'].append({
                    'action': 'Add acoustic damping',
                    'priority': 'low',
                    'details': 'Consider adding sound deadening material to reduce reflections'
                })
        
        return analysis
    
    def calculate_impulse_response_from_sweep(
        self,
        recorded_sweep: List[float],
        original_sweep_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate impulse response from recorded sweep tone.
        This is a simplified version - real implementation would use FFT deconvolution.
        """
        return {
            'method': 'sweep_deconvolution',
            'note': 'Simplified impulse response extraction',
            'samples': recorded_sweep[:1000],
            'sample_rate': original_sweep_params.get('sample_rate_hz', 48000),
            'length_samples': 1000
        }
    
    def generate_test_signals(self) -> Dict[str, Dict[str, Any]]:
        """Generate various test signal configurations."""
        return {
            'pink_noise': {
                'type': 'pink_noise',
                'duration_seconds': 30.0,
                'level_db': -20.0,
                'use_case': 'General system testing and RTA analysis',
                'instructions': 'Play for 30 seconds while measuring with RTA'
            },
            'white_noise': {
                'type': 'white_noise',
                'duration_seconds': 30.0,
                'level_db': -20.0,
                'use_case': 'High-frequency response testing',
                'instructions': 'Use for tweeter testing and high-end calibration'
            },
            'sine_sweep': self.generate_sweep_tone(),
            'impulse': {
                'type': 'impulse',
                'duration_seconds': 0.001,
                'level_db': -6.0,
                'use_case': 'Impulse response measurement',
                'instructions': 'Single sharp impulse for direct IR measurement'
            },
            'multitone': {
                'type': 'multitone',
                'frequencies_hz': [100, 315, 1000, 3150, 10000],
                'duration_seconds': 10.0,
                'level_db': -20.0,
                'use_case': 'Multi-frequency distortion testing',
                'instructions': 'Play all tones simultaneously to check for intermodulation'
            }
        }
    
    def calibrate_microphone(
        self,
        mic_sensitivity_mv_pa: float = 10.0,
        reference_level_db: float = 94.0
    ) -> Dict[str, Any]:
        """
        Calculate microphone calibration values.
        Standard reference: 94 dB SPL = 1 Pa = 1000 mV/Pa mic output
        """
        sensitivity_db = 20 * math.log10(mic_sensitivity_mv_pa / 1000.0)
        
        return {
            'microphone_sensitivity_mv_pa': mic_sensitivity_mv_pa,
            'sensitivity_db_re_1v': sensitivity_db,
            'reference_level_db_spl': reference_level_db,
            'calibration_factor': 10 ** ((reference_level_db - sensitivity_db) / 20),
            'instructions': [
                f'1. Use {reference_level_db} dB SPL calibrator',
                f'2. Microphone sensitivity: {mic_sensitivity_mv_pa} mV/Pa',
                '3. Verify calibration before each measurement session',
                '4. Apply calibration factor to all measurements'
            ]
        }
    
    def analyze_phase_response(
        self,
        left_channel: List[float],
        right_channel: List[float]
    ) -> Dict[str, Any]:
        """
        Analyze phase relationship between left and right channels.
        Important for center image quality.
        """
        if len(left_channel) != len(right_channel):
            return {'error': 'Channel lengths must match'}
        
        cross_correlation = 0.0
        for l, r in zip(left_channel, right_channel):
            cross_correlation += l * r
        
        left_energy = sum(x**2 for x in left_channel)
        right_energy = sum(x**2 for x in right_channel)
        
        if left_energy > 0 and right_energy > 0:
            phase_correlation = cross_correlation / math.sqrt(left_energy * right_energy)
        else:
            phase_correlation = 0.0
        
        phase_quality = 'excellent' if phase_correlation > 0.9 else \
                       'good' if phase_correlation > 0.7 else \
                       'fair' if phase_correlation > 0.5 else 'poor'
        
        return {
            'phase_correlation': phase_correlation,
            'phase_quality': phase_quality,
            'center_image_score': phase_correlation * 100,
            'recommendations': [
                'Check speaker wiring polarity' if phase_correlation < 0.5 else None,
                'Verify time alignment settings' if phase_correlation < 0.7 else None,
                'Phase relationship is good' if phase_correlation > 0.9 else None
            ]
        }
    
    def get_measurement_guide(self) -> Dict[str, Any]:
        """Get comprehensive measurement procedure guide."""
        return {
            'equipment_needed': [
                'Calibrated measurement microphone (UMIK-1 recommended)',
                'Microphone stand or tripod',
                '94 dB SPL calibrator',
                'USB audio interface or direct USB microphone',
                'REW (Room EQ Wizard) software or equivalent'
            ],
            'preparation': [
                '1. Close all windows and doors',
                '2. Turn off HVAC system',
                '3. Eliminate external noise sources',
                '4. Set system volume to reference level',
                '5. Calibrate microphone'
            ],
            'measurement_positions': {
                'driver_seat': {
                    'description': 'Primary listening position',
                    'mic_placement': 'At ear height in driver headrest position',
                    'coordinates': {'x': 32, 'y': 12, 'z': 20}
                },
                'passenger_seat': {
                    'description': 'Secondary listening position',
                    'mic_placement': 'At ear height in passenger headrest position',
                    'coordinates': {'x': 32, 'y': 43, 'z': 20}
                },
                'center': {
                    'description': 'Center reference position',
                    'mic_placement': 'Center of cabin at ear height',
                    'coordinates': {'x': 32, 'y': 27.5, 'z': 20}
                }
            },
            'measurement_sequence': [
                '1. Generate and play log sweep tone',
                '2. Record sweep with measurement microphone',
                '3. Import recording into REW',
                '4. Generate impulse response',
                '5. Analyze frequency response',
                '6. Export data for EQ correction',
                '7. Repeat for each listening position'
            ],
            'analysis_checklist': [
                'Frequency response ±3dB from 80Hz-16kHz',
                'No major peaks or dips >6dB',
                'Smooth response through crossover regions',
                'Left/right channel matching within 2dB',
                'RT60 < 100ms for optimal clarity',
                'Phase correlation > 0.9 for center image'
            ]
        }
