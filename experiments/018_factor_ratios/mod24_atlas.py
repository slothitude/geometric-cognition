"""
EXPERIMENT 115: THE FULL MOD 24 ATLAS
======================================
Experiment 114 explored the 8 coprime positions of (Z/24Z)* = Z2^3.
This experiment maps ALL 24 positions of Z/24Z, including the 16 "dark sector"
positions divisible by 2 or 3.

Key structures:
  1. CRT decomposition: Z/24Z = Z/8Z x Z/3Z
  2. The 16 non-coprime positions (dark sector)
  3. Idempotents {0,1,9,16} -- projection operators
  4. Nilpotents {0,6,12,18} -- decay channels
  5. Zero divisors -- information loss topology
  6. Quadratic residues -- accessibility landscape
  7. Primorial 2-state bounce in nilpotent sector
  8. Pythagorean triples mod 24
  9. Fibonacci / Pisano period
 10. Euler totient landscape
"""

from math import gcd, isqrt, log, exp
from collections import Counter, defaultdict

# ====================================================================
# HELPERS (reused from higgs_position.py and structural_audit.py)
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

def euler_totient(n):
    """Euler's totient function phi(n)."""
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

def coprime24(n):
    return gcd(n, 24) == 1

def centered(n):
    """Mod 24 position in -12/+12 framing."""
    r = n % 24
    return r if r <= 12 else r - 24

def chi5(n):
    """Rail split character = chi_1 mod 6."""
    if not coprime24(n): return 0
    return 1 if n % 6 == 1 else -1

def chi7(n):
    """Sub-position character (mod 12 structure)."""
    if not coprime24(n): return 0
    return 1 if n % 12 in (1, 5) else -1

def chi13(n):
    """Layer character (mod 24 structure)."""
    if not coprime24(n): return 0
    return 1 if n % 24 < 12 else -1

# Characters of (Z/8Z)* via CRT decomposition
def char_mod8_a(n):
    """Non-trivial character of (Z/8Z)* = {1,3,5,7}.
    +1 for {1,5}, -1 for {3,7}. Matches chi7."""
    r = n % 8
    if gcd(r, 8) != 1: return 0
    return 1 if r in (1, 5) else -1

def char_mod8_b(n):
    """Second non-trivial character of (Z/8Z)*.
    +1 for {1,3}, -1 for {5,7}."""
    r = n % 8
    if gcd(r, 8) != 1: return 0
    return 1 if r in (1, 3) else -1

def char_mod8_ab(n):
    """Product character of (Z/8Z)* (both generators flipped).
    +1 for {1,7}, -1 for {3,5}."""
    r = n % 8
    if gcd(r, 8) != 1: return 0
    return 1 if r in (1, 7) else -1

def char_mod3(n):
    """Non-trivial character of (Z/3Z)* = {1,2}.
    +1 for 1 mod 3, -1 for 2 mod 3."""
    r = n % 3
    if r == 0: return 0
    return 1 if r == 1 else -1

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

# ====================================================================
print("=" * 70)
print("EXPERIMENT 115: THE FULL MOD 24 ATLAS")
print("=" * 70)

# ====================================================================
# SECTION 1: CRT DECOMPOSITION
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 1: CRT DECOMPOSITION -- Z/24Z = Z/8Z x Z/3Z")
print("=" * 70)

z8_star = [n for n in range(1, 8) if gcd(n, 8) == 1]
z3_star = [n for n in range(1, 3) if gcd(n, 3) == 1]

print(f"\n  CRT: Z/24Z ~ Z/8Z x Z/3Z  (since gcd(8,3) = 1 and 8*3 = 24)")
print(f"  (Z/8Z)* = {{{', '.join(map(str, z8_star))}}}  (phi(8) = {euler_totient(8)})")
print(f"  (Z/3Z)* = {{{', '.join(map(str, z3_star))}}}  (phi(3) = {euler_totient(3)})")

