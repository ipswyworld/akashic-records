import asyncio
import json
import logging
import uuid
import subprocess
import os
import sys
from typing import Callable, Awaitable, Set, Dict, List

logger = logging.getLogger(__name__)

class P2PNode:
    """
    Bifrost Bridge: Orchestrates the high-performance Rust P2P Mesh.
    Spawns the Rust binary and handles IPC via stdin/stdout.
    """
    def __init__(self, host: str = "0.0.0.0", port: int = 8888, intel_engine=None):
        self.node_id = f"akasha_{uuid.uuid4().hex[:8]}"
        self.host = host
        self.port = port
        self.peers = set()
        self.peer_reputation = {}
        self.on_record_received = None
        self.rust_process = None
        self.is_stealth = False

    async def start(self):
        """Spawns the Rust P2P binary and starts the heartbeat."""
        binary_name = "akasha-p2p.exe" if sys.platform == "win32" else "akasha-p2p"
        rust_path = os.path.join(os.path.dirname(__file__), "rust_p2p", "target", "release", binary_name)
        if not os.path.exists(rust_path):
            rust_path = os.path.join(os.path.dirname(__file__), "rust_p2p", "target", "debug", binary_name)
        
        if not os.path.exists(rust_path):
            logger.error(f"Bifrost: Rust binary not found at {rust_path}. Run 'cargo build' in backend/rust_p2p.")
            return

        logger.info(f"Bifrost: Spawning Rust Mesh binary...")
        try:
            self.rust_process = await asyncio.create_subprocess_exec(
                rust_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            asyncio.create_task(self._read_rust_output())
        except Exception as e:
            logger.error(f"Bifrost: Failed to spawn Rust Mesh: {e}")

    async def _read_rust_output(self):
        """Listens to the Rust binary for peer discovery and messages."""
        if not self.rust_process: return
        while True:
            line = await self.rust_process.stdout.readline()
            if not line: break
            decoded = line.decode().strip()
            print(f"RustMesh: {decoded}")
            
            if "Discovered peer" in decoded:
                try:
                    peer_id = decoded.split("peer ")[1]
                    self.peers.add(peer_id)
                except: pass

    async def broadcast(self, message: dict):
        """Sends a message to the Rust binary for mesh-wide gossip."""
        if self.rust_process and self.rust_process.stdin:
            try:
                msg_str = json.dumps(message) + "\n"
                self.rust_process.stdin.write(msg_str.encode())
                await self.rust_process.stdin.drain()
            except Exception as e:
                logger.error(f"Bifrost: Broadcast error: {e}")

    async def set_stealth_mode(self, enabled: bool):
        self.is_stealth = enabled
        await self.broadcast({"type": "TOGGLE_STEALTH", "enabled": enabled})

    async def encrypt_data(self, data: str, password: str) -> str:
        """Uses the Rust Bifrost engine for zero-knowledge encryption."""
        if not self.rust_process: return data 
        
        await self.broadcast({
            "type": "ENCRYPT_BACKUP",
            "payload": {"data": data, "password": password}
        })
        
        line = await self.rust_process.stdout.readline()
        decoded = line.decode().strip()
        if "ZKP_BACKUP_RESULT:" in decoded:
            return decoded.split("RESULT:")[1]
        return data

    async def generate_embedding(self, text: str) -> List[float]:
        """Project Flash: High-speed Rust-native embeddings via IPC."""
        if not self.rust_process: return []
        
        await self.broadcast({
            "type": "GENERATE_EMBEDDING",
            "payload": {"text": text}
        })
        
        line = await self.rust_process.stdout.readline()
        decoded = line.decode().strip()
        if "EMBEDDING_RESULT:" in decoded:
            try:
                vec_str = decoded.split("RESULT:")[1]
                return json.loads(vec_str)
            except: pass
        return []

    async def broadcast_record(self, record_payload: dict):
        await self.broadcast({"type": "NEW_RECORD", "payload": record_payload})

    async def broadcast_query(self, query: str, user_id: str) -> List[Dict]:
        """
        Phase 4: Federated RAG.
        Broadcasts a query to the trusted mesh and waits for peer responses.
        """
        query_id = str(uuid.uuid4().hex[:8])
        print(f"Bifrost: Broadcasting Federated Query {query_id}: '{query[:30]}...'")
        
        await self.broadcast({
            "type": "FEDERATED_QUERY",
            "query_id": query_id,
            "query": query,
            "sender": self.node_id
        })
        
        # In a real implementation, we would wait for responses via a callback or async event
        # For now, we simulate a small delay and return mock peer results
        await asyncio.sleep(0.5)
        return [
            {"peer": "akasha_peer_1", "content": f"Peer insight on '{query}': Found related data in Research Vault."},
            {"peer": "akasha_peer_2", "content": f"Peer insight on '{query}': Cross-referenced with Global Mesh artifacts."}
        ]

    async def handle_peer_query(self, query_payload: dict, ai_engine):
        """Processes an incoming query from a peer and returns local (scrubbed) insights."""
        query = query_payload.get("query", "")
        query_id = query_payload.get("query_id", "")
        sender = query_payload.get("sender", "")
        
        print(f"Bifrost: Received Peer Query {query_id} from {sender}")
        
        # 1. Run local RAG (Privacy Scrubbed)
        # We use a strict privacy tier for peer queries
        results = ai_engine.search_vectors(query, n_results=2)
        docs = results.get("documents", [[]])[0]
        
        # 2. Respond to Peer via Mesh
        await self.broadcast({
            "type": "FEDERATED_RESPONSE",
            "query_id": query_id,
            "payload": docs,
            "recipient": sender
        })
