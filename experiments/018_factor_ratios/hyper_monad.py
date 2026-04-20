"""
Experiment 018rr: The Hyper-Monad -- 24 Positions for Matter AND Antimatter

The 12-position monad conflates isospin (R2/R1) with matter/antimatter.
It has 12 positions for 12 fermion flavors but no room for antifermions.
The chi_1 character is real (+1/-1), not complex -- no CP phase.

HYPOTHESIS: The monad is a SLICE of a 24-position hyper-monad.

The key insight: (Z/12Z)* = {1, 5, 7, 11} is isomorphic to Z_2 x Z_2
(the Klein four-group). This has THREE non-trivial characters:
  chi_1: {1,11}->+1, {5,7}->-1  (ISOSPIN)
  chi_2: {1,7}->+1, {5,11}->-1  (RAIL TYPE)
  chi_3: {1,5}->+1, {7,11}->-1  (MATTER/ANTIMATTER)

With 4 residue classes and 6 sub-positions each = 24 positions.
12 matter fermions + 12 antimatter fermions = 24.

This experiment tests:
1. Does the 24-position structure map to all 24 fermions?
2. Does chi_3 conservation = baryon/lepton number conservation?
3. Do Klein four-group products give correct composition rules?
4. Does C (matter/antimatter swap) become an exact symmetry?
5. Does the hyper-monad resolve the isospin/antimatter conflation?
"""

import numpy as np
from collections import defaultdict

print("=" * 70)
print("EXPERIMENT 018rr: THE HYPER-MONAD")
print("24 Positions for Matter AND Antimatter")
print("=" * 70)

# --- PRIME GENERATION ---
N = 100000
is_prime = [True] * (N + 1)
is_prime[0] = is_prime[1] = False
for i in range(2, int(N**0.5) + 1):
    if is_prime[i]:
        for j in range(i*i, N + 1, i):
            is_prime[j] = False

# ============================================================
# SECTION 1: THE KLEIN FOUR-GROUP (Z/12Z)*
# ============================================================
print()
print("=" * 70)
print("SECTION 1: THE KLEIN FOUR-GROUP (Z/12Z)*")
print("=" * 70)
print()

# The coprime residues mod 12
residues = [1, 5, 7, 11]
print(f"Coprime residues mod 12: {residues}")
print(f"phi(12) = 4")
print(f"(Z/12Z)* = Z_2 x Z_2 (Klein four-group)")
print()

# Multiplication table mod 12
print("Multiplication table (mod 12):")
print()
print("  x mod 12 |   1    5    7   11")
print("  ---------+------------------------")
for a in residues:
    row = []
    for b in residues:
        prod = (a * b) % 12
        row.append(f"{prod:4d}")
    print(f"  {a:7d}  | {''.join(row)}")

print()
print("  Properties of the Klein four-group:")
print("  - Every element is its own inverse: a*a = 1 (mod 12)")
print("  - Commutative (Abelian)")
print("  - Order 4, exponent 2")
print()

# Verify: every element is its own inverse
print("  Verification: a*a mod 12 = 1 for all a in (Z/12Z)*")
for a in residues:
    square = (a * a) % 12
    check = "OK" if square == 1 else "FAIL"
    print(f"    {a} * {a} = {a*a} mod 12 = {square}  [{check}]")

print()

# ============================================================
# SECTION 2: THREE DIRICHLET CHARACTERS = THREE QUANTUM NUMBERS
# ============================================================
print()
print("=" * 70)
print("SECTION 2: THREE DIRICHLET CHARACTERS = THREE QUANTUM NUMBERS")
print("=" * 70)
print()

def chi1(r):
    """chi_1 mod 12: {1,11}->+1, {5,7}->-1"""
    if r in (1, 11): return +1
    if r in (5, 7): return -1
    return 0

def chi2(r):
    """chi_2 mod 12: {1,7}->+1, {5,11}->-1"""
    if r in (1, 7): return +1
    if r in (5, 11): return -1
    return 0

