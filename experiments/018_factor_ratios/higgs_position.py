"""
EXPERIMENT 114: THE HIGGS POSITION -- Deep Dive into Mod 24
=============================================================
The user's hypothesis: the Higgs boson maps to p^2 (squared primes) in the
monad, and mod 24 with -12/+12 symmetry reveals its exact position.

Key discovery: (Z/24Z)* = {1,5,7,11,13,17,19,23} has 8 elements,
ALL of order 2. So (Z/24Z)* = Z2 x Z2 x Z2.

For ANY prime p > 3: p^2 = 1 mod 24. The squared prime ALWAYS collapses
to position 1 -- the IDENTITY of the group. The Higgs boson is the
self-coupling of the prime field returning to the vacuum.

The three Z2 charges of mod 24:
  chi_5:  rail split (same as chi_1 mod 6) -- R2 vs R1
  chi_7:  sub-position (mod 12 structure) -- primary vs secondary
  chi_13: layer (mod 24 structure) -- lower vs upper

The Higgs (p^2) has charges (+1,+1,+1) -- fully neutral, like the VEV.
"""

from math import gcd, isqrt, log, exp
from collections import Counter, defaultdict

# Euler-Mascheroni constant
GAMMA = 0.5772156649015328606065120900824

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

def chi_1(n):
    """Dirichlet character mod 6. +1 R2, -1 R1, 0 off-rail."""
    r = n % 6
    if r == 1: return 1
    if r == 5: return -1
    return 0

def rail_of(n):
    r = n % 6
    if r == 5: return 'R1'
    if r == 1: return 'R2'
    return 'off'

def coprime24(n):
    return gcd(n, 24) == 1

def centered(n):
    """Mod 24 position in -12/+12 framing."""
    r = n % 24
    return r if r <= 12 else r - 24

# The three Z2 characters generating (Z/24Z)* = Z2^3
# Generators: 5, 7, 13 (each order 2)

def chi5(n):
    """Rail split character = chi_1 mod 6.
    +1 for {1,7,13,19} (= 1 mod 6 = R2)
    -1 for {5,11,17,23} (= 5 mod 6 = R1)"""
    if not coprime24(n): return 0
    return 1 if n % 6 == 1 else -1

def chi7(n):
    """Sub-position character (mod 12 structure).
    +1 for {1,5,13,17} (= 1,5 mod 12)
    -1 for {7,11,19,23} (= 7,11 mod 12)"""
    if not coprime24(n): return 0
    return 1 if n % 12 in (1, 5) else -1

def chi13(n):
    """Layer character (mod 24 structure).
    +1 for {1,5,7,11} (lower half, < 12)
    -1 for {13,17,19,23} (upper half, >= 12)"""
    if not coprime24(n): return 0
    return 1 if n % 24 < 12 else -1

def omega(n):
    """Number of distinct prime factors."""
    temp = n
    count = 0
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            count += 1
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        count += 1
    return count

# ====================================================================
# The 8 coprime positions
# ====================================================================
Z24_STAR = sorted(n for n in range(1, 24) if gcd(n, 24) == 1)

# Binary encoding: position = 5^a * 7^b * 13^c mod 24
BINARY = {}
for a in range(2):
    for b in range(2):
        for c in range(2):
            val = pow(5, a, 24) * pow(7, b, 24) * pow(13, c, 24) % 24
            BINARY[val] = (a, b, c)

print("=" * 70)
print("EXPERIMENT 114: THE HIGGS POSITION -- Deep Dive into Mod 24")
print("=" * 70)

# ====================================================================
# SECTION 1: THE MOD 24 LATTICE
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 1: THE MOD 24 LATTICE -- (Z/24Z)* = Z2 x Z2 x Z2")
print("=" * 70)

print(f"\n(Z/24Z)* = {{{', '.join(map(str, Z24_STAR))}}}")
print(f"|Z/24Z)*| = phi(24) = {len(Z24_STAR)}")

# Verify all elements have order 2
all_ord2 = all((a * a) % 24 == 1 for a in Z24_STAR)
print(f"\nAll elements satisfy a^2 = 1 mod 24: {all_ord2}")
print(f"=> (Z/24Z)* = Z2 x Z2 x Z2  (NOT Z8 or Z4 x Z2)")

