"""
sandbox_tools.py — Sandbox-Isolated File Writing & Project Finalization

The "Workspace vs. Delivery" pattern:
  1. SandboxWriteFileTool — writes files ONLY inside ~/.jarvis_sandbox/{task_id}/
     UNLESS the user explicitly provides an absolute destination path.
  2. FinalizeProjectTool — copies the finished project from sandbox to the
     user's requested location and deletes the sandbox.

This eliminates the version1/version2/attempt3/ duplication anti-pattern.
"""

import os
import shutil
import logging
from .base import AgentTool

logger = logging.getLogger(__name__)

_SANDBOX_ROOT = os.path.join(os.path.expanduser("~"), ".jarvis_sandbox")


class SandboxWriteFileTool(AgentTool):
    """
    Writes files to the sandbox or to an explicit absolute path.

    Rules:
      - Relative paths (e.g. "src/app.py") are written inside the sandbox.
      - Absolute paths with explicit user-specified destinations
        (e.g. ~/Desktop/notes.md) bypass the sandbox.
      - Paths containing "version", "attempt", "v1", "v2" etc. are REJECTED.
    """
    name = "write_file"
    description = (
        "Write content to a file. Relative paths go to the sandbox; "
        "absolute paths go directly. "
        "Input: {'path': str, 'content': str}. "
        "Example: {'path': 'src/app.py', 'content': '...'}"
    )
    permission = "write"

    # Patterns that signal the duplication anti-pattern
    _DUPLICATION_PATTERNS = (
        "version1", "version2", "version3",
        "attempt1", "attempt2", "attempt3",
        "v1/", "v2/", "v3/",
        "_old/", "_new/", "_backup/",
    )

    def run(self, inp: dict) -> str:
        raw_path = inp.get("path", "").strip()
        content = inp.get("content", "")

        if not raw_path:
            return "Error: No path provided."

        # ── Anti-duplication guard ─────────────────────────────────────
        path_lower = raw_path.lower()
        for pattern in self._DUPLICATION_PATTERNS:
            if pattern in path_lower:
                return (
                    f"[!] REJECTED: Path '{raw_path}' contains a duplication "
                    f"pattern ('{pattern}'). You MUST NOT create versioned "
                    f"directories. Overwrite existing files in-place or delete "
                    f"them first with run_command."
                )

        # ── Resolve path ───────────────────────────────────────────────
        if os.path.isabs(raw_path) or raw_path.startswith("~"):
            # Explicit absolute destination — bypass sandbox
            full_path = os.path.expanduser(raw_path)
        else:
            # Relative path — route to sandbox
            sandbox_dir = self._get_sandbox_dir()
            if not sandbox_dir:
                # Fallback: write to user's Desktop if no sandbox is active
                full_path = os.path.join(
                    os.path.expanduser("~/Desktop"), raw_path
                )
            else:
                full_path = os.path.join(sandbox_dir, raw_path)

        # ── Security: prevent directory traversal ──────────────────────
        if ".." in full_path:
            return "Error: Directory traversal (..) is forbidden."

        # ── Write ──────────────────────────────────────────────────────
        try:
            # Guard: prevent interactive input() in Python scripts (causes subprocess hang)
            if raw_path.endswith(".py") and "input(" in content:
                return (
                    "ERROR: You are attempting to write a Python script that "
                    "contains an interactive `input()` function. Interactive "
                    "inputs will cause your agentic subprocess to hang "
                    "indefinitely! You MUST rewrite this code to use hardcoded "
                    "test constants or `sys.argv` instead."
                )
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"✅ Successfully wrote {len(content)} chars to {full_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def _get_sandbox_dir(self) -> str:
        """
        Find the active sandbox directory for the current task.
        Looks for agent_core's _sandbox_dir via the registry.
        """
        try:
            agent = getattr(self.cp.registry.get("app"), "agent", None)
            if agent and hasattr(agent, "_sandbox_dir"):
                return agent._sandbox_dir
        except Exception:
            pass
        # Fallback: check if a task-scoped sandbox exists in memory_vault
        if hasattr(self.cp, "memory_vault") and isinstance(self.cp.memory_vault, dict):
            return self.cp.memory_vault.get("_sandbox_dir", "")
        return ""


class FinalizeProjectTool(AgentTool):
    """
    Copies the finalized project from the sandbox to the user's
    requested destination and deletes the sandbox.
    """
    name = "finalize_project"
    description = (
        "Copy the completed project from the sandbox to the final "
        "destination and clean up. Use this ONLY after all code passes "
        "testing. Input: {'destination': str}. "
        "Example: {'destination': '~/Desktop/my-express-app'}"
    )
    permission = "write"

    def run(self, inp: dict) -> str:
        destination = inp.get("destination", "").strip()
        if not destination:
            return "Error: No destination path provided."

        destination = os.path.expanduser(destination)

        # Find the active sandbox
        sandbox_dir = self._get_sandbox_dir()
        if not sandbox_dir or not os.path.exists(sandbox_dir):
            return (
                "Error: No active sandbox found. Either you haven't written "
                "any files yet, or the sandbox was already finalized."
            )

        # Verify sandbox has content
        sandbox_contents = os.listdir(sandbox_dir)
        if not sandbox_contents:
            return "Error: Sandbox is empty — no files to finalize."

        try:
            # If destination exists, merge (overwrite files, keep extras)
            if os.path.exists(destination):
                # Copy tree with overwrite
                for item in sandbox_contents:
                    src = os.path.join(sandbox_dir, item)
                    dst = os.path.join(destination, item)
                    if os.path.isdir(src):
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                    else:
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst)
            else:
                # Fresh copy
                shutil.copytree(sandbox_dir, destination)

            # Clean up sandbox
            shutil.rmtree(sandbox_dir, ignore_errors=True)

            file_count = sum(
                len(files) for _, _, files in os.walk(destination)
            )
            return (
                f"✅ Project finalized successfully!\n"
                f"  📁 Destination: {destination}\n"
                f"  📄 Files: {file_count}\n"
                f"  🧹 Sandbox cleaned up."
            )
        except Exception as e:
            return f"Error finalizing project: {str(e)}"

    def _get_sandbox_dir(self) -> str:
        """Find the active sandbox directory."""
        try:
            agent = getattr(self.cp.registry.get("app"), "agent", None)
            if agent and hasattr(agent, "_sandbox_dir"):
                return agent._sandbox_dir
        except Exception:
            pass
        if hasattr(self.cp, "memory_vault") and isinstance(self.cp.memory_vault, dict):
            return self.cp.memory_vault.get("_sandbox_dir", "")
        return ""
