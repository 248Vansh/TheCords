from fastapi import FastAPI
from pydantic import BaseModel
from pathwayPipeline import answer_query, get_all_docs
from weather import get_weather
from fastapi.middleware.cors import CORSMiddleware
import json, re, os, requests
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    print("⚠️ Warning: GOOGLE_MAPS_API_KEY is not set in .env")

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
    start: str                  # required
    end: str            # optional


def parse_number_from_gemini(resp):
    """
    Extract the first numeric value from Gemini's response.
    Returns float or None if not found.
    """
    if not resp:
        return None
    resp_clean = resp.replace(",", "")  # remove commas
    match = re.search(r"\d+(\.\d+)?", resp_clean)
    if match:
        return float(match.group(0))
    return None

# -----------------------------
# Traffic + Directions
# -----------------------------
def get_route_with_traffic(start, end):
    """Fetch step-wise route with live traffic from Google Directions API."""
    if not GOOGLE_MAPS_API_KEY:
        return []

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": start,
        "destination": end,
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving",
        "departure_time": "now",
        "traffic_model": "best_guess"
    }

    try:
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
                    "distance": step["distance"]["text"],  # e.g., "1.2 km"
                    "duration": step["duration"]["text"],
                    "traffic_duration": step.get("duration_in_traffic", {}).get("text", step["duration"]["text"]),
                    "instruction": re.sub("<.*?>", "", step["html_instructions"])
                })
        return segments
    except Exception as e:
        print("⚠️ get_route_with_traffic error:", e)
        return []

def fetch_google_distance(origin, destination):
    """Return distance in km between two cities using Google Maps Directions API."""
    if not GOOGLE_MAPS_API_KEY:
        return 0.0
    try:
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {"origin": origin, "destination": destination, "key": GOOGLE_MAPS_API_KEY}
        res = requests.get(url, params=params).json()
        if res.get("status") == "OK":
            total_m = sum(
                leg["distance"]["value"]
                for route in res.get("routes", [])
                for leg in route.get("legs", [])
            )
            return total_m / 1000  # meters → km
    except Exception as e:
        print("⚠️ Google Maps distance error:", e)
    return 0.0

# -----------------------------
# Route endpoint
# -----------------------------
@app.post("/route")
def get_route(req: RouteRequest):
    source = req.start
    destination = req.end
    route_segments = []

    # --- Step 1: Try CSV dataset first ---
    try:
        df = pd.read_csv("./highways/highways_full.csv")
        available_cities = set(df['start_city'].dropna()) | set(df['end_city'].dropna())
        if source in available_cities and destination in available_cities:
            query_csv = f"""
            You are a travel assistant. Find the best route from {source} to {destination} using the highways dataset.
            Return JSON array of segments like:
            [{{"from": "CityName", "to": "CityName", "highway": "NHXX"}}]
            Only JSON, no explanations.
            """
            route_text = answer_query(query_csv)
            print("🔎 Gemini raw output from CSV:", route_text)
            clean_text = re.sub(r"^```json\s*|\s*```$", "", route_text.strip())
            try:
                route_segments = json.loads(clean_text)
            except Exception:
                match = re.search(r"\[.*\]", clean_text, re.DOTALL)
                if match:
                    try:
                        route_segments = json.loads(match.group(0))
                    except:
                        route_segments = []
    except Exception as e:
        print("⚠️ CSV read or processing failed:", e)
        route_segments = []

    # --- Step 2: Fallback to LLM generation if CSV gave nothing ---
    if not route_segments:
        query_fallback = f"""
        You are a travel assistant. Generate a realistic route from {source} to {destination}.
        Return JSON array like:
        [{{"from": "CityName", "to": "CityName", "highway": "NHXX"}}]
        Connect major cities and highways realistically.
        Only JSON, no extra text.
        """
        route_text = answer_query(query_fallback)
        print("🔎 Gemini raw output fallback:", route_text)
        clean_text = re.sub(r"^```json\s*|\s*```$", "", route_text.strip())
        try:
            route_segments = json.loads(clean_text)
        except Exception:
            match = re.search(r"\[.*\]", clean_text, re.DOTALL)
            if match:
                try:
                    route_segments = json.loads(match.group(0))
                except:
                    route_segments = []

    # --- Step 3: If still empty, return empty array ---
    if not route_segments:
        return {"error": "No valid route generated", "route_segments": [], "total_distance_km": 0}

    # --- Step 4: Build final output ---
    route_output = []
    total_distance_km = 0.0
    weather_cache = {}      # cache weather per city
    traffic_cache = {}      # cache traffic per city-pair

    for seg in route_segments:
        start_city = seg.get("from")
        end_city = seg.get("to")
        highway = seg.get("highway", "Unknown")
        if not start_city or not end_city:
            continue

        # --- Traffic caching ---
        pair_key = f"{start_city}-{end_city}"
        if pair_key not in traffic_cache:
            traffic_cache[pair_key] = get_route_with_traffic(start_city, end_city)
        traffic_data = traffic_cache[pair_key]

        # --- Weather caching ---
        if start_city not in weather_cache:
            weather_cache[start_city] = get_weather(start_city)
        if end_city not in weather_cache:
            weather_cache[end_city] = get_weather(end_city)
        desc_from, temp_from = weather_cache[start_city]
        desc_to, temp_to = weather_cache[end_city]

        # --- Segment distance from traffic data ---
        segment_distance = 0.0
        if traffic_data:
            try:
                segment_distance = sum(
                    float(step["distance"].replace(" km", "").replace(",", ""))
                    for step in traffic_data
                    if "distance" in step
                )
            except Exception as e:
                print(f"⚠️ Distance parsing error for {start_city}-{end_city}:", e)
                segment_distance = 0.0

        # --- Google Maps fallback if distance is 0 ---
        if segment_distance == 0.0:
            segment_distance = fetch_google_distance(start_city, end_city)

        total_distance_km += segment_distance
        segment_distance = round(segment_distance, 2)

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
            "distance_km": segment_distance,
            "guidelines": guidelines.strip()
        })

    return {
        "route_segments": route_output,
        "total_distance_km": round(total_distance_km, 2)
    }

