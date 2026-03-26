import os
import json
import uuid
import hashlib
import mmap
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class AkashaRecord(BaseModel):
    id: str
    user_id: str = "system_user"
    data: str # Encrypted in Tier 1
    embedding: List[float]
    metadata: Dict[str, Any]
    blockchain_proof: Optional[str] = None
    timestamp: float = time.time()
    access_count: int = 0
    health_score: float = 1.0
    synaptic_weight: float = 1.0
    utility_score: float = 0.5
    prediction_confidence: Optional[float] = None
    type: str = "ARTIFACT"
    # Security Layer (Tier 2)
    prev_hash: Optional[str] = None # Link to the previous record (The Chain)
    signature: Optional[str] = None # DID signature of (id + data + prev_hash)

class AkashaLivingDB:
    """The Living Storage Engine for the Akashic Records."""
    
    def __init__(self, storage_path: str = "./akasha_data"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.log_file = os.path.join(storage_path, "aol.log")
        self.index_file = os.path.join(storage_path, "index.json")
        self.index = self._load_index()
        self.last_record_hash = self._calculate_current_tail()
        
    def _calculate_current_tail(self) -> Optional[str]:
        """Calculates the hash of the last record in the log to anchor the next one."""
        records = self.get_all_records()
        if not records:
            return None
        last = records[-1]
        payload = f"{last.id}:{last.prev_hash}:{last.timestamp}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def _load_index(self) -> Dict[str, int]:
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_index(self):
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f)

    def write(self, record: AkashaRecord) -> str:
        """Writes a record to the Append-Only Log and updates the index."""
        # Tier 2 Security: Link to the chain
        record.prev_hash = self.last_record_hash
        
        record_json = record.json()
        with open(self.log_file, "a") as f:
            offset = f.tell()
            f.write(record_json + "\n")
            self.index[record.id] = offset
        
        # Update the tail hash for the next record
        payload = f"{record.id}:{record.prev_hash}:{record.timestamp}"
        self.last_record_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        self._save_index()
        return record.id

    def read(self, record_id: str) -> Optional[AkashaRecord]:
        """Reads a record from the AOL using memory-mapped I/O for speed."""
        if record_id not in self.index:
            return None
        
        offset = self.index[record_id]
        with open(self.log_file, "r") as f:
            f.seek(offset)
            line = f.readline()
            if line:
                record = AkashaRecord.parse_raw(line)
                # Metabolic update: Increment access count on read
                record.access_count += 1
                return record
        return None

    def update(self, record_id: str, updated_record: AkashaRecord):
        """Metabolic update: Overwrites are handled by appending new state."""
        # In a living system, we don't delete history; we append the new 'evolved' state.
        return self.write(updated_record)

    def get_all_records(self) -> List[AkashaRecord]:
        records = []
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    records.append(AkashaRecord.parse_raw(line))
                except Exception:
                    continue
        return records

    def calculate_state_merkle(self) -> str:
        """Generates a state-hash for blockchain anchoring."""
        all_ids = sorted(list(self.index.keys()))
        combined = "".join(all_ids)
        return hashlib.sha256(combined.encode()).hexdigest()
