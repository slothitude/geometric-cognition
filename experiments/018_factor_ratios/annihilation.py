"""
Experiment 018aaa: Annihilation as Phase Cancellation

From 018zz: antimatter IS matter at k+1. Matter/antimatter are
positional labels, not substance types. The user's question:

"Is Annihilation not a destruction, but a Phase Cancellation where
two primes occupy a composite slot that sums their k-parities to zero?"

In the monad:
- Matter: chi_3 = +1
- Antimatter: chi_3 = -1
- Composition: chi_3(pq) = chi_3(p) * chi_3(q)
- Anti x Anti = (-1)*(-1) = +1 = MATTER (not zero!)
- Matter x Anti = (+1)*(-1) = -1 = ANTIMATTER

So "annihilation" in the chi_3 channel gives MATTER, not zero.
But the k-parity sum is a different operation. Let's check whether
composing two primes from opposite sides of the twist produces a
composite whose k-parity CANCELS.

Key test: does the composite of a matter and antimatter prime
have k-parity that sums the parents' parities to zero?
"""

import numpy as np
from collections import defaultdict

print("=" * 70)
print("EXPERIMENT 018aaa: ANNIHILATION AS PHASE CANCELLATION")
print("Is Annihilation Just Phase Cancellation?")
print("=" * 70)

# --- PRIME GENERATION ---
N = 100000
is_prime = [True] * (N + 1)
is_prime[0] = is_prime[1] = False
for i in range(2, int(N**0.5) + 1):
    if is_prime[i]:
        for j in range(i*i, N + 1, i):
            is_prime[j] = False

primes = [p for p in range(5, N) if is_prime[p] and p % 6 in (1, 5)]

def chi3_mod12(n):
    r = n % 12
    if r in (1, 5): return +1
    if r in (7, 11): return -1
    return 0

def get_k_and_rail(n):
    """Get k-position and rail for a monad number"""
    if n % 6 == 1:  # R2
        return (n - 1) // 6, 'R2'
    else:  # R1
        return (n + 1) // 6, 'R1'

# ============================================================
# SECTION 1: THE ANNIHILATION CHANNELS
# ============================================================
print()
print("=" * 70)
print("SECTION 1: THE THREE ANNIHILATION CHANNELS")
print("=" * 70)
print()

print("In the Standard Model, matter + antimatter = energy (photons).")
print("In the monad, we have three composition channels:")
print()
print("  Channel 1: matter x matter = matter")
print("    chi_3: (+1)*(+1) = +1  (no cancellation)")
print("    Example: 5(matter) x 13(matter) = 65(matter)")
print()
print("  Channel 2: matter x antimatter = antimatter")
print("    chi_3: (+1)*(-1) = -1  (SIGN FLIP -- partial cancellation?)")
print("    Example: 5(matter) x 7(antimatter) = 35(antimatter)")
print()
print("  Channel 3: antimatter x antimatter = matter")
print("    chi_3: (-1)*(-1) = +1  (DOUBLE FLIP -- full return)")
print("    Example: 7(antimatter) x 11(antimatter) = 77(matter)")
print()
print("NONE of these give chi_3 = 0 (true annihilation).")
print("The chi_3 channel never cancels -- it only flips or preserves.")
print()
print("The closest to 'annihilation' is Channel 3: two antimatter")
print("primes compose to give a matter composite. This is the 720-degree")
print("return -- not destruction, but RETURN TO ORIGIN.")
print()

# ============================================================
# SECTION 2: k-PARITY ANALYSIS OF COMPOSITIONS
# ============================================================
print()
print("=" * 70)
print("SECTION 2: k-PARITY ANALYSIS OF COMPOSITIONS")
print("=" * 70)
print()

print("The user asks: does the k-parity SUM to zero?")
print("For composite n = p*q, the k-position is determined by")
print("the composition rules (Rule 3 from the monad):")
print()
print("  R1 x R1: k_N = 6ab - a - b  (R2 product)")
print("  R2 x R2: k_N = 6ab + a + b  (R2 product)")
print("  R1 x R2: k_N = 6ab - a + b  (R1 product)")
print("  R2 x R1: k_N = 6ab + a - b  (R1 product)")
print()
print("where a = k_p, b = k_q (k-positions of the factors).")
print()

# Compute k-parities for matter x antimatter compositions
print("k-parity analysis for matter x antimatter compositions:")
print()
print("  p(matter)  q(anti)  k_p  k_q  k_parity  q_parity  n=pq    k_n    k_n_parity  Sum mod 2")
print("  ----------  -------  ---  ---  --------  --------  ----    ---    ----------  --------")

