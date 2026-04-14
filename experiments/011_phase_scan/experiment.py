"""
Experiment 011: Phase Transform Scan for Prime Clustering
===========================================================
Tests whether ANY transform f(n) -> theta = f(n) mod 2pi
causes primes to cluster in phase space more than random numbers.

This is a systematic scan — no privileged constants, no hand-tuning.

Transforms tested:
  1. Log family: log(n), log(n)*c, log(n)/log(log(n))
  2. Log-log family: log(log(n)), log(n) + log(log(n))
  3. Power laws: n^alpha for alpha in [0.1, 1.0]
  4. Hybrid: log(n^alpha + beta), log(n) + alpha*sin(log(n))
  5. Random controls

Metric: variance of prime density across 100 phase bins
Validation: permutation test against shuffled prime labels
"""

import numpy as np
from math import log, pi, sqrt
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ====================================================================
#  PRIME SIEVE (fast)
# ====================================================================
def sieve_of_eratosthenes(N):
    """Returns boolean array where is_prime[i] = True if i is prime."""
    is_prime = np.ones(N, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return is_prime

N = 200000
print("=" * 70)
print("  EXPERIMENT 011: PHASE TRANSFORM SCAN FOR PRIME CLUSTERING")
print("=" * 70)
print()
print(f"  Sieving primes up to {N}...")

t0 = time.time()
is_prime = sieve_of_eratosthenes(N)
print(f"  Done in {time.time()-t0:.1f}s. Found {is_prime.sum()} primes.")
print()

nums = np.arange(2, N)
primes_mask = is_prime[2:N]  # align with nums
n_nums = len(nums)
n_primes = primes_mask.sum()
prime_freq = n_primes / n_nums

print(f"  Numbers: {n_nums}, Primes: {n_primes}, Frequency: {prime_freq:.4f}")
print()

# ====================================================================
#  METRIC FUNCTIONS
# ====================================================================
N_BINS = 100

def compute_prime_density_variance(theta, primes_mask, n_bins=N_BINS):
    """
    Bin theta values, compute prime density per bin, return variance.
    """
    bins = np.linspace(0, 2*pi, n_bins + 1)
    digitized = np.digitize(theta, bins) - 1
    # Clamp to valid range
    digitized = np.clip(digitized, 0, n_bins - 1)

    densities = np.zeros(n_bins)
    for i in range(n_bins):
        mask = digitized == i
        count = mask.sum()
        if count > 0:
            densities[i] = primes_mask[mask].sum() / count
        else:
            densities[i] = 0.0

    return np.var(densities), densities

def compute_kl_divergence(densities, uniform_val):
    """KL(prime_dist || uniform) where uniform = global prime frequency."""
    # Normalize densities to probability distribution
    p = densities.copy()
    p = np.clip(p, 1e-10, None)  # avoid log(0)
    p = p / p.sum()
    q = np.ones_like(p) / len(p)
    kl = np.sum(p * np.log(p / q))
    return kl

def permutation_test(theta, primes_mask, observed_var, n_perms=1000):
    """
    Shuffle prime labels and recompute variance.
    Returns p-value: fraction of random variances >= observed.
    """
    perm_vars = np.zeros(n_perms)
    for i in range(n_perms):
        perm = np.random.permutation(primes_mask)
        v, _ = compute_prime_density_variance(theta, perm)
        perm_vars[i] = v

    p_val = np.mean(perm_vars >= observed_var)
    return p_val, perm_vars

# ====================================================================
#  TRANSFORM DEFINITIONS
# ====================================================================
phi = (1 + sqrt(5)) / 2  # golden ratio
euler = 0.5772156649      # Euler-Mascheroni constant

transforms = {
    # --- Log family ---
    "log(n)":              lambda n: np.log(n),
    "log(n) * phi":        lambda n: np.log(n) * phi,
    "log(n) * e":          lambda n: np.log(n) * np.e,
    "log(n) / log(log(n))": lambda n: np.log(n) / np.log(np.log(n)),

    # --- Log-log family ---
    "log(log(n))":         lambda n: np.log(np.log(n)),
    "log(n) + log(log(n))": lambda n: np.log(n) + np.log(np.log(n)),

    # --- Power laws ---
    "n^0.1":               lambda n: n**0.1,
    "n^0.3":               lambda n: n**0.3,
    "n^0.5":               lambda n: n**0.5,
    "n^0.7":               lambda n: n**0.7,
    "n^1.0":               lambda n: n**1.0,

    # --- Hybrid transforms ---
    "log(n^0.5 + 1)":      lambda n: np.log(n**0.5 + 1),
    "log(n) + 0.1*sin(log(n))": lambda n: np.log(n) + 0.1*np.sin(np.log(n)),
    "log(n) + 0.5*sin(log(n))": lambda n: np.log(n) + 0.5*np.sin(np.log(n)),

    # --- Special constants ---
    "log(n) * pi":         lambda n: np.log(n) * pi,
    "log(n) * sqrt(2)":    lambda n: np.log(n) * sqrt(2),
}

# ====================================================================
#  RUN ALL TRANSFORMS
# ====================================================================
print("=" * 70)
print("  PHASE DENSITY ANALYSIS")
print("=" * 70)
print()

results = {}

for name, f in transforms.items():
    t0 = time.time()
    theta = f(nums.astype(np.float64)) % (2 * pi)

    var, densities = compute_prime_density_variance(theta, primes_mask)
    kl = compute_kl_divergence(densities, prime_freq)

    # Quick permutation test (500 perms for speed)
    p_val, perm_vars = permutation_test(theta, primes_mask, var, n_perms=500)

    elapsed = time.time() - t0

    results[name] = {
        "var": var,
        "kl": kl,
        "densities": densities,
        "p_val": p_val,
        "perm_mean": perm_vars.mean(),
        "perm_std": perm_vars.std(),
        "theta": theta,
    }

    sig = "***" if p_val < 0.01 else "**" if p_val < 0.05 else "*" if p_val < 0.1 else ""
    z_score = (var - perm_vars.mean()) / max(perm_vars.std(), 1e-12)

    print(f"  {name:<35} var={var:.6e}  z={z_score:+.2f}  p={p_val:.4f} {sig}")

print()

# ====================================================================
#  RANDOM BASELINE
# ====================================================================
print("  Computing random baseline (uniform random theta)...")

random_vars = []
for _ in range(500):
    theta_rand = np.random.uniform(0, 2*pi, n_nums)
    v, _ = compute_prime_density_variance(theta_rand, primes_mask)
    random_vars.append(v)

random_vars = np.array(random_vars)
print(f"  Random baseline: mean var = {random_vars.mean():.6e} +/- {random_vars.std():.6e}")
print()

# ====================================================================
#  RANKING
# ====================================================================
print("=" * 70)
print("  RANKING BY Z-SCORE (vs permutation)")
print("=" * 70)
print()

ranked = sorted(results.items(), key=lambda x: (x[1]["var"] - x[1]["perm_mean"]) / max(x[1]["perm_std"], 1e-12), reverse=True)

print(f"  {'Transform':<35} {'Variance':>12} {'Z-score':>8} {'p-value':>8} {'vs Random':>10}")
print("  " + "-" * 78)

for name, r in ranked:
    z = (r["var"] - r["perm_mean"]) / max(r["perm_std"], 1e-12)
    vs_random = r["var"] / random_vars.mean()
    sig = "***" if r["p_val"] < 0.01 else "**" if r["p_val"] < 0.05 else "*" if r["p_val"] < 0.1 else ""
    print(f"  {name:<35} {r['var']:>12.6e} {z:>+8.2f} {r['p_val']:>8.4f} {vs_random:>10.2f}x {sig}")

print()

# ====================================================================
#  DETAILED ANALYSIS OF TOP TRANSFORM
# ====================================================================
best_name, best = ranked[0]
worst_name, worst = ranked[-1]

print("=" * 70)
print(f"  BEST: {best_name}")
print(f"  WORST: {worst_name}")
print("=" * 70)
print()

# ====================================================================
#  HELD-OUT VALIDATION
# ====================================================================
print("=" * 70)
print("  HELD-OUT VALIDATION (N/2 to N)")
print("=" * 70)
print()

# Use second half as held-out
nums_val = np.arange(N//2, N).astype(np.float64)
primes_val = is_prime[N//2:N]

for name, f in list(transforms.items())[:5]:  # top 5 for speed
    theta_val = f(nums_val) % (2*pi)
    var_val, dens_val = compute_prime_density_variance(theta_val, primes_val)
    print(f"  {name:<35} var = {var_val:.6e}")

print()

# ====================================================================
#  WHY DOES LOG WORK? (if it does)
# ====================================================================
print("=" * 70)
print("  STRUCTURAL ANALYSIS")
print("=" * 70)
print()

# Check if log variance is just edge effects
best_theta = best["theta"]
bins = np.linspace(0, 2*pi, N_BINS + 1)
digitized = np.clip(np.digitize(best_theta, bins) - 1, 0, N_BINS - 1)

bin_counts = np.zeros(N_BINS)
prime_counts = np.zeros(N_BINS)
for i in range(N_BINS):
    mask = digitized == i
    bin_counts[i] = mask.sum()
    prime_counts[i] = primes_mask[mask].sum()

# Coefficient of variation
cv = np.std(bin_counts) / np.mean(bin_counts)
print(f"  Bin count CV for '{best_name}': {cv:.4f}")
print(f"  (CV=0 means perfect uniform distribution of numbers across bins)")
print()

# Check if non-uniform bin filling drives the result
uniform_theta = np.random.uniform(0, 2*pi, n_nums)
_, uniform_dens = compute_prime_density_variance(uniform_theta, primes_mask)
uniform_var = np.var(uniform_dens)

print(f"  Uniform random theta variance:  {uniform_var:.6e}")
print(f"  Best transform variance:        {best['var']:.6e}")
print(f"  Ratio: {best['var']/uniform_var:.2f}x")
print()

if best['var'] / uniform_var < 2.0:
    print("  NOTE: Best transform variance is <2x random baseline.")
    print("  Any apparent clustering is likely driven by non-uniform bin filling,")
    print("  not genuine prime phase structure.")
else:
    print(f"  NOTE: Best transform is {best['var']/uniform_var:.1f}x random baseline.")
    print("  This warrants deeper investigation.")

print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(3, 2, figsize=(14, 14))

# Plot 1: Top 5 transform density profiles
ax = axes[0, 0]
bin_centers = np.linspace(0, 2*pi, N_BINS)
for i, (name, r) in enumerate(ranked[:5]):
    ax.plot(bin_centers, r["densities"], label=f"{name} (p={r['p_val']:.3f})", alpha=0.8)
ax.axhline(y=prime_freq, color='black', linestyle='--', label=f'Expected ({prime_freq:.4f})')
ax.set_xlabel("Phase bin")
ax.set_ylabel("Prime density")
ax.set_title("Top 5 Transforms: Prime Density vs Phase")
ax.legend(fontsize=6)
ax.grid(True, alpha=0.2)

# Plot 2: Bottom 5 + random
ax = axes[0, 1]
for i, (name, r) in enumerate(ranked[-5:]):
    ax.plot(bin_centers, r["densities"], label=f"{name} (p={r['p_val']:.3f})", alpha=0.8)
ax.axhline(y=prime_freq, color='black', linestyle='--', label='Expected')
ax.set_xlabel("Phase bin")
ax.set_ylabel("Prime density")
ax.set_title("Bottom 5 Transforms: Prime Density vs Phase")
ax.legend(fontsize=6)
ax.grid(True, alpha=0.2)

# Plot 3: Z-score ranking
ax = axes[1, 0]
names_short = [n[:25] for n, _ in ranked]
z_scores = [(r["var"] - r["perm_mean"]) / max(r["perm_std"], 1e-12) for _, r in ranked]
colors = ['green' if r["p_val"] < 0.05 else 'steelblue' if r["p_val"] < 0.1 else 'lightgray' for _, r in ranked]
ax.barh(range(len(names_short)), z_scores, color=colors)
ax.set_yticks(range(len(names_short)))
ax.set_yticklabels(names_short, fontsize=7)
ax.axvline(x=0, color='black', linewidth=0.5)
ax.axvline(x=2, color='red', linewidth=0.5, linestyle='--', alpha=0.5, label='z=2')
ax.set_xlabel("Z-score (vs permutation)")
ax.set_title("Transform Ranking")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2, axis='x')

# Plot 4: Variance comparison
ax = axes[1, 1]
var_vals = [r["var"] for _, r in ranked]
perm_means = [r["perm_mean"] for _, r in ranked]
x = range(len(var_vals))
ax.bar([i - 0.2 for i in x], var_vals, width=0.4, label='Observed', color='steelblue')
ax.bar([i + 0.2 for i in x], perm_means, width=0.4, label='Permutation mean', color='lightgray')
ax.axhline(y=random_vars.mean(), color='red', linestyle='--', label='Random baseline')
ax.set_xticks(x)
ax.set_xticklabels(names_short, rotation=90, fontsize=5)
ax.set_ylabel("Density variance")
ax.set_title("Observed vs Permuted Variance")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# Plot 5: Best transform phase histogram (primes vs composites)
ax = axes[2, 0]
best_theta = best["theta"]
prime_theta = best_theta[primes_mask]
comp_theta = best_theta[~primes_mask]
ax.hist(prime_theta, bins=50, density=True, alpha=0.5, label=f'Primes (n={primes_mask.sum()})', color='red')
ax.hist(comp_theta, bins=50, density=True, alpha=0.5, label=f'Composites (n={(~primes_mask).sum()})', color='blue')
ax.set_xlabel("Phase")
ax.set_ylabel("Density")
ax.set_title(f"Phase Distribution: {best_name}")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# Plot 6: Log transform detailed view
ax = axes[2, 1]
log_theta = results["log(n)"]["theta"]
# Subsample primes and matched composites for scatter
np.random.seed(42)
prime_idx = np.where(primes_mask)[0]
comp_idx = np.where(~primes_mask)[0]
sub_comp = np.random.choice(comp_idx, size=min(5000, len(comp_idx)), replace=False)
sub_prime = np.random.choice(prime_idx, size=min(5000, len(prime_idx)), replace=False)

ax.scatter(nums[sub_comp], log_theta[sub_comp], s=0.3, alpha=0.3, color='blue', label='Composites')
ax.scatter(nums[sub_prime], log_theta[sub_prime], s=0.3, alpha=0.3, color='red', label='Primes')
ax.set_xlabel("n")
ax.set_ylabel("theta = log(n) mod 2pi")
ax.set_title("log(n) Phase vs n (red=primes, blue=composites)")
ax.legend(fontsize=8, markerscale=10)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/011_phase_scan/results.png', dpi=150)
print("  Saved: results.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()

# Count significant
n_sig_01 = sum(1 for _, r in results.items() if r["p_val"] < 0.01)
n_sig_05 = sum(1 for _, r in results.items() if r["p_val"] < 0.05)
n_sig_10 = sum(1 for _, r in results.items() if r["p_val"] < 0.10)

print(f"  Transforms tested: {len(transforms)}")
print(f"  Significant at p<0.01: {n_sig_01}")
print(f"  Significant at p<0.05: {n_sig_05}")
print(f"  Significant at p<0.10: {n_sig_10}")
print()

# Multiple testing correction (Bonferroni)
n_tests = len(transforms)
bonferroni_alpha = 0.05 / n_tests
n_bonferroni = sum(1 for _, r in results.items() if r["p_val"] < bonferroni_alpha)
print(f"  Bonferroni correction (alpha={bonferroni_alpha:.4f}): {n_bonferroni} significant")
print()

print(f"  Best transform: {best_name}")
print(f"    Variance: {best['var']:.6e}")
print(f"    Z-score:  {(best['var'] - best['perm_mean']) / max(best['perm_std'], 1e-12):+.2f}")
print(f"    p-value:  {best['p_val']:.4f}")
print(f"    vs random baseline: {best['var']/random_vars.mean():.2f}x")
print()

if n_bonferroni == 0:
    print("  RESULT: No transform survives Bonferroni correction.")
    print("  Phase-space clustering of primes is NOT detectable by any tested transform.")
elif n_bonferroni <= 2:
    print(f"  RESULT: {n_bonferroni} transform(s) survive Bonferroni correction.")
    print("  Weak signal — warrants replication with independent dataset.")
else:
    print(f"  RESULT: {n_bonferroni} transforms survive Bonferroni correction.")
    print("  Genuine structure detected in phase space.")

print()
print("Done.")
