import shutil
import psutil
import os
import json
import socket
from datetime import datetime

def check_health():
    # 1. Disk Space
    total, used, free = shutil.disk_usage("/")
    disk_usage = (used / total) * 100
    
    # 2. RAM Usage
    memory = psutil.virtual_memory()
    
    # 3. Process Check (FastAPI, Chromadb, etc.)
    pids = psutil.pids()
    akasha_process_alive = any("uvicorn" in (p.name() if hasattr(p, 'name') else "") for p in [psutil.Process(pid) for pid in pids[:100]]) # Simplified check
    
    # 4. Network Status
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        online = True
    except OSError:
        online = False
        
    health_data = {
        "timestamp": datetime.now().isoformat(),
        "disk_usage_percent": round(disk_usage, 2),
        "memory_usage_percent": memory.percent,
        "online_status": online,
        "system_load": psutil.cpu_percent(interval=1),
        "status": "HEALTHY" if disk_usage < 90 and memory.percent < 95 else "CRITICAL"
    }
    
    health_log = "akasha_data/system_user/health_history.json"
    history = []
    if os.path.exists(health_log):
        with open(health_log, "r") as f:
            try:
                history = json.load(f)
            except: pass
            
    history.append(health_data)
    # Keep last 100 entries
    history = history[-100:]
    
    with open(health_log, "w") as f:
        json.dump(history, f, indent=2)
        
    print(f"Health Check complete: {health_data['status']} (Disk: {health_data['disk_usage_percent']}%, RAM: {health_data['memory_usage_percent']}%)")
    return health_data

if __name__ == "__main__":
    check_health()
