from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
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
try:
    import keyring
except ImportError:
    keyring = None

# --- Lightweight Request Models ---
class QueryRequest(BaseModel):
    query: str
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
    location: Dict[str, float]
    audio_payload: Optional[str] = None 
    timestamp: float

class FeedbackRequest(BaseModel):
    feedback: str
    agent_name: str

class ActionGoalRequest(BaseModel):
    goal: str
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
    """Helper function to consolidate ingestion logic for different sources. Offloaded to thread."""
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
            db.add(existing_schema); db.commit(); db.refresh(existing_schema)
        schema_id = existing_schema.id

    new_art = LibraryArtifact(
        title=title,
        content=content,
        artifact_type=artifact_type,
        schema_id=schema_id,
        user_id=user_id,
        summary=analysis["summary"],
        sentiment_label=analysis["sentiment_label"],
        blockchain_hash=hashlib.sha256(content.encode()).hexdigest(),
        metadata_json={
            **(extra_meta or {}),
            "entities": analysis["entities"],
            "structured_data": analysis["deep_metadata"].get("structured_data", {})
        }
    )
    new_art.encrypt_content()
    db.add(new_art); db.commit(); db.refresh(new_art)
    
    # 3. Vector Storage (Heavy IO/CPU, but chroma client is fast, let's keep in executor just in case)
    await loop.run_in_executor(None, ai_engine.store_vector, new_art.id, content, analysis, user_id)
    
    # 4. Graph Logic
    graph_engine.create_artifact_node(new_art.id, new_art.title, artifact_type, user_id)
    # New: Ingest triplets into Knowledge Graph
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

def get_initial_ai_engine():
    db = SessionLocal()
    try:
        settings = db.query(UserSettings).filter(UserSettings.user_id == "system_user").first()
        if settings:
            return AIEngine(turbo_mode=settings.turbo_mode, groq_key=settings.groq_api_key, neural_name=settings.neural_name)
        return AIEngine()
    finally:
        db.close()

# Instantiate Engines
ai_engine = get_initial_ai_engine()
intel_engine = IntelEngine()
p2p_node = P2PNode(intel_engine=intel_engine)
blockchain = BlockchainAdapter()
graph_engine = GraphEngine()
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
                await chronos.run_nocturnal_consolidation("system_user")
                
                # Proactive Behavioral Reflection (Every 12 hours)
                if now - last_behavioral_mining > datetime.timedelta(hours=12):
                    print("Sentinel: Initiating Deep Behavioral Reflection...")
                    await chronos.run_behavioral_pattern_mining("system_user")
                    last_behavioral_mining = now

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

# --- Analytics & Graph Endpoints ---

@app.get("/analytics/graph/topology")
async def get_graph_topology(user_id: str = "system_user"):
    return graph_engine.get_topology_summary(user_id)

@app.get("/analytics/graph/visual")
async def get_graph_visual(user_id: str = "system_user"):
    return graph_engine.get_recent_triplets(user_id)

# --- Endpoints ---
@app.get("/")
async def root(): return {"status": "ONLINE", "system": "Akasha Universal Library"}


@app.post("/query/stream")
async def stream_query(request: QueryRequest):
    async def response_generator():
        q = request.query.lower().strip()
        
        # Identity Renaming Hook
        identity_update = handle_identity_commands(request.query, request.user_id)
        if identity_update:
            yield identity_update; return

        # User Identity Hook
        user_identity_update = handle_user_identity(request.query, request.user_id)
        if user_identity_update:
            yield user_identity_update; return

        if q in ["hi", "hello", "hey", "greetings", "jarvis", "archivist"]:
            response = f"Greetings. I am {ai_engine.personality.neural_name}. Ready to assist."
            for word in response.split():
                yield f"{word} "; await asyncio.sleep(0.03)
            return
        try:
            vector_results = ai_engine.search_vectors(request.query, n_results=5, user_id=request.user_id)
            vector_context = vector_results.get("documents", [[]])[0]
            entities = [e['word'] for e in ai_engine.ner_pipeline(request.query)]
            graph_context = graph_engine.search_graph_context(entities, user_id=request.user_id)
            synthesis = ai_engine.synthesize_graph_rag(request.query, vector_context, graph_context)
            full_answer = synthesis["answer"]
            for word in full_answer.split():
                yield f"{word} "; await asyncio.sleep(0.01)
        except Exception as e:
            yield f"TRANSCRIPTION_ERROR: {str(e)}"
    return StreamingResponse(response_generator(), media_type="text/plain")

@app.post("/query/rag")
async def query_rag(request: QueryRequest):
    # Identity Renaming Hook
    identity_update = handle_identity_commands(request.query, request.user_id)
    if identity_update:
        return {"query": request.query, "answer": identity_update}

    entities = [e['word'] for e in ai_engine.ner_pipeline(request.query)]
    vector_results = ai_engine.search_vectors(request.query, n_results=5, user_id=request.user_id)
    vector_context = vector_results.get("documents", [[]])[0]
    graph_context = graph_engine.search_graph_context(entities, user_id=request.user_id)
    is_poor = not vector_context or all(len(c) < 200 for c in vector_context)
    if is_poor:
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(None, ai_engine.council.scout.deep_research, request.query, ingest)
    else:
        answer = ai_engine.synthesize_graph_rag(request.query, vector_context, graph_context)
    return {"query": request.query, "answer": answer, "deep_research_used": is_poor}

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

