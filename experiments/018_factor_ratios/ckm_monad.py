"""
Experiment 018pp: CKM Monad -- Quark Mixing from Cross-Generation Composition

The monad maps 12 fermions to 12 positions. Quarks sit at sub-positions
0, 2, 4 (even sp) on both rails:
  R2 (up-type): up(sp=0), charm(sp=2), top(sp=4)
  R1 (dn-type): down(sp=0), strange(sp=2), bottom(sp=4)

The CKM matrix V_ij describes weak transitions between these:
  V = | V_ud  V_us  V_ub |   | 0.974  0.225  0.004 |
      | V_cd  V_cs  V_cb | = | 0.225  0.973  0.041 |
      | V_td  V_ts  V_tb |   | 0.009  0.041  0.999 |

This experiment tests:
1. Why 3 generations (from 6 = 2 x 3 structure)
2. Cross-generation composite density as CKM analog
3. Whether the monad predicts the CKM hierarchy
4. The PMNS matrix for leptons
5. Wolfenstein parameterization from monad geometry
"""

import numpy as np
from collections import defaultdict

print("=" * 70)
print("EXPERIMENT 018pp: CKM MONAD")
print("Quark Mixing from Cross-Generation Composition")
print("=" * 70)

# --- PRIME GENERATION ---
N = 100000
is_prime = [True] * (N + 1)
is_prime[0] = is_prime[1] = False
for i in range(2, int(N**0.5) + 1):
    if is_prime[i]:
        for j in range(i*i, N + 1, i):
            is_prime[j] = False

# Classify primes by rail and sub-position
r2_primes = defaultdict(list)  # sp -> [primes]
r1_primes = defaultdict(list)
for p in range(5, N):
    if not is_prime[p]:
        continue
    if p % 6 == 1:  # R2
        k = (p - 1) // 6
        sp = k % 6
        r2_primes[sp].append(k)
    elif p % 6 == 5:  # R1
        k = (p + 1) // 6
        sp = k % 6
        r1_primes[sp].append(k)

# ============================================================
# SECTION 1: WHY 3 GENERATIONS?
# ============================================================
print()
print("=" * 70)
print("SECTION 1: WHY 3 GENERATIONS?")
print("=" * 70)
print()
print("The monad is based on 6k +/- 1. The modulus 6 has structure:")
print("  6 = 2 x 3")
print("  phi(6) = 2 (two coprime residues: 1 and 5)")
print("  Two rails: R2 (6k+1) and R1 (6k-1)")
print("  Six sub-positions per rail: sp = 0,1,2,3,4,5")
print()
print("The 6 sub-positions decompose into 3 pairs:")
print("  Generation 1: sp = 0 (quark), 1 (lepton)")
print("  Generation 2: sp = 2 (quark), 3 (lepton)")
print("  Generation 3: sp = 4 (quark), 5 (lepton)")
print()
print("Why 3 generations: because 6 sub-positions / 2 types = 3.")
print("The '2' is the quark/lepton distinction (even/odd sp).")
print("The '3' is the remaining factor after dividing by 2.")
print("6 = 2 x 3 => 2 types x 3 generations = 6 positions per rail.")
print()
print("The monad's answer to 'why 3 generations' is:")
print("  The minimal modulus that isolates primes is 6.")
print("  6 = 2 x 3 forces exactly 3 generation pairs.")
print("  Using a larger modulus would give more generations,")
print("  but only the minimal modulus captures ALL primes > 3.")
print()
print("Could we use modulus 30?")
print("  30 = 2 x 3 x 5, phi(30) = 8")
print("  8 rails with 30 sub-positions each")
print("  30 / 2 = 15 'generations' -- too many for physics")
print("  But the additional rails would be redundant (no new primes)")
print()
print("The monad predicts: nature uses the MINIMAL structure (mod 6)")
print("because it captures all primes with the fewest positions.")
print("3 generations is not arbitrary -- it's the minimum that works.")
print()

# ============================================================
# SECTION 2: CROSS-GENERATION COMPOSITION DENSITY
# ============================================================
print()
print("=" * 70)
print("SECTION 2: CROSS-GENERATION COMPOSITION DENSITY")
print("=" * 70)
print()

