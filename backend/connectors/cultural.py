from connectors import BaseConnector
from models import UserActivity

class SpotifyConnector(BaseConnector):
    """Syncs 'Now Playing' or recently played tracks."""
    def sync(self, db_session) -> int:
        print(f"Syncing Spotify for {self.user_id}...")
        return 1

class YouTubeConnector(BaseConnector):
    """Syncs watch history and learning patterns."""
    def sync(self, db_session) -> int:
        print(f"Syncing YouTube for {self.user_id}...")
        return 1

class KindleConnector(BaseConnector):
    """Syncs book highlights and annotations."""
    def sync(self, db_session) -> int:
        print(f"Syncing Kindle for {self.user_id}...")
        return 1
