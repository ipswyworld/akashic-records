import os
import sys
import shutil
from pathlib import Path
from alembic.config import Config
from alembic import command

import subprocess

REQUIRED_DIRECTORIES = [
    "akasha_data/system_user",
    "akasha_data/watch",
    "akasha_data/redundancy",
    "akasha_data/sovereign_vault",
    "chroma_db",
    "plugins"
]

def install_dependencies(base_path: Path):
    print("📦 Installing dependencies with uv...")
    req_path = base_path / "requirements.txt"
    if req_path.exists():
        try:
            if shutil.which("uv"):
                subprocess.run(["uv", "pip", "install", "-r", str(req_path)], check=True)
                print("✅ Dependencies installed via uv.")
            else:
                print("⚠️  'uv' not found. Falling back to standard pip...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_path)], check=True)
                print("✅ Dependencies installed via pip.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Dependency installation failed: {e}")
    else:
        print("⚠️  requirements.txt not found. Skipping dependency installation.")

def run_migrations():
    print("🔄 Checking for database migrations...")
    base_path = Path(__file__).parent
    alembic_cfg = Config(base_path / "alembic.ini")
    # Point alembic to the version directory relative to project root
    alembic_cfg.set_main_option("script_location", str(base_path / "alembic"))
    try:
        command.upgrade(alembic_cfg, "head")
        print("✅ Database is up to date.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

def bootstrap_environment():
    print("🚀 Initializing Akasha Environment...")
    
    base_path = Path(__file__).parent
    
    # 0. Install Dependencies
    install_dependencies(base_path)
    
    # 1. Create missing directories
    for dir_path in REQUIRED_DIRECTORIES:
        full_path = base_path / dir_path
        if not full_path.exists():
            print(f"Creating directory: {dir_path}")
            full_path.mkdir(parents=True, exist_ok=True)
            
    # 2. Ensure .env exists
    env_path = base_path / ".env"
    example_env_path = base_path.parent / ".env.example"
    
    if not env_path.exists():
        if example_env_path.exists():
            print("Copying .env.example to .env...")
            shutil.copy(example_env_path, env_path)
        else:
            print("Warning: .env and .env.example not found. Creating empty .env...")
            env_path.touch()

    # 3. Verify database path
    db_path = base_path / "akasha.db"
    if not db_path.exists():
        print("Database not found. It will be initialized by the Neural Core on startup.")

    # 4. Run Migrations
    run_migrations()

    print("✅ Environment bootstrap complete.\n")

if __name__ == "__main__":
    bootstrap_environment()
