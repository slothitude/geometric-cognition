"""
Experiment 011c: Golden Phase Tests (R = m*phi^2)
==================================================
Tests the specific claims of the R = m*phi^2 theory:
1. Phase bakeoff: phi vs pi vs sqrt(2) vs random constants
2. 137 divisibility frequency
3. Phase vs primality correlation
4. TITAN resonance scoring for prime detection

Run ONCE clean. No tuning.
"""

import numpy as np
import random
import math
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ====================================================================
#  CONSTANTS
# ====================================================================
PHI = (1 + 5**0.5) / 2
PI = math.pi
SQRT2 = math.sqrt(2)
EULER = math.e

# ====================================================================
#  FAST PRIME SIEVE
# ====================================================================
def sieve(N):
    is_prime = np.ones(N, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return is_prime

N = 100000
print("=" * 70)
print("  EXPERIMENT 011c: GOLDEN PHASE TESTS (R = m*phi^2)")
print("=" * 70)
print()

print(f"  Sieving primes up to {N}...")
is_prime = sieve(N)
primes_list = [i for i in range(2, N) if is_prime[i]]
print(f"  Found {len(primes_list)} primes.")
print()

# ====================================================================
#  EXPERIMENT 1: PHASE BAKE-OFF
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 1: PHASE BAKE-OFF")
print("=" * 70)
print()

# Use numpy arrays for speed
primes_arr = np.array(primes_list, dtype=np.float64)

def transform_log(p): return np.log(p)
def transform_loglog(p): return np.log(np.log(p[p > 2]))  # skip p=2
def transform_sqrt(p): return np.sqrt(p)
def transform_linear(p): return p

TRANSFORMS = {
    "log": transform_log,
    "loglog": transform_loglog,
    "sqrt": transform_sqrt,
    "linear": transform_linear,
}

CONSTANTS = {
    "phi": PHI,
    "pi": PI,
    "sqrt2": SQRT2,
    "e": EULER,
    "random_1": random.uniform(1.1, 3.9),
    "random_2": random.uniform(1.1, 3.9),
    "random_3": random.uniform(1.1, 3.9),
}

def phase_uniformity(phases):
    """KS test against uniform distribution on [0, 2pi]"""
    from scipy.stats import kstest
    norm = phases / (2 * PI)
    stat, p = kstest(norm, 'uniform')
    return stat, p

def phase_entropy(phases, bins=50):
    """Entropy of phase histogram"""
    hist, _ = np.histogram(phases, bins=bins, range=(0, 2*PI), density=True)
    hist = hist + 1e-12
    from scipy.stats import entropy
    return entropy(hist)

def clustering_score(phases, bins=50):
    """Std of histogram bin counts"""
    hist, _ = np.histogram(phases, bins=bins, range=(0, 2*PI))
    return np.std(hist)

results = []
print(f"  {'Transform':<10} {'Constant':<12} {'KS stat':>8} {'KS p':>8} {'Entropy':>8} {'Clustering':>11}")
print("  " + "-" * 65)

for t_name, t_func in TRANSFORMS.items():
    transformed = t_func(primes_arr)
    if t_name == "loglog":
        # Need to handle separately since array length changes
        valid = primes_arr[primes_arr > 2]
        transformed = np.log(np.log(valid))

    for c_name, c_val in CONSTANTS.items():
        phases = (transformed * c_val) % (2 * PI)

        ks_stat, ks_p = phase_uniformity(phases)
        ent = phase_entropy(phases)
        cluster = clustering_score(phases)

        results.append({
            "transform": t_name,
            "constant": c_name,
            "ks_stat": ks_stat,
            "ks_p": ks_p,
            "entropy": ent,
            "clustering": cluster,
        })

        sig = "***" if ks_p < 0.01 else "**" if ks_p < 0.05 else "*" if ks_p < 0.1 else ""
        print(f"  {t_name:<10} {c_name:<12} {ks_stat:>8.4f} {ks_p:>8.4f} {ent:>8.4f} {cluster:>11.2f} {sig}")

print()

# Check if phi stands out
phi_results = [r for r in results if r["constant"] == "phi"]
non_phi_results = [r for r in results if r["constant"] not in ("phi",)]
phi_mean_ks = np.mean([r["ks_stat"] for r in phi_results])
other_mean_ks = np.mean([r["ks_stat"] for r in non_phi_results])
phi_mean_clust = np.mean([r["clustering"] for r in phi_results])
other_mean_clust = np.mean([r["clustering"] for r in non_phi_results])

print(f"  Phi average KS stat: {phi_mean_ks:.4f}")
print(f"  Other constants average KS stat: {other_mean_ks:.4f}")
print(f"  Phi average clustering: {phi_mean_clust:.2f}")
print(f"  Other constants average clustering: {other_mean_clust:.2f}")
print()

if abs(phi_mean_ks - other_mean_ks) / max(other_mean_ks, 1e-10) < 0.1:
    print("  RESULT: phi is NOT special — similar to all other constants.")
else:
    print("  RESULT: phi differs from other constants.")
print()

# ====================================================================
#  EXPERIMENT 2: 137 FREQUENCY TEST
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 2: 137 DIVISIBILITY FREQUENCY")
print("=" * 70)
print()

# Test: how often does k divide 36*p^2 + 1 for various k?
targets = [137, 131, 139, 149, 151, 127, 163, 167, 173, 179]
n_test_primes = min(5000, len(primes_list))

div_counts = {k: 0 for k in targets}
for p in primes_list[:n_test_primes]:
    n = 36 * (p**2) + 1
    for k in targets:
        if n % k == 0:
            div_counts[k] += 1

# Expected by random chance: each k divides ~1/k of numbers
print(f"  Testing 36*p^2 + 1 for first {n_test_primes} primes")
print(f"  Expected frequency for k: ~1/k (random chance)")
print()
print(f"  {'k':<6} {'Count':>7} {'Frequency':>10} {'Expected':>10} {'Ratio':>7}")
print("  " + "-" * 45)

for k in sorted(targets):
    freq = div_counts[k] / n_test_primes
    expected = 1.0 / k
    ratio = freq / expected if expected > 0 else 0
    marker = " <--" if k == 137 else ""
    print(f"  {k:<6} {div_counts[k]:>7} {freq:>10.4f} {expected:>10.4f} {ratio:>7.2f}{marker}")

print()

# Statistical test: is 137 significantly different from neighbors?
from scipy.stats import chi2_contingency
neighbors = [131, 137, 139, 149]
counts_arr = [[div_counts[k], n_test_primes - div_counts[k]] for k in neighbors]
chi2, p_val, dof, expected = chi2_contingency(counts_arr)
print(f"  Chi-squared test (137 vs neighbors): chi2={chi2:.2f}, p={p_val:.4f}")
if p_val < 0.05:
    print("  137 IS significantly different from neighbors.")
else:
    print("  137 is NOT significantly different from neighbors.")
print()

# ====================================================================
#  EXPERIMENT 3: PHASE VS PRIMALITY
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 3: PRIME DENSITY vs GOLDEN PHASE")
print("=" * 70)
print()

# Compute golden phase for all integers
limit = 100000
nums = np.arange(3, limit, dtype=np.float64)
prime_mask = is_prime[3:limit]

# Golden phase
theta_phi = (np.log(nums) * PHI) % (2 * PI)
# Control phases
theta_pi = (np.log(nums) * PI) % (2 * PI)
theta_sqrt2 = (np.log(nums) * SQRT2) % (2 * PI)
theta_e = (np.log(nums) * EULER) % (2 * PI)
theta_rand = (np.log(nums) * random.uniform(1.5, 3.5)) % (2 * PI)

def prime_density_by_phase(theta, prime_mask, n_bins=50):
    bins = np.linspace(0, 2*PI, n_bins + 1)
    digitized = np.clip(np.digitize(theta, bins) - 1, 0, n_bins - 1)
    densities = np.zeros(n_bins)
    for i in range(n_bins):
        mask = digitized == i
        count = mask.sum()
        if count > 0:
            densities[i] = prime_mask[mask].sum() / count
    return densities

dens_phi = prime_density_by_phase(theta_phi, prime_mask)
dens_pi = prime_density_by_phase(theta_pi, prime_mask)
dens_sqrt2 = prime_density_by_phase(theta_sqrt2, prime_mask)
dens_e = prime_density_by_phase(theta_e, prime_mask)
dens_rand = prime_density_by_phase(theta_rand, prime_mask)

overall_density = prime_mask.sum() / len(prime_mask)

print(f"  Overall prime density: {overall_density:.4f}")
print()
print(f"  {'Constant':<12} {'Var(density)':>14} {'Max deviation':>14} {'Min density':>12} {'Max density':>12}")
print("  " + "-" * 70)

for name, dens in [("phi", dens_phi), ("pi", dens_pi), ("sqrt2", dens_sqrt2),
                    ("e", dens_e), ("random", dens_rand)]:
    var = np.var(dens)
    max_dev = np.max(np.abs(dens - overall_density))
    print(f"  {name:<12} {var:>14.6e} {max_dev:>14.6f} {np.min(dens):>12.4f} {np.max(dens):>12.4f}")

print()

# Permutation test: is phi's density variance exceptional?
n_perms = 1000
perm_vars = []
for _ in range(n_perms):
    theta_perm = (np.log(nums) * random.uniform(1.0, 4.0)) % (2 * PI)
    d = prime_density_by_phase(theta_perm, prime_mask)
    perm_vars.append(np.var(d))

perm_vars = np.array(perm_vars)
p_phi = np.mean(perm_vars >= np.var(dens_phi))
p_pi = np.mean(perm_vars >= np.var(dens_pi))

print(f"  Permutation test (random constants, n={n_perms}):")
print(f"    phi variance p-value: {p_phi:.4f}")
print(f"    pi variance p-value:  {p_pi:.4f}")
print(f"    Permutation mean var: {perm_vars.mean():.6e}")
print(f"    phi var:              {np.var(dens_phi):.6e}")
print(f"    pi var:               {np.var(dens_pi):.6e}")
print()

if p_phi > 0.05:
    print("  RESULT: phi phase shows NO significant prime clustering beyond random constants.")
else:
    print("  RESULT: phi phase shows significant prime clustering.")
print()

# ====================================================================
#  EXPERIMENT 4: TITAN RESONANCE SCORING
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 4: TITAN RESONANCE PRIME DETECTION")
print("=" * 70)
print()

def resonance_score(n, constant=PHI):
    theta = (np.log(n) * constant) % (2 * PI)
    delta = np.minimum(theta, 2*PI - theta)
    return 1.0 / (delta + 1e-9)

def titan_test(constant, sample_size=50000, top_k=500):
    """Score random numbers by resonance, check if top-scoring are more prime."""
    np.random.seed(42)
    candidates = np.random.randint(10**6, 10**7, size=sample_size)

    scores = resonance_score(candidates.astype(np.float64), constant)
    top_idx = np.argsort(scores)[-top_k:]
    rand_idx = np.random.choice(sample_size, top_k, replace=False)

    # Check primality (use sieve up to 10^7)
    big_sieve = sieve(10**7)

    top_primes = sum(big_sieve[candidates[i]] for i in top_idx)
    rand_primes = sum(big_sieve[candidates[i]] for i in rand_idx)

    return {
        "top_prime_count": top_primes,
        "random_prime_count": rand_primes,
        "top_rate": top_primes / top_k,
        "random_rate": rand_primes / top_k,
    }

print("  Testing resonance scoring with different constants:")
print(f"  Sample: {50000} random integers in [10^6, 10^7], top {500} by resonance score")
print()

for const_name, const_val in [("phi", PHI), ("pi", PI), ("sqrt2", SQRT2),
                               ("e", EULER), ("random", random.uniform(1.5, 3.5))]:
    t0 = time.time()
    result = titan_test(const_val, sample_size=50000, top_k=500)
    elapsed = time.time() - t0
    ratio = result["top_rate"] / max(result["random_rate"], 1e-10)
    print(f"  {const_name:<10} top_rate={result['top_rate']:.4f}  "
          f"rand_rate={result['random_rate']:.4f}  ratio={ratio:.2f}x  ({elapsed:.1f}s)")

print()

# ====================================================================
#  EXPERIMENT 5: DIRECT TEST OF R = m*phi^2 PREDICTION
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 5: GOLDEN PHASE RAY PRIME DENSITY")
print("=" * 70)
print()
print("  Prediction: prime density should be enhanced near theta = n*phi mod 2pi")
print("  By factor ~phi^2 = 2.618x")
print()

# Check density near golden phase rays
nums_test = np.arange(3, N, dtype=np.float64)
prime_test = is_prime[3:N]

# Golden phase for each number
theta_test = (np.log(nums_test) * PHI) % (2 * PI)

# Define "near golden ray" as within delta of 0 or pi (phase wraps)
delta_values = [0.01, 0.05, 0.1, 0.2]

print(f"  {'Delta':>7} {'Near ray density':>17} {'Away ray density':>18} {'Ratio':>7} {'p-value':>8}")
print("  " + "-" * 65)

for delta in delta_values:
    near_mask = np.minimum(theta_test, 2*PI - theta_test) < delta
    away_mask = ~near_mask

    near_density = prime_test[near_mask].sum() / max(near_mask.sum(), 1)
    away_density = prime_test[away_mask].sum() / max(away_mask.sum(), 1)
    ratio = near_density / max(away_density, 1e-10)

    # Binomial test
    from scipy.stats import fisher_exact
    table = np.array([
        [prime_test[near_mask].sum(), near_mask.sum() - prime_test[near_mask].sum()],
        [prime_test[away_mask].sum(), away_mask.sum() - prime_test[away_mask].sum()]
    ])
    _, p_val = fisher_exact(table)

    print(f"  {delta:>7.2f} {near_density:>17.4f} {away_density:>18.4f} {ratio:>7.3f} {p_val:>8.4f}")

print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Phase density comparison
ax = axes[0, 0]
bin_centers = np.linspace(0, 2*PI, 50)
for name, dens in [("phi", dens_phi), ("pi", dens_pi), ("sqrt2", dens_sqrt2), ("random", dens_rand)]:
    style = '-' if name == 'phi' else '--'
    lw = 2 if name == 'phi' else 1
    ax.plot(bin_centers, dens, style, linewidth=lw, label=name, alpha=0.7)
ax.axhline(y=overall_density, color='black', linestyle=':', label=f'Expected ({overall_density:.4f})')
ax.set_xlabel("Phase")
ax.set_ylabel("Prime density")
ax.set_title("Prime Density vs Phase (different constants)")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# Plot 2: 137 test bar chart
ax = axes[0, 1]
k_vals = sorted(targets)
k_freqs = [div_counts[k]/n_test_primes for k in k_vals]
k_expected = [1.0/k for k in k_vals]
x = np.arange(len(k_vals))
ax.bar(x - 0.2, k_freqs, 0.4, label='Observed', color='steelblue')
ax.bar(x + 0.2, k_expected, 0.4, label='Expected (1/k)', color='lightgray')
ax.set_xticks(x)
ax.set_xticklabels([str(k) for k in k_vals], rotation=45)
ax.set_ylabel("Divisibility frequency")
ax.set_title("137 Divisibility Test")
# Highlight 137
idx_137 = k_vals.index(137)
ax.bar(idx_137 - 0.2, k_freqs[idx_137], 0.4, color='red', alpha=0.5)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# Plot 3: Resonance score distribution
ax = axes[1, 0]
test_nums = np.random.randint(10**4, 10**5, size=10000)
scores_phi = resonance_score(test_nums.astype(np.float64), PHI)
scores_pi = resonance_score(test_nums.astype(np.float64), PI)
ax.hist(np.log10(scores_phi), bins=50, alpha=0.5, label='phi', color='gold')
ax.hist(np.log10(scores_pi), bins=50, alpha=0.5, label='pi', color='steelblue')
ax.set_xlabel("log10(Resonance score)")
ax.set_ylabel("Count")
ax.set_title("Resonance Score Distribution: phi vs pi")
ax.legend()
ax.grid(True, alpha=0.2)

# Plot 4: Golden phase ray density
ax = axes[1, 1]
deltas = np.linspace(0.005, 0.3, 30)
ratios = []
p_vals = []
for d in deltas:
    near = np.minimum(theta_test, 2*PI - theta_test) < d
    away = ~near
    nd = prime_test[near].sum() / max(near.sum(), 1)
    ad = prime_test[away].sum() / max(away.sum(), 1)
    ratios.append(nd / max(ad, 1e-10))
    table = np.array([
        [prime_test[near].sum(), near.sum() - prime_test[near].sum()],
        [prime_test[away].sum(), away.sum() - prime_test[away].sum()]
    ])
    _, p = fisher_exact(table)
    p_vals.append(p)

ax.plot(deltas, ratios, 'b-', linewidth=2)
ax.axhline(y=1.0, color='black', linestyle='--', label='No effect')
ax.axhline(y=2.618, color='red', linestyle='--', alpha=0.5, label='Predicted (phi^2)')
ax.fill_between(deltas, 1 - 0.05, 1 + 0.05, alpha=0.1, color='gray')
ax.set_xlabel("Delta (proximity to golden phase ray)")
ax.set_ylabel("Prime density ratio (near/away)")
ax.set_title("Golden Phase Ray Enhancement")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/011_phase_scan/golden_phase_results.png', dpi=150)
print("  Saved: golden_phase_results.png")

# ====================================================================
#  FINAL SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  FINAL SUMMARY")
print("=" * 70)
print()

print("  Experiment 1 (Phase Bake-off):")
if abs(phi_mean_ks - other_mean_ks) / max(other_mean_ks, 1e-10) < 0.1:
    print("    FAIL: phi is indistinguishable from other constants")
else:
    print("    PASS: phi shows different behavior")
print()

print("  Experiment 2 (137 Frequency):")
if p_val < 0.05:
    print("    PASS: 137 divides 36*p^2+1 more than expected")
else:
    print("    FAIL: 137 is not special among similar numbers")
print()

print("  Experiment 3 (Phase vs Primality):")
if p_phi > 0.05:
    print("    FAIL: Golden phase shows no prime clustering beyond random")
else:
    print("    PASS: Golden phase predicts primality")
print()

print("  Experiment 4 (TITAN Resonance):")
print("    (See ratio comparison above)")
print()

print("  Experiment 5 (Golden Phase Ray):")
if all(r < 1.05 for r in ratios):
    print("    FAIL: No enhancement near golden phase rays (ratio ~1.0)")
else:
    print("    PARTIAL: Some enhancement detected")
print()

print("  OVERALL: R = m*phi^2 theory predicts golden-ratio phase carries")
print("  signal about primes. Experiment 011 already showed NO phase transform")
print("  carries prime-specific signal. These tests are consistent with that finding.")

print()
print("Done.")
