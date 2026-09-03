# Procedural Terrain Generation: A Comparative Study

A controlled comparison of three procedural terrain generation paradigms — noise-based synthesis, physical simulation, and constraint satisfaction — evaluated under a unified quantitative framework.

MSc Dissertation, Trinity College Dublin, 2026.

---

## Overview

Procedural terrain generation research describes the trade-offs between its paradigms qualitatively but rarely measures them. This project implements one representative algorithm from each of three paradigms and evaluates them against a common set of measures covering generation cost, output quality, and designer controllability.

| Paradigm | Algorithm | Source |
|---|---|---|
| Noise-based | Perlin noise with fBm | `noise` library |
| Simulation-augmented | Particle-based hydraulic erosion | Implemented from Beyer (2015) |
| Constraint-based | Wave Function Collapse (overlapping) | Karth's Python port of Gumin's algorithm |

### Research questions

**RQ1 — Performance.** How do the paradigms compare in generation time, memory footprint, and scaling behaviour?

**RQ2 — Visual quality.** Do quantitative measures of terrain realism differ between paradigms, and does erosion close the gap between raw noise and structurally realistic terrain?

**RQ3 — Controllability.** What fraction of designer-authored specifications can each algorithm satisfy through rejection sampling, and at what cost?

---

## Key findings

- **Erosion costs 36–47× Perlin** at matched resolution; WFC a further two orders of magnitude beyond that.
- **Scaling exponents** (log time vs log pixels): Perlin 1.03, erosion 1.10, WFC 2.10. WFC becomes impractical beyond roughly 256².
- **Erosion increased undrained-depression density by 75–90%** at every resolution tested — the opposite of the drainage improvement the literature attributes to hydraulic simulation. A diagnostic sweep across a 32-fold range of droplet densities established that this is not attributable to insufficient coverage.
- **Controllability is poor across all paradigms** (0–13.3% specification satisfaction). Perlin and erosion perform identically, confirming that post-process simulation confers no additional spatial control.
- The evaluation framework detected a systematic degradation that visual inspection did not.

---

## Repository structure

```
.
├── Algorithms/
│   ├── Perlin_Noise_Based.py              # Perlin generator + save functions
│   ├── Particle_Based_Hydraulic_Erosion.py # Droplet erosion simulation
│   └── WaveFunctionCollapse.py             # Wrapper around Karth's WFC port
├── Analysis/
│   ├── renormalise_metrics.py              # Quality metrics on normalised heightmaps
│   └── erosion_diagnostic.py               # Droplet density sweep
├── Outputs/
│   ├── Perlin/                             # .npy and .png per resolution/seed
│   ├── Hydraulic/
│   ├── WFC/
│   └── *.csv                               # Experimental results
├── Main.py                                 # Experiment runners
├── RQ3_experiment.py                       # Controllability experiments
└── requirements.txt
```

All heightmaps are serialised as 64-bit float NumPy arrays (`.npy`) at full precision, with PNG exports for inspection. Filenames encode algorithm, resolution, and seed — for example `Perlin_res1024_seed3.npy` — so any output traces back to the condition that produced it.

---

## Installation

Requires Python 3.10 or later.

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

The WFC library installs from GitHub:

```bash
pip install git+https://github.com/ikarth/wfc_2019f.git
```

### Dependencies

`numpy`, `scipy`, `noise`, `Pillow`, `matplotlib`, `pandas`, `pyvista` (optional, for 3D inspection)

---

## Usage

### Generate heightmaps

```bash
python Main.py
```

Runs the Perlin and erosion experiments across all resolutions and seeds, writing heightmaps to `Outputs/` and timing data to CSV.

### Run WFC

WFC runs are executed as isolated subprocesses with a timeout, since successive runs within a single interpreter exhibit increasing generation times:

```bash
python WFC_experiment_subprocess.py
```

**Note:** WFC at 256² takes approximately 3.3 hours on a single core. 512² did not complete within the study's time budget.

### Compute quality metrics

```bash
python Analysis/renormalise_metrics.py
```

Loads saved `.npy` files, normalises each heightmap to [0,1], computes all four measure families, and writes `Outputs/rq2_metrics_normalised.csv`.

