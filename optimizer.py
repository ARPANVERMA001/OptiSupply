import osmnx as ox
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, GUROBI_CMD, LpStatus, value
from item_placement import optimize_packing
import networkx as nx
from collections import defaultdict
from geopy.distance import geodesic
import pickle, os
from functools import lru_cache

# File to store the distance cache
CACHE_FILE = 'distance_cache.pkl'

# Load existing cache from file if it exists
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'rb') as f:
        distance_cache = pickle.load(f)
else:
    distance_cache = {}

# Set up OSMnx to use the cache directory
ox.settings.use_cache = True
ox.settings.cache_folder = 'C:\\Users\\arpan\\OneDrive\\Desktop\\logistics_project\\osmnx_cache'

@lru_cache(maxsize=128)
def calculate_distance(loc1, loc2):
    # Convert tuples to strings for dictionary keys
    cache_key = f"{loc1}_{loc2}"
    
    # Check if the distance is in the cache
    if cache_key in distance_cache:
        print(f"Using cached distance for {loc1} to {loc2}")
        return distance_cache[cache_key]
    
    latitude1, longitude1 = loc1
    latitude2, longitude2 = loc2
    
    print(f"Calculating distance between {loc1} and {loc2}")
    
    # Create a new graph for each calculation
    north = max(latitude1, latitude2) + 0.1
    south = min(latitude1, latitude2) - 0.1
    east = max(longitude1, longitude2) + 0.1
    west = min(longitude1, longitude2) - 0.1
    
    try:
        # This will use the OSMnx cache if available
        G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
        G = ox.project_graph(G)
        
        start_node = ox.distance.nearest_nodes(G, longitude1, latitude1)
        end_node = ox.distance.nearest_nodes(G, longitude2, latitude2)
        
        print(f"Start node: {start_node}, End node: {end_node}")
        
        if start_node == end_node:
            distance = geodesic(loc1, loc2).meters
        else:
            try:
                path = nx.shortest_path(G, start_node, end_node, weight='length')
                distance = sum(ox.utils_graph.get_route_edge_attributes(G, path, 'length'))
                print(f"Calculated network distance: {distance} meters")
            except nx.NetworkXNoPath:
                print(f"No path found. Using geodesic distance.")
                distance = geodesic(loc1, loc2).meters
    
    except Exception as e:
        print(f"Error in distance calculation: {str(e)}. Using geodesic distance.")
        distance = geodesic(loc1, loc2).meters

    # Store the calculated distance in the cache
    distance_cache[cache_key] = distance
    
    # Save the updated cache to file
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(distance_cache, f)
    
    return distance

# Function to clear the distance cache (call this if you need to reset the cache)
def clear_distance_cache():
    global distance_cache
    distance_cache.clear()
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    print("Distance cache cleared")

# Function to clear the OSMnx cache (use with caution)
def clear_osmnx_cache():
    ox.settings.cache_folder = 'C:\\Users\\arpan\\OneDrive\\Desktop\\logistics_project\\osmnx_cache'
    ox.utils.config.cache_clear()
    print("OSMnx cache cleared")


def get_items_for_order(order, all_items):
    items_for_order = []
    for item_id, quantity in order.items:
        items_for_order.extend([item for item in all_items if item.id == item_id][:quantity])
    return items_for_order


def update_inventory(supplier, items_packed):
    for item in items_packed:
        supplier.inventory[item.id] -= 1

from collections import defaultdict
def optimize_routes(suppliers, warehouses, trucks, orders, items):
    prob = LpProblem("Logistics_Optimization", LpMinimize)

    # Create shipment variables for each item with its unique quantity_id
    x = LpVariable.dicts("shipment", 
                         [(s.supplier_id, w.warehouse_id, i.id, i.quantity_id) 
                          for s in suppliers for w in warehouses for i in items], 
                         lowBound=0, cat='Binary')  # Changed to Binary

    # Calculate travel distances
    travel_distances = {(s.supplier_id, w.warehouse_id): calculate_distance(s.location, w.location) 
                        for s in suppliers for w in warehouses}

    # Objective: Minimize total travel distance
    prob += lpSum(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id)] * travel_distances[(s.supplier_id, w.warehouse_id)] 
                   for s in suppliers for w in warehouses for i in items)

    # Supply constraints
    for s in suppliers:
        for i in items:
            if i.id in s.inventory:
                prob += lpSum(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id)] 
                              for w in warehouses) <= s.inventory[i.id]
            else:
                # If supplier doesn't have this item, ensure it doesn't supply it
                prob += lpSum(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id)] 
                              for w in warehouses) == 0

    # Demand constraints
    for w in warehouses:
        for item_id, quantity in w.demand.items():
            prob += lpSum(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id)] 
                          for s in suppliers 
                          for i in items if i.id == item_id) == quantity

    # Ensure each item is assigned only once
    for i in items:
        prob += lpSum(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id)] 
                      for s in suppliers for w in warehouses) == 1

    # Solve the problem
    prob.solve(GUROBI_CMD(msg=1))

    # Extract optimized assignments
    optimized_assignments = []
    for s in suppliers:
        for w in warehouses:
            for i in items:
                if x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id)].varValue > 0:
                    optimized_assignments.append(
                        (s.supplier_id, w.warehouse_id, i.id, i.quantity_id, 
                         x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id)].varValue)
                    )

    print("----------------------------------------------------------------------------------------------")
    print(optimized_assignments)
    print("----------------------------------------------------------------------------------------------")

    # Distribute items to trucks based on optimized routes
    supplier_items = defaultdict(list)

    # Collect items for each supplier
    for s_id, w_id, i_id, q_id, qty in optimized_assignments:
        item = next((i for i in items if i.id == i_id and i.quantity_id == q_id), None)
        if item:
            supplier_items[s_id].append((w_id, item, qty))

    # Initialize truck index
    truck_index = 0

    # Process each supplier's items
    for s_id, items_info in supplier_items.items():
        items_to_load = []
        for w_id, item, qty in items_info:
            items_to_load.extend([item] * int(qty))
        
        # Select truck
        truck = trucks[truck_index % len(trucks)]
        
        # Check if truck can carry all items
        if truck.can_carry_items(items_to_load):
            # Optimize packing for the selected truck
            optimize_packing(truck.bin, items_to_load)
            truck_index += 1

    return optimized_assignments