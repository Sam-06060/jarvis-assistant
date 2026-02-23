import json
import os
from datetime import datetime, timedelta

class OfflineCache:
    """Cache AI responses for offline mode"""
    
    def __init__(self, cache_file="data/offline_cache.json"):
        self.cache_file = cache_file
        self.cache = {}
        self.max_age_days = 7
        self.load_cache()
        
        # Pre-populate with common responses
        self.default_responses = {
            "hello": "Hello! How can I help you?",
            "how are you": "I'm functioning optimally, thank you for asking!",
            "what can you do": "I can open apps, control system settings, search the web, manage files, and answer questions.",
            "thanks": "You're welcome!",
            "thank you": "My pleasure!",
            "goodbye": "Goodbye! Have a great day.",
            "who are you": "I'm JARVIS, your AI assistant.",
            "what time is it": f"Current time information requires an active session.",
            "help": "I can help with: opening apps, web searches, system control, file management, and answering questions. Just ask!",
        }
    
    def load_cache(self):
        """Load cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                self._cleanup_old_entries()
        except Exception as e:
            print(f"Warning: Could not load offline cache: {e}")
            self.cache = {}
    
    def save_cache(self):
        """Save cache to disk"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save offline cache: {e}")
    
    def _cleanup_old_entries(self):
        """Remove entries older than max_age_days"""
        cutoff = (datetime.now() - timedelta(days=self.max_age_days)).isoformat()
        old_cache = self.cache.copy()
        self.cache = {
            k: v for k, v in old_cache.items()
            if v.get("timestamp", "") > cutoff
        }
    
    def get(self, query):
        """Get cached response for query"""
        query_lower = query.lower().strip()
        
        # Check default responses first
        if query_lower in self.default_responses:
            return self.default_responses[query_lower]
        
        # Check cache
        if query_lower in self.cache:
            return self.cache[query_lower].get("response")
        
        return None
    
    def set(self, query, response):
        """Cache a response"""
        query_lower = query.lower().strip()
        self.cache[query_lower] = {
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        self.save_cache()
    
    def clear(self):
        """Clear all cached responses"""
        self.cache = {}
        self.save_cache()
    
    def get_fallback_response(self):
        """Get a generic fallback response"""
        return "I'm currently offline and don't have a cached response for that. Please try again when connected."