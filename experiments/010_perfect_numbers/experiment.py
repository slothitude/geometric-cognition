"""
Experiment 010: Mobius Twist and Perfect Numbers
=================================================
Tests whether the Mobius twist (sigma/winding) adds separability
signal for perfect numbers beyond prime-space alone.

Perfect numbers = 6, 28, 496, 8128
All have form 2^(p-1) * (2^p - 1) where (2^p-1) is Mersenne prime.

Controls: nearby composites matched by magnitude and factor count.

Hypothesis: Mobius encoding captures multiplicative PATH structure
(how factors compose), not just factor content (what factors exist).
If so, perfect numbers should be more separable with Mobius than
with prime-space alone.
"""

import torch
import math
import numpy as np
from itertools import combinations
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ====================================================================
#  PRIME UTILITIES
# ====================================================================
def prime_factors_of(n):
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def prime_exponents(n, basis):
    factors = prime_factors_of(n)
    return [factors.get(p, 0) for p in basis]

def is_perfect(n):
    """Check if n is a perfect number (sum of divisors = 2n)"""
    if n < 2:
        return False
    divisors = [1]
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            divisors.append(i)
            if i != n // i:
                divisors.append(n // i)
    return sum(divisors) == n

# ====================================================================
#  DATASET
# ====================================================================
# Perfect numbers up to 10000
perfects = [6, 28, 496, 8128]

# Controls: nearby composites, matched by magnitude and factor structure
# For each perfect number, pick numbers in same magnitude range with
# similar total factor count but NOT perfect
controls = {
    6: [4, 8, 9, 10, 12],
    28: [24, 26, 27, 30, 32],
    496: [480, 486, 500, 504, 512],
    8128: [8000, 8064, 8100, 8192, 8448],
}

all_numbers = sorted(set(perfects + [c for cs in controls.values() for c in cs]))
n_perfects = len(perfects)
n_controls = len(all_numbers) - n_perfects

# Full basis primes (up to largest needed)
max_n = max(all_numbers)
basis = []
for p in range(2, max_n + 1):
    is_p = True
    for i in range(2, int(p**0.5) + 1):
        if p % i == 0:
            is_p = False
            break
    if is_p:
        basis.append(p)

print("=" * 70)
print("  EXPERIMENT 010: MOBIUS TWIST + PERFECT NUMBERS")
print("=" * 70)
print()
print(f"  Perfect numbers: {perfects}")
print(f"  Controls: {n_controls} numbers")
print(f"  All: {all_numbers}")
print()

# Show structure of perfect numbers
print("  Perfect number structure:")
for n in perfects:
    f = prime_factors_of(n)
    print(f"    {n} = {f}")
print()

# ====================================================================
#  ENCODING 1: PRIME-SPACE (baseline)
# ====================================================================
vectors = torch.tensor([prime_exponents(n, basis) for n in all_numbers],
                       dtype=torch.float32)
norms = vectors.norm(dim=1, keepdim=True).clamp(min=1e-8)
unit = vectors / norms

def hypersphere_dist(unit_vecs):
    sim = unit_vecs @ unit_vecs.t()
    sim = torch.clamp(sim, -1 + 1e-7, 1 - 1e-7)
    return torch.acos(sim)

prime_dist = hypersphere_dist(unit)

# ====================================================================
#  ENCODING 2: PRIME-SPACE + MOBIUS TWIST
# ====================================================================
def compute_mobius_encoding(numbers, basis):
    """
    For each number, compute unwrapped angles per prime dimension
    and track sigma (polarity) from winding.
    """
    n = len(numbers)
    d = len(basis)

    # Per-dimension unwrapped angle: theta_d = 2*pi * e_d * phi_d
    # where phi_d = golden_ratio^d (different scale per prime)
    phi = (1 + 5**0.5) / 2
    theta_unwrapped = torch.zeros(n, d)
    for i, num in enumerate(numbers):
        exps = prime_exponents(num, basis)
        for j, e in enumerate(exps):
            # Use a different irrational scaling per dimension to avoid aliasing
            scale = phi ** (j + 1)
            theta_unwrapped[i, j] = 2 * math.pi * e * scale

    sigma = torch.ones(n, d)  # start at +1

    # Count windings to set initial sigma
    for i in range(n):
        for j in range(d):
            k = math.floor(theta_unwrapped[i, j].item() / (2 * math.pi))
            if k % 2 == 1:
                sigma[i, j] = -1.0

    return theta_unwrapped, sigma

theta_u, sigma = compute_mobius_encoding(all_numbers, basis)

def mobius_prime_distance(theta_u, sigma, polarity_weight=1.0):
    """Per-dimension Mobius-aware distance"""
    n, d = theta_u.shape
    total_dist = torch.zeros(n, n)

    for dim in range(d):
        theta = theta_u[:, dim] % (2 * math.pi)
        diff = torch.abs(theta.unsqueeze(1) - theta.unsqueeze(0))
        d_theta = torch.minimum(diff, 2 * math.pi - diff)

        sigma_match = sigma[:, dim].unsqueeze(1) * sigma[:, dim].unsqueeze(0)
        d_sigma = torch.where(sigma_match > 0,
                              torch.zeros(n, n),
                              torch.ones(n, n) * math.pi)

        total_dist += d_theta + polarity_weight * d_sigma

    return total_dist

mobius_dist = mobius_prime_distance(theta_u, sigma, polarity_weight=1.0)

# ====================================================================
#  SEPARABILITY METRIC
# ====================================================================
def separability_score(dist_matrix, perfect_idx, control_idx):
    """
    Score = mean distance between perfects and controls
          - mean distance within perfects group
    Higher = better separation (perfects cluster together, away from controls)
    """
    # Within-perfects distance
    if len(perfect_idx) > 1:
        within = []
        for i, j in combinations(perfect_idx, 2):
            within.append(dist_matrix[i, j].item())
        mean_within = np.mean(within)
    else:
        mean_within = 0.0

    # Between (perfects vs controls)
    between = []
    for pi in perfect_idx:
        for ci in control_idx:
            between.append(dist_matrix[pi, ci].item())
    mean_between = np.mean(between)

    return mean_between - mean_within, mean_within, mean_between

perfect_idx = [all_numbers.index(n) for n in perfects]
control_idx = [i for i, n in enumerate(all_numbers) if n not in perfects]

print("=" * 70)
print("  SEPARABILITY ANALYSIS")
print("=" * 70)
print()

# Prime-space separability
prime_sep, prime_within, prime_between = separability_score(
    prime_dist, perfect_idx, control_idx)
print(f"  Prime-space only:")
print(f"    Within-perfects dist:  {prime_within:.4f} rad")
print(f"    Perfects-to-controls:  {prime_between:.4f} rad")
print(f"    Separability:          {prime_sep:.4f} rad")
print()

# Mobius separability at different polarity weights
mobius_results = {}
for pw in [0.1, 0.5, 1.0, 2.0]:
    md = mobius_prime_distance(theta_u, sigma, polarity_weight=pw)
    sep, within, between = separability_score(md, perfect_idx, control_idx)
    mobius_results[pw] = {"sep": sep, "within": within, "between": between, "dist": md}
    print(f"  Mobius (pw={pw:.1f}):")
    print(f"    Within-perfects dist:  {within:.4f} rad")
    print(f"    Perfects-to-controls:  {between:.4f} rad")
    print(f"    Separability:          {sep:.4f} rad")
    print()

# ====================================================================
#  PER-PERFECT ANALYSIS
# ====================================================================
print("=" * 70)
print("  PER-PERFECT DISTANCE TO NEAREST CONTROL")
print("=" * 70)
print()

for pi, pn in enumerate(perfect_idx):
    p_num = all_numbers[pn]
    print(f"  Perfect number: {p_num}")

    # Prime-space: distance to all controls
    p_dists_prime = [(all_numbers[ci], prime_dist[pn, ci].item())
                     for ci in control_idx]
    p_dists_prime.sort(key=lambda x: x[1])

    # Mobius: distance to all controls
    md = mobius_results[1.0]["dist"]
    p_dists_mobius = [(all_numbers[ci], md[pn, ci].item())
                      for ci in control_idx]
    p_dists_mobius.sort(key=lambda x: x[1])

    print(f"    Prime-space nearest controls:  "
          f"{p_dists_prime[0][0]}({p_dists_prime[0][1]:.3f}), "
          f"{p_dists_prime[1][0]}({p_dists_prime[1][1]:.3f})")
    print(f"    Mobius nearest controls:       "
          f"{p_dists_mobius[0][0]}({p_dists_mobius[0][1]:.3f}), "
          f"{p_dists_mobius[1][0]}({p_dists_mobius[1][1]:.3f})")

    # Does Mobius push perfect further from controls?
    prime_min = p_dists_prime[0][1]
    mobius_min = p_dists_mobius[0][1]
    delta = mobius_min - prime_min
    print(f"    Delta (Mobius - Prime): {delta:+.4f} "
          f"({'better' if delta > 0 else 'worse'})")
    print()

# ====================================================================
#  SIGMA STATE ANALYSIS
# ====================================================================
print("=" * 70)
print("  SIGMA STATE: PERFECTS vs CONTROLS")
print("=" * 70)
print()

# How many sigma dimensions are flipped for each number?
sigma_flips = (sigma < 0).sum(dim=1)

print(f"  {'Number':<8} {'Type':<10} {'Sigma flips':>12} {'Prime factors':>30}")
for i, n in enumerate(all_numbers):
    ntype = "PERFECT" if n in perfects else "control"
    factors = prime_factors_of(n)
    fstr = " x ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items()))
    print(f"  {n:<8} {ntype:<10} {int(sigma_flips[i].item()):>12} {fstr:>30}")

print()

perfect_flips = sigma_flips[perfect_idx].float().numpy()
control_flips = sigma_flips[control_idx].float().numpy()

t_stat, p_val = stats.ttest_ind(perfect_flips, control_flips)
print(f"  Sigma flips (perfects): {perfect_flips.mean():.1f} +/- {perfect_flips.std():.1f}")
print(f"  Sigma flips (controls): {control_flips.mean():.1f} +/- {control_flips.std():.1f}")
print(f"  t-test: t={t_stat:.3f}, p={p_val:.3f}")
if p_val < 0.05:
    print(f"  SIGNIFICANT difference in sigma state")
else:
    print(f"  NOT significant")
print()

# ====================================================================
#  PERMUTATION TEST
# ====================================================================
print("=" * 70)
print("  PERMUTATION TEST")
print("=" * 70)
print()

# Does Mobius separability beat random label assignment?
n_perms = 10000
perm_seps_prime = []
perm_seps_mobius = []

for _ in range(n_perms):
    # Randomly assign 4 numbers as "perfect" and rest as "control"
    perm_perfect = np.random.choice(len(all_numbers), n_perfects, replace=False)
    perm_control = [i for i in range(len(all_numbers)) if i not in perm_perfect]

    s_p, _, _ = separability_score(prime_dist, perm_perfect.tolist(), perm_control)
    s_m, _, _ = separability_score(mobius_results[1.0]["dist"],
                                    perm_perfect.tolist(), perm_control)
    perm_seps_prime.append(s_p)
    perm_seps_mobius.append(s_m)

perm_seps_prime = np.array(perm_seps_prime)
perm_seps_mobius = np.array(perm_seps_mobius)

p_prime = np.mean(perm_seps_prime >= prime_sep)
p_mobius = np.mean(perm_seps_mobius >= mobius_results[1.0]["sep"])

print(f"  Prime-space separability: {prime_sep:.4f}")
print(f"  Permutation mean:         {np.mean(perm_seps_prime):.4f}")
print(f"  p-value:                  {p_prime:.4f}")
print()
print(f"  Mobius separability:      {mobius_results[1.0]['sep']:.4f}")
print(f"  Permutation mean:         {np.mean(perm_seps_mobius):.4f}")
print(f"  p-value:                  {p_mobius:.4f}")
print()

# Delta separability: does Mobius add BEYOND prime-space?
delta_seps = []
for _ in range(n_perms):
    perm_perfect = np.random.choice(len(all_numbers), n_perfects, replace=False)
    perm_control = [i for i in range(len(all_numbers)) if i not in perm_perfect]

    s_p, _, _ = separability_score(prime_dist, perm_perfect.tolist(), perm_control)
    s_m, _, _ = separability_score(mobius_results[1.0]["dist"],
                                    perm_perfect.tolist(), perm_control)
    delta_seps.append(s_m - s_p)

delta_seps = np.array(delta_seps)
actual_delta = mobius_results[1.0]["sep"] - prime_sep
p_delta = np.mean(delta_seps >= actual_delta)

print(f"  Delta (Mobius - Prime):   {actual_delta:+.4f}")
print(f"  Permutation delta mean:   {np.mean(delta_seps):+.4f}")
print(f"  p-value:                  {p_delta:.4f}")
print()

if p_delta < 0.05:
    print(f"  RESULT: Mobius ADDS significant separability beyond prime-space")
elif actual_delta > 0:
    print(f"  RESULT: Mobius improves slightly but NOT significant")
else:
    print(f"  RESULT: Mobius does NOT improve separability")
print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Sigma heatmap
ax = axes[0, 0]
# Show sigma for first 20 prime dimensions (most are 0 beyond that)
n_dims = min(20, len(basis))
sigma_show = sigma[:, :n_dims].numpy()
im = ax.imshow(sigma_show, cmap='RdBu', vmin=-1, vmax=1, aspect='auto')
ax.set_yticks(range(len(all_numbers)))
labels = [f"{n}{'*' if n in perfects else ''}" for n in all_numbers]
ax.set_yticklabels(labels, fontsize=7)
ax.set_xticks(range(n_dims))
ax.set_xticklabels([str(basis[i]) for i in range(n_dims)], fontsize=6, rotation=45)
ax.set_xlabel("Prime dimension")
ax.set_title("Sigma State (* = perfect number)")
plt.colorbar(im, ax=ax)

# Plot 2: Prime-space distances (heatmap)
ax = axes[0, 1]
im = ax.imshow(prime_dist.numpy(), cmap='viridis')
ax.set_xticks(range(len(all_numbers)))
ax.set_xticklabels([str(n) for n in all_numbers], fontsize=6, rotation=45)
ax.set_yticks(range(len(all_numbers)))
ax.set_yticklabels([str(n) for n in all_numbers], fontsize=6)
# Highlight perfect-perfect pairs
for pi in perfect_idx:
    for pj in perfect_idx:
        ax.add_patch(plt.Rectangle((pj-0.5, pi-0.5), 1, 1,
                     fill=False, edgecolor='red', linewidth=2))
ax.set_title("Prime-Space Distances (red = perfect-perfect)")

# Plot 3: Permutation distributions
ax = axes[1, 0]
ax.hist(perm_seps_prime, bins=50, alpha=0.5, label=f'Prime (p={p_prime:.3f})', color='blue')
ax.hist(perm_seps_mobius, bins=50, alpha=0.5, label=f'Mobius (p={p_mobius:.3f})', color='red')
ax.axvline(x=prime_sep, color='blue', linewidth=2, linestyle='--')
ax.axvline(x=mobius_results[1.0]["sep"], color='red', linewidth=2, linestyle='--')
ax.set_xlabel("Separability Score")
ax.set_ylabel("Count")
ax.set_title("Permutation Test (dashed = actual)")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# Plot 4: Delta separability
ax = axes[1, 1]
ax.hist(delta_seps, bins=50, color='gray', alpha=0.7)
ax.axvline(x=actual_delta, color='red', linewidth=2, linestyle='--',
           label=f'Actual delta = {actual_delta:+.3f}')
ax.axvline(x=np.mean(delta_seps), color='black', linewidth=1, linestyle=':',
           label=f'Mean delta = {np.mean(delta_seps):+.3f}')
ax.set_xlabel("Delta Separability (Mobius - Prime)")
ax.set_ylabel("Count")
ax.set_title(f"Does Mobius add beyond prime-space? (p={p_delta:.3f})")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/010_perfect_numbers/results.png', dpi=150)
print("  Saved: results.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print(f"  Prime-space separability: {prime_sep:.4f} (p={p_prime:.4f})")
print(f"  Mobius separability:      {mobius_results[1.0]['sep']:.4f} (p={p_mobius:.4f})")
print(f"  Delta (Mobius - Prime):   {actual_delta:+.4f} (p={p_delta:.4f})")
print(f"  Sigma t-test:             t={t_stat:.3f}, p={p_val:.3f}")
print()

if p_delta < 0.05 and actual_delta > 0:
    print("  RESULT: Mobius twist ADDS significant separability for perfect numbers")
    print("  This suggests winding structure captures multiplicative PATH information")
elif p_prime < 0.05:
    print("  RESULT: Prime-space alone separates perfect numbers")
    print("  Mobius adds nothing significant beyond that")
else:
    print("  RESULT: Neither prime-space nor Mobius significantly separates")
    print("  perfect numbers from matched controls (too few samples)")

print()
print("Done.")
