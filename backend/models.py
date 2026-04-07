from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text, Float, Integer, Boolean
import uuid
import datetime
from database import Base

class User(Base):
    """Sovereign User: The root identity for all data and settings."""
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

class LibraryArtifact(Base):
    """
    The core entity of the Universal Library. Replaces 'MemoryRecord'.
    Can be a book, a research paper, a news article, or a user thought.
    """
    __tablename__ = "library_artifacts"

    # Using String for ID to maintain compatibility with SQLite and PostgreSQL
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=True) # e.g., "Theory of Relativity"
    content = Column(Text, nullable=False) # The actual text or transcript
    
    # Ontology / Taxonomy
    artifact_type = Column(String, default="document") # book, paper, article, memory
    schema_id = Column(String, ForeignKey("object_schemas.id"), nullable=True)
    language = Column(String, default="en")
    
    # Multi-tenancy Isolation
    user_id = Column(String, default="system_user", index=True) # The ID of the Personal Assistant Pod
    
    # AI Metadata
    summary = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String, nullable=True)
    
    # Privacy Tier
    # Options: PUBLIC, SHARED, PRIVATE, SOVEREIGN
    privacy_tier = Column(String, default="PRIVATE")

    def encrypt_content(self):
        """Encrypts content if privacy tier is SOVEREIGN."""
        if self.privacy_tier == "SOVEREIGN":
            from privacy_utils import vault
            self.content = vault.encrypt(self.content)

    def decrypt_content(self):
        """Decrypts content if privacy tier is SOVEREIGN."""
        if self.privacy_tier == "SOVEREIGN":
            from privacy_utils import vault
            self.content = vault.decrypt(self.content)

    # Web3 / Provenance
    blockchain_hash = Column(String, unique=True, nullable=True) # SHA-256 of content
    transaction_id = Column(String, nullable=True) # E.g., Ethereum Tx
    ipfs_cid = Column(String, nullable=True) # Distributed storage link
    arweave_tx = Column(String, nullable=True) # Permanent storage link
    zkp_commitment = Column(String, nullable=True) # Privacy proof
    archivist_signature = Column(String, nullable=True) # DID signature

    # Flexible Metadata
    metadata_json = Column(JSON, default={}) # Stores authors, dates, publishers, etc.
    
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class ObjectSchema(Base):
    """Definitions for typed objects (Anytype Style)."""
    __tablename__ = "object_schemas"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False) # e.g. "Person", "Book"
    description = Column(String)
    definition_json = Column(JSON, default={}) # JSON-LD schema definition
    user_id = Column(String, default="system_user")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SRSCard(Base):
    """Neural Flashcards for Spaced Repetition (Pillar 1)."""
    __tablename__ = "srs_cards"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    artifact_id = Column(String, ForeignKey("library_artifacts.id"))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    # SuperMemo-2 Algorithm fields
    interval = Column(Float, default=1.0) # In days
    repetition = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)
    next_review = Column(DateTime, default=datetime.datetime.utcnow)

class UserTask(Base):
    """Autonomous Goal Tracking (Pillar 3)."""
    __tablename__ = "user_tasks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    task_description = Column(String, nullable=False)
    status = Column(String, default="PENDING") # PENDING, COMPLETED, RESEARCHING
    priority = Column(Integer, default=1)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class UserActivity(Base):
    """Active Stream of Life (Browsing, Music, Media)."""
    __tablename__ = "user_activities"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    activity_type = Column(String) # browser_visit, music_play, video_watch
    title = Column(String)
    content = Column(Text, nullable=True) # Snippets of text or transcript
    source_url = Column(String, nullable=True)
    metadata_json = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class UserCalendarEvent(Base):
    """Personal Schedule Integration."""
    __tablename__ = "user_calendar_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    event_id = Column(String) # ID from Google/Outlook
    summary = Column(String)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    metadata_json = Column(JSON, default={})
    last_synced = Column(DateTime, default=datetime.datetime.utcnow)

