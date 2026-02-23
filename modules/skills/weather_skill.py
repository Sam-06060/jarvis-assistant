from .base import Skill
import requests
import json

class WeatherSkill(Skill):
    def can_handle(self, command: str) -> bool:
        triggers = ["weather", "forecast", "temperature", "rain"]
        return any(t in command.lower() for t in triggers)

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        weather_service = self.app.get('weather')
        
        if not weather_service:
            # self.speech.speak("Weather module is not active.")
            return False

        try:
            if "weather" in cmd:
                location = ""
                if " in " in cmd:
                    location = cmd.split(" in ")[-1].strip()
            
                # If standard "weather", get basic
                result = weather_service.get_weather(location)
                self.speech.speak(result)
                self.log_usage(command)
                return True
        
            if "forecast" in cmd:
                result = weather_service.get_forecast()
                self.speech.speak(result)
                self.log_usage(command)
                return True
        except requests.exceptions.ConnectionError:
            self.speech.speak("I cannot connect to the weather service. Please check your internet connection.")
            return True
        except requests.exceptions.Timeout:
            self.speech.speak("The request to the weather service timed out.")
            return True
        except json.JSONDecodeError:
            self.speech.speak("I received invalid data from the weather provider.")
            return True
        except Exception as e:
            self.logger.error(f"Weather error: {e}")
            self.speech.speak("I encountered an issue checking the weather.")
            return True

        return False
