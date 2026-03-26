from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json

router = APIRouter(prefix="/webhook", tags=["messenger"])

class WebhookMessage(BaseModel):
    """Simulating Twilio webhook format for WhatsApp/Telegram."""
    MessageSid: Optional[str] = None
    SmsSid: Optional[str] = None
    AccountSid: Optional[str] = None
    From: str # The sender identifier (e.g., "whatsapp:+123456789")
    To: Optional[str] = None
    Body: str # The message content
    NumMedia: int = 0
    MediaUrl0: Optional[str] = None # Audio/Image attachment URL
    user_id: Optional[str] = "system_user"

@router.post("/message")
async def receive_message(request: WebhookMessage, req: Request):
    """
    Exposes a generic /webhook/message endpoint.
    Extracts text/audio and routes it to the HeadArchivist for ingestion.
    """
    # Access ai_engine from app state to avoid circular imports
    ai_engine = getattr(req.app.state, "ai_engine", None)
    if not ai_engine:
        # Fallback if not set in state (though it should be)
        from ai_engine import AIEngine
        ai_engine = AIEngine()

    raw_text = request.Body
    if request.MediaUrl0:
        raw_text += f"\n[Media Attachment: {request.MediaUrl0}]"

    # Route to HeadArchivist via AIEngine
    # Ingestion into 3D Graph and Vector DB happens here
    analysis = ai_engine.analyze_artifact(raw_text)
    
    # Simulate saving to database if needed, but analyze_artifact already does heavy lifting
    # For a full ingestion, we'd call the same logic as /ingest/clipper but for messenger
    
    return {
        "status": "SUCCESS",
        "message": "Message received and routed to HeadArchivist",
        "from": request.From,
        "artifact_category": analysis.get("category"),
        "summary": analysis.get("summary")
    }
