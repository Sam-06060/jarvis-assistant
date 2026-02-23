from .base import Skill
import random
import config

class InteractionSkill(Skill):
    def __init__(self, app_context):
        super().__init__(app_context)
        self.instant_responses = {
            # Removed greetings (let Brain handle them with Persona)
            # 'hello': 'Hello! How can I help?',
            # 'hey': 'Yes?',
            # 'hi': 'Hi there!',
            # 'yo': 'What\'s up?',
            # 'sup': 'Hey there!',
            # 'how are you': "I'm functioning optimally!",
            # 'whats up': "All systems operational!",
            
            'thanks': "You're welcome!",
            'thank you': "My pleasure!",
        }

    def can_handle(self, command: str) -> bool:
        cmd = command.lower().strip(".,!?")
        if cmd in self.instant_responses: return True
        
        triggers = ["exit", "shutdown", "goodbye", "quit", "stop", "cancel", "stand by"]
        return any(t in cmd for t in triggers)

    def get_phrases(self) -> list[str]:
        return [
            "exit", "shutdown", "shut down", "goodbye", "quit", 
            "stop listening", "stop", "cancel", "stand by"
        ]

    def handle(self, command: str) -> bool:
        cmd = command.lower().strip(".,!?")
        
        # 1. Instant Responses
        if cmd in self.instant_responses:
            self.speech.speak(self.instant_responses[cmd])
            return True

        # 2. Control Commands
        if "exit" in cmd or "shutdown" in cmd or "quit" in cmd or "goodbye" in cmd:
            self.speech.speak("Goodbye.")
            # We need to signal the app to exit.
            # Using a special return string convention that we will support in CommandProcessor
            return "EXIT"

        if "stop" in cmd or "cancel" in cmd or "stand by" in cmd:
            # self.speech.speak("Standing by.") # Optional, maybe just stop listening
            return "STOP_LISTENING"
            
        return False
