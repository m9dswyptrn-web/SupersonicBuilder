#!/usr/bin/env python3
"""
Phase Alignment Module
Phase control and alignment tools for subwoofer integration
"""

import math
from typing import Dict, List, Optional, Tuple


class PhaseAlignment:
    """Phase control and group delay compensation."""
    
    def __init__(self):
        """Initialize phase alignment tools."""
        self.speed_of_sound_ms = 343.0
        
    def set_phase(self, phase_degrees: float, fine_adjust: bool = False) -> dict:
        """
        Set subwoofer phase.
        
        Args:
            phase_degrees: Phase setting (0-180°)
            fine_adjust: Enable 1° increment fine adjustment
            
        Returns:
            Phase configuration
        """
        if not 0 <= phase_degrees <= 180:
            raise ValueError("Phase must be between 0 and 180 degrees")
        
        if not fine_adjust:
            if phase_degrees not in [0, 180]:
                phase_degrees = 0 if phase_degrees < 90 else 180
        else:
            phase_degrees = round(phase_degrees)
        
        inverted = phase_degrees == 180
        delay_equivalent_at_80hz = self._phase_to_delay(phase_degrees, 80)
        
        return {
            'phase_degrees': round(phase_degrees, 1),
            'inverted': inverted,
            'fine_adjustment_enabled': fine_adjust,
            'delay_equivalent_ms_at_80hz': round(delay_equivalent_at_80hz, 3),
            'recommendation': self._phase_recommendation(phase_degrees)
        }
    
    def calculate_phase_from_delay(self, delay_ms: float, frequency_hz: float) -> dict:
        """
        Calculate phase shift from time delay at specific frequency.
        
        Args:
            delay_ms: Time delay in milliseconds
            frequency_hz: Test frequency
            
        Returns:
            Phase calculation results
        """
        period_ms = 1000.0 / frequency_hz
        
        phase_degrees = (delay_ms / period_ms * 360.0) % 360
        
        if phase_degrees > 180:
            phase_degrees = phase_degrees - 360
        
        wavelength_meters = self.speed_of_sound_ms / frequency_hz
        distance_meters = (delay_ms / 1000.0) * self.speed_of_sound_ms
        
        return {
            'delay_ms': round(delay_ms, 3),
            'frequency_hz': frequency_hz,
            'phase_shift_degrees': round(phase_degrees, 1),
            'period_ms': round(period_ms, 3),
            'wavelength_meters': round(wavelength_meters, 3),
            'equivalent_distance_meters': round(distance_meters, 3),
            'cycles': round(delay_ms / period_ms, 2)
        }
    
    def measure_phase_response(self, subwoofer_config: dict, main_speaker_config: dict,
                              test_frequencies: Optional[List[float]] = None) -> dict:
        """
        Simulate phase meter measurement at crossover region.
        
        Args:
            subwoofer_config: Subwoofer settings with delay and phase
            main_speaker_config: Main speaker settings with delay
            test_frequencies: List of test frequencies (default: crossover region)
            
        Returns:
            Phase response measurements
        """
        if test_frequencies is None:
            test_frequencies = [40, 50, 63, 80, 100, 125, 160, 200]
        
        sub_delay = subwoofer_config.get('delay_ms', 0)
        sub_phase = subwoofer_config.get('phase_degrees', 0)
        main_delay = main_speaker_config.get('delay_ms', 0)
        
        measurements = []
        for freq in test_frequencies:
            sub_phase_total = self._calculate_total_phase(freq, sub_delay, sub_phase)
            main_phase_total = self._calculate_total_phase(freq, main_delay, 0)
            
            phase_difference = (sub_phase_total - main_phase_total) % 360
            if phase_difference > 180:
                phase_difference -= 360
            
            coherence = self._calculate_coherence(phase_difference)
            
            measurements.append({
                'frequency_hz': freq,
                'subwoofer_phase': round(sub_phase_total, 1),
                'main_speaker_phase': round(main_phase_total, 1),
                'phase_difference': round(phase_difference, 1),
                'coherence': round(coherence, 2),
                'status': self._phase_status(phase_difference)
            })
        
        overall_coherence = sum(m['coherence'] for m in measurements) / len(measurements)
        
        return {
            'measurements': measurements,
            'overall_coherence': round(overall_coherence, 2),
            'alignment_quality': self._alignment_quality(overall_coherence),
            'recommendations': self._phase_response_recommendations(measurements)
        }
    
    def optimize_phase_and_delay(self, subwoofer_distance: float, main_speaker_distance: float,
                                unit: str = 'inches', crossover_frequency: float = 80) -> dict:
        """
        Calculate optimal phase and delay settings.
        
        Args:
            subwoofer_distance: Distance to subwoofer
            main_speaker_distance: Distance to main speakers
            unit: 'inches', 'cm', or 'feet'
            crossover_frequency: Crossover frequency in Hz
            
        Returns:
            Optimized settings
        """
        if unit == 'feet':
            subwoofer_distance *= 12
            main_speaker_distance *= 12
            unit = 'inches'
        
        speed = 13.5 if unit == 'inches' else 34.3
        
        sub_delay = subwoofer_distance / speed
        main_delay = main_speaker_distance / speed
        
        delay_difference = sub_delay - main_delay
        
        if delay_difference > 0:
            recommended_delay = delay_difference
            recommended_phase = 0
            action = f"Add {recommended_delay:.2f} ms delay to main speakers"
        elif delay_difference < 0:
            recommended_delay = abs(delay_difference)
            recommended_phase = 0
            action = f"Add {recommended_delay:.2f} ms delay to subwoofer"
        else:
            recommended_delay = 0
            recommended_phase = 0
            action = "Speakers already time-aligned"
        
        phase_check = self.calculate_phase_from_delay(abs(delay_difference), crossover_frequency)
        
        if abs(phase_check['phase_shift_degrees']) > 90:
            recommended_phase = 180
            action += " and invert subwoofer phase (180°)"
        
        return {
            'subwoofer_delay_ms': round(sub_delay, 3),
            'main_speaker_delay_ms': round(main_delay, 3),
            'delay_difference_ms': round(delay_difference, 3),
            'recommended_delay_adjustment_ms': round(recommended_delay, 3),
            'recommended_phase_degrees': recommended_phase,
            'action_required': action,
            'phase_analysis_at_crossover': phase_check,
            'alignment_status': 'good' if abs(delay_difference) < 1 else 'needs_adjustment'
        }
    
    def create_phase_visualization(self, phase_measurements: List[dict]) -> dict:
        """
        Create visualization data for phase response graph.
        
        Args:
            phase_measurements: List of phase measurement dicts
            
        Returns:
            Visualization data for graphing
        """
        frequencies = [m['frequency_hz'] for m in phase_measurements]
        phase_diffs = [m['phase_difference'] for m in phase_measurements]
        coherence = [m['coherence'] for m in phase_measurements]
        
        critical_points = []
        for m in phase_measurements:
            if abs(m['phase_difference']) > 90:
                critical_points.append({
                    'frequency': m['frequency_hz'],
                    'issue': 'Significant phase shift - check alignment'
                })
        
        return {
            'chart_data': {
                'frequencies': frequencies,
                'phase_difference': phase_diffs,
                'coherence': coherence,
                'type': 'phase_response'
            },
            'critical_points': critical_points,
            'x_axis': {'label': 'Frequency (Hz)', 'scale': 'log'},
            'y_axes': [
                {'label': 'Phase Difference (°)', 'range': [-180, 180]},
                {'label': 'Coherence', 'range': [0, 1]}
            ],
            'target_zones': [
                {'range': [-45, 45], 'color': 'green', 'label': 'Excellent'},
                {'range': [-90, 90], 'color': 'yellow', 'label': 'Acceptable'}
            ]
        }
    
    def calculate_group_delay(self, filter_configs: List[dict]) -> dict:
        """
        Calculate group delay from filter configurations.
        
        Args:
            filter_configs: List of filter configs (crossover, subsonic, etc.)
            
        Returns:
            Group delay analysis
        """
        total_group_delay = 0
        
        for filt in filter_configs:
            filter_type = filt.get('type', '')
            frequency = filt.get('frequency_hz', 80)
            slope = filt.get('slope_db_per_octave', 24)
            
            order = slope // 6
            
            delay_at_fc = order / (2 * math.pi * frequency) * 1000
            
            total_group_delay += delay_at_fc
        
        return {
            'total_group_delay_ms': round(total_group_delay, 3),
            'equivalent_distance_inches': round(total_group_delay * 13.5, 2),
            'filter_count': len(filter_configs),
            'recommendation': 'Use delay adjustment to compensate' if total_group_delay > 1 else 'Minimal group delay'
        }
    
    def _phase_to_delay(self, phase_degrees: float, frequency_hz: float) -> float:
        """Convert phase shift to time delay at frequency."""
        period_ms = 1000.0 / frequency_hz
        return (phase_degrees / 360.0) * period_ms
    
    def _calculate_total_phase(self, frequency: float, delay_ms: float, base_phase: float) -> float:
        """Calculate total phase including delay and base phase."""
        period_ms = 1000.0 / frequency
        delay_phase = (delay_ms / period_ms * 360.0) % 360
        total_phase = (base_phase + delay_phase) % 360
        return total_phase
    
    def _calculate_coherence(self, phase_difference: float) -> float:
        """Calculate coherence from phase difference (0-1 scale)."""
        abs_diff = abs(phase_difference)
        coherence = math.cos(math.radians(abs_diff))
        return max(0, coherence)
    
    def _phase_status(self, phase_diff: float) -> str:
        """Determine phase alignment status."""
        abs_diff = abs(phase_diff)
        if abs_diff < 45:
            return 'excellent'
        elif abs_diff < 90:
            return 'good'
        elif abs_diff < 135:
            return 'poor'
        else:
            return 'critical'
    
    def _alignment_quality(self, coherence: float) -> str:
        """Determine overall alignment quality."""
        if coherence > 0.9:
            return 'excellent'
        elif coherence > 0.7:
            return 'good'
        elif coherence > 0.5:
            return 'acceptable'
        else:
            return 'poor'
    
    def _phase_recommendation(self, phase: float) -> str:
        """Generate phase setting recommendation."""
        if phase == 0:
            return 'Normal polarity - start here'
        elif phase == 180:
            return 'Inverted polarity - use if bass sounds thin'
        elif phase < 45:
            return 'Slight phase lead'
        elif phase > 135:
            return 'Approaching polarity inversion'
        else:
            return 'Mid-range phase adjustment'
    
    def _phase_response_recommendations(self, measurements: List[dict]) -> List[str]:
        """Generate recommendations from phase measurements."""
        recs = []
        
        poor_coherence = [m for m in measurements if m['coherence'] < 0.7]
        if poor_coherence:
            freqs = [m['frequency_hz'] for m in poor_coherence]
            recs.append(f"Poor coherence at {freqs} Hz - adjust delay or phase")
        
        large_shifts = [m for m in measurements if abs(m['phase_difference']) > 90]
        if large_shifts:
            recs.append("Large phase shifts detected - try inverting subwoofer phase (180°)")
        
        if not recs:
            recs.append("Phase alignment is excellent")
        
        return recs
