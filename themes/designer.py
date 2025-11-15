#!/usr/bin/env python3
"""
Theme Designer Logic
Handles theme creation, customization, and export/import
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


class ThemeDesigner:
    """Theme designer and customization engine."""
    
    BUTTON_STYLES = ['rounded', 'sharp', 'pill', 'minimal']
    ICON_STYLES = ['modern', 'minimal', 'classic', 'neon', 'outline']
    FONT_FAMILIES = [
        'Roboto', 'Roboto Medium', 'Roboto Mono', 'Roboto Condensed',
        'Open Sans', 'Lato', 'Montserrat', 'Poppins', 'Ubuntu'
    ]
    ANIMATION_SPEEDS = ['slow', 'normal', 'fast', 'instant']
    TRANSITION_EFFECTS = ['fade', 'slide', 'zoom', 'flip', 'none']
    
    SONIC_COLORS = {
        'Sonic Blue': '#0d47a1',
        'Sonic Gray': '#455a64',
        'Sonic Black': '#212121',
        'Sonic White': '#fafafa',
        'Dashboard Blue': '#1565c0',
        'Interior Accent': '#64b5f6'
    }
    
    def __init__(self):
        """Initialize theme designer."""
        self.current_theme = None
    
    def validate_color(self, color: str) -> bool:
        """Validate hex color format."""
        if not color:
            return False
        
        if not color.startswith('#'):
            return False
        
        color = color[1:]
        if len(color) not in [3, 6, 8]:
            return False
        
        try:
            int(color, 16)
            return True
        except ValueError:
            return False
    
    def validate_theme_data(self, theme_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate theme data."""
        required_fields = ['theme_name', 'primary_color', 'secondary_color', 'accent_color']
        
        for field in required_fields:
            if field not in theme_data:
                return False, f"Missing required field: {field}"
        
        color_fields = [
            'primary_color', 'secondary_color', 'accent_color',
            'background_color', 'surface_color', 'text_color',
            'nav_bar_color', 'status_bar_color'
        ]
        
        for field in color_fields:
            if field in theme_data and theme_data[field]:
                if not self.validate_color(theme_data[field]):
                    return False, f"Invalid color format for {field}: {theme_data[field]}"
        
        if 'button_style' in theme_data and theme_data['button_style'] not in self.BUTTON_STYLES:
            return False, f"Invalid button style. Must be one of: {', '.join(self.BUTTON_STYLES)}"
        
        if 'icon_style' in theme_data and theme_data['icon_style'] not in self.ICON_STYLES:
            return False, f"Invalid icon style. Must be one of: {', '.join(self.ICON_STYLES)}"
        
        if 'font_family' in theme_data and theme_data['font_family'] not in self.FONT_FAMILIES:
            return False, f"Invalid font family. Must be one of: {', '.join(self.FONT_FAMILIES)}"
        
        if 'animation_speed' in theme_data and theme_data['animation_speed'] not in self.ANIMATION_SPEEDS:
            return False, f"Invalid animation speed. Must be one of: {', '.join(self.ANIMATION_SPEEDS)}"
        
        if 'transition_effect' in theme_data and theme_data['transition_effect'] not in self.TRANSITION_EFFECTS:
            return False, f"Invalid transition effect. Must be one of: {', '.join(self.TRANSITION_EFFECTS)}"
        
        return True, None
    
    def create_theme_from_template(self, template_name: str, custom_name: str) -> Dict[str, Any]:
        """Create a custom theme based on a template."""
        templates = {
            'Modern Dark': {
                'mode': 'dark',
                'primary_color': '#1a1a1a',
                'secondary_color': '#2d2d2d',
                'accent_color': '#00b8d4',
                'background_color': '#121212',
                'surface_color': '#1e1e1e',
                'text_color': '#ffffff',
                'nav_bar_color': '#1a1a1a',
                'status_bar_color': '#000000'
            },
            'Light Minimal': {
                'mode': 'light',
                'primary_color': '#ffffff',
                'secondary_color': '#f5f5f5',
                'accent_color': '#2196f3',
                'background_color': '#fafafa',
                'surface_color': '#ffffff',
                'text_color': '#212121',
                'nav_bar_color': '#ffffff',
                'status_bar_color': '#f5f5f5'
            },
            'Sonic Blue': {
                'mode': 'dark',
                'primary_color': '#0d47a1',
                'secondary_color': '#1565c0',
                'accent_color': '#64b5f6',
                'background_color': '#0a1929',
                'surface_color': '#1a2332',
                'text_color': '#e3f2fd',
                'nav_bar_color': '#0d47a1',
                'status_bar_color': '#0a1929'
            }
        }
        
        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        theme = templates[template_name].copy()
        theme['theme_name'] = custom_name
        theme['theme_type'] = 'custom'
        theme['button_style'] = 'rounded'
        theme['icon_style'] = 'modern'
        theme['font_family'] = 'Roboto'
        theme['animation_speed'] = 'normal'
        theme['transition_effect'] = 'fade'
        
        return theme
    
    def apply_sonic_colors(self, theme_data: Dict[str, Any], color_scheme: str = 'blue') -> Dict[str, Any]:
        """Apply Sonic interior color scheme to theme."""
        if color_scheme == 'blue':
            theme_data['primary_color'] = self.SONIC_COLORS['Sonic Blue']
            theme_data['secondary_color'] = self.SONIC_COLORS['Dashboard Blue']
            theme_data['accent_color'] = self.SONIC_COLORS['Interior Accent']
            theme_data['mode'] = 'dark'
        elif color_scheme == 'gray':
            theme_data['primary_color'] = self.SONIC_COLORS['Sonic Gray']
            theme_data['secondary_color'] = self.SONIC_COLORS['Sonic Black']
            theme_data['accent_color'] = self.SONIC_COLORS['Dashboard Blue']
            theme_data['mode'] = 'dark'
        
        return theme_data
    
    def export_theme(self, theme_data: Dict[str, Any]) -> str:
        """Export theme as JSON string."""
        export_data = {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'theme': {
                k: v for k, v in theme_data.items()
                if k not in ['id', 'created_at', 'updated_at', 'is_template', 'is_active']
            }
        }
        
        return json.dumps(export_data, indent=2)
    
    def import_theme(self, json_data: str) -> Dict[str, Any]:
        """Import theme from JSON string."""
        try:
            data = json.loads(json_data)
            
            if 'theme' not in data:
                raise ValueError("Invalid theme format: missing 'theme' key")
            
            theme = data['theme']
            
            valid, error = self.validate_theme_data(theme)
            if not valid:
                raise ValueError(f"Invalid theme data: {error}")
            
            theme['theme_type'] = 'custom'
            theme['is_template'] = 0
            theme['is_active'] = 0
            
            return theme
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
    
    def generate_preview_css(self, theme_data: Dict[str, Any]) -> str:
        """Generate CSS for theme preview."""
        css = f"""
:root {{
    --primary-color: {theme_data.get('primary_color', '#1a1a1a')};
    --secondary-color: {theme_data.get('secondary_color', '#2d2d2d')};
    --accent-color: {theme_data.get('accent_color', '#00b8d4')};
    --background-color: {theme_data.get('background_color', '#121212')};
    --surface-color: {theme_data.get('surface_color', '#1e1e1e')};
    --text-color: {theme_data.get('text_color', '#ffffff')};
    --nav-bar-color: {theme_data.get('nav_bar_color', '#1a1a1a')};
    --status-bar-color: {theme_data.get('status_bar_color', '#000000')};
}}

body {{
    background-color: var(--background-color);
    color: var(--text-color);
    font-family: {theme_data.get('font_family', 'Roboto')}, sans-serif;
}}

.preview-nav-bar {{
    background-color: var(--nav-bar-color);
}}

.preview-status-bar {{
    background-color: var(--status-bar-color);
}}

.preview-surface {{
    background-color: var(--surface-color);
}}

.preview-button {{
    background-color: var(--accent-color);
    color: var(--text-color);
    border-radius: {self._get_button_radius(theme_data.get('button_style', 'rounded'))};
}}

.preview-icon {{
    color: var(--accent-color);
}}
"""
        return css
    
    def _get_button_radius(self, style: str) -> str:
        """Get border radius for button style."""
        radius_map = {
            'rounded': '8px',
            'sharp': '0px',
            'pill': '24px',
            'minimal': '4px'
        }
        return radius_map.get(style, '8px')
    
    def get_android_auto_config(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Android Auto configuration from theme."""
        return {
            'day_night_mode': 'auto' if theme_data.get('mode') == 'dark' else 'day',
            'colors': {
                'primary': theme_data.get('primary_color'),
                'primaryDark': theme_data.get('status_bar_color'),
                'accent': theme_data.get('accent_color'),
                'background': theme_data.get('background_color'),
                'surface': theme_data.get('surface_color'),
                'onPrimary': theme_data.get('text_color'),
                'onBackground': theme_data.get('text_color')
            },
            'typography': {
                'fontFamily': theme_data.get('font_family', 'Roboto')
            },
            'shapes': {
                'button': theme_data.get('button_style', 'rounded'),
                'card': 'rounded'
            },
            'animations': {
                'speed': theme_data.get('animation_speed', 'normal'),
                'transitionType': theme_data.get('transition_effect', 'fade')
            }
        }
    
    def compare_themes(self, theme1: Dict[str, Any], theme2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two themes and return differences."""
        differences = {}
        
        compare_fields = [
            'mode', 'primary_color', 'secondary_color', 'accent_color',
            'background_color', 'surface_color', 'text_color',
            'nav_bar_color', 'status_bar_color', 'button_style',
            'icon_style', 'font_family', 'animation_speed', 'transition_effect'
        ]
        
        for field in compare_fields:
            val1 = theme1.get(field)
            val2 = theme2.get(field)
            
            if val1 != val2:
                differences[field] = {
                    'theme1': val1,
                    'theme2': val2
                }
        
        return differences
    
    def get_available_options(self) -> Dict[str, List[str]]:
        """Get all available customization options."""
        return {
            'button_styles': self.BUTTON_STYLES,
            'icon_styles': self.ICON_STYLES,
            'font_families': self.FONT_FAMILIES,
            'animation_speeds': self.ANIMATION_SPEEDS,
            'transition_effects': self.TRANSITION_EFFECTS,
            'sonic_colors': self.SONIC_COLORS
        }
