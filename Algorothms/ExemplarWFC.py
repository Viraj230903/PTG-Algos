import numpy as np
from PIL import Image
from pathlib import Path

Path("Outputs").mkdir(exist_ok=True)

exemplar = np.zeros((32, 32), dtype=np.uint8)
for i in range(32):
    for j in range(32):
        d = np.sqrt((i - 16)**2 + (j - 16)**2)
        if d < 8:
            exemplar[i, j] = 128   # peak
        elif d < 16:
            exemplar[i, j] = 64    # slope
        else:
            exemplar[i, j] = 0     # base

Image.fromarray(exemplar).save("Outputs/wfc_exemplar_simple.png")
np.save("Outputs/wfc_exemplar_simple.npy", exemplar)
print(f"Simple exemplar saved. Unique values: {sorted(np.unique(exemplar))}")