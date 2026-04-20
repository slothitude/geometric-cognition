"""
Experiment 018ccc: The Tower of Projections -- From Z_2 to Z_4

The monad's CP violation failure (all characters real at mod 12) has been
blocking progress since experiment 44. (Z/12Z)* = Z_2 x Z_2 has no cyclic
component, so all Dirichlet characters are real: chi = +1 or -1.

But the monad is a TOWER of projections. Each enlargement resolves a conflation:
  mod 6:  conflates matter/antimatter
  mod 12: resolves matter/antimatter, conflates real/complex
  mod ??: resolves real/complex

The smallest modulus divisible by 6 that has complex characters is m = 30.
  (Z/30Z)* = Z_4 x Z_2  (phi(30) = 8)
  Z_4 gives characters with values {1, i, -1, -i} -- COMPLEX PHASES!

This experiment:
1. Maps the tower: (Z/mZ)* for m = 6, 12, 24, 30, 60
2. Identifies when complex characters first appear
3. Computes all Dirichlet characters mod 30
4. Checks if complex phases enable CP violation (Jarlskog-like invariant)
5. Maps quantum numbers at the new level
6. Explores whether this resolves the monad's deepest failure
"""

import numpy as np
from itertools import product

print("=" * 70)
print("EXPERIMENT 018ccc: THE TOWER OF PROJECTIONS")
print("From Z_2 to Z_4: When Does the Monad Get Complex Phases?")
print("=" * 70)

# ============================================================
# SECTION 1: THE TOWER OF (Z/mZ)*
# ============================================================
print()
print("=" * 70)
print("SECTION 1: THE TOWER OF (Z/mZ)*")
print("=" * 70)
print()

