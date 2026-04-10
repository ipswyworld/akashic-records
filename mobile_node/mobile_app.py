import os
import sys
import time
import json
import base64
import requests
import threading
import asyncio
import websockets
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

# Configuration
API_BASE = "http://localhost:8001"
WS_URL = "ws://localhost:8001/akasha/sensory"
USER_ID = "system_user"
console = Console()

class AkashaMobileAgent:
    """The High-Agency Mobile Interface for the Akasha Neural Core."""
    def __init__(self):
        self.is_running = True
        self.history = []
        self.current_location = {"lat": 0.0, "lon": 0.0}

    def get_headers(self):
        return {"Content-Type": "application/json"}

    async def chat_loop(self):
        console.print(Panel("[bold cyan]Akasha Mobile Node Online[/bold cyan]\n[dim]Sovereign Neural Interface Initialized[/dim]", border_style="cyan"))
        
        while self.is_running:
            try:
                user_input = console.input("[bold yellow]You > [/bold yellow]").strip()
                if not user_input: continue
                if user_input.lower() in ['exit', 'quit']: break

                if user_input.startswith("/see"):
                    await self.capture_vision()
                elif user_input.startswith("/voice"):
                    await self.capture_voice()
                elif user_input.startswith("/run"):
                    await self.execute_mobile_goal(user_input[4:].strip())
                elif user_input.startswith("/todo"):
                    await self.handle_todos(user_input)
                else:
                    await self.ask_archivist(user_input)

            except KeyboardInterrupt:
                break

    async def handle_todos(self, command):
        parts = command.split()
        if len(parts) < 2:
            console.print("[yellow]Usage: /todo [list|add|done] [args][/yellow]")
            return

        subcmd = parts[1].lower()
        if subcmd == "list":
            try:
                r = requests.get(f"{API_BASE}/todos", headers=self.get_headers())
                todos = r.json()
                table = Table(title="Daily Intentions", border_style="cyan")
                table.add_column("ID", style="dim")
                table.add_column("Status", justify="center")
                table.add_column("Intention")
                table.add_column("Category", style="magenta")

                for t in todos:
                    status = "[green]✅[/green]" if t['completed'] else "[yellow]⭕[/yellow]"
                    table.add_row(t['id'][:4], status, t['text'], t['category'])
                
                console.print(table)
            except Exception as e: console.print(f"[red]Sync failed: {e}[/red]")

        elif subcmd == "add":
            text = " ".join(parts[2:])
            if not text: return
            try:
                r = requests.post(f"{API_BASE}/todos", json={"text": text}, headers=self.get_headers())
                res = r.json()
                console.print(f"[green]Captured:[/green] {res['todo']['text']}")
                if res.get('ego_feedback'):
                    console.print(f"[italic dim]Archivist: {res['ego_feedback']}[/italic dim]")
            except Exception as e: console.print(f"[red]Add failed: {e}[/red]")

        elif subcmd == "done":
            if len(parts) < 3: return
            tid = parts[2]
            try:
                r_list = requests.get(f"{API_BASE}/todos", headers=self.get_headers())
                target = next((t for t in r_list.json() if t['id'].startswith(tid)), None)
                if target:
                    r = requests.patch(f"{API_BASE}/todos/{target['id']}", json={"completed": not target['completed']}, headers=self.get_headers())
                    console.print(f"[cyan]Todo {tid} updated.[/cyan]")
                else:
                    console.print(f"[red]Todo {tid} not found.[/red]")
            except Exception as e: console.print(f"[red]Update failed: {e}[/red]")

    async def ask_archivist(self, query):
        """Standard RAG query via the mobile link."""
        console.print("[dim italic]Archivist is thinking...[/dim italic]")
        payload = {
            "query": query,
            "user_id": USER_ID,
            "context": f"Mobile Session | Location: {self.current_location}"
        }
        try:
            r = requests.post(f"{API_BASE}/query/rag", json=payload)
            data = r.json()
            answer = data.get("answer", "No response from core.")
            console.print(Panel(answer, title="[bold yellow]Archivist Response[/bold yellow]", border_style="yellow"))
        except Exception as e:
            console.print(f"[bold red]Core Connection Lost:[/bold red] {e}")

    async def capture_vision(self):
        """Simulates mobile camera capture and analysis."""
        console.print("[bold magenta]Camera > Capturing environment...[/bold magenta]")
        # In a real mobile app, this would trigger the native camera.
        # Here we use a placeholder or check if a file exists.
        img_path = "mobile_node/camera_capture.jpg"
        if not os.path.exists(img_path):
            console.print("[dim]No camera detected. Sending mock visual context...[/dim]")
            # Mock vision call
            payload = {"query": "What do you see in this mobile context?"}
            r = requests.post(f"{API_BASE}/query/rag", json=payload)
            console.print(Panel(r.json().get("answer"), title="Visual Analysis"))
        else:
            # Real image upload
            with open(img_path, "rb") as f:
                files = {"file": f}
                r = requests.post(f"{API_BASE}/vision/analyze", files=files, data={"user_id": USER_ID})
                console.print(Panel(r.json().get("description"), title="Visual Synthesis"))

    async def capture_vision(self):
        # ... (method logic as before) ...
        pass

    async def capture_voice(self, duration=5):
        """Records audio from the microphone and sends it to Akasha."""
        try:
            import sounddevice as sd
            from scipy.io.wavfile import write
            import io

            fs = 44100  # Sample rate
            console.print(f"[bold cyan]Voice HUD > Recording for {duration} seconds...[/bold cyan]")
            
            # Record
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()  # Wait until recording is finished
            
            # Save to buffer
            buffer = io.BytesIO()
            write(buffer, fs, recording)
            audio_bytes = buffer.getvalue()
            
            console.print("[dim]Transcribing speech...[/dim]")
            files = {"file": ("voice.wav", audio_bytes, "audio/wav")}
            r = requests.post(f"{API_BASE}/ingest/audio", files=files, data={"user_id": USER_ID})
            
            data = r.json()
            console.print(Panel(data.get("content", "Transcription failed."), title="Voice Transcript"))
            
            # Follow up with synthesis if there was text
            if data.get("content"):
                await self.ask_archivist(data["content"])

        except ImportError:
            console.print("[bold red]Error:[/bold red] 'sounddevice' and 'scipy' are required for Voice HUD.")
            console.print("Install them with: [bold yellow]pip install sounddevice scipy[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]Voice Error:[/bold red] {e}")

    async def execute_mobile_goal(self, goal):
        """Triggers the Butler to perform mobile-specific tasks."""
        console.print(f"[bold green]Butler > Planning mobile task: '{goal}'...[/bold green]")
        payload = {"goal": goal, "user_id": USER_ID}
        try:
            r = requests.post(f"{API_BASE}/actions/run", json=payload)
            results = r.json().get("results", "Task initiated.")
            console.print(f"[green]Status:[/green] {results}")
        except Exception as e:
            console.print(f"[red]Butler Error:[/red] {e}")

    def update_location_background(self):
        """Silently streams GPS data to the core in the background."""
        while self.is_running:
            self.current_location = {
                "lat": random.uniform(-1.28, -1.30), # Mock Nairobi area
                "lon": random.uniform(36.81, 36.83)
            }
            # Telemetry to core
            payload = {
                "type": "MOBILE_PULSE",
                "title": "Mobile Node Active",
                "url": f"geo:{self.current_location['lat']},{self.current_location['lon']}",
                "user_id": USER_ID
            }
            try: requests.post(f"{API_BASE}/telemetry", json=payload)
            except: pass
            time.sleep(60) # Pulse every minute

if __name__ == "__main__":
    agent = AkashaMobileAgent()
    
    # Start background telemetry
    threading.Thread(target=agent.update_location_background, daemon=True).start()
    
    # Run interactive UI
    asyncio.run(agent.chat_loop())
