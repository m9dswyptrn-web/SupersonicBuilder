import math
from typing import Dict, List, Tuple, Any, Optional


class SpeakerPositioning:
    """
    3D speaker positioning system for virtual sound stage creation.
    Handles speaker placement, distance calculations, and soundstage visualization.
    """
    
    SONIC_SPEAKER_DEFAULTS = {
        'front_left_tweeter': {
            'x': 12.0,
            'y': 8.0,
            'z': 24.0,
            'angle_horizontal': 45,
            'angle_vertical': 0
        },
        'front_right_tweeter': {
            'x': 12.0,
            'y': 47.0,
            'z': 24.0,
            'angle_horizontal': -45,
            'angle_vertical': 0
        },
        'front_left_mid': {
            'x': 18.0,
            'y': 6.0,
            'z': 18.0,
            'angle_horizontal': 40,
            'angle_vertical': 10
        },
        'front_right_mid': {
            'x': 18.0,
            'y': 49.0,
            'z': 18.0,
            'angle_horizontal': -40,
            'angle_vertical': 10
        },
        'rear_left': {
            'x': 50.0,
            'y': 6.0,
            'z': 20.0,
            'angle_horizontal': 135,
            'angle_vertical': 0
        },
        'rear_right': {
            'x': 50.0,
            'y': 49.0,
            'z': 20.0,
            'angle_horizontal': -135,
            'angle_vertical': 0
        },
        'subwoofer': {
            'x': 60.0,
            'y': 27.5,
            'z': 10.0,
            'angle_horizontal': 180,
            'angle_vertical': -20
        }
    }
    
    LISTENING_POSITIONS = {
        'driver': {'x': 32.0, 'y': 12.0, 'z': 20.0},
        'passenger': {'x': 32.0, 'y': 43.0, 'z': 20.0},
        'rear_left': {'x': 48.0, 'y': 12.0, 'z': 18.0},
        'rear_right': {'x': 48.0, 'y': 43.0, 'z': 18.0},
        'center': {'x': 32.0, 'y': 27.5, 'z': 20.0}
    }
    
    SPEED_OF_SOUND_INCHES_PER_MS = 13.5
    
    def __init__(self):
        self.speaker_positions = self.SONIC_SPEAKER_DEFAULTS.copy()
        self.listening_positions = self.LISTENING_POSITIONS.copy()
    
    def set_speaker_position(
        self,
        speaker_name: str,
        x: float,
        y: float,
        z: float,
        angle_horizontal: Optional[float] = None,
        angle_vertical: Optional[float] = None
    ):
        """Set or update a speaker's 3D position."""
        if speaker_name not in self.speaker_positions:
            self.speaker_positions[speaker_name] = {}
        
        self.speaker_positions[speaker_name]['x'] = x
        self.speaker_positions[speaker_name]['y'] = y
        self.speaker_positions[speaker_name]['z'] = z
        
        if angle_horizontal is not None:
            self.speaker_positions[speaker_name]['angle_horizontal'] = angle_horizontal
        if angle_vertical is not None:
            self.speaker_positions[speaker_name]['angle_vertical'] = angle_vertical
    
    def calculate_distance(
        self,
        speaker_name: str,
        listening_position: str = 'driver'
    ) -> float:
        """Calculate distance from speaker to listening position in inches."""
        if speaker_name not in self.speaker_positions:
            raise ValueError(f"Unknown speaker: {speaker_name}")
        if listening_position not in self.listening_positions:
            raise ValueError(f"Unknown listening position: {listening_position}")
        
        speaker = self.speaker_positions[speaker_name]
        listener = self.listening_positions[listening_position]
        
        distance = math.sqrt(
            (speaker['x'] - listener['x'])**2 +
            (speaker['y'] - listener['y'])**2 +
            (speaker['z'] - listener['z'])**2
        )
        
        return distance
    
    def calculate_all_distances(
        self,
        listening_position: str = 'driver'
    ) -> Dict[str, float]:
        """Calculate distances from all speakers to listening position."""
        distances = {}
        
        for speaker_name in self.speaker_positions:
            distances[speaker_name] = self.calculate_distance(speaker_name, listening_position)
        
        return distances
    
    def calculate_time_delays(
        self,
        listening_position: str = 'driver',
        reference_speaker: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate time delays needed for time alignment.
        Delays are relative to the furthest speaker (or reference speaker).
        """
        distances = self.calculate_all_distances(listening_position)
        
        if reference_speaker and reference_speaker in distances:
            max_distance = distances[reference_speaker]
        else:
            max_distance = max(distances.values())
        
        delays = {}
        for speaker_name, distance in distances.items():
            delay_ms = (max_distance - distance) / self.SPEED_OF_SOUND_INCHES_PER_MS
            delays[speaker_name] = max(0, delay_ms)
        
        return delays
    
    def calculate_azimuth(
        self,
        speaker_name: str,
        listening_position: str = 'driver'
    ) -> float:
        """Calculate azimuth angle from listener to speaker (0° = front, ±180° = rear)."""
        speaker = self.speaker_positions[speaker_name]
        listener = self.listening_positions[listening_position]
        
        dx = speaker['x'] - listener['x']
        dy = speaker['y'] - listener['y']
        
        azimuth = math.degrees(math.atan2(dy - 27.5, dx))
        
        return azimuth
    
    def calculate_elevation(
        self,
        speaker_name: str,
        listening_position: str = 'driver'
    ) -> float:
        """Calculate elevation angle from listener to speaker."""
        speaker = self.speaker_positions[speaker_name]
        listener = self.listening_positions[listening_position]
        
        dz = speaker['z'] - listener['z']
        horizontal_distance = math.sqrt(
            (speaker['x'] - listener['x'])**2 +
            (speaker['y'] - listener['y'])**2
        )
        
        elevation = math.degrees(math.atan2(dz, horizontal_distance))
        
        return elevation
    
    def calculate_balance_correction(
        self,
        listening_position: str = 'driver'
    ) -> Dict[str, float]:
        """
        Calculate left/right balance corrections based on listening position.
        Returns gain adjustments in dB for each speaker.
        """
        corrections = {}
        listener = self.listening_positions[listening_position]
        
        for speaker_name, speaker in self.speaker_positions.items():
            if 'left' in speaker_name.lower():
                offset = abs(speaker['y'] - listener['y'])
                corrections[speaker_name] = -0.1 * (offset / 10.0)
            elif 'right' in speaker_name.lower():
                offset = abs(speaker['y'] - listener['y'])
                corrections[speaker_name] = -0.1 * (offset / 10.0)
            else:
                corrections[speaker_name] = 0.0
        
        max_correction = max(abs(v) for v in corrections.values())
        for speaker in corrections:
            corrections[speaker] += max_correction
        
        return corrections
    
    def calculate_fader_settings(
        self,
        listening_position: str = 'driver'
    ) -> Dict[str, Any]:
        """Calculate optimal front/rear fader settings."""
        listener = self.listening_positions[listening_position]
        
        front_speakers = [s for s in self.speaker_positions if 'front' in s.lower()]
        rear_speakers = [s for s in self.speaker_positions if 'rear' in s.lower()]
        
        avg_front_distance = sum(
            self.calculate_distance(s, listening_position) for s in front_speakers
        ) / len(front_speakers) if front_speakers else 0
        
        avg_rear_distance = sum(
            self.calculate_distance(s, listening_position) for s in rear_speakers
        ) / len(rear_speakers) if rear_speakers else 0
        
        if avg_front_distance > 0 and avg_rear_distance > 0:
            ratio = avg_front_distance / avg_rear_distance
            fader_db = 6.0 * (1.0 - ratio)
        else:
            fader_db = 0.0
        
        if listener['x'] < 40:
            fader_position = 'front'
            fader_value = max(-10, min(10, fader_db))
        else:
            fader_position = 'rear'
            fader_value = max(-10, min(10, -fader_db))
        
        return {
            'fader_position': fader_position,
            'fader_db': fader_value,
            'front_distance_avg': avg_front_distance,
            'rear_distance_avg': avg_rear_distance,
            'recommended_setting': f"{abs(fader_value):.1f} dB toward {fader_position}"
        }
    
    def calculate_center_image(
        self,
        listening_position: str = 'driver'
    ) -> Dict[str, Any]:
        """Calculate settings for optimal center image and vocal clarity."""
        left_speakers = [s for s in self.speaker_positions if 'left' in s.lower() and 'front' in s.lower()]
        right_speakers = [s for s in self.speaker_positions if 'right' in s.lower() and 'front' in s.lower()]
        
        if not left_speakers or not right_speakers:
            return {
                'balance_offset_db': 0.0,
                'time_offset_ms': 0.0,
                'quality_score': 0.0
            }
        
        left_distances = [self.calculate_distance(s, listening_position) for s in left_speakers]
        right_distances = [self.calculate_distance(s, listening_position) for s in right_speakers]
        
        avg_left = sum(left_distances) / len(left_distances)
        avg_right = sum(right_distances) / len(right_distances)
        
        distance_diff = avg_right - avg_left
        time_offset_ms = distance_diff / self.SPEED_OF_SOUND_INCHES_PER_MS
        
        balance_offset_db = 0.5 * (distance_diff / 10.0)
        
        listener = self.listening_positions[listening_position]
        center_offset = abs(listener['y'] - 27.5)
        quality_score = max(0, 100 - (center_offset * 2))
        
        return {
            'balance_offset_db': balance_offset_db,
            'time_offset_ms': time_offset_ms,
            'quality_score': quality_score,
            'left_distance_avg': avg_left,
            'right_distance_avg': avg_right,
            'recommendation': 'Apply balance offset for centered vocal image'
        }
    
    def create_soundstage_visualization(
        self,
        listening_position: str = 'driver'
    ) -> Dict[str, Any]:
        """Create data structure for 3D soundstage visualization."""
        listener = self.listening_positions[listening_position]
        
        speakers_viz = []
        for name, pos in self.speaker_positions.items():
            distance = self.calculate_distance(name, listening_position)
            azimuth = self.calculate_azimuth(name, listening_position)
            elevation = self.calculate_elevation(name, listening_position)
            
            speakers_viz.append({
                'name': name,
                'position': {'x': pos['x'], 'y': pos['y'], 'z': pos['z']},
                'distance_inches': distance,
                'azimuth_deg': azimuth,
                'elevation_deg': elevation,
                'angle_horizontal': pos.get('angle_horizontal', 0),
                'angle_vertical': pos.get('angle_vertical', 0)
            })
        
        return {
            'listener_position': listener,
            'speakers': speakers_viz,
            'cabin_dimensions': {
                'length': 68.0,
                'width': 55.0,
                'height': 38.0
            }
        }
    
    def get_preset_positions(self, preset_name: str) -> Dict[str, Any]:
        """Get predefined speaker position presets."""
        presets = {
            'sonic_ltz_default': self.SONIC_SPEAKER_DEFAULTS,
            'competition_front_stage': {
                **self.SONIC_SPEAKER_DEFAULTS,
                'front_left_tweeter': {
                    'x': 14.0,
                    'y': 10.0,
                    'z': 26.0,
                    'angle_horizontal': 50,
                    'angle_vertical': -5
                },
                'front_right_tweeter': {
                    'x': 14.0,
                    'y': 45.0,
                    'z': 26.0,
                    'angle_horizontal': -50,
                    'angle_vertical': -5
                }
            },
            'all_seats_balanced': {
                **self.SONIC_SPEAKER_DEFAULTS,
                'front_left_tweeter': {
                    **self.SONIC_SPEAKER_DEFAULTS['front_left_tweeter'],
                    'angle_horizontal': 30
                },
                'front_right_tweeter': {
                    **self.SONIC_SPEAKER_DEFAULTS['front_right_tweeter'],
                    'angle_horizontal': -30
                }
            }
        }
        
        return presets.get(preset_name, self.SONIC_SPEAKER_DEFAULTS)
    
    def export_to_dsp(
        self,
        listening_position: str = 'driver'
    ) -> Dict[str, Any]:
        """Export positioning data in format compatible with DSP service."""
        delays = self.calculate_time_delays(listening_position)
        balance = self.calculate_balance_correction(listening_position)
        fader = self.calculate_fader_settings(listening_position)
        center = self.calculate_center_image(listening_position)
        
        return {
            'time_delays_ms': delays,
            'balance_corrections_db': balance,
            'fader_settings': fader,
            'center_image_settings': center,
            'listening_position': listening_position
        }
