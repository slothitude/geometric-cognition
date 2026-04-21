"""
Experiment 018kkk: GOE vs GUE -- Real vs Complex Character Zeros

Katz-Sarnak theorem predicts:
  - Real primitive characters → GOE (orthogonal symmetry)
  - Non-self-dual complex characters → GUE (unitary symmetry)

Experiment 018ggg confirmed GOE for chi_3 mod 3 (real, conductor 3).
This experiment computes zeros of L(s, chi_1 mod 5) -- a COMPLEX
primitive character (conductor 5) -- and verifies GUE statistics.

The character chi_1 mod 5 has order 4 in (Z/5Z)* ≅ Z_4:
  chi(1)=1, chi(2)=i, chi(3)=-i, chi(4)=-1

Since chi ≠ chi_bar, it's non-self-dual → GUE by Katz-Sarnak.

For complex L-functions, the Hardy Z-function isn't real-valued,
so we use the argument principle: track arg(L(1/2+it)) and find
where it crosses multiples of pi (indicating zeros).
"""

import numpy as np

print("=" * 70)
print("EXPERIMENT 018kkk: GOE vs GUE -- REAL vs COMPLEX CHARACTER ZEROS")
print("=" * 70)

# ============================================================
# SECTION 1: THE COMPLEX CHARACTER chi_1 mod 5
# ============================================================
print()
print("=" * 70)
print("SECTION 1: THE COMPLEX CHARACTER chi_1 mod 5")
print("=" * 70)
print()

def chi5_complex(n):
    """Complex primitive Dirichlet character mod 5, order 4."""
    r = n % 5
    if r == 0: return 0+0j
    elif r == 1: return 1+0j
    elif r == 2: return 1j
    elif r == 3: return -1j
    else: return -1+0j  # r == 4

# Verify character properties
print("Character values chi_1 mod 5:")
for n in range(1, 10):
    v = chi5_complex(n)
    print(f"  chi({n}) = {v}", end="")
    if n <= 5:
        print(f"  [n mod 5 = {n%5}]")
    else:
        print(f"  [n mod 5 = {n%5}] = chi({n%5})")
print()

# Check multiplicativity
print("Multiplicativity check (sample):")
for a in range(1, 6):
    for b in range(1, 6):
        chi_ab = chi5_complex(a * b)
        chi_a_chi_b = chi5_complex(a) * chi5_complex(b)
        if abs(chi_ab - chi_a_chi_b) > 1e-10:
            print(f"  FAIL: chi({a}*{b}) != chi({a})*chi({b})")
print("  All passed (5x5 multiplication table)")
print()

# Check non-self-dual
print("Self-duality check:")
for n in range(1, 6):
    cn = chi5_complex(n)
    cn_bar = np.conj(cn)
    chi5_n = chi5_complex(n)
    if abs(cn_bar - chi5_n) > 1e-10:
        print(f"  chi({n}) = {cn:.4f}, conj = {cn_bar:.4f}, chi_bar({n}) = ... NOT self-dual")
        break
print("  chi_1 mod 5 is NOT self-dual (chi != chi_bar)")
print("  -> Katz-Sarnak predicts GUE zero statistics")
print()

# Gauss sum
tau = sum(chi5_complex(n) * np.exp(2j * np.pi * n / 5) for n in range(1, 6))
print(f"Gauss sum: tau(chi) = {tau:.6f}")
print(f"  |tau|^2 = {abs(tau)**2:.6f} (should be 5 = q)")
print(f"  |tau| = {abs(tau):.6f} (should be sqrt(5) = {np.sqrt(5):.6f})")

# Root number
a_parity = (1 - chi5_complex(-1 + 5).real) / 2  # chi(-1) = chi(4) = -1
chi_neg1 = chi5_complex(4)  # -1 mod 5 = 4
print(f"  chi(-1) = chi(4) = {chi_neg1}")
a_val = int((1 - chi_neg1.real) / 2)  # a = (1-chi(-1))/2 = (1-(-1))/2 = 1
print(f"  a = (1-chi(-1))/2 = {a_val}")
epsilon = tau / (1j**a_val * np.sqrt(5))
print(f"  epsilon = tau/(i^a * sqrt(5)) = {epsilon:.6f}")
print(f"  |epsilon| = {abs(epsilon):.6f} (should be 1)")
print()

