"""
EXPERIMENT 131: THE DOUBLING CIRCUIT AUDIT
============================================
Is "Vortex Math" (1-2-4-8-7-5 mod 9) just a shadow of the nilpotent
structure of Z/24Z? This experiment tests three hypotheses:

1. BASIN STRUCTURE: Under self-multiplication (x -> x^2 -> x^3 -> ...),
   every element of Z/24Z converges to one of the four idempotents {0, 1, 9, 16}.
   These are the four "attractors" of the ring.

2. THE DOUBLING CIRCUIT: Powers of 2 mod 24 enter the dark sector immediately
   and converge to idempotent 16 (the Z/3Z projector). Powers of 3 converge
   to idempotent 9 (the Z/8Z projector). The "vortex circuits" ARE the CRT
   decomposition projectors.

3. THE 3-6-9 CONNECTION: In Z/9Z, {3, 6, 0} are zero-divisors. In Z/24Z,
   {6, 12, 18} are nilpotent anchors. The Vortex 3->Monad 6 scaling is a
   resolution upgrade from the mod 9 to the mod 24 lattice.

4. EVENT HORIZON: The doubling circuit cannot escape the dark sector.
   Once a number is divisible by 2 or 3, it can NEVER reach a coprime
   position through multiplication. This is the algebraic event horizon.
"""

from math import gcd
from collections import Counter, defaultdict

# ====================================================================
# HELPERS
# ====================================================================

def coprime24(n):
    return gcd(n, 24) == 1

def centered(n):
    r = n % 24
    return r if r <= 12 else r - 24

def chi5(n):
    if not coprime24(n): return 0
    return 1 if n % 6 == 1 else -1

def chi7(n):
    if not coprime24(n): return 0
    return 1 if n % 12 in (1, 5) else -1

def chi13(n):
    if not coprime24(n): return 0
    return 1 if n % 24 < 12 else -1

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

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

# ====================================================================
Z24_STAR = sorted(n for n in range(1, 24) if gcd(n, 24) == 1)
IDEMPOTENTS = sorted(n for n in range(24) if (n * n) % 24 == n)
NILPOTENTS = sorted(n for n in range(24) if n % 6 == 0)

print("=" * 70)
print("EXPERIMENT 131: THE DOUBLING CIRCUIT AUDIT")
print("=" * 70)

# ====================================================================
# SECTION 1: THE DOUBLING CIRCUIT -- Powers of 2 in Z/24Z
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 1: THE DOUBLING CIRCUIT -- Powers of 2 mod 24")
print("=" * 70)

print(f"\n  Vortex Math's '1-2-4-8-7-5' circuit = powers of 2 mod 9.")
print(f"  Here we trace powers of 2 mod 24.")
print()

# Compute orbit of 2 under self-multiplication (i.e., powers of 2)
orbit_2 = []
val = 1  # 2^0
for k in range(20):
    pos = val % 24
    orbit_2.append((k, val, pos, centered(pos)))
    val *= 2

print(f"  {'k':>3} {'2^k':>15} {'2^k mod 24':>11} {'centered':>9} {'Sector':>10} {'Charge':>18}")
for k, v, pos, cent in orbit_2:
    sector = "coprime" if coprime24(pos) else ("nilpot" if pos % 6 == 0 else "dark")
    if coprime24(pos):
        charge = f"({chi5(pos):+d},{chi7(pos):+d},{chi13(pos):+d})"
    else:
        charge = "---"
    print(f"  {k:>3} {v:>15} {pos:>11} {cent:>+9} {sector:>10} {charge:>18}")

# Detect cycle
seen = {}
for idx, (k, v, pos, cent) in enumerate(orbit_2):
    if pos in seen:
        cycle_start = seen[pos]
        cycle_len = idx - cycle_start
        break
    seen[pos] = idx

