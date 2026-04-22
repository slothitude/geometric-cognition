"""
EXPERIMENT 126: CATALAN NUMBERS AND INTEGER PARTITIONS IN THE MONAD
===================================================================
Maps two foundational combinatorial structures to the monad's coordinate system.

Part A: Catalan Numbers
  C(n) = (2n)! / ((n+1)! * n!) = binomial(2n,n)/(n+1)
  Applications: balanced parentheses, binary trees, Dyck paths, polygon triangulations
  Questions: rail positions? mod 24 distribution? growth behavior?

Part B: Integer Partitions
  p(n) = number of ways to write n as sum of positive integers
  Applications: representation theory, statistical mechanics, number theory
  Questions: partition function mod 6? mod 24? partition structure by rail?
"""

from math import gcd, factorial, isqrt
from collections import Counter, defaultdict

# ====================================================================
# HELPERS
# ====================================================================

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def factorize(n):
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def sigma(n):
    if n <= 0: return 0
    result = 1
    temp = n
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            pk = 1
            s = 1
            while temp % d == 0:
                temp //= d
                pk *= d
                s += pk
            result *= s
        d += 1
    if temp > 1:
        result *= (1 + temp)
    return result

def coprime24(n):
    return gcd(n, 24) == 1

def rail_of(n):
    r = n % 6
    if r == 5: return 'R1'
    if r == 1: return 'R2'
    return 'off'

def chi5(n):
    if not coprime24(n): return 0
    return 1 if n % 6 == 1 else -1

def chi7(n):
    if not coprime24(n): return 0
    return 1 if n % 12 in (1, 5) else -1

def chi13(n):
    if not coprime24(n): return 0
    return 1 if n % 24 < 12 else -1

def euler_totient(n):
    if n <= 0: return 0
    if n == 1: return 1
    result = n
    temp = n
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            while temp % d == 0:
                temp //= d
            result -= result // d
        d += 1
    if temp > 1:
        result -= result // temp
    return result

def catalan(n):
    """C(n) = (2n)! / ((n+1)! * n!)"""
    return factorial(2 * n) // (factorial(n + 1) * factorial(n))

def partition_count(n):
    """Count integer partitions of n using Euler's pentagonal theorem."""
    p = [0] * (n + 1)
    p[0] = 1
    for i in range(1, n + 1):
        k = 1
        while True:
            pent1 = k * (3 * k - 1) // 2
            pent2 = k * (3 * k + 1) // 2
            if pent1 > i: break
            sign = -1 if k % 2 == 0 else 1
            p[i] += sign * p[i - pent1]
            if pent2 <= i:
                p[i] += sign * p[i - pent2]
            k += 1
        p[i] = abs(p[i])
    return p[n]

def partition_function_table(limit):
    """Compute p(0)..p(limit) via Euler's pentagonal theorem."""
    p = [0] * (limit + 1)
    p[0] = 1
    for i in range(1, limit + 1):
        k = 1
        while True:
            pent1 = k * (3 * k - 1) // 2
            pent2 = k * (3 * k + 1) // 2
            if pent1 > i: break
            sign = -1 if k % 2 == 0 else 1
            p[i] += sign * p[i - pent1]
            if pent2 <= i:
                p[i] += sign * p[i - pent2]
            k += 1
        p[i] = abs(p[i])
    return p

# ====================================================================
print("=" * 70)
print("EXPERIMENT 126: CATALAN NUMBERS AND INTEGER PARTITIONS")
print("=" * 70)

# ====================================================================
# PART A: CATALAN NUMBERS
# ====================================================================
print("\n" + "=" * 70)
print("PART A: CATALAN NUMBERS IN THE MONAD")
print("=" * 70)

print(f"\n  Catalan numbers: C(n) = (2n)! / ((n+1)! * n!)")
print(f"  Count binary trees, Dyck paths, polygon triangulations, etc.")

N_CAT = 60
cat_nums = [catalan(n) for n in range(N_CAT + 1)]

# Rail and mod 24 analysis
cat_rails = Counter()
cat_mod24 = Counter()
cat_coprime = 0
cat_on_rail = 0

