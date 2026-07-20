from Algorothms import Perlin_Noise_Based as pnb
from pathlib import Path
import time
import tracemalloc
import csv

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

if __name__ == "__main__":
    run_perlin_experiment(
        scale=400.0,
        octaves=4,
        persistence=0.45,
        lacunarity=2.0,
    )