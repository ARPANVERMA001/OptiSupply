from pulp import *

def optimize_routes(suppliers, warehouses, trucks, orders, items):
    prob = LpProblem("Logistics_Optimization", LpMinimize)

    # Constants
    FIXED_TRUCK_COST = 1000  # Cost X for using a truck
    PER_KM_COST = 1  # Cost Y per km of travel

    # Create sets
    all_locations = suppliers + warehouses
    all_location_ids = [l.supplier_id for l in suppliers] + [w.warehouse_id for w in warehouses]

    # Create decision variables
    x = LpVariable.dicts("shipment", 
                         [(s.supplier_id, w.warehouse_id, i.id, i.quantity_id, t.truck_id) 
                          for s in suppliers 
                          for w in warehouses 
                          for i in items
                          for t in trucks], 
                         lowBound=0, cat='Integer')

    y = LpVariable.dicts("route", 
                         [(i, j, t.truck_id) 
                          for i in all_location_ids 
                          for j in all_location_ids 
                          for t in trucks if i != j], 
                         cat='Binary')

    z = LpVariable.dicts("truck_used", 
                         [t.truck_id for t in trucks], 
                         cat='Binary')

    # Calculate travel distances between all locations
    travel_distances = {(i, j): calculate_distance(loc1.location, loc2.location)
                        for loc1 in all_locations
                        for loc2 in all_locations
                        if loc1 != loc2}

    # Objective function: Minimize total cost
    prob += (lpSum(z[t.truck_id] * FIXED_TRUCK_COST for t in trucks) +
             lpSum(y[(i, j, t.truck_id)] * travel_distances[(i, j)] * PER_KM_COST
                   for i in all_location_ids
                   for j in all_location_ids
                   for t in trucks
                   if i != j))

    # Constraints

    # Flow conservation
    for k in all_location_ids:
        for t in trucks:
            prob += (lpSum(y[(i, k, t.truck_id)] for i in all_location_ids if i != k) ==
                     lpSum(y[(k, j, t.truck_id)] for j in all_location_ids if j != k))

    # Ensure items are picked up from suppliers
    for s in suppliers:
        for i in items:
            prob += (lpSum(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id, t.truck_id)]
                           for w in warehouses
                           for t in trucks) <= 
                     s.inventory.get(i.id, 0))

    # Ensure demand is met at warehouses
    for w in warehouses:
        for i in items:
            prob += (lpSum(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id, t.truck_id)]
                           for s in suppliers
                           for t in trucks) >= 
                     w.demand.get(i.id, 0))

    # Link shipments to routes
    for s in suppliers:
        for w in warehouses:
            for t in trucks:
                prob += (lpSum(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id, t.truck_id)]
                               for i in items) <= 
                         len(items) * y[(s.supplier_id, w.warehouse_id, t.truck_id)])

    # Ensure truck capacity is not exceeded
    for t in trucks:
        prob += (lpSum(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id, t.truck_id)] * 
                       (i.length * i.width * i.height)
                       for s in suppliers
                       for w in warehouses
                       for i in items) <= 
                 t.bin.length * t.bin.width * t.bin.height)

    # Limit truck travel distance
    for t in trucks:
        direct_distances = {(s.supplier_id, w.warehouse_id): travel_distances[(s.supplier_id, w.warehouse_id)]
                            for s in suppliers
                            for w in warehouses}
        prob += (lpSum(y[(i, j, t.truck_id)] * travel_distances[(i, j)]
                       for i in all_location_ids
                       for j in all_location_ids if i != j) <= 
                 1.2 * lpSum(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id, t.truck_id)] * 
                             direct_distances[(s.supplier_id, w.warehouse_id)]
                             for s in suppliers
                             for w in warehouses
                             for i in items))

    # Link truck usage to routes
    for t in trucks:
        prob += (lpSum(y[(i, j, t.truck_id)]
                       for i in all_location_ids
                       for j in all_location_ids if i != j) <= 
                 len(all_location_ids) * z[t.truck_id])

    # Solve the problem
    prob.solve(GUROBI_CMD(msg=1))

    # Extract and return results
    results = {
        "status": LpStatus[prob.status],
        "total_cost": value(prob.objective),
        "routes": [],
        "assignments": []
    }

    for t in trucks:
        route = []
        for i in all_location_ids:
            for j in all_location_ids:
                if i != j and value(y[(i, j, t.truck_id)]) > 0.5:
                    route.append((i, j))
        if route:
            results["routes"].append((t.truck_id, route))

    for s in suppliers:
        for w in warehouses:
            for i in items:
                for t in trucks:
                    if value(x[(s.supplier_id, w.warehouse_id, i.id, i.quantity_id, t.truck_id)]) > 0.5:
                        results["assignments"].append((t.truck_id, s.supplier_id, w.warehouse_id, i.id, i.quantity_id))

    return results