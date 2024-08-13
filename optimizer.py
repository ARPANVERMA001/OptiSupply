import osmnx as ox
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, GUROBI_CMD
from item_placement import optimize_packing
import networkx as nx
from collections import defaultdict

def calculate_distance(loc1, loc2):
    latitude1, longitude1 = loc1
    latitude2, longitude2 = loc2
    ox.config(use_cache=True, cache_folder='./osmnx_cache')
    G = ox.graph_from_point(loc1, dist=10000, network_type='drive')
    start_node = ox.distance.nearest_nodes(G, longitude1, latitude1)
    end_node = ox.distance.nearest_nodes(G, longitude2, latitude2)

    return nx.shortest_path_length(G, start_node, end_node, weight='length')


def get_items_for_order(order, all_items):
    items_for_order = []
    for item_id, quantity in order.items:
        items_for_order.extend([item for item in all_items if item.id == item_id][:quantity])
    return items_for_order


def update_inventory(supplier, items_packed):
    for item in items_packed:
        supplier.inventory[item.id] -= 1

def optimize_routes(suppliers, warehouses, trucks, orders, items):
    prob = LpProblem("Logistics_Optimization", LpMinimize)

    # Create demand based on orders
    order_items = []
    for order in orders:
        warehouse = next((w for w in warehouses if w.warehouse_id == order.warehouse_id), None)
        if warehouse:
            warehouse.demand = {item_id: qty for item_id, qty in order.items}
            order_items.extend([(item_id, qty, order.warehouse_id) for item_id, qty in order.items])

    # Filter the items based on the orders
    filtered_items = [item for item in items if any(item.id == item_id for item_id, _, _ in order_items)]

    # Create decision variables including quantity_id
    x = LpVariable.dicts("shipment", 
                         [(s.supplier_id, w.warehouse_id, item.id, item.quantity_id) 
                          for s in suppliers 
                          for w in warehouses 
                          for item in filtered_items], 
                         lowBound=0, cat='Integer')

    # Calculate travel distances between suppliers and warehouses
    travel_distances = {(s.supplier_id, w.warehouse_id): calculate_distance(s.location, w.location)
                        for s in suppliers for w in warehouses}

    # Objective function: Minimize the total transportation distance
    prob += lpSum(x[(s, w, i, q)] * travel_distances[(s, w)] 
                  for (s, w, i, q) in x)

    # Supply constraints: Ensure that the supply from each supplier does not exceed its inventory
    for s in suppliers:
        for i in filtered_items:
            prob += lpSum(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id)] 
                          for w in warehouses) <= s.inventory.get(i.id, 0)

    # Demand constraints: Ensure that the demand at each warehouse is met
    for w in warehouses:
        for i in filtered_items:
            prob += lpSum(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id)] 
                          for s in suppliers) >= w.demand.get(i.id, 0)

    # Solve the optimization problem
    prob.solve(GUROBI_CMD(msg=1))

    # Extract optimized assignments
    optimized_assignments = []
    for s in suppliers:
        for w in warehouses:
            for i in filtered_items:
                if x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id)].varValue > 0:
                    optimized_assignments.append((s.supplier_id, w.warehouse_id, i.id, i.quantity_id))
                    # Assign warehouse ID to item
                    i.warehouse_id = w.warehouse_id

    # Group items by trucks
    truck_assignments = defaultdict(list)
    for order in orders:
        items_for_order = get_items_for_order(order, filtered_items)
        for item in items_for_order:
            assigned = False
            for truck in trucks:
                if truck.can_carry_items([item]):
                    truck_assignments[truck.truck_id].append(item)
                    truck.items.append(item)
                    assigned = True
                    break

            if not assigned:
                print(f"Item {item.id}-{item.quantity_id} could not be assigned to any truck.")

        # Update the inventory after the items are assigned
        for item in items_for_order:
            supplier = next((s for s in suppliers if s.supplier_id == item.supplier_id), None)
            if supplier:
                update_inventory(supplier, [item])

    for truck in trucks:
        print(f"\nTruck ID: {truck.truck_id}")
        print(f"Items in Truck {truck.truck_id}:")
        for item in truck.items:
            print(f" - Item ID: {item.id}, Quantity ID: {item.quantity_id}, Size: {item.length}x{item.width}x{item.height}, Stackable: {item.stackable}, Fragile: {item.fragile}")

    # Optimize item packing within each truck
    for truck in trucks:
        optimize_packing(truck.bin, truck.items)