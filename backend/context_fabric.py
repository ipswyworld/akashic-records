import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models import LibraryArtifact, UserPsychology

logger = logging.getLogger(__name__)

class ContextFabric:
    """
    The Unified Knowledge Layer: Consolidates Relational (SQL), Semantic (Vector), 
    and Relational (Graph) data into a single high-speed context object.
    """
    def __init__(self, ai_engine, graph_engine):
        self.ai = ai_engine
        self.graph = graph_engine

    def weave_context(self, query: str, user_id: str, db: Session) -> Dict[str, Any]:
        """
        Retrieves a 3-dimensional context for any given query.
        1. Semantic: Top-N similar chunks from ChromaDB.
        2. Relational: Knowledge Graph triplets.
        3. Identity: The user's current Digital Ego state.
        """
        logger.info(f"ContextFabric: Weaving context for user {user_id}...")
        
        # 1. Semantic Dimenson (Vector)
        vector_results = self.ai.search_vectors(query, n_results=5, user_id=user_id)
        docs = vector_results.get("documents", [[]])[0]
        
        # 2. Relational Dimension (Graph)
        entities = [e['word'] for e in self.ai.council.ner_pipeline(query)]
        graph_context = self.graph.search_graph_context(entities, user_id=user_id)
        
        # 3. Identity Dimension (Ego)
        ego = db.query(UserPsychology).filter(UserPsychology.user_id == user_id).first()
        ego_summary = f"Mood: {ego.current_mood}, Values: {ego.core_values}" if ego else "Neutral Baseline"

        return {
            "semantic": docs,
            "relational": graph_context,
            "identity": ego_summary,
            "full_text": "\n---\n".join(docs + graph_context)
        }

    def get_artifact_fabric(self, artifact_id: str, db: Session) -> Dict[str, Any]:
        """Pulls everything Akasha knows about a specific artifact."""
        artifact = db.query(LibraryArtifact).filter(LibraryArtifact.id == artifact_id).first()
        if not artifact: return {}
        
        artifact.decrypt_content()
        triplets = self.graph.get_artifact_triplets(artifact_id)
        
        return {
            "core": artifact,
            "connections": triplets,
            "summary": artifact.summary
        }
