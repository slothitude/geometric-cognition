"""
Experiment 018qqq: Does the D_n Rail-Switching Enforce Matter Conservation?

The question: does the non-Abelian rail-switching (R1 reflection in D_n)
PREVENT matter from drifting into the antimatter sector?

The walking sieve on the hyper-monad (mod 12):
  R2 primes (6k+1) = pure rotations in D_12 (stay on rail)
  R1 primes (6k-1) = rotation + reflection (switch rail)

Matter/antimatter: chi_3 quantum number from hyper-monad
  chi_3 = +1: matter sector ({1, 5} mod 12)
  chi_3 = -1: antimatter sector ({7, 11} mod 12)

The composition rule: chi_3(a*b) = chi_3(a) * chi_3(b)
"""

import numpy as np
from collections import Counter

print("=" * 70)
print("EXPERIMENT 018qqq: RAIL-SWITCHING AND MATTER CONSERVATION")
print("=" * 70)

# ============================================================
# SETUP
# ============================================================

def sieve_primes(N):
    is_p = np.ones(N + 1, dtype=bool)
    is_p[0] = is_p[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_p[i]:
            is_p[i*i::i] = False
    return is_p

k_max = 10000
N_max = 12 * k_max + 20
is_prime = sieve_primes(N_max)

# Hyper-monad (mod 12) positions and chi_3 assignments
# (Z/12Z)* = {1, 5, 7, 11}
# chi_1 (isospin): {1, 11} -> +1, {5, 7} -> -1
# chi_3 (matter/AM): {1, 5} -> +1 (matter), {7, 11} -> -1 (antimatter)
#
# R2 (6k+1): residues {1, 7} mod 12
# R1 (6k-1): residues {5, 11} mod 12
#
# Key: R2 contains BOTH matter (1) and antimatter (7)
#       R1 contains BOTH matter (5) and antimatter (11)

def get_hyper_info(n):
    """Get hyper-monad properties for number n."""
    r12 = n % 12
    rail = 'R2' if n % 6 == 1 else 'R1' if n % 6 == 5 else None
    if rail is None:
        return None
    chi3 = +1 if r12 in [1, 5] else -1  # matter/antimatter
    chi1 = +1 if r12 in [1, 11] else -1  # isospin
    sub_pos = r12
    return {
        'rail': rail,
        'chi3': chi3,
        'chi1': chi1,
        'residue_12': r12,
        'matter': 'matter' if chi3 == +1 else 'antimatter',
    }

# ============================================================
# SECTION 1: THE WALKING SIEVE AS MATTER TRANSPORT
# ============================================================
print()
print("=" * 70)
print("SECTION 1: WALKING SIEVE AS MATTER TRANSPORT")
print("=" * 70)

# The walking sieve: each prime generates a walk step
# R2 primes: stay on the same rail (pure rotation)
# R1 primes: switch rail (rotation + reflection)

# Track the walking sieve's chi_3 at each step
walk_steps = []
for k in range(1, k_max):
    for rail_name, rail_fn in [('R2', lambda k: 6*k+1), ('R1', lambda k: 6*k-1)]:
        n = rail_fn(k)
        if n < len(is_prime) and is_prime[n]:
            info = get_hyper_info(n)
            if info:
                walk_steps.append({
                    'k': k,
                    'n': n,
                    'rail': info['rail'],
                    'chi3': info['chi3'],
                    'matter': info['matter'],
                    'k_parity': k % 2,
                })

print(f"\n  Total walking sieve steps: {len(walk_steps)}")
print(f"  Steps by rail:")
r2_steps = [s for s in walk_steps if s['rail'] == 'R2']
r1_steps = [s for s in walk_steps if s['rail'] == 'R1']
print(f"    R2 (rotation only):     {len(r2_steps)}")
print(f"    R1 (rotation+reflect):  {len(r1_steps)}")

# Chi_3 of each step
matter_steps = [s for s in walk_steps if s['chi3'] == +1]
antimatter_steps = [s for s in walk_steps if s['chi3'] == -1]
print(f"\n  Steps by matter sector:")
print(f"    Matter (chi3=+1):     {len(matter_steps)}")
print(f"    Antimatter (chi3=-1): {len(antimatter_steps)}")
print(f"    Balance: {len(matter_steps)/len(antimatter_steps):.4f}")

# ============================================================
# SECTION 2: RAIL-SWITCHING AND SECTOR CROSSING
# ============================================================
print()
print("=" * 70)
print("SECTION 2: RAIL-SWITCHING vs SECTOR CROSSING")
print("=" * 70)

# For each step, did it:
# (a) stay on the same rail? (R2 step)
# (b) switch rail? (R1 step)
# And independently, did it:
# (x) stay in the same matter sector?
# (y) cross to the other matter sector?

print(f"\n  Rail-switching vs matter-sector crossing:")
print(f"  {'Step type':>25} {'Same sector':>12} {'Cross sector':>13} {'Cross %':>8}")

for step_type, steps in [('R2 (no switch)', r2_steps), ('R1 (switch)', r1_steps), ('ALL', walk_steps)]:
    same = [s for s in steps if s['chi3'] == steps[0]['chi3']] if steps else []
    # Actually, count properly
    same_sector = 0
    cross_sector = 0
    # A step "crosses sector" if its chi3 differs from the PREVIOUS step's chi3
    for i, s in enumerate(steps):
        if i == 0:
            same_sector += 1
            continue
        # Find the previous step overall (not just within this type)
        # Actually, let's just count the chi3 distribution
        pass

    # Simpler: just count how many of each type are matter vs antimatter
    m_count = sum(1 for s in steps if s['chi3'] == +1)
    am_count = sum(1 for s in steps if s['chi3'] == -1)
    total = len(steps)
    cross_pct = min(m_count, am_count) / total * 100 if total > 0 else 0
    print(f"    {step_type:>23} matter={m_count:>4}, AM={am_count:>4}  ({cross_pct:.1f}% minority)")

# ============================================================
# SECTION 3: THE SEQUENTIAL WALK -- TRACK CUMULATIVE chi_3
# ============================================================
print()
print("=" * 70)
print("SECTION 3: SEQUENTIAL WALK -- CUMULATIVE MATTER BALANCE")
print("=" * 70)

# Sort all primes on the rails by k value
all_rail_primes = []
for k in range(1, k_max):
    for n in [6*k-1, 6*k+1]:
        if n < len(is_prime) and is_prime[n]:
            info = get_hyper_info(n)
            if info:
                all_rail_primes.append((k, n, info))

all_rail_primes.sort(key=lambda x: x[0])
# Within same k, R1 (6k-1) comes before R2 (6k+1) since 6k-1 < 6k+1
# Actually at same k: 6k-1 < 6k+1, so R1 first

print(f"\n  Total rail primes: {len(all_rail_primes)}")

# Cumulative chi_3 balance
cumulative_chi3 = 0
max_drift = 0
drift_history = []
matter_count = 0
antimatter_count = 0

for k, n, info in all_rail_primes:
    cumulative_chi3 += info['chi3']
    if info['chi3'] == +1:
        matter_count += 1
    else:
        antimatter_count += 1
    max_drift = max(max_drift, abs(cumulative_chi3))
    drift_history.append(cumulative_chi3)

print(f"  Final cumulative chi_3: {cumulative_chi3}")
print(f"  Maximum drift from zero: {max_drift}")
print(f"  Total matter steps: {matter_count}")
print(f"  Total antimatter steps: {antimatter_count}")
print(f"  Matter/antimatter ratio: {matter_count/antimatter_count:.4f}")
print(f"  Net balance / total: {cumulative_chi3/len(all_rail_primes)*100:.2f}%")

# Check if drift scales as sqrt(N) (random walk) or is bounded (conservation)
sqrt_N = np.sqrt(len(all_rail_primes))
print(f"\n  sqrt(N) = {sqrt_N:.1f}")
print(f"  Max drift / sqrt(N) = {max_drift / sqrt_N:.2f}")
print(f"  (Random walk would give ~3-4; bounded would give ~1)")

# ============================================================
# SECTION 4: R1 vs R2 ROLE IN SECTOR TRANSPORT
# ============================================================
print()
print("=" * 70)
print("SECTION 4: R1 (REFLECTION) vs R2 (ROTATION) SECTOR TRANSPORT")
print("=" * 70)

# R2 primes: residues {1, 7} mod 12
#   residue 1 mod 12: chi3 = +1 (matter)
#   residue 7 mod 12: chi3 = -1 (antimatter)
# R2 stays on the SAME rail but CAN be either sector (depends on k parity)

# R1 primes: residues {5, 11} mod 12
#   residue 5 mod 12: chi3 = +1 (matter)
#   residue 11 mod 12: chi3 = -1 (antimatter)
# R1 SWITCHES rail but CAN be either sector

# The key question: does the rail-switching (R1) do anything SPECIAL
# to matter/antimatter, beyond what R2 already does?

print(f"\n  R2 primes (pure rotation, stay on rail):")
r2_matter = sum(1 for s in r2_steps if s['chi3'] == +1)
r2_am = sum(1 for s in r2_steps if s['chi3'] == -1)
print(f"    Matter:     {r2_matter} ({r2_matter/len(r2_steps)*100:.1f}%)")
print(f"    Antimatter: {r2_am} ({r2_am/len(r2_steps)*100:.1f}%)")

print(f"\n  R1 primes (rotation + reflection, switch rail):")
r1_matter = sum(1 for s in r1_steps if s['chi3'] == +1)
r1_am = sum(1 for s in r1_steps if s['chi3'] == -1)
print(f"    Matter:     {r1_matter} ({r1_matter/len(r1_steps)*100:.1f}%)")
print(f"    Antimatter: {r1_am} ({r1_am/len(r1_steps)*100:.1f}%)")

# k-parity determines matter/antimatter sector for R2
print(f"\n  R2 primes by k-parity (staggered fermion structure):")
r2_even_matter = sum(1 for s in r2_steps if s['k'] % 2 == 0 and s['chi3'] == +1)
r2_even_am = sum(1 for s in r2_steps if s['k'] % 2 == 0 and s['chi3'] == -1)
r2_odd_matter = sum(1 for s in r2_steps if s['k'] % 2 == 1 and s['chi3'] == +1)
r2_odd_am = sum(1 for s in r2_steps if s['k'] % 2 == 1 and s['chi3'] == -1)
print(f"    k even: matter={r2_even_matter}, AM={r2_even_am} ({r2_even_matter/(r2_even_matter+r2_even_am)*100:.1f}% matter)")
print(f"    k odd:  matter={r2_odd_matter}, AM={r2_odd_am} ({r2_odd_matter/(r2_odd_matter+r2_odd_am)*100:.1f}% matter)")

# Same for R1
print(f"\n  R1 primes by k-parity:")
r1_even_matter = sum(1 for s in r1_steps if s['k'] % 2 == 0 and s['chi3'] == +1)
r1_even_am = sum(1 for s in r1_steps if s['k'] % 2 == 0 and s['chi3'] == -1)
r1_odd_matter = sum(1 for s in r1_steps if s['k'] % 2 == 1 and s['chi3'] == +1)
r1_odd_am = sum(1 for s in r1_steps if s['k'] % 2 == 1 and s['chi3'] == -1)
r1_even_total = r1_even_matter + r1_even_am
r1_odd_total = r1_odd_matter + r1_odd_am
print(f"    k even: matter={r1_even_matter}, AM={r1_even_am} ({r1_even_matter/r1_even_total*100:.1f}% matter)" if r1_even_total > 0 else "    k even: 0")
print(f"    k odd:  matter={r1_odd_matter}, AM={r1_odd_am} ({r1_odd_matter/r1_odd_total*100:.1f}% matter)" if r1_odd_total > 0 else "    k odd: 0")

# ============================================================
# SECTION 5: THE CRITICAL TEST -- ABELIAN vs NON-ABELIAN MODEL
# ============================================================
print()
print("=" * 70)
print("SECTION 5: ABELIAN vs NON-ABELIAN TRANSPORT")
print("=" * 70)

# Model A: "Abelian only" -- all primes are R2 (pure rotation)
# No rail-switching. Matter/antimatter depends ONLY on k-parity.
# In this model, the walk is purely rotational.

# Model B: "Non-Abelian" -- actual walking sieve with R1 and R2
# Rail-switching occurs. Matter/antimatter depends on k-parity AND rail.

# In both models, track whether chi_3 is conserved

print(f"""
  MODEL A (Abelian only, no rail-switching):
    Every prime is R2 (6k+1), residue mod 12 is either 1 or 7
    residue 1 mod 12: n = 12k + 1 -> k even -> matter
    residue 7 mod 12: n = 12k + 7 -> k even -> antimatter

    Wait -- let's compute directly.
    n = 6k+1
    n mod 12 = 1 if k even, 7 if k odd
    chi_3(n) = +1 if n mod 12 in {{1,5}}, -1 if in {{7,11}}

    So for R2: chi_3 = +1 when k even, chi_3 = -1 when k odd
    This is PERFECTLY staggered: alternating matter/antimatter

  MODEL B (Non-Abelian, with rail-switching):
    R2 primes: chi_3 alternates with k-parity (same as Model A)
    R1 primes: n = 6k-1
      n mod 12 = 11 if k even, 5 if k odd
      chi_3(n) = -1 if residue 11, +1 if residue 5
      So R1: chi_3 = -1 when k even, chi_3 = +1 when k odd

    R1 is OPPOSITE to R2 in its k-parity mapping!
    R2: even k -> matter, odd k -> antimatter
    R1: even k -> antimatter, odd k -> matter
""")

# Verify this computationally
print(f"  Computational verification:")
print(f"    R2, k even -> chi3={get_hyper_info(6*2+1)['chi3']} (matter)")
print(f"    R2, k odd  -> chi3={get_hyper_info(6*3+1)['chi3']} (antimatter)")
print(f"    R1, k even -> chi3={get_hyper_info(6*2-1)['chi3']} (antimatter)")
print(f"    R1, k odd  -> chi3={get_hyper_info(6*3-1)['chi3']} (matter)")

print(f"""
  THE CRITICAL INSIGHT:

  In Model A (no rail-switching), matter/antimatter is EXACTLY
  determined by k-parity. The walk is purely Abelian -- a rotation
  through k-space that alternates sectors perfectly.

  In Model B (with rail-switching), R1 primes INVERT the k-parity
  rule. They transport matter when k is odd (where R2 would transport
  antimatter) and antimatter when k is even (where R2 would transport
  matter).

  The rail-switching does NOT prevent matter-antimatter mixing.
  It OPPOSES the staggered pattern. It CREATES deviations from
  the perfect alternation.
""")

# Quantify: how much does R1 disrupt the staggered pattern?
# Perfect stagger: matter at even k, antimatter at odd k
# Deviation = prime that doesn't match this pattern

perfect_matter = sum(1 for k, n, info in all_rail_primes
                     if info['chi3'] == +1 and k % 2 == 0)
perfect_am = sum(1 for k, n, info in all_rail_primes
                 if info['chi3'] == -1 and k % 2 == 1)
deviant_matter = sum(1 for k, n, info in all_rail_primes
                     if info['chi3'] == +1 and k % 2 == 1)
deviant_am = sum(1 for k, n, info in all_rail_primes
                 if info['chi3'] == -1 and k % 2 == 0)

total_perfect = perfect_matter + perfect_am
total_deviant = deviant_matter + deviant_am

print(f"  Staggered pattern compliance:")
print(f"    Follows stagger (R2 pattern):  {total_perfect} ({total_perfect/len(all_rail_primes)*100:.1f}%)")
print(f"    Violates stagger (R1 pattern): {total_deviant} ({total_deviant/len(all_rail_primes)*100:.1f}%)")

# All R2 primes follow the stagger, all R1 violate it
r2_follows = sum(1 for s in r2_steps if (s['chi3'] == +1 and s['k'] % 2 == 0) or
                                         (s['chi3'] == -1 and s['k'] % 2 == 1))
r1_violates = sum(1 for s in r1_steps if (s['chi3'] == +1 and s['k'] % 2 == 1) or
                                         (s['chi3'] == -1 and s['k'] % 2 == 0))
print(f"    R2 follows stagger:  {r2_follows}/{len(r2_steps)} = {r2_follows/len(r2_steps)*100:.1f}%")
print(f"    R1 violates stagger: {r1_violates}/{len(r1_steps)} = {r1_violates/len(r1_steps)*100:.1f}%")

# ============================================================
# SECTION 6: THE COMMUTATOR MEASURES SECTOR LEAKAGE
# ============================================================
print()
print("=" * 70)
print("SECTION 6: THE COMMUTATOR MEASURES SECTOR LEAKAGE")
print("=" * 70)

# The D_12 commutator [R2(a), R1(b)] = r^(2a) measures the
# non-commutativity of rotation (R2) and reflection (R1).
#
# In physical terms:
# R2 = transport along the same rail (matter stays matter)
# R1 = transport with rail-switch (can flip matter/antimatter)
# [R2, R1] measures whether ORDER matters for sector transport.

# Test: composite a*b where a is R2, b is R1
# Does matter(a*b) depend on whether we compute a*b or b*a?
print(f"\n  Testing commutator of sector transport:")

# For two coprime residues mod 12:
# a=1 (R2, matter), b=5 (R1, matter), a*b=5 (R1, matter)
# a=1 (R2, matter), b=11 (R1, antimatter), a*b=11 (R1, antimatter)
# a=7 (R2, antimatter), b=5 (R1, matter), a*b=11 (R1, antimatter)
# a=7 (R2, antimatter), b=11 (R1, antimatter), a*b=5 (R1, matter)

# Chi_3 is multiplicative: chi_3(a*b) = chi_3(a) * chi_3(b)
# This is ABELIAN -- chi_3 doesn't care about order.

print(f"  chi_3 is multiplicative: chi_3(a*b) = chi_3(a)*chi_3(b)")
print(f"  Multiplication in Z is commutative: a*b = b*a")
print(f"  Therefore chi_3(a*b) = chi_3(b*a) always.")
print(f"  The COMMUTATOR does NOT affect matter/antimatter conservation.")
print(f"  chi_3 conservation is an ABELIAN property, preserved regardless.")

# But what about the WALKING SIEVE specifically?
# The walking sieve assigns chi_3 based on the RESULT of the walk,
# not just the product. The ORDER of sieve steps matters for the
# position in k-space, even if chi_3 is conserved.

# Track: does the walking sieve ever produce a chi_3 violation?
# Composite n = a*b, is chi_3(n) = chi_3(a)*chi_3(b)?
violations = 0
tested = 0
for k in range(1, min(k_max, 3000)):
    for n in [6*k-1, 6*k+1]:
        if n < len(is_prime) and not is_prime[n] and n >= 4:
            info_n = get_hyper_info(n)
            if info_n is None:
                continue
            # Factorize
            temp = n
            factors = []
            for p in range(2, int(n**0.5) + 1):
                while temp % p == 0:
                    factors.append(p)
                    temp //= p
            if temp > 1:
                factors.append(temp)
            if len(factors) >= 2:
                chi3_product = 1
                valid = True
                for f in factors:
                    info_f = get_hyper_info(f)
                    if info_f is None:
                        valid = False
                        break
                    chi3_product *= info_f['chi3']
                if valid:
                    tested += 1
                    if chi3_product != info_n['chi3']:
                        violations += 1

print(f"\n  chi_3 multiplicative conservation test:")
print(f"    Tested: {tested} composites")
print(f"    Violations: {violations}")
print(f"    Conservation rate: {(tested - violations)/tested*100:.1f}%")

# ============================================================
# SECTION 7: CONCLUSION
# ============================================================
print()
print("=" * 70)
print("SECTION 7: CONCLUSION")
print("=" * 70)

print(f"""
  DOES THE NON-ABELIAN RAIL-SWITCHING PREVENT MATTER-ANTIMATTER DRIFT?

  NO. It does the OPPOSITE.

  1. The staggered fermion pattern (k-parity determines sector) is a
     PURELY ABELIAN feature of the residue structure. R2 primes at even
     k are always matter, R2 at odd k are always antimatter.

  2. The R1 rail-switching (the non-Abelian reflection in D_12)
     VIOLATES the staggered pattern. R1 primes at even k are
     antimatter, R1 at odd k are matter -- the OPPOSITE of R2.

  3. The walking sieve's non-Abelian structure does NOT prevent
     matter-antimatter mixing. It CREATES the mixing. Without R1
     primes (pure Abelian model), the stagger would be perfect:
     matter and antimatter would never appear at the same k.

  4. chi_3 conservation is ABELIAN. It follows from the multiplicative
     property chi_3(a*b) = chi_3(a)*chi_3(b), which holds because
     multiplication in Z is commutative. The D_n commutator has
     ZERO effect on chi_3 conservation.

  5. What the non-Abelian layer DOES:
     - It determines HOW charge is transported (the path matters)
     - It creates the deviations from perfect staggering
     - It makes the matter/antimatter balance approximate rather than exact
     - It gives the walk a non-trivial topological structure

  6. What the non-Abelian layer does NOT do:
     - It does NOT enforce matter conservation (that's Abelian)
     - It does NOT prevent sector crossing (it causes it)
     - It does NOT create the chi_3 quantum number (that's Layer 1)

  THE ARCHITECTURE:
    Layer 1 (Abelian): CREATES the chi_3 quantum number and ENFORCES conservation
    Layer 2 (Non-Abelian): TRANSPORTS chi_3 and CREATES deviations from the ideal

  The matter/antimatter separation is an ABELIAN property.
  The rail-switching makes it messy, not perfect.
  The monad's conservation law holds DESPITE the non-Abelian dynamics,
  not BECAUSE of them.
""")

print("=" * 70)
print("EXPERIMENT 018qqq COMPLETE")
print("=" * 70)
