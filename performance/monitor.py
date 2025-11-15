#!/usr/bin/env python3
"""
Snapdragon Performance Monitor
Simulates monitoring of Qualcomm Snapdragon 8-core processor
"""

import random
import time
import math
from datetime import datetime
from typing import Dict, List


class SnapdragonMonitor:
    """Monitor for Qualcomm Snapdragon processor performance."""
    
    def __init__(self):
        """Initialize the monitor."""
        self.cpu_cores = 8
        self.cpu_base_freq = 2.0
        self.total_ram_gb = 12
        self.total_storage_gb = 256
        
        self.performance_mode = 'balanced'
        
        self.base_cpu_usage = [10, 15, 8, 12, 20, 18, 10, 14]
        self.base_temp = 45.0
        self.base_battery_voltage = 3.85
        
        self.mock_processes = [
            {'name': 'Android System', 'cpu': 5.2, 'mem': 450},
            {'name': 'Chrome Browser', 'cpu': 12.5, 'mem': 890},
            {'name': 'Spotify', 'cpu': 3.1, 'mem': 320},
            {'name': 'Google Play Services', 'cpu': 2.8, 'mem': 280},
            {'name': 'WhatsApp', 'cpu': 1.5, 'mem': 210},
            {'name': 'Instagram', 'cpu': 8.3, 'mem': 540},
            {'name': 'YouTube', 'cpu': 15.2, 'mem': 720},
            {'name': 'Gmail', 'cpu': 1.2, 'mem': 180},
            {'name': 'Maps', 'cpu': 4.5, 'mem': 410},
            {'name': 'Camera', 'cpu': 7.8, 'mem': 380}
        ]
        
        self.start_time = time.time()
    
    def get_cpu_metrics(self) -> Dict:
        """Get CPU performance metrics."""
        variation = math.sin(time.time() / 10) * 10
        
        if self.performance_mode == 'high_performance':
            multiplier = 1.3
            freq_multiplier = 1.2
        elif self.performance_mode == 'power_save':
            multiplier = 0.6
            freq_multiplier = 0.7
        else:
            multiplier = 1.0
            freq_multiplier = 1.0
        
        core_usage = []
        for i, base in enumerate(self.base_cpu_usage):
            usage = base * multiplier + variation + random.uniform(-5, 5)
            usage = max(0, min(100, usage))
            core_usage.append(round(usage, 1))
        
        total_usage = sum(core_usage) / len(core_usage)
        
        cpu_freq = self.cpu_base_freq * freq_multiplier + random.uniform(-0.1, 0.1)
        cpu_freq = max(0.8, min(2.5, cpu_freq))
        
        status = 'normal'
        if total_usage > 80:
            status = 'high'
        elif total_usage > 90:
            status = 'critical'
        
        return {
            'core_usage': core_usage,
            'total_usage': round(total_usage, 1),
            'frequency_ghz': round(cpu_freq, 2),
            'core_count': self.cpu_cores,
            'status': status
        }
    
    def get_gpu_metrics(self) -> Dict:
        """Get GPU performance metrics."""
        base_gpu_usage = 35 if self.performance_mode == 'high_performance' else 20
        gpu_usage = base_gpu_usage + random.uniform(-10, 15)
        gpu_usage = max(0, min(100, gpu_usage))
        
        base_gpu_freq = 800 if self.performance_mode == 'high_performance' else 500
        gpu_freq = base_gpu_freq + random.uniform(-50, 50)
        
        gpu_temp = 45 + (gpu_usage * 0.4) + random.uniform(-2, 2)
        
        opengl_fps = 60 - (gpu_usage * 0.2) + random.uniform(-5, 5)
        opengl_fps = max(30, min(120, opengl_fps))
        
        status = 'normal'
        if gpu_usage > 80:
            status = 'high'
        elif gpu_temp > 70:
            status = 'critical'
        
        return {
            'usage_percent': round(gpu_usage, 1),
            'frequency_mhz': round(gpu_freq, 0),
            'temperature_c': round(gpu_temp, 1),
            'opengl_fps': round(opengl_fps, 1),
            'status': status
        }
    
    def get_memory_metrics(self) -> Dict:
        """Get RAM usage metrics."""
        base_usage = 5.5 if self.performance_mode == 'power_save' else 7.2
        used_gb = base_usage + random.uniform(-0.5, 0.8)
        used_gb = max(2, min(self.total_ram_gb * 0.95, used_gb))
        
        free_gb = self.total_ram_gb - used_gb
        usage_percent = (used_gb / self.total_ram_gb) * 100
        
        swap_used_mb = random.uniform(100, 500) if usage_percent > 70 else random.uniform(0, 100)
        
        app_memory = []
        sorted_processes = sorted(self.mock_processes, key=lambda x: x['mem'], reverse=True)
        for proc in sorted_processes[:5]:
            app_memory.append({
                'app': proc['name'],
                'memory_mb': proc['mem'] + random.uniform(-50, 50)
            })
        
        status = 'normal'
        if usage_percent > 80:
            status = 'high'
        elif usage_percent > 90:
            status = 'critical'
        
        return {
            'total_gb': self.total_ram_gb,
            'used_gb': round(used_gb, 2),
            'free_gb': round(free_gb, 2),
            'usage_percent': round(usage_percent, 1),
            'swap_used_mb': round(swap_used_mb, 1),
            'app_memory': app_memory,
            'status': status
        }
    
    def get_storage_metrics(self) -> Dict:
        """Get storage usage metrics."""
        apps_gb = 45 + random.uniform(-2, 2)
        music_gb = 12 + random.uniform(-1, 1)
        videos_gb = 38 + random.uniform(-3, 3)
        photos_gb = 25 + random.uniform(-2, 2)
        system_gb = 18
        other_gb = 15 + random.uniform(-2, 2)
        
        used_gb = apps_gb + music_gb + videos_gb + photos_gb + system_gb + other_gb
        free_gb = self.total_storage_gb - used_gb
        usage_percent = (used_gb / self.total_storage_gb) * 100
        
        status = 'normal'
        if free_gb < 20:
            status = 'warning'
        elif free_gb < 10:
            status = 'critical'
        
        return {
            'total_gb': self.total_storage_gb,
            'used_gb': round(used_gb, 1),
            'free_gb': round(free_gb, 1),
            'usage_percent': round(usage_percent, 1),
            'by_category': {
                'apps': round(apps_gb, 1),
                'music': round(music_gb, 1),
                'videos': round(videos_gb, 1),
                'photos': round(photos_gb, 1),
                'system': round(system_gb, 1),
                'other': round(other_gb, 1)
            },
            'status': status
        }
    
    def get_network_metrics(self) -> Dict:
        """Get network connectivity metrics."""
        is_wifi = random.choice([True, False])
        
        if is_wifi:
            signal_strength = random.randint(65, 100)
            connection_type = 'WiFi'
            speed_down = random.uniform(50, 150)
            speed_up = random.uniform(20, 50)
        else:
            signal_strength = random.randint(50, 95)
            connection_type = random.choice(['4G', '5G'])
            if connection_type == '5G':
                speed_down = random.uniform(100, 300)
                speed_up = random.uniform(30, 80)
            else:
                speed_down = random.uniform(20, 60)
                speed_up = random.uniform(5, 20)
        
        uptime_hours = (time.time() - self.start_time) / 3600
        data_used_mb = uptime_hours * random.uniform(10, 30)
        
        status = 'connected'
        if signal_strength < 30:
            status = 'poor'
        elif signal_strength < 50:
            status = 'fair'
        
        return {
            'connection_type': connection_type,
            'signal_strength': signal_strength,
            'wifi_connected': is_wifi,
            'speed_down_mbps': round(speed_down, 1),
            'speed_up_mbps': round(speed_up, 1),
            'data_used_mb': round(data_used_mb, 1),
            'status': status
        }
    
    def get_temperature_metrics(self) -> Dict:
        """Get temperature metrics."""
        cpu_usage = self.get_cpu_metrics()['total_usage']
        gpu_usage = self.get_gpu_metrics()['usage_percent']
        
        load_factor = (cpu_usage + gpu_usage) / 200
        
        soc_temp = self.base_temp + (load_factor * 25) + random.uniform(-2, 3)
        battery_temp = self.base_temp - 5 + (load_factor * 15) + random.uniform(-1, 2)
        
        is_throttling = soc_temp > 75
        
        status = 'normal'
        if soc_temp > 65:
            status = 'warm'
        elif soc_temp > 75:
            status = 'hot'
        elif soc_temp > 85:
            status = 'critical'
        
        return {
            'soc_temp_c': round(soc_temp, 1),
            'battery_temp_c': round(battery_temp, 1),
            'ambient_temp_c': round(25 + random.uniform(-2, 2), 1),
            'thermal_throttling': is_throttling,
            'status': status
        }
    
    def get_battery_metrics(self) -> Dict:
        """Get battery metrics."""
        is_charging = random.choice([True, False, False])
        
        base_voltage = self.base_battery_voltage
        if is_charging:
            voltage = base_voltage + random.uniform(0.1, 0.3)
            current_ma = random.uniform(-2000, -1000)
        else:
            voltage = base_voltage + random.uniform(-0.1, 0.1)
            current_ma = random.uniform(300, 1500)
        
        battery_percent = 65 + random.uniform(-10, 15)
        battery_percent = max(0, min(100, battery_percent))
        
        if is_charging:
            estimated_runtime_min = None
        else:
            battery_capacity_mah = 4500
            runtime_hours = (battery_percent / 100) * battery_capacity_mah / current_ma
            estimated_runtime_min = runtime_hours * 60
        
        status = 'good'
        if battery_percent < 20:
            status = 'low'
        elif battery_percent < 10:
            status = 'critical'
        
        return {
            'voltage_v': round(voltage, 2),
            'current_ma': round(current_ma, 0),
            'battery_percent': round(battery_percent, 1),
            'is_charging': is_charging,
            'estimated_runtime_min': round(estimated_runtime_min, 0) if estimated_runtime_min else None,
            'capacity_mah': 4500,
            'status': status
        }
    
    def get_process_metrics(self) -> Dict:
        """Get running processes."""
        processes = []
        
        for proc in self.mock_processes:
            cpu = proc['cpu'] + random.uniform(-2, 2)
            cpu = max(0, min(100, cpu))
            
            mem = proc['mem'] + random.uniform(-20, 20)
            mem = max(50, mem)
            
            processes.append({
                'name': proc['name'],
                'pid': random.randint(1000, 9999),
                'cpu_percent': round(cpu, 1),
                'memory_mb': round(mem, 1)
            })
        
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        return {
            'total_count': len(processes) + random.randint(50, 100),
            'top_processes': processes[:10]
        }
    
    def get_all_metrics(self) -> Dict:
        """Get all performance metrics."""
        return {
            'cpu': self.get_cpu_metrics(),
            'gpu': self.get_gpu_metrics(),
            'memory': self.get_memory_metrics(),
            'storage': self.get_storage_metrics(),
            'network': self.get_network_metrics(),
            'temperature': self.get_temperature_metrics(),
            'battery': self.get_battery_metrics(),
            'processes': self.get_process_metrics(),
            'performance_mode': self.performance_mode,
            'timestamp': datetime.now().isoformat()
        }
    
    def set_performance_mode(self, mode: str):
        """Set performance mode."""
        valid_modes = ['high_performance', 'balanced', 'power_save']
        if mode in valid_modes:
            self.performance_mode = mode
            return True
        return False
    
    def get_system_health(self) -> Dict:
        """Get overall system health status."""
        metrics = self.get_all_metrics()
        
        issues = []
        warnings = []
        
        if metrics['cpu']['total_usage'] > 90:
            issues.append('CPU usage critically high')
        elif metrics['cpu']['total_usage'] > 80:
            warnings.append('CPU usage high')
        
        if metrics['gpu']['usage_percent'] > 90:
            issues.append('GPU usage critically high')
        
        if metrics['memory']['usage_percent'] > 90:
            issues.append('Memory usage critically high')
        elif metrics['memory']['usage_percent'] > 80:
            warnings.append('Memory usage high')
        
        if metrics['storage']['free_gb'] < 10:
            issues.append('Storage critically low')
        elif metrics['storage']['free_gb'] < 20:
            warnings.append('Storage running low')
        
        if metrics['temperature']['soc_temp_c'] > 85:
            issues.append('SoC temperature critical')
        elif metrics['temperature']['soc_temp_c'] > 75:
            warnings.append('SoC temperature high')
        
        if metrics['temperature']['thermal_throttling']:
            issues.append('Thermal throttling active')
        
        if metrics['battery']['battery_percent'] < 10:
            issues.append('Battery critically low')
        elif metrics['battery']['battery_percent'] < 20:
            warnings.append('Battery low')
        
        if issues:
            overall_status = 'critical'
        elif warnings:
            overall_status = 'warning'
        else:
            overall_status = 'healthy'
        
        return {
            'status': overall_status,
            'issues': issues,
            'warnings': warnings,
            'metrics_summary': {
                'cpu_usage': metrics['cpu']['total_usage'],
                'gpu_usage': metrics['gpu']['usage_percent'],
                'memory_usage': metrics['memory']['usage_percent'],
                'storage_free': metrics['storage']['free_gb'],
                'temperature': metrics['temperature']['soc_temp_c'],
                'battery': metrics['battery']['battery_percent']
            }
        }
