#!/usr/bin/env python3
"""
FFT Analysis Engine
Real-time frequency analysis for audio visualization
"""

import numpy as np
from typing import List, Tuple, Dict
import math


class FFTAnalyzer:
    """Real-time FFT analysis for audio visualization."""
    
    def __init__(self, sample_rate: int = 48000):
        """Initialize FFT analyzer."""
        self.sample_rate = sample_rate
        self.fft_size = 2048
        self.window = self._create_hann_window(self.fft_size)
        
        self.bands_31 = self._create_31_band_centers()
        self.bands_64 = self._create_64_band_centers()
    
    def _create_hann_window(self, size: int) -> np.ndarray:
        """Create Hann window for FFT."""
        return np.hanning(size)
    
    def _create_31_band_centers(self) -> List[float]:
        """Create 31-band 1/3 octave spectrum analyzer frequencies."""
        return [
            20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160,
            200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600,
            2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000
        ]
    
    def _create_64_band_centers(self) -> List[float]:
        """Create 64-band spectrum analyzer frequencies."""
        min_freq = 20
        max_freq = 20000
        return [min_freq * (max_freq / min_freq) ** (i / 63) for i in range(64)]
    
    def analyze_audio(self, audio_data: np.ndarray, num_bands: int = 31) -> Dict:
        """
        Perform FFT analysis on audio data.
        
        Args:
            audio_data: Audio samples (mono or stereo)
            num_bands: Number of frequency bands (31 or 64)
        
        Returns:
            Dictionary with band levels and frequency data
        """
        if len(audio_data.shape) == 2:
            audio_mono = np.mean(audio_data, axis=1)
        else:
            audio_mono = audio_data
        
        if len(audio_mono) < self.fft_size:
            audio_mono = np.pad(audio_mono, (0, self.fft_size - len(audio_mono)))
        else:
            audio_mono = audio_mono[:self.fft_size]
        
        windowed = audio_mono * self.window
        
        fft_result = np.fft.rfft(windowed)
        magnitude = np.abs(fft_result)
        
        magnitude_db = 20 * np.log10(magnitude + 1e-10)
        
        band_centers = self.bands_31 if num_bands == 31 else self.bands_64
        band_levels = self._calculate_band_levels(magnitude_db, band_centers)
        
        normalized_levels = self._normalize_levels(band_levels)
        
        return {
            'band_levels': normalized_levels,
            'band_centers': band_centers,
            'num_bands': num_bands,
            'raw_magnitude': magnitude_db.tolist(),
            'peak_frequency': self._find_peak_frequency(magnitude, band_centers),
            'bass_level': np.mean(normalized_levels[:int(num_bands * 0.2)]),
            'mid_level': np.mean(normalized_levels[int(num_bands * 0.2):int(num_bands * 0.6)]),
            'treble_level': np.mean(normalized_levels[int(num_bands * 0.6):])
        }
    
    def _calculate_band_levels(self, magnitude_db: np.ndarray, band_centers: List[float]) -> List[float]:
        """Calculate levels for each frequency band."""
        freq_resolution = self.sample_rate / self.fft_size
        band_levels = []
        
        for center_freq in band_centers:
            lower = center_freq / (2 ** (1/6))
            upper = center_freq * (2 ** (1/6))
            
            lower_bin = int(lower / freq_resolution)
            upper_bin = int(upper / freq_resolution)
            
            lower_bin = max(0, min(lower_bin, len(magnitude_db) - 1))
            upper_bin = max(0, min(upper_bin, len(magnitude_db) - 1))
            
            if lower_bin == upper_bin:
                band_level = magnitude_db[lower_bin]
            else:
                band_level = np.mean(magnitude_db[lower_bin:upper_bin + 1])
            
            band_levels.append(float(band_level))
        
        return band_levels
    
    def _normalize_levels(self, levels: List[float]) -> List[float]:
        """Normalize levels to 0-1 range."""
        min_db = -80
        max_db = 0
        
        normalized = []
        for level in levels:
            clamped = max(min_db, min(max_db, level))
            normalized_value = (clamped - min_db) / (max_db - min_db)
            normalized.append(normalized_value)
        
        return normalized
    
    def _find_peak_frequency(self, magnitude: np.ndarray, band_centers: List[float]) -> float:
        """Find the peak frequency in the spectrum."""
        peak_idx = np.argmax(magnitude)
        freq_resolution = self.sample_rate / self.fft_size
        peak_freq = peak_idx * freq_resolution
        return float(peak_freq)
    
    def generate_test_signal(self, duration: float = 1.0, frequencies: List[float] = None) -> np.ndarray:
        """Generate test audio signal with specified frequencies."""
        if frequencies is None:
            frequencies = [440.0, 880.0, 1760.0]
        
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)
        
        signal = np.zeros(num_samples)
        for freq in frequencies:
            signal += np.sin(2 * np.pi * freq * t) / len(frequencies)
        
        return signal * 0.5
    
    def generate_white_noise(self, duration: float = 1.0) -> np.ndarray:
        """Generate white noise test signal."""
        num_samples = int(duration * self.sample_rate)
        return np.random.normal(0, 0.1, num_samples)
    
    def generate_pink_noise(self, duration: float = 1.0) -> np.ndarray:
        """Generate pink noise (1/f) test signal."""
        num_samples = int(duration * self.sample_rate)
        white = np.random.randn(num_samples)
        
        fft_white = np.fft.rfft(white)
        freqs = np.fft.rfftfreq(num_samples, 1/self.sample_rate)
        
        freqs[0] = 1
        pink_filter = 1 / np.sqrt(freqs)
        
        fft_pink = fft_white * pink_filter
        pink = np.fft.irfft(fft_pink, n=num_samples)
        
        pink = pink / np.max(np.abs(pink)) * 0.1
        
        return pink
    
    def generate_sweep(self, duration: float = 2.0, start_freq: float = 20.0, 
                       end_freq: float = 20000.0) -> np.ndarray:
        """Generate logarithmic frequency sweep."""
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)
        
        k = (end_freq / start_freq) ** (1 / duration)
        instantaneous_freq = start_freq * (k ** t)
        
        phase = 2 * np.pi * start_freq * duration / np.log(k) * (k ** t - 1)
        sweep = np.sin(phase)
        
        return sweep * 0.5
