import logging
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models import LibraryArtifact, SRSCard

logger = logging.getLogger(__name__)

class LearningEngine:
    """
    The 'Synaptic Tutor': Active Learning System.
    Generates study paths, quizzes, and explains concepts from the user's library.
    """
    def __init__(self, ai_engine):
        self.ai = ai_engine

    def generate_syllabus(self, artifact_ids: List[str], db: Session) -> Dict[str, Any]:
        """
        Synthesizes a learning path from a collection of artifacts.
        """
        artifacts = db.query(LibraryArtifact).filter(LibraryArtifact.id.in_(artifact_ids)).all()
        for a in artifacts: a.decrypt_content()
        
        context = "\n\n".join([f"Title: {a.title}\nContent: {a.content[:1000]}" for a in artifacts])
        
        prompt = (
            f"You are the Akasha Scholar. Based on the following reference materials:\n{context}\n\n"
            "Create a structured 5-step 'Learning Path' to master this topic. "
            "For each step, provide a Title and a key concept to focus on. "
            "Return a JSON object with a 'topic' and 'steps' (list of {title, concept})."
        )
        
        try:
            response = self.ai.council.llm.invoke(prompt)
            # Simplified extraction
            import re
            match = re.search(r'\{.*\}', response, re.DOTALL)
            return json.loads(match.group()) if match else {"topic": "Syllabus Generation", "steps": []}
        except Exception as e:
            logger.error(f"LearningEngine Syllabus Error: {e}")
            return {"topic": "Error", "steps": []}

    def generate_quiz(self, artifact_id: str, db: Session) -> List[Dict[str, Any]]:
        """Generates 3 interactive questions from a single artifact."""
        artifact = db.query(LibraryArtifact).filter(LibraryArtifact.id == artifact_id).first()
        if not artifact: return []
        artifact.decrypt_content()
        
        prompt = (
            f"You are the Akasha Tutor. Based on this artifact content:\n{artifact.content[:2000]}\n\n"
            "Generate 3 multiple-choice questions to test the user's understanding. "
            "Return a JSON list of objects: {question, options: [], correct_index, explanation}."
        )
        
        try:
            response = self.ai.council.llm.invoke(prompt)
            import re
            match = re.search(r'\[.*\]', response, re.DOTALL)
            return json.loads(match.group()) if match else []
        except Exception as e:
            logger.error(f"LearningEngine Quiz Error: {e}")
            return []
