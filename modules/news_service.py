import feedparser
from datetime import datetime

class NewsService:
    """Get news headlines from RSS feeds"""
    
    def __init__(self):
        self.feeds = {
            "general": "https://news.google.com/rss",
            "tech": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB",
            "business": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB",
            "science": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFptZHpJU0FtVnVHZ0pWVXlnQVAB",
            "world": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB",
        }
    
    def get_headlines(self, category="general", count=5):
        """Get top headlines from a category"""
        try:
            if category not in self.feeds:
                category = "general"
            
            feed_url = self.feeds[category]
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                return "Could not fetch news headlines."
            
            headlines = f"Top {category.capitalize()} News:\n\n"
            
            for i, entry in enumerate(feed.entries[:count], 1):
                title = entry.title
                # Remove source from title if present (Google News format)
                if " - " in title:
                    title = title.split(" - ")[0]
                
                headlines += f"{i}. {title}\n"
            
            return headlines.strip()
            
        except Exception as e:
            return f"Could not fetch news: {str(e)}"
    
    def get_tech_news(self, count=5):
        """Get technology news"""
        return self.get_headlines("tech", count)
    
    def get_business_news(self, count=5):
        """Get business news"""
        return self.get_headlines("business", count)
    
    def get_world_news(self, count=5):
        """Get world news"""
        return self.get_headlines("world", count)
    
    def get_science_news(self, count=5):
        """Get science news"""
        return self.get_headlines("science", count)
    
    def get_news_summary(self):
        """Get a quick summary across categories"""
        try:
            summary = "📰 News Briefing:\n\n"
            
            # Get 2 headlines from each major category
            categories = ["general", "tech", "business"]
            
            for category in categories:
                feed = feedparser.parse(self.feeds[category])
                
                if feed.entries:
                    summary += f"{category.upper()}:\n"
                    for entry in feed.entries[:2]:
                        title = entry.title
                        if " - " in title:
                            title = title.split(" - ")[0]
                        summary += f"• {title}\n"
                    summary += "\n"
            
            return summary.strip()
            
        except Exception as e:
            return f"Could not fetch news summary: {str(e)}"