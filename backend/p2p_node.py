import asyncio
import json
import logging
import uuid
import subprocess
import os
import sys
from typing import Callable, Awaitable, Set, Dict

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
            logger.error(f"Bifrost: Rust binary not found. Run 'cargo build' in backend/rust_p2p.")
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
        while True:
            line = await self.rust_process.stdout.readline()
            if not line: break
            decoded = line.decode().strip()
            print(f"RustMesh: {decoded}")
            
            if "Discovered peer" in decoded:
                peer_id = decoded.split("peer ")[1]
                self.peers.add(peer_id)

    async def broadcast(self, message: dict):
        """Sends a message to the Rust binary for mesh-wide gossip."""
        if self.rust_process and self.rust_process.stdin:
            msg_str = json.dumps(message) + "\n"
            self.rust_process.stdin.write(msg_str.encode())
            await self.rust_process.stdin.drain()

    async def set_stealth_mode(self, enabled: bool):
        self.is_stealth = enabled
        await self.broadcast({"type": "TOGGLE_STEALTH", "enabled": enabled})

    async def encrypt_data(self, data: str, password: str) -> str:
        """Uses the Rust Bifrost engine for zero-knowledge encryption."""
        if not self.rust_process: return data # Fallback
        
        await self.broadcast({
            "type": "ENCRYPT_BACKUP",
            "payload": {"data": data, "password": password}
        })
        
        # Read the result from stdout (simple implementation)
        # In production, use a more robust future-based response system
        line = await self.rust_process.stdout.readline()
        decoded = line.decode().strip()
        if "ZKP_BACKUP_RESULT:" in decoded:
            return decoded.split("RESULT:")[1]
        return data

    async def broadcast_record(self, record_payload: dict):
        await self.broadcast({"type": "NEW_RECORD", "payload": record_payload})
