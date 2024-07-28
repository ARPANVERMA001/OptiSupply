import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, GUROBI_CMD, value
from pulp import *
import matplotlib.colors as mcolors
from matplotlib.path import Path
from mpl_toolkits.mplot3d import proj3d
import numpy as np

class Item:
    def __init__(self, id, length, width, height, weight, stackable, fragile):
        self.id = id
        self.length = length
        self.width = width
        self.height = height
        self.weight = weight
        self.stackable = stackable
        self.fragile = fragile
        self.position = None

class Bin:
    def __init__(self, length, width, height):
        self.length = length
        self.width = width
        self.height = height
        self.items = []

def optimize_packing(bin, items):
    prob = LpProblem("3D_Bin_Packing", LpMaximize)

    # Variables: x[(item_id, dx, dy, dz)] = 1 if item is placed at (dx, dy, dz)
    x = LpVariable.dicts("item_placement", 
                         [(i.id, dx, dy, dz) for i in items 
                          for dx in range(bin.length - i.length + 1)
                          for dy in range(bin.width - i.width + 1)
                          for dz in range(bin.height - i.height + 1)], 
                         cat='Binary')

    # Objective: Maximize the number of items placed with a slight preference for end-filling
    prob += lpSum(x[(i.id, dx, dy, dz)] * (1 + 0.01 * dx / bin.length) for i in items 
                  for dx in range(bin.length - i.length + 1)
                  for dy in range(bin.width - i.width + 1)
                  for dz in range(bin.height - i.height + 1))

    # Constraint: Each item can be placed at most once
    for i in items:
        prob += lpSum(x[(i.id, dx, dy, dz)] for dx in range(bin.length - i.length + 1)
                      for dy in range(bin.width - i.width + 1)
                      for dz in range(bin.height - i.height + 1)) <= 1

    # Constraint: No overlapping of items
    for px in range(bin.length):
        for py in range(bin.width):
            for pz in range(bin.height):
                prob += lpSum(x[(i.id, dx, dy, dz)] 
                              for i in items
                              for dx in range(max(0, px - i.length + 1), min(px + 1, bin.length - i.length + 1))
                              for dy in range(max(0, py - i.width + 1), min(py + 1, bin.width - i.width + 1))
                              for dz in range(max(0, pz - i.height + 1), min(pz + 1, bin.height - i.height + 1))
                              if dx + i.length > px and dy + i.width > py and dz + i.height > pz) <= 1

    # Constraint: Items must be supported (not in mid-air)
    for i in items:
        for dx in range(bin.length - i.length + 1):
            for dy in range(bin.width - i.width + 1):
                for dz in range(1, bin.height - i.height + 1):
                    prob += x[(i.id, dx, dy, dz)] <= lpSum(x[(j.id, dx1, dy1, dz - 1)] 
                                                           for j in items if j.id != i.id
                                                           for dx1 in range(max(0, dx - j.length + 1), min(dx + i.length, bin.length - j.length + 1))
                                                           for dy1 in range(max(0, dy - j.width + 1), min(dy + i.width, bin.width - j.width + 1))
                                                           if (j.id, dx1, dy1, dz - 1) in x and dx1 + j.length > dx and dy1 + j.width > dy)

    # Constraint: Stackable items can be placed on top of other items with appropriate sizing
    for i in items:
        if i.stackable:
            for dx in range(bin.length - i.length + 1):
                for dy in range(bin.width - i.width + 1):
                    for dz in range(1, bin.height - i.height + 1):
                        prob += x[(i.id, dx, dy, dz)] <= lpSum(x[(j.id, dx1, dy1, dz - 1)] 
                                                               for j in items if j.id != i.id and j.length >= i.length and j.width >= i.width
                                                               for dx1 in range(max(0, dx - j.length + i.length), min(dx + 1, bin.length - j.length + 1))
                                                               for dy1 in range(max(0, dy - j.width + i.width), min(dy + 1, bin.width - j.width + 1))
                                                               if (j.id, dx1, dy1, dz - 1) in x and dx1 + j.length >= dx + i.length and dy1 + j.width >= dy + i.width)

    # Constraint: Fragile items must be placed on the floor or fully supported
    for i in items:
        if i.fragile:
            for dx in range(bin.length - i.length + 1):
                for dy in range(bin.width - i.width + 1):
                    for dz in range(1, bin.height - i.height + 1):
                        prob += x[(i.id, dx, dy, dz)] <= lpSum(x[(j.id, dx1, dy1, dz - 1)] 
                                                               for j in items if j.id != i.id and j.length >= i.length and j.width >= i.width
                                                               for dx1 in range(dx, dx + i.length)
                                                               for dy1 in range(dy, dy + i.width)
                                                               if (j.id, dx1, dy1, dz - 1) in x)

    # Constraint: Fragile items cannot have items placed on top of them
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

    prob.solve(GUROBI_CMD(msg=1, timeLimit=600))


    for i in items:
        for dx in range(bin.length - i.length + 1):
            for dy in range(bin.width - i.width + 1):
                for dz in range(bin.height - i.height + 1):
                    if value(x[(i.id, dx, dy, dz)]) == 1:
                        i.position = (dx, dy, dz)
                        bin.items.append(i)

    return prob.status

