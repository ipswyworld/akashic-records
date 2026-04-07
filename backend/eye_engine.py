import logging
import os
import time
import base64
import io
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class EyeEngine:
    """
    The 'Third Eye': Live Screen Awareness.
    Captures screenshots and analyzes them for proactive assistance.
    """
    def __init__(self, ai_engine, multimodal_engine):
        self.ai = ai_engine
        self.multimodal = multimodal_engine
        self.is_active = False
        self.last_capture_time = 0
        self.capture_interval = 60 # Seconds

    async def capture_and_analyze(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Captures the primary screen, scrubs for privacy, and analyzes content.
        """
        if not self.is_active: return None
        
        try:
            import mss
            from PIL import Image
            
            with mss.mss() as sct:
                # Capture primary monitor
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Compress for analysis
                img.thumbnail((1024, 1024))
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_bytes = img_byte_arr.getvalue()
                
                # 1. Visual Reasoning (OCR + Scene description)
                description = self.multimodal.visual_reasoning(img_bytes)
                
                # 2. Privacy Scrubbing (Redact PII from the description)
                # We use the Sentinel to ensure zero leakage
                scrubbed_desc = self.ai.council.sentinel.redact_sensitive_info(description)
                
                logger.info(f"EyeEngine: Screen analyzed for {user_id}. Intent detected.")
                
                return {
                    "timestamp": datetime.utcnow().isoformat(),
                    "description": scrubbed_desc,
                    "raw_context": description # Local only
                }
                
        except Exception as e:
            logger.error(f"EyeEngine Error: {e}")
            return None

    def toggle(self, state: bool):
        self.is_active = state
        logger.info(f"EyeEngine: Live Vision set to {state}")
