"""
Experiment 018c: Prime Squares on the 6k+1 Manifold
====================================================
Rule 3 (Composition) applied to squares p*p where p is on the rails.

For same-rail squares (a = b = k):
  R1: k_N = 6k^2 - 2k = 2k(3k-1)
  R2: k_N = 6k^2 + 2k = 2k(3k+1)

All prime squares land on Rail2 (regardless of which rail p came from).

Tests:
1. Verify the square formulas
2. k_N / k = 2(3k +/- 1) — is this exact?
3. k_N mod p — residue identity for squares
4. k_N factorization in k-space: k_N = 2k(3k +/- 1)
5. Pattern in k_N values: do they have common factors?
6. Squares on the SAME rail — do R1 squares and R2 squares have
   different k-space signatures?
"""

import numpy as np
from math import log, pi, sqrt
from scipy.stats import pearsonr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
    if r == 1: return 1
    elif r == 5: return -1
    return 0

def rail_k(n):
    rail = get_rail(n)
    if rail == -1: return (n + 1) // 6
    elif rail == +1: return (n - 1) // 6
    return 0

N_MAX = 500_000

print("=" * 70)
print("  EXPERIMENT 018c: PRIME SQUARES ON THE 6k+1 MANIFOLD")
print("=" * 70)
print()

is_prime_arr = sieve(N_MAX + 10)

# Collect prime squares
r1_squares = []  # primes from Rail1 (6k-1)
r2_squares = []  # primes from Rail2 (6k+1)

for p in range(5, int(sqrt(N_MAX)) + 1):
    if not is_prime_arr[p]:
        continue
    rail = get_rail(p)
    if rail == 0:
        continue

    n = p * p
    k_n = rail_k(n)
    k_p = rail_k(p)

    entry = {
        'p': p,
        'n': n,
        'rail_p': rail,
        'k_p': k_p,
        'k_n': k_n,
        'rail_n': get_rail(n),
    }

    if rail == -1:
        r1_squares.append(entry)
    elif rail == +1:
        r2_squares.append(entry)

print(f"  Rail1 prime squares (R1*R1 -> R2): {len(r1_squares)}")
print(f"  Rail2 prime squares (R2*R2 -> R2): {len(r2_squares)}")
print()

# ====================================================================
#  TEST 1: VERIFY SQUARE FORMULAS
# ====================================================================
print("=" * 70)
print("  TEST 1: VERIFY SQUARE COMPOSITION FORMULAS")
print("=" * 70)
print()

# R1: k_N = 6k^2 - 2k
violations_r1 = 0
for s in r1_squares:
    expected = 6 * s['k_p']**2 - 2 * s['k_p']
    if s['k_n'] != expected:
        violations_r1 += 1

print(f"  R1: k_N = 6k^2 - 2k = 2k(3k-1)")
print(f"    Violations: {violations_r1}/{len(r1_squares)}")

# R2: k_N = 6k^2 + 2k
violations_r2 = 0
for s in r2_squares:
    expected = 6 * s['k_p']**2 + 2 * s['k_p']
    if s['k_n'] != expected:
        violations_r2 += 1

print(f"  R2: k_N = 6k^2 + 2k = 2k(3k+1)")
print(f"    Violations: {violations_r2}/{len(r2_squares)}")

if violations_r1 == 0 and violations_r2 == 0:
    print("  PERFECT: Both square formulas verified.")
print()

# ====================================================================
#  TEST 2: k_N / k_p RATIO
# ====================================================================
print("=" * 70)
print("  TEST 2: k_N / k_p = 2(3k +/- 1)")
print("=" * 70)
print()

print(f"  {'p':>6} {'rail':>5} {'k_p':>5} {'k_N':>8} {'k_N/k_p':>8} {'2(3k+/-1)':>10}")
print("  " + "-" * 50)

# Show R1 squares
print("  --- Rail1 primes ---")
for s in r1_squares[:8]:
    ratio = s['k_n'] / s['k_p']
    expected_ratio = 2 * (3 * s['k_p'] - 1)
    print(f"  {s['p']:>6} {'R1':>5} {s['k_p']:>5} {s['k_n']:>8} {ratio:>8.1f} {expected_ratio:>10}")

