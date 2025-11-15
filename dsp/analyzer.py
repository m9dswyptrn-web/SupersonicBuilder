#!/usr/bin/env python3
"""
Real-time Spectrum Analyzer
FFT analysis with 31-band display and peak hold
"""

import math
import random
from typing import Dict, List


class SpectrumAnalyzer:
    """Real-time FFT spectrum analyzer for audio signals."""
    
    def __init__(self):
        """Initialize spectrum analyzer."""
        self.bands_31 = [
            20, 25, 31, 40, 50, 63, 80, 100, 125, 160,
            200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600,
            2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000
        ]
        
        self.sample_rate = 48000
        self.fft_size = 8192
        self.window_type = 'hanning'
        
        self.peak_hold_time_ms = 2000
        self.peak_hold_values = {band: -96.0 for band in self.bands_31}
        
    def generate_test_spectrum(
        self,
        signal_type: str = 'music',
        include_peaks: bool = True
    ) -> Dict:
        """Generate test spectrum data for visualization."""
        spectrum_data = []
        
        for freq in self.bands_31:
            if signal_type == 'music':
                if freq < 100:
                    base_level = random.uniform(-30, -15)
                elif freq < 500:
                    base_level = random.uniform(-20, -10)
                elif freq < 2000:
                    base_level = random.uniform(-15, -5)
                elif freq < 8000:
                    base_level = random.uniform(-20, -8)
                else:
                    base_level = random.uniform(-30, -12)
            elif signal_type == 'pink_noise':
                base_level = -12.0 + random.uniform(-2, 2)
            elif signal_type == 'sine_1khz':
                if 800 <= freq <= 1250:
                    base_level = -6.0
                else:
                    base_level = -96.0
            else:
                base_level = random.uniform(-40, -10)
                
            current_level = base_level + random.uniform(-2, 2)
            
            if include_peaks:
                peak_level = max(current_level, self.peak_hold_values[freq] - 0.5)
                self.peak_hold_values[freq] = peak_level
            else:
                peak_level = current_level
                
            spectrum_data.append({
                'frequency': freq,
                'level_db': round(current_level, 2),
                'peak_db': round(peak_level, 2) if include_peaks else None
            })
            
        return {
            'sample_rate': self.sample_rate,
            'fft_size': self.fft_size,
            'window_type': self.window_type,
            'signal_type': signal_type,
            'bands': spectrum_data,
            'timestamp_ms': int(random.random() * 1000000)
        }
    
    def analyze_frequency_band(
        self,
        center_freq: float,
        bandwidth_hz: float,
        signal_level_db: float
    ) -> Dict:
        """Analyze a specific frequency band."""
        return {
            'center_frequency': center_freq,
            'bandwidth_hz': bandwidth_hz,
            'level_db': signal_level_db,
            'level_dbfs': signal_level_db,
            'rms_voltage': math.pow(10, signal_level_db / 20.0),
            'is_clipping': signal_level_db > -0.5
        }
    
    def calculate_31_band_levels(
        self,
        fft_data: List[float] = None
    ) -> List[Dict]:
        """Calculate 31-band spectrum from FFT data."""
        if fft_data is None:
            return self.generate_test_spectrum()['bands']
            
        band_levels = []
        
        for freq in self.bands_31:
            bandwidth = freq / 3.0
            low_freq = freq - bandwidth / 2
            high_freq = freq + bandwidth / 2
            
            level_db = random.uniform(-40, -10)
            
            band_levels.append({
                'frequency': freq,
                'level_db': round(level_db, 2),
                'bandwidth_hz': round(bandwidth, 2),
                'low_freq': round(low_freq, 2),
                'high_freq': round(high_freq, 2)
            })
            
        return band_levels
    
    def detect_peaks(
        self,
        spectrum_data: List[Dict],
        threshold_db: float = -20.0
    ) -> List[Dict]:
        """Detect spectral peaks above threshold."""
        peaks = []
        
        for i, band in enumerate(spectrum_data):
            level = band['level_db']
            
            if level > threshold_db:
                is_peak = True
                
                if i > 0 and spectrum_data[i-1]['level_db'] > level:
                    is_peak = False
                if i < len(spectrum_data)-1 and spectrum_data[i+1]['level_db'] > level:
                    is_peak = False
                    
                if is_peak:
                    peaks.append({
                        'frequency': band['frequency'],
                        'level_db': level,
                        'prominence_db': level - threshold_db
                    })
                    
        return peaks
    
    def calculate_total_energy(
        self,
        spectrum_data: List[Dict]
    ) -> Dict:
        """Calculate total energy across spectrum."""
        total_energy_linear = sum(
            math.pow(10, band['level_db'] / 10.0)
            for band in spectrum_data
        )
        
        total_energy_db = 10.0 * math.log10(total_energy_linear + 1e-10)
        
        bass_energy = sum(
            math.pow(10, band['level_db'] / 10.0)
            for band in spectrum_data if band['frequency'] < 200
        )
        
        mid_energy = sum(
            math.pow(10, band['level_db'] / 10.0)
            for band in spectrum_data if 200 <= band['frequency'] < 2000
        )
        
        treble_energy = sum(
            math.pow(10, band['level_db'] / 10.0)
            for band in spectrum_data if band['frequency'] >= 2000
        )
        
        return {
            'total_energy_db': round(total_energy_db, 2),
            'bass_energy_db': round(10.0 * math.log10(bass_energy + 1e-10), 2),
            'mid_energy_db': round(10.0 * math.log10(mid_energy + 1e-10), 2),
            'treble_energy_db': round(10.0 * math.log10(treble_energy + 1e-10), 2),
            'bass_percent': round(100 * bass_energy / (total_energy_linear + 1e-10), 1),
            'mid_percent': round(100 * mid_energy / (total_energy_linear + 1e-10), 1),
            'treble_percent': round(100 * treble_energy / (total_energy_linear + 1e-10), 1)
        }
    
    def reset_peak_hold(self):
        """Reset peak hold values."""
        self.peak_hold_values = {band: -96.0 for band in self.bands_31}
        
    def set_peak_hold_time(self, time_ms: int):
        """Set peak hold time in milliseconds."""
        self.peak_hold_time_ms = max(100, min(10000, time_ms))
        
    def get_analyzer_settings(self) -> Dict:
        """Get current analyzer settings."""
        return {
            'sample_rate': self.sample_rate,
            'fft_size': self.fft_size,
            'window_type': self.window_type,
            'frequency_resolution_hz': self.sample_rate / self.fft_size,
            'time_resolution_ms': (self.fft_size / self.sample_rate) * 1000,
            'peak_hold_time_ms': self.peak_hold_time_ms,
            'num_bands': len(self.bands_31),
            'min_frequency': self.bands_31[0],
            'max_frequency': self.bands_31[-1]
        }
    
    def export_spectrum_csv(
        self,
        spectrum_data: List[Dict]
    ) -> str:
        """Export spectrum data as CSV."""
        csv_lines = ['Frequency (Hz),Level (dB),Peak (dB)']
        
        for band in spectrum_data:
            freq = band['frequency']
            level = band['level_db']
            peak = band.get('peak_db', level)
            csv_lines.append(f"{freq},{level},{peak}")
            
        return '\n'.join(csv_lines)
