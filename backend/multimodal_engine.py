import whisper
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import io
import os
import uuid
import datetime
from typing import Optional

class MultimodalEngine:
    def __init__(self):
        # 1. Whisper for Audio Memories (Speech-to-Text)
        self.whisper_model = whisper.load_model("base")
        
        # 2. CLIP for Visual Memories (Image-Text Embedding)
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # S3 / Minio Client for raw assets
        import boto3
        self.s3 = boto3.client(
            's3',
            endpoint_url=os.getenv("S3_URL", "http://localhost:9000"),
            aws_access_key_id=os.getenv("S3_USER", "akasha_admin"),
            aws_secret_access_key=os.getenv("S3_PASS", "akasha_password")
        )

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        """Transcribe audio into a text memory."""
        # Note: Whisper expects a file path or array
        with open("tmp_audio.wav", "wb") as f:
            f.write(audio_bytes)
        result = self.whisper_model.transcribe("tmp_audio.wav")
        os.remove("tmp_audio.wav")
        return result["text"]

    def speak(self, text: str, voice_id: Optional[str] = None) -> str:
        """
        Sovereign Voice: Converts AI thoughts into speech locally.
        Uses the Vocalist agent from the Council.
        """
        try:
            from librarians import Vocalist
            vocalist = Vocalist()
            if voice_id:
                vocalist.set_voice(voice_id)
            output_path = f"akasha_data/speech_{uuid.uuid4().hex[:8]}.wav"
            vocalist.speak(text, output_path)
            return output_path
        except Exception as e:
            print(f"TTS Error: {e}")
            return ""

    def analyze_tone(self, audio_bytes: bytes) -> dict:
        """
        VI.31: Emotional Osmosis - Detects emotional tone from audio pitch/energy.
        In production, use a model like wav2vec2-emotion.
        """
        # Mock emotional tone analysis
        import random
        emotions = ["CALM", "URGENT", "EXCITED", "THOUGHTFUL", "STRESSED"]
        return {
            "primary_emotion": random.choice(emotions),
            "energy_level": random.uniform(0.1, 1.0),
            "timestamp": str(datetime.datetime.utcnow())
        }

    def analyze_affect(self, audio_bytes: bytes) -> dict:
        """
        Phase 3: Affective Computing.
        Analyzes audio for stress, fatigue, and excitement.
        """
        import random
        # In a real implementation, this would use a specialized model.
        stress_level = random.uniform(0.0, 1.0)
        fatigue_level = random.uniform(0.0, 1.0)
        excitement_level = random.uniform(0.0, 1.0)
        
        return {
            "stress": stress_level,
            "fatigue": fatigue_level,
            "excitement": excitement_level,
            "detected_mood": "Stressed" if stress_level > 0.7 else "Calm"
        }

    def process_image(self, image_bytes: bytes) -> dict:
        """Analyze image and return its visual features."""
        image = Image.open(io.BytesIO(image_bytes))
        inputs = self.clip_processor(images=image, return_tensors="pt")
        outputs = self.clip_model.get_image_features(**inputs)
        return {
            "features": outputs.tolist(),
            "description": "Visual memory captured in the Akasha"
        }

    def visual_reasoning(self, image_bytes: bytes, model: str = "moondream") -> str:
        """Uses a Vision LLM (Moondream/Llava) to describe the image content for the librarians."""
        try:
            import requests
            import base64
            
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            payload = {
                "model": model,
                "prompt": "Analyze this image in detail. If it's a technical diagram, explain the architecture. If it's a screenshot, transcribe the key text and intent.",
                "stream": False,
                "images": [encoded_image]
            }
            
            # Try preferred model (moondream), fallback to llava if needed
            response = requests.post(f"{os.getenv('OLLAMA_URL', 'http://localhost:11434')}/api/generate", json=payload, timeout=45)
            if response.status_code != 200 and model == "moondream":
                payload["model"] = "llava"
                response = requests.post(f"{os.getenv('OLLAMA_URL', 'http://localhost:11434')}/api/generate", json=payload, timeout=60)
                
            if response.status_code == 200:
                return response.json().get("response", "")
        except Exception as e:
            print(f"Vision Engine Error: {e}")
        return "Visual analysis unavailable."

    def store_raw_asset(self, asset_id: str, data: bytes, bucket: str = "memories") -> str:
        """Secure raw asset in S3-compatible storage."""
        try:
            self.s3.put_object(Bucket=bucket, Key=asset_id, Body=data)
            return f"{bucket}/{asset_id}"
        except Exception as e:
            print(f"S3 Storage Error: {e}")
            return "LocalStore"