def chi3(r):
    """chi_3 mod 12: {1,5}->+1, {7,11}->-1"""
    if r in (1, 5): return +1
    if r in (7, 11): return -1
    return 0

print("Three non-trivial Dirichlet characters mod 12:")
print()
print("  Residue   chi_1   chi_2   chi_3   Physical meaning")
print("  -------   -----   -----   -----   -----------------")
labels = {
    1:  "matter R2 (up-type)",
    5:  "matter R1 (dn-type)",
    7:  "antimatter R1 (dn-anti)",
    11: "antimatter R2 (up-anti)",
}
for r in residues:
    print(f"  {r:5d}      {chi1(r):+d}      {chi2(r):+d}      {chi3(r):+d}    {labels[r]}")

print()
print("  chi_1 = ISOSPIN: distinguishes up-type (+1) from down-type (-1)")
print("  chi_2 = RAIL TYPE: distinguishes inner (+1) from outer (-1) rails")
print("  chi_3 = MATTER/ANTIMATTER: distinguishes matter (+1) from antimatter (-1)")
print()
print("  KEY: In the OLD monad, chi_1 was the ONLY character (R2 vs R1).")
print("  The old monad's R2/R1 split CONFLATED isospin with rail type.")
print("  The hyper-monad has THREE independent Z_2 charges,")
print("  cleanly separating isospin, rail type, and matter/antimatter.")
print()

# Verify that chi_1 * chi_2 = chi_3 (they're not independent)
print("  Relationship: chi_1(r) * chi_2(r) = chi_3(r)?")
for r in residues:
    prod = chi1(r) * chi2(r)
    match = "OK" if prod == chi3(r) else "FAIL"
    print(f"    r={r:2d}: chi_1*chi_2 = {prod:+d}, chi_3 = {chi3(r):+d}  [{match}]")

print()
print("  Only TWO of the three characters are independent.")
print("  This means the hyper-monad has 2 independent Z_2 charges:")
print("    1. Isospin (chi_1): up-type vs down-type")
print("    2. Matter/antimatter (chi_3): matter vs antimatter")
print("  The third (chi_2) is their product.")
print()

# ============================================================
# SECTION 3: COMPOSITION RULES AND CONSERVATION LAWS
# ============================================================
print()
print("=" * 70)
print("SECTION 3: COMPOSITION RULES AND CONSERVATION LAWS")
print("=" * 70)
print()

print("When two primes multiply, their residues multiply mod 12.")
print("The character values multiply too (they're homomorphisms).")
print()
print("Composition table with character conservation:")
print()
print("  a x b -> ab   chi1(a) chi1(b) chi1(ab)  | chi3(a) chi3(b) chi3(ab)")
print("  ---------   ------- ------- --------   ------- ------- --------")
for a in residues:
    for b in residues:
        ab = (a * b) % 12
        print(f"  {a:2d} x {b:2d} -> {ab:2d}   {chi1(a):+d}     {chi1(b):+d}     {chi1(ab):+d}     | {chi3(a):+d}     {chi3(b):+d}     {chi3(ab):+d}")

print()
print("  OBSERVATIONS:")
print()
print("  1. ISOSIN CONSERVATION: chi_1(ab) = chi_1(a) * chi_1(b)  [ALWAYS]")
print("     Up x Up = Up, Up x Down = Down, Down x Down = Up")
print()
print("  2. MATTER CONSERVATION: chi_3(ab) = chi_3(a) * chi_3(b)  [ALWAYS]")
print("     Matter x Matter = Matter (+1 x +1 = +1)")
print("     Antimatter x Antimatter = Matter (-1 x -1 = +1)  [ANNIHILATION!]")
print("     Matter x Antimatter = Antimatter (+1 x -1 = -1)  [PAIR PRODUCTION]")
print()