print()
print("  --- Rail2 primes ---")
for s in r2_squares[:8]:
    ratio = s['k_n'] / s['k_p']
    expected_ratio = 2 * (3 * s['k_p'] + 1)
    print(f"  {s['p']:>6} {'R2':>5} {s['k_p']:>5} {s['k_n']:>8} {ratio:>8.1f} {expected_ratio:>10}")

print()

# ====================================================================
#  TEST 3: RESIDUE IDENTITY FOR SQUARES
# ====================================================================
print("=" * 70)
print("  TEST 3: RESIDUE IDENTITY k_N mod p")
print("=" * 70)
print()

# For R2 squares: k_N = k*p + k (since k_N = 6k^2 + 2k = k(6k+1) + k = k*p + k)
# So k_N mod p = k

correct_r2 = 0
for s in r2_squares:
    if s['k_n'] % s['p'] == s['k_p']:
        correct_r2 += 1
print(f"  R2: k_N mod p == k_p?  {correct_r2}/{len(r2_squares)} ({100*correct_r2/max(len(r2_squares),1):.1f}%)")
print(f"       (k_N = k*p + k, so k_N mod p = k)")

# For R1 squares: k_N = k*p - k (since k_N = 6k^2 - 2k = k(6k-1) - k = k*p - k)
# So k_N mod p = (-k) mod p = p - k
correct_r1 = 0
for s in r1_squares:
    expected = (-s['k_p']) % s['p']
    if s['k_n'] % s['p'] == expected:
        correct_r1 += 1
print(f"  R1: k_N mod p == p-k?  {correct_r1}/{len(r1_squares)} ({100*correct_r1/max(len(r1_squares),1):.1f}%)")
print(f"       (k_N = k*p - k, so k_N mod p = p - k)")
print()

# ====================================================================
#  TEST 4: k_N FACTORIZATION IN k-SPACE
# ====================================================================
print("=" * 70)
print("  TEST 4: k_N FACTORIZATION IN k-SPACE")
print("=" * 70)
print()
print("  R1: k_N = 2k(3k-1)")
print("  R2: k_N = 2k(3k+1)")
print()
print("  Every prime square's k_N factors as 2 * k * (3k +/- 1)")
print("  Is (3k +/- 1) always coprime to k?")
print()

coprime_r1 = 0
coprime_r2 = 0
for s in r1_squares:
    a = s['k_p']
    b = 3 * a - 1
    if np.gcd(a, b) == 1:
        coprime_r1 += 1

for s in r2_squares:
    a = s['k_p']
    b = 3 * a + 1
    if np.gcd(a, b) == 1:
        coprime_r2 += 1

print(f"  R1: gcd(k, 3k-1) == 1?  {coprime_r1}/{len(r1_squares)} ({100*coprime_r1/max(len(r1_squares),1):.1f}%)")
print(f"  R2: gcd(k, 3k+1) == 1?  {coprime_r2}/{len(r2_squares)} ({100*coprime_r2/max(len(r2_squares),1):.1f}%)")

# What about gcd(k, 3k-1)? gcd(k, 3k-1) = gcd(k, -1) = 1 ALWAYS
# And gcd(k, 3k+1) = gcd(k, 1) = 1 ALWAYS
print()
print("  (Always true: gcd(k, 3k-1) = gcd(k,-1) = 1, gcd(k, 3k+1) = gcd(k,1) = 1)")
print()

# Is (3k-1) or (3k+1) ever prime?
prime_3k_r1 = sum(1 for s in r1_squares if is_prime_arr[3*s['k_p']-1])
prime_3k_r2 = sum(1 for s in r2_squares if is_prime_arr[3*s['k_p']+1])

print(f"  R1: (3k-1) is prime?  {prime_3k_r1}/{len(r1_squares)} ({100*prime_3k_r1/max(len(r1_squares),1):.1f}%)")
print(f"  R2: (3k+1) is prime?  {prime_3k_r2}/{len(r2_squares)} ({100*prime_3k_r2/max(len(r2_squares),1):.1f}%)")
print()

