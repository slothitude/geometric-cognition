"""
Experiment 92: Perfect Numbers in the Monad
============================================
Map every known perfect number to the monad's coordinate system.
Find their rail positions, k-indices, sub-positions, chi values.

A perfect number satisfies sigma(n) = 2n.
Even perfect numbers: n = 2^(p-1) * (2^p - 1) where 2^p - 1 is Mersenne prime.
Odd perfect numbers: unknown (none found below 10^1500).

Key question: Where do perfect numbers live in the monad's structure?
"""

from math import gcd, isqrt, log, exp
from fractions import Fraction

GAMMA = 0.5772156649015328606065120900824024310421

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def sigma(n):
    if n <= 0: return 0
    result = 1; temp = n; d = 2
    while d * d <= temp:
        if temp % d == 0:
            p_power = 1; p_sum = 1
            while temp % d == 0:
                temp //= d; p_power *= d; p_sum += p_power
            result *= p_sum
        d += 1
    if temp > 1: result *= (1 + temp)
    return result

def factorize(n):
    factors = []; d = 2
    while d * d <= n:
        while n % d == 0: factors.append(d); n //= d
        d += 1
    if n > 1: factors.append(n)
    return factors

def rail_of(n):
    r = n % 6
    if r == 5: return 'R1'
    if r == 1: return 'R2'
    return f'off-rail(mod6={r})'

def k_of(n):
    if n % 6 == 5: return (n + 1) // 6
    if n % 6 == 1: return (n - 1) // 6
    return None

def sub_pos(n):
    """Sub-position within block of 36: (n-1) // 6 mod 6 for off-rail approx."""
    k = k_of(n)
    if k is not None: return k % 6
    return None

def chi_1(n):
    r = n % 6
    if r == 1: return +1
    if r == 5: return -1
    return 0

def chi_3(n):
    r = n % 12
    if r in [1, 5]: return +1
    if r in [7, 11]: return -1
    return 0

def block_position(n):
    """Position in the 36-block: which of the 12 coprime slots, or which non-coprime slot."""
    return n % 36

def mersenne_prime(p):
    """Check if 2^p - 1 is prime (simple check for small p)."""
    mp = (1 << p) - 1  # 2^p - 1
    return is_prime(mp), mp

def lucas_lehmer(p):
    """Lucas-Lehmer primality test for Mersenne numbers."""
    if p == 2: return True
    mp = (1 << p) - 1
    s = 4
    for _ in range(p - 2):
        s = (s * s - 2) % mp
    return s == 0


# ====================================================================
# SECTION 1: KNOWN PERFECT NUMBERS
# ====================================================================
print("=" * 70)
print("  PERFECT NUMBERS IN THE MONAD")
print("=" * 70)
print()

# All 51 known Mersenne primes (exponents), as of 2024
# We'll generate and analyze the ones we can handle
mersenne_exponents = [
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279,
    2203, 2281, 3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701,
    23209, 44497, 86243, 110503, 132049, 216091, 756839, 859433,
    1257787, 1398269, 2976221, 3021377, 6972593, 13466917, 20996011,
    24036583, 25964951, 30402457, 32582657, 37156667, 42643801,
    43112609, 57885161, 74207281, 77232917, 82589933
]

print(f"  Known Mersenne prime exponents: {len(mersenne_exponents)}")
print()

# Analyze the first several perfect numbers in detail
print("  DETAILED ANALYSIS OF PERFECT NUMBERS:")
print(f"  {'#':>3} {'p':>5} {'n':>20} {'n%6':>4} {'n%12':>5} {'n%36':>5} {'rail':>16} {'chi1':>5} {'chi3':>5} {'M_p%6':>5} {'M_p rail':>8}")
print()

perfect_data = []

