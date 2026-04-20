"""
Experiment 018: Factor Ratios on the 6k±1 Manifold
====================================================
Instead of testing whether the manifold can detect primality (experiments 1-17),
we test whether composites carry recoverable information about their prime
factor composition in the Signed Wheel phase structure, respecting the Z2 rail
group.

Key insight: Field's nominalism uses comparative relations, not absolute values.
The ratios between a composite and its prime factors are the comparative structure.
On the 6k±1 manifold, multiplication composes rails via Z2:
  Rail1 x Rail1 -> Rail2   (-1 x -1 = +1)
  Rail2 x Rail2 -> Rail2   (+1 x +1 = +1)
  Rail1 x Rail2 -> Rail1   (-1 x +1 = -1)

And in Signed Wheel space:
  tau(N) = tau(p1) + tau(p2)         (radial: additive)
  theta(N) = 2pi((tau(p1)+tau(p2)) mod 1)  (phase: modular interference)
  sigma(N) = sigma(p1) * sigma(p2)   (rail: Z2 group)

Tests:
1. Phase decomposition: does theta(N) carry information about which primes
   composed it?
2. Rail fingerprinting: do composites from different factor-rail combos
   have different phase distributions?
3. Factor phase recovery: is there structure in theta(N) - theta(p)?
4. Ratio clustering: do the ratios N/p (for prime factors p) cluster
   in angle space?
"""

