"""
Experiment 018b: Same-Rail Composition Structure
=================================================
The k-index composition formulas are clean ONLY within the same rail:

  Rail1 x Rail1 -> Rail2:  k_N = 6ab - a - b
  Rail2 x Rail2 -> Rail2:  k_N = 6ab + a + b

where a, b are the k-indices of the prime factors on their respective rails.
Cross-rail composition (R1xR2) is asymmetric and doesn't share this structure.

Tests:
1. Verify the composition formulas on actual data
2. Can you recover (a,b) from k_N alone? (inverse problem)
3. Is there structure in k_N mod a or k_N mod b?
4. Walking the rail: can you step from one same-rail semiprime to the next
   by adding prime increments?
"""

import numpy as np
from math import log, pi, sqrt, gcd
from scipy.stats import pearsonr, ks_2samp
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

def get_rail(n):
    if n % 2 == 0 or n % 3 == 0:
        return 0
    r = n % 6
    if r == 1:
        return 1   # Rail2 (6k+1)
    elif r == 5:
        return -1  # Rail1 (6k-1)
    return 0

def rail_k(n):
    """k-index: n = 6k + sigma"""
    rail = get_rail(n)
    if rail == -1:
        return (n + 1) // 6
    elif rail == +1:
        return (n - 1) // 6
    return 0

N_MAX = 200_000

print("=" * 70)
print("  EXPERIMENT 018b: SAME-RAIL COMPOSITION ON 6k±1")
print("=" * 70)
print()

is_prime_arr = sieve(N_MAX + 10)

# Build smallest prime factor table
spf = np.zeros(N_MAX + 10, dtype=np.int32)
for i in range(2, N_MAX + 10):
    if is_prime_arr[i]:
        spf[i::i] = np.where(spf[i::i] == 0, i, spf[i::i])
spf[0] = 0
spf[1] = 0

def factorize(n):
    factors = []
    while n > 1:
        p = spf[n]
        factors.append(p)
        n //= p
    return factors

# ====================================================================
#  COLLECT SAME-RAIL SEMIPRIMES
# ====================================================================
print("  Collecting same-rail semiprimes...")
print()

# Rail1 x Rail1 -> Rail2
r1r1_data = []
# Rail2 x Rail2 -> Rail2
r2r2_data = []

for n in range(25, N_MAX + 1):
    if get_rail(n) == 0:
        continue
    if is_prime_arr[n]:
        continue

    factors = factorize(n)
    if len(factors) != 2 or factors[0] == factors[1]:
        # Only semiprimes with distinct factors
        continue
    # Check for repeated factors (like 5^2=25)
    unique = set(factors)
    if len(unique) != 2:
        continue

    p1, p2 = sorted(factors)
    r1 = get_rail(p1)
    r2 = get_rail(p2)

    # Skip if either factor involves 2 or 3
    if r1 == 0 or r2 == 0:
        continue

    k_n = rail_k(n)
    k_p1 = rail_k(p1)
    k_p2 = rail_k(p2)

    entry = {
        'n': n, 'p1': p1, 'p2': p2,
        'k_n': k_n, 'k_p1': k_p1, 'k_p2': k_p2,
        'rail_n': get_rail(n),
        'rail_p1': r1, 'rail_p2': r2,
    }

    if r1 == -1 and r2 == -1:
        r1r1_data.append(entry)
    elif r1 == +1 and r2 == +1:
        r2r2_data.append(entry)

print(f"  Rail1 x Rail1 -> Rail2 semiprimes: {len(r1r1_data)}")
print(f"  Rail2 x Rail2 -> Rail2 semiprimes: {len(r2r2_data)}")
print()

# ====================================================================
#  TEST 1: VERIFY COMPOSITION FORMULAS
# ====================================================================
print("=" * 70)
print("  TEST 1: VERIFY SAME-RAIL COMPOSITION FORMULAS")
print("=" * 70)
print()

# Rail1 x Rail1: k_N = 6ab - a - b
violations_r1r1 = 0
for d in r1r1_data:
    a, b = d['k_p1'], d['k_p2']
    expected_k = 6*a*b - a - b
    if d['k_n'] != expected_k:
        violations_r1r1 += 1

print(f"  R1xR1 formula: k_N = 6ab - a - b")
print(f"    Violations: {violations_r1r1}/{len(r1r1_data)}")

