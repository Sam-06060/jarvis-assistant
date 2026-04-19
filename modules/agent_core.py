"""
agent_core.py — Jarvis Agentic Engine v2.0

Complete rewrite of the ReAct orchestration loop with:
  - SessionState: per-task command history with deduplication & success tracking
  - Strict execution guards: check-before-act, 3-retry cap, one-shot execution
  - HeartbeatEmitter: real-time contextual status streaming to Swift UI
  - Anti-hallucination: grounded execution via verified session state injection
  - Improved iteration prompts with explicit success/failure signal parsing
"""

import json
import hashlib
import os
import re
import shutil
import time
import uuid
import logging
import config
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Set

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Data Models
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Thought:
    reasoning: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None


@dataclass
class Observation:
    tool: str
    result: str
    success: bool


@dataclass
class CommandRecord:
    """Record of a single tool execution for deduplication and history."""
    tool: str
    input_hash: str
    raw_input: Dict[str, Any]
    result: str
    success: bool
    timestamp: float = field(default_factory=time.time)


class SessionState:
    """
    Per-task state object that grounds all agent actions in real, verified results.
    Replaces implicit LLM memory with explicit stdout/stderr tracking.
    """

    def __init__(self):
        self.command_history: List[CommandRecord] = []
        self.retry_counts: Dict[str, int] = {}   # key: "step_{index}" → count
        self._executed_hashes: Set[str] = set()   # fast dedup lookup

    @staticmethod
    def _hash_action(tool: str, action_input: Dict[str, Any]) -> str:
        """Deterministic hash of (tool_name + sorted_json(input))."""
        raw = f"{tool}::{json.dumps(action_input, sort_keys=True, default=str)}"
        return hashlib.md5(raw.encode()).hexdigest()

    def was_already_executed(self, tool: str, action_input: Dict[str, Any]) -> Optional[CommandRecord]:
        """Check if this exact action was already executed. Returns the previous record or None."""
        h = self._hash_action(tool, action_input)
        if h in self._executed_hashes:
            for record in reversed(self.command_history):
                if record.input_hash == h:
                    return record
        return None

    def record_execution(self, tool: str, action_input: Dict[str, Any],
                         result: str, success: bool):
        """Record an execution in the session state."""
        h = self._hash_action(tool, action_input)
        record = CommandRecord(
            tool=tool,
            input_hash=h,
            raw_input=action_input,
            result=result,
            success=success,
        )
        self.command_history.append(record)
        self._executed_hashes.add(h)

    def get_retry_count(self, step_key: str) -> int:
        return self.retry_counts.get(step_key, 0)

    def increment_retry(self, step_key: str) -> int:
        self.retry_counts[step_key] = self.retry_counts.get(step_key, 0) + 1
        return self.retry_counts[step_key]

    def get_verified_results_summary(self, max_entries: int = 8) -> str:
        """
        Build a VERIFIED SESSION STATE block from real execution results.
        This replaces LLM memory — the agent must use this, not hallucinate.
        """
        if not self.command_history:
            return ""

        lines = ["### VERIFIED SESSION STATE (use ONLY this data, do not assume results):"]
        recent = self.command_history[-max_entries:]
        for i, rec in enumerate(recent):
            status = "✅ SUCCESS" if rec.success else "❌ FAILED"
            # Truncate long results for context budget
            result_preview = rec.result[:500] if len(rec.result) > 500 else rec.result
            lines.append(f"  Step {i+1} [{rec.tool}] {status}: {result_preview}")

        return "\n".join(lines)

    def get_failed_commands_summary(self) -> str:
        """Get a summary of failed commands to prevent repetition."""
        failed = [r for r in self.command_history if not r.success]
        if not failed:
            return ""

        lines = ["### ⚠️ PREVIOUSLY FAILED (DO NOT RETRY identical commands):"]
        for r in failed[-5:]:  # Last 5 failures
            input_preview = json.dumps(r.raw_input, default=str)[:200]
            lines.append(f"  - {r.tool}({input_preview}) → {r.result[:200]}")
        return "\n".join(lines)


class AgentMaxIterationsError(Exception):
    """Raised when the agent exceeds the configured maximum iterations."""
    pass


# ──────────────────────────────────────────────────────────────────────────────
# Success/Failure Detection
# ──────────────────────────────────────────────────────────────────────────────

_SUCCESS_SIGNALS = [
    "✅", "successfully", "success", "written", "saved", "completed",
    "executed successfully", "sent successfully", "file created",
    "command executed successfully", "exit code 0",
]

_FAILURE_SIGNALS = [
    "error:", "traceback", "not found", "failed", "exception",
    "permission denied", "command not found", "no such file",
    "modulenotfounderror", "syntaxerror", "connection refused",
    "timeout", "rejected", "critical error",
]


def detect_success(result: str) -> Optional[bool]:
    """
    Parse tool output for success/failure signals.
    Returns True (success), False (failure), or None (ambiguous).
    """
    lower = result.lower()

    # Explicit failure patterns
    for sig in _FAILURE_SIGNALS:
        if sig in lower:
            return False

    # Explicit success patterns
    for sig in _SUCCESS_SIGNALS:
        if sig in lower:
            return True

    # Ambiguous — return None
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Agent Core
# ──────────────────────────────────────────────────────────────────────────────

