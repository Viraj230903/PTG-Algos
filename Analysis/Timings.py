import pandas as pd
import numpy as np
from pathlib import Path
from scipy.ndimage import minimum_filter

def count_local_minima(heightmap):
    local_min = (heightmap == minimum_filter(heightmap, size=3))
    return int(local_min.sum())

perlin_counts = []
erosion_counts = []

for seed in range(5):
    perlin_path = Path("Outputs/Perlin") / f"Perlin_res1024_seed{seed}.npy"
    erosion_path = Path("Outputs/Hydraulic") / f"Erosion_res1024_seed{seed}.npy"
    
    if perlin_path.exists():
        perlin_counts.append(count_local_minima(np.load(perlin_path)))
    if erosion_path.exists():
        erosion_counts.append(count_local_minima(np.load(erosion_path)))

perlin_mean = np.mean(perlin_counts)
erosion_mean = np.mean(erosion_counts)
reduction = (perlin_mean - erosion_mean) / perlin_mean * 100

print(f"Perlin mean minima: {perlin_mean:.0f}")
print(f"Erosion mean minima: {erosion_mean:.0f}")
print(f"Reduction: {reduction:.1f}%")

perlin = pd.read_csv("Outputs/Perlin/perlin_timing.csv")
erosion = pd.read_csv("Outputs/Hydraulic/erosion_timing.csv")

perlin_1024 = perlin[perlin["resolution"] == 1024]["time_s"].mean()
erosion_1024 = erosion[erosion["resolution"] == 1024]["time_s"].mean()

multiplier = erosion_1024 / perlin_1024
print(f"Perlin mean time at 1024: {perlin_1024:.2f}s")
print(f"Erosion mean time at 1024: {erosion_1024:.2f}s")
print(f"Erosion cost multiplier: {multiplier:.1f}x")