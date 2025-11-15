#!/usr/bin/env python3
"""
Scene and Preset Manager
Manages lighting scenes and quick-access presets
"""

from typing import Dict, List, Optional
from .database import LightingDatabase


class SceneManager:
    """Manager for lighting scenes and presets."""
    
    def __init__(self, led_controller, db: LightingDatabase):
        """Initialize scene manager."""
        self.led_controller = led_controller
        self.db = db
        self.current_scene = None
        
        print("✓ Scene Manager initialized")
    
    def apply_scene(self, scene_name: str) -> bool:
        """Apply a saved scene."""
        scene = self.db.get_scene(scene_name)
        
        if not scene:
            return False
        
        zone_colors = scene['zone_colors']
        self.led_controller.set_all_colors(zone_colors)
        
        brightness = scene.get('brightness', 100)
        self.led_controller.set_global_brightness(brightness)
        
        self.current_scene = scene_name
        
        print(f"✓ Applied scene: {scene_name}")
        return True
    
    def save_current_as_scene(self, scene_name: str, description: str = '') -> bool:
        """Save current lighting state as a scene."""
        zone_colors = {}
        
        for zone_name, zone in self.led_controller.zones.items():
            zone_colors[zone_name] = zone.color
        
        brightness = self.led_controller.global_brightness
        
        scene_id = self.db.save_scene(
            scene_name=scene_name,
            description=description,
            zone_colors=zone_colors,
            mode='static',
            brightness=brightness,
            effect_intensity=0,
            is_favorite=False,
            is_builtin=False
        )
        
        print(f"✓ Saved scene: {scene_name} (ID: {scene_id})")
        return True
    
    def update_scene(self, scene_name: str, zone_colors: Dict, brightness: int,
                     mode: str = 'static', effect_intensity: int = 50) -> bool:
        """Update an existing scene."""
        scene = self.db.get_scene(scene_name)
        
        if not scene:
            return False
        
        if scene.get('is_builtin'):
            print(f"Cannot update built-in scene: {scene_name}")
            return False
        
        self.db.save_scene(
            scene_name=scene_name,
            description=scene.get('description', ''),
            zone_colors=zone_colors,
            mode=mode,
            brightness=brightness,
            effect_intensity=effect_intensity,
            is_favorite=scene.get('is_favorite', False),
            is_builtin=False,
            update_if_exists=True
        )
        
        print(f"✓ Updated scene: {scene_name}")
        return True
    
    def delete_scene(self, scene_name: str) -> bool:
        """Delete a custom scene."""
        success = self.db.delete_scene(scene_name)
        
        if success:
            print(f"✓ Deleted scene: {scene_name}")
        else:
            print(f"Cannot delete scene: {scene_name} (may be built-in)")
        
        return success
    
    def set_favorite(self, scene_name: str, is_favorite: bool) -> bool:
        """Mark a scene as favorite."""
        success = self.db.set_favorite(scene_name, is_favorite)
        
        if success:
            status = "favorited" if is_favorite else "unfavorited"
            print(f"✓ Scene {status}: {scene_name}")
        
        return success
    
    def get_all_scenes(self) -> List[Dict]:
        """Get all available scenes."""
        return self.db.get_all_scenes()
    
    def get_favorite_scenes(self) -> List[Dict]:
        """Get all favorite scenes."""
        all_scenes = self.db.get_all_scenes()
        return [s for s in all_scenes if s.get('is_favorite')]
    
    def get_builtin_scenes(self) -> List[Dict]:
        """Get all built-in scenes."""
        all_scenes = self.db.get_all_scenes()
        return [s for s in all_scenes if s.get('is_builtin')]
    
    def get_custom_scenes(self) -> List[Dict]:
        """Get all custom scenes."""
        all_scenes = self.db.get_all_scenes()
        return [s for s in all_scenes if not s.get('is_builtin')]
    
    def quick_access_solid_color(self, color_name: str) -> bool:
        """Quick access to solid colors."""
        colors = {
            'red': {'r': 255, 'g': 0, 'b': 0},
            'green': {'r': 0, 'g': 255, 'b': 0},
            'blue': {'r': 0, 'g': 0, 'b': 255},
            'purple': {'r': 128, 'g': 0, 'b': 128},
            'white': {'r': 255, 'g': 255, 'b': 255},
            'orange': {'r': 255, 'g': 165, 'b': 0},
            'yellow': {'r': 255, 'g': 255, 'b': 0},
            'cyan': {'r': 0, 'g': 255, 'b': 255},
            'magenta': {'r': 255, 'g': 0, 'b': 255},
            'warm_white': {'r': 255, 'g': 200, 'b': 150}
        }
        
        if color_name not in colors:
            return False
        
        color = colors[color_name]
        
        zone_colors = {}
        for zone_name in self.led_controller.zones.keys():
            zone_colors[zone_name] = color
        
        self.led_controller.set_all_colors(zone_colors)
        self.current_scene = f"solid_{color_name}"
        
        return True
    
    def two_tone_theme(self, color1_name: str, color2_name: str) -> bool:
        """Apply a two-tone color theme."""
        colors = {
            'red': {'r': 255, 'g': 0, 'b': 0},
            'green': {'r': 0, 'g': 255, 'b': 0},
            'blue': {'r': 0, 'g': 0, 'b': 255},
            'purple': {'r': 128, 'g': 0, 'b': 128},
            'white': {'r': 255, 'g': 255, 'b': 255},
            'orange': {'r': 255, 'g': 165, 'b': 0},
            'yellow': {'r': 255, 'g': 255, 'b': 0},
            'cyan': {'r': 0, 'g': 255, 'b': 255}
        }
        
        if color1_name not in colors or color2_name not in colors:
            return False
        
        color1 = colors[color1_name]
        color2 = colors[color2_name]
        
        zone_names = list(self.led_controller.zones.keys())
        
        for i, zone_name in enumerate(zone_names):
            color = color1 if i % 2 == 0 else color2
            self.led_controller.set_zone_color(zone_name, color['r'], color['g'], color['b'])
        
        self.current_scene = f"two_tone_{color1_name}_{color2_name}"
        
        return True
    
    def rainbow_gradient(self) -> bool:
        """Apply rainbow gradient."""
        self.led_controller.set_rainbow_gradient()
        self.current_scene = "rainbow_gradient"
        return True
    
    def get_current_scene(self) -> Optional[str]:
        """Get currently applied scene."""
        return self.current_scene
    
    def get_stats(self) -> Dict:
        """Get scene manager statistics."""
        all_scenes = self.db.get_all_scenes()
        
        return {
            'total_scenes': len(all_scenes),
            'builtin_scenes': len([s for s in all_scenes if s.get('is_builtin')]),
            'custom_scenes': len([s for s in all_scenes if not s.get('is_builtin')]),
            'favorite_scenes': len([s for s in all_scenes if s.get('is_favorite')]),
            'current_scene': self.current_scene
        }
