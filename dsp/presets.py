#!/usr/bin/env python3
"""
DSP Preset Management
Save, load, and manage complete DSP configurations
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class PresetManager:
    """Manage DSP presets including EQ, crossover, time alignment, and bass settings."""
    
    def __init__(self, presets_dir: str = 'services/dsp/presets'):
        """Initialize preset manager."""
        self.presets_dir = presets_dir
        os.makedirs(presets_dir, exist_ok=True)
        
        self.builtin_presets = self._create_builtin_presets()
        
    def _create_builtin_presets(self) -> Dict:
        """Create built-in factory presets."""
        return {
            'flat': {
                'name': 'Flat / Reference',
                'description': 'Neutral reference sound with no coloration',
                'created': '2025-01-01',
                'author': 'Factory',
                'eq': {
                    'enabled': True,
                    'bands': [{
                        'frequency': freq,
                        'gain_db': 0.0,
                        'q_factor': 1.41
                    } for freq in [20, 25, 31, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]]
                },
                'crossover': {
                    'enabled': False,
                    'configuration': '2-way',
                    'frequency': 2500,
                    'slope_db': 24
                },
                'time_alignment': {
                    'enabled': False
                },
                'bass': {
                    'level_db': 0.0,
                    'subsonic_filter_hz': 20,
                    'boost_db': 0.0,
                    'phase_degrees': 0
                }
            },
            'rock': {
                'name': 'Rock',
                'description': 'Enhanced bass and treble for rock music',
                'created': '2025-01-01',
                'author': 'Factory',
                'eq': {
                    'enabled': True,
                    'bands': [
                        {'frequency': 20, 'gain_db': 5.0, 'q_factor': 1.41},
                        {'frequency': 31, 'gain_db': 4.0, 'q_factor': 1.41},
                        {'frequency': 63, 'gain_db': 2.0, 'q_factor': 1.41},
                        {'frequency': 125, 'gain_db': 0.0, 'q_factor': 1.41},
                        {'frequency': 250, 'gain_db': -1.0, 'q_factor': 1.41},
                        {'frequency': 500, 'gain_db': 0.0, 'q_factor': 1.41},
                        {'frequency': 1000, 'gain_db': 1.0, 'q_factor': 1.41},
                        {'frequency': 2000, 'gain_db': 2.0, 'q_factor': 1.41},
                        {'frequency': 4000, 'gain_db': 3.0, 'q_factor': 1.41},
                        {'frequency': 8000, 'gain_db': 4.0, 'q_factor': 1.41},
                        {'frequency': 16000, 'gain_db': 4.0, 'q_factor': 1.41}
                    ]
                },
                'bass': {
                    'level_db': 3.0,
                    'subsonic_filter_hz': 25,
                    'boost_db': 4.0,
                    'phase_degrees': 0
                }
            },
            'jazz': {
                'name': 'Jazz',
                'description': 'Natural midrange for jazz and acoustic music',
                'created': '2025-01-01',
                'author': 'Factory',
                'eq': {
                    'enabled': True,
                    'bands': [
                        {'frequency': 63, 'gain_db': 2.0, 'q_factor': 1.41},
                        {'frequency': 125, 'gain_db': 1.0, 'q_factor': 1.41},
                        {'frequency': 250, 'gain_db': 0.5, 'q_factor': 1.41},
                        {'frequency': 500, 'gain_db': 1.5, 'q_factor': 1.41},
                        {'frequency': 1000, 'gain_db': 2.0, 'q_factor': 1.41},
                        {'frequency': 2000, 'gain_db': 1.5, 'q_factor': 1.41},
                        {'frequency': 4000, 'gain_db': 0.5, 'q_factor': 1.41},
                        {'frequency': 8000, 'gain_db': 1.0, 'q_factor': 1.41},
                        {'frequency': 16000, 'gain_db': 2.0, 'q_factor': 1.41}
                    ]
                },
                'bass': {
                    'level_db': 0.0,
                    'subsonic_filter_hz': 30,
                    'boost_db': 1.0,
                    'phase_degrees': 0
                }
            },
            'classical': {
                'name': 'Classical',
                'description': 'Balanced for orchestral music',
                'created': '2025-01-01',
                'author': 'Factory',
                'eq': {
                    'enabled': True,
                    'bands': [
                        {'frequency': 63, 'gain_db': 1.0, 'q_factor': 1.41},
                        {'frequency': 125, 'gain_db': 0.5, 'q_factor': 1.41},
                        {'frequency': 250, 'gain_db': 0.0, 'q_factor': 1.41},
                        {'frequency': 500, 'gain_db': 1.0, 'q_factor': 1.41},
                        {'frequency': 1000, 'gain_db': 1.5, 'q_factor': 1.41},
                        {'frequency': 2000, 'gain_db': 1.0, 'q_factor': 1.41},
                        {'frequency': 4000, 'gain_db': 0.5, 'q_factor': 1.41},
                        {'frequency': 8000, 'gain_db': 1.0, 'q_factor': 1.41},
                        {'frequency': 16000, 'gain_db': 1.5, 'q_factor': 1.41}
                    ]
                }
            },
            'hip_hop': {
                'name': 'Hip-Hop',
                'description': 'Deep bass emphasis for hip-hop and EDM',
                'created': '2025-01-01',
                'author': 'Factory',
                'eq': {
                    'enabled': True,
                    'bands': [
                        {'frequency': 20, 'gain_db': 8.0, 'q_factor': 1.41},
                        {'frequency': 31, 'gain_db': 7.0, 'q_factor': 1.41},
                        {'frequency': 63, 'gain_db': 5.0, 'q_factor': 1.41},
                        {'frequency': 125, 'gain_db': 3.0, 'q_factor': 1.41},
                        {'frequency': 250, 'gain_db': 0.0, 'q_factor': 1.41},
                        {'frequency': 500, 'gain_db': -1.0, 'q_factor': 1.41},
                        {'frequency': 1000, 'gain_db': 0.0, 'q_factor': 1.41},
                        {'frequency': 2000, 'gain_db': 1.0, 'q_factor': 1.41},
                        {'frequency': 4000, 'gain_db': 2.0, 'q_factor': 1.41},
                        {'frequency': 8000, 'gain_db': 2.0, 'q_factor': 1.41}
                    ]
                },
                'bass': {
                    'level_db': 6.0,
                    'subsonic_filter_hz': 20,
                    'boost_db': 8.0,
                    'phase_degrees': 0
                }
            },
            'car_audio': {
                'name': 'Car Audio Optimized',
                'description': 'Optimized for Chevy Sonic cabin acoustics',
                'created': '2025-01-01',
                'author': 'Factory',
                'eq': {
                    'enabled': True,
                    'bands': [
                        {'frequency': 20, 'gain_db': 2.5, 'q_factor': 1.41},
                        {'frequency': 31, 'gain_db': 1.5, 'q_factor': 1.41},
                        {'frequency': 63, 'gain_db': 0.0, 'q_factor': 1.41},
                        {'frequency': 125, 'gain_db': 0.0, 'q_factor': 1.41},
                        {'frequency': 250, 'gain_db': 0.5, 'q_factor': 1.41},
                        {'frequency': 500, 'gain_db': 0.0, 'q_factor': 1.41},
                        {'frequency': 1000, 'gain_db': 1.0, 'q_factor': 1.41},
                        {'frequency': 2000, 'gain_db': 1.5, 'q_factor': 1.41},
                        {'frequency': 4000, 'gain_db': 2.0, 'q_factor': 1.41},
                        {'frequency': 8000, 'gain_db': 2.5, 'q_factor': 1.41},
                        {'frequency': 16000, 'gain_db': 2.0, 'q_factor': 1.41}
                    ]
                },
                'crossover': {
                    'enabled': True,
                    'configuration': '2-way',
                    'frequency': 2500,
                    'slope_db': 24,
                    'filter_type': 'linkwitz_riley'
                },
                'bass': {
                    'level_db': 3.0,
                    'subsonic_filter_hz': 25,
                    'boost_db': 3.0,
                    'phase_degrees': 0
                }
            }
        }
    
    def get_preset(self, preset_name: str) -> Optional[Dict]:
        """Get a preset by name (builtin or user-saved)."""
        if preset_name in self.builtin_presets:
            return self.builtin_presets[preset_name]
            
        preset_file = os.path.join(self.presets_dir, f"{preset_name}.json")
        if os.path.exists(preset_file):
            with open(preset_file, 'r') as f:
                return json.load(f)
                
        return None
    
    def list_presets(self) -> List[Dict]:
        """List all available presets."""
        presets = []
        
        for name, preset in self.builtin_presets.items():
            presets.append({
                'id': name,
                'name': preset['name'],
                'description': preset.get('description', ''),
                'type': 'builtin',
                'author': preset.get('author', 'Factory')
            })
            
        if os.path.exists(self.presets_dir):
            for filename in os.listdir(self.presets_dir):
                if filename.endswith('.json'):
                    preset_id = filename[:-5]
                    try:
                        with open(os.path.join(self.presets_dir, filename), 'r') as f:
                            preset = json.load(f)
                            presets.append({
                                'id': preset_id,
                                'name': preset.get('name', preset_id),
                                'description': preset.get('description', ''),
                                'type': 'user',
                                'author': preset.get('author', 'User'),
                                'created': preset.get('created', '')
                            })
                    except:
                        pass
                        
        return presets
    
    def save_preset(
        self,
        preset_id: str,
        preset_data: Dict,
        overwrite: bool = False
    ) -> Dict:
        """Save a user preset."""
        if preset_id in self.builtin_presets and not overwrite:
            return {
                'ok': False,
                'error': 'Cannot overwrite builtin preset'
            }
            
        preset_file = os.path.join(self.presets_dir, f"{preset_id}.json")
        
        if os.path.exists(preset_file) and not overwrite:
            return {
                'ok': False,
                'error': 'Preset already exists. Use overwrite=True to replace.'
            }
            
        preset_data['created'] = preset_data.get('created', datetime.now().isoformat())
        preset_data['modified'] = datetime.now().isoformat()
        
        with open(preset_file, 'w') as f:
            json.dump(preset_data, f, indent=2)
            
        return {
            'ok': True,
            'preset_id': preset_id,
            'file': preset_file
        }
    
    def delete_preset(self, preset_id: str) -> Dict:
        """Delete a user preset."""
        if preset_id in self.builtin_presets:
            return {
                'ok': False,
                'error': 'Cannot delete builtin preset'
            }
            
        preset_file = os.path.join(self.presets_dir, f"{preset_id}.json")
        
        if not os.path.exists(preset_file):
            return {
                'ok': False,
                'error': 'Preset not found'
            }
            
        os.remove(preset_file)
        
        return {
            'ok': True,
            'preset_id': preset_id
        }
    
    def export_preset(self, preset_name: str) -> Optional[str]:
        """Export preset as JSON string."""
        preset = self.get_preset(preset_name)
        if preset:
            return json.dumps(preset, indent=2)
        return None
    
    def import_preset(
        self,
        preset_json: str,
        preset_id: str = None
    ) -> Dict:
        """Import preset from JSON string."""
        try:
            preset_data = json.loads(preset_json)
            
            if preset_id is None:
                preset_id = preset_data.get('name', 'imported_preset').lower().replace(' ', '_')
                
            return self.save_preset(preset_id, preset_data)
        except json.JSONDecodeError as e:
            return {
                'ok': False,
                'error': f'Invalid JSON: {str(e)}'
            }
