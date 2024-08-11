class Item:
    def __init__(self, id, length, width, height, weight, stackable, fragile, supplier_id=None, warehouse_id=None, quantity=1, position=None):
        self.id = id
        self.length = length
        self.width = width
        self.height = height
        self.weight = weight
        self.stackable = stackable
        self.fragile = fragile
        self.supplier_id = supplier_id  # Optional: placeholder for supplier ID
        self.warehouse_id = warehouse_id  # Optional: placeholder for warehouse ID
        self.quantity = quantity
        self.position = position if position is not None else (0, 0, 0)

class Bin:
    def __init__(self, length, width, height):
        self.length = length
        self.width = width
        self.height = height
        self.items = []

class Supplier:
    def __init__(self, supplier_id, name, location, inventory):
        self.supplier_id = supplier_id
        self.name = name
        self.location = location  # (latitude, longitude)
        self.inventory = inventory  # {item_id: quantity}

class Warehouse:
    def __init__(self, warehouse_id, name, location):
        self.warehouse_id = warehouse_id
        self.name = name
        self.location = location  # (latitude, longitude)
        self.demand = {}  # Placeholder for demand

class Truck:
    def __init__(self, truck_id, truck_type, bin):
        self.truck_id = truck_id
        self.truck_type = truck_type
        self.bin = bin  # Bin instance that contains dimensions and capacity
        self.items = []

    def can_carry_items(self, items):
        """
        Check if the truck can carry the given list of items without exceeding its capacity
        and dimensions.

        Args:
            items (list[Item]): A list of items to check.

        Returns:
            bool: True if the truck can carry all items, False otherwise.
        """
        total_volume = 0
        for item in items:
            total_volume += item.length * item.width * item.height

        if total_volume <= (self.bin.length * self.bin.width * self.bin.height) and all(
            item.length <= self.bin.length and
            item.width <= self.bin.width and
            item.height <= self.bin.height for item in items):
            return True
        
        return False

class Order:
    def __init__(self, name, warehouse_id, items):
        self.name = name
        self.warehouse_id = warehouse_id
        self.items = items  # [(item_id, qty)]