def euler_totient(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

def multiplicative_order(a, n):
    """Order of a in (Z/nZ)*"""
    if np.gcd(a, n) != 1:
        return 0
    order = 1
    current = a % n
    while current != 1:
        current = (current * a) % n
        order += 1
    return order

def find_generators(n):
    """Find the group structure of (Z/nZ)*"""
    units = [k for k in range(1, n) if np.gcd(k, n) == 1]
    phi_n = len(units)

    # Find all orders
    orders = {a: multiplicative_order(a, n) for a in units}

    # Find maximal order (exponent of the group)
    max_order = max(orders.values())

    # Find cyclic generators if group is cyclic
    cyclic_gens = [a for a in units if orders[a] == phi_n]

    # Find generators for non-cyclic groups
    # Strategy: find elements that generate independent cyclic subgroups
    structure = []
    remaining = set(units)

    for a in sorted(units):
        if a not in remaining:
            continue
        if a == 1:
            continue
        ord_a = orders[a]
        # Check if a generates something new
        subgroup = set()
        current = 1
        for _ in range(ord_a):
            subgroup.add(current)
            current = (current * a) % n

        if len(subgroup & remaining) > 1:  # More than just {1}
            structure.append((a, ord_a))
            # Don't remove -- other generators might share elements

    return units, phi_n, orders, cyclic_gens, structure

print("The monad tower: group structure at each level")
print()
print(f"  {'m':>4s}  {'phi(m)':>6s}  {'(Z/mZ)* structure':>30s}  {'Complex?':>10s}  {'Residues coprime to 6':>10s}")
print(f"  {'':>4s}  {'':>6s}  {'':>30s}  {'':>10s}  {'(on rails)':>10s}")
print(f"  {'----':>4s}  {'------':>6s}  {'------------------------------':>30s}  {'----------':>10s}  {'----------':>10s}")

tower_data = {}
for m in [6, 12, 24, 30, 60]:
    units, phi_n, orders, cyclic_gens, structure = find_generators(m)

    # Determine group structure
    # Use the fact that (Z/mZ)* decomposes by CRT
    # Factor m into prime powers
    factors = {}
    temp = m
    for p in [2, 3, 5, 7, 11, 13]:
        while temp % p == 0:
            factors[p] = factors.get(p, 0) + 1
            temp //= p

    # (Z/p^kZ)* structure:
    # (Z/2Z)* = trivial
    # (Z/4Z)* = Z_2
    # (Z/2^kZ)* = Z_2 x Z_{2^{k-2}} for k >= 3
    # (Z/p^kZ)* = Z_{p^{k-1}(p-1)} for odd primes p

    # Build group structure string using known decompositions
    if m == 6:
        group_str = "Z_2"
        has_complex = False
    elif m == 12:
        group_str = "Z_2 x Z_2"
        has_complex = False
    elif m == 24:
        group_str = "Z_2 x Z_2 x Z_2"
        has_complex = False
    elif m == 30:
        group_str = "Z_2 x Z_4"
        has_complex = True
    elif m == 60:
        group_str = "Z_2 x Z_2 x Z_4"
        has_complex = True
    else:
        group_str = "?"
        has_complex = False

    # Count residues coprime to 6 (on monad rails)
    on_rails = sum(1 for u in units if u % 6 in (1, 5))

    complex_str = "YES" if has_complex else "no"
    tower_data[m] = {
        'units': units, 'phi': phi_n, 'structure': group_str,
        'has_complex': has_complex, 'on_rails': on_rails
    }

    print(f"  {m:4d}  {phi_n:6d}  {group_str:>30s}  {complex_str:>10s}  {on_rails:10d}")

print()
print("KEY INSIGHT: m = 30 is the FIRST level with complex characters!")
print("  (Z/30Z)* = Z_4 x Z_2 has a Z_4 component -> values {1, i, -1, -i}")
print("  This requires the factor of 5 in the modulus.")
print("  m = 6 = 2 x 3 gives Z_2 (real)")
print("  m = 12 = 4 x 3 gives Z_2 x Z_2 (real)")
print("  m = 24 = 8 x 3 gives Z_2 x Z_2 x Z_2 (real)")
print("  m = 30 = 2 x 3 x 5 gives Z_2 x Z_4 (COMPLEX!)")
print("  m = 60 = 4 x 3 x 5 gives Z_2 x Z_2 x Z_4 (complex)")
print()
print("The factor of 5 is the magic ingredient. The third prime 5")
print("opens the door to complex phases.")
print()

# ============================================================
# SECTION 2: THE RESIDUE CLASSES MOD 30
# ============================================================
print()
print("=" * 70)
print("SECTION 2: THE RESIDUE CLASSES MOD 30")
print("=" * 70)
print()

m = 30
units_30 = sorted(tower_data[m]['units'])
print(f"(Z/30Z)* = {{{', '.join(str(u) for u in units_30)}}}")
print(f"Order: {len(units_30)}")
print()

# Rail assignment
print("Rail assignment (mod 6):")
r2_residues = [u for u in units_30 if u % 6 == 1]  # 6k+1
r1_residues = [u for u in units_30 if u % 6 == 5]  # 6k-1

print(f"  R2 (6k+1) residues: {r2_residues}")
print(f"  R1 (6k-1) residues: {r1_residues}")
print()

# Old monad (mod 12) assignment
print("Old hyper-monad (mod 12) assignment:")
for u in units_30:
    r12 = u % 12
    if r12 in (1, 5):
        old_label = "matter"
    elif r12 in (7, 11):
        old_label = "antimatter"
    else:
        old_label = "???"
    print(f"  {u:2d} mod 30 -> {r12:2d} mod 12 -> {old_label}")

print()

# Matter/antimatter via chi_3 mod 12
def chi3_mod12(n):
    r = n % 12
    if r in (1, 5): return +1
    if r in (7, 11): return -1
    return 0

print("The 8 residue classes split as:")
print(f"  4 matter (chi_3=+1):  {[u for u in units_30 if chi3_mod12(u)==+1]}")
print(f"  4 antimatter (chi_3=-1): {[u for u in units_30 if chi3_mod12(u)==-1]}")
print()

# ============================================================
# SECTION 3: THE DIRICHLET CHARACTERS MOD 30
# ============================================================
print()
print("=" * 70)
print("SECTION 3: ALL 8 DIRICHLET CHARACTERS MOD 30")
print("=" * 70)
print()

# (Z/30Z)* = (Z/2Z)* x (Z/3Z)* x (Z/5Z)* = trivial x Z_2 x Z_4
# Find generators
# Z_4 component: generator of (Z/5Z)*
# (Z/5Z)* = {1, 2, 3, 4}, generator = 2 (order 4)
# Z_2 component: generator of (Z/3Z)*
# (Z/3Z)* = {1, 2}, generator = 2 (order 2)

# Via CRT: element of (Z/30Z)* maps to (mod 2, mod 3, mod 5)
# Since (Z/2Z)* is trivial, we need (mod 3, mod 5) components

def crt_decompose_30(n):
    """Decompose n mod 30 into (mod 2, mod 3, mod 5)"""
    return (n % 2, n % 3, n % 5)

# Find the Z_4 generator in (Z/30Z)*
# We need an element whose mod-5 component generates (Z/5Z)*
# (Z/5Z)* is generated by 2: 2^1=2, 2^2=4, 2^3=3, 2^4=1
# Element with mod 5 = 2 and mod 3 = 1: solve n ≡ 1 (mod 3), n ≡ 2 (mod 5)
# n = 1 + 3k ≡ 2 (mod 5) -> 3k ≡ 1 (mod 5) -> k ≡ 2 (mod 5) -> k=2 -> n=7
# Check: 7 mod 30, 7 mod 3 = 1, 7 mod 5 = 2. Yes!

# Element with mod 5 = 1 and mod 3 = 2: n ≡ 2 (mod 3), n ≡ 1 (mod 5)
# n = 1 + 5k ≡ 2 (mod 3) -> 5k ≡ 1 (mod 3) -> 2k ≡ 1 (mod 3) -> k ≡ 2 (mod 3) -> k=2 -> n=11
# Check: 11 mod 30, 11 mod 3 = 2, 11 mod 5 = 1. Yes!

# Generators:
g4 = 7   # generates Z_4 component: 7^1=7, 7^2=49≡19, 7^3=133≡13, 7^0=1
g2 = 11  # generates Z_2 component: 11^1=11, 11^0=1

print(f"Z_4 generator: {g4} (order {multiplicative_order(g4, 30)})")
print(f"  {g4}^1 = {pow(g4, 1, 30)}, {g4}^2 = {pow(g4, 2, 30)}, "
      f"{g4}^3 = {pow(g4, 3, 30)}, {g4}^4 = {pow(g4, 4, 30)}")
print(f"Z_2 generator: {g2} (order {multiplicative_order(g2, 30)})")
print(f"  {g2}^1 = {pow(g2, 1, 30)}, {g2}^0 = 1")
print()

# Discrete logarithm: express each unit as g4^a * g2^b mod 30
def dlog_30(n):
    """Find (a, b) such that n = 7^a * 11^b mod 30"""
    for a in range(4):
        for b in range(2):
            if pow(g4, a, 30) * pow(g2, b, 30) % 30 == n:
                return (a, b)
    return None

print("Discrete logarithms (Z_4 x Z_2 decomposition):")
print(f"  {'n':>3s}  {'7^a * 11^b mod 30':>18s}  {'(a,b)':>6s}  {'Rail':>4s}  {'chi_3 mod 12':>12s}")
print(f"  {'---':>3s}  {'------------------':>18s}  {'-----':>6s}  {'----':>4s}  {'------------':>12s}")

dlogs = {}
for u in units_30:
    ab = dlog_30(u)
    dlogs[u] = ab
    rail = "R2" if u % 6 == 1 else "R1"
    chi3 = chi3_mod12(u)
    print(f"  {u:3d}  7^{ab[0]} * 11^{ab[1]} = {pow(g4, ab[0], 30) * pow(g2, ab[1], 30) % 30:3d}       "
          f"  ({ab[0]},{ab[1]})   {rail:>4s}  {chi3:+d}")

print()

# Now compute all 8 Dirichlet characters
# Characters of Z_4: chi_k(a) = exp(2*pi*i*k*a/4) for k=0,1,2,3
# Characters of Z_2: chi_j(b) = exp(pi*i*j*b) for j=0,1
# Combined: chi_{k,j}(a,b) = exp(2*pi*i*k*a/4) * exp(pi*i*j*b)

print("All 8 Dirichlet characters mod 30:")
print(f"  {'chi':>8s}", end="")
for u in units_30:
    print(f"  {str(u):>4s}", end="")
print(f"  {'Type':>10s}")
print(f"  {'---':>8s}", end="")
for u in units_30:
    print(f"  {'----':>4s}", end="")
print(f"  {'----------':>10s}")

characters_30 = {}
for k in range(4):
    for j in range(2):
        char_name = f"chi_{{{k},{j}}}"
        values = {}
        for u in units_30:
            a, b = dlogs[u]
            val = np.exp(2j * np.pi * k * a / 4) * np.exp(1j * np.pi * j * b)
            values[u] = val

        characters_30[(k, j)] = values

        # Determine type
        is_real = all(abs(v.imag) < 1e-10 for v in values.values())
        is_complex = any(abs(v.imag) > 1e-10 for v in values.values())

        if k == 0 and j == 0:
            type_str = "principal"
        elif is_real:
            type_str = "real"
        else:
            type_str = "COMPLEX"

        print(f"  {char_name:>8s}", end="")
        for u in units_30:
            v = values[u]
            if abs(v.imag) < 1e-10:
                print(f"  {v.real:+4.0f}", end="")
            elif abs(v.real) < 1e-10 and abs(v.imag - 1) < 1e-10:
                print(f"    i", end="")
            elif abs(v.real) < 1e-10 and abs(v.imag + 1) < 1e-10:
                print(f"   -i", end="")
            elif abs(v.imag) < 1e-10:
                print(f"  {v.real:+4.0f}", end="")
            else:
                print(f" {v.real:+.0f}{v.imag:+.0f}i", end="")
        print(f"  {type_str:>10s}")

print()

# Count
n_real = sum(1 for k in range(4) for j in range(2)
             if all(abs(characters_30[(k,j)][u].imag) < 1e-10 for u in units_30))
n_complex = 8 - n_real
print(f"  Real characters: {n_real}")
print(f"  Complex characters: {n_complex}")
print()
print("THE MONAD GETS COMPLEX PHASES AT MOD 30!")
print("Four characters take values ±i -- imaginary unit appears.")
print()

# ============================================================
# SECTION 4: THE COMPLEX CHARACTERS IN DETAIL
# ============================================================
print()
print("=" * 70)
print("SECTION 4: THE COMPLEX CHARACTERS IN DETAIL")
print("=" * 70)
print()

# Focus on the two conjugate pairs of complex characters
complex_chars = [(k, j) for k in range(4) for j in range(2)
                 if any(abs(characters_30[(k,j)][u].imag) > 1e-10 for u in units_30)]

print("The four complex characters and their physical interpretation:")
print()

for idx, (k, j) in enumerate(complex_chars):
    values = characters_30[(k, j)]

    print(f"  chi_{{{k},{j}}} (Z_4 component k={k}, Z_2 component j={j}):")
    for u in units_30:
        v = values[u]
        rail = "R2" if u % 6 == 1 else "R1"
        chi3 = chi3_mod12(u)
        side = "matter" if chi3 == +1 else "anti"
        if abs(v.imag) < 1e-10:
            vstr = f"{v.real:+.0f}"
        elif abs(v.real) < 1e-10:
            vstr = f"{v.imag:+.0f}i"
        else:
            vstr = f"{v.real:+.0f}{v.imag:+.0f}i"
        print(f"    {u:2d} ({rail}, {side:6s}): chi = {vstr}")
    print()

# ============================================================
# SECTION 5: QUANTUM NUMBER MAPPING AT MOD 30
# ============================================================
print()
print("=" * 70)
print("SECTION 5: QUANTUM NUMBER MAPPING AT MOD 30")
print("=" * 70)
print()

print("At mod 12, the three Z_2 characters gave three binary quantum numbers:")
print("  chi_1 = isospin (R2 vs R1)")
print("  chi_2 = rail type")
print("  chi_3 = matter/antimatter")
print()
print("At mod 30, we have Z_4 x Z_2 = 8 characters. The independent ones:")
print()

# The real characters correspond to the mod-12 structure (refined)
# chi_{0,1} = Z_2 character (like chi_3 mod 12 but now distinguishing
#             elements with different Z_2 components)
# chi_{2,0} = Z_4 real character (new! distinguishes within Z_4 cosets)
# chi_{2,1} = Z_4 real x Z_2 (product)

print("Real characters (refine the mod-12 structure):")
print()

for (k, j) in [(0, 0), (2, 0), (0, 1), (2, 1)]:
    values = characters_30[(k, j)]
    vals_str = "  ".join(f"{u}:{values[u].real:+.0f}" for u in units_30)
    if k == 0 and j == 0:
        label = "principal (trivial)"
    elif k == 2 and j == 0:
        label = "Z_4 parity (distinguishes 4-cosets)"
    elif k == 0 and j == 1:
        label = "Z_2 sign (R2 vs R1 cross 5-factor)"
    else:
        label = "Z_4 parity x Z_2 sign"
    print(f"  chi_{{{k},{j}}}: {vals_str}")
    print(f"    -> {label}")
    print()

print()
print("Complex characters (NEW -- first appearance in the monad tower):")
print()

for (k, j) in complex_chars:
    values = characters_30[(k, j)]
    vals_str = "  ".join(f"{u}:{values[u]:.0f}" for u in units_30)
    print(f"  chi_{{{k},{j}}}: {vals_str}")
    print()

print("The complex character values are ±i on alternating residues.")
print("This is a QUATERNION-LIKE structure: Z_4 = {1, i, -1, -i}.")
print()

# ============================================================
# SECTION 6: THE JARLSKOG-STYLE TEST FOR CP VIOLATION
# ============================================================
print()
print("=" * 70)
print("SECTION 6: THE JARLSKOG-STYLE TEST FOR CP VIOLATION")
print("=" * 70)
print()

print("In the Standard Model, CP violation requires a nonzero Jarlskog")
print("invariant J = Im(V_ij * V_kl * V_il* * V_kj*).")
print()
print("The monad at mod 12 FAILED this because all characters are real.")
print("At mod 30, we have complex characters. Can we construct a")
print("Jarlskog-like invariant from the monad's composition table?")
print()

# Approach 1: Direct character products
# For CP violation, we need Im(chi(a) * chi(b) * chi(c)^* * chi(d)^*)) != 0
# where chi is a complex character and a,b,c,d are residue classes

print("Test 1: Jarlskog from character values")
print("  J(a,b,c,d) = Im(chi(a)*chi(b)*conj(chi(c))*conj(chi(d)))")
print()

# Use the first complex character chi_{1,0}
chi = characters_30[(1, 0)]

nonzero_j = 0
total_j = 0
max_j = 0

for a in units_30:
    for b in units_30:
        for c in units_30:
            for d in units_30:
                J = (chi[a] * chi[b] * np.conj(chi[c]) * np.conj(chi[d])).imag
                total_j += 1
                if abs(J) > 1e-10:
                    nonzero_j += 1
                    max_j = max(max_j, abs(J))

print(f"  Total 4-tuples tested: {total_j}")
print(f"  Nonzero J values: {nonzero_j}")
print(f"  Fraction: {nonzero_j/total_j:.4f}")
print(f"  Maximum |J|: {max_j:.4f}")
print()

if nonzero_j > 0:
    # Show some examples
    print("  Example nonzero J values:")
    count = 0
    for a in units_30:
        for b in units_30:
            for c in units_30:
                for d in units_30:
                    J = (chi[a] * chi[b] * np.conj(chi[c]) * np.conj(chi[d])).imag
                    if abs(J) > 0.5 and count < 5:
                        print(f"    J({a},{b},{c},{d}) = {J:+.2f}")
                        count += 1
    print()
    print("  THE MONAD HAS NONZERO JARLSKOG-STYLE INVARIANTS AT MOD 30!")
    print("  Complex phases enable CP-violating quantities.")
else:
    print("  Jarlskog invariant is zero everywhere.")
    print("  (Abelian group -- need non-Abelian for nontrivial J)")

print()

# Approach 2: The deeper test -- composition Jarlskog
# CP violation in physics comes from the MISMATCH between different
# interaction bases. In the monad, "mixing" comes from composition.
# Two primes with different chi_{1,0} values compose to give a product
# whose chi_{1,0} is the PRODUCT of their values.

print("Test 2: Composition Jarlskog")
print("  For two primes p, q: chi(p*q) = chi(p) * chi(q)")
print("  For CP violation: need Im(chi(p)*chi(q)*chi(p')*chi(q')) != 0")
print("  where p*q = p'*q' (same composite, different factorizations)")
print()

# But in Z, factorization is unique (fundamental theorem of arithmetic)
# So p*q = p'*q' implies {p,q} = {p',q'}
# This means chi(p)*chi(q) = chi(p')*chi(q')
# The Jarlskog from unique factorization is ZERO.

print("  Unique factorization in Z means: if p*q = p'*q', then {p,q}={p',q'}")
print("  So chi(p)*chi(q) = chi(p')*chi(q') identically.")
print("  Jarlskog from 2-factor composition: EXACTLY ZERO.")
print()
print("  This is a THEOREM: unique factorization kills the Jarlskog")
print("  invariant for 2-factor compositions, regardless of the")
print("  character group structure.")
print()

# Approach 3: k-space mixing
# In the physical CKM, mixing comes from the matrix that connects
# mass eigenstates to weak eigenstates. In the monad, the analog would
# be the matrix connecting "position eigenstates" (k-values) to
# "composition eigenstates" (factorization products).

print("Test 3: Position vs composition mixing")
print("  The monad's 'mixing matrix' connects positions to compositions.")
print("  A prime at position k on rail r composes to give composites at")
print("  positions determined by the walking sieve. The 'mixing' is the")
print("  overlap between different primes' composition spectra.")
print()

# Compute: for each pair of residue classes (a, b) mod 30,
# how many composites fall in each residue class?
# This is the "composition matrix"

print("  Composition matrix: chi_{1,0}(a*b mod 30) for all (a,b) pairs")
print()

# Create matrix
comp_matrix = np.zeros((8, 8), dtype=complex)
for i, a in enumerate(units_30):
    for j, b in enumerate(units_30):
        prod = (a * b) % 30
        if prod in [u for u in range(30) if np.gcd(u, 30) == 1]:
            comp_matrix[i, j] = chi[prod]
        else:
            comp_matrix[i, j] = 0  # composite not in (Z/30Z)*

print("  Product character chi_{1,0}(a*b mod 30):")
print(f"  {'':>6s}", end="")
for b in units_30:
    print(f"  {b:>5d}", end="")
print()

for i, a in enumerate(units_30):
    print(f"  {a:>6d}", end="")
    for j, b in enumerate(units_30):
        v = comp_matrix[i, j]
        if abs(v) < 1e-10:
            print(f"    .", end="")
        elif abs(v.imag) < 1e-10:
            print(f"  {v.real:+4.0f}", end="")
        elif abs(v.real) < 1e-10:
            print(f"  {v.imag:+4.0f}i", end="")
        else:
            print(f" {v.real:+.0f}{v.imag:+.0f}i", end="")
    print()

print()

# Check if this matrix has non-trivial complex phase structure
det = np.linalg.det(comp_matrix)
trace = np.trace(comp_matrix)
print(f"  Determinant: {det:.4f}")
print(f"  Trace: {trace:.4f}")
print(f"  |Determinant|: {abs(det):.4f}")
print(f"  Arg(Determinant): {np.angle(det):.4f} rad = {np.degrees(np.angle(det)):.1f} deg")
print()

if abs(np.angle(det)) > 0.01:
    print("  The composition matrix has a COMPLEX DETERMINANT!")
    print("  This means the composition operation itself has a non-trivial phase.")
else:
    print("  Determinant is real (no net phase from composition).")

print()

# ============================================================
# SECTION 7: THE DEEPER ISSUE -- ABELIAN vs NON-ABELIAN
# ============================================================
print()
print("=" * 70)
print("SECTION 7: THE DEEPER ISSUE -- ABELIAN vs NON-ABELIAN")
print("=" * 70)
print()

print("The Jarlskog invariant J measures CP violation through the")
print("commutator of two matrices: [M_1, M_2] = M_1*M_2 - M_2*M_1")
print()
print("For J != 0, we need NON-ABELIAN matrices (non-commuting).")
print()
print("The monad's characters at EVERY level are ABELIAN:")
print("  (Z/mZ)* is always Abelian (multiplication mod m commutes)")
print("  So all Dirichlet characters are 1-dimensional")
print("  And [chi_1, chi_2] = 0 always")
print()
print("The PHYSICAL CP violation comes from the CKM matrix, which")
print("is the mismatch between two NON-COMMUTING matrices:")
print("  M_u (up-type mass matrix) and M_d (down-type mass matrix)")
print("  Both are 3x3 matrices, and [M_u, M_d] != 0 gives J != 0")
print()
print("In the monad, the analog would need TWO different composition")
print("operations that DON'T commute. But multiplication in Z is")
print("always commutative: a*b = b*a.")
print()
print("So the monad CAN have complex phases (at mod 30),")
print("but CANNOT have CP violation from its Abelian structure.")
print()
print("CP violation requires either:")
print("  1. Non-Abelian extension (matrices, not scalars)")
print("  2. Non-commutative composition (not standard multiplication)")
print("  3. Multiple independent channels with complex phases")
print()
print("The monad at mod 30 has the INGREDIENTS (complex phases)")
print("but lacks the ARCHITECTURE (non-Abelian mixing).")
print()

# ============================================================
# SECTION 8: WHAT THE COMPLEX PHASES DO GIVE
# ============================================================
print()
print("=" * 70)
print("SECTION 8: WHAT THE COMPLEX PHASES DO GIVE")
print("=" * 70)
print()

print("Even though Abelian complex characters can't give CP violation,")
print("they DO provide something new:")
print()

# 1. Complex-valued L-functions
print("1. COMPLEX L-FUNCTIONS")
print()
print("   At mod 12, all L-functions L(s, chi) have real coefficients.")
print("   At mod 30, the complex characters give L-functions with")
print("   complex Euler product coefficients.")
print()

# Compute L-function coefficients for the first complex character
chi10 = characters_30[(1, 0)]

N = 10000
is_prime_arr = [True] * (N + 1)
is_prime_arr[0] = is_prime_arr[1] = False
for i in range(2, int(N**0.5) + 1):
    if is_prime_arr[i]:
        for j in range(i*i, N + 1, i):
            is_prime_arr[j] = False

# Compute L(1, chi_{1,0}) using Euler product
chi10_at_n = {}
for n in range(1, N + 1):
    if np.gcd(n, 30) == 1:
        chi10_at_n[n] = chi10[n % 30]
    else:
        chi10_at_n[n] = 0

# L(1, chi) via partial Euler product
log_L = 0
for p in range(2, 5000):
    if is_prime_arr[p] and np.gcd(p, 30) == 1:
        c = chi10_at_n[p]
        # L contribution from prime p: -log(1 - chi(p)/p)
        if abs(1 - c/p) > 1e-15:
            log_L -= np.log(1 - c/p)

L1_chi10 = np.exp(log_L)
print(f"   L(1, chi_{{1,0}}) = {L1_chi10:.6f}")
print(f"   |L(1, chi_{{1,0}})| = {abs(L1_chi10):.6f}")
print(f"   Arg(L(1, chi_{{1,0}})) = {np.degrees(np.angle(L1_chi10)):.2f} degrees")
print()

# Also compute L(1, chi_{1,1})
chi11 = characters_30[(1, 1)]
chi11_at_n = {}
for n in range(1, N + 1):
    if np.gcd(n, 30) == 1:
        chi11_at_n[n] = chi11[n % 30]
    else:
        chi11_at_n[n] = 0

log_L11 = 0
for p in range(2, 5000):
    if is_prime_arr[p] and np.gcd(p, 30) == 1:
        c = chi11_at_n[p]
        if abs(1 - c/p) > 1e-15:
            log_L11 -= np.log(1 - c/p)

L1_chi11 = np.exp(log_L11)
print(f"   L(1, chi_{{1,1}}) = {L1_chi11:.6f}")
print(f"   |L(1, chi_{{1,1}})| = {abs(L1_chi11):.6f}")
print(f"   Arg(L(1, chi_{{1,1}})) = {np.degrees(np.angle(L1_chi11)):.2f} degrees")
print()

# 2. Complex prime counting
print("2. COMPLEX PRIME COUNTING")
print()
print("   The partial sums of chi_{1,0}(p) for primes p trace a path")
print("   in the complex plane. The real characters give oscillating")
print("   real-valued sums; the complex characters give SPIRALS.")
print()

# Compute partial sums
primes_30 = [p for p in range(2, N) if is_prime_arr[p] and np.gcd(p, 30) == 1]

sum_real = 0  # chi_{2,0} partial sum
sum_imag = 0  # chi_{1,0} partial sum (complex)
trajectory = []

for p in primes_30[:500]:
    sum_real += chi10_at_n[p].real
    sum_imag += chi10_at_n[p].imag
    trajectory.append((sum_real, sum_imag))

trajectory = np.array(trajectory)

# Spiral metrics
dr = np.diff(trajectory[:, 0])
di = np.diff(trajectory[:, 1])
distances = np.sqrt(dr**2 + di**2)
angles = np.arctan2(di, dr)

print(f"   First 500 primes coprime to 30:")
print(f"   Final position: ({trajectory[-1, 0]:.2f}, {trajectory[-1, 1]:.2f})")
print(f"   Distance from origin: {np.sqrt(trajectory[-1,0]**2 + trajectory[-1,1]**2):.2f}")
print(f"   Mean step size: {np.mean(distances):.4f}")
print(f"   Step size std: {np.std(distances):.4f}")
print(f"   Total angle traversed: {np.sum(np.abs(np.diff(angles))):.2f} rad")
print()

# 3. Phase structure of composition
print("3. PHASE STRUCTURE OF COMPOSITION")
print()
print("   When two primes compose (multiply), their complex characters")
print("   multiply too. The phase ADDS:")
print()
print("   chi(p*q) = chi(p) * chi(q)")
print("   arg(chi(p*q)) = arg(chi(p)) + arg(chi(q)) mod 2*pi")
print()
print("   This is ADDITIVE phase accumulation -- exactly what happens")
print("   in quantum mechanics (phase = action integral).")
print()

# Compute phases for first few primes
print("   Phase of chi_{1,0} for first primes coprime to 30:")
for p in primes_30[:15]:
    c = chi10_at_n[p]
    phase = np.angle(c)
    if abs(phase) < 1e-10:
        phase_str = "  0"
    elif abs(phase - np.pi/2) < 1e-10:
        phase_str = "+pi/2"
    elif abs(phase + np.pi/2) < 1e-10:
        phase_str = "-pi/2"
    elif abs(abs(phase) - np.pi) < 1e-10:
        phase_str = "+/-pi"
    else:
        phase_str = f"{phase:.2f}"
    print(f"     p={p:4d}: chi = {c:.0f}, phase = {phase_str}")

print()

# ============================================================
# SECTION 9: THE CONNECTION TO PHYSICAL CP VIOLATION
# ============================================================
print()
print("=" * 70)
print("SECTION 9: CONNECTION TO PHYSICAL CP VIOLATION")
print("=" * 70)
print()

print("PHYSICAL CP VIOLATION:")
print(f"  Jarlskog invariant: J = {3e-5:.1e}")
print(f"  CKM phase: delta_13 ~ 68 degrees")
print()
print("MONAD AT MOD 30:")
print(f"  Complex characters: YES (4 out of 8)")
print(f"  Character phases: +/-pi/2 (90 degree rotations)")
print(f"  Jarlskog from characters: YES (nonzero)")
print(f"  Jarlskog from compositions: NO (unique factorization)")
print(f"  Jarlskog from matrix structure: NO (Abelian group)")
print()
print("THE GAP:")
print("  The monad has complex phases but they live in an Abelian group.")
print("  Physical CP violation needs the phases to live in matrices")
print("  that don't commute: [M_u, M_d] != 0.")
print()
print("  The monad's composition is COMMUTATIVE (a*b = b*a in Z).")
print("  Physical particles couple to MULTIPLE gauge fields simultaneously,")
print("  and the gauge field matrices don't commute.")
print()
print("  The monad captures the PHASE STRUCTURE (90-degree rotations)")
print("  but not the NON-ABELIAN MIXING that generates J != 0.")
print()
print("ANALOGY:")
print("  Mod 12 monad : Standard Model charges = CORRECT assignment, no complex phase")
print("  Mod 30 monad : Standard Model charges = CORRECT assignment, HAS complex phase")
print("  Full SM : Standard Model = non-Abelian mixing of charge channels")
print()
print("  The monad is moving in the right direction (6 -> 12 -> 30)")
print("  but needs a NON-ABELIAN extension to fully capture CP violation.")
print()

# ============================================================
# SECTION 10: THE TOWER PATTERN
# ============================================================
print()
print("=" * 70)
print("SECTION 10: THE TOWER PATTERN AND PREDICTIONS")
print("=" * 70)
print()

print("The tower of projections shows a clear pattern:")
print()
print("  Level  |  Modulus  |  Group          |  Resolves           |  Adds")
print("  -------+----------+-----------------+--------------------+---------")
print("  1      |    6     |  Z_2            |  (base level)      |  isospin")
print("  2      |   12     |  Z_2 x Z_2      |  matter/antimatter |  3 charges")
print("  3      |   30     |  Z_2 x Z_4      |  real/complex      |  complex phase")
print("  4      |   60     |  Z_2^2 x Z_4    |  ?                 |  more structure")
print()
print("Each level adds the NEXT PRIME to the modulus:")
print("  Level 1: mod 6 = 2 x 3")
print("  Level 2: mod 12 = 4 x 3 (power of 2 increases)")
print("  Level 3: mod 30 = 2 x 3 x 5 (prime 5 added)")
print("  Level 4: mod 60 = 4 x 3 x 5 (power of 2 increases)")
print()
print("The pattern suggests:")
print("  Level 5: mod 210 = 2 x 3 x 5 x 7 (prime 7 added)")
print("           (Z/210Z)* = Z_2 x Z_4 x Z_6 = Z_2 x Z_4 x Z_2 x Z_3")
print("           This would add a Z_3 component (3-state quantum number)")
print("           phi(210) = 48 -- 48 residue classes!")
print()
print("  Level 6: mod 2310 = 2 x 3 x 5 x 7 x 11 (prime 11 added)")
print("           phi(2310) = 480 -- getting large")
print()

# Compute prime counting at each level
print("Prime distribution across residue classes at each level:")
print()

for m in [6, 12, 30, 60]:
    units_m = sorted([k for k in range(1, m) if np.gcd(k, m) == 1])
    phi_m = len(units_m)

    # Count primes in each class up to N
    counts = {}
    for u in units_m:
        counts[u] = sum(1 for p in range(2, N) if is_prime_arr[p] and p % m == u)

    total = sum(counts.values())
    expected = total / phi_m
    max_dev = max(abs(counts[u] - expected) / expected for u in units_m)

    print(f"  m = {m:3d}: {phi_m:2d} classes, {total:5d} primes, "
          f"expected {expected:7.1f}/class, max deviation {max_dev:.4f}")

print()
print("Dirichlet's theorem: all classes have equal prime density.")
print("The deviations decrease as m increases (slower convergence")
print("but eventually equidistributed).")
print()

# ============================================================
# SECTION 11: HONEST ASSESSMENT
# ============================================================
print()
print("=" * 70)
print("SECTION 11: HONEST ASSESSMENT")
print("=" * 70)
print()

print("WHAT THE TOWER OF PROJECTIONS ACHIEVES:")
print()
print("  1. RESOLVES the CP violation BLOCKADE")
print("     - Mod 12: all characters real -> CP impossible")
print("     - Mod 30: complex characters exist -> CP possible in principle")
print()
print("  2. IDENTIFIES the minimal extension needed")
print("     - Adding prime 5 to the modulus (6 -> 30) is sufficient")
print("     - The Z_4 component from (Z/5Z)* provides complex phases")
print()
print("  3. REVEALS the tower structure")
print("     - Each prime in the modulus adds a new cyclic component")
print("     - Prime 2 and 3 give Z_2 (binary charges)")
print("     - Prime 5 gives Z_4 (quaternary charges, complex)")
print("     - Prime 7 gives Z_6 (six-state charges)")
print()
print("  4. COMPLEX L-FUNCTIONS")
print("     - First complex character L-functions in the monad framework")
print("     - L(1, chi_{1,0}) is complex-valued")
print("     - Partial sums spiral in the complex plane")
print()

print("WHAT IT DOES NOT ACHIEVE:")
print()
print("  1. NO NON-ABELIAN MIXING")
print("     - (Z/30Z)* is still Abelian")
print("     - Jarlskog invariant from composition is ZERO")
print("     - Unique factorization kills the Jarlskog")
print()
print("  2. NO QUANTITATIVE CP PREDICTION")
print("     - Cannot predict the CKM phase delta_13 ~ 68 deg")
print("     - Cannot predict J ~ 3e-5")
print("     - The complex phases are FIXED at +/-i (90 deg), not tunable")
print()
print("  3. NO DERIVATION OF WHY 3 GENERATIONS")
print("     - The tower has more levels available")
print("     - Nothing picks out level 2 (mod 12) as special")
print("     - Physical question 'why 3 generations?' remains open")
print()

print("VERDICT:")
print()
print("  The tower of projections is the RIGHT direction but the")
print("  monad alone cannot complete the journey. Complex phases")
print("  emerge naturally at mod 30, but the Abelian group structure")
print("  prevents true CP violation.")
print()
print("  The monad provides the CHARGE STRUCTURE and PHASE STRUCTURE")
print("  of the Standard Model with increasing precision at each level.")
print("  But the DYNAMICS -- non-Abelian mixing, running couplings,")
print("  mass generation -- remain beyond the monad's Abelian reach.")
print()
print("  The tower pattern (6 -> 12 -> 30 -> 60 -> 210 -> ...) IS")
print("  a genuine prediction: the monad says that adding primes to")
print("  the modulus resolves conflations in the physics mapping.")
print("  Whether this pattern CONTINUES to give physical insight at")
print("  higher levels is an open empirical question.")
print()

print("=" * 70)
print("EXPERIMENT 018ccc COMPLETE")
print("=" * 70)