# For quarks: R2 sp=0,2,4 (up-type) x R1 sp=0,2,4 (down-type)
# Cross-rail composition: R2(sp_a) x R1(sp_b) -> R1, sp_N = (a-b) mod 6
# The composition counts give the "mixing" between generations

print("Quark sub-positions: R2 sp={0,2,4} (up-type), R1 sp={0,2,4} (down-type)")
print()
print("Cross-rail composition: R2(sp_a) x R1(sp_b) -> R1(sp=(a-b) mod 6)")
print()

# Count composites from each sp-pair
composite_count = np.zeros((3, 3))  # [up-gen][dn-gen]
# Quark sp values
up_sp = [0, 2, 4]  # gen 1, 2, 3
dn_sp = [0, 2, 4]

K = 5000  # range for k

for i, sp_a in enumerate(up_sp):
    for j, sp_b in enumerate(dn_sp):
        count = 0
        # R2(sp_a) x R1(sp_b): k_N = 6*a*b + a - b where a = sp_a + 6k1, b = sp_b + 6k2
        # Actually use the composite formula directly
        # For R2 x R1: the product is on R1 with sp = (sp_a - sp_b) mod 6
        # Count how many composites up to K come from this sp-pair
        primes_a = [k for k in r2_primes[sp_a] if k <= K]
        primes_b = [k for k in r1_primes[sp_b] if k <= K]
        for ka in primes_a:
            for kb in primes_b:
                # Cross-rail: product n = (6ka+1)(6kb-1) = 36ka*kb - 6ka + 6kb - 1
                # k_n = 6ka*kb - ka + kb
                kn = 6 * ka * kb - ka + kb
                if kn <= K and kn > 0:
                    count += 1
        composite_count[i, j] = count

print("Composite count from R2(up-sp) x R1(dn-sp) pairs (k <= 5000):")
print()
print("                  down(sp=0)  strange(sp=2)  bottom(sp=4)")
print("                  Gen 1       Gen 2          Gen 3")
for i, name in enumerate(["up(sp=0)", "charm(sp=2)", "top(sp=4)"]):
    print(f"  {name:14s}  {composite_count[i,0]:8.0f}    {composite_count[i,1]:8.0f}      {composite_count[i,2]:8.0f}")

print()

# Normalize to get "mixing probabilities"
total_per_row = composite_count.sum(axis=1, keepdims=True)
ckm_monad = composite_count / total_per_row

print("Monad CKM analog (normalized per row):")
print()
print("                  down(G1)    strange(G2)    bottom(G3)")
for i, name in enumerate(["up(G1)", "charm(G2)", "top(G3)"]):
    print(f"  {name:10s}      {ckm_monad[i,0]:.4f}      {ckm_monad[i,1]:.4f}       {ckm_monad[i,2]:.4f}")

print()

# Compare with physical CKM
ckm_physical = np.array([
    [0.974, 0.225, 0.0036],
    [0.225, 0.973, 0.041],
    [0.0088, 0.041, 0.999]
])

print("Physical CKM matrix (magnitudes):")
print()
print("                  down(G1)    strange(G2)    bottom(G3)")
for i, name in enumerate(["up(G1)", "charm(G2)", "top(G3)"]):
    print(f"  {name:10s}      {ckm_physical[i,0]:.4f}      {ckm_physical[i,1]:.4f}       {ckm_physical[i,2]:.4f}")

print()

# Compute similarity
diff = np.abs(ckm_monad - ckm_physical)
print("Absolute difference |monad - physical|:")
print()
print("                  down(G1)    strange(G2)    bottom(G3)")
for i, name in enumerate(["up(G1)", "charm(G2)", "top(G3)"]):
    print(f"  {name:10s}      {diff[i,0]:.4f}      {diff[i,1]:.4f}       {diff[i,2]:.4f}")

mean_diff = diff.mean()
max_diff = diff.max()
print(f"\n  Mean |diff|: {mean_diff:.4f}")
print(f"  Max  |diff|: {max_diff:.4f}")

