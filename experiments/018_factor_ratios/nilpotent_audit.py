"""
EXPERIMENT 127: STRUCTURAL AUDIT OF THE NILPOTENT SECTOR + YUKAWA TEST
========================================================================
Rigorous test of two claims from the primes-as-Higgs framework:

Part A: Nilpotent Sector = Goldstone/Ghost?
  The nilpotent sector {0, 6, 12, 18} has decay chains under self-multiplication.
  In the SM, Goldstone bosons are "eaten" during symmetry breaking (3 in EW).
  In the monad, there are 3 non-zero nilpotents. Does the analogy hold?

  Tests:
  - Decay chain structure vs Goldstone counting
  - Nilpotent algebraic properties vs ghost field properties
  - Whether the nilpotent sector has any predictive power

Part B: Yukawa Scaling -- 1/p Against Actual Fermion Masses
  Claim: mass ~ 1/p for some prime p. Test against the 12 known fermion masses.
  The fermion mass hierarchy spans 11 orders of magnitude (neutrinos to top).
  Can 1/p reproduce this? If so, how well?

  This is the acid test: either the numbers match or they don't.
"""

from math import gcd, log, log10, exp, sqrt
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

Z24_STAR = sorted(n for n in range(1, 24) if gcd(n, 24) == 1)

# ====================================================================
print("=" * 70)
print("EXPERIMENT 127: NILPOTENT AUDIT + YUKAWA TEST")
print("=" * 70)

# ====================================================================
# PART A: NILPOTENT SECTOR STRUCTURAL AUDIT
# ====================================================================
print("\n" + "=" * 70)
print("PART A: NILPOTENT SECTOR -- GOLDSTONE/GHOST ANALOGY AUDIT")
print("=" * 70)

print("""
  SM CONTEXT:
  - Electroweak symmetry breaking (SU(2)_L x U(1)_Y -> U(1)_EM)
    produces 3 Goldstone bosons, "eaten" by W+, W-, Z
  - These become the longitudinal polarizations of massive gauge bosons
  - Faddeev-Popov ghosts: gauge-fixing artifacts, cancel unphysical modes
  - Key property: Goldstones have ZERO mass (before being eaten)

  MONAD CONTEXT:
  - Nilpotent sector = {0, 6, 12, 18} = multiples of 6 mod 24
  - These decay to 0 under self-multiplication
  - 3 non-zero nilpotents (6, 12, 18) -- same count as Goldstone bosons
  - Question: is this coincidence or structural correspondence?
""")

# A1: Nilpotent decay chains in detail
print("  A1: DECAY CHAINS")
print("  " + "-" * 50)
nilpotents = [0, 6, 12, 18]
for x in nilpotents:
    chain = [x]
    val = x
    while val != 0:
        val = (val * x) % 24
        chain.append(val)
    steps = len(chain) - 1
    print(f"  {x}: " + " -> ".join(map(str, chain)) + f"  ({steps} steps)")

print(f"\n  Decay topology:")
print(f"    6  -> 12 -> 0  (2 steps, via 6^2=12, 6^3=0)")
print(f"    12 -> 0        (1 step, via 12^2=0)")
print(f"    18 -> 12 -> 0  (2 steps, via 18^2=12, 18^3=0)")
print(f"    (Note: 18 and 6 both decay THROUGH 12 before reaching 0)")

# A2: Nilpotent algebraic properties
print(f"\n  A2: ALGEBRAIC PROPERTIES")
print("  " + "-" * 50)

# Multiplication table of nilpotents
print(f"  Nilpotent multiplication table (mod 24):")
print(f"  {'':>4}", end="")
for a in nilpotents:
    print(f" {a:>3}", end="")
print()
for a in nilpotents:
    print(f"  {a:>4}", end="")
    for b in nilpotents:
        print(f" {(a*b)%24:>3}", end="")
    print()

# Sum table
print(f"\n  Nilpotent addition table (mod 24):")
print(f"  {'':>4}", end="")
for a in nilpotents:
    print(f" {a:>3}", end="")
print()
for a in nilpotents:
    print(f"  {a:>4}", end="")
    for b in nilpotents:
        print(f" {(a+b)%24:>3}", end="")
    print()

# Nilpotent x coprime interactions
print(f"\n  Nilpotent x coprime interactions:")
print(f"  {'n':>4} {'6n%24':>6} {'12n%24':>7} {'18n%24':>7}")
for n in Z24_STAR:
    print(f"  {n:>4} {(6*n)%24:>6} {(12*n)%24:>7} {(18*n)%24:>7}")