import numpy as np
from math import log, pi, sqrt
from scipy.stats import mannwhitneyu, pearsonr, ks_2samp, ttest_ind
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ====================================================================
#  SIEVE AND HELPERS
# ====================================================================
def sieve(N):
    is_prime = np.ones(N, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return is_prime

def smallest_prime_factor(n, spf_table):
    return spf_table[n]

def factorize(n, spf_table):
    """Return list of prime factors (with repetition)."""
    factors = []
    while n > 1:
        p = spf_table[n]
        factors.append(p)
        n //= p
    return factors

def get_rail(n):
    """Return which 6k±1 rail a number sits on.
    Returns: +1 for Rail2 (6k+1), -1 for Rail1 (6k-1), 0 for multiples of 2/3."""
    if n % 2 == 0 or n % 3 == 0:
        return 0
    r = n % 6
    if r == 1:
        return 1  # Rail 2 (6k+1)
    elif r == 5:
        return -1  # Rail 1 (6k-1)
    return 0

def signed_wheel(n):
    """Compute Signed Wheel (theta, tau, sigma) for n."""
    tau = log(n)
    theta = 2 * pi * (tau % 1.0)
    sigma = get_rail(n)
    return theta, tau, sigma

def rail_k(n):
    """Return the k-index for n on its rail: n = 6k + sigma.
    Rail1 (6k-1): k = (n+1)/6
    Rail2 (6k+1): k = (n-1)/6
    """
    rail = get_rail(n)
    if rail == -1:
        return (n + 1) // 6
    elif rail == +1:
        return (n - 1) // 6
    return 0

def build_unit_index(N_MAX):
    """Build unit index: sequential position within each rail.

    Rail1 (6k-1): 5, 11, 17, 23, 29, 35, ...
      unit_index_r1[n] = sequential position of n in Rail1 sequence
      e.g., unit_index_r1[5]=1, unit_index_r1[11]=2, unit_index_r1[17]=3, ...

    Rail2 (6k+1): 7, 13, 19, 25, 31, 37, ...
      unit_index_r2[n] = sequential position of n in Rail2 sequence
      e.g., unit_index_r2[7]=1, unit_index_r2[13]=2, unit_index_r2[19]=3, ...

    Also build prime-only unit indices:
      prime_unit_r1[n] = position among RAIL1 PRIMES only
      prime_unit_r2[n] = position among RAIL2 PRIMES only
    """
    unit_r1 = np.zeros(N_MAX + 10, dtype=np.int32)  # index within full Rail1
    unit_r2 = np.zeros(N_MAX + 10, dtype=np.int32)  # index within full Rail2
    prime_r1 = np.zeros(N_MAX + 10, dtype=np.int32)  # index among Rail1 primes
    prime_r2 = np.zeros(N_MAX + 10, dtype=np.int32)  # index among Rail2 primes

    idx_r1 = 0
    idx_r2 = 0
    pidx_r1 = 0
    pidx_r2 = 0

    is_prime_arr = sieve(N_MAX + 10)

    for k in range(1, N_MAX // 6 + 2):
        n1 = 6 * k - 1  # Rail1
        n2 = 6 * k + 1  # Rail2

        if n1 <= N_MAX:
            idx_r1 += 1
            unit_r1[n1] = idx_r1
            if is_prime_arr[n1]:
                pidx_r1 += 1
                prime_r1[n1] = pidx_r1

        if n2 <= N_MAX:
            idx_r2 += 1
            unit_r2[n2] = idx_r2
            if is_prime_arr[n2]:
                pidx_r2 += 1
                prime_r2[n2] = pidx_r2

    return unit_r1, unit_r2, prime_r1, prime_r2, is_prime_arr

# ====================================================================
#  MAIN
# ====================================================================
N_MAX = 100_000

print("=" * 70)
print("  EXPERIMENT 018: FACTOR RATIOS ON THE 6k±1 MANIFOLD")
print("  (with Unit Index Tests)")
print("=" * 70)
print()

# Build sieve, factor tables, and unit indices
print("  Building sieve, factor tables, and unit indices...")
t0 = time.time()

# Build unit indices (this also builds the sieve internally)
unit_r1, unit_r2, prime_r1, prime_r2, is_prime_arr = build_unit_index(N_MAX + 10)

# Build smallest prime factor table
spf = np.zeros(N_MAX + 10, dtype=np.int32)
for i in range(2, N_MAX + 10):
    if is_prime_arr[i]:
        spf[i::i] = np.where(spf[i::i] == 0, i, spf[i::i])
spf[0] = 0
spf[1] = 0

elapsed = time.time() - t0
print(f"  Done in {elapsed:.1f}s")
print()

def get_unit_index(n):
    """Return the within-rail unit index for n."""
    rail = get_rail(n)
    if rail == -1:
        return unit_r1[n]
    elif rail == +1:
        return unit_r2[n]
    return 0

def get_prime_unit_index(n):
    """Return the within-rail PRIME-ONLY unit index for n."""
    rail = get_rail(n)
    if rail == -1:
        return prime_r1[n]
    elif rail == +1:
        return prime_r2[n]
    return 0

# ====================================================================
#  BUILD COMPOSITE DATASET
# ====================================================================
# Collect composites on the 6k±1 rails (coprime to 6) with their factors
print("  Building composite dataset on 6k±1 rails...")

composites = []  # list of dicts

for n in range(5, N_MAX + 1):
    if n % 2 == 0 or n % 3 == 0:
        continue  # skip multiples of 2 and 3
    if is_prime_arr[n]:
        continue  # skip primes

    factors = factorize(n, spf)
    rail = get_rail(n)

    # Classify factorization type by rail composition
    rail1_factors = sum(1 for p in factors if get_rail(p) == -1)
    rail2_factors = sum(1 for p in factors if get_rail(p) == +1)
    # Note: factors of 2 and 3 are rail 0, we count them but they don't
    # affect rail parity (2,3 are special)
    rail0_factors = sum(1 for p in factors if get_rail(p) == 0)

    # Compute Signed Wheel for composite
    theta_n, tau_n, sigma_n = signed_wheel(n)

    # Compute factor ratios and their wheel positions
    factor_ratios = []
    for p in set(factors):
        ratio = n / p
        if ratio >= 5 and ratio <= N_MAX:  # keep in range
            theta_r, tau_r, sigma_r = signed_wheel(ratio)
            # Phase step from factor to composite
            d_theta = min(abs(theta_n - theta_r), 2*pi - abs(theta_n - theta_r))
            d_tau = tau_n - tau_r  # should equal tau(p) since log(n/p) = log(n) - log(p)
            factor_ratios.append({
                'factor': p,
                'ratio': ratio,
                'theta_ratio': theta_r,
                'tau_ratio': tau_r,
                'sigma_ratio': sigma_r,
                'd_theta': d_theta,
                'd_tau': d_tau,
                'factor_rail': get_rail(p),
            })

    composites.append({
        'n': n,
        'factors': factors,
        'unique_factors': list(set(factors)),
        'n_factors': len(factors),
        'n_unique': len(set(factors)),
        'rail': rail,
        'rail1_count': rail1_factors,
        'rail2_count': rail2_factors,
        'rail0_count': rail0_factors,
        'theta': theta_n,
        'tau': tau_n,
        'sigma': sigma_n,
        'factor_ratios': factor_ratios,
        'unit_idx': get_unit_index(n),
        'k_idx': rail_k(n),
    })

print(f"  Total composites on 6k±1 rails: {len(composites)}")
print()

# ====================================================================
#  TEST 1: RAIL FINGERPRINTING
# ====================================================================
print("=" * 70)
print("  TEST 1: RAIL FINGERPRINTING")
print("=" * 70)
print()
print("  Does the phase distribution differ by factor-rail composition?")
print("  Rail parity rule: composite rail = product of factor rails (Z2)")
print()

# Group composites by their rail-factor composition
# Focus on semiprimes (2 prime factors, both > 3) for clean groups
semiprimes_r1r1 = [c for c in composites if c['n_unique'] == 2 and c['n_factors'] == 2
                    and c['rail1_count'] == 2 and c['rail0_count'] == 0]  # Rail1 x Rail1 -> Rail2
semiprimes_r2r2 = [c for c in composites if c['n_unique'] == 2 and c['n_factors'] == 2
                    and c['rail2_count'] == 2 and c['rail0_count'] == 0]  # Rail2 x Rail2 -> Rail2
semiprimes_r1r2 = [c for c in composites if c['n_unique'] == 2 and c['n_factors'] == 2
                    and c['rail1_count'] == 1 and c['rail2_count'] == 1 and c['rail0_count'] == 0]  # Rail1 x Rail2 -> Rail1

print(f"  Semiprimes Rail1 x Rail1 -> Rail2: {len(semiprimes_r1r1)}")
print(f"  Semiprimes Rail2 x Rail2 -> Rail2: {len(semiprimes_r2r2)}")
print(f"  Semiprimes Rail1 x Rail2 -> Rail1: {len(semiprimes_r1r2)}")
print()

# Compare phase distributions between groups
if len(semiprimes_r1r1) > 50 and len(semiprimes_r2r2) > 50:
    theta_r1r1 = np.array([c['theta'] for c in semiprimes_r1r1])
    theta_r2r2 = np.array([c['theta'] for c in semiprimes_r2r2])

    # KS test on phase distributions
    ks_stat, ks_p = ks_2samp(theta_r1r1, theta_r2r2)
    print(f"  Rail1x1 vs Rail2x2 phase distributions:")
    print(f"    KS statistic: {ks_stat:.4f}, p={ks_p:.4e}")

    # Also compare means (circular mean)
    def circular_mean(angles):
        return np.arctan2(np.mean(np.sin(angles)), np.mean(np.cos(angles)))

    def circular_std(angles):
        R = sqrt(np.mean(np.cos(angles))**2 + np.mean(np.sin(angles))**2)
        return sqrt(-2 * log(max(R, 1e-10)))

    mean_r1r1 = circular_mean(theta_r1r1)
    mean_r2r2 = circular_mean(theta_r2r2)
    std_r1r1 = circular_std(theta_r1r1)
    std_r2r2 = circular_std(theta_r2r2)

    print(f"    Circular mean Rail1x1: {np.degrees(mean_r1r1):.1f} deg (std: {np.degrees(std_r1r1):.1f})")
    print(f"    Circular mean Rail2x2: {np.degrees(mean_r2r2):.1f} deg (std: {np.degrees(std_r2r2):.1f})")
    print()

if len(semiprimes_r1r2) > 50:
    theta_r1r2 = np.array([c['theta'] for c in semiprimes_r1r2])

    # Compare R1xR2 (lands on Rail1) with R1xR1 (lands on Rail2)
    if len(semiprimes_r1r1) > 50:
        ks2, p2 = ks_2samp(theta_r1r1, theta_r1r2)
        print(f"  Rail1x1 (Rail2) vs Rail1x2 (Rail1) phase:")
        print(f"    KS statistic: {ks2:.4f}, p={p2:.4e}")

    mean_r1r2 = circular_mean(theta_r1r2)
    std_r1r2 = circular_std(theta_r1r2)
    print(f"    Circular mean Rail1x2: {np.degrees(mean_r1r2):.1f} deg (std: {np.degrees(std_r1r2):.1f})")
    print()

# ====================================================================
#  TEST 2: FACTOR PHASE RECOVERY
# ====================================================================
print("=" * 70)
print("  TEST 2: FACTOR PHASE RECOVERY")
print("=" * 70)
print()
print("  For each composite N = p1 x p2, compute phase difference")
print("  theta(N) - theta(p) for each factor p. Is there structure?")
print()

# Collect phase deltas for semiprimes
phase_deltas_r1 = []  # deltas from Rail1 factors
phase_deltas_r2 = []  # deltas from Rail2 factors

for c in composites:
    if c['n_factors'] != 2 or c['n_unique'] != 2 or c['rail0_count'] > 0:
        continue

    for fr in c['factor_ratios']:
        delta = fr['d_theta']  # angular distance between composite and its ratio
        if fr['factor_rail'] == -1:
            phase_deltas_r1.append(delta)
        elif fr['factor_rail'] == +1:
            phase_deltas_r2.append(delta)

phase_deltas_r1 = np.array(phase_deltas_r1)
phase_deltas_r2 = np.array(phase_deltas_r2)

print(f"  Phase deltas from Rail1 factors: {len(phase_deltas_r1)}")
print(f"  Phase deltas from Rail2 factors: {len(phase_deltas_r2)}")
print()

if len(phase_deltas_r1) > 100 and len(phase_deltas_r2) > 100:
    print(f"  Rail1 factor deltas: mean={np.degrees(np.mean(phase_deltas_r1)):.1f} deg, "
          f"std={np.degrees(np.std(phase_deltas_r1)):.1f} deg")
    print(f"  Rail2 factor deltas: mean={np.degrees(np.mean(phase_deltas_r2)):.1f} deg, "
          f"std={np.degrees(np.std(phase_deltas_r2)):.1f} deg")

    ks_delta, p_delta = ks_2samp(phase_deltas_r1, phase_deltas_r2)
    print(f"  KS test (Rail1 vs Rail2 deltas): stat={ks_delta:.4f}, p={p_delta:.4e}")

    # Compare with random: pick random primes and compute delta to composite
    all_rail_primes = [p for p in range(5, N_MAX) if is_prime_arr[p] and get_rail(p) != 0]
    random_deltas = []
    for c in composites[:2000]:
        if c['n_factors'] != 2:
            continue
        # Pick a random prime that's NOT a factor
        attempts = 0
        while attempts < 20:
            rp = all_rail_primes[np.random.randint(len(all_rail_primes))]
            if rp not in c['unique_factors']:
                theta_rp = 2 * pi * (log(rp) % 1.0)
                d = min(abs(c['theta'] - theta_rp), 2*pi - abs(c['theta'] - theta_rp))
                random_deltas.append(d)
                break
            attempts += 1

    random_deltas = np.array(random_deltas)
    all_real_deltas = np.concatenate([phase_deltas_r1, phase_deltas_r2])

    print()
    print(f"  Random (non-factor) deltas: mean={np.degrees(np.mean(random_deltas)):.1f} deg, "
          f"std={np.degrees(np.std(random_deltas)):.1f} deg")
    print(f"  Real (factor) deltas:       mean={np.degrees(np.mean(all_real_deltas)):.1f} deg, "
          f"std={np.degrees(np.std(all_real_deltas)):.1f} deg")

    ks_real_vs_random, p_real_vs_random = ks_2samp(all_real_deltas, random_deltas)
    print(f"  KS test (real factors vs random): stat={ks_real_vs_random:.4f}, p={p_real_vs_random:.4e}")
print()

# ====================================================================
#  TEST 3: RATIO CLUSTERING IN ANGLE SPACE
# ====================================================================
print("=" * 70)
print("  TEST 3: RATIO CLUSTERING IN ANGLE SPACE")
print("=" * 70)
print()
print("  For composites N = p1 x p2, the ratio N/p1 = p2 and N/p2 = p1.")
print("  Do these ratios (which ARE the co-factors) cluster differently")
print("  based on factor-rail composition?")
print()

# For each semiprime, compute the angle of the ratio N/p for each factor
ratio_angles_by_type = {
    'R1_from_R1xR1': [],  # ratio = Rail2 prime, from Rail1xRail1 composite (on Rail2)
    'R1_from_R1xR2': [],  # ratio = Rail1 prime, from Rail1xRail2 composite (on Rail1)
    'R2_from_R1xR1': [],  # ratio = Rail1 prime, from Rail1xRail1 composite (on Rail2)
    'R2_from_R1xR2': [],  # ratio = Rail2 prime, from Rail1xRail2 composite (on Rail1)
    'R2_from_R2xR2': [],  # ratio = Rail2 prime, from Rail2xRail2 composite (on Rail2)
}

for c in composites:
    if c['n_factors'] != 2 or c['n_unique'] != 2 or c['rail0_count'] > 0:
        continue

    for fr in c['factor_ratios']:
        # ratio = N/p, which is the co-factor
        angle = fr['theta_ratio']
        factor_rail = fr['factor_rail']
        ratio_rail = fr['sigma_ratio']

        if c['rail1_count'] == 2:  # Rail1 x Rail1 -> Rail2 composite
            if factor_rail == -1:
                ratio_angles_by_type['R2_from_R1xR1'].append(angle)
        elif c['rail1_count'] == 1 and c['rail2_count'] == 1:  # Rail1 x Rail2 -> Rail1
            if factor_rail == -1:
                ratio_angles_by_type['R1_from_R1xR2'].append(angle)
            elif factor_rail == +1:
                ratio_angles_by_type['R2_from_R1xR2'].append(angle)
        elif c['rail2_count'] == 2:  # Rail2 x Rail2 -> Rail2
            if factor_rail == +1:
                ratio_angles_by_type['R2_from_R2xR2'].append(angle)

for k, v in ratio_angles_by_type.items():
    print(f"  {k}: {len(v)} ratio angles")
print()

# Compare angle distributions of ratios that ARE primes vs the factors themselves
# The key test: do ratios from different composition types have different angular distributions?
pairs_to_test = [
    ('R2_from_R1xR1', 'R2_from_R2xR2', 'Rail2 ratio: R1xR1 source vs R2xR2 source'),
    ('R1_from_R1xR2', 'R2_from_R1xR2', 'Rail1 ratio vs Rail2 ratio from same R1xR2 type'),
]

for key1, key2, label in pairs_to_test:
    a1 = np.array(ratio_angles_by_type[key1])
    a2 = np.array(ratio_angles_by_type[key2])
    if len(a1) > 50 and len(a2) > 50:
        ks, p = ks_2samp(a1, a2)
        print(f"  {label}:")
        print(f"    KS={ks:.4f}, p={p:.4e} (n1={len(a1)}, n2={len(a2)})")
print()

# ====================================================================
#  TEST 4: RAIL PARITY AND PHASE STRUCTURE
# ====================================================================
print("=" * 70)
print("  TEST 4: RAIL PARITY AND PHASE STRUCTURE")
print("=" * 70)
print()
print("  Composites on Rail1 have odd number of Rail1 factors.")
print("  Composites on Rail2 have even number of Rail1 factors (0, 2, 4...).")
print("  Does phase distinguish between 0, 1, 2 Rail1 factors?")
print()

# Group by number of Rail1 factors (excluding 2,3 factors)
by_rail1_count = {}
for c in composites:
    if c['rail0_count'] > 0:
        continue  # only pure rail-rail compositions
    r1 = c['rail1_count']
    if r1 not in by_rail1_count:
        by_rail1_count[r1] = []
    by_rail1_count[r1].append(c['theta'])

print(f"  {'Rail1 factors':>14} {'Count':>8} {'Mean phase (deg)':>17} {'Std (deg)':>10}")
print("  " + "-" * 55)
for r1_count in sorted(by_rail1_count.keys()):
    angles = np.array(by_rail1_count[r1_count])
    if len(angles) > 50:
        mean = np.degrees(circular_mean(angles))
        std = np.degrees(circular_std(angles))
        print(f"  {r1_count:>14} {len(angles):>8} {mean:>17.1f} {std:>10.1f}")

print()

# Pairwise KS tests between rail1-count groups
groups = [(k, np.array(v)) for k, v in sorted(by_rail1_count.items()) if len(v) > 100]
print("  Pairwise KS tests on phase distributions:")
for i in range(len(groups)):
    for j in range(i+1, len(groups)):
        k1, a1 = groups[i]
        k2, a2 = groups[j]
        ks, p = ks_2samp(a1, a2)
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"    {k1} vs {k2} Rail1 factors: KS={ks:.4f}, p={p:.4e} {sig}")
print()

# ====================================================================
#  TEST 5: CLOSE vs DISTANT FACTOR RATIOS
# ====================================================================
print("=" * 70)
print("  TEST 5: CLOSE vs DISTANT FACTOR RATIOS")
print("=" * 70)
print()
print("  Composites of close primes (e.g., 11x13=143) vs distant primes")
print("  (e.g., 5x97=485). Does the manifold see the difference?")
print()

close_ratios = []   # ratio close to 1 (factors similar size)
distant_ratios = []  # ratio far from 1 (factors very different size)

for c in composites:
    if c['n_factors'] != 2 or c['n_unique'] != 2 or c['rail0_count'] > 0:
        continue

    p1, p2 = sorted(c['unique_factors'])
    ratio = p2 / p1  # >= 1.0

    # Phase of the composite
    theta_n = c['theta']

    # "Close" = ratio < 2, "distant" = ratio > 5
    if ratio < 2.0:
        close_ratios.append({'theta': theta_n, 'tau': c['tau'], 'ratio': ratio, 'n': c['n']})
    elif ratio > 5.0:
        distant_ratios.append({'theta': theta_n, 'tau': c['tau'], 'ratio': ratio, 'n': c['n']})

print(f"  Close factor pairs (ratio < 2): {len(close_ratios)}")
print(f"  Distant factor pairs (ratio > 5): {len(distant_ratios)}")

if len(close_ratios) > 100 and len(distant_ratios) > 100:
    theta_close = np.array([r['theta'] for r in close_ratios])
    theta_distant = np.array([r['theta'] for r in distant_ratios])

    ks_cd, p_cd = ks_2samp(theta_close, theta_distant)
    print(f"  Phase distribution KS test: stat={ks_cd:.4f}, p={p_cd:.4e}")

    mean_close = np.degrees(circular_mean(theta_close))
    mean_distant = np.degrees(circular_mean(theta_distant))
    std_close = np.degrees(circular_std(theta_close))
    std_distant = np.degrees(circular_std(theta_distant))

    print(f"  Close:  mean={mean_close:.1f} deg, std={std_close:.1f} deg")
    print(f"  Distant: mean={mean_distant:.1f} deg, std={std_distant:.1f} deg")

    # Control: tau distribution (should differ since distant = larger composites)
    tau_close = np.array([r['tau'] for r in close_ratios])
    tau_distant = np.array([r['tau'] for r in distant_ratios])
    print()
    print(f"  [Control] tau distribution:")
    print(f"    Close:  mean tau={np.mean(tau_close):.2f}")
    print(f"    Distant: mean tau={np.mean(tau_distant):.2f}")

    # Match by tau: only compare composites with similar magnitude
    tau_min = max(np.percentile(tau_close, 25), np.percentile(tau_distant, 25))
    tau_max = min(np.percentile(tau_close, 75), np.percentile(tau_distant, 75))

    matched_close = np.array([r['theta'] for r in close_ratios if tau_min <= r['tau'] <= tau_max])
    matched_distant = np.array([r['theta'] for r in distant_ratios if tau_min <= r['tau'] <= tau_max])

    if len(matched_close) > 50 and len(matched_distant) > 50:
        ks_m, p_m = ks_2samp(matched_close, matched_distant)
        print(f"  Magnitude-matched KS: stat={ks_m:.4f}, p={p_m:.4e} "
              f"(n_close={len(matched_close)}, n_distant={len(matched_distant)})")

print()

# ====================================================================
#  TEST 6: Z2 GROUP VERIFICATION
# ====================================================================
print("=" * 70)
print("  TEST 6: Z2 RAIL GROUP VERIFICATION")
print("=" * 70)
print()
print("  Verify that multiplication on the 6k±1 rails forms Z2.")
print("  Test: for every composite, sigma(N) = product of sigma(factors).")
print()

violations = 0
total_checked = 0
for c in composites:
    if c['rail0_count'] > 0:
        continue
    total_checked += 1
    # Compute expected rail from factor rails
    expected_sigma = 1
    for p in c['factors']:
        expected_sigma *= get_rail(p)
    if c['rail'] != expected_sigma:
        violations += 1

print(f"  Checked: {total_checked} composites (pure rail-rail)")
print(f"  Z2 violations: {violations}/{total_checked} "
      f"({100*violations/max(total_checked,1):.4f}%)")
if violations == 0:
    print("  PERFECT: Rail composition follows Z2 group law exactly.")
print()

# ====================================================================
#  TEST 7: UNIT INDEX RATIOS ON THE RAILS
# ====================================================================
print("=" * 70)
print("  TEST 7: UNIT INDEX RATIOS ON THE RAILS")
print("=" * 70)
print()
print("  Instead of raw numbers, use WITHIN-RAIL sequential positions.")
print("  Each number on a rail has a unit_index = its position in that rail's")
print("  sequence. The unit index ratio of a composite to its factor gives")
print("  a pure rail-topological relationship, stripped of magnitude.")
print()
print("  For N = p1 x p2 (both on rails):")
print("    k_N = rail position of N on its rail")
print("    k_p1 = rail position of p1 on its rail")
print("    k_p2 = rail position of p2 on its rail")
print("    unit_ratio_1 = k_N / k_p1  (how far the composite is vs its factor)")
print("    unit_ratio_2 = k_N / k_p2")
print()

# Collect unit index data for semiprimes
unit_data = []  # list of dicts with unit index info

for c in composites:
    if c['n_factors'] != 2 or c['n_unique'] != 2 or c['rail0_count'] > 0:
        continue

    p1, p2 = sorted(c['unique_factors'])
    k_n = c['unit_idx']  # composite's position on its rail
    k_p1 = get_unit_index(p1)  # factor1's position on its rail
    k_p2 = get_unit_index(p2)  # factor2's position on its rail

    # Prime-only indices
    pk_n = get_prime_unit_index(c['n']) if not is_prime_arr[c['n']] else 0
    pk_p1 = get_prime_unit_index(p1)
    pk_p2 = get_prime_unit_index(p2)

    # k-index (the k in 6k±1)
    kk_n = c['k_idx']
    kk_p1 = rail_k(p1)
    kk_p2 = rail_k(p2)

    if k_p1 == 0 or k_p2 == 0 or k_n == 0:
        continue

    unit_data.append({
        'n': c['n'],
        'p1': p1, 'p2': p2,
        'rail_n': c['rail'],
        'rail_p1': get_rail(p1),
        'rail_p2': get_rail(p2),
        'k_n': k_n, 'k_p1': k_p1, 'k_p2': k_p2,
        'kk_n': kk_n, 'kk_p1': kk_p1, 'kk_p2': kk_p2,
        'unit_ratio_1': k_n / k_p1,
        'unit_ratio_2': k_n / k_p2,
        'kk_ratio_1': kk_n / kk_p1,
        'kk_ratio_2': kk_n / kk_p2,
        'theta': c['theta'],
        'tau': c['tau'],
        'composition': c['rail1_count'],  # 0, 1, or 2 Rail1 factors
        'p1_prime_unit': pk_p1,
        'p2_prime_unit': pk_p2,
    })

print(f"  Semiprimes with unit index data: {len(unit_data)}")
print()

# 7a: Unit index ratio statistics by composition type
print("  7a: Unit index ratio (k_N/k_factor) by factor-rail composition")
print()

by_comp = {}
for ud in unit_data:
    comp = ud['composition']
    if comp not in by_comp:
        by_comp[comp] = []
    by_comp[comp].append(ud)

for comp_type in sorted(by_comp.keys()):
    items = by_comp[comp_type]
    ratios1 = np.array([ud['unit_ratio_1'] for ud in items])
    ratios2 = np.array([ud['unit_ratio_2'] for ud in items])
    all_ratios = np.concatenate([ratios1, ratios2])

    label = {0: 'R2xR2->R2', 1: 'R1xR2->R1', 2: 'R1xR1->R2'}.get(comp_type, f'{comp_type} Rail1')
    print(f"    {label} (n={len(items)}):")
    print(f"      unit_ratio mean={np.mean(all_ratios):.2f}, median={np.median(all_ratios):.2f}, "
          f"std={np.std(all_ratios):.2f}")
    print()

# 7b: k-index ratio (the ACTUAL 6k index, not sequential)
print("  7b: k-index ratio (k_N/k_p using 6k indices) by composition type")
print()

for comp_type in sorted(by_comp.keys()):
    items = by_comp[comp_type]
    kk_ratios = np.concatenate([
        np.array([ud['kk_ratio_1'] for ud in items]),
        np.array([ud['kk_ratio_2'] for ud in items])
    ])

    label = {0: 'R2xR2->R2', 1: 'R1xR2->R1', 2: 'R1xR1->R2'}.get(comp_type, f'{comp_type} Rail1')
    print(f"    {label}: kk_ratio mean={np.mean(kk_ratios):.2f}, "
          f"median={np.median(kk_ratios):.2f}, std={np.std(kk_ratios):.2f}")
print()

# 7c: Can unit index ratios predict phase?
print("  7c: Correlation between unit index ratios and phase theta(N)")
print()

all_unit_ratios = []
all_thetas = []
all_kk_ratios = []
for ud in unit_data:
    all_unit_ratios.append(ud['unit_ratio_1'])
    all_unit_ratios.append(ud['unit_ratio_2'])
    all_thetas.append(ud['theta'])
    all_thetas.append(ud['theta'])
    all_kk_ratios.append(ud['kk_ratio_1'])
    all_kk_ratios.append(ud['kk_ratio_2'])

all_unit_ratios = np.array(all_unit_ratios)
all_thetas = np.array(all_thetas)
all_kk_ratios = np.array(all_kk_ratios)

r_unit_theta, p_unit_theta = pearsonr(all_unit_ratios, all_thetas)
r_kk_theta, p_kk_theta = pearsonr(all_kk_ratios, all_thetas)
r_unit_kk, p_unit_kk = pearsonr(all_unit_ratios, all_kk_ratios)

print(f"    unit_ratio vs theta:  r={r_unit_theta:+.4f}, p={p_unit_theta:.4e}")
print(f"    kk_ratio vs theta:    r={r_kk_theta:+.4f}, p={p_kk_theta:.4e}")
print(f"    unit_ratio vs kk_ratio: r={r_unit_kk:+.4f}, p={p_unit_kk:.4e}")
print()

# 7d: Unit index ratio distributions — do different composition types differ?
print("  7d: KS tests on unit index ratio distributions between composition types")
print()

for i, ct1 in enumerate(sorted(by_comp.keys())):
    for ct2 in list(sorted(by_comp.keys()))[i+1:]:
        r1 = np.concatenate([
            np.array([ud['unit_ratio_1'] for ud in by_comp[ct1]]),
            np.array([ud['unit_ratio_2'] for ud in by_comp[ct1]])
        ])
        r2 = np.concatenate([
            np.array([ud['unit_ratio_1'] for ud in by_comp[ct2]]),
            np.array([ud['unit_ratio_2'] for ud in by_comp[ct2]])
        ])
        ks, p = ks_2samp(r1, r2)
        label1 = {0: 'R2xR2', 1: 'R1xR2', 2: 'R1xR1'}.get(ct1, str(ct1))
        label2 = {0: 'R2xR2', 1: 'R1xR2', 2: 'R1xR1'}.get(ct2, str(ct2))
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"    {label1} vs {label2}: KS={ks:.4f}, p={p:.4e} {sig}")
print()

