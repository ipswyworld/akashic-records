import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from models import SRSCard

class SRSEngine:
    """
    Implements a self-optimizing Spaced Repetition Engine.
    Extends SM-2 with 'Recall Stability' and 'Historical Acceleration'.
    """
    
    @staticmethod
    def calculate_next_review(card: SRSCard, quality: int, history: List[Dict] = None):
        """
        Calculates the next review date based on an optimized SM-2.
        quality: 0-5 (0 = forgot, 5 = perfect recall)
        """
        # Historical Acceleration (Phase 2)
        # If the user consistently gets 5s, we accelerate the interval expansion
        acceleration = 1.0
        if history and len(history) > 3:
            avg_quality = sum([h['quality'] for h in history[-3:]]) / 3
            if avg_quality > 4.5:
                acceleration = 1.2 # 20% faster expansion for high mastery
            elif avg_quality < 3.0:
                acceleration = 0.8 # Slow down for difficult topics

        if quality >= 3:
            if card.repetition == 0:
                card.interval = 1
            elif card.repetition == 1:
                card.interval = 6
            else:
                card.interval = round(card.interval * card.ease_factor * acceleration)
            
            card.repetition += 1
            # Adjust ease factor with a slight bias towards stability
            card.ease_factor = card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        else:
            card.repetition = 0
            card.interval = 1
            card.ease_factor = max(1.3, card.ease_factor - 0.2) # Penalty for forgetting
            
        if card.ease_factor < 1.3:
            card.ease_factor = 1.3
            
        card.next_review = datetime.datetime.utcnow() + datetime.timedelta(days=card.interval)
        return card

    @staticmethod
    def get_due_cards(db: Session, user_id: str):
        now = datetime.datetime.utcnow()
        return db.query(SRSCard).filter(
            SRSCard.user_id == user_id,
            SRSCard.next_review <= now
        ).all()