# ====================================================================
#  TEST 5: ALL SQUARES LAND ON RAIL2 — k_N PARITY
# ====================================================================
print("=" * 70)
print("  TEST 5: k_N PARITY AND STRUCTURE")
print("=" * 70)
print()

# k_N = 2k(3k +/- 1) — always even since 2 is a factor
print("  k_N = 2k(3k +/- 1) is ALWAYS EVEN (factor of 2)")
all_even = all(s['k_n'] % 2 == 0 for s in r1_squares + r2_squares)
print(f"  All k_N even? {all_even}")
print()

# k_N / 2 = k(3k +/- 1)
# What's k_N/2 mod k? = (3k +/- 1) mod k = +/- 1
print("  k_N/2 mod k = (3k +/- 1) mod k = +/- 1")
print()

# k_N / 2k = (3k +/- 1) — this IS on the rails!
# (3k-1) mod 6: depends on k
# (3k+1) mod 6: depends on k
print("  The factor (3k +/- 1):")
print(f"  {'k':>5} {'p(R1)':>6} {'3k-1':>6} {'3k-1 mod 6':>10} {'p(R2)':>6} {'3k+1':>6} {'3k+1 mod 6':>10}")
print("  " + "-" * 60)
for i in range(min(15, len(r1_squares))):
    k = r1_squares[i]['k_p']
    f_r1 = 3*k - 1
    if i < len(r2_squares):
        k2 = r2_squares[i]['k_p']
        f_r2 = 3*k2 + 1
        print(f"  {k:>5} {r1_squares[i]['p']:>6} {f_r1:>6} {f_r1%6:>10} "
              f"{r2_squares[i]['p']:>6} {f_r2:>6} {f_r2%6:>10}")
    else:
        print(f"  {k:>5} {r1_squares[i]['p']:>6} {f_r1:>6} {f_r1%6:>10}")

print()

# ====================================================================
#  TEST 6: k_N SPACING BETWEEN CONSECUTIVE SQUARES
# ====================================================================
print("=" * 70)
print("  TEST 6: k_N SPACING BETWEEN CONSECUTIVE PRIME SQUARES")
print("=" * 70)
print()

# All squares sorted by k_n
all_squares = sorted(r1_squares + r2_squares, key=lambda s: s['n'])

k_gaps = []
for i in range(len(all_squares) - 1):
    dk = all_squares[i+1]['k_n'] - all_squares[i]['k_n']
    k_gaps.append(dk)

k_gaps = np.array(k_gaps)

print(f"  Consecutive prime square k-gaps: {len(k_gaps)}")
print(f"  Mean gap: {np.mean(k_gaps):.1f}")
print(f"  Median gap: {np.median(k_gaps):.1f}")
print(f"  Min gap: {k_gaps.min()}")
print(f"  Max gap: {k_gaps.max()}")
print()

# Distribution
print("  Gap distribution:")
unique_gaps, counts = np.unique(k_gaps, return_counts=True)
sorted_idx = np.argsort(-counts)
for idx in sorted_idx[:15]:
    print(f"    gap={unique_gaps[idx]:>6}: {counts[idx]:>4} ({100*counts[idx]/len(k_gaps):.1f}%)")
print()

# Are the gaps always even?
print(f"  All gaps even? {np.all(k_gaps % 2 == 0)}")
# Since k_N is always even, differences are always even
print(f"  (k_N always even -> gaps always even)")
print()

# Gap / 2 — the "half-step"
half_gaps = k_gaps // 2
print(f"  Half-gaps (gap/2):")
unique_hg, counts_hg = np.unique(half_gaps, return_counts=True)
sorted_hg = np.argsort(-counts_hg)
for idx in sorted_hg[:15]:
    print(f"    half-gap={unique_hg[idx]:>5}: {counts_hg[idx]:>4} ({100*counts_hg[idx]/len(k_gaps):.1f}%)")
print()

# ====================================================================
#  TEST 7: R1 vs R2 SQUARE SIGNATURES
# ====================================================================
print("=" * 70)
print("  TEST 7: R1 vs R2 SQUARE k-SPACE SIGNATURES")
print("=" * 70)
print()

