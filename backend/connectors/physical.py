from connectors import BaseConnector
from models import UserActivity

class HomeAssistantConnector(BaseConnector):
    """Syncs IoT sensor data (temp, humidity, lighting)."""
    def sync(self, db_session) -> int:
        print(f"Syncing Home Assistant for {self.user_id}...")
        return 1

class TeslaConnector(BaseConnector):
    """Syncs vehicle location and travel patterns."""
    def sync(self, db_session) -> int:
        print(f"Syncing Tesla for {self.user_id}...")
        return 1

class WeatherConnector(BaseConnector):
    """Syncs local weather and environmental conditions."""
    def sync(self, db_session) -> int:
        print(f"Syncing Weather for {self.user_id}...")
        return 1
