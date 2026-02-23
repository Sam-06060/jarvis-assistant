from abc import ABC, abstractmethod
from utils.logger import get_logger

logger = get_logger()

class Skill(ABC):
    def __init__(self, app_context):
        """
        app_context: Dictionary or Object containing references to core systems
                     (speech, brain, files, etc.)
        """
        self.app = app_context
        self.speech = app_context.get('speech')
        self.logger = get_logger()
        self.name = self.__class__.__name__

    @abstractmethod
    def can_handle(self, command: str) -> bool:
        """Returns True if this skill should handle the command"""
        pass

    @abstractmethod
    def handle(self, command: str) -> bool:
        """
        Executes the command. 
        Returns True if handled successfully, False otherwise.
        """
        pass

    def get_phrases(self) -> list[str]:
        """
        Returns a list of key phrases/commands this skill handles.
        Used for speech recognition context and fuzzy matching.
        """
        return []

    def log_usage(self, command):
        """Helper to log usage analytics if available"""
        if self.app.get('analytics'):
            self.app['analytics'].log_action(command, self.name)