k_ns_r1 = np.array([s['k_n'] for s in r1_squares])
k_ns_r2 = np.array([s['k_n'] for s in r2_squares])
k_ps_r1 = np.array([s['k_p'] for s in r1_squares])
k_ps_r2 = np.array([s['k_p'] for s in r2_squares])

print(f"  R1 squares: k_N range [{k_ns_r1.min()}, {k_ns_r1.max()}]")
print(f"  R2 squares: k_N range [{k_ns_r2.min()}, {k_ns_r2.max()}]")
print()

# Can you tell if a square came from R1 or R2 by looking at k_N?
# k_N(R1) = 6k^2 - 2k
# k_N(R2) = 6k^2 + 2k
# Difference: k_N(R2) - k_N(R1) = 4k for same k
# But k differs between rails

# Signature: k_N mod 4
print("  k_N mod 4 for R1 squares:")
mods_r1 = k_ns_r1 % 4
for m in sorted(set(mods_r1)):
    count = np.sum(mods_r1 == m)
    print(f"    {m}: {count} ({100*count/len(mods_r1):.1f}%)")

print()
print("  k_N mod 4 for R2 squares:")
mods_r2 = k_ns_r2 % 4
for m in sorted(set(mods_r2)):
    count = np.sum(mods_r2 == m)
    print(f"    {m}: {count} ({100*count/len(mods_r2):.1f}%)")

# k_N = 2k(3k +/- 1). For R1: 2k(3k-1). For R2: 2k(3k+1).
# If k is odd: 2k is 2 mod 4, (3k-1) is even, (3k+1) is even
# If k is even: 2k is 0 mod 4, both factors are 0 mod 4
# So k_N is always divisible by 4 when k is even, and 2 mod 4 when k is odd? No...

# Let me just check k_N mod 6
print()
print("  k_N mod 6 for R1 squares:")
mods6_r1 = k_ns_r1 % 6
for m in sorted(set(mods6_r1)):
    count = np.sum(mods6_r1 == m)
    print(f"    {m}: {count} ({100*count/len(mods6_r1):.1f}%)")

print()
print("  k_N mod 6 for R2 squares:")
mods6_r2 = k_ns_r2 % 6
for m in sorted(set(mods6_r2)):
    count = np.sum(mods6_r2 == m)
    print(f"    {m}: {count} ({100*count/len(mods6_r2):.1f}%)")
print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Experiment 018c: Prime Squares on the 6k+/-1 Manifold", fontsize=14, fontweight='bold')

# Plot 1: k_N vs k_p for both rail types
ax = axes[0, 0]
ax.scatter(k_ps_r1, k_ns_r1, s=20, alpha=0.7, color='blue', label='R1: 6k^2-2k')
ax.scatter(k_ps_r2, k_ns_r2, s=20, alpha=0.7, color='red', label='R2: 6k^2+2k')
k_range = np.arange(1, max(k_ps_r1.max(), k_ps_r2.max()) + 1)
ax.plot(k_range, 6*k_range**2 - 2*k_range, 'b-', alpha=0.3, linewidth=1)
ax.plot(k_range, 6*k_range**2 + 2*k_range, 'r-', alpha=0.3, linewidth=1)
ax.set_xlabel("k_p (prime's k-index)")
ax.set_ylabel("k_N (square's k-index)")
ax.set_title("Square Composition: k_N vs k_p")
ax.legend()
ax.grid(True, alpha=0.2)

# Plot 2: k_N / k_p vs k_p
ax = axes[0, 1]
ratios_r1 = k_ns_r1 / k_ps_r1
ratios_r2 = k_ns_r2 / k_ps_r2
ax.scatter(k_ps_r1, ratios_r1, s=20, alpha=0.7, color='blue', label='R1: 2(3k-1)')
ax.scatter(k_ps_r2, ratios_r2, s=20, alpha=0.7, color='red', label='R2: 2(3k+1)')
ax.plot(k_range, 2*(3*k_range - 1), 'b-', alpha=0.3)
ax.plot(k_range, 2*(3*k_range + 1), 'r-', alpha=0.3)
ax.set_xlabel("k_p")
ax.set_ylabel("k_N / k_p")
ax.set_title("Ratio k_N/k_p = 2(3k +/- 1)")
ax.legend()
ax.grid(True, alpha=0.2)

