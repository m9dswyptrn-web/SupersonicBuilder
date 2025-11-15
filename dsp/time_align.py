#!/usr/bin/env python3
"""
Time Alignment Calculator
Millisecond-precision delay for speaker synchronization and soundstage
"""

import math
from typing import Dict, List, Tuple


class TimeAlignment:
    """Time alignment and delay calculator for speaker positioning."""
    
    def __init__(self):
        """Initialize time alignment calculator."""
        self.speed_of_sound_ms = 343.0
        self.speed_of_sound_inches = 13503.9
        
        self.speaker_positions = {
            'front_left': 'Front Left Door',
            'front_right': 'Front Right Door',
            'rear_left': 'Rear Left Door',
            'rear_right': 'Rear Right Door',
            'center': 'Center Dash',
            'subwoofer': 'Trunk/Rear'
        }
        
        self.chevy_sonic_defaults_inches = {
            'front_left': 36,
            'front_right': 36,
            'rear_left': 60,
            'rear_right': 60,
            'center': 30,
            'subwoofer': 84
        }
    
    def distance_to_delay(
        self,
        distance_meters: float = None,
        distance_inches: float = None,
        distance_feet: float = None
    ) -> Dict:
        """Convert speaker distance to time delay."""
        if distance_meters is not None:
            delay_ms = (distance_meters / self.speed_of_sound_ms) * 1000
            distance_in = distance_meters * 39.3701
        elif distance_inches is not None:
            delay_ms = (distance_inches / self.speed_of_sound_inches) * 1000
            distance_in = distance_inches
        elif distance_feet is not None:
            distance_in = distance_feet * 12
            delay_ms = (distance_in / self.speed_of_sound_inches) * 1000
        else:
            return {'error': 'No distance provided'}
            
        return {
            'delay_ms': round(delay_ms, 3),
            'delay_samples_48k': int(delay_ms * 48),
            'distance_meters': round(distance_in / 39.3701, 3),
            'distance_inches': round(distance_in, 2),
            'distance_feet': round(distance_in / 12, 2)
        }
    
    def delay_to_distance(
        self,
        delay_ms: float,
        unit: str = 'inches'
    ) -> Dict:
        """Convert time delay to speaker distance."""
        distance_meters = (delay_ms / 1000) * self.speed_of_sound_ms
        distance_inches = (delay_ms / 1000) * self.speed_of_sound_inches
        
        result = {
            'delay_ms': delay_ms,
            'distance_meters': round(distance_meters, 3),
            'distance_inches': round(distance_inches, 2),
            'distance_feet': round(distance_inches / 12, 2)
        }
        
        return result
    
    def calculate_speaker_delays(
        self,
        speaker_distances: Dict[str, float],
        listening_position: str = 'driver',
        distance_unit: str = 'inches'
    ) -> Dict:
        """Calculate delay for all speakers based on listening position."""
        delays = {}
        
        if distance_unit == 'inches':
            distances_in = speaker_distances
        elif distance_unit == 'feet':
            distances_in = {k: v * 12 for k, v in speaker_distances.items()}
        elif distance_unit == 'meters':
            distances_in = {k: v * 39.3701 for k, v in speaker_distances.items()}
        else:
            return {'error': 'Invalid distance unit'}
            
        farthest_distance = max(distances_in.values())
        
        for speaker, distance in distances_in.items():
            delay_needed = (farthest_distance - distance) / self.speed_of_sound_inches * 1000
            
            delays[speaker] = {
                'speaker_name': self.speaker_positions.get(speaker, speaker),
                'distance_inches': round(distance, 2),
                'distance_feet': round(distance / 12, 2),
                'delay_ms': round(delay_needed, 3),
                'delay_samples_48k': int(delay_needed * 48),
                'is_reference': distance == farthest_distance
            }
            
        return {
            'listening_position': listening_position,
            'reference_distance_inches': round(farthest_distance, 2),
            'speakers': delays
        }
    
    def calculate_sonic_defaults(
        self,
        listening_position: str = 'driver'
    ) -> Dict:
        """Calculate delays for Chevy Sonic with default speaker positions."""
        if listening_position == 'driver':
            distances = self.chevy_sonic_defaults_inches.copy()
        elif listening_position == 'passenger':
            distances = self.chevy_sonic_defaults_inches.copy()
            distances['front_left'], distances['front_right'] = \
                distances['front_right'], distances['front_left']
            distances['rear_left'], distances['rear_right'] = \
                distances['rear_right'], distances['rear_left']
        elif listening_position == 'center':
            distances = {k: (v + v) / 2 for k, v in self.chevy_sonic_defaults_inches.items()}
        else:
            distances = self.chevy_sonic_defaults_inches.copy()
            
        return self.calculate_speaker_delays(distances, listening_position, 'inches')
    
    def validate_delay_settings(
        self,
        delays: Dict[str, float]
    ) -> Tuple[bool, List[str]]:
        """Validate time alignment delay settings."""
        errors = []
        warnings = []
        
        max_delay_ms = 20.0
        
        for speaker, delay_ms in delays.items():
            if delay_ms < 0:
                errors.append(f"{speaker}: Negative delay ({delay_ms}ms) not allowed")
            elif delay_ms > max_delay_ms:
                errors.append(
                    f"{speaker}: Delay {delay_ms}ms exceeds maximum ({max_delay_ms}ms)"
                )
                
            if delay_ms > 10.0:
                warnings.append(
                    f"{speaker}: High delay ({delay_ms}ms) may indicate measurement error"
                )
                
        delay_values = list(delays.values())
        if delay_values:
            delay_range = max(delay_values) - min(delay_values)
            if delay_range > 15.0:
                warnings.append(
                    f"Large delay range ({delay_range:.1f}ms) detected. "
                    f"Verify speaker measurements."
                )
                
        return len(errors) == 0, errors + warnings
    
    def create_soundstage_visualization(
        self,
        speaker_delays: Dict
    ) -> Dict:
        """Create visualization data for soundstage representation."""
        speakers_data = speaker_delays.get('speakers', {})
        
        visualization = {
            'listening_position': speaker_delays.get('listening_position', 'driver'),
            'speakers': []
        }
        
        position_map = {
            'front_left': {'x': -40, 'y': 30},
            'front_right': {'x': 40, 'y': 30},
            'rear_left': {'x': -40, 'y': -60},
            'rear_right': {'x': 40, 'y': -60},
            'center': {'x': 0, 'y': 35},
            'subwoofer': {'x': 0, 'y': -80}
        }
        
        for speaker_id, speaker_data in speakers_data.items():
            pos = position_map.get(speaker_id, {'x': 0, 'y': 0})
            
            visualization['speakers'].append({
                'id': speaker_id,
                'name': speaker_data['speaker_name'],
                'x': pos['x'],
                'y': pos['y'],
                'distance_inches': speaker_data['distance_inches'],
                'delay_ms': speaker_data['delay_ms'],
                'is_reference': speaker_data.get('is_reference', False)
            })
            
        return visualization
    
    def recommend_measurement_procedure(self) -> Dict:
        """Provide recommendations for measuring speaker distances."""
        return {
            'procedure': [
                {
                    'step': 1,
                    'description': 'Choose listening position (driver seat, center, etc.)'
                },
                {
                    'step': 2,
                    'description': 'Mark head position (where ears will be during listening)'
                },
                {
                    'step': 3,
                    'description': 'Measure from each speaker to head position in straight line'
                },
                {
                    'step': 4,
                    'description': 'Use tape measure or laser distance meter for accuracy'
                },
                {
                    'step': 5,
                    'description': 'Measure to acoustic center of driver (not edge of speaker)'
                },
                {
                    'step': 6,
                    'description': 'For subwoofer, measure to cone center'
                }
            ],
            'tips': [
                'Accuracy ±0.5 inch is sufficient for good time alignment',
                'Remeasure if speaker positions change',
                'Account for seat position if adjustable',
                'Consider both left and right ear positions for center tuning'
            ],
            'tools_needed': [
                'Tape measure (metal, 10+ feet)',
                'Laser distance meter (optional, more accurate)',
                'String or wire for straight-line measurement'
            ]
        }
    
    def export_to_android(
        self,
        speaker_delays: Dict
    ) -> Dict:
        """Export time alignment settings for EOENKK Android head unit."""
        speakers_data = speaker_delays.get('speakers', {})
        
        android_delays = {
            'version': '1.0',
            'listening_position': speaker_delays.get('listening_position', 'driver'),
            'channels': []
        }
        
        for speaker_id, speaker_data in speakers_data.items():
            android_delays['channels'].append({
                'channel_id': speaker_id,
                'channel_name': speaker_data['speaker_name'],
                'delay_milliseconds': speaker_data['delay_ms'],
                'delay_samples': speaker_data['delay_samples_48k'],
                'distance_meters': speaker_data['distance_inches'] / 39.3701,
                'enabled': True
            })
            
        return android_delays
