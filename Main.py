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
            results.append({
                "algorithm": "perlin",
                "resolution": resolution,
                "seed": seed,
                "time_s": round(elapsed, 4),
                "peak_memory_mb": round(peak_mb, 2),
            })

            print(f"Perlin res={resolution} seed={seed}: {elapsed:.3f}s, {peak_mb:.1f} MB")

    csv_path = output_dir / "perlin_timing.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["algorithm", "resolution", "seed", "time_s", "peak_memory_mb"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults written to {csv_path}")
    return results

if __name__ == "__main__":
    run_perlin_experiment(
        scale=100.0,
        octaves=6,
        persistence=0.5,
        lacunarity=2.0,
    )