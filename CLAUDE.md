# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A mathematical research project investigating geometric computation, prime number structure, and the "Monad" — a 12-position circular framework connecting number theory to physics. The project is a series of numbered experiments testing hypotheses about how multiplicative structure, angular phase, and energy dynamics interact. Most experiments produce negative results; the positive findings are carefully documented.

## Running Experiments

```bash
# Run any experiment directly
python experiments/NNN_name/experiment.py

# Example
python experiments/018_factor_ratios/experiment.py
```

- No build system, package manager, or test suite
- Each experiment is a standalone Python script
- Outputs: printed statistics + PNG plots saved alongside the script

## Dependencies

Experiments use some combination of: `numpy`, `scipy`, `matplotlib`, `torch`. Early experiments (001-010) use PyTorch for geometric dynamics; later ones (011+) are pure numpy/scipy. No `requirements.txt` — install as needed.

## Repository Structure

```
experiments/
  001_energy_dynamics/     # Geometric attention energy minimization
  002_repulsion_field/     # Repulsion prevents collapse
  ...
  016_exor_field/          # Composite field test (last in README)
  017_zeta_interference/   # Zeta-zero exploration
  018_factor_ratios/       # The Monad framework (THE_MONAD.md) — very large
```

Each experiment directory contains:
- `experiment.py` — the main script (always present)
- `notes.md` — human-written results/analysis (most directories)
- `.png` plots — generated output
- Experiment 018 has many additional sub-experiment scripts (`walk_test.py`, `higgs_monad.py`, `monad_vm.py`, etc.)

## Key Concepts

- **Signed Wheel**: `(theta, tau, sigma)` — angular phase, log magnitude, rail polarity. The core representation.
- **6k±1 rails**: All primes > 3 sit on two arithmetic progressions (Rail1: 6k-1, Rail2: 6k+1). Rail composition forms Z2 group.
- **Prime-space encoding**: Integers as exponent vectors on the unit hypersphere. Captures factor structure exactly (correlation -0.91).
- **Log-phase encoding**: `theta = 2pi(log n mod 1)`. Destroys factor structure (correlation +0.08). This negative result is important.
- **The Monad** (THE_MONAD.md): A 12-position circle (mod 12 / clock) framework connecting the 6k±1 rails to particle physics, music theory, and Dirichlet characters. Explored in depth in experiment 018.
- **PNT density law**: `2/log(n)` on rails is the complete spatial description of primes (r=0.982). No geometric encoding adds signal beyond this.

## Conventions

- Experiment scripts are self-contained: they define their own sieve, factorization, and helper functions rather than importing shared modules
- Statistical rigor is important: permutation tests, Cohen's d, Bonferroni correction, and density-gradient controls are used throughout
- Negative results are documented with the same care as positive ones — the project values systematic falsification
- Plots use `matplotlib.use('Agg')` for non-interactive rendering
- Commit messages follow the pattern: `Experiment NNN: Descriptive Title`

## Major Documents

- `README.md` — covers experiments 001-016, the original paper draft
- `THE_MONAD.md` — the Monad framework (experiment 018+), the most active research area
- `research_walter_russell_ratios.md` — exploratory notes on Russell's ratios