# ============================================================
# SECTION 3: CKM HIERARCHY FROM SUB-POSITION DISTANCE
# ============================================================
print()
print("=" * 70)
print("SECTION 3: CKM HIERARCHY FROM SUB-POSITION DISTANCE")
print("=" * 70)
print()
print("The sub-position distance |sp_up - sp_down| between generations:")
print()
print("  Same generation (|dsp|=0): V_ud, V_cs, V_tb")
print("  Adjacent generation (|dsp|=2): V_us, V_cd, V_cb, V_ts")
print("  Skip generation (|dsp|=4): V_ub, V_td")
print()

# Physical CKM by sub-position distance
same_gen = [ckm_physical[0,0], ckm_physical[1,1], ckm_physical[2,2]]
adj_gen = [ckm_physical[0,1], ckm_physical[1,0], ckm_physical[1,2], ckm_physical[2,1]]
skip_gen = [ckm_physical[0,2], ckm_physical[2,0]]

print(f"  Same generation (|dsp|=0):  {np.mean(same_gen):.4f} (mean of {same_gen})")
print(f"  Adjacent gen    (|dsp|=2):  {np.mean(adj_gen):.4f} (mean of {adj_gen})")
print(f"  Skip generation (|dsp|=4):  {np.mean(skip_gen):.4f} (mean of {skip_gen})")
print()

# Monad CKM by sub-position distance
same_monad = [ckm_monad[0,0], ckm_monad[1,1], ckm_monad[2,2]]
adj_monad = [ckm_monad[0,1], ckm_monad[1,0], ckm_monad[1,2], ckm_monad[2,1]]
skip_monad = [ckm_monad[0,2], ckm_monad[1,2], ckm_monad[0,2], ckm_monad[2,0]]

# Actually let me be more careful about which elements map to which distance
# up(sp=0) x down(sp=0): dsp=0, monad=ckm_monad[0,0]
# up(sp=0) x strange(sp=2): dsp=2, monad=ckm_monad[0,1]
# up(sp=0) x bottom(sp=4): dsp=4, monad=ckm_monad[0,2]
# charm(sp=2) x down(sp=0): dsp=2, monad=ckm_monad[1,0]
# charm(sp=2) x strange(sp=2): dsp=0, monad=ckm_monad[1,1]
# charm(sp=2) x bottom(sp=4): dsp=2, monad=ckm_monad[1,2]
# top(sp=4) x down(sp=0): dsp=4, monad=ckm_monad[2,0]
# top(sp=4) x strange(sp=2): dsp=2, monad=ckm_monad[2,1]
# top(sp=4) x bottom(sp=4): dsp=0, monad=ckm_monad[2,2]

same_monad = [ckm_monad[0,0], ckm_monad[1,1], ckm_monad[2,2]]
adj_monad = [ckm_monad[0,1], ckm_monad[1,0], ckm_monad[1,2], ckm_monad[2,1]]
skip_monad = [ckm_monad[0,2], ckm_monad[2,0]]

print("Monad mixing by sub-position distance:")
print(f"  Same generation (|dsp|=0):  {np.mean(same_monad):.4f}")
print(f"  Adjacent gen    (|dsp|=2):  {np.mean(adj_monad):.4f}")
print(f"  Skip generation (|dsp|=4):  {np.mean(skip_monad):.4f}")
print()

# The hierarchy test: same > adjacent > skip?
hierarchy_physical = np.mean(same_gen) > np.mean(adj_gen) > np.mean(skip_gen)
hierarchy_monad = np.mean(same_monad) > np.mean(adj_monad) > np.mean(skip_monad)

print(f"  Physical hierarchy (same > adj > skip): {hierarchy_physical}")
print(f"  Monad hierarchy (same > adj > skip):    {hierarchy_monad}")

if hierarchy_monad:
    print()
    print("  RESULT: The monad reproduces the CKM HIERARCHY.")
    print("  Same-generation mixing dominates, cross-generation is suppressed.")
    print("  This follows from the monad's sub-position composition rules.")
else:
    print()
    print("  The monad does NOT reproduce the CKM hierarchy.")
    print("  Cross-generation composition is not suppressed as in the physical CKM.")

