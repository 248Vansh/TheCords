# main.py
from pdfParser import extract_routes
from graphBuilder import build_graph_from_routes
from routeFinder import find_route
from pathwayPipeline import answer_query
from weather import get_weather

if __name__ == "__main__":
    source = "Delhi"
    destination = "Guwahati"

    # 1️⃣ Get initial route from PDF (optional: you can use Gemini to suggest route instead)
    routes = extract_routes("highways/highways.pdf")
    G = build_graph_from_routes(routes)

    # 2️⃣ Ask Gemini for best route using highways data
    query = f"Find the best route from {source} to {destination} using national highways."
    initial_route_text = answer_query(query)
    print(f"Initial route suggested by Gemini:\n{initial_route_text}\n")

    # Assume Gemini outputs comma-separated cities
    route = [city.strip() for city in initial_route_text.split(",")]

    # 3️⃣ Check weather along route
    bad_cities = []
    for city in route:
        desc, temp = get_weather(city)
        print(f"{city}: {desc}, {temp}°C")
        if any(bad in desc.lower() for bad in ["storm", "rain", "mist", "snow", "hail"]):
            print(f"⚠️ Bad weather detected at {city}")
            bad_cities.append(city)

    # 4️⃣ Ask Gemini for alternate route if needed
    if bad_cities:
        avoid_str = ", ".join(bad_cities)
        query_alt = f"Find the best route from {source} to {destination} avoiding these cities due to bad weather: {avoid_str}."
        alternate_route_text = answer_query(query_alt)
        print(f"\nAlternate route suggested by Gemini:\n{alternate_route_text}")
    else:
        print("\nRoute is safe, no bad weather detected along the way.")





