# # from data_structures import *
# # from visualize import *
# # from optimizer import optimize_routes, calculate_distance

# # # Update the main.py code as well:
# # def main():
# #     # Generate all possible items (this remains the same)
# #     all_items = []
# #     all_items.extend(create_items(1, 2, 2, 2, 5, stackable=True, fragile=False, supplier_id=None, warehouse_id=None, quantity=30))
# #     all_items.extend(create_items(2, 1, 1, 1, 2, stackable=True, fragile=True, supplier_id=None, warehouse_id=None, quantity=30))
# #     all_items.extend(create_items(3, 3, 2, 1, 4, stackable=False, fragile=False, supplier_id=None, warehouse_id=None, quantity=30))
# #     all_items.extend(create_items(4, 2, 1, 1, 3, stackable=False, fragile=True, supplier_id=None, warehouse_id=None, quantity=30))
# #     all_items.extend(create_items(5, 4, 3, 2, 6, stackable=True, fragile=False, supplier_id=None, warehouse_id=None, quantity=30))

# #     # Define orders with quantities (the quantity here will match the number of separate Item objects)
# #     orders = [
# #         Order("Order A", 1, [(1, 1), (2, 1), (3, 1)]),  # Items 1, 2, 3 go to Warehouse A
# #         Order("Order B", 2, [(1,1)])
# #     ]

# #     # Filter items to only those that are in the orders
# #     items = []
# #     for order in orders:
# #         for item_id, quantity in order.items:
# #             for _ in range(quantity):
# #                 # Find and append the matching item from all_items
# #                 matching_item = next(item for item in all_items if item.id == item_id)
# #                 items.append(matching_item)

# #     # Define suppliers and warehouses with NCR locations
# #     suppliers = [
# #         Supplier(1, "Supplier A", (28.4595, 77.0266), {1: 30, 2: 30, 3: 30}),  # Gurugram (Gurgaon)
# #         Supplier(2, "Supplier B", (28.4089, 77.3178), {4: 30, 5: 30}),  # Faridabad
# #     ]

# #     warehouses = [
# #         Warehouse(1, "Warehouse A", (28.5355, 77.3910)),  # Noida
# #         Warehouse(2, "Warehouse B", (28.6139, 77.2090)),  # Delhi
# #     ]

# #     # Define trucks
# #     trucks = [
# #         Truck(1, "Truck A", Bin(10, 5, 5)),
# #         Truck(2, "Truck B", Bin(12, 6, 6)),
# #         Truck(3, "Truck C", Bin(18, 4, 8)),
# #     ]

# #     # Optimize routes based on orders
# #     def debug_data(suppliers, warehouses, trucks, items):
# #         print("Suppliers:")
# #         for s in suppliers:
# #             print(f"  {s.supplier_id}: {s.location}")
        
# #         print("\nWarehouses:")
# #         for w in warehouses:
# #             print(f"  {w.warehouse_id}: {w.location}")
        
# #         print("\nTrucks:")
# #         for t in trucks:
# #             print(f"  {t.truck_id}: Capacity {t.bin.length, t.bin.width, t.bin.height}")
        
# #         print("\nItems:")
# #         for i in items:
# #             print(f"  {i.id}: Volume {i.length, i.width, i.height}, Supplier {i.supplier_id}, Warehouse {i.warehouse_id}")

# #         print("\nDistances:")
# #         for s in suppliers:
# #             for w in warehouses:
# #                 dist = calculate_distance(s.location, w.location)
# #                 print(f"  Supplier {s.supplier_id} to Warehouse {w.warehouse_id}: {dist:.2f} meters")

# #     # Call this function before running the optimization
# #     debug_data(suppliers, warehouses, trucks, items)
# #     # optimize_routes(suppliers, warehouses, trucks, items)
# #     optimize_routes(suppliers, warehouses, trucks, orders, items)

# #     # Print the details of which truck is taking which items
# #     for truck in trucks:
# #         print(f"Truck {truck.truck_id} is carrying the following items:")
# #         for item in truck.bin.items:
# #             print(f"Item {item.id}-{item.quantity_id} from Supplier {item.supplier_id} to Warehouse {item.warehouse_id} "
# #                   f"at position {item.position} with dimensions {item.length}x{item.width}x{item.height}.")
# #         print()

# #     # # Visualize the packed trucks
# #     # for truck in trucks:
# #     #     visualize_packing(truck.bin)

