import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.librarians import CouncilOfLibrarians

async def test_mutation():
    print("--- Akasha Manual Mutation Test ---")
    council = CouncilOfLibrarians()
    
    # Define a capability gap
    gap = "Add a method to the Scribe class called 'calculate_readability' that returns a Flesch Reading Ease score for a given text."
    
    print(f"Triggering evolution for: {gap}")
    result = await council.mutation_engine.evolve_system(gap)
    
    print("\n--- Mutation Result ---")
    import json
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    asyncio.run(test_mutation())
