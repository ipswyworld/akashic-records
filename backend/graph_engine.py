from neo4j import GraphDatabase
import os
from typing import List, Dict

class GraphEngine:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "akasha_password")
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            self.is_active = True
        except Exception:
            print("GraphEngine: Neo4j not reachable. Knowledge Graph features will be limited.")
            self.is_active = False
            self.driver = None

    def close(self):
        if self.is_active and self.driver:
            self.driver.close()

    def create_artifact_node(self, artifact_id: str, title: str, artifact_type: str, user_id: str = "system_user"):
        """Creates the root node for a Library Artifact (Book, Paper, etc.)."""
        if not self.is_active: return
        
        # Normalize label (Anytype Style: Typed Nodes)
        label = artifact_type.capitalize() if artifact_type else "Artifact"
        
        try:
            with self.driver.session() as session:
                query = (
                    f"MERGE (a:{label} {{id: $id}}) "
                    "SET a.title = $title, a.type = $type, a.user_id = $user_id, a:Artifact"
                )
                session.execute_write(lambda tx: tx.run(query, id=artifact_id, title=title, type=artifact_type, user_id=user_id))
        except Exception as e:
            print(f"GraphEngine Error: {e}")

    def ingest_triplets(self, artifact_id: str, triplets: List[Dict[str, str]], user_id: str = "system_user"):
        """
        Dynamically builds the Knowledge Graph based on LLM-extracted triplets.
        """
        if not self.is_active: return
        try:
            with self.driver.session() as session:
                for triplet in triplets:
                    subj = triplet.get("subject", "").strip().upper()
                    pred = triplet.get("predicate", "").strip().upper().replace(" ", "_")
                    obj = triplet.get("object", "").strip().upper()

                    if not subj or not pred or not obj:
                        continue

                    # Create the relationship and link it back to the source Artifact
                    # Hebbian Learning: initialize weight or increment if it exists
                    query = f"""
                    MERGE (s:Concept {{name: $subj, user_id: $user_id}})
                    MERGE (o:Concept {{name: $obj, user_id: $user_id}})
                    MERGE (s)-[r:{pred} {{user_id: $user_id}}]->(o)
                    ON CREATE SET r.weight = 1.0
                    ON MATCH SET r.weight = coalesce(r.weight, 1.0) + 0.1
                    WITH s, o, r
                    MATCH (a:Artifact {{id: $artifact_id, user_id: $user_id}})
                    MERGE (a)-[:MENTIONS {{user_id: $user_id}}]->(s)
                    MERGE (a)-[:MENTIONS {{user_id: $user_id}}]->(o)
                    """
                    session.execute_write(lambda tx: tx.run(query, subj=subj, obj=obj, artifact_id=artifact_id, user_id=user_id))
        except Exception as e:
            print(f"GraphEngine Error: {e}")

    def decay_synaptic_weights(self, decay_factor: float = 0.95, user_id: str = None):
        """Applies metabolic decay to all graph relationships."""
        if not self.is_active: return
        try:
            with self.driver.session() as session:
                query = """
                MATCH ()-[r]->()
                WHERE type(r) <> 'MENTIONS'
                """
                if user_id:
                    query += " AND r.user_id = $user_id "
                
                query += " SET r.weight = coalesce(r.weight, 1.0) * $decay_factor"
                
                session.execute_write(lambda tx: tx.run(query, decay_factor=decay_factor, user_id=user_id))
                print(f"GraphEngine: Applied synaptic decay (factor: {decay_factor}, user: {user_id})")
        except Exception as e:
            print(f"GraphEngine Error decaying weights: {e}")

    def prune_dead_synapses(self, threshold: float = 0.1, user_id: str = None):
        """Removes relationships that have decayed below the utility threshold."""
        if not self.is_active: return
        try:
            with self.driver.session() as session:
                query = """
                MATCH ()-[r]->()
                WHERE type(r) <> 'MENTIONS' AND coalesce(r.weight, 1.0) < $threshold
                """
                if user_id:
                    query += " AND r.user_id = $user_id "
                
                query += " DELETE r RETURN count(r) as pruned_count"
                
                result = session.execute_write(lambda tx: tx.run(query, threshold=threshold, user_id=user_id).single())
                pruned_count = result["pruned_count"] if result else 0
                print(f"GraphEngine: Pruned {pruned_count} dead synapses (user: {user_id}).")
        except Exception as e:
            print(f"GraphEngine Error pruning synapses: {e}")

    def detect_contradictions(self, user_id: str = "system_user") -> List[Dict]:
        """Identifies conflicting relationships (e.g., A is-a B and A is-not-a B)."""
        if not self.is_active: return []
        
        contradictions = []
        try:
            with self.driver.session() as session:
                # 1. Simple opposite predicate check (e.g., X IS Y vs X IS_NOT Y)
                # This is a basic pattern-based check.
                query = """
                MATCH (n:Concept {user_id: $user_id})-[r1]->(m:Concept {user_id: $user_id})
                MATCH (n)-[r2]->(m)
                WHERE id(r1) < id(r2) AND 
                      (type(r1) = 'IS_A' AND type(r2) = 'IS_NOT_A' OR
                       type(r1) = 'PART_OF' AND type(r2) = 'NOT_PART_OF' OR
                       type(r1) = 'LOCATED_IN' AND type(r2) = 'NOT_LOCATED_IN')
                RETURN n.name, type(r1), type(r2), m.name
                """
                result = session.run(query, user_id=user_id)
                for record in result:
                    contradictions.append({
                        "type": "DIRECT_OPPOSITE",
                        "subject": record["n.name"],
                        "rel1": record["type(r1)"],
                        "rel2": record["type(r2)"],
                        "object": record["m.name"]
                    })
                
                # 2. Transitive contradiction (A is-a B, B is-a C, C is-not-a A)
                query = """
                MATCH (a:Concept {user_id: $user_id})-[:IS_A*1..3]->(b:Concept {user_id: $user_id})
                MATCH (b)-[:IS_NOT_A]->(a)
                RETURN a.name, b.name
                """
                result = session.run(query, user_id=user_id)
                for record in result:
                    contradictions.append({
                        "type": "TRANSITIVE_CYCLE_CONTRADICTION",
                        "node_a": record["a.name"],
                        "node_b": record["b.name"]
                    })
                    
        except Exception as e:
            print(f"GraphEngine Contradiction Detection Error: {e}")
        return contradictions

    def add_decoy_relationships(self, user_id: str = "system_user", noise_factor: float = 0.1):
        """
        Differential Privacy: Adds 'Decoy' relationships to the graph.
        Makes it harder to fingerprint the user's specific interests via topology.
        """
        if not self.is_active: return
        try:
            with self.driver.session() as session:
                # 1. Get a random subset of existing Concepts
                query = """
                MATCH (c:Concept {user_id: $user_id})
                WITH c, rand() as r
                WHERE r < $noise_factor
                RETURN c.name as name LIMIT 20
                """
                result = session.run(query, user_id=user_id, noise_factor=noise_factor)
                concepts = [r["name"] for r in result]
                
                if len(concepts) < 2: return

                # 2. Create 'DECOY' relationships between them
                import random
                for _ in range(len(concepts) // 2):
                    subj = random.choice(concepts)
                    obj = random.choice(concepts)
                    if subj == obj: continue
                    
                    query = """
                    MERGE (s:Concept {name: $subj, user_id: $user_id})
                    MERGE (o:Concept {name: $obj, user_id: $user_id})
                    MERGE (s)-[r:DECOY {user_id: $user_id}]->(o)
                    SET r.weight = 0.1, r.timestamp = datetime()
                    """
                    session.execute_write(lambda tx: tx.run(query, subj=subj, obj=obj, user_id=user_id))
                print(f"GraphEngine: Injected decoy relationships for user {user_id}")
        except Exception as e:
            print(f"GraphEngine Decoy Error: {e}")
    def search_graph_context(self, entities: List[str], user_id: str = "system_user") -> List[str]:
        """
        Retrieves graph context for a list of entities.
        """
        if not self.is_active or not entities:
            return []
            
        context = []
        try:
            with self.driver.session() as session:
                for entity in entities:
                    query = """
                    MATCH (n:Concept {name: $entity, user_id: $user_id})-[r]->(m:Concept {user_id: $user_id})
                    RETURN n.name, type(r), m.name LIMIT 5
                    UNION
                    MATCH (n:Concept {user_id: $user_id})-[r]->(m:Concept {name: $entity, user_id: $user_id})
                    RETURN n.name, type(r), m.name LIMIT 5
                    """
                    result = session.run(query, entity=entity.upper(), user_id=user_id)
                    for record in result:
                        context.append(f"{record['n.name']} {record['type(r)']} {record['m.name']}")
        except Exception as e:
            print(f"GraphEngine Error: {e}")
        return context

    # --- Graph Data Science (GDS) Algorithms ---

    def get_topology_summary(self, user_id: str) -> Dict:
        """Returns the count of nodes and edges for the user's graph."""
        if not self.is_active: return {"node_count": 0, "edge_count": 0}
        try:
            with self.driver.session() as session:
                node_query = "MATCH (n {user_id: $user_id}) RETURN count(n) as node_count"
                edge_query = "MATCH ()-[r {user_id: $user_id}]->() RETURN count(r) as edge_count"
                
                node_res = session.run(node_query, user_id=user_id).single()
                edge_res = session.run(edge_query, user_id=user_id).single()
                
                return {
                    "node_count": node_res["node_count"] if node_res else 0,
                    "edge_count": edge_res["edge_count"] if edge_res else 0
                }
        except Exception as e:
            print(f"GraphEngine Topology Error: {e}")
            return {"node_count": 0, "edge_count": 0}

    def get_recent_triplets(self, user_id: str, limit: int = 50) -> Dict:
        """Returns nodes and links for 3D graph visualization."""
        if not self.is_active: return {"nodes": [], "links": []}
        try:
            with self.driver.session() as session:
                # Check if we have any Concept nodes first to avoid warnings
                check_query = "MATCH (n:Concept) RETURN count(n) as count LIMIT 1"
                has_concepts = session.run(check_query).single()
                if not has_concepts or has_concepts["count"] == 0:
                    return {"nodes": [], "links": []}

                query = """
                MATCH (n:Concept {user_id: $user_id})-[r]->(m:Concept {user_id: $user_id})
                WHERE type(r) <> 'MENTIONS' AND type(r) <> 'DECOY'
                RETURN n.name as source, m.name as target, type(r) as type, r.weight as weight
                ORDER BY r.timestamp DESC LIMIT $limit
                """
                result = session.run(query, user_id=user_id, limit=limit)
                
                nodes = set()
                links = []
                for record in result:
                    nodes.add(record["source"])
                    nodes.add(record["target"])
                    links.append({
                        "source": record["source"],
                        "target": record["target"],
                        "label": record["type"],
                        "weight": record["weight"]
                    })
                
                return {
                    "nodes": [{"id": name, "name": name, "val": 1} for name in nodes],
                    "links": links
                }
        except Exception as e:
            print(f"GraphEngine Visual Error: {e}")
            return {"nodes": [], "links": []}

    def _ensure_gds_projection(self, user_id: str):
        """Creates a named graph projection in Neo4j GDS memory for the user's pod."""
        if not self.is_active: return False
        graph_name = f"graph_{user_id.replace('-', '_')}"
        try:
            with self.driver.session() as session:
                # Drop existing projection if it exists
                session.run(f"CALL gds.graph.drop('{graph_name}', false)")
                
                # Create new projection
                query = f"""
                CALL gds.graph.project(
                    '{graph_name}',
                    'Concept',
                    {{
                        ALL_RELS: {{
                            type: '*',
                            orientation: 'NATURAL',
                            properties: 'weight'
                        }}
                    }},
                    {{
                        nodeProperties: ['pagerank', 'community_id', 'centrality']
                    }}
                )
                """
                session.run(query)
                return True
        except Exception as e:
            print(f"GraphEngine GDS Projection Error: {e}")
            return False

    def run_graph_topology_analytics(self, user_id: str):
        """Executes PageRank, Louvain, and Betweenness Centrality on the user's graph."""
        if not self.is_active: return
        if not self._ensure_gds_projection(user_id): return
        
        graph_name = f"graph_{user_id.replace('-', '_')}"
        try:
            with self.driver.session() as session:
                # 1. PageRank (Influence)
                session.run(f"CALL gds.pageRank.write('{graph_name}', {{ writeProperty: 'pagerank' }})")
                
                # 2. Louvain (Community Detection / Clustering)
                session.run(f"CALL gds.louvain.write('{graph_name}', {{ writeProperty: 'community_id' }})")
                
                # 3. Betweenness Centrality (Bridging nodes)
                session.run(f"CALL gds.betweenness.write('{graph_name}', {{ writeProperty: 'centrality' }})")
                
                print(f"GraphEngine: Completed GDS analytics for user {user_id}")
        except Exception as e:
            print(f"GraphEngine GDS Execution Error: {e}")

    def get_topology_metrics(self, user_id: str) -> Dict:
        """Retrieves concepts with their calculated topology metrics."""
        if not self.is_active: return {}
        
        metrics = {
            "top_influencers": [], # High PageRank
            "thematic_clusters": {}, # Louvain communities
            "bridge_concepts": [] # High Betweenness Centrality
        }
        
        try:
            with self.driver.session() as session:
                # Get Top Influencers
                query = """
                MATCH (c:Concept {user_id: $user_id})
                WHERE c.pagerank IS NOT NULL
                RETURN c.name as name, c.pagerank as pagerank
                ORDER BY c.pagerank DESC LIMIT 10
                """
                result = session.run(query, user_id=user_id)
                metrics["top_influencers"] = [{"name": r["name"], "score": r["pagerank"]} for r in result]
                
                # Get Bridge Concepts
                query = """
                MATCH (c:Concept {user_id: $user_id})
                WHERE c.centrality IS NOT NULL
                RETURN c.name as name, c.centrality as centrality
                ORDER BY c.centrality DESC LIMIT 10
                """
                result = session.run(query, user_id=user_id)
                metrics["bridge_concepts"] = [{"name": r["name"], "score": r["centrality"]} for r in result]
                
                # Get Clusters
                query = """
                MATCH (c:Concept {user_id: $user_id})
                WHERE c.community_id IS NOT NULL
                RETURN c.name as name, c.community_id as cluster
                """
                result = session.run(query, user_id=user_id)
                for r in result:
                    cluster_id = str(r["cluster"])
                    if cluster_id not in metrics["thematic_clusters"]:
                        metrics["thematic_clusters"][cluster_id] = []
                    metrics["thematic_clusters"][cluster_id].append(r["name"])
                    
        except Exception as e:
            print(f"GraphEngine Metrics Error: {e}")
        return metrics
