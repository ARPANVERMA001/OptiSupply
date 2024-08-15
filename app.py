import numpy as np
from flask import Flask, request, jsonify
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, GUROBI_CMD, value
import matplotlib.colors as mcolors
from matplotlib.path import Path
from mpl_toolkits.mplot3d import proj3d
import matplotlib.pyplot as plt
from optimizer import optimize_routes
from data_structures import *
from item_placement import optimize_packing
from converter import *
import json
app = Flask(__name__)

# class Item:
#     def __init__(self, id, length, width, height, weight, stackable, fragile):
#         self.id = id
#         self.length = length
#         self.width = width
#         self.height = height
#         self.weight = weight
#         self.stackable = stackable
#         self.fragile = fragile
#         self.position = None

#     def __str__(self):
#         return f"Item {self.id}: {self.length}x{self.width}x{self.height}, Weight: {self.weight}, {'Stackable' if self.stackable else 'Not Stackable'}, {'Fragile' if self.fragile else 'Not Fragile'}"

#     def __repr__(self):
#         return f"Item(id={self.id}, length={self.length}, width={self.width}, height={self.height}, weight={self.weight}, stackable={self.stackable}, fragile={self.fragile}, position={self.position})"

# class Bin:
#     def __init__(self, length, width, height):
#         self.length = length
#         self.width = width
#         self.height = height
#         self.items = []

# def optimize_packing(bin, items):
#     prob = LpProblem("3D_Bin_Packing", LpMaximize)

#     # Variables: x[(item_id, dx, dy, dz)] = 1 if item is placed at (dx, dy, dz)
#     x = LpVariable.dicts("item_placement", 
#                          [(i.id, dx, dy, dz) for i in items 
#                           for dx in range(bin.length - i.length + 1)
#                           for dy in range(bin.width - i.width + 1)
#                           for dz in range(bin.height - i.height + 1)], 
#                          cat='Binary')

#     # Objective: Maximize the number of items placed with a slight preference for end-filling
#     prob += lpSum(x[(i.id, dx, dy, dz)] * (1 + 0.01 * dx / bin.length) for i in items 
#                   for dx in range(bin.length - i.length + 1)
#                   for dy in range(bin.width - i.width + 1)
#                   for dz in range(bin.height - i.height + 1))

#     # Constraint: Each item can be placed at most once
#     for i in items:
#         prob += lpSum(x[(i.id, dx, dy, dz)] for dx in range(bin.length - i.length + 1)
#                       for dy in range(bin.width - i.width + 1)
#                       for dz in range(bin.height - i.height + 1)) <= 1

#     # Constraint: No overlapping of items
#     for px in range(bin.length):
#         for py in range(bin.width):
#             for pz in range(bin.height):
#                 prob += lpSum(x[(i.id, dx, dy, dz)] 
#                               for i in items
#                               for dx in range(max(0, px - i.length + 1), min(px + 1, bin.length - i.length + 1))
#                               for dy in range(max(0, py - i.width + 1), min(py + 1, bin.width - i.width + 1))
#                               for dz in range(max(0, pz - i.height + 1), min(pz + 1, bin.height - i.height + 1))
#                               if dx + i.length > px and dy + i.width > py and dz + i.height > pz) <= 1

#     # Constraint: Items must be supported (not in mid-air)
#     for i in items:
#         for dx in range(bin.length - i.length + 1):
#             for dy in range(bin.width - i.width + 1):
#                 for dz in range(1, bin.height - i.height + 1):
#                     prob += x[(i.id, dx, dy, dz)] <= lpSum(x[(j.id, dx1, dy1, dz - 1)] 
#                                                            for j in items if j.id != i.id
#                                                            for dx1 in range(max(0, dx - j.length + 1), min(dx + i.length, bin.length - j.length + 1))
#                                                            for dy1 in range(max(0, dy - j.width + 1), min(dy + i.width, bin.width - j.width + 1))
#                                                            if (j.id, dx1, dy1, dz - 1) in x and dx1 + j.length > dx and dy1 + j.width > dy)

