"""
Experiment 018i: The Monad Maps the Fermions
=============================================
12 fundamental fermions mapped onto the 12-position monad.
Testing whether the monad's structure predicts or correlates
with particle physics properties.

12 fermions:
  6 quarks (u,d,c,s,t,b) + 6 leptons (ve,e,vmu,mu,vtau,tau)
  = 3 generations x 4 particles
  = 12 positions on the monad

Key physical properties:
  - Mass (MeV)
  - Electric charge
  - Weak isospin T3 (+1/2 or -1/2)
  - Generation (I, II, III)
  - Color charge (quarks have it, leptons don't)

Monad properties:
  - Position 0-11
  - Rail (R1 or R2)
  - Sub-position sp (0-5)
  - Self-composition frequency (rev/step)
  - Angular position (0-330 degrees)
"""

import numpy as np
from math import log, log10, sqrt, gcd

# ====================================================================
#  FERMION DATA
# ====================================================================

fermions = {
    # Quarks
    'u':   {'name': 'Up',      'type': 'quark',  'charge': 2/3,  'gen': 1, 'T3': +0.5, 'mass_mev': 2.16,     'color': True},
    'd':   {'name': 'Down',    'type': 'quark',  'charge': -1/3, 'gen': 1, 'T3': -0.5, 'mass_mev': 4.67,     'color': True},
    'c':   {'name': 'Charm',   'type': 'quark',  'charge': 2/3,  'gen': 2, 'T3': +0.5, 'mass_mev': 1270.0,   'color': True},
    's':   {'name': 'Strange', 'type': 'quark',  'charge': -1/3, 'gen': 2, 'T3': -0.5, 'mass_mev': 93.0,     'color': True},
    't':   {'name': 'Top',     'type': 'quark',  'charge': 2/3,  'gen': 3, 'T3': +0.5, 'mass_mev': 172520.0, 'color': True},
    'b':   {'name': 'Bottom',  'type': 'quark',  'charge': -1/3, 'gen': 3, 'T3': -0.5, 'mass_mev': 4180.0,   'color': True},
    # Leptons
    've':  {'name': 'nu_e',    'type': 'lepton', 'charge': 0,    'gen': 1, 'T3': +0.5, 'mass_mev': 1e-9,     'color': False},
    'e':   {'name': 'Electron','type': 'lepton', 'charge': -1,   'gen': 1, 'T3': -0.5, 'mass_mev': 0.511,    'color': False},
    'vm':  {'name': 'nu_mu',   'type': 'lepton', 'charge': 0,    'gen': 2, 'T3': +0.5, 'mass_mev': 1e-7,     'color': False},
    'mu':  {'name': 'Muon',    'type': 'lepton', 'charge': -1,   'gen': 2, 'T3': -0.5, 'mass_mev': 105.66,   'color': False},
    'vt':  {'name': 'nu_tau',  'type': 'lepton', 'charge': 0,    'gen': 3, 'T3': +0.5, 'mass_mev': 1e-5,     'color': False},
    'tau': {'name': 'Tau',     'type': 'lepton', 'charge': -1,   'gen': 3, 'T3': -0.5, 'mass_mev': 1776.86,  'color': False},
}

# Monad functions
def compose_12(pos_a, pos_b):
    rail_a = -1 if pos_a < 6 else +1
    sp_a = pos_a % 6
    rail_b = -1 if pos_b < 6 else +1
    sp_b = pos_b % 6
    if rail_a == -1 and rail_b == -1:
        sp_out = (-sp_a - sp_b) % 6; rail_out = +1
    elif rail_a == +1 and rail_b == +1:
        sp_out = (sp_a + sp_b) % 6; rail_out = +1
    else:
        if rail_a == -1: sp_out = (sp_a - sp_b) % 6
        else: sp_out = (sp_b - sp_a) % 6
        rail_out = -1
    return sp_out if rail_out == -1 else sp_out + 6

