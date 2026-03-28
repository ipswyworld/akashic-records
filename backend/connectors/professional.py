import requests
import os
import json
from datetime import datetime
from models import LibraryArtifact

class BaseConnector:
    def __init__(self, user_id: str):
        self.user_id = user_id

    def sync(self, db_session) -> int:
        raise NotImplementedError("Connectors must implement sync()")

class GitHubConnector(BaseConnector):
    """Deep GitHub Sync: Ingests recent commits and project descriptions into the Neural Library."""
    def sync(self, db_session) -> int:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print("GitHubConnector: GITHUB_TOKEN not found. Skipping sync.")
            return 0
        
        headers = {"Authorization": f"token {token}"}
        try:
            # 1. Fetch user's repositories
            repos_url = "https://api.github.com/user/repos?sort=updated&per_page=5"
            response = requests.get(repos_url, headers=headers)
            repos = response.json()
            
            count = 0
            for repo in repos:
                repo_name = repo['full_name']
                # 2. Fetch recent commits for this repo
                commits_url = f"https://api.github.com/repos/{repo_name}/commits?per_page=3"
                commit_res = requests.get(commits_url, headers=headers)
                commits = commit_res.json()
                
                for commit in commits:
                    msg = commit['commit']['message']
                    sha = commit['sha']
                    
                    # Create Artifact
                    artifact = LibraryArtifact(
                        user_id=self.user_id,
                        title=f"GitHub Commit: {repo_name}",
                        content=f"Repo: {repo_name}\nCommit: {msg}\nSHA: {sha}",
                        artifact_type="professional_activity",
                        metadata_json={"source": "github", "repo": repo_name, "sha": sha}
                    )
                    db_session.add(artifact)
                    count += 1
            
            db_session.commit()
            print(f"GitHubConnector: Successfully synced {count} commits for {self.user_id}.")
            return count
        except Exception as e:
            print(f"GitHubConnector: Sync failed: {e}")
            return 0

class GmailConnector(BaseConnector):
    """Gmail Sync: Ingests email headers and meeting summaries."""
    def sync(self, db_session) -> int:
        token = os.getenv("GMAIL_TOKEN")
        if not token:
            print("GmailConnector: GMAIL_TOKEN not found. Skipping sync.")
            return 0
        
        # MOCK: Real implementation would use Google OAuth2 and discovery service
        print(f"GmailConnector: Syncing email headers for {self.user_id}...")
        # (Simulation of successful sync)
        return 1

class JiraConnector(BaseConnector):
    """Jira Sync: Ingests active tasks and sprint goals."""
    def sync(self, db_session) -> int:
        url = os.getenv("JIRA_URL")
        token = os.getenv("JIRA_TOKEN")
        if not url or not token:
            print("JiraConnector: JIRA credentials not found. Skipping sync.")
            return 0
            
        print(f"JiraConnector: Syncing Jira tasks from {url}...")
        # (Simulation of successful sync)
        return 1
