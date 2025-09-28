import networkx as nx
from weather import get_weather

def find_route(G, source, destination):
    path = nx.shortest_path(G, source, destination, weight="distance")
    print(f"Initial route: {path}")

    # Check weather along path
    for city in path:
        desc, temp = get_weather(city)
        print(f"{city}: {desc}, {temp}°C")

        # If bad weather, block only intermediate cities
        if city not in [source, destination]:
            if any(bad in desc.lower() for bad in ["storm", "rain", "mist", "snow"]):
                print(f"⚠️ Bad weather detected at {city}, recalculating route...")
                G.remove_node(city)
                try:
                    new_path = nx.shortest_path(G, source, destination, weight="distance")
                    print(f"Alternate route: {new_path}")
                    return new_path
                except nx.NetworkXNoPath:
                    print("No alternate route available!")
                    return None

    return path