Normalisation is essential: the algorithms produce output over different native ranges (Perlin roughly [−0.5, 0.5], WFC [0, 192]), and measures derived from elevation differences are otherwise incomparable.

### Run controllability experiments

```bash
python RQ3_experiment.py
```

---

## Evaluation framework

Four measure families, all computed on normalised heightmaps:

| Measure | Computed from | What it captures |
|---|---|---|
| Roughness | Mean and std of local slope magnitude | Spatial variation in surface character |
| Height distribution | First four statistical moments | Statistical shape of the elevation field |
| Slope distribution | Slope angles binned across 0–90° | Physical plausibility of steepness |
| Drainage proxy | Local minima count and density | Hydrological coherence |

**Known limitation.** The drainage proxy assumes a continuous elevation field. On quantised output such as WFC's, every cell inside a constant-valued plateau ties with its neighbourhood minimum and is counted, so the measure registers plateau area rather than drainage structure. It is valid for comparing continuous-output paradigms with one another but not across the continuous–discrete boundary.

---

## Reproducibility

Seeds are assigned sequentially from zero and passed explicitly to each generation function. Algorithm parameters are module-level constants. Every measurement reported in the dissertation can be regenerated by running the relevant script unmodified.

### Parameters

**Perlin:** scale 100.0, 6 octaves, persistence 0.5, lacunarity 2.0

**Erosion:** 0.048 droplets per cell, inertia 0.05, capacity factor 4.0, erosion/deposition rate 0.3, evaporation 0.01, gravity 4.0, brush radius 3, droplet lifetime 30

**WFC:** pattern width 2, rotations 1, backtracking disabled, attempt limit 3, 32×32 exemplar with three elevation bands

---

## Attribution

The hydraulic erosion implementation follows the particle formulation described in Beyer's 2015 thesis, using parameter names and defaults from the widely-used public implementation by Sebastian Lague.

The Wave Function Collapse component wraps [Isaac Karth's Python port](https://github.com/ikarth/wfc_2019f) of [Maxim Gumin's algorithm](https://github.com/mxgmn/WaveFunctionCollapse), rather than reimplementing it. Constraint propagation has subtle failure modes in which an incorrect implementation produces locally plausible output that nonetheless violates adjacency rules; adapting a tested implementation avoids introducing such defects into a paradigm comparison.

Perlin noise generation uses the [`noise`](https://pypi.org/project/noise/) package, a Python binding to a C implementation of Perlin's original algorithm.

---

## References

Beyer, H. T. J. (2015). *Implementation of a Method for Hydraulic Erosion.* Bachelor's Thesis, Technische Universität München.

Gaillard, M., Aubert, J., Beneš, B., et al. (2016). Polynomial methods for procedural terrain generation. arXiv:1610.03525.

Gumin, M. (2016). Wave Function Collapse Algorithm. https://github.com/mxgmn/WaveFunctionCollapse

Karth, I. (2019). wfc_2019f: A Python port of the Wave Function Collapse algorithm. https://github.com/ikarth/wfc_2019f

Mei, X., Decaudin, P., & Hu, B.-G. (2007). Fast hydraulic erosion simulation and visualization on GPU. *Pacific Graphics.*

Møller, T. N., Billeskov, J. A., & Palamas, G. (2020). Expanding Wave Function Collapse with Growing Grids for Procedural Map Generation. *FDG '20.*

Perlin, K. (1985). An image synthesizer. *SIGGRAPH '85*, 287–296.

Togelius, J., Yannakakis, G. N., Stanley, K. O., & Browne, C. (2011). Search-based procedural content generation: A taxonomy and survey. *IEEE Transactions on Computational Intelligence and AI in Games*, 3(3), 172–186.

---

## Limitations

- Each paradigm is represented by a single algorithm; findings are claims about these algorithms as representatives rather than about the paradigms in full generality.
- All implementations are CPU-bound and written in Python. Absolute generation times characterise this implementation, not the achievable performance of the underlying algorithms. The relative comparison, conducted under a common execution model, is the defensible measurement.
- WFC was evaluated at two resolutions with a single seed each; its scaling exponent is fitted to two points.
- No perception study was conducted, so the correspondence between the quantitative measures and human judgement of terrain realism remains unestablished.

---

## Licence

*(Add your chosen licence here — MIT is a reasonable default for academic code.)*