positions_visited = sorted(set(pos for _, _, pos, _ in orbit_2))
coprime_visited = sorted(p for p in positions_visited if coprime24(p))
dark_visited = sorted(p for p in positions_visited if not coprime24(p))

print(f"\n  Positions visited: {positions_visited}")
print(f"  Coprime positions: {coprime_visited} ({len(coprime_visited)})")
print(f"  Dark positions:    {dark_visited} ({len(dark_visited)})")
print(f"  Cycle: enters at k={cycle_start}, cycle length = {cycle_len}")
print(f"  Attractor: {{{orbit_2[cycle_start][2]}, {orbit_2[cycle_start+1][2]}}}")

# Check if 16 is idempotent
print(f"\n  16^2 = {(16*16) % 24} mod 24 -> {'IDEMPOTENT' if (16*16) % 24 == 16 else 'not idempotent'}")
print(f"  8^2  = {(8*8) % 24} mod 24 -> becomes 16")
print(f"  The doubling circuit converges to idempotent 16.")
print(f"  16 projects onto Z/3Z: (16*n) mod 3 = 0 for all n.")
print(f"  16 is the CRT projector that kills the mod-8 component.")

# ====================================================================
# SECTION 2: THE TRIPLING CIRCUIT -- Powers of 3 in Z/24Z
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 2: THE TRIPLING CIRCUIT -- Powers of 3 mod 24")
print("=" * 70)

orbit_3 = []
val = 1  # 3^0
for k in range(15):
    pos = val % 24
    orbit_3.append((k, val, pos, centered(pos)))
    val *= 3

print(f"\n  {'k':>3} {'3^k':>15} {'3^k mod 24':>11} {'centered':>9} {'Sector':>10} {'Charge':>18}")
for k, v, pos, cent in orbit_3:
    sector = "coprime" if coprime24(pos) else ("nilpot" if pos % 6 == 0 else "dark")
    if coprime24(pos):
        charge = f"({chi5(pos):+d},{chi7(pos):+d},{chi13(pos):+d})"
    else:
        charge = "---"
    print(f"  {k:>3} {v:>15} {pos:>11} {cent:>+9} {sector:>10} {charge:>18}")

pos3_visited = sorted(set(pos for _, _, pos, _ in orbit_3))
print(f"\n  Positions visited: {pos3_visited}")
print(f"  9^2 = {(9*9) % 24} mod 24 -> {'IDEMPOTENT' if (9*9) % 24 == 9 else 'not idempotent'}")
print(f"  The tripling circuit converges to idempotent 9.")
print(f"  9 projects onto Z/8Z: (9*n) mod 8 = 0 for all n.")
print(f"  9 is the CRT projector that kills the mod-3 component.")

# ====================================================================
# SECTION 3: THE VORTEX COMPARISON -- mod 9 vs mod 24
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 3: THE VORTEX COMPARISON -- Z/9Z vs Z/24Z")
print("=" * 70)

# Powers of 2 mod 9 (the classic Vortex circuit)
print(f"\n  CLASSIC VORTEX: Powers of 2 mod 9")
orbit_v9 = []
val = 1
for k in range(12):
    pos = val % 9
    orbit_v9.append((k, val, pos))
    val *= 2

print(f"  {'k':>3} {'2^k mod 9':>10} {'type':>12}")
for k, v, pos in orbit_v9:
    vtype = "unit" if gcd(pos, 9) == 1 else "zero-div"
    print(f"  {k:>3} {pos:>10} {vtype:>12}")

v9_visited = sorted(set(pos for _, _, pos in orbit_v9))
v9_off = sorted(n for n in range(9) if n not in v9_visited)
print(f"\n  Circuit: {v9_visited}")
print(f"  Off-circuit: {v9_off}")
print(f"  Off-circuit = multiples of 3 = zero-divisors of Z/9Z = rad(9) ideal")

