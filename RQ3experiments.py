"""
RQ3 experiment: measure controllability of each algorithm via rejection sampling
against fixed designer specifications.

For each (algorithm, spec) pair, generate N heightmaps with different seeds,
check whether each satisfies the spec, and record success rate plus quality
metrics of successful outputs.
"""
from Algorothms import Perlin_Noise_Based as pnb
from Algorothms import Particle_Based_Hydraulic_Erosion as pbhe
from Algorothms import WaveFunctionCollapse as wfc
from pathlib import Path
import numpy as np
import csv
import time


output_dir = Path("Outputs/RQ3")
output_dir.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Specification checks — each returns True if the heightmap satisfies the spec
# ---------------------------------------------------------------------------
def check_spec_point_elevation(heightmap, threshold_frac=0.6):
    """
    Spec 1: The centre of the map must reach at least `threshold_frac` of max height.
    Represents a 'put a mountain here' designer request.
    """
    h_range = heightmap.max() - heightmap.min()
    if h_range == 0:
        return False
    normalised_centre = (heightmap[heightmap.shape[0] // 2, heightmap.shape[1] // 2]
                         - heightmap.min()) / h_range
    return normalised_centre >= threshold_frac


def check_spec_region_mean(heightmap, threshold_frac=0.45):
    """
    Spec 2: The mean of the top-left quadrant must be below `threshold_frac` of max height.
    Represents a 'keep this area low' designer request.
    """
    h_range = heightmap.max() - heightmap.min()
    if h_range == 0:
        return False
    h_norm = (heightmap - heightmap.min()) / h_range
    quadrant = h_norm[:heightmap.shape[0] // 2, :heightmap.shape[1] // 2]
    return quadrant.mean() < threshold_frac


# ---------------------------------------------------------------------------
# Algorithm generation wrappers (return a heightmap given a seed)
# All use fixed 256x256 resolution for RQ3
# ---------------------------------------------------------------------------
RESOLUTION = 256


def gen_perlin(seed):
    return pnb.generate_perlin_heightmap(
        (RESOLUTION, RESOLUTION),
        scale=100.0,
        octaves=6,
        persistence=0.5,
        lacunarity=2.0,
        seed=seed,
    )


def gen_erosion(seed):
    perlin_hmap = gen_perlin(seed)
    return pbhe.erode_heightmap(perlin_hmap, n_droplets=5000, seed=seed)


def gen_wfc(seed):
    return wfc.generate_wfc_heightmap(
        exemplar=Path("Outputs/wfc_exemplar.png"),
        output_shape=(RESOLUTION, RESOLUTION),
        seed=seed,
    )


# ---------------------------------------------------------------------------
# Experiment runner
# ---------------------------------------------------------------------------
def run_rq3_experiment(n_attempts=50):
    """
    Run all algorithm-spec combinations. Save row-per-attempt CSV and a summary.
    """
    algorithms = [
        ("perlin", gen_perlin),
        ("erosion", gen_erosion),
        ("wfc", gen_wfc),
    ]
    specs = [
        ("point_elevation", check_spec_point_elevation),
        ("region_mean", check_spec_region_mean),
    ]

    all_results = []

    for algo_name, algo_gen in algorithms:
        for spec_name, spec_check in specs:
            print(f"\n--- {algo_name} × {spec_name} ---")

            for seed in range(n_attempts):
                start = time.perf_counter()
                try:
                    heightmap = algo_gen(seed)
                    elapsed = time.perf_counter() - start
                    satisfied = bool(spec_check(heightmap))
                    generation_status = "success"
                except Exception as e:
                    elapsed = time.perf_counter() - start
                    satisfied = False
                    heightmap = None
                    generation_status = f"failed: {type(e).__name__}"
                    print(f"  seed={seed}: {generation_status}")

                # Quality metrics for successful attempts only
                if satisfied and heightmap is not None:
                    roughness_std = pnb.compute_roughness(heightmap).get("roughness_std")
                    height_skew = pnb.compute_height_stats(heightmap).get("height_skew")
                    local_minima_count = pnb.compute_drainage_proxy(heightmap).get("local_minima_count")
                else:
                    roughness_std = None
                    height_skew = None
                    local_minima_count = None

                all_results.append({
                    "algorithm": algo_name,
                    "spec": spec_name,
                    "seed": seed,
                    "satisfied": satisfied,
                    "generation_status": generation_status,
                    "generation_time_s": round(elapsed, 3),
                    "roughness_std": roughness_std,
                    "height_skew": height_skew,
                    "local_minima_count": local_minima_count,
                })

                if seed % 10 == 0 or seed == n_attempts - 1:
                    print(f"  seed={seed}: satisfied={satisfied}, time={elapsed:.2f}s")

    # Write full row-per-attempt CSV
    detail_csv = output_dir / "rq3_details.csv"
    with open(detail_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_results[0].keys()))
        writer.writeheader()
        writer.writerows(all_results)
    print(f"\nDetail CSV written to {detail_csv}")

    # Compute and write summary CSV
    summary = compute_summary(all_results)
    summary_csv = output_dir / "rq3_summary.csv"
    with open(summary_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)
    print(f"Summary CSV written to {summary_csv}")

    # Print summary to terminal
    print("\n=== RQ3 Summary ===")
    for row in summary:
        print(f"  {row['algorithm']:8s} × {row['spec']:16s}: "
              f"success={row['success_rate_pct']:.1f}%  "
              f"(N={row['n_attempts']}, {row['n_successes']} satisfied)")

    return all_results, summary


def compute_summary(results):
    """Aggregate detail rows into a per-(algorithm, spec) summary."""
    grouped = {}
    for row in results:
        key = (row["algorithm"], row["spec"])
        grouped.setdefault(key, []).append(row)

    summary = []
    for (algo, spec), rows in grouped.items():
        successes = [r for r in rows if r["satisfied"]]

        def mean_of(field):
            vals = [r[field] for r in successes if r[field] is not None]
            return round(sum(vals) / len(vals), 4) if vals else None

        summary.append({
            "algorithm": algo,
            "spec": spec,
            "n_attempts": len(rows),
            "n_successes": len(successes),
            "success_rate_pct": round(100 * len(successes) / len(rows), 1),
            "mean_success_roughness_std": mean_of("roughness_std"),
            "mean_success_height_skew": mean_of("height_skew"),
            "mean_success_local_minima_count": mean_of("local_minima_count"),
        })

    return summary


if __name__ == "__main__":
    run_rq3_experiment(n_attempts=50)