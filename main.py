from fastapi import FastAPI
from pydantic import BaseModel
from pathwayPipeline import answer_query, get_all_docs, client
from weather import get_weather
from fastapi.middleware.cors import CORSMiddleware
import json, re, os, requests
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Request Models
# -----------------------------
class RouteRequest(BaseModel):
    start: str
    end: str

class ChatRequest(BaseModel):
    message: str

class FuelCostRequest(BaseModel):
    vehicle: str
    fuel_type: str
    distance_km: float

# -----------------------------
# Traffic + Directions
# -----------------------------
def get_route_with_traffic(start, end):
    """Fetch step-wise route with live traffic from Google Directions API."""
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": start,
        "destination": end,
        "key": GOOGLE_API_KEY,
        "mode": "driving",
        "departure_time": "now",
        "traffic_model": "best_guess"
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return []
    data = resp.json()
    if data.get("status") != "OK":
        return []
    
    segments = []
    for leg in data["routes"][0]["legs"]:
        for step in leg["steps"]:
            segments.append({
                "from": step["start_location"],
                "to": step["end_location"],
                "distance": step["distance"]["text"],
                "duration": step["duration"]["text"],
                "traffic_duration": step.get("duration_in_traffic", {}).get("text", step["duration"]["text"]),
                "instruction": re.sub("<.*?>", "", step["html_instructions"])
            })
    return segments

# -----------------------------
# Route endpoint
# -----------------------------
@app.post("/route")
def get_route(req: RouteRequest):
    source = req.start
    destination = req.end

    query_route = f"""
    Find best route from {source} to {destination} using national highways dataset.
    Return ONLY valid JSON array like:
    [{{"from": "CityName", "to": "CityName", "highway": "NHXX"}}]
    No text, no explanations.
    """

    route_text = answer_query(query_route)

    # 🛠 Debug log: see what Gemini gave
    print("🔎 Gemini raw output:", route_text)

    # Remove markdown/json wrappers if any
    clean_text = re.sub(r"^```json\s*|\s*```$", "", route_text.strip())

    # Try parsing JSON
    try:
        segments = json.loads(clean_text)
    except Exception:
        # If Gemini gave text with JSON inside, extract it
        match = re.search(r"\[.*\]", clean_text, re.DOTALL)
        if match:
            try:
                segments = json.loads(match.group(0))
            except:
                segments = []
        else:
            segments = []

    # If still nothing, return error
    if not segments:
        return {"error": "No valid route data received", "raw": route_text}

    # Build final output
    route_output = []
    for seg in segments:
        start_city = seg.get("from")
        end_city = seg.get("to")
        highway = seg.get("highway", "Unknown")

        if not start_city or not end_city:
            continue

        traffic_data = get_route_with_traffic(start_city, end_city)
        desc_from, temp_from = get_weather(start_city)
        desc_to, temp_to = get_weather(end_city)

        traffic_str = traffic_data[0]["traffic_duration"] if traffic_data else "N/A"
        query_guidelines = f"""
        You are a road safety assistant.
        Weather at {end_city}: '{desc_to}', {temp_to}°C.
        Traffic duration: {traffic_str}
        Suggest 3-4 concise, practical driving tips from {start_city} to {end_city} via {highway}.
        Use emojis, max 30 words per tip.
        Only return tips, no extra text.
        """
        guidelines = answer_query(query_guidelines)

        route_output.append({
            "from": f"{start_city} (Weather: {desc_from}, {temp_from}°C)",
            "to": f"{end_city} (Weather: {desc_to}, {temp_to}°C)",
            "highway": highway,
            "traffic": traffic_data,
            "guidelines": guidelines.strip()
        })

    return {"route_segments": route_output}

# -----------------------------
# Cities endpoint
# -----------------------------
@app.get("/cities")
def get_cities():
    try:
        df = pd.read_csv("./highways/highways_full.csv")

        # Collect unique cities from both start and end
        cities = set(df["start_city"].dropna().unique()) | set(df["end_city"].dropna().unique())

        return {"cities": sorted(cities)}
    except Exception as e:
        return {"cities": [], "error": str(e)}

# -----------------------------
# Chat endpoint
# -----------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    user_message = req.message

    city_pattern = re.compile(r"from\s+([A-Za-z\s]+)\s+to\s+([A-Za-z\s]+)", re.IGNORECASE)
    match = city_pattern.search(user_message)
    start_city, end_city = (None, None)
    if match:
        start_city = match.group(1).strip()
        end_city = match.group(2).strip()

    traffic_info, weather_info = None, None
    if start_city and end_city:
        traffic_info = get_route_with_traffic(start_city, end_city)
        desc_from, temp_from = get_weather(start_city)
        desc_to, temp_to = get_weather(end_city)
        weather_info = {
            "from": f"{desc_from}, {temp_from}°C",
            "to": f"{desc_to}, {temp_to}°C"
        }

    prompt = f"""
You are a helpful travel assistant using Pathway. Answer the user's query concisely, practically, and emoji-friendly.

User asked: "{user_message}"

{f"Route from {start_city} to {end_city} detected." if start_city and end_city else ""}
{f"Traffic info: From {start_city} to {end_city}: {traffic_info[0]['traffic_duration'] if traffic_info else 'N/A'}" if traffic_info else ""}
{f"Weather: From {start_city}: {weather_info['from']}, To {end_city}: {weather_info['to']}" if weather_info else ""}

Provide a short, practical, easy-to-read response. Use emojis where relevant. Max 5 sentences.
"""
    response = answer_query(prompt)
    return {"reply": response}

# -----------------------------
# Fuel cost endpoint
# -----------------------------
@app.post("/fuel_cost")
def fuel_cost(req: FuelCostRequest):
    vehicle = req.vehicle
    fuel_type = req.fuel_type
    distance = req.distance_km

    vehicle_mileage_db = {
        "Maruti Swift Dzire": {"Petrol": 23, "Diesel": 28},
        "Hyundai Creta": {"Petrol": 16, "Diesel": 21},
    }
    mileage = vehicle_mileage_db.get(vehicle, {}).get(fuel_type)
    if not mileage:
        return {"error": "Vehicle/fuel data not found"}

    practical_mileage = mileage * 0.85
    fuel_price_db = {"Petrol": 102.5, "Diesel": 93.0, "CNG": 65.0}
    price_per_liter = fuel_price_db.get(fuel_type)
    if not price_per_liter:
        return {"error": "Fuel type not supported"}

    estimated_cost = (distance / practical_mileage) * price_per_liter

    return {
        "vehicle": vehicle,
        "fuel_type": fuel_type,
        "distance_km": distance,
        "official_mileage": mileage,
        "practical_mileage": round(practical_mileage, 2),
        "price_per_liter": price_per_liter,
        "estimated_cost": round(estimated_cost, 2)
    }
