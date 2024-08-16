import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.path import Path
from mpl_toolkits.mplot3d import proj3d
import matplotlib.colors as mcolors

def plot_cuboid(ax, x, y, z, dx, dy, dz, edge_color='black', face_color='gray', alpha=0.5):
    """
    Plots a 3D cuboid on the given axis.

    Parameters:
    ax : matplotlib.axes._subplots.Axes3DSubplot
        The 3D axis to plot on.
    x, y, z : float
        The starting coordinates of the cuboid.
    dx, dy, dz : float
        The dimensions of the cuboid along the x, y, and z axes.
    edge_color : str, optional
        The color of the cuboid edges. Default is 'black'.
    face_color : str, optional
        The color of the cuboid faces. Default is 'gray'.
    alpha : float, optional
        The transparency of the cuboid faces. Default is 0.5.

    Returns:
    poly : matplotlib.art3d.Poly3DCollection
        The polygon collection representing the cuboid.
    """
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
    """
    Visualizes the packing of items in a 3D bin or truck using matplotlib.

    Parameters:
    bin : Bin
        The bin or truck to visualize, containing items to be packed.
    """
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111, projection='3d')

    truck_length, truck_width, truck_height = bin.length, bin.width, bin.height
    
    plot_cuboid(ax, 0, 0, 0, truck_length, truck_width, truck_height, edge_color='black', face_color='#808080', alpha=0.0)
    
    floor = Poly3DCollection([[
        [0, 0, 0],
        [truck_length, 0, 0],
        [truck_length, truck_width, 0],
        [0, truck_width, 0]
    ]], alpha=0.2)
    floor.set_facecolor('gray')
    ax.add_collection3d(floor)
# 40% paper - 20% mid 20% quiz 
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FED766', '#2AB7CA', '#F0B67F']
    item_polygons = {}
    for item in bin.items:
        base_color = colors[int(item.id) % len(colors)]
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
        """
        Handles click events on the plot to display information about the clicked item.

        Parameters:
        event : matplotlib.backend_bases.MouseEvent
            The mouse event triggered by clicking on the plot.
        """
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