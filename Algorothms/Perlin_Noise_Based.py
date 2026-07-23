import noise
import numpy as np
import time
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis
from scipy.ndimage import minimum_filter
from matplotlib.colors import LightSource


def _retry_on_os_error(func, *args, retries=5, delay=0.5, **kwargs):
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except OSError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)

scale = 400.0
octaves = 4
persistence = 0.45
lacunarity = 2.0

output_dir = Path("Outputs/Perlin")
output_dir.mkdir(exist_ok=True)

def generate_perlin_heightmap(shape, scale, octaves, persistence, lacunarity, seed):
    world = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            world[i][j] = noise.pnoise2(
                i / scale, j / scale,
                octaves=octaves, persistence=persistence, lacunarity=lacunarity,
                repeatx=shape[0], repeaty=shape[1], base=seed
            )
    return world

def compute_roughness(heightmap):
    gy, gx = np.gradient(heightmap)
    slope = np.sqrt(gx**2 + gy**2)
    return {
        "roughness_mean": float(slope.mean()),
        "roughness_std": float(slope.std()),
    }

def compute_height_stats(heightmap):
    flat = heightmap.flatten()
    return {
        "height_mean": float(flat.mean()),
        "height_std": float(flat.std()), 
        "height_skew": float(skew(flat)),
        "height_kurtosis": float(kurtosis(flat)),
    }

def compute_drainage_proxy(heightmap):
    local_min = (heightmap == minimum_filter(heightmap, size=3))
    return {"local_minima_count": int(local_min.sum())}

def save_heightmap(heightmap, resolution, seed):
    normalised = ((heightmap - heightmap.min()) / (heightmap.max() - heightmap.min()) * 255).astype(np.uint8)
    img = Image.fromarray(normalised)
    _retry_on_os_error(img.save, output_dir / f"Perlin_res{resolution}_seed{seed}.png")
    _retry_on_os_error(np.save, output_dir / f"Perlin_res{resolution}_seed{seed}.npy", heightmap)

def save_heightmap_colored(heightmap, resolution, seed, output_dir):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(heightmap, cmap='terrain', interpolation='bilinear')
    ax.axis('off')
    _retry_on_os_error(
        fig.savefig,
        output_dir / f"Perlin_colored_res{resolution}_seed{seed}.png",
        bbox_inches='tight', pad_inches=0, dpi=150
    )
    plt.close(fig)

def save_heightmap_hillshaded(heightmap, resolution, seed, output_dir):
    ls = LightSource(azdeg=315, altdeg=45)
    colored = ls.shade(heightmap, cmap=plt.cm.terrain, vert_exag=1.5, blend_mode='soft')

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(colored)
    ax.axis('off')
    _retry_on_os_error(
        fig.savefig,
        output_dir / f"Perlin_hillshaded_res{resolution}_seed{seed}.png",
        bbox_inches='tight', pad_inches=0, dpi=150
    )
    plt.close(fig)