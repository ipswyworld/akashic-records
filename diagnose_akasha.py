import shutil
import requests
import os
import sqlite3
import subprocess

def check_hardware():
    print("\n--- Hardware Doctor ---")
    try:
        import torch
        if torch.cuda.is_available():
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            vram_gb = vram_bytes / (1024**3)
            print(f"✅ GPU: Found ({torch.cuda.get_device_name(0)})")
            print(f"✅ VRAM: {vram_gb:.2f} GB")
            if vram_gb > 16:
                print("   ➡️  Recommendation: vLLM Backend (High VRAM)")
            elif vram_gb > 6:
                print("   ➡️  Recommendation: Ollama / llama.cpp (Mid VRAM)")
            else:
                print("   ➡️  Recommendation: llama.cpp CPU/Quantized (Low VRAM)")
        elif torch.backends.mps.is_available():
            print("✅ GPU: Found (Apple Silicon MPS)")
            print("   ➡️  Recommendation: llama.cpp (Metal)")
        else:
            print("⚠️ GPU: Not Found (CPU Only)")
            print("   ➡️  Recommendation: llama.cpp (CPU/Quantized)")
    except ImportError:
        print("⚠️ PyTorch not installed. Hardware detection limited.")
        if shutil.which("nvidia-smi"):
            print("✅ GPU: NVIDIA driver found, but PyTorch cannot access it.")
        else:
            print("⚠️ GPU: Not detected.")

def check_ffmpeg():
    if shutil.which("ffmpeg"):
        print("✅ FFMPEG: Found")
    else:
        print("❌ FFMPEG: NOT FOUND (Voice features will fail)")

def check_ollama():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200:
            models = [m['name'] for m in r.json().get('models', [])]
            print(f"✅ OLLAMA: Online (Models: {', '.join(models)})")
            if 'tinyllama:latest' not in models and 'llama3:latest' not in models:
                print("   ⚠️  Warning: Recommended models (tinyllama, llama3) not found. Run 'ollama pull tinyllama'.")
        else:
            print("❌ OLLAMA: Server responded with error")
    except:
        print("❌ OLLAMA: Server unreachable at http://localhost:11434")

def check_db():
    db_path = "backend/akasha.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            print(f"✅ DATABASE: Found and reachable at {db_path}")
            conn.close()
        except:
            print("❌ DATABASE: Corruption or lock detected")
    else:
        print("❌ DATABASE: Not found. Will be created on first run.")

def check_rust_mesh():
    binary = "backend/rust_p2p/target/debug/akasha-p2p.exe" if os.name == 'nt' else "backend/rust_p2p/target/debug/akasha-p2p"
    if os.path.exists(binary):
        print(f"✅ RUST MESH: Binary found at {binary}")
    else:
        print("❌ RUST MESH: Binary missing. Run 'cargo build' in backend/rust_p2p")

if __name__ == "__main__":
    print("\n--- Akasha Neural Core Diagnostics ---\n")
    check_hardware()
    check_ffmpeg()
    check_ollama()
    check_db()
    check_rust_mesh()
    print("\n--------------------------------------\n")
