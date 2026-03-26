import os
import asyncio
from typing import Dict
from ai_engine import AIEngine
from graph_engine import GraphEngine
from akasha_db.core import AkashaLivingDB
from akasha_db.metabolism import AkashaMetabolism
from database import engine

class AssistantPod:
    """
    A Personal AI Assistant Pod.
    Isolated context for a specific user.
    """
    def __init__(self, user_id: str, ai_engine: AIEngine, graph_engine: GraphEngine, blockchain_adapter=None, manager=None, is_shared=False):
        self.user_id = user_id
        self.ai_engine = ai_engine
        self.graph_engine = graph_engine
        self.blockchain = blockchain_adapter
        self.is_shared = is_shared
        
        # Isolated Living DB path (Shared pods use a communal directory)
        prefix = "shared_" if is_shared else ""
        storage_path = f"./akasha_data/{prefix}{user_id}"
        self.akasha_db = AkashaLivingDB(storage_path=storage_path)
        
        # User-specific Metabolism
        self.metabolism = AkashaMetabolism(self.akasha_db, self.ai_engine, blockchain=self.blockchain, manager=manager)
        
    async def start(self):
        """Starts the pod's autonomous cycles."""
        asyncio.create_task(self.metabolism.start_metabolic_cycle())
        asyncio.create_task(self.metabolism.heartbeat())

class PodManager:
    """Orchestrates multiple Assistant Pods."""
    def __init__(self, ai_engine: AIEngine, graph_engine: GraphEngine, blockchain_adapter=None, manager=None):
        self.ai_engine = ai_engine
        self.graph_engine = graph_engine
        self.blockchain = blockchain_adapter
        self.manager = manager
        self.pods: Dict[str, AssistantPod] = {}
        self.shared_pods: Dict[str, AssistantPod] = {}

    async def get_pod(self, user_id: str, shared: bool = False) -> AssistantPod:
        pool = self.shared_pods if shared else self.pods
        if user_id not in pool:
            print(f"PodManager: Spinning up {'SHARED ' if shared else ''}Assistant Pod for {user_id}")
            pod = AssistantPod(user_id, self.ai_engine, self.graph_engine, self.blockchain, self.manager, is_shared=shared)
            await pod.start()
            pool[user_id] = pod
        return pool[user_id]
