"""
context_compressor.py — Intelligent agent history compression.

When the agent loop's accumulated history exceeds the token budget,
this module compresses history without losing critical information.

7-step algorithm (all deterministic until step 7):
  1. Measure current token usage.
  2. If under budget: return unchanged.
  3. Identify "anchor" turns that must be preserved.
  4. Mark all other turns as compressible.
  5. Replace compressible observations with 1-line summaries.
  6. If still over budget: remove compressible turns entirely (oldest first).
  7. If STILL over budget: single LLM call to summarise anchor turns.

No LLM calls for steps 1-6. Step 7 is the emergency fallback only.
"""

import re
import logging
from typing import List

logger = logging.getLogger(__name__)


class ContextCompressor:
    """
    Compresses agent history to fit within the token budget.

    Usage:
        compressor = ContextCompressor(brain=brain)
        compressed_history = compressor.compress(history, token_budget)
    """

    # Markers that signal a turn has genuinely useful data
    _ANCHOR_KEYWORDS = (
        "Final Answer:", "final answer:", "FINAL ANSWER:",
        "Observation: ✅", "Observation: ❌",
    )

    def __init__(self, brain):
        """
        Args:
            brain: AIBrain instance — used only for the emergency LLM summarisation (step 7).
        """
        self.brain = brain

    def compress(self, history: List[str], budget) -> List[str]:
        """
        Compress history list to fit within the remaining token budget.

        Args:
            history: Current agent history (list of plain strings).
            budget:  TokenBudget instance (reads remaining() and estimate()).

        Returns:
            Compressed history list.
        """
        if not history:
            return history

        # ── STEP 1: Measure current usage ───────────────────────────────
        full_text = "\n".join(history)
        current_tokens = budget.estimate(full_text)

        # ── STEP 2: Under budget — nothing to do ─────────────────────────
        if budget.remaining() >= 1500:
            return history

        logger.info(
            f"🗜️ ContextCompressor triggered — history={current_tokens} tokens, "
            f"remaining={budget.remaining()}"
        )

        total = len(history)

        # ── STEP 3: Identify anchor turns ───────────────────────────────
        anchor_indices = set()
        anchor_indices.add(0)                                   # Turn 0: task statement
        for i, turn in enumerate(history):
            if any(kw in turn for kw in self._ANCHOR_KEYWORDS):
                anchor_indices.add(i)
        # Last 4 turns are always anchors (most recent context)
        for i in range(max(0, total - 4), total):
            anchor_indices.add(i)

        # ── STEP 4/5: Replace compressible turns with 1-line summaries ──
        compressed = []
        removed_count = 0
        for i, turn in enumerate(history):
            if i in anchor_indices:
                compressed.append(turn)
            else:
                summary = self._one_line_summary(turn)
                compressed.append(summary)

        # ── CHECK: Is it now under budget? ───────────────────────────────
        if budget.remaining() >= budget.estimate("\n".join(compressed)):
            logger.info(f"🗜️ Compression done via summaries — {len(compressed)} turns retained.")
            return compressed

        # ── STEP 6: Remove compressible turns entirely (oldest first) ───
        final = []
        for i, turn in enumerate(compressed):
            if i in anchor_indices:
                final.append(turn)
            else:
                removed_count += 1
                # Skip — don't include this turn at all

        if removed_count > 0:
            final.insert(
                1,  # Right after the task statement
                f"[🗜️ {removed_count} intermediate turns removed by compressor]"
            )

        # ── CHECK: Is it under budget now? ───────────────────────────────
        if budget.remaining() >= budget.estimate("\n".join(final)):
            logger.info(f"🗜️ Compression done by removal — {removed_count} turns dropped.")
            return final

        # ── STEP 7: Emergency LLM summarisation ─────────────────────────
        logger.warning("🗜️ Emergency LLM summarisation triggered — budget critically low.")
        summary_text = self._llm_summarise(final)
        # Replace everything except the last 3 turns with the LLM summary
        last_three = final[-3:] if len(final) >= 3 else final
        emergency_compressed = [
            final[0],   # Task statement (always anchor)
            f"[SUMMARISED HISTORY]\n{summary_text}",
        ] + last_three

        logger.info("🗜️ Emergency LLM compression complete.")
        return emergency_compressed

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _one_line_summary(self, turn: str) -> str:
        """Replace a full turn with a compact single-line summary."""
        # Extract tool name from "Action: tool_name" pattern
        tool_match = re.search(r"Action:\s*(\w+)", turn)
        tool_name = tool_match.group(1) if tool_match else "tool"

        # Extract first 80 chars of the observation
        obs_match = re.search(r"Observation:\s*(.*)", turn, re.DOTALL)
        if obs_match:
            snippet = obs_match.group(1).strip()[:80].replace("\n", " ")
        else:
            snippet = turn.strip()[:80].replace("\n", " ")

        return f"[{tool_name}: {snippet}... (compressed)]"

    def _llm_summarise(self, turns: List[str]) -> str:
        """
        Emergency: use LLM to summarise a list of turns into a compact block.
        This is the LAST resort — only called when all deterministic methods fail.
        """
        joined = "\n".join(turns)
        prompt = (
            "Summarize the following AI agent steps in under 200 words. "
            "Preserve ALL key facts: names, numbers, URLs, file paths, prices, decisions.\n\n"
            f"{joined}"
        )
        system = (
            "You are a concise technical summariser. "
            "Output only the summary. No preamble, no explanation."
        )
        try:
            result = self.brain.ask(prompt, system_prompt=system)
            return result or "[LLM summary unavailable]"
        except Exception as e:
            logger.error(f"ContextCompressor LLM fallback failed: {e}")
            return "[Summary failed — context may be incomplete]"
