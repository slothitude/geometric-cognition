"""
Experiment 004: Prime-Space Encoding
=====================================
Replaces log-phase encoding with prime exponent vectors.

Each number n = p1^e1 * p2^e2 * ... is encoded as a vector (e1, e2, ...)
normalized to the unit hypersphere. Angular distance on the hypersphere
replaces circular distance.

Hypothesis: numbers sharing prime factors point in similar directions
on the hypersphere, so geometric attention should cluster them.

Tests:
  A - Factor correlation (same metric as 003)
  B - Prime power chains (2^n, 3^n)
  C - Clustering analysis
  D - Comparison: prime-space vs log-phase
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

# ---------- Encodings ----------
def encode_prime_space(numbers, basis):
    vectors = torch.tensor([prime_exponents(n, basis) for n in numbers],
                           dtype=torch.float32)
    norms = vectors.norm(dim=1, keepdim=True).clamp(min=1e-8)
    unit = vectors / norms
    return vectors, unit

def encode_log_phase(numbers):
    x = torch.tensor(numbers, dtype=torch.float32)
    tau = torch.log(torch.abs(x) + 1e-8)
    theta = (tau % 1.0) * 2 * math.pi
    return theta, tau

# ---------- Hypersphere distance ----------
def hypersphere_dist(unit_vecs):
    sim = unit_vecs @ unit_vecs.t()
    sim = torch.clamp(sim, -1.0 + 1e-7, 1.0 - 1e-7)
    return torch.acos(sim)

# ---------- Dynamics ----------
def evolve_prime_space(vectors, steps=50, lambda_param=2.5,
                       repel_strength=0.15, lr=0.1):
    state = vectors.clone()
    n = state.shape[0]

    for _ in range(steps):
        norms = state.norm(dim=1, keepdim=True).clamp(min=1e-8)
        unit = state / norms
        dist = hypersphere_dist(unit)

        # Attention (no self)
        dist_ns = dist.clone()
        dist_ns.fill_diagonal_(float('inf'))
        scores = torch.exp(-lambda_param * dist_ns)
        attn = scores / scores.sum(dim=1, keepdim=True)

        # Attraction: weighted average
        attracted = attn @ state

        # Repulsion
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
    return state, state / norms

# ---------- Factor correlation metric ----------
def factor_correlation(numbers, dist_matrix):
    pairs = []
    for i, j in combinations(range(len(numbers)), 2):
        sf = shared_factor_count(numbers[i], numbers[j])
        d = dist_matrix[i, j].item()
        pairs.append((numbers[i], numbers[j], sf, d))

    sf_vals = [sf for _, _, sf, _ in pairs]
    d_vals = [d for _, _, _, d in pairs]
    corr = np.corrcoef(sf_vals, d_vals)[0, 1]
    return corr, pairs

# ====================================================================
#  DATA
# ====================================================================
test_numbers = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
basis_primes = sieve(17)  # [2, 3, 5, 7, 11, 13, 17]

powers_of_2 = [2, 4, 8, 16, 32, 64]
powers_of_3 = [3, 9, 27, 81]
mixed = [2, 3, 4, 6, 8, 9, 12, 16, 24, 27, 32, 48, 64, 81]

# Random primes (no shared factors)
np.random.seed(42)
random_primes = [19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73]

# ====================================================================
#  RUN
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 004: PRIME-SPACE ENCODING")
print("=" * 70)
print(f"  Basis primes: {basis_primes}")
print()

# --- Test A: Factor correlation ---
print("=" * 70)
print("  TEST A: Factor Correlation")
print("=" * 70)
print()

# Prime-space encoding
vectors, unit = encode_prime_space(test_numbers, basis_primes)
print("  Prime exponent vectors:")
for i, n in enumerate(test_numbers):
    exps = [int(vectors[i][j].item()) for j in range(len(basis_primes))]
    nonzero = [(basis_primes[j], exps[j]) for j in range(len(basis_primes)) if exps[j] > 0]
    print(f"    {n:>3} = {' x '.join(f'{p}^{e}' for p, e in nonzero)}")
print()

# Initial distances (before dynamics)
init_dist = hypersphere_dist(unit)
corr_init, pairs_init = factor_correlation(test_numbers, init_dist)

# Evolve
final_state, final_unit = evolve_prime_space(vectors, steps=50,
                                              lambda_param=2.5,
                                              repel_strength=0.15, lr=0.1)
final_dist = hypersphere_dist(final_unit)
corr_final, pairs_final = factor_correlation(test_numbers, final_dist)

print(f"  Prime-space correlation (before dynamics): {corr_init:.4f}")
print(f"  Prime-space correlation (after dynamics):  {corr_final:.4f}")
print()

# Group by shared factors
by_sf = defaultdict(list)
for a, b, sf, d in pairs_final:
    by_sf[sf].append(d)

print(f"  {'Shared Factors':>15} {'Mean Dist':>12} {'N':>5} {'Examples':>30}")
print("  " + "-" * 65)
for sf in sorted(by_sf.keys(), reverse=True):
    dists = by_sf[sf]
    examples = [(a, b) for a, b, s, _ in pairs_final if s == sf][:3]
    ex_str = ", ".join(f"{a}-{b}" for a, b in examples)
    print(f"  {sf:>15} {np.mean(dists):>12.3f} rad {len(dists):>5} {ex_str:>30}")
print()

# --- Log-phase comparison ---
theta, tau = encode_log_phase(test_numbers)
def angular_distance(a, b):
    diff = torch.abs(a - b)
    return torch.minimum(diff, 2 * math.pi - diff)
def pairwise_circ(theta):
    return angular_distance(theta.unsqueeze(1), theta.unsqueeze(0))

log_dist = pairwise_circ(theta)
corr_log, _ = factor_correlation(test_numbers, log_dist)

print(f"  Log-phase encoding correlation:  {corr_log:.4f}")
print(f"  Prime-space encoding correlation: {corr_init:.4f}")
print(f"  (More negative = better factor detection)")
print()

# --- Test B: Prime Power Chains ---
print("=" * 70)
print("  TEST B: Prime Power Chains")
print("=" * 70)
print()

for label, nums in [("2^n", powers_of_2), ("3^n", powers_of_3), ("mixed", mixed)]:
    # Extend basis if needed
    max_n = max(nums)
    basis = sieve(max_n)
    vec, un = encode_prime_space(nums, basis)
    init_d = hypersphere_dist(un)
    mean_init = init_d[~torch.eye(len(nums), dtype=torch.bool)].mean().item()

    fs, fu = evolve_prime_space(vec, steps=50, repel_strength=0.10, lr=0.1)
    final_d = hypersphere_dist(fu)
    mean_final = final_d[~torch.eye(len(nums), dtype=torch.bool)].mean().item()

    print(f"  {label}: {nums}")
    print(f"    Mean angular dist (before): {mean_init:.3f} rad ({math.degrees(mean_init):.1f} deg)")
    print(f"    Mean angular dist (after):  {mean_final:.3f} rad ({math.degrees(mean_final):.1f} deg)")

    # Check pairwise alignment for same-prime members
    for i, j in combinations(range(len(nums)), 2):
        d = final_d[i, j].item()
        sf = shared_factor_count(nums[i], nums[j])
        if d < 0.3:  # close
            print(f"    CLOSE: {nums[i]} <-> {nums[j]}: {d:.3f} rad (shared={sf})")
    print()

# --- Test C: Clustering ---
print("=" * 70)
print("  TEST C: Clustering Analysis")
print("=" * 70)
print()

# Cluster by angular proximity on hypersphere
threshold = 0.5  # radians (~28 deg)
visited = set()
clusters = []
for i in range(len(test_numbers)):
    if i in visited:
        continue
    cluster = [i]
    visited.add(i)
    for j in range(i + 1, len(test_numbers)):
        if j not in visited and final_dist[i, j] < threshold:
            cluster.append(j)
            visited.add(j)
    clusters.append(cluster)

print(f"  Clustering threshold: {threshold} rad ({math.degrees(threshold):.1f} deg)")
print()
for ci, cluster in enumerate(clusters):
    members = [test_numbers[i] for i in cluster]
    primes = [n for n in members if len(prime_factors_of(n)) == 1]
    composites = [n for n in members if n not in primes]
    shared = set.intersection(*[prime_factors_of(m) for m in members]) if members else set()
    print(f"  Cluster {ci+1}: {members}")
    if shared:
        print(f"    Shared prime factors: {shared}")
    else:
        print(f"    No shared factors across all members")
    print(f"    Primes: {primes}, Composites: {composites}")
    print()

# --- Test D: Random control ---
print("=" * 70)
print("  TEST D: Random Control")
print("=" * 70)
print()

basis_ctrl = sieve(73)
vec_r, un_r = encode_prime_space(random_primes, basis_ctrl)
dist_r = hypersphere_dist(un_r)
corr_r, pairs_r = factor_correlation(random_primes, dist_r)

rand_dists = [d for _, _, _, d in pairs_r]
test_dists = [d for _, _, _, d in pairs_final]

print(f"  Test set (with shared factors):")
print(f"    Mean dist: {np.mean(test_dists):.3f}, Std: {np.std(test_dists):.3f}")
print(f"    Correlation: {corr_init:.4f}")
print()
print(f"  Random primes (no shared factors):")
print(f"    Mean dist: {np.mean(rand_dists):.3f}, Std: {np.std(rand_dists):.3f}")
print(f"    Correlation: {corr_r:.4f}")
print()

# t-test: do pairs with shared factors have significantly different distances?
sf_0 = [d for _, _, sf, d in pairs_init if sf == 0]
sf_1 = [d for _, _, sf, d in pairs_init if sf >= 1]
from scipy import stats
if len(sf_1) > 0:
    t_stat, p_val = stats.ttest_ind(sf_0, sf_1)
    print(f"  t-test (sf=0 vs sf>=1 distances): t={t_stat:.3f}, p={p_val:.6f}")
    if p_val < 0.05:
        print(f"  *** STATISTICALLY SIGNIFICANT (p < 0.05) ***")
    else:
        print(f"  Not significant (p >= 0.05)")
print()

# ====================================================================
#  VISUALIZATION
# ====================================================================

# Plot 1: t-SNE projection of prime-space positions (before vs after)
from sklearn.manifold import TSNE

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, (vec, title) in zip(axes, [
    (vectors, "Before Dynamics"),
    (final_state, "After Dynamics"),
]):
    # 2D projection via first two prime dimensions
    # Use PCA-like: project onto top-2 singular vectors
    U, S, V = torch.pca_lowrank(vec, q=2)
    proj = vec @ V[:, :2]

    colors_map = {
        4: 'red', 8: 'red', 16: 'red',     # powers of 2
        9: 'blue',                           # power of 3
        5: 'green', 10: 'green', 15: 'green', # share factor 5
        6: 'orange', 12: 'orange',            # share 2,3
        7: 'purple', 11: 'cyan', 13: 'brown', 17: 'pink',
        14: 'gray',
    }

    for i, n in enumerate(test_numbers):
        c = colors_map.get(n, 'black')
        ax.scatter(proj[i, 0].item(), proj[i, 1].item(), s=80, color=c, zorder=5)
        ax.annotate(str(n), (proj[i, 0].item(), proj[i, 1].item()),
                    textcoords='offset points', xytext=(6, 6), fontsize=9)

    ax.set_title(title, fontsize=12)
    ax.grid(True, alpha=0.2)

plt.suptitle("Prime-Space Positions (PCA projection, colored by shared factors)", fontsize=13)
plt.tight_layout()
plt.savefig('experiments/004_prime_space_encoding/prime_space_positions.png', dpi=150)
print("  Saved: prime_space_positions.png")

# Plot 2: Factor similarity vs distance
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Prime-space
sf_ps = [sf for _, _, sf, _ in pairs_final]
d_ps = [d for _, _, _, d in pairs_final]
axes[0].scatter(sf_ps, d_ps, alpha=0.5, s=25)
axes[0].set_xlabel("Shared Prime Factors")
axes[0].set_ylabel("Angular Distance (rad)")
axes[0].set_title(f"Prime-Space (corr={corr_init:.3f})")
axes[0].grid(True, alpha=0.2)

# Log-phase (for comparison)
sf_lp = [sf for _, _, sf, _ in factor_correlation(test_numbers, log_dist)[1]]
d_lp = [d for _, _, _, d in factor_correlation(test_numbers, log_dist)[1]]
corr_lp = factor_correlation(test_numbers, log_dist)[0]
axes[1].scatter(sf_lp, d_lp, alpha=0.5, s=25, color='orange')
axes[1].set_xlabel("Shared Prime Factors")
axes[1].set_ylabel("Angular Distance (rad)")
axes[1].set_title(f"Log-Phase (corr={corr_lp:.3f})")
axes[1].grid(True, alpha=0.2)

plt.suptitle("Encoding Comparison: Shared Factors vs Distance", fontsize=13)
plt.tight_layout()
plt.savefig('experiments/004_prime_space_encoding/factor_comparison.png', dpi=150)
print("  Saved: factor_comparison.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print(f"  Log-phase encoding correlation:     {corr_log:.4f}")
print(f"  Prime-space correlation (static):   {corr_init:.4f}")
print(f"  Prime-space correlation (dynamic):  {corr_final:.4f}")
print(f"  Random control correlation:         {corr_r:.4f}")
print()

if abs(corr_init) > abs(corr_log) + 0.1:
    print("  RESULT: Prime-space encoding SIGNIFICANTLY improves factor detection")
elif abs(corr_init) > abs(corr_log):
    print("  RESULT: Prime-space encoding marginally improves factor detection")
else:
    print("  RESULT: Prime-space encoding does NOT improve factor detection")

print()
print("Done.")