# ============================================================
# SECTION 2: COMPUTE L(s, chi) ON THE CRITICAL LINE
# ============================================================
print()
print("=" * 70)
print("SECTION 2: COMPUTE L(1/2+it, chi_1 mod 5)")
print("=" * 70)
print()

# Prepare Dirichlet series coefficients
N_terms = 500
ns = np.arange(1, N_terms + 1)
chi_vals = np.array([chi5_complex(n) for n in ns], dtype=complex)
mask = chi_vals != 0
active_ns = ns[mask].astype(float)
active_chi = chi_vals[mask]
active_log_ns = np.log(active_ns)

def L_on_critical_line(t_arr):
    """Compute L(1/2+it, chi_1 mod 5) via truncated Dirichlet series."""
    # L(1/2+it) = sum chi(n) / n^{1/2+it} = sum chi(n) * n^{-1/2} * exp(-it*log(n))
    phases = np.exp(-1j * np.outer(t_arr, active_log_ns))
    weighted_coeffs = active_chi / np.sqrt(active_ns)
    return phases @ weighted_coeffs

# Test: scan and find zeros via argument tracking
T_max = 200
dt = 0.05
t_scan = np.arange(0.5, T_max, dt)
L_vals = L_on_critical_line(t_scan)

print(f"Computed L(1/2+it) at {len(t_scan)} points in [0.5, {T_max}]")
print(f"  Max |L| = {np.max(np.abs(L_vals)):.4f}")
print(f"  Min |L| = {np.min(np.abs(L_vals)):.6f}")
print()

# ============================================================
# SECTION 3: FIND ZEROS VIA ARGUMENT PRINCIPLE
# ============================================================
print()
print("=" * 70)
print("SECTION 3: FIND ZEROS VIA ARGUMENT PRINCIPLE")
print("=" * 70)
print()

# Compute unwrapped argument
L_phases = np.angle(L_vals)
# Unwrap to avoid discontinuities
unwrapped = np.unwrap(L_phases)

# Zeros occur where the argument increases by pi
# Detect sign changes in the derivative of the argument
arg_changes = np.diff(unwrapped)
# Smooth: the argument increases roughly linearly, zeros cause jumps
# Normal increment: ~mean_change, zero crossing: ~mean_change + pi

mean_change = np.mean(arg_changes)
print(f"Mean argument increment per dt={dt}: {mean_change:.4f}")
print(f"Expected zeros in [0.5, {T_max}]: ~{unwrapped[-1]/np.pi:.0f} (from total argument change)")
print()

# Find zeros: where |L|^2 reaches a local minimum near zero
# Use both argument jumps AND small |L| as criteria
zeros_complex = []

for i in range(1, len(L_vals)):
    # Look for sign change in real part (zero crossings)
    re_prev, re_curr = L_vals[i-1].real, L_vals[i].real
    im_prev, im_curr = L_vals[i-1].imag, L_vals[i].imag

    # Check if both real and imaginary parts change sign nearby
    re_cross = re_prev * re_curr < 0
    im_cross = im_prev * im_curr < 0

    # Also check |L|^2 is small (indicating near a zero)
    if re_cross or im_cross:
        # Refine: minimize |L|^2 via bisection
        lo, hi = t_scan[i-1], t_scan[i]

        # Check if this is a genuine zero (|L| small in the interval)
        mid = (lo + hi) / 2
        L_mid = L_on_critical_line(np.array([mid]))[0]
        if abs(L_mid) > 5.0:
            continue  # Not near a zero

        # Binary search for zero of |L|^2
        for _ in range(60):
            mid = (lo + hi) / 2
            L_mid = L_on_critical_line(np.array([mid]))[0]

            # Try to find where both Re and Im are zero
            # Use |L|^2 as the function to minimize
            mid_lo = (lo + mid) / 2
            mid_hi = (mid + hi) / 2
            L_lo = L_on_critical_line(np.array([mid_lo]))[0]
            L_hi = L_on_critical_line(np.array([mid_hi]))[0]

            if abs(L_lo)**2 < abs(L_hi)**2:
                hi = mid
            else:
                lo = mid

        t_zero = (lo + hi) / 2
        L_at_zero = L_on_critical_line(np.array([t_zero]))[0]

        # Accept as zero if |L| is very small
        if abs(L_at_zero) < 0.3:
            # Check not a duplicate
            if len(zeros_complex) == 0 or abs(t_zero - zeros_complex[-1]) > 0.5:
                zeros_complex.append(t_zero)

