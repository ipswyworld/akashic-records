import click
import requests
import json
import os
import sys

# Default local backend URL
API_BASE = "http://localhost:8001"

@click.group()
def cli():
    """Akasha Sovereign Neural Core CLI"""
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
                for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        click.echo(chunk, nl=False)
                click.echo()
        except Exception as e:
            click.echo(f"Error: {e}")
    else:
        url = f"{API_BASE}/query/rag"
        payload = {"query": query}
        try:
            r = requests.post(url, json=payload)
            data = r.json()
            answer = data.get("answer", {}).get("answer", "No response.")
            click.echo(f"\n[Akasha]: {answer}\n")
        except Exception as e:
            click.echo(f"Error: {e}")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def ingest(path):
    """Ingest a file or dataset into the Neural Core."""
    url = f"{API_BASE}/ingest/dataset"
    try:
        files = [('file', open(path, 'rb'))]
        r = requests.post(url, files=files)
        click.echo(f"Status: {r.json().get('message')}")
    except Exception as e:
        click.echo(f"Error: {e}")

@cli.command()
@click.argument('scenario')
def simulate(scenario):
    """Run an OASIS swarm simulation for a 'What-If' scenario."""
    url = f"{API_BASE}/query/rag" # For now, we reuse RAG with a simulation trigger
    payload = {"query": f"Simulate this scenario: {scenario}"}
    try:
        r = requests.post(url, json=payload)
        data = r.json()
        click.echo(f"\n--- Simulation Outcome ---\n")
        click.echo(data.get("answer", {}).get("answer", "No simulation result."))
    except Exception as e:
        click.echo(f"Error: {e}")

@cli.command()
def status():
    """Check the health of the Neural Core and 10 Librarians."""
    url = f"{API_BASE}/analytics"
    try:
        r = requests.get(url)
        data = r.json()
        click.echo(f"Core Name: {data.get('neural_name')}")
        click.echo(f"Status: {data.get('system_status')}")
        click.echo(f"Total Artifacts: {data.get('total_count')}")
    except Exception as e:
        click.echo(f"Error: {e}")

if __name__ == "__main__":
    cli()
