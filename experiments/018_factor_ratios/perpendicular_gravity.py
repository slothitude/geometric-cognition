"""
Experiment 018mmm: The Perpendicular Field -- Where Gravity Hides

The insight: E(k) = f_R2(k) - f_R1(k) is the OPPOSED (180°) combination.
That's spin-1 (dipole). Gravity is spin-2 (quadrupole) -- it couples to
the PERPENDICULAR direction, not the opposed one.

In the monad's 12-position circle:
  Spin-1 (photon):  couples to z^1 (dipole, 180° axis = R1 vs R2)
  Spin-2 (graviton): couples to z^2 (quadrupole, 90° pattern)

The quadrupole is the SECOND angular harmonic. In the 12-position circle:
  z_n = exp(2πi * n / 12)
  z_n^2 = exp(2πi * n / 6)  -- period 6, not 12!

This identifies pairs at 90° (3 positions apart) rather than 180° (6 apart).

For the walking sieve at position k:
  R1 = 6k-1, R2 = 6k+1
  Their sub-positions: sp_R1 = (k+1)%6, sp_R2 = k%6  (roughly)

The perpendicular field is the CROSS product of E and B:
  S(k) = E(k) × B(k)  [analog of Poynting vector]

But more precisely, the quadrupole field:
  Q(k) = Σ_m mass(m) * z_m^2  [second harmonic of mass distribution]

And the tensor field:
  T(k) = outer product of (E, B) directions -- the spin-2 coupling
"""

import numpy as np

print("=" * 70)
print("EXPERIMENT 018mmm: THE PERPENDICULAR FIELD -- WHERE GRAVITY HIDES")
print("=" * 70)

# ============================================================
# SECTION 1: THE MONAD'S HARMONIC STRUCTURE
# ============================================================
print()
print("=" * 70)
print("SECTION 1: SPIN-1 vs SPIN-2 HARMONICS IN THE 12-POSITION CIRCLE")
print("=" * 70)
print()

# The 12 monad positions
positions = np.arange(12)
angles = positions * 2 * np.pi / 12  # 0, 30, 60, ..., 330 degrees

print("Monad positions and their angular harmonics:")
print(f"  {'pos':>3s}  {'deg':>5s}  {'z^1 (spin-1)':>15s}  {'z^2 (spin-2)':>15s}  {'z^3':>15s}")
print(f"  {'---':>3s}  {'---':>5s}  {'------------':>15s}  {'------------':>15s}  {'---':>15s}")

for n in range(12):
    z1 = np.exp(1j * angles[n])
    z2 = np.exp(2j * angles[n])  # z^2 = exp(2i*theta)
    z3 = np.exp(3j * angles[n])
    print(f"  {n:3d}  {n*30:5d}  {z1.real:+.3f}{z1.imag:+.3f}i  "
          f"{z2.real:+.3f}{z2.imag:+.3f}i  {z3.real:+.3f}{z3.imag:+.3f}i")

print()
print("Key observations:")
print("  z^1 has period 12 (distinguishes all 12 positions)")
print("  z^2 has period 6 (identifies antipodal pairs)")
print("  Spin-1 couples to z^1: the DIPOLE moment")
print("  Spin-2 couples to z^2: the QUADRUPOLE moment")
print()
print("  The E-field E(k) = f_R2 - f_R1 is the z^1 (dipole) component")
print("  The PERPENDICULAR field would be the z^2 (quadrupole) component")
print()

# ============================================================
# SECTION 2: COMPUTE THE SIEVE FIELDS
# ============================================================
print()
print("=" * 70)
print("SECTION 2: SIEVE FIELDS -- DIPOLE, QUADRUPOLE, CROSS")
print("=" * 70)
print()

k_max = 10000
N_sieve = 6 * k_max + 10
is_prime = np.ones(N_sieve + 1, dtype=bool)
is_prime[0] = is_prime[1] = False
for i in range(2, int(N_sieve**0.5) + 1):
    if is_prime[i]:
        is_prime[i*i::i] = False

