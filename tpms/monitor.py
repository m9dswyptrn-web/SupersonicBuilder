#!/usr/bin/env python3
"""
TPMS Monitor
Tire pressure monitoring system logic with CAN bus integration
"""

import time
import random
import requests
from threading import Thread, Lock, Event
from datetime import datetime
from typing import Dict, Callable, Optional


class TPMSMonitor:
    """TPMS monitoring system."""
    
    # Sonic recommended pressure: 32-35 PSI
    DEFAULT_MIN_PSI = 28.0
    DEFAULT_RECOMMENDED_PSI = 33.0
    DEFAULT_MAX_PSI = 36.0
    
    # Temperature thresholds
    TEMP_WARNING_F = 150.0
    TEMP_CRITICAL_F = 180.0
    
    # Rapid pressure loss detection (PSI drop per minute)
    RAPID_LOSS_THRESHOLD = 2.0
    
    def __init__(self, can_bus_url: str = None, simulated: bool = True):
        """Initialize TPMS monitor."""
        self.can_bus_url = can_bus_url or 'http://localhost:7000'
        self.simulated = simulated
        
        self.running = False
        self.thread = None
        self.stop_event = Event()
        self.lock = Lock()
        
        # Current readings
        self.current_readings = {
            'front_left': {'pressure_psi': 33.0, 'temperature_f': 75.0, 'last_update': None},
            'front_right': {'pressure_psi': 33.0, 'temperature_f': 75.0, 'last_update': None},
            'rear_left': {'pressure_psi': 33.0, 'temperature_f': 75.0, 'last_update': None},
            'rear_right': {'pressure_psi': 33.0, 'temperature_f': 75.0, 'last_update': None},
            'spare': {'pressure_psi': 60.0, 'temperature_f': 70.0, 'last_update': None}
        }
        
        # Sensor metadata
        self.sensors = {
            'front_left': {'sensor_id': 'TPMS-FL-001', 'battery': 3.0, 'signal': 95},
            'front_right': {'sensor_id': 'TPMS-FR-001', 'battery': 3.1, 'signal': 92},
            'rear_left': {'sensor_id': 'TPMS-RL-001', 'battery': 2.9, 'signal': 90},
            'rear_right': {'sensor_id': 'TPMS-RR-001', 'battery': 3.0, 'signal': 88},
            'spare': {'sensor_id': 'TPMS-SP-001', 'battery': 3.2, 'signal': 85}
        }
        
        # Previous readings for rapid loss detection
        self.previous_readings = {}
        
        # Callbacks
        self.on_reading_callback = None
        self.on_alert_callback = None
    
    def set_callbacks(self, on_reading: Callable = None, on_alert: Callable = None):
        """Set callback functions for new readings and alerts."""
        self.on_reading_callback = on_reading
        self.on_alert_callback = on_alert
    
    def start(self):
        """Start monitoring."""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        self.thread = Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop monitoring."""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        if self.thread:
            self.thread.join(timeout=2)
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running and not self.stop_event.is_set():
            try:
                if self.simulated:
                    self._update_simulated_readings()
                else:
                    self._fetch_can_bus_readings()
                
                # Process readings and check for alerts
                self._process_readings()
                
            except Exception as e:
                print(f"TPMS monitor error: {e}")
            
            # Update every 2 seconds
            self.stop_event.wait(2.0)
    
    def _update_simulated_readings(self):
        """Update simulated tire pressure readings."""
        with self.lock:
            for position in self.current_readings.keys():
                # Simulate slight variations in pressure and temperature
                current = self.current_readings[position]
                
                # Pressure varies ±0.5 PSI
                pressure_delta = random.uniform(-0.5, 0.5)
                new_pressure = max(0, current['pressure_psi'] + pressure_delta)
                
                # Temperature varies ±2°F
                temp_delta = random.uniform(-2, 2)
                new_temp = max(32, current['temperature_f'] + temp_delta)
                
                # Spare tire stays cooler
                if position == 'spare':
                    new_temp = min(new_temp, 80.0)
                
                self.current_readings[position] = {
                    'pressure_psi': round(new_pressure, 1),
                    'temperature_f': round(new_temp, 1),
                    'last_update': datetime.now().isoformat()
                }
    
    def _fetch_can_bus_readings(self):
        """Fetch TPMS data from CAN bus service."""
        try:
            # Try to get TPMS data from CAN bus
            response = requests.get(f'{self.can_bus_url}/api/tpms/current', timeout=1)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('ok'):
                    tpms_data = data.get('readings', {})
                    
                    with self.lock:
                        for position, reading in tpms_data.items():
                            if position in self.current_readings:
                                self.current_readings[position] = {
                                    'pressure_psi': reading.get('pressure_psi', 0),
                                    'temperature_f': reading.get('temperature_f', 70),
                                    'last_update': datetime.now().isoformat()
                                }
        
        except requests.exceptions.RequestException:
            # Fall back to simulated if CAN bus unavailable
            self._update_simulated_readings()
    
    def _process_readings(self):
        """Process readings and trigger callbacks."""
        with self.lock:
            readings_copy = self.current_readings.copy()
        
        # Trigger reading callback
        if self.on_reading_callback:
            for position, reading in readings_copy.items():
                self.on_reading_callback(
                    position, 
                    reading['pressure_psi'],
                    reading['temperature_f'],
                    self.sensors[position]['sensor_id'],
                    self.sensors[position]['battery'],
                    self.sensors[position]['signal']
                )
        
        # Check for rapid pressure loss
        self._check_rapid_pressure_loss(readings_copy)
        
        # Update previous readings
        self.previous_readings = readings_copy
    
    def _check_rapid_pressure_loss(self, current_readings: Dict):
        """Check for rapid pressure loss (possible puncture)."""
        if not self.previous_readings or not self.on_alert_callback:
            return
        
        for position, current in current_readings.items():
            if position not in self.previous_readings:
                continue
            
            previous = self.previous_readings[position]
            
            # Calculate pressure drop rate (PSI per minute)
            pressure_drop = previous['pressure_psi'] - current['pressure_psi']
            
            # Assuming 2 second intervals, convert to per minute
            drop_rate_per_minute = pressure_drop * 30
            
            if drop_rate_per_minute >= self.RAPID_LOSS_THRESHOLD:
                self.on_alert_callback({
                    'type': 'rapid_pressure_loss',
                    'severity': 'critical',
                    'tire_position': position,
                    'pressure_psi': current['pressure_psi'],
                    'drop_rate': drop_rate_per_minute,
                    'message': f"Rapid pressure loss detected in {position.replace('_', ' ')} tire! Possible puncture."
                })
    
    def get_current_readings(self) -> Dict:
        """Get current tire pressure readings."""
        with self.lock:
            return self.current_readings.copy()
    
    def get_reading(self, tire_position: str) -> Optional[Dict]:
        """Get reading for specific tire."""
        with self.lock:
            return self.current_readings.get(tire_position)
    
    def get_sensor_info(self, tire_position: str) -> Optional[Dict]:
        """Get sensor metadata."""
        return self.sensors.get(tire_position)
    
    def set_pressure(self, tire_position: str, pressure_psi: float):
        """Manually set tire pressure (for testing/calibration)."""
        with self.lock:
            if tire_position in self.current_readings:
                self.current_readings[tire_position]['pressure_psi'] = pressure_psi
                self.current_readings[tire_position]['last_update'] = datetime.now().isoformat()
    
    def set_temperature(self, tire_position: str, temperature_f: float):
        """Manually set tire temperature (for testing)."""
        with self.lock:
            if tire_position in self.current_readings:
                self.current_readings[tire_position]['temperature_f'] = temperature_f
                self.current_readings[tire_position]['last_update'] = datetime.now().isoformat()
    
    def simulate_puncture(self, tire_position: str):
        """Simulate a tire puncture (rapid pressure loss)."""
        with self.lock:
            if tire_position in self.current_readings:
                # Drop pressure by 10 PSI immediately
                current = self.current_readings[tire_position]['pressure_psi']
                self.current_readings[tire_position]['pressure_psi'] = max(0, current - 10)
                self.current_readings[tire_position]['last_update'] = datetime.now().isoformat()
    
    def learn_sensor(self, tire_position: str, sensor_id: str = None):
        """Learn/register a TPMS sensor."""
        if tire_position not in self.sensors:
            return False
        
        if sensor_id:
            self.sensors[tire_position]['sensor_id'] = sensor_id
        else:
            # Auto-generate sensor ID
            self.sensors[tire_position]['sensor_id'] = f"TPMS-{tire_position.upper()[:2]}-{random.randint(100, 999)}"
        
        self.sensors[tire_position]['battery'] = 3.2  # Fresh battery
        self.sensors[tire_position]['signal'] = 100
        
        return True
    
    def reset_sensors(self):
        """Reset all TPMS sensors."""
        for position in self.sensors:
            self.sensors[position] = {
                'sensor_id': f"TPMS-UNLEARNED-{position.upper()[:2]}",
                'battery': 0.0,
                'signal': 0
            }
    
    def get_pressure_status(self, tire_position: str, min_psi: float = None, 
                           max_psi: float = None) -> str:
        """Get pressure status (normal/low/high)."""
        min_psi = min_psi or self.DEFAULT_MIN_PSI
        max_psi = max_psi or self.DEFAULT_MAX_PSI
        
        reading = self.get_reading(tire_position)
        if not reading:
            return 'unknown'
        
        pressure = reading['pressure_psi']
        
        if pressure < min_psi:
            return 'low'
        elif pressure > max_psi:
            return 'high'
        else:
            return 'normal'
    
    def get_temperature_status(self, tire_position: str) -> str:
        """Get temperature status (normal/warning/critical)."""
        reading = self.get_reading(tire_position)
        if not reading:
            return 'unknown'
        
        temp = reading['temperature_f']
        
        if temp >= self.TEMP_CRITICAL_F:
            return 'critical'
        elif temp >= self.TEMP_WARNING_F:
            return 'warning'
        else:
            return 'normal'
    
    def adjust_for_temperature(self, base_pressure_psi: float, 
                               ambient_temp_f: float, target_temp_f: float = 68.0) -> float:
        """Adjust recommended pressure for temperature changes."""
        # Rule of thumb: tire pressure changes ~1 PSI per 10°F
        temp_diff = ambient_temp_f - target_temp_f
        pressure_adjustment = temp_diff / 10.0
        
        return round(base_pressure_psi + pressure_adjustment, 1)
