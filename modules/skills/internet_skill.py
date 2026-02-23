from .base import Skill
import webbrowser
import time
import re

class InternetSkill(Skill):
    def can_handle(self, command: str) -> bool:
        cmd = command.lower()
        if any(t in cmd for t in ["toggle internet", "chatgpt", "open ai"]):
            return True
        return self._has_google_intent(cmd)

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        system = self.app.get('system')
        manual_online = getattr(self.app.get('command_processor'), "manual_online_status", True)
        
        try:
            # TOGGLE INTERNET
            if "toggle internet" in cmd:
                cmd_proc = self.app.get('command_processor')
                if cmd_proc:
                    if cmd_proc.manual_online_status:
                        cmd_proc.manual_online_status = False
                        self.speech.speak("Internet disconnected. I am now offline.")
                    else:
                        cmd_proc.manual_online_status = True
                        self.speech.speak("Internet restored. I am back online.")
                return True
        except Exception as e:
            self.logger.error(f"Internet toggle error: {e}")
            self.speech.speak("I couldn't toggle the internet connection state.")
            return True

        try:
            # SEARCH
            if self._has_google_intent(cmd):
                if not manual_online or (system and not system.check_network()):
                    self.speech.speak("Internet is off.")
                    return True

                query = self._extract_google_query(command)
                if query:
                    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    webbrowser.open(url)
                    self.speech.speak(f"Here are the search results for {query}")
                    self.log_usage(f"search {query}")
                    return True
                self.speech.speak("Tell me what you want to search on Google.")
                return True
    
            if "chatgpt" in cmd or "open ai" in cmd:
                self.speech.speak("Opening ChatGPT")
                webbrowser.open("https://chatgpt.com")
                return True
        except webbrowser.Error:
            self.speech.speak("I couldn't open the web browser.")
            return True
        except Exception as e:
            self.logger.error(f"Internet search error: {e}")
            self.speech.speak("I encountered an issue opening the web page.")
            return True
            
        return False

    def _has_google_intent(self, cmd_lower: str) -> bool:
        patterns = [
            r"\bsearch\s+(?:on\s+)?google\b",
            r"\bgoogle\s+(?:about|on|for)\b",
            r"^\s*google\b",
            r"\bopen google\b",
        ]
        return any(re.search(pattern, cmd_lower) for pattern in patterns)

    def _extract_google_query(self, command: str) -> str:
        text = command.strip()

        # Preferred: quoted topic, e.g. quick search on "topic"
        quoted = re.search(r'"([^"]+)"', text)
        if quoted:
            return quoted.group(1).strip()

        patterns = [
            r"\bsearch\s+(?:on\s+)?google\s+(?:about|on|for)?\s*(.+)$",
            r"^\s*google\s+(?:about|on|for)?\s*(.+)$",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                query = match.group(1).strip(" .?!")
                if query:
                    return query

        # Fallback cleanup
        query = re.sub(r"\b(?:could you|can you|please|quickly|quick|make|a|search|on|google|about|for|open)\b", " ", text, flags=re.IGNORECASE)
        query = re.sub(r"\s+", " ", query).strip(" .?!")
        return query