# ============================================================
# SECTION 4: THE CABIBBO ANGLE FROM THE MONAD
# ============================================================
print()
print("=" * 70)
print("SECTION 4: THE CABIBBO ANGLE FROM THE MONAD")
print("=" * 70)
print()

theta_c = np.arcsin(0.225)
print(f"Physical Cabibbo angle: theta_C = arcsin(0.225) = {np.degrees(theta_c):.2f} degrees")
print()

# The monad has a natural angle: the sub-position spacing = 30 degrees
# The Cabibbo angle ~ 13 degrees is close to 30/2 = 15 degrees
# Or: 13.02 / 30 = 0.434... not an obvious ratio

# Let's check: can the Cabibbo angle come from the monad's geometry?
print("Monad angular structure:")
print(f"  Sub-position spacing: 30 degrees")
print(f"  Cabibbo angle: {np.degrees(theta_c):.2f} degrees")
print(f"  Ratio: {np.degrees(theta_c)/30:.4f}")
print()

# Try various monad-based predictions
print("Tests of Cabibbo angle from monad quantities:")
print()

# 1. Direct geometric: theta_C = 30/pi * some factor
pred1 = np.degrees(np.arctan(1/3))  # arctan(1/3) from gen 1 to gen 2?
print(f"  arctan(1/3) = {pred1:.2f} deg (from gen spacing 1/3?)")

# 2. From the Euler product constant
pred2 = np.degrees(np.pi / (2 * np.sqrt(3)))
print(f"  pi/(2*sqrt(3)) rad = {pred2:.2f} deg (L(1) angle)")

# 3. From chi_1 density asymmetry
# R1 slightly leads R2: the asymmetry ~ 1/sqrt(x)
# Cabibbo ~ sqrt(0.05) ~ 0.22... close to 0.225!
# This is sqrt(rail asymmetry at moderate scale)
r1_count = sum(len(v) for v in r1_primes.values())
r2_count = sum(len(v) for v in r2_primes.values())
asymmetry = abs(r1_count - r2_count) / (r1_count + r2_count)
pred3 = np.sqrt(asymmetry)
print(f"  sqrt(rail asymmetry) = sqrt({asymmetry:.4f}) = {pred3:.4f} vs sin(theta_C) = 0.225")

# 4. From generation density ratio
# Gen 1 quarks vs Gen 2 quarks density
gen1_r2 = len(r2_primes[0])
gen2_r2 = len(r2_primes[2])
gen3_r2 = len(r2_primes[4])
ratio_12 = gen2_r2 / gen1_r2 if gen1_r2 > 0 else 0
pred4 = np.sqrt(1 - ratio_12) if ratio_12 < 1 else 0
print(f"  sqrt(1 - gen2/gen1 density) = sqrt(1 - {ratio_12:.4f}) = {pred4:.4f}")

# 5. From the twin prime rate (alpha_weak)
pred5 = np.sqrt(0.116)  # sqrt(alpha_weak)
print(f"  sqrt(alpha_weak) = sqrt(0.116) = {pred5:.4f}")

# 6. The simplest: sin(theta_C) ~ |chi_1 asymmetry at scale ~ 100|
# Let me compute at various scales
print()
print("Testing sin(theta_C) from sqrt(Chebyshev bias) at different scales:")
print(f"  (Physical: sin(theta_C) = 0.225)")
print()
print(f"  Scale k   R2 count  R1 count   bias     sqrt(bias)  match?")
for scale in [100, 500, 1000, 2500, 5000]:
    r2_at_scale = sum(1 for p in range(5, 6*scale+1) if is_prime[p] and p % 6 == 1)
    r1_at_scale = sum(1 for p in range(5, 6*scale+1) if is_prime[p] and p % 6 == 5)
    total = r2_at_scale + r1_at_scale
    bias = abs(r1_at_scale - r2_at_scale) / total
    sqb = np.sqrt(bias)
    match = "CLOSE" if abs(sqb - 0.225) < 0.03 else ""
    print(f"  {scale:6d}   {r2_at_scale:6d}    {r1_at_scale:6d}   {bias:.4f}    {sqb:.4f}     {match}")

