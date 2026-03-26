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

# Default local backend URL
API_BASE = "http://localhost:8001"
console = Console()

@click.group()
def cli():
    """🌌 Akasha Sovereign Neural Core CLI"""
    pass

@cli.command()
@click.argument('query')
@click.option('--stream', is_flag=True, help="Stream the response words")
def ask(query, stream):
    """Ask your Akasha brain a question."""
    if stream:
        url = f"{API_BASE}/query/stream"
        payload = {"query": query}
        try:
            with requests.post(url, json=payload, stream=True) as r:
                console.print(f"[bold amber]Archivist Thinking...[/bold amber]")
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
            payload = {"query": query}
            try:
                r = requests.post(url, json=payload)
                data = r.json()
                answer = data.get("answer", {}).get("answer", "No response.")
                console.print(Panel(answer, title="[bold amber]Akasha Synthesis[/bold amber]", border_style="amber"))
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}")

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

if __name__ == "__main__":
    cli()