# # if _name_ == "_main_":
# #     main()


# from data_structures import *
# from visualize import *
# from optimizer import optimize_routes, calculate_distance

# def main():
#     # Generate all possible items (this remains the same)
#     all_items = []
#     all_items.extend(create_items(1, 2, 2, 2, 5, stackable=True, fragile=False, supplier_id=None, warehouse_id=None, quantity=30))
#     all_items.extend(create_items(2, 1, 1, 1, 2, stackable=True, fragile=True, supplier_id=None, warehouse_id=None, quantity=30))
#     all_items.extend(create_items(3, 3, 2, 1, 4, stackable=False, fragile=False, supplier_id=None, warehouse_id=None, quantity=30))
#     all_items.extend(create_items(4, 2, 1, 1, 3, stackable=False, fragile=True, supplier_id=None, warehouse_id=None, quantity=30))
#     all_items.extend(create_items(5, 4, 3, 2, 6, stackable=True, fragile=False, supplier_id=None, warehouse_id=None, quantity=30))

#     # Define orders with quantities (the quantity here will match the number of separate Item objects)
#     orders = [
#         Order("Order A", 1, [(1, 1), (2, 1), (3, 1)]),  # Items 1, 2, 3 go to Warehouse A
#         Order("Order B", 2, [(1,1)])  # Item 1 goes to Warehouse B
#     ]

#     # Define suppliers and warehouses with NCR locations
#     suppliers = [
#         Supplier(1, "Supplier A", (28.4595, 77.0266), {1: 30, 2: 30, 3: 30}),  # Gurugram (Gurgaon)
#         Supplier(2, "Supplier B", (28.4089, 77.3178), {4: 30, 5: 30}),  # Faridabad
#     ]

#     warehouses = [
#         Warehouse(1, "Warehouse A", (28.5355, 77.3910)),  # Noida
#         Warehouse(2, "Warehouse B", (28.6139, 77.2090)),  # Delhi
#     ]

#     # Define trucks
#     trucks = [
#         Truck(1, "Truck A", Bin(10, 5, 5)),
#         Truck(2, "Truck B", Bin(12, 6, 6)),
#         Truck(3, "Truck C", Bin(18, 4, 8)),
#     ]

#     # Filter items to only those that are in the orders
#     items = []
#     for order in orders:
#         for item_id, quantity in order.items:
#             for _ in range(quantity):
#                 matching_item = next(item for item in all_items if item.id == item_id)
#                 matching_item.warehouse_id = order.warehouse_id  # Assign the correct warehouse
#                 items.append(matching_item)

#     # Debugging: Print out the items, suppliers, and warehouses before optimization
#     def debug_data(suppliers, warehouses, trucks, items):
#         print("Suppliers:")
#         for s in suppliers:
#             print(f"  {s.supplier_id}: {s.location}")
        
#         print("\nWarehouses:")
#         for w in warehouses:
#             print(f"  {w.warehouse_id}: {w.location}")
        
#         print("\nTrucks:")
#         for t in trucks:
#             print(f"  {t.truck_id}: Capacity {t.bin.length, t.bin.width, t.bin.height}")
        
#         print("\nItems:")
#         for i in items:
#             print(f"  {i.id}-{i.quantity_id}: Volume {i.length, i.width, i.height}, Supplier {i.supplier_id}, Warehouse {i.warehouse_id}")

#         print("\nDistances:")
#         for s in suppliers:
#             for w in warehouses:
#                 dist = calculate_distance(s.location, w.location)
#                 print(f"  Supplier {s.supplier_id} to Warehouse {w.warehouse_id}: {dist:.2f} meters")

#     debug_data(suppliers, warehouses, trucks, items)

#     # Optimize routes based on orders
#     optimize_routes(suppliers, warehouses, trucks, orders, items)

#     # Print the details of which truck is taking which items
#     for truck in trucks:
#         print(f"Truck {truck.truck_id} is carrying the following items:")
#         for item in truck.bin.items:
#             print(f"Item {item.id}-{item.quantity_id} from Supplier {item.supplier_id} to Warehouse {item.warehouse_id} "
#                   f"at position {item.position} with dimensions {item.length}x{item.width}x{item.height}.")
#         print()

#     # Visualize the packed trucks (optional)
#     # for truck in trucks:
#     #     visualize_packing(truck.bin)

