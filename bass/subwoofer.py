#!/usr/bin/env python3
"""
Subwoofer Control Module
Advanced subwoofer integration with multiple sub support
"""

import math
from typing import Dict, List, Optional


class SubwooferController:
    """Control subwoofer levels, phase, and delay alignment."""
    
    def __init__(self):
        """Initialize subwoofer controller."""
        self.max_subwoofers = 4
        self.speed_of_sound_inches_per_ms = 13.5
        self.speed_of_sound_cm_per_ms = 34.3
        
    def configure_subwoofer(self, sub_id: int = 1, level_percent: float = 75.0,
                           phase_degrees: float = 0.0, delay_ms: float = 0.0) -> dict:
        """
        Configure individual subwoofer settings.
        
        Args:
            sub_id: Subwoofer ID (1-4)
            level_percent: Output level (0-100%)
            phase_degrees: Phase adjustment (0-180°)
            delay_ms: Delay in milliseconds
            
        Returns:
            Subwoofer configuration dict
        """
        if not 1 <= sub_id <= self.max_subwoofers:
            raise ValueError(f"Subwoofer ID must be between 1 and {self.max_subwoofers}")
        
        if not 0 <= level_percent <= 100:
            raise ValueError("Level must be between 0 and 100%")
        
        if not 0 <= phase_degrees <= 180:
            raise ValueError("Phase must be between 0 and 180 degrees")
        
        if not 0 <= delay_ms <= 50:
            raise ValueError("Delay must be between 0 and 50ms")
        
        level_db = self._percent_to_db(level_percent)
        
        return {
            'subwoofer_id': sub_id,
            'level_percent': round(level_percent, 1),
            'level_db': round(level_db, 2),
            'phase_degrees': round(phase_degrees, 1),
            'delay_ms': round(delay_ms, 3),
            'delay_samples_48k': int(delay_ms * 48),
            'enabled': level_percent > 0
        }
    
    def configure_multiple_subs(self, sub_configs: List[dict]) -> dict:
        """
        Configure multiple subwoofers.
        
        Args:
            sub_configs: List of subwoofer configuration dicts
            
        Returns:
            Multi-sub configuration
        """
        if len(sub_configs) > self.max_subwoofers:
            raise ValueError(f"Maximum {self.max_subwoofers} subwoofers supported")
        
        configured_subs = []
        for config in sub_configs:
            sub_id = config.get('sub_id', len(configured_subs) + 1)
            level = config.get('level_percent', 75.0)
            phase = config.get('phase_degrees', 0.0)
            delay = config.get('delay_ms', 0.0)
            
            configured_subs.append(
                self.configure_subwoofer(sub_id, level, phase, delay)
            )
        
        return {
            'subwoofers': configured_subs,
            'count': len(configured_subs),
            'total_output_db': self._calculate_combined_output(configured_subs),
            'configuration': self._analyze_configuration(configured_subs)
        }
    
    def calculate_delay_from_distance(self, distance: float, unit: str = 'inches',
                                     main_speaker_distance: Optional[float] = None) -> dict:
        """
        Calculate subwoofer delay from distance to listening position.
        
        Args:
            distance: Distance to subwoofer
            unit: 'inches', 'cm', or 'feet'
            main_speaker_distance: Optional distance to main speakers
            
        Returns:
            Delay calculation results
        """
        if unit == 'feet':
            distance = distance * 12
            unit = 'inches'
        
        if unit == 'inches':
            speed = self.speed_of_sound_inches_per_ms
        elif unit == 'cm':
            speed = self.speed_of_sound_cm_per_ms
        else:
            raise ValueError("Unit must be 'inches', 'cm', or 'feet'")
        
        delay_ms = distance / speed
        
        result = {
            'distance': round(distance, 2),
            'unit': unit,
            'delay_ms': round(delay_ms, 3),
            'delay_samples_48k': int(delay_ms * 48)
        }
        
        if main_speaker_distance is not None:
            main_delay_ms = main_speaker_distance / speed
            alignment_delay = delay_ms - main_delay_ms
            
            result['main_speaker_distance'] = round(main_speaker_distance, 2)
            result['main_speaker_delay_ms'] = round(main_delay_ms, 3)
            result['alignment_delay_ms'] = round(alignment_delay, 3)
            result['recommendation'] = self._delay_recommendation(alignment_delay)
        
        return result
    
    def optimize_dual_sub_placement(self, room_dimensions: dict,
                                   listening_position: dict) -> dict:
        """
        Recommend optimal dual subwoofer placement.
        
        Args:
            room_dimensions: {'length': x, 'width': y, 'height': z} in inches
            listening_position: {'x': x, 'y': y} from front-left corner
            
        Returns:
            Placement recommendations
        """
        length = room_dimensions.get('length', 120)
        width = room_dimensions.get('width', 80)
        
        placements = [
            {
                'name': 'Front corners (recommended)',
                'sub1_position': {'x': 0, 'y': 0, 'description': 'Front left corner'},
                'sub2_position': {'x': width, 'y': 0, 'description': 'Front right corner'},
                'phase_config': {'sub1_phase': 0, 'sub2_phase': 0},
                'benefits': ['Even bass distribution', 'Minimizes room modes', 'Easy setup'],
                'rating': 9
            },
            {
                'name': 'Diagonal corners',
                'sub1_position': {'x': 0, 'y': 0, 'description': 'Front left corner'},
                'sub2_position': {'x': width, 'y': length, 'description': 'Rear right corner'},
                'phase_config': {'sub1_phase': 0, 'sub2_phase': 180},
                'benefits': ['Smoothest response', 'Nulls room modes', 'Professional setup'],
                'rating': 10
            },
            {
                'name': 'Mid-wall opposing',
                'sub1_position': {'x': 0, 'y': length/2, 'description': 'Left wall center'},
                'sub2_position': {'x': width, 'y': length/2, 'description': 'Right wall center'},
                'phase_config': {'sub1_phase': 0, 'sub2_phase': 0},
                'benefits': ['Excellent imaging', 'Uniform coverage'],
                'rating': 8
            }
        ]
        
        for placement in placements:
            lp_x = listening_position.get('x', width/2)
            lp_y = listening_position.get('y', length*0.4)
            
            sub1_dist = math.sqrt((placement['sub1_position']['x'] - lp_x)**2 + 
                                 (placement['sub1_position']['y'] - lp_y)**2)
            sub2_dist = math.sqrt((placement['sub2_position']['x'] - lp_x)**2 + 
                                 (placement['sub2_position']['y'] - lp_y)**2)
            
            placement['distances'] = {
                'sub1_to_listener_inches': round(sub1_dist, 1),
                'sub2_to_listener_inches': round(sub2_dist, 1),
                'delay_difference_ms': round(abs(sub1_dist - sub2_dist) / self.speed_of_sound_inches_per_ms, 3)
            }
        
        placements.sort(key=lambda x: x['rating'], reverse=True)
        
        return {
            'room_dimensions': room_dimensions,
            'listening_position': listening_position,
            'placements': placements,
            'recommendation': placements[0]['name']
        }
    
    def calculate_group_output(self, subwoofers: List[dict]) -> dict:
        """
        Calculate combined output of multiple subwoofers.
        
        Args:
            subwoofers: List of subwoofer configs with level_db and phase
            
        Returns:
            Combined output analysis
        """
        if not subwoofers:
            return {'total_output_db': 0, 'phase_issues': True}
        
        total_power = 0
        for sub in subwoofers:
            level_db = sub.get('level_db', 0)
            power = 10 ** (level_db / 10)
            total_power += power
        
        combined_db = 10 * math.log10(total_power) if total_power > 0 else -96
        
        theoretical_increase = 10 * math.log10(len(subwoofers))
        efficiency = (combined_db / theoretical_increase * 100) if theoretical_increase > 0 else 0
        
        phase_issues = self._detect_phase_issues(subwoofers)
        
        return {
            'total_output_db': round(combined_db, 2),
            'subwoofer_count': len(subwoofers),
            'theoretical_increase_db': round(theoretical_increase, 2),
            'efficiency_percent': round(efficiency, 1),
            'phase_issues': phase_issues,
            'recommendation': 'Check phase alignment' if phase_issues else 'Configuration optimal'
        }
    
    def _percent_to_db(self, percent: float) -> float:
        """Convert percentage to dB."""
        if percent <= 0:
            return -96.0
        return 20 * math.log10(percent / 100.0)
    
    def _calculate_combined_output(self, subs: List[dict]) -> float:
        """Calculate combined output level in dB."""
        total_power = sum(10 ** (sub['level_db'] / 10) for sub in subs)
        return round(10 * math.log10(total_power) if total_power > 0 else -96, 2)
    
    def _analyze_configuration(self, subs: List[dict]) -> str:
        """Analyze multi-sub configuration."""
        count = len(subs)
        if count == 1:
            return 'single_subwoofer'
        elif count == 2:
            return 'dual_subwoofer'
        elif count == 3:
            return 'triple_subwoofer'
        elif count == 4:
            return 'quad_subwoofer'
        return 'custom'
    
    def _delay_recommendation(self, alignment_delay: float) -> str:
        """Recommend action based on delay difference."""
        if abs(alignment_delay) < 0.5:
            return 'No adjustment needed - excellent alignment'
        elif abs(alignment_delay) < 2.0:
            return 'Minor delay adjustment recommended'
        elif abs(alignment_delay) < 5.0:
            return 'Delay adjustment needed for optimal integration'
        else:
            return 'Significant delay correction required - check placement'
    
    def _detect_phase_issues(self, subs: List[dict]) -> bool:
        """Detect potential phase cancellation issues."""
        if len(subs) < 2:
            return False
        
        phases = [sub.get('phase_degrees', 0) for sub in subs]
        
        for i in range(len(phases)):
            for j in range(i + 1, len(phases)):
                phase_diff = abs(phases[i] - phases[j])
                if 80 <= phase_diff <= 100:
                    return True
        
        return False
