from graphBuilder import build_graph
from routeFinder import find_route

if __name__ == "__main__":
    G = build_graph()
    find_route(G, "Delhi", "Guwahati")


