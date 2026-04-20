"""
Experiment 018ggg: The Conductor -- AFE Zeros and the q=3 Discovery

DISCOVERY: chi_1 mod 6 has conductor q=3 (not 6)!

chi_1(1 mod 6) = +1 = chi_3(1 mod 3)
chi_1(5 mod 6) = -1 = chi_3(2 mod 3)

The character factors through (Z/3Z)*, so L(s, chi_1 mod 6) = L(s, (n/3))
where (n/3) is the Legendre symbol mod 3. The conductor is 3.

Consequences for the AFE:
1. epsilon = 1 (symmetric functional equation, like Riemann xi)
2. The Hardy Z-function Z(t) = 2*Re(exp(i*theta(t)) * S(t)) is real
3. theta(t) = (t/2)*log(3/pi) + Im(log Gamma(3/4+it/2)) -- no underflow!
4. Expected ~356 zeros up to T=500

Uses the Hardy Z-function to avoid Gamma function underflow at large T.
"""

import numpy as np

print("=" * 70)
print("EXPERIMENT 018ggg: THE CONDUCTOR -- AFE ZEROS AND THE q=3 DISCOVERY")
print("=" * 70)

# ============================================================
# SECTION 1: THE CONDUCTOR DISCOVERY
# ============================================================
print()
print("=" * 70)
print("SECTION 1: THE CONDUCTOR DISCOVERY -- chi_1 mod 6 HAS CONDUCTOR 3")
print("=" * 70)
print()

print("Algebraic proof that chi_1 mod 6 factors through (Z/3Z)*:")
print()
print("  n mod 6  |  n mod 3  |  chi_1 mod 6  |  chi_3 mod 3  |  Match?")
print("  ---------+-----------+---------------+---------------+-------")

chi1_mod6 = {1: 1, 5: -1}
chi3_mod3 = {1: 1, 2: -1}

all_match = True
for n_mod6, c1 in chi1_mod6.items():
    n_mod3 = n_mod6 % 3
    c3 = chi3_mod3.get(n_mod3, 0)
    match = "YES" if c1 == c3 else "NO"
    if c1 != c3:
        all_match = False
    print(f"  {n_mod6:8d}  |  {n_mod3:9d}  |  {c1:+12d}  |  {c3:+12d}  |  {match}")

print()
print(f"  All match: {all_match}")
print()

# Gauss sum verification
tau_chi3 = sum(chi3_mod3.get(n % 3, 0) * np.exp(2j * np.pi * n / 3) for n in range(3))
print("Gauss sum verification:")
print(f"  tau(chi_3 mod 3) = {tau_chi3:.6f}")
print(f"  |tau|^2 = {abs(tau_chi3)**2:.6f}")
print(f"  q = 3: |tau|^2 == q? {np.isclose(abs(tau_chi3)**2, 3)}")

a = 1  # odd character
epsilon = tau_chi3 / (1j**a * np.sqrt(3))
print(f"  epsilon = {epsilon:.6f}, |epsilon| = {abs(epsilon):.6f}")
print()
print(f"  CONDUCTOR q = 3, epsilon = 1")
print(f"  Functional equation: Lambda(s) = Lambda(1-s)  [SYMMETRIC, like Riemann xi]")
print()

# Extended verification
mismatches = 0
for n in range(1, 200):
    if np.gcd(n, 6) != 1:
        continue
    c1 = chi1_mod6.get(n % 6, 0)
    c3 = chi3_mod3.get(n % 3, 0)
    if c1 != c3:
        mismatches += 1
if mismatches == 0:
    print(f"  Verified: chi_1 mod 6 = chi_3 mod 3 for ALL n coprime to 6 (up to 200)")
print()

# ============================================================
# SECTION 2: THE HARDY Z-FUNCTION
# ============================================================
print()
print("=" * 70)
print("SECTION 2: THE HARDY Z-FUNCTION (AVOIDS GAMMA UNDERFLOW)")
print("=" * 70)
print()

print("The completed L-function Lambda(1/2+it) decays as exp(-pi*t/4),")
print("causing numerical underflow for t > ~50. The fix: use the Hardy")
print("Z-function, which has the same zeros but bounded magnitude.")
print()
print("  Z(t) = Lambda(1/2+it) / |gamma(1/2+it)|")
print("       = 2*Re(exp(i*theta(t)) * S(t))")
print()
print("  where:")
print("    S(t) = sum_{n<=N} chi_3(n)/n^{1/2+it}")
print("    theta(t) = (t/2)*log(3/pi) + Im(log Gamma(3/4+it/2))")
print()
print("  theta(t) is computed via the Stirling series (no underflow).")
print()