def place_items(bin, items):
    optimize_packing(bin, items)


def plot_cuboid(ax, x, y, z, dx, dy, dz, edge_color='black', face_color='gray', alpha=0.5):
    xx = [x, x, x+dx, x+dx, x]
    yy = [y, y+dy, y+dy, y, y]
    zz = [z, z, z, z, z]
    ax.plot3D(xx, yy, zz, color=edge_color, linewidth=0.5)
    ax.plot3D(xx, yy, [z+dz]*5, color=edge_color, linewidth=0.5)
    for X, Y in zip(xx, yy):
        ax.plot3D([X, X], [Y, Y], [z, z+dz], color=edge_color, linewidth=0.5)
    
    faces = [
        [xx[0], yy[0], z], [xx[1], yy[1], z], [xx[2], yy[2], z], [xx[3], yy[3], z],
        [xx[0], yy[0], z+dz], [xx[1], yy[1], z+dz], [xx[2], yy[2], z+dz], [xx[3], yy[3], z+dz]
    ]
    poly = Poly3DCollection([faces], alpha=alpha)
    poly.set_facecolor(face_color)
    poly.set_edgecolor(edge_color)
    ax.add_collection3d(poly)

    return poly

def visualize_packing(bin):
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111, projection='3d')

    truck_length, truck_width, truck_height = bin.length, bin.width, bin.height
    
    # cab_length = 3
    # Truck cabin (darker gray)
    # plot_cuboid(ax, 0, 0, 0, cab_length, truck_width, truck_height, edge_color='black', face_color='#404040', alpha=0.8)
    
    plot_cuboid(ax, 0, 0, 0, truck_length, truck_width, truck_height, edge_color='black', face_color='#808080', alpha=0.0)
    
  
    floor = Poly3DCollection([[
        [0, 0, 0],
        [truck_length, 0, 0],
        [truck_length, truck_width, 0],
        [0, truck_width, 0]
    ]], alpha=0.2)
    floor.set_facecolor('gray')
    ax.add_collection3d(floor)

    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FED766', '#2AB7CA', '#F0B67F']
    item_polygons = {}
    for item in bin.items:
        base_color = colors[item.id % len(colors)]
        edge_color = mcolors.to_rgba(base_color, 0.8)
        face_color = mcolors.to_rgba(base_color, 0.6)
        poly = plot_cuboid(ax, *item.position, item.length, item.width, item.height, edge_color=edge_color, face_color=face_color, alpha=0.8)
        item_polygons[item.id] = poly
      
        shine = Poly3DCollection([[
            [item.position[0], item.position[1], item.position[2] + item.height],
            [item.position[0] + item.length, item.position[1], item.position[2] + item.height],
            [item.position[0] + item.length, item.position[1] + item.width, item.position[2] + item.height],
            [item.position[0], item.position[1] + item.width, item.position[2] + item.height]
        ]], alpha=0.2)
        shine.set_facecolor('white')
        ax.add_collection3d(shine)

        ax.text(item.position[0] + item.length / 2,
                item.position[1] + item.width / 2,
                item.position[2] + item.height / 2,
                str(item.id),
                color='black',
                fontsize=10,
                ha='center')

    ax.set_xlim([0, truck_length])
    ax.set_ylim([0, truck_width])
    ax.set_zlim([0, truck_height])
    ax.set_xlabel('Length')
    ax.set_ylabel('Width')
    ax.set_zlabel('Height')
    
    def on_click(event):
        if event.inaxes != ax:
            return
        
        
        x, y = event.xdata, event.ydata
        
        for item_id, poly in item_polygons.items():
          
            verts = poly.get_paths()[0].vertices
            
         
            if verts.shape[1] == 2:
               
                x2d, y2d = verts[:, 0], verts[:, 1]
            else:
               
                x2d, y2d, _ = proj3d.proj_transform(verts[:, 0], verts[:, 1], verts[:, 2], ax.get_proj())
            
            
            path = Path(list(zip(x2d, y2d)))
            
          
            if path.contains_point((x, y)):
                item = next(item for item in bin.items if item.id == item_id)
                print(f"Item ID: {item.id}")
                print(f"Weight: {item.weight}")
                print(f"Stackable: {item.stackable}")
                print(f"Fragile: {item.fragile}")
                print(f"Dimensions: {item.length}x{item.width}x{item.height}")
                print(f"Position: {item.position}")
                print("--------------------")
                break
            
    fig.canvas.mpl_connect('button_press_event', on_click)

    plt.tight_layout()
    plt.show()


