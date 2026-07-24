"""Compare Perlin noise vs hydraulic erosion timing/memory across resolutions."""
from pathlib import Path
import csv
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PERLIN_CSV = ROOT / "Outputs" / "Perlin" / "perlin_timing.csv"
EROSION_CSV = ROOT / "Outputs" / "Hydraulic" / "erosion_timing.csv"
OUT_DIR = ROOT / "Outputs" / "Analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COLOR_PERLIN = "#2a78d6"   # categorical slot 1 (blue)
COLOR_EROSION = "#eb6834"  # categorical slot 2 (orange)
INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"


def load(csv_path):
    by_res = defaultdict(lambda: defaultdict(list))
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            res = int(row["resolution"])
            by_res[res]["time_s"].append(float(row["time_s"]))
            by_res[res]["peak_memory_mb"].append(float(row["peak_memory_mb"]))
    resolutions = sorted(by_res)
    time_mean = np.array([np.mean(by_res[r]["time_s"]) for r in resolutions])
    time_std = np.array([np.std(by_res[r]["time_s"]) for r in resolutions])
    mem_mean = np.array([np.mean(by_res[r]["peak_memory_mb"]) for r in resolutions])
    mem_std = np.array([np.std(by_res[r]["peak_memory_mb"]) for r in resolutions])
    return np.array(resolutions), time_mean, time_std, mem_mean, mem_std


def style_axes(ax):
    ax.set_facecolor("#fcfcfb")
    ax.grid(True, which="both", color=GRID, linewidth=0.8, zorder=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(BASELINE)
    ax.tick_params(colors=SECONDARY_INK, labelsize=9)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)


def plot_metric(ax, resolutions, perlin_vals, perlin_std, erosion_vals, erosion_std, ylabel, log_y=True):
    ax.errorbar(resolutions, perlin_vals, yerr=perlin_std, marker="o", markersize=6,
                linewidth=2, color=COLOR_PERLIN, label="Perlin noise", capsize=3, zorder=3)
    ax.errorbar(resolutions, erosion_vals, yerr=erosion_std, marker="o", markersize=6,
                linewidth=2, color=COLOR_EROSION, label="Hydraulic erosion", capsize=3, zorder=3)
    if log_y:
        ax.set_yscale("log")
    ax.set_xscale("log", base=2)
    ax.set_xticks(resolutions)
    ax.set_xticklabels([str(r) for r in resolutions])
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.set_xlabel("Resolution (px)")
    ax.set_ylabel(ylabel)
    style_axes(ax)


def main():
    p_res, p_time, p_time_std, p_mem, p_mem_std = load(PERLIN_CSV)
    e_res, e_time, e_time_std, e_mem, e_mem_std = load(EROSION_CSV)
    assert np.array_equal(p_res, e_res), "Resolution sets differ between CSVs"

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), facecolor="#fcfcfb")
    fig.suptitle("Perlin noise vs. hydraulic erosion — scaling with resolution",
                 fontsize=13, color=INK, fontweight="bold")

    plot_metric(axes[0], p_res, p_time, p_time_std, e_time, e_time_std,
                "Runtime (s, log scale)")
    axes[0].set_title("Execution time", fontsize=10, color=SECONDARY_INK)

    plot_metric(axes[1], p_res, p_mem, p_mem_std, e_mem, e_mem_std,
                "Peak memory (MB, log scale)")
    axes[1].set_title("Peak memory usage", fontsize=10, color=SECONDARY_INK)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False,
               bbox_to_anchor=(0.5, -0.02), fontsize=9, labelcolor=INK)

    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    out_path = OUT_DIR / "timing_memory_comparison.png"
    fig.savefig(out_path, dpi=200, facecolor=fig.get_facecolor())
    print(f"Saved {out_path}")

    # Single time-only chart, larger, for standalone use
    fig2, ax2 = plt.subplots(figsize=(6.5, 5), facecolor="#fcfcfb")
    plot_metric(ax2, p_res, p_time, p_time_std, e_time, e_time_std,
                "Runtime (s, log scale)")
    ax2.set_title("Execution time vs. resolution", fontsize=11, color=INK)
    ax2.legend(frameon=False, fontsize=9, labelcolor=INK, loc="upper left")
    fig2.tight_layout()
    out_path2 = OUT_DIR / "timing_comparison.png"
    fig2.savefig(out_path2, dpi=200, facecolor=fig2.get_facecolor())
    print(f"Saved {out_path2}")

    plt.close("all")


if __name__ == "__main__":
    main()
