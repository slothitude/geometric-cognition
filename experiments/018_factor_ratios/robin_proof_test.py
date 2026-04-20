"""
Experiment 018o: The Monad Decomposition of Robin's Inequality
==============================================================
Core idea: sigma(n)/n factors into contributions from p=2, p=3, and rail primes.
The monad handles the rail-prime component. If each component is bounded,
then sigma(n) is bounded. This IS the proof strategy.

sigma(n)/n = PROD_{p^k || n} (1 + 1/p + ... + 1/p^k)
           = (2-component) * (3-component) * (rail-prime-component)

Mertens bounds the rail-prime component.
The p=2 and p=3 components have closed-form bounds.
Together they give Robin's inequality.
"""

import numpy as np
from math import log, exp, sqrt, pi
from collections import Counter

EULER_GAMMA = 0.5772156649015329

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def factorize(n):
    """Return dict {prime: exponent}."""
    factors = {}
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def sigma(n):
    s = 0
    for i in range(1, int(sqrt(n)) + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s

def robin_bound(n):
    if n < 16 or log(log(n)) <= 0:
        return float('inf')
    return exp(EULER_GAMMA) * n * log(log(n))

def get_rail(n):
    if n <= 3: return 0
    if n % 2 == 0 or n % 3 == 0: return 0
    k, r = divmod(n, 6)
    if r == 5: return -1
    if r == 1: return 1
    return 0

print("=" * 70)
print("  THE MONAD DECOMPOSITION OF ROBIN'S INEQUALITY")
print("=" * 70)
print()

# ====================================================================
#  1. THE FACTORIZATION OF sigma(n)/n
# ====================================================================
print("  1. sigma(n)/n DECOMPOSED BY PRIME FACTOR")
print()
print("  sigma(n)/n = PROD_{p^k || n} f(p, k)")
print("  where f(p, k) = (1 - p^{-(k+1)}) / (1 - p^{-1})")
print("               = 1 + 1/p + 1/p^2 + ... + 1/p^k")
print()
print("  For the MONAD, we split into three components:")
print("  sigma(n)/n = f(2, k2) * f(3, k3) * PROD_{rail p} f(p, kp)")
print("             = [2-component] * [3-component] * [rail-component]")
print()

def f_component(p, k):
    """Contribution of prime p with exponent k to sigma(n)/n."""
    return (1 - p**(-(k+1))) / (1 - p**(-1))

# Values for small k
print(f"  p=2 component values:")
for k in range(6):
    print(f"    f(2,{k}) = {f_component(2,k):.6f}  (1 + 1/2 + ... + 1/2^{k})")

print()
print(f"  p=3 component values:")
for k in range(5):
    print(f"    f(3,{k}) = {f_component(3,k):.6f}  (1 + 1/3 + ... + 1/3^{k})")

print()
print(f"  p=5 component values (first rail prime, R1 sp=1):")
for k in range(4):
    print(f"    f(5,{k}) = {f_component(5,k):.6f}")

print()
print(f"  Limiting values (k -> infinity):")
print(f"    f(2, inf) = {1/(1-0.5):.6f} = 1/(1-1/2)")
print(f"    f(3, inf) = {1/(1-1/3):.6f} = 1/(1-1/3)")
print(f"    f(5, inf) = {1/(1-1/5):.6f} = 1/(1-1/5)")
print(f"    f(7, inf) = {1/(1-1/7):.6f} = 1/(1-1/7)")
print()

# ====================================================================
#  2. THE MONAD DECOMPOSITION FOR REAL NUMBERS
# ====================================================================
print("  2. MONAD DECOMPOSITION FOR TIGHTEST NUMBERS:")
print()

# Colossally abundant numbers and nearby tight numbers
test_numbers = [2, 3, 4, 6, 12, 24, 60, 120, 360, 720, 2520, 5040,
                10080, 55440, 720720]

print(f"  {'n':>8} {'sig/n':>8} {'ratio':>8} {'f(2)':>6} {'f(3)':>6} {'rail_comp':>10} {'rail_primes':>20}")
for n in test_numbers:
    facts = factorize(n)
    rb = robin_bound(n)
    ratio = sigma(n) / rb if rb != float('inf') else 0

    f2 = f_component(2, facts.get(2, 0))
    f3 = f_component(3, facts.get(3, 0))

    # Rail component
    rail_f = 1.0
    rail_primes = []
    for p, k in sorted(facts.items()):
        if p > 3:
            rail_f *= f_component(p, k)
            rail_primes.append(f"{p}^{k}" if k > 1 else str(p))

    rp_str = '*'.join(rail_primes) if rail_primes else "1"
    print(f"  {n:>8} {sigma(n)/n:>8.4f} {ratio:>8.4f} {f2:>6.4f} {f3:>6.4f} {rail_f:>10.6f} {rp_str:>20}")

print()

# ====================================================================
#  3. BOUNDING EACH COMPONENT
# ====================================================================
print("  3. BOUNDING EACH COMPONENT:")
print()
print("  Component 1: f(2, k2) <= f(2, inf) = 2.0")
print("    This is trivially bounded -- the 2-component never exceeds 2.")
print()
print("  Component 2: f(3, k3) <= f(3, inf) = 1.5")
print("    This is trivially bounded -- the 3-component never exceeds 1.5.")
print()
print("  Component 3: PROD_{rail p^k || n} f(p, k)")
print("    This is where the monad lives. Each rail prime p contributes")
print("    f(p,k) = 1 + 1/p + ... + 1/p^k < 1/(1-1/p) = p/(p-1).")
print()
print("    The PRODUCT of p/(p-1) over all rail primes is Mertens' product:")
print("    PROD_{rail p} p/(p-1) = PROD_{rail p} (1-1/p)^{-1} ~ C * log(x)")
print("    where C = e^gamma / (f(2,inf) * f(3,inf)) = e^gamma / 3")
print()

# Verify the constant
C_mertens = exp(EULER_GAMMA) / (2.0 * 1.5)
print(f"    e^gamma / (f(2)*f(3)) = {exp(EULER_GAMMA):.6f} / {2.0*1.5:.1f} = {C_mertens:.6f}")
print(f"    1/phi(6) * e^gamma = {(1/2) * exp(EULER_GAMMA):.6f}")
print()
print("    Wait -- let's compute this correctly:")
print(f"    Mertens (all primes): PROD p/(p-1) ~ e^gamma * log(x)")
print(f"    Mertens (rail only):  PROD_{{rail}} p/(p-1) ~ e^gamma * log(x) / (2 * 1.5)")
print(f"                        = e^gamma * log(x) / 3")
print(f"                        = {exp(EULER_GAMMA)/3:.6f} * log(x)")
print()

# ====================================================================
#  4. THE KEY INEQUALITY
# ====================================================================
print("  4. THE KEY INEQUALITY:")
print()
print("  sigma(n)/n = f(2,k2) * f(3,k3) * PROD_{rail p^k||n} f(p,k)")
print()
print("  Bounding each factor:")
print("    f(2,k2) <= 2")
print("    f(3,k3) <= 3/2")
print("    f(p,k)  <= p/(p-1) for each rail prime p")
print()
print("  Therefore:")
print("    sigma(n)/n <= 3 * PROD_{rail p|n} p/(p-1)")
print()
print("  Now, PROD_{rail p|n} p/(p-1) <= PROD_{rail p < n} p/(p-1)")
print("                                ~ (e^gamma/3) * log(n)")
print("  (by Mertens' theorem restricted to rail primes)")
print()
print("  Combining:")
print("    sigma(n)/n <= 3 * (e^gamma/3) * log(n)")
print("               = e^gamma * log(n)")
print()
print("  But Robin needs: sigma(n)/n < e^gamma * log(log(n))")
print()
print("  We got:          sigma(n)/n <= e^gamma * log(n)")
print()
print("  This is TOO WEAK by a factor of log(n)/log(log(n)).")
print("  The problem: we used the INFINITE exponent bound f(p,k) <= p/(p-1),")
print("  which overestimates sigma(n)/n for large n.")
print()
print("  THE FIX: for Robin's bound, we need the EXPONENT CONSTRAINT.")
print("  For the k-th prime p_k, the exponent in n satisfies k <= log(n)/log(p_k).")
print("  This means f(p,k) is MUCH smaller than p/(p-1) for large primes.")
print()

# ====================================================================
#  5. THE EXPONENT CONSTRAINT ON THE MONAD
# ====================================================================
print("  5. EXPONENT CONSTRAINTS ON THE MONAD:")
print()
print("  For n with factorization n = p1^a1 * p2^a2 * ...:")
print("    ai <= log(n) / log(pi)")
print()
print("  For the tightest numbers (colossally abundant), the exponents")
print("  are OPTIMALLY chosen to maximize sigma(n)/n. The optimal")
print("  exponent for prime p is roughly: floor(1/(p^epsilon - 1))")
print("  where epsilon = log(log(n))^{-1}.")
print()

# Compute actual exponents for colossally abundant numbers
print("  Actual exponents for colossally abundant numbers:")
print(f"  {'n':>10} {'2':>3} {'3':>3} {'5':>3} {'7':>3} {'11':>3} {'13':>3} {'sig/n':>8} {'bound/ebound':>12}")

ca_numbers = [2, 6, 12, 60, 120, 360, 2520, 5040, 55440, 720720, 1441440]
for n in ca_numbers:
    facts = factorize(n)
    exps = [facts.get(p, 0) for p in [2, 3, 5, 7, 11, 13]]
    sig_ratio = sigma(n) / n
    rb = robin_bound(n)
    ratio = sigma(n) / rb if rb != float('inf') else 0
    print(f"  {n:>10} {exps[0]:>3} {exps[1]:>3} {exps[2]:>3} {exps[3]:>3} {exps[4]:>3} {exps[5]:>3} "
          f"{sig_ratio:>8.4f} {ratio:>12.6f}")

print()

# ====================================================================
#  6. THE MONAD'S WALKING CONSTRAINT AS A BOUND
# ====================================================================
print("  6. WALKING CONSTRAINT -> EXPONENT BOUND:")
print()
print("  On the monad, each prime p creates a walking lattice:")
print("    positions: k_p, k_p+p, k_p+2p, ...")
print("    period: 6 steps on the spiral")
print()
print("  A number n = p^a has DIVISORS 1, p, p^2, ..., p^a")
print("  These correspond to WALKING POSITIONS:")
print("    k_1 = 0 (trivial)")
print("    k_p = rail_k(p)")
print("    k_{p^2} = composition of k_p with k_p")
print("    k_{p^a} = k_p composed a times")
print()
print("  The monad frequency of p^a is:")

# Compute frequency of p^a on the monad
print()
print(f"  {'p':>3} {'a':>3} {'p^a':>10} {'rail':>5} {'sp':>3} {'freq':>6}")
for p in [5, 7, 11, 13]:
    for a in range(1, 5):
        val = p ** a
        rail = get_rail(val)
        if rail != 0:
            k = (val + 1) // 6 if rail == -1 else (val - 1) // 6
            sp = k % 6
            freq = 0.5 if rail == -1 else sp / 6
            rail_label = 'R1' if rail == -1 else 'R2'
        else:
            sp = '-'
            freq = '-'
            rail_label = '---'
        print(f"  {p:>3} {a:>3} {val:>10} {rail_label:>5} {sp:>3} {freq:>6}")

print()

# ====================================================================
#  7. THE INTERFERENCE BOUND ON f(p,k)
# ====================================================================
print("  7. INTERFERENCE BOUND ON f(p,k):")
print()
print("  For a prime p on the monad, p^a has frequency that depends on")
print("  how many times we self-compose p's position.")
print()
print("  f(p,k) = 1 + 1/p + 1/p^2 + ... + 1/p^k")
print("         = (p^{k+1} - 1) / (p^k * (p-1))")
print("         < p / (p-1)")
print()
print("  The INTERFERENCE CONSTRAINT says: the sub-position of p^a")
print("  must follow the composition rules. For R2 x R2 (constructive):")
print("    sp(p^a) = a * sp(p) mod 6")
print()
print("  This means: p^a visits only CERTAIN sub-positions on the monad.")
print("  It cannot appear at arbitrary positions -- it follows a periodic")
print("  orbit determined by sp(p).")
print()
print("  But this constrains WHERE p^a can be, not HOW BIG sigma gets.")
print("  The bound on sigma comes from the SIZE of p, not its position.")
print()

# ====================================================================
#  8. THE REAL BOUND: LOG-LOG DECOMPOSITION
# ====================================================================
print("  8. THE REAL BOUND: DECOMPOSING log(sigma(n)/n)")
print()
print("  Taking logs:")
print("  log(sigma(n)/n) = sum_{p^k||n} log(f(p,k))")
print("                  = sum_{p^k||n} log(1 + 1/p + ... + 1/p^k)")
print("                  < sum_{p|n} log(p/(p-1))")
print("                  = -sum_{p|n} log(1 - 1/p)")
print("                  < sum_{p|n} 1/(p-1)  [since -log(1-x) < x/(1-x)]")
print()

# Check this bound for colossally abundant numbers
print("  Checking the bound sum_{p|n} 1/(p-1) vs log(log(n)):")
print()
print(f"  {'n':>10} {'sig/n':>8} {'sum 1/(p-1)':>12} {'log(log(n))':>12} {'ratio':>8}")

for n in [6, 12, 60, 120, 360, 2520, 5040, 55440, 720720, 1441440, 4324320]:
    facts = factorize(n)
    bound_sum = sum(1.0/(p-1) for p in facts if p > 1)
    loglogn = log(log(n)) if n > 16 else 0
    sig_ratio = sigma(n) / n
    ratio = bound_sum / loglogn if loglogn > 0 else 0
    print(f"  {n:>10} {sig_ratio:>8.4f} {bound_sum:>12.6f} {loglogn:>12.6f} {ratio:>8.4f}")

print()

# ====================================================================
#  9. THE CRITICAL OBSERVATION
# ====================================================================
print("  9. THE CRITICAL OBSERVATION:")
print()
print("  For colossally abundant numbers, sum 1/(p-1) over their prime")
print("  factors is BOUNDED by approximately log(log(n)).")
print()
print("  This is because:")
print("    - Colossally abundant numbers include ALL primes up to some limit")
print("    - sum_{p<x} 1/(p-1) ~ sum_{p<x} 1/p ~ log(log(x))  (Mertens)")
print("    - For n = product of primes up to x, we have n ~ e^x, so x ~ log(n)")
print("    - Therefore sum_{p|n} 1/(p-1) ~ log(log(log(n)))... no wait")
print()
print("  Actually, for n = PROD p^{a_p}, the sum 1/(p-1) over distinct")
print("  prime factors of n is bounded by sum_{p <= p_max} 1/(p-1)")
print("  where p_max is the largest prime factor of n.")
print()
print("  By Mertens: sum_{p <= P} 1/p ~ log(log(P)) + B (Mertens constant)")
print()
print("  And Robin's bound is e^gamma * log(log(n)).")
print()
print("  The gap: sum 1/(p-1) grows like log(log(P)) where P <= n.")
print("  But log(log(n)) also grows like log(log(P)) (slowly).")
print("  The CONSTANT in front is e^gamma, which comes from Mertens.")
print()

# ====================================================================
#  10. THE MONAD-SPECIFIC BOUND
# ====================================================================
print("  10. MONAD-SPECIFIC BOUND ON sigma(n)/n:")
print()

# For numbers whose factors are ALL on the rails (coprime to 6):
# sigma(n)/n = PROD_{rail p^k||n} f(p,k)
# The largest this can be is bounded by Mertens restricted to rail primes

# Find the n (coprime to 6) that maximizes sigma(n)/n
print("  Maximum sigma(n)/n for rail-only numbers (coprime to 6):")
print()

# These are products of rail primes only (no factors of 2 or 3)
# Start with small products of rail primes
rail_primes = [p for p in range(5, 200) if is_prime(p) and get_rail(p) != 0]
rail_r1 = [p for p in rail_primes if get_rail(p) == -1]
rail_r2 = [p for p in rail_primes if get_rail(p) == 1]

# Products of first k rail primes
best_rail_sig = 0
best_rail_n = 0
print(f"  {'k':>3} {'n':>12} {'sig/n':>8} {'ratio':>8} {'factors':>30}")

n_rail = 1
for k in range(1, 16):
    n_rail *= rail_primes[k-1]
    if n_rail > 10**9:
        break
    sr = sigma(n_rail) / n_rail
    rb = robin_bound(n_rail)
    ratio = sigma(n_rail) / rb if rb != float('inf') else 0
    facts = factorize(n_rail)
    fact_str = '*'.join(str(p) for p in sorted(facts.keys()))
    print(f"  {k:>3} {n_rail:>12} {sr:>8.4f} {ratio:>8.4f} {fact_str:>30}")
    if sr > best_rail_sig:
        best_rail_sig = sr
        best_rail_n = n_rail

print()
print(f"  Best rail-only sigma/n = {best_rail_sig:.6f} at n={best_rail_n}")
print(f"  Robin bound at that n = {robin_bound(best_rail_n)/best_rail_n:.6f}")
print(f"  Ratio = {best_rail_sig / (robin_bound(best_rail_n)/best_rail_n):.6f}")
print()

# ====================================================================
#  11. THE MONAD BOUND: SEPARATING R1 AND R2 CONTRIBUTIONS
# ====================================================================
print("  11. R1 vs R2 PRIME CONTRIBUTIONS:")
print()
print("  Rail primes split into R1 (6k-1) and R2 (6k+1).")
print("  On the monad, these compose differently.")
print("  Do R1 and R2 primes contribute equally to sigma(n)/n?")
print()

# Compute Mertens product for R1 primes only and R2 primes only
r1_primes = [p for p in range(5, 10000) if is_prime(p) and get_rail(p) == -1]
r2_primes = [p for p in range(5, 10000) if is_prime(p) and get_rail(p) == 1]

prod_r1 = 1.0
prod_r2 = 1.0
for p in r1_primes:
    prod_r1 *= 1.0 / (1.0 - 1.0/p)
for p in r2_primes:
    prod_r2 *= 1.0 / (1.0 - 1.0/p)

print(f"  PROD_{{R1 p < 10000}} p/(p-1) = {prod_r1:.6f}")
print(f"  PROD_{{R2 p < 10000}} p/(p-1) = {prod_r2:.6f}")
print(f"  Product R1*R2 = {prod_r1*prod_r2:.6f}")
print(f"  PROD_{{all p < 10000, coprime to 6}} p/(p-1) = {prod_r1*prod_r2:.6f}")
print()

# Mertens prediction for rail primes
mertens_rail = exp(EULER_GAMMA) * log(10000) / 3
print(f"  Mertens prediction (rail): e^gamma * log(10000) / 3 = {mertens_rail:.6f}")
print(f"  Actual: {prod_r1*prod_r2:.6f}")
print(f"  Ratio: {prod_r1*prod_r2/mertens_rail:.6f}")
print()

print(f"  R1/R2 split:")
print(f"    R1 product: {prod_r1:.6f} = {prod_r1/(prod_r1*prod_r2)*100:.1f}% of total")
print(f"    R2 product: {prod_r2:.6f} = {prod_r2/(prod_r1*prod_r2)*100:.1f}% of total")
print(f"    R2/R1 ratio: {prod_r2/prod_r1:.6f}")
print(f"    Expected: sqrt(Mertens_rail) each ~ {sqrt(mertens_rail):.6f}")
print()

# ====================================================================
#  12. THE PATH FORWARD: THREE LEMMAS
# ====================================================================
print("=" * 70)
print("  THE PATH FORWARD: THREE LEMMAS TO PROVE RH VIA THE MONAD")
print("=" * 70)
print()
print("  LEMMA 1 (Mertens on the Monad):")
print("    PROD_{rail p < x} p/(p-1) = (e^gamma/3) * log(x) * (1 + o(1))")
print("    STATUS: ESTABLISHED (Mertens' theorem restricted to 6k+/-1)")
print("    This is the monad's L-function at s=1.")
print()
print("  LEMMA 2 (Exponent Constraint):")
print("    For n = PROD p_i^{a_i}, sigma(n)/n = PROD f(p_i, a_i)")
print("    where f(p,a) = (1-p^{-(a+1)})/(1-p^{-1}) < p/(p-1)")
print("    The DIFFERENCE p/(p-1) - f(p,a) = p^{-a}/(p-1)")
print("    For a >= 1, this is at most 1/(p(p-1)) < 1/p^2")
print("    STATUS: ESTABLISHED (elementary)")
print()
print("  LEMMA 3 (The Hard Part - Monad Interference => Robin):")
print("    The interference rules on the monad create a STRUCTURAL")
print("    constraint that forces:")
print("      sigma(n)/n < e^gamma * log(log(n))  for all n >= 5041")
print("    STATUS: OPEN")
print()
print("  What Lemma 3 requires:")
print("    - Show that the monad's walking lattices cover positions")
print("      with bounded 'completeness' (the lattice can't be too dense)")
print("    - Translate this geometric completeness bound into an")
print("      arithmetic bound on sigma(n)/n")
print("    - The bound must equal e^gamma * log(log(n))")
print()
print("  The monad provides the STRUCTURE for this proof:")
print("    - Divisors form a lattice on the 12-position circle")
print("    - The lattice is constrained by interference rules")
print("    - Mertens' theorem gives the L-function bound")
print("    - What's missing: the GEOMETRIC-TO-ANALYTIC bridge")
print()
print("  This bridge would need to express the density of the walking")
print("  lattice in monad coordinates and show it equals the Mertens")
print("  product. The harmonic series (1:2:3:4:5) in the spiral")
print("  might be the key -- it could constrain how quickly the")
print("  product can grow.")
print()

# ====================================================================
#  13. HARMONIC CONSTRAINT TEST
# ====================================================================
print("  13. HARMONIC CONSTRAINT TEST:")
print()
print("  The monad's spiral has harmonic series 1:2:3:4:5 in revolutions.")
print("  Each prime p walks with angular velocity sp*30 deg/step.")
print("  Does this constrain the Mertens product?")
print()

# The Mertens product PROD p/(p-1) over rail primes can be split by sp:
print("  Mertens product by sub-position (sp=0..5):")
print(f"  {'sp':>3} {'freq':>6} {'count':>6} {'product':>12}")

sp_products = {i: 1.0 for i in range(6)}
sp_counts = {i: 0 for i in range(6)}

for p in rail_primes:
    rail = get_rail(p)
    k = (p + 1) // 6 if rail == -1 else (p - 1) // 6
    sp = k % 6
    sp_products[sp] *= 1.0 / (1.0 - 1.0/p)
    sp_counts[sp] += 1

for sp in range(6):
    freq = sp / 6
    print(f"  {sp:>3} {freq:>6.3f} {sp_counts[sp]:>6} {sp_products[sp]:>12.6f}")

print()
print(f"  Product of all sp products: {np.prod(list(sp_products.values())):.6f}")
print(f"  Total Mertens (rail): {prod_r1*prod_r2:.6f}")
print()

# Check if products are related by the harmonic series
prods = [sp_products[sp] for sp in range(6)]
print("  Ratio of adjacent sp products:")
for sp in range(1, 6):
    if prods[sp-1] > 0:
        print(f"    sp={sp}/sp={sp-1}: {prods[sp]/prods[sp-1]:.6f}")

print()

# ====================================================================
#  SUMMARY
# ====================================================================
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print("  The monad decomposition of sigma(n)/n splits into:")
print("    [2-component] * [3-component] * [rail-prime-component]")
print()
print("  Components 1 and 2 are bounded by 2 and 3/2 respectively.")
print("  Component 3 is bounded by Mertens' theorem on rail primes.")
print()
print("  The naive bound gives sigma(n)/n < e^gamma * log(n),")
print("  which is TOO WEAK by a factor of log(n)/log(log(n)).")
print()
print("  To close this gap, we need to show that the EXPONENT")
print("  constraint (ai <= log(n)/log(pi)) converts the Mertens")
print("  product from log(n) to log(log(n)).")
print()
print("  This is equivalent to the well-known fact that the sum")
print("  of reciprocals of primes up to n is ~ log(log(n)),")
print("  which IS Mertens' theorem. The log(log(n)) comes from the")
print("  double-logarithmic growth of the prime harmonic sum.")
print()
print("  THE MONAD'S CONTRIBUTION to a potential RH proof:")
print("    1. Provides the geometric framework (walking lattices)")
print("    2. Decomposes the problem into 3 clean components")
print("    3. Connects the bound to L-functions via Mertens")
print("    4. Identifies the missing piece: geometric -> analytic bridge")
print()
print("  The monad doesn't prove RH. But it shows WHERE the proof")
print("  lives -- in the transition from the monad's geometric")
print("  interference constraints to the analytic bound from")
print("  Mertens' theorem. This is a genuine research direction.")
print()
print("Done.")