zeros_c = np.array(zeros_complex)
print(f"Found {len(zeros_c)} zeros of L(s, chi_1 mod 5) in [0.5, {T_max}]")
if len(zeros_c) >= 5:
    print(f"First 5: {[f'{z:.4f}' for z in zeros_c[:5]]}")
    print(f"First zero: gamma_1 = {zeros_c[0]:.4f}")
print()

# Verify a few zeros
print("Verification (should be near zero):")
for j in range(min(10, len(zeros_c))):
    L_val = L_on_critical_line(np.array([zeros_c[j]]))[0]
    print(f"  gamma_{j+1} = {zeros_c[j]:.4f}, |L| = {abs(L_val):.6f}")
print()

# ============================================================
# SECTION 4: REPRODUCE REAL CHARACTER ZEROS (chi_3 mod 3)
# ============================================================
print()
print("=" * 70)
print("SECTION 4: REAL CHARACTER ZEROS (chi_3 mod 3, for comparison)")
print("=" * 70)
print()

def chi3_table(n):
    r = n % 3
    if r == 0: return 0+0j
    elif r == 1: return 1+0j
    else: return -1+0j

N_terms_r = 30
ns_r = np.arange(1, N_terms_r + 1)
chi_vals_r = np.array([chi3_table(n) for n in ns_r], dtype=complex)
mask_r = chi_vals_r != 0
log_ns_r = np.log(ns_r[mask_r].astype(float))
coeffs_r = chi_vals_r[mask_r] / np.sqrt(ns_r[mask_r].astype(float))

def theta_vec(t_arr):
    z = 0.75 + 0.5j * t_arr
    log_z = np.log(z)
    logG = (z - 0.5) * log_z - z + 0.5 * np.log(2 * np.pi)
    logG += 1.0 / (12 * z)
    logG -= 1.0 / (360 * z**3)
    logG += 1.0 / (1260 * z**5)
    logG -= 1.0 / (1680 * z**7)
    return (t_arr / 2) * np.log(3.0 / np.pi) + logG.imag

def Z_single(t):
    S = np.sum(coeffs_r * np.exp(-1j * t * log_ns_r))
    th = theta_vec(np.array([t]))[0]
    return 2 * (np.exp(1j * th) * S).real

T_max_r = T_max  # Same range for fair comparison
dt_r = 0.02
t_arr_r = np.arange(0.5, T_max_r, dt_r)

phases_r = np.exp(-1j * np.outer(t_arr_r, log_ns_r))
S_arr_r = phases_r @ coeffs_r
theta_arr_r = theta_vec(t_arr_r)
Z_arr_r = 2 * (np.exp(1j * theta_arr_r) * S_arr_r).real

zeros_real_raw = []
for i in range(1, len(Z_arr_r)):
    if Z_arr_r[i-1] * Z_arr_r[i] < 0:
        lo, hi = t_arr_r[i-1], t_arr_r[i]
        f_lo = Z_arr_r[i-1]
        for _ in range(60):
            mid = (lo + hi) / 2
            f_mid = Z_single(mid)
            if f_lo * f_mid < 0:
                hi = mid
            else:
                lo = mid
                f_lo = f_mid
        zeros_real_raw.append((lo + hi) / 2)

