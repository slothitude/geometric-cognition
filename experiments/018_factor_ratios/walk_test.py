"""
Experiment 018d: Prime Steps on the Rail — Walking by Adding Factors
=====================================================================
When you add a prime factor p to k_N, you get the k-index of the NEXT
composite on the rail that shares factor p, where the other factor has
advanced one rail position.

For R1xR1->R2: k_N = 6ab - a - b
  k_N + p1 = 6ab - a - b + 6a - 1 = 6a(b+1) - a - (b+1) = k(p1, 6(b+1)-1)
  So adding p1 advances p2 to the next Rail1 position.

For R2xR2->R2: k_N = 6ab + a + b
  k_N + p1 = 6ab + a + b + 6a + 1 = 6a(b+1) + a + (b+1) = k(p1, 6(b+1)+1)
  Same pattern.

For R1xR2->R1: k_N = 6ab + a - b
  k_N + p1 = 6ab + a - b + 6a - 1 = 6a(b+1) + a - (b+1) - 1... hmm
  Need to check cross-rail case separately.
"""

import numpy as np
from math import log, pi, sqrt, gcd

def sieve(N):
    is_prime = np.ones(N, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return is_prime

def get_rail(n):
    if n % 2 == 0 or n % 3 == 0: return 0
    r = n % 6
    return 1 if r == 1 else (-1 if r == 5 else 0)

def rail_k(n):
    rail = get_rail(n)
    if rail == -1: return (n + 1) // 6
    elif rail == +1: return (n - 1) // 6
    return 0

N_MAX = 500_000

print("=" * 70)
print("  EXPERIMENT 018d: PRIME STEPS — WALKING THE RAIL BY ADDING FACTORS")
print("=" * 70)
print()

is_prime_arr = sieve(N_MAX + 10)

spf = np.zeros(N_MAX + 10, dtype=np.int32)
for i in range(2, N_MAX + 10):
    if is_prime_arr[i]:
        spf[i::i] = np.where(spf[i::i] == 0, i, spf[i::i])
spf[0] = 0; spf[1] = 0

def factorize(n):
    factors = []
    while n > 1:
        factors.append(spf[n])
        n //= spf[n]
    return factors

# ====================================================================
#  TEST 1: ALGEBRAIC VERIFICATION — SAME RAIL
# ====================================================================
print("=" * 70)
print("  TEST 1: ALGEBRAIC VERIFICATION — SAME RAIL WALKING")
print("=" * 70)
print()

# Collect same-rail semiprimes
data = {'R1R1': [], 'R2R2': [], 'R1R2': []}

for n in range(25, N_MAX + 1):
    if get_rail(n) == 0 or is_prime_arr[n]: continue
    factors = factorize(n)
    if len(factors) != 2: continue
    unique = set(factors)
    if len(unique) != 2: continue
    p1, p2 = sorted(factors)
    r1, r2 = get_rail(p1), get_rail(p2)
    if r1 == 0 or r2 == 0: continue

    k_n = rail_k(n)
    k_p1, k_p2 = rail_k(p1), rail_k(p2)

    if r1 == -1 and r2 == -1: key = 'R1R1'
    elif r1 == +1 and r2 == +1: key = 'R2R2'
    else: key = 'R1R2'

    data[key].append({
        'n': n, 'p1': p1, 'p2': p2,
        'k_n': k_n, 'k_p1': k_p1, 'k_p2': k_p2,
        'r1': r1, 'r2': r2
    })

# For R1xR1: adding p1 should give k(p1, next Rail1 number after p2)
# next after p2 = 6(k_p2+1) - 1 = 6k_p2 + 5
# expected new k = 6*k_p1*(k_p2+1) - k_p1 - (k_p2+1)
correct_r1r1_p1 = 0
correct_r1r1_p2 = 0
total_r1r1 = 0

for d in data['R1R1']:
    k_new = d['k_n'] + d['p1']
    expected_k = 6 * d['k_p1'] * (d['k_p2'] + 1) - d['k_p1'] - (d['k_p2'] + 1)
    if k_new == expected_k:
        correct_r1r1_p1 += 1

    k_new2 = d['k_n'] + d['p2']
    expected_k2 = 6 * (d['k_p1'] + 1) * d['k_p2'] - (d['k_p1'] + 1) - d['k_p2']
    if k_new2 == expected_k2:
        correct_r1r1_p2 += 1

    total_r1r1 += 1

print(f"  R1xR1: k_N + p1 == k(p1, next Rail1 after p2)?")
print(f"    {correct_r1r1_p1}/{total_r1r1} ({100*correct_r1r1_p1/max(total_r1r1,1):.1f}%)")
print(f"  R1xR1: k_N + p2 == k(next Rail1 after p1, p2)?")
print(f"    {correct_r1r1_p2}/{total_r1r1} ({100*correct_r1r1_p2/max(total_r1r1,1):.1f}%)")

# For R2xR2
correct_r2r2_p1 = 0
correct_r2r2_p2 = 0
total_r2r2 = 0

for d in data['R2R2']:
    k_new = d['k_n'] + d['p1']
    expected_k = 6 * d['k_p1'] * (d['k_p2'] + 1) + d['k_p1'] + (d['k_p2'] + 1)
    if k_new == expected_k:
        correct_r2r2_p1 += 1

    k_new2 = d['k_n'] + d['p2']
    expected_k2 = 6 * (d['k_p1'] + 1) * d['k_p2'] + (d['k_p1'] + 1) + d['k_p2']
    if k_new2 == expected_k2:
        correct_r2r2_p2 += 1

    total_r2r2 += 1

print(f"  R2xR2: k_N + p1 == k(p1, next Rail2 after p2)?")
print(f"    {correct_r2r2_p1}/{total_r2r2} ({100*correct_r2r2_p1/max(total_r2r2,1):.1f}%)")
print(f"  R2xR2: k_N + p2 == k(next Rail2 after p1, p2)?")
print(f"    {correct_r2r2_p2}/{total_r2r2} ({100*correct_r2r2_p2/max(total_r2r2,1):.1f}%)")
print()

# ====================================================================
#  TEST 2: WALK THE RAIL — FOLLOWING THE CHAIN
# ====================================================================
print("=" * 70)
print("  TEST 2: WALKING CHAINS — FOLLOWING PRIME STEPS")
print("=" * 70)
print()
print("  Start with 5x7=35, keep adding 5 to walk along Rail1:")
print()

# 35 = 5x7, Rail1, k=6
# Adding 5 repeatedly walks us through 5xn for increasing n on Rail1/Rail2
n = 35
k = rail_k(n)
print(f"  Start: {n} = 5 x 7, k={k}, rail={'R2' if get_rail(n)==1 else 'R1'}")

for step in range(10):
    k_new = k + 5
    # Check which rail
    n_r1 = 6 * k_new - 1
    n_r2 = 6 * k_new + 1
    # Since we started on Rail1 (6k-1), the result should also be on Rail1
    # if it's R1xR2 pattern, or Rail2 if R1xR1 pattern
    # Check: does 5 divide n_r1 or n_r2?
    if n_r1 % 5 == 0 and n_r1 <= N_MAX:
        other = n_r1 // 5
        other_rail = get_rail(other)
        other_prime = is_prime_arr[other]
        p_marker = "P" if other_prime else "C"
        print(f"  k={k}+5={k_new}: {n_r1} = 5 x {other} ({'R1' if other_rail==-1 else 'R2' if other_rail==1 else '??'}) [{p_marker}]")
        k = k_new
        n = n_r1
    elif n_r2 % 5 == 0 and n_r2 <= N_MAX:
        other = n_r2 // 5
        other_rail = get_rail(other)
        other_prime = is_prime_arr[other]
        p_marker = "P" if other_prime else "C"
        print(f"  k={k}+5={k_new}: {n_r2} = 5 x {other} ({'R1' if other_rail==-1 else 'R2' if other_rail==1 else '??'}) [{p_marker}]")
        k = k_new
        n = n_r2
    else:
        print(f"  k={k}+5={k_new}: no clean factorization by 5 at this position")
        break

print()

# Now walk with 7 from 35
print("  Now walk from 35 by adding 7:")
n = 35
k = rail_k(n)
print(f"  Start: {n} = 5 x 7, k={k}")

for step in range(8):
    k_new = k + 7
    n_r1 = 6 * k_new - 1
    n_r2 = 6 * k_new + 1
    if n_r1 % 7 == 0 and n_r1 <= N_MAX:
        other = n_r1 // 7
        other_prime = is_prime_arr[other]
        p_marker = "P" if other_prime else "C"
        print(f"  k={k}+7={k_new}: {n_r1} = 7 x {other} [{p_marker}]")
        k = k_new
    elif n_r2 % 7 == 0 and n_r2 <= N_MAX:
        other = n_r2 // 7
        other_prime = is_prime_arr[other]
        p_marker = "P" if other_prime else "C"
        print(f"  k={k}+7={k_new}: {n_r2} = 7 x {other} [{p_marker}]")
        k = k_new
    else:
        print(f"  k={k}+7={k_new}: no clean factorization by 7")
        break

print()

# ====================================================================
#  TEST 3: WALK FROM 25 (SQUARE)
# ====================================================================
print("=" * 70)
print("  TEST 3: WALKING FROM 25 (SQUARE) BY ADDING 5")
print("=" * 70)
print()

n = 25
k = rail_k(25)
print(f"  Start: 25 = 5^2, k={k}, Rail2")

for step in range(12):
    k_new = k + 5
    n_r1 = 6 * k_new - 1
    n_r2 = 6 * k_new + 1
    found = False
    for candidate in [n_r2, n_r1]:  # check Rail2 first since 25 is Rail2
        if candidate % 5 == 0 and candidate <= N_MAX and candidate >= 5:
            other = candidate // 5
            other_rail = get_rail(other)
            other_prime = is_prime_arr[other]
            p_marker = "P" if other_prime else "C"
            rail_str = 'R1' if other_rail==-1 else 'R2' if other_rail==1 else 'R0'
            print(f"  k={k}+5={k_new}: {candidate} = 5 x {other} ({rail_str}) [{p_marker}]")
            k = k_new
            found = True
            break
    if not found:
        print(f"  k={k}+5={k_new}: no factorization by 5")
        break

print()

# ====================================================================
#  TEST 4: WALK FROM 49 (SQUARE ON RAIL2)
# ====================================================================
print("=" * 70)
print("  TEST 4: WALKING FROM 49 BY ADDING 7")
print("=" * 70)
print()

n = 49
k = rail_k(49)
print(f"  Start: 49 = 7^2, k={k}, Rail2")

for step in range(10):
    k_new = k + 7
    n_r1 = 6 * k_new - 1
    n_r2 = 6 * k_new + 1
    found = False
    for candidate in [n_r2, n_r1]:
        if candidate % 7 == 0 and candidate <= N_MAX and candidate >= 7:
            other = candidate // 7
            other_prime = is_prime_arr[other]
            p_marker = "P" if other_prime else "C"
            rail_str = 'R1' if get_rail(other)==-1 else 'R2' if get_rail(other)==1 else 'R0'
            print(f"  k={k}+7={k_new}: {candidate} = 7 x {other} ({rail_str}) [{p_marker}]")
            k = k_new
            found = True
            break
    if not found:
        print(f"  k={k}+7={k_new}: no factorization by 7")
        break

print()

# ====================================================================
#  TEST 5: BIDIRECTIONAL WALKING
# ====================================================================
print("=" * 70)
print("  TEST 5: BIDIRECTIONAL — SUBTRACTING PRIME STEPS")
print("=" * 70)
print()
print("  If k_N + p walks forward, does k_N - p walk backward?")
print("  143 = 11x13 (R1xR2->R1, k=24)")
print("  k-11 = 13 -> 6*13-1=77 = 7x11. Backward from 11x13 to 7x11!")
print("  k-13 = 11 -> 6*11-1=65 = 5x13. Backward from 11x13 to 5x13!")
print()

n = 143
k = rail_k(143)
print(f"  Start: 143 = 11 x 13, k={k}")

# Walk backward by 11
for step in range(5):
    k_new = k - 11
    if k_new < 1: break
    n_r1 = 6 * k_new - 1
    n_r2 = 6 * k_new + 1
    for candidate in [n_r1, n_r2]:
        if candidate % 11 == 0 and candidate >= 11:
            other = candidate // 11
            other_prime = is_prime_arr[other]
            p_marker = "P" if other_prime else "C"
            print(f"  k={k}-11={k_new}: {candidate} = 11 x {other} [{p_marker}]")
            k = k_new
            break
    else:
        break

print()
print("  Walk backward by 13:")
k = rail_k(143)
for step in range(5):
    k_new = k - 13
    if k_new < 1: break
    n_r1 = 6 * k_new - 1
    n_r2 = 6 * k_new + 1
    for candidate in [n_r1, n_r2]:
        if candidate % 13 == 0 and candidate >= 13:
            other = candidate // 13
            other_prime = is_prime_arr[other]
            p_marker = "P" if other_prime else "C"
            print(f"  k={k}-13={k_new}: {candidate} = 13 x {other} [{p_marker}]")
            k = k_new
            break
    else:
        break

print()

# ====================================================================
#  TEST 6: THE FULL CHAIN FOR A PRIME
# ====================================================================
print("=" * 70)
print("  TEST 6: FULL CHAIN FOR PRIME p=5 ON RAIL1")
print("=" * 70)
print()
print("  5 x {every rail number in order} — walking by adding 5 each time")
print()

k = rail_k(25)  # Start from 5x5=25
print(f"  {'step':>5} {'k':>6} {'N':>8} {'= 5 x':>8} {'rail':>5} {'prime?':>7}")
print("  " + "-" * 50)

step = 0
while step < 25:
    n_r2 = 6 * k + 1
    n_r1 = 6 * k - 1
    for candidate in [n_r2, n_r1]:
        if candidate % 5 == 0 and candidate <= N_MAX:
            other = candidate // 5
            rail_str = 'R1' if get_rail(other)==-1 else 'R2' if get_rail(other)==1 else 'R0'
            p_marker = "YES" if is_prime_arr[other] else "no"
            print(f"  {step:>5} {k:>6} {candidate:>8} {'5 x':>8}{other:>4} {rail_str:>5} {p_marker:>7}")
            break
    k += 5
    step += 1

print()

# ====================================================================
#  SUMMARY
# ====================================================================
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print("  RULE 4 — THE WALKING RULE:")
print("  Adding a prime factor p to k_N gives the k-index of the next")
print("  composite on the rail that shares factor p.")
print()
print("  k_N + p = k(p x next_number_on_other_factor's_rail)")
print()
print("  This works because:")
print("    k_N = 6ab +/- a +/- b  (composition formula)")
print("    k_N + p = 6a(b+1) +/- a +/- (b+1)  (advance b by one rail position)")
print()
print("  The prime IS the step size. The rail IS the number line.")
print("  Walking forward = advancing the other factor.")
print("  Walking backward = retreating the other factor.")
print()
print("  This gives a bijection between prime multiples and rail positions.")
print()
print("Done.")