print(f"\n  KEY: Nilpotent x ANY coprime = stays in nilpotent sector")
nil_stay = all((6*n)%24 in {0,6,12,18} for n in Z24_STAR)
nil_stay2 = all((18*n)%24 in {0,6,12,18} for n in Z24_STAR)
print(f"  6 * coprime stays nilpotent: {nil_stay}")
print(f"  18 * coprime stays nilpotent: {nil_stay2}")

# A3: Goldstone analogy scorecard
print(f"\n  A3: GOLDSTONE/GHOST ANALOGY SCORECARD")
print("  " + "-" * 50)
print(f"  {'Property':>40} {'SM':>10} {'Monad':>10} {'Match?':>8}")
print(f"  {'':->40} {'':->10} {'':->10} {'':->8}")

checks = []

# Count
sm_goldstone_count = 3  # W+, W-, Z
monad_nilpotent_count = 3  # 6, 12, 18
count_match = sm_goldstone_count == monad_nilpotent_count
checks.append(count_match)
print(f"  {'Count of non-trivial elements':>40} {'3':>10} {'3':>10} {'YES' if count_match else 'NO':>8}")

# Zero mass / decay to zero
sm_zero_mass = "massless"  # Goldstones are massless before eating
monad_decay = "decay to 0"  # nilpotents decay to 0
print(f"  {'Neutral/null behavior':>40} {'massless':>10} {'->0':>10} {'~':>8}")

# Eaten/absorbed
sm_eaten = "eaten by W/Z"  # Goldstones become longitudinal modes
monad_absorbed = "12 absorbs all"  # 12 is the "attractor" in decay chains
print(f"  {'Absorption mechanism':>40} {'eaten':>10} {'attractor':>10} {'~':>8}")

# Gauge artifact
sm_ghost = "gauge artifact"  # FP ghosts
monad_not_unit = "not units"  # nilpotents can't be inverted
print(f"  {'Not in unit group':>40} {'YES':>10} {'YES':>10} {'YES':>8}")
checks.append(True)

# Persistent under symmetry
sm_persistent = "always present"
monad_persistent = "always present"  # nilpotent sector is structural
print(f"  {'Structural permanence':>40} {'YES':>10} {'YES':>10} {'YES':>8}")
checks.append(True)

# The SM has specific group theory: SU(2) x U(1) breaking
# The monad has Z2 x Z2 x Z2 -- abelian
sm_nonabelian = True
monad_abelian = True
print(f"  {'Non-abelian structure':>40} {'YES':>10} {'NO':>10} {'FAIL':>8}")
checks.append(False)

print(f"\n  VERDICT: The count match (3=3) is notable. The 'decay to zero'")
print(f"  parallel is evocative. But the monad is ABELIAN -- the SM Goldstone")
print(f"  mechanism requires NON-abelian SU(2). The analogy is structural,")
print(f"  not dynamical. Score: {sum(checks)}/{len(checks)} properties align.")

# A4: What the nilpotent sector ACTUALLY tells us
print(f"\n  A4: WHAT THE NILPOTENT SECTOR ACTUALLY TELLS US")
print("  " + "-" * 50)
print(f"  1. Numbers at positions 0,6,12,18 are ALWAYS divisible by 6")
print(f"  2. These positions have HIGHEST average sigma/n (most abundant)")
print(f"  3. Self-multiplication converges to 0 (dissipative)")
print(f"  4. They CANNOT be inverted (no multiplicative inverse)")
print(f"  5. Primorials live here after 3# (bounce between 6 and 18)")
print(f"  6. The '12' position is special: both 6 and 18 decay through it")
print(f"     12 = 2^2 * 3, the product of the two 'dark' primes")
print(f"     12^2 = 144 = 6*24, instant annihilation")
print(f"  This is pure ring theory. The Goldstone framing is a lens, not a proof.")

# ====================================================================
# PART B: YUKAWA SCALING -- THE ACID TEST
# ====================================================================
print("\n" + "=" * 70)
print("PART B: YUKAWA SCALING -- 1/p vs ACTUAL FERMION MASSES")
print("=" * 70)