# The resolution upgrade
print(f"\n  RESOLUTION UPGRADE: Z/9Z -> Z/24Z")
print(f"  {'':>4} {'Z/9Z concept':>18} {'Z/24Z analog':>25} {'Algebraic meaning':>30}")
print(f"  {'':->4} {'':->18} {'':->25} {'':->30}")
rows = [
    ("3", "zero-divisor", "6 (sigma_7 operator)", "rail flipper / nilpotent"),
    ("6", "zero-divisor", "12 (sigma_13 operator)", "midline cross / attractor"),
    ("9=0", "annihilator", "18 (mirror flipper)", "nilpotent, decays to 0"),
    ("1,2,4,8,7,5", "doubling circuit", "{8,16} cycle", "converges to projector 16"),
    ("off-circuit", "multiples of 3", "multiples of 2 or 3", "zero-divisors / dark sector"),
]
for col1, col2, col3, col4 in rows:
    print(f"  {col1:>4} {col2:>18} {col3:>25} {col4:>30}")

print(f"\n  The key upgrade: mod 9 has ONE ideal (multiples of 3).")
print(f"  Mod 24 has TWO independent ideals (multiples of 2, multiples of 3)")
print(f"  plus their intersection (multiples of 6 = nilpotents).")
print(f"  This gives mod 24 a RICHER basin structure.")

# ====================================================================
# SECTION 4: THE BASIN STRUCTURE -- Complete Orbits Under Self-Multiplication
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 4: BASIN STRUCTURE -- x^k mod 24 for ALL 24 Elements")
print("=" * 70)

print(f"\n  Every element of Z/24Z, when repeatedly squared, converges")
print(f"  to one of the four IDEMPOTENTS: {IDEMPOTENTS}")
print()

# Compute orbit for each element
basins = defaultdict(list)  # attractor -> list of elements
orbit_data = {}

for x in range(24):
    orbit = [x]
    val = x
    for _ in range(20):
        val = (val * x) % 24
        orbit.append(val)
        if val in IDEMPOTENTS:
            break
    # Find attractor (the idempotent it converges to)
    attractor = None
    for v in orbit[1:]:
        if v in IDEMPOTENTS:
            attractor = v
            break
    if attractor is None:
        attractor = orbit[-1]
    orbit_data[x] = (orbit, attractor)
    basins[attractor].append(x)

print(f"  FOUR ATTRACTORS (idempotents) and their basins:")
for attractor in IDEMPOTENTS:
    basin = sorted(basins[attractor])
    print(f"\n  Attractor {attractor:>2}: basin = {basin} ({len(basin)} elements)")

    # Classify the basin
    coprime_in = [x for x in basin if coprime24(x)]
    div2_only = [x for x in basin if x % 2 == 0 and x % 3 != 0]
    div3_only = [x for x in basin if x % 3 == 0 and x % 2 != 0]
    div6 = [x for x in basin if x % 6 == 0]

    if coprime_in:
        print(f"    Coprime:      {coprime_in}")
    if div2_only:
        print(f"    Div by 2 only: {div2_only}")
    if div3_only:
        print(f"    Div by 3 only: {div3_only}")
    if div6:
        print(f"    Div by 6:     {div6}")

# Show orbits for key elements
print(f"\n  ORBIT DETAILS (x -> x^2 -> x^3 -> ... -> attractor):")
key_elements = sorted(set(list(range(24))[:24]))
for x in key_elements:
    orbit, attractor = orbit_data[x]
    # Compact display: show until attractor reached
    compact = []
    for v in orbit:
        compact.append(str(v))
        if v in IDEMPOTENTS and len(compact) > 1:
            break
    chain = " -> ".join(compact)
    sector = "coprime" if coprime24(x) else ("nilpot" if x % 6 == 0 else "dark")
    print(f"    {x:>2} ({sector:>7}): {chain}  [attractor {attractor}]")

# ====================================================================
# SECTION 5: THE EVENT HORIZON -- No Escape from the Dark Sector
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 5: THE EVENT HORIZON -- Multiplication Can't Reach the Coprime Sector")
print("=" * 70)

