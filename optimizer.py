import osmnx as ox
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, GUROBI_CMD
from item_placement import optimize_packing
import networkx as nx

def calculate_distance(loc1, loc2):
    latitude1, longitude1 = loc1
    latitude2, longitude2 = loc2

    G = ox.graph_from_point(loc1, dist=10000, network_type='drive')
    start_node = ox.distance.nearest_nodes(G, longitude1, latitude1)
    end_node = ox.distance.nearest_nodes(G, longitude2, latitude2)

    return nx.shortest_path_length(G, start_node, end_node, weight='length')

def optimize_routes(suppliers, warehouses, trucks, orders, items):
    prob = LpProblem("Logistics_Optimization", LpMinimize)

    # Create demand based on orders
    for order in orders:
        warehouse = next((w for w in warehouses if w.warehouse_id == order.warehouse_id), None)
        if warehouse:
            warehouse.demand = {item_id: qty for item_id, qty in order.items}

    x = LpVariable.dicts("shipment", 
                         [(s.supplier_id, w.warehouse_id, item.id) for s in suppliers 
                          for w in warehouses for item in items], 
                         lowBound=0, cat='Integer')

    travel_distances = {(s.supplier_id, w.warehouse_id): calculate_distance(s.location, w.location) 
                        for s in suppliers for w in warehouses}
    prob += lpSum(x[(s, w, i)] * travel_distances[(s, w)] for s, w, i in x)

    # Supply constraints
    for s in suppliers:
        for i in items:
            prob += lpSum(x[(s.supplier_id, w.warehouse_id, i.id)] for w in warehouses) <= s.inventory.get(i.id, 0)
    
    # Demand constraints
    for w in warehouses:
        for i in items:
            prob += lpSum(x[(s.supplier_id, w.warehouse_id, i.id)] for s in suppliers) >= w.demand.get(i.id, 0)

    prob.solve(GUROBI_CMD(msg=1))

    # Extract optimized assignments
    optimized_assignments = []
    for s in suppliers:
        for w in warehouses:
            for i in items:
                if x[(s.supplier_id, w.warehouse_id, i.id)].varValue > 0:
                    optimized_assignments.append((s.supplier_id, w.warehouse_id, i.id, x[(s.supplier_id, w.warehouse_id, i.id)].varValue))
    
    print("----------------------------------------------------------------------------------------------")
    print(optimized_assignments)
    print("----------------------------------------------------------------------------------------------")
    # # Distribute items to trucks based on optimized routes
    # truck_index = 0
    # for s_id, w_id, i_id, qty in optimized_assignments:
    #     item = next((i for i in items if i.id == i_id), None)
    #     warehouse = next((w for w in warehouses if w.warehouse_id == w_id), None)
    #     if item and warehouse:
    #         items_to_load = [item] * int(qty)
    #         truck = trucks[truck_index % len(trucks)]
    #         if truck.can_carry_items(items_to_load):
    #             optimize_packing(truck.bin, items_to_load)
    #             truck_index += 1

    # Distribute items to trucks based on optimized routes
    from collections import defaultdict

    # Dictionary to group items by supplier
    supplier_items = defaultdict(list)

    # Collect items for each supplier
    for s_id, w_id, i_id, qty in optimized_assignments:
        item = next((i for i in items if i.id == i_id), None)
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