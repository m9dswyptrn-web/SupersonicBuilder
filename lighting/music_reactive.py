#!/usr/bin/env python3
"""
Music Reactive Engine
Syncs lighting effects with audio from the Audio Visualizer service
"""

import time
import requests
import threading
from typing import Dict, Callable, Optional
from datetime import datetime


class MusicReactiveEngine:
    """Engine for music-reactive lighting effects."""
    
    def __init__(self, led_controller):
        """Initialize music reactive engine."""
        self.led_controller = led_controller
        self.audio_visualizer_url = 'http://localhost:8300'
        
        self.mode = 'off'
        self.sensitivity = 50
        self.running = False
        self.thread = None
        
        self.bass_threshold = 0.6
        self.beat_threshold = 0.7
        
        self.last_bass_time = 0
        self.last_beat_time = 0
        
        self.color_index = 0
        self.party_colors = [
            {'r': 255, 'g': 0, 'b': 0},
            {'r': 0, 'g': 255, 'b': 0},
            {'r': 0, 'g': 0, 'b': 255},
            {'r': 255, 'g': 255, 'b': 0},
            {'r': 255, 'g': 0, 'b': 255},
            {'r': 0, 'g': 255, 'b': 255},
            {'r': 255, 'g': 128, 'b': 0}
        ]
        
        print("✓ Music Reactive Engine initialized")
        print(f"  - Audio Visualizer: {self.audio_visualizer_url}")
    
    def set_mode(self, mode: str):
        """Set reactive mode."""
        valid_modes = ['off', 'bass_pulse', 'spectrum', 'beat_sync', 'breathing', 'party']
        
        if mode not in valid_modes:
            return False
        
        self.stop()
        self.mode = mode
        
        if mode != 'off':
            self.start()
        
        return True
    
    def set_sensitivity(self, sensitivity: int):
        """Set sensitivity (0-100)."""
        self.sensitivity = max(0, min(100, sensitivity))
        
        sensitivity_factor = self.sensitivity / 100.0
        self.bass_threshold = 0.4 + (0.4 * (1.0 - sensitivity_factor))
        self.beat_threshold = 0.5 + (0.4 * (1.0 - sensitivity_factor))
    
    def start(self):
        """Start music reactive processing."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.thread.start()
        
        print(f"✓ Music reactive mode started: {self.mode}")
    
    def stop(self):
        """Stop music reactive processing."""
        if not self.running:
            return
        
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
        
        self.led_controller.stop_animation()
        
        print("✓ Music reactive mode stopped")
    
    def _processing_loop(self):
        """Main processing loop for music reactive effects."""
        while self.running:
            try:
                if self.mode == 'bass_pulse':
                    self._bass_pulse_mode()
                elif self.mode == 'spectrum':
                    self._spectrum_mode()
                elif self.mode == 'beat_sync':
                    self._beat_sync_mode()
                elif self.mode == 'breathing':
                    self._breathing_mode()
                elif self.mode == 'party':
                    self._party_mode()
                
                time.sleep(0.05)
                
            except Exception as e:
                print(f"Music reactive error: {e}")
                time.sleep(0.5)
    
    def _get_audio_data(self) -> Optional[Dict]:
        """Get audio data from visualizer service."""
        try:
            response = requests.get(
                f'{self.audio_visualizer_url}/api/audio/current',
                timeout=0.5
            )
            
            if response.status_code == 200:
                return response.json()
            
        except requests.exceptions.RequestException:
            pass
        
        return self._generate_mock_audio_data()
    
    def _generate_mock_audio_data(self) -> Dict:
        """Generate mock audio data for development."""
        import random
        import math
        
        t = time.time()
        
        bass = abs(math.sin(t * 2.0)) * random.uniform(0.5, 1.0)
        beat = 1.0 if (int(t * 2) % 2 == 0) else 0.3
        
        frequency_bands = [
            random.uniform(0.3, 0.8) for _ in range(8)
        ]
        
        return {
            'bass_level': bass,
            'beat_detected': beat > 0.8,
            'beat_strength': beat,
            'frequency_bands': frequency_bands,
            'rms_level': random.uniform(0.4, 0.7),
            'timestamp': datetime.now().isoformat()
        }
    
    def _bass_pulse_mode(self):
        """Bass pulse mode - lights pulse with bass kicks."""
        audio_data = self._get_audio_data()
        
        if not audio_data:
            return
        
        bass_level = audio_data.get('bass_level', 0)
        
        if bass_level > self.bass_threshold:
            current_time = time.time()
            
            if current_time - self.last_bass_time > 0.1:
                intensity = (bass_level - self.bass_threshold) / (1.0 - self.bass_threshold)
                self.led_controller.pulse_all(intensity)
                self.last_bass_time = current_time
    
    def _spectrum_mode(self):
        """Spectrum mode - colors follow frequency bands."""
        audio_data = self._get_audio_data()
        
        if not audio_data:
            return
        
        frequency_bands = audio_data.get('frequency_bands', [0] * 8)
        
        zone_names = list(self.led_controller.zones.keys())
        
        band_colors = [
            {'r': 255, 'g': 0, 'b': 0},
            {'r': 255, 'g': 127, 'b': 0},
            {'r': 255, 'g': 255, 'b': 0},
            {'r': 0, 'g': 255, 'b': 0},
            {'r': 0, 'g': 255, 'b': 255},
            {'r': 0, 'g': 0, 'b': 255},
            {'r': 138, 'g': 43, 'b': 226},
            {'r': 255, 'g': 0, 'b': 255}
        ]
        
        for i, zone_name in enumerate(zone_names):
            if i < len(frequency_bands):
                band_level = frequency_bands[i]
                color = band_colors[i % len(band_colors)]
                
                r = int(color['r'] * band_level)
                g = int(color['g'] * band_level)
                b = int(color['b'] * band_level)
                
                self.led_controller.set_zone_color(zone_name, r, g, b)
    
    def _beat_sync_mode(self):
        """Beat sync mode - flash on beats."""
        audio_data = self._get_audio_data()
        
        if not audio_data:
            return
        
        beat_detected = audio_data.get('beat_detected', False)
        beat_strength = audio_data.get('beat_strength', 0)
        
        if beat_detected and beat_strength > self.beat_threshold:
            current_time = time.time()
            
            if current_time - self.last_beat_time > 0.2:
                zone_names = list(self.led_controller.zones.keys())
                
                import random
                flash_zone = random.choice(zone_names)
                
                self.led_controller.flash_zone(flash_zone, 0.1)
                self.last_beat_time = current_time
    
    def _breathing_mode(self):
        """Breathing mode - smooth fade in/out with music."""
        audio_data = self._get_audio_data()
        
        if not audio_data:
            return
        
        rms_level = audio_data.get('rms_level', 0.5)
        
        target_brightness = int(30 + (rms_level * 70))
        
        current_brightness = self.led_controller.global_brightness
        
        if abs(target_brightness - current_brightness) > 5:
            new_brightness = current_brightness + (target_brightness - current_brightness) * 0.1
            self.led_controller.set_global_brightness(int(new_brightness))
    
    def _party_mode(self):
        """Party mode - rapid color changes."""
        audio_data = self._get_audio_data()
        
        if not audio_data:
            return
        
        beat_detected = audio_data.get('beat_detected', False)
        
        if beat_detected:
            self.color_index = (self.color_index + 1) % len(self.party_colors)
            
            zone_names = list(self.led_controller.zones.keys())
            
            for i, zone_name in enumerate(zone_names):
                color_idx = (self.color_index + i) % len(self.party_colors)
                color = self.party_colors[color_idx]
                
                self.led_controller.set_zone_color(
                    zone_name,
                    color['r'],
                    color['g'],
                    color['b']
                )
    
    def get_status(self) -> Dict:
        """Get music reactive engine status."""
        return {
            'mode': self.mode,
            'running': self.running,
            'sensitivity': self.sensitivity,
            'bass_threshold': self.bass_threshold,
            'beat_threshold': self.beat_threshold,
            'audio_visualizer_url': self.audio_visualizer_url,
            'last_bass_time': self.last_bass_time,
            'last_beat_time': self.last_beat_time
        }
    
    def test_connection(self) -> bool:
        """Test connection to audio visualizer."""
        try:
            response = requests.get(
                f'{self.audio_visualizer_url}/health',
                timeout=2.0
            )
            return response.status_code == 200
        except:
            return False
    
    def get_stats(self) -> Dict:
        """Get engine statistics."""
        return {
            'mode': self.mode,
            'running': self.running,
            'sensitivity': self.sensitivity,
            'audio_connected': self.test_connection(),
            'uptime_seconds': int(time.time() - self.last_bass_time) if self.last_bass_time > 0 else 0
        }
