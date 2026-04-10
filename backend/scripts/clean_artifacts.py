import os
import shutil
import logging

logger = logging.getLogger(__name__)

def clean_build_artifacts(root_dir="."):
    """
    Recursively deletes __pycache__, .pytest_cache, and rust build artifacts.
    """
    count = 0
    size_saved = 0
    
    for root, dirs, files in os.walk(root_dir):
        # 1. Python Caches
        if "__pycache__" in dirs:
            path = os.path.join(root, "__pycache__")
            size_saved += get_dir_size(path)
            shutil.rmtree(path)
            dirs.remove("__pycache__")
            count += 1
            
        if ".pytest_cache" in dirs:
            path = os.path.join(root, ".pytest_cache")
            size_saved += get_dir_size(path)
            shutil.rmtree(path)
            dirs.remove(".pytest_cache")
            count += 1

        # 2. Rust Build Artifacts
        if "target" in dirs and "Cargo.toml" in os.listdir(root):
            path = os.path.join(root, "target")
            size_saved += get_dir_size(path)
            shutil.rmtree(path)
            dirs.remove("target")
            count += 1
            
        # 3. Node Modules (Optional: only if requested, usually too heavy to delete)
        # if "node_modules" in dirs:
        #     ...
            
    print(f"Cleanup: Removed {count} artifact directories. Saved approx {size_saved / (1024*1024):.2f} MB.")

def get_dir_size(path):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total

if __name__ == "__main__":
    # If run from backend/scripts/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    clean_build_artifacts(project_root)