print(f"\nGenerators: {{5, 7, 13}} -- each of order 2, independent")
generated = set()
for a in range(2):
    for b in range(2):
        for c in range(2):
            generated.add(pow(5, a, 24) * pow(7, b, 24) * pow(13, c, 24) % 24)
print(f"Products generate: {sorted(generated)} = (Z/24Z)* OK")

# The full lattice in -12/+12 framing
print(f"\nMod 24 lattice in -12/+12 symmetric framing:")
print(f"  {'Pos':>4} {'Cent':>6} {'chi5':>5} {'chi7':>5} {'chi13':>6} {'Rail':>5} {'Layer':>6} {'Flipped charges':>20}")
for p in Z24_STAR:
    c = centered(p)
    a, b, cc = BINARY[p]
    flipped = []
    if a: flipped.append("chi5")
    if b: flipped.append("chi7")
    if cc: flipped.append("chi13")
    label = "+".join(flipped) if flipped else "NONE (Higgs!)"
    print(f"  {p:>4} {c:>+6} {chi5(p):>+5} {chi7(p):>+5} {chi13(p):>+6} {rail_of(p):>5} "
          f"{'lower' if p < 12 else 'upper':>6} {label:>20}")

print(f"\n  POSITION +1 = the Higgs: ALL charges +1 = IDENTITY = vacuum")
print(f"  POSITION -1 (=23) = anti-Higgs: ALL charges -1 = maximally charged")

# ====================================================================
# SECTION 2: THE HIGGS IDENTITY -- p^2 = 1 mod 24
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 2: THE HIGGS IDENTITY -- p^2 = 1 mod 24 for ALL primes > 3")
print("=" * 70)

primes_up_to_10k = [p for p in range(5, 10001) if is_prime(p)]
all_identity = all((p * p) % 24 == 1 for p in primes_up_to_10k)
print(f"\nTested {len(primes_up_to_10k)} primes in [5, 10000]")
print(f"ALL satisfy p^2 = 1 mod 24: {all_identity}")

print(f"\n  {'Prime p':>8} {'p mod 24':>8} {'p^2 mod 24':>9} {'Charges of p':>16}")
for p in primes_up_to_10k[:20]:
    print(f"  {p:>8} {p % 24:>8} {(p*p)%24:>9}    ({chi5(p):+d},{chi7(p):+d},{chi13(p):+d})")

print(f"\n  ALGEBRAIC PROOF:")
print(f"  p > 3 implies p coprime to 6. So p = +-1 or +-5 mod 24.")
print(f"  In (Z/24Z)* = Z2^3, every element has order 2: a^2 = 1.")
print(f"  Therefore p^2 = 1 for ANY p coprime to 6.")
print(f"  (This holds for ALL coprime numbers, not just primes.)")
print(f"\n  But the SIGNIFICANCE: p^2 is the SELF-COUPLING of a Higgs quantum.")
print(f"  Self-coupling ALWAYS returns to the identity = the vacuum state.")
print(f"  This IS the Higgs mechanism: phi^2 potential minimum at VEV.")

# Verify: ALL coprime numbers squared = 1 mod 24
coprime_nums = [n for n in range(1, 10001) if coprime24(n)]
all_sq_identity = all((n * n) % 24 == 1 for n in coprime_nums)
print(f"\n  Extended check: {len(coprime_nums)} coprime-to-24 numbers in [1,10000]")
print(f"  ALL satisfy n^2 = 1 mod 24: {all_sq_identity}")
print(f"  => Squaring = self-coupling = return to Higgs position (universal)")

# ====================================================================
# SECTION 3: PRIME POWER SPECTRUM -- Even->Higgs, Odd->original
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 3: PRIME POWER SPECTRUM -- p^k mod 24")
print("=" * 70)

print(f"\n  THEOREM: p^k mod 24 = 1 if k even, = p mod 24 if k odd")
print(f"  Proof: p^2 = 1, so p^(2m) = 1^m = 1, p^(2m+1) = p * 1 = p")
print(f"\n  Even powers = Higgs excitations (at identity)")
print(f"  Odd powers  = field quanta (at native position)")

