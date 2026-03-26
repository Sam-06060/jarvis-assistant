import requests
import json
import time

class WeatherService:
    """
    Get weather information using Open-Meteo (Solid Reliability)
    Strategy: 
    1. Get Coordinates from IP (ip-api.com)
    2. Get Weather from coords (open-meteo.com)
    """
    
    def __init__(self):
        self.location_cache = None
    
    def _get_location(self):
        """Get Latitude/Longitude from IP"""
        if self.location_cache:
            return self.location_cache
            
        try:
            # Free IP Geolocation API
            response = requests.get("http://ip-api.com/json/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.location_cache = {
                    "lat": data['lat'],
                    "lon": data['lon'],
                    "city": data['city'],
                    "country": data['country']
                }
                return self.location_cache
        except Exception as e:
            print(f"⚠️ Geolocation failed: {e}")
            return None
            
    def get_weather(self, location_query=""):
        """Get current weather"""
        try:
            # 1. Resolve Coordinates
            lat, lon, city_name, country_name = None, None, None, None
            
            if location_query:
                # Use Open-Meteo Geocoding API (Free, No Key)
                geo_url = "https://geocoding-api.open-meteo.com/v1/search"
                geo_params = {"name": location_query, "count": 1, "language": "en", "format": "json"}
                geo_resp = requests.get(geo_url, params=geo_params, timeout=5)
                
                if geo_resp.status_code == 200 and geo_resp.json().get('results'):
                    res = geo_resp.json()['results'][0]
                    lat = res['latitude']
                    lon = res['longitude']
                    city_name = res['name']
                    country_name = res.get('country', '')
                else:
                    print(f"⚠️ Geocoding failed for '{location_query}', falling back to local.")
            
            # Fallback to local IP if no query or geocoding failed
            if lat is None:
                loc = self._get_location()
                if not loc:
                    return {"error": "Couldn't locate you or that city to check the weather."}
                lat, lon, city_name, country_name = loc['lat'], loc['lon'], loc['city'], loc['country']
            
            # 2. Get Weather from Open-Meteo
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true",
                "temperature_unit": "celsius",
                "windspeed_unit": "kmh"
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                current = data['current_weather']
                
                temp = current['temperature']
                wind = current['windspeed']
                # WMO Weather interpretation codes
                wmo_code = current['weathercode']
                condition = self._decode_wmo(wmo_code)
                
                return f"""
Weather in {city_name}, {country_name}:
• Condition: {condition}
• Temperature: {temp}°C
• Wind: {wind} km/h
"""
            else:
                return "Open-Meteo is unavailable right now."
                
        except Exception as e:
            return f"Weather Logic Error: {e}"

    def _decode_wmo(self, code):
        """Translate WMO codes to text"""
        if code == 0: return "Clear Sky ☀️"
        if code in [1, 2, 3]: return "Partly Cloudy ⛅️"
        if code in [45, 48]: return "Foggy 🌫️"
        if code in [51, 53, 55]: return "Drizzle 🌧️"
        if code in [61, 63, 65]: return "Rain ☔️"
        if code in [71, 73, 75]: return "Snow ❄️"
        if code in [95, 96, 99]: return "Thunderstorm ⚡️"
        return "Overcast ☁️"

    def get_forecast(self, location="", days=3):
        # Open-Meteo supports forecast too, but keeping it simple for now
        return self.get_weather()