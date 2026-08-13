"""
RQ3: Designer controllability via rejection sampling.

For each algorithm, generate N heightmaps at 128^2 with distinct seeds and test
each against two fixed designer specifications. Records the boolean outcome, the
underlying continuous statistic, and the RQ2 quality metrics, so success rates
can be re-derived at other thresholds and quality can be cross-tabbed against
spec satisfaction without re-running the experiment.

Unequal N by design: WFC's generation cost at 128^2 (~643 s/run) makes N=30
infeasible. Success rates are reported with Wilson score intervals so the wider
uncertainty on WFC is visible rather than hidden.

Results append to Outputs/RQ3/rq3_runs.csv after every run. Re-running the
script skips (algorithm, seed) pairs already present, so an interrupted WFC
sweep can be resumed.
"""

import csv
import math
import random
import time
from pathlib import Path

import numpy as np

from Algorothms import Perlin_Noise_Based as pnb
from Algorothms import Particle_Based_Hydraulic_Erosion as pbhe
from Algorothms import WaveFunctionCollapse as wfc


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RES = 128

N_RUNS = {
    "perlin": 30,
    "erosion": 30,
    "wfc": 10,
}

# !! SET THIS TO THE SAME SCALE YOU USED FOR RQ1/RQ2 !!
# If RQ1 varied scale with resolution, mirror that rule here instead of using a
# constant, otherwise the RQ3 maps are not comparable to your other results.
PERLIN_SCALE = 100.0
PERLIN_OCTAVES = 6
PERLIN_PERSISTENCE = 0.5
PERLIN_LACUNARITY = 2.0

# Droplet count kept below the ~0.2 droplets/cell stability ceiling identified in
# the erosion diagnostic.
EROSION_DENSITY = 0.15
EROSION_DROPLETS = int(EROSION_DENSITY * RES * RES)

# WFC exemplar. Swap to wfc_exemplar.npy if the simple one is not what your
# RQ1/RQ2 runs used.
EXEMPLAR_PATH = Path("Outputs/wfc_exemplar_simple.npy")

# Spec thresholds
SPEC1_THRESHOLD = 0.8   # centre elevation must reach >= 80% of range
SPEC2_THRESHOLD = 0.3   # top-left quadrant mean must fall below 30% of range

OUTPUT_DIR = Path("Outputs/RQ3")
RUNS_CSV = OUTPUT_DIR / "rq3_runs.csv"
SUMMARY_CSV = OUTPUT_DIR / "rq3_summary.csv"
SAVE_MAPS = True

# Abort an algorithm's loop after this many consecutive failures, so the script
# never grinds through 30 seeds repeating one signature error.
MAX_CONSECUTIVE_FAILURES = 2

FIELDNAMES = [
    "algorithm",
    "seed",
    "resolution",
    "gen_time_s",
    "spec1_centre_value",
    "spec1_pass",
    "spec2_quadrant_mean",
    "spec2_pass",
    "height_mean",
    "height_std",
    "roughness",
    "drainage_proxy",
]


# ---------------------------------------------------------------------------
# Generation adapters
#
# Each returns (raw_heightmap, elapsed_seconds). Timing covers generation only.
# ---------------------------------------------------------------------------
def generate_perlin(seed, res):
    t0 = time.perf_counter()
    hm = pnb.generate_perlin_heightmap(
        shape=(res, res),
        scale=PERLIN_SCALE,
        octaves=PERLIN_OCTAVES,
        persistence=PERLIN_PERSISTENCE,
        lacunarity=PERLIN_LACUNARITY,
        seed=seed,
    )
    return np.asarray(hm, dtype=np.float64), time.perf_counter() - t0


def generate_erosion(seed, res):
    """Erosion is applied to a Perlin base with the same seed, so the erosion and
    Perlin rows at a given seed are directly comparable: any difference in spec
    satisfaction is attributable to the erosion pass alone."""
    t0 = time.perf_counter()
    base = pnb.generate_perlin_heightmap(
        shape=(res, res),
        scale=PERLIN_SCALE,
        octaves=PERLIN_OCTAVES,
        persistence=PERLIN_PERSISTENCE,
        lacunarity=PERLIN_LACUNARITY,
        seed=seed,
    )
    hm = pbhe.erode_heightmap(
        np.asarray(base, dtype=np.float64),
        n_droplets=EROSION_DROPLETS,
        seed=seed,
    )
    return np.asarray(hm, dtype=np.float64), time.perf_counter() - t0


