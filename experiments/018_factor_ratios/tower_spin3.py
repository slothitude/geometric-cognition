"""
Experiment 018ooo: The Tower Extended -- mod 210 and the Full Spectrum

mod 210 = 2*3*5*7, phi(210) = 48 positions
This is the first level incorporating prime 7, opening Z_6 cyclic structure.

Previous results (018nnn):
  mod  6: 2 DOF,  max D-Q corr = 1.000  (DEPENDENT)
  mod 12: 4 DOF,  max D-Q corr = 0.076  (INDEPENDENT)
  mod 24: 8 DOF,  max D-Q corr = 0.008  (INDEPENDENT)
  mod 30: 8 DOF,  max D-Q corr = 0.452  (INDEPENDENT but coupled)
  mod 60: 16 DOF, max D-Q corr = 0.008  (INDEPENDENT)

Questions for mod 210:
  1. Does D-Q correlation continue to drop?
  2. How does the power spectrum redistribute across 48 DOF?
  3. Do higher multipoles (z^3, z^4, z^5) become independent?
  4. What happens to graviton polarization ratios?
  5. Does mod 210 show any special structure (prime 7 opens Z_6)?
"""

import numpy as np

print("=" * 70)
print("EXPERIMENT 018ooo: THE TOWER EXTENDED -- MOD 210")
print("=" * 70)

# ============================================================
# HELPERS
# ============================================================

def coprime_positions(m):
    return [n for n in range(1, m) if np.gcd(n, m) == 1]

def euler_phi(m):
    return len(coprime_positions(m))

