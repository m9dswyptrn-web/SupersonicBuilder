import math
from typing import Dict, List, Tuple, Any


class CabinAcoustics:
    """
    Acoustic modeling for 2014 Chevy Sonic cabin.
    Handles cabin dimensions, material properties, and acoustic calculations.
    """
    
    SONIC_CABIN_DIMENSIONS = {
        'length_inches': 68.0,
        'width_inches': 55.0,
        'height_inches': 38.0,
        'volume_cubic_ft': 82.0
    }
    
    MATERIAL_ABSORPTION_COEFFICIENTS = {
        'carpet': {
            '125Hz': 0.08,
            '250Hz': 0.24,
            '500Hz': 0.57,
            '1000Hz': 0.69,
            '2000Hz': 0.71,
            '4000Hz': 0.73
        },
        'plastic_trim': {
            '125Hz': 0.05,
            '250Hz': 0.06,
            '500Hz': 0.07,
            '1000Hz': 0.09,
            '2000Hz': 0.08,
            '4000Hz': 0.10
        },
        'glass': {
            '125Hz': 0.35,
            '250Hz': 0.25,
            '500Hz': 0.18,
            '1000Hz': 0.12,
            '2000Hz': 0.07,
            '4000Hz': 0.04
        },
        'metal_door': {
            '125Hz': 0.15,
            '250Hz': 0.10,
            '500Hz': 0.06,
            '1000Hz': 0.05,
            '2000Hz': 0.05,
            '4000Hz': 0.03
        },
        'headliner': {
            '125Hz': 0.10,
            '250Hz': 0.25,
            '500Hz': 0.45,
            '1000Hz': 0.65,
            '2000Hz': 0.70,
            '4000Hz': 0.75
        },
        'seat_fabric': {
            '125Hz': 0.20,
            '250Hz': 0.40,
            '500Hz': 0.60,
            '1000Hz': 0.70,
            '2000Hz': 0.75,
            '4000Hz': 0.80
        }
    }
    
    SONIC_MATERIAL_DISTRIBUTION = {
        'carpet': 0.15,
        'plastic_trim': 0.30,
        'glass': 0.20,
        'metal_door': 0.15,
        'headliner': 0.10,
        'seat_fabric': 0.10
    }
    
    SPEED_OF_SOUND_INCHES_PER_MS = 13.5
    
    def __init__(self):
        self.dimensions = self.SONIC_CABIN_DIMENSIONS.copy()
        self.materials = self.MATERIAL_ABSORPTION_COEFFICIENTS.copy()
        self.distribution = self.SONIC_MATERIAL_DISTRIBUTION.copy()
    
    def calculate_room_modes(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Calculate standing wave frequencies (room modes) for the cabin.
        Uses length, width, and height to find modal frequencies.
        """
        length = self.dimensions['length_inches']
        width = self.dimensions['width_inches']
        height = self.dimensions['height_inches']
        
        speed_of_sound = 13503.9
        
        modes = {
            'axial': [],
            'tangential': [],
            'oblique': []
        }
        
        for n in range(1, 6):
            modes['axial'].append({
                'mode': f'Length {n}',
                'frequency_hz': (n * speed_of_sound) / (2 * length),
                'dimension': 'length',
                'order': n
            })
            modes['axial'].append({
                'mode': f'Width {n}',
                'frequency_hz': (n * speed_of_sound) / (2 * width),
                'dimension': 'width',
                'order': n
            })
            modes['axial'].append({
                'mode': f'Height {n}',
                'frequency_hz': (n * speed_of_sound) / (2 * height),
                'dimension': 'height',
                'order': n
            })
        
        for nx in range(1, 4):
            for ny in range(1, 4):
                freq = speed_of_sound * math.sqrt((nx/length)**2 + (ny/width)**2) / 2
                if freq < 500:
                    modes['tangential'].append({
                        'mode': f'LW {nx},{ny}',
                        'frequency_hz': freq,
                        'dimensions': 'length-width',
                        'order': (nx, ny)
                    })
        
        for nx in range(1, 3):
            for ny in range(1, 3):
                for nz in range(1, 3):
                    freq = speed_of_sound * math.sqrt(
                        (nx/length)**2 + (ny/width)**2 + (nz/height)**2
                    ) / 2
                    if freq < 500:
                        modes['oblique'].append({
                            'mode': f'LWH {nx},{ny},{nz}',
                            'frequency_hz': freq,
                            'dimensions': 'length-width-height',
                            'order': (nx, ny, nz)
                        })
        
        for mode_type in modes:
            modes[mode_type] = sorted(modes[mode_type], key=lambda x: x['frequency_hz'])
        
        return modes
    
    def calculate_rt60(self, frequency_band: str = '1000Hz') -> float:
        """
        Calculate RT60 (reverberation time) for the cabin at a given frequency.
        RT60 is the time it takes for sound to decay by 60dB.
        """
        volume_m3 = self.dimensions['volume_cubic_ft'] * 0.0283168
        
        total_absorption = 0.0
        for material, proportion in self.distribution.items():
            absorption_coef = self.materials[material].get(frequency_band, 0.1)
            total_absorption += absorption_coef * proportion
        
        surface_area_m2 = 2 * (
            (self.dimensions['length_inches'] * self.dimensions['width_inches']) +
            (self.dimensions['width_inches'] * self.dimensions['height_inches']) +
            (self.dimensions['height_inches'] * self.dimensions['length_inches'])
        ) * 0.00064516
        
        sabine_absorption = total_absorption * surface_area_m2
        
        if sabine_absorption > 0:
            rt60 = 0.161 * volume_m3 / sabine_absorption
        else:
            rt60 = 1.0
        
        return rt60
    
    def calculate_absorption_spectrum(self) -> Dict[str, float]:
        """Calculate weighted absorption coefficients across frequency bands."""
        spectrum = {}
        
        for freq_band in ['125Hz', '250Hz', '500Hz', '1000Hz', '2000Hz', '4000Hz']:
            total_absorption = 0.0
            for material, proportion in self.distribution.items():
                absorption_coef = self.materials[material][freq_band]
                total_absorption += absorption_coef * proportion
            
            spectrum[freq_band] = total_absorption
        
        return spectrum
    
    def recommend_eq_correction(self) -> List[Dict[str, Any]]:
        """
        Recommend EQ corrections based on cabin acoustics.
        Addresses room modes and material absorption characteristics.
        """
        modes = self.calculate_room_modes()
        absorption = self.calculate_absorption_spectrum()
        
        corrections = []
        
        for mode in modes['axial'][:6]:
            freq = mode['frequency_hz']
            if 20 <= freq <= 200:
                corrections.append({
                    'frequency_hz': freq,
                    'gain_db': -3.0,
                    'q_factor': 4.0,
                    'reason': f"Room mode: {mode['mode']}",
                    'type': 'parametric_cut'
                })
        
        if absorption.get('125Hz', 0) < 0.15:
            corrections.append({
                'frequency_hz': 100,
                'gain_db': 2.0,
                'q_factor': 0.7,
                'reason': 'Low bass absorption in cabin',
                'type': 'low_shelf'
            })
        
        if absorption.get('4000Hz', 0) > 0.3:
            corrections.append({
                'frequency_hz': 8000,
                'gain_db': 2.5,
                'q_factor': 0.7,
                'reason': 'High treble absorption from materials',
                'type': 'high_shelf'
            })
        
        return corrections
    
    def calculate_early_reflections(
        self,
        speaker_position: Tuple[float, float, float],
        listener_position: Tuple[float, float, float]
    ) -> List[Dict[str, Any]]:
        """
        Calculate early reflection paths from speaker to listener.
        Returns reflection points and delays.
        """
        reflections = []
        
        surfaces = [
            {'name': 'floor', 'axis': 2, 'value': 0},
            {'name': 'ceiling', 'axis': 2, 'value': self.dimensions['height_inches']},
            {'name': 'left_door', 'axis': 1, 'value': 0},
            {'name': 'right_door', 'axis': 1, 'value': self.dimensions['width_inches']},
            {'name': 'dashboard', 'axis': 0, 'value': 0},
            {'name': 'rear', 'axis': 0, 'value': self.dimensions['length_inches']}
        ]
        
        direct_distance = math.sqrt(
            (speaker_position[0] - listener_position[0])**2 +
            (speaker_position[1] - listener_position[1])**2 +
            (speaker_position[2] - listener_position[2])**2
        )
        
        for surface in surfaces:
            axis = surface['axis']
            surface_val = surface['value']
            
            mirror_speaker = list(speaker_position)
            mirror_speaker[axis] = 2 * surface_val - speaker_position[axis]
            
            reflection_distance = math.sqrt(
                (mirror_speaker[0] - listener_position[0])**2 +
                (mirror_speaker[1] - listener_position[1])**2 +
                (mirror_speaker[2] - listener_position[2])**2
            )
            
            delay_ms = (reflection_distance - direct_distance) / self.SPEED_OF_SOUND_INCHES_PER_MS
            
            material = 'floor' if 'floor' in surface['name'] else \
                      'ceiling' if 'ceiling' in surface['name'] else \
                      'glass' if 'door' in surface['name'] else 'plastic_trim'
            
            reflections.append({
                'surface': surface['name'],
                'delay_ms': delay_ms,
                'path_length_inches': reflection_distance,
                'material': material,
                'attenuation_db': -2.0
            })
        
        reflections.sort(key=lambda x: x['delay_ms'])
        
        return reflections[:5]
    
    def get_cabin_info(self) -> Dict[str, Any]:
        """Get complete cabin acoustic information."""
        modes = self.calculate_room_modes()
        absorption = self.calculate_absorption_spectrum()
        rt60_values = {
            freq: self.calculate_rt60(freq)
            for freq in ['125Hz', '250Hz', '500Hz', '1000Hz', '2000Hz', '4000Hz']
        }
        
        return {
            'dimensions': self.dimensions,
            'room_modes': modes,
            'absorption_spectrum': absorption,
            'rt60_values': rt60_values,
            'material_distribution': self.distribution,
            'recommended_corrections': self.recommend_eq_correction()
        }
