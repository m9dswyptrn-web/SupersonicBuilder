#!/usr/bin/env python3
"""
31-Band Parametric Equalizer Engine
Professional-grade EQ with per-channel control for car audio DSP
"""

import math
from typing import Dict, List, Tuple


class ParametricEqualizer:
    """31-band parametric equalizer with per-channel control."""
    
    def __init__(self):
        """Initialize 31-band parametric EQ."""
        self.bands_31 = [
            20, 25, 31, 40, 50, 63, 80, 100, 125, 160,
            200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600,
            2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000
        ]
        
        self.channels = {
            'front_left': 'Front Left',
            'front_right': 'Front Right',
            'rear_left': 'Rear Left',
            'rear_right': 'Rear Right',
            'subwoofer': 'Subwoofer',
            'center': 'Center (optional)'
        }
        
        self.default_q = 1.41
        
    def create_band(
        self,
        frequency: float,
        gain_db: float,
        q_factor: float = None,
        channel: str = 'all'
    ) -> Dict:
        """Create parametric EQ band with specified parameters."""
        if q_factor is None:
            q_factor = self.default_q
            
        gain_db = max(-12.0, min(12.0, gain_db))
        q_factor = max(0.1, min(10.0, q_factor))
        
        bandwidth_hz = frequency / q_factor
        
        return {
            'frequency': frequency,
            'gain_db': gain_db,
            'q_factor': q_factor,
            'bandwidth_hz': round(bandwidth_hz, 2),
            'channel': channel,
            'filter_type': 'peaking'
        }
    
    def calculate_filter_coefficients(
        self,
        frequency: float,
        gain_db: float,
        q_factor: float,
        sample_rate: int = 48000
    ) -> Dict:
        """Calculate biquad filter coefficients for parametric EQ."""
        A = math.pow(10, gain_db / 40.0)
        omega = 2.0 * math.pi * frequency / sample_rate
        sin_omega = math.sin(omega)
        cos_omega = math.cos(omega)
        alpha = sin_omega / (2.0 * q_factor)
        
        b0 = 1.0 + alpha * A
        b1 = -2.0 * cos_omega
        b2 = 1.0 - alpha * A
        a0 = 1.0 + alpha / A
        a1 = -2.0 * cos_omega
        a2 = 1.0 - alpha / A
        
        return {
            'b0': b0 / a0,
            'b1': b1 / a0,
            'b2': b2 / a0,
            'a1': a1 / a0,
            'a2': a2 / a0,
            'frequency': frequency,
            'gain_db': gain_db,
            'q_factor': q_factor
        }
    
    def create_31_band_eq(
        self,
        gains: Dict[int, float] = None,
        q_factor: float = None,
        channel: str = 'all'
    ) -> List[Dict]:
        """Create complete 31-band EQ curve."""
        if gains is None:
            gains = {freq: 0.0 for freq in self.bands_31}
        
        if q_factor is None:
            q_factor = self.default_q
            
        eq_curve = []
        for freq in self.bands_31:
            gain = gains.get(freq, 0.0)
            band = self.create_band(freq, gain, q_factor, channel)
            eq_curve.append(band)
            
        return eq_curve
    
    def create_per_channel_eq(
        self,
        channel_gains: Dict[str, Dict[int, float]]
    ) -> Dict[str, List[Dict]]:
        """Create separate EQ curves for each channel."""
        per_channel_eq = {}
        
        for channel, gains in channel_gains.items():
            if channel in self.channels:
                per_channel_eq[channel] = self.create_31_band_eq(
                    gains=gains,
                    channel=channel
                )
                
        return per_channel_eq
    
    def calculate_frequency_response(
        self,
        eq_curve: List[Dict],
        sample_rate: int = 48000,
        num_points: int = 1000
    ) -> List[Dict]:
        """Calculate frequency response curve from EQ settings."""
        min_freq = 20.0
        max_freq = 20000.0
        
        frequencies = [
            min_freq * math.pow(max_freq / min_freq, i / (num_points - 1))
            for i in range(num_points)
        ]
        
        response = []
        for freq in frequencies:
            total_gain = 0.0
            
            for band in eq_curve:
                band_freq = band['frequency']
                band_gain = band['gain_db']
                band_q = band['q_factor']
                
                omega = 2.0 * math.pi * freq / sample_rate
                omega_0 = 2.0 * math.pi * band_freq / sample_rate
                
                delta_omega = omega - omega_0
                bandwidth = omega_0 / band_q
                
                if abs(delta_omega) < bandwidth:
                    factor = 1.0 - abs(delta_omega) / bandwidth
                    total_gain += band_gain * factor
                    
            response.append({
                'frequency': round(freq, 2),
                'gain_db': round(total_gain, 3)
            })
            
        return response
    
    def validate_eq_settings(
        self,
        eq_curve: List[Dict]
    ) -> Tuple[bool, List[str]]:
        """Validate EQ settings for safety and quality."""
        errors = []
        warnings = []
        
        for band in eq_curve:
            if band['gain_db'] < -12.0 or band['gain_db'] > 12.0:
                errors.append(
                    f"Band {band['frequency']}Hz: Gain {band['gain_db']}dB "
                    f"out of range (-12 to +12 dB)"
                )
                
            if band['q_factor'] < 0.1 or band['q_factor'] > 10.0:
                errors.append(
                    f"Band {band['frequency']}Hz: Q factor {band['q_factor']} "
                    f"out of range (0.1 to 10.0)"
                )
                
            if band['gain_db'] > 6.0:
                warnings.append(
                    f"Band {band['frequency']}Hz: High gain ({band['gain_db']}dB) "
                    f"may cause clipping"
                )
                
        max_total_gain = sum(b['gain_db'] for b in eq_curve if b['gain_db'] > 0)
        if max_total_gain > 18.0:
            warnings.append(
                f"Total positive gain ({max_total_gain:.1f}dB) is very high. "
                f"Reduce output level to prevent clipping."
            )
            
        return len(errors) == 0, errors + warnings
    
    def recommend_headroom(
        self,
        eq_curve: List[Dict]
    ) -> Dict:
        """Calculate recommended headroom to prevent clipping."""
        max_gain = max(b['gain_db'] for b in eq_curve)
        total_positive_gain = sum(b['gain_db'] for b in eq_curve if b['gain_db'] > 0)
        
        recommended_reduction_db = max(0, max_gain + 3.0)
        
        return {
            'max_gain_db': round(max_gain, 2),
            'total_positive_gain_db': round(total_positive_gain, 2),
            'recommended_headroom_db': round(recommended_reduction_db, 2),
            'reduce_master_volume_db': round(max(0, max_gain), 2),
            'clipping_risk': 'high' if max_gain > 6.0 else 'medium' if max_gain > 3.0 else 'low'
        }
    
    def export_to_android(
        self,
        eq_curve: List[Dict],
        channel: str = 'all'
    ) -> Dict:
        """Export EQ settings for EOENKK Android head unit."""
        android_eq = {
            'version': '2.0',
            'dsp_type': 'parametric_31_band',
            'channel': channel,
            'sample_rate': 48000,
            'bands': []
        }
        
        for i, band in enumerate(eq_curve):
            android_eq['bands'].append({
                'band_index': i,
                'frequency_hz': band['frequency'],
                'gain_millibels': int(band['gain_db'] * 100),
                'q_factor': band['q_factor'],
                'bandwidth_hz': band['bandwidth_hz'],
                'filter_type': 'peaking'
            })
            
        return android_eq
    
    def import_from_android(
        self,
        android_config: Dict
    ) -> List[Dict]:
        """Import EQ settings from Android configuration."""
        eq_curve = []
        
        for band in android_config.get('bands', []):
            freq = band.get('frequency_hz', 1000)
            gain_db = band.get('gain_millibels', 0) / 100.0
            q_factor = band.get('q_factor', self.default_q)
            
            eq_curve.append(self.create_band(freq, gain_db, q_factor))
            
        return eq_curve
    
    def apply_sonic_cabin_correction(
        self,
        eq_curve: List[Dict]
    ) -> List[Dict]:
        """Apply Chevy Sonic cabin acoustic correction to EQ."""
        sonic_correction = {
            20: 2.5,
            25: 2.0,
            31: 1.5,
            40: 1.0,
            50: 0.5,
            63: 0.0,
            80: -0.5,
            100: -0.5,
            125: 0.0,
            160: 0.0,
            200: 0.5,
            250: 0.5,
            315: 0.0,
            400: 0.0,
            500: 0.0,
            630: 0.5,
            800: 1.0,
            1000: 1.0,
            1250: 0.5,
            1600: 0.0,
            2000: 0.5,
            2500: 1.0,
            3150: 1.5,
            4000: 2.0,
            5000: 2.5,
            6300: 2.5,
            8000: 2.0,
            10000: 1.5,
            12500: 1.0,
            16000: 0.5,
            20000: 0.0
        }
        
        corrected = []
        for band in eq_curve:
            freq = band['frequency']
            correction = sonic_correction.get(freq, 0.0)
            new_gain = band['gain_db'] + correction
            new_gain = max(-12.0, min(12.0, new_gain))
            
            corrected_band = band.copy()
            corrected_band['gain_db'] = new_gain
            corrected_band['original_gain_db'] = band['gain_db']
            corrected_band['cabin_correction_db'] = correction
            corrected.append(corrected_band)
            
        return corrected
    
    def get_band_info(self) -> List[Dict]:
        """Get information about all 31 EQ bands."""
        band_info = []
        
        for freq in self.bands_31:
            if freq < 200:
                region = 'Sub-bass'
            elif freq < 500:
                region = 'Bass'
            elif freq < 2000:
                region = 'Low-mid'
            elif freq < 4000:
                region = 'Mid'
            elif freq < 8000:
                region = 'High-mid'
            else:
                region = 'Treble'
                
            band_info.append({
                'frequency': freq,
                'frequency_label': f"{freq}Hz",
                'region': region,
                'bandwidth_default_hz': freq / self.default_q
            })
            
        return band_info