# -----------------------------
# Cities endpoint
# -----------------------------
@app.get("/cities")
def get_cities():
    try:
        df = pd.read_csv("./highways/highways_full.csv")
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
        weather_info = {"from": f"{desc_from}, {temp_from}°C", "to": f"{desc_to}, {temp_to}°C"}

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
    start = req.start
    end = req.end

    if not start or not end:
        return {"error": "Please provide both start and end cities."}

    # --- Ask Gemini for distance ---
    distance_query = f"""
    You are a travel assistant. Estimate realistic driving distance in km from {start} to {end}.
    Return only a number in km. No extra text.
    """
    try:
        distance_resp = answer_query(distance_query)
        distance = parse_number_from_gemini(distance_resp)

        # Fallback to Google Maps if Gemini fails
        if not distance or distance == 0:
            distance = fetch_google_distance(start, end)

        if not distance or distance == 0:
            return {"error": "Could not determine distance from Gemini or Google Maps."}
    except Exception as e:
        return {"error": f"Gemini distance error: {str(e)}"}

    # --- Ask Gemini for fuel price ---
    fuel_query = f"""
    You are a travel assistant. Provide the current price per liter in INR for {fuel_type} fuel in India.
    Return only a number, no text.
    """
    try:
        fuel_resp = answer_query(fuel_query)
        price_per_liter = parse_number_from_gemini(fuel_resp)

        # Fallback to default if Gemini fails
        if not price_per_liter:
            fuel_price_db = {"Petrol": 110, "Diesel": 100, "CNG": 80}
            price_per_liter = fuel_price_db.get(fuel_type, 110)
    except Exception as e:
        price_per_liter = 110  # fallback default

    # --- Vehicle mileage (local DB) ---
    vehicle_mileage_db = {
        "Honda City": {"Petrol": 16, "Diesel": 14},
        "Maruti Swift": {"Petrol": 18, "Diesel": 21},
        "Hyundai Creta": {"Petrol": 16, "Diesel": 21},
        "Toyota Fortuner": {"Petrol": 10, "Diesel": 12},
        "Royal Enfield Classic": {"Petrol": 35},
    }
    mileage = vehicle_mileage_db.get(vehicle, {}).get(fuel_type)
    if not mileage:
        return {"error": f"No data for {vehicle} with {fuel_type}"}

    practical_mileage = mileage * 0.85
    estimated_cost = (distance / practical_mileage) * price_per_liter

    return {
        "vehicle": vehicle,
        "fuel_type": fuel_type,
        "distance_km": round(distance, 2),
        "official_mileage": mileage,
        "practical_mileage": round(practical_mileage, 2),
        "price_per_liter": round(price_per_liter, 2),
        "estimated_cost": round(estimated_cost, 2)
    }