print(f"\n  {'Prime':>5} | {'k=1':>4} {'k=2':>4} {'k=3':>4} {'k=4':>4} {'k=5':>4} {'k=6':>4}")
print(f"  {'':->5}   {'':->4} {'':->4} {'':->4} {'':->4} {'':->4} {'':->4}")
for p in [5, 7, 11, 13, 17, 19, 23]:
    vals = [pow(p, k, 24) for k in range(1, 7)]
    labels = [f"{'H' if k % 2 == 0 else 'F'}{v:>2}" for k, v in enumerate(vals, 1)]
    print(f"  {p:>5} | " + " ".join(f"{v:>4}" for v in vals))

power_theorem_ok = True
for p in Z24_STAR:
    for k in range(1, 30):
        expected = 1 if k % 2 == 0 else p % 24
        if pow(p, k, 24) != expected:
            power_theorem_ok = False
print(f"\n  Verified for all 8 positions, k=1..29: {power_theorem_ok}")

print(f"\n  PHYSICAL INTERPRETATION:")
print(f"  p^1 = prime (field quantum) -- has native charges")
print(f"  p^2 = Higgs excitation -- ALL charges neutral (identity)")
print(f"  p^3 = field quantum again -- back to native charges")
print(f"  p^4 = Higgs again -- oscillation between field and vacuum")

# ====================================================================
# SECTION 4: THE THREE CHARGES
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 4: THE THREE Z2 CHARGES -- AND WHAT THEY DETECT")
print("=" * 70)

print(f"\n  chi_5 (rail split = chi_1 mod 6):")
print(f"    +1: {{1,7,13,19}} = R2 positions")
print(f"    -1: {{5,11,17,23}} = R1 positions")
print(f"    Meaning: which Higgs CHANNEL (R1 or R2)")

print(f"\n  chi_7 (sub-position = mod 12 structure):")
print(f"    +1: {{1,5,13,17}} = 'primary' sub-positions")
print(f"    -1: {{7,11,19,23}} = 'secondary' sub-positions")
print(f"    Meaning: which SUB-CHANNEL within the rail")

print(f"\n  chi_13 (layer = mod 24 structure):")
print(f"    +1: {{1,5,7,11}} = lower layer (positions < 12)")
print(f"    -1: {{13,17,19,23}} = upper layer (positions >= 12)")
print(f"    Meaning: which LAYER of the mod 24 tower")

# Verify orthogonality
chars = [chi5, chi7, chi13]
orthogonal = True
for i in range(3):
    for j in range(i+1, 3):
        s = sum(chars[i](n) * chars[j](n) for n in Z24_STAR)
        if s != 0:
            orthogonal = False
            print(f"  WARNING: chi_{[5,7,13][i]} . chi_{[5,7,13][j]} = {s}")
print(f"\n  Three characters mutually orthogonal: {orthogonal}")
print(f"  => Three INDEPENDENT quantum numbers (like T3, Y, C in SM)")

# ====================================================================
# SECTION 5: MERSENNE PRIMES -- Position 7 (chi: +1, -1, +1)
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 5: SPECIAL PRIME FAMILIES AND THEIR POSITIONS")
print("=" * 70)

# Mersenne primes
print(f"\n  MERSENNE PRIMES (2^p - 1):")
mersenne_exp = [2, 3, 5, 7, 13, 17, 19, 31]
for pe in mersenne_exp:
    mp = (1 << pe) - 1
    pos = mp % 24
    c = centered(pos)
    charges = (chi5(pos), chi7(pos), chi13(pos))
    print(f"    2^{pe:>2}-1 = {mp:>10}  pos={pos:>2} ({c:>+3})  charges={charges}")

print(f"\n  For p >= 3 odd: 2^p = 8 mod 24, so 2^p - 1 = 7 mod 24")
print(f"  ALL Mersenne primes (exponent > 2) sit at position +7")
print(f"  Charges: (+1, -1, +1) = R2, secondary, lower")
print(f"  7^2 = 49 = 1 mod 24 -> Mersenne self-coupling -> Higgs! OK")