for i, p in enumerate(mersenne_exponents[:30]):  # first 30 (manageable size)
    # Mersenne prime
    Mp = (1 << p) - 1  # 2^p - 1

    # Perfect number
    n = (1 << (p - 1)) * Mp  # 2^(p-1) * (2^p - 1)

    # Monad coordinates
    n_mod6 = n % 6
    n_mod12 = n % 12
    n_mod36 = n % 36
    rail = rail_of(n)
    c1 = chi_1(n)
    c3 = chi_3(n)

    # Mersenne prime coordinates
    mp_mod6 = Mp % 6
    mp_rail = rail_of(Mp)

    # Verify perfection
    if n < 10**15:  # only verify small ones
        is_perfect = (sigma(n) == 2 * n)
        verify_str = "VERIFIED" if is_perfect else "ERROR"
    else:
        verify_str = "by construction"

    perfect_data.append({
        'idx': i + 1, 'p': p, 'n': n, 'Mp': Mp,
        'n_mod6': n_mod6, 'n_mod36': n_mod36, 'rail': rail,
        'mp_mod6': mp_mod6, 'mp_rail': mp_rail
    })

    if n < 10**25:  # print manageable numbers
        n_str = str(n)
    else:
        n_str = f"2^{p-1}*(2^{p}-1)"

    print(f"  {i+1:>3} {p:>5} {n_str:>20} {n_mod6:>4} {n_mod12:>5} {n_mod36:>5} {rail:>16} {c1:>5} {c3:>5} {mp_mod6:>5} {mp_rail:>8}")

print()


# ====================================================================
# SECTION 2: THE PATTERN
# ====================================================================
print("=" * 70)
print("  SECTION 2: THE PATTERN")
print("=" * 70)
print()

print("  OBSERVATION 1: Where do perfect numbers live?")
print()

# Count rail positions
rail_counts = {}
for pd in perfect_data:
    r = pd['rail']
    rail_counts[r] = rail_counts.get(r, 0) + 1

for r, count in sorted(rail_counts.items()):
    print(f"    {r}: {count} perfect numbers")

print()
print("  ALL perfect numbers (for p >= 3) are = 4 (mod 6).")
print("  They are OFF-RAIL: divisible by 2, NOT divisible by 3.")
print()
print("  PROOF:")
print("    n = 2^(p-1) * (2^p - 1)")
print("    For odd prime p >= 3:")
print("      2^(p-1) mod 6: p-1 is even, so 2^(p-1) = 4^((p-1)/2)")
print("      4^k mod 6 = 4 for all k >= 1. So 2^(p-1) = 4 (mod 6)")
print("      2^p mod 6: for odd p, 2^p mod 6 = 2. So 2^p - 1 = 1 (mod 6)")
print("      Therefore n = 4 * 1 = 4 (mod 6)")
print()
print("  OBSERVATION 2: All Mersenne primes (for p >= 3) are on R2.")
print("    2^p - 1 = 1 (mod 6) for all odd primes p.")
print("    Proof: 2^p = 2 * 2^(p-1) = 2 * 4^((p-1)/2).")
print("    4^k mod 6 = 4, so 2 * 4^k mod 6 = 8 mod 6 = 2.")
print("    Therefore 2^p - 1 = 1 (mod 6). QED")
print()

# Special case: p=2 gives n=6 (the first perfect number)
print("  SPECIAL CASE: p=2 gives n=6 = 2*3")
print("    6 mod 6 = 0. Divisible by BOTH 2 and 3.")
print("    This is the ONLY perfect number divisible by 3.")
print("    The monad's chi_1(6) = 0, chi_3(6) = 0. Complete null.")
print()

print("  OBSERVATION 3: Position in the 36-block")
print()

# Check n mod 36 for all perfect numbers
mod36_counts = {}
for pd in perfect_data:
    m36 = pd['n_mod36']
    mod36_counts[m36] = mod36_counts.get(m36, 0) + 1

print("    n mod 36 distribution:")
for m, count in sorted(mod36_counts.items()):
    print(f"      n = {m} (mod 36): {count} perfect numbers")

print()

# For p >= 3: n mod 36
# n = 2^(p-1) * (2^p - 1)
# 2^(p-1) mod 36: depends on p-1
# 4^1 = 4, 4^2 = 16, 4^3 = 64 = 28, 4^4 = 256 = 4 (mod 36)
# So 4^k mod 36 cycles with period 3: 4, 16, 28, 4, 16, 28...
# For p-1 = 2k: 2^(p-1) = 4^k. k mod 3 determines the value.
# (2^p - 1) mod 36: need to compute