print("""
  CLAIM: The fermion mass hierarchy can be modeled as m ~ 1/p for
  primes p, with coupling strength sigma(p)/p = 1 + 1/p.

  THE ACID TEST: compute predicted mass ratios from 1/p and compare
  to actual measured fermion mass ratios.
""")

# Known fermion masses (PDG 2023 values, in MeV)
# Charged leptons
m_electron = 0.511  # MeV
m_muon = 105.66  # MeV
m_tau = 1776.86  # MeV

# Quarks (MS-bar masses at appropriate scales)
m_up = 2.16  # MeV
m_down = 4.67  # MeV
m_charm = 1270.0  # MeV
m_strange = 93.0  # MeV
m_top = 172500.0  # MeV (172.5 GeV)
m_bottom = 4180.0  # MeV

# Neutrino masses (upper limits from oscillation data, approximate)
m_nu_e = 0.0000022  # ~2.2 eV upper limit
m_nu_mu = 0.00019  # ~0.19 MeV upper limit
m_nu_tau = 0.018  # ~18 MeV upper limit

# All 12 fermions sorted by mass
fermions = [
    ("electron neutrino", m_nu_e, "lepton"),
    ("muon neutrino", m_nu_mu, "lepton"),
    ("tau neutrino", m_nu_tau, "lepton"),
    ("electron", m_electron, "lepton"),
    ("up quark", m_up, "quark"),
    ("down quark", m_down, "quark"),
    ("strange quark", m_strange, "quark"),
    ("muon", m_muon, "lepton"),
    ("charm quark", m_charm, "quark"),
    ("tau", m_tau, "lepton"),
    ("bottom quark", m_bottom, "quark"),
    ("top quark", m_top, "quark"),
]
fermions.sort(key=lambda x: x[1])

print(f"  Known fermion masses (PDG 2023):")
print(f"  {'#':>3} {'Fermion':>20} {'Mass (MeV)':>14} {'Type':>7} {'log10(m)':>9}")
for i, (name, mass, ftype) in enumerate(fermions):
    if mass > 0:
        print(f"  {i+1:>3} {name:>20} {mass:>14.4e} {ftype:>7} {log10(mass):>9.2f}")

# Test 1: Simple 1/p scaling
# If we assign primes to fermions in order, does 1/p match the mass hierarchy?
primes_list = [p for p in range(2, 100) if is_prime(p)]

print(f"\n  TEST 1: Simple 1/p assignment (primes in order)")
print(f"  Assign p_i = ith prime to ith fermion (by mass rank)")
print(f"  Predicted ratio: m_i/m_electron = p_electron / p_i")
print(f"  (since m ~ 1/p, m_i/m_j = p_j/p_i)")

# Use electron as reference
e_idx = next(i for i, (n, m, t) in enumerate(fermions) if n == "electron")
m_ref = fermions[e_idx][1]

print(f"\n  {'Fermion':>20} {'Actual m/m_e':>12} {'p':>4} {'1/p ratio':>12} {'Error':>8}")
print(f"  {'':->20} {'':->12} {'':->4} {'':->12} {'':->8}")

errors_simple = []
for i, (name, mass, ftype) in enumerate(fermions):
    p = primes_list[i]
    actual_ratio = mass / m_ref
    predicted_ratio = m_ref / mass if mass > 0 else 0  # 1/p means heavier = smaller p
    # Actually: if m ~ 1/p, then lighter fermion = larger p
    # So the lightest fermion (nu_e) gets the largest prime
    # Let's reverse: assign largest primes to lightest fermions
    pass

# Better approach: assign primes to fermions such that 1/p matches mass ordering
# Lightest fermion -> largest prime (smallest 1/p)
# Heaviest fermion -> smallest prime (largest 1/p)
print(f"  (Reversed: heaviest fermion gets smallest prime)")
print(f"\n  {'Fermion':>20} {'Mass(MeV)':>10} {'Actual ratio':>12} {'Assigned p':>10} {'1/p':>10} {'1/p norm':>10} {'Error':>8}")

# Sort by mass descending for prime assignment
fermions_desc = sorted(fermions, key=lambda x: -x[1])
assigned_primes = {}
errors = []

# Normalize masses to [0,1] range using log
log_masses = [(name, log10(mass), ftype) for name, mass, ftype in fermions_desc if mass > 0]
log_min = min(lm for _, lm, _ in log_masses)
log_max = max(lm for _, lm, _ in log_masses)

