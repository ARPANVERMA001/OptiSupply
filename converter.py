from data_structures import*

def convert_trucks(trucks_data):
    trucks = []
    for truck in trucks_data:
        bin_dimensions = truck['dim']
        truck_instance = Truck(
            truck_id=truck['truckId'],
            truck_type=truck['name'],
            bin=Bin(
                length=bin_dimensions['l'],
                width=bin_dimensions['b'],
                height=bin_dimensions['h']
            )
        )
        trucks.append(truck_instance)
    return trucks

def convert_orders(orders_data):
    orders = []
    for order in orders_data:
        items = [(item['item'], item['qty']) for item in order['items']]
        order_instance = Order(
            name="Order " + str(order['_id']),  # Assuming order name is derived from ID
            warehouse_id=order['warehouse'],
            items=items
        )
        orders.append(order_instance)
    return orders
def convert_items(items_data):
    items = []
    for item in items_data:
        item_instance = create_items(
            item_id=item['itemId'],
            quantity=100,  # This field is not present in the provided data, so set to None or provide a default value
            length=item['dim']['l'],
            width=item['dim']['b'],
            height=item['dim']['h'],
            weight=item['weight'],
            stackable=item['stackable'],
            fragile=item['fragile']
        )
        items.extend(item_instance)
    return items

def convert_suppliers(suppliers_data):
    suppliers = []
    for supplier in suppliers_data:
        inventory = {inv['itemId']: inv['qty'] for inv in supplier['inventories']}
        supplier_instance = Supplier(
            supplier_id=supplier['supplierId'],
            name=supplier['name'],
            location=(supplier['lat'], supplier['long']),
            inventory=inventory
        )
        suppliers.append(supplier_instance)
    return suppliers

def convert_warehouses(warehouses_data):
    warehouses = []
    for warehouse in warehouses_data:
        warehouse_instance = Warehouse(
            warehouse_id=warehouse['warehouseId'],
            name=warehouse['name'],
            location=(warehouse['lat'], warehouse['long'])
        )
        warehouses.append(warehouse_instance)
    return warehouses
