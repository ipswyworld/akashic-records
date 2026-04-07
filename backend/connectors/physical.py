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

class WearableConnector(BaseConnector):
    """
    Phase 3: Affective Computing.
    Syncs health data (HRV, Sleep, Activity) and correlates with cognitive patterns.
    """
    def sync(self, db_session) -> int:
        print(f"Syncing Wearable Health Data for {self.user_id}...")
        # Mock retrieval of health metrics
        mock_data = {
            "hrv": 65,
            "sleep_score": 82,
            "steps": 4500,
            "stress_index": 0.4
        }
        # In a real implementation, we would save this to UserActivity or a new Health table
        return 1