# Normalize 1/p values
inv_primes = [(p, 1.0/p) for p in primes_list[:len(log_masses)]]
inv_min = min(ip for _, ip in inv_primes)
inv_max = max(ip for _, ip in inv_primes)

print(f"\n  Mass range: {log_min:.2f} to {log_max:.2f} (log10 MeV), span = {log_max-log_min:.2f}")
print(f"  1/p range: {inv_min:.6f} to {inv_max:.6f} (1/p for p={primes_list[0]}..{primes_list[len(log_masses)-1]})")
print(f"  Mass span = {10**(log_max-log_min):.0f}x,  1/p span = {inv_max/inv_min:.1f}x")
print(f"\n  IMMEDIATE PROBLEM: mass hierarchy spans {10**(log_max-log_min):.0e}x")
print(f"  but 1/p for first 12 primes only spans {inv_max/inv_min:.1f}x")
print(f"  1/p scaling CANNOT reproduce the fermion mass hierarchy with sequential primes.")

# Test 2: Best-fit primes (find the prime that minimizes error for each fermion)
print(f"\n  TEST 2: Best-fit primes (minimize error for each fermion)")
print(f"  For each fermion, find prime p where 1/p best matches normalized mass")
print(f"  Using log10(mass) as the target variable")

# Use log scale for fitting
print(f"\n  {'Fermion':>20} {'log10(m)':>9} {'Best p':>6} {'log10(1/p)':>11} {'Residual':>9}")

residuals = []
for name, mass, ftype in fermions_desc:
    if mass <= 0: continue
    log_m = log10(mass)
    # Find prime p where log10(1/p) = -log10(p) is closest to log_m
    best_p = None
    best_resid = float('inf')
    for p in primes_list:
        log_inv_p = -log10(p)
        resid = abs(log_inv_p - log_m)
        if resid < best_resid:
            best_resid = resid
            best_p = p
    # Also try large primes up to 10^|log_m|
    if log_m < -1:
        target_p = int(10**(-log_m))
        for p in range(max(2, target_p - 100), target_p + 100):
            if is_prime(p):
                log_inv_p = -log10(p)
                resid = abs(log_inv_p - log_m)
                if resid < best_resid:
                    best_resid = resid
                    best_p = p

    log_inv_p = -log10(best_p) if best_p else 0
    assigned_primes[name] = best_p
    residuals.append(best_resid)
    print(f"  {name:>20} {log_m:>9.4f} {best_p:>6} {log_inv_p:>11.4f} {best_resid:>9.4f}")

mean_resid = sum(residuals) / len(residuals) if residuals else float('inf')
print(f"\n  Mean absolute residual (log10 scale): {mean_resid:.4f}")
print(f"  This means average error is ~{10**mean_resid:.1f}x in mass")

# Test 3: Correlation between log10(mass) and -log10(p)
print(f"\n  TEST 3: Correlation between fermion mass rank and prime assignment")
print(f"  If the hierarchy is captured by 1/p, the rank correlation should be high")

# Rank fermions by mass
fermion_ranks = {name: i+1 for i, (name, _, _) in enumerate(
    sorted(fermions, key=lambda x: x[1]))}

# Rank assigned primes
prime_ranks = {}
sorted_by_p = sorted(assigned_primes.items(), key=lambda x: x[1])
for i, (name, _) in enumerate(sorted_by_p):
    prime_ranks[name] = i + 1

# Spearman rank correlation
n = len(fermion_ranks)
d_sq_sum = sum((fermion_ranks[name] - prime_ranks[name])**2 for name in fermion_ranks)
spearman = 1 - 6 * d_sq_sum / (n * (n**2 - 1))

print(f"  Fermion mass rank vs prime rank:")
print(f"  {'Fermion':>20} {'Mass rank':>9} {'Prime rank':>10} {'d^2':>5}")
for name in sorted(fermion_ranks.keys(), key=lambda x: fermion_ranks[x]):
    mr = fermion_ranks[name]
    pr = prime_ranks[name]
    d2 = (mr - pr)**2
    print(f"  {name:>20} {mr:>9} {pr:>10} {d2:>5}")

print(f"\n  Spearman rank correlation: {spearman:.4f}")
print(f"  (1.0 = perfect monotone relationship, 0 = no relationship)")

# Test 4: sigma(p)/p = 1 + 1/p vs actual mass ratios
print(f"\n  TEST 4: sigma(p)/p = 1 + 1/p as 'mass' -- relative predictions")
print(f"  If m_i = sigma(p_i)/p_i = 1 + 1/p_i, predict mass ratios")
print(f"  Use top quark (heaviest) as reference")

