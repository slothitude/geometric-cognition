"""
Experiment 018nnn: The Tower -- Spin-2 at mod 12, 24, 30, 60

At mod 6 (2 DOF), the quadrupole is just a rotation of the dipole --
no independent spin-2. This experiment climbs the tower of projections
to find where spin-2 becomes independent.

Degrees of freedom by modulus:
  mod 6:  phi(6)=2   positions, 2 DOF  -> spin-1 only
  mod 12: phi(12)=4  positions, 4 DOF  -> spin-1 + spin-2 possible
  mod 24: phi(24)=8  positions, 8 DOF
  mod 30: phi(30)=8  positions, 8 DOF
  mod 60: phi(60)=16 positions, 16 DOF -> rich multipole structure

At each level, we compute:
  - Dipole (z^1): spin-1 coupling
  - Quadrupole (z^2): spin-2 coupling (perpendicular)
  - Octupole (z^3): spin-3
  - Check whether quadrupole is INDEPENDENT of dipole
"""

import numpy as np
from itertools import product

print("=" * 70)
print("EXPERIMENT 018nnn: THE TOWER -- SPIN-2 AT MOD 12, 24, 30, 60")
print("=" * 70)

# ============================================================
# HELPER: COPRIME POSITIONS AND MULTIPOLE DECOMPOSITION
# ============================================================

def coprime_positions(m):
    """Return positions coprime to m."""
    return [n for n in range(1, m) if np.gcd(n, m) == 1]

def euler_phi(m):
    """Euler's totient."""
    return len(coprime_positions(m))