# Map all 24 positions to CRT pairs
print(f"\n  Full CRT map: n mod 24 -> (n mod 8, n mod 3)")
print(f"  {'n%24':>5} {'n%8':>4} {'n%3':>4} {'gcd':>4} {'Type':>8}")
for n in range(24):
    ptype = "coprime" if coprime24(n) else "dark"
    print(f"  {n:>5} {n%8:>4} {n%3:>4} {gcd(n,24):>4} {ptype:>8}")

# Show the 8 coprime positions with CRT decomposition
print(f"\n  Coprime positions with CRT and charge factorization:")
print(f"  {'Pos':>4} {'(m8,m3)':>8} {'chi5':>5} {'chi7':>5} {'chi13':>6}")
for pos in Z24_STAR:
    m8, m3 = pos % 8, pos % 3
    print(f"  {pos:>4} ({m8},{m3})  {chi5(pos):>+5} {chi7(pos):>+5} {chi13(pos):>+6}")

# Verify charge factorizations
chi5_eq_c3 = all(chi5(pos) == char_mod3(pos) for pos in Z24_STAR)
chi7_eq_c8a = all(chi7(pos) == char_mod8_a(pos) for pos in Z24_STAR)
chi13_eq_ent = all(chi13(pos) == char_mod8_ab(pos) * char_mod3(pos) for pos in Z24_STAR)

print(f"\n  Charge factorization proofs:")
print(f"    chi_5  = char_mod3              (purely mod 3): {chi5_eq_c3}")
print(f"    chi_7  = char_mod8_a            (purely mod 8): {chi7_eq_c8a}")
print(f"    chi_13 = char_mod8_ab * char_mod3 (entangled): {chi13_eq_ent}")

print(f"\n  PHYSICAL MEANING (SM gauge analogy):")
print(f"    mod 3 sector = color/rail charge (chi_5 = rail split)")
print(f"    mod 8 sector = isospin/generation (chi_7 = sub-position)")
print(f"    chi_13 (layer) = entangled product of both sectors")

# ====================================================================
# SECTION 2: THE 16 NON-COPRIME POSITIONS -- THE DARK SECTOR
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 2: THE 16 NON-COPRIME POSITIONS -- THE DARK SECTOR")
print("=" * 70)

dark_positions = sorted(n for n in range(24) if not coprime24(n))
print(f"\n  Dark positions: {{{', '.join(map(str, dark_positions))}}}")
print(f"  Count: {len(dark_positions)} of 24")

by_2_only = sorted(n for n in range(24) if n % 2 == 0 and n % 3 != 0)
by_3_only = sorted(n for n in range(24) if n % 3 == 0 and n % 2 != 0)
by_both = sorted(n for n in range(24) if n % 2 == 0 and n % 3 == 0)
print(f"\n  Divisibility breakdown:")
print(f"    By 2 only: {by_2_only} ({len(by_2_only)} positions)")
print(f"    By 3 only: {by_3_only} ({len(by_3_only)} positions)")
print(f"    By both 6: {by_both} ({len(by_both)} positions)")

# sigma(n)/n heatmap across ALL 24 positions
N_SCAN = 50000
pos_mass = defaultdict(list)
abundant_at = defaultdict(int)
total_at = defaultdict(int)

for n in range(1, N_SCAN + 1):
    pos = n % 24
    sn = sigma(n)
    pos_mass[pos].append(sn / n)
    total_at[pos] += 1
    if sn > 2 * n:
        abundant_at[pos] += 1

print(f"\n  sigma(n)/n heatmap (n = 1..{N_SCAN}, by mod 24 position):")
print(f"  {'Pos':>4} {'Type':>8} {'Count':>7} {'Avg s/n':>8} {'Min s/n':>8} {'Max s/n':>8} {'Abund%':>7}")
for pos in range(24):
    vals = pos_mass[pos]
    avg = sum(vals) / len(vals)
    abund_pct = 100 * abundant_at[pos] / total_at[pos]
    ptype = "coprime" if coprime24(pos) else "dark"
    print(f"  {pos:>4} {ptype:>8} {len(vals):>7} {avg:>8.4f} {min(vals):>8.4f} {max(vals):>8.4f} {abund_pct:>6.1f}%")

avg_by_pos = {pos: sum(pos_mass[pos]) / len(pos_mass[pos]) for pos in range(24)}
sorted_mass = sorted(avg_by_pos.items(), key=lambda x: -x[1])

