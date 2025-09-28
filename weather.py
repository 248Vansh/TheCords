import requests

def get_weather(city):
    url = f"https://wttr.in/{city}?format=j1" 
    response = requests.get(url).json()
    
    # Current weather
    current = response["current_condition"][0]
    weather_desc = current["weatherDesc"][0]["value"]
    temp = current["temp_C"]
    
    return f"{weather_desc}, {temp}°C"


print(get_weather("Delhi"))
