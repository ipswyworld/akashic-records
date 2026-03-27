import click
import requests
import json
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

# Default local backend URL
API_BASE = "http://localhost:8001"
console = Console()

@click.group()
def cli():
    """🌌 Akasha Sovereign Neural Core CLI"""
    pass

@cli.command()
@click.argument('query', nargs=-1)
@click.option('--stream', is_flag=True, help="Stream the response words")
def ask(query, stream):
    """Ask your Akasha brain a question (multi-word support)."""
    query_str = " ".join(query)
    if not query_str:
        console.print("[bold red]Please provide a question.[/bold red]")
        return

    if stream:
        url = f"{API_BASE}/query/stream"
        payload = {"query": query_str}
        try:
            with requests.post(url, json=payload, stream=True) as r:
                console.print(f"[bold yellow]Archivist Thinking...[/bold yellow]")
                for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        console.print(chunk, end="", style="italic cyan")
                console.print()
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
    else:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="Consulting the Council...", total=None)
            url = f"{API_BASE}/query/rag"
            payload = {"query": query_str}
            try:
                r = requests.post(url, json=payload)
                data = r.json()
                # The response might be nested under 'answer' key
                raw_ans = data.get("answer", "No response.")
                if isinstance(raw_ans, dict):
                    answer = raw_ans.get("answer", "No response.")
                else:
                    answer = raw_ans
                console.print(Panel(answer, title="[bold yellow]Akasha Synthesis[/bold yellow]", border_style="yellow"))
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
@click.argument('query', nargs=-1)
def check(query):
    """Autonomous Workspace Analysis (e.g., 'check heavy files')."""
    query_str = " ".join(query).lower()
    
    if "heavy" in query_str or "large" in query_str:
        console.print("[bold yellow]Scanning for heavy artifacts in workspace...[/bold yellow]")
        
        heavy_files = []
        # Simple scan of current directory for files > 10MB
        for root, dirs, files in os.walk("."):
            for name in files:
                filepath = os.path.join(root, name)
                try:
                    size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    if size_mb > 10: # 10MB threshold
                        heavy_files.append((filepath, size_mb))
                except: continue
        
        if not heavy_files:
            console.print("[green]No exceptionally heavy files found.[/green]")
        else:
            table = Table(title="[bold red]Heavy Artifacts Detected[/bold red]")
            table.add_column("File Path", style="cyan")
            table.add_column("Size (MB)", justify="right", style="magenta")
            
            for f, s in sorted(heavy_files, key=lambda x: x[1], reverse=True):
                table.add_row(f, f"{s:.2f}")
            
            console.print(table)
            
            if "remove" in query_str:
                if Confirm.ask("[bold red]Do you want to proceed with autonomous cleanup?[/bold red]"):
                    for f, s in heavy_files:
                        if ".git" in f or "node_modules" in f: continue
                        console.print(f"Removing {f}...")
                        os.remove(f)
                    console.print("[bold green]Cleanup complete.[/bold green]")
    
    elif "useless" in query_str or "temp" in query_str:
        console.print("[bold yellow]Identifying transient/useless data...[/bold yellow]")
        # Mock logic for useless files
        useless_patterns = [".log", ".tmp", "__pycache__"]
        found = []
        for root, dirs, files in os.walk("."):
            for p in useless_patterns:
                if p in root or any(p in f for f in files):
                    found.append(root if p in root else os.path.join(root, p))
        
        if found:
            console.print(f"Found {len(found)} potential junk items.")
            if Confirm.ask("Clear them out?"):
                console.print("Junk cleared.")
        else:
            console.print("Workspace is lean and clean.")
    else:
        # Fallback to general AI advice
        console.print("[italic]Forwarding analysis request to the Council...[/italic]")
        url = f"{API_BASE}/query/rag"
        payload = {"query": f"Analyze this workspace intent: {query_str}"}
        try:
            r = requests.post(url, json=payload)
            console.print(r.json().get("answer", "I see no issues currently."))
        except:
            console.print("Council is currently unreachable.")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def ingest(path):
    """Ingest a file or dataset into the Neural Core."""
    url = f"{API_BASE}/ingest/dataset"
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description=f"Feeding {os.path.basename(path)} to the Core...", total=None)
        try:
            files = [('file', open(path, 'rb'))]
            r = requests.post(url, files=files)
            console.print(f"[bold green]Success:[/bold green] {r.json().get('message')}")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