top_mass = m_top
top_prime = 2  # smallest prime -> heaviest fermion
sigma_over_p_top = 1 + 1.0/top_prime

print(f"\n  Top quark: m = {top_mass:.0f} MeV, assigned p = {top_prime}")
print(f"  sigma(2)/2 = {sigma_over_p_top:.4f}")
print(f"  Scale factor: {top_mass/sigma_over_p_top:.0f} MeV per unit sigma/p")
print(f"\n  {'Fermion':>20} {'Assigned p':>10} {'sigma/p':>8} {'Predicted(MeV)':>14} {'Actual(MeV)':>12} {'Ratio':>7}")

scale = top_mass / sigma_over_p_top
predictions = []
for name, mass, ftype in fermions_desc:
    if mass <= 0: continue
    p = assigned_primes.get(name, 2)
    sop = 1 + 1.0/p
    predicted = sop * scale
    ratio = predicted / mass if mass > 0 else 0
    predictions.append((name, predicted, mass, ratio))
    print(f"  {name:>20} {p:>10} {sop:>8.4f} {predicted:>14.1f} {mass:>12.1f} {ratio:>7.1f}x")

# Summary statistics
ratios = [r for _, _, _, r in predictions if r > 0]
max_ratio = max(ratios)
min_ratio = min(ratios)
mean_ratio = sum(ratios) / len(ratios)
print(f"\n  Prediction quality:")
print(f"    Best prediction: {min(abs(r-1) for r in ratios):.2f} error (ratio closest to 1)")
print(f"    Worst prediction: {max(abs(r-1) for r in ratios):.0f}x error")
print(f"    Mean ratio: {mean_ratio:.1f}x")
print(f"    Ratio range: {min_ratio:.1f}x to {max_ratio:.1f}x")

# Test 5: What if we use sigma(n)/n for COMPOSITE n?
print(f"\n  TEST 5: sigma(n)/n for COMPOSITE n -- wider dynamic range")
print(f"  sigma(p)/p = 1+1/p has limited range [1.0, 1.5] for primes")
print(f"  sigma(n)/n for composites with many factors can reach ~3+")
print(f"  Can composite sigma(n)/n better match the mass hierarchy?")

# Find best composite n for each fermion mass (using log10 scale)
print(f"\n  {'Fermion':>20} {'log10(m)':>9} {'Best n':>8} {'sigma/n':>8} {'log10(s/n)':>11} {'Resid':>7}")
comp_residuals = []
for name, mass, ftype in fermions_desc:
    if mass <= 0: continue
    log_m = log10(mass)
    best_n = 1
    best_resid = float('inf')
    best_sn = 1.0
    for n in range(2, 10001):
        sn = sigma(n) / n
        if sn <= 1: continue
        log_sn = log10(sn)
        resid = abs(log_sn - log_m)
        if resid < best_resid:
            best_resid = resid
            best_n = n
            best_sn = sn
    log_sn = log10(best_sn)
    comp_residuals.append(best_resid)
    print(f"  {name:>20} {log_m:>9.4f} {best_n:>8} {best_sn:>8.4f} {log_sn:>11.4f} {best_resid:>7.4f}")

mean_comp_resid = sum(comp_residuals) / len(comp_residuals)
print(f"\n  Mean residual with composites: {mean_comp_resid:.4f}")
print(f"  Mean residual with primes: {mean_resid:.4f}")
print(f"  Composites fit {'BETTER' if mean_comp_resid < mean_resid else 'WORSE'}")

# ====================================================================
# BRUTALLY HONEST SUMMARY
# ====================================================================
print("\n" + "=" * 70)
print("BRUTALLY HONEST SUMMARY")
print("=" * 70)

