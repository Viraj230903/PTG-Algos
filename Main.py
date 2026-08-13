from Algorothms import Particle_Based_Hydraulic_Erosion as he
from Algorothms import Perlin_Noise_Based as pnb
from Algorothms import WaveFunctionCollapse as wfc
from pathlib import Path
import time
import tracemalloc
import csv
import numpy as np

output_dir = Path("Outputs/Perlin")
output_dir.mkdir(exist_ok=True)

def run_perlin_experiment(scale, octaves, persistence, lacunarity,
                          resolutions=(256, 512, 1024, 2048),
                          seeds_per_resolution=5):
    results = []

    for resolution in resolutions:
        for seed in range(seeds_per_resolution):
            tracemalloc.start()
            start = time.perf_counter()

            heightmap = pnb.generate_perlin_heightmap(
                (resolution, resolution), scale, octaves, persistence, lacunarity, seed
            )

            elapsed = time.perf_counter() - start
            _, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_mb = peak_bytes / (1024 * 1024)

            pnb.save_heightmap(heightmap, resolution, seed)
            pnb.save_heightmap_colored(heightmap, resolution,seed, output_dir)
            pnb.save_heightmap_hillshaded(heightmap, resolution, seed, output_dir)
            roughness_mean = pnb.compute_roughness(heightmap).get("roughness_mean")
            roughness_std = pnb.compute_roughness(heightmap).get("roughness_std")
            height_mean = pnb.compute_height_stats(heightmap).get("height_mean")
            height_std =  pnb.compute_height_stats(heightmap).get("height_std")
            height_skew = pnb.compute_height_stats(heightmap).get("height_skew")
            height_kurtosis = pnb.compute_height_stats(heightmap).get("height_kurtosis")
            local_minima_count = pnb.compute_drainage_proxy(heightmap).get("local_minima_count")
            results.append({
                "algorithm": "perlin",
                "resolution": resolution,
                "seed": seed,
                "time_s": round(elapsed, 4),
                "peak_memory_mb": round(peak_mb, 2),
                "roughness_mean": roughness_mean,
                "roughness_std": roughness_std, 
                "height_mean": height_mean,
                "height_std": height_std, 
                "height_skew": height_skew,
                "height_kurtosis": height_kurtosis,
                "local_minima_count": local_minima_count
            })

            print(f"Perlin res={resolution} seed={seed}: {elapsed:.3f}s, {peak_mb:.1f} MB, roughness_mean:{roughness_mean}, roughness_std:{roughness_std}, height_mean:{height_mean}, height_std:{height_std}, height_skew:{height_skew}, height_kurtosis:{height_kurtosis}, local_minima_count:{local_minima_count}")

    csv_path = output_dir / "perlin_timing.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["algorithm", "resolution", "seed", "time_s", "peak_memory_mb", "roughness_mean", "roughness_std", "height_mean", "height_std", "height_skew", "height_kurtosis", "local_minima_count"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults written to {csv_path}")
    return results

perlin_dir = Path("Outputs/Perlin")
output_dir = Path("Outputs/Hydraulic")
output_dir.mkdir(exist_ok=True)


def run_erosion_experiment(resolutions=(256, 512, 1024, 2048),
                           seeds_per_resolution=5,
                           n_droplets=50000):
    results = []

    for resolution in resolutions:
        # Scale droplet count with map area so erosion density stays roughly constant
        droplets_this_resolution = int(n_droplets * (resolution / 1024) ** 2)

        for seed in range(seeds_per_resolution):
            perlin_path = perlin_dir / f"Perlin_res{resolution}_seed{seed}.npy"
            if not perlin_path.exists():
                print(f"Missing {perlin_path} — skipping")
                continue

            perlin_heightmap = np.load(perlin_path)

            tracemalloc.start()
            start = time.perf_counter()

            eroded = he.erode_heightmap(
                perlin_heightmap,
                n_droplets=droplets_this_resolution,
                seed=seed
            )

            elapsed = time.perf_counter() - start
            _, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_mb = peak_bytes / (1024 * 1024)

            he.save_heightmap(eroded, resolution, seed)
            he.save_heightmap_colored(eroded, resolution, seed)
            he.save_heightmap_hillshaded(eroded, resolution, seed)
            roughness_mean = he.compute_roughness(eroded).get("roughness_mean")
            roughness_std = he.compute_roughness(eroded).get("roughness_std")
            height_mean = he.compute_height_stats(eroded).get("height_mean")
            height_std = he.compute_height_stats(eroded).get("height_std")
            height_skew = he.compute_height_stats(eroded).get("height_skew")
            height_kurtosis = he.compute_height_stats(eroded).get("height_kurtosis")
            local_minima_count = he.compute_drainage_proxy(eroded).get("local_minima_count")
            results.append({
                "algorithm": "erosion",
                "resolution": resolution,
                "seed": seed,
                "n_droplets": droplets_this_resolution,
                "time_s": round(elapsed, 4),
                "peak_memory_mb": round(peak_mb, 2),
                "roughness_mean": roughness_mean,
                "roughness_std": roughness_std,
                "height_mean": height_mean,
                "height_std": height_std,
                "height_skew": height_skew,
                "height_kurtosis": height_kurtosis,
                "local_minima_count": local_minima_count
            })

            print(f"Erosion res={resolution} seed={seed} droplets={droplets_this_resolution}: "
                  f"{elapsed:.2f}s, {peak_mb:.1f} MB, roughness_mean:{roughness_mean}, roughness_std:{roughness_std}, height_mean:{height_mean}, height_std:{height_std}, height_skew:{height_skew}, height_kurtosis:{height_kurtosis}, local_minima_count:{local_minima_count}")

    csv_path = output_dir / "erosion_timing.csv"
    with open(csv_path, "w", newline="") as f:
        f, fieldnames=["algorithm", "resolution", "seed", "n_droplets", "time_s", "peak_memory_mb", "roughness_mean", "roughness_std", "height_mean", "height_std", "height_skew", "height_kurtosis", "local_minima_count"]

        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults written to {csv_path}")
    return results