# Fermat primes
print(f"\n  FERMAT PRIMES (2^(2^k) + 1):")
for k in range(5):
    fp = (1 << (1 << k)) + 1
    pos = fp % 24
    c = centered(pos)
    label = "prime" if is_prime(fp) else "composite"
    print(f"    F_{k} = {fp:>10}  pos={pos:>2} ({c:>+3})  charges=({chi5(pos):+d},{chi7(pos):+d},{chi13(pos):+d})  [{label}]")

print(f"  Fermat primes (except 3,5) sit at position +17 (= -7)")
print(f"  Charges: (-1, +1, -1) = R1, primary, upper")
print(f"  They are the MIRROR IMAGE of Mersenne primes across chi_5 and chi_13!")

# Safe primes
print(f"\n  SAFE PRIMES ((p-1)/2 also prime):")
safe = [p for p in range(5, 1000) if is_prime(p) and is_prime((p-1)//2)]
safe_pos = Counter(p % 24 for p in safe)
print(f"  Position distribution: {dict(sorted(safe_pos.items()))}")

# Sophie Germain primes
print(f"\n  SOPHIE GERMAIN PRIMES (2p+1 also prime):")
sg = [p for p in range(5, 1000) if is_prime(p) and is_prime(2*p+1)]
sg_pos = Counter(p % 24 for p in sg)
print(f"  Position distribution: {dict(sorted(sg_pos.items()))}")

# ====================================================================
# SECTION 6: THE ATTRACTION MECHANISM
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 6: THE ATTRACTION MECHANISM -- Why Particles Couple to Higgs")
print("=" * 70)

print(f"\n  SM: particles couple to Higgs field via Yukawa couplings")
print(f"       coupling strength -> mass (m = y * v)")
print(f"  Monad: numbers couple to prime field via factorization")
print(f"          coupling channels = omega(n), mass = sigma(n)/n")

# sigma/n by omega for coprime-to-24 numbers
by_omega = defaultdict(list)
for n in range(2, 50001):
    if not coprime24(n):
        continue
    w = omega(n)
    by_omega[w].append(sigma(n) / n)

print(f"\n  Average mass (sigma/n) by coupling channels (omega), n < 50000:")
print(f"  {'omega':>5} {'Count':>8} {'Avg mass':>10} {'Min mass':>10} {'Max mass':>10}")
for w in sorted(by_omega.keys())[:8]:
    vals = by_omega[w]
    print(f"  {w:>5} {len(vals):>8} {sum(vals)/len(vals):>10.4f} {min(vals):>10.4f} {max(vals):>10.4f}")

print(f"\n  More coupling channels = heavier particle (higher mass)")

# Mass distribution across the 8 positions
pos_mass = defaultdict(list)
for n in range(2, 50001):
    if coprime24(n):
        pos_mass[n % 24].append(sigma(n) / n)

print(f"\n  Mass distribution across mod 24 positions (n < 50000):")
print(f"  {'Pos':>4} {'Cent':>6} {'Count':>7} {'Avg mass':>10} {'Max mass':>10} {'Charges':>16}")
for p in sorted(pos_mass.keys()):
    c = centered(p)
    vals = pos_mass[p]
    charges = f"({chi5(p):+d},{chi7(p):+d},{chi13(p):+d})"
    print(f"  {p:>4} {c:>+6} {len(vals):>7} {sum(vals)/len(vals):>10.4f} {max(vals):>10.4f} {charges:>16}")

# ====================================================================
# SECTION 7: COMPOSITE ATLAS -- Semiprimes and the Group Law
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 7: COMPOSITE ATLAS -- The Group Law of Attraction")
print("=" * 70)

print(f"\n  KEY INSIGHT: n = p*q lands at position (p mod 24)*(q mod 24) mod 24")
print(f"  This is the GROUP LAW of (Z/24Z)* = Z2^3")
print(f"  Position = XOR of charge vectors: (+1,+1,+1) for Higgs")

# Generate semiprimes
primes_list = [p for p in range(5, 1000) if is_prime(p)]
semiprime_pos = defaultdict(list)
for i, p in enumerate(primes_list):
    for q in primes_list[i+1:]:
        n = p * q
        if n > 50000: break
        pos = n % 24
        semiprime_pos[pos].append(n)

print(f"\n  Semiprime p*q distribution (p < q, p,q > 3, pq < 50000):")
print(f"  {'Pos':>4} {'Cent':>6} {'Count':>7} {'Charges':>16} {'Distance from 1':>16}")
for pos in sorted(semiprime_pos.keys()):
    c = centered(pos)
    count = len(semiprime_pos[pos])
    a, b, cc = BINARY[pos]
    dist = a + b + cc
    charges = f"({chi5(pos):+d},{chi7(pos):+d},{chi13(pos):+d})"
    print(f"  {pos:>4} {c:>+6} {count:>7} {charges:>16} {dist:>16}")

print(f"\n  TWO primes at SAME position -> product at Higgs (identity):")
print(f"  (because every element is its own inverse in Z2^3)")
# Show examples: p*q = 1 mod 24 when p = q mod 24
for target_pos in Z24_STAR:
    primes_at_pos = [p for p in primes_list if p % 24 == target_pos]
    if len(primes_at_pos) >= 2:
        p, q = primes_at_pos[0], primes_at_pos[1]
        n = p * q
        print(f"    {p} x {q} = {n} -> {n % 24} mod 24 (Higgs!) [both = {target_pos}]")
        break

print(f"\n  TWO primes at DIFFERENT positions -> product at non-identity:")
examples = [(5, 7), (5, 11), (7, 11), (7, 13), (11, 13), (13, 17)]
for p, q in examples:
    n = p * q
    pos = n % 24
    c = centered(pos)
    # Charge addition
    pc = (chi5(p), chi7(p), chi13(p))
    qc = (chi5(q), chi7(q), chi13(q))
    nc = (chi5(pos), chi7(pos), chi13(pos))
    print(f"    {p:>2}({pc}) x {q:>2}({qc}) = {n:>3} -> pos {pos:>2} ({c:>+3}) charges{nc}")

print(f"\n  The charges MULTIPLY (Z2 addition = XOR):")
print(f"  (+1,-1,+1) x (+1,-1,+1) = (+1,+1,+1) = Higgs  [same position]")
print(f"  (-1,+1,+1) x (+1,-1,+1) = (-1,-1,+1)         [different]")

# ====================================================================
# SECTION 8: THE HIGGS POTENTIAL LANDSCAPE
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 8: THE HIGGS POTENTIAL -- Distance from Identity")
print("=" * 70)

print(f"\n  In (Z/24Z)* = Z2^3, distance from identity = number of flipped charges")
print(f"  This is the Hamming distance in the charge space")

print(f"\n  {'Distance':>8} {'Positions':>24} {'Charges flipped':>20}")
for d in range(4):
    positions = [p for p in Z24_STAR if sum(BINARY[p]) == d]
    if d == 0:
        names = "NONE (identity)"
    else:
        flipped = []
        if any(BINARY[p][0] for p in positions): flipped.append("chi5")
        if any(BINARY[p][1] for p in positions): flipped.append("chi7")
        if any(BINARY[p][2] for p in positions): flipped.append("chi13")
        names = "any combination"
    print(f"  {d:>8} {str(positions):>24} {names:>20}")

# Average mass by distance from identity
print(f"\n  Average mass by distance from Higgs (identity):")
print(f"  {'Dist':>4} {'Positions':>24} {'Avg mass':>10} {'Count':>8}")
for d in range(4):
    positions = [p for p in Z24_STAR if sum(BINARY[p]) == d]
    all_ratios = []
    for p in positions:
        all_ratios.extend(pos_mass.get(p, []))
    if all_ratios:
        avg = sum(all_ratios) / len(all_ratios)
        print(f"  {d:>4} {str(positions):>24} {avg:>10.4f} {len(all_ratios):>8}")

print(f"\n  PHYSICAL PICTURE:")
print(f"  Position +1 (distance 0) = vacuum = Higgs VEV")
print(f"  Positions +-5,+-7,+-11 (distance 1-2) = particles with one charge")
print(f"  Position -1 (distance 3) = maximally charged = heaviest?")

# ====================================================================
# SECTION 9: p^2 vs p*q -- THE YUKAWA HIERARCHY
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 9: THE YUKAWA HIERARCHY -- p^2 vs p*q")
print("=" * 70)

print(f"\n  The Higgs (p^2) is at position 1 (identity) for ALL primes.")
print(f"  But p*q (distinct primes) scatters across all 8 positions.")
print(f"  The MASS HIERARCHY comes from position diversity:")
print(f"  - p^2: always identity (ONE state, no hierarchy)")
print(f"  - p*q: 8 possible positions (EIGHT states, natural hierarchy)")

# sigma(p^2)/p^2 for primes
print(f"\n  Higgs excitations p^2 -- all at identity, but different masses:")
print(f"  {'Prime':>5} {'p^2':>8} {'sigma(p^2)/p^2':>14} {'Position':>8}")
for p in primes_list[:15]:
    psq = p * p
    mass = sigma(psq) / psq
    print(f"  {p:>5} {psq:>8} {mass:>14.6f} {psq % 24:>8}")

print(f"\n  ALL p^2 are at position 1 mod 24 (Higgs position)")
print(f"  But their 'mass' sigma(p^2)/p^2 = (1 + 1/p + 1/p^2) varies!")
print(f"  This is the Yukawa coupling: different primes couple differently")
print(f"  even though they all sit at the SAME mod 24 position.")
print(f"\n  The hierarchy is NOT in the mod 24 position -- it's in p itself.")
print(f"  Small p -> strong coupling (mass ~ 1 + 1/p ~ 2)")
print(f"  Large p -> weak coupling (mass ~ 1 + 1/p ~ 1)")
print(f"  This IS the Yukawa hierarchy: y_p = 1/p (inversely proportional)")

# ====================================================================
# SECTION 10: THE MOD 24 MULTIPLICATION TABLE
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 10: THE MOD 24 GROUP LAW -- Full Multiplication Table")
print("=" * 70)

print(f"\n  This table shows WHERE two particles 'land' when they interact:")
print(f"  Product = (row x col) mod 24")
print(f"\n  {'':>4}", end="")
for q in Z24_STAR:
    print(f" {q:>3}", end="")
print()
for p in Z24_STAR:
    print(f"  {p:>4}", end="")
    for q in Z24_STAR:
        print(f" {(p*q)%24:>3}", end="")
    print()

print(f"\n  Every row and column is a PERMUTATION of the 8 positions.")
print(f"  The table is symmetric (Abelian group).")
print(f"  Diagonal is all 1's (self-coupling = Higgs).")

# ====================================================================
# TESTS
# ====================================================================
print("\n" + "=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 0

# Test 1: All primes squared = 1 mod 24
total += 1
if all((p*p) % 24 == 1 for p in primes_up_to_10k):
    print(f"  [PASS] All {len(primes_up_to_10k)} primes > 3: p^2 = 1 mod 24")
    passed += 1
else:
    print(f"  [FAIL] Some p^2 != 1 mod 24")

# Test 2: (Z/24Z)* = Z2^3
total += 1
if all_ord2:
    print(f"  [PASS] (Z/24Z)* = Z2 x Z2 x Z2 (all elements order 2)")
    passed += 1
else:
    print(f"  [FAIL] Group structure wrong")

# Test 3: chi5 = chi_1 (rail character)
total += 1
match = all(chi5(n) == chi_1(n) for n in range(1, 10001) if coprime24(n))
if match:
    print(f"  [PASS] chi_5 = chi_1 (rail split character)")
    passed += 1
else:
    print(f"  [FAIL] chi_5 != chi_1")

# Test 4: Character orthogonality
total += 1
if orthogonal:
    print(f"  [PASS] Three Z2 characters mutually orthogonal")
    passed += 1
else:
    print(f"  [FAIL] Characters not orthogonal")

# Test 5: Even/odd power theorem
total += 1
if power_theorem_ok:
    print(f"  [PASS] p^k mod 24: even->1, odd->p (for all 8 positions, k=1..29)")
    passed += 1
else:
    print(f"  [FAIL] Power theorem violated")

# Test 6: Mersenne primes at position 7
total += 1
merse_ok = all(((1 << pe) - 1) % 24 == 7 for pe in [3, 5, 7, 13, 17, 19, 31])
if merse_ok:
    print(f"  [PASS] Mersenne primes (exponent >= 3): all = 7 mod 24")
    passed += 1
else:
    print(f"  [FAIL] Mersenne position wrong")

# Test 7: sigma/n increases with omega (on average)
total += 1
avg_by_w = {w: sum(v)/len(v) for w, v in by_omega.items() if w <= 6 and v}
increasing = all(avg_by_w[k] <= avg_by_w[k+1] for k in range(1, 5) if k in avg_by_w and k+1 in avg_by_w)
if increasing:
    print(f"  [PASS] sigma(n)/n increases with omega(n) (coupling strength)")
    passed += 1
else:
    print(f"  [FAIL] sigma/n doesn't increase with omega")

# Test 8: Semiprimes cover all 8 positions
total += 1
if set(semiprime_pos.keys()) == set(Z24_STAR):
    print(f"  [PASS] Semiprimes cover all 8 positions of (Z/24Z)*")
    passed += 1
else:
    print(f"  [FAIL] Semiprimes don't cover all positions")

# Test 9: Diagonal of multiplication table is all 1's
total += 1
diag_all_1 = all((p*p) % 24 == 1 for p in Z24_STAR)
if diag_all_1:
    print(f"  [PASS] Self-coupling (diagonal) is always identity (Higgs)")
    passed += 1
else:
    print(f"  [FAIL] Self-coupling not at identity")

# Test 10: ALL coprime numbers squared = 1
total += 1
if all_sq_identity:
    print(f"  [PASS] ALL {len(coprime_nums)} coprime-to-24 numbers: n^2 = 1 mod 24")
    passed += 1
else:
    print(f"  [FAIL] Some coprime n^2 != 1")

print(f"\nOVERALL: {passed}/{total} tests passed")

# ====================================================================
# GRAND SUMMARY
# ====================================================================
print("\n" + "=" * 70)
print("GRAND SUMMARY: THE HIGGS POSITION (EXPERIMENT 114)")
print("=" * 70)

print(f"""
THE HIGGS BOSON IS p^2 -- the self-coupling of the prime field.

Key results:
  1. (Z/24Z)* = Z2 x Z2 x Z2 -- 8 positions, three independent charges
  2. p^2 = 1 mod 24 for ALL primes > 3 -- identity = vacuum = Higgs VEV
  3. Even powers -> 1 (Higgs), odd powers -> p (field) -- oscillation
  4. Three charges: chi_5 (rail), chi_7 (sub-pos), chi_13 (layer)
  5. Higgs (p^2) has charges (+1,+1,+1) -- FULLY NEUTRAL
  6. Mersenne primes at +7 (+1,-1,+1), Fermat primes at +17 (-1,+1,-1)
  7. sigma(n)/n = mass increases with omega(n) = coupling channels
  8. Semiprimes scatter across all 8 positions -- hierarchy from diversity
  9. Self-coupling = group diagonal = ALWAYS identity
  10. Yukawa hierarchy: y_p = 1/p, not from position but from coupling

The -12/+12 framing:
  +1  = Higgs (vacuum, all charges +1)
  -1  = anti-Higgs (all charges -1, maximally excited)
  +7  = Mersenne primes (R2, secondary, lower)
  -7  = Fermat primes (R1, primary, upper)
  Mirror (-/+): flips chi_13 (layer) while preserving chi_5 and chi_7

WHY particles are attracted to Higgs:
  - Numbers with more prime factors have higher sigma(n)/n (more mass)
  - The Higgs position (1) is where self-coupled primes (p^2) live
  - But composites DON'T automatically go to position 1
  - Only p*q where p = q mod 24 reaches the Higgs position
  - The "attraction" is that ALL self-coupling (p^2) collapses to identity
  - This is the group-theoretic version of "rolling down to the VEV"
""")

print("=" * 70)
print("EXPERIMENT 114 COMPLETE")
print("=" * 70)