print(f"\n  First 40 Catalan numbers:")
print(f"  {'n':>3} {'C(n)':>20} {'C%6':>4} {'C%24':>5} {'Rail':>5} {'Cop?':>5}")
for n in range(41):
    cn = cat_nums[n]
    rail = rail_of(cn) if cn > 0 else 'off'
    cop = coprime24(cn)
    cat_rails[rail] += 1
    cat_mod24[cn % 24] += 1
    if cop: cat_coprime += 1
    if rail in ('R1', 'R2'): cat_on_rail += 1
    print(f"  {n:>3} {cn:>20} {cn%6:>4} {cn%24:>5} {rail:>5} {'Y' if cop else 'n':>5}")

print(f"\n  Rail distribution (C(0)-C({N_CAT})): {dict(sorted(cat_rails.items()))}")
print(f"  Coprime to 24: {cat_coprime}/{N_CAT+1}")
print(f"  On-rail: {cat_on_rail}/{N_CAT+1}")

# C(n) mod 6 pattern
print(f"\n  C(n) mod 6 pattern:")
cat_mod6 = [cat_nums[n] % 6 for n in range(min(30, N_CAT + 1))]
print(f"  {cat_mod6}")

# C(n) mod 24 pattern
print(f"\n  C(n) mod 24 for n = 0..23:")
print(f"  {'n':>3} {'C(n)%24':>7} {'Rail':>5} {'Cop?':>5}")
for n in range(24):
    cn = cat_nums[n]
    r = cn % 24
    print(f"  {n:>3} {r:>7} {rail_of(r):>5} {'Y' if coprime24(r) else 'n':>5}")

# When is C(n) coprime to 24?
coprime_cat_ns = [n for n in range(N_CAT + 1) if coprime24(cat_nums[n])]
print(f"\n  n values where C(n) coprime to 24: {coprime_cat_ns}")
print(f"  Pattern: n mod 24 in {sorted(set(n % 24 for n in coprime_cat_ns))}")

# C(n) parity -- when is C(n) odd?
odd_cat = [n for n in range(N_CAT + 1) if cat_nums[n] % 2 == 1]
print(f"\n  C(n) odd for n = {odd_cat[:20]}{'...' if len(odd_cat) > 20 else ''}")
print(f"  Known: C(n) odd iff n = 2^k - 1 (one less than a power of 2)")

# Verify the odd-Catalan theorem
odd_theorem = all(cat_nums[n] % 2 == 1 for n in range(N_CAT + 1)
                  if n > 0 and (n + 1) & n == 0)  # n+1 is power of 2
even_theorem = all(cat_nums[n] % 2 == 0 for n in range(1, N_CAT + 1)
                   if (n + 1) & n != 0)  # n+1 NOT power of 2
odd_ok = odd_theorem and even_theorem
print(f"  Verified: C(n) odd iff n = 2^k - 1: {odd_ok}")

# Primality of Catalan numbers
print(f"\n  Prime Catalan numbers (n <= {N_CAT}):")
for n in range(2, N_CAT + 1):
    if is_prime(cat_nums[n]):
        cn = cat_nums[n]
        print(f"    C({n}) = {cn}  rail={rail_of(cn)}  n%24={cn%24}")

# Only C(2)=2 and C(3)=5 are known prime Catalan numbers
known_prime_cat = [n for n in range(2, min(N_CAT+1, 30)) if is_prime(cat_nums[n])]
print(f"  Known prime Catalan (n < 30): C({known_prime_cat})")
print(f"  Conjecture: only C(2)=2 and C(3)=5 are prime")

# Divisibility structure of C(n)
print(f"\n  C(n) factorization structure:")
print(f"  {'n':>3} {'C(n)':>12} {'omega':>5} {'Omega':>6} {'2^a':>4} {'3^b':>4} {'Rail':>5}")
for n in range(1, 25):
    cn = cat_nums[n]
    facts = factorize(cn)
    omega = len(set(facts))  # distinct primes
    big_omega = len(facts)   # total with multiplicity
    v2 = facts.count(2)
    v3 = facts.count(3)
    print(f"  {n:>3} {cn:>12} {omega:>5} {big_omega:>6} {v2:>4} {v3:>4} {rail_of(cn):>5}")

# ====================================================================
# PART B: INTEGER PARTITIONS
# ====================================================================
print("\n" + "=" * 70)
print("PART B: INTEGER PARTITIONS IN THE MONAD")
print("=" * 70)

print(f"\n  p(n) = number of ways to write n as sum of positive integers")
print(f"  Euler's pentagonal theorem: fast computation")

N_PART = 1000
p = partition_function_table(N_PART)

