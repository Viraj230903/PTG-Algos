import numpy as np
from pathlib import Path
from scipy.ndimage import minimum_filter

def count_local_minima(heightmap):
    local_min = (heightmap == minimum_filter(heightmap, size=3))
    return int(local_min.sum())

# Adjust these paths if your files are elsewhere
perlin_counts = []
erosion_counts = []
for seed in range(5):
    p = Path("Outputs/Perlin") / f"Perlin_res1024_seed{seed}.npy"
    e = Path("Outputs/Hydraulic") / f"Erosion_res1024_seed{seed}.npy"
    if p.exists(): perlin_counts.append(count_local_minima(np.load(p)))
    if e.exists(): erosion_counts.append(count_local_minima(np.load(e)))

perlin_mean = np.mean(perlin_counts)
erosion_mean = np.mean(erosion_counts)
reduction = (perlin_mean - erosion_mean) / perlin_mean * 100
print(f"Perlin mean: {perlin_mean:.0f}, Erosion mean: {erosion_mean:.0f}")
print(f"Reduction: {reduction:.1f}%")