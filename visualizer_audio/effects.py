#!/usr/bin/env python3
"""
Visual Effects Engine
Music-reactive animations and particle effects
"""

import numpy as np
from typing import Dict, List, Tuple
import time
import random


class EffectsEngine:
    """Generate music-reactive visual effects."""
    
    def __init__(self):
        """Initialize effects engine."""
        self.particles = []
        self.max_particles = 1000
        self.effect_intensity = 0.8
        
        self.color_pulse_state = 0.0
        self.last_update = time.time()
    
    def generate_particles(self, bass_level: float, beat_detected: bool, 
                          num_particles: int = 10) -> List[Dict]:
        """
        Generate particle effects synced to bass.
        
        Args:
            bass_level: Bass frequency energy (0-1)
            beat_detected: Whether a beat was detected
            num_particles: Number of particles to generate
        
        Returns:
            List of particle definitions
        """
        new_particles = []
        
        if beat_detected and bass_level > 0.5:
            particle_count = int(num_particles * bass_level * self.effect_intensity)
            
            for _ in range(particle_count):
                particle = {
                    'x': random.uniform(0, 1),
                    'y': random.uniform(0.4, 0.6),
                    'vx': random.uniform(-0.5, 0.5),
                    'vy': random.uniform(-1.0, -0.3),
                    'size': random.uniform(2, 8) * bass_level,
                    'color': self._get_bass_color(bass_level),
                    'life': 1.0,
                    'decay': random.uniform(0.01, 0.03)
                }
                new_particles.append(particle)
        
        return new_particles
    
    def update_particles(self, dt: float) -> List[Dict]:
        """
        Update existing particles.
        
        Args:
            dt: Delta time since last update
        
        Returns:
            List of active particles
        """
        active_particles = []
        
        for particle in self.particles:
            particle['life'] -= particle['decay'] * dt * 60
            
            if particle['life'] > 0:
                particle['x'] += particle['vx'] * dt
                particle['y'] += particle['vy'] * dt
                particle['vy'] += 0.5 * dt
                
                active_particles.append(particle)
        
        self.particles = active_particles[-self.max_particles:]
        
        return self.particles
    
    def add_particles(self, particles: List[Dict]):
        """Add new particles to the system."""
        self.particles.extend(particles)
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]
    
    def generate_color_pulse(self, beat_detected: bool, beat_strength: float, 
                            bpm: float) -> Dict:
        """
        Generate color pulsing effect synced to beat.
        
        Args:
            beat_detected: Whether a beat was detected
            beat_strength: Strength of the beat (0-1)
            bpm: Current BPM
        
        Returns:
            Color pulse parameters
        """
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        if beat_detected:
            self.color_pulse_state = beat_strength
        else:
            decay_rate = bpm / 120.0
            self.color_pulse_state *= (1.0 - decay_rate * dt)
            self.color_pulse_state = max(0.0, self.color_pulse_state)
        
        hue = (current_time * 0.1) % 1.0
        
        brightness = 0.5 + (self.color_pulse_state * 0.5)
        
        return {
            'pulse_strength': self.color_pulse_state,
            'hue': hue,
            'saturation': 0.8,
            'brightness': brightness,
            'beat_flash': beat_detected
        }
    
    def generate_waveform_distortion(self, bass_level: float, mid_level: float, 
                                    treble_level: float) -> Dict:
        """
        Generate waveform distortion effect based on frequency content.
        
        Args:
            bass_level: Bass energy (0-1)
            mid_level: Mid energy (0-1)
            treble_level: Treble energy (0-1)
        
        Returns:
            Distortion parameters
        """
        return {
            'amplitude_scale': 1.0 + (bass_level * 0.5),
            'frequency_warp': mid_level * 2.0,
            'phase_shift': treble_level * np.pi,
            'thickness': 1.0 + (bass_level * 3.0)
        }
    
    def generate_spectrum_glow(self, band_levels: List[float]) -> List[Dict]:
        """
        Generate glow effect for spectrum bars.
        
        Args:
            band_levels: Frequency band levels (0-1)
        
        Returns:
            Glow parameters for each band
        """
        glow_effects = []
        
        for i, level in enumerate(band_levels):
            glow = {
                'intensity': level * 0.8,
                'radius': 5 + (level * 15),
                'color_shift': i / len(band_levels)
            }
            glow_effects.append(glow)
        
        return glow_effects
    
    def generate_circular_waves(self, beat_detected: bool, bpm: float) -> List[Dict]:
        """
        Generate circular wave effects for circular visualizer.
        
        Args:
            beat_detected: Whether a beat was detected
            bpm: Current BPM
        
        Returns:
            List of wave definitions
        """
        waves = []
        
        if beat_detected:
            wave = {
                'radius': 0.0,
                'max_radius': 1.0,
                'speed': bpm / 60.0,
                'opacity': 1.0,
                'thickness': 3.0,
                'creation_time': time.time()
            }
            waves.append(wave)
        
        return waves
    
    def _get_bass_color(self, bass_level: float) -> Tuple[int, int, int]:
        """Get color based on bass level."""
        if bass_level > 0.8:
            return (255, 50, 50)
        elif bass_level > 0.6:
            return (255, 100, 50)
        elif bass_level > 0.4:
            return (255, 150, 0)
        else:
            return (255, 200, 0)
    
    def set_intensity(self, intensity: float):
        """Set effect intensity (0-1)."""
        self.effect_intensity = max(0.0, min(1.0, intensity))
    
    def clear_particles(self):
        """Clear all particles."""
        self.particles = []
    
    def get_rgb_lighting_data(self, bass_level: float, mid_level: float, 
                             treble_level: float, beat_detected: bool) -> Dict:
        """
        Generate RGB lighting controller data for port 8500.
        
        Args:
            bass_level: Bass energy (0-1)
            mid_level: Mid energy (0-1)
            treble_level: Treble energy (0-1)
            beat_detected: Whether a beat was detected
        
        Returns:
            RGB lighting data for external controller
        """
        r = int(bass_level * 255)
        g = int(mid_level * 255)
        b = int(treble_level * 255)
        
        if beat_detected:
            brightness = 1.0
            strobe = True
        else:
            brightness = 0.3 + (max(bass_level, mid_level, treble_level) * 0.7)
            strobe = False
        
        return {
            'mode': 'music_reactive',
            'color': {
                'r': r,
                'g': g,
                'b': b
            },
            'brightness': brightness,
            'strobe': strobe,
            'beat_flash': beat_detected,
            'bass_level': bass_level,
            'mid_level': mid_level,
            'treble_level': treble_level
        }
