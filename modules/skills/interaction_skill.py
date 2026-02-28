from .base import Skill
import random
import re
import config

# ============================================================
# SHUTDOWN / EXIT NLP PATTERNS
# ============================================================
EXIT_DIRECT_TRIGGERS = [
    "exit", "shutdown", "shut down", "quit", "goodbye", "bye",
    "terminate", "power off", "turn off", "log off", "sign off",
    "close jarvis", "kill jarvis", "end jarvis",
]

EXIT_NLP_PATTERNS = [
    r"\bi'?m\s+done\b",                     # "i'm done", "im done"
    r"\bthat'?s?\s+(?:it|all)\s+for\s+(?:today|now|tonight)\b",  # "that's it for today"
    r"\bclose\s+everything\b",               # "close everything"
    r"\bend\s+(?:the\s+)?session\b",         # "end session", "end the session"
    r"\bwrap\s+(?:it\s+)?up\b",              # "wrap it up", "wrap up"
    r"\bcall\s+it\s+a\s+(?:day|night)\b",    # "call it a day"
    r"\bdone\s+for\s+(?:now|today|tonight)\b",  # "done for now"
    r"\btime\s+to\s+(?:go|sleep|leave)\b",   # "time to go"
    r"\bi\s+(?:want|need)\s+to\s+(?:close|stop|end)\b",  # "i want to close"
    r"\blet'?s?\s+(?:stop|end|finish)\b",    # "let's stop"
    r"\bno\s+more\s+(?:commands?|tasks?)\b", # "no more commands"
    r"\bgood\s*(?:bye|night)\b",             # "good bye", "goodnight"
]


class InteractionSkill(Skill):
    def __init__(self, app_context):
        super().__init__(app_context)
        self.instant_responses = {
            'thanks': "You're welcome!",
            'thank you': "My pleasure!",
        }

    def can_handle(self, command: str) -> bool:
        cmd = command.lower().strip(".,!?")
        if cmd in self.instant_responses:
            return True
        
        return self._is_exit_intent(cmd) or self._is_stop_intent(cmd)

    def get_phrases(self) -> list[str]:
        return [
            # Direct
            "exit", "shutdown", "shut down", "goodbye", "quit", "bye",
            "stop listening", "stop", "cancel", "stand by",
            "terminate", "power off", "turn off", "log off",
            # NLP-style
            "i'm done", "done for now", "call it a day",
            "wrap it up", "end session", "that's all",
            "time to go", "close everything", "goodnight",
        ]

    def handle(self, command: str) -> bool:
        cmd = command.lower().strip(".,!?")
        
        # 1. Instant Responses
        if cmd in self.instant_responses:
            self.speech.speak(self.instant_responses[cmd])
            return True

        # 2. Exit / Shutdown (NLP-aware)
        if self._is_exit_intent(cmd):
            self.speech.speak("Goodbye.")
            return "EXIT"

        # 3. Stop / Stand By
        if self._is_stop_intent(cmd):
            return "STOP_LISTENING"
            
        return False

    def _is_exit_intent(self, cmd):
        """NLP-aware exit/shutdown detection."""
        # Direct triggers
        for trigger in EXIT_DIRECT_TRIGGERS:
            if trigger in cmd:
                return True
        # NLP patterns
        for pattern in EXIT_NLP_PATTERNS:
            if re.search(pattern, cmd):
                return True
        return False

    def _is_stop_intent(self, cmd):
        """Check for stop/pause/standby intent."""
        stop_triggers = ["stop", "cancel", "stand by", "standby", "pause"]
        return any(t in cmd for t in stop_triggers)