# Rail2 x Rail2: k_N = 6ab + a + b
violations_r2r2 = 0
for d in r2r2_data:
    a, b = d['k_p1'], d['k_p2']
    expected_k = 6*a*b + a + b
    if d['k_n'] != expected_k:
        violations_r2r2 += 1

print(f"  R2xR2 formula: k_N = 6ab + a + b")
print(f"    Violations: {violations_r2r2}/{len(r2r2_data)}")

if violations_r1r1 == 0 and violations_r2r2 == 0:
    print("  PERFECT: Both formulas verified on all semiprimes.")
print()

# ====================================================================
#  TEST 2: THE RATIO k_N / k_p — IS IT THE OTHER FACTOR?
# ====================================================================
print("=" * 70)
print("  TEST 2: RATIO k_N / k_p")
print("=" * 70)
print()

# For R2xR2: k_N = 6ab + a + b
# k_N / a = 6b + 1 + b/a = (6b+1) + b/a = p2 + k_p2/k_p1
# So k_N / a ~ p2 (off by k_p2/k_p1, which is small for large k_p1)
# k_N / b ~ p1 (off by k_p1/k_p2)

print("  For R2xR2: k_N = 6ab + a + b")
print("  k_N / a = 6b + 1 + b/a ~ p2 + small correction")
print("  k_N / b = 6a + 1 + a/b ~ p1 + small correction")
print()

# Test: k_N / k_p1 vs p2, and k_N / k_p2 vs p1
ratio_a_p2_r2r2 = []  # (k_N/k_p1, p2)
ratio_b_p1_r2r2 = []  # (k_N/k_p2, p1)

for d in r2r2_data:
    ratio_a_p2_r2r2.append((d['k_n'] / d['k_p1'], d['p2']))
    ratio_b_p1_r2r2.append((d['k_n'] / d['k_p2'], d['p1']))

ratios_a = np.array([x[0] for x in ratio_a_p2_r2r2])
targets_p2 = np.array([x[1] for x in ratio_a_p2_r2r2])
ratios_b = np.array([x[0] for x in ratio_b_p1_r2r2])
targets_p1 = np.array([x[1] for x in ratio_b_p1_r2r2])

r_a, p_a = pearsonr(ratios_a, targets_p2)
r_b, p_b = pearsonr(ratios_b, targets_p1)

print(f"  R2xR2: k_N/k_p1 vs p2:  r={r_a:.6f}, p={p_a:.2e}")
print(f"  R2xR2: k_N/k_p2 vs p1:  r={r_b:.6f}, p={p_b:.2e}")

# The actual relationship: k_N/a = p2 + b/a
# Error = b/a = k_p2/k_p1
errors_a = ratios_a - targets_p2  # should be k_p2/k_p1
expected_errors_a = np.array([d['k_p2'] / d['k_p1'] for d in r2r2_data])
r_err, p_err = pearsonr(errors_a, expected_errors_a)
print(f"  Error k_N/a - p2 vs k_p2/k_p1: r={r_err:.6f} (should be 1.0)")
print()

# Now for R1xR1: k_N = 6ab - a - b
# k_N / a = 6b - 1 - b/a = (6b-1) - b/a = p2 - k_p2/k_p1
# where p2 = 6k_p2 - 1 for Rail1 primes

ratio_a_p2_r1r1 = []
ratio_b_p1_r1r1 = []
for d in r1r1_data:
    ratio_a_p2_r1r1.append((d['k_n'] / d['k_p1'], d['p2']))
    ratio_b_p1_r1r1.append((d['k_n'] / d['k_p2'], d['p1']))

ratios_a1 = np.array([x[0] for x in ratio_a_p2_r1r1])
targets_p2_1 = np.array([x[1] for x in ratio_a_p2_r1r1])
ratios_b1 = np.array([x[0] for x in ratio_b_p1_r1r1])
targets_p1_1 = np.array([x[1] for x in ratio_b_p1_r1r1])

r_a1, p_a1 = pearsonr(ratios_a1, targets_p2_1)
r_b1, p_b1 = pearsonr(ratios_b1, targets_p1_1)

print(f"  R1xR1: k_N/k_p1 vs p2:  r={r_a1:.6f}, p={p_a1:.2e}")
print(f"  R1xR1: k_N/k_p2 vs p1:  r={r_b1:.6f}, p={p_b1:.2e}")

