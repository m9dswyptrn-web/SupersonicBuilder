#!/usr/bin/env python3
"""
Real-time Driving Tips Generator
Provides intelligent driving suggestions for fuel economy optimization
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import random


class DrivingTipGenerator:
    """Generates real-time driving tips based on vehicle data."""
    
    def __init__(self):
        """Initialize tip generator."""
        self.last_tip_time = {}
        self.tip_cooldown_seconds = 10
        self.active_tips = set()
        self.tip_history = []
        
        self.sonic_specific_tips = {
            'turbo_lag': "1.4L Turbo: Keep RPM above 1800 for responsive turbo power",
            'boost_efficiency': "Turbo is most efficient at 2000-2500 RPM in top gear",
            'downshift_turbo': "Use turbo boost for passing - more efficient than high RPM NA power",
            'engine_warmup': "Allow 30-60 seconds warmup before driving for turbo longevity",
            'premium_fuel': "Premium fuel not required, but can improve MPG by 2-3% in Sonic LTZ"
        }
    
    def analyze_driving(self, vehicle_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze current driving and generate relevant tips.
        
        Args:
            vehicle_data: Current vehicle telemetry
        
        Returns:
            List of driving tips
        """
        tips = []
        
        speed = vehicle_data.get('speed_mph', 0)
        rpm = vehicle_data.get('rpm', 0)
        throttle = vehicle_data.get('throttle_percent', 0)
        fuel_rate = vehicle_data.get('fuel_rate_gph', 0)
        instant_mpg = vehicle_data.get('instant_mpg', 0)
        
        tip = self._check_acceleration(speed, rpm, throttle)
        if tip:
            tips.append(tip)
        
        tip = self._check_speed_consistency(speed)
        if tip:
            tips.append(tip)
        
        tip = self._check_rpm_efficiency(rpm, speed, throttle)
        if tip:
            tips.append(tip)
        
        tip = self._check_braking_pattern(vehicle_data)
        if tip:
            tips.append(tip)
        
        tip = self._check_idle_time(rpm, speed)
        if tip:
            tips.append(tip)
        
        tip = self._check_highway_speed(speed, rpm)
        if tip:
            tips.append(tip)
        
        tip = self._check_coasting(speed, throttle)
        if tip:
            tips.append(tip)
        
        tip = self._check_turbo_usage(rpm, throttle, speed)
        if tip:
            tips.append(tip)
        
        filtered_tips = self._filter_cooldown(tips)
        
        return filtered_tips
    
    def _check_acceleration(self, speed: float, rpm: int, throttle: float) -> Optional[Dict[str, Any]]:
        """Check acceleration patterns."""
        if throttle > 75 and speed < 35:
            return {
                'type': 'acceleration',
                'severity': 'warning',
                'title': 'Accelerating Too Hard',
                'message': 'Ease off the throttle - you can improve MPG by 10-15% with gradual acceleration',
                'icon': '⚠️',
                'potential_savings_mpg': 4.5,
                'action': 'Reduce throttle to 40-50%'
            }
        
        if throttle > 60 and rpm > 3500:
            return {
                'type': 'acceleration',
                'severity': 'warning',
                'title': 'High RPM Acceleration',
                'message': 'Shift to higher gear or reduce throttle - current RPM is inefficient',
                'icon': '⚠️',
                'potential_savings_mpg': 3.0,
                'action': f'Shift up or reduce throttle below {rpm} RPM'
            }
        
        if 20 <= throttle <= 35 and rpm < 2500 and speed > 10:
            return {
                'type': 'acceleration',
                'severity': 'success',
                'title': 'Perfect Acceleration',
                'message': 'Excellent throttle control! This is optimal for fuel economy.',
                'icon': '✅',
                'potential_savings_mpg': 0,
                'action': 'Keep it up!'
            }
        
        return None
    
    def _check_speed_consistency(self, speed: float) -> Optional[Dict[str, Any]]:
        """Check for speed consistency."""
        if not hasattr(self, 'speed_history'):
            self.speed_history = []
        
        self.speed_history.append(speed)
        
        if len(self.speed_history) > 30:
            self.speed_history = self.speed_history[-30:]
        
        if len(self.speed_history) >= 10:
            recent_speeds = self.speed_history[-10:]
            avg_speed = sum(recent_speeds) / len(recent_speeds)
            speed_variance = sum((s - avg_speed) ** 2 for s in recent_speeds) / len(recent_speeds)
            
            if speed_variance > 100 and avg_speed > 40:
                return {
                    'type': 'speed_consistency',
                    'severity': 'info',
                    'title': 'Inconsistent Speed',
                    'message': 'Try to maintain steady speed for better fuel economy',
                    'icon': '💡',
                    'potential_savings_mpg': 2.5,
                    'action': 'Use cruise control on highway'
                }
            
            if speed_variance < 20 and avg_speed > 45:
                return {
                    'type': 'speed_consistency',
                    'severity': 'success',
                    'title': 'Steady Speed',
                    'message': 'Great speed consistency! This maximizes MPG.',
                    'icon': '✅',
                    'potential_savings_mpg': 0,
                    'action': 'Keep maintaining this speed'
                }
        
        return None
    
    def _check_rpm_efficiency(self, rpm: int, speed: float, throttle: float) -> Optional[Dict[str, Any]]:
        """Check RPM efficiency."""
        if speed > 40 and rpm > 3000:
            return {
                'type': 'rpm',
                'severity': 'warning',
                'title': 'RPM Too High',
                'message': f'Shift to higher gear - {rpm} RPM is inefficient at {speed:.0f} MPH',
                'icon': '⚠️',
                'potential_savings_mpg': 3.5,
                'action': 'Shift up for better fuel economy'
            }
        
        if speed > 30 and 1500 <= rpm <= 2500:
            return {
                'type': 'rpm',
                'severity': 'success',
                'title': 'Optimal RPM Range',
                'message': f'{rpm} RPM is perfect for the 1.4L Turbo engine',
                'icon': '✅',
                'potential_savings_mpg': 0,
                'action': 'Maintain this RPM range'
            }
        
        if rpm < 1200 and throttle > 50 and speed > 5:
            return {
                'type': 'rpm',
                'severity': 'warning',
                'title': 'Engine Lugging',
                'message': 'Downshift to avoid engine damage - RPM too low for current load',
                'icon': '⚠️',
                'potential_savings_mpg': 0,
                'action': 'Downshift immediately'
            }
        
        return None
    
    def _check_braking_pattern(self, vehicle_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check braking patterns."""
        if not hasattr(self, 'prev_speed'):
            self.prev_speed = vehicle_data.get('speed_mph', 0)
            return None
        
        current_speed = vehicle_data.get('speed_mph', 0)
        speed_delta = self.prev_speed - current_speed
        self.prev_speed = current_speed
        
        if speed_delta > 15:
            return {
                'type': 'braking',
                'severity': 'warning',
                'title': 'Hard Braking Detected',
                'message': 'Anticipate stops earlier and coast to slow down gradually',
                'icon': '⚠️',
                'potential_savings_mpg': 2.0,
                'action': 'Look ahead and brake earlier next time'
            }
        
        if 3 <= speed_delta <= 8 and current_speed > 5:
            return {
                'type': 'braking',
                'severity': 'success',
                'title': 'Smooth Braking',
                'message': 'Excellent deceleration technique!',
                'icon': '✅',
                'potential_savings_mpg': 0,
                'action': 'Keep using gradual braking'
            }
        
        return None
    
    def _check_idle_time(self, rpm: int, speed: float) -> Optional[Dict[str, Any]]:
        """Check for excessive idling."""
        if not hasattr(self, 'idle_start_time'):
            self.idle_start_time = None
        
        if rpm > 600 and speed < 1:
            if self.idle_start_time is None:
                self.idle_start_time = datetime.now()
            else:
                idle_duration = (datetime.now() - self.idle_start_time).total_seconds()
                
                if idle_duration > 60:
                    return {
                        'type': 'idle',
                        'severity': 'warning',
                        'title': 'Long Idle Time',
                        'message': f'Idling for {int(idle_duration)} seconds - consider turning off engine',
                        'icon': '⚠️',
                        'potential_savings_mpg': 0,
                        'action': 'Turn off engine if waiting > 30 seconds'
                    }
        else:
            self.idle_start_time = None
        
        return None
    
    def _check_highway_speed(self, speed: float, rpm: int) -> Optional[Dict[str, Any]]:
        """Check highway speed optimization."""
        if 45 <= speed <= 54 and rpm < 2000:
            return {
                'type': 'highway_speed',
                'severity': 'info',
                'title': 'Below Optimal Highway Speed',
                'message': 'Increase to 55-65 MPH for best highway fuel economy',
                'icon': '💡',
                'potential_savings_mpg': 1.5,
                'action': 'Accelerate to 55-65 MPH range'
            }
        
        if 55 <= speed <= 65:
            return {
                'type': 'highway_speed',
                'severity': 'success',
                'title': 'Optimal Highway Speed',
                'message': f'{speed:.0f} MPH is perfect for maximum highway MPG!',
                'icon': '✅',
                'potential_savings_mpg': 0,
                'action': 'Maintain this speed'
            }
        
        if speed > 75:
            mpg_loss = (speed - 65) * 0.15
            return {
                'type': 'highway_speed',
                'severity': 'warning',
                'title': 'Speed Too High',
                'message': f'Slow down to 55-65 MPH to improve MPG by {mpg_loss:.1f}',
                'icon': '⚠️',
                'potential_savings_mpg': mpg_loss,
                'action': 'Reduce speed for better fuel economy'
            }
        
        return None
    
    def _check_coasting(self, speed: float, throttle: float) -> Optional[Dict[str, Any]]:
        """Check for coasting opportunities."""
        if speed > 30 and throttle < 3:
            return {
                'type': 'coasting',
                'severity': 'success',
                'title': 'Coasting Detected',
                'message': 'Excellent! Coasting saves fuel and maintains momentum.',
                'icon': '✅',
                'potential_savings_mpg': 0,
                'action': 'Continue coasting when safe'
            }
        
        if speed > 50 and 10 < throttle < 25:
            return {
                'type': 'coasting',
                'severity': 'info',
                'title': 'Coasting Opportunity',
                'message': 'Release throttle and coast to maintain current speed',
                'icon': '💡',
                'potential_savings_mpg': 1.0,
                'action': 'Lift off throttle and coast'
            }
        
        return None
    
    def _check_turbo_usage(self, rpm: int, throttle: float, speed: float) -> Optional[Dict[str, Any]]:
        """Check turbo efficiency (Sonic LTZ 1.4L Turbo specific)."""
        if rpm > 1800 and rpm < 2500 and throttle > 30 and throttle < 60:
            return {
                'type': 'turbo',
                'severity': 'success',
                'title': 'Optimal Turbo Range',
                'message': 'Perfect! Turbo is providing efficient boost at this RPM.',
                'icon': '🚀',
                'potential_savings_mpg': 0,
                'action': 'Maintain 1800-2500 RPM range'
            }
        
        if rpm < 1500 and throttle > 60:
            return {
                'type': 'turbo',
                'severity': 'info',
                'title': 'Turbo Lag Zone',
                'message': 'Downshift or increase RPM above 1800 for responsive turbo power',
                'icon': '💡',
                'potential_savings_mpg': 0,
                'action': 'Keep RPM above 1800 for turbo boost'
            }
        
        return None
    
    def _filter_cooldown(self, tips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter tips based on cooldown period."""
        filtered = []
        now = datetime.now()
        
        for tip in tips:
            tip_type = tip['type']
            
            if tip_type in self.last_tip_time:
                time_since_last = (now - self.last_tip_time[tip_type]).total_seconds()
                
                if time_since_last < self.tip_cooldown_seconds:
                    continue
            
            self.last_tip_time[tip_type] = now
            filtered.append(tip)
        
        return filtered
    
    def get_random_sonic_tip(self) -> Dict[str, Any]:
        """Get a random Sonic LTZ specific tip."""
        tip_key = random.choice(list(self.sonic_specific_tips.keys()))
        tip_message = self.sonic_specific_tips[tip_key]
        
        return {
            'type': 'sonic_specific',
            'severity': 'info',
            'title': '2014 Sonic LTZ Tip',
            'message': tip_message,
            'icon': '🚗',
            'potential_savings_mpg': 0,
            'action': 'Vehicle-specific optimization'
        }
    
    def get_eco_challenge_tips(self, current_mpg: float, target_mpg: float) -> List[Dict[str, Any]]:
        """Get tips for eco challenges."""
        tips = []
        
        if current_mpg < target_mpg:
            deficit = target_mpg - current_mpg
            
            tips.append({
                'type': 'eco_challenge',
                'severity': 'info',
                'title': 'Challenge Progress',
                'message': f'You need {deficit:.1f} more MPG to reach your goal of {target_mpg:.1f} MPG',
                'icon': '🎯',
                'potential_savings_mpg': deficit,
                'action': 'Focus on smooth acceleration and steady speeds'
            })
        else:
            tips.append({
                'type': 'eco_challenge',
                'severity': 'success',
                'title': 'Challenge Complete!',
                'message': f'Congratulations! You achieved {current_mpg:.1f} MPG (target: {target_mpg:.1f})',
                'icon': '🏆',
                'potential_savings_mpg': 0,
                'action': 'Keep up the excellent driving!'
            })
        
        return tips