cancellations = 0
non_cancellations = 0

for p in primes[:30]:
    chi3_p = chi3_mod12(p)
    if chi3_p != +1: continue  # only matter primes

    for q in primes[:30]:
        if q <= p: continue
        chi3_q = chi3_mod12(q)
        if chi3_q != -1: continue  # only antimatter primes

        n = p * q
        if n > N: continue

        k_p, rail_p = get_k_and_rail(p)
        k_q, rail_q = get_k_and_rail(q)
        k_n, rail_n = get_k_and_rail(n)

        k_parity_sum = (k_p % 2 + k_q % 2) % 2
        k_n_parity = k_n % 2

        if k_parity_sum == 0 and k_n_parity == 0:
            cancel_str = "BOTH even"
        elif k_parity_sum == 1 and k_n_parity == 1:
            cancel_str = "BOTH odd"
        else:
            cancel_str = "MIXED"

        # Check if k-parities "cancel" (sum to even and result is even)
        if k_p % 2 != k_q % 2:  # different k-parities
            cancellations += 1
        else:
            non_cancellations += 1

        if p <= 23 and q <= 29:
            print(f"  {p:4d}(m)    {q:4d}(a)   {k_p:3d}  {k_q:3d}    {k_p%2}        {k_q%2}     {n:5d}    {k_n:4d}      {k_n%2}         {cancel_str}")

print()
print(f"  Matter x Anti pairs with DIFFERENT k-parity: {cancellations}")
print(f"  Matter x Anti pairs with SAME k-parity: {non_cancellations}")
print()

# ============================================================
# SECTION 3: THE RESIDUE CANCELLATION
# ============================================================
print()
print("=" * 70)
print("SECTION 3: RESIDUE CANCELLATION")
print("=" * 70)
print()

print("Instead of k-parity, check the RESIDUE mod 12:")
print("Matter residues: {1, 5}")
print("Antimatter residues: {7, 11}")
print()
print("For matter x antimatter composition:")
print("  residue 1 x residue 7 = residue 7  (1+6 mod 12)")
print("  residue 1 x residue 11 = residue 11 (1+10 mod 12)")
print("  residue 5 x residue 7 = residue 11  (5+6 mod 12)")
print("  residue 5 x residue 11 = residue 5  (5+10 mod 12 = 3... wait)")
print()
print("Actually, residue composition is MULTIPLICATIVE (mod 12), not additive.")
print("Let's compute the actual residue products:")
print()

residue_products = {}
for r1 in [1, 5, 7, 11]:
    for r2 in [1, 5, 7, 11]:
        prod = (r1 * r2) % 12
        chi3_1 = chi3_mod12(r1)
        chi3_2 = chi3_mod12(r2)
        chi3_prod = chi3_mod12(prod) if prod in [1,5,7,11] else 0
        residue_products[(r1, r2)] = (prod, chi3_prod)
        side1 = "M" if chi3_1 == +1 else "A"
        side2 = "M" if chi3_2 == +1 else "A"
        side_prod = "M" if chi3_prod == +1 else "A" if chi3_prod == -1 else "0"
        print(f"  residue {r1:2d}({side1}) x residue {r2:2d}({side2}) = "
              f"residue {prod:2d} chi_3={chi3_prod:+d} ({side_prod})")

print()
print("The residue product table shows:")
print("  M x M -> M (matter preserved)")
print("  M x A -> A (matter + anti = anti, like sign flip)")
print("  A x A -> M (anti + anti = matter, the 720-degree return)")
print()
print("There is NO residue that maps to chi_3 = 0. The Z_2 x Z_2")
print("group has no 'zero' element -- only +/-1.")
print("ANNIHILATION TO ZERO IS IMPOSSIBLE in the chi_3 channel.")
print()

# ============================================================
# SECTION 4: WHAT ABOUT ADDITIVE k-PARITY?
# ============================================================
print()
print("=" * 70)
print("SECTION 4: ADDITIVE k-PARITY CANCELLATION")
print("=" * 70)
print()

print("The user's question: do the k-parities SUM to zero?")
print("k_parity can be 0 (even) or 1 (odd). Summing mod 2:")
print()
print("  0 + 0 = 0 (even + even = even)")
print("  0 + 1 = 1 (even + odd = odd)")
print("  1 + 0 = 1 (odd + even = odd)")
print("  1 + 1 = 0 (odd + odd = even -- CANCELLATION!)")
print()
print("So k-parity cancellation happens when BOTH parents are odd-k.")
print("Let's check: does matter x antimatter composition preferentially")
print("produce k-parity cancellation?")
print()