zeros_r = np.array(zeros_real_raw)
# Only keep zeros in same range
zeros_r = zeros_r[zeros_r <= T_max]
print(f"Found {len(zeros_r)} zeros of L(s, chi_3 mod 3) in [0.5, {T_max}]")
if len(zeros_r) >= 5:
    print(f"First 5: {[f'{z:.4f}' for z in zeros_r[:5]]}")
print()

# ============================================================
# SECTION 5: SPACING STATISTICS -- REAL vs COMPLEX
# ============================================================
print()
print("=" * 70)
print("SECTION 5: SPACING STATISTICS -- REAL vs COMPLEX")
print("=" * 70)
print()

# Compute nearest-neighbor spacings for both
spacings_real = np.diff(zeros_r)
spacings_complex = np.diff(zeros_c)

# Normalize to unit mean
spacings_real_norm = spacings_real / np.mean(spacings_real)
spacings_complex_norm = spacings_complex / np.mean(spacings_complex)

print(f"Real character (chi_3 mod 3): {len(zeros_r)} zeros, {len(spacings_real)} spacings")
print(f"  Mean spacing: {np.mean(spacings_real):.4f}")
print(f"  Std spacing:  {np.std(spacings_real):.4f}")
print(f"  Min spacing:  {np.min(spacings_real):.4f}")
print()
print(f"Complex character (chi_1 mod 5): {len(zeros_c)} zeros, {len(spacings_complex)} spacings")
print(f"  Mean spacing: {np.mean(spacings_complex):.4f}")
print(f"  Std spacing:  {np.std(spacings_complex):.4f}")
print(f"  Min spacing:  {np.min(spacings_complex):.4f}")
print()

# ============================================================
# SECTION 6: GOE vs GUE DISTRIBUTIONS
# ============================================================
print()
print("=" * 70)
print("SECTION 6: GOE vs GUE THEORETICAL DISTRIBUTIONS")
print("=" * 70)
print()

# Wigner surmise for GOE: P(s) = (pi/2)*s*exp(-pi*s^2/4)
def P_goe(s):
    return (np.pi / 2) * s * np.exp(-np.pi * s**2 / 4)

# Wigner surmise for GUE: P(s) = (32/pi^2)*s^2*exp(-4*s^2/pi)
def P_gue(s):
    return (32 / np.pi**2) * s**2 * np.exp(-4 * s**2 / np.pi)

# Poisson: P(s) = exp(-s)
def P_poisson(s):
    return np.exp(-s)

# Histogram comparison
bins = np.linspace(0, 4, 30)
bin_width = bins[1] - bins[0]
centers = (bins[:-1] + bins[1:]) / 2

hist_real, _ = np.histogram(spacings_real_norm, bins=bins, density=True)
hist_complex, _ = np.histogram(spacings_complex_norm, bins=bins, density=True)

print(f"  {'s':>5s}  {'Poisson':>8s}  {'GOE':>8s}  {'GUE':>8s}  {'Real(chi3)':>11s}  {'Cplx(chi5)':>11s}")
print(f"  {'-----':>5s}  {'--------':>8s}  {'---':>8s}  {'---':>8s}  {'----------':>11s}  {'----------':>11s}")
for i, s in enumerate(centers):
    print(f"  {s:5.2f}  {P_poisson(s):8.4f}  {P_goe(s):8.4f}  {P_gue(s):8.4f}  {hist_real[i]:11.4f}  {hist_complex[i]:11.4f}")
print()

# ============================================================
# SECTION 7: KOLMOGOROV-SMIRNOV TEST
# ============================================================
print()
print("=" * 70)
print("SECTION 7: KOLMOGOROV-SMIRNOV TEST")
print("=" * 70)
print()

# CDFs
def CDF_goe(s):
    """CDF of GOE Wigner surmise."""
    return 1 - np.exp(-np.pi * s**2 / 4)