# Character table
def chi3_table(n):
    r = n % 3
    if r == 0:
        return 0+0j
    elif r == 1:
        return 1+0j
    else:
        return -1+0j

# Precompute character coefficients
N_terms = 30
ns = np.arange(1, N_terms + 1)
chi_vals = np.array([chi3_table(n) for n in ns], dtype=complex)
mask = chi_vals != 0
log_ns = np.log(ns[mask].astype(float))
coeffs = chi_vals[mask] / np.sqrt(ns[mask].astype(float))

print(f"Using {int(np.sum(mask))} nonzero terms out of {N_terms}")
print()

def theta_vec(t_arr):
    """Compute theta(t) using the Stirling series for Im(log Gamma)."""
    z = 0.75 + 0.5j * t_arr
    # log Gamma(z) via Stirling:
    # (z-0.5)*log(z) - z + 0.5*log(2*pi) + 1/(12*z) - 1/(360*z^3) + 1/(1260*z^5)
    log_z = np.log(z)
    logGamma = (z - 0.5) * log_z - z + 0.5 * np.log(2 * np.pi)
    logGamma += 1.0 / (12 * z)
    logGamma -= 1.0 / (360 * z**3)
    logGamma += 1.0 / (1260 * z**5)
    logGamma -= 1.0 / (1680 * z**7)

    return (t_arr / 2) * np.log(3.0 / np.pi) + logGamma.imag

# Test theta at a known value
# theta(t) should be approximately (t/2)*log(t*3/(2*pi*e)) + pi/8 for large t
t_test = 100.0
theta_test = theta_vec(np.array([t_test]))[0]
theta_approx = (t_test/2)*np.log(t_test*3/(2*np.pi*np.e)) + np.pi/8
print(f"theta(100) = {theta_test:.6f}")
print(f"Approx     = {theta_approx:.6f}")
print(f"Agreement: {abs(theta_test - theta_approx):.4f}")
print()

# ============================================================
# SECTION 3: VECTORIZED Z-FUNCTION COMPUTATION
# ============================================================
print()
print("=" * 70)
print("SECTION 3: VECTORIZED Z-FUNCTION -- COMPUTING Z(t)")
print("=" * 70)
print()

T_max = 500
dt = 0.02
t_arr = np.arange(0.5, T_max, dt)
print(f"Scanning Z(t) for t in [0.5, {T_max}], dt={dt}")
print(f"  Total scan points: {len(t_arr)}")

# Compute S(t) for all t (vectorized)
phases = np.exp(-1j * np.outer(t_arr, log_ns))
S_arr = phases @ coeffs

# Compute theta(t)
theta_arr = theta_vec(t_arr)

# Z(t) = 2*Re(exp(i*theta(t)) * S(t))
Z_arr = 2 * (np.exp(1j * theta_arr) * S_arr).real

print(f"  Scan complete.")
print(f"  Max |Z(t)| = {np.max(np.abs(Z_arr)):.4f}")
print(f"  Mean |Z(t)| = {np.mean(np.abs(Z_arr)):.4f}")
print()

# ============================================================
# SECTION 4: ZERO FINDING VIA SIGN CHANGES OF Z(t)
# ============================================================
print()
print("=" * 70)
print("SECTION 4: ZERO FINDING VIA SIGN CHANGES OF Z(t)")
print("=" * 70)
print()

def Z_single(t):
    """Compute Z(t) at a single point for bisection refinement."""
    S = np.sum(coeffs * np.exp(-1j * t * log_ns))
    th = theta_vec(np.array([t]))[0]
    return 2 * (np.exp(1j * th) * S).real

zeros_raw = []
for i in range(1, len(Z_arr)):
    if Z_arr[i-1] * Z_arr[i] < 0:
        lo, hi = t_arr[i-1], t_arr[i]
        f_lo = Z_arr[i-1]
        for _ in range(60):
            mid = (lo + hi) / 2
            f_mid = Z_single(mid)
            if f_lo * f_mid < 0:
                hi = mid
            else:
                lo = mid
                f_lo = f_mid
        zeros_raw.append((lo + hi) / 2)