errors_a1 = ratios_a1 - targets_p2_1
expected_errors_a1 = np.array([-d['k_p2'] / d['k_p1'] for d in r1r1_data])
r_err1, p_err1 = pearsonr(errors_a1, expected_errors_a1)
print(f"  Error k_N/a - p2 vs -k_p2/k_p1: r={r_err1:.6f} (should be 1.0)")
print()

# ====================================================================
#  TEST 3: THE INTEGER RATIO — FLOOR(k_N / k_p)
# ====================================================================
print("=" * 70)
print("  TEST 3: FLOOR(k_N / k_p) vs THE OTHER FACTOR")
print("=" * 70)
print()
print("  Since k_N / k_p ~ the other factor (p_other),")
print("  does floor(k_N / k_p) EXACTLY equal p_other?")
print()

# R2xR2: k_N/a = p2 + b/a, so floor(k_N/a) = p2 if b/a < 1, i.e., b < a
# Since p1 <= p2, we have k_p1 <= k_p2, so b/a can be > 1
# Better to use k_N/k_p2 where k_p2 >= k_p1

exact_count = 0
total = 0
for d in r2r2_data:
    # Use the larger k-index as denominator
    if d['k_p2'] >= d['k_p1']:
        floor_ratio = d['k_n'] // d['k_p2']
        if floor_ratio == d['p1']:
            exact_count += 1
        total += 1

print(f"  R2xR2: floor(k_N/k_p_larger) == p_smaller?")
print(f"    {exact_count}/{total} ({100*exact_count/max(total,1):.1f}%)")

# R1xR1 same test
exact_count1 = 0
total1 = 0
for d in r1r1_data:
    if d['k_p2'] >= d['k_p1']:
        floor_ratio = d['k_n'] // d['k_p2']
        if floor_ratio == d['p1']:
            exact_count1 += 1
        total1 += 1

print(f"  R1xR1: floor(k_N/k_p_larger) == p_smaller?")
print(f"    {exact_count1}/{total1} ({100*exact_count1/max(total1,1):.1f}%)")
print()

# ====================================================================
#  TEST 4: WALKING THE RAIL — ADDING PRIME STEPS
# ====================================================================
print("=" * 70)
print("  TEST 4: WALKING THE RAIL BY PRIME STEPS")
print("=" * 70)
print()
print("  For same-rail composites on Rail2, can you step from one")
print("  to the next by adding prime increments in k-space?")
print()

# Collect all Rail2 semiprimes (both R1xR1 and R2xR2 land here)
rail2_semiprimes = sorted(
    [d for d in r1r1_data] + [d for d in r2r2_data],
    key=lambda d: d['k_n']
)

# For consecutive Rail2 semiprimes, what's the k-step?
k_steps = []
step_types = []
for i in range(len(rail2_semiprimes) - 1):
    dk = rail2_semiprimes[i+1]['k_n'] - rail2_semiprimes[i]['k_n']
    k_steps.append(dk)
    # Classify: both R1xR1, both R2xR2, or mixed
    type_i = 'R1R1' if rail2_semiprimes[i]['rail_p1'] == -1 else 'R2R2'
    type_j = 'R1R1' if rail2_semiprimes[i+1]['rail_p1'] == -1 else 'R2R2'
    step_types.append(f"{type_i}->{type_j}")

k_steps = np.array(k_steps)

print(f"  Consecutive Rail2 semiprime k-steps: {len(k_steps)}")
print(f"  Mean step: {np.mean(k_steps):.2f}")
print(f"  Median step: {np.median(k_steps):.1f}")
print(f"  Min step: {k_steps.min()}")
print(f"  Max step: {k_steps.max()}")
print(f"  Step = 1 (adjacent k): {np.sum(k_steps == 1)} ({100*np.mean(k_steps==1):.1f}%)")
print(f"  Step = 2: {np.sum(k_steps == 2)} ({100*np.mean(k_steps==2):.1f}%)")
print(f"  Step = 3: {np.sum(k_steps == 3)} ({100*np.mean(k_steps==3):.1f}%)")
print()

