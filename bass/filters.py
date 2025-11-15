#!/usr/bin/env python3
"""
Bass Filters Module
Subsonic filters and low-pass crossovers for bass management
"""

import math
from typing import Dict, List, Tuple, Optional


class BassFilters:
    """Subsonic filters and crossover management."""
    
    def __init__(self):
        """Initialize filter calculator."""
        self.subsonic_range = (10, 50)
        self.crossover_range = (50, 250)
        self.available_slopes = [12, 18, 24, 48]
        
    def create_subsonic_filter(self, frequency_hz: float = 25, slope_db: int = 24) -> dict:
        """
        Create subsonic (high-pass) filter to remove rumble.
        
        Args:
            frequency_hz: Cutoff frequency (10-50 Hz)
            slope_db: Filter slope (12, 18, 24 dB/octave)
            
        Returns:
            Subsonic filter configuration
        """
        if not self.subsonic_range[0] <= frequency_hz <= self.subsonic_range[1]:
            raise ValueError(f"Frequency must be between {self.subsonic_range[0]} and {self.subsonic_range[1]} Hz")
        
        if slope_db not in self.available_slopes[:3]:
            raise ValueError(f"Slope must be one of: 12, 18, 24 dB/octave")
        
        filter_order = slope_db // 6
        q_factor = self._calculate_butterworth_q(filter_order)
        
        return {
            'type': 'subsonic_highpass',
            'frequency_hz': round(frequency_hz, 1),
            'slope_db_per_octave': slope_db,
            'filter_order': filter_order,
            'q_factor': round(q_factor, 3),
            'attenuation_at_10hz': round(self._calculate_attenuation(frequency_hz, 10, slope_db), 1),
            'attenuation_at_20hz': round(self._calculate_attenuation(frequency_hz, 20, slope_db), 1),
            'purpose': 'Remove subsonic rumble and protect speakers',
            'recommendations': self._subsonic_recommendations(frequency_hz, slope_db)
        }
    
    def create_lowpass_crossover(self, frequency_hz: float = 80, slope_db: int = 24,
                                 alignment: str = 'linkwitz_riley') -> dict:
        """
        Create low-pass crossover for subwoofer.
        
        Args:
            frequency_hz: Crossover frequency (50-250 Hz)
            slope_db: Crossover slope (12, 18, 24, 48 dB/octave)
            alignment: Filter alignment ('linkwitz_riley', 'butterworth', 'bessel')
            
        Returns:
            Low-pass crossover configuration
        """
        if not self.crossover_range[0] <= frequency_hz <= self.crossover_range[1]:
            raise ValueError(f"Frequency must be between {self.crossover_range[0]} and {self.crossover_range[1]} Hz")
        
        if slope_db not in self.available_slopes:
            raise ValueError(f"Slope must be one of: {self.available_slopes} dB/octave")
        
        filter_order = slope_db // 6
        
        if alignment == 'linkwitz_riley':
            q_factor = 0.707
            phase_response = 'Flat summed response with complementary highpass'
        elif alignment == 'butterworth':
            q_factor = self._calculate_butterworth_q(filter_order)
            phase_response = 'Maximally flat passband'
        elif alignment == 'bessel':
            q_factor = 0.577
            phase_response = 'Linear phase, optimal time alignment'
        else:
            raise ValueError("Alignment must be 'linkwitz_riley', 'butterworth', or 'bessel'")
        
        return {
            'type': 'lowpass_crossover',
            'frequency_hz': round(frequency_hz, 1),
            'slope_db_per_octave': slope_db,
            'filter_order': filter_order,
            'alignment': alignment,
            'q_factor': round(q_factor, 3),
            'phase_response': phase_response,
            'attenuation_at_2x': round(-slope_db, 1),
            'attenuation_at_10x': round(-slope_db * math.log2(10), 1),
            'recommendations': self._crossover_recommendations(frequency_hz, slope_db, alignment)
        }
    
    def recommend_crossover_frequency(self, subwoofer_spec: dict, main_speakers: dict) -> dict:
        """
        Recommend optimal crossover frequency based on speaker specs.
        
        Args:
            subwoofer_spec: {'max_frequency': Hz, 'recommended_range': (low, high)}
            main_speakers: {'min_frequency': Hz, 'type': 'component/coax/6.5/etc'}
            
        Returns:
            Crossover recommendations
        """
        sub_max = subwoofer_spec.get('max_frequency', 200)
        main_min = main_speakers.get('min_frequency', 80)
        speaker_type = main_speakers.get('type', 'coax')
        
        if '6.5' in speaker_type or '6' in speaker_type:
            recommended_freq = 80
            notes = '6.5" speakers work well with 80 Hz crossover'
        elif '5.25' in speaker_type or '5' in speaker_type:
            recommended_freq = 100
            notes = '5.25" speakers need higher crossover for protection'
        elif 'component' in speaker_type.lower():
            recommended_freq = 63
            notes = 'Component speakers can handle lower crossover'
        elif 'coax' in speaker_type.lower():
            recommended_freq = 80
            notes = 'Coaxial speakers typically cross at 80 Hz'
        else:
            recommended_freq = 80
            notes = 'Default 80 Hz crossover for general use'
        
        recommended_freq = max(50, min(recommended_freq, min(sub_max, main_min)))
        
        alternatives = [
            {'frequency': 50, 'use_case': 'Large subwoofer, full-range mains'},
            {'frequency': 63, 'use_case': 'THX standard, home theater'},
            {'frequency': 80, 'use_case': 'Most common, balanced integration'},
            {'frequency': 100, 'use_case': 'Small mains, car audio'},
            {'frequency': 120, 'use_case': 'Very small speakers, laptop replacement'}
        ]
        
        return {
            'recommended_frequency': recommended_freq,
            'recommended_slope': 24,
            'recommended_alignment': 'linkwitz_riley',
            'notes': notes,
            'alternatives': alternatives,
            'subwoofer_limit': sub_max,
            'main_speaker_limit': main_min
        }
    
    def create_bass_boost(self, boost_type: str = 'shelf', frequency_hz: float = 60,
                         boost_db: float = 3.0, q_factor: float = 0.7) -> dict:
        """
        Create bass boost EQ curve.
        
        Args:
            boost_type: 'shelf' or 'peak'
            frequency_hz: Center/corner frequency (20-120 Hz)
            boost_db: Boost amount (0-12 dB)
            q_factor: Q factor for peak boost (0.5-2.0)
            
        Returns:
            Bass boost configuration
        """
        if boost_type not in ['shelf', 'peak']:
            raise ValueError("Boost type must be 'shelf' or 'peak'")
        
        if not 20 <= frequency_hz <= 120:
            raise ValueError("Frequency must be between 20 and 120 Hz")
        
        if not 0 <= boost_db <= 12:
            raise ValueError("Boost must be between 0 and 12 dB")
        
        if boost_type == 'shelf':
            bandwidth_octaves = None
            affected_range = f"All frequencies below {frequency_hz} Hz"
        else:
            if not 0.5 <= q_factor <= 2.0:
                raise ValueError("Q factor must be between 0.5 and 2.0")
            bandwidth_octaves = round(1.0 / q_factor, 2)
            lower_freq = frequency_hz / (2 ** (bandwidth_octaves / 2))
            upper_freq = frequency_hz * (2 ** (bandwidth_octaves / 2))
            affected_range = f"{round(lower_freq)} Hz to {round(upper_freq)} Hz"
        
        headroom_warning = boost_db > 6
        
        return {
            'type': f'bass_boost_{boost_type}',
            'frequency_hz': round(frequency_hz, 1),
            'boost_db': round(boost_db, 1),
            'q_factor': round(q_factor, 2) if boost_type == 'peak' else None,
            'bandwidth_octaves': bandwidth_octaves,
            'affected_range': affected_range,
            'headroom_warning': headroom_warning,
            'recommendations': self._boost_recommendations(boost_type, frequency_hz, boost_db)
        }
    
    def create_preset_filters(self, preset_name: str) -> dict:
        """
        Create filter preset configurations.
        
        Args:
            preset_name: 'tight_bass', 'deep_bass', 'flat_response', 'competition_spl'
            
        Returns:
            Complete filter preset
        """
        presets = {
            'tight_bass': {
                'name': 'Tight Bass (Music)',
                'description': 'Fast, punchy bass for music. Minimal room interaction.',
                'subsonic_filter': self.create_subsonic_filter(30, 24),
                'lowpass_crossover': self.create_lowpass_crossover(80, 24, 'linkwitz_riley'),
                'bass_boost': None,
                'phase': 0,
                'use_case': 'Rock, Metal, Electronic music'
            },
            'deep_bass': {
                'name': 'Deep Bass (Movies)',
                'description': 'Extended low frequency for movie effects and rumble.',
                'subsonic_filter': self.create_subsonic_filter(20, 18),
                'lowpass_crossover': self.create_lowpass_crossover(100, 24, 'linkwitz_riley'),
                'bass_boost': self.create_bass_boost('shelf', 40, 3.0),
                'phase': 0,
                'use_case': 'Movies, explosions, thunder effects'
            },
            'flat_response': {
                'name': 'Flat Response',
                'description': 'Accurate, uncolored bass reproduction.',
                'subsonic_filter': self.create_subsonic_filter(25, 24),
                'lowpass_crossover': self.create_lowpass_crossover(80, 24, 'linkwitz_riley'),
                'bass_boost': None,
                'phase': 0,
                'use_case': 'Critical listening, studio monitoring'
            },
            'competition_spl': {
                'name': 'Competition SPL',
                'description': 'Maximum output at specific frequency. WARNING: High distortion.',
                'subsonic_filter': self.create_subsonic_filter(35, 12),
                'lowpass_crossover': self.create_lowpass_crossover(50, 12, 'butterworth'),
                'bass_boost': self.create_bass_boost('peak', 40, 12.0, 2.0),
                'phase': 0,
                'use_case': 'SPL competitions only - not for music listening',
                'warning': 'Extreme settings - may damage equipment'
            }
        }
        
        if preset_name not in presets:
            raise ValueError(f"Preset must be one of: {list(presets.keys())}")
        
        return presets[preset_name]
    
    def analyze_filter_interaction(self, subsonic: dict, crossover: dict,
                                   boost: Optional[dict] = None) -> dict:
        """
        Analyze interaction between filters.
        
        Args:
            subsonic: Subsonic filter config
            crossover: Crossover filter config
            boost: Optional bass boost config
            
        Returns:
            Filter interaction analysis
        """
        subsonic_freq = subsonic.get('frequency_hz', 25)
        crossover_freq = crossover.get('frequency_hz', 80)
        
        usable_range = (subsonic_freq, crossover_freq)
        bandwidth_octaves = math.log2(crossover_freq / subsonic_freq)
        
        issues = []
        if bandwidth_octaves < 1.5:
            issues.append("Warning: Narrow usable bandwidth - consider adjusting filters")
        
        if subsonic_freq > 30:
            issues.append("High subsonic filter may reduce bass extension")
        
        if crossover_freq < 60:
            issues.append("Low crossover frequency may burden main speakers")
        
        total_boost_db = 0
        if boost:
            total_boost_db = boost.get('boost_db', 0)
            if total_boost_db > 6:
                issues.append("High bass boost may cause clipping - reduce input levels")
        
        return {
            'usable_frequency_range': usable_range,
            'bandwidth_octaves': round(bandwidth_octaves, 2),
            'total_bass_boost_db': round(total_boost_db, 1),
            'estimated_headroom_reduction_db': round(total_boost_db * 1.5, 1),
            'issues': issues,
            'status': 'optimal' if not issues else 'needs_attention'
        }
    
    def _calculate_butterworth_q(self, order: int) -> float:
        """Calculate Q factor for Butterworth filter."""
        if order == 1:
            return 0.5
        elif order == 2:
            return 0.707
        elif order == 3:
            return 1.0
        elif order == 4:
            return 0.707
        else:
            return 0.707
    
    def _calculate_attenuation(self, cutoff_freq: float, test_freq: float, slope_db: int) -> float:
        """Calculate filter attenuation at test frequency."""
        if test_freq >= cutoff_freq:
            return 0.0
        
        frequency_ratio = test_freq / cutoff_freq
        octaves_below = -math.log2(frequency_ratio)
        attenuation = octaves_below * slope_db
        
        return attenuation
    
    def _subsonic_recommendations(self, freq: float, slope: int) -> List[str]:
        """Generate subsonic filter recommendations."""
        recs = []
        
        if freq <= 20:
            recs.append("Maximum bass extension - use only with high-quality subwoofers")
        elif freq <= 25:
            recs.append("Good balance of extension and protection")
        elif freq <= 30:
            recs.append("Safe for most subwoofers")
        else:
            recs.append("Conservative setting - may reduce bass impact")
        
        if slope == 24:
            recs.append("24 dB/octave provides excellent protection")
        elif slope == 18:
            recs.append("18 dB/octave balances protection and extension")
        else:
            recs.append("12 dB/octave is gentle but less protective")
        
        return recs
    
    def _crossover_recommendations(self, freq: float, slope: int, alignment: str) -> List[str]:
        """Generate crossover recommendations."""
        recs = []
        
        if freq == 80:
            recs.append("80 Hz is the most common crossover frequency")
        elif freq < 80:
            recs.append(f"{freq} Hz allows subwoofer to handle more mid-bass")
        else:
            recs.append(f"{freq} Hz reduces load on main speakers")
        
        if slope >= 24:
            recs.append("Steep slope provides good driver protection")
        
        if alignment == 'linkwitz_riley':
            recs.append("Linkwitz-Riley ensures flat summed response")
        
        return recs
    
    def _boost_recommendations(self, boost_type: str, freq: float, boost_db: float) -> List[str]:
        """Generate bass boost recommendations."""
        recs = []
        
        if boost_db > 6:
            recs.append("WARNING: High boost levels may cause distortion")
            recs.append("Reduce input levels by at least 6 dB to prevent clipping")
        elif boost_db > 3:
            recs.append("Moderate boost - monitor for distortion")
        
        if boost_type == 'shelf':
            recs.append("Shelf boost affects all bass frequencies equally")
        else:
            recs.append(f"Peak boost centered at {freq} Hz - use for targeting room modes")
        
        return recs
