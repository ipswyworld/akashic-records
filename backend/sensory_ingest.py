import logging
import io
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SensoryIngestEngine:
    """
    Sensory Ingestion Engine: The 'Eyes and Ears' of Akasha.
    Manages real-time audio/visual streams and environmental context.
    """
    def __init__(self, ai_engine, multimodal_engine, graph_engine=None):
        self.ai = ai_engine
        self.multimodal = multimodal_engine
        self.graph = graph_engine
        self.is_listening = False
        self.last_visual_context = ""

    async def ingest_audio_stream(self, audio_chunk: bytes, user_id: str):
        """
        Processes a chunk of audio from the WebSocket or Hardware Bridge.
        """
        try:
            # 1. Transcribe
            text = self.multimodal.transcribe_audio(audio_chunk)
            
            if len(text.strip()) > 10:
                logger.info(f"Sensory: Audio captured: {text[:100]}...")
                
                # Bridge 3: Real-time Graph Context from Audio
                if self.graph:
                    try:
                        analysis = self.ai.analyze_artifact(text, privacy_tier="PRIVATE")
                        node_id = f"audio_{int(datetime.utcnow().timestamp())}"
                        self.graph.create_artifact_node(node_id, "Live Audio Stream", "sensory_input", user_id)
                        self.graph.ingest_triplets(node_id, analysis["graph_triplets"], user_id)
                    except Exception as ge:
                        logger.error(f"Sensory: Graph Bridge Error (Audio): {ge}")

                # 2. Analyze Emotional Tone (Emotional Osmosis)
                tone = self.multimodal.analyze_tone(audio_chunk)
                
                # --- Phase 3: Affective Analysis ---
                affect = self.multimodal.analyze_affect(audio_chunk)
                # ----------------------------------
                
                # 3. Trigger Proactive Response if 'URGENT' or high stress
                if tone["primary_emotion"] == "URGENT" or affect["stress"] > 0.8:
                    logger.warning("Sensory: High Stress or URGENT tone detected. Flagging for Head Archivist.")
                
                return {
                    "text": text,
                    "tone": tone,
                    "affect": affect,
                    "timestamp": str(datetime.utcnow())
                }
            return None
        except Exception as e:
            logger.error(f"Sensory: Audio ingestion error: {e}")
            return None

    async def capture_visual_context(self, image_bytes: bytes, user_id: str):
        """
        Processes a screen snap or webcam frame to update the 'Working Context'.
        """
        try:
            # 1. Visual Reasoning (LLaVA)
            description = self.multimodal.visual_reasoning(image_bytes)
            self.last_visual_context = description
            
            logger.info(f"Sensory: Visual Context Updated: {description[:100]}...")
            
            # 2. Extract Graph Entities from Vision
            visual_triplets = self.ai.council.get_agent("image_entity").extract_visual_triplets(description)
            
            # Bridge 3: Real-time Graph Context from Vision
            if self.graph and visual_triplets:
                try:
                    node_id = f"vision_{int(datetime.utcnow().timestamp())}"
                    self.graph.create_artifact_node(node_id, "Live Visual Context", "sensory_input", user_id)
                    self.graph.ingest_triplets(node_id, visual_triplets, user_id)
                except Exception as ge:
                    logger.error(f"Sensory: Graph Bridge Error (Vision): {ge}")

            return {
                "description": description,
                "triplets": visual_triplets,
                "timestamp": str(datetime.utcnow())
            }
        except Exception as e:
            logger.error(f"Sensory: Visual ingestion error: {e}")
            return None

    def get_current_context(self) -> str:
        """Returns the latest environmental context for the Oracle."""
        return f"Environmental Context: {self.last_visual_context}"
