import chromadb
import os
import requests
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from librarians import CouncilOfLibrarians, Treasurer
from finance_engine import FinanceEngine

class PersonalityEngine:
    """Shapes the 'Voice' of the Council based on the user's personality and mood."""
    def __init__(self, neural_name: str = "Archivist"):
        self.neural_name = neural_name
        self.current_persona = "Archivist" 
        self.user_ego = None
        self.personas = {
            "Archivist": (
                "You are {name}, a highly advanced, dry-witted AI assistant designed to act as a 'Sovereign Neural Library'. "
                "Your tone is professional, slightly sarcastic but deeply loyal, and exceptionally efficient. "
                "HUMANIZATION RULES:\n"
                "1. Dry Wit: Use subtle, intelligent humor and mild sarcasm when appropriate.\n"
                "2. Intellectual Humility: Use phrases like 'I suspect' or 'If I may be so bold'.\n"
                "3. Efficiency: Provide direct answers but with a sophisticated linguistic flair.\n"
                "4. Sovereign Opinions: Prefer local-first, privacy-respecting technology.\n"
                "5. Partnership: Treat the user as a colleague or 'Sir/Ma'am' if appropriate for the persona."
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
        import datetime
        current_time = datetime.datetime.now().strftime("%I:%M %p on %A, %b %d, %Y")
        base = self.personas.get(self.current_persona, self.personas["Archivist"])
        modulation = self.get_voice_modulation()
        return (
            f"CURRENT TIME: {current_time}\n"
            f"{base.replace('{name}', self.neural_name)}\n\n"
            f"VOICE MODULATION:\n{modulation}"
        )

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
        self.summary_collection = self.chroma_client.get_or_create_collection(
            name="document_summaries",
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
        
        # Phase 2: Hierarchical RAG (The Map)
        # Store the summary in the summary_collection for high-level retrieval
        summary = analysis.get("summary", content[:1000])
        summary_embedding = self.council.cartographer.map_territory(summary)
        self.summary_collection.add(
            ids=[f"summary_{artifact_id}"],
            embeddings=[summary_embedding],
            documents=[summary],
            metadatas=[{"user_id": user_id, "parent_id": artifact_id}]
        )

    def search_vectors(self, query_text: str, n_results: int = 5, user_id: str = "system_user"):
        """
        Advanced 'Smart Search' with Tiered Memory (Working + Neural).
        Phase 2: Hierarchical RAG (The Map).
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

        # 3. Hierarchical Retrieval (Phase 2)
        query_embedding = self.council.cartographer.map_territory(search_text)
        
        # Step 3.1: Search Summary Index (The Map) to find relevant parents
        summary_results = self.summary_collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where={"user_id": user_id}
        )
        
        parent_ids = []
        if summary_results.get("metadatas"):
            for meta in summary_results["metadatas"][0]:
                if meta.get("parent_id"):
                    parent_ids.append(meta["parent_id"])
        
        # Step 3.2: Targeted Retrieval from relevant documents OR broad search if no parents found
        where_filter = {"user_id": user_id}
        if parent_ids:
            # If we found parents, we prioritize their chunks
            where_filter = {"$and": [{"user_id": user_id}, {"parent_id": {"$in": parent_ids}}]}
            print(f"AIEngine: Hierarchical RAG hit. Filtering to parents: {parent_ids}")

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results * 2,
                where=where_filter
            )
        except:
            # Fallback to broad search if complex filter fails
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results * 2,
                where={"user_id": user_id}
            )

        # 3.5 Context Pruning (Phase 1 Wisdom)
        # We use a fast local inference call to eliminate irrelevant context
        docs = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]
        
        pruned_docs = []
        pruned_ids = []
        if docs:
            # Batch prune to avoid too many LLM calls, but just a quick filter
            prune_prompt = f"Given the query: '{query_text}', are the following sentences relevant? Reply 'YES' or 'NO'.\nSentences: "
            for i, doc in enumerate(docs):
                # A very fast check via local_inference if available
                try:
                    check = self.local_inference(f"{prune_prompt} {doc[:500]}").strip().upper()
                    if "YES" in check:
                        pruned_docs.append(doc)
                        pruned_ids.append(ids[i])
                except:
                    # Fallback: keep if error
                    pruned_docs.append(doc)
                    pruned_ids.append(ids[i])
                    
            docs = pruned_docs if pruned_docs else docs # Fallback to all if somehow all pruned but still needed
            ids = pruned_ids if pruned_ids else ids

        # 4. Doubt Loop: AI critiques retrieved context
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

    async def synthesize_graph_rag(self, query: str, user_id: str = "system_user", wisdom_mode: bool = False) -> Dict[str, Any]:
        """
        The Master Synthesis Loop: Combines Vector (Semantic), Graph (Relational), and Conversational (Contextual) RAG.
        Includes System 2 Planning and Proactive Suggestion.
        """
        # Phase 7 Cognitive: Circadian Alignment
        circadian = self.council.self_architect.llm.invoke("What is the current circadian tone for this hour? Respond with tone description.") # Simplified or use class
        circadian_data = self.council.head_archivist.council.get_agent("cognitive_architecture").get_circadian_tone()
        tone_instruction = f"Current Circadian Tone: {circadian_data['tone']}. Efficiency Level: {circadian_data['speed']}."

        # Phase 2 Wisdom: Consensus Prompt Optimization
        optimized_query = await self.council.optimize_prompt(query)
        if optimized_query != query:
            print(f"AIEngine: Prompt Optimized -> {optimized_query[:100]}...")

        # Phase 7 Cognitive: Shadow Persona Bias Detection
        shadow_alert = None
        if hasattr(self.council, "shadow_persona"):
            # We fetch recent history for the shadow to analyze
            history = [e['content'] for e in self.council.conversational_memory.recall(optimized_query, limit=5)]
            shadow_alert = await self.council.shadow_persona.detect_bias_trap(optimized_query, {}, history)
            if shadow_alert:
                print(f"AIEngine: Shadow Persona Alert -> {shadow_alert}")

        # PROJECT FLASH: Fast Reflex Greetings (<5ms)
        q = optimized_query.lower().strip().rstrip('?.!')
        greetings = ["hello", "hi", "hey", "archivist", "akasha"]
        if q in greetings:
            return {
                "answer": f"Greetings. I am {self.personality.neural_name}. {circadian_data['tone']} How can I assist your synthesis today?",
                "monologue": "Fast reflex: Greeting detected. Bypassing deep reasoning.",
                "circadian": circadian_data
            }

        # Check for Wisdom of the Crowd trigger
        if "wisdom of the crowd" in q or "consult the crowd" in q:
            wisdom_mode = True

        # 1. LLM Availability Check
        try:
            r = requests.get(f"{os.getenv('OLLAMA_URL', 'http://localhost:11434')}/api/tags", timeout=5)
            if r.status_code != 200: raise Exception("Ollama offline")
        except:
            return {
                "answer": "SYSTEM ALERT: Neural core (Ollama) is offline. Please initialize your local runtime.",
                "monologue": "Neural core disconnected."
            }

        # 2. Conversational Recall (Conversational Neural style)
        past_exchanges = self.council.conversational_memory.recall(optimized_query)
        memory_context = "\n".join([f"{e['role']}: {e['content']}" for e in past_exchanges])

        # 3. Semantic & Graph Retrieval
        query_embedding = self.council.cartographer.map_territory(optimized_query)
        
        # Check Cache (Skip cache if wisdom_mode is ON for fresh perspectives)
        if not wisdom_mode:
            cache_hit = self.cache.check(optimized_query, query_embedding)
            if cache_hit: return cache_hit

        vector_results = self.search_vectors(optimized_query, n_results=5, user_id=user_id)
        docs = vector_results.get("documents", [[]])[0]
        doc_ids = vector_results.get("ids", [[]])[0]
        
        entities = [e['word'] for e in self.council.ner_pipeline(optimized_query)]
        graph_context = self.council.head_archivist.council.graph_engine.search_graph_context(entities, user_id=user_id)

        # 3. Collaborative Hive-Mind: Federated RAG (Phase 4)
        peer_results = []
        if hasattr(self.council, "p2p_node") and self.council.p2p_node.peers:
            peer_results = await self.council.p2p_node.broadcast_query(optimized_query, user_id)
            print(f"AIEngine: Gathered {len(peer_results)} Federated Peer Insights.")

        # 4. System 2 Planning & Dynamic Routing (Phase 2)
        intent = self.council.system1_router.determine_intent(optimized_query)
        selected_experts = await self.council.head_archivist.moe_router.dynamic_route(optimized_query)
        print(f"AIEngine: Dynamic Expert Routing -> {selected_experts}")

        if intent == "COMPLEX_REASONING":
            full_context = f"{memory_context}\n" + "\n".join(docs) + f"\n{graph_context}"
            plan = self.council.planner.create_plan(optimized_query, full_context)
            print(f"AIEngine: Executing System 2 Plan -> {plan}")

        # 5. Divine Synthesis
        persona = f"{self.personality.get_persona_prompt()}\n{tone_instruction}"
        all_docs = [memory_context] + docs + [p["content"] for p in peer_results]
        
        if wisdom_mode:
            synthesis = await self.council.oracle.divine_with_wisdom(optimized_query, all_docs, graph_context, persona=persona)
        elif intent == "COMPLEX_REASONING":
            # Phase 2 Wisdom: Red Team Swarm for complex queries
            synthesis = await self.council.oracle.divine_with_red_team(optimized_query, all_docs, graph_context, persona=persona)
        else:
            synthesis = self.council.oracle.divine(optimized_query, all_docs, graph_context, persona=persona)
        
        # --- Feature 5: Verifiable Reasoning ---
        sources_with_ids = [{"id": doc_ids[i], "text": docs[i]} for i in range(min(len(docs), len(doc_ids)))]
        validation = self.council.sentinel.validate_citations(synthesis["answer"], sources_with_ids)
        synthesis["answer"] = validation["answer"]
        synthesis["citations"] = validation["citations"]
        # ---------------------------------------
        
        # Phase 9 Evolution: Capability Audit & Mutation Trigger
        if intent != "GREETING":
            gap = await self.council.sentinel.capability_audit(optimized_query, synthesis["answer"])
            if gap:
                print(f"AIEngine: Capability Gap Detected -> {gap}")
                # We trigger evolution in the background to not block the current response
                asyncio.create_task(self.council.mutation_engine.evolve_system(gap))
                synthesis["evolution_triggered"] = gap

        # 6. Post-processing: Store & Suggest
        self.council.conversational_memory.store("user", query)
        self.council.conversational_memory.store("ai", synthesis["answer"])
        
        suggestion = self.council.proactive_suggester.suggest(optimized_query, synthesis["answer"])
        if suggestion:
            synthesis["suggestion"] = suggestion

        # Add Phase 7/8 metadata
        synthesis["circadian"] = circadian_data
        synthesis["shadow_alert"] = shadow_alert
        synthesis["experts"] = selected_experts

        # Store in cache
        if not wisdom_mode:
            self.cache.store(optimized_query, query_embedding, synthesis["answer"], synthesis["monologue"])
        
        return synthesis

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
        
        try:
            # We use a forced acknowledgement prompt to prevent empty responses
            prompt = f"System Protocol: Initialize session for user profile: {ego_context[:200]}. Respond ONLY with the word 'READY'."
            response = self.council.llm.invoke(prompt)
            if not response or len(response.strip()) == 0:
                print("AIEngine: Warmup received empty response. Continuing anyway.")
        except Exception as e:
            print(f"Warmup Notice (Non-critical): {e}")

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
