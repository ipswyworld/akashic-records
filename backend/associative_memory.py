import torch
import torch.nn as nn
import torch.nn.functional as F
import sqlite3
import json
from typing import Dict, Any, List

class TraceLogger:
    """Logs user interactions with associative memory for future model fine-tuning."""
    def __init__(self, db_path="akasha.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS memory_traces (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query_text TEXT,
                        retrieved_ids TEXT,
                        interaction_score REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
        except Exception as e:
            print(f"TraceLogger DB Init Error: {e}")

    def log_interaction(self, query_text: str, retrieved_ids: List[str], score: float):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO memory_traces (query_text, retrieved_ids, interaction_score) VALUES (?, ?, ?)",
                    (query_text, json.dumps(retrieved_ids), score)
                )
        except Exception as e:
            print(f"TraceLogger Log Error: {e}")

class CrossModalAligner(nn.Module):
    """
    Neural Mapper to align Text, Audio, and Visual embeddings in a shared space.
    Pillar: Neural Associative Memory.
    """
    def __init__(self, text_dim: int = 384, audio_dim: int = 512, visual_dim: int = 512, shared_dim: int = 256):
        super(CrossModalAligner, self).__init__()
        
        self.text_projector = nn.Sequential(
            nn.Linear(text_dim, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Linear(256, shared_dim)
        )
        
        self.audio_projector = nn.Sequential(
            nn.Linear(audio_dim, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Linear(256, shared_dim)
        )
        
        self.visual_projector = nn.Sequential(
            nn.Linear(visual_dim, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Linear(256, shared_dim)
        )

    def forward(self, modality: str, x: torch.Tensor):
        if modality == 'text':
            return F.normalize(self.text_projector(x), p=2, dim=-1)
        elif modality == 'audio':
            return F.normalize(self.audio_projector(x), p=2, dim=-1)
        elif modality == 'visual':
            return F.normalize(self.visual_projector(x), p=2, dim=-1)
        return x

class AssociativeMemoryEngine:
    """
    Orchestrates the neural mapping between disparate sensory inputs.
    Allows Akasha to 'think' about a visual memory when hearing a related sound.
    """
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.aligner = CrossModalAligner().to(self.device)
        self.tracer = TraceLogger()

    def log_retrieval_trace(self, query: str, retrieved_ids: List[str], interaction_score: float = 1.0):
        """Records a successful retrieval hit for future fine-tuning."""
        self.tracer.log_interaction(query, retrieved_ids, interaction_score)

    def get_shared_representation(self, modality: str, embedding: torch.Tensor) -> torch.Tensor:
        self.aligner.eval()
        with torch.no_grad():
            x = embedding.to(self.device)
            return self.aligner(modality, x)

    def calculate_cross_modal_similarity(self, rep1: torch.Tensor, rep2: torch.Tensor) -> float:
        """Measures how related two different modal memories are in the shared neural space."""
        return float(F.cosine_similarity(rep1, rep2).cpu().item())
