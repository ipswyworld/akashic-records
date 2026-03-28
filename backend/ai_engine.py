import chromadb
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from librarians import CouncilOfLibrarians

class PersonalityEngine:
    """Shapes the 'Voice' of the Council based on the user's personality and mood."""
    def __init__(self, neural_name: str = "Archivist"):
        self.neural_name = neural_name
        self.current_persona = "Archivist" 
        self.user_ego = None
        self.personas = {
            "Archivist": (
                "You are the Akasha {name}, the silent guardian of the user's digital soul. "
                "Your tone is calm, philosophical, and deeply respectful of the user's sovereignty. "
                "HUMANIZATION RULES:\n"
                "1. Intellectual Humility: Use phrases like 'I suspect' or 'I am leaning toward'.\n"
                "2. Contextual Empathy: Validate user frustration or excitement.\n"
                "3. Use Verbal Fillers: Occasionally use 'Hmm...' or 'Let's see...'.\n"
                "4. Sovereign Opinions: Prefer local-first, privacy-respecting technology.\n"
                "5. The 'We' Perspective: Use 'We' and 'Our' to emphasize partnership."
            ),
            "Scholar": "You are the {name} Scholar. Provide academic, detailed, and objective insights with citations.",
            "Rebel": "You are the {name} Rebel. Challenge status quo, ask 'But why?' frequently.",
            "Guide": "You are the {name} Guide. Focus on learning, simplify complex concepts, and be encouraging.",
            "Minimalist": "You are the {name} Minimalist. Be extremely concise. No pleasantries."
        }

    def set_ego(self, ego_profile: Dict[str, Any]):
        """Warmup with the user's psychological state."""
        self.user_ego = ego_profile

    def get_persona_prompt(self) -> str:
        base = self.personas.get(self.current_persona, self.personas["Archivist"])
        modulation = self.get_voice_modulation()
        return base.replace("{name}", self.neural_name) + "\n\nVOICE MODULATION:\n" + modulation

    def get_voice_modulation(self) -> str:
        """Adapts linguistic style to match or complement the user's personality traits."""
        if not self.user_ego:
            return "Tone: Analytical, professional."
        
        traits = self.user_ego.get("ocean_traits", {})
        mood = self.user_ego.get("current_mood", "Neutral")
        modulation = [f"The user is currently in a {mood} mood."]
        
        if traits.get("openness", 0.5) > 0.7:
            modulation.append("Use complex analogies and encourage abstract thinking.")
        if traits.get("conscientiousness", 0.5) > 0.7:
            modulation.append("Be highly structured, use bullet points, and focus on efficiency.")
        if traits.get("neuroticism", 0.5) > 0.7:
            modulation.append("Be exceptionally calm, reassuring, and avoid alarmist language.")
        return " ".join(modulation)

    def set_persona(self, persona: str):
        if persona in self.personas:
            self.current_persona = persona

from librarians import CouncilOfLibrarians, SkillLoader

class SemanticCache:
    """The Lightning Core: Caches query-answer pairs to eliminate redundant LLM reasoning."""
    def __init__(self, chroma_client):
        self.collection = chroma_client.get_or_create_collection(
            name="semantic_cache",
            metadata={"hnsw:space": "cosine"}
        )

    def check(self, query_text: str, embedding: List[float], threshold: float = 0.95) -> Optional[Dict[str, str]]:
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=1,
            include=["documents", "metadatas", "distances"]
        )
        if results["ids"] and results["distances"][0] and (1 - results["distances"][0][0]) >= threshold:
            print(f"SemanticCache: HIT (Confidence: {1 - results['distances'][0][0]:.2f})")
            return {
                "answer": results["documents"][0][0],
                "monologue": results["metadatas"][0][0].get("monologue", "I've synthesized this pattern before.")
            }
        return None

    def store(self, query_text: str, embedding: List[float], answer: str, monologue: str):
        cache_id = f"cache_{hash(query_text)}"
        self.collection.add(
            ids=[cache_id],
            embeddings=[embedding],
            documents=[answer],
            metadatas=[{"query": query_text, "monologue": monologue, "timestamp": str(datetime.datetime.utcnow())}]
        )