print("  Computing n mod 36 pattern for Mersenne exponents:")
for pd in perfect_data[:20]:
    p = pd['p']
    if p == 2:
        print(f"    p={p:>5}: n mod 36 = {pd['n_mod36']}")
        continue
    power2 = pow(2, p-1, 36)
    mersenne = (pow(2, p, 36) - 1) % 36
    n_mod36 = (power2 * mersenne) % 36
    k = (p-1) // 2  # exponent for 4^k
    phase = k % 3
    print(f"    p={p:>5}: 2^(p-1) mod 36 = {power2:>2}, M_p mod 36 = {mersenne:>2}, "
          f"n mod 36 = {n_mod36:>2}, 4^(k={k}) phase={phase}")

print()


# ====================================================================
# SECTION 3: SIGMA STRUCTURE OF PERFECT NUMBERS
# ====================================================================
print("=" * 70)
print("  SECTION 3: SIGMA STRUCTURE OF PERFECT NUMBERS")
print("=" * 70)
print()

print("  For perfect n = 2^(p-1) * M_p:")
print("    sigma(n) = sigma(2^(p-1)) * sigma(M_p)")
print("             = (2^p - 1) * (M_p + 1)")
print("             = M_p * (M_p + 1)")
print("             = M_p * 2^p")
print("             = 2 * 2^(p-1) * M_p")
print("             = 2n. QED (perfection)")
print()
print("  In the monad's decomposition:")
print("    sigma(n)/n = sigma(2^(p-1))/2^(p-1) * sigma(M_p)/M_p")
print("               = (2^p - 1)/2^(p-1) * (M_p + 1)/M_p")
print("               = 2 * (1 - 1/2^p) * (1 + 1/M_p)")
print()
print("  For the Mertens bound comparison:")
print("    sigma(n)/n = 2 * (1 - 1/2^p) * (1 + 1/M_p)")
print("    Bound:     e^gamma * ln(ln(n))")
print()

# Compute for small perfect numbers
print(f"  {'p':>5} {'sigma/n':>12} {'2.0':>6} {'bound':>10} {'ratio':>10} {'slack':>10}")
for p in [2, 3, 5, 7, 13, 17, 19, 31]:
    Mp = (1 << p) - 1
    n = (1 << (p - 1)) * Mp
    sn_ratio = 2.0 * (1 - 1.0/(2**p)) * (1 + 1.0/Mp)
    bound = exp(GAMMA) * log(log(n))
    ratio = sn_ratio / bound
    slack = 1.0 - 1.0/(2**p)
    print(f"  {p:>5} {sn_ratio:>12.6f} {'2.0':>6} {bound:>10.4f} {ratio:>10.6f} {slack:>10.6f}")

print()
print("  sigma(n)/n approaches 2 from below as p grows.")
print("  Perfect numbers are FAR from Robin danger -- they're at ratio = 2,")
print("  while Robin's bound is about e^gamma * ln(ln(n)) >> 2 for large n.")
print("  The slack (1 - 1/2^p) is the ONLY thing keeping sigma(n)/n < 2.")
print()


# ====================================================================
# SECTION 4: MONAD COORDINATE MAP
# ====================================================================
print("=" * 70)
print("  SECTION 4: MONAD COORDINATE MAP OF PERFECT NUMBERS")
print("=" * 70)
print()

print("  The 36-block has 12 coprime positions: 1,5,7,11,13,17,19,23,25,29,31,35")
print("  Perfect numbers land at position 4 or 0 (mod 36) -- both non-coprime.")
print()
print("  The monad's chi_1 character gives 0 for ALL perfect numbers.")
print("  They are INVISIBLE to the rail sign character.")
print()
print("  This means:")
print("  1. Perfect numbers have ZERO rail identity")
print("  2. They exist in the 'shadow' between the two rails")
print("  3. The monad sees them as structurally null (chi_1 = 0)")
print("  4. They are defined ENTIRELY by their factor-2 structure")
print()

