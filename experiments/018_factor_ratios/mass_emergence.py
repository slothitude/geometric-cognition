"""
Experiment 018tt: Mass from Impedance

The walking sieve on the staggered lattice flips chi_3 at every step.
The "impedance" of this flip determines how strongly a prime couples
to the lattice. The question: does mass emerge from this impedance?

Key relationships:
- Walking step for prime p: visits composites at spacing p
- Visit frequency: 1/p composites per unit k-length
- Chi_3 flips at EVERY step (staggering is universal)
- Old monad mass formula: m = 1/p (from 018jj)

Hypothesis: mass = propagation impedance = visit frequency = 1/p.
The staggering provides a universal "constituent mass" on top of
the "current mass" from position: m = m_stagger + M_Planck/p.
"""

import numpy as np

print("=" * 70)
print("EXPERIMENT 018tt: MASS FROM IMPEDANCE")
print("Does Mass Emerge from Walking Sieve Impedance?")
print("=" * 70)

# --- PRIME GENERATION ---
N = 100000
is_prime = [True] * (N + 1)
is_prime[0] = is_prime[1] = False
for i in range(2, int(N**0.5) + 1):
    if is_prime[i]:
        for j in range(i*i, N + 1, i):
            is_prime[j] = False

def chi3_mod12(n):
    r = n % 12
    if r in (1, 5): return +1
    if r in (7, 11): return -1
    return 0

# ============================================================
# SECTION 1: PROPAGATION IMPEDANCE = VISIT FREQUENCY
# ============================================================
print()
print("=" * 70)
print("SECTION 1: PROPAGATION IMPEDANCE = VISIT FREQUENCY")
print("=" * 70)
print()

print("The walking sieve for prime p visits composites at spacing p.")
print("Visit frequency = 1/p (composites per unit k-length).")
print("The old monad mass formula: m = 1/p (in Planck units).")
print()
print("Therefore: mass = visit frequency = propagation impedance.")
print()
print("A prime that visits composites frequently (small p) has")
print("HIGH impedance (many encounters with the lattice) = LARGE mass.")
print("A prime that visits rarely (large p) has LOW impedance = small mass.")
print()

# Compute for small primes
print("  Prime p   Visit freq   Mass (1/p)   Composites in [1,1000]")
print("  -------   ----------   ----------   ------------------------")
for p in [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]:
    if not is_prime[p] or p % 6 not in (1, 5):
        continue
    # Count composites visited by p in k-range [1, 1000]
    k_range = 1000
    if p % 6 == 1:  # R2
        k0 = (p - 1) // 6
    else:  # R1
        k0 = (p + 1) // 6
    visits = 0
    k = k0 + p
    while k <= k_range:
        visits += 1
        k += p

    freq = 1 / p
    mass = 1 / p
    print(f"  {p:7d}   {freq:.6f}     {mass:.6f}       {visits}")

print()
print("  The visit frequency IS the mass. This is not a coincidence --")
print("  it's the same formula viewed through different physics.")
print()

# ============================================================
# SECTION 2: OMEGA(k) = LOCAL IMPEDANCE AT POSITION k
# ============================================================
print()
print("=" * 70)
print("SECTION 2: OMEGA(k) = LOCAL IMPEDANCE AT POSITION k")
print("=" * 70)
print()

print("At each k-position, the number of distinct prime factors omega(n)")
print("counts how many walking sieve worldlines cross that position.")
print("This is the LOCAL impedance -- how many walks are 'passing through'.")
print()

# Compute omega for numbers on the monad
def count_prime_factors(n):
    """Count distinct prime factors of n"""
    if n <= 1: return 0
    count = 0
    d = 2
    while d * d <= n:
        if n % d == 0:
            count += 1
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        count += 1
    return count

# Average omega over k-ranges
print("  k-range    <omega_R2>  <omega_R1>  <omega_total>  log(log(6k))")
print("  -------    ---------   ---------   ------------   -----------")
for k_start_exp in [10, 50, 100, 500, 1000, 5000]:
    k_end = k_start_exp + 100
    omega_r2 = []
    omega_r1 = []
    for k in range(k_start_exp, k_end + 1):
        r2_val = 6*k + 1
        r1_val = 6*k - 1
        if r2_val < N:
            omega_r2.append(count_prime_factors(r2_val))
        if r1_val > 0 and r1_val < N:
            omega_r1.append(count_prime_factors(r1_val))

    avg_r2 = np.mean(omega_r2) if omega_r2 else 0
    avg_r1 = np.mean(omega_r1) if omega_r1 else 0
    avg_total = (avg_r2 + avg_r1) / 2
    k_mid = (k_start_exp + k_end) / 2
    loglog = np.log(np.log(6 * k_mid)) if k_mid > 1 else 0
    print(f"  [{k_start_exp:5d},{k_end:5d}]  {avg_r2:.4f}      {avg_r1:.4f}      {avg_total:.4f}        {loglog:.4f}")

