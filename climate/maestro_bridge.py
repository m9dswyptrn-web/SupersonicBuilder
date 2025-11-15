#!/usr/bin/env python3
"""
Maestro RR2 Bridge
Communicates with Maestro RR2 service on port 7200 for CAN bus integration
"""

import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MaestroBridge:
    """Bridge to Maestro RR2 service for CAN bus communication."""
    
    def __init__(self, maestro_url: str = "http://localhost:7200"):
        """
        Initialize Maestro bridge.
        
        Args:
            maestro_url: URL of Maestro RR2 service
        """
        self.maestro_url = maestro_url
        self.connected = False
        self._check_connection()
    
    def _check_connection(self):
        """Check if Maestro service is available."""
        try:
            response = requests.get(f"{self.maestro_url}/health", timeout=2)
            self.connected = response.status_code == 200
        except Exception as e:
            logger.warning(f"Maestro RR2 service not available: {e}")
            self.connected = False
    
    def get_climate_status(self) -> Optional[Dict[str, Any]]:
        """
        Get current climate status from Maestro.
        
        Returns:
            Climate status dictionary or None
        """
        if not self.connected:
            self._check_connection()
            
        if not self.connected:
            return None
        
        try:
            response = requests.get(
                f"{self.maestro_url}/api/climate/status",
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('climate')
            
        except Exception as e:
            logger.error(f"Error getting climate status: {e}")
        
        return None
    
    def send_temperature_command(self, temp: float, zone: str = 'driver') -> bool:
        """
        Send temperature set command to Maestro.
        
        Args:
            temp: Temperature in Celsius
            zone: Zone identifier ('driver', 'passenger', 'rear')
        
        Returns:
            Success status
        """
        if not self.connected:
            return False
        
        try:
            response = requests.post(
                f"{self.maestro_url}/api/climate/temperature",
                json={'temperature': temp, 'zone': zone},
                timeout=2
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Error sending temperature command: {e}")
            return False
    
    def send_fan_command(self, speed: int) -> bool:
        """
        Send fan speed command to Maestro.
        
        Args:
            speed: Fan speed (0-7)
        
        Returns:
            Success status
        """
        if not self.connected:
            return False
        
        try:
            response = requests.post(
                f"{self.maestro_url}/api/climate/fan",
                json={'speed': speed},
                timeout=2
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Error sending fan command: {e}")
            return False
    
    def send_ac_command(self, enabled: bool) -> bool:
        """
        Send AC toggle command to Maestro.
        
        Args:
            enabled: AC state
        
        Returns:
            Success status
        """
        if not self.connected:
            return False
        
        try:
            response = requests.post(
                f"{self.maestro_url}/api/climate/ac",
                json={'enabled': enabled},
                timeout=2
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Error sending AC command: {e}")
            return False
    
    def send_recirculation_command(self, enabled: bool) -> bool:
        """
        Send recirculation toggle command to Maestro.
        
        Args:
            enabled: Recirculation state
        
        Returns:
            Success status
        """
        if not self.connected:
            return False
        
        try:
            response = requests.post(
                f"{self.maestro_url}/api/climate/recirculation",
                json={'enabled': enabled},
                timeout=2
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Error sending recirculation command: {e}")
            return False
    
    def send_defrost_command(self, location: str, enabled: bool) -> bool:
        """
        Send defrost command to Maestro.
        
        Args:
            location: 'front' or 'rear'
            enabled: Defrost state
        
        Returns:
            Success status
        """
        if not self.connected:
            return False
        
        try:
            response = requests.post(
                f"{self.maestro_url}/api/climate/defrost",
                json={'location': location, 'enabled': enabled},
                timeout=2
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Error sending defrost command: {e}")
            return False
    
    def send_auto_command(self, enabled: bool) -> bool:
        """
        Send auto climate command to Maestro.
        
        Args:
            enabled: Auto mode state
        
        Returns:
            Success status
        """
        if not self.connected:
            return False
        
        try:
            response = requests.post(
                f"{self.maestro_url}/api/climate/auto",
                json={'enabled': enabled},
                timeout=2
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Error sending auto command: {e}")
            return False
    
    def sync_state_from_vehicle(self) -> Optional[Dict[str, Any]]:
        """
        Sync climate state from vehicle via Maestro.
        
        Returns:
            Vehicle climate state or None
        """
        return self.get_climate_status()
    
    def get_vehicle_data(self) -> Optional[Dict[str, Any]]:
        """
        Get vehicle data including outside temperature.
        
        Returns:
            Vehicle data dictionary or None
        """
        if not self.connected:
            return None
        
        try:
            response = requests.get(
                f"{self.maestro_url}/api/vehicle/data",
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('vehicle')
            
        except Exception as e:
            logger.error(f"Error getting vehicle data: {e}")
        
        return None