# Plot 3: k_N on Rail2 — positions of squares
ax = axes[0, 2]
show_n = min(200, len(all_squares))
for s in all_squares[:show_n]:
    color = 'blue' if s['rail_p'] == -1 else 'red'
    y = 0.3 if s['rail_p'] == -1 else 0.7
    ax.scatter(s['k_n'], y, s=30, alpha=0.7, color=color)
from matplotlib.lines import Line2D
ax.legend(handles=[
    Line2D([0],[0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='R1^2'),
    Line2D([0],[0], marker='o', color='w', markerfacecolor='red', markersize=8, label='R2^2'),
])
ax.set_xlabel("k_N position on Rail2")
ax.set_title("Square Positions on Rail2")
ax.legend()
ax.set_yticks([])
ax.grid(True, alpha=0.2, axis='x')

# Plot 4: k-gap distribution
ax = axes[1, 0]
ax.hist(k_gaps, bins=50, color='steelblue', alpha=0.7)
ax.set_xlabel("k-gap between consecutive prime squares")
ax.set_ylabel("Count")
ax.set_title("Square k-Gaps")
ax.grid(True, alpha=0.2)

# Plot 5: k_N factorization — k_N/2k vs k_p
ax = axes[1, 1]
factor_r1 = k_ns_r1 / (2 * k_ps_r1)  # should be (3k-1)
factor_r2 = k_ns_r2 / (2 * k_ps_r2)  # should be (3k+1)
ax.scatter(k_ps_r1, factor_r1, s=20, alpha=0.7, color='blue', label='R1: (3k-1)')
ax.scatter(k_ps_r2, factor_r2, s=20, alpha=0.7, color='red', label='R2: (3k+1)')
ax.plot(k_range, 3*k_range - 1, 'b-', alpha=0.3)
ax.plot(k_range, 3*k_range + 1, 'r-', alpha=0.3)
ax.set_xlabel("k_p")
ax.set_ylabel("k_N / (2*k_p)")
ax.set_title("Factor (3k +/- 1)")
ax.legend()
ax.grid(True, alpha=0.2)

# Plot 6: Residue k_N mod p
ax = axes[1, 2]
residues_r1 = np.array([s['k_n'] % s['p'] for s in r1_squares])
residues_r2 = np.array([s['k_n'] % s['p'] for s in r2_squares])
ax.scatter(k_ps_r1, residues_r1, s=20, alpha=0.7, color='blue', label='R1: k_N mod p = p-k')
ax.scatter(k_ps_r2, residues_r2, s=20, alpha=0.7, color='red', label='R2: k_N mod p = k')
ax.plot(k_ps_r1, k_ps_r1, 'b--', alpha=0.3, label='y=k (R2 target)')
ax.plot(k_ps_r1, [s['p'] - s['k_p'] for s in r1_squares], 'r--', alpha=0.3, label='y=p-k (R1 target)')
ax.set_xlabel("k_p")
ax.set_ylabel("k_N mod p")
ax.set_title("Residue Identity")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/018_factor_ratios/squares_results.png', dpi=150)
print("  Saved: squares_results.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print("  Prime squares on the 6k+/-1 manifold:")
print()
print("  ALL prime squares land on Rail2 (6k+1), regardless of source rail.")
print()
print("  Composition formulas (Rule 3):")
print("    R1: k_N = 6k^2 - 2k = 2k(3k-1)")
print("    R2: k_N = 6k^2 + 2k = 2k(3k+1)")
print()
print("  Key identities:")
print("    k_N is ALWAYS EVEN (factor of 2)")
print("    k_N/k_p = 2(3k +/- 1) — grows linearly with k")
print("    k_N mod p = k (R2) or p-k (R1) — residue identity")
print("    gcd(k, 3k +/- 1) = 1 ALWAYS (k-space factors coprime)")
print("    k_N/2k = (3k +/- 1) — the cofactor in k-space")
print()
print("  The (3k +/- 1) cofactor determines the 'spread' of the square")
print("  on Rail2. R1 and R2 primes produce slightly different spreads,")
print("  but both land on the same rail.")
print()
print("Done.")