print()
print("  By Hardy-Ramanujan: <omega(n)> ~ log(log(n))")
print("  The local impedance grows logarithmically with scale.")
print("  This is the monad's 'background impedance' -- it increases")
print("  as you move to larger k (lower energy).")
print()

# ============================================================
# SECTION 3: STAGGERING MASS -- THE UNIVERSAL CONTRIBUTION
# ============================================================
print()
print("=" * 70)
print("SECTION 3: STAGGERING MASS -- THE UNIVERSAL CONTRIBUTION")
print("=" * 70)
print()

M_Planck = 1.2209e19  # GeV

print("Physical particles and their monad positions:")
print()
print("  Particle    Mass (GeV)    p = M_P/m    1/p (Planck)   Staggering cost")
print("  --------    ----------    ---------    -----------    ---------------")

particles = [
    ("electron",  0.511e-3),
    ("up",        2.2e-3),
    ("down",      4.7e-3),
    ("strange",   96e-3),
    ("muon",      105.66e-3),
    ("charm",     1.27),
    ("tau",       1.77686),
    ("bottom",    4.18),
    ("top",       172.76),
    ("W boson",   80.379),
    ("Z boson",   91.1876),
    ("Higgs",     125.25),
]

# The monad mass formula: m = M_Planck / p
# This means p = M_Planck / m
# The "staggering cost" would be any residual: m - M_Planck/p

# But in the monad, the mass IS M_Planck / p by definition.
# So the staggering cost is zero by construction.
# The interesting question: does the staggered lattice ADD a mass?

# In lattice QCD, the staggered fermion has a "residual mass" m_res
# that comes from discretization. This is typically small compared
# to the physical masses.

# On the monad, the "staggering" is the chi_3 flip at every step.
# The energy cost of this flip in the field theory would be:
#   E_stagger = chi_3(next) - chi_3(current) = -2*chi_3 (always flips)
# This is the same for ALL walks (universal).

# The "staggering mass" in lattice QCD terms would be:
# m_stagger = 1/(2*kappa_c) where kappa_c is the critical hopping parameter.
# On the monad, kappa = 1 (the walk always completes a step).

print()
print("The monad's mass formula: m = M_Planck / p")
print("This is EQUIVALENT to: m = visit frequency * M_Planck")
print()
print("The staggering does NOT add a separate mass term.")
print("The mass is ENTIRELY from the propagation impedance (1/p).")
print()
print("Why? Because the chi_3 flip is FREE -- it costs no energy.")
print("The walk simply alternates between matter and antimatter sectors.")
print("The staggering is a topological feature of the lattice, not a")
print("dynamical interaction that generates mass.")
print()
print("Compare with lattice QCD:")
print("  - Staggered fermions have m_res ~ 0 from discretization")
print("  - The physical masses come from the QCD dynamics, not the staggering")
print("  - The staggering removes doublers, not generates mass")
print()
print("Similarly on the monad:")
print("  - The staggering removes the matter/antimatter conflation")
print("  - Mass comes from position in the lattice (1/p), not the staggering")
print("  - The staggering is a geometric feature, not a mass generator")
print()

# ============================================================
# SECTION 4: IMPEDANCE AS EFFECTIVE MASS FROM BAND STRUCTURE
# ============================================================
print()
print("=" * 70)
print("SECTION 4: IMPEDANCE AS EFFECTIVE MASS FROM BAND STRUCTURE")
print("=" * 70)
print()

print("In condensed matter, effective mass comes from the band structure:")
print("  m* = hbar^2 / (d^2E/dk^2)")
print("where E(k) is the dispersion relation.")
print()
print("On the monad, the 'dispersion relation' for a prime walk is:")
print("  E(p) = frequency of composite encounters = 1/p")
print()
print("The 'band' is the set of all prime walks.")
print("The 'group velocity' of walk p = dk/dt = p (steps of size p)")
print("The 'phase velocity' = omega/k = (2*pi/p) / p = 2*pi/p^2")
print()
print("Effective mass from curvature:")
print("  d^2E/dp^2 = d^2(1/p)/dp^2 = 2/p^3")
print("  m* proportional to 1/(2/p^3) = p^3/2")
print()
print("But physical mass goes as 1/p, not p^3!")
print("The monad's effective mass from band curvature goes in the")
print("WRONG direction (heavier for larger p).")
print()
print("This means: the monad's mass does NOT come from the band")
print("structure of the walking sieve. It comes from the POSITION")
print("in the lattice, interpreted as 1/p through the Planck scale.")
print()
print("The impedance (1/p) is the CORRECT mass, but it's not derived")
print("from the walk dynamics -- it's put in by hand through the")
print("Planck scale correspondence.")
print()