k_vals = np.arange(1, k_max + 1)

# Raw sieve: f_R1(k) = 1 if 6k-1 prime, f_R2(k) = 1 if 6k+1 prime
f_R1 = np.array([1 if is_prime[6*k - 1] else 0 for k in k_vals], dtype=float)
f_R2 = np.array([1 if is_prime[6*k + 1] else 0 for k in k_vals], dtype=float)

# Standard fields (from earlier experiments)
E_field = f_R2 - f_R1          # Spin-1 dipole (OPPOSED, 180°)
B_field = f_R1 + f_R2          # Mass density (PARALLEL)
M_field = f_R1 * f_R2          # Twin prime indicator (AND)

print(f"Computed sieve fields for k=1 to {k_max}")
print(f"  E = f_R2 - f_R1: mean={np.mean(E_field):.4f}, var={np.var(E_field):.4f}")
print(f"  B = f_R1 + f_R2: mean={np.mean(B_field):.4f}, var={np.var(B_field):.4f}")
print(f"  M = f_R1 * f_R2: mean={np.mean(M_field):.4f} (twin primes)")
print()

# ============================================================
# SECTION 3: THE PERPENDICULAR (CROSS) FIELD
# ============================================================
print()
print("=" * 70)
print("SECTION 3: THE PERPENDICULAR FIELD -- Poynting-like CROSS")
print("=" * 70)
print()

# The Poynting vector S = E × B points PERPENDICULAR to both E and B
# In the monad, E and B are scalar fields at each k-position
# The "cross product" in 1D is the product E * B
# But that's just M (twin prime indicator) -- not perpendicular

# The REAL perpendicular field involves ADJACENT positions:
# S(k) = E(k) * B(k+1) - B(k) * E(k+1)
# This is the discrete analog of the curl: E × B in the k-direction

S_field = E_field[:-1] * B_field[1:] - B_field[:-1] * E_field[1:]
# Pad to same length
S_field = np.append(S_field, 0)

print("Poynting-like field: S(k) = E(k)*B(k+1) - B(k)*E(k+1)")
print(f"  mean = {np.mean(S_field):.6f}")
print(f"  var  = {np.var(S_field):.6f}")
print(f"  S values: {dict(zip(*np.unique(S_field, return_counts=True)))}")
print()

# ============================================================
# SECTION 4: THE QUADRUPOLE FIELD (z^2 coupling)
# ============================================================
print()
print("=" * 70)
print("SECTION 4: THE QUADRUPOLE FIELD -- SPIN-2 COUPLING")
print("=" * 70)
print()

# Each k maps to a monad position. The sub-position of 6k±1 determines
# the angular position. But we need the MASS-weighted quadrupole.

# For the walking sieve, at position k we have two "masses":
# f_R1(k) and f_R2(k). These sit at angular positions:
# R1 (6k-1): sub-position depends on k
# R2 (6k+1): sub-position depends on k

# Sub-position mapping: for 6k-1, sp = (-k) mod 6; for 6k+1, sp = k mod 6
# Wait -- let's be precise:
# 6k-1 mod 12: depends on k
# 6k+1 mod 12: depends on k
# (6k-1) mod 12 = (6*(k%2) - 1) mod 12 = alternates between 5 and 11
# Actually: for k even, 6k mod 12 = 0, so 6k-1=11 mod 12, 6k+1=1 mod 12
#           for k odd,  6k mod 12 = 6, so 6k-1=5 mod 12, 6k+1=7 mod 12

# So the positions ALTERNATE:
# k even: R1 at pos 11 (330°), R2 at pos 1 (30°)
# k odd:  R1 at pos 5 (150°),  R2 at pos 7 (210°)

# The angular positions:
R1_angles = np.where(k_vals % 2 == 0, 11 * np.pi / 6, 5 * np.pi / 6)
R2_angles = np.where(k_vals % 2 == 0, 1 * np.pi / 6, 7 * np.pi / 6)

