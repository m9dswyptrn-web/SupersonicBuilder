#!/usr/bin/env python3
"""
Beat Detection Engine
Real-time beat detection and BPM analysis
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import deque
import time


class BeatDetector:
    """Real-time beat detection and rhythm analysis."""
    
    def __init__(self, sample_rate: int = 48000):
        """Initialize beat detector."""
        self.sample_rate = sample_rate
        self.hop_size = 512
        
        self.beat_history = deque(maxlen=100)
        self.energy_history = deque(maxlen=43)
        
        self.last_beat_time = 0
        self.current_bpm = 120.0
        self.beat_confidence = 0.0
        
        self.kick_threshold = 0.7
        self.snare_threshold = 0.6
        self.hihat_threshold = 0.4
    
    def detect_beat(self, audio_data: np.ndarray, bass_level: float, 
                    mid_level: float, treble_level: float) -> Dict:
        """
        Detect beats in audio data.
        
        Args:
            audio_data: Audio samples
            bass_level: Bass frequency energy (0-1)
            mid_level: Mid frequency energy (0-1)
            treble_level: Treble frequency energy (0-1)
        
        Returns:
            Dictionary with beat detection results
        """
        energy = self._calculate_energy(audio_data)
        
        self.energy_history.append(energy)
        
        beat_detected, beat_strength = self._detect_onset(energy)
        
        kick_detected = bass_level > self.kick_threshold and beat_detected
        snare_detected = mid_level > self.snare_threshold and beat_detected
        hihat_detected = treble_level > self.hihat_threshold
        
        current_time = time.time()
        
        if beat_detected:
            if self.last_beat_time > 0:
                interval = current_time - self.last_beat_time
                instant_bpm = 60.0 / interval if interval > 0 else 120.0
                
                if 40 <= instant_bpm <= 200:
                    self.current_bpm = self.current_bpm * 0.9 + instant_bpm * 0.1
            
            self.beat_history.append(current_time)
            self.last_beat_time = current_time
        
        bpm_confidence = self._calculate_bpm_confidence()
        
        rhythm_pattern = self._analyze_rhythm_pattern()
        
        return {
            'beat_detected': beat_detected,
            'beat_strength': beat_strength,
            'bpm': round(self.current_bpm, 1),
            'bpm_confidence': bpm_confidence,
            'kick_detected': kick_detected,
            'snare_detected': snare_detected,
            'hihat_detected': hihat_detected,
            'rhythm_pattern': rhythm_pattern,
            'energy_level': energy,
            'bass_level': bass_level,
            'mid_level': mid_level,
            'treble_level': treble_level
        }
    
    def _calculate_energy(self, audio_data: np.ndarray) -> float:
        """Calculate instantaneous energy of audio signal."""
        energy = np.sum(audio_data ** 2) / len(audio_data)
        return float(energy)
    
    def _detect_onset(self, energy: float) -> Tuple[bool, float]:
        """Detect beat onset using energy-based method."""
        if len(self.energy_history) < 10:
            return False, 0.0
        
        avg_energy = np.mean(list(self.energy_history)[:-1])
        variance = np.var(list(self.energy_history)[:-1])
        
        threshold = avg_energy + 0.5 * np.sqrt(variance)
        
        if energy > threshold * 1.5:
            beat_strength = min(1.0, (energy - threshold) / threshold)
            return True, beat_strength
        
        return False, 0.0
    
    def _calculate_bpm_confidence(self) -> float:
        """Calculate confidence in current BPM estimate."""
        if len(self.beat_history) < 4:
            return 0.0
        
        intervals = []
        beats = list(self.beat_history)
        for i in range(1, len(beats)):
            intervals.append(beats[i] - beats[i-1])
        
        if not intervals:
            return 0.0
        
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        if avg_interval == 0:
            return 0.0
        
        coefficient_of_variation = std_interval / avg_interval
        
        confidence = max(0.0, 1.0 - coefficient_of_variation * 2)
        
        return confidence
    
    def _analyze_rhythm_pattern(self) -> str:
        """Analyze the rhythm pattern."""
        if len(self.beat_history) < 8:
            return "detecting"
        
        bpm = self.current_bpm
        
        if 60 <= bpm <= 90:
            return "slow"
        elif 90 < bpm <= 120:
            return "moderate"
        elif 120 < bpm <= 140:
            return "upbeat"
        elif 140 < bpm <= 180:
            return "fast"
        else:
            return "very_fast"
    
    def reset(self):
        """Reset beat detection state."""
        self.beat_history.clear()
        self.energy_history.clear()
        self.last_beat_time = 0
        self.current_bpm = 120.0
        self.beat_confidence = 0.0
    
    def get_beat_grid(self, num_beats: int = 16) -> List[float]:
        """Get predicted beat times for next N beats."""
        if self.current_bpm == 0:
            return []
        
        beat_interval = 60.0 / self.current_bpm
        current_time = time.time()
        
        time_since_last_beat = current_time - self.last_beat_time if self.last_beat_time > 0 else 0
        
        beat_grid = []
        for i in range(num_beats):
            next_beat_time = current_time + (beat_interval - time_since_last_beat) + (i * beat_interval)
            beat_grid.append(next_beat_time)
        
        return beat_grid
    
    def sync_to_beat(self, current_time: float) -> Dict:
        """Get synchronization info for beat-synced effects."""
        if self.current_bpm == 0 or self.last_beat_time == 0:
            return {
                'phase': 0.0,
                'next_beat_in': 0.0,
                'beat_progress': 0.0
            }
        
        beat_interval = 60.0 / self.current_bpm
        time_since_beat = current_time - self.last_beat_time
        
        phase = (time_since_beat % beat_interval) / beat_interval
        
        next_beat_in = beat_interval - (time_since_beat % beat_interval)
        
        return {
            'phase': phase,
            'next_beat_in': next_beat_in,
            'beat_progress': phase,
            'bpm': self.current_bpm
        }
