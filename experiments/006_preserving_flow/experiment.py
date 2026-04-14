"""
Experiment 006: Structure-Preserving Flow + Diffusion Characterization
========================================================================
Two parts:

Part 1: Characterize the degradation as diffusion
  - Measure correlation at many learning rates
  - Fit a model: correlation = f(lr, steps)
  - Determine the diffusion coefficient

Part 2: Structure-preserving update
  - Compute gradient from attention + repulsion
  - Project out the alignment-breaking component
  - Update on sphere with constrained gradient
  - Track correlation preservation
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
def tangent_step(state, numbers, lambda_param=2.5, repel_strength=0.15, lr=0.05):
    """Single tangent-space update step. Returns new state and gradient."""
    n = state.shape[0]
    dist = hypersphere_dist(state)

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

    grad = lr * ((attracted - state) + repulsion)

    # Project to tangent space
    for i in range(n):
        x = state[i]
        g = grad[i]
        grad[i] = g - (g.dot(x)) * x

    new_state = state + grad
    new_state = new_state / new_state.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return new_state, grad

def structure_preserving_step(state, numbers, lambda_param=2.5,
                               repel_strength=0.15, lr=0.05, preserve_strength=1.0):
    """
    Structure-preserving update:
    1. Compute standard gradient
    2. For each factor-sharing pair, compute alignment-breaking component
    3. Project out alignment-breaking component
    """
    n = state.shape[0]

    # Standard gradient
    new_state_naive, grad = tangent_step(state, numbers, lambda_param,
                                          repel_strength, lr)

    # Build factor-sharing pair set
    sf_pairs = []
    for i, j in combinations(range(n), 2):
        if shared_factor_count(numbers[i], numbers[j]) > 0:
            sf_pairs.append((i, j))

    # For each point, compute alignment-preserving correction
    correction = torch.zeros_like(state)

    for i, j in sf_pairs:
        # Current alignment (cosine similarity)
        cos_ij = state[i].dot(state[j]).clamp(-1 + 1e-7, 1 - 1e-7)

        # After gradient, would alignment decrease?
        new_cos_ij = new_state_naive[i].dot(new_state_naive[j]).clamp(-1 + 1e-7, 1 - 1e-7)

        if new_cos_ij < cos_ij:
            # Alignment is being destroyed — add corrective force
            # Push i and j back toward each other
            diff_i = state[j] - state[i]
            diff_j = state[i] - state[j]
            loss = (cos_ij - new_cos_ij) * preserve_strength

            # Add correction proportional to alignment loss
            correction[i] += loss * diff_i / (diff_i.norm() + 1e-8)
            correction[j] += loss * diff_j / (diff_j.norm() + 1e-8)

    # Apply correction + project to tangent space
    corrected = new_state_naive + correction
    for i in range(n):
        x = corrected[i]
        norm = x.norm().clamp(min=1e-8)
        corrected[i] = x / norm

    return corrected, grad

# ====================================================================
#  DATA
# ====================================================================
numbers = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
basis_primes = sieve(17)
vectors, unit = encode_prime_space(numbers, basis_primes)
init_dist = hypersphere_dist(unit)
corr_init, _ = factor_correlation(numbers, init_dist)

print("=" * 70)
print("  EXPERIMENT 006: STRUCTURE-PRESERVING FLOW")
print("=" * 70)
print()
print(f"  Initial factor correlation: {corr_init:.4f}")
print()

steps = 50

# ====================================================================
#  PART 1: DIFFUSION CHARACTERIZATION
# ====================================================================
print("=" * 70)
print("  PART 1: Diffusion Characterization (lr sweep)")
print("=" * 70)
print()

lrs = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
diffusion_data = []

for lr in lrs:
    state = unit.clone()
    corrs = []
    for _ in range(steps):
        c, _ = factor_correlation(numbers, hypersphere_dist(state))
        corrs.append(c)
        state, _ = tangent_step(state, numbers, lr=lr)

    diffusion_data.append({"lr": lr, "corrs": corrs, "final_corr": corrs[-1]})
    print(f"  lr={lr:>6.3f}: corr {corr_init:.4f} -> {corrs[-1]:.4f}")

print()

# Fit exponential decay model: corr(t) = corr_init * exp(-D * lr * t) + baseline
final_corrs = [d["final_corr"] for d in diffusion_data]
lr_vals = [d["lr"] for d in diffusion_data]

# Simple fit: final_corr ≈ a * exp(-b * lr * steps) + c
from scipy.optimize import curve_fit

def decay_model(lr, a, b, c):
    return a * np.exp(-b * lr * steps) + c

try:
    popt, _ = curve_fit(decay_model, lr_vals, final_corrs,
                        p0=[-0.91, 1.0, 0.0],
                        bounds=([-2, 0, -1], [0, 100, 1]))
    a_fit, b_fit, c_fit = popt
    print(f"  Decay model: corr(lr) = {a_fit:.4f} * exp(-{b_fit:.4f} * lr * {steps}) + {c_fit:.4f}")
    print(f"  Diffusion coefficient D ~ {b_fit:.4f}")
    print(f"  Half-life at lr=0.01: {math.log(2)/(b_fit*0.01):.0f} steps")
    print()
except:
    print("  Could not fit decay model")
    print()

# ====================================================================
#  PART 2: STRUCTURE-PRESERVING FLOW
# ====================================================================
print("=" * 70)
print("  PART 2: Structure-Preserving Flow")
print("=" * 70)
print()

preserve_configs = [
    ("Standard tangent", 0.0),
    ("Weak preserve (0.5)", 0.5),
    ("Medium preserve (1.0)", 1.0),
    ("Strong preserve (2.0)", 2.0),
]

preserve_results = {}
for label, ps in preserve_configs:
    state = unit.clone()
    corrs = []
    energies = []

    for step in range(steps):
        dist = hypersphere_dist(state)
        c, _ = factor_correlation(numbers, dist)
        corrs.append(c)
        # Energy: sum of distances (lower = more clustered)
        mask = ~torch.eye(len(numbers), dtype=torch.bool)
        energies.append(dist[mask].sum().item())

        if ps == 0.0:
            state, _ = tangent_step(state, numbers, lr=0.05)
        else:
            state, _ = structure_preserving_step(state, numbers, lr=0.05,
                                                  preserve_strength=ps)

    final_dist = hypersphere_dist(state)
    fc, _ = factor_correlation(numbers, final_dist)

    # Separation: mean dist for shared-factor vs no-shared-factor pairs
    sf_pairs_d = []
    nsf_pairs_d = []
    for i, j in combinations(range(len(numbers)), 2):
        d = final_dist[i, j].item()
        if shared_factor_count(numbers[i], numbers[j]) > 0:
            sf_pairs_d.append(d)
        else:
            nsf_pairs_d.append(d)

    sep = np.mean(nsf_pairs_d) - np.mean(sf_pairs_d)

    preserve_results[label] = {
        "corrs": corrs, "energies": energies, "final_corr": fc,
        "separation": sep, "sf_mean": np.mean(sf_pairs_d),
        "nsf_mean": np.mean(nsf_pairs_d),
    }

    print(f"  {label}")
    print(f"    Correlation: {corr_init:.4f} -> {fc:.4f} "
          f"({'PRESERVED' if abs(fc) > 0.5 else 'degraded'})")
    print(f"    Shared-factor mean dist:   {np.mean(sf_pairs_d):.3f}")
    print(f"    No-factor mean dist:       {np.mean(nsf_pairs_d):.3f}")
    print(f"    Separation gap:            {sep:.3f} rad")
    print()

# ====================================================================
#  VISUALIZATION
# ====================================================================

# Plot 1: Diffusion characterization — correlation vs lr
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
for d in diffusion_data:
    plt.plot(d["corrs"], label=f"lr={d['lr']:.3f}", alpha=0.7)
plt.axhline(y=corr_init, color='black', linestyle='--', alpha=0.5)
plt.xlabel("Step")
plt.ylabel("Factor Correlation")
plt.title("Diffusion: Correlation Decay")
plt.legend(fontsize=7)
plt.grid(True, alpha=0.2)

plt.subplot(1, 2, 2)
plt.semilogx([d["lr"] for d in diffusion_data],
             [d["final_corr"] for d in diffusion_data], 'bo-')
plt.axhline(y=corr_init, color='black', linestyle='--', alpha=0.5,
            label=f"Static ({corr_init:.3f})")
plt.xlabel("Learning Rate (log scale)")
plt.ylabel("Final Correlation")
plt.title("Correlation vs Step Size")
plt.legend()
plt.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/006_preserving_flow/diffusion_characterization.png', dpi=150)
print("  Saved: diffusion_characterization.png")

# Plot 2: Preserving flow comparison
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
for label in preserve_results:
    plt.plot(preserve_results[label]["corrs"], label=label)
plt.axhline(y=corr_init, color='black', linestyle='--', alpha=0.5,
            label=f"Static ({corr_init:.3f})")
plt.xlabel("Step")
plt.ylabel("Factor Correlation")
plt.title("Structure-Preserving Flow")
plt.legend(fontsize=8)
plt.grid(True, alpha=0.2)

plt.subplot(1, 2, 2)
labels = list(preserve_results.keys())
seps = [preserve_results[l]["separation"] for l in labels]
corrs_f = [preserve_results[l]["final_corr"] for l in labels]
x = range(len(labels))
plt.bar(x, seps, color=['red', 'orange', 'green', 'blue'])
plt.xticks(x, [l.split("(")[0].strip() for l in labels], fontsize=8)
plt.ylabel("Separation Gap (rad)")
plt.title("Factor Separation by Preserve Strength")
plt.grid(True, alpha=0.2, axis='y')

plt.tight_layout()
plt.savefig('experiments/006_preserving_flow/preserving_comparison.png', dpi=150)
print("  Saved: preserving_comparison.png")

# Plot 3: Correlation vs Separation trade-off
plt.figure(figsize=(8, 6))
plt.scatter(corrs_f, seps, s=100)
for i, label in enumerate(labels):
    plt.annotate(label, (corrs_f[i], seps[i]),
                textcoords='offset points', xytext=(10, 5), fontsize=8)
plt.xlabel("Factor Correlation")
plt.ylabel("Separation Gap (rad)")
plt.title("Correlation vs Separation Trade-off")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig('experiments/006_preserving_flow/tradeoff.png', dpi=150)
print("  Saved: tradeoff.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print(f"  Static encoding correlation: {corr_init:.4f}")
print()
print("  Part 1 — Diffusion characterization:")
print(f"    Correlation degrades smoothly with lr")
print(f"    lr=0.001: {diffusion_data[0]['final_corr']:.4f}")
print(f"    lr=0.01:  {diffusion_data[3]['final_corr']:.4f}")
print(f"    lr=0.10:  {diffusion_data[6]['final_corr']:.4f}")
print()
print("  Part 2 — Structure-preserving flow:")
for label in preserve_results:
    r = preserve_results[label]
    print(f"    {label}: corr={r['final_corr']:.4f}, sep={r['separation']:.3f}")
print()

# Find best
best_label = max(preserve_results, key=lambda l: abs(preserve_results[l]["final_corr"]))
best = preserve_results[best_label]
if abs(best["final_corr"]) > abs(corr_init) * 0.8:
    print("  RESULT: Structure-preserving flow MAINTAINS correlation > 80% of static")
elif abs(best["final_corr"]) > 0.5:
    print("  RESULT: Structure-preserving flow partially maintains correlation")
else:
    print("  RESULT: Even preserving flow cannot maintain factor structure")

print()
print("Done.")