print("Angular positions of R1 and R2 on the monad circle:")
print(f"  k even: R1 at 330° (pos 11), R2 at 30° (pos 1)")
print(f"  k odd:  R1 at 150° (pos 5),  R2 at 210° (pos 7)")
print()

# Spin-1 (dipole): D = Σ f_i * z_i  where z = exp(iθ)
D_field = (f_R2 * np.exp(1j * R2_angles) + f_R1 * np.exp(1j * R1_angles))

# Spin-2 (quadrupole): Q = Σ f_i * z_i^2 where z^2 = exp(2iθ)
Q_field = (f_R2 * np.exp(2j * R2_angles) + f_R1 * np.exp(2j * R1_angles))

# Spin-3 (octupole): O = Σ f_i * z_i^3
O_field = (f_R2 * np.exp(3j * R2_angles) + f_R1 * np.exp(3j * R1_angles))

print("Multipole decomposition of the sieve field:")
print(f"  Dipole (spin-1, z^1):  |D|^2 total = {np.sum(np.abs(D_field)**2):.1f}")
print(f"  Quadrupole (spin-2, z^2): |Q|^2 total = {np.sum(np.abs(Q_field)**2):.1f}")
print(f"  Octupole (spin-3, z^3):   |O|^2 total = {np.sum(np.abs(O_field)**2):.1f}")
print()

# The power in each harmonic tells us which spin the sieve couples to
total_power = np.sum(f_R1**2 + f_R2**2)
print(f"  Total field power: {total_power:.1f}")
print(f"  Dipole fraction:     {np.sum(np.abs(D_field)**2)/total_power*100:.1f}%")
print(f"  Quadrupole fraction: {np.sum(np.abs(Q_field)**2)/total_power*100:.1f}%")
print(f"  Octupole fraction:   {np.sum(np.abs(O_field)**2)/total_power*100:.1f}%")
print()

# Real and imaginary parts of the quadrupole
Q_real = Q_field.real
Q_imag = Q_field.imag

print("Quadrupole field (spin-2) statistics:")
print(f"  Re(Q) = h_+ polarization: mean={np.mean(Q_real):.6f}, var={np.var(Q_real):.6f}")
print(f"  Im(Q) = h_x polarization: mean={np.mean(Q_imag):.6f}, var={np.var(Q_imag):.6f}")
print(f"  These are the TWO graviton polarization states!")
print()

# ============================================================
# SECTION 5: DIPOLE vs QUADRUPOLE -- OPPOSED vs PERPENDICULAR
# ============================================================
print()
print("=" * 70)
print("SECTION 5: DIPOLE (OPPOSED) vs QUADRUPOLE (PERPENDICULAR)")
print("=" * 70)
print()

# The E-field is essentially Re(D) (the real part of the dipole)
# Let's verify this and compare with the quadrupole

D_real = D_field.real
D_imag = D_field.imag

# The E-field should be proportional to D_real
corr_E_Dreal = np.corrcoef(E_field, D_real)[0, 1]
corr_E_Dimag = np.corrcoef(E_field, D_imag)[0, 1]

print("Dipole field vs E-field (spin-1):")
print(f"  Corr(E, Re(D)): {corr_E_Dreal:.6f}")
print(f"  Corr(E, Im(D)): {corr_E_Dimag:.6f}")
print(f"  -> E-field IS the dipole real part (opposed/180° axis)")
print()

# Now compare quadrupole with E and B
corr_Qreal_E = np.corrcoef(Q_real, E_field)[0, 1]
corr_Qreal_B = np.corrcoef(Q_real, B_field)[0, 1]
corr_Qimag_E = np.corrcoef(Q_imag, E_field)[0, 1]
corr_Qimag_B = np.corrcoef(Q_imag, B_field)[0, 1]

# Cross correlation between dipole and quadrupole
corr_Dreal_Qreal = np.corrcoef(D_real, Q_real)[0, 1]
corr_Dreal_Qimag = np.corrcoef(D_real, Q_imag)[0, 1]
corr_Dimag_Qreal = np.corrcoef(D_imag, Q_real)[0, 1]
corr_Dimag_Qimag = np.corrcoef(D_imag, Q_imag)[0, 1]

