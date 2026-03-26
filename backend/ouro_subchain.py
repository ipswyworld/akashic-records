import uuid
import time
import hashlib
import json
from typing import List, Dict, Any

class NanoTx:
    def __init__(self, payload: bytes, refs: List[str] = None):
        self.id = str(uuid.uuid4())
        self.timestamp = int(time.time())
        self.payload = payload
        self.refs = refs or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "payload": self.payload.hex(),
            "refs": self.refs
        }

class AkashaSubchain:
    """
    A local NanoChain implementation for Akasha, 
    mirrored from the Bifrost Rust core.
    """
    def __init__(self, context: str, public_key: str):
        self.id = str(uuid.uuid4())
        self.context = context
        self.public_key = public_key
        self.tx_cache: List[NanoTx] = []
        self.batch_count = 0

    def add_artifact(self, artifact_metadata: Dict[str, Any]) -> NanoTx:
        payload = json.dumps(artifact_metadata).encode('utf-8')
        # Use previous artifact as a reference to build the DAG
        refs = [self.tx_cache[-1].id] if self.tx_cache else []
        tx = NanoTx(payload, refs)
        self.tx_cache.append(tx)
        return tx

    def should_batch(self, threshold: int = 10) -> bool:
        return len(self.tx_cache) >= threshold

    def calculate_merkle_root(self) -> str:
        if not self.tx_cache:
            return hashlib.sha256(b"empty").hexdigest()

        # Initial layer: hashes of serialized transactions
        layer = []
        for tx in self.tx_cache:
            tx_data = json.dumps(tx.to_dict(), sort_keys=True).encode('utf-8')
            layer.append(hashlib.sha256(tx_data).digest())

        # Build Merkle Tree
        while len(layer) > 1:
            if len(layer) % 2 == 1:
                layer.append(layer[-1])
            
            new_layer = []
            for i in range(0, len(layer), 2):
                combined = layer[i] + layer[i+1]
                new_layer.append(hashlib.sha256(combined).digest())
            layer = new_layer

        return layer[0].hex()

    def create_batch(self) -> Dict[str, Any]:
        root = self.calculate_merkle_root()
        batch = {
            "nanochain_id": self.id,
            "batch_index": self.batch_count,
            "root": root,
            "tx_count": len(self.tx_cache),
            "timestamp": int(time.time()),
            "context": self.context
        }
        
        # We don't clear the cache here yet; 
        # we wait for successful anchoring in the adapter.
        return batch

    def clear_cache(self):
        self.tx_cache = []
        self.batch_count += 1

class OuroborosSubchain(AkashaSubchain):
    """Alias/Wrapper for AkashaSubchain used in main engines."""
    def __init__(self, context="global", public_key="system_default"):
        super().__init__(context, public_key)