# What about n mod 12?
print("  Position mod 12:")
mod12_counts = {}
for pd in perfect_data:
    m12 = pd['n'] % 12
    mod12_counts[m12] = mod12_counts.get(m12, 0) + 1

for m, count in sorted(mod12_counts.items()):
    chi1_val = chi_1(m)
    chi3_val = chi_3(m)
    print(f"    n = {m} (mod 12): {count} perfect numbers, chi_1={chi1_val}, chi_3={chi3_val}")

print()
print("  All perfect numbers (p >= 3) are = 4 (mod 12).")
print("  Position 4 in the 12-circle: between R1(5) and R2(7).")
print("  chi_1(4) = 0, chi_3(4) = 0. Double null.")
print()

# The deeper structure: mod 72, mod 144
print("  Deeper structure (mod 72):")
mod72_counts = {}
for pd in perfect_data:
    m72 = pd['n'] % 72
    mod72_counts[m72] = mod72_counts.get(m72, 0) + 1

for m, count in sorted(mod72_counts.items()):
    print(f"    n = {m:>2} (mod 72): {count} perfect numbers")

print()


# ====================================================================
# SECTION 5: THE PERFECT NUMBER CYCLE IN MOD 36
# ====================================================================
print("=" * 70)
print("  SECTION 5: THE MOD 36 CYCLE")
print("=" * 70)
print()

print("  2^(p-1) mod 36 cycles with period 6 (since phi(36) = 12, but 2 is")
print("  not coprime to 36):")
for k in range(1, 13):
    print(f"    2^{k} mod 36 = {pow(2, k, 36)}")

print()
print("  For p-1 = 2m (even), 2^(p-1) = 4^m:")
for m in range(1, 10):
    print(f"    4^{m} mod 36 = {pow(4, m, 36)}")

print()
print("  4^m mod 36 cycles: 4, 16, 28, 4, 16, 28, ... (period 3)")
print()
print("  2^p mod 36 for odd primes p:")
for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
    print(f"    p={p:>2}: 2^{p} mod 36 = {pow(2, p, 36)}, M_p mod 36 = {(pow(2,p,36)-1)%36}")

print()
print("  So n mod 36 = (4^(p-1)/2 mod 36) * ((2^p - 1) mod 36) mod 36")
print("  Phase depends on (p-1)/2 mod 3 and 2^p mod 36.")
print()


# ====================================================================
# SECTION 6: ODD PERFECT NUMBERS -- MONAD CONSTRAINTS
# ====================================================================
print("=" * 70)
print("  SECTION 6: ODD PERFECT NUMBERS -- WHAT THE MONAD SAYS")
print("=" * 70)
print()

print("  If an odd perfect number exists, it must satisfy sigma(n) = 2n.")
print("  In the monad's decomposition:")
print("    sigma(n)/n = 2")
print("    = PROD_{p^a || n} sigma(p^a)/p^a")
print("    = PROD_{p^a || n} (1 + 1/p + ... + 1/p^a)")
print()
print("  For this product to equal EXACTLY 2:")
print("    Each factor is > 1, so we need a careful balance.")
print("    The factor for p=2 would give exactly 2 if 2^(p-1)*(2^p-1).")
print("    Without factor 2 (odd n), we need OTHER primes to multiply to 2.")
print()
print("  Monad constraints on an odd perfect number n:")
print("    1. n must be on R1 or R2 (odd, not divisible by 2 or 3... wait)")
print("    2. n could be divisible by 3. Let's check both cases.")
print()