# WFC Experiments
from Algorothms import WaveFunctionCollapse as wfc

wfc_output_dir = Path("Outputs/WFC")
wfc_output_dir.mkdir(parents=True, exist_ok=True)


def run_wfc_experiment(
    exemplar_path=Path("Outputs/wfc_exemplar.png"),
    resolutions=(128, 256, 512, 1024),
    seeds_per_resolution=5,
):
    results = []

    for resolution in resolutions:
        for seed in range(seeds_per_resolution):
            print(f"WFC res={resolution} seed={seed}: starting...")

            tracemalloc.start()
            start = time.perf_counter()

            try:
                heightmap = wfc.generate_wfc_heightmap(
                    exemplar=exemplar_path,
                    output_shape=(resolution, resolution),
                    seed=seed,
                )

                elapsed = time.perf_counter() - start
                _, peak_bytes = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                peak_mb = peak_bytes / (1024 * 1024)

                wfc.save_heightmap(heightmap, resolution, seed)
                wfc.save_heightmap_colored(heightmap, resolution, seed)
                wfc.save_heightmap_hillshaded(heightmap, resolution, seed)

                roughness_mean = wfc.compute_roughness(heightmap).get("roughness_mean")
                roughness_std = wfc.compute_roughness(heightmap).get("roughness_std")
                height_mean = wfc.compute_height_stats(heightmap).get("height_mean")
                height_std = wfc.compute_height_stats(heightmap).get("height_std")
                height_skew = wfc.compute_height_stats(heightmap).get("height_skew")
                height_kurtosis = wfc.compute_height_stats(heightmap).get("height_kurtosis")
                local_minima_count = wfc.compute_drainage_proxy(heightmap).get("local_minima_count")

                results.append({
                    "algorithm": "wfc",
                    "resolution": resolution,
                    "seed": seed,
                    "time_s": round(elapsed, 4),
                    "peak_memory_mb": round(peak_mb, 2),
                    "status": "success",
                    "roughness_mean": roughness_mean,
                    "roughness_std": roughness_std,
                    "height_mean": height_mean,
                    "height_std": height_std,
                    "height_skew": height_skew,
                    "height_kurtosis": height_kurtosis,
                    "local_minima_count": local_minima_count,
                })

                print(f"  → success: {elapsed:.2f}s, {peak_mb:.1f} MB, "
                      f"minima={local_minima_count}")

            except RuntimeError as e:
                elapsed = time.perf_counter() - start
                tracemalloc.stop()

                results.append({
                    "algorithm": "wfc",
                    "resolution": resolution,
                    "seed": seed,
                    "time_s": round(elapsed, 4),
                    "peak_memory_mb": None,
                    "status": "failed",
                    "roughness_mean": None,
                    "roughness_std": None,
                    "height_mean": None,
                    "height_std": None,
                    "height_skew": None,
                    "height_kurtosis": None,
                    "local_minima_count": None,
                })

                print(f"  → failed after {elapsed:.2f}s: {e}")

    csv_path = wfc_output_dir / "wfc_timing.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "algorithm", "resolution", "seed", "time_s", "peak_memory_mb", "status",
                "roughness_mean", "roughness_std", "height_mean", "height_std",
                "height_skew", "height_kurtosis", "local_minima_count",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    n_success = sum(1 for r in results if r["status"] == "success")
    n_failed = sum(1 for r in results if r["status"] == "failed")
    print(f"\nResults written to {csv_path}")
    print(f"Summary: {n_success} succeeded, {n_failed} failed out of {len(results)}")

    return results

if __name__ == "__main__":
    run_wfc_experiment(
        resolutions=(128, 256, 512, 1024, 2048),
        seeds_per_resolution=1,
    )

# if __name__ == "__main__":
#     run_erosion_experiment()

# if __name__ == "__main__":
#     run_perlin_experiment(
#         scale=100.0,
#         octaves=6,
#         persistence=0.5,  
#         lacunarity=2.0,
#     )