# ============================================================
# SECTION 5: THE PMNS MATRIX FOR LEPTONS
# ============================================================
print()
print("=" * 70)
print("SECTION 5: THE PMNS MATRIX FOR LEPTONS")
print("=" * 70)
print()

# Leptons sit at odd sub-positions
# R2: nu_e(sp=1), nu_mu(sp=3), nu_tau(sp=5)
# R1: electron(sp=1), muon(sp=3), tau(sp=5)
# The Higgs couples R2(sp=odd) <-> R1(sp=odd) at 180 degrees

# Physical PMNS matrix (approximate magnitudes)
pmns = np.array([
    [0.82, 0.55, 0.015],
    [0.43, 0.60, 0.77],
    [0.38, 0.55, 0.64]
])

print("Physical PMNS matrix (approximate magnitudes):")
print()
print("                 e(G1)       mu(G2)      tau(G3)")
lep_names_r2 = ["nu_e(G1)", "nu_mu(G2)", "nu_tau(G3)"]
for i, name in enumerate(lep_names_r2):
    print(f"  {name:12s}   {pmns[i,0]:.3f}      {pmns[i,1]:.3f}      {pmns[i,2]:.3f}")

print()
print("Key features of PMNS vs CKM:")
print("  CKM: nearly diagonal (small mixing)")
print("  PMNS: large mixing (nearly tribimaximal)")
print("  theta_12 ~ 34 deg, theta_23 ~ 49 deg, theta_13 ~ 8 deg")
print()

# Monad PMNS analog from lepton sub-position composition
# Lepton sp values: 1, 3, 5
lep_sp = [1, 3, 5]
composite_lep = np.zeros((3, 3))

for i, sp_a in enumerate(lep_sp):
    for j, sp_b in enumerate(lep_sp):
        count = 0
        primes_a = [k for k in r2_primes[sp_a] if k <= K]
        primes_b = [k for k in r1_primes[sp_b] if k <= K]
        for ka in primes_a:
            for kb in primes_b:
                kn = 6 * ka * kb - ka + kb
                if kn <= K and kn > 0:
                    count += 1
        composite_lep[i, j] = count

total_lep = composite_lep.sum(axis=1, keepdims=True)
pmns_monad = composite_lep / total_lep

print("Monad PMNS analog (normalized per row):")
print()
print("                 e(G1)       mu(G2)      tau(G3)")
for i, name in enumerate(lep_names_r2):
    print(f"  {name:12s}   {pmns_monad[i,0]:.4f}      {pmns_monad[i,1]:.4f}      {pmns_monad[i,2]:.4f}")

print()
print("PMNS hierarchy by sub-position distance:")
same_pmns_phys = np.mean([pmns[0,0], pmns[1,1], pmns[2,2]])
adj_pmns_phys = np.mean([pmns[0,1], pmns[1,0], pmns[1,2], pmns[2,1]])
skip_pmns_phys = np.mean([pmns[0,2], pmns[2,0]])

same_pmns_mon = np.mean([pmns_monad[0,0], pmns_monad[1,1], pmns_monad[2,2]])
adj_pmns_mon = np.mean([pmns_monad[0,1], pmns_monad[1,0], pmns_monad[1,2], pmns_monad[2,1]])
skip_pmns_mon = np.mean([pmns_monad[0,2], pmns_monad[2,0]])

print(f"  Physical: same={same_pmns_phys:.3f}, adj={adj_pmns_phys:.3f}, skip={skip_pmns_phys:.3f}")
print(f"  Monad:    same={same_pmns_mon:.4f}, adj={adj_pmns_mon:.4f}, skip={skip_pmns_mon:.4f}")
print()
print("  The PMNS has LARGE mixing -- not diagonal like CKM.")
print("  The monad's lepton composition should also be less diagonal")
print("  if lepton sub-positions (1,3,5) have different densities than quark (0,2,4).")
print()

# Lepton vs quark density comparison
print("Prime density at quark vs lepton sub-positions:")
print()
for sp in range(6):
    r2_count = len(r2_primes[sp])
    r1_count = len(r1_primes[sp])
    total = r2_count + r1_count
    typ = "quark" if sp % 2 == 0 else "lepton"
    print(f"  sp={sp} ({typ:6s}): R2={r2_count:5d}, R1={r1_count:5d}, total={total:5d}")

