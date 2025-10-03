from fastapi import FastAPI
from pydantic import BaseModel
from pdfParser import extract_routes
from graphBuilder import build_graph_from_routes
from pathwayPipeline import answer_query
from weather import get_weather
from fastapi.middleware.cors import CORSMiddleware
import json
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RouteRequest(BaseModel):
    start: str
    end: str

@app.post("/route")
def get_route(req: RouteRequest):
    source = req.start
    destination = req.end

    # Extract highways graph (optional if used later)
    routes = extract_routes("highways/highways.pdf")
    G = build_graph_from_routes(routes)

    # Ask Gemini to return structured JSON for route
    query_route = f"""
    Find the best route from {source} to {destination} using national highways.
    Return the result as a JSON array of segments with this format:
    [
        {{"from": "CityName", "to": "CityName", "highway": "NHXX"}}
    ]
    Only return JSON, no extra text.
    """
    route_text = answer_query(query_route)

    # Clean up Gemini response from Markdown code blocks
    clean_text = route_text.strip()
    clean_text = re.sub(r"^```json\s*", "", clean_text)
    clean_text = re.sub(r"^```", "", clean_text)
    clean_text = re.sub(r"```$", "", clean_text)

    # Parse JSON
    try:
        segments = json.loads(clean_text)
    except json.JSONDecodeError:
        print("Failed to parse JSON from Gemini:", route_text)
        segments = []

    print("Parsed segments:", segments)

    # Add weather info and **short emoji-friendly guidelines**
    route_output = []
    for seg in segments:
        desc_from, temp_from = get_weather(seg["from"])
        desc_to, temp_to = get_weather(seg["to"])

        # Ask Gemini for concise, emoji-friendly travel guidelines
        query_guidelines = f"""
        You are a road safety assistant. 
        The weather at {seg['to']} is '{desc_to}' with temperature {temp_to}°C. 
        Suggest **3-4 very short, practical safety tips** for driving from {seg['from']} to {seg['to']} via {seg['highway']}.
        Use relevant **emojis** for each tip instead of numbers.
        Keep each tip under 15-30 words and **make it easy to read**.
        Example format:
        🛑 Slow down
        💡 Use lights , visibility low
        ↔️ Keep distance as there fast moving vehicles
        🧠 Stay alert as there are wild animals nearby
        Only return the tips, no extra text.
        """
        guidelines = answer_query(query_guidelines)

        route_output.append({
            "from": f"{seg['from']} (Weather: {desc_from}, {temp_from}°C)",
            "to": f"{seg['to']} (Weather: {desc_to}, {temp_to}°C)",
            "highway": seg["highway"],
            "guidelines": guidelines.strip()
        })

    print("Route output:", route_output)

    return {"route_segments": route_output}

@app.get("/cities")
def get_cities():
    """
    Returns a list of unique cities extracted from highways.pdf using Gemini/Pathway
    """
    query_cities = """
    Extract all unique city names from the highways dataset.
    Return the result as a JSON array like:
    ["Delhi", "Jaipur", "Udaipur", "Mumbai", ...]
    Only return JSON, no extra text.
    """
    city_text = answer_query(query_cities)

    clean_text = city_text.strip()
    clean_text = re.sub(r"^```json\s*", "", clean_text)
    clean_text = re.sub(r"^```", "", clean_text)
    clean_text = re.sub(r"```$", "", clean_text)

    try:
        cities = json.loads(clean_text)
    except json.JSONDecodeError:
        print("Failed to parse city JSON:", city_text)
        cities = []

    return {"cities": sorted(set(cities))}

from fastapi import FastAPI
from pydantic import BaseModel
from pathwayPipeline import answer_query
from fastapi.middleware.cors import CORSMiddleware

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    user_message = req.message

    # Enforce concise, structured, emoji-friendly responses
    prompt = f"""
You are a helpful travel assistant.
Answer the user's query in a very concise, practical way.
- Use short paragraphs or bullet points.
- Use emojis to highlight key points if relevant.
- Avoid long explanations.
- Maximum 5 sentences.
User asked: {user_message}
"""
    response = answer_query(prompt)
    return {"reply": response}