print(f"\n  Heaviest 5 positions (highest avg sigma/n):")
for pos, avg in sorted_mass[:5]:
    ptype = "coprime" if coprime24(pos) else "dark"
    print(f"    pos {pos:>2} ({ptype:>7}): {avg:.4f}")
print(f"\n  Lightest 5 positions:")
for pos, avg in sorted_mass[-5:]:
    ptype = "coprime" if coprime24(pos) else "dark"
    print(f"    pos {pos:>2} ({ptype:>7}): {avg:.4f}")

# ====================================================================
# SECTION 3: IDEMPOTENTS -- THE PROJECTION OPERATORS
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 3: IDEMPOTENTS -- THE PROJECTION OPERATORS")
print("=" * 70)

idempotents = sorted(n for n in range(24) if (n * n) % 24 == n)
print(f"\n  Idempotents (e^2 = e mod 24): {idempotents}")

for e in idempotents:
    m8, m3 = e % 8, e % 3
    role = {0: "annihilator (absorbs everything)",
            1: "identity (Higgs position, coprime)",
            9: "projector onto Z/8Z (9%8=1, 9%3=0)",
            16: "projector onto Z/3Z (16%8=0, 16%3=1)"}.get(e, "unknown")
    print(f"    e = {e:>2}: CRT = ({m8}, {m3}), {role}")

# Verify projection: 9 kills mod 3, 16 kills mod 8
proj9_ok = all((9 * n) % 3 == 0 for n in range(24))
proj16_ok = all((16 * n) % 8 == 0 for n in range(24))

print(f"\n  Projection verification:")
print(f"    9 * anything mod 3  = 0 (kills mod 3 component): {proj9_ok}")
print(f"    16 * anything mod 8 = 0 (kills mod 8 component): {proj16_ok}")

# Show the projection table
print(f"\n  Projection table (9*n and 16*n mod 24):")
print(f"  {'n':>3} {'n%8':>4} {'n%3':>4} {'9n%24':>6} {'9n%8':>5} {'9n%3':>5} {'16n%24':>7} {'16n%8':>6} {'16n%3':>6}")
for n in range(12):
    e9 = (9 * n) % 24
    e16 = (16 * n) % 24
    print(f"  {n:>3} {n%8:>4} {n%3:>4} {e9:>6} {e9%8:>5} {e9%3:>5} {e16:>7} {e16%8:>6} {e16%3:>6}")

# ====================================================================
# SECTION 4: NILPOTENTS -- THE DECAY CHANNEL
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 4: NILPOTENTS -- THE DECAY CHANNEL")
print("=" * 70)

# Compute rad(24) = product of distinct prime factors of 24
rad24 = 1
temp = 24
d = 2
while d * d <= temp:
    if temp % d == 0:
        rad24 *= d
        while temp % d == 0:
            temp //= d
    d += 1
if temp > 1:
    rad24 *= temp

# Nilpotents = multiples of rad(24) mod 24
nilpotents_theory = sorted(n for n in range(24) if n % rad24 == 0)

# Verify computationally
nilpotents_comp = set()
for x in range(24):
    val = x
    for k in range(1, 30):
        val = (val * x) % 24
        if val == 0:
            nilpotents_comp.add(x)
            break
nilpotents = sorted(nilpotents_comp)

print(f"\n  rad(24) = {rad24}")
print(f"  Nilpotents (computational): {nilpotents}")
print(f"  Multiples of {rad24} mod 24: {nilpotents_theory}")
print(f"  Match: {nilpotents == nilpotents_theory}")

# Decay chains
print(f"\n  Decay chains (x -> x^2 -> x^3 -> ... -> 0):")
for x in nilpotents:
    chain = [x]
    val = x
    while val != 0:
        val = (val * x) % 24
        chain.append(val)
    steps = len(chain) - 1
    print(f"    {x}: " + " -> ".join(map(str, chain)) + f"  ({steps} multiplications)")

