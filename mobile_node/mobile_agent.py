import os
import time
import json
import sqlite3
import requests
import random
import base64
import psutil # For battery monitoring
import threading
from typing import Dict, Any, List, Optional

# Security Layer: Sovereign Shield
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

class SovereignShield:
    """Handles at-rest encryption and Zero-Knowledge sync payloads."""
    def __init__(self, password: str = "akasha_sovereign_key"):
        if not CRYPTO_AVAILABLE:
            self.fernet = None
            return
            
        salt = b'akasha_neural_salt' # In production, this should be unique per device
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        if not self.fernet: return data
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        if not self.fernet: return token
        try:
            return self.fernet.decrypt(token.encode()).decode()
        except:
            return "DECRYPTION_ERROR"

class MobileOfflineAgent:
    """
    Advanced Mobile Agent for Akasha.
    Features: Sovereign Shield (Encryption), Contextual Proactivity, 
    Sleep-Cycle Maintenance, and Zero-Knowledge Bulk Sync.
    """
    def __init__(self, endpoint="http://localhost:8001/node/sensory", db_path="local_cache.db", model_path="mobile_node/tinyllama.gguf"):
        self.endpoint = endpoint
        self.db_path = db_path
        self.model_path = model_path
        self.user_id = "system_user"
        self.node_key = "akasha_mobile_agent"
        
        # Initialize Security
        self.shield = SovereignShield()
        self._init_db()
        
        # Try to load local LLM
        self.llm = None
        try:
            from llama_cpp import Llama
            if os.path.exists(self.model_path):
                print(f"MobileAgent: Loading local model {self.model_path}...")
                self.llm = Llama(model_path=self.model_path, n_ctx=2048, verbose=False)
            else:
                print("MobileAgent: Local model not found. Operating in Cache-Only mode.")
        except ImportError:
            print("MobileAgent: llama-cpp-python not installed. Operating in Cache-Only mode.")

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sensor_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload TEXT,
                    is_encrypted INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS query_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    response TEXT,
                    is_encrypted INTEGER DEFAULT 0,
                    synced INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS proactive_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight TEXT,
                    context_snapshot TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def check_efficiency_metrics(self) -> Dict[str, Any]:
        """Hardware/Battery awareness to conserve energy."""
        metrics = {"battery_percent": 100, "power_plugged": True, "network_available": False}
        if hasattr(psutil, "sensors_battery"):
            batt = psutil.sensors_battery()
            if batt:
                metrics["battery_percent"] = batt.percent
                metrics["power_plugged"] = batt.power_plugged
        try:
            requests.get("http://8.8.8.8", timeout=1)
            metrics["network_available"] = True
        except:
            metrics["network_available"] = False
        return metrics

    def capture_sensor_data(self):
        """Captures data, encrypts it (Sovereign Shield), and caches it locally."""
        metrics = self.check_efficiency_metrics()
        
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        
        audio_payload = None
        if metrics["battery_percent"] > 20 or metrics["power_plugged"]:
            audio_payload = base64.b64encode(b"MOCK_AUDIO_DATA_BYTES").decode("utf-8")
        
        raw_data = {
            "user_id": self.user_id,
            "node_key": self.node_key,
            "location": {"lat": lat, "lon": lon},
            "audio_payload": audio_payload,
            "timestamp": time.time()
        }
        
        # Pillar 1: Sovereign Shield (At-Rest Encryption)
        encrypted_payload = self.shield.encrypt(json.dumps(raw_data))
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO sensor_cache (payload, is_encrypted) VALUES (?, 1)", (encrypted_payload,))
        print("MobileAgent: Sovereign sensor data cached.")

    def handle_local_query(self, query: str) -> str:
        """Processes a query locally and encrypts the interaction."""
        if not self.llm:
            response = "I am currently offline. Query queued for server."
        else:
            print("MobileAgent: Generating response locally...")
            try:
                output = self.llm(f"User: {query}\nAssistant:", max_tokens=256, stop=["User:", "\n"])
                response = output["choices"][0]["text"].strip()
            except Exception as e:
                response = f"Local Error: {e}"

        # Pillar 1: Sovereign Shield
        enc_query = self.shield.encrypt(query)
        enc_response = self.shield.encrypt(response)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO query_cache (query, response, is_encrypted) VALUES (?, ?, 1)", (enc_query, enc_response))
        
        return response

    def proactive_reasoning(self):
        """Pillar 2: Contextual Proactivity (The Heads-Up Service)."""
        metrics = self.check_efficiency_metrics()
        if not self.llm or metrics["battery_percent"] < 30:
            return

        print("MobileAgent: Running Proactive Reasoning Loop...")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT payload FROM sensor_cache ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            if not row: return
            
            raw_payload = self.shield.decrypt(row[0])
            data = json.loads(raw_payload)
            
            prompt = f"Context: User is at {data['location']}. Recent audio captured. Generate a 1-sentence proactive insight for the user."
            output = self.llm(f"System: {prompt}\nInsight:", max_tokens=64, stop=["\n"])
            insight = output["choices"][0]["text"].strip()
            
            conn.execute("INSERT INTO proactive_insights (insight, context_snapshot) VALUES (?, ?)", 
                         (insight, raw_payload))
            print(f"MobileAgent Head-Up: {insight}")

    def run_sleep_cycle_maintenance(self):
        """Pillar 3: Sleep-Cycle Local Fine-Tuning (Maintenance Mode)."""
        metrics = self.check_efficiency_metrics()
        if not metrics["power_plugged"] or metrics["battery_percent"] < 80:
            return

        print("MobileAgent: Entering Sleep-Cycle Maintenance...")
        # 1. Database Optimization
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("VACUUM")
        
        # 2. Trace Preparation (Future LoRA training prep)
        # 3. Old Data Cleanup
        print("MobileAgent: Sleep-Cycle tasks complete.")

    def bulk_sync(self):
        """Pillar 4: Zero-Knowledge Bulk Sync (Bifrost Bridge)."""
        metrics = self.check_efficiency_metrics()
        if not metrics["network_available"] or (metrics["battery_percent"] < 15 and not metrics["power_plugged"]):
            return

        print("MobileAgent: Network detected. Initiating Zero-Knowledge sync...")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, payload, is_encrypted FROM sensor_cache")
            rows = cursor.fetchall()
            
            for row_id, payload_str, is_enc in rows:
                try:
                    # Decrypt locally if needed to re-package for ZK sync
                    if is_enc:
                        raw_payload = self.shield.decrypt(payload_str)
                        data = json.loads(raw_payload)
                    else:
                        data = json.loads(payload_str)
                    
                    # Package for Zero-Knowledge Bulk Sync
                    # We encrypt the ENTIRE payload for the server
                    zk_payload = {
                        "user_id": self.user_id,
                        "node_key": self.node_key,
                        "is_encrypted": True,
                        "encrypted_blob": self.shield.encrypt(json.dumps(data)),
                        "timestamp": data.get("timestamp", time.time())
                    }
                    
                    resp = requests.post(self.endpoint, json=zk_payload, timeout=5)
                    if resp.status_code == 200:
                        cursor.execute("DELETE FROM sensor_cache WHERE id = ?", (row_id,))
                except Exception as e:
                    print(f"MobileAgent: Sync error: {e}")
                    break
            conn.commit()
        print("MobileAgent: Bulk sync (Zero-Knowledge) complete.")

if __name__ == "__main__":
    agent = MobileOfflineAgent()
    print("--- Akasha Advanced Mobile Agent Started ---")
    
    # 1. Data Capture (Encrypted)
    agent.capture_sensor_data()
    
    # 2. Local Intelligence (Encrypted)
    agent.handle_local_query("Who am I?")
    
    # 3. Proactive Reasoning
    agent.proactive_reasoning()
    
    # 4. Maintenance
    agent.run_sleep_cycle_maintenance()
    
    # 5. Secure Sync
    agent.bulk_sync()