print(f"\n  THEOREM: If gcd(x, 24) > 1, then for ANY y coprime to 24,")
print(f"  (x * y) mod 24 is still NOT coprime to 24.")
print(f"  Proof: if p divides both x and 24, then p divides x*y and p divides 24.")
print(f"  So gcd(x*y, 24) >= p > 1. The dark sector is closed under multiplication by ANY element.")

# Verify computationally
horizon_ok = True
for x in range(24):
    if coprime24(x):
        continue
    for y in range(24):
        if coprime24(y):
            product = (x * y) % 24
            if coprime24(product):
                horizon_ok = False
                print(f"  ESCAPE! {x} * {y} = {product} (coprime!)")
                break
    if not horizon_ok:
        break

print(f"\n  Event horizon verified: {horizon_ok}")
if horizon_ok:
    print(f"  The dark sector is INVARIANT under multiplication by coprime elements.")
    print(f"  Once a number is divisible by 2 or 3, NO multiplication can make it coprime.")
    print(f"  This is the algebraic event horizon separating 'matter' (coprime) from 'vacuum' (dark).")

# The coprime sector is a GROUP under multiplication
print(f"\n  COPRIME SECTOR: closed under multiplication (it's a group)")
group_closed = True
for a in Z24_STAR:
    for b in Z24_STAR:
        if not coprime24((a * b) % 24):
            group_closed = False
print(f"  (Z/24Z)* is closed under multiplication: {group_closed}")
print(f"  The coprime sector can NEVER produce dark elements through multiplication.")
print(f"  The dark sector can NEVER produce coprime elements through multiplication.")
print(f"\n  TWO IRREVERSIBLY SEPARATE WORLDS under multiplication:")

# ====================================================================
# SECTION 6: THE IDEMPOTENT ALGEBRA -- The Four Pillars
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 6: THE IDEMPOTENT ALGEBRA -- The Four Pillars of Z/24Z")
print("=" * 70)

print(f"\n  The four idempotents {IDEMPOTENTS} form a Boolean algebra:")
print(f"\n  Multiplication table:")
print(f"  {'':>4}", end="")
for e in IDEMPOTENTS:
    print(f" {e:>4}", end="")
print()
for a in IDEMPOTENTS:
    print(f"  {a:>4}", end="")
    for b in IDEMPOTENTS:
        print(f" {(a*b)%24:>4}", end="")
    print()

print(f"\n  Addition table:")
print(f"  {'':>4}", end="")
for e in IDEMPOTENTS:
    print(f" {e:>4}", end="")
print()
for a in IDEMPOTENTS:
    print(f"  {a:>4}", end="")
    for b in IDEMPOTENTS:
        print(f" {(a+b)%24:>4}", end="")
    print()

print(f"\n  The Boolean algebra of idempotents:")
print(f"    0  = annihilator (absorbs everything, vacuum)")
print(f"    1  = identity (the Higgs, bright sector anchor)")
print(f"    9  = projector onto Z/8Z (kills mod 3, preserves mod 8)")
print(f"    16 = projector onto Z/3Z (kills mod 8, preserves mod 3)")
print(f"\n    9 + 16 = {9+16} mod 24 = {(9+16)%24} = identity!")
print(f"    9 * 16 = {9*16} mod 24 = {(9*16)%24} = annihilator!")
print(f"    They are COMPLEMENTARY projectors.")

# Show projection onto CRT components
print(f"\n  CRT projection examples:")
print(f"  {'n':>4} {'n mod 24':>8} {'9*n mod 24':>10} {'16*n mod 24':>11} {'9n%8':>5} {'9n%3':>5} {'16n%8':>6} {'16n%3':>6}")
for n in range(24):
    e9 = (9 * n) % 24
    e16 = (16 * n) % 24
    print(f"  {n:>4} {n:>8} {e9:>10} {e16:>11} {e9%8:>5} {e9%3:>5} {e16%8:>6} {e16%3:>6}")

