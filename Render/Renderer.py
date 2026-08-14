import numpy as np
import pyvista as pv
from pathlib import Path

heightmap = np.load(Path("Outputs/WFC") / "WFC_res128_seed0.npy")
heightmap = heightmap[::2, ::2]

lo, hi = heightmap.min(), heightmap.max()
heightmap = (heightmap - lo) / (hi - lo)

rows, cols = heightmap.shape
x = np.arange(cols)
y = np.arange(rows)
x, y = np.meshgrid(x, y)
z = heightmap * (0.15 * max(rows, cols)) 

grid = pv.StructuredGrid(x, y, z)

plotter = pv.Plotter()
plotter.add_mesh(
    grid,
    scalars=z.ravel(order="F"), 
    cmap="terrain",
    clim=[np.percentile(z, 1), np.percentile(z, 99)] 
)
plotter.camera_position = 'iso'   
plotter.enable_terrain_style()
plotter.show()