def self_comp_freq(pos):
    orbit = [pos]
    p = pos
    for _ in range(24):
        p = compose_12(p, pos)
        orbit.append(p)
        if p == pos: break
    period = len(orbit) - 1
    if period == 0: return 0.0
    # Positive angular sweep
    total = 0
    for i in range(period):
        diff = (orbit[i+1] - orbit[i]) * 30.0
        if diff < 0: diff += 360
        total += diff
    return total / (360.0 * period)

# ====================================================================
#  MAPPING SCHEMES
# ====================================================================

print("=" * 70)
print("  EXPERIMENT 018i: THE MONAD MAPS THE FERMIONS")
print("=" * 70)
print()

# Scheme A: T3=+1/2 on R1, T3=-1/2 on R2, sp = generation-based
# This is the MOST natural mapping: Z2 rail = weak isospin
# Within each rail: even sp = quark, odd sp = lepton (alternating by gen)
scheme_a = {
    0: 'u',   # R1, sp=0: up quark (Gen I, T3=+1/2, quark)
    1: 've',  # R1, sp=1: electron neutrino (Gen I, T3=+1/2, lepton)
    2: 'c',   # R1, sp=2: charm quark (Gen II, T3=+1/2, quark)
    3: 'vm',  # R1, sp=3: muon neutrino (Gen II, T3=+1/2, lepton)
    4: 't',   # R1, sp=4: top quark (Gen III, T3=+1/2, quark)
    5: 'vt',  # R1, sp=5: tau neutrino (Gen III, T3=+1/2, lepton)
    6: 'd',   # R2, sp=0: down quark (Gen I, T3=-1/2, quark)
    7: 'e',   # R2, sp=1: electron (Gen I, T3=-1/2, lepton)
    8: 's',   # R2, sp=2: strange quark (Gen II, T3=-1/2, quark)
    9: 'mu',  # R2, sp=3: muon (Gen II, T3=-1/2, lepton)
   10: 'b',   # R2, sp=4: bottom quark (Gen III, T3=-1/2, quark)
   11: 'tau', # R2, sp=5: tau (Gen III, T3=-1/2, lepton)
}

# Scheme B: Quarks on R1, Leptons on R2
scheme_b = {
    0: 'u',   1: 'd',   2: 'c',   3: 's',   4: 't',   5: 'b',
    6: 've',  7: 'e',   8: 'vm',  9: 'mu',  10: 'vt', 11: 'tau',
}

# Scheme C: Up-type quarks and neutrinos on R1; Down-type quarks and charged leptons on R2
# Ordered by generation within each group
scheme_c = {
    0: 'u',   # Gen I up-type
    1: 'd',   # Gen I down-type
    2: 'c',   # Gen II up-type
    3: 's',   # Gen II down-type
    4: 't',   # Gen III up-type
    5: 'b',   # Gen III down-type
    6: 've',  # Gen I neutrino
    7: 'e',   # Gen I charged
    8: 'vm',  # Gen II neutrino
    9: 'mu',  # Gen II charged
   10: 'vt',  # Gen III neutrino
   11: 'tau', # Gen III charged
}

# ====================================================================
#  TEST 1: SCHEME A — WEAK ISOSPIN MAPPING
# ====================================================================
print("=" * 70)
print("  SCHEME A: T3=+1/2 -> R1, T3=-1/2 -> R2 (WEAK ISOSPIN)")
print("=" * 70)
print()
print("  This is the most natural mapping: Z2 rail = weak isospin")
print("  R1 = T3=+1/2 (u, c, t, ve, vmu, vtau)")
print("  R2 = T3=-1/2 (d, s, b, e, mu, tau)")
print("  Within each rail: even sp = quark, odd sp = lepton")
print()

scheme = scheme_a

print(f"  {'pos':>3} {'rail':>4} {'sp':>3} {'angle':>6} {'freq':>5} {'particle':>10} {'Q':>5} {'T3':>5} {'gen':>4} {'mass(MeV)':>10} {'attractor':>9}")
print("  " + "-" * 85)

