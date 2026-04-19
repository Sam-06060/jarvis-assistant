"""
plan_mode.py — Jarvis Plan Mode

Generates a senior-engineer quality PLAN.md for complex tasks, sends it to the
Swift UI for inline rendering, and waits for user approval before executing.

Socket protocol:
  Python → Swift:     {"type": "plan_render", "plan": {...}}
  Swift  → Python:    {"type": "plan_approval", "approved": true|false}
"""

import os
import re
import json
import uuid
import logging
import threading
from dataclasses import dataclass, field
from typing import List, Optional, Any

import config

logger = logging.getLogger(__name__)

_PLAN_DIR = getattr(config, "PLAN_PROJECTS_DIR", os.path.expanduser("~/Jarvis/Projects"))


# ──────────────────────────────────────────────────────────────────────────────
# Data Models
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class PlanModeStep:
    number: int
    title: str
    description: str
    tool: str
    expected_output: str = "text"


@dataclass
class PlanDocument:
    project_slug: str
    folder_path: str
    goal: str
    steps: List[PlanModeStep]
    status: str = "work_not_yet_assigned"   # → "approved" → "in_progress" → "completed"
    plan_md_path: str = ""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "project_slug": self.project_slug,
            "folder_path": self.folder_path,
            "goal": self.goal,
            "status": self.status,
            "plan_md_path": self.plan_md_path,
            "steps": [
                {
                    "number": s.number,
                    "title": s.title,
                    "description": s.description,
                    "tool": s.tool,
                    "expected_output": s.expected_output,
                }
                for s in self.steps
            ],
        }

    def render_markdown(self) -> str:
        """Render the plan as a Markdown string for the PLAN.md file and chat UI."""
        lines = [
            f"# Plan: {self.goal}",
            "",
            f"**Status**: {self.status.replace('_', ' ').title()}",
            f"**Project**: `{self.project_slug}`",
            "",
            "## Steps",
            "",
        ]
        for s in self.steps:
            lines.append(f"### Step {s.number}: {s.title}")
            lines.append(f"**Tool**: `{s.tool}`")
            lines.append(f"{s.description}")
            lines.append(f"*Expected output*: {s.expected_output}")
            lines.append("")
        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Plan Mode Engine
# ──────────────────────────────────────────────────────────────────────────────

