<<<<<<< HEAD
The comparative study of procedural terrain generation.Comparative study of procedural terrain generation.

A quantitative comparison of three procedural terrain generation paradigms: noise based synthesis, physical simulation and constraint satisfaction, conducted under a common quantitative measure.
=======
# Procedural Terrain Generation: A Comparative Study

A controlled comparison of three procedural terrain generation paradigms — noise-based synthesis, physical simulation, and constraint satisfaction — evaluated under a unified quantitative framework.
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

MSc Dissertation, Trinity College Dublin, 2026.

---

## Overview

<<<<<<< HEAD
Qualitative descriptions of the trade-offs among procedural terrain generation paradigms are found in procedure terrain generation research, but few studies quantify the trade-offs. This project is based on the implementation of a single implementation of each of the three paradigms and a comparison of them with respect to a number of common metrics spanning generation costs, output quality, and designer controllability.

| Paradigm | Algorithm | Source |
|---|---|---|
Lebesgue-Stieltjes integral | Minimal/neural networks | Fuzzy logic |
Sim-aug | PBHE | implemented from Beyer (2015) |
Prospective | Wave Function Collapse (overlapping) | Karth's Python port of Gumin's algorithm |

### Research questions

**RQ1 — Performance.** What are the differences between the paradigms in terms of generation time, memory consumption and scalability?

**RQ2 — Visual quality.** Are quantitative techniques for terrain realism paradigm-dependent and does erosion help bridge the gap between noise and structurally realistic terrain?

**RQ3 — Controllability.** How many fraction of the designer's specs each algorithm can meet using rejection sampling and how many fraction can't?How many fraction of the designer's specs can each algorithm meet using rejection sampling and how many fraction can't?
=======
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
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

---

## Key findings

<<<<<<< HEAD
Erosion is 36-47x Perlin at same resolution, WFC two orders of magnitude further away.
- **Scaling exponents** (log time vs log pixels): Perlin 1.03, erosion 1.10, WFC 2.10. WFC is impractical beyond about 256².
The literature reports that hydraulic simulation actually increased the density of undrained depressions by 75-90% for each of the resolutions investigated. This was not due to the lack of coverage because a diagnostic sweep was carried out over a range of 32-fold droplet density.
The controllability for all paradigms is below average (0–13.3% specification satisfaction). Perlin and erosion do the same thing, which means that they give the same spatial control after post processing.
The evaluation framework identified a system degradation that the visual inspection did not.
=======
- **Erosion costs 36–47× Perlin** at matched resolution; WFC a further two orders of magnitude beyond that.
- **Scaling exponents** (log time vs log pixels): Perlin 1.03, erosion 1.10, WFC 2.10. WFC becomes impractical beyond roughly 256².
- **Erosion increased undrained-depression density by 75–90%** at every resolution tested — the opposite of the drainage improvement the literature attributes to hydraulic simulation. A diagnostic sweep across a 32-fold range of droplet densities established that this is not attributable to insufficient coverage.
- **Controllability is poor across all paradigms** (0–13.3% specification satisfaction). Perlin and erosion perform identically, confirming that post-process simulation confers no additional spatial control.
- The evaluation framework detected a systematic degradation that visual inspection did not.
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

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

<<<<<<< HEAD
All heightmaps are serialised as 64-bit float NumPy arrays (`.npy`) for full precision, and PNG images (`.png`) for inspection. The filenames contain algorithm, resolution, and seed (e.g. Perlin_res1024_seed3.npy) and the output is traceable back to the condition.
=======
All heightmaps are serialised as 64-bit float NumPy arrays (`.npy`) at full precision, with PNG exports for inspection. Filenames encode algorithm, resolution, and seed — for example `Perlin_res1024_seed3.npy` — so any output traces back to the condition that produced it.
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

---

## Installation

<<<<<<< HEAD
Requires Python 3.10+
=======
Requires Python 3.10 or later.
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

<<<<<<< HEAD
The WFC library will be installed from GitHub:
=======
The WFC library installs from GitHub:
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

```bash
pip install git+https://github.com/ikarth/wfc_2019f.git
```

### Dependencies

<<<<<<< HEAD
`numpy`, `scipy`, `noise`, `Pillow`, `matplotlib`, `pandas`, `pyvista` (optional, if used to inspect 3D objects)
=======
`numpy`, `scipy`, `noise`, `Pillow`, `matplotlib`, `pandas`, `pyvista` (optional, for 3D inspection)
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

---

## Usage

### Generate heightmaps

```bash
python Main.py
```

<<<<<<< HEAD
Runs the Perlin and Erosion experiments for all resolution and seed values, saves heightmaps into Outputs/ and timing data to CSV file.

### Run WFC

The WFC runs are performed as individual subprocesses with a timeout; successive runs of a single interpreter have growing generation times:
=======
Runs the Perlin and erosion experiments across all resolutions and seeds, writing heightmaps to `Outputs/` and timing data to CSV.