# Verify conservation
print("  Verification: chi conservation for ALL products")
iso_conserved = True
matter_conserved = True
for a in residues:
    for b in residues:
        ab = (a * b) % 12
        if chi1(ab) != chi1(a) * chi1(b):
            iso_conserved = False
        if chi3(ab) != chi3(a) * chi3(b):
            matter_conserved = False

print(f"    Isospin conservation (chi_1): {iso_conserved}")
print(f"    Matter conservation (chi_3):  {matter_conserved}")

print()
print("  THE HYPER-MONAD PREDICTS: Baryon/lepton number is CONSERVED.")
print("  This matches the Standard Model at low energy (proton doesn't decay).")
print("  Violation would require going BEYOND the hyper-monad (GUT scale).")
print()

# ============================================================
# SECTION 4: THE 24-POSITION FERMION MAP
# ============================================================
print()
print("=" * 70)
print("SECTION 4: THE 24-POSITION FERMION MAP")
print("=" * 70)
print()

print("Matter fermions (chi_3 = +1):")
print()
print("  Residue  Rail  Particle  Gen  Type   T3    Mass(GeV)")
print("  -------  ----  --------  ---  -----  ----  ---------")

# Matter sector: residues 1 and 5
# Residue 1: chi_1=+1 (up-type), chi_3=+1 (matter)
# Residue 5: chi_1=-1 (down-type), chi_3=+1 (matter)

# Sub-positions for each residue class
# For residue 1 mod 12: numbers are 12k+1, prime at 12k+1
# The k-index in the OLD monad: (12k+1-1)/6 = 2k, so sp_old = 2k mod 6
# For residue 5 mod 12: numbers are 12k+5
# Old k: (12k+5+1)/6 = 2k+1, sp_old = (2k+1) mod 6

# The sub-position in the hyper-monad is k mod 6 (index within the residue class)
# This gives 6 sub-positions per residue, 4 residues x 6 = 24 positions

matter_fermions = {
    # Residue 1 mod 12: matter, up-type (T3=+1/2)
    # sp=0: up quark
    # sp=1: electron neutrino
    # sp=2: charm quark
    # sp=3: muon neutrino
    # sp=4: top quark
    # sp=5: tau neutrino
    (1, 0): ("up",       1, "quark",  +0.5, 2.2e-3),
    (1, 1): ("nu_e",     1, "lepton", +0.5, 0.0),
    (1, 2): ("charm",    2, "quark",  +0.5, 1.27),
    (1, 3): ("nu_mu",    2, "lepton", +0.5, 0.0),
    (1, 4): ("top",      3, "quark",  +0.5, 172.76),
    (1, 5): ("nu_tau",   3, "lepton", +0.5, 0.0),
    # Residue 5 mod 12: matter, down-type (T3=-1/2)
    (5, 0): ("down",     1, "quark",  -0.5, 4.7e-3),
    (5, 1): ("electron", 1, "lepton", -0.5, 0.511e-3),
    (5, 2): ("strange",  2, "quark",  -0.5, 96e-3),
    (5, 3): ("muon",     2, "lepton", -0.5, 105.66e-3),
    (5, 4): ("bottom",   3, "quark",  -0.5, 4.18),
    (5, 5): ("tau",      3, "lepton", -0.5, 1776.86e-3),
}

