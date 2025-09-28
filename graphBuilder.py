import networkx as nx

def build_graph_from_routes(routes):
    G = nx.Graph()
    for route in routes:
        for i in range(len(route) - 1):
            # here distance is dummy; you can later use Google Maps API for real
            G.add_edge(route[i], route[i+1], distance=100)
    return G