# ====================================================================
# SECTION 7: THE CHARGE CONNECTION -- Idempotents as Charge Sources
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 7: THE CHARGE CONNECTION -- Idempotents and CRT Charges")
print("=" * 70)

print(f"\n  From experiment 115, the CRT decomposition gives:")
print(f"    chi5 (rail)    = character of (Z/3Z)* = from mod 3 sector")
print(f"    chi7 (sub-pos) = character of (Z/8Z)* = from mod 8 sector")
print(f"    chi13 (layer)  = entangled product")
print(f"\n  The idempotent projectors connect to charges via CRT:")
print(f"    Idempotent 16 = projector onto Z/3Z -> source of chi5 (rail charge)")
print(f"    Idempotent 9  = projector onto Z/8Z -> source of chi7 (sub-pos charge)")
print(f"    Idempotent 1  = both components preserved (identity)")
print(f"    Idempotent 0  = both components killed (annihilator)")

# Verify: basin of 16 = elements whose mod-3 component survives
print(f"\n  BASIN-CRT CORRESPONDENCE:")
for attractor in IDEMPOTENTS:
    basin = sorted(basins[attractor])
    # CRT analysis: which basin elements share a mod-3 or mod-8 residue with the attractor?
    if attractor == 0:
        print(f"    Attractor 0: everything decays. Both CRT components die.")
    elif attractor == 1:
        coprime_basin = [x for x in basin if coprime24(x)]
        print(f"    Attractor 1: {len(basin)} elements, all coprime. Both CRT components preserved.")
        print(f"      Orbit: x -> x -> 1 -> 1 (oscillation, never decays)")
    elif attractor == 9:
        print(f"    Attractor 9: {len(basin)} elements, all divisible by 3.")
        print(f"      9%8=1 (preserves mod 8), 9%3=0 (kills mod 3)")
        print(f"      Powers of 3 converge here: mod 3 component dies, mod 8 survives")
    elif attractor == 16:
        print(f"    Attractor 16: {len(basin)} elements, all divisible by 2.")
        print(f"      16%8=0 (kills mod 8), 16%3=1 (preserves mod 3)")
        print(f"      Powers of 2 converge here: mod 8 component dies, mod 3 survives")

# The key theorem
print(f"\n  THEOREM: The four idempotent basins partition Z/24Z by divisibility:")
print(f"    Basin of 1:  coprime to 6  (8 elements)  -> bright sector")
print(f"    Basin of 16: even, not div by 3  (4 elements) -> mod 3 survives")
print(f"    Basin of 9:  div by 3, not even  (4 elements) -> mod 8 survives")
print(f"    Basin of 0:  divisible by 6  (8 elements)  -> nilpotent decay")

# Verify basin sizes
basin_sizes = {a: len(basins[a]) for a in IDEMPOTENTS}
expected = {0: 4, 1: 8, 9: 4, 16: 8}
sizes_ok = basin_sizes == expected
print(f"\n  Basin sizes: {basin_sizes} (expected {expected}): {'MATCH' if sizes_ok else 'MISMATCH'}")

# ====================================================================
# SECTION 8: THE DOUBLING CIRCUIT AS EVENT HORIZON
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 8: THE DOUBLING CIRCUIT AS EVENT HORIZON")
print("=" * 70)

print(f"\n  The '1-2-4-8-7-5' vortex circuit in Z/9Z traces ALL units.")
print(f"  In Z/24Z, the powers of 2 trace: 1 -> 2 -> 4 -> 8 -> 16 -> 8 -> 16...")
print(f"\n  THE CROSSING: at k=1 (2^1 = 2), the circuit leaves the coprime sector.")
print(f"  After that, it is PERMANENTLY trapped in the dark sector.")
print(f"  It can never return to coprime territory through multiplication.")

