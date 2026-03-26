import os
import json
import asyncio
import random
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

class ShadowPersona(BaseModel):
    """A dynamic, ephemeral agent seeded with psychological and contextual data."""
    id: str
    name: str
    ocean_traits: Dict[str, float]
    role: str
    background: str
    memory_context: str
    current_mood: str = "Neutral"
    
    def get_persona_prompt(self) -> str:
        traits_str = ", ".join([f"{trait}: {value:.2f}" for trait, value in self.ocean_traits.items()])
        return (
            f"You are {self.name}, a {self.role}. \n"
            f"Background: {self.background}\n"
            f"Personality (OCEAN): {traits_str}\n"
            f"Current Mood: {self.current_mood}\n"
            f"Context: {self.memory_context}\n"
            "Respond naturally, staying in character. Reflect your personality traits in your tone and decisions."
        )

class SimulationSandbox:
    """The private environment where Shadow Personas interact (OASIS Logic)."""
    def __init__(self, llm, orchestrator_llm=None):
        self.llm = llm
        self.orchestrator = orchestrator_llm or llm
        self.personas: List[ShadowPersona] = []
        self.history: List[Dict[str, Any]] = []
        self.world_state: Dict[str, Any] = {}
        
        # OASIS-style interaction chains
        self.action_chain = PromptTemplate(
            template="{persona_prompt}\n\nWorld State: {world_state}\nRecent History: {history}\n\n"
                     "You are in a parallel digital world. What is your next action? "
                     "Options: [SPEAK, OBSERVE, REFLECT, PROPOSE_CHANGE].\n"
                     "Return a JSON object with 'action' and 'content'.\nAction:",
            input_variables=["persona_prompt", "world_state", "history"]
        ) | llm | JsonOutputParser()

    def add_persona(self, persona: ShadowPersona):
        self.personas.append(persona)

    async def run_step(self):
        """Executes one 'time-step' of the simulation."""
        step_actions = []
        # For large swarms, we'd use a subset or parallelize more aggressively
        # Here we simulate the emergence by having personas react to the history
        active_personas = random.sample(self.personas, min(len(self.personas), 5))
        
        for p in active_personas:
            try:
                history_str = "\n".join([f"{h['name']}: {h['content']}" for h in self.history[-10:]])
                action = await self.action_chain.ainvoke({
                    "persona_prompt": p.get_persona_prompt(),
                    "world_state": json.dumps(self.world_state),
                    "history": history_str
                })
                
                record = {
                    "step": len(self.history),
                    "name": p.name,
                    "action": action.get("action", "REFLECT"),
                    "content": action.get("content", ""),
                    "persona_id": p.id
                }
                self.history.append(record)
                step_actions.append(record)
            except Exception as e:
                print(f"Simulation Error for {p.name}: {e}")
        
        return step_actions

    async def run_simulation(self, steps: int = 5):
        """Runs the simulation for a set number of steps and returns a synthesis."""
        for i in range(steps):
            print(f"Simulation Sandbox: Step {i+1}/{steps}...")
            await self.run_step()
            
        # Final Synthesis via Orchestrator
        synthesis_prompt = PromptTemplate(
            template="You are the Simulation Observer. Analyze the following interaction history of {count} agents "
                     "and synthesize the emergent outcomes, consensus, or conflicts.\n\nHistory:\n{history}\n\n"
                     "Synthesis (Emergent Predictions):",
            input_variables=["count", "history"]
        )
        history_summary = "\n".join([f"{h['name']} ({h['action']}): {h['content']}" for h in self.history])
        return await (synthesis_prompt | self.orchestrator | StrOutputParser()).ainvoke({
            "count": len(self.personas),
            "history": history_summary[:8000] # Cap for context limits
        })

class SwarmDirector:
    """The bridge between the static Council of Librarians and the dynamic Swarm."""
    def __init__(self, council):
        self.council = council # CouncilOfLibrarians
        self.sandbox = SimulationSandbox(council.llm, council.creative_llm)

    def generate_swarm(self, seed_context: str, count: int = 10, ocean_base: Dict[str, float] = None):
        """Generates a swarm of shadow personas based on a seed and psychological base."""
        base = ocean_base or {"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5}
        
        roles = ["Critic", "Supporter", "Innovator", "Skeptic", "Pragmatist", "Visionary", "Harmonizer", "Disruptor"]
        
        for i in range(count):
            # Vary traits slightly from base to create diversity
            traits = {k: max(0.0, min(1.0, v + random.uniform(-0.2, 0.2))) for k, v in base.items()}
            role = random.choice(roles)
            name = f"Shadow-{role}-{i}"
            
            p = ShadowPersona(
                id=str(uuid.uuid4()),
                name=name,
                ocean_traits=traits,
                role=role,
                background=f"An ephemeral shadow persona generated to explore the implications of: {seed_context[:100]}",
                memory_context=seed_context
            )
            self.sandbox.add_persona(p)
        
        print(f"SwarmDirector: Generated {count} shadow personas.")

    async def run_impact_simulation(self, artifact_text: str, user_psychology: Dict[str, float] = None):
        """
        Runs a simulation to predict the impact of an artifact on the user's worldview.
        This is the OASIS equivalent of MCTS research paths.
        """
        self.generate_swarm(artifact_text, count=12, ocean_base=user_psychology)
        self.sandbox.world_state = {"seed_artifact": artifact_text[:500]}
        
        print("SwarmDirector: Running Emergent Impact Simulation...")
        synthesis = await self.sandbox.run_simulation(steps=3)
        return synthesis