class PlanMode:
    """
    Generates, renders, and manages implementation plans for complex tasks.
    Integrates with the socket server to request user approval before execution.
    """

    def __init__(self, brain, registry):
        self.brain = brain
        self.registry = registry
        self._approval_events: dict = {}   # task_id → threading.Event
        self._approval_results: dict = {}  # task_id → bool

    # ── Plan Generation ──────────────────────────────────────────────────────

    def create_plan(self, task: str, available_tools: List[str]) -> PlanDocument:
        """
        Use the LLM to generate a structured plan, write PLAN.md, and return a PlanDocument.
        """
        slug = self._slugify(task)
        folder_path = os.path.join(_PLAN_DIR, slug)
        os.makedirs(folder_path, exist_ok=True)

        steps = self._deterministic_plan(task, available_tools)
        if not steps:
            steps = []

        # LLM call to generate a structured JSON plan
        tools_preview = ", ".join(available_tools[:15]) or "web_search, write_file, run_command"
        system_prompt = (
            "You are JARVIS, a world-class Senior Software Architect and Principal Engineer. "
            "Your task is to generate a flawless, professional implementation plan for the user's request.\n\n"
            "Each step must follow these high-quality engineering standards:\n"
            "1. ATOMICITY: Each step must be a single, testable unit of work.\n"
            "2. DEFENSIVE DESIGN: Include validation steps (e.g., 'Check if file exists', 'Verify data integrity').\n"
            "3. STRATEGIC SEQUENCING: Prioritize data gathering before modification.\n"
            "4. TOOL PRECISION: Choose the absolute best tool for the job. Use specialized tools (get_market_data) over generic ones (web_search) whenever possible.\n\n"
            "Expected JSON Schema (Array of Steps):\n"
            '  {"number": int, "title": str, "description": str, "tool": str, "expected_output": str}\n\n'
            f"Available tools: {tools_preview}\n\n"
            "RULES:\n"
            "- 3-6 steps maximum. Be concise but thorough.\n"
            "- 'description': Provide a technical objective for the agent executor.\n"
            "- 'expected_output': Define a clear, verifiable success condition.\n"
            "- Do NOT use `run_command` for tasks where a safe tool (web_search, write_file) exists.\n"
            "- For messaging tasks, ensure the message content is generated or retrieved FIRST.\n"
            "- Output ONLY valid JSON array. No markdown, no prose, no conversational filler."
        )
        user_prompt = f"Plan this task: {task}"

        if not steps:
            try:
                raw = self.brain.ask(user_prompt, system_prompt=system_prompt, is_agentic=False)
                if raw:
                    cleaned = raw.strip()
                    if cleaned.startswith("```"):
                        cleaned = re.sub(r"```(?:json)?\s*(.*?)\s*```", r"\1", cleaned, flags=re.DOTALL).strip()
                    data = json.loads(cleaned)
                    if isinstance(data, list):
                        for item in data:
                            steps.append(PlanModeStep(
                                number=int(item.get("number", len(steps) + 1)),
                                title=str(item.get("title", "Step")),
                                description=str(item.get("description", "")),
                                tool=str(item.get("tool", "web_search")),
                                expected_output=str(item.get("expected_output", "text")),
                            ))
            except Exception as e:
                logger.error(f"❌ PlanMode LLM generation failed: {e}")
                # Fallback: single-step direct plan
                steps = [PlanModeStep(
                    number=1,
                    title=task[:60],
                    description=task,
                    tool="web_search" if "web_search" in available_tools else "run_command",
                    expected_output="text",
                )]

        doc = PlanDocument(
            project_slug=slug,
            folder_path=folder_path,
            goal=task,
            steps=steps,
        )

        # Write PLAN.md
        plan_md_path = os.path.join(folder_path, "PLAN.md")
        try:
            with open(plan_md_path, "w", encoding="utf-8") as f:
                f.write(doc.render_markdown())
            doc.plan_md_path = plan_md_path
            logger.info(f"📋 PLAN.md written to {plan_md_path}")
        except Exception as e:
            logger.warning(f"⚠️ Could not write PLAN.md: {e}")

        return doc

    def _deterministic_plan(self, task: str, available_tools: List[str]) -> List[PlanModeStep]:
        """Fast, reliable plans for obvious tasks that should not need an LLM."""
        try:
            from modules.live_data_service import LiveDataService
            if not LiveDataService.is_market_data_query(task):
                return []
        except Exception:
            return []

        text = task.lower()
        complex_terms = [
            "compare", "analyze", "analyse", "research", "report", "forecast",
            "trend", "historical", "history", "chart", "graph", "portfolio",
            "backtest", "strategy", "why", "explain", "deep dive", "top ",
            "best ", "volatility", "moving average",
        ]
        if any(term in text for term in complex_terms):
            return []

        market_tool = "get_market_data" if "get_market_data" in available_tools else "web_search"
        steps = [PlanModeStep(
            number=1,
            title="Get Live Market Data",
            description=f"Retrieve the live market quote requested by the user: {task}",
            tool=market_tool,
            expected_output="A fresh quote with symbol, price, currency, source, and timestamp.",
        )]

        if any(k in text for k in ("email", "mail")) and "send_email" in available_tools:
            steps.append(PlanModeStep(
                number=2,
                title="Email Result",
                description="Email the retrieved live quote to the user.",
                tool="send_email",
                expected_output="Email sent confirmation.",
            ))

        return steps

    # ── Socket: Send Plan to UI ───────────────────────────────────────────────

    def send_plan_to_ui(self, doc: PlanDocument) -> bool:
        """
        Broadcast the plan to Swift UI for inline rendering.
        Returns True if broadcast succeeded, False otherwise.
        """
        server = self.registry.get("socket_server")
        if not server:
            logger.warning("⚠️ PlanMode: socket_server not available — cannot send plan to UI.")
            return False

        try:
            msg = json.dumps({
                "type": "plan_render",
                "plan": doc.to_dict(),
                "markdown": doc.render_markdown(),
            }) + "\n"
            encoded = msg.encode("utf-8")
            with server.lock:
                for client in list(server.clients):
                    try:
                        client.sendall(encoded)
                    except Exception:
                        pass
            logger.info(f"📤 Plan sent to UI: {doc.project_slug}")
            return True
        except Exception as e:
            logger.error(f"❌ PlanMode send_plan_to_ui failed: {e}")
            return False

    # ── Approval Gate ─────────────────────────────────────────────────────────

    def wait_for_approval(self, doc: PlanDocument, timeout_seconds: float = 600.0) -> bool:
        """
        Block until the user approves or rejects the plan via the Swift UI.
        Returns True if approved, False if rejected or timed out.
        """
        event = threading.Event()
        self._approval_events[doc.task_id] = event
        self._approval_results[doc.task_id] = False

        logger.info(f"⏸️ PlanMode: waiting for approval (task_id={doc.task_id}, timeout={timeout_seconds}s)")
        fired = event.wait(timeout=timeout_seconds)

        result = self._approval_results.pop(doc.task_id, False)
        self._approval_events.pop(doc.task_id, None)

        if not fired:
            logger.info("⏱️ PlanMode: approval timed out — treating as rejected.")
            return False

        return result

    def receive_approval(self, task_id: str, approved: bool):
        """
        Called by socket_server when a plan_approval message arrives from Swift UI.
        """
        self._approval_results[task_id] = approved
        event = self._approval_events.get(task_id)
        if event:
            event.set()
        logger.info(f"📬 PlanMode: approval received for {task_id} → {'APPROVED' if approved else 'REJECTED'}")

    # ── Full Flow ─────────────────────────────────────────────────────────────

    def run(self, task: str, available_tools: List[str], heartbeat=None) -> dict:
        """
        Full Plan Mode flow:
        1. Create plan
        2. Send to UI
        3. Wait for approval
        Returns: {"approved": bool, "plan": PlanDocument}
        """
        if heartbeat:
            heartbeat.emit("Generating implementation plan...", "active")

        doc = self.create_plan(task, available_tools)

        if heartbeat:
            heartbeat.emit(f"📋 Plan ready — {len(doc.steps)} steps. Awaiting your approval...", "active")

        sent = self.send_plan_to_ui(doc)
        if not sent:
            # Fallback: auto-approve if no UI connection (e.g. CLI mode)
            logger.info("📋 PlanMode: no UI — auto-approving plan for CLI mode")
            return {"approved": True, "plan": doc}

        approved = self.wait_for_approval(doc)

        if heartbeat:
            if approved:
                heartbeat.emit("✅ Plan approved — starting execution", "success")
            else:
                heartbeat.emit("❌ Plan rejected by user", "failed")
                heartbeat.clear()

        return {"approved": approved, "plan": doc}

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _slugify(text: str) -> str:
        """Produce a URL-safe folder name from a task string."""
        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_-]+", "-", text)
        text = text.strip("-")[:50]
        return text or "plan"
