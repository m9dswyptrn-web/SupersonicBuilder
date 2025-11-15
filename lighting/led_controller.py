#!/usr/bin/env python3
"""
LED Controller Module
Simulates WS2812B LED strip control and hardware interface
"""

import time
import threading
from typing import Dict, List, Tuple
from datetime import datetime


class LEDZone:
    """Represents a single LED zone."""
    
    def __init__(self, name: str, led_count: int):
        """Initialize LED zone."""
        self.name = name
        self.led_count = led_count
        self.color = {'r': 0, 'g': 0, 'b': 0}
        self.brightness = 100
        self.enabled = True
    
    def set_color(self, r: int, g: int, b: int):
        """Set zone color (0-255)."""
        self.color = {
            'r': max(0, min(255, r)),
            'g': max(0, min(255, g)),
            'b': max(0, min(255, b))
        }
    
    def set_brightness(self, brightness: int):
        """Set zone brightness (0-100)."""
        self.brightness = max(0, min(100, brightness))
    
    def get_actual_color(self) -> Dict[str, int]:
        """Get color adjusted for brightness."""
        if not self.enabled:
            return {'r': 0, 'g': 0, 'b': 0}
        
        factor = self.brightness / 100.0
        return {
            'r': int(self.color['r'] * factor),
            'g': int(self.color['g'] * factor),
            'b': int(self.color['b'] * factor)
        }
    
    def to_dict(self) -> Dict:
        """Convert zone to dictionary."""
        return {
            'name': self.name,
            'led_count': self.led_count,
            'color': self.color,
            'brightness': self.brightness,
            'enabled': self.enabled,
            'actual_color': self.get_actual_color()
        }


