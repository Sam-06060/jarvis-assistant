from abc import ABC, abstractmethod

class AgentTool(ABC):
    """
    Base class for all Agentic Mode Tools.
    Any class inheriting from this in the modules/agent_tools directory
    will be automatically discovered and loaded by the JARVIS backend.
    """
    name: str = "undefined_tool"
    description: str = "Missing description"
    tier: int = 1  # DEPRECATED — kept for backward compat; use `permission` instead.

    # ── 3-Tier Permission Model ──────────────────────────────────────────
    #   "safe"        — Auto-execute, no prompt. Read-only or internal ops.
    #                   (e.g. web_search, get_weather, calculator, recall_fact)
    #   "write"       — Auto-execute with logging. Creates/modifies files.
    #                   (e.g. write_file, finalize_project, apply_code_change)
    #   "destructive" — Requires HITL approval via socket UI. Irreversible.
    #                   (e.g. run_command, send_message, send_email, system_control)
    permission: str = "safe"

    # If True, this tool handles its OWN approval flow internally
    # (e.g. socket-based "Approve & Run" button in the Swift UI).
    # commands.py will skip the voice confirmation gate for these tools
    # to prevent a double-prompt UX.
    self_approving: bool = False

    def __init__(self, command_processor):
        """
        Injected with the centralized CommandProcessor containing context, memory, and routing.
        """
        self.cp = command_processor

    @abstractmethod
    def run(self, args: dict):
        """
        Executes the tool with the provided arguments.
        Must return a string summarizing the result.
        """
        pass