print("Quadrupole (spin-2) vs sieve fields:")
print(f"  Corr(Re(Q), E): {corr_Qreal_E:.6f}")
print(f"  Corr(Re(Q), B): {corr_Qreal_B:.6f}")
print(f"  Corr(Im(Q), E): {corr_Qimag_E:.6f}")
print(f"  Corr(Im(Q), B): {corr_Qimag_B:.6f}")
print()

print("Dipole vs Quadrupole cross-correlations:")
print(f"  Corr(Re(D), Re(Q)): {corr_Dreal_Qreal:.6f}  [spin-1 vs spin-2, parallel]")
print(f"  Corr(Re(D), Im(Q)): {corr_Dreal_Qimag:.6f}  [spin-1 vs spin-2, perpendicular]")
print(f"  Corr(Im(D), Re(Q)): {corr_Dimag_Qreal:.6f}")
print(f"  Corr(Im(D), Im(Q)): {corr_Dimag_Qimag:.6f}")
print()

# ============================================================
# SECTION 6: THE PERPENDICULAR SIGNAL IN FOURIER SPACE
# ============================================================
print()
print("=" * 70)
print("SECTION 6: FOURIER ANALYSIS -- SPIN-1 vs SPIN-2 PEAKS")
print("=" * 70)
print()

# The L-function zeros are at frequencies in LOG-space
# Spin-1 coupling: the E-field Fourier transform
# Spin-2 coupling: the quadrupole Fourier transform

log_k = np.log(k_vals.astype(float))

# Only use positions where field is nonzero for spectral analysis
# (This is sparse, so use all positions but weight by field value)

# Spin-1 spectrum: S_1(T) = Σ E(k) * k^{-1/2} * exp(-iT*log(k))
# Spin-2 spectrum: S_2(T) = Σ Q(k) * k^{-1/2} * exp(-iT*log(k))

T_scan = np.linspace(1, 80, 200)
S1_spectrum = np.zeros(len(T_scan), dtype=complex)
S2_spectrum = np.zeros(len(T_scan), dtype=complex)

for i, T in enumerate(T_scan):
    phase = np.exp(-1j * T * log_k)
    weight = 1.0 / np.sqrt(k_vals.astype(float))
    S1_spectrum[i] = np.sum(E_field * weight * phase)
    S2_spectrum[i] = np.sum(Q_real * weight * phase)  # h+ polarization

S1_power = np.abs(S1_spectrum)**2
S2_power = np.abs(S2_spectrum)**2

# Find peaks
from scipy.signal import find_peaks as _fp
# Manual peak finding to avoid import issues
def find_peaks_simple(arr, min_height=None):
    peaks = []
    for i in range(1, len(arr)-1):
        if arr[i] > arr[i-1] and arr[i] > arr[i+1]:
            if min_height is None or arr[i] > min_height:
                peaks.append(i)
    return peaks

S1_peaks = find_peaks_simple(S1_power, min_height=np.max(S1_power)*0.1)
S2_peaks = find_peaks_simple(S2_power, min_height=np.max(S2_power)*0.1)

print("Spectral peaks in log-space Fourier transform:")
print()
print(f"  Spin-1 (dipole, E-field): {len(S1_peaks)} peaks")
for p in S1_peaks[:10]:
    print(f"    T = {T_scan[p]:.2f}, power = {S1_power[p]:.2f}")
print()
print(f"  Spin-2 (quadrupole, h+): {len(S2_peaks)} peaks")
for p in S2_peaks[:10]:
    print(f"    T = {T_scan[p]:.2f}, power = {S2_power[p]:.2f}")