print(f"\n  PHYSICAL MEANING:")
print(f"    Nilpotent sector = {{0, 6, 12, 18}} = multiples of 6 = OFF-RAIL")
print(f"    These 'decay to zero' under self-multiplication")
print(f"    The off-rail is the dissipative sector of the monad")
print(f"    Unlike coprime positions (which cycle forever), nilpotents die")

# ====================================================================
# SECTION 5: ZERO DIVISORS -- INFORMATION LOSS
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 5: ZERO DIVISORS -- INFORMATION LOSS")
print("=" * 70)

zd_pairs = []
for a in range(1, 24):
    for b in range(1, 24):
        if (a * b) % 24 == 0:
            zd_pairs.append((a, b))

zd_set = sorted(set(a for a, b in zd_pairs))
non_coprime_set = sorted(n for n in range(1, 24) if not coprime24(n))

print(f"\n  Zero divisors: {{{', '.join(map(str, zd_set))}}}")
print(f"  Count: {len(zd_set)} = all non-coprime positions: {zd_set == non_coprime_set}")

# Annihilation graph
ann_pairs = sorted(set((min(a, b), max(a, b)) for a, b in zd_pairs if a <= b))
print(f"\n  Annihilation pairs (a * b = 0 mod 24):")
for a, b in ann_pairs:
    print(f"    {a:>2} * {b:>2} = 0 mod 24")

# Annihilation degree
ann_degree = Counter(a for a, b in zd_pairs)
print(f"\n  Annihilation degree (how many others each position kills):")
print(f"  {'Pos':>4} {'Degree':>7} {'Div by':>8}")
for pos in sorted(ann_degree.keys()):
    divby = []
    if pos % 2 == 0: divby.append("2")
    if pos % 3 == 0: divby.append("3")
    print(f"  {pos:>4} {ann_degree[pos]:>7} {'x'.join(divby):>8}")

print(f"\n  CONNECTION TO LANDAUER BOUNDARY:")
print(f"    Zero divisors = irreversible operations")
print(f"    a * b = 0 loses all information about both a and b")
print(f"    This IS the algebraic form of erasure = Landauer cost")

# ====================================================================
# SECTION 6: QUADRATIC RESIDUES
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 6: QUADRATIC RESIDUES -- THE ACCESSIBILITY LANDSCAPE")
print("=" * 70)

qr = sorted(set((n * n) % 24 for n in range(24)))
non_qr = sorted(n for n in range(24) if n not in qr)

print(f"\n  QR set: {{{', '.join(map(str, qr))}}} ({len(qr)} of 24 reachable)")
print(f"  Non-QR: {{{', '.join(map(str, non_qr))}}} ({len(non_qr)} forbidden to squares)")

qr_coprime = [q for q in qr if coprime24(q)]
qr_dark = [q for q in qr if not coprime24(q)]
print(f"\n  QR among coprime: {qr_coprime}  (only position 1 = the Higgs!)")
print(f"  QR among dark:    {qr_dark}")

print(f"\n  Integers mapping to each QR position:")
for q in qr:
    sources = sorted(n for n in range(24) if (n * n) % 24 == q)
    print(f"    pos {q:>2} <- n = {sources}")

print(f"\n  ACCESSIBILITY LANDSCAPE:")
print(f"    18 of 24 positions are FORBIDDEN to perfect squares")
print(f"    Among coprime: only +1 (identity/Higgs) is reachable")
print(f"    Squaring any coprime number lands at 1 = proven in exp 114")

# ====================================================================
# SECTION 7: PRIMORIALS
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 7: PRIMORIALS -- THE 2-STATE BOUNCE")
print("=" * 70)

primes_for_primorial = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
primorial = 1
primorial_data = []

print(f"\n  p# mod 24 for successive primes:")
print(f"  {'p':>3} {'p#%24':>6} {'centered':>9} {'chi7(p)':>8} {'Sector':>10}")
for p in primes_for_primorial:
    primorial *= p
    pos = primorial % 24
    c7 = chi7(p) if coprime24(p) else 0
    sector = "nilpotent" if pos % 6 == 0 else ("coprime" if coprime24(pos) else "dark")
    primorial_data.append((p, pos))
    print(f"  {p:>3} {pos:>6} {centered(pos):>+9} {c7:>+8} {sector:>10}")