# 7e: Prime unit index — factors indexed among primes on their rail
print("  7e: Prime unit index (factor's position among primes on its rail)")
print("      Testing if the prime-unit-index of factors correlates with phase")
print()

prime_unit_ratios_r1 = []  # (prime_unit of Rail1 factor, theta of composite)
prime_unit_ratios_r2 = []  # (prime_unit of Rail2 factor, theta of composite)

for ud in unit_data:
    if ud['p1_prime_unit'] > 0:
        if ud['rail_p1'] == -1:
            prime_unit_ratios_r1.append((ud['p1_prime_unit'], ud['theta']))
        else:
            prime_unit_ratios_r2.append((ud['p1_prime_unit'], ud['theta']))
    if ud['p2_prime_unit'] > 0:
        if ud['rail_p2'] == -1:
            prime_unit_ratios_r1.append((ud['p2_prime_unit'], ud['theta']))
        else:
            prime_unit_ratios_r2.append((ud['p2_prime_unit'], ud['theta']))

if len(prime_unit_ratios_r1) > 100:
    pur1, thr1 = zip(*prime_unit_ratios_r1)
    r_pur1, p_pur1 = pearsonr(np.array(pur1), np.array(thr1))
    print(f"    Rail1 prime-unit vs theta: r={r_pur1:+.4f}, p={p_pur1:.4e} (n={len(pur1)})")

