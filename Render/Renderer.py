import numpy as np
import pyvista as pv
from pathlib import Path


def view_heightmap(npy_path, vert_exag=10, downsample=1, cmap="gist_earth"):
    heightmap = np.load(npy_path)

    if downsample > 1:
        heightmap = heightmap[::downsample, ::downsample]

    norm = (heightmap - heightmap.min()) / (heightmap.max() - heightmap.min() + 1e-9)

    rows, cols = norm.shape
    x = np.arange(cols)
    y = np.arange(rows)
    x, y = np.meshgrid(x, y)
    z = norm * vert_exag

    grid = pv.StructuredGrid(x, y, z)

    plotter = pv.Plotter()
    plotter.add_mesh(
        grid,
        scalars=z.ravel(),
        cmap=cmap,
        clim=[np.percentile(z, 1), np.percentile(z, 99)],
    )
    plotter.enable_terrain_style()
    plotter.show()


if __name__ == "__main__":
    # Adjust path to whichever file you want to view
    view_heightmap(Path("Outputs/WFC") / "WFC_res128_seed0.npy")