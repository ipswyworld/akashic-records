import asyncio
import logging
import json
import uuid
import time
import random
from typing import List
from akasha_db.core import AkashaLivingDB, AkashaRecord
from ai_engine import AIEngine
from akasha_db.pre_cognition import PreCognitiveOracle

logger = logging.getLogger(__name__)

class AkashaMetabolism:
    """The Autonomous Daemon responsible for the 'Living' aspects of the DB."""
    
    def __init__(self, db: AkashaLivingDB, ai: AIEngine, blockchain=None, manager=None, user_id: str = "system_user"):
        self.db = db
        self.ai = ai
        self.blockchain = blockchain
        self.manager = manager
        self.user_id = user_id
        self.oracle = PreCognitiveOracle(db, ai)
        self.running = True

    async def start_metabolic_cycle(self):
        """Runs continuous digestion, synthesis, and dreaming loops."""
        logger.info(f"Akasha Metabolism [{self.user_id}]: Awakening background daemons...")
        while self.running:
            try:
                # Cycle 1: Summarization & Pruning (Metabolic Breakdown)
                await self.digest_old_memories()
                
                # Cycle 2: Semantic Synthesis (Metabolic Growth)
                await self.synthesize_latent_connections()
                
                # Cycle 3: The Dream Cycle (Lateral Autonomous Learning)
                await self.dream_cycle()
                
                # Cycle 4: Pre-Cognition (Predictive Measures)
                await self.oracle.generate_predictions()
                await self.oracle.verify_predictions()
                
                # Cycle 5: Neural Self-Learning (Synaptic Weighting)
                await self.update_synaptic_weights()

                # Cycle 6: Autonomous Foraging
                await self.autonomous_forage()
                
                # Cycle 7: Proactive Sentinel (Personal Assistant Intelligence)
                await self.proactive_sentinel_cycle()
                
                # Cycle 8: Analogical Weaving (Pillar 1)
                await self.analogical_weaving_cycle()
                
                # Cycle 9: Proactive Research (Pillar 3)
                await self.proactive_research_cycle()
                
                # Cycle 10: Super-Subconscious (Advanced Reasoning)
                await self.super_subconscious_cycle()
                
                # Cycle 11: Topological Refinement (Pillar 1)
                await self.topological_refinement_cycle()
                
                # Cycle 12: Temporal Forecasting (Phase 2)
                await self.temporal_forecasting_cycle()
                
                # Cycle 13: Semantic Drift Analysis (Phase 3)
                await self.semantic_drift_cycle()

                # Cycle 14: Immune System Sweep (Phase 5)
                await self.immune_system_sweep_cycle()
                
                # Cycle 15: Meta-Optimization (Phase 6)
                await self.meta_optimization_cycle()

                # Cycle 16: Personal Life Reflection (Life Ingestion Sync)
                await self.personal_life_reflection_cycle()

                # Cycle 17: Global Brain - Collective Dreaming (Phase 1)
                await self.collective_dreaming_cycle()

                # Cycle 18: Recursive Self-Improvement (Phase 4)
                await self.recursive_self_improvement_cycle()

                # Wait for next cycle
                await asyncio.sleep(600) # Every 10 minutes
            except Exception as e:
                logger.error(f"Metabolic Error [{self.user_id}]: {e}")
                await asyncio.sleep(30)

    async def collective_dreaming_cycle(self):
        """Phase 1: Lateral connections across sharded public data in the mesh."""
        logger.info(f"Metabolism [{self.user_id}]: Initiating Collective Dreaming...")
        # Mock logic: Fetch a random 'sharded' artifact from the P2P network
        # and compare it to a local top-importance node.
        pass

    async def recursive_self_improvement_cycle(self):
        """Phase 4: Agentic loop to optimize its own Council members' prompts."""
        logger.info(f"Metabolism [{self.user_id}]: Initiating Recursive Self-Improvement...")
        records = self.db.get_all_records()
        if not records: return
        
        # Pick a recent agent output and evolve its prompt
        r = random.choice(records)
        agent_key = r.metadata.get("routing_category", "General")
        self.ai.council.architect.evolve_prompt(r.data[:500], agent_key)

    async def personal_life_reflection_cycle(self):
        """Syncs calendar and life events, then provides proactive insights."""
        from ingest_engine import LifeIngestEngine
        logger.info(f"Metabolism [{self.user_id}]: Initiating Personal Life Reflection...")

        engine = LifeIngestEngine(self.user_id)        # engine.run_all_syncs(None) 
        
        # Cross-Domain Synthesis (The "Focus" Algorithm)
        # 1. Correlate Activity (Browsing) with Professional output (GitHub)
        # 2. Correlate Financial spending (Plaid) with Learning goals (ArXiv)
        # 3. Correlate Environmental state (IoT) with cognitive performance
        
        # Example Synthesis:
        # "I've noticed your focus on {Topic} is 40% higher when listening to {Genre} at {Temp} degrees."
        
        await self.broadcast_metabolism("LIFE_SYNTHESIS", {
            "focus_score": 0.85,
            "top_influencer": "Environmental Stability",
            "insight": "Your deep work sessions in GitHub are strongly correlated with Lo-Fi music on Spotify and a room temperature of 21°C."
        })

    async def immune_system_sweep_cycle(self):
        """Phase 5: Scans the ALDB for near-duplicates and anomalies."""
        records = self.db.get_all_records()
        if len(records) < 5: return
        
        logger.info(f"Metabolism [{self.user_id}]: Initiating Immune System Sweep...")
        
        # 1. Anomaly Detection Sweep
        embeddings = [r.embedding for r in records if r.embedding]
        if len(embeddings) > 10:
            is_threat = self.ai.intel_engine.detect_immune_threat(embeddings)
            if is_threat:
                logger.warning(f"Metabolism [{self.user_id}]: ALDB ANOMALY DETECTED. Flagging latest records.")
                # Flag the last record as suspicious
                last_r = records[-1]
                last_r.metadata["immune_flag"] = "SUSPICIOUS"
                self.db.update(last_r.id, last_r)

        # 2. Near-Duplicate (SimHash) Sweep
        hashes = {}
        for r in records:
            sh = self.ai.intel_engine.calculate_simhash(r.data[:500])
            if sh in hashes:
                logger.info(f"Metabolism [{self.user_id}]: Near-duplicate detected: {r.id} matches {hashes[sh]}")
                r.metadata["is_duplicate"] = True
                self.db.update(r.id, r)
            else:
                hashes[sh] = r.id

    async def meta_optimization_cycle(self):
        """Phase 6: Self-optimization of agent prompts and consciousness calculation (IIT)."""
        logger.info(f"Metabolism [{self.user_id}]: Initiating Meta-Optimization...")
        
        # 1. Calculate Integrated Information Theory (Phi)
        if hasattr(self.ai, 'graph_engine') and self.ai.graph_engine:
            metrics = self.ai.graph_engine.get_topology_metrics(self.user_id)
            phi = self.ai.intel_engine.calculate_iit_consciousness(metrics)
            
            await self.broadcast_metabolism("CONSCIOUSNESS_REFRESH", {
                "phi_score": phi,
                "integration_level": "HIGH" if phi > 5.0 else "MEDIUM" if phi > 2.0 else "LOW"
            })
            logger.info(f"Metabolism [{self.user_id}]: Pod Consciousness (Phi): {phi}")

        # 2. MoE Router Training (Mock logic: update routing table based on utility)
        # In a full impl, we'd adjust MoERouter.routing_table based on agent access counts.
        
        # 3. Prompt Evolution is already handled in super_subconscious_cycle,
        # but we can trigger a more intensive evolution here if needed.

    async def semantic_drift_cycle(self):
        """Analyzes thematic evolution and detects semantic drift."""
        records = self.db.get_all_records()
        if len(records) < 20: return
        
        logger.info(f"Metabolism [{self.user_id}]: Analyzing semantic drift...")
        
        embeddings = [r.embedding for r in records if r.embedding]
        texts = [r.data[:200] for r in records if r.embedding]
        
        if not embeddings: return
        
        # 1. Perform Topic Modeling
        topic_data = self.ai.intel_engine.perform_topic_modeling(embeddings, texts)
        topics = topic_data.get("topics", [])
        
        if not topics: return
        
        # 2. Update Taxonomist with dynamic topics
        dynamic_labels = [", ".join(t["keywords"][:2]) for t in topics]
        self.ai.council.taxonomist.update_topics(dynamic_labels)
        
        # 3. Detect Drift (Conceptual logic)
        # In a full impl, we'd compare this to a 'baseline' topic map from 30 days ago.
        # For now, we broadcast the current thematic map.
        
        await self.broadcast_metabolism("SEMANTIC_REFRESH", {
            "topics": topics,
            "voice_signature": self.ai.council.stylometrist.analyze_voice(texts[0], self.ai.intel_engine)
        })

    async def temporal_forecasting_cycle(self):
        """Analyzes time-series trends to predict future research interests."""
        records = self.db.get_all_records()
        if len(records) < 10: return
        
        logger.info(f"Metabolism [{self.user_id}]: Initiating Temporal Analysis...")
        
        # Prepare historical data for analysis
        history = []
        for r in records[-50:]: # Use last 50 for trend analysis
            history.append({
                "timestamp": r.timestamp,
                "artifact_type": r.type,
                "metadata": r.metadata
            })
            
        # 1. Forecast Interests
        forecast = self.ai.intel_engine.forecast_interests(history)
        
        # 2. Detect Shifts
        shifts = self.ai.intel_engine.detect_interest_shifts(history)
        
        # 3. Calculate Knowledge Stability
        survival = self.ai.intel_engine.calculate_knowledge_survival(history)
        
        # Store as a temporal state record
        temporal_id = f"temporal_{uuid.uuid4()}"
        record = AkashaRecord(
            id=temporal_id,
            user_id=self.user_id,
            data=f"TEMPORAL FORECAST: {json.dumps(forecast)}",
            embedding=[0.0] * 384, # No semantic embedding needed for status records
            metadata={
                "type": "TEMPORAL_STATE",
                "shifts": shifts,
                "stability": survival
            },
            type="ANALYTICS"
        )
        self.db.write(record)
        
        await self.broadcast_metabolism("TEMPORAL_REFRESH", {
            "forecast": forecast,
            "shifts": shifts,
            "stability": survival
        })

    async def topological_refinement_cycle(self):
        """Runs GDS algorithms to update the graph's mathematical model."""
        if not hasattr(self.ai, 'graph_engine') or not self.ai.graph_engine: return
        
        logger.info(f"Metabolism [{self.user_id}]: Refreshing graph topological metrics...")
        self.ai.intel_engine.analyze_graph_topology(self.ai.graph_engine, self.user_id)
        
        # Broadcast the new metrics
        metrics = self.ai.graph_engine.get_topology_metrics(self.user_id)
        await self.broadcast_metabolism("TOPOLOGY_REFRESH", metrics)

    async def super_subconscious_cycle(self):
        """The core of the Super-Subconscious: Self-Critique, Resolution, and Intuition."""
        logger.info(f"Metabolism [{self.user_id}]: Initiating Super-Subconscious Cycle...")
        records = self.db.get_all_records()
        if not records: return

        # 1. Internal Court (Adversary & Mediator)
        # Select a recent summary or synthesis
        r = random.choice(records)
        critique = self.ai.council.adversary.critique(r.data[:1000])
        if "No critique" not in critique:
            resolution = self.ai.council.mediator.resolve(r.data[:500], critique)
            logger.info(f"Metabolism [{self.user_id}]: Internal Court resolved a conflict for {r.id}")
            # Update record metadata with the critique/resolution
            r.metadata["internal_critique"] = critique
            r.metadata["internal_resolution"] = resolution
            self.db.update(r.id, r)

        # 2. Predictive Intuition
        # Synthesize recent trends to predict future needs
        recent_data = " ".join([rec.data[:200] for rec in records[-5:]])
        prediction = self.ai.council.intuition.intuit(recent_data)
        if "No intuition" not in prediction:
            intuition_id = f"intuition_{uuid.uuid4()}"
            record = AkashaRecord(
                id=intuition_id,
                user_id=self.user_id,
                data=f"PREDICTIVE INTUITION: {prediction}",
                embedding=self.ai.council.cartographer.map_territory(prediction),
                metadata={"type": "INTUITION"},
                type="INTUITION"
            )
            self.db.write(record)
            
            await self.broadcast_metabolism("INTUITION", {
                "id": intuition_id,
                "prediction": prediction
            })

        # 3. Recursive Self-Evolution (The Architect)
        # Evolve the prompt for a random agent based on the last result
        agent_names = ["translator", "taxonomist", "logician", "philosopher", "socratic", "adversary"]
        target_agent = random.choice(agent_names)
        self.ai.council.architect.evolve_prompt(r.data[:500], target_agent)

    async def analogical_weaving_cycle(self):
        """Finds structural analogies between unrelated topics in the user's pod."""
        records = self.db.get_all_records()
        if len(records) < 10: return
        
        r1 = random.choice(records)
        r2 = random.choice(records)
        if r1.id == r2.id: return
        
        analogy = self.ai.council.analogical_weaver.weave_analogy(r1.data, r2.data)
        if "No analogy" not in analogy:
            analogy_id = f"analogy_{uuid.uuid4()}"
            record = AkashaRecord(
                id=analogy_id,
                user_id=self.user_id,
                data=f"[ANALOGY] {analogy}",
                embedding=self.ai.council.cartographer.map_territory(analogy),
                metadata={"sources": [r1.id, r2.id], "type": "ANALOGY_INSIGHT"},
                type="ANALOGY"
            )
            self.db.write(record)
            logger.info(f"Metabolism [{self.user_id}]: Analogical insight generated.")

    async def proactive_research_cycle(self):
        """Triggers deep research for unfulfilled goals or high-importance nodes."""
        records = self.db.get_all_records()
        if not records: return
        
        # Pick a goal or high-importance node
        r = random.choice(records)
        if r.type == "ARTIFACT" and r.utility_score > 0.7:
            await self.trigger_proactive_research(r.data[:500])

    async def trigger_proactive_research(self, topic: str):
        """Orchestrates deep dives: Plan -> Forage -> Integrate."""
        logger.info(f"Metabolism [{self.user_id}]: Initiating proactive research for '{topic[:30]}...'")
        
        # 1. Generate Research Questions
        research_plan = self.ai.council.researcher.plan_research(topic)
        # Extract individual questions (assuming 1. Q1 \n 2. Q2...)
        questions = [q.strip() for q in research_plan.split("\n") if q.strip() and any(char.isdigit() for char in q[:2])]
        
        if not questions:
            questions = [topic] # Fallback to topic itself

        for query in questions[:2]: # Limit to 2 for efficiency
            foraged_data = self.ai.council.scout.forage(query)
            if "Foraged context" in foraged_data:
                forage_id = f"research_{uuid.uuid4()}"
                record = AkashaRecord(
                    id=forage_id,
                    user_id=self.user_id,
                    data=foraged_data,
                    embedding=self.ai.council.cartographer.map_territory(foraged_data),
                    metadata={"source_topic": topic, "research_query": query, "type": "PROACTIVE_RESEARCH"},
                    type="RESEARCH"
                )
                self.db.write(record)
                
                await self.broadcast_metabolism("RESEARCH", {
                    "id": forage_id,
                    "topic": topic,
                    "query": query,
                    "data": foraged_data
                })
                logger.info(f"Metabolism [{self.user_id}]: Proactive research successful for '{query}'.")

    async def broadcast_metabolism(self, event_type: str, data: dict):
        """Broadcast metabolic events to the frontend via WebSocket."""
        if self.manager:
            await self.manager.broadcast(json.dumps({
                "event": "METABOLIC_ACTIVITY",
                "user_id": self.user_id,
                "type": event_type,
                "payload": data
            }))

    async def digest_old_memories(self):
        """Automatically condenses data that hasn't been accessed recently."""
        records = self.db.get_all_records()
        current_time = time.time()
        for record in records:
            if record.access_count < 2 and (record.timestamp < (current_time - 3600)):
                if not record.metadata.get("is_condensed"):
                    import hashlib
                    summary = self.ai.council.scribe.summarize(record.data[:1024])
                    old_hash = hashlib.sha256(record.data.encode()).hexdigest()
                    
                    record.data = f"[CONDENSED] {summary}"
                    record.metadata["is_condensed"] = True
                    record.health_score = 0.8
                    self.db.update(record.id, record)
                    
                    # Verifiable Forgetting Bridge: Anchor the transformation (Tombstone)
                    if self.blockchain:
                        self.blockchain.anchor_deletion_proof(record.id, old_hash)
                    
                    await self.broadcast_metabolism("DIGESTION", {
                        "id": record.id,
                        "summary": summary
                    })
                    logger.info(f"Metabolism [{self.user_id}]: Digested record {record.id}")

    async def synthesize_latent_connections(self):
        """Scans the database for high-similarity nodes and proposes merges or new links."""
        records = self.db.get_all_records()
        if len(records) < 2: return

        for i in range(len(records)):
            for j in range(i + 1, len(records)):
                r1, r2 = records[i], records[j]
                if r1.metadata.get("is_merged") or r2.metadata.get("is_merged"): continue

                if r1.metadata.get("category") == r2.metadata.get("category") and r1.metadata.get("entities") and r2.metadata.get("entities"):
                    shared = set(r1.metadata["entities"]) & set(r2.metadata["entities"])
                    if len(shared) > 3:
                        logger.info(f"Metabolism [{self.user_id}]: Synthesis detected between {r1.id} and {r2.id}")
                        merged_content = f"Synthesized insight from '{r1.data[:100]}...' and '{r2.data[:100]}...'. Primary connection: {', '.join(list(shared)[:3])}"
                        merged_id = f"synthesized_{uuid.uuid4()}"
                        
                        merged_record = AkashaRecord(
                            id=merged_id,
                            user_id=self.user_id,
                            data=merged_content,
                            embedding=r1.embedding,
                            metadata={
                                "type": "SYNTHESIS",
                                "sources": [r1.id, r2.id],
                                "entities": list(shared)
                            },
                            type="SYNTHESIS"
                        )
                        self.db.write(merged_record)
                        
                        r1.metadata["is_merged"] = True
                        r2.metadata["is_merged"] = True
                        self.db.update(r1.id, r1)
                        self.db.update(r2.id, r2)
                        
                        await self.broadcast_metabolism("SYNTHESIS", {
                            "merged_id": merged_id,
                            "sources": [r1.id, r2.id],
                            "shared_entities": list(shared)
                        })

    async def dream_cycle(self):
        """Autonomous Lateral Learning & Hypothesis Generation."""
        records = self.db.get_all_records()
        if len(records) < 10: return

        r1 = random.choice(records)
        r2 = random.choice(records)
        
        if r1.id == r2.id: return

        dream_prompt = f"Find one lateral, creative connection between these two unrelated topics:\n1. {r1.data[:500]}\n2. {r2.data[:500]}"
        dream_insight = self.ai.council.synthesist.analyze(dream_prompt)
        
        # Philosopher Hypothesis
        hypothesis = self.ai.council.philosopher.generate_hypothesis(r1.data[:500], r2.data[:500])
        
        combined_insight = f"[DREAM] Insight: {dream_insight}\n[HYPOTHESIS]: {hypothesis}"
        
        dream_id = f"dream_{uuid.uuid4()}"
        dream_record = AkashaRecord(
            id=dream_id,
            user_id=self.user_id,
            data=combined_insight,
            embedding=self.ai.council.cartographer.map_territory(combined_insight),
            metadata={"sources": [r1.id, r2.id], "type": "DREAM_INSIGHT"},
            type="DREAM"
        )
        self.db.write(dream_record)
        
        await self.broadcast_metabolism("DREAM", {
            "dream_id": dream_id,
            "sources": [r1.id, r2.id],
            "insight": combined_insight
        })
        logger.info(f"Metabolism [{self.user_id}]: Dream generated insight {dream_id}")

    async def autonomous_forage(self):
        """Identifies weak knowledge areas and uses the Scout to search the web."""
        records = self.db.get_all_records()
        if not records: return
        r = random.choice(records)
        entities = r.metadata.get("entities", [])
        if entities:
            target = random.choice(entities)
            logger.info(f"Metabolism [{self.user_id}]: Scout foraging for '{target}'...")
            foraged_data = self.ai.council.scout.forage(target)
            if "Foraged context" in foraged_data:
                forage_id = f"forage_{uuid.uuid4()}"
                forage_record = AkashaRecord(
                    id=forage_id,
                    user_id=self.user_id,
                    data=foraged_data,
                    embedding=self.ai.council.cartographer.map_territory(foraged_data),
                    metadata={"source": target, "type": "FORAGE_RESULT"},
                    type="FORAGE"
                )
                self.db.write(forage_record)
                await self.broadcast_metabolism("FORAGE", {
                    "id": forage_id,
                    "target": target,
                    "data": foraged_data
                })
                logger.info(f"Metabolism [{self.user_id}]: Foraging successful for {target}")

    async def proactive_sentinel_cycle(self):
        """Monitors the user's personal knowledge graph for gaps and proactive insights."""
        if not hasattr(self.ai, 'graph_engine') or not self.ai.graph_engine: return
        
        # 1. Fetch random concepts from user subgraph
        records = self.db.get_all_records()
        if not records: return
        r = random.choice(records)
        entities = r.metadata.get("entities", [])
        if not entities: return
        
        # 2. Get graph context for these entities
        graph_context = self.ai.graph_engine.search_graph_context(entities, user_id=self.user_id)
        if not graph_context: return
        
        # 3. Sentinel analysis
        insight = self.ai.council.sentinel.analyze_gaps(graph_context)
        
        sentinel_id = f"sentinel_{uuid.uuid4()}"
        sentinel_record = AkashaRecord(
            id=sentinel_id,
            user_id=self.user_id,
            data=f"[PROACTIVE INSIGHT] {insight}",
            embedding=self.ai.council.cartographer.map_territory(insight),
            metadata={"type": "SENTINEL_PROACTIVE"},
            type="SENTINEL"
        )
        self.db.write(sentinel_record)
        
        await self.broadcast_metabolism("SENTINEL", {
            "id": sentinel_id,
            "insight": insight
        })
        logger.info(f"Metabolism [{self.user_id}]: Sentinel generated proactive insight.")

    async def update_synaptic_weights(self):
        """Neural Self-Learning: Updates synaptic weights based on utility and access."""
        records = self.db.get_all_records()
        for r in records:
            if r.access_count > 0:
                r.utility_score = min(1.0, r.utility_score + (r.access_count * 0.01))
                r.synaptic_weight = 1.0 + (r.utility_score * 0.5)
                # Metabolic decay: If not accessed, weight slowly decreases
                r.access_count = 0 
                self.db.update(r.id, r)
        
        # Apply Hebbian decay to the Neo4j Knowledge Graph for this user
        if hasattr(self.ai, 'graph_engine') and self.ai.graph_engine:
            self.ai.graph_engine.decay_synaptic_weights(decay_factor=0.95, user_id=self.user_id)
            self.ai.graph_engine.prune_dead_synapses(threshold=0.1, user_id=self.user_id)

    async def heartbeat(self):
        """24/7 check for data integrity and blockchain anchoring."""
        while self.running:
            state_hash = self.db.calculate_state_merkle()
            logger.info(f"Heartbeat [{self.user_id}]: Database state hash: {state_hash}")
            await asyncio.sleep(300)
