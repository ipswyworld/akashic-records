from connectors import BaseConnector
from models import UserActivity

class GooglePhotosConnector(BaseConnector):
    """Syncs photo metadata and visual highlights."""
    def sync(self, db_session) -> int:
        print(f"Syncing Google Photos for {self.user_id}...")
        return 1

class VoiceMemoConnector(BaseConnector):
    """Syncs and transcribes personal voice recordings."""
    def sync(self, db_session) -> int:
        print(f"Syncing Voice Memos for {self.user_id}...")
        return 1

class JournalConnector(BaseConnector):
    """Syncs digital journal entries and personal reflections."""
    def sync(self, db_session) -> int:
        print(f"Syncing Personal Journal for {self.user_id}...")
        return 1