_EXEMPLAR_CACHE = None


def _load_exemplar():
    global _EXEMPLAR_CACHE
    if _EXEMPLAR_CACHE is None:
        if not EXEMPLAR_PATH.exists():
            raise FileNotFoundError(
                f"WFC exemplar not found at {EXEMPLAR_PATH.resolve()}"
            )
        _EXEMPLAR_CACHE = np.load(EXEMPLAR_PATH)
        print(
            f"[info] exemplar loaded: shape={_EXEMPLAR_CACHE.shape} "
            f"dtype={_EXEMPLAR_CACHE.dtype} "
            f"range=[{_EXEMPLAR_CACHE.min()}, {_EXEMPLAR_CACHE.max()}]"
        )
    return _EXEMPLAR_CACHE


def generate_wfc(seed, res):
    exemplar = _load_exemplar()
    # Seed the global RNGs as well, in case the WFC port ignores its seed argument.
    random.seed(seed)
    np.random.seed(seed)
    t0 = time.perf_counter()
    hm = wfc.generate_wfc_heightmap(
        exemplar=exemplar,
        output_shape=(res, res),
        seed=seed,
    )
    return np.asarray(hm, dtype=np.float64), time.perf_counter() - t0


GENERATORS = {
    "perlin": generate_perlin,
    "erosion": generate_erosion,
    "wfc": generate_wfc,
}

# The metric functions are duplicated across all three modules; use one
# consistently so the numbers are guaranteed comparable.
METRICS_MODULE = pnb


# ---------------------------------------------------------------------------
# Normalisation, specifications, metrics
# ---------------------------------------------------------------------------
def normalise(hm):
    """Min-max normalise to [0, 1]. Matches the RQ2 metric pipeline so thresholds
    mean the same thing across algorithms with different raw ranges."""
    lo, hi = float(np.nanmin(hm)), float(np.nanmax(hm))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi - lo == 0.0:
        return None
    return (hm - lo) / (hi - lo)


def spec1_centre_elevation(hm_norm):
    """'Put a mountain here.' Normalised elevation at the centre pixel."""
    r, c = hm_norm.shape[0] // 2, hm_norm.shape[1] // 2
    return float(hm_norm[r, c])


def spec2_quadrant_mean(hm_norm):
    """'Keep this area low ground.' Mean of the top-left quadrant."""
    r, c = hm_norm.shape[0] // 2, hm_norm.shape[1] // 2
    return float(np.mean(hm_norm[:r, :c]))