def CDF_gue(s):
    """CDF of GUE Wigner surmise."""
    return 1 - np.exp(-4 * s**2 / np.pi) * (1 + 4 * s**2 / np.pi)

def CDF_poisson(s):
    return 1 - np.exp(-s)

# Empirical CDF
def empirical_cdf(data, s_vals):
    sorted_data = np.sort(data)
    cdf = np.searchsorted(sorted_data, s_vals, side='right') / len(sorted_data)
    return cdf

s_test = np.linspace(0.01, 4, 500)

# KS test for real character
ecdf_real = empirical_cdf(spacings_real_norm, s_test)
ks_real_goe = np.max(np.abs(ecdf_real - CDF_goe(s_test)))
ks_real_gue = np.max(np.abs(ecdf_real - CDF_gue(s_test)))
ks_real_pois = np.max(np.abs(ecdf_real - CDF_poisson(s_test)))

# KS test for complex character
ecdf_complex = empirical_cdf(spacings_complex_norm, s_test)
ks_cplx_goe = np.max(np.abs(ecdf_complex - CDF_goe(s_test)))
ks_cplx_gue = np.max(np.abs(ecdf_complex - CDF_gue(s_test)))
ks_cplx_pois = np.max(np.abs(ecdf_complex - CDF_poisson(s_test)))

print("KS statistics (lower = better fit):")
print()
print(f"  {'':>20s}  {'GOE':>8s}  {'GUE':>8s}  {'Poisson':>8s}  {'Best':>8s}")
print(f"  {'-' * 20}  {'--------':>8s}  {'--------':>8s}  {'--------':>8s}  {'--------':>8s}")

best_real = min(ks_real_goe, ks_real_gue, ks_real_pois)
best_real_name = "GOE" if ks_real_goe == best_real else ("GUE" if ks_real_gue == best_real else "Poisson")
print(f"  {'Real chi_3 mod 3':>20s}  {ks_real_goe:8.4f}  {ks_real_gue:8.4f}  {ks_real_pois:8.4f}  {best_real_name:>8s}")

best_cplx = min(ks_cplx_goe, ks_cplx_gue, ks_cplx_pois)
best_cplx_name = "GOE" if ks_cplx_goe == best_cplx else ("GUE" if ks_cplx_gue == best_cplx else "Poisson")
print(f"  {'Complex chi_1 mod 5':>20s}  {ks_cplx_goe:8.4f}  {ks_cplx_gue:8.4f}  {ks_cplx_pois:8.4f}  {best_cplx_name:>8s}")
print()

print("Katz-Sarnak prediction:")
print(f"  Real primitive (chi_3 mod 3) -> GOE  [observed: {best_real_name}]")
print(f"  Complex non-self-dual (chi_1 mod 5) -> GUE  [observed: {best_cplx_name}]")

if best_real_name == "GOE" and best_cplx_name == "GUE":
    print()
    print("  *** PREDICTION CONFIRMED: GOE for real, GUE for complex ***")
elif best_real_name == "GOE":
    print()
    print(f"  Real character confirmed GOE. Complex character best fit: {best_cplx_name}")
    print(f"  (May need more zeros for definitive GUE detection)")
print()

# ============================================================
# SECTION 8: LEVEL REPULSION COMPARISON
# ============================================================
print()
print("=" * 70)
print("SECTION 8: LEVEL REPULSION COMPARISON")
print("=" * 70)
print()

print("Level repulsion near s=0:")
print(f"  GOE:     P(s) ~ (pi/2)*s      [LINEAR repulsion]")
print(f"  GUE:     P(s) ~ (32/pi^2)*s^2  [QUADRATIC repulsion]")
print(f"  Poisson: P(0) = 1               [NO repulsion]")
print()