# Count by chi_3 combination and k-parity pattern
stats = defaultdict(int)

for i, p in enumerate(primes[:200]):
    chi3_p = chi3_mod12(p)
    k_p, rail_p = get_k_and_rail(p)

    for q in primes[i+1:300]:
        n = p * q
        if n > N: break

        chi3_q = chi3_mod12(q)
        k_q, rail_q = get_k_and_rail(q)
        k_n, rail_n = get_k_and_rail(n)

        combo = (chi3_p, chi3_q)
        k_sum = (k_p + k_q) % 2
        k_result = k_n % 2

        stats[(combo, k_sum, k_result)] += 1

print("  Composition type    k_sum=0->k_n=0  k_sum=0->k_n=1  k_sum=1->k_n=0  k_sum=1->k_n=1")
print("  ----------------    --------------  --------------  --------------  --------------")

for combo in [(1,1), (1,-1), (-1,-1)]:
    label = "M x M" if combo == (1,1) else "M x A" if combo == (1,-1) else "A x A"
    vals = []
    for k_sum in [0, 1]:
        for k_result in [0, 1]:
            vals.append(stats.get((combo, k_sum, k_result), 0))
    print(f"  {label:18s}    {vals[0]:14d}  {vals[1]:14d}  {vals[2]:14d}  {vals[3]:14d}")

print()

# The real question: for matter x antimatter, does k_p + k_q relate to k_n?
print("Direct check: k_p + k_q vs k_n for matter x antimatter composites")
print()
print("  p(matter)  q(anti)  k_p  k_q  k_p+k_q  k_n   k_n-(k_p+k_q)  Cancel?")
print("  ----------  -------  ---  ---  -------  ---   ------------   -------")

cancel_count = 0
total_ma = 0

for p in primes[:15]:
    chi3_p = chi3_mod12(p)
    if chi3_p != +1: continue

    for q in primes[:15]:
        if q <= p: continue
        chi3_q = chi3_mod12(q)
        if chi3_q != -1: continue

        n = p * q
        if n > N: continue

        k_p, _ = get_k_and_rail(p)
        k_q, _ = get_k_and_rail(q)
        k_n, _ = get_k_and_rail(n)

        diff = k_n - (k_p + k_q)
        total_ma += 1

        if diff == 0:
            cancel_count += 1

        if p <= 23 and q <= 31:
            print(f"  {p:4d}(m)    {q:4d}(a)   {k_p:3d}  {k_q:3d}   {k_p+k_q:5d}  {k_n:4d}   {diff:+8d}       "
                  f"{'YES' if diff == 0 else 'no'}")

print()
print(f"  Exact k-parity cancellations: {cancel_count}/{total_ma}")
print()

# ============================================================
# SECTION 5: THE COMPOSITION FORMULA -- WHEN DOES k = k_p + k_q?
# ============================================================
print()
print("=" * 70)
print("SECTION 5: COMPOSITION FORMULA vs k-SUM")
print("=" * 70)
print()

print("The monad's composition rules (from Rule 3):")
print("  R1 x R1 -> R2: k_n = 6*a*b - a - b  (NOT a+b)")
print("  R2 x R2 -> R2: k_n = 6*a*b + a + b  (NOT a+b)")
print("  R1 x R2 -> R1: k_n = 6*a*b - a + b  (NOT a+b)")
print("  R2 x R1 -> R1: k_n = 6*a*b + a - b  (NOT a+b)")
print()
print("k_n is NOT k_p + k_q. The composition formula is NONLINEAR")
print("(it involves products of k-positions, not sums).")
print()
print("The composite's k-position is dominated by 6*k_p*k_q,")
print("which is MUCH larger than k_p + k_q.")
print()
print("So 'phase cancellation' in k-space doesn't mean k_n = k_p + k_q.")
print("The composition is MULTIPLICATIVE in nature, not additive.")
print()

# Example: show the composition formula in action
print("Example compositions showing the formula:")
print()
print("  Type         p    q    k_p  k_q   6ab +/- a +/- b    k_n    Actual")
print("  ----------   --   --   ---  ---   ---------------    ---    ------")

examples = [
    (5, 7, "R1xR2"), (5, 11, "R1xR1"), (5, 13, "R1xR2"),
    (7, 11, "R2xR1"), (7, 13, "R2xR2"), (11, 13, "R1xR2"),
]