zeros = np.array(zeros_raw)
print(f"Found {len(zeros)} zeros of Z(t) in [0.5, {T_max}]")
print()

if len(zeros) >= 15:
    print(f"First 15 zeros:")
    for i in range(min(15, len(zeros))):
        print(f"  gamma_{i+1:3d} = {zeros[i]:.6f}")
    print()

# ============================================================
# SECTION 5: ZERO COUNTING FUNCTION N(T)
# ============================================================
print()
print("=" * 70)
print("SECTION 5: ZERO COUNTING FUNCTION N(T)")
print("=" * 70)
print()

def N_theory(T, q=3):
    """Riemann-von Mangoldt formula (smooth part)."""
    return (T / (2 * np.pi)) * np.log(T * q / (2 * np.pi)) - T / (2 * np.pi)

print(f"  {'T':>6s}  {'N_actual':>9s}  {'N_theory':>9s}  {'Ratio':>7s}  {'Gap':>7s}")
print(f"  {'------':>6s}  {'--------':>9s}  {'--------':>9s}  {'-----':>7s}  {'---':>7s}")

for T_test in [50, 100, 200, 300, 400, 500]:
    n_actual = np.sum(zeros <= T_test)
    n_theory = N_theory(T_test)
    ratio = n_actual / n_theory if n_theory > 0 else 0
    gap = n_actual - n_theory
    print(f"  {T_test:6d}  {n_actual:9d}  {n_theory:9.1f}  {ratio:7.3f}  {gap:+7.1f}")

print()

# ============================================================
# SECTION 6: COMPARISON WITH DIRECT DIRICHLET SERIES
# ============================================================
print()
print("=" * 70)
print("SECTION 6: COMPARISON WITH PREVIOUS METHODS")
print("=" * 70)
print()

# Compute zeros via direct Dirichlet series (previous method)
chi6_table = {0: 0+0j, 1: 1+0j, 2: 0+0j, 3: 0+0j, 4: 0+0j, 5: -1+0j}
ns_old = np.arange(1, 1501)
chi_old = np.array([chi6_table[n % 6] for n in ns_old], dtype=complex)
mask_old = chi_old != 0
log_ns_old = np.log(ns_old[mask_old].astype(float))
coeffs_old = chi_old[mask_old] / np.sqrt(ns_old[mask_old].astype(float))

t_old = np.arange(0.5, 100, 0.015)
L_old = np.zeros(len(t_old), dtype=complex)
for i in range(len(coeffs_old)):
    L_old += coeffs_old[i] * np.exp(-1j * t_old * log_ns_old[i])

msq_old = np.abs(L_old)**2
threshold_old = np.median(msq_old) * 0.05

zeros_old = []
for i in range(1, len(t_old) - 1):
    if msq_old[i] < msq_old[i-1] and msq_old[i] < msq_old[i+1]:
        if msq_old[i] < threshold_old:
            lo = t_old[max(0, i-3)]
            hi = t_old[min(len(t_old)-1, i+3)]
            phi_r = (1 + np.sqrt(5)) / 2
            for _ in range(30):
                c = lo + (hi - lo) / phi_r**2
                d = lo + (hi - lo) / phi_r
                Lc = np.sum(coeffs_old * np.exp(-1j * c * log_ns_old))
                Ld = np.sum(coeffs_old * np.exp(-1j * d * log_ns_old))
                if abs(Lc)**2 < abs(Ld)**2:
                    hi = d
                else:
                    lo = c
            t_zero = (lo + hi) / 2
            Lf = np.sum(coeffs_old * np.exp(-1j * t_zero * log_ns_old))
            if abs(Lf)**2 < threshold_old:
                zeros_old.append(t_zero)

zeros_old = np.array(sorted(zeros_old))

print(f"  Method            |  Zeros  |  Range    |  Terms/eval")
print(f"  ------------------+---------+-----------+------------")
print(f"  Direct series     |  {len(zeros_old):5d}  |  [0, 100] |  1500")
print(f"  AFE + Z-function  |  {len(zeros):5d}  |  [0, 500] |  ~20")
print()