# Distribution of steps
print("  Step distribution (top 20):")
unique_steps, counts = np.unique(k_steps, return_counts=True)
sorted_idx = np.argsort(-counts)
for idx in sorted_idx[:20]:
    print(f"    step={unique_steps[idx]:>5}: {counts[idx]:>5} ({100*counts[idx]/len(k_steps):.1f}%)")
print()

# ====================================================================
#  TEST 5: k-SPACE MODULAR ARITHMETIC
# ====================================================================
print("=" * 70)
print("  TEST 5: k_N mod k_p — RESIDUE STRUCTURE")
print("=" * 70)
print()
print("  For R2xR2: k_N = 6ab + a + b")
print("  k_N mod a = (6ab + a + b) mod a = b mod a = k_p2 mod k_p1")
print("  k_N mod b = (6ab + a + b) mod b = a mod b = k_p1 mod k_p2")
print()
print("  The residues directly give you the other factor's k-index (mod first).")
print()

# Verify
correct_mod = 0
total_mod = 0
for d in r2r2_data:
    a, b = d['k_p1'], d['k_p2']
    res_a = d['k_n'] % a
    expected_res_a = b % a
    if res_a == expected_res_a:
        correct_mod += 1
    total_mod += 1

print(f"  R2xR2: k_N mod k_p1 == k_p2 mod k_p1?")
print(f"    {correct_mod}/{total_mod} ({100*correct_mod/max(total_mod,1):.1f}%)")

# Same for R1xR1: k_N = 6ab - a - b
# k_N mod a = (6ab - a - b) mod a = (-b) mod a = (a - b%a) mod a
correct_mod1 = 0
total_mod1 = 0
for d in r1r1_data:
    a, b = d['k_p1'], d['k_p2']
    res_a = d['k_n'] % a
    expected_res_a = (-b) % a
    if res_a == expected_res_a:
        correct_mod1 += 1
    total_mod1 += 1

print(f"  R1xR1: k_N mod k_p1 == (-k_p2) mod k_p1?")
print(f"    {correct_mod1}/{total_mod1} ({100*correct_mod1/max(total_mod1,1):.1f}%)")
print()

# ====================================================================
#  TEST 6: GIVEN k_N AND ONE FACTOR'S k, RECOVER THE OTHER
# ====================================================================
print("=" * 70)
print("  TEST 6: FACTOR RECOVERY FROM k_N AND ONE k-INDEX")
print("=" * 70)
print()
print("  For R2xR2: k_N = 6ab + a + b")
print("  Given k_N and a, solve for b:")
print("  k_N = 6ab + a + b = b(6a+1) + a = b*p1 + a")
print("  So: b = (k_N - a) / p1  (exact division if k_N and a are correct)")
print()

# Test recovery
recovered_count = 0
total_recovery = 0
for d in r2r2_data:
    a, b = d['k_p1'], d['k_p2']
    k_n = d['k_n']
    p1 = d['p1']  # = 6a + 1

    # Recover b from k_N and a
    numerator = k_n - a
    if numerator % p1 == 0:
        recovered_b = numerator // p1
        if recovered_b == b:
            recovered_count += 1
    total_recovery += 1

print(f"  R2xR2: Recover k_p2 from k_N and k_p1?")
print(f"    b = (k_N - a) / p1")
print(f"    {recovered_count}/{total_recovery} ({100*recovered_count/max(total_recovery,1):.1f}%)")

# R1xR1: k_N = 6ab - a - b = b(6a-1) - a = b*p1 - a
# b = (k_N + a) / p1
recovered_count1 = 0
total_recovery1 = 0
for d in r1r1_data:
    a, b = d['k_p1'], d['k_p2']
    k_n = d['k_n']
    p1 = d['p1']  # = 6a - 1

    numerator = k_n + a
    if numerator % p1 == 0:
        recovered_b = numerator // p1
        if recovered_b == b:
            recovered_count1 += 1
    total_recovery1 += 1

print(f"  R1xR1: Recover k_p2 from k_N and k_p1?")
print(f"    b = (k_N + a) / p1")
print(f"    {recovered_count1}/{total_recovery1} ({100*recovered_count1/max(total_recovery1,1):.1f}%)")
print()

# ====================================================================
#  TEST 7: CAN YOU FACTOR FROM k_N ALONE?
# ====================================================================
print("=" * 70)
print("  TEST 7: FACTORIZATION FROM k_N ALONE (HARD PROBLEM)")
print("=" * 70)
print()
print("  k_N = 6ab ± a ± b (depending on rail type)")
print("  This is equivalent to factoring N itself (just reformulated).")
print("  But the k-space formula may reveal structure not visible in N-space.")
print()

