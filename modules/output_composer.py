"""
output_composer.py — Multi-channel output formatting for the Jarvis agent.

Transforms raw step outputs (strings from tool calls) into a polished,
channel-appropriate final response.

Channels:
  "voice" — Spoken TTS output: prose under 150 words, no markdown.
  "text"  — Structured markdown with sections and code blocks (default).
  "file"  — Written to ~/Desktop/Jarvis_Output_{timestamp}.md, auto-opened.

Quality Gate:
  After composing, checks that key named entities from step outputs are
  represented in the final output. If entity coverage < 80%, triggers one
  LLM refinement call to include the missing facts.
"""

import os
import re
import time
import subprocess
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class OutputComposer:
    """
    Composes final agent output from accumulated step results.

    Usage:
        composer = OutputComposer(brain=brain)
        final = composer.compose(
            task_goal="Research Python frameworks and email John",
            step_outputs={1: "Django, FastAPI...", 2: "FastAPI is fastest..."},
            output_channel="text"
        )
    """

    def __init__(self, brain):
        self.brain = brain

    def compose(
        self,
        task_goal: str,
        step_outputs: Dict[int, str],
        output_channel: str = "text",
    ) -> str:
        """
        Build the final response from all step outputs.

        Args:
            task_goal:      The original user task (used for quality gate).
            step_outputs:   {step_id: result_string} from MemoryManager.
            output_channel: "voice", "text", or "file".

        Returns:
            Final formatted string (or file confirmation if channel is "file").
        """
        if not step_outputs:
            return "I completed the task, but there were no results to report."

        # ── 1. Aggregate all step outputs ────────────────────────────────
        aggregated = self._aggregate(step_outputs)

        # ── 2. Format for the target channel ─────────────────────────────
        channel = output_channel.lower()
        if channel == "voice":
            composed = self._format_voice(aggregated, task_goal)
        elif channel == "file":
            return self._format_file(aggregated, task_goal)
        else:
            # Default: "text"
            composed = self._format_text(aggregated, task_goal)

        # ── 3. Quality gate ───────────────────────────────────────────────
        composed = self._quality_gate(composed, aggregated)

        return composed

    # ─────────────────────────────────────────────────────────────────────────
    # Private: Aggregation
    # ─────────────────────────────────────────────────────────────────────────

    def _aggregate(self, step_outputs: Dict[int, str]) -> str:
        """Combine step outputs into a single ordered text block."""
        parts = []
        for step_id in sorted(step_outputs.keys()):
            result = step_outputs[step_id].strip()
            if result:
                parts.append(result)
        return "\n\n".join(parts)

    # ─────────────────────────────────────────────────────────────────────────
    # Private: Channel Formatters
    # ─────────────────────────────────────────────────────────────────────────

    def _format_voice(self, content: str, task_goal: str) -> str:
        """
        Strip markdown, condense numbers/symbols, return prose ≤ 150 words.
        """
        # Strip markdown headers, bullets, bold, code fences
        text = re.sub(r"```[\s\S]*?```", "[code omitted]", content)
        text = re.sub(r"#+ ", "", text)
        text = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", text)
        text = re.sub(r"_{1,2}(.*?)_{1,2}", r"\1", text)
        text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)  # links → text
        text = re.sub(r"\bhttps?://\S+", "the link", text)
        text = re.sub(r"\s+", " ", text).strip()

        # Trim to 150 words
        words = text.split()
        if len(words) > 150:
            text = " ".join(words[:147]) + "..."

        return text

    def _format_text(self, content: str, task_goal: str) -> str:
        """
        Structure content as clean markdown with a header derived from the task goal.
        """
        # Generate a short title from the task goal
        title_words = task_goal.strip().rstrip("?.!").split()
        title = " ".join(title_words[:8])
        if len(title_words) > 8:
            title += "..."

        header = f"## {title}\n\n"

        # If content already looks structured, return as-is under the header
        if re.search(r"(#{1,3} |\n- |\n\d+\.)", content):
            return header + content.strip()

        # Otherwise wrap paragraphs
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        body = "\n\n".join(paragraphs)
        return header + body

    def _format_file(self, content: str, task_goal: str) -> str:
        """
        Write the composed output to ~/Desktop/Jarvis_Output_{timestamp}.md
        and open it. Returns a short confirmation string for speech.
        """
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            desktop = os.path.expanduser("~/Desktop")
            filename = f"Jarvis_Output_{timestamp}.md"
            path = os.path.join(desktop, filename)

            title_words = task_goal.strip().rstrip("?.!").split()
            title = " ".join(title_words[:8])

            md_content = f"# {title}\n\n_{time.strftime('%A, %B %d %Y at %I:%M %p')}_\n\n---\n\n{content.strip()}\n"

            with open(path, "w", encoding="utf-8") as f:
                f.write(md_content)

            subprocess.run(["open", path], check=False)
            logger.info(f"📄 OutputComposer wrote file: {path}")
            return f"I've prepared the results and opened them on your Desktop: {filename}"

        except Exception as e:
            logger.error(f"OutputComposer file write failed: {e}")
            # Fall back to text format
            return self._format_text(content, task_goal)

    # ─────────────────────────────────────────────────────────────────────────
    # Private: Quality Gate
    # ─────────────────────────────────────────────────────────────────────────

    def _quality_gate(self, output: str, source_data: str) -> str:
        """
        Check that named entities from source_data appear in output.
        If coverage < 80%, trigger one LLM refinement call.
        """
        entities = self._extract_entities(source_data)
        if not entities:
            return output  # Nothing to check

        missing = [e for e in entities if e.lower() not in output.lower()]
        coverage = 1.0 - (len(missing) / len(entities))

        logger.debug(
            f"📊 OutputComposer quality gate: {coverage:.0%} coverage, "
            f"missing: {missing[:5]}"
        )

        if coverage >= 0.80:
            return output  # Good enough — no LLM call needed

        # One refinement call to include missing facts
        logger.info(f"📊 Quality gate triggered — {len(missing)} entities missing. Refining...")
        missing_str = ", ".join(missing[:10])
        prompt = (
            f"The following response is missing these important facts: {missing_str}.\n\n"
            f"Revise the response to naturally include these facts where relevant:\n\n"
            f"{output}"
        )
        system = (
            "You are a response editor. Incorporate the missing facts naturally "
            "into the existing text. Do not change the overall structure. "
            "Output only the revised response."
        )
        try:
            refined = self.brain.ask(prompt, system_prompt=system)
            if refined and len(refined) > 50:
                logger.info("📊 Quality gate refinement applied.")
                return refined
        except Exception as e:
            logger.warning(f"OutputComposer quality gate LLM call failed: {e}")

        return output  # Return unrefined if LLM fails

    def _extract_entities(self, text: str) -> list:
        """
        Extract candidate named entities from text.
        Uses simple heuristics: proper nouns, numbers, URLs, file paths.
        No NLP library required.
        """
        entities = []

        # Capitalised proper nouns (2-3 word sequences)
        proper = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b", text)
        entities.extend(proper)

        # Numbers (prices, versions, counts)
        numbers = re.findall(r"\b\d+(?:\.\d+)?(?:%|°C|°F|ms|GB|TB|MB|K|M|B)?\b", text)
        entities.extend(numbers)

        # URLs
        urls = re.findall(r"https?://\S+", text)
        entities.extend(urls)

        # File paths
        paths = re.findall(r"~?/[\w\-./]+\.\w+", text)
        entities.extend(paths)

        # Deduplicate (preserve order) and cap at 30
        seen = set()
        unique = []
        for e in entities:
            if e not in seen and len(e) > 2:
                seen.add(e)
                unique.append(e)

        return unique[:30]