# if _name_ == "_main_":
#     main()



from data_structures import *
from visualize import *
from optimizer import optimize_routes, calculate_distance

def main():
    # Generate all possible items (this remains the same)
    all_items = []
    all_items.extend(create_items(1, 2, 2, 2, 5, stackable=True, fragile=False, supplier_id=None, warehouse_id=None, quantity=30))
    all_items.extend(create_items(2, 1, 1, 1, 2, stackable=True, fragile=True, supplier_id=None, warehouse_id=None, quantity=30))
    all_items.extend(create_items(3, 3, 2, 1, 4, stackable=False, fragile=False, supplier_id=None, warehouse_id=None, quantity=30))
    all_items.extend(create_items(4, 2, 1, 1, 3, stackable=False, fragile=True, supplier_id=None, warehouse_id=None, quantity=30))
    all_items.extend(create_items(5, 4, 3, 2, 6, stackable=True, fragile=False, supplier_id=None, warehouse_id=None, quantity=30))

    # Define orders with quantities (the quantity here will match the number of separate Item objects)
    orders = [
        Order("Order A", 1, [(1, 1), (2, 1), (3, 1)]),  # Items 1, 2, 3 go to Warehouse A
        Order("Order B", 2, [(1, 1)])  # Item 1 goes to Warehouse B
    ]

    # Define suppliers and warehouses with NCR locations
    suppliers = [
        Supplier(1, "Supplier A", (28.4595, 77.0266), {1: 30, 2: 30, 3: 30}),  # Gurugram (Gurgaon)
        Supplier(2, "Supplier B", (28.4089, 77.3178), {4: 30, 5: 30}),  # Faridabad
    ]

    warehouses = [
        Warehouse(1, "Warehouse A", (28.5355, 77.3910)),  # Noida
        Warehouse(2, "Warehouse B", (28.6139, 77.2090)),  # Delhi
    ]

    # Define trucks
    trucks = [
        Truck(1, "Truck A", Bin(10, 5, 5)),
        Truck(2, "Truck B", Bin(12, 6, 6)),
        Truck(3, "Truck C", Bin(18, 4, 8)),
    ]

    # Filter items to only those that are in the orders
    items = []
    for order in orders:
        for item_id, quantity in order.items:
            matching_items = [item for item in all_items if item.id == item_id and item not in items]
            for i in range(quantity):
                item = matching_items[i]
                item.warehouse_id = order.warehouse_id  # Assign the correct warehouse
                item.quantity_id = len([it for it in items if it.id == item_id]) + 1  # Ensure unique quantity_id
                items.append(item)
    
    # Calculate warehouse demand from filtered items
    for warehouse in warehouses:
        warehouse.demand = {}
        for item in items:
            if item.warehouse_id == warehouse.warehouse_id:
                if item.id in warehouse.demand:
                    warehouse.demand[item.id] += 1
                else:
                    warehouse.demand[item.id] = 1
    
    # Debugging: Print out the items, suppliers, and warehouses before optimization
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

        print("\nDistances:")
        for s in suppliers:
            for w in warehouses:
                dist = calculate_distance(s.location, w.location)
                print(f"  Supplier {s.supplier_id} to Warehouse {w.warehouse_id}: {dist:.2f} meters")
        print("\nWarehouses Demand:")
        for w in warehouses:
            print(f"Warehouse {w.warehouse_id} Demand: {w.demand}")
        
        print("\nSupplier Inventory:")
        for s in suppliers:
            print(f"Supplier {s.supplier_id} Inventory: {s.inventory}")

    debug_data(suppliers, warehouses, trucks, items)

    # Optimize routes based on orders
    # optimize_routes(suppliers, warehouses, trucks, items)
    optimize_routes(suppliers, warehouses, trucks, orders, items)

    # Print the details of which truck is taking which items
    for truck in trucks:
        print(f"Truck {truck.truck_id} is carrying the following items:")
        for item in truck.bin.items:
            print(f"Item {item.id}-{item.quantity_id} from Supplier {item.supplier_id} to Warehouse {item.warehouse_id} "
                  f"at position {item.position} with dimensions {item.length}x{item.width}x{item.height}.")
        print()

    # Visualize the packed trucks (optional)
    for truck in trucks:
        visualize_packing(truck.bin)

if _name_ == "_main_":
    main()