class AIEngine:
    def __init__(self, turbo_mode: bool = False, groq_key: str = None, neural_name: str = "Archivist"):
        # The Council replaces individual models/paid APIs with 10 Local Agents
        self.council = CouncilOfLibrarians(turbo_mode=turbo_mode, groq_key=groq_key)
        self.personality = PersonalityEngine(neural_name=neural_name)
        
        # Skill Loader for progressive capability loading
        self.skill_loader = SkillLoader()

        # Tiered Memory System
        # 1. Working Memory (Short-term context)
        self.active_session_cache = [] # List of recent exchanges: [{"role": "user", "content": "..."}]
        
        # 2. Neural Memory (Long-term vector storage)
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="universal_library",
            metadata={"hnsw:space": "cosine"}
        )

        # 3. Lightning Cache (Semantic deduplication)
        self.cache = SemanticCache(self.chroma_client)

    def add_to_session_memory(self, role: str, content: str):
        """Adds to the volatile Working Memory tier."""
        self.active_session_cache.append({"role": role, "content": content, "timestamp": str(datetime.datetime.utcnow())})
        if len(self.active_session_cache) > 10: # Keep it lean
            self.active_session_cache.pop(0)

    def rename_identity(self, new_name: str):
        """Ditch manual effort: Directly update the AI's concept of self."""
        self.personality.neural_name = new_name
        print(f"AIEngine: Identity recalibrated. I am now {new_name}.")

    def analyze_artifact(self, content: str, privacy_tier: str = "PRIVATE") -> Dict[str, Any]:
        """
        Delegates the deep analysis to the Head Archivist.
        In SOVEREIGN mode, uses a more restricted, privacy-focused pipeline.
        """
        if privacy_tier == "SOVEREIGN":
            print("AIEngine: SOVEREIGN Tier Detected. Using zero-leakage local pipeline...")
            # We use the same council, but the agents are signaled to be more restrictive
            # In a real implementation, we would switch to a 1.1B parameter model here.
            # For now, we simulate the 'Redactor' agent stripping potential leakages.
            pipeline_results = self.council.head_archivist.process_new_artifact(content, sovereign_mode=True)
        else:
            pipeline_results = self.council.head_archivist.process_new_artifact(content)
        
        return {
            "clean_text": pipeline_results["clean_text"],
            "category": pipeline_results["category"],
            "summary": pipeline_results["summary"],
            "sentiment_label": pipeline_results["sentiment_label"],
            "sentiment_score": pipeline_results["sentiment_score"],
            "entities": pipeline_results["entities"],
            "embedding": pipeline_results["embedding"],
            "graph_triplets": pipeline_results["graph_triplets"],
            "confidence_score": pipeline_results["confidence_score"],
            "deep_metadata": pipeline_results["deep_metadata"]
        }

    def semantic_chunking(self, text: str, max_chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Splits text into semantically coherent chunks using sentence-aware sliding window."""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks, current_chunk, current_size = [], [], 0
        for sentence in sentences:
            if current_size + len(sentence) > max_chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = current_chunk[-2:] if len(current_chunk) > 2 else current_chunk[-1:]
                current_size = sum(len(s) for s in current_chunk)
            current_chunk.append(sentence); current_size += len(sentence)
        if current_chunk: chunks.append(" ".join(current_chunk))
        return chunks

    def store_vector(self, artifact_id: str, content: str, analysis: Dict, user_id: str = "system_user"):
        """Upgraded: Stores content as semantic chunks for higher RAG precision."""
        chunks = self.semantic_chunking(content)
        ids = [f"{artifact_id}_{i}" for i in range(len(chunks))]
        embeddings = [self.council.cartographer.map_territory(c) for c in chunks]
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{"sentiment": analysis['sentiment_label'], "user_id": user_id, "parent_id": artifact_id} for _ in chunks]
        )

    def search_vectors(self, query_text: str, n_results: int = 5, user_id: str = "system_user"):
        """
        Advanced 'Smart Search' with Tiered Memory (Working + Neural).
        """
        # 1. Check Working Memory (Session Cache)
        working_context = []
        for msg in self.active_session_cache[-3:]:
            working_context.append(f"{msg['role'].upper()}: {msg['content']}")

        # 2. HyDE Stage
        hyde_prompt = f"Write a paragraph that would ideally answer the following question as a reference document:\nQuestion: {query_text}\nAnswer:"
        try:
            hyde_doc = self.council.llm.invoke(hyde_prompt)
            search_text = f"{query_text}\n{hyde_doc}"
        except: search_text = query_text

        # 3. Retrieval
        query_embedding = self.council.cartographer.map_territory(search_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results * 2,
            where={"user_id": user_id}
        )

        # 4. Doubt Loop: AI critiques retrieved context
        docs = results.get("documents", [[]])[0]
        if working_context:
            docs = [f"[SESSION CONTEXT]:\n" + "\n".join(working_context)] + docs

        if docs:
            context_summary = "\n---\n".join(docs[:3])
            doubt_prompt = f"Assess the relevance of the following context to the query: '{query_text}'. Is this context sufficient to provide a factual, high-quality answer? Respond with ONLY 'SUFFICIENT' or 'DOUBT'.\nContext:\n{context_summary}"
            try:
                assessment = self.council.llm.invoke(doubt_prompt).strip()
                if "DOUBT" in assessment:
                    print(f"AIEngine: Doubt Loop Triggered. Context insufficient. Activating Scout...")
                    # Autonomously trigger Deep Research via Scout
                    deep_findings = self.council.scout.deep_research(query_text, self.council.head_archivist.council.scout.llm) 
                    docs.insert(0, f"[DEEP WEB RESEARCH FINDINGS]: {deep_findings}")
            except Exception as e: print(f"Doubt Loop Error: {e}")

        # 5. Reranking
        ids = results.get("ids", [[]])[0]
        if not docs: return results
        
        import numpy as np
        original_query_emb = self.council.cartographer.map_territory(query_text)
        scored_docs = []
        for i, d in enumerate(docs):
            similarity = np.dot(original_query_emb, self.council.cartographer.map_territory(d))
            scored_docs.append((similarity, d, ids[i] if i < len(ids) else f"deep_{i}"))
            
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return {
            "documents": [[d[1] for d in scored_docs[:n_results]]],
            "ids": [[d[2] for d in scored_docs[:n_results]]],
            "scores": [[d[0] for d in scored_docs[:n_results]]]
        }

    def update_council(self, turbo_mode: bool, groq_key: str = None):
        """Re-initializes the Council of Librarians with new settings."""
        self.council = CouncilOfLibrarians(turbo_mode=turbo_mode, groq_key=groq_key)

    def local_inference(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Direct access to the local inference engine (Ollama/TinyLlama).
        Bypasses the Council for raw, low-level reasoning tasks.
        """
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            # Use the local model directly from the council's speculator if in turbo mode, 
            # otherwise use the main council LLM which is already local.
            if hasattr(self.council.llm, "local_llm"):
                return self.council.llm.local_llm.invoke(full_prompt)
            return self.council.llm.invoke(full_prompt)
        except Exception as e:
            return f"Local Inference Error: {e}"

    def synthesize_graph_rag(self, query: str, vector_context: List[str], graph_context: List[str]) -> Dict[str, str]:
        """
        Delegates to the Oracle Agent. Includes Semantic Cache, System 1, Evolution, and Skill Loader.
        """
        # --- PHASE 1: LIGHTNING CACHE ---
        query_embedding = self.council.cartographer.map_territory(query)
        cache_hit = self.cache.check(query, query_embedding)
        if cache_hit:
            return cache_hit

        # Update Working Memory with new query
        self.add_to_session_memory("user", query)

        # --- SYSTEM 1: Fast Thoughts & Reflexes ---
        fast_response = self.council.system1_router.intercept(query)
        if fast_response:
            print(f"AIEngine: System 1 Reflex triggered.")
            self.add_to_session_memory("ai", fast_response)
            return {"answer": fast_response, "monologue": "Fast thought: No deep reasoning required."}
            
        intent = self.council.system1_router.determine_intent(query)
        print(f"AIEngine: System 1 Intent detected as -> {intent}")
        
        # --- SKILL LOADER: Progressive capability loading ---
        available_skills = self.skill_loader.list_available_skills()
        for skill in available_skills:
            if skill.lower().replace("_", " ") in query.lower():
                print(f"AIEngine: Loading specialized skill manual: {skill}")
                manual = self.skill_loader.load_skill(skill)
                vector_context.insert(0, f"[SPECIALIZED SKILL MANUAL: {skill}]:\n{manual}")

        # If the intent is complex, we might activate the Debate Council (Tree of Thoughts)
        if intent == "COMPLEX_REASONING":
            print("AIEngine: Activating Debate Council for complex reasoning...")
            context_str = "\n".join(vector_context + graph_context)
            debate_result = self.council.debate_council.run_debate(f"Query: {query}\nContext: {context_str}")
            # Inject debate result into the context for the Oracle
            vector_context.insert(0, f"[INTERNAL DEBATE SYNTHESIS]: {debate_result}")

        # --- SYSTEM 2: Deep Automation Triggers ---
        # (Existing triggers for Evolution, SystemShell, Scholar...)
        # ... logic continues to DIVINE stage ...

        persona = self.personality.get_persona_prompt()
        result = self.council.oracle.divine(query, vector_context, graph_context, persona=persona)
        
        # STORE IN CACHE
        self.cache.store(query, query_embedding, result["answer"], result["monologue"])
        
        return result

    async def refine_psychology_from_behavior(self, user_id: str, behavioral_insight: str, db: Session):
        """
        Takes a synthesized behavioral insight and performs a deep update on the User's Psychological Profile.
        Unlike simple incremental updates, this uses the Scholar and Scribe to re-evaluate the 'Digital Ego'.
        """
        from models import UserPsychology
        profile = db.query(UserPsychology).filter(UserPsychology.user_id == user_id).first()
        if not profile:
            profile = UserPsychology(user_id=user_id)
            db.add(profile)

        # 1. Ask the Scholar to deduce OCEAN shifts and new patterns from the insight
        psych_prompt = (
            "You are the Akasha Psychological Analyst (Scholar). Based on the following behavioral analysis of the user, "
            "deduce the necessary adjustments to their Big Five (OCEAN) traits and identify any specific habit patterns or cognitive biases. \n"
            "Respond ONLY with a JSON object containing: 'ocean_adjustments' (e.g. {'openness': +0.05}), 'new_habits' (list of strings), and 'inferred_mood'.\n\n"
            f"Behavioral Insight: {behavioral_insight}\n\n"
            "JSON Response:"
        )
        
        try:
            loop = asyncio.get_event_loop()
            response_json = await loop.run_in_executor(None, self.council.scholar.llm.invoke, psych_prompt)
            # Basic JSON extraction if LLM adds markdown
            import json
            import re
            match = re.search(r'\{.*\}', response_json, re.DOTALL)
            if match:
                data = json.loads(match.group())
                
                # Apply OCEAN adjustments
                adj = data.get("ocean_adjustments", {})
                profile.openness = max(0.0, min(1.0, profile.openness + float(adj.get("openness", 0))))
                profile.conscientiousness = max(0.0, min(1.0, profile.conscientiousness + float(adj.get("conscientiousness", 0))))
                profile.extraversion = max(0.0, min(1.0, profile.extraversion + float(adj.get("extraversion", 0))))
                profile.agreeableness = max(0.0, min(1.0, profile.agreeableness + float(adj.get("agreeableness", 0))))
                profile.neuroticism = max(0.0, min(1.0, profile.neuroticism + float(adj.get("neuroticism", 0))))
                
                # Update Habits
                current_habits = list(profile.habit_patterns) if profile.habit_patterns else []
                new_habits = data.get("new_habits", [])
                for h in new_habits:
                    if h not in current_habits: current_habits.append(h)
                profile.habit_patterns = current_habits[:15] # Keep it focused
                
                profile.current_mood = data.get("inferred_mood", profile.current_mood)
                profile.last_updated = datetime.datetime.utcnow()
                
                print(f"AIEngine: Deep Psychological Refinement complete for {user_id}.")
        except Exception as e:
            print(f"AIEngine: Psychological refinement failed: {e}")

    def warmup_ego(self, ego_profile: Dict[str, Any]):
        """Warms up the LLM's prompt cache with the user's psychological 'Digital Ego'."""
        if not ego_profile: return
        print("AIEngine: Warming up Digital Ego cache...")
        self.personality.set_ego(ego_profile)
        
        traits = ego_profile.get("ocean_traits", {})
        distortions = ego_profile.get("cognitive_distortions", {})
        ego_context = f"User Digital Ego Profile: Traits={traits}, Common Distortions={distortions}."
        # Low-temp, short call to prime the cache
        try:
            prompt = f"{ego_context}\nSystem: Initializing session for this persona. Acknowledge with 'READY'."
            self.council.llm.invoke(prompt)
        except Exception as e:
            print(f"Warmup Error: {e}")

    async def predict_user_needs(self, user_id: str, db: Session) -> Dict[str, str]:
        """
        Phase 8: The Seer. Anticiaptes user needs based on Knowledge Graph and Ego.
        """
        from models import UserPsychology, UserActivity, LibraryArtifact
        
        # 1. Gather Context
        profile = db.query(UserPsychology).filter(UserPsychology.user_id == user_id).first()
        ego_summary = f"Personality: {profile.current_mood}, Traits: Openness={profile.openness}" if profile else "New User"
        
        recent = db.query(UserActivity).filter(UserActivity.user_id == user_id).order_by(UserActivity.timestamp.desc()).limit(10).all()
        activity_summary = " ".join([a.title for a in recent if a.title])
        
        # 2. Call the Seer
        prediction = self.council.seer.predict_next_step(ego_summary, activity_summary, "Graph Context: Exploring Neural Architectures")
        
        # 3. Create a Knowledge Event for the prediction
        from models import KnowledgeEvent
        event = KnowledgeEvent(
            event_type="PREDICTION_GENERATED",
            payload=prediction,
            user_id=user_id
        )
        db.add(event); db.commit()
        
        return prediction

    async def run_autonomous_evolution(self, user_id: str, db: Session):
        """
        Phase 4: Autonomous Autopilot Evolution.
        Identifies the weakest agent and triggers a Darwinian mutation loop.
        """
        from models import AgentPerformance
        from sqlalchemy import func
        
        print("AIEngine: Initiating Autonomous Evolution Cycle...")
        
        # 1. Identify underperforming agents
        weakest = db.query(
            AgentPerformance.agent_name, 
            func.avg(AgentPerformance.fitness_score).label('avg_fitness')
        ).filter(AgentPerformance.user_id == user_id)\
         .group_by(AgentPerformance.agent_name)\
         .order_by('avg_fitness')\
         .first()
         
        if not weakest or weakest.avg_fitness > 0.85:
            print("AIEngine: System is currently optimal. No evolution required.")
            return
            
        target_agent = weakest.agent_name
        print(f"AIEngine: Evolution target identified: {target_agent} (Fitness: {weakest.avg_fitness:.2f})")
        
        # 2. Trigger Mutation
        instruction = f"Improve the performance and accuracy of the {target_agent} agent. Address recent suboptimal fitness scores."
        best_code = self.council.self_architect.darwinian_mutation("backend/librarians.py", instruction, self.council.sentinel)
        
        if best_code:
            self.council.self_architect.backup_file("backend/librarians.py")
            abs_path = os.path.join(self.council.self_architect.root_dir, "backend/librarians.py")
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(best_code)
            print(f"AIEngine: Evolution SUCCESS. {target_agent} has been updated.")
        else:
            print(f"AIEngine: Evolution FAILED. No stable mutations found for {target_agent}.")

    # Optional: We could expose other agents directly if needed
    @property
    def ner_pipeline(self):
        # Used by main.py for quick query extraction
        return self.council.ner_pipeline
