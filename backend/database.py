from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import functools
from dotenv import load_dotenv

load_dotenv()

# --- Persistent Memory: In-Memory Cache (Digital Ego Offloading) ---
def lru_cache_with_ttl(maxsize=128, ttl=300):
    """Simple LRU cache for metadata/ego data to speed up repeated queries."""
    return functools.lru_cache(maxsize=maxsize)

# Switched to SQLite for easier local development
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./akasha.db"
)

# connect_args={"check_same_thread": False} is needed only for SQLite
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