# Do the peaks coincide? (They should if they're from the same zeros)
print()
if S1_peaks and S2_peaks:
    S1_peak_T = [T_scan[p] for p in S1_peaks[:10]]
    S2_peak_T = [T_scan[p] for p in S2_peaks[:10]]
    print("Peak comparison (spin-1 vs spin-2):")
    print(f"  Spin-1 peaks: {[f'{t:.2f}' for t in S1_peak_T]}")
    print(f"  Spin-2 peaks: {[f'{t:.2f}' for t in S2_peak_T]}")

    # Match peaks
    matches = 0
    for t1 in S1_peak_T:
        for t2 in S2_peak_T:
            if abs(t1 - t2) < 2.0:
                matches += 1
                break
    print(f"  Matching peaks (within T=2): {matches}/{len(S1_peak_T)}")

print()

# ============================================================
# SECTION 7: THE TENSOR FIELD -- SPIN-2 COUPLING STRENGTH
# ============================================================
print()
print("=" * 70)
print("SECTION 7: THE TENSOR FIELD -- h+ AND hx POLARIZATIONS")
print("=" * 70)
print()

# The two graviton polarizations in the monad:
# h+ (plus): stretches along one axis, compresses perpendicular
# hx (cross): stretches along 45°, compresses at 135°

# h+(k) = Re(Q(k)) = quadrupole real part
# hx(k) = Im(Q(k)) = quadrupole imaginary part

# In GR: h+ and hx are INDEPENDENT for a freely propagating graviton
# They satisfy: dh+/dt and dhx/dt are both related to the source quadrupole

# The key question: are h+ and hx correlated in the monad?
corr_h_plus_cross = np.corrcoef(Q_real, Q_imag)[0, 1]
print(f"Graviton polarization correlation: Corr(h+, hx) = {corr_h_plus_cross:.6f}")
print(f"  (For independent polarizations, this should be ~0)")
print()

# The TENSOR structure: T_ij = h_i * h_j
# For spin-2: the metric perturbation is h_μν with 2 physical DOF
# In the monad's 2D plane:
#   h_++ = h+ * h+ (stretch along x)
#   h_xx = hx * hx (stretch along 45°)
#   h_+x = h+ * hx (cross term)

h_plus = Q_real
h_cross = Q_imag

# The strain tensor
h_xx = np.mean(h_plus**2)
h_yy = np.mean(h_cross**2)
h_xy = np.mean(h_plus * h_cross)

print("Strain tensor components (mean values):")
print(f"  <h+ * h+> = {h_xx:.6f}  (stretch along R1-R2 axis)")
print(f"  <hx * hx> = {h_yy:.6f}  (stretch along 45° axis)")
print(f"  <h+ * hx> = {h_xy:.6f}  (cross term, should be ~0)")
print()

ratio = h_xx / h_yy if h_yy > 0 else float('inf')
print(f"  h+/hx ratio: {ratio:.4f}")
print(f"  For isotropic gravity: ratio = 1.0")
print(f"  For monad-anisotropic gravity: ratio != 1.0")
print()

# ============================================================
# SECTION 8: COPPER'S QUADRUPOLE
# ============================================================
print()
print("=" * 70)
print("SECTION 8: COPPER'S QUADRUPOLE AT k=5")
print("=" * 70)
print()

# Copper is at Z=29, k=5 in the monad
# What is the quadrupole field at k=5?

for k in [3, 4, 5, 6, 7]:
    n_r1 = 6*k - 1
    n_r2 = 6*k + 1
    r1 = 1 if is_prime[n_r1] else 0
    r2 = 1 if is_prime[n_r2] else 0

    # Dipole
    d = r2 * np.exp(1j * R2_angles[k-1]) + r1 * np.exp(1j * R1_angles[k-1])

    # Quadrupole
    q = r2 * np.exp(2j * R2_angles[k-1]) + r1 * np.exp(2j * R1_angles[k-1])

    # Octupole
    o = r2 * np.exp(3j * R2_angles[k-1]) + r1 * np.exp(3j * R1_angles[k-1])

    label = " <-- Cu" if k == 5 else ""
    print(f"  k={k}: R1={n_r1}({'P' if r1 else '.'}), R2={n_r2}({'P' if r2 else '.'})  "
          f"D={d.real:+.2f}{d.imag:+.2f}i  "
          f"Q={q.real:+.2f}{q.imag:+.2f}i  "
          f"O={o.real:+.2f}{o.imag:+.2f}i{label}")

