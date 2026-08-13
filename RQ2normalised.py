import numpy as np
from pathlib import Path
from scipy.stats import skew, kurtosis
from scipy.ndimage import minimum_filter
import csv

def normalise(heightmap):
    h_min, h_max = heightmap.min(), heightmap.max()
    return (heightmap - h_min) / (h_max - h_min + 1e-12)

def compute_roughness(h):
    gy, gx = np.gradient(h)
    slope = np.sqrt(gx**2 + gy**2)
    return {
        "roughness_mean": float(slope.mean()),
        "roughness_std": float(slope.std()),
    }


def compute_height_stats(h):
    flat = h.flatten()
    return {
        "height_mean": float(flat.mean()),
        "height_std": float(flat.std()),
        "height_skew": float(skew(flat)),
        "height_kurtosis": float(kurtosis(flat)),
    }


def compute_slope_distribution(h):
    gy, gx = np.gradient(h)
    slope_deg = np.degrees(np.arctan(np.sqrt(gx**2 + gy**2)))
    hist, edges = np.histogram(slope_deg, bins=18, range=(0, 90))
    mode_idx = int(hist.argmax())
    mode_centre = float((edges[mode_idx] + edges[mode_idx + 1]) / 2)
    return {
        "slope_mean_deg": float(slope_deg.mean()),
        "slope_std_deg": float(slope_deg.std()),
        "slope_mode_deg": mode_centre,
    }


def compute_drainage_proxy(h):
    local_min = (h == minimum_filter(h, size=3))
    return {
        "local_minima_count": int(local_min.sum()),
        "local_minima_density": float(local_min.sum() / h.size),
    }


def compute_all_metrics(h):
    result = {}
    result.update(compute_roughness(h))
    result.update(compute_height_stats(h))
    result.update(compute_slope_distribution(h))
    result.update(compute_drainage_proxy(h))
    return result

SOURCES = [
    {
        "algorithm": "perlin",
        "dir": Path("Outputs/Perlin"),
        "pattern": "Perlin_res{res}_seed{seed}.npy",
        "resolutions": [256, 512, 1024, 2048],
        "seeds": [0, 1, 2, 3, 4],
    },
    {
        "algorithm": "erosion",
        "dir": Path("Outputs/Hydraulic"),
        "pattern": "Erosion_res{res}_seed{seed}.npy",
        "resolutions": [256, 512, 1024, 2048],
        "seeds": [0, 1, 2, 3, 4],
    },
    {
        "algorithm": "wfc",
        "dir": Path("Outputs/WFC"),
        "pattern": "WFC_res{res}_seed{seed}.npy",
        "resolutions": [128, 256],
        "seeds": [0],
    },
]


def main():
    results = []
    missing = []

    for source in SOURCES:
        algo = source["algorithm"]
        for res in source["resolutions"]:
            for seed in source["seeds"]:
                filename = source["pattern"].format(res=res, seed=seed)
                path = source["dir"] / filename

                if not path.exists():
                    missing.append(str(path))
                    continue

                heightmap = np.load(path)
                h_norm = normalise(heightmap)

                metrics = compute_all_metrics(h_norm)
                row = {
                    "algorithm": algo,
                    "resolution": res,
                    "seed": seed,
                    "raw_min": float(heightmap.min()),
                    "raw_max": float(heightmap.max()),
                    **metrics,
                }
                results.append(row)
                print(f"{algo:8s} res={res:5d} seed={seed}: "
                      f"rough_mean={metrics['roughness_mean']:.5f}  "
                      f"rough_std={metrics['roughness_std']:.5f}  "
                      f"skew={metrics['height_skew']:+.4f}  "
                      f"minima={metrics['local_minima_count']:6d} "
                      f"({metrics['local_minima_density']*100:.2f}%)")

    if not results:
        print("\nNo files found. Check the SOURCES paths and filename patterns.")
        return

    out_dir = Path("Outputs")
    out_dir.mkdir(exist_ok=True)
    csv_path = out_dir / "rq2_metrics_normalised.csv"

    fieldnames = list(results[0].keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nWrote {len(results)} rows to {csv_path}")

    if missing:
        print(f"\n{len(missing)} files not found:")
        for m in missing[:10]:
            print(f"  {m}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")


if __name__ == "__main__":
    main()