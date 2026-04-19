"""
memory_skill_tools.py — Long-term memory tools for the Jarvis agent.

Gives the agent the ability to store and retrieve facts that persist
across sessions, via the MemoryManager Tier 4 (Long-Term Knowledge).

Tools registered here:
  remember_fact — Store a fact permanently (survives restarts).
  recall_fact   — Retrieve a previously stored fact.
"""

import logging
from .base import AgentTool

logger = logging.getLogger(__name__)


class RememberFactTool(AgentTool):
    name = "remember_fact"
    description = (
        "Store a fact in Jarvis's permanent long-term memory (survives restarts). "
        "Use for user preferences, contact details, frequently used file paths, or any "
        "information the user wants Jarvis to always know. "
        "Input: {'key': str, 'value': str}. "
        "Example: {'key': 'user_city', 'value': 'Bengaluru'}"
    )
    permission = "safe"

    def run(self, inp: dict) -> str:
        key = str(inp.get("key", "")).strip()
        value = inp.get("value")

        if not key:
            return "Error: 'key' is required to remember a fact."
        if value is None:
            return "Error: 'value' is required to remember a fact."

        memory = self.cp.registry.get("memory")
        if not memory:
            return "Error: MemoryManager service is not available."

        try:
            memory.know(key, value)
            logger.info(f"🧠 RememberFactTool: stored '{key}' = '{str(value)[:60]}'")
            return f"✅ I've stored: **{key}** = {value}. I'll remember this permanently."
        except Exception as e:
            logger.error(f"RememberFactTool error: {e}")
            return f"Error storing fact: {str(e)}"


class RecallFactTool(AgentTool):
    name = "recall_fact"
    description = (
        "Retrieve a fact previously stored in Jarvis's long-term memory. "
        "Input: {'key': str}. "
        "Example: {'key': 'user_city'} → returns 'Bengaluru'"
    )
    permission = "safe"

    def run(self, inp: dict) -> str:
        key = str(inp.get("key", "")).strip()

        if not key:
            return "Error: 'key' is required to recall a fact."

        memory = self.cp.registry.get("memory")
        if not memory:
            return "Error: MemoryManager service is not available."

        try:
            value = memory.lookup(key)
            if value is None:
                # Also try session memory as a fallback
                value = memory.recall(key)
            if value is None:
                return f"I don't have any stored memory for key '{key}'."
            logger.debug(f"🧠 RecallFactTool: recalled '{key}' = '{str(value)[:60]}'")
            return f"Recalled from memory — **{key}**: {value}"
        except Exception as e:
            logger.error(f"RecallFactTool error: {e}")
            return f"Error recalling fact: {str(e)}"


class SessionMemoryTool(AgentTool):
    name = "session_memory"
    description = (
        "Store or retrieve a fact for the current session only "
        "(does NOT persist after Jarvis restarts). "
        "Useful for temporary context like 'the user asked about X' or 'last result was Y'. "
        "Input: {'action': 'store'|'retrieve', 'key': str, 'value': str (for store)}."
    )
    permission = "safe"

    def run(self, inp: dict) -> str:
        action = str(inp.get("action", "retrieve")).lower()
        key = str(inp.get("key", "")).strip()

        if not key:
            return "Error: 'key' is required."

        memory = self.cp.registry.get("memory")
        if not memory:
            return "Error: MemoryManager service is not available."

        try:
            if action == "store":
                value = inp.get("value", "")
                memory.remember(key, value, ttl_seconds=3600)
                return f"✅ Stored in session memory: {key} = {value}"
            else:
                value = memory.recall(key)
                if value is None:
                    return f"No session memory found for key '{key}'."
                return f"Session memory — {key}: {value}"
        except Exception as e:
            logger.error(f"SessionMemoryTool error: {e}")
            return f"Error accessing session memory: {str(e)}"