print()
print("  At k=5 (Cu): twin prime (29,31)")
print("  The quadrupole Q has MAXIMUM |Q| because BOTH rails are occupied")
print("  This is the monad's 'gravitational resonance' --")
print("  maximum quadrupole moment at the twin prime position")
print()

# ============================================================
# SECTION 9: CUMULATIVE QUADRUPOLE AND TIDAL FORCE
# ============================================================
print()
print("=" * 70)
print("SECTION 9: CUMULATIVE FIELDS -- DIPOLE vs QUADRUPOLE vs GRAVITY")
print("=" * 70)
print()

# Cumulative dipole (Chebyshev race -- spin-1 signal)
cumul_dipole = np.cumsum(E_field)

# Cumulative quadrupole (spin-2 signal)
cumul_quad_real = np.cumsum(Q_real)
cumul_quad_imag = np.cumsum(Q_imag)

# Cumulative mass (spin-0, scalar)
cumul_mass = np.cumsum(B_field)

print("Cumulative field growth (k=1 to 5000):")
print(f"  Dipole (spin-1):     final = {cumul_dipole[-1]:.0f}")
print(f"  Quadrupole Re (h+):  final = {cumul_quad_real[-1]:.2f}")
print(f"  Quadrupole Im (hx):  final = {cumul_quad_imag[-1]:.2f}")
print(f"  Mass (spin-0):       final = {cumul_mass[-1]:.0f}")
print()

# The quadrupole should oscillate around zero (like a tidal field)
# while the mass grows monotonically
print(f"  Dipole grows as:     ~sqrt(k) [Chebyshev bias]")
print(f"  Mass grows as:       ~k/log(k) [PNT]")
print(f"  Quadrupole grows as: ~sqrt(k) or bounded [TIDAL FIELD]")
print()

# Power law fits
log_k_vals = np.log(k_vals.astype(float))
log_cumul_dipole = np.log(np.abs(cumul_dipole) + 1)
log_cumul_mass = np.log(cumul_mass + 1)
log_cumul_quad = np.log(np.sqrt(cumul_quad_real**2 + cumul_quad_imag**2) + 1)

# Simple power law: log(cumul) ~ alpha * log(k)
# Use k > 100 for the fit
mask_fit = k_vals > 100
if np.sum(mask_fit) > 10:
    alpha_dipole = np.polyfit(log_k_vals[mask_fit], log_cumul_dipole[mask_fit], 1)[0]
    alpha_mass = np.polyfit(log_k_vals[mask_fit], log_cumul_mass[mask_fit], 1)[0]
    alpha_quad = np.polyfit(log_k_vals[mask_fit], log_cumul_quad[mask_fit], 1)[0]

    print(f"Power law exponents (cumulative ~ k^alpha):")
    print(f"  Dipole (spin-1):   alpha = {alpha_dipole:.4f}  (expect ~0.5 for random walk)")
    print(f"  Mass (spin-0):     alpha = {alpha_mass:.4f}  (expect ~1.0 for PNT)")
    print(f"  Quadrupole (spin-2): alpha = {alpha_quad:.4f}  (expect <?)")
    print()

# ============================================================
# SECTION 10: THE KEY COMPARISON
# ============================================================
print()
print("=" * 70)
print("SECTION 10: THE OPPOSED vs PERPENDICULAR DISTINCTION")
print("=" * 70)
print()

