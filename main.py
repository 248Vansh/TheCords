from fastapi import FastAPI
from pydantic import BaseModel
from pdfParser import extract_routes
from graphBuilder import build_graph_from_routes
from routeFinder import find_route
from pathwayPipeline import answer_query
from weather import get_weather
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RouteRequest(BaseModel):
    start: str
    end: str


def summarize_route(long_text: str):
    prompt = f"""
    Summarize the following route description into bullet points.
    Include only key cities, highways, and main advice. Avoid long paragraphs.

    Route:
    {long_text}
    """
    summary = answer_query(prompt)
    return summary

@app.post("/route")
def get_route(req: RouteRequest):
    source = req.start
    destination = req.end

    routes = extract_routes("highways/highways.pdf")
    G = build_graph_from_routes(routes)

    query = f"Find the best route from {source} to {destination} using national highways."
    initial_route_text = answer_query(query)

    # Summarize the output
    initial_route_summary = summarize_route(initial_route_text)

    # Weather checks
    route_cities = [city.strip() for city in initial_route_text.split(",")]
    bad_cities = []
    weather_info = []
    for city in route_cities:
        desc, temp = get_weather(city)
        weather_info.append({"city": city, "weather": desc, "temp": temp})
        if any(bad in desc.lower() for bad in ["storm", "rain", "mist", "snow", "hail"]):
            bad_cities.append(city)

    alternate_route_text = None
    alternate_route_summary = None
    if bad_cities:
        avoid_str = ", ".join(bad_cities)
        query_alt = f"Find the best route from {source} to {destination} avoiding these cities due to bad weather: {avoid_str}."
        alternate_route_text = answer_query(query_alt)
        alternate_route_summary = summarize_route(alternate_route_text)

    return {
        "initial_route": initial_route_summary,
        "weather": weather_info,
        "bad_cities": bad_cities,
        "alternate_route": alternate_route_summary,
    }