class LEDController:
    """Main LED controller for all zones."""
    
    def __init__(self):
        """Initialize LED controller with all zones."""
        self.zones = {
            'dashboard': LEDZone('Dashboard Underglow', 30),
            'footwell_driver': LEDZone('Footwell Driver', 20),
            'footwell_passenger': LEDZone('Footwell Passenger', 20),
            'door_left': LEDZone('Door Left', 25),
            'door_right': LEDZone('Door Right', 25),
            'cupholder': LEDZone('Cup Holder', 15),
            'trunk': LEDZone('Trunk', 40)
        }
        
        self.global_brightness = 100
        self.master_enabled = True
        self.auto_dim_enabled = False
        self.parking_brake_dim = False
        
        self.animation_active = False
        self.animation_thread = None
        self.animation_stop_flag = False
        
        self.hardware_type = 'WS2812B'
        self.pwm_frequency = 1000
        self.serial_connected = False
        
        print("✓ LED Controller initialized")
        print(f"  - Total zones: {len(self.zones)}")
        print(f"  - Total LEDs: {sum(z.led_count for z in self.zones.values())}")
    
    def set_zone_color(self, zone_name: str, r: int, g: int, b: int):
        """Set color for a specific zone."""
        if zone_name in self.zones:
            self.zones[zone_name].set_color(r, g, b)
            self._send_to_hardware(zone_name)
            return True
        return False
    
    def set_zone_brightness(self, zone_name: str, brightness: int):
        """Set brightness for a specific zone."""
        if zone_name in self.zones:
            self.zones[zone_name].set_brightness(brightness)
            self._send_to_hardware(zone_name)
            return True
        return False
    
    def set_all_colors(self, zone_colors: Dict[str, Dict[str, int]]):
        """Set colors for all zones."""
        for zone_name, color in zone_colors.items():
            if zone_name in self.zones:
                self.zones[zone_name].set_color(
                    color.get('r', 0),
                    color.get('g', 0),
                    color.get('b', 0)
                )
        self._send_to_hardware('all')
    
    def set_global_brightness(self, brightness: int):
        """Set global brightness for all zones."""
        self.global_brightness = max(0, min(100, brightness))
        
        for zone in self.zones.values():
            zone.set_brightness(int(zone.brightness * self.global_brightness / 100))
        
        self._send_to_hardware('all')
    
    def enable_zone(self, zone_name: str, enabled: bool):
        """Enable or disable a zone."""
        if zone_name in self.zones:
            self.zones[zone_name].enabled = enabled
            self._send_to_hardware(zone_name)
            return True
        return False
    
    def turn_off_all(self):
        """Turn off all zones."""
        for zone in self.zones.values():
            zone.set_color(0, 0, 0)
        self._send_to_hardware('all')
    
    def get_zone_status(self, zone_name: str) -> Dict:
        """Get status of a specific zone."""
        if zone_name in self.zones:
            return self.zones[zone_name].to_dict()
        return None
    
    def get_all_zones_status(self) -> Dict:
        """Get status of all zones."""
        return {
            'zones': {name: zone.to_dict() for name, zone in self.zones.items()},
            'global_brightness': self.global_brightness,
            'master_enabled': self.master_enabled,
            'auto_dim_enabled': self.auto_dim_enabled,
            'parking_brake_dim': self.parking_brake_dim,
            'animation_active': self.animation_active,
            'hardware_type': self.hardware_type,
            'serial_connected': self.serial_connected
        }
    
    def apply_auto_dim(self):
        """Apply auto-dimming based on time of day."""
        hour = datetime.now().hour
        
        if 22 <= hour or hour < 6:
            dim_level = 30
        elif 6 <= hour < 8:
            dim_level = 50
        elif 20 <= hour < 22:
            dim_level = 70
        else:
            dim_level = 100
        
        self.set_global_brightness(dim_level)
        return dim_level
    
    def apply_parking_brake_dim(self, engaged: bool):
        """Dim lights when parking brake is engaged."""
        self.parking_brake_dim = engaged
        
        if engaged:
            self.set_global_brightness(40)
        else:
            self.set_global_brightness(100)
    
    def fade_in(self, duration: float = 2.0):
        """Fade in all zones."""
        steps = 20
        step_delay = duration / steps
        
        original_brightness = self.global_brightness
        
        for i in range(steps + 1):
            brightness = int((i / steps) * original_brightness)
            self.set_global_brightness(brightness)
            time.sleep(step_delay)
    
    def fade_out(self, duration: float = 2.0):
        """Fade out all zones."""
        steps = 20
        step_delay = duration / steps
        
        original_brightness = self.global_brightness
        
        for i in range(steps, -1, -1):
            brightness = int((i / steps) * original_brightness)
            self.set_global_brightness(brightness)
            time.sleep(step_delay)
    
    def pulse_zone(self, zone_name: str, intensity: float = 1.0):
        """Pulse a specific zone (for bass hits)."""
        if zone_name not in self.zones:
            return
        
        zone = self.zones[zone_name]
        original_brightness = zone.brightness
        
        pulse_brightness = min(100, int(original_brightness * (1.0 + intensity * 0.5)))
        
        zone.set_brightness(pulse_brightness)
        self._send_to_hardware(zone_name)
        
        time.sleep(0.05)
        
        zone.set_brightness(original_brightness)
        self._send_to_hardware(zone_name)
    
    def pulse_all(self, intensity: float = 1.0):
        """Pulse all zones simultaneously."""
        for zone_name in self.zones.keys():
            self.pulse_zone(zone_name, intensity)
    
    def flash_zone(self, zone_name: str, duration: float = 0.1):
        """Flash a zone briefly."""
        if zone_name not in self.zones:
            return
        
        zone = self.zones[zone_name]
        original_color = zone.color.copy()
        
        zone.set_color(255, 255, 255)
        self._send_to_hardware(zone_name)
        
        time.sleep(duration)
        
        zone.set_color(original_color['r'], original_color['g'], original_color['b'])
        self._send_to_hardware(zone_name)
    
    def set_rainbow_gradient(self):
        """Set rainbow gradient across all zones."""
        colors = [
            {'r': 255, 'g': 0, 'b': 0},
            {'r': 255, 'g': 127, 'b': 0},
            {'r': 255, 'g': 255, 'b': 0},
            {'r': 0, 'g': 255, 'b': 0},
            {'r': 0, 'g': 0, 'b': 255},
            {'r': 75, 'g': 0, 'b': 130},
            {'r': 148, 'g': 0, 'b': 211}
        ]
        
        zone_names = list(self.zones.keys())
        for i, zone_name in enumerate(zone_names):
            color = colors[i % len(colors)]
            self.zones[zone_name].set_color(color['r'], color['g'], color['b'])
        
        self._send_to_hardware('all')
    
    def start_animation(self, animation_func, *args):
        """Start an animation in a separate thread."""
        self.stop_animation()
        
        self.animation_stop_flag = False
        self.animation_active = True
        
        def animation_wrapper():
            animation_func(*args)
            self.animation_active = False
        
        self.animation_thread = threading.Thread(target=animation_wrapper, daemon=True)
        self.animation_thread.start()
    
    def stop_animation(self):
        """Stop any running animation."""
        if self.animation_active:
            self.animation_stop_flag = True
            
            if self.animation_thread:
                self.animation_thread.join(timeout=1.0)
            
            self.animation_active = False
    
    def _send_to_hardware(self, zone_name: str):
        """Simulate sending data to hardware (WS2812B/PWM/Serial)."""
        pass
    
    def get_hardware_status(self) -> Dict:
        """Get hardware connection status."""
        return {
            'hardware_type': self.hardware_type,
            'pwm_frequency': self.pwm_frequency,
            'serial_connected': self.serial_connected,
            'total_leds': sum(z.led_count for z in self.zones.values()),
            'power_draw_estimate_watts': self._estimate_power_draw()
        }
    
    def _estimate_power_draw(self) -> float:
        """Estimate power draw based on LED colors and brightness."""
        total_power = 0.0
        
        for zone in self.zones.values():
            actual_color = zone.get_actual_color()
            
            brightness_factor = (actual_color['r'] + actual_color['g'] + actual_color['b']) / (255 * 3)
            
            power_per_led = 0.06
            zone_power = zone.led_count * power_per_led * brightness_factor
            total_power += zone_power
        
        return round(total_power, 2)
    
    def simulate_serial_connect(self, connected: bool):
        """Simulate serial connection to Arduino/ESP32."""
        self.serial_connected = connected
        return connected
    
    def get_stats(self) -> Dict:
        """Get controller statistics."""
        enabled_zones = sum(1 for z in self.zones.values() if z.enabled)
        total_leds = sum(z.led_count for z in self.zones.values())
        active_leds = sum(z.led_count for z in self.zones.values() if z.enabled)
        
        return {
            'total_zones': len(self.zones),
            'enabled_zones': enabled_zones,
            'total_leds': total_leds,
            'active_leds': active_leds,
            'global_brightness': self.global_brightness,
            'master_enabled': self.master_enabled,
            'animation_active': self.animation_active,
            'power_draw_watts': self._estimate_power_draw()
        }
