import numpy as np
import pyvista as pv
from pathlib import Path

heightmap = np.load(Path("Outputs/Perlin") / "Perlin_res256_seed1.npy")
heightmap = heightmap[::2, ::2]

rows, cols = heightmap.shape
x = np.arange(cols)
y = np.arange(rows)
x, y = np.meshgrid(x, y)
z = heightmap * 30

grid = pv.StructuredGrid(x, y, z)

plotter = pv.Plotter()
plotter.add_mesh(
    grid,
    scalars=z.ravel(order="F"),  # StructuredGrid stores points in Fortran order
    cmap="terrain",
    clim=[np.percentile(z, 1), np.percentile(z, 99)]  # use both percentiles, not z.min()
)
plotter.camera_position = 'iso'   
plotter.enable_terrain_style()
plotter.show()
