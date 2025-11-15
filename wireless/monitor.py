#!/usr/bin/env python3
"""
Wireless Charger Monitor Module
Simulated monitoring of wireless charging pad and phone charging status
"""

import random
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta


class WirelessChargerMonitor:
    """Monitor for wireless charging pad and phone charging status."""
    
    def __init__(self):
        """Initialize the wireless charger monitor."""
        self.phone_on_pad = False
        self.charging_active = False
        self.phone_model = None
        self.qi_compatible = True
        self.battery_percent = 0
        self.start_battery = 0
        self.charging_start_time = None
        self.alignment_score = 100
        self.pad_temp_c = 25.0
        self.phone_temp_c = 25.0
        self.input_power_w = 0.0
        self.output_power_w = 0.0
        self.charging_power_w = 0.0
        self.coil_health_percent = 100.0
        self.charging_cycles = 0
        
        self.phone_models = [
            'iPhone 15 Pro', 'iPhone 14', 'iPhone 13',
            'Samsung Galaxy S24', 'Samsung Galaxy S23', 'Samsung Galaxy S22',
            'Google Pixel 8 Pro', 'Google Pixel 7',
            'OnePlus 12', 'OnePlus 11',
            'Xiaomi 14', 'Unknown Phone'
        ]
    
    def simulate_phone_placement(self, alignment: str = 'good'):
        """Simulate placing a phone on the charging pad."""
        self.phone_on_pad = True
        self.phone_model = random.choice(self.phone_models)
        self.qi_compatible = 'Unknown' not in self.phone_model
        self.battery_percent = random.randint(15, 75)
        self.start_battery = self.battery_percent
        self.charging_start_time = datetime.now()
        
        if alignment == 'good':
            self.alignment_score = random.randint(90, 100)
        elif alignment == 'moderate':
            self.alignment_score = random.randint(70, 89)
        else:
            self.alignment_score = random.randint(40, 69)
        
        if self.qi_compatible and self.alignment_score >= 60:
            self.charging_active = True
            self._update_charging_power()
        else:
            self.charging_active = False
            self.charging_power_w = 0.0
    
    def simulate_phone_removal(self):
        """Simulate removing the phone from the charging pad."""
        self.phone_on_pad = False
        self.charging_active = False
        self.phone_model = None
        self.charging_power_w = 0.0
        self.input_power_w = 0.0
        self.output_power_w = 0.0
        self.alignment_score = 100
        self.pad_temp_c = max(25.0, self.pad_temp_c - 5.0)
        self.phone_temp_c = max(25.0, self.phone_temp_c - 5.0)
        
        if self.charging_start_time:
            self.charging_cycles += 1
            self.coil_health_percent = max(85.0, self.coil_health_percent - 0.01)
            self.charging_start_time = None
    
    def _update_charging_power(self):
        """Update charging power based on various factors."""
        if not self.charging_active:
            self.charging_power_w = 0.0
            self.input_power_w = 0.0
            self.output_power_w = 0.0
            return
        
        base_power = 10.0
        
        if self.battery_percent < 20:
            base_power = 15.0
        elif self.battery_percent < 50:
            base_power = 12.0
        elif self.battery_percent > 80:
            base_power = 7.0
        
        alignment_factor = self.alignment_score / 100.0
        temp_factor = 1.0 if self.pad_temp_c < 40 else 0.8
        
        self.output_power_w = base_power * alignment_factor * temp_factor
        
        efficiency = self.get_efficiency_percent() / 100.0
        self.input_power_w = self.output_power_w / efficiency if efficiency > 0 else 0.0
        
        self.charging_power_w = self.output_power_w
        
        self.output_power_w += random.uniform(-0.5, 0.5)
        self.input_power_w += random.uniform(-0.7, 0.7)
        self.charging_power_w = max(0.0, self.charging_power_w)
    
    def update_charging_status(self):
        """Update charging status simulation (call this periodically)."""
        if not self.phone_on_pad:
            return
        
        if self.charging_active:
            charge_rate = self.charging_power_w / 50.0
            self.battery_percent = min(100, self.battery_percent + charge_rate)
            
            heat_generation = self.charging_power_w * (1 - self.get_efficiency_percent() / 100.0)
            self.pad_temp_c = min(55.0, self.pad_temp_c + heat_generation * 0.1)
            self.phone_temp_c = min(50.0, self.phone_temp_c + heat_generation * 0.08)
            
            ambient_cooling = 0.5
            self.pad_temp_c = max(25.0, self.pad_temp_c - ambient_cooling)
            self.phone_temp_c = max(25.0, self.phone_temp_c - ambient_cooling)
            
            self.alignment_score = max(40, self.alignment_score + random.randint(-2, 2))
            self.alignment_score = min(100, self.alignment_score)
            
            if self.battery_percent >= 100:
                self.charging_active = False
                self.charging_power_w = 0.0
        
        self._update_charging_power()
    
    def get_charging_status(self) -> Dict:
        """Get current charging status."""
        return {
            'phone_detected': self.phone_on_pad,
            'charging_active': self.charging_active,
            'battery_percent': int(self.battery_percent) if self.phone_on_pad else None,
            'charging_power_w': round(self.charging_power_w, 2),
            'time_to_full_minutes': self.estimate_time_to_full(),
            'phone_model': self.phone_model,
            'qi_compatible': self.qi_compatible,
            'status': self._get_status_message()
        }
    
    def _get_status_message(self) -> str:
        """Get human-readable status message."""
        if not self.phone_on_pad:
            return 'No phone detected'
        elif not self.qi_compatible:
            return 'Phone not Qi compatible'
        elif not self.charging_active:
            return 'Phone detected but not charging'
        elif self.battery_percent >= 100:
            return 'Fully charged'
        elif self.alignment_score < 60:
            return 'Poor alignment - adjust phone'
        elif self.pad_temp_c > 45:
            return 'Charging (high temperature)'
        else:
            return 'Charging normally'
    
    def estimate_time_to_full(self) -> Optional[int]:
        """Estimate time to full charge in minutes."""
        if not self.charging_active or self.battery_percent >= 100:
            return None
        
        if self.charging_power_w <= 0:
            return None
        
        battery_capacity_wh = 15.0
        remaining_percent = 100 - self.battery_percent
        remaining_wh = battery_capacity_wh * (remaining_percent / 100.0)
        
        hours_to_full = remaining_wh / self.charging_power_w if self.charging_power_w > 0 else 999
        minutes_to_full = int(hours_to_full * 60)
        
        if self.battery_percent > 80:
            minutes_to_full *= 1.5
        
        return max(1, minutes_to_full)
    
    def get_efficiency_metrics(self) -> Dict:
        """Get charging efficiency metrics."""
        efficiency = self.get_efficiency_percent()
        heat_generation = self.input_power_w - self.output_power_w
        
        return {
            'input_power_w': round(self.input_power_w, 2),
            'output_power_w': round(self.output_power_w, 2),
            'efficiency_percent': round(efficiency, 1),
            'heat_generation_w': round(heat_generation, 2),
            'pad_temp_c': round(self.pad_temp_c, 1),
            'phone_temp_c': round(self.phone_temp_c, 1),
            'status': 'excellent' if efficiency > 80 else 'good' if efficiency > 65 else 'poor'
        }
    
    def get_efficiency_percent(self) -> float:
        """Calculate current charging efficiency."""
        if self.input_power_w <= 0:
            return 0.0
        
        base_efficiency = 75.0
        
        alignment_bonus = (self.alignment_score - 70) * 0.3
        temp_penalty = max(0, (self.pad_temp_c - 35) * 0.5)
        coil_factor = self.coil_health_percent / 100.0
        
        efficiency = (base_efficiency + alignment_bonus - temp_penalty) * coil_factor
        
        return max(50.0, min(90.0, efficiency))
    
    def get_phone_compatibility(self) -> Dict:
        """Get phone compatibility information."""
        return {
            'phone_model': self.phone_model or 'Unknown',
            'qi_compatible': self.qi_compatible,
            'max_supported_power_w': 15.0 if self.qi_compatible else 0.0,
            'current_power_w': round(self.charging_power_w, 2),
            'alignment_score': self.alignment_score,
            'alignment_status': self._get_alignment_status(),
            'positioning_tip': self._get_positioning_tip()
        }
    
    def _get_alignment_status(self) -> str:
        """Get alignment status description."""
        if self.alignment_score >= 90:
            return 'Excellent'
        elif self.alignment_score >= 75:
            return 'Good'
        elif self.alignment_score >= 60:
            return 'Fair'
        else:
            return 'Poor'
    
    def _get_positioning_tip(self) -> str:
        """Get positioning guidance tip."""
        if self.alignment_score >= 90:
            return 'Phone is perfectly aligned'
        elif self.alignment_score >= 75:
            return 'Good alignment - minor adjustments may improve charging'
        elif self.alignment_score >= 60:
            return 'Try centering the phone on the charging pad'
        else:
            return 'Phone is poorly aligned - move it to the center of the pad'
    
    def get_pad_health(self) -> Dict:
        """Get wireless charging pad health information."""
        temp_status = 'normal'
        if self.pad_temp_c > 50:
            temp_status = 'critical'
        elif self.pad_temp_c > 45:
            temp_status = 'warning'
        elif self.pad_temp_c > 40:
            temp_status = 'elevated'
        
        coil_status = 'excellent'
        if self.coil_health_percent < 90:
            coil_status = 'good'
        if self.coil_health_percent < 85:
            coil_status = 'fair'
        if self.coil_health_percent < 80:
            coil_status = 'poor'
        
        return {
            'pad_temp_c': round(self.pad_temp_c, 1),
            'temp_status': temp_status,
            'coil_health_percent': round(self.coil_health_percent, 1),
            'coil_status': coil_status,
            'charging_cycles': self.charging_cycles,
            'thermal_throttling': self.pad_temp_c > 48,
            'needs_maintenance': self.coil_health_percent < 85 or self.charging_cycles > 10000,
            'estimated_lifespan_cycles': int(100000 * (self.coil_health_percent / 100.0))
        }
    
    def check_alerts(self) -> list:
        """Check for alert conditions."""
        alerts = []
        
        if self.phone_on_pad and self.battery_percent >= 100:
            alerts.append({
                'type': 'fully_charged',
                'severity': 'info',
                'message': 'Phone is fully charged - remove from charger to preserve battery health'
            })
        
        if self.phone_on_pad and self.alignment_score < 60:
            alerts.append({
                'type': 'misalignment',
                'severity': 'warning',
                'message': 'Phone not aligned properly - adjust position for better charging'
            })
        
        if self.pad_temp_c > 48:
            alerts.append({
                'type': 'overheating',
                'severity': 'critical',
                'message': 'Overheating detected - charging may be reduced or stopped'
            })
        elif self.pad_temp_c > 45:
            alerts.append({
                'type': 'high_temperature',
                'severity': 'warning',
                'message': 'High temperature detected - consider removing phone case'
            })
        
        if self.phone_on_pad and self.charging_active and self.get_efficiency_percent() < 60:
            alerts.append({
                'type': 'low_efficiency',
                'severity': 'warning',
                'message': 'Remove case for better charging efficiency'
            })
        
        if self.coil_health_percent < 85:
            alerts.append({
                'type': 'coil_degradation',
                'severity': 'warning',
                'message': 'Charging coil showing signs of wear - consider service'
            })
        
        if self.phone_on_pad and 80 <= self.battery_percent < 100 and self.charging_active:
            alerts.append({
                'type': 'battery_care',
                'severity': 'info',
                'message': 'Battery at 80% - consider unplugging to extend battery lifespan'
            })
        
        return alerts
    
    def get_all_metrics(self) -> Dict:
        """Get all current metrics."""
        return {
            'charging_status': self.get_charging_status(),
            'efficiency': self.get_efficiency_metrics(),
            'compatibility': self.get_phone_compatibility(),
            'pad_health': self.get_pad_health(),
            'alerts': self.check_alerts(),
            'timestamp': datetime.now().isoformat()
        }
