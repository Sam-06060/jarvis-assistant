"""
HOW TO CREATE A CUSTOM JARVIS SKILL
=====================================

1. Create a new .py file in this directory (e.g. my_skill.py)
2. Inherit from the Skill base class
3. Implement can_handle() and handle()
4. Restart Jarvis — your skill is automatically loaded. No other changes needed.

IMPORTANT — PHRASE SAFETY RULES:
  - Do NOT use phrases similar to built-in commands (e.g. "hello jarvis",
    "what time is it", "play music") — the fuzzy matcher may route
    real commands to your skill by accident.
  - Use UNIQUE, SPECIFIC phrases that are unlikely to match anything else.
  - Prefer phrases with 3+ distinctive words.
  - Use the EXACT same phrase in both get_phrases() AND your can_handle() check.

EXAMPLE SKILL (copy this as a starting point):
"""

from modules.skills.base import Skill


class ExampleCustomSkill(Skill):
    """
    Example custom skill — responds to unique phrases that won't
    accidentally match common Jarvis commands.

    Replace this with your own logic.
    """

    # ── Define your trigger phrases here ────────────────────────────────────
    # Keep these UNIQUE and SPECIFIC — don't use common words like
    # "hello", "jarvis", "play", "time", etc. on their own.
    PHRASES = [
        "run custom skill demo",
        "test my custom skill",
        "activate custom demo",
    ]

    def get_phrases(self) -> list[str]:
        """
        Return key phrases for speech recognition context.
        These improve transcription accuracy AND are used by the fuzzy matcher.

        SAFETY: Keep these specific enough that they won't fuzzy-match
        common commands. Aim for 3+ unique words.
        """
        return self.PHRASES

    def can_handle(self, command: str) -> bool:
        """
        Hard guard — always check the EXACT command here, even after fuzzy matching.
        This is the final safety net preventing false positives.
        """
        cmd = command.lower().strip()
        return any(phrase in cmd for phrase in self.PHRASES)

    def handle(self, command: str) -> bool:
        """Execute the command. Return True if handled, False to pass to next skill."""
        speech = self.app.get("speech")
        if speech:
            speech.speak("Custom skill is working perfectly!")
        else:
            self.logger.info("Custom skill triggered (no speech engine)")
        return True
