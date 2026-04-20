"""
Experiment 018w: The Walking Sieve -- Prime Generation via k-Space Lattices
============================================================================
Instead of testing divisibility, WALK the lattices. Each prime p generates
a regular lattice in k-space: k = p*m + offset. All composite positions
are visited. Whatever remains unvisited is prime.

This is a Sieve of Eratosthenes that works entirely in k-space:
- No division of N needed
- No primality testing needed
- Just mark lattice positions as composite
- Primes are the unmarked positions

The monad's walking rule (experiment 018e) makes this possible:
  k_next = k_current + p  (same rail, same factor p)
  Walking by prime p visits every composite that has p as a factor.
"""

import numpy as np
from math import isqrt, log
import time

# ====================================================================
#  CORE FUNCTIONS
# ====================================================================
def rail_of(n):
    if n % 6 == 5: return 'R1'
    if n % 6 == 1: return 'R2'
    return None

def k_of(n):
    if n % 6 == 5: return (n + 1) // 6
    if n % 6 == 1: return (n - 1) // 6
    return None

def from_k_rail(k, rail):
    """Convert (k, rail) back to number."""
    if rail == 'R1': return 6*k - 1
    if rail == 'R2': return 6*k + 1
    return None

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

# ====================================================================
#  1. THE WALKING LATTICE STRUCTURE
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 018w: THE WALKING SIEVE")
print("=" * 70)
print()
print("  1. LATTICE STRUCTURE IN k-SPACE")
print()
print("  Each prime p creates TWO lattices (one per rail):")
print("  - Same-rail lattice:  k = p*m + k(p),  rail = rail(p)")
print("  - Opposite-rail lattice: k = p*m + (p - k(p)), rail = opposite(p)")
print()

# Show lattices for first few primes
primes_rail = [p for p in range(5, 50) if is_prime(p) and p % 2 != 0 and p % 3 != 0]
for p in primes_rail[:5]:
    kp = k_of(p)
    rp = rail_of(p)
    opp = 'R2' if rp == 'R1' else 'R1'
    opp_offset = p - kp

    print(f"  p={p} ({rp}, k={kp})")
    print(f"    Same-rail ({rp}):  k = {p}*m + {kp}")
    same_vals = [from_k_rail(p*m + kp, rp) for m in range(1, 5)]
    print(f"      composites: {same_vals}")

    print(f"    Opp-rail ({opp}):   k = {p}*m + {opp_offset}")
    opp_vals = [from_k_rail(p*m + opp_offset, opp) for m in range(0, 4)]
    print(f"      composites: {opp_vals}")
    print()

# ====================================================================
#  2. THE WALKING SIEVE ALGORITHM
# ====================================================================
print("=" * 70)
print("  2. THE WALKING SIEVE ALGORITHM")
print("=" * 70)
print()

def walking_sieve(limit):
    """Generate all primes on the rails up to `limit` using k-space lattice walking.

    Returns list of primes in [5, limit] that are on R1 or R2.
    Also returns 2 and 3 for completeness.
    """
    # k ranges from 1 to (limit+1)//6
    k_max = (limit + 1) // 6

    # Two sieve arrays: one per rail
    # sieve_R1[k] = False means 6k-1 is composite
    # sieve_R2[k] = False means 6k+1 is composite
    sieve_R1 = np.ones(k_max + 1, dtype=bool)  # True = potentially prime
    sieve_R2 = np.ones(k_max + 1, dtype=bool)

    # For each prime p, walk its two lattices
    for p_idx in range(1, k_max + 1):
        # p_idx is the k-index of the potential prime p
        # First check if p_idx position on either rail is still marked prime

        # R1 candidate: 6*p_idx - 1
        if p_idx <= k_max and sieve_R1[p_idx]:
            p = 6*p_idx - 1
            if p > limit: break
            # p is prime! Walk its lattices to mark composites

            # Same-rail lattice (R1): k = p*m + p_idx, starting at m=2
            # (m=1 gives k=p_idx+p_idx which is 6k-1 = p*7, but we want m=2
            #  to skip p itself... actually m=1 gives k = p+p_idx, value = 6(p+p_idx)-1)
            # Wait: for same rail, offset = k(p) = p_idx
            for k in range(p + p_idx, k_max + 1, p):
                sieve_R1[k] = False

            # Opposite-rail lattice (R2): k = p*m + (p - p_idx), starting at m=0
            opp_offset = p - p_idx
            for k in range(opp_offset, k_max + 1, p):
                if k >= 1:
                    sieve_R2[k] = False

        # R2 candidate: 6*p_idx + 1
        if p_idx <= k_max and sieve_R2[p_idx]:
            p = 6*p_idx + 1
            if p > limit: break
            # p is prime! Walk its lattices

            # Same-rail lattice (R2): k = p*m + p_idx, starting at m=2
            for k in range(p + p_idx, k_max + 1, p):
                sieve_R2[k] = False

            # Opposite-rail lattice (R1): k = p*m + (p - p_idx), starting at m=0
            opp_offset = p - p_idx
            for k in range(opp_offset, k_max + 1, p):
                if k >= 1:
                    sieve_R1[k] = False

    # Collect primes
    primes = [2, 3]
    for k in range(1, k_max + 1):
        if sieve_R1[k]:
            n = 6*k - 1
            if n <= limit and n >= 5:
                primes.append(n)
        if sieve_R2[k]:
            n = 6*k + 1
            if n <= limit and n >= 5:
                primes.append(n)

    return sorted(primes)


