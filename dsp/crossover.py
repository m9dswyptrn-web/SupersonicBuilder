#!/usr/bin/env python3
"""
Active Crossover Logic
2-way, 3-way, 4-way crossover configurations with multiple filter types
"""

import math
from typing import Dict, List, Tuple


class ActiveCrossover:
    """Active crossover system for multi-way speaker configurations."""
    
    def __init__(self):
        """Initialize active crossover."""
        self.filter_types = {
            'butterworth': 'Butterworth (maximally flat)',
            'linkwitz_riley': 'Linkwitz-Riley (phase-coherent)',
            'bessel': 'Bessel (linear phase)'
        }
        
        self.slopes = {
            12: '12 dB/octave (2nd order)',
            18: '18 dB/octave (3rd order)',
            24: '24 dB/octave (4th order)',
            36: '36 dB/octave (6th order)',
            48: '48 dB/octave (8th order)'
        }
        
        self.crossover_configs = {
            '2-way': {
                'description': 'Woofer + Tweeter',
                'crossovers': ['low_high'],
                'typical_frequency': 2500
            },
            '3-way': {
                'description': 'Woofer + Midrange + Tweeter',
                'crossovers': ['low_mid', 'mid_high'],
                'typical_frequencies': [250, 2500]
            },
            '4-way': {
                'description': 'Subwoofer + Woofer + Midrange + Tweeter',
                'crossovers': ['sub_low', 'low_mid', 'mid_high'],
                'typical_frequencies': [80, 250, 2500]
            }
        }
    
    def create_crossover_point(
        self,
        frequency: float,
        slope_db: int = 24,
        filter_type: str = 'linkwitz_riley'
    ) -> Dict:
        """Create a crossover point with specified parameters."""
        if filter_type not in self.filter_types:
            filter_type = 'linkwitz_riley'
            
        if slope_db not in self.slopes:
            slope_db = 24
            
        order = slope_db // 6
        
        return {
            'frequency': frequency,
            'slope_db': slope_db,
            'filter_type': filter_type,
            'order': order,
            'q_factor': self._get_q_factor(filter_type, order)
        }
    
    def _get_q_factor(self, filter_type: str, order: int) -> float:
        """Get Q factor for filter type and order."""
        if filter_type == 'butterworth':
            if order == 2:
                return 0.707
            elif order == 4:
                return 0.541
            else:
                return 0.707
        elif filter_type == 'linkwitz_riley':
            return 0.707
        elif filter_type == 'bessel':
            return 0.577
        else:
            return 0.707
    
    def create_2way_crossover(
        self,
        frequency: float = 2500,
        slope_db: int = 24,
        filter_type: str = 'linkwitz_riley'
    ) -> Dict:
        """Create 2-way crossover (woofer/tweeter)."""
        crossover_point = self.create_crossover_point(frequency, slope_db, filter_type)
        
        return {
            'configuration': '2-way',
            'description': 'Woofer + Tweeter',
            'crossover_points': [crossover_point],
            'outputs': {
                'low': {
                    'name': 'Woofer',
                    'filter': 'low_pass',
                    'frequency': frequency,
                    'slope_db': slope_db,
                    'range': f'20Hz - {frequency}Hz'
                },
                'high': {
                    'name': 'Tweeter',
                    'filter': 'high_pass',
                    'frequency': frequency,
                    'slope_db': slope_db,
                    'range': f'{frequency}Hz - 20kHz'
                }
            }
        }
    
    def create_3way_crossover(
        self,
        low_mid_freq: float = 250,
        mid_high_freq: float = 2500,
        slope_db: int = 24,
        filter_type: str = 'linkwitz_riley'
    ) -> Dict:
        """Create 3-way crossover (woofer/midrange/tweeter)."""
        crossover_low_mid = self.create_crossover_point(low_mid_freq, slope_db, filter_type)
        crossover_mid_high = self.create_crossover_point(mid_high_freq, slope_db, filter_type)
        
        return {
            'configuration': '3-way',
            'description': 'Woofer + Midrange + Tweeter',
            'crossover_points': [crossover_low_mid, crossover_mid_high],
            'outputs': {
                'low': {
                    'name': 'Woofer',
                    'filter': 'low_pass',
                    'frequency': low_mid_freq,
                    'slope_db': slope_db,
                    'range': f'20Hz - {low_mid_freq}Hz'
                },
                'mid': {
                    'name': 'Midrange',
                    'filter': 'band_pass',
                    'low_frequency': low_mid_freq,
                    'high_frequency': mid_high_freq,
                    'slope_db': slope_db,
                    'range': f'{low_mid_freq}Hz - {mid_high_freq}Hz'
                },
                'high': {
                    'name': 'Tweeter',
                    'filter': 'high_pass',
                    'frequency': mid_high_freq,
                    'slope_db': slope_db,
                    'range': f'{mid_high_freq}Hz - 20kHz'
                }
            }
        }
    
    def create_4way_crossover(
        self,
        sub_low_freq: float = 80,
        low_mid_freq: float = 250,
        mid_high_freq: float = 2500,
        slope_db: int = 24,
        filter_type: str = 'linkwitz_riley'
    ) -> Dict:
        """Create 4-way crossover (subwoofer/woofer/midrange/tweeter)."""
        crossover_sub_low = self.create_crossover_point(sub_low_freq, slope_db, filter_type)
        crossover_low_mid = self.create_crossover_point(low_mid_freq, slope_db, filter_type)
        crossover_mid_high = self.create_crossover_point(mid_high_freq, slope_db, filter_type)
        
        return {
            'configuration': '4-way',
            'description': 'Subwoofer + Woofer + Midrange + Tweeter',
            'crossover_points': [crossover_sub_low, crossover_low_mid, crossover_mid_high],
            'outputs': {
                'sub': {
                    'name': 'Subwoofer',
                    'filter': 'low_pass',
                    'frequency': sub_low_freq,
                    'slope_db': slope_db,
                    'range': f'20Hz - {sub_low_freq}Hz'
                },
                'low': {
                    'name': 'Woofer',
                    'filter': 'band_pass',
                    'low_frequency': sub_low_freq,
                    'high_frequency': low_mid_freq,
                    'slope_db': slope_db,
                    'range': f'{sub_low_freq}Hz - {low_mid_freq}Hz'
                },
                'mid': {
                    'name': 'Midrange',
                    'filter': 'band_pass',
                    'low_frequency': low_mid_freq,
                    'high_frequency': mid_high_freq,
                    'slope_db': slope_db,
                    'range': f'{low_mid_freq}Hz - {mid_high_freq}Hz'
                },
                'high': {
                    'name': 'Tweeter',
                    'filter': 'high_pass',
                    'frequency': mid_high_freq,
                    'slope_db': slope_db,
                    'range': f'{mid_high_freq}Hz - 20kHz'
                }
            }
        }
    
    def calculate_filter_response(
        self,
        crossover_point: Dict,
        filter_mode: str,
        num_points: int = 1000
    ) -> List[Dict]:
        """Calculate frequency response for a crossover filter."""
        min_freq = 20.0
        max_freq = 20000.0
        
        frequencies = [
            min_freq * math.pow(max_freq / min_freq, i / (num_points - 1))
            for i in range(num_points)
        ]
        
        fc = crossover_point['frequency']
        slope_db = crossover_point['slope_db']
        order = crossover_point['order']
        
        response = []
        for freq in frequencies:
            if filter_mode == 'low_pass':
                if freq <= fc:
                    gain_db = 0.0
                else:
                    octaves = math.log2(freq / fc)
                    gain_db = -slope_db * octaves
            elif filter_mode == 'high_pass':
                if freq >= fc:
                    gain_db = 0.0
                else:
                    octaves = math.log2(fc / freq)
                    gain_db = -slope_db * octaves
            else:
                gain_db = 0.0
                
            gain_db = max(-96.0, gain_db)
            
            response.append({
                'frequency': round(freq, 2),
                'gain_db': round(gain_db, 3)
            })
            
        return response
    
    def validate_crossover_frequencies(
        self,
        frequencies: List[float]
    ) -> Tuple[bool, List[str]]:
        """Validate crossover frequency selections."""
        errors = []
        
        if not frequencies:
            errors.append("No crossover frequencies specified")
            return False, errors
            
        sorted_freqs = sorted(frequencies)
        
        for i, freq in enumerate(sorted_freqs):
            if freq < 20 or freq > 20000:
                errors.append(f"Frequency {freq}Hz out of audible range (20Hz - 20kHz)")
                
            if i > 0:
                prev_freq = sorted_freqs[i - 1]
                ratio = freq / prev_freq
                if ratio < 2.0:
                    errors.append(
                        f"Crossover points {prev_freq}Hz and {freq}Hz are too close "
                        f"(ratio {ratio:.2f} < 2.0)"
                    )
                    
        return len(errors) == 0, errors
    
    def recommend_crossover_frequencies(
        self,
        speaker_config: str,
        speaker_specs: Dict = None
    ) -> Dict:
        """Recommend crossover frequencies based on speaker configuration."""
        recommendations = {
            '2-way': {
                'frequencies': [2500],
                'description': 'Standard 2-way component system',
                'notes': 'Adjust based on woofer size (larger woofer = lower crossover)'
            },
            '3-way': {
                'frequencies': [250, 2500],
                'description': 'Full-range 3-way system',
                'notes': 'Low crossover for 6.5" woofer, high for 1" tweeter'
            },
            '4-way': {
                'frequencies': [80, 250, 2500],
                'description': '4-way with subwoofer integration',
                'notes': 'Sub at 80Hz (typical car audio), woofer/mid/tweet above'
            }
        }
        
        return recommendations.get(speaker_config, recommendations['2-way'])
    
    def export_to_android(
        self,
        crossover_config: Dict
    ) -> Dict:
        """Export crossover settings for EOENKK Android head unit."""
        android_crossover = {
            'version': '1.0',
            'configuration': crossover_config['configuration'],
            'outputs': []
        }
        
        for output_name, output_config in crossover_config['outputs'].items():
            android_output = {
                'output_name': output_name,
                'display_name': output_config['name'],
                'filter_type': output_config['filter'],
                'enabled': True
            }
            
            if output_config['filter'] == 'low_pass':
                android_output['frequency_hz'] = output_config['frequency']
                android_output['slope_db_octave'] = output_config['slope_db']
            elif output_config['filter'] == 'high_pass':
                android_output['frequency_hz'] = output_config['frequency']
                android_output['slope_db_octave'] = output_config['slope_db']
            elif output_config['filter'] == 'band_pass':
                android_output['low_frequency_hz'] = output_config['low_frequency']
                android_output['high_frequency_hz'] = output_config['high_frequency']
                android_output['slope_db_octave'] = output_config['slope_db']
                
            android_crossover['outputs'].append(android_output)
            
        return android_crossover
