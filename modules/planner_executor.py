"""
planner_executor.py — Dual-Role Orchestration Layer for Jarvis

Contains:
1. StatelessPlanner: Decomposes a user prompt into a structured JSON array of tasks.
2. TaskExecutor: Sequentially executes tasks via Jarvis's existing agentic sandbox.
3. Orchestrator Entrypoint: Wires the two together for the CLI.
"""

import json
import logging
import sys
from typing import List, Dict, Any

from core.registry import ServiceRegistry
import config

logger = logging.getLogger(__name__)

class StatelessPlanner:
    def __init__(self, brain):
        """
        Stateless Planner role that uses the core AI Brain.
        """
        self.brain = brain

    def plan(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Decomposes the goal into a structured JSON array of discrete, sequential tasks.
        Validates the schema and retries once upon failure.
        """
        system_prompt = (
            "You are the Jarvis Planning Orchestrator.\n"
            "Your sole job is to break down the user's goal into a precise, sequential task list.\n"
            "You MUST output exactly valid JSON in the form of an array of objects.\n"
            "Do not include any chat filler, markdown blocks, or other text outside the JSON array.\n\n"
            "DEVELOPER-FIRST DIRECTIVE (ZERO-PLAYBOOK POLICY FOR CODE):\n"
            "If a task involves scraping, data analysis, math, financial formatting, or hitting a known API, "
            "do NOT waste steps searching for 'expert playbooks' or learning how to do it. You are a Senior Python Developer.\n"
            "You MUST NEVER generate steps involving 'search_awesome_skills' or 'fetch_skill_playbook' "
            "if the task is solvable via a custom Python script. "
            "Just formulate a plan that writes a Python script immediately. Consolidate your plan: Step 1 should usually be "
            "'Write and execute a Python script to do X'.\n\n"
            "FINANCIAL PRECISION PROTOCOL:\n"
            "When the goal involves market data (prices, % change, volatility), ALWAYS include a step to "
            "'Identify and verify the data calculation methodology (e.g., Rolling 24-hour vs. UTC Daily Open)' "
            "to ensure cross-source consistency.\n\n"
            "Schema for each object:\n"
            "[\n"
            "  {\n"
            '    "step": <integer>,\n'
            '    "title": "<string> (short title)",\n'
            '    "description": "<string> (highly detailed actionable instruction)",\n'
            '    "skill_hint": "<string> (name of tool you recommend, or null)"\n'
            "  }\n"
            "]"
        )
        
        user_prompt = f"Goal: {prompt}\nDecompose this into a JSON array of tasks."
        
        for attempt in range(2):
            try:
                # The Planner uses brain.ask directly for a zero-shot structured run
                raw_response = self.brain.ask(user_prompt, system_prompt=system_prompt, is_agentic=False)
                if not raw_response:
                    raise ValueError("Empty response received from LLM.")
                    
                # Clean up potential markdown code block formatting
                cleaned = raw_response.strip()
                if cleaned.startswith("```"):
                    lines = cleaned.split("\n")
                    if lines[0].startswith("```"): lines = lines[1:]
                    if lines[-1].startswith("```"): lines = lines[:-1]
                    cleaned = "\n".join(lines).strip()
                    
                data = json.loads(cleaned)
                
                # Validation rules mapping to schema constraints
                if not isinstance(data, list):
                    raise ValueError("Root element must be a JSON array.")
                    
                for step_obj in data:
                    for key in ("step", "title", "description", "skill_hint"):
                        if key not in step_obj:
                            raise ValueError(f"Missing required key '{key}' in task: {step_obj}")
                            
                return data

            except json.JSONDecodeError as decode_err:
                err_msg = f"JSON Decode Error: {decode_err}"
                if attempt == 1:
                    raise RuntimeError(f"Planner failed to generate valid JSON after 2 attempts. {err_msg}\nResponse:\n{raw_response}")
                logger.warning(f"Planner JSON parsing failed on attempt 1. Retrying... ({err_msg})")
                
            except Exception as e:
                if attempt == 1:
                    raise RuntimeError(f"Planner execution failed: {str(e)}")
                logger.warning(f"Planner error on attempt 1. Retrying... ({str(e)})")
                
        return []

class TaskExecutor:
    def __init__(self, registry):
        """
        Executor role that routes individual tasks through the existing AgentCore.
        """
        self.registry = registry

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accepts a single task, instantiates a fresh AgentCore context to keep
        the context window minimal, and runs the task to completion sequentially.
        """
        from modules.agent_core import AgentCore
        
        # Instantiate a freshly isolated execution instance for this single task chunk
        agent_cfg = config.AgentConfig(
            enabled=True,
            max_iterations=getattr(config, "AGENTIC_MAX_ITERATIONS", 30),
            timeout=getattr(config, "AGENTIC_TIMEOUT_SECONDS", 120),
            retry_budget=getattr(config, "TOOL_CALL_MAX_RETRIES", 2)
        )
        
        # We spawn a fresh agent core! This guarantees history is tiny and completely isolated
        agent = AgentCore(registry=self.registry, config=agent_cfg)
        
        task_desc = f"Task Title: {task['title']}\nInstructions: {task['description']}"
        if task.get('skill_hint'):
            task_desc += f"\nRecommended Tool: {task['skill_hint']}"
            
        try:
            # We proxy this perfectly through the existing ReAct sandbox architecture
            output = agent.run(task_desc)
            
            # Determine success based on the typical error signatures that AgentCore's exception catcher emits
            status = "success"
            error = None
            if output and ("I've hit my planning limit" in output or "An error occurred in my agentic core" in output):
                status = "failed"
                error = output
                
            return {
                "step": task["step"],
                "status": status,
                "output": output,
                "error": error
            }
        except Exception as e:
             return {
                 "step": task["step"],
                 "status": "failed",
                 "output": "",
                 "error": str(e)
             }

def execute_split_plan(prompt: str, registry, logger_instance=None):
    """
    Programmatic entry point for the Planner-Executor system.
    Includes heartbeat integration and resilient step execution.
    Partial results from each step are forwarded to the next.
    """
    brain = registry.get("brain")
    if not brain:
        return "Error: Brain not found in registry."

    # Heartbeat emitter for live UI updates
    try:
        from modules.heartbeat import HeartbeatEmitter
        hud = registry.get("hud")
        socket_server = registry.get("socket_server")
        heartbeat = HeartbeatEmitter(hud_queue=hud, socket_server=socket_server)
    except Exception:
        heartbeat = None

    planner = StatelessPlanner(brain=brain)
    executor = TaskExecutor(registry=registry)

    # Bypass planning entirely for trivial/short tasks (< 8 words)
    word_count = len(prompt.split())
    if word_count < 8 and "\n" not in prompt:
        if heartbeat:
            heartbeat.emit("Direct Execution...", "active")
        tasks = [{
            "step": 1,
            "title": "Direct Execution",
            "description": prompt,
            "skill_hint": None
        }]
    else:
        try:
            if heartbeat:
                heartbeat.emit("Planning tasks...", "active")
            tasks = planner.plan(prompt)
        except Exception as e:
            if heartbeat:
                heartbeat.emit("Planning failed", "failed")
            return f"Planning Error: {str(e)}"

    if not tasks:
        return "Error: Planner returned no tasks."

    if heartbeat:
        heartbeat.set_total_steps(len(tasks))

    results = {}
    failed_steps = set()
    final_output = ""

    for i, task in enumerate(tasks):
        step_num = task.get("step", i + 1)
        step_label = f"Step {step_num}/{len(tasks)}: {task['title']}"

        if heartbeat:
            heartbeat.step_start(step_label, step_index=i)

        # Cross-step context injection: append output of previous step if chained
        task_with_context = dict(task)
        if results and final_output:
            prev_output_preview = final_output[:500]
            task_with_context["description"] = (
                f"{task['description']}\n\n"
                f"[PREVIOUS STEP OUTPUT]: {prev_output_preview}"
            )

        result = executor.execute(task_with_context)
        results[step_num] = result

        if result["status"] == "success":
            final_output = result["output"] or ""
            if heartbeat:
                heartbeat.step_complete(step_label, success=True)
        else:
            failed_steps.add(step_num)
            logger.warning(f"⚠️ Step {step_num} failed: {result['error']}")
            if heartbeat:
                heartbeat.step_complete(step_label, success=False)
            # Continue to next step unless it depends on this one

    if heartbeat:
        heartbeat.clear()

    # Build summary
    completed = len(tasks) - len(failed_steps)
    if failed_steps:
        failed_info = f" ({len(failed_steps)} step(s) skipped)"
    else:
        failed_info = ""

    logger.info(f"✅ Planner-Executor: {completed}/{len(tasks)} steps completed{failed_info}")
    return final_output if final_output else f"Completed {completed}/{len(tasks)} steps{failed_info}."


def run_planner_executor_cli(prompt: str):
    """
    Orchestrator Entrypoint designed for CLI execution.
    Boots minimal core systems without HUD and wires the Planner to the Executor sequentially.
    """
    import queue
    from jarvis import JarvisApp
    
    print("\n" + "="*60)
    print("🤖 Jarvis Planner–Executor Orchestration Initiated")
    print("="*60 + "\n")
    
    print("[1/4] Booting core subsystems (without HUD)...")
    hud_q = queue.Queue()
    app = JarvisApp(hud_queue=hud_q)
    
    # We suppress terminal logs internally just for subsystem boot aesthetics
    logging.getLogger().setLevel(logging.ERROR)
    try:
        app.initialize_systems()
    except Exception as e:
        print(f"❌ Core boot error: {e}")
        sys.exit(1)
    finally:
        # Restore logging level to what config mandates so executor works correctly
        logging.getLogger().setLevel(logging.INFO)
    
    brain = ServiceRegistry.get("brain")
    if not brain:
        print("❌ CRITICAL: AI Brain failed to load from registry.")
        sys.exit(1)
        
    planner = StatelessPlanner(brain=brain)
    executor = TaskExecutor(registry=ServiceRegistry)
    
    print(f"\n[2/4] Planning discrete tasks for: '{prompt}'...")
    try:
        tasks = planner.plan(prompt)
    except Exception as plan_err:
        print(f"\n❌ Planning Phase Failed:\n{plan_err}")
        sys.exit(1)
        
    if not tasks:
        print("\n❌ Planner returned an empty task list.")
        sys.exit(1)
        
    print(f"\n✅ Plan finalized! Extracting {len(tasks)} sequential tasks:")
    for t in tasks:
        hint_str = f" (Hint: {t['skill_hint']})" if t.get('skill_hint') else ""
        print(f"  [{t['step']}] {t['title']}{hint_str}")
        
    print("\n[3/4] Execution Phase Beginning...\n" + "-"*60)
    
    for task in tasks:
        print(f"\n▶️ STEP {task['step']}: {task['title']}")
        print(f"   Context: {task['description']}\n   Working...")
        
        result = executor.execute(task)
        
        if result["status"] == "success":
            print(f"\n✅ Step {task['step']} Success")
            print(f"   Agent Output:\n   {result['output']}")
            print("-" * 60)
        else:
            print(f"\n❌ Step {task['step']} Failed!")
            print(f"   Error Details: {result['error']}")
            print("\n⏸️ Execution Halt: Proceeding with sequential failure safeguard surface.")
            sys.exit(1)
            
    print("\n[4/4] 🎉 All planned steps completed successfully.")