def standard_sieve(limit):
    """Standard Sieve of Eratosthenes for comparison."""
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[0] = sieve[1] = False
    for i in range(2, isqrt(limit) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False
    return [i for i in range(limit + 1) if sieve[i]]


# ====================================================================
#  3. VERIFY WALKING SIEVE
# ====================================================================
print("  3. VERIFICATION")
print()

for limit in [100, 1000, 10000, 100000]:
    ws = walking_sieve(limit)
    ss = standard_sieve(limit)
    match = ws == ss
    print(f"  Limit {limit:>7}: walking_sieve={len(ws)} primes, standard={len(ss)}, match={match}")

print()


# ====================================================================
#  4. LATTICE VISUALIZATION
# ====================================================================
print("=" * 70)
print("  4. LATTICE VISUALIZATION (k-space, first 30 positions)")
print("=" * 70)
print()

k_show = 30

# Collect which primes mark which positions
R1_markers = {}  # k -> set of primes that mark it as composite
R2_markers = {}

for p in primes_rail:
    kp = k_of(p)
    rp = rail_of(p)
    opp = 'R2' if rp == 'R1' else 'R1'
    opp_offset = p - kp

    # Same rail
    for m in range(1, k_show // p + 2):
        k = p*m + kp
        if 1 <= k <= k_show:
            if rp == 'R1':
                R1_markers.setdefault(k, set()).add(p)
            else:
                R2_markers.setdefault(k, set()).add(p)

    # Opposite rail
    for m in range(0, k_show // p + 2):
        k = p*m + opp_offset
        if 1 <= k <= k_show:
            if opp == 'R1':
                R1_markers.setdefault(k, set()).add(p)
            else:
                R2_markers.setdefault(k, set()).add(p)

print("  R1 (6k-1):")
print(f"  {'k':>3} {'value':>6} {'status':>8} {'marked by'}")
for k in range(1, k_show + 1):
    val = 6*k - 1
    if k in R1_markers:
        markers = sorted(R1_markers[k])
        print(f"  {k:>3} {val:>6} {'COMP':>8} {markers}")
    else:
        prime_str = "PRIME" if is_prime(val) else "?"
        print(f"  {k:>3} {val:>6} {prime_str:>8}")

print()
print("  R2 (6k+1):")
print(f"  {'k':>3} {'value':>6} {'status':>8} {'marked by'}")
for k in range(1, k_show + 1):
    val = 6*k + 1
    if k in R2_markers:
        markers = sorted(R2_markers[k])
        print(f"  {k:>3} {val:>6} {'COMP':>8} {markers}")
    else:
        prime_str = "PRIME" if is_prime(val) else "?"
        print(f"  {k:>3} {val:>6} {prime_str:>8}")

print()


# ====================================================================
#  5. SPEED BENCHMARK
# ====================================================================
print("=" * 70)
print("  5. SPEED BENCHMARK: WALKING SIEVE vs STANDARD SIEVE")
print("=" * 70)
print()

limits = [10000, 50000, 100000, 500000, 1000000, 5000000, 10000000]

print(f"  {'limit':>10} {'walking':>12} {'standard':>12} {'ratio':>8}")
print(f"  {'':>10} {'(ms)':>12} {'(ms)':>12} {'':>8}")

for limit in limits:
    # Walking sieve
    t0 = time.perf_counter()
    ws = walking_sieve(limit)
    t_walk = (time.perf_counter() - t0) * 1000

    # Standard sieve
    t0 = time.perf_counter()
    ss = standard_sieve(limit)
    t_std = (time.perf_counter() - t0) * 1000

    ratio = t_walk / t_std if t_std > 0 else 1
    match = ws == ss

    print(f"  {limit:>10} {t_walk:>11.2f} {t_std:>11.2f} {ratio:>7.2f}x {'OK' if match else 'ERR'}")

print()


# ====================================================================
#  6. LATTICE DENSITY ANALYSIS
# ====================================================================
print("=" * 70)
print("  6. LATTICE DENSITY: HOW MANY MARKS PER POSITION?")
print("=" * 70)
print()

# Count how many different primes mark each composite position
limit = 10000
k_max = (limit + 1) // 6

R1_count = np.zeros(k_max + 1, dtype=int)
R2_count = np.zeros(k_max + 1, dtype=int)

for p in range(5, isqrt(limit) + 1, 2):
    if p % 3 == 0 or not is_prime(p): continue
    kp = k_of(p)
    rp = rail_of(p)
    opp = 'R2' if rp == 'R1' else 'R1'
    opp_offset = p - kp

    for m in range(1, k_max // p + 2):
        k = p*m + kp
        if 1 <= k <= k_max:
            if rp == 'R1':
                R1_count[k] += 1
            else:
                R2_count[k] += 1

    for m in range(0, k_max // p + 2):
        k = p*m + opp_offset
        if 1 <= k <= k_max:
            if opp == 'R1':
                R1_count[k] += 1
            else:
                R2_count[k] += 1

# Distribution of mark counts
print("  R1 composites: distribution of factor count")
r1_comp_counts = R1_count[1:]
r1_comp_nonzero = r1_comp_counts[r1_comp_counts > 0]
for c in range(0, int(r1_comp_nonzero.max()) + 1):
    n = np.sum(r1_comp_nonzero == c)
    if n > 0:
        print(f"    {c} factors: {n:>5} positions")

print()
print("  R2 composites: distribution of factor count")
r2_comp_counts = R2_count[1:]
r2_comp_nonzero = r2_comp_counts[r2_comp_counts > 0]
for c in range(0, int(r2_comp_nonzero.max()) + 1):
    n = np.sum(r2_comp_nonzero == c)
    if n > 0:
        print(f"    {c} factors: {n:>5} positions")

print()

# Prime positions have zero marks
r1_primes = np.sum(r1_comp_counts == 0)
r2_primes = np.sum(r2_comp_counts == 0)
print(f"  R1 prime positions (unmarked): {r1_primes}")
print(f"  R2 prime positions (unmarked): {r2_primes}")
print(f"  Total rail primes in range: {r1_primes + r2_primes}")
actual = sum(1 for p in range(5, limit+1) if is_prime(p) and p % 2 != 0 and p % 3 != 0)
print(f"  Actual rail primes in range: {actual}")
print(f"  Match: {r1_primes + r2_primes == actual}")
print()


# ====================================================================
#  7. DUAL-RAIL INTERFERENCE IN THE SIEVE
# ====================================================================
print("=" * 70)
print("  7. DUAL-RAIL INTERFERENCE PATTERN")
print("=" * 70)
print()
print("  Composites that are marked by BOTH rails (shared factors):")
print()

# Find positions where both R1 and R2 have marks from the same prime
# This happens for numbers like N = R1_prime * R2_prime (heterodyne composites)
print("  Example: numbers marked on both rails by prime p=5 (R1)")
print()

p = 5
kp = 1  # k_of(5)
# R1 lattice: k = 5m + 1
# R2 lattice: k = 5m + 4 (offset = 5-1=4)
print(f"  R1 lattice (5m+1): ", end="")
r1_ks = [5*m + 1 for m in range(1, 8)]
print([f"k={k}(={6*k-1})" for k in r1_ks])

print(f"  R2 lattice (5m+4): ", end="")
r2_ks = [5*m + 4 for m in range(0, 8)]
print([f"k={k}(={6*k+1})" for k in r2_ks])

print()
print("  Notice: R1 and R2 lattices for the SAME prime are offset")
print("  They NEVER overlap (different rails). But their VALUES")
print("  can be related through the monad's interference rules.")
print()


# ====================================================================
#  8. SIEVE EFFICIENCY: MARKS PER PRIME
# ====================================================================
print("=" * 70)
print("  8. SIEVE EFFICIENCY: MARKS PER PRIME FOUND")
print("=" * 70)
print()

for limit in [1000, 10000, 100000, 1000000]:
    k_max = (limit + 1) // 6

    # Count total marks made
    total_marks = 0
    primes_found = 0

    for p in range(5, isqrt(limit) + 1, 2):
        if p % 3 == 0 or not is_prime(p): continue
        kp = k_of(p)

        # Same rail marks
        for m in range(1, k_max // p + 2):
            k = p*m + kp
            if 1 <= k <= k_max:
                total_marks += 1

        # Opposite rail marks
        opp_offset = p - kp
        for m in range(0, k_max // p + 2):
            k = p*m + opp_offset
            if 1 <= k <= k_max:
                total_marks += 1

    primes_found = sum(1 for p in range(5, limit+1) if is_prime(p) and p % 2 != 0 and p % 3 != 0)
    positions = 2 * k_max  # R1 + R2 positions
    density = primes_found / positions * 100 if positions > 0 else 0

    print(f"  Limit {limit:>8}: {total_marks:>8} marks, {primes_found:>5} primes, "
          f"{positions:>6} positions, prime density {density:.1f}%")

print()


# ====================================================================
#  9. THE MONAD SIEVE: WALKING BY COMPOSITION
# ====================================================================
print("=" * 70)
print("  9. MONAD SIEVE: COMPOSING LATTICES")
print("=" * 70)
print()
print("  Key insight: composite = prime1 * prime2 = intersection of")
print("  prime1's lattice and prime2's lattice.")
print()
print("  Each composite is visited by ALL its prime factors.")
print("  Number of visits = number of distinct prime factors.")
print()
print("  This means the sieve naturally counts prime factors!")
print()

# Show for specific composites
examples = [35, 55, 65, 77, 91, 95, 119, 121, 143, 169]
print(f"  {'N':>5} {'rail':>4} {'k':>4} {'factors':>12} {'# marks':>8} {'visiting primes'}")
for N in examples:
    r = rail_of(N)
    k = k_of(N)
    # Count marks from sieve
    if r == 'R1':
        marks = R1_count[k] if k <= k_max else 0
    else:
        marks = R2_count[k] if k <= k_max else 0

    # Get actual factors
    factors = []
    temp = N
    for d in range(2, isqrt(N) + 1):
        while temp % d == 0:
            factors.append(d)
            temp //= d
    if temp > 1: factors.append(temp)

    # Which primes visit this position?
    visitors = []
    for p in sorted(set(factors)):
        if p > 3 and p % 2 != 0 and p % 3 != 0:
            visitors.append(p)

    fs = ' x '.join(str(f) for f in factors)
    print(f"  {N:>5} {r:>4} {k:>4} {fs:>12} {marks:>8} {visitors}")

print()


# ====================================================================
#  SUMMARY
# ====================================================================
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print("  THE WALKING SIEVE:")
print("  - Pure lattice walking in k-space, no division")
print("  - Each prime p marks a regular lattice with stride p")
print("  - Two lattices per prime (same rail + opposite rail)")
print("  - Unmarked positions are prime")
print("  - Number of marks = number of distinct prime factors")
print()
print("  SPEED vs STANDARD SIEVE:")
print("  - Walking sieve tests only rail positions (2/3 fewer)")
print("  - But has dual-rail bookkeeping overhead")
print("  - Standard sieve uses contiguous array (cache-friendly)")
print("  - Walking sieve uses two arrays with stride-p access")
print()
print("  STRUCTURAL INSIGHTS:")
print("  - Each composite is visited by every prime factor")
print("  - The sieve naturally counts omega(n) (distinct prime factors)")
print("  - Factorization = reading back which lattices contain position k_N")
print("  - This IS the walking rule from experiment 018e, applied as a sieve")
print()
print("Done.")
