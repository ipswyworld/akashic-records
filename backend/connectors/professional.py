from connectors import BaseConnector
from models import UserActivity, UserLifeEntity
import uuid

class GitHubConnector(BaseConnector):
    """Syncs commits and code activity."""
    def sync(self, db_session) -> int:
        # Mocking GitHub API call
        print(f"Syncing GitHub for {self.user_id}...")
        return 1

class GmailConnector(BaseConnector):
    """Syncs email headers and meeting invites."""
    def sync(self, db_session) -> int:
        print(f"Syncing Gmail for {self.user_id}...")
        return 1

class JiraConnector(BaseConnector):
    """Syncs project tasks and deadlines."""
    def sync(self, db_session) -> int:
        print(f"Syncing Jira for {self.user_id}...")
        return 1
