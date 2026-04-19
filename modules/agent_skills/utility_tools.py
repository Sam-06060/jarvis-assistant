import logging
from datetime import datetime
from .base import AgentTool

logger = logging.getLogger(__name__)

# ── Timezone map for common cities ──────────────────────────────────────────
# Uses zoneinfo (stdlib Python 3.9+). Covers the cities users ask about most.
_CITY_TZ = {
    # UK / Europe
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "rome": "Europe/Rome",
    "madrid": "Europe/Madrid",
    "amsterdam": "Europe/Amsterdam",
    "moscow": "Europe/Moscow",
    "istanbul": "Europe/Istanbul",
    "dubai": "Asia/Dubai",
    # Americas
    "new york": "America/New_York",
    "los angeles": "America/Los_Angeles",
    "chicago": "America/Chicago",
    "toronto": "America/Toronto",
    "sao paulo": "America/Sao_Paulo",
    "mexico city": "America/Mexico_City",
    # Asia / Pacific
    "tokyo": "Asia/Tokyo",
    "beijing": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",
    "hong kong": "Asia/Hong_Kong",
    "singapore": "Asia/Singapore",
    "seoul": "Asia/Seoul",
    "mumbai": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
    "kolkata": "Asia/Kolkata",
    "bangalore": "Asia/Kolkata",
    "karachi": "Asia/Karachi",
    "sydney": "Australia/Sydney",
    "melbourne": "Australia/Melbourne",
    # Middle East / Africa
    "riyadh": "Asia/Riyadh",
    "cairo": "Africa/Cairo",
    "nairobi": "Africa/Nairobi",
}

def _get_tz_for_city(city: str):
    """Return a ZoneInfo object for the given city name, or None if unknown."""
    try:
        from zoneinfo import ZoneInfo
        key = city.lower().strip()
        # Direct match
        if key in _CITY_TZ:
            return ZoneInfo(_CITY_TZ[key])
        # Partial match (e.g. "new york city" → "new york")
        for city_key, tz_name in _CITY_TZ.items():
            if city_key in key or key in city_key:
                return ZoneInfo(tz_name)
    except Exception:
        pass
    return None

class WeatherTool(AgentTool):
    name = "get_weather"
    description = "Get current weather or forecast. Input: {'location': str}. If user wants their current location (e.g. 'what's the weather'), you MUST pass 'CURRENT_LOCATION' to dynamically fetch their Mac's GPS/IP location."
    permission = "safe"
    
    def run(self, inp: dict):
        weather_service = self.cp.registry.get("weather")
        if not weather_service: return "Weather service unavailable."
        
        loc = inp.get('location', '').strip()
        # "Agent's thinking": Agent explicitly passes CURRENT_LOCATION
        if loc.upper() in ["CURRENT_LOCATION", "CURRENT", "MAC", ""]: 
            loc_data = weather_service._get_location()
            if loc_data:
                loc = loc_data.get("city", "")
            else:
                return "Error: Could not determine Mac's current location dynamically. Ask the user for a city."
                
        result = weather_service.get_weather(loc)
        
        # Handle API failing gracefully
        if isinstance(result, dict) and "error" in result:
            return result["error"]
        return result

class CalculatorTool(AgentTool):
    name = "calculator"
    description = "Perform math calculations. Input: {'expression': str}. Example: {'expression': 'sqrt(256) * 12'}"
    permission = "safe"
    
    def run(self, inp: dict):
        calc = self.cp.registry.get("calculator")
        if not calc: return "Calculator service unavailable."
        return f"Calculation Result: {calc.calculate(inp.get('expression', ''))}"

class ReminderTool(AgentTool):
    name = "manage_reminders"
    description = "Add, list, or remove reminders. Input: {'action': 'add'|'list'|'remove', 'text': str, 'time': str (optional for add)}. Example: {'action': 'add', 'text': 'Buy milk', 'time': '5pm'}"
    permission = "write"
    
    def run(self, args: dict):
        reminders = self.cp.registry.get('reminders')
        if not reminders: return "Reminder manager unavailable."
        action = args.get("action", "list").lower()
        if action == "list":
            return reminders.get_active_reminders()
        elif action == "add":
            return reminders.add_reminder(args.get("text"), args.get("time"))
        elif action == "remove":
            return reminders.cancel_reminder(args.get("id"))
        return "Invalid action for ReminderTool."

class AlarmTool(AgentTool):
    name = "manage_alarms"
    description = "Set or list alarms. Input: {'action': 'set'|'list', 'time': str}. Example: {'action': 'set', 'time': '7am'}"
    permission = "write"
    
    def run(self, inp: dict):
        alarms = self.cp.registry.get('alarms')
        if not alarms: return "Alarm manager unavailable."
        action = inp.get('action', 'list').lower()
        if action == 'set':
            success, msg = alarms.set_alarm(inp.get('time', ''))
            return msg
        return alarms.get_active_reminders() # Fallback for listing

class TranslatorTool(AgentTool):
    name = "translator"
    description = "Translate text. Input: {'text': str, 'target_language': str}. Example: {'text': 'Hello', 'target_language': 'French'}"
    permission = "safe"
    
    def run(self, inp: dict):
        translator = self.cp.registry.get("translator")
        if not translator: return "Translator service unavailable."
        result = translator.translate(inp.get('text', ''), inp.get('target_language', ''))
        return f"Translation ({inp.get('target_language', '')}): {result}"

class ClockTool(AgentTool):
    name = "get_time"
    description = (
        "Get the current local time, optionally for a specific city. "
        "Input: {'location': str (optional city name)}. "
        "When location is given, returns the correct local time for THAT city — NOT the user's system time. "
        "Example: {'location': 'London'} returns UK time; {} or {'location': ''} returns local system time."
    )
    permission = "safe"

    def run(self, inp: dict):
        location = (inp.get('location') or '').strip()

        if location:
            tz = _get_tz_for_city(location)
            if tz:
                from datetime import timezone
                now = datetime.now(tz)
                return (
                    f"The current local time in {location.title()} is "
                    f"{now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')} "
                    f"({now.strftime('%Z, UTC%z')})."
                )
            else:
                # Unknown city — say so clearly rather than silently returning local time
                return (
                    f"I don't have timezone data for '{location}'. "
                    f"My local system time is {datetime.now().strftime('%I:%M %p')} — "
                    f"but that is NOT the time in {location}."
                )

        # No location → return system time
        now = datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."

class MusicTool(AgentTool):
    name = "play_music"
    description = "Play music, songs, or artists. Input: {'action': 'play', 'song': str, 'app': str (optional, default 'Spotify')}"
    permission = "write"
    
    def run(self, args: dict):
        music = self.cp.registry.get("music")
        if not music: return "Music service unavailable."
        song = args.get("song")
        logger.info(f"🔗 Chaining MusicTool to standard Skill: play {song}")
        self.cp.process(f"play {song}")
        return f"Successfully triggered playback for: {song}"

class NowPlayingTool(AgentTool):
    name = "get_now_playing"
    description = "Find out what song is currently playing on Spotify or Apple Music."
    permission = "safe"
    
    def run(self, inp: dict):
        music = self.cp.registry.get("music")
        if not music: return "Music service unavailable."
        return music.get_current_track()
