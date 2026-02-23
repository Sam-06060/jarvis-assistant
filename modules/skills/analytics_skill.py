from .base import Skill

class AnalyticsSkill(Skill):
    def can_handle(self, command: str) -> bool:
        triggers = ["stats", "statistics", "analytics", "usage", "how many commands", "jarvis stats"]
        return any(t in command.lower() for t in triggers)
    
    def handle(self, command: str) -> bool:
        cmd = command.lower()
        analytics = self.app.get('analytics')
        
        if not analytics:
            return False
        
        # Jarvis-specific stats
        if "jarvis stats" in cmd or "jarvis statistics" in cmd:
            result = analytics.get_stats()
            self.speech.speak(result)
            return True
        
        # Overall stats/statistics
        if "stats" in cmd or "statistics" in cmd or "analytics" in cmd:
            result = analytics.get_stats()
            self.speech.speak(result)
            return True
        
        # Today's stats
        if "today" in cmd or "how many" in cmd:
            result = analytics.get_today_stats()
            self.speech.speak(result)
            return True
        
        # Reset stats
        if "reset" in cmd:
            result = analytics.reset_stats()
            self.speech.speak(result)
            return True
        
        return False