### Run WFC

WFC runs are executed as isolated subprocesses with a timeout, since successive runs within a single interpreter exhibit increasing generation times:
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

```bash
python WFC_experiment_subprocess.py
```

<<<<<<< HEAD
Note: WFC at 256² requires about 3.3 hours of runtime on a single core. The study was time-budgeted for 512², which was not completed.
=======
**Note:** WFC at 256² takes approximately 3.3 hours on a single core. 512² did not complete within the study's time budget.
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

### Compute quality metrics

```bash
python Analysis/renormalise_metrics.py
```

<<<<<<< HEAD
Loads in file, normalises each heightmap to [0,1] range, calculates all four measure families and saves a file named Outputs/rq2_metrics_normalised.csv.

The algorithms output results on various native ranges (Perlin in the range of [−0.5, 0.5] and WFC in the range of [0, 192] and results based on the elevation difference are otherwise uncomparable.
=======
Loads saved `.npy` files, normalises each heightmap to [0,1], computes all four measure families, and writes `Outputs/rq2_metrics_normalised.csv`.

Normalisation is essential: the algorithms produce output over different native ranges (Perlin roughly [−0.5, 0.5], WFC [0, 192]), and measures derived from elevation differences are otherwise incomparable.
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

### Run controllability experiments

```bash
python RQ3_experiment.py
```

---

## Evaluation framework

<<<<<<< HEAD
There are four measure families that are all computed on normalised heightmaps:

Measure | Computed from | What it captures |
|---|---|---|
Roughness | Mean and std of local slope magnitude | Spatial variation in surface character |
Fit to the distribution of heights | Compute first four moments of the height distribution | Compute the statistical shape of the elevation field |
Physical plausibility of steepness | Slope distribution | Slope angles binned across 0-90° |
Drainage proxy | Local minima count and density | Hydrological coherence |

**Known limitation.** The drainage proxy assumes an elevation field that is continuous. In the case of quantised output, like the WFC's, all cells within a plateau of a constant output value are "linked" to the minimum output value of their neighbourhood, and are thus counted; the measure is not measuring drainage structure but the area of the plateau. It can be used to compare any two continuous-output paradigms, but not between continuous and discrete.
=======
Four measure families, all computed on normalised heightmaps:

| Measure | Computed from | What it captures |
|---|---|---|
| Roughness | Mean and std of local slope magnitude | Spatial variation in surface character |
| Height distribution | First four statistical moments | Statistical shape of the elevation field |
| Slope distribution | Slope angles binned across 0–90° | Physical plausibility of steepness |
| Drainage proxy | Local minima count and density | Hydrological coherence |

**Known limitation.** The drainage proxy assumes a continuous elevation field. On quantised output such as WFC's, every cell inside a constant-valued plateau ties with its neighbourhood minimum and is counted, so the measure registers plateau area rather than drainage structure. It is valid for comparing continuous-output paradigms with one another but not across the continuous–discrete boundary.
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

---

## Reproducibility

<<<<<<< HEAD
Seeds are given sequentially starting from 0, and they are passed directly to the generation functions. Constants that are defined at the module level are called algorithm parameters. All measurements given in the dissertation can be reproduced by executing the respective script with no changes.
=======
Seeds are assigned sequentially from zero and passed explicitly to each generation function. Algorithm parameters are module-level constants. Every measurement reported in the dissertation can be regenerated by running the relevant script unmodified.
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

### Parameters

**Perlin:** scale 100.0, 6 octaves, persistence 0.5, lacunarity 2.0

<<<<<<< HEAD
Erosion = 0.048 droplets per cell, Inertia = 0.05, Capacity factor = 4.0, Erosion/deposition rate = 0.3, Evaporation rate = 0.01, Gravity = 4.0, Brush radius = 3, Droplet lifetime = 30

WFC: pattern width 2, rotations 1, backtracking not allowed, attempt limit 3, 32×32 exemplar, 3 elevation bands
=======
**Erosion:** 0.048 droplets per cell, inertia 0.05, capacity factor 4.0, erosion/deposition rate 0.3, evaporation 0.01, gravity 4.0, brush radius 3, droplet lifetime 30

**WFC:** pattern width 2, rotations 1, backtracking disabled, attempt limit 3, 32×32 exemplar with three elevation bands
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

---

## Attribution

<<<<<<< HEAD
The particle formulation implemented in the hydraulic erosion is taken from Beyer's 2015 thesis, and the parameter names and defaults are taken from the well known public implementation by Sebastian Lague.

Instead of implementing the algorithm, the Wave Function Collapse component is a Python port by Isaac Karth of Maxim Gumin's algorithm. Constraint propagation is a tricky problem with subtle failure modes: even though it is executed correctly, it may return locally consistent results that fail to meet the adjacency rules, causing the result to be wrong. A tested implementation of constraint propagation avoids such defects even when applied to a paradigm comparison.

noise generation is done with the python package [noise](https://pypi.org/project/noise/) which is a python binding to a C implementation of Perlin's original algorithm.
=======
The hydraulic erosion implementation follows the particle formulation described in Beyer's 2015 thesis, using parameter names and defaults from the widely-used public implementation by Sebastian Lague.

The Wave Function Collapse component wraps [Isaac Karth's Python port](https://github.com/ikarth/wfc_2019f) of [Maxim Gumin's algorithm](https://github.com/mxgmn/WaveFunctionCollapse), rather than reimplementing it. Constraint propagation has subtle failure modes in which an incorrect implementation produces locally plausible output that nonetheless violates adjacency rules; adapting a tested implementation avoids introducing such defects into a paradigm comparison.

Perlin noise generation uses the [`noise`](https://pypi.org/project/noise/) package, a Python binding to a C implementation of Perlin's original algorithm.
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

---

## References

<<<<<<< HEAD
Beyer, H. T. J. (2015). Bachelor's thesis on Implementation of a Method for Hydraulic Erosion at Technische Universität München.

Gaillard, M., Aubert, J., Beneš, B., et al. (2016). A polynomial approach to procedural terrain generation. arXiv:1610.03525.

Gumin, M. (2016). Wave Function Collapse Algorithm. github.com/mxgmn/WaveFunctionCollapse Algorithm.

Karth, I. (2019). wfc_2019f: A python implementation of the Wave Function Collapse algorithm. https://github.com/ikarth/wfc_2019f

Mei, X., Decaudin, P., & Hu, B.-G. (2007). Simulating, and visualizing, fast hydraulic erosion on GPU. *Pacific Graphics.*

Møller, T. N., Billeskov, J. A., & Palamas, G. (2020). Procedural Map Generation using Expanding Wave Function Collapse and Growing Grids. *FDG '20.*

Perlin, K. (1985). An image synthesizer. *SIGGRAPH '85*, 287–296.

Togelius, J., Yannakakis, G. N., Stanley, K. O., & Browne, C. (2011). Taxonomy and Survey of Search-based Procedural Content Generation. IEEE Transactions on Computational Intelligence and AI in Games, 3(3):172-186.
=======
Beyer, H. T. J. (2015). *Implementation of a Method for Hydraulic Erosion.* Bachelor's Thesis, Technische Universität München.

Gaillard, M., Aubert, J., Beneš, B., et al. (2016). Polynomial methods for procedural terrain generation. arXiv:1610.03525.

Gumin, M. (2016). Wave Function Collapse Algorithm. https://github.com/mxgmn/WaveFunctionCollapse

Karth, I. (2019). wfc_2019f: A Python port of the Wave Function Collapse algorithm. https://github.com/ikarth/wfc_2019f

Mei, X., Decaudin, P., & Hu, B.-G. (2007). Fast hydraulic erosion simulation and visualization on GPU. *Pacific Graphics.*

Møller, T. N., Billeskov, J. A., & Palamas, G. (2020). Expanding Wave Function Collapse with Growing Grids for Procedural Map Generation. *FDG '20.*

Perlin, K. (1985). An image synthesizer. *SIGGRAPH '85*, 287–296.

Togelius, J., Yannakakis, G. N., Stanley, K. O., & Browne, C. (2011). Search-based procedural content generation: A taxonomy and survey. *IEEE Transactions on Computational Intelligence and AI in Games*, 3(3), 172–186.
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

---

## Limitations

<<<<<<< HEAD
- One algorithm per paradigm: findings are claims about algorithms as representatives and not about the paradigms in full generality.
- All implementations are CPU-intensive and in Python. Absolute generation times describe this implementation, not the performance that might be reached by the underlying algorithms. The defensible measurement is the relative comparison, under the same execution model.
- The evaluation of WFC was performed at two resolutions and using only one seed; the scaling exponent is fitted to two points.
There has been no perception study done, therefore there is no established link between the amount of the quantitative measures and human judgement of terrain realism.
=======
- Each paradigm is represented by a single algorithm; findings are claims about these algorithms as representatives rather than about the paradigms in full generality.
- All implementations are CPU-bound and written in Python. Absolute generation times characterise this implementation, not the achievable performance of the underlying algorithms. The relative comparison, conducted under a common execution model, is the defensible measurement.
- WFC was evaluated at two resolutions with a single seed each; its scaling exponent is fitted to two points.
- No perception study was conducted, so the correspondence between the quantitative measures and human judgement of terrain realism remains unestablished.
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf

---

## Licence

<<<<<<< HEAD
Use the appropriate license for your code (a good default choice is MIT for academic code).
=======
*(Add your chosen licence here — MIT is a reasonable default for academic code.)*
>>>>>>> fae3316933c60cb984882ff3ccaf3cad0e0b0bdf
