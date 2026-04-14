"""
Experiment 005: Structure-Preserving Dynamics on Prime-Space Hypersphere
=========================================================================
The prime-space encoding gives -0.91 factor correlation statically.
Naive dynamics degrade it to +0.07 because they push points off the
sphere and destroy directional structure.

Fix: constrain evolution to the hypersphere via tangent-space updates.
Track correlation preservation over time.

Three configs:
  A - Unconstrained (baseline from 004, correlation degrades)
  B - Sphere-constrained (re-normalize after each step)
  C - Tangent-space update (proper Riemannian gradient on sphere)
"""

import torch
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from itertools import combinations
from collections import defaultdict

# ---------- Prime utilities ----------
def sieve(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

def prime_exponents(n, basis):
    result = []
    temp = n
    for p in basis:
        e = 0
        while temp % p == 0 and temp > 0:
            e += 1
            temp //= p
        result.append(float(e))
    return result

def prime_factors_of(n):
    factors = set()
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.add(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.add(temp)
    return factors

def shared_factor_count(a, b):
    return len(prime_factors_of(a) & prime_factors_of(b))

# ---------- Encoding ----------
def encode_prime_space(numbers, basis):
    vectors = torch.tensor([prime_exponents(n, basis) for n in numbers],
                           dtype=torch.float32)
    norms = vectors.norm(dim=1, keepdim=True).clamp(min=1e-8)
    unit = vectors / norms
    return vectors, unit

# ---------- Distances ----------
def hypersphere_dist(unit_vecs):
    sim = unit_vecs @ unit_vecs.t()
    sim = torch.clamp(sim, -1.0 + 1e-7, 1.0 - 1e-7)
    return torch.acos(sim)

def factor_correlation(numbers, dist_matrix):
    pairs = []
    for i, j in combinations(range(len(numbers)), 2):
        sf = shared_factor_count(numbers[i], numbers[j])
        d = dist_matrix[i, j].item()
        pairs.append((numbers[i], numbers[j], sf, d))
    sf_vals = [sf for _, _, sf, _ in pairs]
    d_vals = [d for _, _, _, d in pairs]
    if np.std(d_vals) < 1e-10:
        return 0.0, pairs
    corr = np.corrcoef(sf_vals, d_vals)[0, 1]
    if np.isnan(corr):
        corr = 0.0
    return corr, pairs

# ---------- Dynamics ----------
def evolve_unconstrained(vectors, steps=50, lambda_param=2.5,
                         repel_strength=0.15, lr=0.1):
    """Original dynamics from 004 — no sphere constraint"""
    state = vectors.clone()
    n = state.shape[0]
    corrs = []

    for _ in range(steps):
        norms = state.norm(dim=1, keepdim=True).clamp(min=1e-8)
        unit = state / norms
        dist = hypersphere_dist(unit)
        corr, _ = factor_correlation(numbers, dist)
        corrs.append(corr)

        dist_ns = dist.clone()
        dist_ns.fill_diagonal_(float('inf'))
        scores = torch.exp(-lambda_param * dist_ns)
        attn = scores / scores.sum(dim=1, keepdim=True)

        attracted = attn @ state

        repulsion = torch.zeros_like(state)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                d_ij = dist[i, j] + 1e-6
                strength = repel_strength / (d_ij ** 2)
                direction = state[i] - state[j]
                dn = direction.norm() + 1e-8
                repulsion[i] += strength * direction / dn

        state = state + lr * ((attracted - state) + repulsion)

    norms = state.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return state, state / norms, corrs

def evolve_sphere_projected(vectors, steps=50, lambda_param=2.5,
                            repel_strength=0.15, lr=0.1):
    """After each update, project back to unit sphere"""
    state = vectors.clone()
    # Start on sphere
    state = state / state.norm(dim=1, keepdim=True).clamp(min=1e-8)
    n = state.shape[0]
    corrs = []

    for _ in range(steps):
        dist = hypersphere_dist(state)
        corr, _ = factor_correlation(numbers, dist)
        corrs.append(corr)

        dist_ns = dist.clone()
        dist_ns.fill_diagonal_(float('inf'))
        scores = torch.exp(-lambda_param * dist_ns)
        attn = scores / scores.sum(dim=1, keepdim=True)

        attracted = attn @ state

        repulsion = torch.zeros_like(state)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                d_ij = dist[i, j] + 1e-6
                strength = repel_strength / (d_ij ** 2)
                direction = state[i] - state[j]
                dn = direction.norm() + 1e-8
                repulsion[i] += strength * direction / dn

        state = state + lr * ((attracted - state) + repulsion)
        # PROJECT BACK TO SPHERE
        state = state / state.norm(dim=1, keepdim=True).clamp(min=1e-8)

    return state, state, corrs

def evolve_tangent_space(vectors, steps=50, lambda_param=2.5,
                         repel_strength=0.15, lr=0.1):
    """Proper Riemannian: compute gradient in tangent space, retract to sphere"""
    state = vectors.clone()
    state = state / state.norm(dim=1, keepdim=True).clamp(min=1e-8)
    n = state.shape[0]
    d = state.shape[1]
    corrs = []

    for _ in range(steps):
        dist = hypersphere_dist(state)
        corr, _ = factor_correlation(numbers, dist)
        corrs.append(corr)

        dist_ns = dist.clone()
        dist_ns.fill_diagonal_(float('inf'))
        scores = torch.exp(-lambda_param * dist_ns)
        attn = scores / scores.sum(dim=1, keepdim=True)

        # Attraction: weighted average
        attracted = attn @ state

        # Repulsion in ambient space
        repulsion = torch.zeros_like(state)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                d_ij = dist[i, j] + 1e-6
                strength = repel_strength / (d_ij ** 2)
                direction = state[i] - state[j]
                dn = direction.norm() + 1e-8
                repulsion[i] += strength * direction / dn

        # Gradient in ambient space
        grad = lr * ((attracted - state) + repulsion)

        # PROJECT GRADIENT TO TANGENT SPACE of sphere at state
        # Tangent space: all vectors perpendicular to state
        # T_x(S^d) = {v : v . x = 0}
        for i in range(n):
            x = state[i]
            g = grad[i]
            # Remove component along x
            g_tangent = g - (g.dot(x)) * x
            grad[i] = g_tangent

        # Retraction: exponential map approximation
        # x_new = normalize(x + g_tangent)
        state = state + grad
        state = state / state.norm(dim=1, keepdim=True).clamp(min=1e-8)

    return state, state, corrs

# ====================================================================
#  DATA
# ====================================================================
numbers = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
basis_primes = sieve(17)

vectors, unit = encode_prime_space(numbers, basis_primes)
init_dist = hypersphere_dist(unit)
corr_init, _ = factor_correlation(numbers, init_dist)

print("=" * 70)
print("  EXPERIMENT 005: STRUCTURE-PRESERVING DYNAMICS")
print("=" * 70)
print()
print(f"  Initial factor correlation: {corr_init:.4f}")
print(f"  (Goal: preserve or improve this value)")
print()

steps = 50

# ====================================================================
#  RUN ALL THREE CONFIGS
# ====================================================================
configs = [
    ("A: Unconstrained", evolve_unconstrained,
     {"vectors": vectors, "steps": steps, "lambda_param": 2.5,
      "repel_strength": 0.15, "lr": 0.1}),
    ("B: Sphere-projected", evolve_sphere_projected,
     {"vectors": vectors, "steps": steps, "lambda_param": 2.5,
      "repel_strength": 0.15, "lr": 0.1}),
    ("C: Tangent-space", evolve_tangent_space,
     {"vectors": vectors, "steps": steps, "lambda_param": 2.5,
      "repel_strength": 0.15, "lr": 0.1}),
]

results = {}
for label, fn, kwargs in configs:
    state, final_unit, corrs = fn(**kwargs)
    final_dist = hypersphere_dist(final_unit)
    corr_f, pairs = factor_correlation(numbers, final_dist)

    # Cluster purity: within shared-factor pairs, what fraction are < threshold?
    sf_pairs = [(i, j) for i, j in combinations(range(len(numbers)), 2)
                if shared_factor_count(numbers[i], numbers[j]) > 0]
    no_sf_pairs = [(i, j) for i, j in combinations(range(len(numbers)), 2)
                   if shared_factor_count(numbers[i], numbers[j]) == 0]

    if sf_pairs:
        sf_dists = [final_dist[i, j].item() for i, j in sf_pairs]
        no_sf_dists = [final_dist[i, j].item() for i, j in no_sf_pairs]
        separation = np.mean(no_sf_dists) - np.mean(sf_dists)
    else:
        sf_dists, no_sf_dists, separation = [], [], 0

    results[label] = {
        "corrs": corrs, "final_corr": corr_f, "pairs": pairs,
        "final_dist": final_dist, "final_unit": final_unit,
        "sf_dists": sf_dists, "no_sf_dists": no_sf_dists,
        "separation": separation,
    }

    print(f"  {label}")
    print(f"    Correlation: {corr_init:.4f} -> {corr_f:.4f} "
          f"({'PRESERVED' if abs(corr_f) > 0.5 else 'DEGRADED'})")
    print(f"    Mean dist (shared factors):   {np.mean(sf_dists):.3f} rad")
    print(f"    Mean dist (no shared factors): {np.mean(no_sf_dists):.3f} rad")
    print(f"    Separation gap: {separation:.3f} rad")
    print()

# ====================================================================
#  PARAMETER SWEEP ON BEST CONFIG (tangent-space)
# ====================================================================
print("=" * 70)
print("  PARAMETER SWEEP: Tangent-space dynamics")
print("=" * 70)
print()

sweep = [
    {"lambda_param": 1.0, "repel_strength": 0.05, "lr": 0.05},
    {"lambda_param": 2.5, "repel_strength": 0.05, "lr": 0.05},
    {"lambda_param": 1.0, "repel_strength": 0.15, "lr": 0.05},
    {"lambda_param": 2.5, "repel_strength": 0.15, "lr": 0.05},
    {"lambda_param": 1.0, "repel_strength": 0.05, "lr": 0.01},
    {"lambda_param": 2.5, "repel_strength": 0.05, "lr": 0.01},
]

sweep_results = []
for params in sweep:
    _, final_u, corrs = evolve_tangent_space(
        vectors=vectors, steps=steps, **params)
    fd = hypersphere_dist(final_u)
    c, _ = factor_correlation(numbers, fd)
    sweep_results.append({**params, "corr": c, "corrs": corrs})

print(f"  {'lambda':>8} {'repel':>8} {'lr':>6} {'corr_final':>12} {'preserved':>10}")
print("  " + "-" * 50)
for r in sweep_results:
    preserved = "YES" if abs(r["corr"]) > 0.5 else "no"
    print(f"  {r['lambda_param']:>8.1f} {r['repel_strength']:>8.2f} "
          f"{r['lr']:>6.2f} {r['corr']:>12.4f} {preserved:>10}")

print()

# ====================================================================
#  VISUALIZATION
# ====================================================================

# Plot 1: Correlation over time for all 3 configs
plt.figure(figsize=(10, 5))
for label in ["A: Unconstrained", "B: Sphere-projected", "C: Tangent-space"]:
    corrs = results[label]["corrs"]
    plt.plot(corrs, label=f"{label} (final={corrs[-1]:.3f})")
plt.axhline(y=corr_init, color='black', linestyle='--', alpha=0.5,
            label=f"Static encoding ({corr_init:.3f})")
plt.xlabel("Step")
plt.ylabel("Factor Correlation")
plt.title("Correlation Preservation Over Time")
plt.legend(fontsize=9)
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig('experiments/005_aligned_dynamics/correlation_over_time.png', dpi=150)
print("  Saved: correlation_over_time.png")

# Plot 2: Final positions on hypersphere (PCA projection)
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

color_map = {}
# Color by primary factor
for n in numbers:
    pf = min(prime_factors_of(n))  # smallest prime factor
    color_map[n] = {2: 'red', 3: 'blue', 5: 'green', 7: 'purple',
                    11: 'cyan', 13: 'orange', 17: 'brown'}[pf]

for ax, label in zip(axes, ["A: Unconstrained", "B: Sphere-projected",
                             "C: Tangent-space"]):
    fu = results[label]["final_unit"]
    U, S, V = torch.pca_lowrank(fu, q=min(2, fu.shape[1]))
    proj = fu @ V[:, :2]

    for i, n in enumerate(numbers):
        ax.scatter(proj[i, 0].item(), proj[i, 1].item(), s=80,
                   color=color_map[n], zorder=5)
        ax.annotate(str(n), (proj[i, 0].item(), proj[i, 1].item()),
                    textcoords='offset points', xytext=(6, 6), fontsize=9)
    ax.set_title(f"{label}\ncorr={results[label]['final_corr']:.3f}", fontsize=10)
    ax.grid(True, alpha=0.2)

# Legend
from matplotlib.patches import Patch
legend = [Patch(facecolor=c, label=f"smallest factor: {p}")
          for p, c in [(2, 'red'), (3, 'blue'), (5, 'green'),
                       (7, 'purple'), (11, 'cyan'), (13, 'orange'), (17, 'brown')]]
axes[2].legend(handles=legend, fontsize=7, loc='lower right')

plt.suptitle("Final Positions (PCA, colored by smallest prime factor)", fontsize=13)
plt.tight_layout()
plt.savefig('experiments/005_aligned_dynamics/final_positions.png', dpi=150)
print("  Saved: final_positions.png")

# Plot 3: Parameter sweep correlation traces
plt.figure(figsize=(10, 5))
for r in sweep_results:
    label = f"λ={r['lambda_param']}, repel={r['repel_strength']}, lr={r['lr']}"
    plt.plot(r["corrs"], label=f"{label} → {r['corr']:.3f}", alpha=0.7)
plt.axhline(y=corr_init, color='black', linestyle='--', alpha=0.5)
plt.xlabel("Step")
plt.ylabel("Factor Correlation")
plt.title("Tangent-Space Parameter Sweep")
plt.legend(fontsize=7)
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig('experiments/005_aligned_dynamics/parameter_sweep.png', dpi=150)
print("  Saved: parameter_sweep.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print(f"  Static encoding correlation:   {corr_init:.4f}")
print()
for label in ["A: Unconstrained", "B: Sphere-projected", "C: Tangent-space"]:
    fc = results[label]["final_corr"]
    sep = results[label]["separation"]
    print(f"  {label}: corr={fc:.4f}, separation={sep:.3f} rad")
print()

best = max(sweep_results, key=lambda r: abs(r["corr"]))
print(f"  Best tangent-space params: lambda={best['lambda_param']}, "
      f"repel={best['repel_strength']}, lr={best['lr']}")
print(f"  Best correlation: {best['corr']:.4f}")
print()

if abs(best["corr"]) > abs(corr_init) * 0.9:
    print("  RESULT: Tangent-space dynamics PRESERVE factor structure")
elif abs(best["corr"]) > 0.5:
    print("  RESULT: Tangent-space dynamics PARTIALLY preserve structure")
else:
    print("  RESULT: Even tangent-space dynamics degrade factor structure")
    print("  The issue is fundamental: dynamics mix the clean encoding")

print()
print("Done.")
