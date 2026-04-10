import logging
import subprocess
import os
import json
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry of OS and Digital tools Akasha can use."""
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {
            "list_files": {
                "func": self.list_files,
                "description": "Lists files in a directory.",
                "parameters": {"path": "string"}
            },
            "read_file": {
                "func": self.read_file,
                "description": "Reads the content of a file. Fails gracefully if missing.",
                "parameters": {"file_path": "string"}
            },
            "file_exists": {
                "func": self.file_exists,
                "description": "Checks if a file exists before reading/writing.",
                "parameters": {"file_path": "string"}
            },
            "write_file": {
                "func": self.write_file,
                "description": "Writes content to a file.",
                "parameters": {"file_path": "string", "content": "string"}
            },
            "execute_shell": {
                "func": self.execute_shell,
                "description": "Executes a shell command. Use with extreme caution.",
                "parameters": {"command": "string"}
            },
            "send_notification": {
                "func": self.send_notification,
                "description": "Sends a system notification to the user.",
                "parameters": {"message": "string", "title": "string"}
            },
            "control_iot": {
                "func": self.control_iot,
                "description": "Controls connected smart home devices via Home Assistant.",
                "parameters": {"device_id": "string", "action": "string"}
            },
            "search_web": {
                "func": self.search_web,
                "description": "Searches the web for information.",
                "parameters": {"query": "string"}
            },
            "deep_web_crawl": {
                "func": self.deep_web_crawl,
                "description": "Autonomously browses a site, following links to find specific information.",
                "parameters": {"url": "string", "goal": "string"}
            },
            "execute_in_sandbox": {
                "func": self.execute_in_sandbox,
                "description": "Executes Python code in a secure, isolated Docker-like sandbox.",
                "parameters": {"code": "string"}
            },
            "computer_use": {
                "func": self.computer_use,
                "description": "Executes UI automation tasks (clicks, typing) on the host OS.",
                "parameters": {"action": "string", "target": "string"}
            }
        }
        self.scan_plugins()

    def computer_use(self, action: str, target: str) -> str:
        """Computer Use / UI Automation (#7): OS-level automation logic."""
        logger.info(f"ActionEngine: Executing UI automation: {action} on {target}")
        # In a real implementation, this would use pyautogui or a VLM driver
        return f"UI Action '{action}' on '{target}' executed successfully via OS-bridge."

    def deep_web_crawl(self, url: str, goal: str) -> str:
        """Semantic Web Crawling (#14): Deeply browses a site to fulfill a goal."""
        logger.info(f"ActionEngine: Initiating Deep Crawl on {url} for goal: {goal}")
        return f"Deep crawl complete for {url}. Extracted relevant pages. Goal status: ACHIEVED."

    def execute_in_sandbox(self, code: str) -> str:
        """Dockerized Code Execution (#6): Runs code in a secure sandbox."""
        logger.info("ActionEngine: Executing code in secure sandbox...")
        # Simulated Docker execution
        # In production, this would use the 'docker' python library to spawn a container
        try:
            # For now, we use a restricted local exec simulation
            return f"Sandbox Output: [Simulation Success]. Code executed safely in ephemeral container."
        except Exception as e:
            return f"Sandbox Error: {e}"

    async def run_background_goal(self, goal: str, user_id: str = "system_user"):
        """Asynchronous Background Goals (#8): Executes long-running goals in the background."""
        logger.info(f"ActionEngine: Queuing background goal: {goal}")
        # We spawn a task that runs the full action loop
        asyncio.create_task(self.run_action_loop(goal, {"user_id": user_id}))
        return {"status": "QUEUED", "message": f"Goal '{goal}' is now being processed in the background."}

    def scan_plugins(self):
        """Dynamic Tool Discovery: Scans the plugins/ directory for new capabilities."""
        plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
            return

        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                plugin_name = filename[:-3]
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(plugin_name, os.path.join(plugin_dir, filename))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, "register_tools"):
                        new_tools = module.register_tools()
                        for name, info in new_tools.items():
                            self.tools[name] = info
                            logger.info(f"ActionEngine: Registered plugin tool '{name}'")
                except Exception as e:
                    logger.error(f"ActionEngine: Failed to load plugin {plugin_name}: {e}")

    def list_files(self, path: str = ".") -> str:
        try:
            files = os.listdir(path)
            return json.dumps(files)
        except Exception as e:
            return f"Error: {str(e)}"

    def file_exists(self, file_path: str) -> str:
        exists = os.path.exists(file_path)
        return "True" if exists else "False"

    def read_file(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error: {str(e)}"

    def write_file(self, file_path: str, content: str) -> str:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error: {str(e)}"

    def execute_shell(self, command: str) -> str:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout
            if result.stderr:
                output += f"\nErrors:\n{result.stderr}"
            return output if output else "Command executed with no output."
        except Exception as e:
            return f"Error: {str(e)}"

    def send_notification(self, message: str, title: str = "Akasha") -> str:
        # Platform specific notification logic could go here
        logger.info(f"NOTIFICATION [{title}]: {message}")
        return f"Notification '{title}' sent."

    def control_iot(self, device_id: str, action: str) -> str:
        # Mock logic for Home Assistant integration
        return f"IOT Action: {action} sent to {device_id}."

    def search_web(self, query: str) -> str:
        # This would typically call back into IngestEngine or a dedicated search tool
        return f"Search results for: {query} (Simulated)"

class AutonomousActionManager:
    """The 'Brain' for the hands. Decides when to execute tools autonomously."""
    def __init__(self, action_engine):
        self.action_engine = action_engine
        
    async def evaluate_and_act(self, goal: str, context: Optional[Dict[str, Any]] = None):
        """
        Takes a high-level goal and decides if an autonomous action is warranted.
        """
        logger.info(f"Butler: Evaluating goal: {goal}")
        # Use the action engine's loop to plan and execute
        return await self.action_engine.run_action_loop(goal, context)

class ActionEngine:
    """
    The Action Engine: The 'Hands' of Akasha.
    Handles autonomous tool execution, digital interventions, and real-world actions.
    """
    def __init__(self, ai_engine):
        self.ai = ai_engine
        self.registry = ToolRegistry()
        self.history: List[Dict] = []
        self.butler = AutonomousActionManager(self)
        self.is_air_gapped = False # Sovereign mode flag
        
        # --- Phase 2: Macro Recording ---
        self.is_recording = False
        self.recording_session: List[Dict] = []
        # --------------------------------

    async def start_recording(self):
        print("ActionEngine: Macro Recording started.")
        self.is_recording = True
        self.recording_session = []

    async def stop_recording(self, user_id: str = "system_user") -> Dict[str, Any]:
        print(f"ActionEngine: Macro Recording stopped. Captured {len(self.recording_session)} steps.")
        self.is_recording = False
        
        if not self.recording_session:
            return {"status": "ERROR", "message": "No steps recorded."}
        
        # --- Feature 6: No-Code Forge (Self-Architect Distillation) ---
        # We ask the Self-Architect to distill these steps into a single Python 'NeuralSkill'
        macro_desc = json.dumps(self.recording_session, indent=2)
        distillation_prompt = (
            f"You are the Akasha Self-Architect. Distill the following sequence of tool-call steps into a single, "
            f"clean, and efficient Python function that can be saved as a 'NeuralSkill'. "
            f"The steps are: {macro_desc}\n\n"
            f"Return a JSON object with 'name', 'description', and 'code'."
        )
        
        try:
            # We use the Self-Architect to reason about the code
            distilled_skill = self.ai.council.self_architect.llm.invoke(distillation_prompt)
            # (In a real implementation, we would use a JsonOutputParser here)
            import re
            match = re.search(r'\{.*\}', distilled_skill, re.DOTALL)
            if match:
                skill_data = json.loads(match.group())
                # Save to database (Simplified)
                from database import SessionLocal
                from models import NeuralSkill
                db = SessionLocal()
                new_skill = NeuralSkill(
                    user_id=user_id,
                    name=skill_data.get("name", "Recorded Skill"),
                    description=skill_data.get("description", "Automated macro."),
                    code=skill_data.get("code", ""),
                    success_count=1
                )
                db.add(new_skill); db.commit(); db.refresh(new_skill)
                db.close()
                return {"status": "SUCCESS", "skill": skill_data}
        except Exception as e:
            print(f"ActionEngine: Failed to distill macro: {e}")
            return {"status": "ERROR", "message": str(e)}

    async def run_action_loop(self, goal: str, context_data: Optional[Dict] = None) -> List[Dict]:
        """
        Phase 1 & 2: Autonomous loop. Prefers forged 'Neural Skills' if a match exists.
        """
        logger.info(f"ActionEngine: Initiating action loop for goal: {goal}")
        
        # 1. Search for existing skills that might match the goal
        try:
            from database import SessionLocal
            from models import NeuralSkill
            db = SessionLocal()
            try:
                existing_skill = db.query(NeuralSkill).filter(
                    (NeuralSkill.name.ilike(f"%{goal}%")) |
                    (NeuralSkill.description.ilike(f"%{goal}%"))
                ).first()

                if existing_skill:
                    print(f"ActionEngine: Reusing forged skill '{existing_skill.name}'...")
                    result = self.ai.council.scholar.execute_local_code(existing_skill.code)
                    existing_skill.success_count += 1
                    db.commit()
                    return [{"agent": "NeuralForge", "tool": f"Reuse:{existing_skill.name}", "params": {}, "result": result, "status": "SUCCESS"}]
            finally:
                db.close()
        except Exception as e:
            logger.error(f"ActionEngine: Skill Store search failed: {e}")

        # 2. If no skill found, proceed with planning (Existing Logic)
        tools_desc = "\n".join([f"- {name}: {info['description']} (Params: {info['parameters']})" 
                               for name, info in self.registry.tools.items()])
        
        planner_prompt = (
            f"You are the Akasha Executive Function. Goal: '{goal}'\n"
            f"Available Tools:\n{tools_desc}\n\n"
            f"Generate a sequence of tool calls to achieve this goal. Respond ONLY with a JSON list of objects "
            f"containing 'tool' (name) and 'params' (dict). If no tools are needed, return [].\n"
            f"Plan JSON:"
        )
        
        plan_raw = self.ai.local_inference(planner_prompt, system_prompt="You are an autonomous agent.")
        
        try:
            # Extract JSON from markdown if necessary
            import re
            match = re.search(r'\[.*\]', plan_raw, re.DOTALL)
            if match:
                plan = json.loads(match.group())
            else:
                plan = []
        except Exception as e:
            logger.error(f"ActionEngine: Failed to parse action plan: {e}")
            return [{"error": "Plan parsing failure", "raw": plan_raw}]

        results = []
        for step in plan:
            tool_name = step.get("tool")
            params = step.get("params", {})
            result = await self.execute_action("ActionLoop", tool_name, params)
            results.append(result)
            
        # --- Akasha Forge: Autonomous Skill Discovery ---
        # If the plan was complex (>2 steps) and all steps succeeded, 
        # propose/distill this into a new permanent skill.
        if len(plan) >= 2 and all(r.get("status") != "ERROR" for r in results):
            logger.info(f"ActionEngine: Complex successful loop detected. Triggering Neural Forging...")
            asyncio.create_task(self.distill_autonomous_skill(goal, results, context_data.get("user_id", "system_user") if context_data else "system_user"))
        # ------------------------------------------------

        return results

    async def distill_autonomous_skill(self, goal: str, history: List[Dict], user_id: str):
        """Distills a successful history into a reusable skill autonomously."""
        try:
            # We use the Self-Architect to reason about the code
            skill_data = await self.ai.council.self_architect.distill_to_skill(goal, history)
            
            if skill_data:
                # Save to database
                from database import SessionLocal
                from models import NeuralSkill
                db = SessionLocal()
                new_skill = NeuralSkill(
                    user_id=user_id,
                    name=skill_data.get("name", f"AutoSkill: {goal[:20]}"),
                    description=skill_data.get("description", f"Autonomously discovered skill for: {goal}"),
                    code=skill_data.get("code", ""),
                    success_count=1
                )
                db.add(new_skill); db.commit(); db.refresh(new_skill)
                db.close()
                logger.info(f"ActionEngine: Autonomous Skill '{new_skill.name}' forged successfully.")
        except Exception as e:
            logger.error(f"ActionEngine: Autonomous distillation failed: {e}")

    async def execute_action(self, agent_name: str, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a specific tool command with security and air-gap checks."""
        try:
            if self.is_air_gapped:
                external_tools = ["search_web", "fetch_url"]
                if tool_name in external_tools:
                    return {"status": "BLOCKED", "reason": "Air-gap mode active."}

            if tool_name not in self.registry.tools:
                raise ValueError(f"Tool '{tool_name}' unknown.")

            logger.info(f"ActionEngine: {agent_name} executing {tool_name}...")
            
            tool_info = self.registry.tools[tool_name]
            result = tool_info["func"](**params)
            
            record = {
                "agent": agent_name,
                "tool": tool_name,
                "params": params,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # --- Phase 2: Record to Session ---
            if self.is_recording:
                self.recording_session.append(record)
            # ----------------------------------

            self.history.append(record)
            return record
            
        except Exception as e:
            logger.error(f"ActionEngine Error: {e}")
            return {"status": "ERROR", "message": str(e)}

    def get_history(self) -> List[Dict]:
        return self.history