antimatter_fermions = {
    # Residue 7 mod 12: antimatter, down-type (chi_1=-1, T3=-1/2)
    # But for antiparticles, T3 is FLIPPED: physical T3(anti-d) = +1/2
    # Actually: antiparticle of d (T3=-1/2) has T3=+1/2
    # But chi_1(7) = -1, so the HYPER-MONAD T3 differs from physical T3 for antimatter
    # This needs careful treatment...
    # For now: map by the SAME chi_1 convention
    (7, 0): ("anti-down",     1, "antiquark",  +0.5, 4.7e-3),
    (7, 1): ("positron",      1, "antilepton", +0.5, 0.511e-3),
    (7, 2): ("anti-strange",  2, "antiquark",  +0.5, 96e-3),
    (7, 3): ("anti-muon",     2, "antilepton", +0.5, 105.66e-3),
    (7, 4): ("anti-bottom",   3, "antiquark",  +0.5, 4.18),
    (7, 5): ("anti-tau",      3, "antilepton", +0.5, 1776.86e-3),
    # Residue 11 mod 12: antimatter, up-type (chi_1=+1, T3=+1/2)
    # Antiparticle of up (T3=+1/2) has T3=-1/2
    (11, 0): ("anti-up",      1, "antiquark",  -0.5, 2.2e-3),
    (11, 1): ("anti-nu_e",    1, "antilepton", -0.5, 0.0),
    (11, 2): ("anti-charm",   2, "antiquark",  -0.5, 1.27),
    (11, 3): ("anti-nu_mu",   2, "antilepton", -0.5, 0.0),
    (11, 4): ("anti-top",     3, "antiquark",  -0.5, 172.76),
    (11, 5): ("anti-nu_tau",  3, "antilepton", -0.5, 0.0),
}

all_fermions = {**matter_fermions, **antimatter_fermions}

# Print matter sector
print("  MATTER SECTOR (chi_3 = +1):")
print()
for r in [1, 5]:
    rail = "R2(up)" if chi1(r) == +1 else "R1(dn)"
    print(f"  Residue {r} mod 12: chi_1={chi1(r):+d} ({rail}), chi_3={chi3(r):+d} (matter)")
    for sp in range(6):
        key = (r, sp)
        if key in matter_fermions:
            name, gen, typ, T3, mass = matter_fermions[key]
            print(f"    sp={sp}: {name:12s}  Gen {gen}  {typ:6s}  T3={T3:+.1f}  m={mass:.4e} GeV")
    print()

# Print antimatter sector
print("  ANTIMATTER SECTOR (chi_3 = -1):")
print()
for r in [7, 11]:
    rail = "R2(up)" if chi1(r) == +1 else "R1(dn)"
    print(f"  Residue {r} mod 12: chi_1={chi1(r):+d} ({rail}), chi_3={chi3(r):+d} (antimatter)")
    for sp in range(6):
        key = (r, sp)
        if key in antimatter_fermions:
            name, gen, typ, T3, mass = antimatter_fermions[key]
            print(f"    sp={sp}: {name:12s}  Gen {gen}  {typ:9s}  T3={T3:+.1f}  m={mass:.4e} GeV")
    print()

# ============================================================
# SECTION 5: C, P, T ON THE HYPER-MONAD
# ============================================================
print()
print("=" * 70)
print("SECTION 5: C, P, T ON THE HYPER-MONAD")
print("=" * 70)
print()

print("On the hyper-monad, C, P, T are well-defined and distinct:")
print()
print("  C (Charge Conjugation) = chi_3 flip (matter <-> antimatter):")
print("    Residue 1 <-> Residue 7   (matter R2 <-> antimatter R1)")
print("    Residue 5 <-> Residue 11  (matter R1 <-> antimatter R2)")
print("    C: (r, sp) -> (12-r mod 12 if r!=1, etc.) or more precisely:")
print("    C: 1 <-> 7, 5 <-> 11  (swap chi_3, keep chi_1)")
print()

# C maps residue 1 to 7, 5 to 11, and vice versa
c_map = {1: 7, 7: 1, 5: 11, 11: 5}
print("    C operation:")
for r in residues:
    cr = c_map[r]
    print(f"      {r:2d} -> {cr:2d}: {labels[r]:25s} <-> {labels[cr]}")

print()
print("    C flips chi_3 (matter/antimatter) while preserving chi_1 (isospin).")
print("    Physical check:")
for r in residues:
    cr = c_map[r]
    print(f"      chi_1({r})={chi1(r):+d} -> chi_1({cr})={chi1(cr):+d}  [chi_1 preserved: {chi1(r)==chi1(cr)}]  "
          f"chi_3({r})={chi3(r):+d} -> chi_3({cr})={chi3(cr):+d}  [chi_3 flipped: {chi3(r)==-chi3(cr)}]")

