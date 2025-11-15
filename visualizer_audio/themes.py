#!/usr/bin/env python3
"""
Theme Manager
Manage color schemes and visual themes for the audio visualizer
"""

from typing import Dict, List


class ThemeManager:
    """Manage visualizer themes and color schemes."""
    
    def __init__(self):
        """Initialize theme manager with built-in themes."""
        self.themes = self._create_builtin_themes()
        self.current_theme = 'dark'
    
    def _create_builtin_themes(self) -> Dict[str, Dict]:
        """Create built-in color themes."""
        return {
            'dark': {
                'name': 'Dark Mode',
                'description': 'Classic dark theme with vibrant colors',
                'background': '#0a0a0a',
                'primary': '#1a1a1a',
                'secondary': '#2a2a2a',
                'text': '#ffffff',
                'accent': '#00ff88',
                'spectrum': {
                    'type': 'gradient',
                    'colors': ['#00ffff', '#00ff88', '#88ff00', '#ffff00', '#ff8800', '#ff0000'],
                    'positions': [0, 0.2, 0.4, 0.6, 0.8, 1.0]
                },
                'waveform': '#00ff88',
                'beat_flash': '#ffffff',
                'particle_colors': ['#00ffff', '#00ff88', '#88ff00'],
                'vu_meter': {
                    'normal': '#00ff88',
                    'warning': '#ffff00',
                    'peak': '#ff0000'
                }
            },
            
            'neon': {
                'name': 'Neon',
                'description': 'Bright neon colors inspired by cyberpunk aesthetics',
                'background': '#000000',
                'primary': '#0d0021',
                'secondary': '#1a0042',
                'text': '#ff00ff',
                'accent': '#00ffff',
                'spectrum': {
                    'type': 'gradient',
                    'colors': ['#ff00ff', '#ff00aa', '#ff0055', '#ff0000', '#ffaa00', '#ffff00'],
                    'positions': [0, 0.2, 0.4, 0.6, 0.8, 1.0]
                },
                'waveform': '#ff00ff',
                'beat_flash': '#00ffff',
                'particle_colors': ['#ff00ff', '#00ffff', '#ff0000'],
                'vu_meter': {
                    'normal': '#00ffff',
                    'warning': '#ff00aa',
                    'peak': '#ff00ff'
                }
            },
            
            'retro': {
                'name': 'Retro',
                'description': 'Vintage 80s aesthetic with warm colors',
                'background': '#1a0f0a',
                'primary': '#2a1a0f',
                'secondary': '#3a251a',
                'text': '#ffddaa',
                'accent': '#ff6600',
                'spectrum': {
                    'type': 'gradient',
                    'colors': ['#ff00aa', '#ff0066', '#ff6600', '#ffaa00', '#ffdd00', '#ffff88'],
                    'positions': [0, 0.2, 0.4, 0.6, 0.8, 1.0]
                },
                'waveform': '#ff6600',
                'beat_flash': '#ffff88',
                'particle_colors': ['#ff00aa', '#ff6600', '#ffdd00'],
                'vu_meter': {
                    'normal': '#ffaa00',
                    'warning': '#ff6600',
                    'peak': '#ff0066'
                }
            },
            
            'minimal': {
                'name': 'Minimal',
                'description': 'Clean, minimalist design with monochrome palette',
                'background': '#f5f5f5',
                'primary': '#ffffff',
                'secondary': '#e0e0e0',
                'text': '#333333',
                'accent': '#666666',
                'spectrum': {
                    'type': 'gradient',
                    'colors': ['#333333', '#555555', '#777777', '#999999', '#bbbbbb', '#dddddd'],
                    'positions': [0, 0.2, 0.4, 0.6, 0.8, 1.0]
                },
                'waveform': '#666666',
                'beat_flash': '#333333',
                'particle_colors': ['#333333', '#666666', '#999999'],
                'vu_meter': {
                    'normal': '#666666',
                    'warning': '#444444',
                    'peak': '#222222'
                }
            },
            
            'ocean': {
                'name': 'Ocean',
                'description': 'Cool ocean-inspired blues and teals',
                'background': '#001a2e',
                'primary': '#002a42',
                'secondary': '#003a56',
                'text': '#aaddff',
                'accent': '#00ddff',
                'spectrum': {
                    'type': 'gradient',
                    'colors': ['#000055', '#0055aa', '#00aaff', '#00ffff', '#aaffff', '#ffffff'],
                    'positions': [0, 0.2, 0.4, 0.6, 0.8, 1.0]
                },
                'waveform': '#00ddff',
                'beat_flash': '#ffffff',
                'particle_colors': ['#0055aa', '#00aaff', '#00ffff'],
                'vu_meter': {
                    'normal': '#00aaff',
                    'warning': '#00ffff',
                    'peak': '#aaffff'
                }
            },
            
            'fire': {
                'name': 'Fire',
                'description': 'Intense warm colors like flames',
                'background': '#1a0000',
                'primary': '#2a0a00',
                'secondary': '#3a1500',
                'text': '#ffddaa',
                'accent': '#ff4400',
                'spectrum': {
                    'type': 'gradient',
                    'colors': ['#440000', '#880000', '#cc2200', '#ff4400', '#ff8800', '#ffdd00'],
                    'positions': [0, 0.2, 0.4, 0.6, 0.8, 1.0]
                },
                'waveform': '#ff4400',
                'beat_flash': '#ffdd00',
                'particle_colors': ['#cc2200', '#ff4400', '#ff8800'],
                'vu_meter': {
                    'normal': '#ff8800',
                    'warning': '#ff4400',
                    'peak': '#cc2200'
                }
            }
        }
    
    def get_theme(self, theme_name: str) -> Dict:
        """Get theme by name."""
        return self.themes.get(theme_name, self.themes['dark'])
    
    def get_all_themes(self) -> List[Dict]:
        """Get all available themes."""
        return [
            {
                'id': theme_id,
                'name': theme_data['name'],
                'description': theme_data['description']
            }
            for theme_id, theme_data in self.themes.items()
        ]
    
    def add_custom_theme(self, theme_id: str, theme_data: Dict):
        """Add a custom theme."""
        self.themes[theme_id] = theme_data
    
    def set_current_theme(self, theme_name: str):
        """Set the current active theme."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_current_theme(self) -> Dict:
        """Get the currently active theme."""
        return self.themes[self.current_theme]
    
    def get_spectrum_color(self, theme_name: str, position: float) -> str:
        """
        Get spectrum color at a specific position (0-1) for a theme.
        
        Args:
            theme_name: Name of the theme
            position: Position in spectrum (0-1)
        
        Returns:
            Color hex string
        """
        theme = self.get_theme(theme_name)
        spectrum = theme['spectrum']
        
        if spectrum['type'] == 'gradient':
            colors = spectrum['colors']
            positions = spectrum['positions']
            
            for i in range(len(positions) - 1):
                if positions[i] <= position <= positions[i + 1]:
                    t = (position - positions[i]) / (positions[i + 1] - positions[i])
                    return self._interpolate_color(colors[i], colors[i + 1], t)
            
            return colors[-1]
        
        return theme['accent']
    
    def _interpolate_color(self, color1: str, color2: str, t: float) -> str:
        """Interpolate between two hex colors."""
        c1 = self._hex_to_rgb(color1)
        c2 = self._hex_to_rgb(color2)
        
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        
        return self._rgb_to_hex(r, g, b)
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        """Convert RGB to hex color."""
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def create_custom_gradient(self, colors: List[str], name: str = "Custom") -> Dict:
        """Create a custom gradient theme."""
        positions = [i / (len(colors) - 1) for i in range(len(colors))]
        
        return {
            'name': name,
            'description': 'Custom gradient theme',
            'background': '#0a0a0a',
            'primary': '#1a1a1a',
            'secondary': '#2a2a2a',
            'text': '#ffffff',
            'accent': colors[0],
            'spectrum': {
                'type': 'gradient',
                'colors': colors,
                'positions': positions
            },
            'waveform': colors[0],
            'beat_flash': '#ffffff',
            'particle_colors': colors[:3],
            'vu_meter': {
                'normal': colors[0],
                'warning': colors[len(colors)//2] if len(colors) > 1 else colors[0],
                'peak': colors[-1]
            }
        }