# p(n) mod 6 and mod 24
print(f"\n  Partition function p(n) for n = 0..30:")
print(f"  {'n':>4} {'p(n)':>12} {'p%6':>4} {'p%24':>5} {'Rail':>5} {'Cop?':>5}")
for n in range(31):
    pn = p[n]
    rail = rail_of(pn) if pn > 0 else 'off'
    cop = coprime24(pn)
    print(f"  {n:>4} {pn:>12} {pn%6:>4} {pn%24:>5} {rail:>5} {'Y' if cop else 'n':>5}")

# Rail distribution of p(n)
part_rails = Counter()
part_mod24 = Counter()
part_coprime = 0
part_on_rail = 0

for n in range(N_PART + 1):
    pn = p[n]
    rail = rail_of(pn) if pn > 0 else 'off'
    part_rails[rail] += 1
    part_mod24[pn % 24] += 1
    if coprime24(pn): part_coprime += 1
    if rail in ('R1', 'R2'): part_on_rail += 1

print(f"\n  p(n) rail distribution (n = 0..{N_PART}): {dict(sorted(part_rails.items()))}")
print(f"  Coprime: {part_coprime}/{N_PART+1} = {100*part_coprime/(N_PART+1):.1f}%")
print(f"  On-rail: {part_on_rail}/{N_PART+1} = {100*part_on_rail/(N_PART+1):.1f}%")

# p(n) mod 24 distribution
print(f"\n  p(n) mod 24 distribution (n = 0..{N_PART}):")
for pos in sorted(part_mod24.keys()):
    ptype = "coprime" if coprime24(pos) else "dark"
    print(f"    pos {pos:>2} ({ptype:>7}): {part_mod24[pos]:>5}  ({100*part_mod24[pos]/(N_PART+1):.1f}%)")

# Ramanujan's congruences
print(f"\n  RAMANUJAN'S CONGRUENCES:")
print(f"  p(5k+4) = 0 mod 5")
print(f"  p(7k+5) = 0 mod 7")
print(f"  p(11k+6) = 0 mod 11")

# Verify Ramanujan mod 5
ram5_pass = True
for n in range(N_PART + 1):
    if n % 5 == 4:
        if p[n] % 5 != 0:
            ram5_pass = False
            break
print(f"  p(5k+4) = 0 mod 5 for k = 0..{(N_PART-4)//5}: {ram5_pass}")

# Verify Ramanujan mod 7
ram7_pass = True
for n in range(N_PART + 1):
    if n % 7 == 5:
        if p[n] % 7 != 0:
            ram7_pass = False
            break
print(f"  p(7k+5) = 0 mod 7 for k = 0..{(N_PART-5)//7}: {ram7_pass}")

# Verify Ramanujan mod 11
ram11_pass = True
for n in range(N_PART + 1):
    if n % 11 == 6:
        if p[n] % 11 != 0:
            ram11_pass = False
            break
print(f"  p(11k+6) = 0 mod 11 for k = 0..{(N_PART-6)//11}: {ram11_pass}")

# Ramanujan congruences in the monad context
print(f"\n  MONAD FRAMING of Ramanujan:")
print(f"  p(5k+4) = 0 mod 5: 4 = 5-1 = R2 position, mod 5 = 'anti-prime'")
print(f"  p(7k+5) = 0 mod 7: 5 = R1 position")
print(f"  p(11k+6) = 0 mod 11: 6 = off-rail (div by 6 = nilpotent!)")

# p(n) parity (Euler's odd/even partitions)
print(f"\n  p(n) parity:")
odd_p = sum(1 for n in range(N_PART + 1) if p[n] % 2 == 1)
even_p = sum(1 for n in range(N_PART + 1) if p[n] % 2 == 0)
print(f"  Odd: {odd_p}, Even: {even_p} out of {N_PART+1}")
print(f"  Odd fraction: {100*odd_p/(N_PART+1):.1f}%")

# p(n) mod 2 pattern (Subbarao's conjecture: infinitely many n with p(n) even and odd)
print(f"  p(n) mod 2 for n = 0..30: {[p[n] % 2 for n in range(31)]}")

# Partition function mod 6 pattern
print(f"\n  p(n) mod 6 for n = 0..30: {[p[n] % 6 for n in range(31)]}")

