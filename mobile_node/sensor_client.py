import requests
import json
import time
import random
import base64

class SensorClient:
    """Simulates a lightweight mobile app sending GPS and audio data to Akasha."""
    def __init__(self, endpoint="http://localhost:8001/node/sensory", user_id="system_user", node_key="akasha_mobile_test"):
        self.endpoint = endpoint
        self.user_id = user_id
        self.node_key = node_key

    def capture_sensor_data(self):
        """Simulates capturing GPS and small audio data."""
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        
        # Simulating mock audio (base64)
        mock_audio = base64.b64encode(b"MOCK_AUDIO_DATA_BYTES").decode("utf-8")
        
        return {
            "user_id": self.user_id,
            "node_key": self.node_key,
            "location": {"lat": lat, "lon": lon},
            "audio_payload": mock_audio,
            "timestamp": time.time()
        }

    def stream_to_node(self):
        """Sends captured data to the main Akasha backend."""
        data = self.capture_sensor_data()
        try:
            print(f"Streaming data from mobile node: {self.node_key} to {self.endpoint}...")
            response = requests.post(self.endpoint, json=data, timeout=10)
            if response.status_code == 200:
                print(f"SUCCESS: Data ingested. Server response: {response.json().get('status')}")
            else:
                print(f"FAILED: Server returned {response.status_code} - {response.text}")
        except Exception as e:
            print(f"CONNECTION ERROR: {str(e)}")

if __name__ == "__main__":
    client = SensorClient()
    # Stream once for simulation
    client.stream_to_node()
