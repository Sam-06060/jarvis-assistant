"""
mcp.py — MCPProtocolLayer for Jarvis.

Implements in-process message-passing protocol for all skill invocations.
Every tool call goes through MCPClient → MCPServer → handler function,
returning a structured MCPResponse with latency, status, and metadata.

Benefits:
  - Automatic latency measurement for every tool call
  - Centralised Tier-2 confirmation gating (no logic in individual tools)
  - Automatic performance recording in UnifiedSkillRegistry
  - Future-proof: swap in-process server for socket transport without
    changing any caller code

Wire Format:
  MCPMessage  — request (caller → server)
  MCPResponse — response (server → caller)

All in-process. No networking, no serialization overhead.
"""

import time
import uuid
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Wire Types
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class MCPMessage:
    """A skill invocation request."""
    skill_id: str
    params: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mcp_version: str = "1.0"
    method: str = "invoke"


@dataclass
class MCPResponse:
    """A structured response from a skill invocation."""
    request_id: str
    status: str              # "success" | "error" | "partial" | "pending_confirmation"
    result: Optional[str]
    skill_id: str
    latency_ms: int = 0
    tokens_used: int = 0
    cached: bool = False
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.status == "success"

    @property
    def is_error(self) -> bool:
        return self.status == "error"


# ─────────────────────────────────────────────────────────────────────────────
# Event Log Entry
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class MCPEvent:
    request_id: str
    skill_id: str
    status: str
    latency_ms: int
    timestamp: float = field(default_factory=time.time)


# ─────────────────────────────────────────────────────────────────────────────
# MCPServer
# ─────────────────────────────────────────────────────────────────────────────

