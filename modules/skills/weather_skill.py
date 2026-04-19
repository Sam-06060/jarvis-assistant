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
            # FIX: Use Jarvis's AI Brain to smartly extract the desired location (No regex)
            brain = self.app.get('brain')
            location = ""
            
            if brain:
                prompt = (
                    f"Analyze this request: '{command}'.\n"
                    f"Extract the city or location the user is asking about.\n"
                    f"If the user is asking for their current/local location (e.g. 'what's the weather', 'weather here', 'my location'), "
                    f"reply ONLY with the exact word: 'CURRENT_LOCATION'.\n"
                    f"Otherwise, reply ONLY with the city name (e.g. 'London'). Output nothing else."
                )
                
                # Cloud-first fast generation if available, fallback to local
                extracted = brain.ask(prompt, system_prompt="You are a strict data extractor. Follow rules exactly.")
                if extracted:
                    extracted_clean = extracted.strip()
                    # Clean up random AI chatter
                    for prefix in ["location:", "city:"]:
                        if extracted_clean.lower().startswith(prefix):
                            extracted_clean = extracted_clean[len(prefix):].strip()
                            
                    if "CURRENT_LOCATION" in extracted_clean.upper() or extracted_clean == "":
                        # He identified it's current location, use Mac coordinates
                        loc_data = weather_service._get_location()
                        if loc_data:
                            location = loc_data.get("city", "")
                    else:
                        location = extracted_clean

            if "forecast" in cmd and "weather" not in cmd:
                result = weather_service.get_forecast(location)
            else:
                result = weather_service.get_weather(location)
                
            # Handle API failing gracefully
            if isinstance(result, dict) and "error" in result:
                self.speech.speak(result["error"])
            else:
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
