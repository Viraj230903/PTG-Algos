import numpy as np
import pyvista as pv
from pathlib import Path

# Load a heightmap you already generated
heightmap = np.load(Path("Outputs/Perlin") / "Perlin_res1024_seed4.npy")

heightmap = heightmap[::2, ::2]

rows, cols = heightmap.shape
x = np.arange(cols)
y = np.arange(rows)
x, y = np.meshgrid(x, y)
z = heightmap * 30

grid = pv.StructuredGrid(x, y, z)

plotter = pv.Plotter()
plotter.add_mesh(grid, scalars=z.ravel(), cmap="terrain", show_scalar_bar=False)
plotter.enable_terrain_style()
plotter.show()