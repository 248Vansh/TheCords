import networkx as nx

def build_graph():
    G = nx.Graph()

    # Simple demo route Delhi -> Kanpur -> Patna -> Kolkata -> Guwahati
    G.add_edge("Delhi", "Kanpur", distance=500)
    G.add_edge("Kanpur", "Patna", distance=600)
    G.add_edge("Patna", "Kolkata", distance=470)
    G.add_edge("Kolkata", "Guwahati", distance=1000)
    G.add_edge("Patna", "Guwahati", distance=900)  # Alternate path skipping Kolkata

    return G
