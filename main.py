from data_structures import*
from visualize import*
from optimizer import optimize_routes

# Update the main.py code as well:
def main():
    # Generate items with separate objects for each quantity and unique IDs
    items = []
    items.extend(create_items(1, 2, 2, 2, 5, stackable=True, fragile=False, supplier_id=1, warehouse_id=None, quantity=10))
    items.extend(create_items(2, 1, 1, 1, 2, stackable=True, fragile=True, supplier_id=1, warehouse_id=None, quantity=5))
    items.extend(create_items(3, 3, 2, 1, 4, stackable=False, fragile=False, supplier_id=1, warehouse_id=None, quantity=7))
    items.extend(create_items(4, 2, 1, 1, 3, stackable=False, fragile=True, supplier_id=2, warehouse_id=None, quantity=15))
    items.extend(create_items(5, 4, 3, 2, 6, stackable=True, fragile=False, supplier_id=2, warehouse_id=None, quantity=10))

    # Define orders with quantities (the quantity here will match the number of separate Item objects)
    orders = [
        Order("Order A", 1, [(1, 1), (2, 1), (3, 1)]),  # Items 1, 2, 3 go to Warehouse A
        Order("Order B", 2, [(4, 2)]),
    ]

    # Define suppliers and warehouses
    suppliers = [
        Supplier(1, "Supplier A", (40.7128, -74.0060), {1: 10, 2: 5, 3: 7}),
        Supplier(2, "Supplier B", (34.0522, -118.2437), {4: 15, 5: 10}),
    ]

    warehouses = [
        Warehouse(1, "Warehouse A", (41.8781, -87.6298)),
        Warehouse(2, "Warehouse B", (29.7604, -95.3698)),
    ]

    # Define trucks
    trucks = [
        Truck(1, "Truck A", Bin(10, 5, 5)),
        Truck(2, "Truck B", Bin(12, 6, 6)),
    ]

    # Optimize routes based on orders
    optimize_routes(suppliers, warehouses, trucks, orders, items)

    # Print the details of which truck is taking which items
    for truck in trucks:
        print(f"Truck {truck.truck_id} is carrying the following items:")
        for item in truck.bin.items:
            print(f"Item {item.id}-{item.quantity_id} from Supplier {item.supplier_id} to Warehouse {item.warehouse_id} "
                  f"at position {item.position} with dimensions {item.length}x{item.width}x{item.height}.")
        print()

    # Visualize the packed trucks
    for truck in trucks:
        visualize_packing(truck.bin)

if __name__ == "__main__":
    main()