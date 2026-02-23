from .base import Skill

class TranslatorSkill(Skill):
    def can_handle(self, command: str) -> bool:
        triggers = ["translate", "how do you say", "how to say", "what do you call"]
        return any(t in command.lower() for t in triggers)
    
    def handle(self, command: str) -> bool:
        translator = self.app.get('translator')
        
        if not translator:
            return False
        
        # Use the built-in parser (Google Translate)
        result = translator.parse_translation_command(command)
        self.speech.speak(result)
        return True