for pos in range(12):
    f = scheme[pos]
    p = fermions[f]
    rail = "R1" if pos < 6 else "R2"
    sp = pos % 6
    angle = pos * 30
    freq = self_comp_freq(pos)
    is_attr = "***YES***" if pos in [0, 3, 6, 9] else ""

    print(f"  {pos:>3} {rail:>4} {sp:>3} {angle:>4}deg {freq:>5.3f} {p['name']:>10} "
          f"{p['charge']:>+5.2f} {p['T3']:>+4.1f} {p['gen']:>4} {p['mass_mev']:>10.3f} {is_attr:>9}")

print()

# ====================================================================
#  TEST 2: RAIL = WEAK ISOSPIN CORRELATION
# ====================================================================
print("=" * 70)
print("  TEST 2: RAIL/ISOSPIN ALIGNMENT CHECK")
print("=" * 70)
print()

# Check: do all R1 particles have T3=+1/2 and all R2 have T3=-1/2?
isospin_match = 0
for pos in range(12):
    f = scheme[pos]
    p = fermions[f]
    rail = -1 if pos < 6 else +1
    if (rail == -1 and p['T3'] == +0.5) or (rail == +1 and p['T3'] == -0.5):
        isospin_match += 1

print(f"  T3 matches rail assignment: {isospin_match}/12 ({100*isospin_match/12:.0f}%)")
print()