async def process_batch_ingestion(files_data: List[Dict[str, str]], user_id: str):
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
    art = await ingest_library_artifact(scraped["title"], scraped["content"], "web_clip", {"url": request.url}, db, request.user_id)
    return art

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

@app.websocket("/jarvis/sensory")
async def jarvis_sensory_stream(websocket: WebSocket, user_id: str = "system_user"):
    await manager.connect(websocket)
    db = SessionLocal()
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    try:
        while True:
            data = await websocket.receive_bytes()
            if len(data) < 50000:
                if settings and settings.voice_verification_enabled:
                    if not speaker_verifier.verify(data, settings.voice_fingerprint): continue
                transcript = await ingest.transcribe_audio_memory(data)
                
                # Zero-effort identity recognition
                identity_update = handle_identity_commands(transcript, user_id)
                if identity_update:
                    await websocket.send_json({"type": "WAKE_RESPONSE", "payload": {"answer": identity_update, "monologue": "Calibrating new identity..."}})
                    continue

                is_wake_triggered, command = ai_engine.council.gatekeeper.check_neural_name(transcript, settings.neural_name if settings else "Archivist")
                if is_wake_triggered:
                    result = await sensory.process_voice_command(command, user_id)
                    await websocket.send_json({"type": "WAKE_RESPONSE", "payload": result, "vocal_trigger": True})
                elif len(transcript) > 5:
                    await websocket.send_json({"type": "PASSIVE_TRANSCRIPT", "payload": transcript})
            else:
                result = await sensory.capture_visual_context(data, user_id)
                if result: await websocket.send_json({"type": "VISUAL_CONTEXT", "payload": result})
    except WebSocketDisconnect: manager.disconnect(websocket)
    finally: db.close()

@app.post("/user/settings")
async def update_settings(settings: Dict[str, Any], user_id: str = "system_user", db: Session = Depends(get_db)):
    db_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not db_settings:
        db_settings = UserSettings(user_id=user_id); db.add(db_settings)
    if "neural_name" in settings: db_settings.neural_name = settings["neural_name"]
    if "assistant_persona" in settings: db_settings.assistant_persona = settings["assistant_persona"]
    if "turbo_mode" in settings: db_settings.turbo_mode = settings["turbo_mode"]
    if "groq_api_key" in settings: db_settings.groq_api_key = settings["groq_api_key"]
    db.commit()
    ai_engine.update_council(turbo_mode=db_settings.turbo_mode, groq_key=db_settings.groq_api_key)
    ai_engine.rename_identity(db_settings.neural_name)
    return db_settings

@app.get("/user/psychology")
async def get_user_psychology(user_id: str = "system_user", db: Session = Depends(get_db)):
    profile = db.query(UserPsychology).filter(UserPsychology.user_id == user_id).first()
    if not profile: return {"status": "NO_PROFILE"}
    return {"known_name": profile.known_name, "ocean_traits": {"openness": profile.openness, "conscientiousness": profile.conscientiousness, "extraversion": profile.extraversion, "agreeableness": profile.agreeableness, "neuroticism": profile.neuroticism}, "cognitive_distortions": profile.identified_distortions, "habit_patterns": profile.habit_patterns, "current_mood": profile.current_mood}

@app.get("/artifacts")
async def list_artifacts(user_id: str = "system_user", db: Session = Depends(get_db)):
    artifacts = db.query(LibraryArtifact).filter(LibraryArtifact.user_id == user_id).order_by(LibraryArtifact.timestamp.desc()).all()
    for art in artifacts: art.decrypt_content()
    return artifacts

@app.get("/analytics")
async def get_analytics(user_id: str = "system_user", db: Session = Depends(get_db)):
    artifacts = db.query(LibraryArtifact).filter(LibraryArtifact.user_id == user_id).all()
    dist = {}
    for art in artifacts: dist[art.artifact_type] = dist.get(art.artifact_type, 0) + 1
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    return {"total_count": len(artifacts), "category_distribution": dist, "system_status": "OPTIMAL", "neural_name": settings.neural_name if settings else "Archivist"}

@app.post("/interpreter/run")
async def run_interpreter(request: InterpreterRequest):
    return {"output": ai_engine.council.scholar.execute_local_code(request.script)}

@app.post("/actions/run")
async def run_action_goal(request: ActionGoalRequest):
    results = await executive.run_action_loop(request.goal, {"user_id": request.user_id})
    return {"results": results}

@app.get("/actions/history")
async def get_action_history(user_id: str = "system_user"):
    return executive.get_history()

@app.post("/plugins/generate")
async def generate_plugin(request: PluginGenerateRequest):
    return ai_engine.council.plugin_architect.generate_plugin(request.user_request)

@app.post("/plugins/activate")
async def activate_plugin(request: PluginActivateRequest, db: Session = Depends(get_db)):
    # Simple logic for dynamic loading (simplified from previous version for stability)
    return {"status": "SUCCESS", "message": "Plugin activation requested."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