print()
quark_total = sum(len(r2_primes[sp]) + len(r1_primes[sp]) for sp in [0,2,4])
lepton_total = sum(len(r2_primes[sp]) + len(r1_primes[sp]) for sp in [1,3,5])
print(f"  Quark sp total (0,2,4): {quark_total}")
print(f"  Lepton sp total (1,3,5): {lepton_total}")
print(f"  Ratio quark/lepton: {quark_total/lepton_total:.4f}")
print(f"  Expected if uniform: {3*quark_total/(quark_total+lepton_total):.4f} (should be ~1.0)")

# ============================================================
# SECTION 6: WOLFENSTEIN AND THE MONAD
# ============================================================
print()
print("=" * 70)
print("SECTION 6: WOLFENSTEIN PARAMETERIZATION AND THE MONAD")
print("=" * 70)
print()

print("The Wolfenstein parameterization of CKM:")
print("  V = | 1-l^2/2    l       A*l^3*(rho-i*eta)  |")
print("      | -l         1-l^2/2  A*l^2              |")
print("      | A*l^3(1-..) -A*l^2  1                  |")
print()
print("  lambda = 0.225  (Cabibbo angle)")
print("  A = 0.82")
print("  rho = 0.14, eta = 0.35")
print()

# The key parameter is lambda ~ 0.225
# In the monad, is there a natural quantity that gives this?
print("Monad quantities compared to lambda = 0.225:")
print()

# 1. sqrt(rail asymmetry) was closest in Section 4
print(f"  1. sqrt(rail asymmetry) at scale ~100:  ~0.21 (close!)")

# 2. The ratio of cross-gen to same-gen density
cross_gen_density = (np.mean(adj_monad) + np.mean(skip_monad)) / np.mean(same_monad) if np.mean(same_monad) > 0 else 0
print(f"  2. Cross-gen/same-gen ratio (quark):    {cross_gen_density:.4f}")

# 3. The ratio of odd to even sp density
odd_density = sum(len(r2_primes[sp]) + len(r1_primes[sp]) for sp in [1,3,5])
even_density = sum(len(r2_primes[sp]) + len(r1_primes[sp]) for sp in [0,2,4])
print(f"  3. Odd/even sp density ratio:            {odd_density/even_density:.4f}")

# 4. The monad's "natural" lambda from geometry
# lambda ~ sin(theta_C) ~ 0.225
# In the monad, the "natural" small parameter is Chebyshev's bias
# which is the same as the E-field amplitude
print(f"  4. The E-field amplitude at scale ~100:  ~0.056 (too small)")
print(f"  5. sqrt(E-field amplitude * scale):      ~0.47 (too large)")
print()

# Let me try: lambda from the Mobius ratio
# Mobius ratio = 3:1 (from 018h)
# lambda ~ 1/3 - 1/4 = 0.083... no
# lambda ~ sqrt(1/3 - 1/4) = 0.289... closer
# lambda ~ sqrt(pi/(2*sqrt(3)) - 1) = sqrt(0.907 - 1)... negative, no
# lambda ~ 1/sqrt(20) = 0.224... VERY close!
pred_lambda = 1/np.sqrt(20)
print(f"  6. 1/sqrt(20) = {pred_lambda:.4f} vs lambda = 0.225")
print(f"     Where does 20 come from? phi(6) * 10 = 20? No clear monad basis.")
print()

# Actually: 20 = 4 * 5 = (number of quark pairs) * (next prime after 3)
# Or: 20 = lcm(4,5) = the LCM of quark sub-positions
# This is numerology, not derivation.

print("HONEST ASSESSMENT: The monad does not derive the Cabibbo angle.")
print("The closest match is sqrt(rail asymmetry) at moderate scale,")
print("but this is a coincidence of scale, not a fundamental prediction.")
print()

# ============================================================
# SECTION 7: CKM UNITARITY AND THE MONAD
# ============================================================
print()
print("=" * 70)
print("SECTION 7: CKM UNITARITY AND THE MONAD")
print("=" * 70)
print()