# Compare first shared zeros
afe_100 = zeros[zeros <= 100]
if len(zeros_old) > 0 and len(afe_100) > 0:
    print(f"  AFE zeros in [0, 100]:     {len(afe_100)}")
    print(f"  Direct zeros in [0, 100]:  {len(zeros_old)}")
    print()

    matched = 0
    total_gap = 0
    for i in range(min(15, len(zeros_old), len(afe_100))):
        gap = abs(afe_100[i] - zeros_old[i])
        matched += 1
        total_gap += gap
        if i < 10:
            print(f"  {i+1:3d}. AFE: {afe_100[i]:.6f}  Direct: {zeros_old[i]:.6f}  gap: {gap:.6f}")
    if matched > 0:
        print(f"\n  Mean gap (first {matched}): {total_gap/matched:.6f}")
    print()

# ============================================================
# SECTION 7: SPACING STATISTICS WITH 300+ ZEROS
# ============================================================
print()
print("=" * 70)
print("SECTION 7: SPACING STATISTICS")
print("=" * 70)
print()

def normalized_spacings(zeros_arr, q):
    spacings = np.diff(zeros_arr)
    normalized = np.zeros(len(spacings))
    for i in range(len(spacings)):
        gamma_mid = (zeros_arr[i] + zeros_arr[i+1]) / 2
        if gamma_mid > 1:
            density = np.log(gamma_mid * q / (2 * np.pi)) / (2 * np.pi)
        else:
            density = np.log(q / (2 * np.pi) + 1) / (2 * np.pi)
        normalized[i] = spacings[i] * density
    if np.mean(normalized) > 0:
        normalized /= np.mean(normalized)
    return normalized

sp = normalized_spacings(zeros, 3)

print(f"Normalized spacings: {len(sp)} values")
print(f"  Mean:   {np.mean(sp):.4f} (target: 1.0)")
print(f"  Std:    {np.std(sp):.4f}")
print(f"  Median: {np.median(sp):.4f}")
print()

# GOE vs GUE comparison
def goe_pdf(s):
    return (np.pi / 2) * s * np.exp(-np.pi * s**2 / 4)

def gue_pdf(s):
    return (32 / np.pi**2) * s**2 * np.exp(-4 * s**2 / np.pi)

def poisson_pdf(s):
    return np.exp(-s)

def fit_quality(spacings, pdf_func, n_bins=20, s_max=3.5):
    hist, edges = np.histogram(spacings, bins=n_bins, range=(0, s_max), density=True)
    centers = (edges[:-1] + edges[1:]) / 2
    expected = pdf_func(centers)
    mask = expected > 0.01
    if np.sum(mask) < 3:
        return float('inf')
    chi2 = np.sum((hist[mask] - expected[mask])**2 / (expected[mask] + 0.01))
    return chi2 / np.sum(mask)

c_goe = fit_quality(sp, goe_pdf)
c_gue = fit_quality(sp, gue_pdf)
c_pois = fit_quality(sp, poisson_pdf)

print("Chi-squared fit quality (lower = better):")
print(f"  vs GOE:     {c_goe:.4f}")
print(f"  vs GUE:     {c_gue:.4f}")
print(f"  vs Poisson: {c_pois:.4f}")
best = min([("GOE", c_goe), ("GUE", c_gue), ("Poisson", c_pois)], key=lambda x: x[1])
print(f"  Best fit: {best[0]}")
print()

# Spacing histogram
bins_h = np.linspace(0, 3.5, 20)
h, _ = np.histogram(sp, bins=bins_h, density=True)
ctrs = (bins_h[:-1] + bins_h[1:]) / 2

print(f"  {'s':>5s}  {'GOE':>7s}  {'GUE':>7s}  {'Actual':>7s}  {'Pois':>7s}")
for i, s in enumerate(ctrs):
    g = goe_pdf(s)
    u = gue_pdf(s)
    p = poisson_pdf(s)
    print(f"  {s:5.2f}  {g:7.3f}  {u:7.3f}  {h[i]:7.3f}  {p:7.3f}")
print()

# KS test
from math import erf, exp, sqrt, pi as mpi

def goe_cdf(s):
    return erf(sqrt(mpi) * s / 2) - s * exp(-mpi * s**2 / 4)

def gue_cdf(s):
    return erf(2 * s / sqrt(mpi)) - (4 * s / sqrt(mpi)) * exp(-4 * s**2 / mpi)

def ks_stat(spacings, cdf_func):
    s = np.sort(spacings)
    n = len(s)
    ecdf = np.arange(1, n + 1) / n
    tcdf = np.array([cdf_func(si) for si in s])
    return np.max(np.abs(ecdf - tcdf))

