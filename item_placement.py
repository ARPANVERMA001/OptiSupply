from pulp import LpProblem, LpMaximize, LpVariable, lpSum, GUROBI_CMD, value

def optimize_packing(bin, items):
    print("INSIDE OPTIMIZE_PACKING")

    # Create a hash map to store the mapping of unique IDs to items
    item_hash_map = {}
    
    # Generate unique IDs combining item ID and quantity ID, and update the hash map
    unique_items = []
    for idx, item in enumerate(items):
        unique_id = f"{item.id}_{item.quantity_id}"
        item_hash_map[unique_id] = item
        unique_items.append((unique_id, item))

    print("ITEMS TO LOAD: ", [(uid, _) for uid, _ in unique_items])

    # Initialize the optimization problem
    prob = LpProblem("3D_Bin_Packing", LpMaximize)

    # Define decision variables for item placement using unique IDs
    x = LpVariable.dicts("item_placement", 
                         [(uid, dx, dy, dz) for uid, item in unique_items 
                          for dx in range(bin.length - item.length + 1)
                          for dy in range(bin.width - item.width + 1)
                          for dz in range(bin.height - item.height + 1)], 
                         cat='Binary')

    # Objective: Maximize space utilization
    prob += lpSum(x[(uid, dx, dy, dz)] * (1 + 0.01 * dx / bin.length) for uid, item in unique_items 
                  for dx in range(bin.length - item.length + 1)
                  for dy in range(bin.width - item.width + 1)
                  for dz in range(bin.height - item.height + 1))

    # Each item can only be placed in one position
    for uid, item in unique_items:
        prob += lpSum(x[(uid, dx, dy, dz)] for dx in range(bin.length - item.length + 1)
                      for dy in range(bin.width - item.width + 1)
                      for dz in range(bin.height - item.height + 1)) <= 1

    # Ensure items do not overlap in the bin
    for px in range(bin.length):
        for py in range(bin.width):
            for pz in range(bin.height):
                prob += lpSum(x[(uid, dx, dy, dz)] 
                              for uid, item in unique_items
                              for dx in range(max(0, px - item.length + 1), min(px + 1, bin.length - item.length + 1))
                              for dy in range(max(0, py - item.width + 1), min(py + 1, bin.width - item.width + 1))
                              for dz in range(max(0, pz - item.height + 1), min(pz + 1, bin.height - item.height + 1))
                              if dx + item.length > px and dy + item.width > py and dz + item.height > pz) <= 1

    # Support constraint for all items: Ensure no item is floating in the air
    for uid, item in unique_items:
        for dx in range(bin.length - item.length + 1):
            for dy in range(bin.width - item.width + 1):
                for dz in range(1, bin.height - item.height + 1):  # Start from height 1 to ensure items are supported
                    prob += x[(uid, dx, dy, dz)] <= lpSum(x[(j_uid, dx1, dy1, dz - item.height)] 
                                                           for j_uid, j_item in unique_items if j_uid != uid
                                                           for dx1 in range(dx, min(dx + item.length, bin.length - j_item.length + 1))
                                                           for dy1 in range(dy, min(dy + item.width, bin.width - j_item.width + 1))
                                                           if (j_uid, dx1, dy1, dz - item.height) in x)

    # Fragile items must be placed on the floor or fully supported
    for uid, item in unique_items:
        if item.fragile:
            for dx in range(bin.length - item.length + 1):
                for dy in range(bin.width - item.width + 1):
                    for dz in range(1, bin.height - item.height + 1):
                        prob += x[(uid, dx, dy, dz)] <= lpSum(x[(j_uid, dx1, dy1, dz - item.height)] 
                                                               for j_uid, j_item in unique_items if j_uid != uid
                                                               for dx1 in range(dx, min(dx + item.length, bin.length - j_item.length + 1))
                                                               for dy1 in range(dy, min(dy + item.width, bin.width - j_item.width + 1))
                                                               if (j_uid, dx1, dy1, dz - item.height) in x)

    # Fragile items cannot have items placed on top of them
    for uid, item in unique_items:
        if item.fragile:
            for dx in range(bin.length - item.length + 1):
                for dy in range(bin.width - item.width + 1):
                    for dz in range(bin.height - item.height):
                        prob += lpSum(x[(j_uid, dx1, dy1, dz1)] 
                                      for j_uid, j_item in unique_items if j_uid != uid
                                      for dx1 in range(max(0, dx - j_item.length + 1), min(dx + item.length, bin.length - j_item.length + 1))
                                      for dy1 in range(max(0, dy - j_item.width + 1), min(dy + item.width, bin.width - j_item.width + 1))
                                      for dz1 in range(dz + item.height, min(dz + item.height + j_item.height, bin.height))
                                      if (j_uid, dx1, dy1, dz1) in x and dx1 + j_item.length > dx and dy1 + j_item.width > dy) <= (1 - x[(uid, dx, dy, dz)]) * 1000

    # Set a time limit for the solver to improve performance
    prob.solve(GUROBI_CMD(msg=1))  # Adjust timeLimit as needed

    # Extract and assign positions
    assigned_positions = set()  # Keep track of assigned positions to ensure no duplicates
    for uid, item in unique_items:
        print(f"Checking placement for item {uid}")
        placed = False
        for dx in range(bin.length - item.length + 1):
            for dy in range(bin.width - item.width + 1):
                for dz in range(bin.height - item.height + 1):
                    if value(x[(uid, dx, dy, dz)]) == 1:
                        print("1...")
                        print(item.id)
                        if (dx, dy, dz) not in assigned_positions:
                            print("2...")
                            print(item.id)
                            item.position = (dx, dy, dz)
                            bin.items.append(item)
                            assigned_positions.add((dx, dy, dz))
                            placed = True
                            print(f"Item {uid} placed at position {item.position}")
                            break  # Exit after placing the item to prevent multiple placements
                        else:
                            print(f"Position {dx, dy, dz} is already occupied!")
                if placed:
                    break
            if placed:
                break

    return prob.status