class UserLifeEntity(Base):
    """Long-term Personal Assets (Accounts, Devices, Projects, Wallets)."""
    __tablename__ = "user_life_entities"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    entity_type = Column(String) # bank_account, github_repo, iot_device, crypto_wallet
    name = Column(String)
    identifier = Column(String) # e.g. "0x...", "user/repo"
    metadata_json = Column(JSON, default={})
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class UserToken(Base):
    """Secure Storage for OAuth2 Access and Refresh Tokens."""
    __tablename__ = "user_tokens"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    provider = Column(String) # google, spotify, github
    access_token = Column(String)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    scopes = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class UserSettings(Base):
    """Sovereign Settings: Custom identity and Voice Biometrics."""
    __tablename__ = "user_settings"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, unique=True, index=True, default="system_user")
    
    # Unified Identity (Replaces technical 'wake_names')
    neural_name = Column(String, default="Archivist")
    assistant_persona = Column(String, default="Archivist")
    wake_words = Column(String, default="Archivist, Akasha") # Comma-separated triggers
    
    # Voice Fingerprinting (Stored as a vector/embedding)
    voice_fingerprint = Column(JSON, nullable=True) 
    voice_verification_enabled = Column(Boolean, default=False)
    
    # Privacy & Sovereignty
    biometric_lock = Column(Boolean, default=False)
    
    # Speed & Optimization
    turbo_mode = Column(Boolean, default=False) # If true, uses Groq for chat synthesis
    groq_api_key = Column(String, nullable=True) # Encrypted in production

    # Integrations (Phase 2 expansion)
    integrations = Column(JSON, default={}) # Stores { "Slack": true, "Spotify": false, ... }
    
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class UserPsychology(Base):
    """The 'Ego' and Psychological Profile of the User."""
    __tablename__ = "user_psychology"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, unique=True, index=True, default="system_user")
    
    # Identity
    known_name = Column(String, default="User")
    
    # Big Five (OCEAN) - Scores from 0.0 to 1.0, learned slowly over time
    openness = Column(Float, default=0.5)
    conscientiousness = Column(Float, default=0.5)
    extraversion = Column(Float, default=0.5)
    agreeableness = Column(Float, default=0.5)
    neuroticism = Column(Float, default=0.5)
    
    # Cognitive Tracking
    identified_distortions = Column(JSON, default={}) # e.g., {"catastrophizing": 2}
    habit_patterns = Column(JSON, default=[])
    
    # The AI's "Theory of Mind" regarding the user's current state
    current_mood = Column(String, default="Neutral")
    core_values = Column(JSON, default=[]) # e.g. ["Freedom", "Knowledge", "Creativity"]
    current_goals = Column(JSON, default=[]) # e.g. ["Write a book", "Learn Rust"]
    life_narrative = Column(Text, nullable=True) # A synthesized "Autobiography"
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class NeuralSkill(Base):
    """The Skill Library: Stores reusable, executable Python snippets discovered by agents."""
    __tablename__ = "neural_skills"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    description = Column(Text)
    code = Column(Text)
    language = Column(String, default="python")
    success_count = Column(Integer, default=1)
    user_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AgentPerformance(Base):
    """Fitness Tracking: Records benchmark results for agents to guide evolution."""
    __tablename__ = "agent_performance"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_name = Column(String, index=True)
    task_category = Column(String) # e.g., "Math", "Summarization"
    fitness_score = Column(Float) # 0.0 to 1.0
    latency_ms = Column(Float)
    error_log = Column(Text, nullable=True)
    user_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class KnowledgeEvent(Base):
    """The Akashic Log: Immutable event store for every modification to the library."""
    __tablename__ = "knowledge_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String, index=True) # ARTIFACT_CREATED, THOUGHT_REFINED, CODE_EVOLVED
    payload = Column(JSON) # The full state of the change
    user_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    version = Column(Integer, default=1)