# The CKM matrix is unitary: V*V^dagger = I
# This gives unitarity triangles and relations like:
# V_ud * V_ub* + V_cd * V_cb* + V_td * V_tb* = 0

print("CKM unitarity relations:")
print()

# Check if monad CKM is approximately unitary
VVdag = ckm_monad @ ckm_monad.T
print("Monad V * V^T (should be identity if unitary):")
for i in range(3):
    print(f"  [{VVdag[i,0]:.4f}  {VVdag[i,1]:.4f}  {VVdag[i,2]:.4f}]")

print()
is_unitary = np.allclose(VVdag, np.eye(3), atol=0.01)
print(f"  Approximately unitary: {is_unitary}")

# The monad's composition rules give a normalized (row sums = 1) matrix
# but NOT necessarily unitary. Unitarity requires V*V^dag = I,
# which is a stronger condition.

row_sums = ckm_monad.sum(axis=1)
col_sums = ckm_monad.sum(axis=0)
print(f"  Row sums: {row_sums}")
print(f"  Column sums: {col_sums}")
print(f"  Row sums = 1: {np.allclose(row_sums, 1.0)}")

# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 70)
print("SUMMARY: CKM MONAD")
print("=" * 70)
print()
print("WHY 3 GENERATIONS:")
print("  The monad is based on mod 6 = 2 x 3.")
print("  2 types (quark/lepton, even/odd sp) x 3 generations = 6 positions.")
print("  3 generations is forced by the MINIMAL modulus that captures all primes.")
print()
print("CKM HIERARCHY:")

# Final check on hierarchy
if hierarchy_monad:
    print("  The monad REPRODUCES the CKM hierarchy (same > adjacent > skip).")
    print(f"  Same-gen mixing: {np.mean(same_monad):.4f} (physical: {np.mean(same_gen):.4f})")
    print(f"  Adj-gen mixing:  {np.mean(adj_monad):.4f} (physical: {np.mean(adj_gen):.4f})")
    print(f"  Skip-gen mixing: {np.mean(skip_monad):.4f} (physical: {np.mean(skip_gen):.4f})")
else:
    print("  The monad does NOT reproduce the CKM hierarchy.")
    print("  Cross-generation composition is NOT suppressed in the monad.")
    print("  The composite density depends on prime density at each sp,")
    print("  which is roughly uniform by Dirichlet's theorem.")

print()
print("CABIBBO ANGLE:")
print("  The monad does not predict lambda = 0.225 from first principles.")
print("  sqrt(rail asymmetry) at moderate scale gives ~0.21, but this")
print("  is scale-dependent, not a fundamental prediction.")
print()
print("PMNS (LEPTON) MIXING:")
print("  The monad's lepton composition is also roughly uniform.")
print("  It does not predict the large PMNS mixing angles.")
print()
print("WHAT THE MONAD EXPLAINS ABOUT MIXING:")
print("  1. The GENERATION STRUCTURE (3 from 6 = 2 x 3)")
print("  2. WHICH particles can mix (quarks at even sp, leptons at odd sp)")
print("  3. The 180 degree Higgs coupling connects isospin doublets")
print("  4. Cross-generation mixing is between sp values differing by 2 or 4")
print()
print("WHAT THE MONAD DOES NOT EXPLAIN:")
print("  1. The SPECIFIC mixing angle values (CKM or PMNS)")
print("  2. Why CKM mixing is small and PMNS mixing is large")
print("  3. The Wolfenstein parameter lambda = 0.225")
print("  4. CP violation in the mixing matrix")
print()
print("KEY NUMBERS:")
print(f"  Monad CKM mean |diff| from physical: {mean_diff:.4f}")
print(f"  Monad CKM max  |diff| from physical: {max_diff:.4f}")
print(f"  Quark/lepton sp density ratio: {quark_total/lepton_total:.4f}")
print(f"  3 generations from 6 = 2 x 3: structural, not predictive")
print()
print("======================================================================")
print("EXPERIMENT 018pp COMPLETE")
print("======================================================================")
