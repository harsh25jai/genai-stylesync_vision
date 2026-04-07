import requests

def get_weather(city: str) -> str:
    """Fetches real-time temperature and conditions for a city."""
    try:
        # Geocoding to get Lat/Lon
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
        if not geo.get('results'): return "City not found."
        
        lat, lon = geo['results'][0]['latitude'], geo['results'][0]['longitude']
        
        # Fetch Weather
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        temp = w['current_weather']['temperature']
        return f"It is currently {temp}°C in {city}."
    except:
        return "Weather data currently unavailable."