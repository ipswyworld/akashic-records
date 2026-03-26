import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from librarians import CouncilOfLibrarians

async def test_swarm():
    print("Testing Akasha-OASIS Swarm Integration...")
    
    # Initialize Council (using local model)
    council = CouncilOfLibrarians(turbo_mode=False)
    
    seed_text = (
        "Universal Basic Income (UBI) has been proposed as a solution to AI-driven job replacement. "
        "Critics argue it will cause inflation, while supporters say it will empower creative freedom."
    )
    
    print("\n1. Testing Swarm Generation...")
    # Generate a small swarm for testing
    council.swarm_director.generate_swarm(seed_text, count=5)
    print(f"Swarm Size: {len(council.swarm_director.sandbox.personas)}")
    
    print("\n2. Testing Emergent Impact Simulation (OASIS Loop)...")
    # This runs a few steps of interaction
    synthesis = await council.head_archivist.run_swarm_simulation(seed_text)
    
    print("\n--- SIMULATION SYNTHESIS ---")
    print(synthesis)
    print("--- END ---")

if __name__ == "__main__":
    asyncio.run(test_swarm())