# Show bounce pattern after 3#
print(f"\n  Bounce pattern after 3# (position 6):")
current = 6
for p in [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    c7 = chi7(p)
    action = "STAY" if c7 == 1 else "FLIP"
    current = (current * p) % 24
    print(f"    * {p:>2} (chi7={c7:+d}) -> pos {current:>2}  [{action}]")

bounce_positions = [pos for _, pos in primorial_data[2:]]
bounce_ok = all(p in (6, 18) for p in bounce_positions)
print(f"\n  All primorials after 3# in {{6, 18}}: {bounce_ok}")
print(f"  Both are NILPOTENT positions (multiples of 6)!")
print(f"  The primorial is a 2-state quantum system in the nilpotent sector")

# ====================================================================
# SECTION 8: PYTHAGOREAN TRIPLES MOD 24
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 8: PYTHAGOREAN TRIPLES MOD 24")
print("=" * 70)

print(f"\n  Only QR positions can appear as squares: {qr}")

# Generate primitive triples
triples = []
for m in range(2, 50):
    for n in range(1, m):
        if gcd(m, n) != 1: continue
        if (m + n) % 2 == 0: continue
        a = m * m - n * n
        b = 2 * m * n
        c = m * m + n * n
        triples.append((a, b, c))

print(f"\n  Primitive triples mod 24 (first 15):")
print(f"  {'(a,b,c)':>18} {'a^2%24':>6} {'b^2%24':>6} {'c^2%24':>6}")
for a, b, c in triples[:15]:
    print(f"  ({a:>4},{b:>4},{c:>4}) {(a*a)%24:>6} {(b*b)%24:>6} {(c*c)%24:>6}")

c_sq_mods = set((c * c) % 24 for _, _, c in triples)
print(f"\n  c^2 mod 24 for ALL {len(triples)} primitive triples: {sorted(c_sq_mods)}")
print(f"  Always 1 (c coprime to 6 => c^2 = 1 mod 24): {c_sq_mods == {1}}")

famous = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29)]
print(f"\n  Famous triples mod 24:")
print(f"  {'Triple':>18} {'a^2':>4} {'b^2':>4} {'c^2':>4}")
for a, b, c in famous:
    print(f"  ({a:>2},{b:>2},{c:>2})          {(a*a)%24:>4} {(b*b)%24:>4} {(c*c)%24:>4}")

print(f"\n  Right triangles have a 'preferred topology' in mod 24:")
print(f"    The hypotenuse c always lands at 1 = the Higgs identity!")

# ====================================================================
# SECTION 9: FIBONACCI / PISANO PERIOD AT MOD 24
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 9: FIBONACCI / PISANO PERIOD AT MOD 24")
print("=" * 70)

fib_seq = [0, 1]
for i in range(2, 10000):
    next_fib = (fib_seq[-1] + fib_seq[-2]) % 24
    fib_seq.append(next_fib)
    if len(fib_seq) >= 4 and fib_seq[-2] == 0 and fib_seq[-1] == 1:
        pisano_period = i - 1
        fib_seq = fib_seq[:-2]
        break

print(f"\n  Pisano period pi(24) = {pisano_period}")
print(f"  (Verified: pi(24) = lcm(pi(8), pi(3)) = lcm(12, 8) = 24)")

print(f"\n  Full Fibonacci cycle mod 24 ({len(fib_seq)} elements):")
for i, f in enumerate(fib_seq):
    bar = '#' * (f + 1) if f > 0 else '.'
    print(f"    F_{i:>2} = {f:>2}  {bar}")

visited = sorted(set(fib_seq))
never_visited = sorted(n for n in range(24) if n not in visited)
coprime_visited = sorted(n for n in visited if coprime24(n))
dark_visited = sorted(n for n in visited if not coprime24(n))
coprime_missed = sorted(n for n in range(24) if coprime24(n) and n not in visited)

print(f"\n  Positions visited: {visited} ({len(visited)} of 24)")
print(f"  Never visited: {never_visited} ({len(never_visited)} positions)")
print(f"\n  Coprime visited: {coprime_visited}")
print(f"  Coprime MISSED: {coprime_missed}")
print(f"  Dark visited: {dark_visited}")