if len(prime_unit_ratios_r2) > 100:
    pur2, thr2 = zip(*prime_unit_ratios_r2)
    r_pur2, p_pur2 = pearsonr(np.array(pur2), np.array(thr2))
    print(f"    Rail2 prime-unit vs theta: r={r_pur2:+.4f}, p={p_pur2:.4e} (n={len(pur2)})")
print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
print("  Generating visualizations...")

fig, axes = plt.subplots(3, 3, figsize=(18, 15))
fig.suptitle("Experiment 018: Factor Ratios on the 6k±1 Manifold (with Unit Index)", fontsize=14, fontweight='bold')

# Plot 1: Phase distributions by rail composition type
ax = axes[0, 0]
if len(semiprimes_r1r1) > 50:
    ax.hist([c['theta'] for c in semiprimes_r1r1], bins=60, alpha=0.5, density=True,
            label='R1xR1->R2', color='blue')
if len(semiprimes_r2r2) > 50:
    ax.hist([c['theta'] for c in semiprimes_r2r2], bins=60, alpha=0.5, density=True,
            label='R2xR2->R2', color='red')
if len(semiprimes_r1r2) > 50:
    ax.hist([c['theta'] for c in semiprimes_r1r2], bins=60, alpha=0.5, density=True,
            label='R1xR2->R1', color='green')