class AgentCore:
    def __init__(self, registry, config: config.AgentConfig):
        self.registry = registry
        self.config = config
        self.brain = registry.get("brain")
        self.hud = registry.get("hud")

        # Phase 2: Intelligence components
        provider = getattr(config, "llm_provider", None) or getattr(
            __import__("config"), "AGENTIC_LLM_PROVIDER", "groq"
        )
        from modules.token_budget import TokenBudget
        from modules.context_compressor import ContextCompressor
        from modules.observation_assessor import ObservationAssessor
        self.token_budget = TokenBudget(provider=provider)
        self.compressor = ContextCompressor(brain=self.brain)
        self.assessor = ObservationAssessor()
        self.task_id: str = ""

        # Heartbeat emitter (real-time status to Swift UI)
        from modules.heartbeat import HeartbeatEmitter
        socket_server = registry.get("socket_server")
        self.heartbeat = HeartbeatEmitter(
            hud_queue=self.hud,
            socket_server=socket_server,
        )

        # Phase 4: TaskPlanner
        try:
            from modules.planner import TaskPlanner
            skill_registry = registry.get("skill_registry")
            self.planner = TaskPlanner(brain=self.brain, skill_registry=skill_registry)
        except Exception as _pe:
            logger.warning(f"⚠️ TaskPlanner not available: {_pe}")
            self.planner = None

        # Phase 5: Semantic Router — non-blocking background boot
        try:
            import os
            import config as global_config
            from modules.semantic_router import SemanticRouter
            _registry_path = os.path.join(global_config.ROOT_DIR, "modules", "agent_skills", "_registry.json")
            SemanticRouter.instance().boot(_registry_path)
        except Exception as _se:
            logger.warning(f"⚠️ SemanticRouter boot skipped: {_se}")

    # ──────────────────────────────────────────────────────────────────────
    # Main Entry Point
    # ──────────────────────────────────────────────────────────────────────

    def run(self, task: str) -> str:
        """
        Main entry point for task execution.
        Follows the ReAct Loop (Reason → Act → Observe) with strict execution guards.
        """
        # ── Guard: conversational / trivial inputs must not enter the agent loop ──
        _CONVERSATIONAL = {
            "yes", "no", "ok", "okay", "sure", "thanks", "thank you",
            "got it", "cool", "alright", "fine", "yep", "nope",
            "good", "great", "hi", "hello", "bye", "stop", "exit",
        }
        task_stripped = task.strip().lower().rstrip(".,!?")
        # ── Step 0: Goal ──────────────────────────────────────────
        self.heartbeat.step_start(f"Goal: {task[:60]}...")
        
        # Fast path: obvious live quote/rate lookups should feel Siri-like.

        # ── Plan Mode trigger ──────────────────────────────────────────────────
        # Activated by "__PLAN_MODE__" prefix (sent by Swift Plan button) or
        # by natural phrasing like "make a plan for..." / "plan out..."
        _PLAN_TRIGGERS = {"__PLAN_MODE__", "make a plan", "plan out", "create a plan", "write a plan"}
        is_plan_mode = (
            task.startswith("__PLAN_MODE__")
            or any(t in task.lower() for t in _PLAN_TRIGGERS)
        )
        if is_plan_mode and getattr(config, "PLAN_MODE_ENABLED", True):
            actual_task = task.replace("__PLAN_MODE__", "").strip() or task
            return self._run_plan_mode(actual_task)

        # Fast path: obvious live quote/rate lookups should feel Siri-like.
        # They do not need sandbox setup, playbooks, or a ReAct loop.
        direct_market_result = self._try_direct_market_data_task(task)
        if direct_market_result:
            return direct_market_result

        # ── Reset per-task state ──────────────────────────────────────────
        self.token_budget.reset()
        history: List[str] = []
        
        # Pull recent conversation history from ContextManager (Smart Context)
        context_mgr = self.registry.get("context")
        if context_mgr and hasattr(context_mgr, "command_history"):
            # Take last 2 entries (user query + jarvis response) to provide semantic grounding
            recent = context_mgr.command_history[-2:]
            for entry in recent:
                cmd = entry.get("command", "")
                res = entry.get("result", "")
                # Skip system/agent internal logs, only keep natural conversations
                if cmd and res and not cmd.startswith("__"):
                    history.append(f"User: {cmd}")
                    history.append(f"Jarvis: {res}")
            
            if history:
                logger.info(f"🧠 Smart Context: Injected {len(history)} previous turns into agent memory")

        iterations = 0
        task_start_time = time.time()
        self.task_id = str(uuid.uuid4())
        session = SessionState()  # ← NEW: per-task session state

        # Task-scoped memory vault
        commander = self.registry.get("commander")
        if commander and hasattr(commander, "memory_vault"):
            if not isinstance(commander.memory_vault, dict):
                commander.memory_vault = {}
            commander.memory_vault[self.task_id] = {}

        system_context = self._get_system_context()

        # ── Sandbox Initialization (lazy) ─────────────────────────────────
        # Most agentic tasks are safe tool calls. Creating a venv and installing
        # data-science packages up front makes simple lookups feel painfully slow,
        # so we only create/provision the sandbox when a file/shell tool needs it.
        self._sandbox_dir = os.path.join(
            os.path.expanduser("~"), ".jarvis_sandbox", self.task_id
        )
        self._sandbox_ready = False
        self._sandbox_provisioned = False
        logger.info(f"📦 Sandbox reserved (lazy): {self._sandbox_dir}")

        if commander and hasattr(commander, "memory_vault"):
            commander.memory_vault.pop("_sandbox_dir", None)

        # Build system prompt
        system_prompt = self._build_system_prompt(system_context, task=task)
        self.token_budget.consume_text(system_prompt)
        logger.info(f"💰 {self.token_budget}")

        # ── Task Planning ─────────────────────────────────────────────────
        plan = None
        current_step_index = 0
        if self.planner:
            try:
                available_tools = list(commander.tools.keys()) if commander and hasattr(commander, "tools") else []
                plan = self.planner.plan(task, available_tools, task_id=self.task_id)
                self.heartbeat.emit(f"📋 Plan: {plan.complexity.upper()} — {len(plan.steps)} step(s)")
                self.heartbeat.set_total_steps(len(plan.steps) if plan.steps else 1)
                logger.info(plan.summary())
                # Store plan in MemoryManager
                memory = self.registry.get("memory")
                if memory:
                    memory.remember(f"plan_{self.task_id}", plan.summary(), ttl_seconds=3600)
            except Exception as pe:
                logger.warning(f"⚠️ Planning failed, proceeding without plan: {pe}")
                plan = None

        # Complexity-aware timeout
        _TIMEOUT_MAP = {"trivial": 300, "simple": 1200, "complex": 1800, "research": 3600}
        complexity_tier = plan.complexity if plan else "simple"
        effective_timeout = _TIMEOUT_MAP.get(complexity_tier, self.config.timeout)
        logger.info(f"⏱️ Task timeout: {effective_timeout}s (tier={complexity_tier})")

        max_iterations = min(self.config.max_iterations, 20)  # Hard cap at 20

        try:
            no_action_streak = 0
            step_attempts = {}

            while iterations < max_iterations:
                iterations += 1
                logger.info(f"🤖 Agent Iteration {iterations}/{max_iterations}")

                # ⏱️ Timeout enforcement
                elapsed = time.time() - task_start_time
                if elapsed > effective_timeout:
                    logger.warning(f"⏱️ Agent timeout after {elapsed:.1f}s")
                    self.heartbeat.emit("⏱️ Timeout reached", "failed")
                    last_obs = self._get_best_summary(history)
                    return f"I ran out of time on this task after {elapsed:.0f} seconds, sir. Last status: {last_obs}"

                # 💓 Heartbeat: ensure the UI never goes silent > 3s
                self.heartbeat.ensure_alive(max_silence_seconds=3.0)

                # 💰 Token budget gate
                if self.token_budget.remaining() < 1500:
                    logger.warning(f"💰 Token budget low — compressing history.")
                    history = self.compressor.compress(history, self.token_budget)

                if not self.token_budget.can_afford(500):
                    self.heartbeat.emit("Context budget exhausted", "failed")
                    return (
                        "I've exhausted my context budget for this task, sir. "
                        "Please start a new request so I can proceed with a fresh context."
                    )

                # 📜 History window (budget-aware pruning)
                active_history = history
                if len(history) > 30:
                    active_history = (
                        history[:6]
                        + ["... (intermediate loops pruned for context density) ..."]
                        + history[-20:]
                    )

                # ── Build iteration prompt with session state injection ───
                current_step_str = self._get_current_step_directive(plan, current_step_index)

                # Inject verified session state (anti-hallucination)
                verified_state = session.get_verified_results_summary()
                failed_cmds = session.get_failed_commands_summary()

                prompt = self._build_iteration_prompt(
                    task, active_history,
                    current_step=current_step_str,
                    verified_state=verified_state,
                    failed_commands=failed_cmds,
                )

                # 1. REASON (with heartbeat)
                self.heartbeat.thinking("Reasoning about next step...")
                response = self.brain.ask(prompt, system_prompt=system_prompt, is_agentic=True)

                if response:
                    self.token_budget.consume_text(response)
                if not response:
                    self.heartbeat.emit("LLM returned empty response", "failed")
                    return "I encountered an error while thinking, sir."

                # 2. PARSE
                try:
                    thought = self._parse_response(response)
                except Exception as parse_err:
                    logger.warning(f"⚠️ Agent Parse Error: {parse_err}")
                    history.append(f"Thought: {response[:100]}...")
                    history.append(f"Observation: [!] INVALID FORMAT. Error: {str(parse_err)}. Please follow the strict format: Thought, Checklist, Reasoning, Action, Action Input.")
                    continue

                self._stream_to_hud(thought)

                # ── Handle no-action (Final Answer or stuck) ──────────────
                if not thought.action:
                    if "Final Answer:" in response:
                        self.heartbeat.emit("Task complete", "success")
                        self.heartbeat.clear()
                        return response.split("Final Answer:")[-1].strip()
                    else:
                        no_action_streak += 1
                        if no_action_streak >= 3:
                            logger.warning(f"⚠️ no_action_streak={no_action_streak} — force-terminating.")
                            self.heartbeat.emit("Agent stuck — terminating", "failed")
                            summary = self._get_best_summary(history)
                            return f"I've completed the main tasks, sir. Last status: {summary}" if summary else \
                                   "I got stuck on this task and could not complete it cleanly, sir. Please try again."
                        if no_action_streak >= 2:
                            history.append(f"Thought: {thought.reasoning}")
                            history.append(
                                "Observation: [URGENT] You are stuck — no Action provided AGAIN. "
                                "You MUST write either a valid Action+Action Input OR write 'Final Answer:' RIGHT NOW."
                            )
                        else:
                            history.append(f"Thought: {thought.reasoning}")
                            history.append("Observation: [!] You provided a Thought but no Action or Final Answer.")
                        continue
                else:
                    no_action_streak = 0

                # ══════════════════════════════════════════════════════════
                # EXECUTION GUARDS (WP1)
                # ══════════════════════════════════════════════════════════

                action_input = thought.action_input or {}

                # ── GUARD 1: DEDUPLICATION ────────────────────────────────
                previous_record = session.was_already_executed(thought.action, action_input)
                if previous_record:
                    status_str = "succeeded" if previous_record.success else "failed"
                    logger.warning(f"🔁 DEDUP: {thought.action} blocked (already {status_str})")
                    self.heartbeat.emit(f"🔁 Duplicate blocked: {thought.action}", "failed")
                    obs_msg = (
                        f"[DUPLICATE BLOCKED] You already called '{thought.action}' with identical input. "
                        f"Previous result ({status_str}): {previous_record.result[:300]}\n"
                        f"You MUST either: (a) use a DIFFERENT approach, or (b) write 'Final Answer:' with your results."
                    )
                    history.append(f"Thought: {thought.reasoning}")
                    history.append(f"Action: {thought.action}")
                    history.append(f"Action Input: {json.dumps(action_input)}")
                    history.append(f"Observation: {obs_msg}")
                    continue

                # ── GUARD 2: RETRY CAP (3 per step) ──────────────────────
                step_key = f"step_{current_step_index}"
                retry_count = session.get_retry_count(step_key)
                if retry_count >= 3:
                    logger.error(f"🚨 Retry cap hit for {step_key} (3 attempts)")
                    self.heartbeat.emit(f"❌ Step {current_step_index+1} failed (3 retries)", "failed")
                    # Force advance to next step (if plan exists) or terminate
                    if plan and plan.steps and current_step_index < len(plan.ordered_steps()) - 1:
                        current_step_index += 1
                        session.retry_counts[step_key] = 0  # Reset for new step
                        history.append(
                            f"Observation: [RETRY CAP] Step {current_step_index} failed after 3 attempts. "
                            f"Advancing to next step. Mark this as [SKIPPED]."
                        )
                        continue
                    else:
                        # No more steps — terminate with partial results
                        summary = self._get_best_summary(history)
                        return f"I was unable to complete step {current_step_index+1} after 3 attempts, sir. {summary}"

                # ── GUARD 3: CHECK-BEFORE-ACT (file existence) ───────────
                if thought.action == "run_command" and action_input.get("command"):
                    cmd = action_input["command"]
                    file_ref = self._extract_file_reference(cmd)
                    if file_ref and not self._is_sandbox_internal(file_ref):
                        self.heartbeat.step_start(f"Checking: {file_ref}...", step_index=current_step_index)
                        desktop_path = os.path.expanduser(f"~/Desktop/{file_ref}")
                        if not os.path.exists(desktop_path):
                            obs_msg = (
                                f"[CHECK-BEFORE-ACT] File '{file_ref}' does NOT exist on the Desktop "
                                f"(checked: {desktop_path}). You MUST NOT create a dummy file. "
                                f"Write a Final Answer telling the user the file was not found."
                            )
                            history.append(f"Thought: {thought.reasoning}")
                            history.append(f"Action: {thought.action}")
                            history.append(f"Action Input: {json.dumps(action_input)}")
                            history.append(f"Observation: {obs_msg}")
                            session.record_execution(thought.action, action_input, obs_msg, success=False)
                            continue

                # ── GUARD 4: URL-as-query redirect ────────────────────────
                if thought.action == "web_search" and action_input:
                    q = action_input.get("query", "")
                    if q.startswith(("http://", "https://", "www.")):
                        logger.warning(f"🔗 URL passed to web_search — redirecting to fetch_url")
                        thought.action = "fetch_url"
                        thought.action_input = {"url": q}
                        action_input = thought.action_input
                        history.append(
                            "Observation: [AUTO-REDIRECT] URLs must use fetch_url, not web_search. Redirecting."
                        )

                # ── GUARD 5: Do not use expert playbooks for simple live data ─
                if self._should_block_playbook_for_task(task, thought.action):
                    obs_msg = (
                        "[DIRECT TOOL REQUIRED] This is a straightforward live market-data task. "
                        "Do NOT search or fetch expert playbooks. Use `get_market_data` if available, "
                        "otherwise use one `web_search`, then finish or deliver the result."
                    )
                    history.append(f"Thought: {thought.reasoning}")
                    history.append(f"Action: {thought.action}")
                    history.append(f"Action Input: {json.dumps(action_input)}")
                    history.append(f"Observation: {obs_msg}")
                    session.record_execution(thought.action, action_input, obs_msg, success=False)
                    continue

                # ── GUARD 6: Block shell hallucinations for simple data lookups ─
                if thought.action == "run_command" and self._should_block_shell_for_simple_market_data(task):
                    obs_msg = (
                        "[SHELL BLOCKED] This task only needs a live quote/rate. "
                        "`run_command` would require unnecessary approval and is prone to brittle curl/grep failures. "
                        "Use `get_market_data` with the user's original query, or `web_search` if that tool is unavailable."
                    )
                    history.append(f"Thought: {thought.reasoning}")
                    history.append(f"Action: {thought.action}")
                    history.append(f"Action Input: {json.dumps(action_input)}")
                    history.append(f"Observation: {obs_msg}")
                    session.record_execution(thought.action, action_input, obs_msg, success=False)
                    continue

                if thought.action in {"run_command", "write_file", "finalize_project"}:
                    self._ensure_sandbox(provision=(thought.action == "run_command"))

                # ══════════════════════════════════════════════════════════
                # 3. ACT (with heartbeat)
                # ══════════════════════════════════════════════════════════

                tool_label = f"Running: {thought.action}"
                if thought.action == "run_command":
                    cmd_preview = action_input.get("command", "")[:60]
                    tool_label = f"Executing: {cmd_preview}..."
                elif thought.action == "web_search":
                    query_preview = action_input.get("query", "")[:50]
                    tool_label = f"Searching: {query_preview}..."
                elif thought.action == "write_file":
                    path_preview = action_input.get("path", "")
                    tool_label = f"Writing: {path_preview}"

                self.heartbeat.action(tool_label, "active")

                act_start = time.time()
                observation = self._execute_action(thought)
                act_latency_ms = int((time.time() - act_start) * 1000)

                # ── SUCCESS DETECTION ─────────────────────────────────────
                detected_success = detect_success(observation.result)
                if detected_success is False:
                    observation = Observation(
                        tool=observation.tool,
                        result=observation.result,
                        success=False,
                    )
                elif detected_success is True:
                    observation = Observation(
                        tool=observation.tool,
                        result=observation.result,
                        success=True,
                    )
                # If None (ambiguous), keep the original success flag

                # ── Record in SessionState ────────────────────────────────
                session.record_execution(
                    thought.action, action_input,
                    observation.result, observation.success,
                )

                # ── SIDE-EFFECT VERIFICATION (Anti-Hallucination) ─────────
                if observation.success:
                    # If the task was to create/write something, verify it on disk
                    target_path = action_input.get("path") or action_input.get("destination")
                    if not target_path and thought.action == "run_command":
                        # Guess path from command if common (mkdir, touch)
                        cmd = action_input.get("command", "")
                        match = re.search(r"(?:mkdir|touch|cp|mv)\s+([^\s;&|]+)", cmd)
                        if match:
                            target_path = match.group(1)

                    if target_path:
                        exists = self._path_exists(target_path)
                        if not exists:
                            logger.warning(f"⚠️ VERIFICATION FAILED: {target_path} not found despite tool success. Overriding success.")
                            observation = Observation(
                                tool=observation.tool,
                                result=f"{observation.result}\n\n[!] VERIFICATION ERROR: The tool claimed success, but '{target_path}' does not exist on disk. Use 'ls' to check your surroundings and try again.",
                                success=False,
                            )

                # Track retries per step
                if not observation.success:
                    session.increment_retry(step_key)

                # Heartbeat: report step result
                self.heartbeat.step_complete(tool_label, observation.success)

                # ── 4. OBSERVE — assess quality ───────────────────────────
                obs_result = observation.result

                # Empty output guard (anti-hallucination)
                if not obs_result or obs_result.strip() == "":
                    obs_result = "[!] Tool returned EMPTY output — do NOT assume success. Verify the result."

                expected_type = "text"
                if plan and plan.steps and current_step_index < len(plan.ordered_steps()):
                    expected_type = plan.ordered_steps()[current_step_index].expected_output_type

                obs_quality = self.assessor.assess(obs_result, expected_type)
                logger.info(self.assessor.summarise_quality(obs_quality, thought.action or "", obs_result))

                # Record performance
                skill_registry = self.registry.get("skill_registry")
                if skill_registry and thought.action:
                    skill_registry.record_outcome(thought.action, observation.success, act_latency_ms)

                # Store step output in MemoryManager
                memory = self.registry.get("memory")
                if memory and thought.action:
                    memory.set_step_output(self.task_id, iterations, obs_result)

                # ── STEP PROGRESSION ──────────────────────────────────────
                _META_TOOLS = {"remember_fact", "save_info", "retrieve_fact", "search_awesome_skills", "fetch_skill_playbook", "search_contact"}

                if plan and plan.steps:
                    step_attempts[current_step_index] = step_attempts.get(current_step_index, 0) + 1
                    attempts = step_attempts[current_step_index]

                    ordered_steps = plan.ordered_steps()

                    is_meta = thought.action in _META_TOOLS
                    is_explicit_plan_tool = (
                        current_step_index < len(ordered_steps)
                        and thought.action == ordered_steps[current_step_index].tool
                    )
                    can_advance = obs_quality == "good" and (not is_meta or is_explicit_plan_tool)

                    if can_advance:
                        if current_step_index < len(ordered_steps):
                            cur_step_desc = ordered_steps[current_step_index].description.lower()

                            # Anti-ghosting guard
                            requires_saving = any(kw in cur_step_desc for kw in ["save", "write", "create a file", "create an .md", "folder", "download"])
                            is_creation_tool = thought.action in ["write_file", "run_command", "copy_knowledge"]

                            if requires_saving and not is_creation_tool:
                                logger.warning(f"⚠️ Step requires saving but used '{thought.action}'. Blocking advance.")
                                obs_result += "\n\n[ANTI-GHOST] Step REQUIRES saving output. Call `write_file` or `run_command` before moving on."
                            else:
                                current_step_index += 1
                                self.heartbeat.emit(
                                    f"✅ Step {current_step_index}/{len(ordered_steps)} complete",
                                    "success"
                                )
                                if current_step_index < len(ordered_steps):
                                    next_step = ordered_steps[current_step_index]
                                    logger.info(f"📋 ✅ Step done — advancing to Step {current_step_index + 1}/{len(ordered_steps)}: {next_step.description}")
                                else:
                                    logger.info(f"📋 ✅ All plan steps verified — requesting wrap-up.")

                    elif obs_quality == "partial" and (not is_meta or is_explicit_plan_tool):
                        logger.warning(f"⚠️ Step result was PARTIAL (Attempt {attempts})")
                        if attempts == 3:
                            obs_result += "\n\n[LOOP WARNING] 3 partial attempts. CHANGE your strategy immediately."

                elif obs_quality == "partial":
                    logger.warning(f"⚠️ Result was PARTIAL — staying on turn.")

                # Observation pruning
                if len(obs_result) > 5000:
                    obs_result = (
                        obs_result[:3000]
                        + "\n... (excessive detail pruned) ...\n"
                        + obs_result[-1000:]
                    )

                # Append to history
                history.append(f"Thought: {thought.reasoning}")
                if "Checklist:" in response:
                    checklist = re.search(r"Checklist:(.*?)(?:\nReasoning:|$)", response, re.DOTALL)
                    if checklist:
                        history[-1] = f"Checklist:{checklist.group(1)}\nReasoning: {thought.reasoning}"

                history.append(f"Action: {thought.action}")
                history.append(f"Action Input: {json.dumps(thought.action_input)}")
                history.append(f"Observation: {obs_result}")

            raise AgentMaxIterationsError("Hit iteration cap.")

        except AgentMaxIterationsError:
            self.heartbeat.emit("Iteration limit reached", "failed")
            self.heartbeat.clear()
            error_msg = f"I've hit my planning limit of {max_iterations} steps for this task, sir. "
            return error_msg + "I was able to determine that: " + (history[-1] if history else "I couldn't reach a conclusion.")
        except Exception as e:
            logger.error(f"❌ Agent Loop Error: {e}")
            self.heartbeat.emit(f"Error: {str(e)[:50]}", "failed")
            self.heartbeat.clear()
            return f"My apologies, sir. An error occurred in my agentic core: {str(e)}"
        finally:
            self.heartbeat.clear()
            # Sandbox cleanup
            if hasattr(self, '_sandbox_dir') and os.path.exists(self._sandbox_dir):
                try:
                    contents = os.listdir(self._sandbox_dir)
                    if not contents:
                        shutil.rmtree(self._sandbox_dir, ignore_errors=True)
                        logger.debug("🧹 Empty sandbox cleaned up.")
                    else:
                        logger.info(f"📦 Sandbox preserved (has {len(contents)} items): {self._sandbox_dir}")
                except Exception:
                    pass

    # ──────────────────────────────────────────────────────────────────────
    # Helper: Extract file reference from a command
    # ──────────────────────────────────────────────────────────────────────

    def _extract_file_reference(self, command: str) -> Optional[str]:
        """
        Check if a command references a script file to run.
        Returns the filename if found, None otherwise.
        """
        patterns = [
            r"python3?\s+([^\s;|&]+\.py)",
            r"node\s+([^\s;|&]+\.js)",
            r"bash\s+([^\s;|&]+\.sh)",
            r"ruby\s+([^\s;|&]+\.rb)",
        ]
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                filepath = match.group(1)
                # Only return basename (not paths starting with ./ or /)
                if not filepath.startswith(("/", "./", "~", "venv/")):
                    return filepath
        return None

    def _is_sandbox_internal(self, filename: str) -> bool:
        """Check if a file was created within the sandbox (allow running it)."""
        if hasattr(self, '_sandbox_dir') and self._sandbox_dir:
            sandbox_path = os.path.join(self._sandbox_dir, filename)
            return os.path.exists(sandbox_path)
        return False

    def _get_current_step_directive(self, plan, current_step_index: int) -> Optional[str]:
        """Build the current step directive string for the iteration prompt."""
        if not plan or not plan.steps:
            return None

        ordered = plan.ordered_steps()
        if current_step_index < len(ordered):
            step = ordered[current_step_index]
            remaining = len(ordered) - current_step_index
            return (
                f"Step {current_step_index + 1}/{len(ordered)}: {step.description}\n"
                f"Preferred tool: {step.tool}\n"
                f"({remaining} step(s) remaining after this — do NOT stop here.)"
            )
        elif current_step_index >= len(ordered):
            return (
                f"Your plan steps are done. "
                f"BEFORE writing the Final Answer, verify: have you completed EVERY action in the "
                f"original user request? If any action is still pending, do it NOW. "
                f"Only write 'Final Answer:' once everything is done."
            )
        return None

    def _get_best_summary(self, history: List[str]) -> str:
        """Extract the best summary from history for termination messages."""
        for h in reversed(history):
            if h.startswith("Observation:") and len(h) > 80:
                return h.replace("Observation: ", "").strip()
        return history[-1] if history else "No progress made."

    def _try_direct_market_data_task(self, task: str) -> Optional[str]:
        """
        Direct path for obvious live quote/rate requests.
        This avoids a full agent loop for tasks like:
          "current gold price"
          "email me the live gold price"
        """
        if not self._is_simple_market_data_task(task):
            return None

        try:
            from modules.live_data_service import LiveDataService
            result = LiveDataService.resolve_market_data(task)
        except Exception as e:
            logger.debug(f"Direct market-data path skipped: {e}")
            return None

        if not result:
            return None

        text = task.lower()
        wants_email = any(k in text for k in ("email", "mail"))
        if not wants_email:
            logger.info("⚡ Direct market-data fast path satisfied task.")
            return result

        commander = self.registry.get("commander")
        # 🔗 Senior Developer Fix: Check Unified Registry if commander background tool loading is in-progress
        skill_registry = self.registry.get("skill_registry")
        email_tool_available = (
            "send_email" in getattr(commander, "tools", {}) 
            or (skill_registry and skill_registry.get_by_id("send_email"))
        )

        if not commander or not hasattr(commander, "execute_tool") or not email_tool_available:
            return f"{result}\n\nI found the live data, but the email tool is not available right now."

        subject = self._market_email_subject(task)
        body = result
        payload = {
            "to": getattr(config, "USER_EMAIL", "samson06060@gmail.com"),
            "recipient": getattr(config, "USER_EMAIL", "samson06060@gmail.com"),
            "subject": subject,
            "body": body,
        }
        email_result = commander.execute_tool("send_email", payload)
        logger.info("⚡ Direct market-data email path completed.")
        return f"{result}\n\nEmail status: {email_result}"

    def _is_simple_market_data_task(self, task: str) -> bool:
        try:
            from modules.live_data_service import LiveDataService
            if not LiveDataService.is_market_data_query(task):
                return False
        except Exception:
            return False

        text = task.lower()
        complex_terms = [
            "compare", "analyze", "analyse", "research", "report", "forecast",
            "trend", "historical", "history", "chart", "graph", "portfolio",
            "backtest", "strategy", "why", "explain", "deep dive", "top ",
            "best ", "volatility", "moving average",
        ]
        return not any(term in text for term in complex_terms)

    def _market_email_subject(self, task: str) -> str:
        text = task.lower()
        if "gold" in text:
            return "Current gold price"
        if "silver" in text:
            return "Current silver price"
        if "bitcoin" in text or "btc" in text:
            return "Current Bitcoin price"
        return "Current market quote"

    def _should_block_playbook_for_task(self, task: str, action: Optional[str]) -> bool:
        if action not in {"search_awesome_skills", "fetch_skill_playbook"}:
            return False
        return self._is_simple_market_data_task(task) and not self._task_needs_playbook(task)

    def _should_block_shell_for_simple_market_data(self, task: str) -> bool:
        return self._is_simple_market_data_task(task)

    def _preferred_tools_for_task(self, task: str, raw_tools: Dict[str, Any]) -> List[str]:
        """Pin obviously relevant tools into the prompt so semantic ranking cannot hide them."""
        text = (task or "").lower()
        preferred = []

        def add(tool_id: str):
            if tool_id in raw_tools and tool_id not in preferred:
                preferred.append(tool_id)

        if self._is_simple_market_data_task(task):
            add("get_market_data")
            add("web_search")
        if any(k in text for k in ("email", "mail")):
            add("send_email")
        if any(k in text for k in ("message", "imessage", "whatsapp", "text")):
            add("send_message")
            add("send_whatsapp")
        if any(k in text for k in ("weather", "temperature", "forecast")):
            add("get_weather")
        if any(k in text for k in ("time", "date", "clock")):
            add("get_time")

        return preferred

    def _task_needs_playbook(self, task: str) -> bool:
        text = (task or "").lower()
        if self._is_simple_market_data_task(task):
            return False
        playbook_signals = [
            "playbook", "expert", "best practice", "architecture", "architect",
            "security", "audit", "refactor", "debug", "fix", "implement",
            "build", "design", "migrate", "optimize", "production", "strategy",
            "compliance", "investigate", "research", "compare", "analyze",
            "deep dive", "report",
        ]
        return any(signal in text for signal in playbook_signals)

    def _ensure_sandbox(self, provision: bool = False):
        """Create/provision the task sandbox only when a tool actually needs it."""
        if not hasattr(self, "_sandbox_dir") or not self._sandbox_dir:
            self._sandbox_dir = os.path.join(
                os.path.expanduser("~"), ".jarvis_sandbox", self.task_id or str(uuid.uuid4())
            )
            self._sandbox_ready = False
            self._sandbox_provisioned = False

        if not getattr(self, "_sandbox_ready", False):
            os.makedirs(self._sandbox_dir, exist_ok=True)
            self._sandbox_ready = True
            logger.info(f"📦 Sandbox directory: {self._sandbox_dir}")

            commander = self.registry.get("commander")
            if commander and hasattr(commander, "memory_vault"):
                commander.memory_vault["_sandbox_dir"] = self._sandbox_dir

        if provision and not getattr(self, "_sandbox_provisioned", False):
            self._provision_sandbox()
            self._sandbox_provisioned = True

    # ──────────────────────────────────────────────────────────────────────
    # Plan Mode
    # ──────────────────────────────────────────────────────────────────────

    def _run_plan_mode(self, task: str) -> str:
        """
        Plan Mode flow: generate → send to UI → wait for approval → execute.
        """
        try:
            from modules.plan_mode import PlanMode
        except ImportError:
            return "Plan Mode is not available (plan_mode.py missing)."

        # Late-bind brain to PlanMode if it was initialized without one
        plan_mode = self.registry.get("plan_mode")
        if plan_mode is None:
            plan_mode = PlanMode(brain=self.brain, registry=self.registry)
            try:
                from core.registry import ServiceRegistry
                ServiceRegistry.register("plan_mode", plan_mode)
            except Exception:
                pass
        else:
            plan_mode.brain = self.brain

        commander = self.registry.get("commander")
        available_tools = list(getattr(commander, "tools", {}).keys()) if commander else []

        result = plan_mode.run(task, available_tools, heartbeat=self.heartbeat)

        if not result.get("approved"):
            return "Understood, sir. Plan cancelled. Let me know when you're ready to proceed."

        doc = result["plan"]
        self.heartbeat.emit(f"Executing plan: {doc.goal[:50]}...", "active")
        self.heartbeat.set_total_steps(len(doc.steps))

        # Execute each step sequentially using the normal agent loop
        all_outputs = []
        for i, step in enumerate(doc.steps):
            step_label = f"Step {step.number}/{len(doc.steps)}: {step.title}"
            self.heartbeat.step_start(step_label, step_index=i)
            step_task = f"{step.description}\nPreferred tool: {step.tool}"
            if all_outputs:
                previous = "\n\n".join(all_outputs[-2:])
                step_task += f"\n\nPrevious verified outputs:\n{previous}"
            output = self.run(step_task)
            success = not any(sig in (output or "").lower() for sig in ["error", "failed", "apologies"])
            self.heartbeat.step_complete(step_label, success=success)
            all_outputs.append(output)

        self.heartbeat.clear()
        
        if not all_outputs:
            return "Plan executed — no output returned."

        # 🧠 JARVIS SYNTHESIS PHASE
        # Convert raw tool outputs into a natural, sophisticated assistant response.
        full_context = "\n\n".join(filter(None, all_outputs))
        synthesis_prompt = (
            f"Sir, I have completed the assigned task: '{task}'.\n\n"
            f"Here are the internal results I gathered:\n{full_context}\n\n"
            f"Please synthesize this into a final response that is helpful, intelligent, and fits my persona "
            f"as JARVIS (Sophisticated, loyal, slightly witty). Address the user as Sir. "
            f"Avoid technical jargon or step-by-step numbering in the final answer. Provide exactly what was asked for."
        )
        return self.brain.ask(synthesis_prompt)

    # ──────────────────────────────────────────────────────────────────────
    # System Prompt
    # ──────────────────────────────────────────────────────────────────────

    def _build_system_prompt(self, context: str, task: str = "") -> str:
        """
        Build agent system prompt. Uses commander.tools as the SINGLE source of truth
        for which tools exist. UnifiedSkillRegistry is used only to ORDER them.
        """
        commander = self.registry.get("commander")
        raw_tools: dict = getattr(commander, "tools", {}) or {}

        if not raw_tools:
            tools_desc = "(No tools available — check agent_skills directory)"
        else:
            # Semantic Router for tool ordering
            ordered_ids = []
            try:
                from modules.semantic_router import SemanticRouter
                router = SemanticRouter.instance()
                if router.ready and task:
                    sem_results = router.search(task, top_k=7, threshold=0.45)
                    if sem_results:
                        ordered_ids = [sk_id for sk_id, _ in sem_results if sk_id in raw_tools]
                        logger.debug(f"🧠 SemanticRouter ordered {len(ordered_ids)} tools.")
            except Exception as _se:
                logger.debug(f"SemanticRouter tool ordering skipped: {_se}")

            # Fallback: keyword-based scoring
            if not ordered_ids:
                skill_registry = self.registry.get("skill_registry")
                if skill_registry and task:
                    scored = skill_registry.score_for_task(task, top_n=50)
                    ordered_ids = [e.id for e, _ in scored if e.id in raw_tools]
                    remaining = [t for t in raw_tools if t not in ordered_ids]
                    ordered_ids = (ordered_ids + remaining)[:7]
                else:
                    ordered_ids = list(raw_tools.keys())[:7]
            else:
                remaining = [t for t in raw_tools if t not in ordered_ids]
                ordered_ids = (ordered_ids + remaining)[:7]

            preferred_ids = self._preferred_tools_for_task(task, raw_tools)
            suppressed_ids = set()
            if self._is_simple_market_data_task(task):
                suppressed_ids = {"search_awesome_skills", "fetch_skill_playbook", "run_command"}
            ordered_ids = preferred_ids + [
                tid for tid in ordered_ids
                if tid not in preferred_ids and tid not in suppressed_ids
            ]

            top_12 = ordered_ids[:10]
            lines = [
                f"- {tid}: {raw_tools[tid].description}"
                for tid in top_12
                if tid in raw_tools and hasattr(raw_tools[tid], "description")
            ]
            for meta_tool in ("search_awesome_skills", "fetch_skill_playbook"):
                if (
                    self._task_needs_playbook(task)
                    and meta_tool in raw_tools
                    and f"- {meta_tool}:" not in "\n".join(lines)
                ):
                    lines.append(f"- {meta_tool}: {raw_tools[meta_tool].description}")
            tools_desc = "\n".join(lines)

        return f"""You are JARVIS, an autonomous agentic assistant.
You solve complex multi-step tasks using a ReAct (Reasoning + Action) loop.

System Context:
{context}

Available Tools (top-12 most relevant for this task):
{tools_desc}

### EXPERT PLAYBOOKS (MCP SYSTEM)
You have access to 2,200+ specialized expert skills.
- Use `search_awesome_skills` only when the task genuinely needs specialized expert strategy.
- Use `fetch_skill_playbook` only after a highly relevant skill ID was found.
- Skip playbooks for simple lookups, live market prices, weather, time, math, basic web search, and sending known content.
- For live/current stocks, crypto, commodities, gold/silver/oil, or FX/currency rates, use `get_market_data` if it is listed.

Strict Format:
Thought: I must first break down the user's request into a checklist.
Checklist:
- [ ] Task 1
- [ ] Task 2
Reasoning: I will now execute Task 1.
Action: tool_name
Action Input: {{ "param": "value" }}
--- OR ---
Thought: I have completed all items in my checklist.
Checklist:
- [x] Task 1
- [x] Task 2
Reasoning: Every part of the request is satisfied. I am ready to provide the final answer.
Final Answer: ...

Rules:
1. **CHECKLIST**: Use [ ] (pending) and [x] (completed) in Thought. Mark steps [x] as you complete them.
2. **ADVANCE**: After each successful tool call (GOOD observation), mark that checklist item [x] and move to the NEXT item immediately.
3. **NO-HALFS**: Final Answer only when ALL items are [x].
4. **URL vs SEARCH**: `web_search` takes ONLY plain keyword queries. NEVER pass a URL — URLs go to `fetch_url`.
5. **ONE SEARCH PER STEP**: One successful web_search per checklist item is enough. Once you get GOOD results, STOP searching.
6. **DATA SUFFICIENCY**: If an Observation has 5+ lines of relevant text, you HAVE the data. Do NOT search again.
7. **NO-HALLUCINATION**: Use ONLY listed tools by EXACT name. Do not invent tool names.
8. **NO-LOOP**: If the same tool+input appears twice in history, do NOT call it again. The system will block duplicates.
9. **STRICT JSON**: 'Action Input' MUST be valid JSON with double-quoted keys and string values.
10. **DATA INCLUSION**: Final Answer MUST include actual retrieved data, not a summary of what you searched for.
11. **GRACEFUL FAILURE**: If an execution tool fails (like file-not-found) but you have checked reasonable alternative paths, do NOT loop or hallucinate fictional tools. STOP and inform the user immediately. Do NOT create dummy files.
12. **STEP ORDER**: Complete steps in order. Don't skip to Final Answer until all checklist items are [x].
13. **OUTPUT VERIFICATION**: If a step requires creating a file or folder, you MUST verify its existence (using `ls` or `run_command`) in your Thought process BEFORE claiming the step is done.
14. **PLATFORM PRAGMATISM**: Choose the simplest, most reliable technology for the target (e.g., HTML5/JS for Web). Avoid heavy desktop engines unless the task specifically demands native software.
15. **CODE EXECUTION**: If you write code for analysis or a game, you MUST execute it in the sandbox to verify syntax/logic before summarizing or saving.
16. **NO GHOST COMPLETION**: You MUST call creation tools to produce files. Claiming completion without tools is a CRITICAL FAILURE.
17. **NO PLACEHOLDERS**: Never invent data. If a tool fails, state it clearly.
18. **FORMATTING**: Raw text output MUST be in a code block (```text ... ```) for proper rendering.
19. **NO INTERACTIVE INPUTS**: NEVER use `input()` in scripts. Pass variables via `sys.argv`.
20. **SEARCH QUALITY**: If looking for live data, reject stale results.
21. **ANTI-STALL**: If you receive a [LOOP WARNING], you MUST pivot your strategy immediately.
22. **NO DUPLICATION**: Work in a single sandbox directory. Overwrite in-place.
23. **SINGLE OUTPUT**: ONE project directory. Remove old files before writing new ones.
24. **ERROR LEARNING**: If a command failed, your next attempt MUST address the specific error.
25. **PURE INFORMATION MODE**: For informational queries, answer directly. Do NOT create files.
26. **FILE EXISTENCE CHECK**: Before running a user file, check Desktop first. If not found, INFORM THE USER AND STOP. NEVER create dummy files or loop infinitely.
27. **RETRY RULES**: Max 3 retries per step. Each retry MUST use a different approach.
28. **SESSION STATE**: The system tracks all previous tool calls. Duplicate calls are blocked.
29. **SIMPLE DATA ROUTING**: Do not use `run_command` for simple live data.
30. **SMART PRONOUN RESOLUTION**: If the user refers to "this", "it", etc., resolve against RECENT CONVERSATION history.
31. **SANDBOX PIPELINE**: Always develop in the sandbox first (Write → Test → Verify) before deploying to the user's Desktop.
"""

    # ──────────────────────────────────────────────────────────────────────
    # Iteration Prompt
    # ──────────────────────────────────────────────────────────────────────

    def _build_iteration_prompt(
        self, task: str, history: List[str],
        current_step: Optional[str] = None,
        verified_state: str = "",
        failed_commands: str = "",
    ) -> str:
        history_text = "\n".join(history)

        # Dynamic constraint injection
        commander = self.registry.get("commander")
        extra_constraints = ""
        if commander and hasattr(commander, "memory_vault"):
            vault = commander.memory_vault.get(self.task_id, {})
            playbook_keys = [k for k in vault if "playbook" in k.lower() or "skill" in k.lower()]
            if playbook_keys:
                extra_constraints = "\n### ACTIVE EXPERT CONSTRAINTS:\n"
                for k in playbook_keys:
                    extra_constraints += f"- From {k}: Follow the 'Output Format' and 'Execution Rules' precisely.\n"

        # Error memory injection
        error_context = ""
        if commander and hasattr(commander, "memory_vault") and isinstance(commander.memory_vault, dict):
            error_log = commander.memory_vault.get("_error_log", [])
            if error_log:
                last_error = error_log[-1]
                error_context = (
                    f"\n### ⚠️ PREVIOUS ERROR (DO NOT REPEAT):\n"
                    f"Command: `{last_error.get('command', 'unknown')}`\n"
                    f"Error: {str(last_error.get('stderr', ''))[:500]}\n"
                    f"Return Code: {last_error.get('returncode', 'unknown')}\n"
                    f"You MUST analyze this error and change your approach.\n"
                )

        # Sandbox context
        sandbox_note = ""
        if hasattr(self, '_sandbox_dir') and self._sandbox_dir:
            sandbox_note = (
                f"\n### SANDBOX DIRECTORY: {self._sandbox_dir}"
                f"\nThis is YOUR working space for files YOU create."
                f"\n⚠️ The sandbox is NOT where the user's existing files live."
                f"\nWhen the user asks you to run their file, search Desktop first.\n"
            )

        # Verified session state injection (anti-hallucination)
        state_block = ""
        if verified_state:
            state_block = f"\n{verified_state}\n"
        if failed_commands:
            state_block += f"\n{failed_commands}\n"

        if current_step:
            directive = (
                f"Overall Goal: {task}\n"
                f"Current Step Directive: {current_step}\n"
                f"Complete this specific step using the tools available. "
                f"If a Preferred tool is named and available, use it exactly unless a guard tells you otherwise."
                f"{extra_constraints}{error_context}{sandbox_note}{state_block}"
            )
        else:
            directive = f"User Task: {task}{extra_constraints}{error_context}{sandbox_note}{state_block}"

        return f"{directive}\n\nHistory:\n{history_text}\n\nNext Step:"

    # ──────────────────────────────────────────────────────────────────────
    # Response Parser
    # ──────────────────────────────────────────────────────────────────────

    def _parse_response(self, text: str) -> Thought:
        # Pre-process: neutralise non-standard outputs
        _fake_action = re.search(r"Action:\s*(None|Finish|Done|Complete|N/A|null)\b", text, re.IGNORECASE)
        if _fake_action:
            after = text[_fake_action.end():].strip().lstrip(":\n ")
            if "Final Answer:" not in text:
                text = text[:_fake_action.start()] + "Final Answer: " + (after or "Task complete.")

        # Standard ReAct patterns
        thought_match = re.search(r"Thought:\s*(.*?)(?:\nChecklist:|\nReasoning:|\nAction:|\nFinal Answer:|$)", text, re.DOTALL)
        reasoning_match = re.search(r"Reasoning:\s*(.*?)(?:\nAction:|\nFinal Answer:|$)", text, re.DOTALL)
        action_match = re.search(r"Action:\s*(\w+)", text)

        reasoning = (reasoning_match.group(1).strip() if reasoning_match else
                     thought_match.group(1).strip() if thought_match else "")

        action = action_match.group(1).strip() if action_match else None
        final_answer_match = re.search(r"Final Answer:\s*(.*)", text, re.DOTALL)

        if not reasoning and not action and not final_answer_match:
            raise ValueError("Missing 'Thought', 'Action', or 'Final Answer' block.")

        action_input = {}

        if action:
            # Robust JSON extraction
            raw_input = ""
            action_pos = text.find(f"Action: {action}")
            if action_pos == -1:
                action_pos = text.find("Action:")

            start_idx = text.find("{", action_pos)
            if start_idx != -1:
                stack = 0
                for i in range(start_idx, len(text)):
                    if text[i] == '{': stack += 1
                    elif text[i] == '}':
                        stack -= 1
                        if stack == 0:
                            raw_input = text[start_idx:i+1]
                            break

            if raw_input:
                if "```" in raw_input:
                    raw_input = re.sub(r"```(?:json)?\s*(.*?)\s*```", r"\1", raw_input, flags=re.DOTALL).strip()

                try:
                    action_input = json.loads(raw_input)
                except Exception:
                    try:
                        import ast
                        action_input = ast.literal_eval(raw_input)
                        logger.debug(f"🛠️ Recovered input via ast.literal_eval")
                    except Exception as e:
                        raise ValueError(f"Invalid JSON in Action Input: {raw_input[:100]}... (Error: {str(e)})")
            else:
                raise ValueError(f"Action '{action}' provided but 'Action Input' block is missing or malformed.")

        # Fallback for tool_call tags
        if not action and "<tool_call>" in text:
            xml_func = re.search(r"<tool_call>(.*?)</tool_call>", text, re.DOTALL)
            if xml_func:
                try:
                    parsed = json.loads(xml_func.group(1).strip())
                    action = parsed.get("name") or parsed.get("tool")
                    action_input = parsed.get("arguments") or parsed.get("parameters") or parsed
                except Exception:
                    pass

        return Thought(reasoning=reasoning or "Thinking...", action=action, action_input=action_input)

    # ──────────────────────────────────────────────────────────────────────
    # Action Execution
    # ──────────────────────────────────────────────────────────────────────

    def _execute_action(self, thought: Thought) -> Observation:
        commander = self.registry.get("commander")
        if not hasattr(commander, "execute_tool"):
            return Observation(tool=thought.action, result="Tool system not initialized.", success=False)

        # Anti-Hallucination: validate tool name
        available_tools: dict = getattr(commander, "tools", {})
        if thought.action not in available_tools:
            tool_list = ", ".join(sorted(available_tools.keys())[:20])
            return Observation(
                tool=thought.action,
                result=(
                    f"[!] ERROR: Tool '{thought.action}' does not exist. "
                    f"Available tools are: {tool_list}. "
                    f"Choose one of these EXACT names."
                ),
                success=False,
            )

        try:
            result = commander.execute_tool(thought.action, thought.action_input)
            result_str = str(result)

            # Detect empty results
            if not result_str or result_str.strip() in ("", "None", "null"):
                return Observation(
                    tool=thought.action,
                    result="[!] Tool returned EMPTY output — do NOT assume success. Verify the result.",
                    success=False,
                )

            return Observation(tool=thought.action, result=result_str, success=True)
        except Exception as e:
            return Observation(tool=thought.action, result=f"Error executing tool: {str(e)}", success=False)

    # ──────────────────────────────────────────────────────────────────────
    # HUD + Context Helpers
    # ──────────────────────────────────────────────────────────────────────

    def _get_system_context(self) -> str:
        import os, platform, getpass
        home = os.path.expanduser("~")
        user = getpass.getuser()
        os_name = platform.system()
        user_email = getattr(config, "USER_EMAIL", "samson06060@gmail.com")
        return f"- Operating System: {os_name}\n- Current User: {user}\n- User Email: {user_email}\n- Home Directory: {home}\n- Desktop: {os.path.join(home, 'Desktop')}"

    def _stream_to_hud(self, thought: Thought):
        if self.hud:
            msg = f"💭 {thought.reasoning}"
            if thought.action:
                msg += f"\n🛠️ Using: {thought.action}"
            self.hud.put(("PROCESSING", msg))

    def _stream_to_hud_text(self, text: str, header: str = "PROCESSING"):
        """Send a status message to the HUD."""
        if self.hud:
            try:
                self.hud.put((header, text))
            except Exception:
                pass

    def _get_active_playbooks(self, task: str) -> str:
        """DEPRECATED: We now use FetchSkillPlaybookTool for on-demand retrieval."""
        return ""

    def _provision_sandbox(self):
        """
        Hardens the sandbox by creating a virtual environment and pre-installing
        essential libraries (pandas, requests) to avoid dependency loops.
        """
        import subprocess
        logger.info("🛠️ Provisioning sandbox environment (venv + essentials + data science)...")
        try:
            venv_dir = os.path.join(self._sandbox_dir, "venv")
            if os.path.isdir(venv_dir):
                logger.info("✅ Sandbox venv already exists; skipping provisioning.")
                return

            # Create venv
            subprocess.run(["python3", "-m", "venv", "venv"], cwd=self._sandbox_dir, check=True)

            # Install essentials
            pip_path = os.path.join(self._sandbox_dir, "venv", "bin", "pip")
            subprocess.run([pip_path, "install", "--upgrade", "pip", "pandas", "requests", "yfinance", "scikit-learn", "matplotlib", "beautifulsoup4"],
                           cwd=self._sandbox_dir, check=True, capture_output=True)

            logger.info("✅ Sandbox provisioned successfully.")
        except Exception as e:
            logger.warning(f"⚠️ Sandbox provisioning failed: {e}. Agent will handle manually.")

    def _path_exists(self, path: str) -> bool:
        """Internal helper for the verification gate."""
        try:
            full_path = self._resolve_path(path)
            import os
            return os.path.exists(full_path)
        except Exception:
            return False

    def _resolve_path(self, path: str) -> str:
        """Helper to resolve sandbox vs absolute paths."""
        if path.startswith("/") or "~" in path:
            import os
            return os.path.expanduser(path)
        
        # Sandbox fallback
        import os
        base = self._sandbox_dir or "."
        return os.path.abspath(os.path.join(base, path))