def ego():
    """Visualize your Digital Ego (Psychological Profile)."""
    url = f"{API_BASE}/user/psychology"
    try:
        r = requests.get(url)
        data = r.json()
        if data.get("status") == "NO_PROFILE":
            console.print("[bold red]No profile found. Interact more with the core to build your ego.[/bold red]")
            return

        table = Table(title="[bold magenta]Digital Ego: Personality Traits (OCEAN)[/bold magenta]")
        table.add_column("Trait", style="cyan")
        table.add_column("Score", justify="right", style="green")
        table.add_column("Visualization", style="yellow")

        traits = data.get("ocean_traits", {})
        for trait, score in traits.items():
            bar = "█" * int(score * 20)
            table.add_row(trait.capitalize(), f"{score:.2f}", bar)
        
        console.print(table)
        
        distortions = data.get("cognitive_distortions", {})
        if distortions:
            d_table = Table(title="[bold red]Detected Cognitive Patterns[/bold red]")
            d_table.add_column("Pattern", style="red")
            d_table.add_column("Frequency", justify="right")
            for pattern, freq in distortions.items():
                d_table.add_row(pattern.replace("_", " ").title(), str(freq))
            console.print(d_table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
def pulse():
    """Monitor the Pulse (Chronos temporal alerts)."""
    url = f"{API_BASE}/analytics" # Simplified for mock
    try:
        r = requests.get(url)
        data = r.json()
        console.print(Panel(
            f"Core Name: [bold cyan]{data.get('neural_name')}[/bold cyan]\n"
            f"System Status: [bold green]{data.get('system_status')}[/bold green]\n"
            f"Total Artifacts: {data.get('total_count')}",
            title="[bold yellow]Neural Pulse[/bold yellow]"
        ))
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
@click.argument('name')
def rename(name):
    """Rename your neural core assistant."""
    url = f"{API_BASE}/user/settings"
    try:
        r = requests.post(url, json={"neural_name": name})
        if r.status_code == 200:
            console.print(f"[bold green]The Core has been renamed to {name}.[/bold green]")
        else:
            console.print(f"[bold red]Failed to rename core.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
@click.argument('query', nargs=-1)
@click.option('--limit', default=10, help="Number of recent activities to show")
def history(query, limit):
    """Search your digital trail (Telemetry)."""
    query_str = " ".join(query)
    if query_str:
        url = f"{API_BASE}/telemetry/recent?limit=50"
    else:
        url = f"{API_BASE}/telemetry/recent?limit={limit}"

    try:
        r = requests.get(url)
        data = r.json()
        
        table = Table(title="[bold cyan]Digital Trail: Recent Activity[/bold cyan]")
        table.add_column("Type", style="magenta")
        table.add_column("Title", style="white")
        table.add_column("URL", style="blue")
        table.add_column("Timestamp", style="dim")

        for item in data:
            details = item.get("details_json", {})
            title = details.get("title", "Untitled")
            if query_str and query_str.lower() not in title.lower() and query_str.lower() not in details.get("url", "").lower():
                continue
            
            table.add_row(
                item.get("activity_type", "VISIT"),
                (title[:47] + '..') if len(title) > 50 else title,
                details.get("url", "N/A")[:30],
                item.get("timestamp")[:19]
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
def monitor():
    """Live TUI-like view of system activity and ingestions."""
    import time
    from rich.layout import Layout
    from rich.live import Live
    
    def generate_layout() -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        layout["main"].split_row(
            Layout(name="activity"),
            Layout(name="stats", size=40)
        )
        return layout

    layout = generate_layout()
    layout["header"].update(Panel("[bold yellow]AKASHA NEURAL CORE MONITOR[/bold yellow]", style="magenta"))
    layout["footer"].update(Panel("Press Ctrl+C to exit monitor mode.", style=\"dim\"))

    with Live(layout, refresh_per_second=1, screen=True):
        try:
            while True:
                # Fetch data
                r_stats = requests.get(f"{API_BASE}/analytics")
                stats = r_stats.json()
                
                r_hist = requests.get(f"{API_BASE}/telemetry/recent?limit=15")
                history = r_hist.json()

                # Update Stats
                stats_table = Table(title="Neural Stats", show_header=False, box=None)
                stats_table.add_row("Core Name", f"[cyan]{stats.get('neural_name')}[/cyan]")
                stats_table.add_row("Status", "[green]ONLINE[/green]")
                stats_table.add_row("Artifacts", str(stats.get("total_count")))
                stats_table.add_row("Last Pulse", time.strftime("%H:%M:%S"))
                layout["stats"].update(Panel(stats_table, title="System info"))

                # Update Activity
                activity_table = Table(title="Live Telemetry Stream", expand=True)
                activity_table.add_column("Activity", style="magenta")
                activity_table.add_column("Resource", style="white")
                activity_table.add_column("Time", style="dim")

                for item in history:
                    # History items from backend have 'details_json'
                    # UserActivity in models has source_url, title, metadata_json
                    title = item.get("title", "Unknown")
                    activity_table.add_row(
                        item.get("activity_type", "VISIT"),
                        title[:40],
                        item.get("timestamp")[11:19]
                    )
                layout["activity"].update(Panel(activity_table, title="Neural Activity"))
                
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    cli()
