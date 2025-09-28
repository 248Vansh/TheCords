import requests

def get_weather(city):
    url = f"https://wttr.in/{city}?format=j1"
    try:
        response = requests.get(url).json()
        current = response["current_condition"][0]
        desc = current["weatherDesc"][0]["value"]
        temp = current["temp_C"]
        return desc, temp
    except Exception as e:
        return "Unknown", "N/A"