#     # Constraint: Stackable items can be placed on top of other items with appropriate sizing
#     for i in items:
#         if i.stackable:
#             for dx in range(bin.length - i.length + 1):
#                 for dy in range(bin.width - i.width + 1):
#                     for dz in range(1, bin.height - i.height + 1):
#                         prob += x[(i.id, dx, dy, dz)] <= lpSum(x[(j.id, dx1, dy1, dz - 1)] 
#                                                                for j in items if j.id != i.id and j.length >= i.length and j.width >= i.width
#                                                                for dx1 in range(max(0, dx - j.length + i.length), min(dx + 1, bin.length - j.length + 1))
#                                                                for dy1 in range(max(0, dy - j.width + i.width), min(dy + 1, bin.width - j.width + 1))
#                                                                if (j.id, dx1, dy1, dz - 1) in x and dx1 + j.length >= dx + i.length and dy1 + j.width >= dy + i.width)

#     # Constraint: Fragile items must be placed on the floor or fully supported
#     for i in items:
#         if i.fragile:
#             for dx in range(bin.length - i.length + 1):
#                 for dy in range(bin.width - i.width + 1):
#                     for dz in range(1, bin.height - i.height + 1):
#                         prob += x[(i.id, dx, dy, dz)] <= lpSum(x[(j.id, dx1, dy1, dz - 1)] 
#                                                                for j in items if j.id != i.id and j.length >= i.length and j.width >= i.width
#                                                                for dx1 in range(dx, dx + i.length)
#                                                                for dy1 in range(dy, dy + i.width)
#                                                                if (j.id, dx1, dy1, dz - 1) in x)

#     # Constraint: Fragile items cannot have items placed on top of them
#     for i in items:
#         if i.fragile:
#             for dx in range(bin.length - i.length + 1):
#                 for dy in range(bin.width - i.width + 1):
#                     for dz in range(bin.height - i.height):
#                         prob += lpSum(x[(j.id, dx1, dy1, dz1)] 
#                                       for j in items if j.id != i.id
#                                       for dx1 in range(max(0, dx - j.length + 1), min(dx + i.length, bin.length - j.length + 1))
#                                       for dy1 in range(max(0, dy - j.width + 1), min(dy + i.width, bin.width - j.width + 1))
#                                       for dz1 in range(dz + i.height, min(dz + i.height + j.height, bin.height))
#                                       if (j.id, dx1, dy1, dz1) in x and dx1 + j.length > dx and dy1 + j.width > dy) <= (1 - x[(i.id, dx, dy, dz)]) * 1000

#     prob.solve(GUROBI_CMD(msg=1, timeLimit=600))


#     for i in items:
#         for dx in range(bin.length - i.length + 1):
#             for dy in range(bin.width - i.width + 1):
#                 for dz in range(bin.height - i.height + 1):
#                     if value(x[(i.id, dx, dy, dz)]) == 1:
#                         i.position = (dx, dy, dz)
#                         bin.items.append(i)

#     return prob.status


# def place_items(bin, items):
#     optimize_packing(bin, items)

def print_item_positions(bin):
    positions = []
    for item in bin.items:
        if item.position is not None:
            positions.append({
                "id": item.id,
                "position": item.position,
                "dimensions": (item.length, item.width, item.height)
            })
    return positions
def trucks_to_json(trucks):
    trucks_data = []
    print("############")
    print(trucks)
    print("############")

    for truck in trucks:
        truck_info = {
            "truckId": truck.truck_id,
            "items": [
                {
                    "itemId": item.id,
                    "quantity_id": item.quantity_id,
                    "position": item.position,
                    "dimensions": (item.length, item.width, item.height),
                    "supplier": item.supplier_id,
                    "warehouse": item.warehouse_id
                }
                for item in truck.bin.items
            ]
        }
        trucks_data.append(truck_info)
    
    return trucks_data


