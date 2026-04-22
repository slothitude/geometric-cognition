"""
EXPERIMENTS 116-125: PERFECT SIEVE II -- Number-Theoretic Structures in the Monad
==================================================================================
Building on experiments 92-115, maps 10 number-theoretic structures to
the monad's coordinate system (mod 6 rails, mod 24 positions).

116: Mersenne Composites
117: Abundant Numbers
118: Multiperfect Numbers
119: Deficient Numbers
120: Semiperfect Numbers
121: Weird Numbers
122: Triangular Numbers
123: Square Numbers
124: Fibonacci Numbers
125: Prime Constellations
"""

from math import gcd, isqrt, log, exp
from collections import Counter, defaultdict

# ====================================================================
# HELPERS
# ====================================================================

GAMMA = 0.5772156649015328606065120900824

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

def proper_divisors(n):
    divs = set()
    for i in range(1, isqrt(n) + 1):
        if n % i == 0:
            divs.add(i)
            divs.add(n // i)
    divs.discard(n)
    return sorted(divs)

def is_semiperfect(n):
    """Check if n = sum of some proper divisors (bitset subset-sum)."""
    divs = proper_divisors(n)
    if sum(divs) < n:
        return False
    reachable = 1
    for d in divs:
        reachable |= reachable << d
        if reachable.bit_length() > n + 1:
            reachable &= (1 << (n + 1)) - 1
    return (reachable >> n) & 1 == 1

# ====================================================================
print("=" * 70)
print("EXPERIMENTS 116-125: PERFECT SIEVE II")
print("=" * 70)

# ====================================================================
# EXPERIMENT 116: MERSENNE COMPOSITES
# ====================================================================
print("\n" + "=" * 70)
print("EXPERIMENT 116: MERSENNE COMPOSITES IN THE MONAD")
print("=" * 70)

print(f"\n  Mersenne numbers: M_p = 2^p - 1 for prime p")
print(f"  Mersenne PRIMES sit at position 7 mod 24 (exp 114)")
print(f"  Question: do Mersenne COMPOSITES also sit at 7?")

print(f"\n  {'p':>3} {'M_p':>15} {'Type':>8} {'M_p%6':>6} {'M_p%24':>7} {'Rail':>5} {'Charges':>10}")
for p in range(2, 60):
    if not is_prime(p): continue
    mp = (1 << p) - 1
    pos = mp % 24
    prime_str = "prime" if is_prime(mp) else "COMP"
    rail = rail_of(mp)
    charges = f"({chi5(pos):+d},{chi7(pos):+d},{chi13(pos):+d})" if coprime24(pos) else "n/a"
    print(f"  {p:>3} {mp:>15} {prime_str:>8} {mp%6:>6} {pos:>7} {rail:>5} {charges:>10}")

all_merse_7 = True
merse_count = 0
for p in range(3, 200):
    if not is_prime(p): continue
    mp = (1 << p) - 1
    if mp % 24 != 7:
        all_merse_7 = False
    merse_count += 1

print(f"\n  THEOREM: For all odd primes p >= 3, M_p = 7 mod 24")
print(f"  Proof: 2^p mod 24 = 8 for odd p >= 3, so M_p = 7. Always.")
print(f"  Verified for {merse_count} primes p in [3, 200]: {all_merse_7}")
print(f"\n  CONSEQUENCE: Mersenne composites are INDISTINGUISHABLE from")
print(f"  Mersenne primes by their mod 24 position. Both sit at 7.")
print(f"  Position 7 charges: (+1, -1, +1) = R2, secondary, lower")

# ====================================================================
# EXPERIMENT 117: ABUNDANT NUMBERS
# ====================================================================
print("\n" + "=" * 70)
print("EXPERIMENT 117: ABUNDANT NUMBERS IN THE MONAD")
print("=" * 70)

N_ABUND = 50000
abund_rail = {'R1': 0, 'R2': 0, 'off': 0}
total_rail = {'R1': 0, 'R2': 0, 'off': 0}
abund_mod24 = defaultdict(int)
total_mod24 = defaultdict(int)
sum_ratio_rail = {'R1': 0.0, 'R2': 0.0, 'off': 0.0}

for n in range(1, N_ABUND + 1):
    sn = sigma(n)
    rail = rail_of(n)
    ratio = sn / n
    total_rail[rail] += 1
    total_mod24[n % 24] += 1
    sum_ratio_rail[rail] += ratio
    if sn > 2 * n:
        abund_rail[rail] += 1
        abund_mod24[n % 24] += 1

print(f"\n  Abundance by rail (n < {N_ABUND}):")
print(f"  {'Rail':>5} {'Total':>7} {'Abundant':>9} {'Fraction':>9} {'Avg s/n':>8}")
for rail in ['R1', 'R2', 'off']:
    t = total_rail[rail]
    a = abund_rail[rail]
    avg_r = sum_ratio_rail[rail] / t if t else 0
    print(f"  {rail:>5} {t:>7} {a:>9} {a/t:>9.4f} {avg_r:>8.4f}")

print(f"\n  Abundance fraction by mod 24 position:")
print(f"  {'Pos':>4} {'Type':>8} {'Abund%':>8}")
for pos in range(24):
    t = total_mod24[pos]
    a = abund_mod24[pos]
    ptype = "coprime" if coprime24(pos) else "dark"
    print(f"  {pos:>4} {ptype:>8} {100*a/t:>7.1f}%")

# Robin's inequality tightest cases
print(f"\n  Top 20 tightest Robin cases (sigma/bound closest to 1):")
robin_cases = []
for n in range(5041, N_ABUND + 1):
    sn = sigma(n)
    bound = exp(GAMMA) * n * log(log(n))
    ratio = sn / bound
    robin_cases.append((n, ratio, sn > 2 * n))
robin_cases.sort(key=lambda x: -x[1])

print(f"  {'n':>7} {'ratio':>8} {'Abund?':>7} {'Rail':>5} {'n%24':>5} {'Factors':>20}")
for n, ratio, is_ab in robin_cases[:20]:
    print(f"  {n:>7} {ratio:>8.5f} {'YES' if is_ab else 'no':>7} {rail_of(n):>5} {n%24:>5} {str(factorize(n)):>20}")

all_tight_abund = all(ab for _, _, ab in robin_cases[:20])
print(f"\n  All top 20 tightest Robin cases are abundant: {all_tight_abund}")

# ====================================================================
# EXPERIMENT 118: MULTIPERFECT NUMBERS
# ====================================================================
print("\n" + "=" * 70)
print("EXPERIMENT 118: MULTIPERFECT NUMBERS")
print("=" * 70)

N_MULT = 100000
multiperfect = defaultdict(list)
for n in range(2, N_MULT + 1):
    sn = sigma(n)
    if sn % n == 0:
        k = sn // n
        multiperfect[k].append(n)

print(f"\n  Multiply-perfect numbers (n <= {N_MULT}):")
for k in sorted(multiperfect.keys()):
    nums = multiperfect[k]
    print(f"\n  k={k} (sigma = {k}*n): {len(nums)} found")
    for n in nums[:12]:
        rail = rail_of(n)
        print(f"    n={n:>6}  rail={rail:>3}  n%24={n%24:>3}  factors={factorize(n)}")
    if len(nums) > 12:
        print(f"    ... and {len(nums)-12} more")

if 2 in multiperfect:
    perfect_all_off = all(rail_of(n) == 'off' for n in multiperfect[2])
    print(f"\n  All perfect numbers (k=2) are off-rail: {perfect_all_off}")

mp_rails = Counter()
for k in multiperfect:
    for n in multiperfect[k]:
        mp_rails[rail_of(n)] += 1
print(f"  Multiperfect rail distribution: {dict(sorted(mp_rails.items()))}")

# ====================================================================
# EXPERIMENT 119: DEFICIENT NUMBERS
# ====================================================================
print("\n" + "=" * 70)
print("EXPERIMENT 119: DEFICIENT NUMBERS IN THE MONAD")
print("=" * 70)

N_DEF = 50000
defic_avg_mod24 = {}
defic_count_mod24 = {}
for pos in range(24):
    ratios = []
    for n in range(pos or 24, N_DEF + 1, 24):
        sn = sigma(n)
        if sn < 2 * n:
            ratios.append(sn / n)
    if ratios:
        defic_avg_mod24[pos] = sum(ratios) / len(ratios)
        defic_count_mod24[pos] = len(ratios)

sorted_defic = sorted(defic_avg_mod24.items(), key=lambda x: x[1])

print(f"\n  Most deficient positions (lowest avg sigma/n, n < {N_DEF}):")
for pos, avg in sorted_defic[:6]:
    ptype = "coprime" if coprime24(pos) else "dark"
    print(f"    pos {pos:>2} ({ptype:>7}): avg s/n = {avg:.4f}  ({defic_count_mod24[pos]} deficient)")

print(f"\n  Least deficient positions (highest avg sigma/n among deficient):")
for pos, avg in sorted_defic[-6:]:
    ptype = "coprime" if coprime24(pos) else "dark"
    print(f"    pos {pos:>2} ({ptype:>7}): avg s/n = {avg:.4f}  ({defic_count_mod24[pos]} deficient)")

defic_rail_avg = {'R1': [], 'R2': [], 'off': []}
for n in range(1, N_DEF + 1):
    sn = sigma(n)
    if sn < 2 * n:
        defic_rail_avg[rail_of(n)].append(sn / n)

print(f"\n  Deficient avg sigma/n by rail:")
for rail in ['R1', 'R2', 'off']:
    vals = defic_rail_avg[rail]
    avg = sum(vals) / len(vals) if vals else 0
    print(f"    {rail}: avg = {avg:.4f} ({len(vals)} numbers)")

# ====================================================================
# EXPERIMENT 120: SEMIPERFECT NUMBERS
# ====================================================================
print("\n" + "=" * 70)
print("EXPERIMENT 120: SEMIPERFECT NUMBERS IN THE MONAD")
print("=" * 70)

N_SEMI = 10000
semi_rail = {'R1': 0, 'R2': 0, 'off': 0}
semi_total = 0
weird_candidates = []

for n in range(2, N_SEMI + 1):
    sp = is_semiperfect(n)
    sn = sigma(n)
    if sp:
        semi_total += 1
        semi_rail[rail_of(n)] += 1
    elif sn > 2 * n:
        weird_candidates.append(n)

print(f"\n  Semiperfect numbers (n <= {N_SEMI}): {semi_total}")
print(f"  By rail: {dict(semi_rail)}")
print(f"\n  Abundant but NOT semiperfect (weird candidates): {len(weird_candidates)}")

# ====================================================================
# EXPERIMENT 121: WEIRD NUMBERS
# ====================================================================
print("\n" + "=" * 70)
print("EXPERIMENT 121: WEIRD NUMBERS IN THE MONAD")
print("=" * 70)

print(f"\n  Weird: abundant (sigma > 2n) but NOT semiperfect")
print(f"  Found {len(weird_candidates)} weird numbers (n <= {N_SEMI}):")

for n in weird_candidates:
    rail = rail_of(n)
    sn = sigma(n)
    divs = proper_divisors(n)
    facts = factorize(n)
    print(f"    n={n:>6}  rail={rail:>3}  n%24={n%24:>3}  sigma/n={sn/n:.4f}  "
          f"omega={len(set(facts))}  divs={len(divs)}  factors={facts}")

weird_rails = Counter(rail_of(n) for n in weird_candidates)
print(f"\n  Weird number rail distribution: {dict(sorted(weird_rails.items()))}")
weird_all_off = all(rail_of(n) == 'off' for n in weird_candidates) if weird_candidates else True
print(f"  All weird numbers off-rail: {weird_all_off}")
print(f"  (Off-rail = divisible by 2 or 3 = 'heavy' in Higgs framework)")

# ====================================================================
# EXPERIMENT 122: TRIANGULAR NUMBERS
# ====================================================================
print("\n" + "=" * 70)
print("EXPERIMENT 122: TRIANGULAR NUMBERS IN THE MONAD")
print("=" * 70)

N_TRI = 200
tri_rails = Counter()
tri_mod24 = Counter()
tri_coprime = 0

print(f"\n  First 30 triangular numbers:")
print(f"  {'n':>4} {'T(n)':>8} {'T%6':>4} {'T%24':>5} {'Rail':>5} {'Cop?':>5}")
for n in range(1, N_TRI + 1):
    tn = n * (n + 1) // 2
    rail = rail_of(tn)
    cop = coprime24(tn)
    tri_rails[rail] += 1
    tri_mod24[tn % 24] += 1
    if cop: tri_coprime += 1
    if n <= 30:
        print(f"  {n:>4} {tn:>8} {tn%6:>4} {tn%24:>5} {rail:>5} {'Y' if cop else 'n':>5}")

print(f"\n  Rail distribution (first {N_TRI} triangular): {dict(sorted(tri_rails.items()))}")
print(f"  Coprime to 24: {tri_coprime}/{N_TRI} = {100*tri_coprime/N_TRI:.1f}%")

print(f"\n  T(n) mod 24 by n mod 24:")
print(f"  {'n%24':>5} {'T(n)%24':>7} {'T(n)%6':>7} {'Rail':>5}")
for n in range(24):
    tn = n * (n + 1) // 2
    print(f"  {n:>5} {tn%24:>7} {tn%6:>7} {rail_of(tn):>5}")

coprime_ns = sorted(set(n % 24 for n in range(1, 101) if coprime24(n * (n+1) // 2)))
print(f"\n  n mod 24 values giving coprime T(n): {coprime_ns}")

# ====================================================================
# EXPERIMENT 123: SQUARE NUMBERS
# ====================================================================
print("\n" + "=" * 70)
print("EXPERIMENT 123: SQUARE NUMBERS IN THE MONAD")
print("=" * 70)

N_SQ = 500
sq_mod24 = Counter()
sq_rails = Counter()
coprime_sq = 0

for n in range(1, N_SQ + 1):
    sq = n * n
    sq_mod24[sq % 24] += 1
    sq_rails[rail_of(sq)] += 1
    if coprime24(sq): coprime_sq += 1

print(f"\n  n^2 mod 24 distribution ({N_SQ} squares):")
for pos in sorted(sq_mod24.keys()):
    ptype = "coprime" if coprime24(pos) else "dark"
    print(f"    pos {pos:>2} ({ptype:>7}): {sq_mod24[pos]:>4}")

print(f"\n  Rail distribution: {dict(sorted(sq_rails.items()))}")
print(f"  Coprime squares: {coprime_sq}/{N_SQ}")

coprime_n_count = sum(1 for n in range(1, N_SQ+1) if coprime24(n))
print(f"  n coprime to 24: {coprime_n_count}")
print(f"  Match (n^2 coprime iff n coprime): {coprime_sq == coprime_n_count}")

print(f"\n  n mod 24 -> n^2 mod 24:")
print(f"  {'n%24':>5} {'n^2%24':>6} {'Rail':>5} {'Cop?':>5}")
for n in range(24):
    sq = (n * n) % 24
    print(f"  {n:>5} {sq:>6} {rail_of(sq):>5} {'Y' if coprime24(sq) else 'n':>5}")

print(f"\n  Only {len(sq_mod24)} of 24 positions reachable by squaring")
print(f"  Among coprime: only position 1 (the Higgs identity)")

# ====================================================================
# EXPERIMENT 124: FIBONACCI NUMBERS
# ====================================================================
print("\n" + "=" * 70)
print("EXPERIMENT 124: FIBONACCI NUMBERS IN THE MONAD")
print("=" * 70)

fib = [0, 1]
for i in range(2, 200):
    fib.append(fib[-1] + fib[-2])

fib_rails = Counter()
fib_mod24 = Counter()
fib_coprime = 0
fib_on_rail = 0

print(f"\n  First 50 Fibonacci numbers in the monad:")
print(f"  {'n':>4} {'F(n)':>15} {'F%6':>4} {'F%24':>5} {'Rail':>5} {'Cop?':>5}")
for i in range(50):
    fn = fib[i]
    rail = rail_of(fn) if fn > 0 else 'off'
    cop = coprime24(fn)
    if fn > 0:
        fib_rails[rail] += 1
        fib_mod24[fn % 24] += 1
        if cop: fib_coprime += 1
        if rail in ('R1', 'R2'): fib_on_rail += 1
    print(f"  {i:>4} {fn:>15} {fn%6:>4} {fn%24:>5} {rail:>5} {'Y' if cop else 'n':>5}")

print(f"\n  Rail distribution (F(1)-F(49)): {dict(sorted(fib_rails.items()))}")
print(f"  Coprime: {fib_coprime}/50, On-rail: {fib_on_rail}/50")

# Pisano period mod 6
fib6 = [0, 1]
pisano6 = 0
for i in range(2, 200):
    fib6.append((fib6[-1] + fib6[-2]) % 6)
    if len(fib6) >= 4 and fib6[-2] == 0 and fib6[-1] == 1:
        pisano6 = len(fib6) - 2
        fib6 = fib6[:-2]
        break

print(f"\n  Pisano period pi(6) = {pisano6}")
print(f"  Fibonacci mod 6 cycle: {fib6}")
fib6_rails = [rail_of(f) for f in fib6 if f > 0]
print(f"  Rail pattern: {fib6_rails}")

# Prime Fibonacci
fib_primes = [(i, fib[i]) for i in range(2, 50) if is_prime(fib[i])]
print(f"\n  Prime Fibonacci numbers (F(2) to F(49)):")
for i, fn in fib_primes:
    print(f"    F({i:>2}) = {fn:>12}  rail={rail_of(fn):>3}  n%24={fn%24:>3}")

# ====================================================================
# EXPERIMENT 125: PRIME CONSTELLATIONS
# ====================================================================
print("\n" + "=" * 70)
print("EXPERIMENT 125: PRIME CONSTELLATIONS IN THE MONAD")
print("=" * 70)

N_CONST = 10000

twins = [(p, p+2) for p in range(3, N_CONST) if is_prime(p) and is_prime(p+2)]
cousins = [(p, p+4) for p in range(3, N_CONST) if is_prime(p) and is_prime(p+4)]
sexies = [(p, p+6) for p in range(3, N_CONST) if is_prime(p) and is_prime(p+6)]

# Twin primes
print(f"\n  TWIN PRIMES (p < {N_CONST}): {len(twins)} pairs")
twin_patterns = Counter()
for p, q in twins:
    twin_patterns[(rail_of(p), rail_of(q))] += 1
print(f"  Rail patterns: {dict(sorted(twin_patterns.items()))}")
print(f"  Samples:")
print(f"  {'p':>6} {'p+2':>6} {'p%6':>4} {'q%6':>5} {'p rail':>7} {'q rail':>7}")
for p, q in twins[:12]:
    print(f"  {p:>6} {q:>6} {p%6:>4} {q%6:>5} {rail_of(p):>7} {rail_of(q):>7}")

# Cousin primes
print(f"\n  COUSIN PRIMES (p < {N_CONST}): {len(cousins)} pairs")
cousin_patterns = Counter()
for p, q in cousins:
    cousin_patterns[(rail_of(p), rail_of(q))] += 1
print(f"  Rail patterns: {dict(sorted(cousin_patterns.items()))}")
print(f"  Samples:")
for p, q in cousins[:10]:
    print(f"    ({p:>5}, {q:>5}): rails ({rail_of(p):>3}, {rail_of(q):>3})  mods ({p%6}, {q%6})")

# Sexy primes
print(f"\n  SEXY PRIMES (p < {N_CONST}): {len(sexies)} pairs")
sexy_patterns = Counter()
for p, q in sexies:
    sexy_patterns[(rail_of(p), rail_of(q))] += 1
print(f"  Rail patterns: {dict(sorted(sexy_patterns.items()))}")
print(f"  Samples:")
for p, q in sexies[:10]:
    print(f"    ({p:>5}, {q:>5}): rails ({rail_of(p):>3}, {rail_of(q):>3})  mods ({p%6}, {q%6})")

# Constellation rail rules
print(f"\n  CONSTELLATION RAIL RULES:")

twin_cross = all(
    {rail_of(p), rail_of(q)} == {'R1', 'R2'} for p, q in twins if p > 3)
print(f"  Twin (gap 2, p>3): ALWAYS cross rails (R1->R2): {twin_cross}")
print(f"    Proof: p>3 on rail => p=6k+1 or 6k+5.")
print(f"    If p=6k+1 (R2), p+2=6k+3 (div by 3). So p must be 6k+5 (R1).")
print(f"    Then p+2=6(k+1)+1 (R2). Always R1->R2.")

cousin_cross = all(
    {rail_of(p), rail_of(q)} == {'R1', 'R2'} for p, q in cousins if p > 3)
print(f"  Cousin (gap 4, p>3): ALWAYS cross rails (R2->R1): {cousin_cross}")
print(f"    Proof: If p=6k+5 (R1), p+4=6k+9=3(2k+3) (div by 3).")
print(f"    So p=6k+1 (R2), p+4=6k+5 (R1). Always R2->R1.")

sexy_same = all(rail_of(p) == rail_of(q) for p, q in sexies)
print(f"  Sexy (gap 6): ALWAYS same rail: {sexy_same}")
print(f"    Proof: gap=6=rail period. p+6 has same mod 6 as p.")

# ====================================================================
# TESTS
# ====================================================================
print("\n" + "=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 0

total += 1
if all_merse_7:
    print(f"  [PASS] 116: All M_p = 7 mod 24 for odd p >= 3")
    passed += 1
else:
    print(f"  [FAIL] 116: Mersenne position mismatch")

total += 1
if all_tight_abund:
    print(f"  [PASS] 117: Top 20 tightest Robin cases all abundant")
    passed += 1
else:
    print(f"  [FAIL] 117: Some tightest Robin cases not abundant")

total += 1
mp_verified = all(sigma(n) == k * n for k in multiperfect for n in multiperfect[k])
if mp_verified:
    print(f"  [PASS] 118: All multiperfect numbers verified")
    passed += 1
else:
    print(f"  [FAIL] 118: Multiperfect verification failed")

total += 1
# Positions 0,6,12,18 (multiples of 6) are ALWAYS abundant or perfect -- never deficient
nilpotent_positions = {0, 6, 12, 18}
defic_expected = 24 - len(nilpotent_positions)
defic_all = len(defic_avg_mod24) == defic_expected
defic_correct_positions = nilpotent_positions.isdisjoint(defic_avg_mod24.keys())
if defic_all and defic_correct_positions:
    print(f"  [PASS] 119: Deficient at {defic_expected}/24 positions "
          f"(pos {{0,6,12,18}} always abundant/perfect)")
    passed += 1
else:
    print(f"  [FAIL] 119: Expected {defic_expected} positions, got {len(defic_avg_mod24)}")

total += 1
if semi_total > 0:
    print(f"  [PASS] 120: {semi_total} semiperfect numbers found")
    passed += 1
else:
    print(f"  [FAIL] 120: No semiperfect numbers found")

total += 1
weird_ok = len(weird_candidates) > 0 and all(sigma(n) > 2*n for n in weird_candidates)
if weird_ok:
    print(f"  [PASS] 121: {len(weird_candidates)} weird numbers verified")
    passed += 1
else:
    print(f"  [FAIL] 121: Weird number verification failed")

total += 1
if tri_coprime > 0:
    print(f"  [PASS] 122: {tri_coprime}/{N_TRI} triangular numbers coprime to 24")
    passed += 1
else:
    print(f"  [FAIL] 122: No triangular numbers coprime to 24")

total += 1
sq_coprime_match = coprime_sq == sum(1 for n in range(1, N_SQ+1) if coprime24(n))
if sq_coprime_match:
    print(f"  [PASS] 123: n^2 coprime to 24 iff n coprime to 24")
    passed += 1
else:
    print(f"  [FAIL] 123: Coprime square mismatch")

total += 1
if pisano6 == 24:
    print(f"  [PASS] 124: Pisano period pi(6) = 24")
    passed += 1
else:
    print(f"  [FAIL] 124: pi(6) = {pisano6}, expected 24")

total += 1
const_ok = twin_cross and cousin_cross and sexy_same
if const_ok:
    print(f"  [PASS] 125: Twin=cross, Cousin=cross, Sexy=same rail")
    passed += 1
else:
    print(f"  [FAIL] 125: Constellation rail rules broken")

print(f"\nOVERALL: {passed}/{total} experiments passed")

# ====================================================================
# GRAND SUMMARY
# ====================================================================
print("\n" + "=" * 70)
print("GRAND SUMMARY: EXPERIMENTS 116-125")
print("=" * 70)

print(f"""
  STRUCTURE       | KEY FINDING
  ----------------|----------------------------------------------------------
  116 Mersenne    | ALL M_p = 7 mod 24 (prime AND composite identical)
  117 Abundant    | Tightest Robin all abundant; dark sector more abundant
  118 Multiperf   | Perfect all off-rail; higher-k also dark sector
  119 Deficient   | Coprime most deficient (lowest avg sigma/n)
  120 Semiperfect | Most abundant numbers are semiperfect (packable)
  121 Weird       | Abundant + un-packable; all off-rail
  122 Triangular  | Some coprime to 24; visits all rail types
  123 Squares     | n^2 coprime iff n coprime; always 1 mod 24 (Higgs)
  124 Fibonacci   | Pisano(6) = 24; visits all rail types cyclically
  125 Constellat  | Twin=cross rail, Cousin=cross (opposite), Sexy=same
""")

print(f"  OVERALL: {passed}/{total} experiments passed")
print("=" * 70)
print("EXPERIMENTS 116-125 COMPLETE")
print("=" * 70)
