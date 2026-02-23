from .base import Skill

class NewsSkill(Skill):
    def can_handle(self, command: str) -> bool:
        return "news" in command.lower()

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        news = self.app.get('news')
        if not news: return False

        try:
            if "tech" in cmd:
                result = news.get_tech_news()
            elif "business" in cmd:
                result = news.get_business_news()
            elif "world" in cmd:
                result = news.get_world_news()
            else:
                result = news.get_headlines()
            
            self.speech.speak(result)
            self.log_usage(command)
            return True
        except Exception as e:
            self.logger.error(f"News error: {e}")
            self.speech.speak("I couldn't fetch the news at the moment.")
            return True