ax.set_xlabel("Phase theta (rad)")
ax.set_ylabel("Density")
ax.set_title("Phase by Factor-Rail Type")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# Plot 2: Phase deltas from factors (Rail1 vs Rail2)
ax = axes[0, 1]
if len(phase_deltas_r1) > 100 and len(phase_deltas_r2) > 100:
    ax.hist(np.degrees(phase_deltas_r1), bins=60, alpha=0.5, density=True,
            label=f'From Rail1 factors (n={len(phase_deltas_r1)})', color='blue')
    ax.hist(np.degrees(phase_deltas_r2), bins=60, alpha=0.5, density=True,
            label=f'From Rail2 factors (n={len(phase_deltas_r2)})', color='red')
    if len(random_deltas) > 50:
        ax.hist(np.degrees(random_deltas), bins=60, alpha=0.3, density=True,
                label=f'Random non-factors (n={len(random_deltas)})', color='gray')
ax.set_xlabel("Angular distance to factor ratio (deg)")
ax.set_ylabel("Density")
ax.set_title("Factor Phase Recovery")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# Plot 3: Phase by number of Rail1 factors
ax = axes[0, 2]
colors = ['blue', 'green', 'orange', 'red', 'purple']
for idx, r1_count in enumerate(sorted(by_rail1_count.keys())):
    angles = np.array(by_rail1_count[r1_count])
    if len(angles) > 100:
        ax.hist(angles, bins=60, alpha=0.4, density=True,
                label=f'{r1_count} Rail1 factors (n={len(angles)})',
                color=colors[idx % len(colors)])
