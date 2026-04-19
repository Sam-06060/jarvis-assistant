"""
token_budget.py — Per-task token accounting for the Jarvis agent loop.

Tracks token consumption across all LLM calls within a single task,
enforces provider-specific limits, and signals when context compression
is required. Uses character-count estimation (len/3.5) — no LLM calls,
no extra dependencies.
"""

import threading
import logging

logger = logging.getLogger(__name__)


class TokenBudget:
    """
    Lightweight token budget tracker for a single agent task.

    Usage:
        budget = TokenBudget(provider="groq")
        budget.consume_text(system_prompt)        # deduct system prompt cost
        if budget.can_afford(500):
            response = brain.ask(prompt)
            budget.consume_text(response)
        if budget.remaining() < 1500:
            history = compressor.compress(history, budget)
    """

    # Conservative limits — leave headroom for responses
    PROVIDER_LIMITS = {
        "groq":        6_000,
        "gemini":     28_000,
        "openrouter": 28_000,
        "nvidia":      6_000,
        "ollama":      3_800,
    }

    def __init__(self, provider: str = "groq"):
        provider_key = provider.lower()
        self.max_budget: int = self.PROVIDER_LIMITS.get(provider_key, 6_000)
        self._consumed: int = 0
        self._lock = threading.Lock()
        logger.debug(f"💰 TokenBudget initialised — provider={provider}, max={self.max_budget}")

    # ── Core API ────────────────────────────────────────────────────────────

    @staticmethod
    def estimate(text: str) -> int:
        """Fast token count approximation. No LLM call needed."""
        return max(1, int(len(str(text)) / 3.5))

    def consume(self, tokens: int):
        """Deduct a known number of tokens from the budget."""
        with self._lock:
            self._consumed += tokens
        logger.debug(f"💰 Budget consumed {tokens} tokens — remaining: {self.remaining()}")

    def consume_text(self, text: str):
        """Estimate and deduct the cost of a text string."""
        self.consume(self.estimate(text))

    def remaining(self) -> int:
        """Return remaining token budget (never negative)."""
        with self._lock:
            return max(0, self.max_budget - self._consumed)

    def can_afford(self, text_or_tokens) -> bool:
        """
        Check whether the budget can cover a given cost.
        Accepts either a token count (int) or a text string (auto-estimated).
        """
        tokens = (
            text_or_tokens
            if isinstance(text_or_tokens, int)
            else self.estimate(text_or_tokens)
        )
        return self.remaining() >= tokens

    def usage_pct(self) -> float:
        """Return fraction of budget consumed (0.0 – 1.0)."""
        with self._lock:
            return self._consumed / self.max_budget

    def reset(self):
        """Reset the budget counter. Call at the start of each new task."""
        with self._lock:
            self._consumed = 0
        logger.debug("💰 TokenBudget reset for new task.")

    def __repr__(self) -> str:
        return (
            f"TokenBudget(consumed={self._consumed}, "
            f"remaining={self.remaining()}, "
            f"max={self.max_budget}, "
            f"usage={self.usage_pct():.1%})"
        )