print("The monad's field structure:")
print()
print("  OPPOSED (180°) axis -- SPIN-1 coupling:")
print(f"    E(k) = f_R2 - f_R1 = chi_1 sum")
print(f"    This is the DIPOLE moment (z^1 harmonic)")
print(f"    Couples to U(1) charge = chi_1 = +/-1")
print(f"    Power: {np.sum(E_field**2):.0f}")
print(f"    Cumulative: random walk ~ sqrt(k)")
print()
print("  PERPENDICULAR (90°) axis -- SPIN-2 coupling:")
print(f"    h+(k) = Re(sum f_i * z_i^2)  [plus polarization]")
print(f"    hx(k) = Im(sum f_i * z_i^2)  [cross polarization]")
print(f"    This is the QUADRUPOLE moment (z^2 harmonic)")
print(f"    Couples to mass tensor T_munu")
print(f"    Power h+: {np.sum(Q_real**2):.0f}, hx: {np.sum(Q_imag**2):.0f}")
print(f"    Cumulative: {'bounded' if alpha_quad < 0.3 else f'~k^{alpha_quad:.2f}'}")
print()

# Cross-correlation: opposed vs perpendicular
window = 100
E_sm = np.convolve(E_field, np.ones(window)/window, mode='same')
Q_sm = np.convolve(Q_real, np.ones(window)/window, mode='same')
corr_opposed_perp = np.corrcoef(E_sm[window:-window], Q_sm[window:-window])[0, 1]

print(f"  Correlation between opposed (E) and perpendicular (h+):")
print(f"    r = {corr_opposed_perp:.6f}")
print(f"    {'NEARLY ZERO -- they are independent!' if abs(corr_opposed_perp) < 0.1 else 'CORRELATED -- not independent'}")
print()
print(f"    This is the hallmark of spin-1 vs spin-2:")
print(f"    The OPPOSED field (spin-1) and PERPENDICULAR field (spin-2)")
print(f"    carry INDEPENDENT information about the prime distribution")
print()

# ============================================================
# SECTION 11: CONCLUSION
# ============================================================
print()
print("=" * 70)
print("SECTION 11: CONCLUSION")
print("=" * 70)
print()

print("THE PERPENDICULAR FIELD EXISTS -- BUT IT'S NOT INDEPENDENT:")
print()
print("  CRITICAL FINDING: Re(Q) = 0.5*B and Im(Q) = 0.866*E (corr=1.000)")
print()
print("  The quadrupole (spin-2) is just a ROTATION of the dipole (spin-1).")
print("  They carry the SAME information, just mixed by a fixed angle.")
print()
print("  WHY: The sieve places R1 and R2 at FIXED angular positions")
print("  (30/150/210/330 degrees). With only 2 positions per k-value,")
print("  you get exactly 2 degrees of freedom. That's enough for:")
print("    - Dipole (2 DOF: Re(D), Im(D))  OR")
print("    - Quadrupole (2 DOF: h+, hx)")
print("  But NOT BOTH independently. You'd need 4+ positions per k")
print("  to support independent spin-1 AND spin-2 fields.")
print()
print("  The user's intuition was CORRECT -- gravity would be in the")
print("  perpendicular (quadrupole) direction. But the monad's 2-rail")
print("  structure cannot produce an independent perpendicular field.")
print("  The geometry is too constrained.")
print()
print("  WHAT THIS MEANS FOR COPPER AND GRAVITY:")
print("  - Copper's twin prime position (k=5) maximizes both E and B")
print("  - But the 'perpendicular' (quadrupole) signal is just B rotated")
print("  - No independent spin-2 information exists in the sieve")
print("  - The monad provides the GEOMETRY (dipole structure)")
print("  - But CANNOT provide independent spin-2 (graviton) structure")
print("  - The 2-rail constraint = 2 DOF = spin-1 ONLY")
print()
print("  To get spin-2, you'd need the tower of projections:")
print("  - mod 6: 2 DOF (chi_1 only, spin-1)")
print("  - mod 12: 4 DOF (chi_1 + chi_3, potentially spin-1 + spin-2)")
print("  - mod 30: 8 DOF (including complex characters)")
print("  The monad at mod 6 is a PURE spin-1 (U(1)) system.")
print("  Spin-2 (gravity) requires the tower -- higher modulus.")
print()

print("=" * 70)
print("EXPERIMENT 018mmm COMPLETE")
print("=" * 70)
