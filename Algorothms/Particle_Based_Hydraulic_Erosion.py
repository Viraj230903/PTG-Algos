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


DEFAULT_PARAMS = {
    "inertia": 0.05,                    
    "sediment_capacity_factor": 4.0,    
    "min_sediment_capacity": 0.01,      
    "erosion_speed": 0.3,               
    "deposit_speed": 0.3,               
    "evaporation_rate": 0.01,           
    "gravity": 4.0,                     
    "erosion_radius": 3,                
    "max_lifetime": 30,                 
    "initial_speed": 1.0,
    "initial_water": 1.0,
}

def _build_brush(radius):
    offsets = []
    weight_sum = 0.0

    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            distance = np.sqrt(dx**2 + dy**2)
            if distance <= radius:
                weight = max(0, radius - distance)
                offsets.append((dx, dy, weight))
                weight_sum += weight

    return [(dx, dy, w / weight_sum) for (dx, dy, w) in offsets]

def _compute_gradient_and_height(heightmap, x, y):
    xi = int(x)
    yi = int(y)
    u = x - xi                     
    v = y - yi                      

    h_nw = heightmap[yi, xi]
    h_ne = heightmap[yi, xi + 1]
    h_sw = heightmap[yi + 1, xi]
    h_se = heightmap[yi + 1, xi + 1]

    grad_x = (h_ne - h_nw) * (1 - v) + (h_se - h_sw) * v
    grad_y = (h_sw - h_nw) * (1 - u) + (h_se - h_ne) * u

    height = (h_nw * (1 - u) * (1 - v)
             + h_ne * u * (1 - v)
             + h_sw * (1 - u) * v
             + h_se * u * v)

    return grad_x, grad_y, height

def _simulate_droplet(heightmap, brush, params, rng):

    h, w = heightmap.shape

    x = rng.uniform(1, w - 2)
    y = rng.uniform(1, h - 2)
    dir_x = 0.0
    dir_y = 0.0
    speed = params["initial_speed"]
    water = params["initial_water"]
    sediment = 0.0

    for _ in range(params["max_lifetime"]):
        node_x = int(x)
        node_y = int(y)

        grad_x, grad_y, height_current = _compute_gradient_and_height(heightmap, x, y)

        dir_x = dir_x * params["inertia"] - grad_x * (1 - params["inertia"])
        dir_y = dir_y * params["inertia"] - grad_y * (1 - params["inertia"])

        length = np.sqrt(dir_x**2 + dir_y**2)
        if length != 0:
            dir_x /= length
            dir_y /= length

        x += dir_x
        y += dir_y

        if (dir_x == 0 and dir_y == 0) or x < 1 or x >= w - 2 or y < 1 or y >= h - 2:
            break

        _, _, height_new = _compute_gradient_and_height(heightmap, x, y)
        delta_h = height_new - height_current

        capacity = max(
            -delta_h * speed * water * params["sediment_capacity_factor"],
            params["min_sediment_capacity"]
        )

        if sediment > capacity or delta_h > 0:
            if delta_h > 0:
                amount = min(delta_h, sediment)
            else:
                amount = (sediment - capacity) * params["deposit_speed"]

            sediment -= amount
            heightmap[node_y, node_x] += amount

        else:
            amount = min((capacity - sediment) * params["erosion_speed"], -delta_h)
            for dx, dy, weight in brush:
                px, py = node_x + dx, node_y + dy
                if 0 <= px < w and 0 <= py < h:
                    heightmap[py, px] -= amount * weight
            sediment += amount

        speed = np.sqrt(max(0.0, speed**2 + delta_h * params["gravity"]))
        water *= (1 - params["evaporation_rate"])

def erode_heightmap(heightmap, n_droplets=50000, params=None, seed=0):
    if params is None:
        params = DEFAULT_PARAMS

    heightmap = heightmap.copy().astype(np.float64)

    brush = _build_brush(params["erosion_radius"])
    rng = np.random.default_rng(seed)

    for _ in range(n_droplets):
        _simulate_droplet(heightmap, brush, params, rng)

    return heightmap

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

def save_heightmap(heightmap, resolution, seed, output_dir=Path("Outputs/Hydraulic")):
    output_dir.mkdir(exist_ok=True)

    normalised = ((heightmap - heightmap.min()) /
                  (heightmap.max() - heightmap.min()) * 255).astype(np.uint8)

    img = Image.fromarray(normalised)
    _retry_on_os_error(img.save, output_dir / f"Erosion_res{resolution}_seed{seed}.png")
    _retry_on_os_error(np.save, output_dir / f"Erosion_res{resolution}_seed{seed}.npy", heightmap)


def save_heightmap_colored(heightmap, resolution, seed, output_dir=Path("Outputs/Hydraulic")):
    output_dir.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(heightmap, cmap='terrain', interpolation='bilinear')
    ax.axis('off')
    fig.savefig(
        output_dir / f"Erosion_colored_res{resolution}_seed{seed}.png",
        bbox_inches='tight', pad_inches=0, dpi=150
    )
    plt.close(fig)


def save_heightmap_hillshaded(heightmap, resolution, seed, output_dir=Path("Outputs/Hydraulic")):
    output_dir.mkdir(exist_ok=True)
    ls = LightSource(azdeg=315, altdeg=45)
    colored = ls.shade(heightmap, cmap=plt.cm.terrain, vert_exag=1.5, blend_mode='soft')

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(colored)
    ax.axis('off')
    fig.savefig(
        output_dir / f"Erosion_hillshaded_res{resolution}_seed{seed}.png",
        bbox_inches='tight', pad_inches=0, dpi=150
    )
    plt.close(fig)
    
if __name__ == "__main__":
    input_path = Path("Outputs/Perlin") / "Perlin_res1024_seed0.npy"
    if not input_path.exists():
        print(f"Missing {input_path}. Generate a Perlin heightmap first.")
    else:
        perlin_heightmap = np.load(input_path)
        print(f"Loaded {input_path}, shape={perlin_heightmap.shape}")

        eroded = erode_heightmap(perlin_heightmap, n_droplets=10000, seed=0)
        save_heightmap(eroded, 1024, 0)
        print("Saved Erosion_res1024_seed0.png and .npy")