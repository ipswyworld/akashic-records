from connectors import BaseConnector
from models import UserActivity

class BrowserHistoryConnector(BaseConnector):
    """Syncs browser history and active tab telemetry."""
    def sync(self, db_session) -> int:
        print(f"Syncing Browser History for {self.user_id}...")
        return 1

class GoogleMapsConnector(BaseConnector):
    """Syncs location history and place patterns."""
    def sync(self, db_session) -> int:
        print(f"Syncing Google Maps for {self.user_id}...")
        return 1

class SocialMediaConnector(BaseConnector):
    """Syncs Twitter/X and Reddit activity."""
    def sync(self, db_session) -> int:
        print(f"Syncing Social Media for {self.user_id}...")
        return 1
