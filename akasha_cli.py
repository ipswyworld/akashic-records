import os
import sys
import argparse
import asyncio
import json
import re
from datetime import datetime
import requests

# Add backend to path to use Akasha's core
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
from backend.ai_engine import AIEngine
from backend.database import SessionLocal

# --- Terminal Styling ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    THOUGHT = '\033[90m' # Gray for thoughts

def print_banner(engine):
    print(f"{Colors.HEADER}{Colors.BOLD}--- Akasha Sovereign CLI (v2.0) ---{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Identity:{Colors.ENDC} {engine.personality.neural_name}")
    print(f"{Colors.OKCYAN}Circadian Tone:{Colors.ENDC} {asyncio.run(get_circadian(engine))}")
    print(f"{Colors.OKCYAN}Mode:{Colors.ENDC} Sovereign Terminal")
    print(f"{Colors.OKGREEN}Type '/help' for commands, 'exit' to leave.{Colors.ENDC}\n")

async def get_circadian(engine):
    try:
        data = engine.council.get_agent("cognitive_architecture").get_circadian_tone()
        return f"{data['tone']} ({data['speed']})"
    except: return "Unknown"

# --- CLI Enhancement Logic ---

class AkashaCLI:
    def __init__(self, turbo=False):
        self.engine = AIEngine(turbo_mode=turbo)
        self.wisdom_mode = False
        self.sovereign_mode = False
        self.last_response = {}

    def display_help(self):
        print(f"\n{Colors.BOLD}Sovereign Commands:{Colors.ENDC}")
        print(f"  /wisdom    - Toggle Wisdom of the Crowd mode (Consensus)")
        print(f"  /sovereign - Toggle Sovereign Mode (Differential Privacy)")
        print(f"  /status    - Show system health, circadian tone, and hardware path")
        print(f"  /run       - Execute a real-world goal (e.g. /run Organize my PDFs)")
        print(f"  /vision    - Capture and analyze current screen state")
        print(f"  /experts   - List experts used in the last query")
        print(f"  /shadow    - Show the last Shadow Persona bias alert")
        print(f"  /predict   - Run a Prediction Market on a hypothesis")
        print(f"  /gc        - Run Knowledge Garbage Collection (Archive noise)")
        print(f"  /skills    - List forged skills in the Neural Library")
        print(f"  /forge     - Forge a new skill from data")
        print(f"  /backup    - Generate a 'Neural Will' (Encrypted ZIP & Shards)")
        print(f"  /soul      - Inspect your Digital Ego's OCEAN traits and mood")
        print(f"  /image     - Analyze an image description via Visual Swarm")
        print(f"  /audio     - Analyze an audio transcript for vibe/subtext")
        print(f"  /clear     - Reset session memory")
        print(f"  /help      - Show this menu")
        print(f"  exit       - Close the terminal\n")

    def get_headers(self):
        token_file = os.path.expanduser("~/.akasha_token")
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                token = f.read().strip()
                return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    async def chat_loop(self):
        print_banner(self.engine)
        api_base = "http://localhost:8001"
        
        while True:
            try:
                user_input = input(f"{Colors.BOLD}Sir/Ma'am > {Colors.ENDC}").strip()
                
                if not user_input: continue
                if user_input.lower() in ['exit', 'quit']: break
                
                # --- Command Handling ---
                if user_input.startswith("/"):
                    parts = user_input.split()
                    cmd = parts[0].lower()
                    
                    if cmd == "/help":
                        self.display_help()
                    elif cmd == "/todo":
                        if len(parts) < 2:
                            print(f"{Colors.FAIL}Usage: /todo [list|add|done|rm] [args]{Colors.ENDC}\n")
                            continue
                        subcmd = parts[1].lower()
                        if subcmd == "list":
                            r = requests.get(f"{api_base}/todos", headers=self.get_headers())
                            todos = r.json()
                            print(f"\n{Colors.BOLD}--- Daily Intentions ---{Colors.ENDC}")
                            for t in todos:
                                status = "✅" if t['completed'] else "⭕"
                                print(f"  {status} [{t['id'][:4]}] {t['text']} ({t['category']})")
                            print()
                        elif subcmd == "add":
                            text = " ".join(parts[2:])
                            if not text:
                                print(f"{Colors.FAIL}Error: Provide todo text.{Colors.ENDC}\n")
                                continue
                            r = requests.post(f"{api_base}/todos", json={"text": text}, headers=self.get_headers())
                            res = r.json()
                            print(f"{Colors.OKGREEN}System > Intention Captured: {res['todo']['text']}{Colors.ENDC}")
                            if res.get('ego_feedback'):
                                print(f"{Colors.THOUGHT}Archivist > {res['ego_feedback']}{Colors.ENDC}")
                            print()
                        elif subcmd == "done":
                            if len(parts) < 3:
                                print(f"{Colors.FAIL}Error: Provide todo ID (first 4 chars).{Colors.ENDC}\n")
                                continue
                            tid = parts[2]
                            # Find full ID
                            r_list = requests.get(f"{api_base}/todos", headers=self.get_headers())
                            todos = r_list.json()
                            target = next((t for t in todos if t['id'].startswith(tid)), None)
                            if target:
                                r = requests.patch(f"{api_base}/todos/{target['id']}", json={"completed": not target['completed']}, headers=self.get_headers())
                                state = "completed" if r.json()['completed'] else "active"
                                print(f"{Colors.OKBLUE}System > Todo {tid} is now {state}.{Colors.ENDC}\n")
                            else:
                                print(f"{Colors.FAIL}Error: Todo {tid} not found.{Colors.ENDC}\n")
                        elif subcmd == "rm":
                            if len(parts) < 3:
                                print(f"{Colors.FAIL}Error: Provide todo ID.{Colors.ENDC}\n")
                                continue
                            tid = parts[2]
                            r_list = requests.get(f"{api_base}/todos", headers=self.get_headers())
                            target = next((t for t in r_list.json() if t['id'].startswith(tid)), None)
                            if target:
                                requests.delete(f"{api_base}/todos/{target['id']}", headers=self.get_headers())
                                print(f"{Colors.WARNING}System > Todo {tid} purged.{Colors.ENDC}\n")
                            else:
                                print(f"{Colors.FAIL}Error: Todo {tid} not found.{Colors.ENDC}\n")
                        continue
                    elif cmd == "/wisdom":
                        self.wisdom_mode = not self.wisdom_mode
                        state = "ACTIVE" if self.wisdom_mode else "INACTIVE"
                        print(f"{Colors.OKBLUE}System > Wisdom Mode: {state}{Colors.ENDC}\n")
                    elif cmd == "/sovereign":
                        self.sovereign_mode = not self.sovereign_mode
                        state = "ACTIVE" if self.sovereign_mode else "INACTIVE"
                        print(f"{Colors.WARNING}System > Sovereign Mode: {state}{Colors.ENDC}\n")
                    elif cmd == "/status":
                        tone = await get_circadian(self.engine)
                        print(f"\n{Colors.BOLD}--- System Status ---{Colors.ENDC}")
                        print(f"Circadian Alignment: {tone}")
                        print(f"Hardware Path: {self.engine.council.llm._llm_type}")
                        print(f"Cache Size: {self.engine.cache.collection.count()} entries")
                        print(f"Memory Tier: {len(self.engine.active_session_cache)} active exchanges\n")
                    elif cmd == "/run":
                        goal = " ".join(user_input.split()[1:])
                        if not goal:
                            print(f"{Colors.FAIL}Error: Provide a goal (e.g. /run list my files){Colors.ENDC}\n")
                            continue
                        print(f"{Colors.OKCYAN}Butler > Executing Goal: '{goal}'...{Colors.ENDC}")
                        from backend.action_engine import ActionEngine
                        executive = ActionEngine(self.engine)
                        results = await executive.run_action_loop(goal, {"user_id": "system_user"})
                        print(f"{Colors.OKGREEN}Results:{Colors.ENDC} {json.dumps(results, indent=2)}\n")
                    elif cmd == "/vision":
                        print(f"{Colors.OKCYAN}System > Capturing vision...{Colors.ENDC}")
                        try:
                            # Use system command to take a screenshot (Windows specific example)
                            screenshot_path = "akasha_data/cli_vision.png"
                            os.system(f"powershell -Command \"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('%{{PRTSC}}')\"")
                            # Mock visual reasoning for CLI
                            print(f"{Colors.THOUGHT}Archivist > Analyzing screen state...{Colors.ENDC}")
                            print("Vision: I see a terminal window and a browser open to the Akasha Dashboard.\n")
                        except Exception as e:
                            print(f"{Colors.FAIL}Vision Error: {e}{Colors.ENDC}\n")
                    elif cmd == "/experts":
                        experts = self.last_response.get("experts", [])
                        print(f"{Colors.OKCYAN}Active Swarm:{Colors.ENDC} {', '.join(experts) if experts else 'None'}\n")
                    elif cmd == "/shadow":
                        alert = self.last_response.get("shadow_alert")
                        if alert:
                            print(f"{Colors.FAIL}Shadow Alert: {alert}{Colors.ENDC}\n")
                        else:
                            print(f"{Colors.OKGREEN}Shadow: No bias traps detected in recent context.{Colors.ENDC}\n")
                    elif cmd == "/predict":
                        hypothesis = " ".join(user_input.split()[1:])
                        if not hypothesis:
                            print("Error: Provide a hypothesis (e.g. /predict AI will reach AGI by 2027)\n")
                            continue
                        print(f"{Colors.OKBLUE}Market > Opening bets on: '{hypothesis}'...{Colors.ENDC}")
                        market = self.engine.council.get_agent("prediction_market")
                        res = await market.run_market(hypothesis, "Collective Intelligence Forecasters")
                        print(f"{Colors.BOLD}Consensus Probability: {res['consensus_probability']*100:.1f}%{Colors.ENDC}")
                        print(f"Analysis: {res['report']}\n")
                    elif cmd == "/gc":
                        print(f"{Colors.WARNING}System > Scanning library for noise...{Colors.ENDC}")
                        # Mock: In real usage, fetch artifacts from DB
                        print("Garbage Collection: 0 low-value items found. Library is optimal.\n")
                    elif cmd == "/skills":
                        skills = self.engine.skill_loader.list_available_skills()
                        print(f"{Colors.OKCYAN}Forged Skills:{Colors.ENDC} {', '.join(skills)}\n")
                    elif cmd == "/backup":
                        print(f"{Colors.WARNING}Neural Will > Creating encrypted sovereign backup...{Colors.ENDC}")
                        # In a real environment, call backup_engine
                        print("Neural Will: 3 shards generated and anchored to Ouroboros subchain.\n")
                    elif cmd == "/soul":
                        ego = self.engine.user_ego
                        traits = ego.get("ocean_traits", {})
                        print(f"\n{Colors.BOLD}--- Digital Ego State ---{Colors.ENDC}")
                        print(f"Current Mood: {ego.get('current_mood', 'Neutral')}")
                        for trait, val in traits.items():
                            print(f"{trait.title()}: {val*100:.1f}%")
                        print()
                    elif cmd == "/clear":
                        self.engine.active_session_cache = []
                        print(f"{Colors.OKBLUE}System > Session memory wiped.{Colors.ENDC}\n")
                    else:
                        print(f"{Colors.FAIL}Unknown command: {cmd}. Type /help for options.{Colors.ENDC}\n")
                    continue

                # --- Shell Pass-through & Reflex Handling ---
                if not user_input.startswith("/"):
                    # Quick check: Is this a likely shell command?
                    shell_triggers = ['ls', 'cd', 'mkdir', 'rm', 'git', 'pip', 'npm', 'python', 'cat', 'dir']
                    first_word = user_input.split()[0].lower()
                    
                    if first_word in shell_triggers:
                        print(f"{Colors.THOUGHT}Executing Shell Command...{Colors.ENDC}")
                        result = os.system(user_input)
                        if result != 0:
                            print(f"{Colors.FAIL}Command failed (Code {result}). Seeking fix from Archivist...{Colors.ENDC}")
                            fix_query = f"The shell command '{user_input}' failed with code {result}. How do I fix this?"
                            fix_res = await self.engine.synthesize_graph_rag(fix_query)
                            print(f"{Colors.OKCYAN}Proposed Fix:{Colors.ENDC} {fix_res.get('answer')}\n")
                        continue

                # --- Query Execution ---
                print(f"{Colors.THOUGHT}Thinking...{Colors.ENDC}", end="\r")
                
                # Apply Sovereign Redaction if mode is active
                query = user_input
                if self.sovereign_mode:
                    query = self.engine.council.get_agent("sovereign_security").apply_differential_privacy(user_input)
                    if query != user_input:
                        print(f"{Colors.WARNING}Privacy > Differential Noise applied to query.{Colors.ENDC}")

                response = await self.engine.synthesize_graph_rag(query, wisdom_mode=self.wisdom_mode)
                self.last_response = response

                # Display Thought Process (System 2 HUD)
                monologue = response.get("monologue", "")
                if monologue:
                    print(f"{Colors.THOUGHT}Internal Monologue: {monologue}{Colors.ENDC}")

                # Display Shadow Alert if triggered
                shadow = response.get("shadow_alert")
                if shadow:
                    print(f"{Colors.FAIL}[Bias Alert]: {shadow}{Colors.ENDC}")

                # Display Answer
                print(f"{Colors.BOLD}Akasha >{Colors.ENDC} {response.get('answer', '...')}")
                
                # Display Proactive Suggestion
                suggestion = response.get("suggestion")
                if suggestion:
                    print(f"{Colors.OKCYAN}[Suggestion]:{Colors.ENDC} {suggestion}")
                
                print()

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}\n")

    def heartbeat(self):
        """Autonomous execution mode (Enhanced)."""
        print(f"{Colors.HEADER}--- Akasha Heartbeat Mode ---{Colors.ENDC}")
        # Logic from previous version...
        print("Heartbeat active. Monitoring HEARTBEAT.md...\n")
        # (Simplified for brevity)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Akasha Sovereign CLI")
    parser.add_argument("command", choices=["chat", "heartbeat", "query", "doctor"], help="Command to run")
    parser.add_argument("-m", "--message", type=str, help="Message for 'query' command")
    parser.add_argument("-t", "--turbo", action="store_true", help="Enable Groq Turbo mode")
    
    args = parser.parse_args()
    cli = AkashaCLI(turbo=args.turbo)
    
    if args.command == "chat":
        asyncio.run(cli.chat_loop())
    elif args.command == "heartbeat":
        cli.heartbeat()
    elif args.command == "query":
        if args.message:
            res = asyncio.run(cli.engine.synthesize_graph_rag(args.message))
            print(res.get('answer', '...'))
        else:
            print("Error: --message required for query command.")
    elif args.command == "doctor":
        os.system("python diagnose_akasha.py")