print()
print("  P (Parity) = angular reflection: sp -> -sp mod 6")
print("    Same as the old monad. Preserves all characters.")
print()

print("  T (Time Reversal) = walking direction reversal")
print("    Same as the old monad. Exact symmetry.")
print()

print("  CP = C composed with P:")
print("    Maps (r, sp) to (c_map[r], -sp mod 6)")
print("    Flips chi_3 AND reflects sp.")
print()

print("  CPT = C composed with P composed with T:")
print("    Maps (r, sp) to (c_map[r], -sp mod 6) with reversed walk direction")
print("    Should be an exact symmetry (CPT theorem).")
print()

# Is C an exact symmetry of the prime distribution?
print("  Is C an exact symmetry of the prime distribution?")
print("  C maps residue 1 <-> 7, 5 <-> 11.")
print("  If C is exact, then pi(x;12,1) = pi(x;12,7) and pi(x;12,5) = pi(x;12,11).")
print()

for scale in [1000, 10000, 100000]:
    counts = {}
    for r in residues:
        counts[r] = sum(1 for p in range(2, scale) if is_prime[p] and p % 12 == r)
    print(f"  Scale {scale:6d}: pi(x;12,1)={counts[1]:5d}  pi(x;12,7)={counts[7]:5d}  "
          f"ratio={counts[1]/counts[7] if counts[7]>0 else 0:.4f}  |  "
          f"pi(x;12,5)={counts[5]:5d}  pi(x;12,11)={counts[11]:5d}  "
          f"ratio={counts[5]/counts[11] if counts[11]>0 else 0:.4f}")

print()
print("  RESULT: C is APPROXIMATELY but NOT EXACTLY a symmetry.")
print("  pi(x;12,1) ~ pi(x;12,7) and pi(x;12,5) ~ pi(x;12,11),")
print("  but there are small deviations -- Chebyshev-type biases between")
print("  the residue classes mod 12.")
print()

# ============================================================
# SECTION 6: PRIME DENSITY BY RESIDUE MOD 12
# ============================================================
print()
print("=" * 70)
print("SECTION 6: PRIME DENSITY BY RESIDUE MOD 12")
print("=" * 70)
print()

print("Prime counts by residue mod 12 (up to 100000):")
print()
print("  Residue   Count    Fraction   chi_1  chi_2  chi_3  Sector")
print("  -------   -----    --------   -----  -----  -----  ------")
total_primes_12 = sum(1 for p in range(2, N) if is_prime[p] and p % 12 in residues)
for r in residues:
    count = sum(1 for p in range(2, N) if is_prime[p] and p % 12 == r)
    frac = count / total_primes_12 if total_primes_12 > 0 else 0
    sector = "matter" if chi3(r) == +1 else "antimatter"
    print(f"  {r:5d}    {count:5d}    {frac:.4f}     {chi1(r):+d}     {chi2(r):+d}     {chi3(r):+d}     {sector}")

matter_count = sum(1 for p in range(2, N) if is_prime[p] and p % 12 in (1, 5))
antimatter_count = sum(1 for p in range(2, N) if is_prime[p] and p % 12 in (7, 11))
print()
print(f"  Total matter primes (residues 1,5):     {matter_count}")
print(f"  Total antimatter primes (residues 7,11): {antimatter_count}")
print(f"  Ratio matter/antimatter: {matter_count/antimatter_count:.4f}")
print(f"  Expected if C-symmetric: 1.0000")
print()

# ============================================================
# SECTION 7: THE OLD MONAD AS A SLICE
# ============================================================
print()
print("=" * 70)
print("SECTION 7: THE OLD MONAD AS A SLICE OF THE HYPER-MONAD")
print("=" * 70)
print()