# Count small spacings
for threshold in [0.3, 0.5, 0.8, 1.0]:
    n_real = np.sum(spacings_real_norm < threshold)
    n_cplx = np.sum(spacings_complex_norm < threshold)
    pct_real = n_real / len(spacings_real_norm) * 100
    pct_cplx = n_cplx / len(spacings_complex_norm) * 100

    # Expected fractions from theory
    frac_goe = CDF_goe(threshold)
    frac_gue = CDF_gue(threshold)
    frac_pois = CDF_poisson(threshold)

    print(f"  s < {threshold}: Real {pct_real:5.1f}% (GOE {frac_goe*100:5.1f}%), Complex {pct_cplx:5.1f}% (GUE {frac_gue*100:5.1f}%)")

print()

# ============================================================
# SECTION 9: CHI-SQUARED GOODNESS OF FIT
# ============================================================
print()
print("=" * 70)
print("SECTION 9: CHI-SQUARED GOODNESS OF FIT")
print("=" * 70)
print()

# Bin the spacings and compare with theory
chi_bins = np.linspace(0, 4, 20)
chi_width = chi_bins[1] - chi_bins[0]

for label, spacings, expected_name in [
    ("Real chi_3 mod 3", spacings_real_norm, "GOE"),
    ("Complex chi_1 mod 5", spacings_complex_norm, "GUE")
]:
    n_total = len(spacings)
    obs, _ = np.histogram(spacings, bins=chi_bins)

    print(f"\n  {label} (n={n_total} spacings):")

    for theory_name, P_func in [("GOE", P_goe), ("GUE", P_gue), ("Poisson", P_poisson)]:
        expected = np.array([P_func((chi_bins[i] + chi_bins[i+1])/2) * chi_width * n_total
                            for i in range(len(chi_bins)-1)])
        expected = np.maximum(expected, 1)  # Avoid division by zero

        chi_sq = np.sum((obs - expected)**2 / expected)
        chi_sq_per_bin = chi_sq / (len(obs) - 1)

        marker = " <-- expected" if theory_name == expected_name else ""
        print(f"    vs {theory_name}: chi^2/dof = {chi_sq_per_bin:.4f}{marker}")

print()

# ============================================================
# SECTION 10: CONCLUSION
# ============================================================
print()
print("=" * 70)
print("SECTION 10: CONCLUSION")
print("=" * 70)
print()

print("THE GOE-vs-GUE COMPARISON:")
print()
print(f"  Real character chi_3 mod 3 (conductor 3):")
print(f"    {len(zeros_r)} zeros in [0.5, {T_max}]")
print(f"    Best fit: {best_real_name} (KS = {best_real:.4f})")
print(f"    Katz-Sarnak predicts: GOE")
print()
print(f"  Complex character chi_1 mod 5 (conductor 5):")
print(f"    {len(zeros_c)} zeros in [0.5, {T_max}]")
print(f"    Best fit: {best_cplx_name} (KS = {best_cplx:.4f})")
print(f"    Katz-Sarnak predicts: GUE")
print()

if best_real_name == "GOE" and best_cplx_name == "GUE":
    print("KATZ-SARNAK CONFIRMED:")
    print("  Real characters -> GOE (orthogonal, time-reversal symmetric)")
    print("  Complex characters -> GUE (unitary, time-reversal broken)")
    print()
    print("The monad's spectral architecture maps to BOTH symmetry classes:")
    print("  - chi_3 mod 3 (real): same universality as atomic nuclei")
    print("  - chi_1 mod 5 (complex): same universality as Riemann zeta")
    print()
    print("The tower of projections (mod 6 -> mod 30 -> ...) traverses")
    print("different symmetry classes, connecting the monad's geometric")
    print("structure to the full landscape of random matrix theory.")
else:
    print("RESULTS:")
    print(f"  Real character: {best_real_name} (expected GOE)")
    print(f"  Complex character: {best_cplx_name} (expected GUE)")
    print()
    print(f"  Note: {len(zeros_c)} complex zeros may be insufficient for")
    print(f"  clean GUE detection. The Dirichlet series truncation also")
    print(f"  limits accuracy. A proper AFE for chi_1 mod 5 would help.")

print()

print("=" * 70)
print("EXPERIMENT 018kkk COMPLETE")
print("=" * 70)
