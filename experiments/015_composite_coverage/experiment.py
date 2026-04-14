"""
Experiment 015: Composite Coverage vs Prime Survival
=====================================================
Tests whether the density of composite factorizations at a lattice
position k predicts whether 6k±1 is prime.

Coverage(k, sign) = number of non-trivial factorizations of 6k+sign
    = number of pairs (a, b) with a,b on 6k±1 lattice, a <= b, a >= 5, a*b = 6k+sign

Hypothesis: primes occur at positions with LOW ambient composite coverage.
Null: coverage is independent of primality (primes are just PNT-random).
"""

import numpy as np
from math import log, pi, sqrt
from scipy.stats import mannwhitneyu, pearsonr
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ====================================================================
#  FAST SIEVE
# ====================================================================
def sieve(N):
    is_prime = np.ones(N, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return is_prime

N_MAX = 200_000
print("=" * 70)
print("  EXPERIMENT 015: COMPOSITE COVERAGE vs PRIME SURVIVAL")
print("=" * 70)
print()

is_prime_arr = sieve(N_MAX + 10)

# ====================================================================
#  BUILD LATTICE
# ====================================================================
K_MAX = N_MAX // 6 + 1

# lattice numbers: all n = 6k±1 for k >= 1
# n in {5, 7, 11, 13, 17, 19, 23, 25, ...}
lattice_numbers = []  # sorted list of all 6k±1 numbers
for k in range(1, K_MAX + 1):
    for sign in (-1, +1):
        n = 6 * k + sign
        if n >= 5 and n <= N_MAX:
            lattice_numbers.append(n)

lattice_numbers = sorted(set(lattice_numbers))
lattice_set = set(lattice_numbers)

print(f"  Lattice numbers (6k±1, k>=1): {len(lattice_numbers)}")
print(f"  Primes on lattice: {sum(1 for n in lattice_numbers if is_prime_arr[n])}")
print()

# ====================================================================
#  COMPUTE COVERAGE
# ====================================================================
print("  Computing composite coverage (factorization counts)...")
t0 = time.time()

# coverage_minus[k] = number of lattice factorizations of 6k-1
# coverage_plus[k]  = number of lattice factorizations of 6k+1
coverage_minus = np.zeros(K_MAX + 1, dtype=np.int32)
coverage_plus = np.zeros(K_MAX + 1, dtype=np.int32)

# For each lattice number a, iterate over lattice numbers b >= a
# such that a*b <= N_MAX
for i, a in enumerate(lattice_numbers):
    if a * a > N_MAX:
        break
    for j in range(i, len(lattice_numbers)):
        b = lattice_numbers[j]
        n = a * b
        if n > N_MAX:
            break

        # Find k and sign: n = 6k + sign
        if n % 6 == 1:
            k = (n - 1) // 6
            coverage_plus[k] += 1
        elif n % 6 == 5:
            k = (n + 1) // 6
            coverage_minus[k] += 1

elapsed = time.time() - t0
print(f"  Done in {elapsed:.1f}s")
print()

# ====================================================================
#  BUILD ANALYSIS DATASET
# ====================================================================
# For each lattice point (k, sign), record:
#   - coverage (number of factorizations)
#   - is_prime
#   - k value (for density correction)

data = []  # list of (k, sign, coverage, is_prime, n)

for k in range(1, K_MAX + 1):
    for sign in (-1, +1):
        n = 6 * k + sign
        if n < 5 or n > N_MAX:
            continue

        cov = coverage_plus[k] if sign == +1 else coverage_minus[k]
        data.append({
            'k': k,
            'sign': sign,
            'n': n,
            'coverage': cov,
            'is_prime': is_prime_arr[n],
            'log_n': log(n),
        })

data = sorted(data, key=lambda d: d['k'])
ks = np.array([d['k'] for d in data])
coverages = np.array([d['coverage'] for d in data])
primes = np.array([d['is_prime'] for d in data])
log_ns = np.array([d['log_n'] for d in data])

print(f"  Total lattice points: {len(data)}")
print(f"  With coverage 0: {np.sum(coverages == 0)}")
print(f"  With coverage > 0: {np.sum(coverages > 0)}")
print()

# ====================================================================
#  TEST 1: COVERAGE DISTRIBUTION — PRIMES vs COMPOSITES
# ====================================================================
print("=" * 70)
print("  TEST 1: COVERAGE DISTRIBUTION (primes vs composites)")
print("=" * 70)
print()

prime_cov = coverages[primes]
comp_cov = coverages[~primes]

print(f"  Primes: coverage mean={prime_cov.mean():.2f}, median={np.median(prime_cov):.0f}")
print(f"  Comps:  coverage mean={comp_cov.mean():.2f}, median={np.median(comp_cov):.0f}")
print()

# Fraction with zero coverage
print(f"  Primes with coverage=0:  {np.sum(prime_cov == 0)}/{len(prime_cov)} "
      f"({np.mean(prime_cov == 0)*100:.1f}%)")
print(f"  Comps with coverage=0:   {np.sum(comp_cov == 0)}/{len(comp_cov)} "
      f"({np.mean(comp_cov == 0)*100:.1f}%)")
print()

# Mann-Whitney U test
U, p_mw = mannwhitneyu(prime_cov, comp_cov, alternative='less')
print(f"  Mann-Whitney U (primes < composites): U={U:.0f}, p={p_mw:.2e}")
print()

# ====================================================================
#  TEST 2: PRIME RATE BY COVERAGE LEVEL
# ====================================================================
print("=" * 70)
print("  TEST 2: PRIME RATE BY COVERAGE LEVEL")
print("=" * 70)
print()

print(f"  {'Coverage':>10} {'Count':>7} {'Primes':>7} {'Prime rate':>11} {'Expected (PNT)':>15}")
print("  " + "-" * 60)

for cov_level in sorted(set(coverages)):
    mask = coverages == cov_level
    count = mask.sum()
    prime_count = primes[mask].sum()
    rate = prime_count / count if count > 0 else 0
    # Expected PNT rate for these numbers
    expected = np.mean(2.0 / log_ns[mask]) if count > 0 else 0

    if count > 100:  # only show bins with enough data
        print(f"  {cov_level:>10} {count:>7} {prime_count:>7} {rate:>11.4f} {expected:>15.4f}")

print()

# ====================================================================
#  TEST 3: DENSITY-CORRECTED ANALYSIS
# ====================================================================
print("=" * 70)
print("  TEST 3: DENSITY-CORRECTED (residual prime rate vs coverage)")
print("=" * 70)
print()
print("  Remove PNT density effect, then check if coverage explains residuals.")
print()

# Bin by k (group similar-density numbers)
N_K_BINS = 50
k_bins = np.linspace(ks.min(), ks.max(), N_K_BINS + 1)
k_digitized = np.clip(np.digitize(ks, k_bins) - 1, 0, N_K_BINS - 1)

# For each k-bin, compute average coverage and residual prime rate
bin_coverage = np.zeros(N_K_BINS)
bin_prime_rate = np.zeros(N_K_BINS)
bin_expected_rate = np.zeros(N_K_BINS)
bin_count = np.zeros(N_K_BINS)

for i in range(N_K_BINS):
    mask = k_digitized == i
    count = mask.sum()
    bin_count[i] = count
    if count > 0:
        bin_coverage[i] = coverages[mask].mean()
        bin_prime_rate[i] = primes[mask].mean()
        bin_expected_rate[i] = np.mean(2.0 / log_ns[mask])

residual_rate = bin_prime_rate - bin_expected_rate

# Correlation between coverage and residual
valid = bin_count > 50
r_cov_resid, p_cov_resid = pearsonr(bin_coverage[valid], residual_rate[valid])

print(f"  Coverage vs residual prime rate: r={r_cov_resid:.4f}, p={p_cov_resid:.4f}")

if p_cov_resid < 0.05 and r_cov_resid < 0:
    print("  SIGNIFICANT: Higher coverage -> lower prime rate (beyond PNT)")
    print("  Composite sieving explains variance beyond density law.")
elif p_cov_resid < 0.05 and r_cov_resid > 0:
    print("  SIGNIFICANT but POSITIVE: Higher coverage -> higher prime rate??")
    print("  This is likely an artifact (coverage correlates with k).")
else:
    print("  NOT significant: Coverage adds nothing beyond the PNT density law.")

print()

# ====================================================================
#  TEST 4: PERMUTATION TEST
# ====================================================================
print("=" * 70)
print("  TEST 4: PERMUTATION TEST (shuffle within k-neighborhoods)")
print("=" * 70)
print()

# Within each k-bin, shuffle prime labels and recompute coverage-rate correlation
n_perms = 1000
perm_rs = []

for _ in range(n_perms):
    perm_primes = primes.copy()
    # Shuffle within k-bins
    for i in range(N_K_BINS):
        mask = k_digitized == i
        idx = np.where(mask)[0]
        if len(idx) > 1:
            perm_primes[idx] = np.random.permutation(perm_primes[idx])

    # Recompute residual rates
    perm_resid = np.zeros(N_K_BINS)
    for i in range(N_K_BINS):
        mask = k_digitized == i
        if bin_count[i] > 0:
            perm_resid[i] = perm_primes[mask].mean() - bin_expected_rate[i]

    r_perm, _ = pearsonr(bin_coverage[valid], perm_resid[valid])
    perm_rs.append(r_perm)

perm_rs = np.array(perm_rs)
p_perm = np.mean(perm_rs <= r_cov_resid) if r_cov_resid < 0 else np.mean(perm_rs >= r_cov_resid)
z_perm = (r_cov_resid - perm_rs.mean()) / max(perm_rs.std(), 1e-9)

print(f"  Observed r: {r_cov_resid:.4f}")
print(f"  Permutation mean r: {perm_rs.mean():.4f}")
print(f"  z-score: {z_perm:+.3f}")
print(f"  p-value: {p_perm:.4f}")

if p_perm < 0.05:
    print("  SIGNIFICANT after permutation correction.")
else:
    print("  NOT significant after permutation correction.")

print()

# ====================================================================
#  TEST 5: LOCAL SUPPRESSION ZONES
# ====================================================================
print("=" * 70)
print("  TEST 5: LOCAL SUPPRESSION (coverage at k predicts primality at k±1)")
print("=" * 70)
print()
print("  Does high coverage at position k suppress primes at neighboring k?")
print()

# For each k, compute average coverage of neighbors and check prime rate
neighbor_cov = np.zeros(len(data))
for idx in range(len(data)):
    k = data[idx]['k']
    # Average coverage of positions k-2 to k+2 (excluding self)
    neighbor_indices = [j for j in range(len(data))
                        if abs(data[j]['k'] - k) <= 2 and data[j]['k'] != k]
    if neighbor_indices:
        neighbor_cov[idx] = np.mean([coverages[j] for j in neighbor_indices])

# Split into high/low neighbor coverage
median_ncov = np.median(neighbor_cov[neighbor_cov > 0])
high_ncov_mask = neighbor_cov >= median_ncov
low_ncov_mask = neighbor_cov < median_ncov

high_prime_rate = primes[high_ncov_mask].mean()
low_prime_rate = primes[low_ncov_mask].mean()

print(f"  Median neighbor coverage: {median_ncov:.2f}")
print(f"  Prime rate (low neighbor cov):  {low_prime_rate:.4f}")
print(f"  Prime rate (high neighbor cov): {high_prime_rate:.4f}")
print(f"  Ratio: {low_prime_rate / max(high_prime_rate, 1e-10):.3f}")
print()

# After PNT correction
high_expected = np.mean(2.0 / log_ns[high_ncov_mask])
low_expected = np.mean(2.0 / log_ns[low_ncov_mask])
print(f"  Expected (PNT) low cov:  {low_expected:.4f}")
print(f"  Expected (PNT) high cov: {high_expected:.4f}")
print(f"  After correction: low={low_prime_rate - low_expected:+.4f}, high={high_prime_rate - high_expected:+.4f}")
print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Prime rate vs coverage
ax = axes[0, 0]
cov_levels = sorted(set(coverages))
rates = []
counts_list = []
for cl in cov_levels:
    mask = coverages == cl
    count = mask.sum()
    if count > 50:
        rates.append(primes[mask].mean())
        counts_list.append(count)
    else:
        rates.append(np.nan)
        counts_list.append(count)

ax.bar(range(len(cov_levels)), rates, color='steelblue', alpha=0.7)
ax.set_xticks(range(len(cov_levels)))
ax.set_xticklabels([str(c) for c in cov_levels], fontsize=8)
ax.set_xlabel("Coverage (number of factorizations)")
ax.set_ylabel("Prime rate")
ax.set_title("Prime Rate by Composite Coverage Level")
ax.axhline(y=primes.mean(), color='red', linestyle='--', label=f'Overall ({primes.mean():.3f})')
ax.legend()
ax.grid(True, alpha=0.2, axis='y')

# Plot 2: Coverage vs k
ax = axes[0, 1]
k_vals = np.array([d['k'] for d in data])
# Average coverage per k
unique_ks = sorted(set(k_vals))
avg_cov_by_k = [coverages[k_vals == k].mean() for k in unique_ks]
ax.plot(unique_ks, avg_cov_by_k, 'b-', linewidth=0.5, alpha=0.5)
# Smoothed
from scipy.ndimage import uniform_filter1d
smoothed = uniform_filter1d(np.array(avg_cov_by_k, dtype=float), size=50)
ax.plot(unique_ks, smoothed, 'r-', linewidth=2, label='Smoothed')
ax.set_xlabel("k")
ax.set_ylabel("Average coverage")
ax.set_title("Composite Coverage vs Position k")
ax.legend()
ax.grid(True, alpha=0.2)

# Plot 3: Residual prime rate vs coverage
ax = axes[1, 0]
ax.scatter(bin_coverage[valid], residual_rate[valid], s=20, alpha=0.5, color='steelblue')
ax.axhline(y=0, color='black', linewidth=0.5)
ax.set_xlabel("Average coverage (per k-bin)")
ax.set_ylabel("Residual prime rate (observed - PNT)")
ax.set_title(f"Density-Corrected: Coverage vs Residual (r={r_cov_resid:.3f}, p={p_cov_resid:.3f})")
ax.grid(True, alpha=0.2)

# Plot 4: Permutation distribution
ax = axes[1, 1]
ax.hist(perm_rs, bins=50, color='lightgray', alpha=0.7, label='Permuted')
ax.axvline(x=r_cov_resid, color='red', linewidth=2, linestyle='--',
           label=f'Observed r={r_cov_resid:.3f}')
ax.axvline(x=perm_rs.mean(), color='black', linewidth=1, linestyle=':',
           label=f'Null mean={perm_rs.mean():.3f}')
ax.set_xlabel("Correlation (coverage vs residual prime rate)")
ax.set_ylabel("Count")
ax.set_title("Permutation Test")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/015_composite_coverage/results.png', dpi=150)
print("  Saved: results.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()

print(f"  Primes have coverage=0: {np.mean(prime_cov == 0)*100:.1f}%")
print(f"  Comps have coverage=0:  {np.mean(comp_cov == 0)*100:.1f}%")
print()

if p_perm < 0.05 and r_cov_resid < 0:
    print("  RESULT: Composite coverage SIGNIFICANTLY predicts prime locations")
    print("  beyond what the PNT density law explains.")
    print("  Primes survive in low-coverage (low-sieve-pressure) zones.")
    print("  This is the Sieve of Eratosthenes showing spatial structure.")
elif abs(r_cov_resid) < 0.1 and p_perm > 0.1:
    print("  RESULT: Composite coverage does NOT predict prime locations")
    print("  beyond the PNT density law. Coverage correlates with k (position),")
    print("  which already encodes the density. No spatial structure in the sieve.")
else:
    print(f"  RESULT: Marginal signal (r={r_cov_resid:.3f}, p={p_perm:.4f}).")
    print("  Coverage may carry weak spatial information, but it's mostly")
    print("  explained by the density gradient (coverage increases with k).")

print()
print("Done.")