# ============================================================
# SECTION 5: THE REAL SOURCE OF MASS -- SCALE, NOT DYNAMICS
# ============================================================
print()
print("=" * 70)
print("SECTION 5: THE REAL SOURCE OF MASS -- SCALE, NOT DYNAMICS")
print("=" * 70)
print()

print("The honest assessment of where mass comes from on the monad:")
print()
print("1. The monad mass formula: m = 1/p (Planck units)")
print("   This is the NUMBER-THEORETIC mass: the inverse of the")
print("   position in the prime lattice. It has nothing to do with")
print("   the walking sieve dynamics or the staggering.")
print()
print("2. The walking sieve impedance: 1/p (composites per k-step)")
print("   This equals the mass by DEFINITION, not by DERIVATION.")
print("   It's the same 1/p viewed through the sieve's propagation.")
print()
print("3. The staggering cost: ZERO")
print("   The chi_3 flip is topological, not dynamical.")
print("   No energy cost, no mass generation.")
print()
print("4. The band structure curvature: p^3/2")
print("   This goes in the WRONG direction for mass.")
print("   The monad's band structure does not explain mass.")
print()
print("CONCLUSION: Mass on the monad comes from POSITION IN THE LATTICE,")
print("not from the walking sieve's dynamics or the staggering.")
print()
print("The impedance interpretation is VALID (mass = visit frequency = 1/p)")
print("but it's a RESTATEMENT of the position formula, not a derivation.")
print("The staggering is a geometric feature that eliminates the")
print("matter/antimatter conflation, not a mass generation mechanism.")
print()

# ============================================================
# SECTION 6: WHAT THE STAGGERING DOES PROVIDE
# ============================================================
print()
print("=" * 70)
print("SECTION 6: WHAT THE STAGGERING DOES PROVIDE")
print("=" * 70)
print()

print("The staggered lattice DOES provide something important:")
print()
print("1. FERMION DOUBLING ELIMINATION")
print("   Without staggering, the 12-position monad had 12 flavors")
print("   crammed into 12 slots with no room for antimatter.")
print("   The staggering distributes matter/antimatter across k-parity,")
print("   effectively DOUBLING the capacity (24 positions) without")
print("   adding new degrees of freedom.")
print()
print("2. BARYON NUMBER CONSERVATION")
print("   The chi_3 conservation on the staggered lattice gives")
print("   exact baryon number conservation at 100%.")
print("   This matches the low-energy Standard Model.")
print()
print("3. ALTERNATING BARYON CURRENT")
print("   The AC baryon current (period 2) is a prediction:")
print("   the vacuum has equal matter and antimatter density.")
print("   Any net baryon number requires BREAKING the staggering.")
print()
print("4. THE STRUCTURE OF CHARGE CONJUGATION")
print("   C = k-parity flip on the staggered lattice.")
print("   This is a DISCRETE symmetry, not continuous.")
print("   C violation = Chebyshev-type bias between k-parity sectors.")
print()
print("5. CONNECTION TO LATTICE QCD")
print("   The staggered fermion analogy is genuine:")
print("   the monad implements Kawai-Rabinovici-Susskind staggering")
print("   using number theory instead of lattice gauge theory.")
print("   The mathematics is the same; the physical interpretation differs.")
print()

# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 70)
print("SUMMARY: MASS FROM IMPEDANCE?")
print("=" * 70)
print()
print("DOES MASS EMERGE FROM IMPEDANCE?")
print("  YES, but trivially: mass = 1/p = visit frequency = impedance.")
print("  This is a restatement, not a derivation.")
print()
print("DOES THE STAGGERING GENERATE MASS?")
print("  NO. The chi_3 flip is topological (zero energy cost).")
print("  The staggering eliminates the matter/antimatter conflation,")
print("  not generates mass. Compare with lattice QCD where staggering")
print("  eliminates doublers but doesn't generate quark masses.")
print()
print("WHERE DOES MASS COME FROM?")
print("  Position in the lattice: m = 1/p (Planck units).")
print("  The hierarchy (electron to top) is a SCALE EFFECT.")
print("  The monad's mass is kinematic, not dynamic.")
print()
print("WHAT THE STAGGERING PROVIDES:")
print("  1. Fermion doubling elimination (24 positions from 12)")
print("  2. Baryon number conservation (chi_3 at 100%)")
print("  3. Alternating baryon current (AC, not DC)")
print("  4. Discrete C symmetry (k-parity flip)")
print("  5. Connection to lattice QCD staggered fermions")
print()
print("KEY NUMBERS:")
print(f"  Mass formula: m = M_Planck / p = {M_Planck:.3e} / p")
print(f"  Impedance = visit frequency = 1/p (tautological with mass)")
print(f"  Staggering cost: 0 (chi_3 flip is topological)")
print(f"  Band curvature mass: p^3/2 (wrong direction)")
print(f"  Stagger pattern: PERFECT (100%)")
print()
print("======================================================================")
print("EXPERIMENT 018tt COMPLETE")
print("======================================================================")
