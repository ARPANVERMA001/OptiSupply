import osmnx as ox
import networkx as nx
from geopy.distance import geodesic
import pickle
import os

def calculate_distance(loc1, loc2, graph_cache_path='./osmnx_cache/graph.pkl', dist=100000):
    latitude1, longitude1 = loc1
    latitude2, longitude2 = loc2
    
    print(f"Calculating distance between {loc1} and {loc2}")
    
    ox.settings.use_cache = True
    ox.settings.cache_folder = './osmnx_cache'
    
    # Use a bounding box that includes both locations
    north = max(latitude1, latitude2)
    south = min(latitude1, latitude2)
    east = max(longitude1, longitude2)
    west = min(longitude1, longitude2)
    
    # Add a buffer to ensure the graph covers a bit more than just the exact area
    buffer = 0.1  # Approximately 11 km at the equator
    north += buffer
    south -= buffer
    east += buffer
    west -= buffer
    
    try:
        if os.path.exists(graph_cache_path):
            with open(graph_cache_path, 'rb') as f:
                G = pickle.load(f)
            print("Loaded graph from cache")
        else:
            print(f"Creating new graph for bounding box: N={north}, S={south}, E={east}, W={west}")
            G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
            with open(graph_cache_path, 'wb') as f:
                pickle.dump(G, f)
            print("Created and cached new graph")
        
        # Ensure the graph is projected
        G = ox.project_graph(G)
        
        # Get the nearest nodes
        start_node = ox.distance.nearest_nodes(G, longitude1, latitude1)
        end_node = ox.distance.nearest_nodes(G, longitude2, latitude2)
        
        print(f"Start node: {start_node}, End node: {end_node}")
        
        if start_node == end_node:
            print("Start and end nodes are the same. Using geodesic distance.")
            return geodesic(loc1, loc2).meters
        
        try:
            path = nx.shortest_path(G, start_node, end_node, weight='length')
            distance = sum(ox.utils_graph.get_route_edge_attributes(G, path, 'length'))
            print(f"Calculated network distance: {distance} meters")
            return distance
        except nx.NetworkXNoPath:
            print(f"No path found between nodes {start_node} and {end_node}. Using geodesic distance.")
            return geodesic(loc1, loc2).meters
    
    except Exception as e:
        print(f"Error in distance calculation: {str(e)}. Using geodesic distance.")
        return geodesic(loc1, loc2).meters

# Test the function
suppliers = [
    (28.4595, 77.0266),  # Gurugram (Gurgaon)
    (28.4089, 77.3178),  # Faridabad
]
warehouses = [
    (28.5355, 77.3910),  # Noida
    (28.6139, 77.2090),  # Delhi
]

for s in suppliers:
    for w in warehouses:
        distance = calculate_distance(s, w)
        print(f"Distance from {s} to {w}: {distance} meters")
        print("---")