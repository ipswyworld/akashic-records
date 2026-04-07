import click
import requests
import json
import os
import sys
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

# Add backend to path if needed for local logic pass-through
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Default local backend URL
API_BASE = "http://localhost:8001"
TOKEN_FILE = os.path.expanduser("~/.akasha_token")
console = Console()

def get_headers():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            token = f.read().strip()
            return {"Authorization": f"Bearer {token}"}
    return {"Authorization": "Bearer null"} # Default for dormant auth

@click.group()
def cli():
    """🌌 Akasha Sovereign Neural Core CLI"""
    pass

@cli.command()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def login(username, password):
    """Authenticate with the Neural Core."""
    url = f"{API_BASE}/auth/login"
    try:
        r = requests.post(url, data={"username": username, "password": password})
        if r.status_code == 200:
            token = r.json().get("access_token")
            with open(TOKEN_FILE, 'w') as f:
                f.write(token)
            console.print("[bold green]Authenticated successfully.[/bold green]")
        else:
            console.print(f"[bold red]Login failed:[/bold red] {r.text}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
@click.argument('query', nargs=-1)
def ask(query):
    """Ask your Akasha brain a question."""
    query_str = " ".join(query)
    if not query_str:
        console.print("[bold red]Please provide a question.[/bold red]")
        return

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="Consulting the Council...", total=None)
        url = f"{API_BASE}/query/rag"
        payload = {"query": query_str}
        try:
            r = requests.post(url, json=payload, headers=get_headers())
            data = r.json()
            answer = data.get("answer", "No response.")
            if isinstance(answer, dict): answer = answer.get("answer", str(answer))
            console.print(Panel(answer, title="[bold yellow]Akasha Synthesis[/bold yellow]", border_style="yellow"))
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
@click.argument('goal', nargs=-1)
def run(goal):
    """Execute a real-world goal (Autonomous Computer Use)."""
    goal_str = " ".join(goal)
    if not goal_str:
        console.print("[bold red]Please provide a goal.[/bold red]")
        return

    console.print(f"[bold cyan]Butler > Planning and executing: '{goal_str}'...[/bold cyan]")
    url = f"{API_BASE}/query/rag" # For now we route through RAG which triggers ActionEngine if logic allows
    # Better: Direct action endpoint
    url_action = f"{API_BASE}/actions/history" # Mock/Placeholder for direct action trigger
    
    # We use the smarter synthesis loop which should trigger the butler
    payload = {"query": f"Goal: {goal_str}. Use your tools to execute this."}
    try:
        r = requests.post(f"{API_BASE}/query/rag", json=payload, headers=get_headers())
        data = r.json()
        console.print(Panel(data.get("answer", "Goal processing initiated."), title="[bold green]Executive Result[/bold green]"))
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
def vision():
    """Capture and analyze the current screen state."""
    console.print("[bold cyan]System > Capturing vision...[/bold cyan]")
    url = f"{API_BASE}/eye/pulse"
    try:
        r = requests.get(url, headers=get_headers())
        data = r.json()
        console.print(Panel(data.get("analysis", "Vision capture failed."), title="[bold magenta]Visual Analysis[/bold magenta]"))
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def ingest(path):
    """Ingest a file, folder, or dataset into the Neural Core."""
    if os.path.isdir(path):
        console.print(f"[bold yellow]Ingesting directory: {path}[/bold yellow]")
        for root, dirs, files in os.walk(path):
            for name in files:
                file_path = os.path.join(root, name)
                ingest_file(file_path)
    else:
        ingest_file(path)

def ingest_file(file_path):
    url = f"{API_BASE}/ingest/dataset"
    console.print(f"[dim]Feeding {os.path.basename(file_path)}...[/dim]")
    try:
        with open(file_path, 'rb') as f:
            files = [('file', f)]
            r = requests.post(url, files=files, headers=get_headers())
            if r.status_code != 200:
                console.print(f"[red]Failed to ingest {file_path}[/red]")
    except Exception as e:
        console.print(f"[red]Error ingesting {file_path}: {e}[/red]")

@cli.command()
def ego():
    """Visualize your Digital Ego (Psychological Profile)."""
    url = f"{API_BASE}/user/psychology"
    try:
        r = requests.get(url, headers=get_headers())
        data = r.json()
        table = Table(title="[bold magenta]Digital Ego State[/bold magenta]")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Mood", data.get("current_mood", "Neutral"))
        traits = data.get("ocean_traits", {})
        for t, v in traits.items():
            table.add_row(t.capitalize(), f"{v*100:.1f}%")
        
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
def pulse():
    """Monitor system health and temporal alerts."""
    url = f"{API_BASE}/analytics"
    try:
        r = requests.get(url, headers=get_headers())
        data = r.json()
        console.print(Panel(
            f"Core Name: [bold cyan]{data.get('neural_name')}[/bold cyan]\n"
            f"Status: [bold green]{data.get('system_status')}[/bold green]\n"
            f"Artifacts Indexed: {data.get('total_count')}",
            title="[bold yellow]Neural Pulse[/bold yellow]"
        ))
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
@click.argument('agent_name', default="Economist")
@click.argument('folder_path', default="chronojanus")
def train(agent_name, folder_path):
    """Universal Specialist Training: Point a librarian at any dataset."""
    url = f"{API_BASE}/user/training/specialize"
    console.print(f"[bold yellow]Initiating {agent_name} specialization on '{folder_path}'...[/bold yellow]")
    try:
        payload = {"agent_name": agent_name, "folder_path": folder_path}
        r = requests.post(url, json=payload, headers=get_headers())
        data = r.json()
        if data.get("status") == "TRAINING_STARTED":
            console.print(f"[bold green]Success:[/bold green] {data.get('message')}")
        else:
            console.print(f"[bold red]Failed:[/bold red] {data.get('message')}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    cli()