# For R2xR2: k_N + 1 = 6ab + a + b + 1 = (6a+1)(6b+1)/6 + correction...
# Actually: 6*k_N + 1 = 36ab + 6a + 6b + 1 = (6a+1)(6b+1) = p1 * p2 = N
# So k_N = (N-1)/6, which is trivially true since N = 6*k_N + 1 on Rail2.

# The interesting question: does k_N have special factorizability properties?
# k_N = 6ab + a + b for R2xR2
# = a(6b+1) + b
# = a*p2 + b

# So k_N mod p2 = b = k_p2. And k_N mod p1 = a = k_p1 (if a < p2)

# This means: the RESIDUE of k_N when divided by p gives you the k-index of p!
print("  For R2xR2: k_N = a*p2 + k_p2")
print("  So: k_N mod p2 = k_p2 (the k-index of the OTHER factor)")
print()
print("  And: k_N mod p1 = k_p1 (since k_N = b*p1 + k_p1)")
print()

# Verify
correct_residue = 0
for d in r2r2_data:
    if d['k_n'] % d['p2'] == d['k_p2']:
        correct_residue += 1
print(f"  R2xR2: k_N mod p2 == k_p2? {correct_residue}/{len(r2r2_data)} "
      f"({100*correct_residue/max(len(r2r2_data),1):.1f}%)")

correct_residue1 = 0
for d in r2r2_data:
    if d['k_n'] % d['p1'] == d['k_p1']:
        correct_residue1 += 1
print(f"  R2xR2: k_N mod p1 == k_p1? {correct_residue1}/{len(r2r2_data)} "
      f"({100*correct_residue1/max(len(r2r2_data),1):.1f}%)")

# R1xR1: k_N = a*p2 - k_p2 (since p2 = 6b-1)
# k_N + k_p2 = a*p2, so (k_N + k_p2) / p2 = a = k_p1
# Equivalently: k_N mod p2 = p2 - k_p2 (if k_p2 != 0)
correct_residue_r1 = 0
for d in r1r1_data:
    expected = (-d['k_p2']) % d['p2']
    if d['k_n'] % d['p2'] == expected:
        correct_residue_r1 += 1
print(f"  R1xR1: k_N mod p2 == (-k_p2) mod p2? {correct_residue_r1}/{len(r1r1_data)} "
      f"({100*correct_residue_r1/max(len(r1r1_data),1):.1f}%)")

# AND: (k_N + k_p2) % p2 == 0
# i.e., k_N ≡ -k_p2 (mod p2), so k_N + k_p2 ≡ 0 (mod p2)
correct_additive = 0
for d in r1r1_data:
    if (d['k_n'] + d['k_p2']) % d['p2'] == 0:
        correct_additive += 1
print(f"  R1xR1: (k_N + k_p2) mod p2 == 0? {correct_additive}/{len(r1r1_data)} "
      f"({100*correct_additive/max(len(r1r1_data),1):.1f}%)")
print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Experiment 018b: Same-Rail Composition on 6k±1", fontsize=14, fontweight='bold')

# Plot 1: k_N / k_p1 vs p2 (R2xR2)
ax = axes[0, 0]
ax.scatter(ratios_a[:3000], targets_p2[:3000], s=2, alpha=0.3, color='blue')
lim_min = min(ratios_a[:3000].min(), targets_p2[:3000].min())
lim_max = max(ratios_a[:3000].max(), targets_p2[:3000].max())
ax.plot([lim_min, lim_max], [lim_min, lim_max], 'r-', linewidth=1, label='y=x')
ax.set_xlabel("k_N / k_p1")
ax.set_ylabel("p2 (other factor)")
ax.set_title(f"R2xR2: k_N/k_p1 ~ p2 (r={r_a:.4f})")
ax.legend()
ax.grid(True, alpha=0.2)

