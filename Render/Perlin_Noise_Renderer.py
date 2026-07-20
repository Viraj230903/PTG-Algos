import numpy as np
import pyvista as pv
from pathlib import Path

# Load a heightmap you already generated
heightmap = np.load(Path("Outputs/Perlin") / "Perlin_res1024_seed4.npy")

# Optionally downsample so it renders fast (1024x1024 = 1M triangles, heavy)
heightmap = heightmap[::2, ::2]  # halve resolution -> 512x512, 250k triangles

# Build a structured grid from the heightmap
rows, cols = heightmap.shape
x = np.arange(cols)
y = np.arange(rows)
x, y = np.meshgrid(x, y)
z = heightmap * 30  # exaggerate vertical scale so it feels like terrain

# Wrap in a pyvista StructuredGrid
grid = pv.StructuredGrid(x, y, z)

# Show with terrain colouring
plotter = pv.Plotter()
plotter.add_mesh(grid, scalars=z.ravel(), cmap="terrain", show_scalar_bar=False)
plotter.enable_terrain_style()  # mouse-controlled fly camera
plotter.show()