# Check: sp = generation encoding
gen_match = 0
for pos in range(12):
    f = scheme[pos]
    p = fermions[f]
    sp = pos % 6
    expected_gen = (sp // 2) + 1 if pos < 6 else (sp // 2) + 1
    if p['gen'] == expected_gen:
        gen_match += 1

print(f"  Generation matches sp//2+1: {gen_match}/12 ({100*gen_match/12:.0f}%)")
print()

# Check: even sp = quark, odd sp = lepton
type_match = 0
for pos in range(12):
    f = scheme[pos]
    p = fermions[f]
    sp = pos % 6
    if (sp % 2 == 0 and p['type'] == 'quark') or (sp % 2 == 1 and p['type'] == 'lepton'):
        type_match += 1

print(f"  Quark/lepton matches even/odd sp: {type_match}/12 ({100*type_match/12:.0f}%)")
print()

# ====================================================================
#  TEST 3: THE FOUR ATTRACTORS
# ====================================================================
print("=" * 70)
print("  TEST 3: THE FOUR ATTRACTORS (positions 0, 3, 6, 9)")
print("=" * 70)
print()
print("  The monad has 4 attractor positions at 0, 90, 180, 270 degrees.")
print("  Russell's four positions: seed(0), compression(90), reversal(180), radiation(270)")
print()

attractors = {0: 'seed', 3: 'compression', 6: 'reversal', 9: 'radiation'}
for pos, label in attractors.items():
    f = scheme[pos]
    p = fermions[f]
    rail = "R1" if pos < 6 else "R2"
    print(f"  {pos:>2} ({pos*30}deg) = {label:>11}: {p['name']:>10} "
          f"(Q={p['charge']:+.2f}, T3={p['T3']:+.1f}, gen={p['gen']}, "
          f"mass={p['mass_mev']:.3f} MeV)")

print()

# Special significance of each attractor particle
print("  Physical significance:")
print("    Up quark (0deg):     Most abundant quark in the universe. Proton = uud.")
print("    Muon neutrino (90deg): First detected neutrino flavor (1962).")
print("    Down quark (180deg): Partner of up quark. Neutron = udd.")
print("    Muon (270deg):      First discovered 'second generation' particle.")
print()

# ====================================================================
#  TEST 4: MASS RATIOS VS MONAD FREQUENCIES
# ====================================================================
print("=" * 70)
print("  TEST 4: MASS RATIOS vs MONAD STRUCTURE")
print("=" * 70)
print()

# Within each rail, compare mass ratios
print("  R1 particles (T3=+1/2):")
print(f"  {'particle':>10} {'pos':>3} {'sp':>3} {'freq':>6} {'mass':>12} {'log(mass)':>10}")
for pos in range(6):
    f = scheme[pos]
    p = fermions[f]
    freq = self_comp_freq(pos)
    lm = log(p['mass_mev']) if p['mass_mev'] > 0 else -999
    print(f"  {p['name']:>10} {pos:>3} {pos%6:>3} {freq:>6.3f} {p['mass_mev']:>12.3f} {lm:>10.2f}")

print()
print("  R2 particles (T3=-1/2):")
print(f"  {'particle':>10} {'pos':>3} {'sp':>3} {'freq':>6} {'mass':>12} {'log(mass)':>10}")
for pos in range(6, 12):
    f = scheme[pos]
    p = fermions[f]
    freq = self_comp_freq(pos)
    lm = log(p['mass_mev']) if p['mass_mev'] > 0 else -999
    print(f"  {p['name']:>10} {pos:>3} {pos%6:>3} {freq:>6.3f} {p['mass_mev']:>12.3f} {lm:>10.2f}")

print()

# Key mass ratios
print("  Key mass ratios compared to monad ratios:")
print()

key_ratios = [
    ("m_d / m_u", 4.67 / 2.16, "R2(sp=0) / R1(sp=0)", "cross-rail, same gen"),
    ("m_e / m_u", 0.511 / 2.16, "R2(sp=1) / R1(sp=0)", "cross-rail, same gen"),
    ("m_c / m_s", 1270.0 / 93.0, "R1(sp=2) / R2(sp=2)", "cross-rail, same gen"),
    ("m_mu / m_s", 105.66 / 93.0, "R2(sp=3) / R2(sp=2)", "same rail, same gen"),
    ("m_t / m_b", 172520.0 / 4180.0, "R1(sp=4) / R2(sp=4)", "cross-rail, same gen"),
    ("m_tau / m_b", 1776.86 / 4180.0, "R2(sp=5) / R2(sp=4)", "same rail, same gen"),
    ("m_c / m_u", 1270.0 / 2.16, "R1(sp=2) / R1(sp=0)", "same rail, Gen II/I"),
    ("m_t / m_c", 172520.0 / 1270.0, "R1(sp=4) / R1(sp=2)", "same rail, Gen III/II"),
    ("m_b / m_d", 4180.0 / 4.67, "R2(sp=4) / R2(sp=0)", "same rail, Gen III/I"),
    ("m_mu / m_e", 105.66 / 0.511, "R2(sp=3) / R2(sp=1)", "same rail, Gen II/I"),
    ("m_tau / m_mu", 1776.86 / 105.66, "R2(sp=5) / R2(sp=3)", "same rail, Gen III/II"),
]

print(f"  {'ratio':>15} {'value':>12} {'monad mapping':>25} {'notes':>30}")
print("  " + "-" * 90)
for name, val, monad, notes in key_ratios:
    print(f"  {name:>15} {val:>12.3f} {monad:>25} {notes:>30}")

print()

# ====================================================================
#  TEST 5: WEAK INTERACTION AS MONAD COMPOSITION
# ====================================================================
print("=" * 70)
print("  TEST 5: WEAK INTERACTION AS MONAD COMPOSITION")
print("=" * 70)
print()
print("  The weak force couples T3=+1/2 (R1) and T3=-1/2 (R2) particles.")
print("  In the monad: R1 x R2 -> R1 (heterodyne).")
print("  This means: composing a weak doublet returns to the R1 sector.")
print()
print("  Weak doublet partners (same generation, opposite T3):")
print()

for gen in range(1, 4):
    # Find the R1 and R2 particles for this generation
    r1_particles = [(pos, scheme[pos]) for pos in range(6) if fermions[scheme[pos]]['gen'] == gen]
    r2_particles = [(pos, scheme[pos]) for pos in range(6, 12) if fermions[scheme[pos]]['gen'] == gen]

    print(f"  Generation {gen}:")
    for r1_pos, r1_key in r1_particles:
        r1_name = fermions[r1_key]['name']
        for r2_pos, r2_key in r2_particles:
            r2_name = fermions[r2_key]['name']
            result_pos = compose_12(r1_pos, r2_pos)
            result_key = scheme[result_pos]
            result_name = fermions[result_key]['name']

            sp_r1 = r1_pos % 6
            sp_r2 = r2_pos % 6
            sp_result = result_pos % 6
            rail_result = "R1" if result_pos < 6 else "R2"

            print(f"    {r1_name:>10}(R1,sp={sp_r1}) x {r2_name:>10}(R2,sp={sp_r2}) "
                  f"-> {result_name:>10}({rail_result},sp={sp_result})  "
                  f"[sp = ({sp_r1}-{sp_r2})%6 = {sp_result}]")
    print()

# ====================================================================
#  TEST 6: KOIDE'S FORMULA AND THE MONAD
# ====================================================================
print("=" * 70)
print("  TEST 6: KOIDE'S FORMULA AND THE MONAD")
print("=" * 70)
print()
print("  Koide's formula: (m1+m2+m3)/(sqrt(m1)+sqrt(m2)+sqrt(m3))^2 = 2/3")
print("  2/3 = up-quark charge = the R2(sp=4) frequency ratio!")
print()

# Charged leptons are at positions 7(e), 9(mu), 11(tau) in Scheme A
me = 0.511
mmu = 105.66
mtau = 1776.86

koide = (me + mmu + mtau) / (sqrt(me) + sqrt(mmu) + sqrt(mtau))**2
print(f"  Koide value for (e, mu, tau): {koide:.6f}")
print(f"  Exact 2/3:                    {2/3:.6f}")
print(f"  Deviation:                     {abs(koide - 2/3):.6f}")
print()

# Their monad positions: 7, 9, 11 (R2, sp=1,3,5 — all odd)
# Their frequencies: 1/6, 1/2, 5/6
# Average frequency: (1/6 + 1/2 + 5/6) / 3 = (1+3+5)/(6*3) = 9/18 = 1/2
avg_freq = (1/6 + 1/2 + 5/6) / 3
print(f"  Average monad frequency of (e, mu, tau): {avg_freq:.4f}")
print(f"  These are the three ODD sp positions on R2: 1, 3, 5")
print(f"  Their sp values form an arithmetic progression: 1, 3, 5")
print(f"  Average sp = 3 = the tritone position (90deg/270deg)")
print()

# Check Koide-like formulas for quark triplets
print("  Koide-like check for quark triplets:")
for label, keys in [("up-type (u,c,t)", ['u','c','t']), ("down-type (d,s,b)", ['d','s','b'])]:
    masses = [fermions[k]['mass_mev'] for k in keys]
    if all(m > 0 for m in masses):
        koide_val = sum(masses) / sum(sqrt(m) for m in masses)**2
        print(f"    {label}: Koide = {koide_val:.6f}")

print()

# ====================================================================
#  TEST 7: CHARGE PATTERN IN THE MONAD
# ====================================================================
print("=" * 70)
print("  TEST 7: ELECTRIC CHARGE PATTERN")
print("=" * 70)
print()

print("  Charge distribution on the monad (Scheme A):")
print()

for pos in range(12):
    f = scheme[pos]
    p = fermions[f]
    rail = "R1" if pos < 6 else "R2"
    sp = pos % 6
    angle = pos * 30

    # Visual charge bar
    if p['charge'] > 0:
        bar = "+" * int(p['charge'] * 10)
    elif p['charge'] < 0:
        bar = "-" * int(abs(p['charge']) * 10)
    else:
        bar = "0"

    print(f"  pos {pos:>2} ({rail},sp={sp}, {angle:>3}deg): "
          f"{p['name']:>10} Q={p['charge']:>+5.2f}  {bar}")

print()

# Check: charge sum by rail
r1_charge = sum(fermions[scheme[pos]]['charge'] for pos in range(6))
r2_charge = sum(fermions[scheme[pos]]['charge'] for pos in range(6, 12))
print(f"  R1 charge sum: {r1_charge:+.2f}")
print(f"  R2 charge sum: {r2_charge:+.2f}")
print(f"  Total charge:  {r1_charge + r2_charge:+.2f}")
print()

# Charge by sp pair (generation pairs)
for sp_base in range(0, 6, 2):
    charges = []
    particles = []
    for sp in [sp_base, sp_base + 1]:
        for rail_offset in [0, 6]:
            pos = rail_offset + sp
            f = scheme[pos]
            p = fermions[f]
            charges.append(p['charge'])
            particles.append(f"{p['name']}(Q={p['charge']:+.2f})")

    gen = sp_base // 2 + 1
    total = sum(charges)
    print(f"  Gen {gen} (sp {sp_base},{sp_base+1}): "
          f"{', '.join(particles)} = total Q = {total:+.2f}")

print()

# ====================================================================
#  TEST 8: GENERATION STRUCTURE IN SP-SPACE
# ====================================================================
print("=" * 70)
print("  TEST 8: GENERATION STRUCTURE")
print("=" * 70)
print()
print("  Within each rail, sp pairs encode generations:")
print("  Gen I:  sp=0 (quark), sp=1 (lepton)")
print("  Gen II: sp=2 (quark), sp=3 (lepton)")
print("  Gen III: sp=4 (quark), sp=5 (lepton)")
print()

for gen in range(1, 4):
    sp_base = (gen - 1) * 2
    print(f"  Generation {gen}:")

    # R1 (T3=+1/2)
    for sp in [sp_base, sp_base + 1]:
        pos = sp  # R1
        f = scheme[pos]
        p = fermions[f]
        freq = self_comp_freq(pos)
        print(f"    R1 sp={sp}: {p['name']:>10} (Q={p['charge']:+.2f}, "
              f"mass={p['mass_mev']:.3f} MeV, freq={freq:.3f})")

    # R2 (T3=-1/2)
    for sp in [sp_base, sp_base + 1]:
        pos = sp + 6  # R2
        f = scheme[pos]
        p = fermions[f]
        freq = self_comp_freq(pos)
        print(f"    R2 sp={sp}: {p['name']:>10} (Q={p['charge']:+.2f}, "
              f"mass={p['mass_mev']:.3f} MeV, freq={freq:.3f})")

    # Mass ratios within generation
    r1_quark = fermions[scheme[sp_base]]
    r2_quark = fermions[scheme[sp_base + 6]]
    r1_lep = fermions[scheme[sp_base + 1]]
    r2_lep = fermions[scheme[sp_base + 7]]

    if r2_quark['mass_mev'] > 0 and r1_quark['mass_mev'] > 0:
        ratio = r1_quark['mass_mev'] / r2_quark['mass_mev']
        print(f"    Quark mass ratio (up/down-type): {r1_quark['name']}/{r2_quark['name']} = {ratio:.3f}")

    if r2_lep['mass_mev'] > 0 and r1_lep['mass_mev'] > 1e-15:
        ratio = r1_lep['mass_mev'] / r2_lep['mass_mev']
        print(f"    Lepton mass ratio (neutrino/charged): {r1_lep['name']}/{r2_lep['name']} = {ratio:.2e}")

    print()

# ====================================================================
#  TEST 9: COMPOSITION TABLE AS INTERACTION MAP
# ====================================================================
print("=" * 70)
print("  TEST 9: COMPOSITION TABLE AS INTERACTION MAP")
print("=" * 70)
print()
print("  Monad composition rules as particle interaction patterns:")
print()
print("  R1 x R1 -> R2 (destructive):  T3=+1/2 x T3=+1/2 -> T3=-1/2 sector")
print("  R2 x R2 -> R2 (constructive):  T3=-1/2 x T3=-1/2 -> T3=-1/2 sector")
print("  R1 x R2 -> R1 (heterodyne):    T3=+1/2 x T3=-1/2 -> T3=+1/2 sector")
print()

# Specific interactions
print("  Notable compositions:")
print()

# Weak doublet compositions
print("  Weak doublet self-annihilation (quark x lepton within same gen):")
for gen in range(1, 4):
    sp_base = (gen - 1) * 2
    # Quark R1 x Lepton R2 (same gen, different type)
    q_pos = sp_base  # R1 quark
    l_pos = sp_base + 1 + 6  # R2 lepton
    result = compose_12(q_pos, l_pos)
    q_name = fermions[scheme[q_pos]]['name']
    l_name = fermions[scheme[l_pos]]['name']
    r_name = fermions[scheme[result]]['name']
    r_rail = "R1" if result < 6 else "R2"
    print(f"    {q_name} x {l_name} -> {r_name} ({r_rail},sp={result%6})")

print()

# Cross-generation compositions
print("  Cross-generation compositions (potential CKM/PMNS mixing):")
ckm_pairs = [
    (0, 8, "u x s"),   # u(0) x s(8)
    (2, 6, "c x d"),   # c(2) x d(6)
    (4, 10, "t x b"),  # t(4) x b(10)
    (0, 6, "u x d"),   # u(0) x d(6) — same gen
    (2, 8, "c x s"),   # c(2) x s(8) — same gen
]
for a, b, label in ckm_pairs:
    result = compose_12(a, b)
    a_name = fermions[scheme[a]]['name']
    b_name = fermions[scheme[b]]['name']
    r_name = fermions[scheme[result]]['name']
    r_rail = "R1" if result < 6 else "R2"
    print(f"    {label:>8} -> {r_name} ({r_rail},sp={result%6})")

print()

# ====================================================================
#  TEST 10: LOG-MASS VS MONAD ANGULAR POSITION
# ====================================================================
print("=" * 70)
print("  TEST 10: LOG-MASS vs ANGULAR POSITION")
print("=" * 70)
print()

# For particles with meaningful masses (> 0.01 MeV), check log-mass vs angle
print(f"  {'particle':>10} {'pos':>3} {'angle':>6} {'log10(mass)':>12} {'freq':>6}")
print("  " + "-" * 45)

massive = []
for pos in range(12):
    f = scheme[pos]
    p = fermions[f]
    if p['mass_mev'] > 0.01:
        lm = log10(p['mass_mev'])
        freq = self_comp_freq(pos)
        massive.append((pos, p['name'], pos * 30, lm, freq))
        print(f"  {p['name']:>10} {pos:>3} {pos*30:>4}deg {lm:>12.2f} {freq:>6.3f}")

print()

# Check correlation between log-mass and frequency for massive R2 particles
r2_massive = [(pos, lm, freq) for pos, name, angle, lm, freq in massive if pos >= 6]
if len(r2_massive) >= 3:
    from math import log10
    log_masses = [lm for _, lm, _ in r2_massive]
    freqs = [freq for _, _, freq in r2_massive]
    if len(set(freqs)) > 1:
        # Pearson correlation
        n = len(log_masses)
        mean_x = sum(log_masses) / n
        mean_y = sum(freqs) / n
        cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_masses, freqs))
        std_x = sqrt(sum((x - mean_x)**2 for x in log_masses))
        std_y = sqrt(sum((y - mean_y)**2 for y in freqs))
        if std_x > 0 and std_y > 0:
            r = cov / (std_x * std_y)
            print(f"  R2 log-mass vs frequency correlation: r = {r:.3f}")

