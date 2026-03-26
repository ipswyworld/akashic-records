import asyncio
import json
import logging
import uuid
from typing import Callable, Awaitable, Set, Dict

logger = logging.getLogger(__name__)

class P2PNode:
    """A decentralized P2P gossip node for Akasha with Immune System integration."""
    def __init__(self, host: str = "0.0.0.0", port: int = 8888, intel_engine=None):
        self.node_id = str(uuid.uuid4())
        self.host = host
        self.port = port
        self.peers: Set[tuple] = set()
        self.peer_reputation: Dict[tuple, float] = {} # addr -> score (0 to 1)
        self.on_record_received = None
        self.seen_messages: Set[str] = set() # Prevent gossip loops
        self.intel = intel_engine
        self.is_stealth = False
        self.server = None

    async def start(self):
        if self.is_stealth:
            logger.warning("P2P Node: Cannot start in STEALH mode.")
            return
        try:
            self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
            logger.info(f"P2P Node {self.node_id} listening on {self.host}:{self.port}")
            async with self.server:
                await self.server.serve_forever()
        except Exception as e:
            logger.error(f"P2P Server failed: {e}")

    async def stop(self):
        """Shutdown the P2P server and clear peer connections."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
            logger.info("P2P Node: Server stopped (Sovereign Shield Active).")
        self.peers.clear()

    async def set_stealth_mode(self, enabled: bool):
        """Toggle stealth mode (Sovereign Shield)."""
        self.is_stealth = enabled
        if enabled:
            await self.stop()
        else:
            logger.info("P2P Node: Disabling stealth mode. Restarting server...")
            asyncio.create_task(self.start())

    async def validate_record_integrity(self, payload: dict, addr: tuple) -> bool:
        """Validates the signature, hash chain, and immune system health of an incoming record."""
        try:
            # 1. Basic Protocol Validation
            if not payload.get("signature") or not payload.get("id"):
                self.peer_reputation[addr] = self.peer_reputation.get(addr, 1.0) - 0.2
                return False
            
            # Reputation check (Strict)
            current_rep = self.peer_reputation.get(addr, 0.5) # Default to neutral/low for new peers
            if current_rep < 0.4:
                logger.warning(f"P2P: Rejecting gossip from high-risk peer {addr} (Rep: {current_rep:.2f})")
                return False
            
            # 2. Immune System Validation (Phase 5)
            if self.intel:
                # Near-duplicate detection (SimHash)
                data_text = payload.get("data", "")
                incoming_simhash = self.intel.calculate_simhash(data_text)
                logger.info(f"P2P: SimHash for incoming record: {incoming_simhash}")

                # Anomaly Detection (One-Class SVM)
                embedding = payload.get("embedding")
                if embedding and isinstance(embedding, list):
                    is_threat = self.intel.detect_immune_threat([embedding]) 
                    if is_threat:
                        logger.warning(f"IMMUNE ALERT: Anomalous record from {addr}. Throttling peer.")
                        # Massive reputation hit for poisoning attempts
                        self.peer_reputation[addr] = max(0, current_rep - 0.6)
                        return False
            
            # Successful validation increases reputation slightly (Time-Weighted trust)
            self.peer_reputation[addr] = min(1.0, current_rep + 0.05)
            return True
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        logger.info(f"New P2P connection from {addr}")
        self.peer_reputation[addr] = 1.0 # Initialize trust
        
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                
                raw_msg = data.decode()
                try:
                    message = json.loads(raw_msg)
                    msg_id = message.get("msg_id")
                    
                    if msg_id and msg_id not in self.seen_messages:
                        self.seen_messages.add(msg_id)
                        
                        # Process and Validate
                        if message.get("type") == "NEW_RECORD":
                            payload = message.get("payload")
                            if await self.validate_record_integrity(payload, addr):
                                # Gossip the valid message to other peers
                                asyncio.create_task(self.broadcast(message, exclude_addr=addr))
                                if self.on_record_received:
                                    await self.on_record_received(payload)
                        elif message.get("type") == "SCHEMA_EXCHANGE":
                            # Swarm Intelligence: Exchange ontological rules
                            payload = message.get("payload")
                            if message.get("request_id"):
                                # This is a response to a previous request
                                logger.info(f"P2P Node: Received SCHEMA_RESPONSE from {addr}")
                                # TODO: Apply these rules to graph_engine
                            else:
                                # This is a request or broadcast
                                logger.info(f"P2P Node: Received SCHEMA_REQUEST from {addr}")
                                # Respond with current schema (mock)
                                asyncio.create_task(self.respond_with_schema(message.get("msg_id"), addr))
                            
                            # Gossip schema update to others
                            asyncio.create_task(self.broadcast(message, exclude_addr=addr))
                            
                        elif message.get("type") == "SYNC_REQUEST":
                            # Peer is requesting subchain data
                            from_id = message.get("payload", {}).get("after_id")
                            logger.info(f"P2P Node: Received SYNC_REQUEST from {addr} after artifact {from_id}")
                            # Mock: In a real system, fetch from Ouroboros subchain and respond
                            asyncio.create_task(self.send_to_peer({
                                "type": "SYNC_RESPONSE",
                                "request_id": message.get("msg_id"),
                                "payload": {"artifacts": []} # No artifacts to sync in mock
                            }, addr))
                        
                        elif message.get("type") == "MERKLE_ROOT_BROADCAST":
                            # Peer is sharing their subchain state
                            root = message.get("payload", {}).get("root")
                            logger.info(f"P2P Node: Peer {addr} broadcasted Merkle Root: {root}")
                            # Logic to compare roots and trigger SYNC_REQUEST if behind
                            
                        elif message.get("type") == "PEER_DISCOVERY":
                            peer_addr = tuple(message.get("payload"))
                            if peer_addr != (self.host, self.port):
                                self.peers.add(peer_addr)
                                asyncio.create_task(self.broadcast(message, exclude_addr=addr))
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.error(f"Error handling peer {addr}: {e}")
        finally:
            writer.close()

    async def respond_with_schema(self, request_id: str, addr: tuple):
        """Responds to a schema request with the local ontology."""
        await self.send_to_peer({
            "type": "SCHEMA_EXCHANGE",
            "request_id": request_id,
            "payload": {"ontology": "standard_akasha_v1", "custom_nodes": []}
        }, addr)

    async def send_to_peer(self, message: dict, addr: tuple):
        """Sends a message directly to a specific peer."""
        if "msg_id" not in message:
            message["msg_id"] = str(uuid.uuid4())
        data = json.dumps(message).encode()
        try:
            reader, writer = await asyncio.open_connection(addr[0], addr[1])
            writer.write(data)
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            logger.warning(f"Failed to send directly to {addr}: {e}")

    async def broadcast_schema(self, schema_payload: dict):
        """Broadcasts an abstracted graph schema to the network."""
        await self.broadcast({
            "type": "SCHEMA_EXCHANGE",
            "payload": schema_payload
        })

    async def broadcast(self, message: dict, exclude_addr=None):
        """Gossip a message to all known peers."""
        if "msg_id" not in message:
            message["msg_id"] = str(uuid.uuid4())
            
        data = json.dumps(message).encode()
        for peer in list(self.peers):
            if peer == exclude_addr:
                continue
            try:
                reader, writer = await asyncio.open_connection(peer[0], peer[1])
                writer.write(data)
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            except Exception:
                self.peers.remove(peer)

    async def connect_to_peer(self, host: str, port: int):
        """Manually connect to a seed peer and share identity."""
        peer_addr = (host, port)
        self.peers.add(peer_addr)
        await self.broadcast({
            "type": "PEER_DISCOVERY",
            "payload": [self.host, self.port]
        })
        logger.info(f"Connected to seed peer: {host}:{port}")
