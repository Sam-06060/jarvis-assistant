"""
planner.py — TaskPlanner for the Jarvis agent.

Before the execution loop begins, the TaskPlanner decomposes a raw task
into a validated, ordered plan of steps with dependency edges and tool
requirements. This prevents the agent from mixing planning and execution
in the same reasoning step.

Complexity tiers:
  "trivial"  — Single clear atomic action (< 8 words, no multi-step signals).
               Returns a 1-step plan with no LLM call.
  "simple"   — 2-3 steps, clear tool requirements.
               Uses one fast LLM call.
  "complex"  — Multi-step with dependencies between steps.
               Uses one structured LLM call (JSON output).
  "research" — Information gathering + synthesis + optional delivery.
               Uses one structured LLM call with research-specific framing.
"""

import re
import json
import uuid
import logging
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PlanStep:
    id: int
    description: str
    tool: str                          # Primary tool to use for this step
    depends_on: List[int] = field(default_factory=list)   # step IDs whose output is needed
    input_from_step: Optional[int] = None  # Inject output of this step as input (cross-step chaining)
    expected_output_type: str = "text" # "text" | "data" | "action_confirmed" | "file"
    can_parallelize: bool = False
    is_best_effort: bool = False       # True if required tool is missing from registry


@dataclass
class Plan:
    goal: str
    task_id: str
    steps: List[PlanStep]
    complexity: str                    # "trivial" | "simple" | "complex" | "research"

    def ordered_steps(self) -> List[PlanStep]:
        """Return steps in dependency order (simple topological sort)."""
        resolved = []
        resolved_ids = set()
        remaining = list(self.steps)

        while remaining:
            progress = False
            for step in list(remaining):
                if all(dep in resolved_ids for dep in step.depends_on):
                    resolved.append(step)
                    resolved_ids.add(step.id)
                    remaining.remove(step)
                    progress = True
            if not progress:
                # Circular dependency — just append the rest as-is
                resolved.extend(remaining)
                break
        return resolved

    def summary(self) -> str:
        lines = [f"Plan [{self.complexity.upper()}] — {len(self.steps)} step(s):"]
        for s in self.steps:
            dep = f" (needs step {s.depends_on})" if s.depends_on else ""
            lines.append(f"  {s.id}. [{s.tool}] {s.description}{dep}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Complexity Signals (mirrors improved _is_complex_query logic)
# ─────────────────────────────────────────────────────────────────────────────

_MULTI_STEP_SIGNALS = [
    " and then ", " after that ", " followed by ",
    " then ", " afterwards ", " next, ", " finally, ",
]

_ACTION_VERBS = [
    "search", "find", "get", "fetch", "look up",
    "email", "send", "write", "create", "generate",
    "open", "play", "calculate", "translate", "summarize",
    "analyze", "compare", "research", "book", "schedule",
]

_RESEARCH_SIGNALS = [
    "compare ", "analyze ", "analyse ", "research ", "investigate ",
    "summarize this", "write a report", "make a plan",
    "pros and cons", "best options", "top options",
    "top ", "best ", "difference between",
]

_MUSIC_GUARD = {"play", "song", "music", "spotify", "track", "album"}


# ─────────────────────────────────────────────────────────────────────────────
# TaskPlanner
# ─────────────────────────────────────────────────────────────────────────────

class TaskPlanner:
    """
    Decomposes a user task into an ordered, dependency-aware Plan.

    Usage:
        planner = TaskPlanner(brain=brain, skill_registry=skill_registry)
        plan = planner.plan(task="Research best Python frameworks and email John",
                            available_tools=["web_search", "send_email"],
                            task_id="abc-123")
        print(plan.summary())
    """

    # Max tokens for the planner LLM call (use a fast/cheap model for this)
    _PLAN_MAX_TOKENS = 512

    def __init__(self, brain, skill_registry=None):
        self.brain = brain
        self.registry = skill_registry

    # ─────────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────────

    def plan(
        self,
        task: str,
        available_tools: List[str],
        task_id: Optional[str] = None,
    ) -> Plan:
        """
        Generate a Plan for the given task.

        Args:
            task:            Raw user task string.
            available_tools: List of registered tool/skill IDs.
            task_id:         Optional UUID; generated if not provided.

        Returns:
            A validated Plan object.
        """
        task_id = task_id or str(uuid.uuid4())
        complexity = self._classify_complexity(task)

        logger.info(f"📋 TaskPlanner: complexity={complexity} task='{task[:60]}'")

        market_plan = self._market_data_plan(task, available_tools, task_id, complexity)
        if market_plan:
            return market_plan

        # Trivial tasks: skip LLM entirely, return a single-step plan
        if complexity == "trivial":
            best_tool = self._guess_tool(task, available_tools)
            return Plan(
                goal=task,
                task_id=task_id,
                steps=[PlanStep(
                    id=1,
                    description=task,
                    tool=best_tool,
                    expected_output_type="text",
                )],
                complexity="trivial",
            )

        # For all other complexities: use LLM to decompose
        steps = self._llm_decompose(task, available_tools, complexity)

        # Validate that required tools exist
        steps = self._validate_tools(steps, available_tools)

        plan = Plan(goal=task, task_id=task_id, steps=steps, complexity=complexity)
        logger.info(f"📋 {plan.summary()}")
        return plan

    def replan(self, original_plan: Plan, failed_step: PlanStep, reason: str) -> Plan:
        """
        Generate an alternative plan when a step fails with no retry budget.
        Removes the failed step and tries to find an alternative tool.
        """
        logger.warning(
            f"🔄 Replanning: step {failed_step.id} failed — {reason}"
        )
        available = [
            e.id for e in self.registry.get_all()
        ] if self.registry else []

        # Find alternative tools (exclude the failed one)
        alt_tools = [t for t in available if t != failed_step.tool]

        new_steps = []
        for step in original_plan.steps:
            if step.id == failed_step.id:
                # Replace with best-effort alternative
                alt = self._guess_tool(step.description, alt_tools)
                new_steps.append(PlanStep(
                    id=step.id,
                    description=step.description,
                    tool=alt,
                    depends_on=step.depends_on,
                    expected_output_type=step.expected_output_type,
                    is_best_effort=True,
                ))
            else:
                new_steps.append(step)

        return Plan(
            goal=original_plan.goal,
            task_id=original_plan.task_id,
            steps=new_steps,
            complexity=original_plan.complexity,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Complexity Classification (no LLM)
    # ─────────────────────────────────────────────────────────────────────────

    def _classify_complexity(self, task: str) -> str:
        """
        Complexity is determined by the number of DISTINCT DELIVERABLES the user wants,
        not by verb count or word length. This prevents over-engineering.

        Tiers:
          trivial  — 0-1 deliverable, single atomic action
          simple   — 2-3 deliverables, direct tool chain
          complex  — 4+ deliverables OR genuine research/build tasks
        """
        text = task.lower()
        words = text.split()
        wc = len(words)

        # Music guard — never plan a music command as complex
        if _MUSIC_GUARD & set(words):
            return "trivial"

        # Trivial: short commands with no connectors
        if wc < 10 and "\n" not in task and not any(s in text for s in _MULTI_STEP_SIGNALS):
            return "trivial"

        # Market data is ALWAYS simple regardless of length — direct tool available
        from modules.live_data_service import LiveDataService
        is_market = LiveDataService.is_market_data_query(task)
        if is_market:
            return "simple"

        # Count distinct DELIVERABLES (what the user wants as output)
        # These are concrete outcomes: a file, an email, a message, a web result
        deliverable_signals = [
            ("save", "file", "write", "create", ".md", ".txt", ".py", ".json"),  # file
            ("email", "mail", "send email"),                                        # email
            ("message", "whatsapp", "text", "imessage"),                             # message
            ("search", "look up", "find", "research", "web"),                       # web lookup
            ("remind", "alarm", "timer", "schedule"),                               # reminder
            ("play", "music", "song", "spotify"),                                   # media
            ("weather", "forecast", "temperature"),                                 # weather
            ("calculate", "compute", "math"),                                       # calc
        ]
        deliverable_count = sum(
            1 for group in deliverable_signals
            if any(kw in text for kw in group)
        )

        if deliverable_count <= 1:
            return "trivial"
        if deliverable_count <= 3:
            return "simple"

        # Genuine research/build requests still go complex
        has_research = any(s in text for s in _RESEARCH_SIGNALS)
        if has_research or (wc >= 35 and ("\n" in task or "://" in task)):
            return "complex"

        # Explicit multi-step language
        if any(s in text for s in _MULTI_STEP_SIGNALS):
            return "complex"

        return "simple"

    # ─────────────────────────────────────────────────────────────────────────
    # LLM Decomposition
    # ─────────────────────────────────────────────────────────────────────────

    def _llm_decompose(
        self, task: str, available_tools: List[str], complexity: str
    ) -> List[PlanStep]:
        """
        Tool-aware plan decomposition.
        Injects actual tool names+descriptions so the LLM maps to REAL tools,
        not abstract fictional steps. Caps plans at 5 steps (simple) or 8 (complex).
        """
        # Build a compact tool reference — name + one-line description
        tool_lines = []
        if self.registry:
            for entry in self.registry.get_all():
                if entry.id in available_tools:
                    desc = (entry.description or "")[:80]
                    tool_lines.append(f"  - {entry.id}: {desc}")
        if not tool_lines:
            # Fallback: plain list
            tool_lines = [f"  - {t}" for t in available_tools[:20]]
        tools_desc = "\n".join(tool_lines) or "  - web_search\n  - write_file"

        max_steps = 5 if complexity == "simple" else 8

        if complexity == "complex":
            mandate = (
                "### COMPLEX TASK MANDATE:\n"
                "Break into logical dependency steps.\n"
                "Use the sandbox (run_command) for code generation/testing.\n"
                "Only use search_awesome_skills for genuinely novel tasks with no direct tool."
            )
        else:
            mandate = (
                "### PRAGMATIC MANDATE (SIMPLE TASK):\n"
                "Map EACH user deliverable to EXACTLY ONE tool call.\n"
                "NEVER add research, methodology-verification, or configuration steps.\n"
                "NEVER use run_command to write email scripts — use send_email tool directly.\n"
                "NEVER use run_command to fetch market data — use get_market_data directly.\n"
                "'me' / 'myself' as recipient = use USER_EMAIL from system context directly."
            )

        system = (
            "You are JARVIS task planner. Output ONLY valid JSON — no prose, no markdown fences.\n"
            "GOLDEN RULE: Every step maps to exactly one tool from the Available Tools list.\n"
            "FORBIDDEN steps: 'research methodology', 'configure X', 'verify cross-source', "
            "'identify calculation method', 'set up environment'. These are hallucinated steps.\n"
            "If a direct tool exists for the action, USE IT. Never write code when a tool handles it."
        )

        prompt = (
            f"Decompose this task into at most {max_steps} ordered steps.\n\n"
            f"Available Tools:\n{tools_desc}\n\n"
            f"Task: {task}\n\n"
            f"{mandate}\n\n"
            "Output ONLY a JSON array. Each object must have:\n"
            '  {"id": int, "description": "short action", "tool": "exact_tool_name", '
            '"depends_on": [list of step ids], "output_type": "text"|"file"|"data"|"action_confirmed"}\n\n'
            "Example for \'get gold price, save to file, email me\':\n"
            '[{"id":1,"description":"Get live gold price","tool":"get_market_data","depends_on":[],"output_type":"data"},\n'
            ' {"id":2,"description":"Save price data to ~/Desktop/gold.md","tool":"write_file","depends_on":[1],"output_type":"file"},\n'
            ' {"id":3,"description":"Email results to user","tool":"send_email","depends_on":[1],"output_type":"action_confirmed"}]'
        )

        try:
            raw = self.brain.ask(prompt, system_prompt=system, is_agentic=False)
            if not raw:
                raise ValueError("Empty response from LLM")
            steps = self._parse_plan(raw.strip(), available_tools)
            # Hard-cap
            return steps[:max_steps]
        except Exception as e:
            logger.warning(f"📋 TaskPlanner LLM decompose failed ({e}) — falling back to single-step.")
            best_tool = self._guess_tool(task, available_tools)
            return [PlanStep(id=1, description=task, tool=best_tool)]

    def _parse_plan(self, raw: str, available_tools: List[str]) -> List[PlanStep]:
        """Parse LLM JSON output into PlanStep list. Robust to minor formatting issues."""
        # Strip markdown fences if present
        raw = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`")

        # Find the JSON array
        start = raw.find("[")
        end = raw.rfind("]")
        if start == -1 or end == -1:
            raise ValueError(f"No JSON array found in: {raw[:200]}")

        data = json.loads(raw[start:end + 1])
        steps = []
        for item in data:
            tool = item.get("tool", "web_search")
            # Validate tool exists; fall back gracefully
            if tool not in available_tools and available_tools:
                tool = self._guess_tool(item.get("description", ""), available_tools)
                is_best_effort = True
            else:
                is_best_effort = False

            steps.append(PlanStep(
                id=int(item.get("id", len(steps) + 1)),
                description=item.get("description", "Execute step"),
                tool=tool,
                depends_on=[int(d) for d in item.get("depends_on", [])],
                expected_output_type=item.get("output_type", "text"),
                is_best_effort=is_best_effort,
            ))
        return steps if steps else [PlanStep(id=1, description="Execute task", tool="web_search")]

    def _market_data_plan(
        self,
        task: str,
        available_tools: List[str],
        task_id: str,
        complexity: str,
    ) -> Optional[Plan]:
        """Deterministic fast plan for simple live market data tasks."""
        try:
            from modules.live_data_service import LiveDataService
            if not LiveDataService.is_market_data_query(task):
                return None
        except Exception:
            return None

        text = task.lower()
        complex_terms = [
            "compare", "analyze", "analyse", "research", "report", "forecast",
            "trend", "historical", "history", "chart", "graph", "portfolio",
            "backtest", "strategy", "why", "explain", "deep dive", "top ",
            "best ", "volatility", "moving average",
        ]
        # Deep research or complex trend analysis still requires the LLM decomposition
        if complexity == "research" or any(term in text for term in complex_terms):
            return None

        asks_delivery = any(k in text for k in ("email", "mail", "send it", "send me"))
        asks_save = any(k in text for k in ("save", "file", "write", "record", "goldybhai.md", ".md", ".txt"))
        
        market_tool = "get_market_data" if "get_market_data" in available_tools else (
            "web_search" if "web_search" in available_tools else self._guess_tool(task, available_tools)
        )

        steps = [PlanStep(
            id=1,
            description=f"Get the live market data: {task}",
            tool=market_tool,
            expected_output_type="data",
        )]

        current_id = 2
        if asks_save and "write_file" in available_tools:
            # Try to extract filename
            fname = "market_data.md"
            if "goldybhai.md" in text: fname = "goldybhai.md"
            elif ".md" in text: 
                match = re.search(r"(\w+\.md)", text)
                if match: fname = match.group(1)
            
            steps.append(PlanStep(
                id=current_id,
                description=f"Save the retrieved data to {fname} on the Desktop.",
                tool="write_file",
                depends_on=[1],
                input_from_step=1,
                expected_output_type="file",
            ))
            current_id += 1

        if asks_delivery and "send_email" in available_tools:
            steps.append(PlanStep(
                id=current_id,
                description="Email the results to the user.",
                tool="send_email",
                depends_on=[1],
                input_from_step=1,
                expected_output_type="action_confirmed",
            ))

        return Plan(goal=task, task_id=task_id, steps=steps, complexity=complexity)

    # ─────────────────────────────────────────────────────────────────────────
    # Tool Validation
    # ─────────────────────────────────────────────────────────────────────────

    def _validate_tools(self, steps: List[PlanStep], available: List[str]) -> List[PlanStep]:
        """Mark steps as best-effort if their required tool is not registered."""
        for step in steps:
            if step.tool not in available:
                logger.warning(
                    f"📋 Step {step.id}: tool '{step.tool}' not in registry — marking best_effort."
                )
                step.is_best_effort = True
                step.tool = self._guess_tool(step.description, available)
        return steps

    def _guess_tool(self, description: str, available: List[str]) -> str:
        """
        Heuristic: pick the most likely tool from available based on description keywords.
        Never returns a tool that isn't in available.
        """
        if not available:
            return "web_search"

        desc = description.lower()
        priority_map = [
            (["research", "analyze", "analyse", "compare", "report", "deep dive"], "web_search"),
            (["send", "message", "whatsapp", "imessage"], "send_message"),
            (["email", "mail"],                            "send_email"),
            (["gold", "silver", "oil", "stock", "share", "market", "crypto", "bitcoin", "ethereum", "currency", "forex", "exchange rate", "price", "rate"], "get_market_data"),
            (["play", "music", "song", "spotify"],         "control_music"),
            (["weather", "temperature", "rain"],           "get_weather"),
            (["calculate", "math"],                        "calculator"),
            (["remind", "reminder"],                       "manage_reminders"),
            (["file", "write", "save", "create file"],     "write_file"),
            (["url", "fetch", "webpage"],                  "fetch_url"),
            (["time", "date", "clock"],                    "get_time"),
            (["remember", "store", "memorise"],            "remember_fact"),
            (["recall", "lookup"],                         "recall_fact"),
            (["system", "battery", "cpu", "volume"],       "get_system_status"),
            (["ac", "air conditioning"],                   "control_ac"),
        ]

        for keywords, tool_id in priority_map:
            if tool_id in available and any(k in desc for k in keywords):
                return tool_id

        # Default: web_search if available, else first tool
        return "web_search" if "web_search" in available else available[0]