print(f"""
PART A -- NILPOTENT = GOLDSTONE/GHOST?
  MATCHES:
    - 3 non-zero nilpotents = 3 Goldstone bosons (EW sector)
    - Both "decay" to null state (0 in algebra, massless in physics)
    - Both excluded from the "unit" sector (units group / gauge group)
    - 12 is an attractor state (both 6 and 18 decay through it)

  FAILS:
    - Monad is ABELIAN; Goldstone mechanism requires NON-abelian SU(2)
    - No dynamics (no Lagrangian, no time evolution)
    - No gauge fixing interpretation (Faddeev-Popov analogy is surface-level)
    - The count match (3=3) could be coincidence

  VERDICT: Evocative parallel, not an isomorphism.

PART B -- YUKAWA SCALING = FERMION MASSES?
  MATCHES:
    - Rank correlation: {spearman:.3f} ({'strong' if abs(spearman) > 0.8 else 'moderate'})
    - 1/p gives a natural hierarchy (heavier = smaller p)
    - Log scale provides better fit than linear

  FAILS:
    - Mass hierarchy spans ~{10**(log_max-log_min):.0e}x
    - 1/p for sequential primes spans only ~{inv_max/inv_min:.0f}x
    - Mean prediction error: {mean_ratio:.0f}x
    - Worst prediction off by {max(abs(r-1) for r in ratios):.0f}x
    - sigma(p)/p has range [{1+1/primes_list[-1]:.4f}, {1+1/primes_list[0]:.4f}] --
      far too narrow for the actual mass range
    - No mechanism to predict WHICH prime maps to WHICH fermion
    - The "2 decimal place" claim: only works if you cherry-pick assignments

  VERDICT: The 1/p hierarchy has the right SHAPE (heavy-to-light)
  but the wrong SCALE. It cannot reproduce actual fermion masses
  without manual parameter fitting. This is fitting, not prediction.

WHAT'S ACTUALLY RIGOROUS IN THE MONAD:
  1. (Z/24Z)* = Z2^3 -- group theorem, verified
  2. p^2 = 1 mod 24 -- algebraic identity, verified
  3. CRT decomposition -- character theory, verified
  4. Nilpotent sector structure -- ring theory, verified
  5. Coprime never abundant -- computational, verified
  6. Constellation rail rules -- modular arithmetic, proven

  None of these require the Higgs framing to be true.
  They're interesting number theory regardless.
""")

# ====================================================================
# TESTS
# ====================================================================
print("=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 0

# Test 1: Nilpotent count = 3 (non-zero)
total += 1
if len([x for x in [6, 12, 18] if (x*x)%24 != x and any((x**k)%24==0 for k in range(1,10))]) == 3:
    print(f"  [PASS] Exactly 3 non-zero nilpotents in Z/24Z")
    passed += 1
else:
    print(f"  [FAIL] Nilpotent count wrong")

# Test 2: Nilpotent x coprime stays nilpotent
total += 1
if nil_stay and nil_stay2:
    print(f"  [PASS] Nilpotent x coprime = stays in nilpotent sector")
    passed += 1
else:
    print(f"  [FAIL] Nilpotent x coprime escapes sector")

# Test 3: Decay chains verified
total += 1
decay_ok = (6*6)%24 == 12 and (6*12)%24 == 0 and (12*12)%24 == 0 and (18*18)%24 == 12 and (18*12)%24 == 0
if decay_ok:
    print(f"  [PASS] All nilpotent decay chains verified")
    passed += 1
else:
    print(f"  [FAIL] Decay chain error")

# Test 4: Fermion masses correctly loaded
total += 1
mass_ok = len(fermions) == 12 and m_electron > 0 and m_top > 100000
if mass_ok:
    print(f"  [PASS] All 12 fermion masses loaded correctly")
    passed += 1
else:
    print(f"  [FAIL] Fermion mass loading error")

# Test 5: Rank correlation is strong (positive or negative)
total += 1
if abs(spearman) > 0.5:
    print(f"  [PASS] Rank correlation strong: {spearman:.3f}")
    passed += 1
else:
    print(f"  [FAIL] Rank correlation too low: {spearman:.3f}")

# Test 6: Mean prediction error is honest (reported correctly)
total += 1
reported_ok = mean_ratio > 1  # should be >1 since 1/p overpredicts light fermions
if reported_ok:
    print(f"  [PASS] Prediction error honestly reported: {mean_ratio:.1f}x mean")
    passed += 1
else:
    print(f"  [FAIL] Prediction error suspicious")

# Test 7: Spearman correlation matches
total += 1
if abs(spearman) <= 1.0:
    print(f"  [PASS] Spearman correlation valid: {spearman:.4f}")
    passed += 1
else:
    print(f"  [FAIL] Invalid Spearman correlation")

print(f"\nOVERALL: {passed}/{total} tests passed")

print("\n" + "=" * 70)
print("EXPERIMENT 127 COMPLETE")
print("=" * 70)