# Plot 2: k_N / k_p1 vs p2 (R1xR1)
ax = axes[0, 1]
ax.scatter(ratios_a1[:3000], targets_p2_1[:3000], s=2, alpha=0.3, color='red')
lim_min = min(ratios_a1[:3000].min(), targets_p2_1[:3000].min())
lim_max = max(ratios_a1[:3000].max(), targets_p2_1[:3000].max())
ax.plot([lim_min, lim_max], [lim_min, lim_max], 'r-', linewidth=1, label='y=x')
ax.set_xlabel("k_N / k_p1")
ax.set_ylabel("p2 (other factor)")
ax.set_title(f"R1xR1: k_N/k_p1 ~ p2 (r={r_a1:.4f})")
ax.legend()
ax.grid(True, alpha=0.2)

# Plot 3: k-step distribution
ax = axes[0, 2]
ax.hist(k_steps, bins=100, color='steelblue', alpha=0.7)
ax.set_xlabel("k-step between consecutive Rail2 semiprimes")
ax.set_ylabel("Count")
ax.set_title("Rail2 Semiprime k-Steps")
ax.set_xlim(0, min(100, k_steps.max()))
ax.grid(True, alpha=0.2)

# Plot 4: Factor unit index scatter (R2xR2)
ax = axes[1, 0]
k_p1s = np.array([d['k_p1'] for d in r2r2_data[:5000]])
k_p2s = np.array([d['k_p2'] for d in r2r2_data[:5000]])
k_ns = np.array([d['k_n'] for d in r2r2_data[:5000]])
sc = ax.scatter(k_p1s, k_p2s, c=k_ns, s=3, alpha=0.5, cmap='viridis')
plt.colorbar(sc, ax=ax, label='k_N')
ax.set_xlabel("k_p1 (Rail2)")
ax.set_ylabel("k_p2 (Rail2)")
ax.set_title("R2xR2: Factor k-indices (color=k_N)")
ax.grid(True, alpha=0.2)

# Plot 5: Factor unit index scatter (R1xR1)
ax = axes[1, 1]
k_p1s_1 = np.array([d['k_p1'] for d in r1r1_data[:5000]])
k_p2s_1 = np.array([d['k_p2'] for d in r1r1_data[:5000]])
k_ns_1 = np.array([d['k_n'] for d in r1r1_data[:5000]])
sc2 = ax.scatter(k_p1s_1, k_p2s_1, c=k_ns_1, s=3, alpha=0.5, cmap='plasma')
plt.colorbar(sc2, ax=ax, label='k_N')
ax.set_xlabel("k_p1 (Rail1)")
ax.set_ylabel("k_p2 (Rail1)")
ax.set_title("R1xR1: Factor k-indices (color=k_N)")
ax.grid(True, alpha=0.2)

# Plot 6: Residue structure - k_N mod p vs k_index
ax = axes[1, 2]
sample = r2r2_data[:2000]
residues = [d['k_n'] % d['p1'] for d in sample]
k_indices = [d['k_p1'] for d in sample]
ax.scatter(k_indices, residues, s=3, alpha=0.3, color='green')
ax.plot([0, max(k_indices)], [0, max(k_indices)], 'r-', linewidth=1, label='y=x (k_p1)')
ax.set_xlabel("k_p1")
ax.set_ylabel("k_N mod p1")
ax.set_title("R2xR2: Residue = k_p1")
ax.legend()
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/018_factor_ratios/same_rail_results.png', dpi=150)
print("  Saved: same_rail_results.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print("  Same-rail composition formulas VERIFIED:")
print("    R1xR1: k_N = 6ab - a - b  (0 violations)")
print("    R2xR2: k_N = 6ab + a + b  (0 violations)")
print()
print("  The k-index ratio k_N/k_p APPROXIMATES the other factor (r>0.999)")
print("  with small error = k_other/k_self.")
print()
print("  RESIDUE IDENTITY (the cleanest result):")
print("    R2xR2: k_N mod p_factor = k_index_of_factor")
print("    R1xR1: (k_N + k_index) mod p_factor = 0")
print()
print("  FACTOR RECOVERY:")
print("    Given k_N and one factor's k-index (or the factor itself),")
print("    the other factor's k-index is EXACTLY recoverable:")
print("    R2xR2: b = (k_N - a) / p1")
print("    R1xR1: b = (k_N + a) / p1")
print()
print("  This is the same as integer factorization reformulated in k-space.")
print("  No free lunch — but the k-space formulation reveals the residue")
print("  structure that's hidden in N-space.")
print()
print("Done.")