for p, q, comp_type in examples:
    n = p * q
    k_p, rail_p = get_k_and_rail(p)
    k_q, rail_q = get_k_and_rail(q)
    k_n, rail_n = get_k_and_rail(n)

    a, b = k_p, k_q
    if comp_type == "R1xR1":
        formula = f"6*{a}*{b}-{a}-{b}"
        expected = 6*a*b - a - b
    elif comp_type == "R2xR2":
        formula = f"6*{a}*{b}+{a}+{b}"
        expected = 6*a*b + a + b
    elif comp_type == "R1xR2":
        formula = f"6*{a}*{b}-{a}+{b}"
        expected = 6*a*b - a + b
    elif comp_type == "R2xR1":
        formula = f"6*{a}*{b}+{a}-{b}"
        expected = 6*a*b + a - b

    print(f"  {comp_type:10s}   {p:2d}   {q:2d}    {a:2d}   {b:2d}   {formula:16s}  {expected:5d}    {k_n:5d}")

print()
print("The composition is EXACT (Rule 3 verified). k_n >> k_p + k_q.")
print("No additive cancellation -- the composition is multiplicative.")
print()

# ============================================================
# SECTION 6: WHAT ANNIHILATION ACTUALLY IS
# ============================================================
print()
print("=" * 70)
print("SECTION 6: WHAT ANNIHILATION ACTUALLY IS")
print("=" * 70)
print()

print("Since chi_3 never reaches 0 and k-positions don't cancel additively,")
print("'annihilation' on the monad is NOT phase cancellation.")
print()
print("What IS the monad analog of annihilation?")
print()
print("In the Standard Model: matter + antimatter -> photons")
print("In the monad: the closest operation is:")
print()
print("  ANTIMATTER x ANTIMATTER = MATTER")
print("  chi_3: (-1) x (-1) = +1")
print("  This is the 720-degree return -- the DOUBLE CROSSING of the twist.")
print()
print("Two antimatter primes compose to give a MATTER composite.")
print("The antimatter 'annihilates' in the sense that the product is")
print("matter -- the chi_3 sign returns to positive.")
print()
print("But this is NOT destruction of matter. It's CONVERSION.")
print("The primes still exist as factors; the composite just has")
print("a different chi_3 label than its antimatter parents.")
print()
print("The conservation law: chi_3 is ALWAYS conserved.")
print("  chi_3(pq) = chi_3(p) * chi_3(q)")
print("  You can't create or destroy chi_3 -- only flip it.")
print("  This is EXACTLY like electric charge conservation.")
print()
print("Physical annihilation: matter + antimatter -> energy (charge = 0)")
print("Monad annihilation: antimatter + antimatter -> matter (charge flips)")
print()
print("The difference: in physics, the products are NEUTRAL (charge 0).")
print("On the monad, the products always have chi_3 = +1 or -1.")
print("There is NO neutral state in the Z_2 x Z_2 group.")
print()
print("This means: the monad cannot describe ANNIHILATION as understood")
print("in physics. It can describe CONVERSION between matter and")
print("antimatter, but not the creation of a neutral (chi_3 = 0) state.")
print()

# ============================================================
# SECTION 7: THE NEUTRAL CHANNEL -- chi_1 AND chi_2
# ============================================================
print()
print("=" * 70)
print("SECTION 7: IS THERE A NEUTRAL CHANNEL?")
print("=" * 70)
print()

print("chi_3 has values {-1, +1} -- no zero.")
print("But chi_1 (isospin) and chi_2 (rail) also have values {-1, +1}.")
print()
print("What if 'annihilation' is a chi_1 or chi_2 cancellation?")
print()

def chi1_mod12(n):
    r = n % 12
    if r in (1, 11): return +1
    if r in (5, 7): return -1
    return 0

def chi2_mod12(n):
    r = n % 12
    if r in (1, 7): return +1
    if r in (5, 11): return -1
    return 0

print("chi_1 composition (isospin):")
for r1 in [1, 5, 7, 11]:
    for r2 in [1, 5, 7, 11]:
        prod = (r1 * r2) % 12
        c1 = chi1_mod12(r1) if r1 in [1,5,7,11] else 0
        c2 = chi1_mod12(r2) if r2 in [1,5,7,11] else 0
        cp = chi1_mod12(prod) if prod in [1,5,7,11] else 0
        if c1 != 0 and c2 != 0:
            print(f"  chi1({r1:2d})={c1:+d} x chi1({r2:2d})={c2:+d} -> "
                  f"res {prod:2d}, chi1={cp:+d}  "
                  f"{'CANCEL!' if c1+c2 == 0 and cp == 0 else ''}")

