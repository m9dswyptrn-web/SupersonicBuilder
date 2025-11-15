#!/usr/bin/env python3
"""
HVAC Control Logic
Advanced climate control with multi-zone support
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import random


class HVACMode(Enum):
    """HVAC air distribution modes."""
    OFF = "off"
    FACE = "face"
    FEET = "feet"
    DEFROST = "defrost"
    FACE_FEET = "face_feet"
    FEET_DEFROST = "feet_defrost"
    AUTO = "auto"


class FanSpeed(Enum):
    """Fan speed levels."""
    OFF = 0
    SPEED_1 = 1
    SPEED_2 = 2
    SPEED_3 = 3
    SPEED_4 = 4
    SPEED_5 = 5
    SPEED_6 = 6
    SPEED_7 = 7
    AUTO = -1


@dataclass
class ZoneState:
    """Climate state for a single zone."""
    temperature: float
    fan_speed: int
    heated_seat_level: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HVACState:
    """Complete HVAC system state."""
    driver_zone: ZoneState
    passenger_zone: Optional[ZoneState]
    rear_zone: Optional[ZoneState]
    mode: str
    ac_enabled: bool
    recirculation: bool
    defrost_front: bool
    defrost_rear: bool
    heated_mirrors: bool
    auto_mode: bool
    max_ac: bool
    outside_temp: Optional[float]
    sun_load: int
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'driver_zone': self.driver_zone.to_dict(),
            'passenger_zone': self.passenger_zone.to_dict() if self.passenger_zone else None,
            'rear_zone': self.rear_zone.to_dict() if self.rear_zone else None,
            'mode': self.mode,
            'ac_enabled': self.ac_enabled,
            'recirculation': self.recirculation,
            'defrost_front': self.defrost_front,
            'defrost_rear': self.defrost_rear,
            'heated_mirrors': self.heated_mirrors,
            'auto_mode': self.auto_mode,
            'max_ac': self.max_ac,
            'outside_temp': self.outside_temp,
            'sun_load': self.sun_load,
            'timestamp': self.timestamp
        }


class HVACController:
    """Advanced HVAC control with multi-zone support."""
    
    TEMP_MIN_C = 16.0
    TEMP_MAX_C = 30.0
    TEMP_MIN_F = 60.0
    TEMP_MAX_F = 86.0
    FAN_MAX = 7
    
    def __init__(self, multi_zone: bool = True, rear_zone: bool = False):
        """
        Initialize HVAC controller.
        
        Args:
            multi_zone: Enable dual-zone climate control
            rear_zone: Enable rear zone control
        """
        self.multi_zone = multi_zone
        self.rear_zone_enabled = rear_zone
        
        self.state = HVACState(
            driver_zone=ZoneState(temperature=22.0, fan_speed=0),
            passenger_zone=ZoneState(temperature=22.0, fan_speed=0) if multi_zone else None,
            rear_zone=ZoneState(temperature=22.0, fan_speed=0) if rear_zone else None,
            mode=HVACMode.AUTO.value,
            ac_enabled=False,
            recirculation=False,
            defrost_front=False,
            defrost_rear=False,
            heated_mirrors=False,
            auto_mode=False,
            max_ac=False,
            outside_temp=None,
            sun_load=0,
            timestamp=datetime.now().timestamp()
        )
    
    def set_temperature(self, temp: float, zone: str = 'driver', unit: str = 'C') -> Dict[str, Any]:
        """
        Set temperature for a zone.
        
        Args:
            temp: Temperature value
            zone: 'driver', 'passenger', or 'rear'
            unit: 'C' or 'F'
        
        Returns:
            Updated state
        """
        if unit == 'F':
            temp = self._fahrenheit_to_celsius(temp)
        
        temp = max(self.TEMP_MIN_C, min(temp, self.TEMP_MAX_C))
        
        if zone == 'driver':
            self.state.driver_zone.temperature = temp
        elif zone == 'passenger' and self.state.passenger_zone:
            self.state.passenger_zone.temperature = temp
        elif zone == 'rear' and self.state.rear_zone:
            self.state.rear_zone.temperature = temp
        
        self.state.timestamp = datetime.now().timestamp()
        
        return self.get_state()
    
    def set_fan_speed(self, speed: int, zone: str = 'driver') -> Dict[str, Any]:
        """
        Set fan speed for a zone.
        
        Args:
            speed: Fan speed (0-7, or -1 for auto)
            zone: 'driver', 'passenger', or 'rear'
        
        Returns:
            Updated state
        """
        if speed == -1:
            self.state.auto_mode = True
            speed = 7
        else:
            speed = max(0, min(speed, self.FAN_MAX))
            if speed > 0:
                self.state.auto_mode = False
        
        if zone == 'driver':
            self.state.driver_zone.fan_speed = speed
        elif zone == 'passenger' and self.state.passenger_zone:
            self.state.passenger_zone.fan_speed = speed
        elif zone == 'rear' and self.state.rear_zone:
            self.state.rear_zone.fan_speed = speed
        
        self.state.timestamp = datetime.now().timestamp()
        
        return self.get_state()
    
    def set_mode(self, mode: str) -> Dict[str, Any]:
        """
        Set HVAC air distribution mode.
        
        Args:
            mode: HVAC mode (face, feet, defrost, etc.)
        
        Returns:
            Updated state
        """
        try:
            HVACMode(mode)
            self.state.mode = mode
        except ValueError:
            pass
        
        if mode == HVACMode.DEFROST.value:
            self.state.defrost_front = True
        
        self.state.timestamp = datetime.now().timestamp()
        
        return self.get_state()
    
    def toggle_ac(self) -> Dict[str, Any]:
        """
        Toggle AC on/off.
        
        Returns:
            Updated state
        """
        self.state.ac_enabled = not self.state.ac_enabled
        
        if not self.state.ac_enabled:
            self.state.max_ac = False
        
        self.state.timestamp = datetime.now().timestamp()
        
        return self.get_state()
    
    def set_max_ac(self, enabled: bool) -> Dict[str, Any]:
        """
        Set max AC mode.
        
        Args:
            enabled: True to enable max AC
        
        Returns:
            Updated state
        """
        self.state.max_ac = enabled
        
        if enabled:
            self.state.ac_enabled = True
            self.state.recirculation = True
            self.state.driver_zone.fan_speed = self.FAN_MAX
            if self.state.passenger_zone:
                self.state.passenger_zone.fan_speed = self.FAN_MAX
        
        self.state.timestamp = datetime.now().timestamp()
        
        return self.get_state()
    
    def toggle_recirculation(self) -> Dict[str, Any]:
        """
        Toggle recirculation mode.
        
        Returns:
            Updated state
        """
        self.state.recirculation = not self.state.recirculation
        self.state.timestamp = datetime.now().timestamp()
        
        return self.get_state()
    
    def toggle_defrost(self, location: str = 'front') -> Dict[str, Any]:
        """
        Toggle defrost.
        
        Args:
            location: 'front' or 'rear'
        
        Returns:
            Updated state
        """
        if location == 'front':
            self.state.defrost_front = not self.state.defrost_front
            
            if self.state.defrost_front:
                self.state.mode = HVACMode.DEFROST.value
                self.state.ac_enabled = True
        elif location == 'rear':
            self.state.defrost_rear = not self.state.defrost_rear
        
        self.state.timestamp = datetime.now().timestamp()
        
        return self.get_state()
    
    def toggle_heated_mirrors(self) -> Dict[str, Any]:
        """
        Toggle heated mirrors.
        
        Returns:
            Updated state
        """
        self.state.heated_mirrors = not self.state.heated_mirrors
        self.state.timestamp = datetime.now().timestamp()
        
        return self.get_state()
    
    def set_auto_mode(self, enabled: bool) -> Dict[str, Any]:
        """
        Enable/disable automatic climate control.
        
        Args:
            enabled: True to enable auto mode
        
        Returns:
            Updated state
        """
        self.state.auto_mode = enabled
        
        if enabled:
            self.state.mode = HVACMode.AUTO.value
            self.state.driver_zone.fan_speed = 7
            if self.state.passenger_zone:
                self.state.passenger_zone.fan_speed = 7
        
        self.state.timestamp = datetime.now().timestamp()
        
        return self.get_state()
    
    def set_heated_seat(self, level: int, seat: str = 'driver') -> Dict[str, Any]:
        """
        Set heated seat level.
        
        Args:
            level: Heat level (0-3)
            seat: 'driver' or 'passenger'
        
        Returns:
            Updated state
        """
        level = max(0, min(level, 3))
        
        if seat == 'driver':
            self.state.driver_zone.heated_seat_level = level
        elif seat == 'passenger' and self.state.passenger_zone:
            self.state.passenger_zone.heated_seat_level = level
        
        self.state.timestamp = datetime.now().timestamp()
        
        return self.get_state()
    
    def update_outside_temp(self, temp: float, unit: str = 'C'):
        """
        Update outside temperature.
        
        Args:
            temp: Outside temperature
            unit: 'C' or 'F'
        """
        if unit == 'F':
            temp = self._fahrenheit_to_celsius(temp)
        
        self.state.outside_temp = temp
    
    def update_sun_load(self, load: int):
        """
        Update sun load compensation (0-100%).
        
        Args:
            load: Sun load percentage
        """
        self.state.sun_load = max(0, min(load, 100))
    
    def apply_preset(self, preset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a climate preset.
        
        Args:
            preset: Preset configuration
        
        Returns:
            Updated state
        """
        self.set_temperature(preset['temp_driver'], 'driver', 'C')
        
        if preset.get('temp_passenger') and self.state.passenger_zone:
            self.set_temperature(preset['temp_passenger'], 'passenger', 'C')
        
        if preset.get('temp_rear') and self.state.rear_zone:
            self.set_temperature(preset['temp_rear'], 'rear', 'C')
        
        self.set_fan_speed(preset['fan_speed'], 'driver')
        self.set_mode(preset['mode'])
        
        self.state.ac_enabled = preset.get('ac_enabled', False)
        self.state.recirculation = preset.get('recirculation', False)
        self.state.defrost_front = preset.get('defrost_front', False)
        self.state.defrost_rear = preset.get('defrost_rear', False)
        self.state.auto_mode = preset.get('auto_mode', False)
        
        if preset.get('heated_seat_driver') is not None:
            self.set_heated_seat(preset['heated_seat_driver'], 'driver')
        
        if preset.get('heated_seat_passenger') is not None and self.state.passenger_zone:
            self.set_heated_seat(preset['heated_seat_passenger'], 'passenger')
        
        return self.get_state()
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current HVAC state.
        
        Returns:
            Current state dictionary
        """
        state_dict = self.state.to_dict()
        
        state_dict['temp_limits'] = {
            'min_c': self.TEMP_MIN_C,
            'max_c': self.TEMP_MAX_C,
            'min_f': self.TEMP_MIN_F,
            'max_f': self.TEMP_MAX_F
        }
        
        state_dict['fan_max'] = self.FAN_MAX
        state_dict['multi_zone'] = self.multi_zone
        state_dict['rear_zone_enabled'] = self.rear_zone_enabled
        
        return state_dict
    
    def simulate_auto_adjustment(self):
        """Simulate automatic climate adjustment based on conditions."""
        if not self.state.auto_mode:
            return
        
        if self.state.outside_temp is not None:
            target_temp = self.state.driver_zone.temperature
            
            if self.state.outside_temp > target_temp + 5:
                self.state.ac_enabled = True
                self.state.driver_zone.fan_speed = 6
            elif self.state.outside_temp < target_temp - 5:
                self.state.ac_enabled = False
                self.state.driver_zone.fan_speed = 5
            else:
                self.state.driver_zone.fan_speed = 3
    
    def _celsius_to_fahrenheit(self, celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9/5) + 32
    
    def _fahrenheit_to_celsius(self, fahrenheit: float) -> float:
        """Convert Fahrenheit to Celsius."""
        return (fahrenheit - 32) * 5/9