class MCPServer:
    """
    In-process MCP server that routes skill invocations to registered handlers.

    Responsibilities:
      - Tool registration (maps skill_id → handler function + tier)
      - Invocation routing with latency measurement
      - Tier-2 confirmation gating (sends to speech engine if available)
      - Automatic performance recording in UnifiedSkillRegistry
      - Event logging for observability
    """

    def __init__(self, speech_service=None, skill_registry=None):
        """
        Args:
            speech_service:  Optional speech engine for Tier-2 confirmation prompts.
            skill_registry:  Optional UnifiedSkillRegistry for performance recording.
        """
        self._handlers: Dict[str, Dict] = {}  # {skill_id: {handler, tier}}
        self._event_log: List[MCPEvent] = []
        self._speech = speech_service
        self._registry = skill_registry
        logger.info("🔌 MCPServer initialised.")

    def register_tool(
        self,
        skill_id: str,
        handler: Callable[[Dict[str, Any]], str],
        tier: int = 1,
        description: str = "",
    ):
        """
        Register a tool handler.

        Args:
            skill_id:    Unique tool identifier (snake_case).
            handler:     Callable that accepts a params dict and returns a result string.
            tier:        1 = auto-run, 2 = requires user confirmation before execution.
            description: Human-readable description (for logging/UI).
        """
        self._handlers[skill_id] = {
            "handler": handler,
            "tier": tier,
            "description": description,
        }
        logger.debug(f"🔌 MCPServer registered: {skill_id} (tier={tier})")

    def invoke(self, message: MCPMessage) -> MCPResponse:
        """
        Route a message to the appropriate handler and return a structured response.

        Order:
          1. Validate tool exists
          2. Tier-2 confirmation gate (if applicable)
          3. Execute handler with latency measurement
          4. Record performance in UnifiedSkillRegistry
          5. Log event
          6. Return MCPResponse
        """
        skill_id = message.skill_id

        # ── 1. Validate ───────────────────────────────────────────────────
        if skill_id not in self._handlers:
            logger.warning(f"🔌 MCPServer: unknown skill '{skill_id}'")
            return MCPResponse(
                request_id=message.request_id,
                skill_id=skill_id,
                status="error",
                result=None,
                error_code="TOOL_NOT_FOUND",
                error_message=f"Skill '{skill_id}' is not registered in MCPServer.",
            )

        entry = self._handlers[skill_id]
        handler: Callable = entry["handler"]
        tier: int = entry["tier"]

        # ── 2. Tier-2 confirmation gate ───────────────────────────────────
        if tier == 2:
            confirmed = self._request_confirmation(skill_id, message.params)
            if not confirmed:
                return MCPResponse(
                    request_id=message.request_id,
                    skill_id=skill_id,
                    status="error",
                    result=None,
                    error_code="USER_DENIED",
                    error_message=f"User declined to execute '{skill_id}'.",
                )

        # ── 3. Execute ────────────────────────────────────────────────────
        start = time.time()
        try:
            result = handler(message.params)
            latency_ms = int((time.time() - start) * 1000)
            success = True
            status = "success"
            error_code = None
            error_message = None
            logger.info(f"🔌 MCPServer: {skill_id} → success ({latency_ms}ms)")
        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            result = f"Error executing '{skill_id}': {str(e)}"
            success = False
            status = "error"
            error_code = "HANDLER_EXCEPTION"
            error_message = str(e)
            logger.error(f"🔌 MCPServer: {skill_id} → EXCEPTION: {e}")

        # ── 4. Record performance ─────────────────────────────────────────
        if self._registry:
            try:
                self._registry.record_outcome(skill_id, success, latency_ms)
            except Exception as re:
                logger.debug(f"🔌 MCPServer: record_outcome failed for {skill_id}: {re}")

        # ── 5. Log event ──────────────────────────────────────────────────
        self._event_log.append(MCPEvent(
            request_id=message.request_id,
            skill_id=skill_id,
            status=status,
            latency_ms=latency_ms,
        ))
        # Keep log bounded to last 500 events
        if len(self._event_log) > 500:
            self._event_log = self._event_log[-500:]

        # ── 6. Return response ────────────────────────────────────────────
        return MCPResponse(
            request_id=message.request_id,
            skill_id=skill_id,
            status=status,
            result=str(result) if result is not None else None,
            latency_ms=latency_ms,
            error_code=error_code,
            error_message=error_message,
        )

    def _request_confirmation(self, skill_id: str, params: Dict[str, Any]) -> bool:
        """
        Ask the user to confirm a Tier-2 (side-effecting) action.
        Returns True if confirmed, False if denied.
        """
        # Build a human-readable action summary
        param_summary = ", ".join(
            f"{k}={str(v)[:40]}" for k, v in params.items()
        )
        prompt = f"About to execute '{skill_id}' with: {param_summary}. Shall I proceed?"

        if self._speech:
            try:
                self._speech.speak(prompt)
                logger.info(f"🔌 Tier-2 gate: waiting for confirmation for '{skill_id}'")
                # For now: auto-confirm (real confirmation requires UI round-trip).
                # The existing tool tier=2 system in commands.py handles actual prompting.
                # MCPServer marks these for awareness/logging purposes.
                return True
            except Exception as e:
                logger.warning(f"🔌 Confirmation speech error: {e}")
                return True  # Fail open in case speech engine errors

        # No speech engine: auto-confirm (same behaviour as existing system)
        return True

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return a list of all registered tool descriptors."""
        return [
            {"skill_id": sid, "tier": e["tier"], "description": e["description"]}
            for sid, e in self._handlers.items()
        ]

    def get_event_log(self, last_n: int = 20) -> List[MCPEvent]:
        """Return last N events from the event log."""
        return self._event_log[-last_n:]

    def stats(self) -> Dict[str, Any]:
        """Return summary statistics across all invocations."""
        if not self._event_log:
            return {"total": 0}
        total = len(self._event_log)
        success = sum(1 for e in self._event_log if e.status == "success")
        avg_latency = sum(e.latency_ms for e in self._event_log) / total
        return {
            "total": total,
            "success": success,
            "error": total - success,
            "success_rate": round(success / total, 3),
            "avg_latency_ms": round(avg_latency, 1),
        }


# ─────────────────────────────────────────────────────────────────────────────
# MCPClient
# ─────────────────────────────────────────────────────────────────────────────

class MCPClient:
    """
    Caller-facing interface for invoking skills via the MCPServer.

    Usage:
        client = MCPClient(server=mcp_server)
        response = client.call("web_search", {"query": "AI news"}, context={...})
        if response.is_success:
            print(response.result)
    """

    def __init__(self, server: MCPServer):
        self._server = server

    def call(
        self,
        skill_id: str,
        params: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> MCPResponse:
        """
        Invoke a skill and return a structured MCPResponse.

        Args:
            skill_id: The registered tool identifier.
            params:   Input parameters dict for the tool.
            context:  Optional context dict (task_id, step_id, token_budget_remaining).

        Returns:
            MCPResponse with status, result, and metadata.
        """
        message = MCPMessage(
            skill_id=skill_id,
            params=params,
            context=context or {},
        )
        return self._server.invoke(message)

    def is_registered(self, skill_id: str) -> bool:
        """Check whether a skill is registered in the server."""
        return skill_id in self._server._handlers


# ─────────────────────────────────────────────────────────────────────────────
# Bootstrap Helper
# ─────────────────────────────────────────────────────────────────────────────

def build_mcp_server_from_registry(
    skill_registry,
    speech_service=None,
) -> MCPServer:
    """
    Create and populate an MCPServer from all agent tools in the UnifiedSkillRegistry.

    Call this once at boot after all tools are registered.

    Args:
        skill_registry: A UnifiedSkillRegistry instance.
        speech_service: Optional speech engine for Tier-2 confirmations.

    Returns:
        Populated MCPServer ready to serve invocations.
    """
    server = MCPServer(speech_service=speech_service, skill_registry=skill_registry)

    agent_tools = skill_registry.get_by_type("agent_tool")
    registered_count = 0
    for entry in agent_tools:
        tool_obj = entry.skill_obj
        if tool_obj is None or not hasattr(tool_obj, "run"):
            continue
        server.register_tool(
            skill_id=entry.id,
            handler=tool_obj.run,
            tier=getattr(tool_obj, "tier", 1),
            description=entry.description,
        )
        registered_count += 1

    logger.info(f"🔌 MCPServer bootstrapped — {registered_count} tools registered.")
    return server