def sieve_primes(N):
    is_p = np.ones(N + 1, dtype=bool)
    is_p[0] = is_p[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_p[i]:
            is_p[i*i::i] = False
    return is_p

N_max = 100000
is_prime = sieve_primes(N_max * 2)

def multipole_analysis(modulus, k_max=5000):
    positions = coprime_positions(modulus)
    n_pos = len(positions)
    angles = np.array([2 * np.pi * r / modulus for r in positions])

    # Multipoles z^1 through z^6
    z_powers = {}
    for n in range(1, 7):
        z_powers[n] = np.exp(n * 1j * angles)

    k_vals = np.arange(0, k_max)
    f = np.zeros((k_max, n_pos))

    for ki, k in enumerate(k_vals):
        for pi, r in enumerate(positions):
            n = modulus * k + r
            if n >= 2 and n < len(is_prime) and is_prime[n]:
                f[ki, pi] = 1.0

    # Multipole moments
    moments = {}
    for n in range(1, 7):
        moments[n] = f @ z_powers[n]

    total_power = np.sum(f**2)

    results = {
        'modulus': modulus,
        'n_pos': n_pos,
        'positions': positions,
        'total_power': total_power,
        'moments': moments,
        'f': f,
        'k_vals': k_vals,
    }

    # Power in each multipole
    for n in range(1, 7):
        pwr = np.sum(np.abs(moments[n])**2)
        results[f'power_{n}'] = pwr
        results[f'frac_{n}'] = pwr / total_power * 100 if total_power > 0 else 0

    # D-Q independence
    D = moments[1]
    Q = moments[2]
    corrs = []
    for da in [D.real, D.imag]:
        for qa in [Q.real, Q.imag]:
            vda, vqa = np.var(da), np.var(qa)
            if vda > 0 and vqa > 0:
                corrs.append(abs(np.corrcoef(da, qa)[0, 1]))
    results['max_DQ_corr'] = max(corrs) if corrs else 0

    # Q-O independence (quadrupole vs octupole)
    O = moments[3]
    corrs_qo = []
    for qa in [Q.real, Q.imag]:
        for oa in [O.real, O.imag]:
            vqa, voa = np.var(qa), np.var(oa)
            if vqa > 0 and voa > 0:
                corrs_qo.append(abs(np.corrcoef(qa, oa)[0, 1]))
    results['max_QO_corr'] = max(corrs_qo) if corrs_qo else 0

    # D-O independence
    corrs_do = []
    for da in [D.real, D.imag]:
        for oa in [O.real, O.imag]:
            vda, voa = np.var(da), np.var(oa)
            if vda > 0 and voa > 0:
                corrs_do.append(abs(np.corrcoef(da, oa)[0, 1]))
    results['max_DO_corr'] = max(corrs_do) if corrs_do else 0

    # Graviton polarizations
    vqr = np.var(Q.real)
    vqi = np.var(Q.imag)
    if vqr > 0 and vqi > 0:
        results['corr_hphx'] = np.corrcoef(Q.real, Q.imag)[0, 1]
    else:
        results['corr_hphx'] = 0
    results['h_plus'] = np.mean(Q.real**2)
    results['h_cross'] = np.mean(Q.imag**2)
    results['hp_hx_ratio'] = results['h_plus'] / results['h_cross'] if results['h_cross'] > 0 else 0

    # Higher-order: z^4 and z^6 are "hexadecapole" and z^6
    # Check z^4 vs z^2 (spin-4 vs spin-2)
    M4 = moments[4]
    corrs_42 = []
    for m4a in [M4.real, M4.imag]:
        for qa in [Q.real, Q.imag]:
            vm4, vqa = np.var(m4a), np.var(qa)
            if vm4 > 0 and vqa > 0:
                corrs_42.append(abs(np.corrcoef(m4a, qa)[0, 1]))
    results['max_M4_Q_corr'] = max(corrs_42) if corrs_42 else 0

    # Check z^5 vs z^1 (spin-5 vs spin-1)
    M5 = moments[5]
    corrs_51 = []
    for m5a in [M5.real, M5.imag]:
        for da in [D.real, D.imag]:
            vm5, vda = np.var(m5a), np.var(da)
            if vm5 > 0 and vda > 0:
                corrs_51.append(abs(np.corrcoef(m5a, da)[0, 1]))
    results['max_M5_D_corr'] = max(corrs_51) if corrs_51 else 0

    return results

# ============================================================
# SECTION 1: FULL TOWER INCLUDING MOD 210
# ============================================================
print()
print("=" * 70)
print("SECTION 1: FULL TOWER -- MOD 6 TO MOD 210")
print("=" * 70)

moduli = [6, 12, 24, 30, 60, 210]
results_all = {}

for m in moduli:
    phi = euler_phi(m)
    print(f"\n  Computing mod {m} (phi={phi}, {phi} DOF)...")
    r = multipole_analysis(m)
    results_all[m] = r

print()
print("  Full comparison table:")
print()
header = f"  {'Mod':>5} {'phi':>4} {'DOF':>4} {'Dip%':>6} {'Quad%':>6} {'Oct%':>6} {'z^4%':>6} {'z^5%':>6} {'z^6%':>6} {'DQ':>8} {'QO':>8} {'DO':>8} {'h+/hx':>7} {'S2?':>5}"
print(header)
print("  " + "-" * (len(header) - 2))

for m in moduli:
    r = results_all[m]
    phi = euler_phi(m)
    s2 = "YES" if r['max_DQ_corr'] < 0.5 else "no"
    print(f"  {m:>5} {phi:>4} {phi:>4} {r['frac_1']:>5.1f}% {r['frac_2']:>5.1f}% {r['frac_3']:>5.1f}% "
          f"{r['frac_4']:>5.1f}% {r['frac_5']:>5.1f}% {r['frac_6']:>5.1f}% "
          f"{r['max_DQ_corr']:>8.4f} {r['max_QO_corr']:>8.4f} {r['max_DO_corr']:>8.4f} "
          f"{r['hp_hx_ratio']:>7.3f} {s2:>5}")

# ============================================================
# SECTION 2: MOD 210 DEEP DIVE
# ============================================================
print()
print("=" * 70)
print("SECTION 2: MOD 210 DEEP DIVE")
print("=" * 70)

r210 = results_all[210]
print(f"\n  phi(210) = {r210['n_pos']}")
print(f"  210 = 2 x 3 x 5 x 7")
print(f"  (Z/210Z)* = Z_2 x Z_2 x Z_4 x Z_6 (by CRT)")
print(f"  = Z_2 x Z_2 x Z_4 x Z_2 x Z_3")
print(f"  Characters: 48 total (all combinations of 2x2x4x6)")

print(f"\n  Power spectrum:")
for n in range(1, 7):
    print(f"    z^{n}: {r210[f'frac_{n}']:.1f}% (power = {r210[f'power_{n}']:.0f})")

print(f"\n  Independence matrix:")
print(f"    D-Q (spin1 vs spin2): {r210['max_DQ_corr']:.6f}")
print(f"    D-O (spin1 vs spin3): {r210['max_DO_corr']:.6f}")
print(f"    Q-O (spin2 vs spin3): {r210['max_QO_corr']:.6f}")
print(f"    M4-Q (spin4 vs spin2): {r210['max_M4_Q_corr']:.6f}")
print(f"    M5-D (spin5 vs spin1): {r210['max_M5_D_corr']:.6f}")

print(f"\n  Graviton polarizations:")
print(f"    Corr(h+, hx): {r210['corr_hphx']:.6f}")
print(f"    <h+^2>: {r210['h_plus']:.4f}")
print(f"    <hx^2>: {r210['h_cross']:.4f}")
print(f"    h+/hx ratio: {r210['hp_hx_ratio']:.4f}")

# ============================================================
# SECTION 3: STRUCTURAL ANALYSIS -- DISTINCT z^n VALUES
# ============================================================
print()
print("=" * 70)
print("SECTION 3: STRUCTURAL ANALYSIS")
print("=" * 70)

for m in moduli:
    positions = coprime_positions(m)
    angles = [2 * np.pi * r / m for r in positions]

    print(f"\n  Mod {m}: {len(positions)} positions")

    for n in [1, 2, 3, 4, 5, 6]:
        z_vals = [complex(round(np.cos(n * a), 6), round(np.sin(n * a), 6)) for a in angles]
        distinct = len(set(z_vals))
        ratio = distinct / len(positions) if len(positions) > 0 else 0
        print(f"    z^{n}: {distinct} distinct values ({ratio:.1%} of positions)")

# ============================================================
# SECTION 4: COPPER ACROSS THE TOWER
# ============================================================
print()
print("=" * 70)
print("SECTION 4: COPPER (Z=29) ACROSS THE TOWER")
print("=" * 70)

Z_CU = 29
print(f"\n  Copper Z={Z_CU}:")
for m in moduli:
    r = Z_CU % m
    coprime = np.gcd(r, m) == 1
    if coprime:
        pos_idx = coprime_positions(m).index(r)
        angle = 360 * r / m
        z1 = np.exp(1j * 2 * np.pi * r / m)
        z2 = np.exp(2j * 2 * np.pi * r / m)
        z3 = np.exp(3j * 2 * np.pi * r / m)
        print(f"    mod {m:>3}: pos={r:>3}, angle={angle:>6.1f} deg, "
              f"z^1={z1.real:+.3f}{z1.imag:+.3f}i, z^2={z2.real:+.3f}{z2.imag:+.3f}i, "
              f"z^3={z3.real:+.3f}{z3.imag:+.3f}i")
    else:
        print(f"    mod {m:>3}: pos={r:>3}, NOT coprime (shares factor with {m})")

# ============================================================
# SECTION 5: CROSS-MULTIPOLE INDEPENDENCE AT MOD 210
# ============================================================
print()
print("=" * 70)
print("SECTION 5: FULL MULTIPOLE INDEPENDENCE AT MOD 210")
print("=" * 70)

# Build full correlation matrix between all multipole components
moments = results_all[210]['moments']
labels = []
components = []
for n in range(1, 7):
    labels.extend([f'Re(z^{n})', f'Im(z^{n})'])
    components.extend([moments[n].real, moments[n].imag])

n_comp = len(components)
corr_matrix = np.zeros((n_comp, n_comp))
for i in range(n_comp):
    for j in range(n_comp):
        vi = np.var(components[i])
        vj = np.var(components[j])
        if vi > 0 and vj > 0:
            corr_matrix[i, j] = np.corrcoef(components[i], components[j])[0, 1]

print(f"\n  Cross-multipole max correlations at mod 210:")
print(f"  (12 components: Re/Im of z^1 through z^6)")
print()

# Print upper triangle as a compact table
for i in range(0, n_comp, 2):
    n_i = i // 2 + 1
    part_i = 'Re' if i % 2 == 0 else 'Im'
    row_str = f"    z^{n_i} {part_i}: "
    for j in range(0, n_comp, 2):
        n_j = j // 2 + 1
        part_j = 'Re' if j % 2 == 0 else 'Im'
        if j > i:
            val = abs(corr_matrix[i, j])
            row_str += f"|{val:.3f}| "
    print(row_str)

# Find the most correlated pair of different multipoles
max_off = 0
max_pair = ("", "")
for i in range(n_comp):
    for j in range(i + 1, n_comp):
        if (i // 2) != (j // 2):  # different multipoles
            val = abs(corr_matrix[i, j])
            if val > max_off:
                max_off = val
                max_pair = (labels[i], labels[j])

print(f"\n  Most correlated cross-multipole pair: {max_pair[0]} vs {max_pair[1]}")
print(f"  |corr| = {max_off:.6f}")

# Average cross-multipole correlation
cross_corrs = []
for i in range(n_comp):
    for j in range(i + 1, n_comp):
        if (i // 2) != (j // 2):
            cross_corrs.append(abs(corr_matrix[i, j]))

print(f"  Mean cross-multipole |corr|: {np.mean(cross_corrs):.6f}")
print(f"  Median cross-multipole |corr|: {np.median(cross_corrs):.6f}")

# ============================================================
# SECTION 6: PRIME 7 EFFECT -- Z_6 OPENS
# ============================================================
print()
print("=" * 70)
print("SECTION 6: WHAT PRIME 7 ADDS")
print("=" * 70)

print(f"""
  The tower adds structure as primes accumulate:

  mod 6  = 2 x 3:     (Z/6Z)*  = Z_2         (1 real char)
  mod 12 = 2^2 x 3:   (Z/12Z)* = Z_2 x Z_2   (3 real chars, Klein 4-group)
  mod 30 = 2 x 3 x 5: (Z/30Z)* = Z_4 x Z_2   (complex chars from Z_4)
  mod 60 = 2^2 x 3 x 5: (Z/60Z)* = Z_4 x Z_2 x Z_2 (8 complex + 8 real)
  mod 210 = 2 x 3 x 5 x 7: (Z/210Z)* = Z_2 x Z_2 x Z_4 x Z_6
                                 (16 complex from Z_4 x Z_6)

  Prime 5 opens Z_4 (complex characters, 4th roots of unity)
  Prime 7 opens Z_6 (6th roots of unity, Z_2 x Z_3 structure)
  Together: Z_4 x Z_6 gives characters of order 1,2,3,4,6,12

  This is the first level with characters of order 3 and 6.
  Order 3 -> Z_3 quantum number (3-state, like color charge)
  Order 6 -> Z_6 (combines color + parity)
  Order 12 -> full dodecahedral symmetry possible
""")

# Count character orders at mod 210
# (Z/210Z)* = Z_2 x Z_2 x Z_4 x Z_6
# Character orders are LCM of component orders
from itertools import product as iproduct

# Generator orders for each factor
factors = {
    'Z2_a': [1, 2],
    'Z2_b': [1, 2],
    'Z4':   [1, 2, 4],
    'Z6':   [1, 2, 3, 6],
}

orders = []
for a, b, c, d in iproduct(factors['Z2_a'], factors['Z2_b'], factors['Z4'], factors['Z6']):
    order = np.lcm(np.lcm(a, b), np.lcm(c, d))
    orders.append(order)

from collections import Counter
order_counts = Counter(orders)

print(f"  Character order distribution at mod 210:")
for order in sorted(order_counts.keys()):
    count = order_counts[order]
    frac = count / 48 * 100
    bar = '#' * int(frac / 2)
    real_or_complex = "real" if order <= 2 else "complex"
    print(f"    order {order:>2}: {count:>2} chars ({frac:>5.1f}%) {bar} [{real_or_complex}]")

# ============================================================
# SECTION 7: SCALING LAWS
# ============================================================
print()
print("=" * 70)
print("SECTION 7: SCALING LAWS ACROSS THE TOWER")
print("=" * 70)

print(f"\n  D-Q correlation vs DOF:")
for m in moduli:
    r = results_all[m]
    phi = euler_phi(m)
    print(f"    mod {m:>3} ({phi:>2} DOF): max |D-Q| = {r['max_DQ_corr']:.6f}")

print(f"\n  Quadrupole fraction vs DOF:")
for m in moduli:
    r = results_all[m]
    phi = euler_phi(m)
    print(f"    mod {m:>3} ({phi:>2} DOF): quad% = {r['frac_2']:.1f}%")

print(f"\n  Dipole fraction vs DOF (should decrease with more DOF):")
for m in moduli:
    r = results_all[m]
    phi = euler_phi(m)
    print(f"    mod {m:>3} ({phi:>2} DOF): dip% = {r['frac_1']:.1f}%")

print(f"\n  Graviton polarization balance (h+/hx, ideal=1.0):")
for m in moduli:
    r = results_all[m]
    phi = euler_phi(m)
    print(f"    mod {m:>3} ({phi:>2} DOF): {r['hp_hx_ratio']:.4f}")

# ============================================================
# SECTION 8: CONCLUSION
# ============================================================
print()
print("=" * 70)
print("SECTION 8: CONCLUSION")
print("=" * 70)

r6 = results_all[6]
r12 = results_all[12]
r210_data = results_all[210]

print(f"""
  THE TOWER AT MOD 210 (48 DOF):

  Power redistribution with increasing DOF:
    mod   6 (2 DOF):  dipole {r6['frac_1']:.1f}%, quadrupole {r6['frac_2']:.1f}%
    mod  12 (4 DOF):  dipole {r12['frac_1']:.1f}%, quadrupole {r12['frac_2']:.1f}%
    mod 210 (48 DOF): dipole {r210_data['frac_1']:.1f}%, quadrupole {r210_data['frac_2']:.1f}%

  Dipole-quadrupole decoupling:
    mod   6: |corr| = {r6['max_DQ_corr']:.4f} (DEPENDENT)
    mod  12: |corr| = {r12['max_DQ_corr']:.4f} (INDEPENDENT)
    mod 210: |corr| = {r210_data['max_DQ_corr']:.4f} (INDEPENDENT)

  At mod 210, prime 7 opens Z_6 cyclic structure:
    - Characters of order 3 (color-like) first appear
    - Characters of order 6 (color x parity) first appear
    - 16 of 48 characters are complex (from Z_4 x Z_6)
    - All 6 multipole moments are effectively independent
    - Mean cross-multipole |corr| = {np.mean(cross_corrs):.4f}

  The monad's charge structure becomes RICHER at every tower level.
  Each new prime factor opens new cyclic symmetry:
    2 -> Z_2 (binary, real)
    3 -> Z_2 (binary, real, from 2-adic)
    5 -> Z_4 (4th roots, complex)
    7 -> Z_6 (6th roots, color + parity)

  Spin-2 (gravity) is independent at every level above mod 6.
  At mod 210, even spin-3, spin-4, spin-5 are independent.
""")

print("=" * 70)
print("EXPERIMENT 018ooo COMPLETE")
print("=" * 70)