# ====================================================================
# SECTION 10: EULER TOTIENT LANDSCAPE
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 10: EULER TOTIENT LANDSCAPE")
print("=" * 70)

phi_by_pos = defaultdict(list)
phi_ratio_by_pos = defaultdict(list)
for n in range(1, N_SCAN + 1):
    pos = n % 24
    phi_n = euler_totient(n)
    phi_by_pos[pos].append(phi_n)
    phi_ratio_by_pos[pos].append(phi_n / n)

print(f"\n  phi(n) landscape (n = 1..{N_SCAN}):")
print(f"  {'Pos':>4} {'Type':>8} {'Avg phi':>8} {'Avg phi/n':>9} {'Min phi/n':>9} {'Max phi/n':>9}")
for pos in range(24):
    ratios = phi_ratio_by_pos[pos]
    if not ratios: continue
    avg_phi = sum(phi_by_pos[pos]) / len(phi_by_pos[pos])
    avg_ratio = sum(ratios) / len(ratios)
    ptype = "coprime" if coprime24(pos) else "dark"
    print(f"  {pos:>4} {ptype:>8} {avg_phi:>8.1f} {avg_ratio:>9.4f} {min(ratios):>9.4f} {max(ratios):>9.4f}")

avg_screen = {pos: sum(phi_ratio_by_pos[pos]) / len(phi_ratio_by_pos[pos])
              for pos in range(24)}
sorted_screen = sorted(avg_screen.items(), key=lambda x: -x[1])

print(f"\n  Highest screening fraction (most 'transparent'):")
for pos, avg in sorted_screen[:5]:
    ptype = "coprime" if coprime24(pos) else "dark"
    print(f"    pos {pos:>2} ({ptype:>7}): avg phi/n = {avg:.4f}")
print(f"\n  Lowest screening fraction (most 'shielded'):")
for pos, avg in sorted_screen[-5:]:
    ptype = "coprime" if coprime24(pos) else "dark"
    print(f"    pos {pos:>2} ({ptype:>7}): avg phi/n = {avg:.4f}")

print(f"\n  phi(n)/n = screening fraction = fraction of numbers coprime to n")
print(f"  In Higgs framework: screening fraction = how much of the field")
print(f"  'passes through' n without coupling (lower = more mass coupling)")

