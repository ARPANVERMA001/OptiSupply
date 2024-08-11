from pulp import LpProblem, LpMaximize, LpVariable, lpSum, GUROBI_CMD, value

def optimize_packing(bin, items):
    """
    This function optimizes the placement of items within a bin (truck) using a 3D bin-packing algorithm.
    It ensures that the items are packed efficiently within the bin's dimensions, respecting constraints like
    stackability and avoiding overlaps.

    Args:
        bin (Bin): The bin (truck capacity) in which the items need to be packed.
        items (list[Item]): The list of items to be packed.

    Returns:
        None: The function modifies the `position` attribute of each `Item` in the list to reflect its placement
        within the bin.
    """
    prob = LpProblem("3D_Bin_Packing", LpMaximize)

    # Define decision variables for item placement
    x = LpVariable.dicts("item_placement", 
                         [(i.id, dx, dy, dz) for i in items 
                          for dx in range(bin.length - i.length + 1)
                          for dy in range(bin.width - i.width + 1)
                          for dz in range(bin.height - i.height + 1)], 
                         cat='Binary')

    # Objective: Maximize space utilization
    prob += lpSum(x[(i.id, dx, dy, dz)] * (1 + 0.01 * dx / bin.length) for i in items 
                  for dx in range(bin.length - i.length + 1)
                  for dy in range(bin.width - i.width + 1)
                  for dz in range(bin.height - i.height + 1))

    # Each item can only be placed in one position
    for i in items:
        prob += lpSum(x[(i.id, dx, dy, dz)] for dx in range(bin.length - i.length + 1)
                      for dy in range(bin.width - i.width + 1)
                      for dz in range(bin.height - i.height + 1)) <= 1

    # Ensure items do not overlap in the bin
    for px in range(bin.length):
        for py in range(bin.width):
            for pz in range(bin.height):
                prob += lpSum(x[(i.id, dx, dy, dz)] 
                              for i in items
                              for dx in range(max(0, px - i.length + 1), min(px + 1, bin.length - i.length + 1))
                              for dy in range(max(0, py - i.width + 1), min(py + 1, bin.width - i.width + 1))
                              for dz in range(max(0, pz - i.height + 1), min(pz + 1, bin.height - i.height + 1))
                              if dx + i.length > px and dy + i.width > py and dz + i.height > pz) <= 1

    # Stackable items constraint: Ensure stackable items can only be placed on other items
    for i in items:
        if i.stackable:
            for dx in range(bin.length - i.length + 1):
                for dy in range(bin.width - i.width + 1):
                    for dz in range(1, bin.height - i.height + 1):  # Start from height 1 to allow stacking
                        prob += x[(i.id, dx, dy, dz)] <= lpSum(x[(j.id, dx1, dy1, dz - i.height)] 
                                                               for j in items if j.id != i.id
                                                               for dx1 in range(dx, min(dx + i.length, bin.length - j.length + 1))
                                                               for dy1 in range(dy, min(dy + i.width, bin.width - j.width + 1))
                                                               if (j.id, dx1, dy1, dz - i.height) in x)

    # Fragile items must be placed on the floor or fully supported
    for i in items:
        if i.fragile:
            for dx in range(bin.length - i.length + 1):
                for dy in range(bin.width - i.width + 1):
                    for dz in range(1, bin.height - i.height + 1):
                        prob += x[(i.id, dx, dy, dz)] <= lpSum(x[(j.id, dx1, dy1, dz - i.height)] 
                                                               for j in items if j.id != i.id
                                                               for dx1 in range(dx, min(dx + i.length, bin.length - j.length + 1))
                                                               for dy1 in range(dy, min(dy + i.width, bin.width - j.width + 1))
                                                               if (j.id, dx1, dy1, dz - i.height) in x)

    # Fragile items cannot have items placed on top of them
    for i in items:
        if i.fragile:
            for dx in range(bin.length - i.length + 1):
                for dy in range(bin.width - i.width + 1):
                    for dz in range(bin.height - i.height):
                        prob += lpSum(x[(j.id, dx1, dy1, dz1)] 
                                      for j in items if j.id != i.id
                                      for dx1 in range(max(0, dx - j.length + 1), min(dx + i.length, bin.length - j.length + 1))
                                      for dy1 in range(max(0, dy - j.width + 1), min(dy + i.width, bin.width - j.width + 1))
                                      for dz1 in range(dz + i.height, min(dz + i.height + j.height, bin.height))
                                      if (j.id, dx1, dy1, dz1) in x and dx1 + j.length > dx and dy1 + j.width > dy) <= (1 - x[(i.id, dx, dy, dz)]) * 1000

    # Set a time limit for the solver to improve performance
    prob.solve(GUROBI_CMD(msg=1, timeLimit=100))  # Adjust timeLimit as needed

    # Extract and assign positions
    for i in items:
        for dx in range(bin.length - i.length + 1):
            for dy in range(bin.width - i.width + 1):
                for dz in range(bin.height - i.height + 1):
                    if value(x[(i.id, dx, dy, dz)]) == 1:
                        i.position = (dx, dy, dz)
                        bin.items.append(i)
                        break  # Exit after placing the item to prevent multiple placements

    return prob.status