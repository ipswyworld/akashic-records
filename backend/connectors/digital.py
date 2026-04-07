from typing import List, Dict, Any, Optional
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
    """
    Phase 2: Social Media Shadow Driver.
    Syncs Twitter/X and Reddit activity into the Knowledge Graph.
    """
    def sync(self, db_session) -> int:
        print(f"ShadowDriver: Syncing Social Media (X/Reddit) for {self.user_id}...")
        # Mock retrieval
        return 1

class GenericSocialConnector(BaseConnector):
    """
    The 'Universal Social Adapter'.
    Can be dynamically configured with an API endpoint, headers, and a mapping schema
    to connect to ANY social media platform with an accessible API.
    """
    def __init__(self, user_id: str, platform_name: str, api_config: Dict[str, Any]):
        super().__init__(user_id)
        self.platform_name = platform_name
        self.api_url = api_config.get("url")
        self.headers = api_config.get("headers", {})
        self.mapping = api_config.get("mapping", {"content": "text", "title": "id"})

    def sync(self, db_session) -> int:
        if not self.api_url:
            print(f"GenericSocial: No URL configured for {self.platform_name}.")
            return 0
            
        print(f"GenericSocial: Connecting to {self.platform_name} for {self.user_id}...")
        try:
            import requests
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            data = response.json()
            
            # If it's a list of posts
            posts = data if isinstance(data, list) else data.get("posts", [])
            count = 0
            for post in posts[:10]:
                content = post.get(self.mapping.get("content", "text"), "")
                title = f"{self.platform_name} Post: {post.get(self.mapping.get('title', 'id'), 'Unknown')}"
                
                # We defer to the main ingest_library_artifact logic
                # In a real sync, this would call the main.py function
                count += 1
            
            print(f"GenericSocial: Successfully synced {count} items from {self.platform_name}.")
            return count
        except Exception as e:
            print(f"GenericSocial: Sync failed for {self.platform_name}: {e}")
            return 0

class SlackShadowDriver(BaseConnector):
    """
    Phase 2: Slack Shadow Driver.
    Syncs recent messages from prioritized channels to the Knowledge Graph.
    """
    def sync(self, db_session) -> int:
        print(f"ShadowDriver: Syncing Slack workspace for {self.user_id}...")
        # Mock retrieval of 5 recent messages
        mock_messages = [
            {"channel": "general", "user": "jb", "text": "Let's focus on the neural mesh implementation today."},
            {"channel": "dev", "user": "alice", "text": "I've pushed the new P2P protocol updates."},
        ]
        count = 0
        for msg in mock_messages:
            # In a real implementation, we would ingest these as LibraryArtifacts
            # For now, we simulate the 'Hands' reaching into Slack
            count += 1
        return count

class ObsidianShadowDriver(BaseConnector):
    """
    Phase 2: Obsidian Shadow Driver.
    Syncs local markdown notes and detects frontmatter tags for Graph-RAG.
    """
    def sync(self, db_session) -> int:
        print(f"ShadowDriver: Syncing Obsidian Vault for {self.user_id}...")
        # Mock vault scanning
        mock_files = ["Personal/Manifesto.md", "Projects/Akasha/Roadmap.md"]
        return len(mock_files)

class SemanticClipboard(BaseConnector):
    """
    Phase 2: Semantic Clipboard.
    Captures clipboard content and automatically classifies intent.
    """
    def process_clip(self, text: str, db_session) -> Dict[str, Any]:
        print(f"SemanticClipboard: Processing intent for '{text[:20]}...'")
        # Logic to determine if this is a Task, a Fact, or a Reference
        if "TODO" in text.upper() or "FIX" in text.upper():
            return {"intent": "TASK", "content": text}
        return {"intent": "KNOWLEDGE", "content": text}

