from data_structures import Supplier, Warehouse, Item, Truck, Order, Bin
from optimizer import optimize_routes
from item_placement import optimize_packing
from visualize import visualize_packing

def main():
    # Define items with quantities
    items = [
        Item(id=1, length=2, width=2, height=2, weight=5, stackable=True, fragile=False, supplier_id=1, quantity=10),
        Item(2, 1, 1, 1, 2, stackable=True, fragile=True, supplier_id=1, quantity=5),
        Item(3, 3, 2, 1, 4, stackable=False, fragile=False, supplier_id=1, quantity=7),
        Item(4, 2, 1, 1, 3, stackable=False, fragile=True, supplier_id=2, quantity=15),
        Item(5, 4, 3, 2, 6, stackable=True, fragile=False, supplier_id=2, quantity=10),
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

    # Define orders with quantities
    orders = [
        Order("Order A", 1, [(1, 1), (2, 1), (3, 1)]),  # Items 1, 2, 3 go to Warehouse A
        Order("Order B", 2, [(4, 2)]),          # Items 4, 5 go to Warehouse B
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
            print(f"Item {item.id} from Supplier {item.supplier_id} to Warehouse {item.warehouse_id} "
                  f"at position {item.position} with dimensions {item.length}x{item.width}x{item.height}.")
        print()

    # Visualize the packed trucks
    for truck in trucks:
        visualize_packing(truck.bin)

if __name__ == "__main__":
    main()