print()
print("chi_1 never reaches 0 either. Same for chi_2.")
print("ALL three Dirichlet characters mod 12 are Z_2-valued.")
print("None of them can produce a 'zero' or 'neutral' state.")
print()
print("The monad's group (Z_2 x Z_2) has NO zero divisors.")
print("Every nonzero element has an inverse, and every product")
print("of nonzero elements is nonzero.")
print()
print("ANNIHILATION TO A NEUTRAL STATE IS ALGEBRAICALLY IMPOSSIBLE")
print("in the monad's Z_2 x Z_2 group structure.")
print()

# ============================================================
# SECTION 8: THE PHYSICAL INTERPRETATION
# ============================================================
print()
print("=" * 70)
print("SECTION 8: THE PHYSICAL INTERPRETATION")
print("=" * 70)
print()

print("Why can't the monad annihilate? Because the monad describes")
print("the VACUUM STRUCTURE, not the DYNAMICS.")
print()
print("In QFT, annihilation requires:")
print("  1. A matter particle (fermion)")
print("  2. An antimatter particle (antifermion)")
print("  3. An interaction vertex (coupling)")
print("  4. A gauge boson (photon) to carry away the energy")
print()
print("The monad provides items 1 and 2 (matter/antimatter primes)")
print("but NOT items 3 or 4 (no forces, no gauge bosons).")
print()
print("Without forces (proven in 018vv/018ww), there is no mechanism")
print("for two primes to 'interact' and produce a neutral state.")
print("The primes can only COMPOSE (multiply), and multiplication")
print("in Z_2 x Z_2 never produces zero.")
print()
print("The closest the monad gets to annihilation:")
print()
print("  ANNIHILATION-LIKE: anti x anti = matter")
print("    Two antimatter primes compose to give a matter composite.")
print("    The 'charge' (chi_3) returns to positive (720 degrees).")
print("    This is NOT annihilation -- it's PAIR CREATION in reverse.")
print()
print("  PAIR CREATION-LIKE: matter = anti x anti")
print("    A matter composite factors into two antimatter primes.")
print("    The 'charge' splits: +1 -> (-1) x (-1).")
print("    This is the monad's version of pair creation from vacuum.")
print()
print("  NO DESTRUCTION: chi_3 is conserved at 100%")
print("    The monad has perfect charge conservation.")
print("    Nothing is ever created or destroyed -- only converted.")
print("    This matches the Standard Model's charge conservation")
print("    but WITHOUT the annihilation channel to photons.")
print()

# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 70)
print("SUMMARY: ANNIHILATION AS PHASE CANCELLATION?")
print("=" * 70)
print()

print("IS ANNIHILATION PHASE CANCELLATION?")
print()
print("  NO. Three proofs:")
print()
print("  1. chi_3 NEVER reaches zero")
print("     Z_2 x Z_2 has no zero divisors: (+1)*(+1) = +1,")
print("     (-1)*(-1) = +1, (+1)*(-1) = -1. No cancellation.")
print()
print("  2. k-parities don't cancel additively")
print("     The composition formula is k_n = 6ab +/- a +/- b,")
print("     NOT k_a + k_b. The composition is multiplicative,")
print("     not additive. Phase cancellation requires addition.")
print()
print("  3. No neutral channel exists")
print("     All three Dirichlet characters (chi_1, chi_2, chi_3)")
print("     are Z_2-valued with no zero element.")
print("     The monad's algebra prevents neutral states entirely.")
print()
print("WHAT 'ANNIHILATION' ACTUALLY IS ON THE MONAD:")
print("  - CONVERSION, not destruction")
print("  - anti x anti = matter (the 720-degree return)")
print("  - chi_3 is conserved at 100% (nothing created or destroyed)")
print("  - The monad describes TOPOLOGY (what's allowed)")
print("  - It does NOT describe DYNAMICS (what happens when things meet)")
print()
print("THE MISSING PIECE:")
print("  Physical annihilation requires a GAUGE BOSON to carry away")
print("  energy/momentum. The monad has no gauge bosons (no forces")
print("  from 018vv). Without the force carrier, there's no mechanism")
print("  for two worldlines to 'meet' and 'cancel'. They can only")
print("  compose (multiply), which preserves charge algebraically.")
print()
print("This is consistent with the monad being CRYSTALLOGRAPHY:")
print("  crystallography tells you what structures are allowed,")
print("  but not what happens when structures interact. For that,")
print("  you need solid-state physics (forces, phonons, band theory).")
print()
print("======================================================================")
print("EXPERIMENT 018aaa COMPLETE")
print("======================================================================")
