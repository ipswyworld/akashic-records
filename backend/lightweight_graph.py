import sqlite3
import os
import json
import datetime
from typing import List, Dict, Any, Optional

class SQLiteGraphEngine:
    """A lightweight Knowledge Graph engine using SQLite for local-first efficiency."""
    def __init__(self, db_path: str = "akasha_db/knowledge_graph.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Concepts (Nodes)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concepts (
                    name TEXT PRIMARY KEY,
                    user_id TEXT,
                    type TEXT DEFAULT 'Concept',
                    pagerank REAL DEFAULT 0.0,
                    community_id INTEGER DEFAULT 0,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Relationships (Edges)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    target TEXT,
                    predicate TEXT,
                    weight REAL DEFAULT 1.0,
                    user_id TEXT,
                    artifact_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(source) REFERENCES concepts(name),
                    FOREIGN KEY(target) REFERENCES concepts(name)
                )
            """)
            conn.commit()

    def create_artifact_node(self, artifact_id: str, title: str, artifact_type: str, user_id: str = "system_user"):
        """Artifacts are concepts too, or root nodes for context."""
        self.upsert_concept(title, user_id, type=artifact_type, metadata={"artifact_id": artifact_id})

    def upsert_concept(self, name: str, user_id: str, type: str = "Concept", metadata: Dict = None):
        name = name.strip().upper()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO concepts (name, user_id, type, metadata)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                type = excluded.type,
                metadata = excluded.metadata,
                timestamp = CURRENT_TIMESTAMP
            """, (name, user_id, type, json.dumps(metadata) if metadata else None))
            conn.commit()

    def ingest_triplets(self, artifact_id: str, triplets: List[Dict[str, str]], user_id: str = "system_user"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for triplet in triplets:
                subj = triplet.get("subject", "").strip().upper()
                pred = triplet.get("predicate", "").strip().upper().replace(" ", "_")
                obj = triplet.get("object", "").strip().upper()

                if not subj or not pred or not obj:
                    continue

                # Ensure nodes exist
                cursor.execute("INSERT OR IGNORE INTO concepts (name, user_id) VALUES (?, ?)", (subj, user_id))
                cursor.execute("INSERT OR IGNORE INTO concepts (name, user_id) VALUES (?, ?)", (obj, user_id))

                # Add relationship or increment weight (Hebbian Learning)
                cursor.execute("""
                    SELECT id, weight FROM relationships 
                    WHERE source = ? AND target = ? AND predicate = ? AND user_id = ?
                """, (subj, obj, pred, user_id))
                existing = cursor.fetchone()

                if existing:
                    new_weight = existing[1] + 0.1
                    cursor.execute("UPDATE relationships SET weight = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?", (new_weight, existing[0]))
                else:
                    cursor.execute("""
                        INSERT INTO relationships (source, target, predicate, weight, user_id, artifact_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (subj, obj, pred, 1.0, user_id, artifact_id))
            conn.commit()

    def search_graph_context(self, entities: List[str], user_id: str = "system_user") -> List[str]:
        context = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for entity in entities:
                entity = entity.upper()
                cursor.execute("""
                    SELECT source, predicate, target FROM relationships
                    WHERE (source = ? OR target = ?) AND user_id = ?
                    LIMIT 10
                """, (entity, entity, user_id))
                for row in cursor.fetchall():
                    context.append(f"{row[0]} {row[1]} {row[2]}")
        return list(set(context))

    def get_topology_summary(self, user_id: str) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM concepts WHERE user_id = ?", (user_id,))
            node_count = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM relationships WHERE user_id = ?", (user_id,))
            edge_count = cursor.fetchone()[0]
            return {"node_count": node_count, "edge_count": edge_count}

    def get_recent_triplets(self, user_id: str, limit: int = 50) -> Dict:
        nodes = set()
        links = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT source, target, predicate, weight FROM relationships
                WHERE user_id = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (user_id, limit))
            for row in cursor.fetchall():
                nodes.add(row[0])
                nodes.add(row[1])
                links.append({
                    "source": row[0],
                    "target": row[1],
                    "label": row[2],
                    "weight": row[3]
                })
        return {
            "nodes": [{"id": name, "name": name, "val": 1} for name in nodes],
            "links": links
        }

    def close(self):
        pass # SQLite connections are handled contextually here