def safe_scalar(fn, hm):
    """Call a metric function and coerce the result to float. Returns nan on
    failure so one bad metric never costs an expensive WFC run."""
    try:
        val = fn(hm)
    except Exception as exc:
        print(f"[warn] metric {getattr(fn, '__name__', fn)} failed: {exc}")
        return float("nan")
    if isinstance(val, dict):
        val = list(val.values())[0]
    if isinstance(val, (tuple, list, np.ndarray)):
        val = np.ravel(np.asarray(val, dtype=object))[0]
    try:
        return float(val)
    except (TypeError, ValueError):
        return float("nan")


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
def wilson_interval(successes, n, z=1.96):
    """Wilson score interval for a binomial proportion. Behaves sensibly at 0 and
    1 successes, unlike the normal approximation -- which matters because several
    cells here are expected to be 0/10 or 30/30."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = successes / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


# ---------------------------------------------------------------------------
# CSV persistence with resume support
# ---------------------------------------------------------------------------
def load_completed():
    if not RUNS_CSV.exists():
        return set()
    done = set()
    with open(RUNS_CSV, newline="") as f:
        for row in csv.DictReader(f):
            done.add((row["algorithm"], int(row["seed"])))
    return done


def append_row(row):
    write_header = not RUNS_CSV.exists()
    with open(RUNS_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------
def run_sweep():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    completed = load_completed()

    # Cheapest first, so a crash during WFC still leaves complete Perlin and
    # erosion datasets on disk.
    for algo in ("perlin", "erosion", "wfc"):
        n = N_RUNS[algo]
        generate = GENERATORS[algo]
        consecutive_failures = 0

        for seed in range(n):
            if (algo, seed) in completed:
                print(f"[skip] {algo} seed={seed} already recorded")
                continue

            print(f"[run ] {algo} seed={seed} ...", flush=True)
            try:
                hm, elapsed = generate(seed, RES)
            except Exception as exc:
                consecutive_failures += 1
                print(f"[FAIL] {algo} seed={seed}: {type(exc).__name__}: {exc}")
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    print(
                        f"[ABORT] {algo}: {consecutive_failures} consecutive "
                        "failures -- this is a code problem, not a seed problem. "
                        "Fix the adapter and re-run; completed seeds are kept."
                    )
                    break
                continue

            hm_norm = normalise(hm)
            if hm_norm is None:
                consecutive_failures += 1
                print(f"[FAIL] {algo} seed={seed}: degenerate or non-finite output")
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    print(f"[ABORT] {algo}: repeated degenerate output.")
                    break
                continue

            consecutive_failures = 0

            centre = spec1_centre_elevation(hm_norm)
            quad = spec2_quadrant_mean(hm_norm)

            row = {
                "algorithm": algo,
                "seed": seed,
                "resolution": RES,
                "gen_time_s": round(elapsed, 4),
                "spec1_centre_value": round(centre, 6),
                "spec1_pass": int(centre >= SPEC1_THRESHOLD),
                "spec2_quadrant_mean": round(quad, 6),
                "spec2_pass": int(quad < SPEC2_THRESHOLD),
                "height_mean": round(float(np.mean(hm_norm)), 6),
                "height_std": round(float(np.std(hm_norm)), 6),
                "roughness": round(
                    safe_scalar(METRICS_MODULE.compute_roughness, hm_norm), 6
                ),
                "drainage_proxy": round(
                    safe_scalar(METRICS_MODULE.compute_drainage_proxy, hm_norm), 6
                ),
            }
            append_row(row)

            if SAVE_MAPS:
                np.save(OUTPUT_DIR / f"rq3_{algo}_res{RES}_seed{seed}.npy", hm_norm)

            print(
                f"[done] {algo} seed={seed} t={elapsed:.2f}s "
                f"centre={centre:.3f} quad={quad:.3f}",
                flush=True,
            )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
def summarise():
    if not RUNS_CSV.exists():
        print("No runs recorded yet.")
        return

    with open(RUNS_CSV, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("No runs recorded yet.")
        return

    out_rows = []
    for algo in ("perlin", "erosion", "wfc"):
        subset = [r for r in rows if r["algorithm"] == algo]
        if not subset:
            continue
        n = len(subset)

        for pass_key, value_key, label in (
            ("spec1_pass", "spec1_centre_value", "spec1_point_elevation"),
            ("spec2_pass", "spec2_quadrant_mean", "spec2_region_mean"),
        ):
            successes = sum(int(r[pass_key]) for r in subset)
            lo, hi = wilson_interval(successes, n)
            values = [float(r[value_key]) for r in subset]

            # Quality cross-tab: roughness of satisfying vs non-satisfying maps.
            passing = [float(r["roughness"]) for r in subset if int(r[pass_key]) == 1]
            failing = [float(r["roughness"]) for r in subset if int(r[pass_key]) == 0]

            out_rows.append(
                {
                    "algorithm": algo,
                    "spec": label,
                    "n": n,
                    "successes": successes,
                    "success_rate": round(successes / n, 4),
                    "wilson_lo": round(lo, 4),
                    "wilson_hi": round(hi, 4),
                    "statistic_mean": round(float(np.mean(values)), 4),
                    "statistic_std": round(float(np.std(values)), 4),
                    "statistic_min": round(float(np.min(values)), 4),
                    "statistic_max": round(float(np.max(values)), 4),
                    "roughness_passing": (
                        round(float(np.nanmean(passing)), 4) if passing else ""
                    ),
                    "roughness_failing": (
                        round(float(np.nanmean(failing)), 4) if failing else ""
                    ),
                    "mean_gen_time_s": round(
                        float(np.mean([float(r["gen_time_s"]) for r in subset])), 3
                    ),
                }
            )

    with open(SUMMARY_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"\nSummary written to {SUMMARY_CSV}\n")
    for r in out_rows:
        print(
            f"{r['algorithm']:<8} {r['spec']:<22} "
            f"{r['successes']}/{r['n']} = {r['success_rate']:.2f} "
            f"[{r['wilson_lo']:.2f}, {r['wilson_hi']:.2f}]  "
            f"stat mean={r['statistic_mean']:.3f} "
            f"range=[{r['statistic_min']:.3f}, {r['statistic_max']:.3f}]"
        )


if __name__ == "__main__":
    run_sweep()
    summarise()