import datetime
from sqlalchemy.orm import Session
from models import UserActivity
from typing import Dict, Any

class TelemetryIngestEngine:
    """Handles high-frequency activity streams from browser extensions and OS sensors."""
    
    @staticmethod
    def log_activity(db: Session, user_id: str, activity_data: Dict[str, Any]):
        """Logs a single activity (e.g., page view, search, app switch)."""
        new_activity = UserActivity(
            user_id=user_id,
            activity_type=activity_data.get("type", "BROWSER_VIEW"),
            details_json={
                "url": activity_data.get("url"),
                "title": activity_data.get("title"),
                "app": activity_data.get("app"),
                "duration": activity_data.get("duration", 0),
                "timestamp": str(datetime.datetime.utcnow())
            },
            timestamp=datetime.datetime.utcnow()
        )
        db.add(new_activity)
        db.commit()
        return new_activity

    @staticmethod
    def get_recent_activity(db: Session, user_id: str, limit: int = 20):
        return db.query(UserActivity).filter(UserActivity.user_id == user_id).order_by(UserActivity.timestamp.desc()).limit(limit).all()
