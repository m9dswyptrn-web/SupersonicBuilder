#!/usr/bin/env python3
"""
Battery Health Tracking Module
Provides battery health analysis and care tips
"""

import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class BatteryHealthTracker:
    """Track and analyze battery health and provide care recommendations."""
    
    def __init__(self):
        """Initialize battery health tracker."""
        self.battery_percent = 50
        self.voltage_v = 3.8
        self.current_ma = 0
        self.temperature_c = 25.0
        self.cycle_count = 0
        self.health_percent = 100.0
        self.charging_history = []
    
    def update_from_charging_metrics(self, battery_percent: int, 
                                     charging_power_w: float,
                                     phone_temp_c: float):
        """Update battery metrics from charging data."""
        self.battery_percent = battery_percent
        self.temperature_c = phone_temp_c
        
        if charging_power_w > 0:
            self.current_ma = (charging_power_w / self.voltage_v) * 1000
        else:
            self.current_ma = 0
        
        self.voltage_v = self._calculate_voltage(battery_percent)
    
    def _calculate_voltage(self, percent: int) -> float:
        """Calculate battery voltage based on charge level."""
        min_v = 3.3
        max_v = 4.2
        
        voltage = min_v + (max_v - min_v) * (percent / 100.0)
        
        return round(voltage, 2)
    
    def get_battery_info(self) -> Dict:
        """Get comprehensive battery information."""
        return {
            'battery_percent': self.battery_percent,
            'voltage_v': self.voltage_v,
            'current_ma': round(self.current_ma, 0),
            'temperature_c': round(self.temperature_c, 1),
            'health_percent': round(self.health_percent, 1),
            'cycle_count': self.cycle_count,
            'status': self._get_battery_status(),
            'condition': self._get_battery_condition()
        }
    
    def _get_battery_status(self) -> str:
        """Get battery status description."""
        if self.battery_percent >= 100:
            return 'Fully Charged'
        elif self.battery_percent >= 80:
            return 'High'
        elif self.battery_percent >= 50:
            return 'Medium'
        elif self.battery_percent >= 20:
            return 'Low'
        else:
            return 'Very Low'
    
    def _get_battery_condition(self) -> str:
        """Get battery health condition."""
        if self.health_percent >= 95:
            return 'Excellent'
        elif self.health_percent >= 85:
            return 'Good'
        elif self.health_percent >= 75:
            return 'Fair'
        elif self.health_percent >= 60:
            return 'Poor'
        else:
            return 'Replace Soon'
    
    def is_in_optimal_range(self) -> bool:
        """Check if battery is in optimal charging range (20-80%)."""
        return 20 <= self.battery_percent <= 80
    
    def get_optimal_range_status(self) -> Dict:
        """Get status relative to optimal charging range."""
        in_range = self.is_in_optimal_range()
        
        if self.battery_percent < 20:
            message = "Battery below optimal range - OK to charge"
            recommendation = "Start charging to maintain battery health"
        elif self.battery_percent > 80:
            message = "Battery above optimal range - consider unplugging"
            recommendation = "Unplug to maximize battery lifespan"
        else:
            message = "Battery in optimal range (20-80%)"
            recommendation = "This is the best range for battery longevity"
        
        return {
            'in_optimal_range': in_range,
            'current_percent': self.battery_percent,
            'optimal_min': 20,
            'optimal_max': 80,
            'message': message,
            'recommendation': recommendation
        }
    
    def analyze_charging_impact(self, charging_power_w: float,
                                pad_temp_c: float,
                                duration_minutes: int) -> Dict:
        """Analyze the impact of current charging on battery health."""
        impact_score = 100.0
        factors = []
        
        if charging_power_w > 12:
            impact = (charging_power_w - 12) * 2
            impact_score -= impact
            factors.append(f"High power charging ({charging_power_w}W) reduces longevity")
        
        if pad_temp_c > 40:
            impact = (pad_temp_c - 40) * 1.5
            impact_score -= impact
            factors.append(f"Elevated temperature ({pad_temp_c}°C) stresses battery")
        
        if self.battery_percent > 90:
            impact = (self.battery_percent - 90)
            impact_score -= impact
            factors.append(f"Charging above 90% ({self.battery_percent}%) is less efficient")
        
        if duration_minutes > 180:
            impact = (duration_minutes - 180) / 30
            impact_score -= impact
            factors.append(f"Extended charging time ({duration_minutes}min) not ideal")
        
        impact_score = max(0, min(100, impact_score))
        
        if impact_score >= 90:
            impact_level = 'minimal'
        elif impact_score >= 75:
            impact_level = 'low'
        elif impact_score >= 60:
            impact_level = 'moderate'
        elif impact_score >= 40:
            impact_level = 'high'
        else:
            impact_level = 'severe'
        
        return {
            'impact_score': round(impact_score, 1),
            'impact_level': impact_level,
            'factors': factors,
            'health_preservation_tips': self._get_health_preservation_tips(impact_score)
        }
    
    def _get_health_preservation_tips(self, impact_score: float) -> List[str]:
        """Get tips for preserving battery health based on impact score."""
        tips = []
        
        if impact_score < 90:
            tips.append("Use slower charging (5-10W) when possible")
        
        if impact_score < 75:
            tips.append("Remove phone case to reduce heat buildup")
        
        if impact_score < 60:
            tips.append("Avoid charging to 100% regularly")
        
        if impact_score < 40:
            tips.append("Consider stopping charge at 80%")
        
        return tips
    
    def get_care_recommendations(self) -> List[Dict]:
        """Get personalized battery care recommendations."""
        recommendations = []
        
        if self.battery_percent > 80:
            recommendations.append({
                'priority': 'high',
                'category': 'charging_range',
                'title': 'Battery above optimal range',
                'message': 'Consider unplugging at 80% to extend battery life',
                'action': 'Unplug device'
            })
        
        if self.battery_percent < 20:
            recommendations.append({
                'priority': 'medium',
                'category': 'charging_range',
                'title': 'Battery below optimal range',
                'message': 'OK to charge, but avoid going below 20% regularly',
                'action': 'Charge to 80%'
            })
        
        if self.temperature_c > 40:
            recommendations.append({
                'priority': 'critical',
                'category': 'temperature',
                'title': 'High battery temperature',
                'message': f'Battery temperature is {self.temperature_c}°C - remove from charger',
                'action': 'Cool down device'
            })
        
        if self.health_percent < 80:
            recommendations.append({
                'priority': 'high',
                'category': 'battery_health',
                'title': 'Battery health declining',
                'message': f'Battery health at {self.health_percent}% - consider replacement',
                'action': 'Schedule service'
            })
        
        if self.cycle_count > 500:
            recommendations.append({
                'priority': 'medium',
                'category': 'maintenance',
                'title': 'High cycle count',
                'message': f'{self.cycle_count} charging cycles - battery may show reduced capacity',
                'action': 'Monitor performance'
            })
        
        recommendations.append({
            'priority': 'info',
            'category': 'best_practice',
            'title': 'Optimal charging practice',
            'message': 'Keep battery between 20-80% for maximum longevity',
            'action': 'Follow 20-80 rule'
        })
        
        return recommendations
    
    def get_charging_profile(self) -> Dict:
        """Get recommended charging profile for battery health."""
        if self.battery_percent < 20:
            target = 80
            recommended_power = 10.0
            message = "Charge to 80% at moderate speed"
        elif self.battery_percent < 50:
            target = 80
            recommended_power = 10.0
            message = "Charge to 80% for optimal health"
        elif self.battery_percent < 80:
            target = 80
            recommended_power = 7.0
            message = "Nearly at optimal level - slow charging recommended"
        else:
            target = 80
            recommended_power = 5.0
            message = "Above optimal range - consider unplugging"
        
        return {
            'current_percent': self.battery_percent,
            'target_percent': target,
            'recommended_power_w': recommended_power,
            'message': message,
            'stop_at_target': True
        }
    
    def predict_battery_lifespan(self) -> Dict:
        """Predict battery lifespan based on current health and usage."""
        cycles_remaining = int((1000 - self.cycle_count) * (self.health_percent / 100.0))
        
        estimated_days = cycles_remaining * 2
        
        months_remaining = estimated_days / 30
        years_remaining = months_remaining / 12
        
        if years_remaining > 3:
            lifespan_status = 'Excellent'
        elif years_remaining > 2:
            lifespan_status = 'Good'
        elif years_remaining > 1:
            lifespan_status = 'Fair'
        else:
            lifespan_status = 'Consider Replacement'
        
        return {
            'current_health_percent': round(self.health_percent, 1),
            'current_cycle_count': self.cycle_count,
            'estimated_cycles_remaining': cycles_remaining,
            'estimated_months_remaining': round(months_remaining, 1),
            'estimated_years_remaining': round(years_remaining, 1),
            'lifespan_status': lifespan_status,
            'replacement_recommended': years_remaining < 1
        }
    
    def get_daily_tips(self) -> List[str]:
        """Get daily battery care tips."""
        all_tips = [
            "Charge your phone in a cool, well-ventilated area",
            "Avoid using phone while fast charging to reduce heat",
            "Remove thick cases during wireless charging",
            "Calibrate battery by doing a 0-100% charge once a month",
            "Use airplane mode while charging for faster charging",
            "Avoid exposing phone to extreme temperatures",
            "Don't leave phone in hot car while charging",
            "Use original or certified Qi chargers",
            "Keep wireless charging pad clean for better contact",
            "Avoid charging to 100% every night",
            "Enable optimized battery charging if available",
            "Consider charging to 80% for daily use",
            "Let battery drop to 20% before charging",
            "Unplug when fully charged to avoid trickle charging",
            "Monitor battery health regularly"
        ]
        
        random.shuffle(all_tips)
        return all_tips[:3]