ax.set_xlabel("Phase theta (rad)")
ax.set_ylabel("Density")
ax.set_title("Phase by Rail1 Factor Count")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# Plot 4: Close vs Distant factor pairs
ax = axes[1, 0]
if len(close_ratios) > 100 and len(distant_ratios) > 100:
    ax.hist(theta_close, bins=60, alpha=0.5, density=True,
            label=f'Close (ratio<2, n={len(close_ratios)})', color='green')
    ax.hist(theta_distant, bins=60, alpha=0.5, density=True,
            label=f'Distant (ratio>5, n={len(distant_ratios)})', color='red')
ax.set_xlabel("Phase theta (rad)")
ax.set_ylabel("Density")
ax.set_title("Close vs Distant Factor Pairs")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# Plot 5: Ratio angles in Signed Wheel space
ax = axes[1, 1]
# Scatter: x = ratio (N/p), y = theta of ratio
sample_ratios = []
for c in composites[:5000]:
    for fr in c['factor_ratios']:
        sample_ratios.append((fr['ratio'], fr['theta_ratio'], fr['factor_rail']))

if sample_ratios:
    ratios, thetas, rails = zip(*sample_ratios)
    ratios = np.array(ratios)
    thetas = np.array(thetas)
    rails = np.array(rails)

    mask_r1 = rails == -1
    mask_r2 = rails == +1

    ax.scatter(np.log(ratios[mask_r1]), thetas[mask_r1], s=2, alpha=0.3,
               color='blue', label='Ratio from Rail1 factor')
    ax.scatter(np.log(ratios[mask_r2]), thetas[mask_r2], s=2, alpha=0.3,
               color='red', label='Ratio from Rail2 factor')

