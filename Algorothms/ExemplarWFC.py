import numpy as np
from PIL import Image
from pathlib import Path

Path("Outputs").mkdir(exist_ok=True)

# Build a *periodic* (toroidally tileable) exemplar so WFC can legitimately
# extrapolate it across arbitrarily large output canvases with
# input_periodic/output_periodic=True. A single centered, non-repeating
# radial bump (the previous exemplar) has no valid way to keep going once
# WFC runs off its edges, which is why convergence failed at res>=256.
size = 32
i, j = np.meshgrid(np.arange(size), np.arange(size), indexing="ij")

# Sums of cosines with integer frequencies over `size` are exactly periodic
# on a size x size torus, giving a rolling hills pattern that tiles cleanly.
raw = (
    np.cos(2 * np.pi * 2 * i / size) * np.cos(2 * np.pi * 2 * j / size)
    + 0.5 * np.cos(2 * np.pi * 3 * i / size + 1.0) * np.cos(2 * np.pi * 3 * j / size + 1.0)
)
raw = (raw - raw.min()) / (raw.max() - raw.min())  # normalise to [0, 1]

# Quantise into the same four height bands as before (peak/upper/lower/base)
exemplar = np.zeros((size, size), dtype=np.uint8)
exemplar[raw >= 0.75] = 192   # peak
exemplar[(raw >= 0.5) & (raw < 0.75)] = 128   # upper slope
exemplar[(raw >= 0.25) & (raw < 0.5)] = 64    # lower slope
exemplar[raw < 0.25] = 0      # base

Image.fromarray(exemplar).save("Outputs/wfc_exemplar.png")
np.save("Outputs/wfc_exemplar.npy", exemplar)
print(f"Exemplar saved. Shape: {exemplar.shape}, unique values: {sorted(np.unique(exemplar))}")
