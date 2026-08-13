import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from scipy.stats import skew, kurtosis
from scipy.ndimage import minimum_filter
import time
import csv

from Algorothms import Particle_Based_Hydraulic_Erosion as pbhe


RESOLUTION = 512
SEED = 0
PERLIN_PATH = Path("Outputs/Perlin") / f"Perlin_res{RESOLUTION}_seed{SEED}.npy"

DROPLET_COUNTS = [12500, 50000, 200000, 400000]

LIFETIME_VARIANTS = [(200000, 30), (200000, 60)]


def normalise(h):
    return (h - h.min()) / (h.max() - h.min() + 1e-12)


def compute_metrics(h_raw):
    h = normalise(h_raw)
    gy, gx = np.gradient(h)
    slope = np.sqrt(gx**2 + gy**2)
    flat = h.flatten()
    local_min = (h == minimum_filter(h, size=3))
    return {
        "roughness_mean": float(slope.mean()),
        "roughness_std": float(slope.std()),
        "height_skew": float(skew(flat)),
        "height_kurtosis": float(kurtosis(flat)),
        "slope_mean_deg": float(np.degrees(np.arctan(slope)).mean()),
        "local_minima_count": int(local_min.sum()),
        "local_minima_density": float(local_min.sum() / h.size),
    }


def main():
    if not PERLIN_PATH.exists():
        print(f"Missing {PERLIN_PATH}")
        return

    base = np.load(PERLIN_PATH)
    print(f"Loaded base heightmap: {base.shape}\n")

    results = []

    m = compute_metrics(base)
    results.append({
        "condition": "perlin_baseline",
        "n_droplets": 0,
        "lifetime": 0,
        "time_s": 0.0,
        **m,
    })
    print(f"{'perlin_baseline':24s} minima={m['local_minima_count']:6d} "
          f"({m['local_minima_density']*100:5.2f}%)  "
          f"rough_std={m['roughness_std']:.5f}  skew={m['height_skew']:+.4f}")

    for n in DROPLET_COUNTS:
        start = time.perf_counter()
        eroded = pbhe.erode_heightmap(base, n_droplets=n, seed=SEED)
        elapsed = time.perf_counter() - start

        m = compute_metrics(eroded)
        results.append({
            "condition": f"erosion_{n}_lifetime30",
            "n_droplets": n,
            "lifetime": 30,
            "time_s": round(elapsed, 2),
            **m,
        })
        np.save(Path("Outputs") / f"diag_erosion_{n}_lt30.npy", eroded)

        delta = (m["local_minima_density"] / results[0]["local_minima_density"] - 1) * 100
        print(f"{'n=' + str(n) + ' lt=30':24s} minima={m['local_minima_count']:6d} "
              f"({m['local_minima_density']*100:5.2f}%)  "
              f"rough_std={m['roughness_std']:.5f}  skew={m['height_skew']:+.4f}  "
              f"[{delta:+.1f}% vs base, {elapsed:.0f}s]")

    for n, lifetime in LIFETIME_VARIANTS:
        if lifetime == 30:
            continue  
        params = dict(pbhe.DEFAULT_PARAMS)
        params["max_lifetime"] = lifetime

        start = time.perf_counter()
        eroded = pbhe.erode_heightmap(base, n_droplets=n, params=params, seed=SEED)
        elapsed = time.perf_counter() - start

        m = compute_metrics(eroded)
        results.append({
            "condition": f"erosion_{n}_lifetime{lifetime}",
            "n_droplets": n,
            "lifetime": lifetime,
            "time_s": round(elapsed, 2),
            **m,
        })
        np.save(Path("Outputs") / f"diag_erosion_{n}_lt{lifetime}.npy", eroded)

        delta = (m["local_minima_density"] / results[0]["local_minima_density"] - 1) * 100
        print(f"{'n=' + str(n) + ' lt=' + str(lifetime):24s} minima={m['local_minima_count']:6d} "
              f"({m['local_minima_density']*100:5.2f}%)  "
              f"rough_std={m['roughness_std']:.5f}  skew={m['height_skew']:+.4f}  "
              f"[{delta:+.1f}% vs base, {elapsed:.0f}s]")

    csv_path = Path("Outputs") / "erosion_diagnostic.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nWritten to {csv_path}")


if __name__ == "__main__":
    main()