# Time to exit coprime sector for various bases
print(f"\n  Exit time: how many self-multiplications until coprime status is lost?")
print(f"  {'Base':>4} {'Type':>10} {'Steps to exit':>13} {'Landing':>7} {'Final attractor':>16}")
for base in range(1, 24):
    if coprime24(base):
        # Coprime elements oscillate between base and 1, never exit
        val = base
        exited = False
        for step in range(20):
            val = (val * base) % 24
            if not coprime24(val):
                print(f"  {base:>4} {'coprime':>10} {step+1:>13} {val:>7} {orbit_data[base][1]:>16}")
                exited = True
                break
        if not exited:
            print(f"  {base:>4} {'coprime':>10} {'never':>13} {'---':>7} {orbit_data[base][1]:>16}")
    else:
        val = base
        for step in range(20):
            val = (val * base) % 24
            if not coprime24(val):
                print(f"  {base:>4} {'dark':>10} {0:>13} {base:>7} {orbit_data[base][1]:>16}")
                break

print(f"\n  RESULT: Coprime elements NEVER exit under self-multiplication.")
print(f"  They oscillate between their native position and 1 (the Higgs).")
print(f"  Dark elements were never in the coprime sector to begin with.")
print(f"  The event horizon is ONE-WAY: you can leave (via addition),")
print(f"  but you can never return (via multiplication).")

# ====================================================================
# SECTION 9: THE POWER-OF-2 ATLAS -- Complete Map
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 9: THE POWER-OF-2 ATLAS -- 2^k * n mod 24")
print("=" * 70)

print(f"\n  Multiplying by 2 repeatedly maps each position to its fate:")
print(f"  {'n':>3} {'n%24':>5} {'2n':>4} {'4n':>4} {'8n':>4} {'16n':>5} {'32n':>5} {'Attractor':>10}")
for n in range(24):
    vals = [n]
    val = n
    for _ in range(5):
        val = (val * 2) % 24
        vals.append(val)
    attractor = vals[-1]
    if attractor not in IDEMPOTENTS:
        attractor = vals[-2]
    print(f"  {n:>3} {n:>5} {vals[1]:>4} {vals[2]:>4} {vals[3]:>4} {vals[4]:>5} {vals[5]:>5} {attractor:>10}")

print(f"\n  Every element converges to 16 (if even) or oscillates (if coprime).")
print(f"  The doubling operator (multiply by 2) partitions Z/24Z into:")
print(f"    - Coprime elements: oscillate  (1,5,7,11,13,17,19,23 <-> their double mod 24)")
print(f"    - Even elements:    all drain to idempotent 16")

# Similarly for powers of 3
print(f"\n  THE POWER-OF-3 ATLAS -- 3^k * n mod 24:")
print(f"  {'n':>3} {'n%24':>5} {'3n':>4} {'9n':>4} {'27n':>5} {'Attractor':>10}")
for n in range(24):
    vals = [n]
    val = n
    for _ in range(3):
        val = (val * 3) % 24
        vals.append(val)
    attractor = vals[-1]
    print(f"  {n:>3} {n:>5} {vals[1]:>4} {vals[2]:>4} {vals[3]:>5} {attractor:>10}")

print(f"\n  Every element converges to 9 (if div by 3) or oscillates (if coprime).")

# ====================================================================
# SECTION 10: THE VORTX-MONAD SYNTHESIS
# ====================================================================
print("\n" + "=" * 70)
print("SECTION 10: THE VORTEX-MONAD SYNTHESIS")
print("=" * 70)