@app.route('/solve',methods=['POST'])
def solve():
    data = request.json
    trucks_data = data['trucks']
    orders_data = data['orders']
    suppliers_data=data['suppliers']
    warehouses_data=data['warehouses']
    items_data=data['items']
    print("########trucks#########")
    print(trucks_data)
    print("########orders#########")
    print(orders_data)
    print("########suppliers#########")
    print(suppliers_data)
    print("########warehouses#########")
    print(warehouses_data)
    print("########Items#########")
    print(items_data)
    suppliers = convert_suppliers(suppliers_data)
    trucks = convert_trucks(trucks_data)
    orders = convert_orders(orders_data)
    warehouses = convert_warehouses(warehouses_data)
    all_items=convert_items(items_data)
    items = []
    for order in orders:
        for item_id, quantity in order.items:
            matching_items = [item for item in all_items if item.id == item_id and item not in items]
            for i in range(quantity):
                item = matching_items[i]
                item.warehouse_id = order.warehouse_id  # Assign the correct warehouse
                item.quantity_id = len([it for it in items if it.id == item_id]) + 1  # Ensure unique quantity_id
                items.append(item)
    for warehouse in warehouses:
        warehouse.demand = {}
        for item in items:
            if item.warehouse_id == warehouse.warehouse_id:
                if item.id in warehouse.demand:
                    warehouse.demand[item.id] += 1
                else:
                    warehouse.demand[item.id] = 1
    def debug_data(suppliers, warehouses, trucks, items):
        print("Suppliers:")
        for s in suppliers:
            print(f"  {s.supplier_id}: {s.location}")
        
        print("\nWarehouses:")
        for w in warehouses:
            print(f"  {w.warehouse_id}: {w.location}")
        
        print("\nTrucks:")
        for t in trucks:
            print(f"  {t.truck_id}: Capacity {t.bin.length, t.bin.width, t.bin.height}")
        
        print("\nItems:")
        for i in items:
            print(f"  {i.id}-{i.quantity_id}: Volume {i.length, i.width, i.height}, Supplier {i.supplier_id}, Warehouse {i.warehouse_id}")

        
        print("\nWarehouses Demand:")
        for w in warehouses:
            print(f"Warehouse {w.warehouse_id} Demand: {w.demand}")
        
        print("\nSupplier Inventory:")
        for s in suppliers:
            print(f"Supplier {s.supplier_id} Inventory: {s.inventory}")

    debug_data(suppliers, warehouses, trucks, items)
    optimize_routes(suppliers, warehouses, trucks, orders, items)
    for truck in trucks:
        print(f"Truck {truck.truck_id} is carrying the following items:")
        for item in truck.bin.items:
            print(f"Item {item.id}-{item.quantity_id} from Supplier {item.supplier_id} to Warehouse {item.warehouse_id} "
                  f"at position {item.position} with dimensions {item.length}x{item.width}x{item.height}.")
        print()
    result=trucks_to_json(trucks)
    print(result)
    # Create Trucks
# trucks = [Truck(t['truckId'], t['name'], Bin(t['dim']['l'], t['dim']['b'], t['dim']['h'])) for t in trucks_data]

    return jsonify({'data':result})

@app.route('/pack', methods=['POST'])
def pack():
    data = request.json
    bin_data = data['bin']
    items_data = data['items']
    # print(items_data)
    bin = Bin(bin_data['length'], bin_data['width'], bin_data['height'])
    items = [Item(item['id'], item['l'], item['b'], item['h'], item['weight'], item['stackable'], item['fragile']) for item in items_data]
    
    print(items)
    print('#####')
    print(bin.length,bin.height,bin.width)
    optimize_packing(bin, items)
    # optimize_routes(suppliers, warehouses, trucks, orders, items)
    

    positions = print_item_positions(bin)
    return jsonify({"status": "success", "positions": positions})
    # return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
