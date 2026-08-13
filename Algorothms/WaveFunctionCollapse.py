import numpy as np
from PIL import Image
from pathlib import Path
from wfc import wfc_control
from scipy.stats import skew, kurtosis
from scipy.ndimage import minimum_filter
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

DEFAULT_PARAMS = {
    "pattern_width": 2,
    "rotations": 1,
    "attempt_limit": 3,
    "output_periodic": False,
    "input_periodic": False,
    "loc_heuristic": "entropy",
    "choice_heuristic": "weighted",
    "backtracking": False,
}

def _compute_gradient_and_height(heightmap, x, y):
    xi = int(x)
    yi = int(y)
    u = x - xi                      
    v = y - yi                      

    # Four surrounding heights
    h_nw = heightmap[yi, xi]
    h_ne = heightmap[yi, xi + 1]
    h_sw = heightmap[yi + 1, xi]
    h_se = heightmap[yi + 1, xi + 1]

    # Gradient by bilinear interpolation
    grad_x = (h_ne - h_nw) * (1 - v) + (h_se - h_sw) * v
    grad_y = (h_sw - h_nw) * (1 - u) + (h_se - h_ne) * u

    # Interpolated height at (x, y)
    height = (h_nw * (1 - u) * (1 - v)
             + h_ne * u * (1 - v)
             + h_sw * (1 - u) * v
             + h_se * u * v)

    return grad_x, grad_y, height


def generate_wfc_heightmap(exemplar, output_shape, params=None, seed=0):

    if params is None:
        params = DEFAULT_PARAMS

    np.random.seed(seed)

    if isinstance(exemplar, (str, Path)):
        exemplar_arr = np.array(Image.open(str(exemplar)))
    else:
        exemplar_arr = np.asarray(exemplar)

    if exemplar_arr.ndim == 2:
        exemplar_arr = np.stack([exemplar_arr] * 3, axis=-1)

    output_size = (output_shape[1], output_shape[0])

    try:
        result = wfc_control.execute_wfc(
            image=exemplar_arr,
            pattern_width=params["pattern_width"],
            rotations=params["rotations"],
            output_size=output_size,
            attempt_limit=params["attempt_limit"],
            output_periodic=params["output_periodic"],
            input_periodic=params["input_periodic"],
            loc_heuristic=params["loc_heuristic"],
            choice_heuristic=params["choice_heuristic"],
            backtracking=params["backtracking"],
        )
    except Exception as e:
        raise RuntimeError(f"WFC failed to converge: {e}") from e

    if result.ndim == 3:
        result = result[:, :, 0]

    return result.astype(np.float64)

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

def save_heightmap(heightmap, resolution, seed, output_dir=Path("Outputs/WFC")):
    output_dir.mkdir(parents=True, exist_ok=True)

    normalised = ((heightmap - heightmap.min()) /
                  (heightmap.max() - heightmap.min() + 1e-9) * 255).astype(np.uint8)

    img = Image.fromarray(normalised)
    img.save(output_dir / f"WFC_res{resolution}_seed{seed}.png")
    np.save(output_dir / f"WFC_res{resolution}_seed{seed}.npy", heightmap)

def save_heightmap_colored(heightmap, resolution, seed, output_dir=Path("Outputs/WFC")):
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(heightmap, cmap="gist_earth", interpolation="nearest")
    ax.axis("off")
    fig.savefig(
        output_dir / f"WFC_colored_res{resolution}_seed{seed}.png",
        bbox_inches="tight", pad_inches=0, dpi=150,
    )
    plt.close(fig)

def save_heightmap_hillshaded(heightmap, resolution, seed, output_dir=Path("Outputs/WFC")):
    output_dir.mkdir(parents=True, exist_ok=True)
    ls = LightSource(azdeg=315, altdeg=45)
    colored = ls.shade(heightmap, cmap=plt.cm.gist_earth, vert_exag=1.5, blend_mode="soft")

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(colored)
    ax.axis("off")
    fig.savefig(
        output_dir / f"WFC_hillshaded_res{resolution}_seed{seed}.png",
        bbox_inches="tight", pad_inches=0, dpi=150,
    )
    plt.close(fig)

if __name__ == "__main__":
    exemplar_path = Path("Outputs/wfc_exemplar.png")
    if not exemplar_path.exists():
        print(f"Missing {exemplar_path}. Run the exemplar creation script first.")
    else:
        print(f"Loading exemplar from {exemplar_path}")
        print("Running WFC at 128x128 (small test)...")

        heightmap = generate_wfc_heightmap(
            exemplar=exemplar_path,
            output_shape=(128, 128),
            seed=0,
        )

        save_heightmap(heightmap, resolution=128, seed=0)
        print(f"Output shape: {heightmap.shape}")
        print(f"Unique values in output: {sorted(np.unique(heightmap))}")
        print("Saved to Outputs/WFC/")