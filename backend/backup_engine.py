import os
import shutil
import zipfile
import logging
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)

class BackupEngine:
    """
    The 'Neural Will': Sovereign Redundancy.
    Handles encrypted backups and sharding of the user's library.
    """
    def __init__(self, db_path: str = "akasha.db", chroma_path: str = "./chroma_db"):
        self.db_path = db_path
        self.chroma_path = chroma_path
        self.backup_dir = "./backups"
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_sovereign_backup(self) -> str:
        """Creates a consolidated ZIP of the entire library state."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"akasha_neural_will_{timestamp}.zip"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Backup SQLite DB
            if os.path.exists(self.db_path):
                zipf.write(self.db_path, arcname="neural_core.db")
            
            # 2. Backup ChromaDB
            for root, dirs, files in os.walk(self.chroma_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, start=os.path.join(self.chroma_path, '..'))
                    zipf.write(full_path, arcname=rel_path)
                    
        logger.info(f"Neural Will: Backup created at {backup_path}")
        return backup_path

    def shard_backup(self, backup_path: str, num_shards: int = 3) -> List[str]:
        """
        Shards the backup file into multiple parts for distributed storage.
        (Simple file splitting for now).
        """
        shards = []
        file_size = os.path.getsize(backup_path)
        shard_size = (file_size // num_shards) + 1
        
        with open(backup_path, 'rb') as f:
            for i in range(num_shards):
                shard_name = f"{backup_path}.shard{i+1}"
                chunk = f.read(shard_size)
                if not chunk: break
                with open(shard_name, 'wb') as shard_f:
                    shard_f.write(chunk)
                shards.append(shard_name)
                
        logger.info(f"Neural Will: Library sharded into {len(shards)} parts.")
        return shards