def sieve_primes(N):
    """Simple sieve up to N."""
    is_p = np.ones(N + 1, dtype=bool)
    is_p[0] = is_p[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_p[i]:
            is_p[i*i::i] = False
    return is_p

N_max = 100000
is_prime = sieve_primes(N_max * 2)

def multipole_analysis(modulus, k_max=5000):
    """
    At each k, look at positions n = modulus*k + r for r coprime to modulus.
    Check which are prime. Compute multipole moments.
    Returns correlation matrix between dipole and quadrupole.
    """
    positions = coprime_positions(modulus)
    n_pos = len(positions)
    angles = np.array([2 * np.pi * r / modulus for r in positions])

    # z^1 (dipole), z^2 (quadrupole), z^3 (octupole) for each position
    z1 = np.exp(1j * angles)
    z2 = np.exp(2j * angles)
    z3 = np.exp(3j * angles)

    # Fields at each k
    k_vals = np.arange(0, k_max)
    f = np.zeros((k_max, n_pos))  # f[k, pos_idx] = 1 if prime, 0 otherwise

    for ki, k in enumerate(k_vals):
        for pi, r in enumerate(positions):
            n = modulus * k + r
            if n >= 2 and n < len(is_prime) and is_prime[n]:
                f[ki, pi] = 1.0

    # Multipole moments at each k
    # Dipole: D(k) = sum_i f_i * z1_i
    D = f @ z1  # complex array, length k_max
    # Quadrupole: Q(k) = sum_i f_i * z2_i
    Q = f @ z2
    # Octupole: O(k) = sum_i f_i * z3_i
    O = f @ z3

    # Total field power
    total_power = np.sum(f**2)

    # Power in each multipole
    dipole_power = np.sum(np.abs(D)**2)
    quad_power = np.sum(np.abs(Q)**2)
    oct_power = np.sum(np.abs(O)**2)

    # Independence check: is quadrupole correlated with dipole?
    D_real, D_imag = D.real, D.imag
    Q_real, Q_imag = Q.real, Q.imag
    O_real, O_imag = O.real, O.imag

    # Correlation matrix
    corr_Dr_Qr = np.corrcoef(D_real, Q_real)[0, 1] if np.var(D_real) > 0 and np.var(Q_real) > 0 else 0
    corr_Dr_Qi = np.corrcoef(D_real, Q_imag)[0, 1] if np.var(D_real) > 0 and np.var(Q_imag) > 0 else 0
    corr_Di_Qr = np.corrcoef(D_imag, Q_real)[0, 1] if np.var(D_imag) > 0 and np.var(Q_real) > 0 else 0
    corr_Di_Qi = np.corrcoef(D_imag, Q_imag)[0, 1] if np.var(D_imag) > 0 and np.var(Q_imag) > 0 else 0

    # Max absolute correlation between dipole and quadrupole
    max_corr = max(abs(corr_Dr_Qr), abs(corr_Dr_Qi), abs(corr_Di_Qr), abs(corr_Di_Qi))

    # h+ and hx correlation (should be ~0 for independent graviton polarizations)
    corr_hplus_hcross = np.corrcoef(Q_real, Q_imag)[0, 1] if np.var(Q_real) > 0 and np.var(Q_imag) > 0 else 0

    # Strain tensor
    h_xx = np.mean(Q_real**2) if np.var(Q_real) > 0 else 0
    h_yy = np.mean(Q_imag**2) if np.var(Q_imag) > 0 else 0
    h_xy = np.mean(Q_real * Q_imag)

    return {
        'modulus': modulus,
        'n_pos': n_pos,
        'positions': positions,
        'angles_deg': [r * 360 / modulus for r in positions],
        'total_power': total_power,
        'dipole_power': dipole_power,
        'quad_power': quad_power,
        'oct_power': oct_power,
        'dipole_frac': dipole_power / total_power * 100 if total_power > 0 else 0,
        'quad_frac': quad_power / total_power * 100 if total_power > 0 else 0,
        'oct_frac': oct_power / total_power * 100 if total_power > 0 else 0,
        'max_DQ_corr': max_corr,
        'corr_Dr_Qr': corr_Dr_Qr,
        'corr_Dr_Qi': corr_Dr_Qi,
        'corr_Di_Qr': corr_Di_Qr,
        'corr_Di_Qi': corr_Di_Qi,
        'corr_hplus_hcross': corr_hplus_hcross,
        'h_xx': h_xx,
        'h_yy': h_yy,
        'h_xy': h_xy,
        'D': D,
        'Q': Q,
        'O': O,
        'f': f,
        'k_vals': k_vals,
    }

# ============================================================
# SECTION 1: MOD 6 BASELINE (CONFIRM 018mmm)
# ============================================================
print()
print("=" * 70)
print("SECTION 1: MOD 6 BASELINE")
print("=" * 70)
print()

r6 = multipole_analysis(6)
print(f"Mod 6: {r6['n_pos']} positions, phi(6)={euler_phi(6)}")
print(f"  Positions: {r6['positions']} at {r6['angles_deg']} degrees")
print(f"  Dipole power: {r6['dipole_frac']:.1f}%")
print(f"  Quadrupole power: {r6['quad_frac']:.1f}%")
print(f"  Max D-Q correlation: {r6['max_DQ_corr']:.6f}")
print(f"  h+/hx correlation: {r6['corr_hplus_hcross']:.6f}")
print(f"  Verdict: {'DEPENDENT (spin-1 only)' if r6['max_DQ_corr'] > 0.99 else 'INDEPENDENT'}")
print()

# ============================================================
# SECTION 2: MOD 12
# ============================================================
print()
print("=" * 70)
print("SECTION 2: MOD 12 -- 4 DEGREES OF FREEDOM")
print("=" * 70)
print()

r12 = multipole_analysis(12)
print(f"Mod 12: {r12['n_pos']} positions, phi(12)={euler_phi(12)}")
print(f"  Positions: {r12['positions']} at {r12['angles_deg']} degrees")
print(f"  Dipole power: {r12['dipole_frac']:.1f}%")
print(f"  Quadrupole power: {r12['quad_frac']:.1f}%")
print(f"  Octupole power: {r12['oct_frac']:.1f}%")
print()
print(f"  Dipole-Quadrupole correlations:")
print(f"    Corr(Re(D), Re(Q)): {r12['corr_Dr_Qr']:.6f}")
print(f"    Corr(Re(D), Im(Q)): {r12['corr_Dr_Qi']:.6f}")
print(f"    Corr(Im(D), Re(Q)): {r12['corr_Di_Qr']:.6f}")
print(f"    Corr(Im(D), Im(Q)): {r12['corr_Di_Qi']:.6f}")
print(f"    Max |correlation|:  {r12['max_DQ_corr']:.6f}")
print()
print(f"  Graviton polarizations:")
print(f"    Corr(h+, hx): {r12['corr_hplus_hcross']:.6f}")
print(f"    <h+^2>: {r12['h_xx']:.6f}, <hx^2>: {r12['h_yy']:.6f}, <h+*hx>: {r12['h_xy']:.6f}")
print(f"    h+/hx ratio: {r12['h_xx']/r12['h_yy']:.4f}" if r12['h_yy'] > 0 else "    h+/hx ratio: N/A")
print()
independent = r12['max_DQ_corr'] < 0.95
print(f"  Verdict: {'INDEPENDENT quadrupole! Spin-2 EXISTS!' if independent else 'DEPENDENT (still spin-1 only)'}")
print()

# ============================================================
# SECTION 3: MOD 24
# ============================================================
print()
print("=" * 70)
print("SECTION 3: MOD 24 -- 8 DEGREES OF FREEDOM")
print("=" * 70)
print()

r24 = multipole_analysis(24)
print(f"Mod 24: {r24['n_pos']} positions, phi(24)={euler_phi(24)}")
print(f"  Positions: {r24['positions']}")
print(f"  Dipole power: {r24['dipole_frac']:.1f}%")
print(f"  Quadrupole power: {r24['quad_frac']:.1f}%")
print(f"  Octupole power: {r24['oct_frac']:.1f}%")
print()
print(f"  Dipole-Quadrupole correlations:")
print(f"    Corr(Re(D), Re(Q)): {r24['corr_Dr_Qr']:.6f}")
print(f"    Corr(Re(D), Im(Q)): {r24['corr_Dr_Qi']:.6f}")
print(f"    Corr(Im(D), Re(Q)): {r24['corr_Di_Qr']:.6f}")
print(f"    Corr(Im(D), Im(Q)): {r24['corr_Di_Qi']:.6f}")
print(f"    Max |correlation|:  {r24['max_DQ_corr']:.6f}")
print()
print(f"  Graviton polarizations:")
print(f"    Corr(h+, hx): {r24['corr_hplus_hcross']:.6f}")
print(f"    <h+^2>: {r24['h_xx']:.6f}, <hx^2>: {r24['h_yy']:.6f}, <h+*hx>: {r24['h_xy']:.6f}")
print(f"    h+/hx ratio: {r24['h_xx']/r24['h_yy']:.4f}" if r24['h_yy'] > 0 else "    h+/hx ratio: N/A")
print()
independent = r24['max_DQ_corr'] < 0.95
print(f"  Verdict: {'INDEPENDENT quadrupole! Spin-2 EXISTS!' if independent else 'DEPENDENT'}")
print()

# ============================================================
# SECTION 4: MOD 30
# ============================================================
print()
print("=" * 70)
print("SECTION 4: MOD 30 -- 8 DOF WITH COMPLEX CHARACTERS")
print("=" * 70)
print()

r30 = multipole_analysis(30)
print(f"Mod 30: {r30['n_pos']} positions, phi(30)={euler_phi(30)}")
print(f"  Positions: {r30['positions']}")
print(f"  Dipole power: {r30['dipole_frac']:.1f}%")
print(f"  Quadrupole power: {r30['quad_frac']:.1f}%")
print(f"  Octupole power: {r30['oct_frac']:.1f}%")
print()
print(f"  Dipole-Quadrupole correlations:")
print(f"    Corr(Re(D), Re(Q)): {r30['corr_Dr_Qr']:.6f}")
print(f"    Corr(Re(D), Im(Q)): {r30['corr_Dr_Qi']:.6f}")
print(f"    Corr(Im(D), Re(Q)): {r30['corr_Di_Qr']:.6f}")
print(f"    Corr(Im(D), Im(Q)): {r30['corr_Di_Qi']:.6f}")
print(f"    Max |correlation|:  {r30['max_DQ_corr']:.6f}")
print()
print(f"  Graviton polarizations:")
print(f"    Corr(h+, hx): {r30['corr_hplus_hcross']:.6f}")
print(f"    <h+^2>: {r30['h_xx']:.6f}, <hx^2>: {r30['h_yy']:.6f}, <h+*hx>: {r30['h_xy']:.6f}")
print(f"    h+/hx ratio: {r30['h_xx']/r30['h_yy']:.4f}" if r30['h_yy'] > 0 else "    h+/hx ratio: N/A")
print()
independent = r30['max_DQ_corr'] < 0.95
print(f"  Verdict: {'INDEPENDENT quadrupole! Spin-2 EXISTS!' if independent else 'DEPENDENT'}")
print()

# ============================================================
# SECTION 5: MOD 60
# ============================================================
print()
print("=" * 70)
print("SECTION 5: MOD 60 -- 16 DEGREES OF FREEDOM")
print("=" * 70)
print()

r60 = multipole_analysis(60)
print(f"Mod 60: {r60['n_pos']} positions, phi(60)={euler_phi(60)}")
print(f"  Positions: {r60['positions']}")
print(f"  Dipole power: {r60['dipole_frac']:.1f}%")
print(f"  Quadrupole power: {r60['quad_frac']:.1f}%")
print(f"  Octupole power: {r60['oct_frac']:.1f}%")
print()
print(f"  Dipole-Quadrupole correlations:")
print(f"    Corr(Re(D), Re(Q)): {r60['corr_Dr_Qr']:.6f}")
print(f"    Corr(Re(D), Im(Q)): {r60['corr_Dr_Qi']:.6f}")
print(f"    Corr(Im(D), Re(Q)): {r60['corr_Di_Qr']:.6f}")
print(f"    Corr(Im(D), Im(Q)): {r60['corr_Di_Qi']:.6f}")
print(f"    Max |correlation|:  {r60['max_DQ_corr']:.6f}")
print()
print(f"  Graviton polarizations:")
print(f"    Corr(h+, hx): {r60['corr_hplus_hcross']:.6f}")
print(f"    <h+^2>: {r60['h_xx']:.6f}, <hx^2>: {r60['h_yy']:.6f}, <h+*hx>: {r60['h_xy']:.6f}")
print(f"    h+/hx ratio: {r60['h_xx']/r60['h_yy']:.4f}" if r60['h_yy'] > 0 else "    h+/hx ratio: N/A")
print()
independent = r60['max_DQ_corr'] < 0.95
print(f"  Verdict: {'INDEPENDENT quadrupole! Spin-2 EXISTS!' if independent else 'DEPENDENT'}")
print()

# ============================================================
# SECTION 6: COMPARISON ACROSS THE TOWER
# ============================================================
print()
print("=" * 70)
print("SECTION 6: COMPARISON ACROSS THE TOWER")
print("=" * 70)
print()

print(f"  {'Mod':>4s}  {'phi':>4s}  {'DOF':>4s}  {'Dip%':>6s}  {'Quad%':>6s}  {'Oct%':>6s}  "
      f"{'MaxDQ':>7s}  {'h+hx':>7s}  {'h+/hx':>6s}  {'Spin-2?':>8s}")
print(f"  {'----':>4s}  {'---':>4s}  {'---':>4s}  {'-----':>6s}  {'-----':>6s}  {'-----':>6s}  "
      f"{'------':>7s}  {'------':>7s}  {'-----':>6s}  {'-------':>8s}")

for r in [r6, r12, r24, r30, r60]:
    ratio = f"{r['h_xx']/r['h_yy']:.3f}" if r['h_yy'] > 0 else "N/A"
    spin2 = "YES" if r['max_DQ_corr'] < 0.95 else "no"
    print(f"  {r['modulus']:4d}  {r['n_pos']:4d}  {r['n_pos']:4d}  {r['dipole_frac']:5.1f}%  "
          f"{r['quad_frac']:5.1f}%  {r['oct_frac']:5.1f}%  "
          f"{r['max_DQ_corr']:7.4f}  {r['corr_hplus_hcross']:+7.4f}  {ratio:>6s}  {spin2:>8s}")

print()

# ============================================================
# SECTION 7: WHY MOD 6 FAILS AND HIGHER MOD SUCCEEDS
# ============================================================
print()
print("=" * 70)
print("SECTION 7: THE STRUCTURAL REASON")
print("=" * 70)
print()

print("At mod 6: positions {1, 5} -> angles {30, 150} degrees")
print("  z^2 values: exp(60i) and exp(300i)")
print("  These are CONJUGATES -> Re(Q) and Im(Q) are linear combos of B and E")
print("  -> quadrupole = rotation of dipole, NOT independent")
print()

for m in [12, 24, 30, 60]:
    r = {'mod 12': r12, 'mod 24': r24, 'mod 30': r30, 'mod 60': r60}[f'mod {m}']
    positions = r['positions']
    angles = [pos * 360 / m for pos in positions]
    z2_vals = [np.exp(2j * np.pi * pos / m) for pos in positions]

    # Check if z^2 values are all conjugate pairs
    unique_z2 = set()
    for z in z2_vals:
        found = False
        for u in unique_z2:
            if abs(z - u) < 1e-6 or abs(z - np.conj(u)) < 1e-6:
                found = True
                break
        if not found:
            unique_z2.add(z)

    n_unique_z2 = len(unique_z2)
    n_pos = len(positions)

    print(f"Mod {m}: {n_pos} positions, {n_unique_z2} distinct z^2 values")
    print(f"  z^2 has {n_unique_z2} independent directions (need >2 for independent Q)")
    if r['max_DQ_corr'] < 0.95:
        print(f"  -> INDEPENDENT spin-2 at this level!")
    else:
        print(f"  -> Still constrained (max DQ corr = {r['max_DQ_corr']:.4f})")
    print()

# ============================================================
# SECTION 8: COPPER ACROSS THE TOWER
# ============================================================
print()
print("=" * 70)
print("SECTION 8: COPPER (Z=29) ACROSS THE TOWER")
print("=" * 70)
print()

print("Copper Z=29 at each modulus level:")
for m in [6, 12, 24, 30, 60]:
    pos = 29 % m
    coprime = np.gcd(29, m) == 1
    angle = pos * 360 / m
    z1 = np.exp(2j * np.pi * pos / m)
    z2 = np.exp(4j * np.pi * pos / m)
    print(f"  mod {m:2d}: pos={pos:2d}, coprime={coprime}, angle={angle:6.1f} deg, "
          f"z^1={z1.real:+.3f}{z1.imag:+.3f}i, z^2={z2.real:+.3f}{z2.imag:+.3f}i")

print()

# ============================================================
# SECTION 9: CONCLUSION
# ============================================================
print()
print("=" * 70)
print("SECTION 9: CONCLUSION")
print("=" * 70)
print()

# Find the first modulus where spin-2 becomes independent
first_spin2 = None
for r in [r6, r12, r24, r30, r60]:
    if r['max_DQ_corr'] < 0.95:
        first_spin2 = r['modulus']
        break

print("THE TOWER OF PROJECTIONS AND SPIN-2:")
print()
if first_spin2:
    print(f"  Spin-2 (independent quadrupole) FIRST appears at mod {first_spin2}")
    print(f"  This is where phi(m) > 2 DOF allows perpendicular field to be independent")
else:
    print(f"  Spin-2 does NOT appear at any tested modulus")
    print(f"  The quadrupole remains a rotation of the dipole at all levels")
print()

print("Power distribution across multipoles by modulus:")
for r in [r6, r12, r24, r30, r60]:
    print(f"  mod {r['modulus']:2d}: dipole {r['dipole_frac']:5.1f}%, "
          f"quadrupole {r['quad_frac']:5.1f}%, octupole {r['oct_frac']:5.1f}%")

print()
print("The key metric: max |correlation| between dipole and quadrupole:")
print("  < 0.5: strongly independent (genuine spin-2)")
print("  0.5-0.95: partially independent (mixed spin-1/2)")
print("  > 0.95: dependent (pure spin-1, quadrupole = rotation of dipole)")
print()
for r in [r6, r12, r24, r30, r60]:
    level = "INDEPENDENT" if r['max_DQ_corr'] < 0.5 else ("MIXED" if r['max_DQ_corr'] < 0.95 else "DEPENDENT")
    print(f"  mod {r['modulus']:2d}: max |D-Q corr| = {r['max_DQ_corr']:.4f} -> {level}")

print()

print("=" * 70)
print("EXPERIMENT 018nnn COMPLETE")
print("=" * 70)
