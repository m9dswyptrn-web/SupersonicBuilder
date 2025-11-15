#!/usr/bin/env python3
"""
Test Tone Generator Module
Generate bass test signals for calibration and measurement
"""

import math
import random
from typing import Dict, List, Optional


class TestToneGenerator:
    """Generate various test tones for bass calibration."""
    
    def __init__(self):
        """Initialize test tone generator."""
        self.sample_rate = 48000
        self.bit_depth = 24
        
    def generate_sine_wave(self, frequency_hz: float, duration_seconds: float = 10.0,
                          amplitude_db: float = -20.0) -> dict:
        """
        Generate sine wave test tone.
        
        Args:
            frequency_hz: Frequency (20-200 Hz for bass)
            duration_seconds: Duration in seconds
            amplitude_db: Amplitude in dB (0 = full scale)
            
        Returns:
            Sine wave configuration
        """
        if not 20 <= frequency_hz <= 200:
            raise ValueError("Frequency must be between 20 and 200 Hz for bass testing")
        
        if not 0.1 <= duration_seconds <= 60:
            raise ValueError("Duration must be between 0.1 and 60 seconds")
        
        if not -60 <= amplitude_db <= 0:
            raise ValueError("Amplitude must be between -60 and 0 dB")
        
        num_samples = int(duration_seconds * self.sample_rate)
        amplitude_linear = 10 ** (amplitude_db / 20.0)
        
        wavelength_samples = self.sample_rate / frequency_hz
        num_cycles = duration_seconds * frequency_hz
        
        return {
            'type': 'sine_wave',
            'frequency_hz': round(frequency_hz, 1),
            'duration_seconds': duration_seconds,
            'amplitude_db': amplitude_db,
            'amplitude_linear': round(amplitude_linear, 4),
            'sample_rate': self.sample_rate,
            'bit_depth': self.bit_depth,
            'num_samples': num_samples,
            'num_cycles': round(num_cycles, 1),
            'wavelength_samples': round(wavelength_samples, 1),
            'use_case': self._sine_use_case(frequency_hz)
        }
    
    def generate_sweep_tone(self, start_hz: float = 20, end_hz: float = 200,
                           duration_seconds: float = 30.0, sweep_type: str = 'logarithmic',
                           amplitude_db: float = -20.0) -> dict:
        """
        Generate frequency sweep for response measurement.
        
        Args:
            start_hz: Start frequency
            end_hz: End frequency
            duration_seconds: Sweep duration
            sweep_type: 'logarithmic' or 'linear'
            amplitude_db: Amplitude in dB
            
        Returns:
            Sweep tone configuration
        """
        if not 10 <= start_hz < end_hz <= 500:
            raise ValueError("Invalid frequency range")
        
        if sweep_type not in ['logarithmic', 'linear']:
            raise ValueError("Sweep type must be 'logarithmic' or 'linear'")
        
        num_samples = int(duration_seconds * self.sample_rate)
        amplitude_linear = 10 ** (amplitude_db / 20.0)
        
        frequency_span_octaves = math.log2(end_hz / start_hz)
        
        return {
            'type': f'{sweep_type}_sweep',
            'start_frequency_hz': start_hz,
            'end_frequency_hz': end_hz,
            'duration_seconds': duration_seconds,
            'sweep_type': sweep_type,
            'amplitude_db': amplitude_db,
            'amplitude_linear': round(amplitude_linear, 4),
            'sample_rate': self.sample_rate,
            'num_samples': num_samples,
            'frequency_span_octaves': round(frequency_span_octaves, 2),
            'sweep_rate_hz_per_second': round((end_hz - start_hz) / duration_seconds, 2),
            'use_case': 'Measure frequency response and find room modes'
        }
    
    def generate_pink_noise(self, duration_seconds: float = 30.0, amplitude_db: float = -20.0,
                           bass_weighted: bool = True, lowpass_hz: Optional[float] = 200) -> dict:
        """
        Generate pink noise test signal.
        
        Args:
            duration_seconds: Duration in seconds
            amplitude_db: Amplitude in dB
            bass_weighted: Apply bass weighting
            lowpass_hz: Optional low-pass filter frequency
            
        Returns:
            Pink noise configuration
        """
        if not 1 <= duration_seconds <= 300:
            raise ValueError("Duration must be between 1 and 300 seconds")
        
        num_samples = int(duration_seconds * self.sample_rate)
        amplitude_linear = 10 ** (amplitude_db / 20.0)
        
        if bass_weighted:
            noise_type = 'bass_weighted_pink_noise'
            description = 'Pink noise with emphasis on bass frequencies'
        else:
            noise_type = 'pink_noise'
            description = 'Pink noise (-3 dB/octave spectral slope)'
        
        return {
            'type': noise_type,
            'duration_seconds': duration_seconds,
            'amplitude_db': amplitude_db,
            'amplitude_linear': round(amplitude_linear, 4),
            'sample_rate': self.sample_rate,
            'num_samples': num_samples,
            'bass_weighted': bass_weighted,
            'lowpass_filter_hz': lowpass_hz,
            'description': description,
            'use_case': 'General system testing and SPL measurement'
        }
    
    def generate_burst_tone(self, frequency_hz: float = 40, burst_duration_ms: float = 100,
                           silence_duration_ms: float = 400, num_bursts: int = 10,
                           amplitude_db: float = -10.0) -> dict:
        """
        Generate tone burst for transient response testing.
        
        Args:
            frequency_hz: Burst frequency
            burst_duration_ms: Duration of each burst
            silence_duration_ms: Silence between bursts
            num_bursts: Number of bursts
            amplitude_db: Amplitude in dB
            
        Returns:
            Burst tone configuration
        """
        if not 20 <= frequency_hz <= 200:
            raise ValueError("Frequency must be between 20 and 200 Hz")
        
        burst_samples = int(burst_duration_ms / 1000 * self.sample_rate)
        silence_samples = int(silence_duration_ms / 1000 * self.sample_rate)
        
        total_samples = (burst_samples + silence_samples) * num_bursts
        total_duration = total_samples / self.sample_rate
        
        amplitude_linear = 10 ** (amplitude_db / 20.0)
        
        return {
            'type': 'burst_tone',
            'frequency_hz': frequency_hz,
            'burst_duration_ms': burst_duration_ms,
            'silence_duration_ms': silence_duration_ms,
            'num_bursts': num_bursts,
            'amplitude_db': amplitude_db,
            'amplitude_linear': round(amplitude_linear, 4),
            'total_duration_seconds': round(total_duration, 2),
            'burst_samples': burst_samples,
            'silence_samples': silence_samples,
            'use_case': 'Test transient response and port resonance'
        }
    
    def generate_multitone(self, frequencies: List[float], duration_seconds: float = 10.0,
                          amplitude_db_each: float = -26.0) -> dict:
        """
        Generate multi-frequency test signal.
        
        Args:
            frequencies: List of frequencies to combine
            duration_seconds: Duration
            amplitude_db_each: Amplitude per tone (will be summed)
            
        Returns:
            Multitone configuration
        """
        if not frequencies:
            raise ValueError("Must specify at least one frequency")
        
        if len(frequencies) > 10:
            raise ValueError("Maximum 10 simultaneous frequencies")
        
        for freq in frequencies:
            if not 20 <= freq <= 200:
                raise ValueError(f"All frequencies must be between 20 and 200 Hz")
        
        amplitude_per_tone = 10 ** (amplitude_db_each / 20.0)
        combined_amplitude = amplitude_per_tone * math.sqrt(len(frequencies))
        combined_amplitude_db = 20 * math.log10(combined_amplitude)
        
        num_samples = int(duration_seconds * self.sample_rate)
        
        return {
            'type': 'multitone',
            'frequencies_hz': sorted(frequencies),
            'num_tones': len(frequencies),
            'duration_seconds': duration_seconds,
            'amplitude_db_per_tone': amplitude_db_each,
            'combined_amplitude_db': round(combined_amplitude_db, 2),
            'sample_rate': self.sample_rate,
            'num_samples': num_samples,
            'use_case': 'Test intermodulation distortion and linearity'
        }
    
    def create_calibration_sequence(self) -> dict:
        """
        Create complete calibration test sequence.
        
        Returns:
            Sequence of calibration tones
        """
        sequence = [
            {
                'step': 1,
                'name': 'Subsonic Test',
                'tone': self.generate_sine_wave(20, 5.0, -20),
                'instructions': 'Listen for port chuffing or distortion. If present, raise subsonic filter.'
            },
            {
                'step': 2,
                'name': 'Deep Bass',
                'tone': self.generate_sine_wave(30, 5.0, -20),
                'instructions': 'Check for clean reproduction. Adjust subwoofer level.'
            },
            {
                'step': 3,
                'name': 'Mid Bass',
                'tone': self.generate_sine_wave(50, 5.0, -20),
                'instructions': 'Verify smooth transition from subwoofer to mains.'
            },
            {
                'step': 4,
                'name': 'Crossover Frequency',
                'tone': self.generate_sine_wave(80, 5.0, -20),
                'instructions': 'Check phase alignment. Try inverting subwoofer phase.'
            },
            {
                'step': 5,
                'name': 'Upper Bass',
                'tone': self.generate_sine_wave(100, 5.0, -20),
                'instructions': 'Ensure main speakers are handling this frequency cleanly.'
            },
            {
                'step': 6,
                'name': 'Frequency Sweep',
                'tone': self.generate_sweep_tone(20, 200, 30.0, 'logarithmic', -20),
                'instructions': 'Listen for resonances, nulls, and smooth response.'
            },
            {
                'step': 7,
                'name': 'Pink Noise',
                'tone': self.generate_pink_noise(30.0, -20, True, 200),
                'instructions': 'Use SPL meter to verify level and consistency.'
            }
        ]
        
        total_duration = sum(s['tone']['duration_seconds'] for s in sequence)
        
        return {
            'sequence': sequence,
            'total_steps': len(sequence),
            'total_duration_seconds': round(total_duration, 1),
            'estimated_time_minutes': round(total_duration / 60 + 2, 1)
        }
    
    def create_spl_test_tones(self) -> dict:
        """
        Create tones for SPL (Sound Pressure Level) measurement.
        
        Returns:
            SPL test tone configurations
        """
        test_frequencies = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200]
        
        tones = []
        for freq in test_frequencies:
            tone = self.generate_sine_wave(freq, 10.0, -20)
            tones.append({
                'frequency_hz': freq,
                'tone_config': tone,
                'measurement_instructions': f'Measure SPL at {freq} Hz. Target: 75 dB C-weighted at listening position.'
            })
        
        return {
            'test_tones': tones,
            'measurement_standard': 'C-weighted, slow response',
            'target_level_db': 75,
            'microphone_position': 'Primary listening position at ear height',
            'notes': 'Use calibrated SPL meter. Adjust subwoofer level for flat response.'
        }
    
    def simulate_spl_measurement(self, frequency_hz: float, subwoofer_level: float = 75.0,
                                room_acoustics: str = 'average') -> dict:
        """
        Simulate SPL measurement results.
        
        Args:
            frequency_hz: Test frequency
            subwoofer_level: Base level setting
            room_acoustics: 'dead', 'average', or 'live'
            
        Returns:
            Simulated measurement
        """
        room_gain = {'dead': 0, 'average': 3, 'live': 6}
        base_gain = room_gain.get(room_acoustics, 3)
        
        if frequency_hz < 40:
            modal_variation = random.uniform(-6, 3)
        elif frequency_hz < 80:
            modal_variation = random.uniform(-4, 4)
        else:
            modal_variation = random.uniform(-2, 2)
        
        measured_spl = subwoofer_level + base_gain + modal_variation
        
        return {
            'frequency_hz': frequency_hz,
            'measured_spl_db': round(measured_spl, 1),
            'room_gain_db': base_gain,
            'modal_variation_db': round(modal_variation, 1),
            'room_acoustics': room_acoustics,
            'status': self._spl_status(measured_spl, frequency_hz)
        }
    
    def _sine_use_case(self, frequency: float) -> str:
        """Determine use case for sine wave frequency."""
        if frequency < 30:
            return 'Test subwoofer extension and port tuning'
        elif frequency < 60:
            return 'Test deep bass response and room modes'
        elif frequency < 100:
            return 'Test crossover region and phase alignment'
        else:
            return 'Test upper bass and main speaker integration'
    
    def _spl_status(self, measured_spl: float, frequency: float) -> str:
        """Determine SPL measurement status."""
        if 73 <= measured_spl <= 77:
            return 'Excellent - within target range'
        elif 70 <= measured_spl <= 80:
            return 'Good - close to target'
        elif measured_spl < 70:
            return f'Too quiet - increase subwoofer level or check phase at {frequency} Hz'
        else:
            return f'Too loud - reduce subwoofer level or check for room mode at {frequency} Hz'
