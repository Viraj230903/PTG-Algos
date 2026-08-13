"""
Diagnostic: does erosion's local-minima increase disappear at higher droplet density?

Takes a single Perlin heightmap at 512x512 and applies erosion at four droplet
densities, recording normalised metrics after each. If the local-minima increase
is caused by insufficient droplet coverage, higher densities should reverse it.
"""
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

# Baseline for 512 in the main experiment was 12,500 droplets.
# Test 1x, 4x, 16x, 32x that density.
DROPLET_COUNTS = [12500, 50000, 200000, 400000]

# Also vary lifetime at the highest density to test whether droplets are
# terminating before they can carve connected channels.
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

    # Baseline: un-eroded Perlin
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

    # Density sweep at default lifetime
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

    # Lifetime variant — requires erode_heightmap to accept a params dict.
    # If your signature differs, comment this block out.
    for n, lifetime in LIFETIME_VARIANTS:
        if lifetime == 30:
            continue  # already covered above
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