print()

# ====================================================================
#  TEST 11: COMPARING ALL THREE SCHEMES
# ====================================================================
print("=" * 70)
print("  TEST 11: COMPARING MAPPING SCHEMES")
print("=" * 70)
print()

def score_mapping(scheme, label):
    """Score a mapping on several physical consistency checks."""
    score = 0
    max_score = 0

    # 1. Rail should separate by some physical binary
    # Check T3 alignment
    t3_match = sum(1 for pos in range(12)
                   if (pos < 6 and fermions[scheme[pos]]['T3'] == +0.5) or
                      (pos >= 6 and fermions[scheme[pos]]['T3'] == -0.5))
    score += t3_match
    max_score += 12

    # 2. Generation structure in sp
    gen_match = sum(1 for pos in range(12)
                   if fermions[scheme[pos]]['gen'] == (pos % 6) // 2 + 1)
    score += gen_match
    max_score += 12

    # 3. Type consistency (quarks/leptons grouped)
    # Check if quarks are on same rail or same sp-parity
    quark_sp = [pos % 6 for pos in range(12) if fermions[scheme[pos]]['type'] == 'quark']
    lepton_sp = [pos % 6 for pos in range(12) if fermions[scheme[pos]]['type'] == 'lepton']
    # All quarks have same parity?
    quark_parity = [sp % 2 for sp in quark_sp]
    if len(set(quark_parity)) == 1:
        score += 6
    max_score += 6

    # 4. Charge ordering within rails
    # Check if charge increases/decreases monotonically with sp within each rail
    for rail_start in [0, 6]:
        charges = [fermions[scheme[rail_start + sp]]['charge'] for sp in range(6)]
        if all(charges[i] >= charges[i+1] for i in range(5)):
            score += 3
        elif all(charges[i] <= charges[i+1] for i in range(5)):
            score += 3
        max_score += 3

    return score, max_score

for scheme_map, label in [(scheme_a, "A: T3=+1/2->R1"),
                           (scheme_b, "B: Quarks->R1"),
                           (scheme_c, "C: Quarks->R1 by gen")]:
    score, max_score = score_mapping(scheme_map, label)
    print(f"  Scheme {label}: {score}/{max_score} ({100*score/max_score:.0f}%)")

print()

# ====================================================================
#  SUMMARY
# ====================================================================
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print("  SCHEME A (T3=+1/2 -> R1, T3=-1/2 -> R2) is the most natural mapping:")
print()
print("  PERFECT ALIGNMENTS:")
print("  - Rail = Weak isospin T3 (12/12 match)")
print("  - Generation = sp//2 + 1 (12/12 match)")
print("  - Quark/lepton = even/odd sp (12/12 match)")
print()
print("  THE Z2 RAIL RULE = WEAK ISOSPIN CONSERVATION:")
print("  - R1(T3=+1/2) x R2(T3=-1/2) -> R1(T3=+1/2) [heterodyne = weak coupling]")
print("  - R1 x R1 -> R2 [destructive = no same-T3 scattering to same sector]")
print("  - R2 x R2 -> R2 [constructive = same-T3 products stay in T3=-1/2]")
print()
print("  FOUR ATTRACTORS:")
print("  - 0deg (Up quark):      most abundant matter in universe")
print("  - 90deg (mu neutrino):   first detected beyond Gen I")
print("  - 180deg (Down quark):   neutron component, R2 fixed point")
print("  - 270deg (Muon):         first 2nd-gen particle discovered")
print()
print("  KOIDE'S 2/3:")
print("  - Charged leptons are at R2 odd sp (1,3,5)")
print("  - Their monad frequencies: 1/6, 1/2, 5/6")
print("  - Average: 1/2")
print("  - Koide formula gives 2/3 for (e, mu, tau)")
print("  - 2/3 is the up-quark charge AND the sp=4 R2 frequency")
print()
print("Done.")