# ====================================================================
# TESTS
# ====================================================================
print("\n" + "=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 0

# Test 1: CRT factorization
total += 1
if chi5_eq_c3 and chi7_eq_c8a and chi13_eq_ent:
    print(f"  [PASS] CRT factorization: chi5 from mod3, chi7 from mod8, chi13 entangled")
    passed += 1
else:
    print(f"  [FAIL] CRT factorization mismatch")

# Test 2: Idempotents = {0,1,9,16}
total += 1
if idempotents == [0, 1, 9, 16]:
    print(f"  [PASS] Idempotents = {{0, 1, 9, 16}}")
    passed += 1
else:
    print(f"  [FAIL] Idempotents = {idempotents}, expected [0, 1, 9, 16]")

# Test 3: Idempotent projection
total += 1
if proj9_ok and proj16_ok:
    print(f"  [PASS] Idempotents project correctly (9 kills mod3, 16 kills mod8)")
    passed += 1
else:
    print(f"  [FAIL] Idempotent projection failed")

# Test 4: Nilradical = {0,6,12,18}
total += 1
if nilpotents == [0, 6, 12, 18]:
    print(f"  [PASS] Nilradical = {{0, 6, 12, 18}} = multiples of 6")
    passed += 1
else:
    print(f"  [FAIL] Nilradical = {nilpotents}, expected [0, 6, 12, 18]")

# Test 5: QR set = {0,1,4,9,12,16}
total += 1
if qr == [0, 1, 4, 9, 12, 16]:
    print(f"  [PASS] QR set = {{0, 1, 4, 9, 12, 16}}")
    passed += 1
else:
    print(f"  [FAIL] QR set = {qr}, expected [0, 1, 4, 9, 12, 16]")

# Test 6: Primorial bounce
total += 1
if bounce_ok:
    print(f"  [PASS] Primorials after 3# bounce between 6 and 18")
    passed += 1
else:
    print(f"  [FAIL] Primorial bounce pattern incorrect")

# Test 7: Pythagorean triples c^2 = 1 mod 24
total += 1
if c_sq_mods == {1}:
    print(f"  [PASS] Primitive Pythagorean triples: c^2 = 1 mod 24 always")
    passed += 1
else:
    print(f"  [FAIL] c^2 mod 24 = {c_sq_mods}, expected {{1}}")

# Test 8: Pisano period
total += 1
fib_check = [0, 1]
for i in range(2, pisano_period + 2):
    fib_check.append((fib_check[-1] + fib_check[-2]) % 24)
pisano_ok = fib_check[pisano_period] == 0 and fib_check[pisano_period + 1] == 1
if pisano_ok and pisano_period == 24:
    print(f"  [PASS] Pisano period pi(24) = {pisano_period} verified")
    passed += 1
else:
    print(f"  [FAIL] Pisano period = {pisano_period}, expected 24")

# Test 9: Dark sector heavier than coprime
total += 1
coprime_avg_mass = sum(avg_by_pos[p] for p in Z24_STAR) / len(Z24_STAR)
dark_avg_mass = sum(avg_by_pos[p] for p in dark_positions) / len(dark_positions)
if dark_avg_mass > coprime_avg_mass:
    print(f"  [PASS] Dark avg sigma/n ({dark_avg_mass:.4f}) > coprime ({coprime_avg_mass:.4f})")
    passed += 1
else:
    print(f"  [FAIL] Dark ({dark_avg_mass:.4f}) NOT heavier than coprime ({coprime_avg_mass:.4f})")

# Test 10: Zero divisors = all non-coprime
total += 1
if zd_set == non_coprime_set:
    print(f"  [PASS] Zero divisors = all non-coprime positions")
    passed += 1
else:
    print(f"  [FAIL] Zero divisors don't match non-coprime set")

print(f"\nOVERALL: {passed}/{total} tests passed")

# ====================================================================
# GRAND SUMMARY
# ====================================================================
print("\n" + "=" * 70)
print("GRAND SUMMARY: THE FULL MOD 24 ATLAS (EXPERIMENT 115)")
print("=" * 70)

print(f"""
THE MOD 24 RING HAS 24 POSITIONS, NOT JUST 8.
  8 coprime positions: (Z/24Z)* = Z2^3  (the "bright" sector)
  16 non-coprime positions:              (the "dark" sector)

Key results:
  1. CRT: Z/24Z = Z/8Z x Z/3Z. Three charges factor as:
     chi_5  (rail)    = purely mod 3   (color sector)
     chi_7  (sub-pos) = purely mod 8   (isospin sector)
     chi_13 (layer)   = entangled mod8 x mod3

  2. Idempotents {{0,1,9,16}} are projection operators:
     9  projects onto Z/8Z (kills mod 3 component)
     16 projects onto Z/3Z (kills mod 8 component)

  3. Nilpotents {{0,6,12,18}} = multiples of 6 = off-rail:
     Decay to 0 under self-multiplication (dissipative sector)

  4. Zero divisors = all 16 dark positions:
     Information loss topology of the ring

  5. QR set = {{0,1,4,9,12,16}}: only 6/24 reachable by squaring
     Among coprime: only position 1 (the Higgs!)

  6. Primorials bounce 6 <-> 18 (nilpotent sector) after 3#
     Controlled by chi_7 of the added prime

  7. Primitive Pythagorean triples: c^2 = 1 mod 24 (Higgs!)
     The hypotenuse always lands at the identity

  8. Pisano period pi(24) = {pisano_period}
     Fibonacci visits 13 of 24 positions; misses 11 and 19 (coprime)

  9. Dark sector has HIGHER avg sigma/n than coprime (off-rail = heavier)
     Consistent with primes-as-Higgs: more factors = more mass

 10. phi(n)/n screening fraction maps the "transparency" landscape
""")

print("=" * 70)
print("EXPERIMENT 115 COMPLETE")
print("=" * 70)