ax.set_xlabel("log(ratio)")
ax.set_ylabel("theta(ratio)")
ax.set_title("Ratios in Signed Wheel Space")
ax.legend(fontsize=8, markerscale=5)
ax.grid(True, alpha=0.2)

# Plot 6: Z2 visualization
ax = axes[1, 2]
for c in composites[:3000]:
    if c['rail0_count'] > 0 or c['n_factors'] != 2 or c['n_unique'] != 2:
        continue
    p1, p2 = sorted(c['unique_factors'])
    r1 = get_rail(p1)
    r2 = get_rail(p2)
    target_rail = c['rail']
    color = 'blue' if target_rail == 1 else 'red'
    ax.scatter(r1 * r2, target_rail, s=3, alpha=0.1, color=color)

ax.set_xlabel("sigma(p1) * sigma(p2)")
ax.set_ylabel("sigma(N) = composite rail")
ax.set_title("Z2 Rail Group Verification")
ax.set_xticks([-1, 1])
ax.set_xticklabels(['-1 (Rail1)', '+1 (Rail2)'])
ax.set_yticks([-1, 1])
ax.set_yticklabels(['-1 (Rail1)', '+1 (Rail2)'])
ax.grid(True, alpha=0.3)

# Plot 7: Unit index ratio distributions by composition type
ax = axes[2, 0]
for comp_type in sorted(by_comp.keys()):
    items = by_comp[comp_type]
    ratios = np.concatenate([
        np.array([ud['unit_ratio_1'] for ud in items]),
        np.array([ud['unit_ratio_2'] for ud in items])
    ])
    label = {0: 'R2xR2->R2', 1: 'R1xR2->R1', 2: 'R1xR1->R2'}.get(comp_type)
    color = {0: 'red', 1: 'green', 2: 'blue'}.get(comp_type)
    ax.hist(ratios, bins=80, alpha=0.5, density=True, label=label, color=color)
