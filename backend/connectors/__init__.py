from typing import List, Dict, Any

class BaseConnector:
    def __init__(self, user_id: str):
        self.user_id = user_id

    def sync(self, db_session) -> int:
        raise NotImplementedError
