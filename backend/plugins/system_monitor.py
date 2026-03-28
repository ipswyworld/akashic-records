import os
import psutil
import platform
import json
from datetime import datetime

def get_system_health():
    """Returns a summary of CPU, RAM, and Battery health."""
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    battery = psutil.sensors_battery()
    
    health = {
        "cpu_load": f"{cpu_usage}%",
        "ram_used": f"{ram.percent}%",
        "ram_available": f"{ram.available // (1024*1024)} MB",
        "battery": f"{battery.percent}%" if battery else "N/A",
        "os": platform.system(),
        "status": "OPTIMAL" if cpu_usage < 80 else "HIGH_LOAD"
    }
    return json.dumps(health)

def get_disk_usage(path="/"):
    """Checks disk space for a given path."""
    try:
        usage = psutil.disk_usage(path)
        return json.dumps({
            "total": f"{usage.total // (1024*1024*1024)} GB",
            "used": f"{usage.used // (1024*1024*1024)} GB",
            "free": f"{usage.free // (1024*1024*1024)} GB",
            "percent": f"{usage.percent}%"
        })
    except Exception as e:
        return f"Error: {str(e)}"

def register_tools():
    """Interface for Akasha ActionEngine."""
    return {
        "get_system_health": {
            "func": get_system_health,
            "description": "Returns real-time CPU, RAM, and Battery health statistics.",
            "parameters": {}
        },
        "get_disk_usage": {
            "func": get_disk_usage,
            "description": "Checks available disk space.",
            "parameters": {"path": "string"}
        }
    }