print("  If n = 1 (mod 6) [R2]:")
print("    chi_1(n) = +1. Has rail identity.")
print("    sigma(n)/n = 2 exactly.")
print("    The rail Mertens contribution C_rail would need to be exactly 2/C3.")
print()
print("  If n = 5 (mod 6) [R1]:")
print("    chi_1(n) = -1. Has rail identity.")
print("    Same sigma constraint.")
print()
print("  If n = 3 (mod 6) [divisible by 3, not 2]:")
print("    chi_1(n) = 0. Off-rail.")
print("    C3 contributes to sigma(n)/n.")
print()
print("  The monad says: odd perfect numbers MUST be on-rail (R1 or R2)")
print("  OR off-rail via divisibility by 3. The Euler form tells us")
print("  they must be p^(4k+1) * m^2 for some prime p = 1 (mod 4).")
print()

# Check: what mod 6 positions are possible for odd perfect numbers?
# Known: must be = 1 (mod 12) or = 9 (mod 36) [various theorems]
print("  Known constraints (from literature):")
print("    - Must be = 1 (mod 12) or = 9 (mod 36)")
print("    - Must have at least 10 distinct prime factors")
print("    - Must be > 10^1500")
print()
print("  If n = 1 (mod 12): n is on R2 (= 1 mod 6). chi_1 = +1.")
print("  If n = 9 (mod 36): n mod 6 = 9 mod 6 = 3. Divisible by 3. chi_1 = 0.")
print()
print("  MONAD VERDICT on odd perfect numbers:")
print("  They would live on R2 or at the chi_1=0 position 3 mod 6.")
print("  Either way, they need sigma(n)/n = 2.0 exactly, which requires")
print("  a very specific balance of prime power factors.")
print("  The monad can CHECK any candidate but cannot PREDICT existence.")
print()


# ====================================================================
# SECTION 7: AMICABLE NUMBERS AND SOCIAL NUMBERS
# ====================================================================
print("=" * 70)
print("  SECTION 7: AMICABLE & SOCIABLE NUMBERS IN THE MONAD")
print("=" * 70)
print()

# Known small amicable pairs
amicable_pairs = [(220, 284), (1184, 1210), (2620, 2924), (5020, 5564),
                  (6232, 6368), (10744, 10856), (12285, 14595), (17296, 18416)]

print("  Amicable pairs (sigma(a)=a+b, sigma(b)=a+b):")
print(f"  {'a':>6} {'b':>6} {'a%6':>4} {'b%6':>4} {'a rail':>16} {'b rail':>16} {'a%36':>5} {'b%36':>5}")
for a, b in amicable_pairs:
    print(f"  {a:>6} {b:>6} {a%6:>4} {b%6:>4} {rail_of(a):>16} {rail_of(b):>16} {a%36:>5} {b%36:>5}")

print()
print("  Pattern: amicable pairs span DIFFERENT mod-6 positions.")
print("  They are NOT confined to one rail. Social connections cross rails.")
print()


# ====================================================================
# SUMMARY
# ====================================================================
print("=" * 70)
print("  SUMMARY: PERFECT NUMBERS IN THE MONAD")
print("=" * 70)
print()
print("  1. Even perfect numbers (p >= 3) are ALL = 4 (mod 6).")
print("     They live in the chi_1 = 0 shadow. Invisible to the rail character.")
print()
print("  2. Their Mersenne prime factors are ALL on R2 (= 1 mod 6).")
print("     Mersenne primes > 3 are always R2 citizens.")
print()
print("  3. The factor 2^(p-1) places them at mod-6 position 4.")
print("     They are always divisible by 2, never by 3 (except n=6).")
print()
print("  4. sigma(n)/n = 2 exactly -- far below Robin danger.")
print("     Perfect numbers are structurally SAFE from the sigma bound.")
print()
print("  5. Odd perfect numbers would be on R2 or at position 3 mod 6.")
print("     The monad constrains but cannot prove non-existence.")
print()
print("  6. Amicable pairs cross rail boundaries freely.")
print("     Social number relationships are inter-rail phenomena.")
print()
print("  THE MONAD'S VIEW: Perfect numbers are shadow creatures.")
print("  They live between the rails, at position 4 mod 6.")
print("  The dual-rail structure doesn't see them -- chi_1 = 0 for all.")
print("  Their perfection comes entirely from the 2-world (powers of 2),")
print("  not from the rail world (primes > 3).")
print()
print("Done.")