ax.set_xlabel("Unit index ratio (k_N / k_factor)")
ax.set_ylabel("Density")
ax.set_title("Unit Index Ratio by Composition Type")
ax.legend(fontsize=8)
ax.set_xlim(0, 100)
ax.grid(True, alpha=0.2)

# Plot 8: k-index ratio vs phase
ax = axes[2, 1]
sample_kk = [(ud['kk_ratio_1'], ud['theta'], ud['composition']) for ud in unit_data[:5000]]
if sample_kk:
    kk_r, th_r, comp_r = zip(*sample_kk)
    kk_r = np.array(kk_r)
    th_r = np.array(th_r)
    comp_r = np.array(comp_r)
    for ct, color, label in [(0, 'red', 'R2xR2'), (1, 'green', 'R1xR2'), (2, 'blue', 'R1xR1')]:
        mask = comp_r == ct
        if mask.any():
            ax.scatter(kk_r[mask], np.degrees(th_r[mask]), s=3, alpha=0.3,
                       color=color, label=label)
ax.set_xlabel("k-index ratio (kk_N / kk_factor)")
ax.set_ylabel("theta(N) degrees")
ax.set_title("k-index Ratio vs Phase")
ax.legend(fontsize=8, markerscale=5)
ax.set_xlim(0, 200)
ax.grid(True, alpha=0.2)

# Plot 9: Unit index space — scatter of (unit_idx of p1, unit_idx of p2) colored by rail
ax = axes[2, 2]
for ud in unit_data[:5000]:
    u1 = get_unit_index(ud['p1'])
    u2 = get_unit_index(ud['p2'])
    color = {0: 'red', 1: 'green', 2: 'blue'}.get(ud['composition'], 'gray')
    ax.scatter(u1, u2, s=3, alpha=0.2, color=color)
ax.set_xlabel("Unit index of p1 (smaller factor)")
ax.set_ylabel("Unit index of p2 (larger factor)")
ax.set_title("Factor Unit Indices (colored by composition)")
ax.grid(True, alpha=0.2)
# Add legend manually
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='R2xR2->R2'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=8, label='R1xR2->R1'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='R1xR1->R2'),
]
ax.legend(handles=legend_elements, fontsize=7)

plt.tight_layout()
plt.savefig('experiments/018_factor_ratios/results.png', dpi=150)
print("  Saved: results.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print("  This experiment tests the COMPARATIVE structure between composites")
print("  and their prime factors on the 6k±1 manifold, inspired by Field's")
print("  nominalism: the ratios are the real structure, not the labels.")
print()
print(f"  Z2 rail group: {'VERIFIED' if violations == 0 else f'{violations} violations'}")
print(f"  Composites tested: {len(composites)}")
print()
print("  Key findings above. Check KS tests and p-values for significance.")
print()
print("Done.")