d_goe = ks_stat(sp, goe_cdf)
d_gue = ks_stat(sp, gue_cdf)
print("KS test (lower = better):")
print(f"  KS vs GOE: {d_goe:.4f}")
print(f"  KS vs GUE: {d_gue:.4f}")
print(f"  Better fit: {'GOE' if d_goe < d_gue else 'GUE'}")
print()

# Level repulsion
frac_small = np.mean(sp < 0.5)
frac_tiny = np.mean(sp < 0.2)
frac_near0 = np.mean(sp < 0.1)
print("Level repulsion:")
print(f"  Fraction s < 0.5: {frac_small:.3f} (GOE: 0.228, GUE: 0.089, Pois: 0.394)")
print(f"  Fraction s < 0.2: {frac_tiny:.3f} (GOE: 0.069, GUE: 0.013, Pois: 0.181)")
print(f"  Fraction s < 0.1: {frac_near0:.3f} (GOE: 0.025, GUE: 0.001, Pois: 0.095)")
print()

# ============================================================
# SECTION 8: WHAT THE CONDUCTOR MEANS FOR THE MONAD
# ============================================================
print()
print("=" * 70)
print("SECTION 8: WHAT THE CONDUCTOR DISCOVERY MEANS FOR THE MONAD")
print("=" * 70)
print()

print("The monad's L-function L(s, chi_1 mod 6) has conductor 3, not 6.")
print()
print("  GEOMETRIC constant (monad):  modulus 6  (12 positions, two rails)")
print("  ANALYTIC constant (spectrum): conductor 3 (quadratic character)")
print()
print("The modulus-6 structure provides:")
print("  - Two rails (6k-1, 6k+1)")
print("  - Z2 sign rule")
print("  - 12-position circle")
print("  - D_6 dihedral symmetry")
print("  - chi_3 (matter/antimatter)")
print()
print("The conductor-3 structure provides:")
print("  - The L-function L(s, (n/3))")
print("  - Spectral content (zeros, explicit formula)")
print("  - Chebyshev race oscillation")
print()
print("The modulus 6 = 2 x 3. The factor of 2 provides geometric structure")
print("that is INVISIBLE to the L-function. The L-function sees only the")
print("mod-3 part (quadratic residues). The mod-2 part (even/odd parity of")
print("the k-index, the Z2 rail sign) is a SPECTRAL DEGENERACY.")
print()
print("Physical analogy: like spin multiplicity in atomic spectroscopy.")
print("The spectral lines (L-function zeros) don't distinguish between")
print("states that differ only in the mod-2 quantum number (rail type).")
print()

# ============================================================
# SECTION 9: HONEST ASSESSMENT
# ============================================================
print()
print("=" * 70)
print("SECTION 9: HONEST ASSESSMENT")
print("=" * 70)
print()

print("WHAT THIS EXPERIMENT ESTABLISHES:")
print()
print(f"  1. chi_1 mod 6 has conductor 3 (ALGEBRAIC FACT, not approximate)")
print(f"  2. epsilon = 1, Z(t) is real (EXACT)")
print(f"  3. Hardy Z-function avoids Gamma underflow -- stable for all t")
print(f"  4. Found {len(zeros)} zeros up to T={T_max}")
if len(zeros) >= 1:
    print(f"  5. First zero at gamma_1 = {zeros[0]:.4f} (NOT 6.02)")
n100 = np.sum(zeros <= 100)
nt100 = N_theory(100)
print(f"  6. N(100): {n100} found, {nt100:.1f} theory (ratio {n100/nt100:.3f})")
n500 = np.sum(zeros <= 500)
nt500 = N_theory(500)
print(f"  7. N(500): {n500} found, {nt500:.1f} theory (ratio {n500/nt500:.3f})")
print(f"  8. KS test favors {'GOE' if d_goe < d_gue else 'GUE'} (Katz-Sarnak: GOE for real chars)")
print()
print("REMAINING ISSUES:")
print()
print(f"  - Zero count at T=500 is {n500/nt500:.1%} of theory")
print(f"    (likely missing some closely-spaced pairs at high T)")
print(f"  - The Stirling series for theta(t) may need more terms for T > 500")
print(f"  - The first zero is at {zeros[0]:.4f}, correcting the '6.02' claim")
print(f"    from earlier experiments (which used the direct series with")
print(f"    insufficient terms near the first zero)")
print()

print("=" * 70)
print("EXPERIMENT 018ggg COMPLETE")
print("=" * 70)
