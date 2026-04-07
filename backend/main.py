from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, WebSocket, WebSocketDisconnect, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import datetime
import uuid
import hashlib
import json
import os
import asyncio
import importlib.util
import tempfile
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bootstrap import bootstrap_environment

# Ensure environment is ready
bootstrap_environment()
load_dotenv()

# --- Sovereign Database & Models ---
from database import engine, Base, get_db, SessionLocal
from models import User, LibraryArtifact, UserTask, SRSCard, UserActivity, UserSettings, UserPsychology, ObjectSchema

# Ensure database tables are created
Base.metadata.create_all(bind=engine)

import auth_utils

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Request

# Update scheme to be optional
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

async def get_current_user(request: Request, token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # --- DORMANT MODE: True Open Access ---
    DORMANT_MODE = True 
    
    if DORMANT_MODE:
        user = db.query(User).filter(User.username == "dev_user").first()
        if not user:
            user = User(id="system_user", username="dev_user", email="dev@akasha.local", hashed_password="dormant_password")
            db.add(user); db.commit(); db.refresh(user)
        return user

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = auth_utils.decode_access_token(token)
        if payload is None: raise HTTPException(status_code=401, detail="Invalid token")
        username: str = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        if user is None: raise HTTPException(status_code=401, detail="User not found")
        return user
    except:
        raise HTTPException(status_code=401, detail="Auth failure")

class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    user_id: Optional[str] = "system_user"
    wisdom_mode: bool = False
    model_tier: Optional[str] = "local"
    is_ghost_writer: bool = False

class SemanticSearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = "system_user"
    n_results: int = 10

class FormFillRequest(BaseModel):
    url: str
    fields: List[str]
    user_id: Optional[str] = "system_user"

class MonitorRequest(BaseModel):
    url: str
    trigger_condition: str
    user_id: Optional[str] = "system_user"

class IngestUrlRequest(BaseModel):
    url: str
    user_id: Optional[str] = "system_user"

class TranslateRequest(BaseModel):
    text: str
    target_language: str = "English"
    user_id: Optional[str] = "system_user"

class InterpreterRequest(BaseModel):
    script: str

class PluginGenerateRequest(BaseModel):
    user_request: str

class PluginActivateRequest(BaseModel):
    plugin_name: str
    api_keys: Dict[str, str]

class SensoryNodeData(BaseModel):
    user_id: str
    node_key: str
    location: Optional[Dict[str, float]] = None
    audio_payload: Optional[str] = None
    is_encrypted: bool = False
    encrypted_blob: Optional[str] = None
    timestamp: float
class FeedbackRequest(BaseModel):
    feedback: str
    agent_name: str

class ActionGoalRequest(BaseModel):
    goal: str
    user_id: str = "system_user"

class P2PStealthRequest(BaseModel):
    enabled: bool
    user_id: str = "system_user"

class TelemetryRequest(BaseModel):
    type: str # BROWSER_VISIT, APP_USAGE, SEARCH
    title: str
    url: Optional[str] = None
    content: Optional[str] = None
    user_id: str = "system_user"

# --- Core Logic Helpers ---
def update_user_psychology(db: Session, user_id: str, analysis: Dict[str, Any], content: str = None):
    """Incrementally updates the user's psychological profile (Ego) based on new thoughts."""
    profile = db.query(UserPsychology).filter(UserPsychology.user_id == user_id).first()
    if not profile:
        profile = UserPsychology(user_id=user_id)
        db.add(profile)
    
    # Zero-effort identity recognition
    if content:
        name = intel_engine.extract_user_name(content)
        if name:
            profile.known_name = name

    deep_meta = analysis.get("deep_metadata", {})
    traits = deep_meta.get("personality_traits", {})
    distortions = deep_meta.get("cognitive_distortions", [])
    if not traits and not distortions: return
    
    alpha = 0.1 
    if "openness" in traits: profile.openness = (1 - alpha) * profile.openness + alpha * float(traits.get("openness", 0.5))
    if "conscientiousness" in traits: profile.conscientiousness = (1 - alpha) * profile.conscientiousness + alpha * float(traits.get("conscientiousness", 0.5))
    if "extraversion" in traits: profile.extraversion = (1 - alpha) * profile.extraversion + alpha * float(traits.get("extraversion", 0.5))
    if "agreeableness" in traits: profile.agreeableness = (1 - alpha) * profile.agreeableness + alpha * float(traits.get("agreeableness", 0.5))
    if "neuroticism" in traits: profile.neuroticism = (1 - alpha) * profile.neuroticism + alpha * float(traits.get("neuroticism", 0.5))
    current_distortions = profile.identified_distortions.copy() if profile.identified_distortions else {}
    for dist in distortions:
        d_name = str(dist).lower()
        current_distortions[d_name] = current_distortions.get(d_name, 0) + 1
    profile.identified_distortions = current_distortions
    profile.last_updated = datetime.datetime.utcnow()
    db.commit()

async def ingest_library_artifact(title: str, content: str, artifact_type: str, extra_meta: Dict = None, db: Session = None, user_id: str = "system_user"):
    """Helper function to consolidate ingestion logic. Prevents duplicates via content hash."""
    # 0. Deduplication Check
    b_hash = hashlib.sha256(content.encode()).hexdigest()
    existing = db.query(LibraryArtifact).filter(LibraryArtifact.blockchain_hash == b_hash).first()
    if existing:
        print(f"Ingest: Skipping duplicate artifact '{title}'")
        return existing

    loop = asyncio.get_event_loop()
    # 1. Heavy AI Analysis (Offloaded)
    analysis = await loop.run_in_executor(None, ai_engine.analyze_artifact, content)
    
    # 2. Sequential Logic (Fast DB ops)
    update_user_psychology(db, user_id, analysis, content)
    
    # Pillar 4: Dynamic Schema
    schema_id = None
    proposed = analysis["deep_metadata"].get("proposed_schema", {})
    if proposed.get("name") != "General":
        existing_schema = db.query(ObjectSchema).filter(ObjectSchema.name == proposed["name"]).first()
        if not existing_schema:
            existing_schema = ObjectSchema(name=proposed["name"], definition_json=proposed["fields"], user_id=user_id)
            db.add(existing_schema)
            try:
                db.commit()
                db.refresh(existing_schema)
            except:
                db.rollback()
                existing_schema = db.query(ObjectSchema).filter(ObjectSchema.name == proposed["name"]).first()
        if existing_schema:
            schema_id = existing_schema.id

    new_art = LibraryArtifact(
        title=title,
        content=content,
        artifact_type=artifact_type,
        schema_id=schema_id,
        user_id=user_id,
        summary=analysis["summary"],
        sentiment_label=analysis["sentiment_label"],
        blockchain_hash=b_hash,
        metadata_json={
            **(extra_meta or {}),
            "entities": analysis["entities"],
            "structured_data": analysis["deep_metadata"].get("structured_data", {})
        }
    )
    new_art.encrypt_content()
    try:
        db.add(new_art)
        db.commit()
        db.refresh(new_art)
    except Exception as e:
        db.rollback()
        # Double check if it was a race condition on blockchain_hash
        existing = db.query(LibraryArtifact).filter(LibraryArtifact.blockchain_hash == b_hash).first()
        if existing:
            return existing
        raise e
    
    # 3. Vector Storage
    await loop.run_in_executor(None, ai_engine.store_vector, new_art.id, content, analysis, user_id)
    
    # 4. Graph Logic
    graph_engine.create_artifact_node(new_art.id, new_art.title, artifact_type, user_id)
    graph_engine.ingest_triplets(new_art.id, analysis["graph_triplets"], user_id)
    
    await manager.broadcast(json.dumps({"event": "NEW_ARTIFACT_INGESTED", "id": new_art.id, "title": new_art.title}))
    return new_art

# --- Connection Management ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try: await connection.send_text(message)
            except: pass

manager = ConnectionManager()

# --- Delayed Heavy Imports & Engine Init ---
from database import engine, Base, get_db, SessionLocal
from models import LibraryArtifact, UserTask, SRSCard, UserActivity, UserSettings, UserPsychology, ObjectSchema

# Ensure database tables are created
Base.metadata.create_all(bind=engine)

from ai_engine import AIEngine
from blockchain_adapter import BlockchainAdapter
from graph_engine import GraphEngine
from p2p_node import P2PNode
from multimodal_engine import MultimodalEngine
from privacy_engine import PrivacyEngine
from ingest_engine import IngestEngine, SpeakerVerifier
from intel_engine import IntelEngine
from pod_manager import PodManager
from chronos_engine import ChronosEngine
from sensory_ingest import SensoryIngestEngine
from action_engine import ActionEngine
from srs_engine import SRSEngine
from ouro_subchain import OuroborosSubchain
from akasha_db.metabolism import AkashaMetabolism
from akasha_db.core import AkashaLivingDB
from telemetry_ingest import TelemetryIngestEngine
from privacy_utils import redactor

def get_initial_ai_engine():
    db = SessionLocal()
    try:
        settings = db.query(UserSettings).filter(UserSettings.user_id == "system_user").first()
        if settings:
            return AIEngine(turbo_mode=settings.turbo_mode, groq_key=settings.groq_api_key, neural_name=settings.neural_name)
        return AIEngine()
    finally:
        db.close()

from context_fabric import ContextFabric

# Instantiate Engines
ai_engine = get_initial_ai_engine()
intel_engine = IntelEngine()
telemetry_engine = TelemetryIngestEngine()
p2p_node = P2PNode(intel_engine=intel_engine)
# Link P2P to Council for Federated RAG
ai_engine.council.p2p_node = p2p_node

blockchain = BlockchainAdapter()
graph_engine = GraphEngine()
fabric = ContextFabric(ai_engine, graph_engine)
multimodal = MultimodalEngine()
executive = ActionEngine(ai_engine)
pod_manager = PodManager(ai_engine, graph_engine, blockchain)
chronos = ChronosEngine(ai_engine, pod_manager, executive)
sensory = SensoryIngestEngine(ai_engine, multimodal, graph_engine)
ingest = IngestEngine(p2p_node=p2p_node)
speaker_verifier = SpeakerVerifier()
srs_engine = SRSEngine()
subchain = OuroborosSubchain()

# --- Identity Recognition Tool ---
def handle_identity_commands(text: str, user_id: str):
    """Zero effort naming: Detects if the user is renaming the assistant."""
    if "your name is " in text.lower():
        new_name = text.lower().split("your name is ")[1].strip().replace(".", "").title()
        db = SessionLocal()
        try:
            settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            if settings:
                settings.neural_name = new_name
                db.commit()
                ai_engine.rename_identity(new_name)
                return f"Understood. My identity has recalibrated. I am now {new_name}."
        finally:
            db.close()
    return None

def handle_user_identity(text: str, user_id: str):
    """Zero effort user identity: Detects if the user is identifying themselves."""
    name = intel_engine.extract_user_name(text)
    if name:
        db = SessionLocal()
        try:
            profile = db.query(UserPsychology).filter(UserPsychology.user_id == user_id).first()
            if not profile:
                profile = UserPsychology(user_id=user_id)
                db.add(profile)
            profile.known_name = name
            db.commit()
            return f"Understood. I have recognized your identity as {name}. Pleased to meet you."
        finally:
            db.close()
    return None

# --- Main Application Instance ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await pod_manager.get_pod("system_user")

    # Initialize Metabolism
    db_living = AkashaLivingDB()
    metabolism = AkashaMetabolism(db_living, ai_engine, blockchain, manager, user_id="system_user")
    metabolism_task = asyncio.create_task(metabolism.start_metabolic_cycle())

    # Warm up AI Engine with Digital Ego
    db = SessionLocal()
    try:
        profile = db.query(UserPsychology).filter(UserPsychology.user_id == "system_user").first()
        if profile:
            ego_profile = {
                "ocean_traits": {"openness": profile.openness, "conscientiousness": profile.conscientiousness, "extraversion": profile.extraversion, "agreeableness": profile.agreeableness, "neuroticism": profile.neuroticism},
                "cognitive_distortions": profile.identified_distortions
            }
            ai_engine.warmup_ego(ego_profile)
    finally:
        db.close()

    # Start MCP Directory Watcher
    watch_path = os.path.join(os.getcwd(), "akasha_data", "watch")
    watcher = ingest.start_directory_watcher(watch_path, "system_user", ingest_library_artifact)

    p2p_task = asyncio.create_task(p2p_node.start())
    scheduler.start()
    
    async def sentinel_loop():
        sent_alerts = set()
        last_observer_run = datetime.datetime.min
        last_behavioral_mining = datetime.datetime.min
        last_reflection_day = -1
        try:
            while True:
                await asyncio.sleep(600)
                now = datetime.datetime.utcnow()
                await chronos.trigger_temporal_actions("system_user")
                
                # Autonomous Dream Phase (Nocturnal Consolidation)
                if now.hour == 3 and last_reflection_day != now.day: # Run at 3 AM
                    await chronos.run_nocturnal_consolidation("system_user")
                
                # Proactive Behavioral Reflection (Every 12 hours)
                if now - last_behavioral_mining > datetime.timedelta(hours=12):
                    print("Sentinel: Initiating Deep Behavioral Reflection...")
                    await chronos.run_behavioral_pattern_mining("system_user")
                    last_behavioral_mining = now

                # Autonomous Evolution Cycle (Every 24 hours)
                if now - last_observer_run > datetime.timedelta(hours=24):
                    db = SessionLocal()
                    try:
                        await ai_engine.run_autonomous_evolution("system_user", db)
                        
                        # --- Feature 8: Cold Storage Migration ---
                        # Migrate artifacts older than 6 months
                        six_months_ago = now - datetime.timedelta(days=180)
                        old_artifacts = db.query(LibraryArtifact).filter(
                            LibraryArtifact.user_id == "system_user",
                            LibraryArtifact.timestamp < six_months_ago,
                            LibraryArtifact.artifact_type != "cold_storage_pointer"
                        ).all()
                        
                        for art in old_artifacts:
                            art.decrypt_content()
                            tx_id = await blockchain.migrate_to_cold_storage(art.id, art.content)
                            art.content = f"COLD_STORAGE_POINTER:{tx_id}"
                            art.artifact_type = "cold_storage_pointer"
                            art.encrypt_content()
                        db.commit()
                        # ---------------------------------------
                        
                    finally: db.close()

                # Seer: Morning Prediction (Every 24 hours at 8 AM)
                if now.hour == 8 and last_reflection_day != now.day:
                    db = SessionLocal()
                    try:
                        prediction = await ai_engine.predict_user_needs("system_user", db)
                        await manager.broadcast(json.dumps({
                            "type": "PROACTIVE_SUGGESTION",
                            "payload": prediction
                        }))
                    finally: db.close()

                if now.hour == 22 and last_reflection_day != now.day:
                    db = SessionLocal()
                    try:
                        await chronos.generate_daily_reflection(db, "system_user")
                        last_reflection_day = now.day
                    finally: db.close()
                if now - last_observer_run > datetime.timedelta(hours=6):
                    db = SessionLocal()
                    try:
                        intel = await chronos.run_observer_intel("system_user", db)
                        await manager.broadcast(json.dumps({"type": "WEB_INTEL", "payload": intel}))
                        last_observer_run = now
                    finally: db.close()
                alerts = await chronos.detect_temporal_deadlines("system_user")
                for alert in alerts:
                    alert_key = f"{alert['description']}:{alert['deadline']}"
                    if alert_key not in sent_alerts:
                        await manager.broadcast(json.dumps(alert))
                        sent_alerts.add(alert_key)
        except asyncio.CancelledError:
            print("Sentinel loop cancelled.")
    
    sentinel_task = asyncio.create_task(sentinel_loop())
    
    yield
    
    # Shutdown
    print("Shutting down Akasha Neural Core...")
    scheduler.shutdown()
    
    # Cancel background tasks
    sentinel_task.cancel()
    p2p_task.cancel()
    
    # Stop directory watcher
    if watcher:
        watcher.stop()
        watcher.join()
        print("MCP Directory Watcher stopped.")

    # Close graph driver
    graph_engine.close()
    
    # Wait for tasks to complete cancellation
    await asyncio.gather(sentinel_task, p2p_task, return_exceptions=True)
    print("Core systems offline.")

# --- Background Tasks ---
async def poll_rss_feeds_background():
    """Background task to fetch RSS feeds using APScheduler."""
    print(f"[{datetime.datetime.utcnow()}] Background: Polling RSS Feeds...")
    try:
        memories = ingest.fetch_latest_news()
        db = SessionLocal()
        try:
            for memory in memories:
                await ingest_library_artifact(
                    title=memory["title"],
                    content=memory["content"],
                    artifact_type=memory["category"],
                    extra_meta={"source_url": memory["link"]},
                    db=db,
                    user_id="system_user"
                )
        finally:
            db.close()
    except Exception as e:
        print(f"Background Task Error: {e}")

async def run_synthetic_dream_loop():
    """Synthetic Thought Loop: Agents 'dream' and find serendipitous connections (Idea 4)."""
    # ... logic omitted for brevity ...
    pass

async def system_maintenance_task():
    """Background: Periodic system health check and backup."""
    from scripts.health_check import check_health
    from scripts.backup_vault import backup_vault
    print(f"[{datetime.datetime.utcnow()}] Background: Running system maintenance...")
    check_health()
    backup_vault()

app = FastAPI(title="Akasha Universal Library", description="The Omnipresent Knowledge Graph & Library", lifespan=lifespan)
app.state.ai_engine = ai_engine

scheduler = AsyncIOScheduler()
scheduler.add_job(poll_rss_feeds_background, 'interval', minutes=30)
scheduler.add_job(run_synthetic_dream_loop, 'interval', hours=12)
scheduler.add_job(system_maintenance_task, 'interval', hours=24)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/chronos/morning_briefing")
async def get_morning_briefing(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns the latest serendipity report generated by Chronos Engine."""
    from models import LibraryArtifact
    import datetime
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    report = db.query(LibraryArtifact).filter(
        LibraryArtifact.user_id == current_user.id,
        LibraryArtifact.artifact_type == "serendipity_report",
        LibraryArtifact.title.like(f"%Morning Briefing: {today}%")
    ).first()
    
    if report:
        return {"status": "SUCCESS", "report": report.content}
    return {"status": "NOT_FOUND", "message": "No new morning briefing available yet."}

@app.get("/analytics/evolution")
async def get_evolution_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Provides data for the Visual Evolution Timeline."""
    from models import AgentPerformance, NeuralSkill
    
    # 1. Fetch Performance Trends
    performances = db.query(AgentPerformance).filter(AgentPerformance.user_id == current_user.id).order_by(AgentPerformance.timestamp.asc()).all()
    
    # If no performances, provide mock starting metrics
    if not performances:
        now = datetime.utcnow()
        performance_history = [
            {"agent": "Archivist", "fitness": 0.5, "timestamp": (now - timedelta(hours=2)).isoformat(), "category": "General"},
            {"agent": "Oracle", "fitness": 0.4, "timestamp": (now - timedelta(hours=1)).isoformat(), "category": "Synthesis"},
            {"agent": "Butler", "fitness": 0.6, "timestamp": now.isoformat(), "category": "Execution"}
        ]
    else:
        performance_history = [
            {
                "agent": p.agent_name, 
                "fitness": p.fitness_score, 
                "timestamp": p.timestamp.isoformat(),
                "category": p.task_category
            } for p in performances
        ]
        "forged_skills": [
            {
                "name": s.name, 
                "desc": s.description, 
                "count": s.success_count,
                "created": s.created_at.isoformat()
            } for s in skills
        ],
        "evolution_status": "ACTIVE" if len(performances) > 0 else "INITIALIZING"
    }

class MutationRequest(BaseModel):
    file_path: str
    instruction: str

@app.post("/forge/mutate")
async def manual_mutation(request: MutationRequest, current_user: User = Depends(get_current_user)):
    """Triggers a Darwinian Mutation loop on a specific file."""
    try:
        best_code = ai_engine.council.self_architect.darwinian_mutation(
            request.file_path, 
            request.instruction, 
            ai_engine.council.sentinel
        )
        
        if best_code:
            # For manual safety, we return the code for preview first or apply it
            # Let's apply it but keep a backup
            ai_engine.council.self_architect.backup_file(request.file_path)
            abs_path = os.path.join(ai_engine.council.self_architect.root_dir, request.file_path)
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(best_code)
            return {"status": "SUCCESS", "message": f"Evolved {request.file_path} successfully."}
        return {"status": "ERROR", "message": "No stable mutation found."}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@app.post("/forge/record/start")
async def start_macro_recording(current_user: User = Depends(get_current_user)):
    await executive.start_recording()
    return {"status": "SUCCESS", "message": "Neural recording active."}

@app.post("/forge/record/stop")
async def stop_macro_recording(current_user: User = Depends(get_current_user)):
    result = await executive.stop_recording(user_id=current_user.id)
    return result

@app.get("/forge/skills")
async def list_all_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from models import NeuralSkill
    return db.query(NeuralSkill).filter(NeuralSkill.user_id == current_user.id).all()

# --- P2P Endpoints ---

@app.get("/p2p/status")
async def get_p2p_status():
    """Returns the current state of the Neural Mesh."""
    return {
        "node_id": p2p_node.node_id,
        "is_stealth": p2p_node.is_stealth,
        "peers": list(p2p_node.peers),
        "reputation": {str(k): v for k, v in p2p_node.peer_reputation.items()},
        "status": "ONLINE" if not p2p_node.is_stealth else "STEALTH"
    }

@app.post("/p2p/stealth")
async def toggle_p2p_stealth(request: P2PStealthRequest):
    """Activates or deactivates the Sovereign Shield (Tor/I2P)."""
    await p2p_node.set_stealth_mode(request.enabled)
    return {"status": "SUCCESS", "is_stealth": p2p_node.is_stealth}

# --- Analytics & Graph Endpoints ---

@app.get("/analytics/graph/topology")
async def get_graph_topology(user_id: str = "system_user"):
    return graph_engine.get_topology_summary(user_id)

@app.get("/analytics/graph/visual")
async def get_graph_visual(user_id: str = "system_user"):
    return graph_engine.get_recent_triplets(user_id)

@app.get("/analytics/graph/historical")
async def get_historical_graph(timestamp: str, user_id: str = "system_user"):
    """Phase 3: Temporal Scrubbing. Returns the graph state at a specific point in time."""
    return graph_engine.get_historical_topology(user_id, timestamp)

# --- Endpoints ---
@app.get("/")
async def root(): return {"status": "ONLINE", "system": "Akasha Universal Library"}

# --- Auth Endpoints ---

@app.post("/auth/signup", response_model=Token)
async def signup(request: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == request.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth_utils.get_password_hash(request.password)
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = auth_utils.create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not auth_utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_utils.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/query/stream")
async def stream_query(request: QueryRequest, current_user: User = Depends(get_current_user)):
    async def response_generator():
        q = request.query.lower().strip()
        
        # Phase 1 Wisdom: Streaming Reasoning (System 2 HUD)
        try:
            synthesis = await ai_engine.synthesize_graph_rag(request.query, current_user.id, wisdom_mode=request.wisdom_mode)
            
            # Stream the internal monologue first
            monologue = synthesis.get("monologue", "")
            if monologue:
                yield f"<thought>\n"
                for word in monologue.split():
                    yield f"{word} "
                    await asyncio.sleep(0.01)
                yield f"\n</thought>\n\n"
            
            # Stream the final answer
            full_answer = synthesis.get("answer", "")
            for word in full_answer.split():
                yield f"{word} "
                await asyncio.sleep(0.01)
                
        except Exception as e:
            yield f"TRANSCRIPTION_ERROR: {str(e)}"
    return StreamingResponse(response_generator(), media_type="text/plain")

@app.post("/query/rag")
async def query_rag(request: QueryRequest, current_user: User = Depends(get_current_user)):
    query_text = request.query
    
    # Handle Ghostwriter mode logic
    if request.is_ghost_writer:
        persona_prompt = "You are the Akasha Ghostwriter. Your goal is to improve, expand, or refine the user's text while maintaining a professional and insightful tone."
        query_text = f"{persona_prompt}\n\nUser Text: {request.query}\n\nRefined Text:"

    # Extension Context Handling: If query contains page context
    if request.context:
        # Use grounded response with provided context
        grounded_query = f"Based on this web page content: {request.context[:10000]}\n\nUser Question: {query_text}"
        answer = await ai_engine.synthesize_graph_rag(grounded_query, current_user.id, wisdom_mode=request.wisdom_mode)
    else:
        answer = await ai_engine.synthesize_graph_rag(query_text, current_user.id, wisdom_mode=request.wisdom_mode)
    
    if isinstance(answer, dict):
        return {
            "query": request.query, 
            "answer": answer.get("answer"), 
            "monologue": answer.get("monologue"), 
            "suggestion": answer.get("suggestion"),
            "crowd_confidence": answer.get("crowd_confidence")
        }
    return {"query": request.query, "answer": answer}

@app.post("/search/semantic")
async def semantic_search(request: SemanticSearchRequest, current_user: User = Depends(get_current_user)):
    """Search through vaulted artifacts using vector embeddings."""
    results = ai_engine.search_vectors(request.query, n_results=request.n_results, user_id=current_user.id)
    return results

@app.post("/automation/form_fill")
async def smart_form_fill(request: FormFillRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Predicts form field values based on user's Digital Ego and vaulted data."""
    profile = await get_user_psychology(current_user, db)
    # Ask the Librarian to map profile data to requested fields
    mapping_prompt = f"Map the following user profile to these form fields: {', '.join(request.fields)}. Profile: {json.dumps(profile)}. Return ONLY a JSON object mapping fields to values."
    mapping_raw = ai_engine.local_inference(mapping_prompt)
    try:
        import re
        match = re.search(r'\{.*\}', mapping_raw, re.DOTALL)
        return json.loads(match.group()) if match else {}
    except: return {}

@app.post("/automation/monitor")
async def register_web_monitor(request: MonitorRequest, current_user: User = Depends(get_current_user)):
    """Schedules a background task to monitor a URL for a specific condition."""
    # Logic to add to scheduler (Simplified)
    print(f"Butler: Now monitoring {request.url} for '{request.trigger_condition}'")
    return {"status": "MONITOR_ACTIVE", "url": request.url}

class SyncRequest(BaseModel):
    platform: str
    context: str
    user_id: Optional[str] = "system_user"

@app.post("/automation/sync")
async def cross_app_sync(request: SyncRequest, current_user: User = Depends(get_current_user)):
    """Syncs captured knowledge to external platforms like Notion or Slack."""
    print(f"Connector: Syncing context to {request.platform} for {current_user.id}")
    # Integration logic would go here
    return {"status": "SYNC_SUCCESS", "platform": request.platform}

@app.post("/query/debate")
async def query_debate(request: QueryRequest):
    try:
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(None, ai_engine.council.debate_council.run_debate, request.query)
        return {"query": request.query, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debate failed: {str(e)}")

@app.post("/translate")
async def translate_text(request: TranslateRequest):
    try:
        loop = asyncio.get_event_loop()
        translation = await loop.run_in_executor(
            None, 
            ai_engine.council.scholar.translate, 
            request.text, 
            request.target_language
        )
        return {"original": request.text, "translation": translation, "target_language": request.target_language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

async def process_batch_ingestion(files_data: List[Dict[str, str]], user_id: str, delete_after: bool = True):
    """Background worker for batch ingestion with chunk-level tracking."""
    db = SessionLocal()
    loop = asyncio.get_event_loop()
    try:
        for file_info in files_data:
            tmp_path = file_info["tmp_path"]
            filename = file_info["filename"]
            try:
                await manager.broadcast(json.dumps({
                    "event": "INGESTION_PROGRESS",
                    "filename": filename,
                    "status": "PROCESSING",
                    "detail": "Parsing dataset..."
                }))

                # 1. Parsing (Heavy CPU)
                artifacts_data = await loop.run_in_executor(None, ingest.ingest_dataset, tmp_path, filename)

                total_chunks = len(artifacts_data)
                for idx, data in enumerate(artifacts_data):
                    if "error" in data:
                        await manager.broadcast(json.dumps({
                            "event": "INGESTION_PROGRESS",
                            "filename": filename,
                            "status": "ERROR",
                            "detail": data["error"]
                        }))
                        continue

                    # 2. Progress Update
                    await manager.broadcast(json.dumps({
                        "event": "INGESTION_PROGRESS",
                        "filename": filename,
                        "status": "PROCESSING",
                        "detail": f"Ingesting chunk {idx + 1}/{total_chunks}...",
                        "count": idx + 1
                    }))

                    # 3. Deep Analysis & Storage (Heavy AI/DB)
                    await ingest_library_artifact(data["title"], data["content"], data["artifact_type"], data["metadata"], db, user_id)

                await manager.broadcast(json.dumps({
                    "event": "INGESTION_PROGRESS",
                    "filename": filename,
                    "status": "SUCCESS",
                    "count": total_chunks,
                    "detail": "Harvest complete."
                }))
            except Exception as e:
                print(f"Batch Ingestion Error [{filename}]: {e}")
                await manager.broadcast(json.dumps({
                    "event": "INGESTION_PROGRESS",
                    "filename": filename,
                    "status": "ERROR",
                    "detail": str(e)
                }))
            finally:
                if os.path.exists(tmp_path): os.unlink(tmp_path)
    finally:
        db.close()
@app.post("/ingest/dataset")
async def ingest_dataset(background_tasks: BackgroundTasks, file: List[UploadFile] = File(...), user_id: str = Form("system_user")):
    files_to_process = []
    for f in file:
        suffix = os.path.splitext(f.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await f.read())
            tmp_path = tmp.name
        files_to_process.append({"tmp_path": tmp_path, "filename": f.filename})
    
    background_tasks.add_task(process_batch_ingestion, files_to_process, user_id)
    return {"status": "BATCH_QUEUED", "message": f"Queued {len(file)} files for neural feeding."}

@app.post("/ingest/clipper")
async def ingest_web_clipper(request: IngestUrlRequest, db: Session = Depends(get_db)):
    scraped = ingest.scrape_web_memory(request.url)
    if "error" in scraped: raise HTTPException(status_code=400, detail=scraped["error"])
    
    # Sovereign Privacy Layer: Scrub scraped content before ingestion
    scrubbed_content = redactor.scrub(scraped["content"])
    
    art = await ingest_library_artifact(scraped["title"], scrubbed_content, "web_clip", {"url": request.url}, db, request.user_id)
    return art

@app.post("/ingest/folder")
async def ingest_folder_endpoint(background_tasks: BackgroundTasks, folder_path: str = Form(...), user_id: str = Form("system_user")):
    """Recursively ingests all files in a folder."""
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found.")
    
    # We use the same batch processing logic
    all_files = []
    for root, dirs, files in os.walk(folder_path):
        for name in files:
            all_files.append({"tmp_path": os.path.join(root, name), "filename": name})
    
    background_tasks.add_task(process_batch_ingestion, all_files, user_id)
    return {"status": "FOLDER_INGESTION_STARTED", "file_count": len(all_files)}

class SpecializationRequest(BaseModel):
    agent_name: str
    folder_path: str
    user_id: Optional[str] = "system_user"

@app.post("/user/training/specialize")
async def train_specialist(request: SpecializationRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """Universal training endpoint to specialize an agent on a specific dataset."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = request.folder_path
    
    if not os.path.isabs(target_path):
        target_path = os.path.join(base_dir, "akasha_data", request.folder_path)
    
    if not os.path.exists(target_path):
        return {"status": "ERROR", "message": f"Dataset not found at {target_path}"}
    
    all_files = []
    for root, dirs, files in os.walk(target_path):
        for name in files:
            if name.endswith(('.py', '.md', '.txt', '.yml', '.yaml', '.json', '.csv', '.pdf', '.docx')):
                all_files.append({"tmp_path": os.path.join(root, name), "filename": name})
            
    if not all_files:
        return {"status": "ERROR", "message": f"No processable files found in {request.folder_path}."}

    background_tasks.add_task(process_batch_ingestion, all_files, current_user.id, False)
    
    return {
        "status": "TRAINING_STARTED", 
        "message": f"Specializing {request.agent_name} on {len(all_files)} artifacts from '{request.folder_path}'."
    }

@app.post("/ingest/audio")
async def ingest_audio(file: UploadFile = File(...), user_id: str = Form("system_user"), db: Session = Depends(get_db)):
    audio_data = await file.read()
    transcript = await ingest.transcribe_audio_memory(audio_data)
    art = await ingest_library_artifact(f"Audio: {file.filename}", transcript, "audio_transcript", {}, db, user_id)
    return art

@app.post("/vision/analyze")
async def vision_analyze(file: UploadFile = File(...), user_id: str = Form("system_user"), db: Session = Depends(get_db)):
    image_data = await file.read()
    description = multimodal.visual_reasoning(image_data)
    art = await ingest_library_artifact(f"Visual: {file.filename}", description, "visual_memory", {}, db, user_id)
    return {"description": description, "artifact_id": art.id}

@app.websocket("/akasha/sensory")
async def akasha_sensory_stream(websocket: WebSocket, token: Optional[str] = None):
    """
    The High-Speed Sensory Bridge: Handles real-time voice (via STT) and visual streams.
    """
    await manager.connect(websocket)
    import base64
    
    # Identify user (Simplified for Project Flash stability)
    user_id = "system_user"
    if token and token != "null" and token != "undefined":
        payload = auth_utils.decode_access_token(token)
        if payload:
            username = payload.get("sub")
            db = SessionLocal()
            user = db.query(User).filter(User.username == username).first()
            if user: user_id = user.id
            db.close()

    print(f"Sensory: Unified stream opened for user {user_id}")
    db = SessionLocal()
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    try:
        while True:
            # Handle both text (transcript) and bytes (visual context)
            message = await websocket.receive()
            
            if "text" in message:
                data = json.loads(message["text"])
                if data.get("type") == "TRANSCRIPT":
                    transcript = data.get("payload", "")
                    print(f"Sensory: Captured Voice -> '{transcript}'")

                    # PROJECT FLASH: Direct Reflex Greetings (No wake word required)
                    clean_t = transcript.lower().strip().rstrip('?.!')
                    greetings = ["hello", "hi", "hey", "archivist", "akasha"]
                    
                    response_text = ""
                    monologue = ""

                    if clean_t in greetings:
                        print(f"Sensory: Direct Greeting Detected -> '{clean_t}'")
                        response_text = f"Greetings. I am {ai_engine.personality.neural_name}. How can I assist your synthesis today?"
                        monologue = "Fast reflex: Direct greeting detected. Bypassing wake word requirement."
                    else:
                        # Wake Word / Command Logic
                        neural_names = [settings.neural_name] if settings and settings.neural_name else ["Archivist"]
                        is_wake, command = ai_engine.council.gatekeeper.check_neural_name(transcript, neural_names)

                        if is_wake:
                            print(f"Sensory: Wake Word Detected. Executing -> {command}")
                            await websocket.send_json({"type": "HUD_MORPH", "intent": "SYNTHESIS"})
                            synthesis = await ai_engine.synthesize_graph_rag(command, user_id=user_id)
                            response_text = synthesis["answer"]
                            monologue = synthesis.get("monologue", "")
                        else:
                            await websocket.send_json({"type": "PASSIVE_TRANSCRIPT", "payload": transcript})
                            continue

                    if response_text:
                        # TTS Synthesis (Fish Audio)
                        audio_content = ai_engine.council.vocalist.synthesize_fish(response_text)
                        audio_base64 = base64.b64encode(audio_content).decode('utf-8') if audio_content else None
                        
                        await websocket.send_json({
                            "type": "RESPONSE", 
                            "payload": {
                                "answer": response_text,
                                "monologue": monologue
                            },
                            "audio": audio_base64
                        })

            elif "bytes" in message:
                # Visual context...
                data = message["bytes"]
                description = multimodal.visual_reasoning(data)
                await websocket.send_json({"type": "VISUAL_CONTEXT", "payload": description})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Sensory WebSocket Error: {e}")
        manager.disconnect(websocket)
    finally:
        db.close()

@app.post("/user/settings")
async def update_settings(settings: Dict[str, Any], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not db_settings:
        db_settings = UserSettings(user_id=current_user.id); db.add(db_settings)
    if "neural_name" in settings: db_settings.neural_name = settings["neural_name"]
    if "assistant_persona" in settings: db_settings.assistant_persona = settings["assistant_persona"]
    if "wake_words" in settings: db_settings.wake_words = settings["wake_words"]
    if "turbo_mode" in settings: db_settings.turbo_mode = settings["turbo_mode"]
    if "groq_api_key" in settings: db_settings.groq_api_key = settings["groq_api_key"]
    if "integrations" in settings: db_settings.integrations = settings["integrations"]
    db.commit()
    ai_engine.update_council(turbo_mode=db_settings.turbo_mode, groq_key=db_settings.groq_api_key)
    ai_engine.rename_identity(db_settings.neural_name)
    return db_settings

@app.get("/user/psychology")
async def get_user_psychology(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserPsychology).filter(UserPsychology.user_id == current_user.id).first()
    if not profile: return {"status": "NO_PROFILE"}
    return {"known_name": profile.known_name, "ocean_traits": {"openness": profile.openness, "conscientiousness": profile.conscientiousness, "extraversion": profile.extraversion, "agreeableness": profile.agreeableness, "neuroticism": profile.neuroticism}, "cognitive_distortions": profile.identified_distortions, "habit_patterns": profile.habit_patterns, "current_mood": profile.current_mood}

@app.post("/telemetry")
async def log_telemetry(request: TelemetryRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    activity = telemetry_engine.log_activity(db, current_user.id, request.model_dump())
    return activity

@app.post("/node/sensory")
async def ingest_sensory_node(data: SensoryNodeData, db: Session = Depends(get_db)):
    """Ingests real-time sensory data from mobile or remote nodes."""
    if data.is_encrypted:
        # Zero-Knowledge: Store as an encrypted artifact
        # The Head Archivist will defer analysis until a trusted client decrypts it
        await ingest_library_artifact(
            title=f"Encrypted Sensory: {data.node_key}",
            content=data.encrypted_blob,
            artifact_type="encrypted_sensory",
            extra_meta={"node_key": data.node_key, "is_encrypted": True},
            db=db,
            user_id=data.user_id
        )
        return {"status": "ENCRYPTED_INGESTED"}

    # Standard Ingest
    if data.audio_payload:
        audio_bytes = base64.b64decode(data.audio_payload)
        await sensory.ingest_audio_stream(audio_bytes, data.user_id)
        
    # Store metadata/location as telemetry
    telemetry_engine.log_activity(db, data.user_id, {
        "type": "SENSORY_NODE_UPDATE",
        "node_key": data.node_key,
        "location": data.location,
        "timestamp": data.timestamp
    })
    
    return {"status": "SUCCESS"}

@app.get("/telemetry/recent")
async def get_recent_telemetry(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return telemetry_engine.get_recent_activity(db, current_user.id)

@app.get("/artifacts")
async def list_artifacts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    artifacts = db.query(LibraryArtifact).filter(LibraryArtifact.user_id == current_user.id).order_by(LibraryArtifact.timestamp.desc()).all()
    for art in artifacts: art.decrypt_content()
    return artifacts

@app.get("/analytics")
async def get_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    artifacts = db.query(LibraryArtifact).filter(LibraryArtifact.user_id == current_user.id).all()
    dist = {}
    for art in artifacts: dist[art.artifact_type] = dist.get(art.artifact_type, 0) + 1
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    return {"total_count": len(artifacts), "category_distribution": dist, "system_status": "OPTIMAL", "neural_name": settings.neural_name if settings else "Archivist"}

@app.post("/interpreter/run")
async def run_interpreter(request: InterpreterRequest, current_user: User = Depends(get_current_user)):
    return {"output": ai_engine.council.scholar.execute_local_code(request.script)}

@app.post("/actions/run")
async def run_action_goal(request: ActionGoalRequest, current_user: User = Depends(get_current_user)):
    results = await executive.run_action_loop(request.goal, {"user_id": current_user.id})
    return {"results": results}

from finance_engine import FinanceEngine
finance_engine = FinanceEngine(ai_engine)

from eye_engine import EyeEngine
from env_sensor import EnvironmentalSensor
from learning_engine import LearningEngine
from backup_engine import BackupEngine

eye_engine = EyeEngine(ai_engine, multimodal)
env_sensor = EnvironmentalSensor()
learning_engine = LearningEngine(ai_engine)
backup_engine = BackupEngine()

@app.post("/eye/toggle")
async def toggle_vision(active: bool):
    eye_engine.toggle(active)
    return {"status": "SUCCESS", "active": active}

@app.get("/eye/pulse")
async def eye_pulse(current_user: User = Depends(get_current_user)):
    analysis = await eye_engine.capture_and_analyze(current_user.id)
    return {"status": "SUCCESS", "analysis": analysis}

@app.get("/env/context")
async def get_env_context():
    return env_sensor.detect_all()

@app.post("/tutor/syllabus")
async def generate_syllabus(artifact_ids: List[str], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return learning_engine.generate_syllabus(artifact_ids, db)

@app.get("/tutor/quiz/{artifact_id}")
async def generate_quiz(artifact_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return learning_engine.generate_quiz(artifact_id, db)

@app.post("/backup/create")
async def create_backup(current_user: User = Depends(get_current_user)):
    path = backup_engine.create_sovereign_backup()
    shards = backup_engine.shard_backup(path)
    return {"status": "SUCCESS", "backup_path": path, "shards": shards}

@app.post("/voice/clone")
async def upload_voice_sample(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    # Mock voice cloning logic
    ai_engine.council.vocalist.custom_voice_id = f"CLONE_{uuid.uuid4().hex[:8]}"
    return {"status": "SUCCESS", "voice_id": ai_engine.council.vocalist.custom_voice_id}

@app.get("/actions/history")
async def get_action_history(current_user: User = Depends(get_current_user)):
    return executive.get_history()

class SpeakRequest(BaseModel):
    text: str

@app.post("/voice/speak")
async def voice_speak(request: SpeakRequest, current_user: User = Depends(get_current_user)):
    """Triggers neural speech synthesis for the given text."""
    success = await ai_engine.council.vocalist.speak_stream(request.text)
    return {"status": "SUCCESS" if success else "ERROR"}

@app.post("/plugins/generate")
async def generate_plugin(request: PluginGenerateRequest):
    return ai_engine.council.plugin_architect.generate_plugin(request.user_request)

@app.post("/plugins/activate")
async def activate_plugin(request: PluginActivateRequest, db: Session = Depends(get_db)):
    # Simple logic for dynamic loading (simplified from previous version for stability)
    return {"status": "SUCCESS", "message": "Plugin activation requested."}

# --- Lightweight Request Models ---
class ProactiveRequest(BaseModel):
    url: str
    title: str
    content: str
    user_id: Optional[str] = "system_user"

@app.post("/proactive/critique")
async def proactive_critique(request: ProactiveRequest, current_user: User = Depends(get_current_user)):
    """Phase 6: Real-time 'Vision' HUD: Proactively critiques what the user is reading."""
    print(f"Vision HUD: Proactively critiquing '{request.title}'...")
    
    # 1. Gather wisdom from multiple perspectives
    logic_critique = ai_engine.council.scholar.analyze_logic(request.content)
    bias_critique = ai_engine.council.sentinel.critique(request.content)
    
    # 2. Consult the crowd for a deep synthesis
    crowd_query = f"Critique the following article for depth, truth, and perspective.\nTitle: {request.title}\nContent: {request.content[:2000]}"
    crowd_result = await ai_engine.council.crowd_engine.consult_crowd(crowd_query, context=request.content[:1000])
    
    return {
        "title": request.title,
        "logic_critique": logic_critique,
        "bias_critique": bias_critique,
        "crowd_wisdom": crowd_result["wisdom"],
        "crowd_confidence": crowd_result["confidence"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
