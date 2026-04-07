import logging
import subprocess
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class EnvironmentalSensor:
    """
    Environmental Perception: Detects physical and network context.
    """
    @staticmethod
    def get_wifi_ssid() -> Optional[str]:
        """Detects current WiFi SSID (Win32 specific)."""
        try:
            import pywifi
            # Simplified check using netsh
            output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8', errors='ignore')
            for line in output.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    return line.split(":")[1].strip()
        except:
            pass
        return None

    @staticmethod
    def get_location_context() -> Dict[str, Any]:
        """Approximates location via IP."""
        try:
            # Use a free API for IP-based geolocation
            response = requests.get('https://ipapi.co/json/', timeout=5)
            data = response.json()
            return {
                "city": data.get("city"),
                "country": data.get("country_name"),
                "is_home": False # Default
            }
        except:
            return {"city": "Unknown", "country": "Unknown", "is_home": False}

    def detect_all(self) -> Dict[str, Any]:
        return {
            "ssid": self.get_wifi_ssid(),
            "location": self.get_location_context()
        }
