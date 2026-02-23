from fuzzywuzzy import fuzz, process
import config

class FuzzyMatcher:
    """Fuzzy matching for commands and app names"""
    
    def __init__(self):
        self.app_names = list(config.MAC_APPS.keys())
        self.command_aliases = {
            "netflix": ["netfix", "netflex", "net flix"],
            "youtube": ["youtub", "utube", "you tube"],
            "spotify": ["spotfy", "spotifi"],
            "calculator": ["calc", "calculater"],
            "chrome": ["crome", "chrme", "google chrome"],
            "safari": ["safri", "safari browser"],
            "facetime": ["face time", "video call"],
            "messages": ["message", "imessage", "text"],
            "calendar": ["calender", "cal"],
            "notes": ["note"],
            "mail": ["email", "gmail"],
        }
    
    def match_app_name(self, user_input, threshold=70):
        """Find best matching app name"""
        user_input = user_input.lower().strip()
        
        # Direct match first
        if user_input in self.app_names:
            return config.MAC_APPS[user_input]
        
        # Check aliases
        for correct, aliases in self.command_aliases.items():
            if user_input in aliases or user_input == correct:
                if correct in config.MAC_APPS:
                    return config.MAC_APPS[correct]
        
        # Fuzzy match against app names
        match = process.extractOne(user_input, self.app_names, scorer=fuzz.ratio)
        if match and match[1] >= threshold:
            return config.MAC_APPS[match[0]]
        
        # Fuzzy match against display names
        display_names = list(config.MAC_APPS.values())
        match = process.extractOne(user_input, display_names, scorer=fuzz.ratio)
        if match and match[1] >= threshold:
            return match[0]
        
        return None
    
    def suggest_command(self, user_input, command_list, threshold=60):
        """Suggest closest matching command"""
        match = process.extractOne(user_input, command_list, scorer=fuzz.ratio)
        if match and match[1] >= threshold:
            return match[0]
        return None
    
    def is_similar(self, str1, str2, threshold=80):
        """Check if two strings are similar"""
        return fuzz.ratio(str1.lower(), str2.lower()) >= threshold