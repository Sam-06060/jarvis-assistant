"""
observation_assessor.py — Deterministic quality evaluation for agent tool outputs.

Assesses whether a tool's result is "good", "partial", or "failed" based
on the step's expected output type. Zero LLM calls — purely rule-based.

Quality levels:
  "good"    — The result adequately satisfies the step requirement.
  "partial" — The result is present but may be incomplete.
  "failed"  — The tool errored, returned nothing, or is clearly wrong.
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class ObservationAssessor:
    """
    Deterministic, zero-LLM quality checker for agent tool observations.

    Usage:
        assessor = ObservationAssessor()
        quality = assessor.assess(observation_text, expected_output_type)
        # quality is "good", "partial", or "failed"
    """

    # Strings that unambiguously indicate tool failure
    FAILURE_PREFIXES = (
        "Error:", "[!]", "Failed", "Error executing",
        "unavailable", "not found", "not loaded",
        "NameError", "AttributeError", "Exception",
    )

    # Keywords that confirm a side-effecting action completed
    CONFIRMATION_KEYWORDS = (
        "success", "sent", "created", "done", "✅",
        "confirmed", "executed", "completed", "added",
        "deleted", "removed", "updated", "saved", "written",
    )

    # Patterns that suggest real data is present
    _DATA_PATTERNS = [
        r"\d+",                                 # any number
        r"[A-Z][a-z]+ [A-Z][a-z]+",             # Proper Name
        r"\d{4}-\d{2}-\d{2}",                   # date
        r"\$[\d,]+",                            # price
        r"\bhttps?://\S+",                      # URL
        r"\b[A-Z]{2,}\b",                       # acronym / ticker
    ]

    def assess(self, observation: str, expected_output_type: str = "text") -> str:
        """
        Evaluate the quality of an agent tool's output.

        Args:
            observation:          The string result returned by the tool.
            expected_output_type: One of "text", "data", "action_confirmed", "file".

        Returns:
            "good" | "partial" | "failed"
        """
        obs = str(observation).strip()

        # ── UNIVERSAL FAILURE CHECKS ──────────────────────────────────────
        if not obs or len(obs) < 5:
            logger.debug("ObservationAssessor: FAILED — empty/tiny response")
            return "failed"

        if any(obs.startswith(fp) or fp.lower() in obs[:100].lower()
               for fp in self.FAILURE_PREFIXES):
            logger.debug(f"ObservationAssessor: FAILED — failure prefix detected in: {obs[:60]}")
            return "failed"

        # ── ACTION CONFIRMATION FAST-PATH ────────────────────────────────
        # send_whatsapp/write_file/save_info return short messages like:
        #   "Message sent to Zoheb Clg."
        #   "Successfully wrote content to ~/Desktop/rate_limiter.py."
        # Promote any result containing a confirmation keyword to 'good' immediately
        # BEFORE type-specific length checks, so action tools don't cause false stalls.
        if any(kw.lower() in obs.lower() for kw in self.CONFIRMATION_KEYWORDS) and len(obs) < 200:
            logger.debug(f"ObservationAssessor: GOOD (action confirmation fast-path) — {obs[:60]}")
            return "good"

        # ── TYPE-SPECIFIC CHECKS ──────────────────────────────────────────
        otype = expected_output_type.lower()

        if otype == "action_confirmed":
            confirmed = any(kw.lower() in obs.lower() for kw in self.CONFIRMATION_KEYWORDS)
            quality = "good" if confirmed else "partial"
            logger.debug(f"ObservationAssessor: action_confirmed → {quality}")
            return quality

        if otype == "data":
            # Expect at least one data pattern (number, name, date, price, URL)
            has_data = any(re.search(pat, obs) for pat in self._DATA_PATTERNS)
            if not has_data:
                logger.debug("ObservationAssessor: data → PARTIAL — no data patterns found")
                return "partial"
            quality = "good" if len(obs) > 80 else "partial"
            logger.debug(f"ObservationAssessor: data → {quality}")
            return quality

        if otype == "file":
            # File operations should mention a path or confirmation keyword
            has_path = bool(re.search(r"[\\/~][\w\-./]+\.\w+", obs))
            has_confirm = any(kw.lower() in obs.lower() for kw in self.CONFIRMATION_KEYWORDS)
            
            # 🛡️ Mermaid Validation: If writing a report/markdown, check for backticks
            if obs.lower().endswith(".md") or "report" in obs.lower():
                if "mermaid" in obs.lower() and "```mermaid" not in obs.lower():
                    logger.debug("ObservationAssessor: file → PARTIAL — Mermaid missing backticks")
                    return "partial"

            quality = "good" if (has_path or has_confirm) else "partial"
            logger.debug(f"ObservationAssessor: file → {quality}")
            return quality

        if otype == "report":
            # Reports must be substantive and have correct formatting
            if len(obs) < 200:
                logger.debug("ObservationAssessor: report → PARTIAL — too short")
                return "partial"
            if "mermaid" in obs.lower() and "```mermaid" not in obs.lower():
                logger.debug("ObservationAssessor: report → PARTIAL — Mermaid missing backticks")
                return "partial"
            return "good"

        # Default: "text" — just needs to be substantive
        quality = "good" if len(obs) >= 80 else "partial"

        logger.debug(f"ObservationAssessor: text → {quality} (len={len(obs)})")
        return quality

    def summarise_quality(self, quality: str, tool_name: str, observation: str) -> str:
        """Return a compact one-line description for HUD/logging."""
        snippet = observation[:60].replace("\n", " ") + ("..." if len(observation) > 60 else "")
        icons = {"good": "✅", "partial": "⚠️", "failed": "❌"}
        return f"{icons.get(quality, '?')} [{tool_name}] {quality.upper()}: {snippet}"