bin = Bin(18, 4, 8)



items = [
    Item(id=1, length=3, width=2, height=2, weight=30, stackable=True, fragile=False),
    Item(id=2, length=2, width=2, height=3, weight=25, stackable=True, fragile=False),
    Item(id=3, length=4, width=3, height=2, weight=35, stackable=False, fragile=True),
    Item(id=4, length=2, width=2, height=2, weight=20, stackable=True, fragile=False),
    Item(id=5, length=3, width=3, height=1, weight=15, stackable=True, fragile=False),
    Item(id=6, length=1, width=1, height=4, weight=10, stackable=True, fragile=False),
    Item(id=7, length=2, width=1, height=3, weight=12, stackable=True, fragile=False),
    Item(id=8, length=3, width=2, height=1, weight=18, stackable=True, fragile=False),
    Item(id=9, length=2, width=2, height=2, weight=22, stackable=True, fragile=False),
    Item(id=10, length=1, width=1, height=3, weight=8, stackable=True, fragile=False),
    Item(id=11, length=2, width=3, height=2, weight=28, stackable=True, fragile=False),
    Item(id=12, length=3, width=1, height=2, weight=16, stackable=True, fragile=False),
    Item(id=13, length=2, width=2, height=1, weight=14, stackable=True, fragile=False),
    Item(id=14, length=1, width=3, height=2, weight=13, stackable=True, fragile=False),
    Item(id=15, length=2, width=1, height=4, weight=17, stackable=True, fragile=False),
    Item(id=16, length=4, width=3, height=2, weight=35, stackable=False, fragile=True),

# # Item 17 cannot bre placed as there isn't sufficient room for it, hence the code takes 
# # a lot of time to get to the solution which actually just dosen't contain 17!
    # Item(id=17, length=4, width=3, height=2, weight=35, stackable=False, fragile=True),

]

# TRIVIAL EXAMPLE!

# items = [
#     # Item(id=1, length=3, width=2, height=2, weight=30, stackable=True, fragile=False),
#     Item(id=2, length=2, width=2, height=3, weight=25, stackable=True, fragile=False),
#     Item(id=3, length=2, width=2, height=3, weight=25, stackable=True, fragile=False),
#     Item(id=4, length=2, width=2, height=3, weight=25, stackable=True, fragile=False),
#     Item(id=5, length=2, width=2, height=3, weight=25, stackable=True, fragile=False),
#     Item(id=6, length=2, width=2, height=3, weight=25, stackable=True, fragile=False),
#     Item(id=7, length=2, width=2, height=3, weight=25, stackable=True, fragile=False),
#     Item(id=8, length=2, width=2, height=3, weight=25, stackable=True, fragile=False),
#     Item(id=9, length=2, width=2, height=3, weight=25, stackable=True, fragile=False),
#     Item(id=10, length=2, width=2, height=3, weight=25, stackable=True, fragile=False),
#     Item(id=11, length=2, width=2, height=3, weight=25, stackable=True, fragile=False),
#     Item(id=12, length=2, width=2, height=3, weight=25, stackable=True, fragile=False),
# ]

place_items(bin, items)
def print_item_positions(bin):
    print("Item Positions:")
    for item in bin.items:
        if item.position is not None:
            print(f"Item ID: {item.id}")
            print(f"Position: {item.position}")
            print(f"Dimensions: {item.length}x{item.width}x{item.height}")
            print("--------------------")
        else:
            print(f"Item ID: {item.id} has not been placed.")
            print("--------------------")

print("Click on the items for their properties.")
print("Note: The position here is of the bottom-right-front corner.")
print_item_positions(bin)
visualize_packing(bin)