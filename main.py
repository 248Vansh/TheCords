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

    # Ask Gemini to return structured JSON
    query = f"""
    Find the best route from {source} to {destination} using national highways.
    Return the result as a JSON array of segments with this format:
    [
        {{"from": "CityName", "to": "CityName", "highway": "NHXX"}}
    ]
    Only return JSON, no extra text.
    """
    route_text = answer_query(query)

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

    # Debug: Print parsed segments
    print("Parsed segments:", segments)

    # Add weather info and guidelines
    route_output = []
    for seg in segments:
        desc_from, temp_from = get_weather(seg["from"])
        desc_to, temp_to = get_weather(seg["to"])

        # Ask Gemini for travel guidelines given weather
        query_guidelines = f"""
        You are a road safety assistant. 
        The weather at {seg['to']} is '{desc_to}' with temperature {temp_to}°C. 
        Suggest travel safety guidelines for someone driving from {seg['from']} to {seg['to']} via {seg['highway']}.
        Keep it short and practical.
        """
        guidelines = answer_query(query_guidelines)

        route_output.append({
            "from": f"{seg['from']} (Weather: {desc_from}, {temp_from}°C)",
            "to": f"{seg['to']} (Weather: {desc_to}, {temp_to}°C)",
            "highway": seg["highway"],
            "guidelines": guidelines.strip()
        })

    # Debug: Print final route output
    print("Route output:", route_output)

    return {"route_segments": route_output}