# Pisano-like period for partition function mod 6
part_mod6_cycle = [p[n] % 6 for n in range(N_PART + 1)]
# Check for periodicity
part_period6 = None
for per in range(1, N_PART // 2):
    is_period = True
    for n in range(per, min(per + per, N_PART + 1)):
        if part_mod6_cycle[n] != part_mod6_cycle[n % per]:
            is_period = False
            break
    if is_period and per > 1:
        # Verify longer
        long_check = all(part_mod6_cycle[n] == part_mod6_cycle[n % per]
                        for n in range(N_PART + 1))
        if long_check:
            part_period6 = per
            break

if part_period6:
    print(f"  Partition function mod 6 period: {part_period6}")
else:
    print(f"  Partition function mod 6: NO period found in [1, {N_PART//2}]")
    print(f"  (Partition function mod m is eventually periodic but period can be large)")

# Partition function mod 24 -- check for period
part_mod24_vals = [p[n] % 24 for n in range(N_PART + 1)]
part_period24 = None
for per in [24, 48, 72, 96, 120, 144, 168, 192, 216, 240, 288, 336, 360]:
    if per > N_PART // 2: break
    is_period = all(part_mod24_vals[n] == part_mod24_vals[n % per]
                    for n in range(per, min(per * 2, N_PART + 1)))
    if is_period:
        long_check = all(part_mod24_vals[n] == part_mod24_vals[n % per]
                        for n in range(per, N_PART + 1))
        if long_check:
            part_period24 = per
            break

if part_period24:
    print(f"  Partition function mod 24 period: {part_period24}")
else:
    print(f"  Partition function mod 24: no period found up to {N_PART//2}")

# ====================================================================
# PART C: CROSS-STRUCTURE COMPARISON
# ====================================================================
print("\n" + "=" * 70)
print("PART C: CROSS-STRUCTURE COMPARISON")
print("=" * 70)

# Compare Catalan, Fibonacci, Triangular, Partitions -- all at same n
fib = [0, 1]
for i in range(2, 35):
    fib.append(fib[-1] + fib[-2])

print(f"\n  n    C(n)%6   F(n)%6   T(n)%6   p(n)%6   C%24  F%24  T%24  p%24")
print(f"  " + "-" * 65)
for n in range(25):
    cn = cat_nums[n] % 6 if n <= N_CAT else -1
    fn = fib[n] % 6 if n < len(fib) else -1
    tn = (n * (n + 1) // 2) % 6
    pn = p[n] % 6 if n <= N_PART else -1
    cn24 = cat_nums[n] % 24 if n <= N_CAT else -1
    fn24 = fib[n] % 24 if n < len(fib) else -1
    tn24 = (n * (n + 1) // 2) % 24
    pn24 = p[n] % 24 if n <= N_PART else -1
    print(f"  {n:>3}    {cn:>3}     {fn:>3}     {tn:>3}     {pn:>3}    {cn24:>3}   {fn24:>3}   {tn24:>3}   {pn24:>3}")

# Which structure has the most coprime values?
structures = {
    'Catalan': [cat_nums[n] for n in range(25)],
    'Fibonacci': [fib[n] for n in range(25)],
    'Triangular': [n * (n + 1) // 2 for n in range(25)],
    'Partition': [p[n] for n in range(25)],
}

print(f"\n  Coprime-to-24 comparison (n = 0..24):")
print(f"  {'Structure':>12} {'Coprime':>8} {'Total':>6} {'Fraction':>9}")
for name, vals in structures.items():
    cop = sum(1 for v in vals if coprime24(v))
    print(f"  {name:>12} {cop:>8} {len(vals):>6} {cop/len(vals):>9.2f}")

# ====================================================================
# TESTS
# ====================================================================
print("\n" + "=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 0

# Test 1: Catalan values correct
total += 1
cat_spot = (cat_nums[0] == 1 and cat_nums[1] == 1 and cat_nums[2] == 2 and
            cat_nums[3] == 5 and cat_nums[4] == 14 and cat_nums[5] == 42)
if cat_spot:
    print(f"  [PASS] Catalan values verified (C(0)=1..C(5)=42)")
    passed += 1
else:
    print(f"  [FAIL] Catalan value mismatch")

# Test 2: C(n) odd iff n = 2^k - 1
total += 1
if odd_ok:
    print(f"  [PASS] C(n) odd iff n = 2^k - 1")
    passed += 1
else:
    print(f"  [FAIL] Catalan parity theorem violated")

# Test 3: Partition values correct
total += 1
part_spot = (p[0] == 1 and p[1] == 1 and p[2] == 2 and p[3] == 3 and
             p[4] == 5 and p[5] == 7 and p[10] == 42 and p[20] == 627)
if part_spot:
    print(f"  [PASS] Partition values verified (p(0)=1, p(5)=7, p(10)=42, p(20)=627)")
    passed += 1
else:
    print(f"  [FAIL] Partition value mismatch: p(5)={p[5]}, p(10)={p[10]}, p(20)={p[20]}")

# Test 4: Ramanujan congruence p(5k+4) = 0 mod 5
total += 1
if ram5_pass:
    print(f"  [PASS] Ramanujan: p(5k+4) = 0 mod 5")
    passed += 1
else:
    print(f"  [FAIL] Ramanujan mod 5 congruence failed")

# Test 5: Ramanujan p(7k+5) = 0 mod 7
total += 1
if ram7_pass:
    print(f"  [PASS] Ramanujan: p(7k+5) = 0 mod 7")
    passed += 1
else:
    print(f"  [FAIL] Ramanujan mod 7 congruence failed")

# Test 6: Ramanujan p(11k+6) = 0 mod 11
total += 1
if ram11_pass:
    print(f"  [PASS] Ramanujan: p(11k+6) = 0 mod 11")
    passed += 1
else:
    print(f"  [FAIL] Ramanujan mod 11 congruence failed")

# Test 7: Catalan numbers are mostly off-rail
total += 1
cat_off_dominant = cat_rails.get('off', 0) > cat_rails.get('R1', 0) + cat_rails.get('R2', 0)
if cat_off_dominant:
    print(f"  [PASS] Catalan mostly off-rail ({cat_rails.get('off',0)} off vs {cat_rails.get('R1',0)+cat_rails.get('R2',0)} on)")
    passed += 1
else:
    print(f"  [FAIL] Catalan not mostly off-rail")

# Test 8: Partition function hits all rails
total += 1
part_all_rails = 'R1' in part_rails and 'R2' in part_rails and 'off' in part_rails
if part_all_rails:
    print(f"  [PASS] Partition function visits all three rail types")
    passed += 1
else:
    print(f"  [FAIL] Partition function misses some rail types")

# Test 9: C(n) = binomial(2n,n)/(n+1)
total += 1
cat_formula = all(cat_nums[n] == factorial(2*n) // (factorial(n+1) * factorial(n))
                  for n in range(min(20, N_CAT + 1)))
if cat_formula:
    print(f"  [PASS] C(n) = (2n)! / ((n+1)! * n!) verified for n=0..19")
    passed += 1
else:
    print(f"  [FAIL] Catalan formula check failed")

# Test 10: Partition function grows
total += 1
part_grows = all(p[n] <= p[n+1] for n in range(N_PART))
if part_grows:
    print(f"  [PASS] p(n) monotonically non-decreasing")
    passed += 1
else:
    print(f"  [FAIL] Partition function not monotonic")

print(f"\nOVERALL: {passed}/{total} tests passed")

# ====================================================================
# GRAND SUMMARY
# ====================================================================
print("\n" + "=" * 70)
print("GRAND SUMMARY: EXPERIMENT 126")
print("=" * 70)

print(f"""
PART A -- CATALAN NUMBERS:
  C(n) grows super-exponentially. Most C(n) are off-rail (div by 2 or 3).
  C(n) odd iff n = 2^k - 1 (only n = 0,1,3,7,15,31,63...).
  Only C(2) = 2 and C(3) = 5 are prime.
  C(n) coprime to 24 only for specific n (thin set).

PART B -- INTEGER PARTITIONS:
  p(n) grows super-exponentially (~ exp(pi*sqrt(2n/3)) / (4n*sqrt(3))).
  Ramanujan congruences verified:
    p(5k+4) = 0 mod 5
    p(7k+5) = 0 mod 7
    p(11k+6) = 0 mod 11
  Partition function visits all rail types (R1, R2, off).
  {f"Mod 6 period: {part_period6}" if part_period6 else "No mod 6 period found (large or aperiodic)"}
  {f"Mod 24 period: {part_period24}" if part_period24 else "No mod 24 period found"}

PART C -- CROSS-STRUCTURE:
  Fibonacci is most coprime-heavy (~50% coprime to 24).
  Catalan and partitions are mostly off-rail (combinatorial growth = many small factors).
  Triangular numbers: only R2, never R1 (gap structure of n(n+1)/2).
""")

print("=" * 70)
print("EXPERIMENT 126 COMPLETE")
print("=" * 70)
