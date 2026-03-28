from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import os
import hashlib
import hmac
from datetime import datetime

router = APIRouter(prefix="/webhook", tags=["messenger"])

class WebhookMessage(BaseModel):
    """Simulating Twilio/Signal/Telegram webhook format."""
    MessageSid: Optional[str] = None
    SmsSid: Optional[str] = None
    AccountSid: Optional[str] = None
    From: str # The sender identifier
    To: Optional[str] = None
    Body: str # The message content
    Signature: Optional[str] = None # For verifying sender authenticity
    user_id: Optional[str] = "system_user"

def verify_sovereign_signature(body: str, signature: str) -> bool:
    """
    Verifies that the message came from an authorized device using an HMAC-SHA256 signature.
    The secret key should be shared between Akasha and the mobile/remote client.
    """
    secret = os.getenv("SOVEREIGN_BRIDGE_SECRET", "default_secret_change_me")
    if not signature: return False
    
    expected = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@router.post("/message")
async def receive_message(request: WebhookMessage, req: Request):
    """
    The Sovereign Bridge: Securely routes remote commands to the local HeadArchivist.
    Supports encrypted/verified triggers for 'Ask AI' and 'System Commands' while away.
    """
    # 1. Security Check (Sovereign Mode)
    if os.getenv("REQUIRE_BRIDGE_SIGNATURE", "false").lower() == "true":
        if not verify_sovereign_signature(request.Body, request.Signature):
            raise HTTPException(status_code=401, detail="Unauthorized Sovereign Bridge Access")

    ai_engine = getattr(req.app.state, "ai_engine", None)
    if not ai_engine:
        from ai_engine import AIEngine
        ai_engine = AIEngine()

    raw_text = request.Body
    print(f"Sovereign Bridge: Received remote input from {request.From}")

    # 2. Check for Direct Commands (e.g., "Ask: ...", "Cmd: ...")
    if raw_text.lower().startswith("ask:"):
        query = raw_text[4:].strip()
        # Perform Graph-RAG Search and Synthesis
        # (This simulates the /jarvis/ask flow remotely)
        vector_results = ai_engine.search_vectors(query, user_id=request.user_id)
        docs = vector_results.get("documents", [[]])[0]
        synthesis = ai_engine.synthesize_graph_rag(query, docs, [])
        
        return {
            "status": "SUCCESS",
            "type": "AI_RESPONSE",
            "payload": {
                "answer": synthesis.get("answer"),
                "monologue": synthesis.get("monologue")
            }
        }
    
    elif raw_text.lower().startswith("cmd:"):
        # Remote System Command (Highly sensitive, requires verified signature)
        if os.getenv("REQUIRE_BRIDGE_SIGNATURE", "false").lower() != "true":
             return {"status": "ERROR", "message": "Remote commands require SOVEREIGN_BRIDGE_SECRET verification."}
             
        cmd_request = raw_text[4:].strip()
        result = ai_engine.council.system_shell.execute(cmd_request)
        return {"status": "SUCCESS", "type": "SHELL_OUTPUT", "payload": result}

    # 3. Default: Ingest as a new artifact
    analysis = ai_engine.analyze_artifact(raw_text)
    
    # Store in Vector DB
    artifact_id = f"remote_{int(datetime.utcnow().timestamp())}"
    ai_engine.store_vector(artifact_id, raw_text, analysis, user_id=request.user_id)

    return {
        "status": "SUCCESS",
        "type": "INGESTION_ACK",
        "artifact_category": analysis.get("category"),
        "summary": analysis.get("summary")
    }
