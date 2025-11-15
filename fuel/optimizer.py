#!/usr/bin/env python3
"""
Fuel Economy Optimizer
Calculates MPG, efficiency scores, and optimal driving patterns
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import math


class FuelEconomyOptimizer:
    """Optimizes fuel economy and calculates driving efficiency."""
    
    SONIC_LTZ_SPECS = {
        'engine': '1.4L Turbo',
        'optimal_rpm_min': 1500,
        'optimal_rpm_max': 2500,
        'shift_rpm': 2200,
        'redline_rpm': 6500,
        'epa_highway_mpg': 40,
        'epa_city_mpg': 28,
        'epa_combined_mpg': 33,
        'tank_capacity_gallons': 12.6,
        'optimal_highway_speed_min': 55,
        'optimal_highway_speed_max': 65
    }
    
    def __init__(self):
        """Initialize optimizer."""
        self.session_data = []
        self.trip_start_time = None
        self.trip_distance = 0
        self.trip_fuel_consumed = 0
        self.instant_mpg_history = []
        self.efficiency_events = []
    
    def calculate_instant_mpg(self, speed_mph: float, fuel_rate_gph: float) -> float:
        """
        Calculate instantaneous MPG.
        
        Args:
            speed_mph: Current speed in MPH
            fuel_rate_gph: Fuel consumption rate in gallons per hour
        
        Returns:
            Instant MPG
        """
        if fuel_rate_gph <= 0 or speed_mph <= 0:
            return 0
        
        mpg = speed_mph / fuel_rate_gph
        
        return min(mpg, 99.9)
    
    def calculate_trip_mpg(self, distance_miles: float, fuel_gallons: float) -> float:
        """
        Calculate trip average MPG.
        
        Args:
            distance_miles: Distance traveled
            fuel_gallons: Fuel consumed
        
        Returns:
            Trip average MPG
        """
        if fuel_gallons <= 0:
            return 0
        
        return distance_miles / fuel_gallons
    
    def calculate_efficiency_score(self, data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate driving efficiency score (0-100).
        
        Factors:
        - Smooth acceleration (25%)
        - Smooth braking (25%)
        - Optimal RPM usage (20%)
        - Speed consistency (15%)
        - Idle time reduction (15%)
        
        Returns:
            Efficiency score breakdown
        """
        if not data_points:
            return {
                'total_score': 0,
                'acceleration_score': 0,
                'braking_score': 0,
                'rpm_score': 0,
                'speed_consistency_score': 0,
                'idle_score': 0
            }
        
        accel_score = self._score_acceleration(data_points)
        brake_score = self._score_braking(data_points)
        rpm_score = self._score_rpm_usage(data_points)
        speed_score = self._score_speed_consistency(data_points)
        idle_score = self._score_idle_time(data_points)
        
        total = (
            accel_score * 0.25 +
            brake_score * 0.25 +
            rpm_score * 0.20 +
            speed_score * 0.15 +
            idle_score * 0.15
        )
        
        return {
            'total_score': round(total, 1),
            'acceleration_score': round(accel_score, 1),
            'braking_score': round(brake_score, 1),
            'rpm_score': round(rpm_score, 1),
            'speed_consistency_score': round(speed_score, 1),
            'idle_score': round(idle_score, 1),
            'grade': self._get_grade(total)
        }
    
    def _score_acceleration(self, data_points: List[Dict[str, Any]]) -> float:
        """Score acceleration smoothness (0-100)."""
        if len(data_points) < 2:
            return 100
        
        harsh_accel_count = 0
        total_accel_events = 0
        
        for i in range(1, len(data_points)):
            prev = data_points[i-1]
            curr = data_points[i]
            
            speed_delta = curr.get('speed_mph', 0) - prev.get('speed_mph', 0)
            
            if speed_delta > 0:
                total_accel_events += 1
                
                if speed_delta > 8:
                    harsh_accel_count += 1
        
        if total_accel_events == 0:
            return 100
        
        harsh_ratio = harsh_accel_count / total_accel_events
        score = max(0, 100 - (harsh_ratio * 200))
        
        return score
    
    def _score_braking(self, data_points: List[Dict[str, Any]]) -> float:
        """Score braking smoothness (0-100)."""
        if len(data_points) < 2:
            return 100
        
        harsh_brake_count = 0
        total_brake_events = 0
        
        for i in range(1, len(data_points)):
            prev = data_points[i-1]
            curr = data_points[i]
            
            speed_delta = prev.get('speed_mph', 0) - curr.get('speed_mph', 0)
            
            if speed_delta > 0:
                total_brake_events += 1
                
                if speed_delta > 10:
                    harsh_brake_count += 1
        
        if total_brake_events == 0:
            return 100
        
        harsh_ratio = harsh_brake_count / total_brake_events
        score = max(0, 100 - (harsh_ratio * 200))
        
        return score
    
    def _score_rpm_usage(self, data_points: List[Dict[str, Any]]) -> float:
        """Score RPM efficiency (0-100)."""
        optimal_rpm_time = 0
        total_time = len(data_points)
        
        for point in data_points:
            rpm = point.get('rpm', 0)
            speed = point.get('speed_mph', 0)
            
            if speed > 0:
                if self.SONIC_LTZ_SPECS['optimal_rpm_min'] <= rpm <= self.SONIC_LTZ_SPECS['optimal_rpm_max']:
                    optimal_rpm_time += 1
        
        if total_time == 0:
            return 100
        
        score = (optimal_rpm_time / total_time) * 100
        
        return score
    
    def _score_speed_consistency(self, data_points: List[Dict[str, Any]]) -> float:
        """Score speed consistency (0-100)."""
        if len(data_points) < 10:
            return 100
        
        speeds = [p.get('speed_mph', 0) for p in data_points if p.get('speed_mph', 0) > 5]
        
        if not speeds:
            return 100
        
        avg_speed = sum(speeds) / len(speeds)
        
        variance = sum((s - avg_speed) ** 2 for s in speeds) / len(speeds)
        std_dev = math.sqrt(variance)
        
        coefficient_variation = (std_dev / avg_speed) if avg_speed > 0 else 0
        
        score = max(0, 100 - (coefficient_variation * 200))
        
        return score
    
    def _score_idle_time(self, data_points: List[Dict[str, Any]]) -> float:
        """Score idle time reduction (0-100)."""
        idle_count = 0
        total_count = len(data_points)
        
        for point in data_points:
            rpm = point.get('rpm', 0)
            speed = point.get('speed_mph', 0)
            
            if rpm > 600 and speed < 1:
                idle_count += 1
        
        if total_count == 0:
            return 100
        
        idle_ratio = idle_count / total_count
        score = max(0, 100 - (idle_ratio * 300))
        
        return score
    
    def _get_grade(self, score: float) -> str:
        """Get letter grade from score."""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def get_optimal_shift_point(self, current_rpm: int, throttle_percent: float) -> Tuple[bool, str]:
        """
        Determine if driver should shift gears.
        
        Returns:
            (should_shift, message)
        """
        if current_rpm > 3000:
            return True, f"Shift to higher gear at {current_rpm} RPM for better fuel economy"
        
        if current_rpm < 1200 and throttle_percent > 50:
            return True, "Downshift to avoid lugging the engine"
        
        return False, ""
    
    def get_optimal_highway_speed(self, current_speed: float) -> Dict[str, Any]:
        """Get optimal highway speed recommendation."""
        min_speed = self.SONIC_LTZ_SPECS['optimal_highway_speed_min']
        max_speed = self.SONIC_LTZ_SPECS['optimal_highway_speed_max']
        
        if current_speed < min_speed:
            mpg_loss = (min_speed - current_speed) * 0.1
            return {
                'optimal': False,
                'message': f"Increase speed to {min_speed}-{max_speed} MPH for optimal highway efficiency",
                'estimated_mpg_gain': round(mpg_loss, 1),
                'recommended_speed': min_speed
            }
        
        if current_speed > max_speed:
            mpg_loss = (current_speed - max_speed) * 0.15
            return {
                'optimal': False,
                'message': f"Reduce speed to {min_speed}-{max_speed} MPH for optimal highway efficiency",
                'estimated_mpg_loss': round(mpg_loss, 1),
                'recommended_speed': max_speed
            }
        
        return {
            'optimal': True,
            'message': f"Excellent! Maintaining optimal highway speed ({current_speed:.0f} MPH)",
            'estimated_mpg_gain': 0,
            'recommended_speed': current_speed
        }
    
    def calculate_fuel_cost(self, fuel_gallons: float, price_per_gallon: float) -> Dict[str, Any]:
        """Calculate fuel costs."""
        total_cost = fuel_gallons * price_per_gallon
        
        return {
            'fuel_gallons': round(fuel_gallons, 2),
            'price_per_gallon': price_per_gallon,
            'total_cost': round(total_cost, 2)
        }
    
    def calculate_cost_per_mile(self, distance_miles: float, fuel_gallons: float, 
                                price_per_gallon: float) -> float:
        """Calculate cost per mile."""
        if distance_miles <= 0:
            return 0
        
        total_cost = fuel_gallons * price_per_gallon
        cost_per_mile = total_cost / distance_miles
        
        return round(cost_per_mile, 3)
    
    def project_monthly_cost(self, avg_mpg: float, monthly_miles: float, 
                            price_per_gallon: float) -> Dict[str, Any]:
        """Project monthly fuel costs."""
        if avg_mpg <= 0:
            return {
                'monthly_miles': monthly_miles,
                'monthly_gallons': 0,
                'monthly_cost': 0,
                'annual_cost': 0
            }
        
        monthly_gallons = monthly_miles / avg_mpg
        monthly_cost = monthly_gallons * price_per_gallon
        annual_cost = monthly_cost * 12
        
        return {
            'monthly_miles': monthly_miles,
            'monthly_gallons': round(monthly_gallons, 2),
            'monthly_cost': round(monthly_cost, 2),
            'annual_cost': round(annual_cost, 2)
        }
    
    def get_range_estimate(self, current_mpg: float, fuel_remaining_gallons: float) -> Dict[str, Any]:
        """Estimate remaining range."""
        if current_mpg <= 0:
            current_mpg = self.SONIC_LTZ_SPECS['epa_combined_mpg']
        
        range_miles = current_mpg * fuel_remaining_gallons
        
        return {
            'range_miles': round(range_miles, 1),
            'fuel_remaining_gallons': round(fuel_remaining_gallons, 2),
            'estimated_mpg': round(current_mpg, 1)
        }
    
    def compare_to_epa(self, actual_mpg: float, driving_type: str = 'combined') -> Dict[str, Any]:
        """Compare actual MPG to EPA ratings."""
        if driving_type == 'highway':
            epa_mpg = self.SONIC_LTZ_SPECS['epa_highway_mpg']
        elif driving_type == 'city':
            epa_mpg = self.SONIC_LTZ_SPECS['epa_city_mpg']
        else:
            epa_mpg = self.SONIC_LTZ_SPECS['epa_combined_mpg']
        
        difference = actual_mpg - epa_mpg
        percent_diff = (difference / epa_mpg) * 100
        
        if percent_diff > 5:
            status = 'excellent'
            message = f"You're beating EPA ratings by {percent_diff:.1f}%!"
        elif percent_diff > 0:
            status = 'good'
            message = f"You're above EPA ratings by {percent_diff:.1f}%"
        elif percent_diff > -5:
            status = 'fair'
            message = f"You're slightly below EPA ratings by {abs(percent_diff):.1f}%"
        else:
            status = 'poor'
            message = f"You're below EPA ratings by {abs(percent_diff):.1f}%. Check driving habits."
        
        return {
            'actual_mpg': round(actual_mpg, 1),
            'epa_mpg': epa_mpg,
            'difference': round(difference, 1),
            'percent_difference': round(percent_diff, 1),
            'status': status,
            'message': message
        }
    
    def detect_coasting_opportunity(self, speed_mph: float, throttle_percent: float, 
                                   upcoming_stop: bool = False) -> Tuple[bool, str]:
        """Detect if driver should coast instead of accelerating."""
        if speed_mph > 35 and throttle_percent < 5:
            if upcoming_stop:
                return True, "Coast in neutral to save fuel - stop ahead detected"
            return True, "Good coasting technique! Maintain momentum."
        
        if speed_mph > 45 and throttle_percent > 70:
            return True, "Release throttle and coast to maintain speed"
        
        return False, ""
    
    def get_acceleration_recommendation(self, throttle_percent: float, 
                                       rpm: int, speed_mph: float) -> str:
        """Get acceleration recommendation."""
        if throttle_percent > 80:
            return "⚠️ Accelerating too hard - ease off throttle for better MPG"
        
        if throttle_percent > 60 and rpm > 3000:
            return "⚠️ High RPM + high throttle - shift up or reduce throttle"
        
        if throttle_percent > 50 and speed_mph < 20:
            return "💡 Gradual acceleration from stop saves 10-15% fuel"
        
        if 20 <= throttle_percent <= 40 and rpm < 2500:
            return "✅ Excellent acceleration technique!"
        
        return ""