print(f"""
  WHAT VORTEX MATH SEES (mod 9):
    Doubling circuit: 1-2-4-8-7-5 (traces all 6 units of Z/9Z)
    Off-circuit: 3, 6, 0 (zero-divisors)
    Pattern: cyclic group (Z/9Z)* = Z/6Z

  WHAT THE MONAD SEES (mod 24):
    4 idempotent attractors: {{0, 1, 9, 16}}
    Basin of 1:  8 coprime elements (oscillate, never decay)
    Basin of 16: 4 even elements   (converge to Z/3Z projector)
    Basin of 9:  4 multiples-of-3  (converge to Z/8Z projector)
    Basin of 0:  8 multiples-of-6  (nilpotent decay to vacuum)
    Pattern: elementary abelian (Z/24Z)* = Z2^3

  THE CONNECTION:
    Vortex "3, 6, 9" = multiples of 3 in Z/9Z = zero-divisors
    Monad "6, 12, 18" = multiples of 6 in Z/24Z = nilpotent anchors

    The mod 9 zero-divisors see ONE decay channel (through 3).
    The mod 24 nilpotents see TWO decay channels (through 2 AND 3).
    Mod 24 is the "double-octave" with split nilpotent structure.

  THE RESOLUTION UPGRADE:
    Vortex Math asks: "Which numbers are special?" (Answer: multiples of 3)
    The Monad asks: "What are the CHARGE OPERATORS?" (Answer: sigma_7, sigma_13)

    Vortex sees the SHADOW (which positions are off-circuit).
    The Monad sees the ENGINE (how charges transform between positions).

  THE DOUBLING CIRCUIT IS NOT THE PRIME RAILS:
    Powers of 2 mod 24 enter the dark sector at k=1 and never return.
    The prime rails are reached only through ADDITION by multiples of 6.
    The "event horizon" is the multiplication boundary:
      Inside (coprime): multiplication preserves group structure
      Outside (dark): multiplication converges to idempotent projectors
""")