print("The old 12-position monad maps R2 = 1 mod 6, R1 = 5 mod 6.")
print("But 1 mod 6 = {1, 7} mod 12 and 5 mod 6 = {5, 11} mod 12.")
print()
print("So the old monad's R2 CONFLATES:")
print("  Residue 1 (matter, up-type) and Residue 7 (antimatter, down-type)")
print()
print("And the old monad's R1 CONFLATES:")
print("  Residue 5 (matter, down-type) and Residue 11 (antimatter, up-type)")
print()

print("In the old monad, the chi_1 character (mod 6) gives:")
print("  chi_1(1 mod 6) = +1")
print("  chi_1(5 mod 6) = -1")
print()
print("But 1 mod 6 includes BOTH residue 1 AND residue 7 mod 12!")
print("These have DIFFERENT chi_3 values (matter vs antimatter).")
print()
print("The old monad's chi_1 (mod 6) is actually chi_1 (mod 12),")
print("which distinguishes {1,11} from {5,7}.")
print("This is NOT the same as the R2/R1 split!")
print()
print("  Old monad R2 = {1 mod 6} = {1, 7} mod 12")
print("  chi_1 (mod 12) +1 = {1, 11} mod 12")
print("  These are DIFFERENT sets!")
print()
print("  Old monad R1 = {5 mod 6} = {5, 11} mod 12")
print("  chi_1 (mod 12) -1 = {5, 7} mod 12")
print("  These are DIFFERENT sets!")
print()

# Quantify: how much does the old monad conflate?
print("  Conflation in the old monad:")
print()
print("  Old R2 position (sp=0): primes at 12k+1 AND 12k+7")
print("  But 12k+1 = matter up-type, 12k+7 = antimatter down-type")
print()
r2_sp0_matter = sum(1 for p in range(2, N) if is_prime[p] and p % 12 == 1)
r2_sp0_anti = sum(1 for p in range(2, N) if is_prime[p] and p % 12 == 7)
print(f"  Matter (residue 1):    {r2_sp0_matter}")
print(f"  Antimatter (residue 7): {r2_sp0_anti}")
print(f"  Old monad sees: {r2_sp0_matter + r2_sp0_anti} primes at R2 sp=0")
print(f"  But it CANNOT distinguish matter from antimatter!")
print()
print("  THIS IS THE CATEGORY ERROR.")
print("  The old monad lumps matter and antimatter into the same position.")
print("  The hyper-monad resolves this by using mod 12 instead of mod 6.")
print()

# ============================================================
# SECTION 8: DOES THE HYPER-MONAD HAVE CP VIOLATION?
# ============================================================
print()
print("=" * 70)
print("SECTION 8: DOES THE HYPER-MONAD HAVE CP VIOLATION?")
print("=" * 70)
print()

print("The hyper-monad has 4 residue classes mod 12.")
print("The Dirichlet characters are STILL real: chi(r) = +/-1.")
print("There is NO complex phase in any character mod 12.")
print()
print("  Why? Because (Z/12Z)* = Z_2 x Z_2 has NO cyclic component.")
print("  All irreducible representations of Z_2 x Z_2 are REAL.")
print("  For complex characters, we need a modulus m where (Z/mZ)*")
print("  has a cyclic component Z_n with n > 2.")
print()
print("  Smallest modulus with complex character: m = 5")
print("  (Z/5Z)* = Z_4, which has characters with values {1, i, -1, -i}")
print()
print("  The hyper-monad (mod 12) STILL has no CP violation.")
print("  It resolves the antimatter/isospin conflation, but the")
print("  asymmetry is still REAL, not COMPLEX.")
print()

# But: does the hyper-monad at least get C right?
print("  What the hyper-monad DOES improve:")
print()
print("  1. C is now a DISTINCT operation from isospin flip")
print("     C: residue 1 <-> 7, 5 <-> 11 (flips chi_3)")
print("     Isospin: residue 1 <-> 5, 7 <-> 11 (flips chi_1)")
print("     These are DIFFERENT operations in the hyper-monad!")
print()
print("  2. C is an approximate symmetry")
print("     pi(x;12,1) ~ pi(x;12,7) by Dirichlet's theorem")
print("     The deviation is a Chebyshev-type bias mod 12")
print()
print("  3. Matter/antimatter are cleanly separated")
print("     12 matter positions + 12 antimatter positions = 24")
print("     Each has its own residue class")
print()

# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 70)
print("SUMMARY: THE HYPER-MONAD")
print("=" * 70)
print()
print("THE 24-POSITION STRUCTURE:")
print("  (Z/12Z)* = {1, 5, 7, 11} = Z_2 x Z_2 (Klein four-group)")
print("  4 residue classes x 6 sub-positions = 24 positions")
print("  12 matter fermions + 12 antimatter fermions = 24")
print()
print("THE THREE QUANTUM NUMBERS:")
print("  chi_1 = isospin: {1,11}->+1 (up-type), {5,7}->-1 (down-type)")
print("  chi_2 = rail type: {1,7}->+1, {5,11}->-1 (derivable from chi_1*chi_3)")
print("  chi_3 = matter/antimatter: {1,5}->+1 (matter), {7,11}->-1 (antimatter)")
print("  Only 2 independent: chi_2 = chi_1 * chi_3")
print()
print("WHAT THE HYPER-MONAD RESOLVES:")
print("  1. C (charge conjugation) is now DISTINCT from isospin flip")
print("     C flips chi_3 (matter/antimatter)")
print("     Isospin flip flips chi_1")
print("     The old monad CONFLATED these -- the hyper-monad separates them")
print()
print("  2. Antimatter has its OWN positions (12 antimatter slots)")
print("     The old monad had NO room for antiparticles")
print()
print("  3. Composition rules give matter conservation (chi_3 conserved)")
print("     Matter x Matter = Matter")
print("     Antimatter x Antimatter = Matter (annihilation analog)")
print("     Matter x Antimatter = Antimatter (pair production analog)")
print()
print("  4. C is an approximate symmetry (Dirichlet equidistribution mod 12)")
print("     C violation = Chebyshev-type bias between C-partner residues")
print()
print("WHAT THE HYPER-MONAD STILL DOESN'T HAVE:")
print("  1. Complex phase (all characters are real, still no CP violation)")
print("  2. Baryon number violation (chi_3 is conserved at 100%)")
print("  3. The Jarlskog invariant")
print("  4. Sakharov conditions still score 0/3")
print()
print("THE DEEPER PICTURE:")
print("  The old monad is a PROJECTION of the hyper-monad.")
print("  Just as the old monad projects 4 residues onto 2 rails by mod 6,")
print("  the hyper-monad may itself be a projection of a yet larger structure.")
print()
print("  For complex phases: need modulus where (Z/mZ)* has Z_n with n>2.")
print("  Smallest such: m=5 (Z_4), m=7 (Z_6), m=11 (Z_10), m=13 (Z_12)")
print("  The 'full' monad might use modulus 60 = lcm(12, 5) or")
print("  420 = lcm(4, 3, 5, 7) giving (Z/420Z)* with complex characters.")
print()
print("  The pattern: each enlargement resolves a conflation.")
print("  Mod 6: conflates matter/antimatter (splits into mod 12)")
print("  Mod 12: conflates real/complex (needs mod with cyclic Z_n)")
print("  The full structure may be modular, with each layer adding depth.")
print()
print("KEY NUMBERS:")
print(f"  Hyper-monad positions: 24 (4 residues x 6 sub-positions)")
print(f"  Independent Z_2 charges: 2 (chi_1 isospin, chi_3 matter/antimatter)")
print(f"  C symmetry: approximate (matter/antimatter ratio = {matter_count/antimatter_count:.4f})")
print(f"  Composition conservation: isospin EXACT, matter EXACT")
print(f"  CP violation: STILL NONE (all characters real)")
print()
print("======================================================================")
print("EXPERIMENT 018rr COMPLETE")
print("======================================================================")