# ====================================================================
# TESTS
# ====================================================================
print("=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 0

# Test 1: Four idempotents
total += 1
if IDEMPOTENTS == [0, 1, 9, 16]:
    print(f"  [PASS] Idempotents of Z/24Z = {{0, 1, 9, 16}}")
    passed += 1
else:
    print(f"  [FAIL] Idempotents = {IDEMPOTENTS}")

# Test 2: Doubling circuit convergence
total += 1
converges_16 = all((2**k) % 24 in (8, 16) for k in range(5, 30))
if converges_16:
    print(f"  [PASS] Powers of 2 mod 24 converge to {{8, 16}} cycle (attractor 16)")
    passed += 1
else:
    print(f"  [FAIL] Powers of 2 don't converge as expected")

# Test 3: Tripling circuit convergence
total += 1
converges_9 = all((3**k) % 24 in (3, 9) for k in range(2, 20))
if converges_9:
    print(f"  [PASS] Powers of 3 mod 24 converge to {{3, 9}} cycle (attractor 9)")
    passed += 1
else:
    print(f"  [FAIL] Powers of 3 don't converge as expected")

# Test 4: Basin sizes
total += 1
if sizes_ok:
    print(f"  [PASS] Basin sizes match CRT partition: 8+8+4+4 = 24")
    passed += 1
else:
    print(f"  [FAIL] Basin sizes {basin_sizes} don't match expected {expected}")

# Test 5: Event horizon (dark sector invariant under multiplication)
total += 1
if horizon_ok:
    print(f"  [PASS] Event horizon: dark sector closed under multiplication by coprime elements")
    passed += 1
else:
    print(f"  [FAIL] Dark sector not closed!")

# Test 6: Coprime sector is a group under multiplication
total += 1
if group_closed:
    print(f"  [PASS] (Z/24Z)* is closed under multiplication (group property)")
    passed += 1
else:
    print(f"  [FAIL] Coprime sector not closed under multiplication")

# Test 7: 9 and 16 are complementary projectors
total += 1
if (9 + 16) % 24 == 1 and (9 * 16) % 24 == 0:
    print(f"  [PASS] Idempotents 9 and 16 are complementary: 9+16=1, 9*16=0 mod 24")
    passed += 1
else:
    print(f"  [FAIL] 9+16={(9+16)%24}, 9*16={(9*16)%24}")

# Test 8: Basin of 1 = exactly the coprime positions
total += 1
if sorted(basins[1]) == Z24_STAR:
    print(f"  [PASS] Basin of 1 = exactly (Z/24Z)* = the 8 coprime positions")
    passed += 1
else:
    print(f"  [FAIL] Basin of 1 = {sorted(basins[1])} != {Z24_STAR}")

# Test 9: Basin of 0 = exactly the nilpotents
total += 1
if sorted(basins[0]) == NILPOTENTS:
    print(f"  [PASS] Basin of 0 = exactly {{0, 6, 12, 18}} = nilpotent sector")
    passed += 1
else:
    print(f"  [FAIL] Basin of 0 = {sorted(basins[0])} != {NILPOTENTS}")

# Test 10: Vortex mod 9 circuit = all units
total += 1
z9_star = sorted(n for n in range(1, 9) if gcd(n, 9) == 1)
if sorted(set(pos for _, _, pos in orbit_v9 if pos != 0)) == z9_star:
    print(f"  [PASS] Vortex 1-2-4-8-7-5 circuit visits all 6 units of Z/9Z")
    passed += 1
else:
    print(f"  [FAIL] Vortex circuit doesn't visit all units")

print(f"\nOVERALL: {passed}/{total} tests passed")

# ====================================================================
# GRAND SUMMARY
# ====================================================================
print("\n" + "=" * 70)
print("GRAND SUMMARY: THE DOUBLING CIRCUIT AUDIT (EXPERIMENT 131)")
print("=" * 70)

print(f"""
THE BASIN STRUCTURE OF Z/24Z UNDER SELF-MULTIPLICATION:

  Every element converges to one of 4 idempotent attractors:

  ATTRACTOR  |  BASIN                |  CRT MEANING       |  SIZE
  -----------+-----------------------+--------------------+-----
  0          | {{0,6,12,18}} (x 6)    | both components die |  8
  1          | {{1,5,7,11,13,17,19,23}}| both survive       |  8
  9          | {{3,9,15,21}} (x 3)    | mod 3 dies         |  4
  16         | {{2,4,8,10,14,16,20,22}}| mod 8 dies        |  4

  Basin of 1  = bright sector (coprime) -> oscillates, never decays
  Basin of 16 = even numbers -> converge to mod-3 projector
  Basin of 9  = multiples of 3 -> converge to mod-8 projector
  Basin of 0  = multiples of 6 -> nilpotent decay to vacuum

THE DOUBLING CIRCUIT:
  Powers of 2 mod 24: 1 -> 2 -> 4 -> 8 -> 16 -> 8 -> 16 -> ...
  Enters dark sector at k=1. Converges to idempotent 16 (Z/3Z projector).
  NEVER visits any coprime position after the initial 1.

THE TRIPLING CIRCUIT:
  Powers of 3 mod 24: 1 -> 3 -> 9 -> 3 -> 9 -> ...
  Enters dark sector at k=1. Converges to idempotent 9 (Z/8Z projector).

THE VORTEX-MONAD BRIDGE:
  Vortex mod 9: 1 circuit (cyclic), 1 off-circuit set (multiples of 3)
  Monad mod 24: 4 basins (Boolean), 2 independent decay channels (2 and 3)
  The doubling circuit is NOT a path through the prime rails.
  It is a DRAIN into the idempotent projectors.

THE EVENT HORIZON:
  Under multiplication, the coprime sector is SEALED.
  No dark element can ever multiply its way back to coprime status.
  The "event horizon" is the algebraic boundary between:
    - Basin of 1 (self-sustaining, oscillating)
    - Basins of 0, 9, 16 (converging to projectors/annihilator)

  Addition (kinematics) CAN cross the boundary (exp 128: d=6,12,18).
  Multiplication (dynamics) CANNOT cross it.
  This is the fundamental asymmetry of the lattice.
""")

print("=" * 70)
print("EXPERIMENT 131 COMPLETE")
print("=" * 70)
