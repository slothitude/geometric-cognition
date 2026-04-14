"""
Experiment 017: Zeta-Zero Interference Structure
=================================================
Tests whether the zeros of the Riemann zeta function produce
detectable structure in primes beyond the PNT density law.

This is the legitimate "wave interference" model for primes.
The explicit formula:

  psi(x) ~ x - sum_rho x^rho / rho

where rho = 1/2 + i*gamma are non-trivial zeta zeros, gives an
exact relationship between zeta zeros and prime counting.

Five tests:
1. Spectral analysis: detect oscillations at gamma frequencies
2. Direct zero-wave correlation with primality
3. Prime counting error vs zero sum (should work — established math)
4. Random zero control (do actual zeros matter?)
5. Local prime probability modulation
"""

import numpy as np
from math import log, pi, sqrt
from scipy.stats import pearsonr
from scipy.signal import periodogram
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ====================================================================
#  FAST SIEVE
# ====================================================================
def sieve(N):
    is_prime = np.ones(N, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return is_prime

N_MAX = 200_000
print("=" * 70)
print("  EXPERIMENT 017: ZETA-ZERO INTERFERENCE STRUCTURE")
print("=" * 70)
print()

is_prime_arr = sieve(N_MAX)

# ====================================================================
#  ZETA ZEROS (first 15 imaginary parts)
# ====================================================================
# These are well-established constants, computed to high precision
# by Odlyzko and others. We use 12-digit approximations.
GAMMAS = np.array([
    14.134725142,    # gamma_1
    21.022039639,    # gamma_2
    25.010857580,    # gamma_3
    30.424876126,    # gamma_4
    32.935061588,    # gamma_5
    37.586178159,    # gamma_6
    40.918719012,    # gamma_7
    43.327073281,    # gamma_8
    48.005150881,    # gamma_9
    49.773832478,    # gamma_10
    52.970321478,    # gamma_11
    56.446247696,    # gamma_12
    59.347044003,    # gamma_13
    60.831778525,    # gamma_14
    65.112544048,    # gamma_15
])

print(f"  Zeta zeros: {len(GAMMAS)}")
print(f"  gamma range: [{GAMMAS[0]:.2f}, {GAMMAS[-1]:.2f}]")
print()

# ====================================================================
#  HELPER: ZETA WAVE FUNCTIONS
# ====================================================================
def zeta_wave(n, gammas):
    """Sum of cos(gamma * log(n)) for all gammas."""
    log_n = np.log(n)
    return np.sum(np.cos(gammas * log_n))

def zeta_wave_array(ns, gammas):
    """Vectorized zeta wave over array of n values."""
    log_ns = np.log(ns)
    result = np.zeros(len(ns))
    for g in gammas:
        result += np.cos(g * log_ns)
    return result

def zeta_wave_weighted(n, gammas):
    """Weighted by 1/sqrt(n) — closer to the explicit formula."""
    log_n = np.log(n)
    return np.sum(np.cos(gammas * log_n)) / sqrt(n)

# ====================================================================
#  BUILD DATA
# ====================================================================
ns = np.arange(5, N_MAX, dtype=np.float64)
log_ns = np.log(ns)
prime_indicator = is_prime_arr[ns.astype(int)].astype(float)

# Expected PNT density for each n
pnt_density = 1.0 / log_ns

print(f"  Range: [5, {N_MAX}]")
print(f"  Primes: {prime_indicator.sum():.0f}")
print(f"  PNT expected: {pnt_density.sum():.0f}")
print()

# ====================================================================
#  TEST 1: SPECTRAL ANALYSIS IN LOG-SPACE
# ====================================================================
print("=" * 70)
print("  TEST 1: LOG-SPACE OSCILLATION DETECTION")
print("=" * 70)
print()
print("  Remove PNT density, then look for periodic components")
print("  in the prime residual signal.")
print()

# Build prime counting residual in log-space
# Create uniform grid in log-space
log_grid = np.linspace(log(5), log(N_MAX), 10000)
grid_step = log_grid[1] - log_grid[0]

# For each grid point, count primes in a small window
bin_width = 0.01  # in log-space
prime_density_grid = np.zeros(len(log_grid))
total_density_grid = np.zeros(len(log_grid))

for i, lg in enumerate(log_grid):
    # Count lattice points in [lg - bw/2, lg + bw/2]
    lo = np.exp(lg - bin_width / 2)
    hi = np.exp(lg + bin_width / 2)
    lo_int = max(5, int(lo))
    hi_int = min(N_MAX - 1, int(hi) + 1)

    count = hi_int - lo_int
    if count > 0:
        prime_count = is_prime_arr[lo_int:hi_int].sum()
        prime_density_grid[i] = prime_count / count
        total_density_grid[i] = count

# PNT expected density on grid
pnt_grid = 1.0 / log_grid

# Residual (observed - expected)
valid = total_density_grid > 10
residual = np.zeros(len(log_grid))
residual[valid] = prime_density_grid[valid] - pnt_grid[valid]

# Spectral analysis
freqs, power = periodogram(residual[valid], fs=1.0 / grid_step)

# Expected peak frequencies from zeta zeros
print(f"  Expected peak frequencies (from zeta zeros):")
for i, g in enumerate(GAMMAS[:5]):
    print(f"    gamma_{i+1} = {g:.3f}")
print()

# Find top peaks in spectrum
top_idx = np.argsort(power)[-20:][::-1]
top_freqs = freqs[top_idx]
top_powers = power[top_idx]

print(f"  Top spectral peaks:")
for i in range(min(10, len(top_idx))):
    freq = top_freqs[i]
    pwr = top_powers[i]

    # Check if close to any gamma
    closest_gamma = GAMMAS[np.argmin(np.abs(GAMMAS - freq))]
    dist = abs(freq - closest_gamma)
    match = f"~gamma_{np.argmin(np.abs(GAMMAS - freq))+1}" if dist < 1.0 else ""

    print(f"    freq = {freq:.3f}, power = {pwr:.6f}  {match}")

print()

# Check specifically at gamma frequencies
print(f"  Power at zeta-zero frequencies:")
for g in GAMMAS[:5]:
    idx = np.argmin(np.abs(freqs - g))
    pwr = power[idx]
    # Compare to median power
    median_pwr = np.median(power[freqs > 1.0])
    ratio = pwr / max(median_pwr, 1e-10)
    print(f"    gamma={g:.2f}: power={pwr:.6f} ({ratio:.1f}x median)")

print()

# ====================================================================
#  TEST 2: DIRECT ZERO-WAVE CORRELATION WITH PRIMALITY
# ====================================================================
print("=" * 70)
print("  TEST 2: DIRECT ZERO-WAVE vs PRIMALITY")
print("=" * 70)
print()

# Use 6k±1 lattice for clean signal
K_MAX = N_MAX // 6 + 1
lattice_k = []
lattice_n = []
lattice_sign = []

for k in range(1, K_MAX + 1):
    for sign in (-1, +1):
        n = 6 * k + sign
        if n < 5 or n > N_MAX:
            continue
        lattice_k.append(k)
        lattice_n.append(n)
        lattice_sign.append(sign)

lattice_k = np.array(lattice_k, dtype=np.float64)
lattice_n = np.array(lattice_n, dtype=np.float64)
lattice_sign = np.array(lattice_sign)
lattice_prime = is_prime_arr[lattice_n.astype(int)]

print(f"  Lattice points: {len(lattice_n)}")
print(f"  Lattice primes: {lattice_prime.sum()}")
print()

# Compute zeta wave on lattice
wave = zeta_wave_array(lattice_n, GAMMAS)

# Correlation with primality
r_wave, p_wave = pearsonr(wave, lattice_prime.astype(float))
print(f"  Wave vs primality: r = {r_wave:.4f}, p = {p_wave:.2e}")

# After controlling for k (density gradient)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

X_k = lattice_k.reshape(-1, 1)
X_wave = wave.reshape(-1, 1)
X_both = np.column_stack([lattice_k, wave])
y = lattice_prime.astype(int)

clf_k = LogisticRegression(max_iter=300, solver='lbfgs').fit(X_k, y)
auc_k = roc_auc_score(y, clf_k.predict_proba(X_k)[:, 1])

clf_both = LogisticRegression(max_iter=300, solver='lbfgs').fit(X_both, y)
auc_both = roc_auc_score(y, clf_both.predict_proba(X_both)[:, 1])

print(f"  AUC (k only):          {auc_k:.4f}")
print(f"  AUC (k + zeta wave):   {auc_both:.4f}")
print(f"  Improvement from wave: {auc_both - auc_k:+.4f}")
print()

# ====================================================================
#  TEST 3: PRIME COUNTING ERROR vs ZERO SUM (ESTABLISHED MATH)
# ====================================================================
print("=" * 70)
print("  TEST 3: PRIME COUNTING ERROR vs ZERO SUM")
print("=" * 70)
print()
print("  The explicit formula predicts that pi(x) - Li(x) error is")
print("  correlated with the sum over zeta zeros. This SHOULD work.")
print()

# Compute pi(x) at sample points
sample_xs = np.arange(1000, N_MAX, 1000)
pi_x = np.array([is_prime_arr[:int(x)].sum() for x in sample_xs])

# Li(x) approximation (logarithmic integral)
Li_x = np.array([x / log(x) + x / log(x)**2 for x in sample_xs])

# Error: pi(x) - Li(x)
error = pi_x - Li_x

# Zero sum: sum of cos(gamma * log(x)) / sqrt(x) for each x
zero_sum = np.zeros(len(sample_xs))
for x_i, x in enumerate(sample_xs):
    log_x = log(x)
    for g in GAMMAS:
        zero_sum[x_i] += np.cos(g * log_x) / sqrt(x)

# Correlation
r_error, p_error = pearsonr(error, zero_sum)
print(f"  Error vs zero sum: r = {r_error:.4f}, p = {p_error:.2e}")

# Now test: does the zero sum explain error BEYOND just 1/log(x)?
# The error is known to be O(x * exp(-c * sqrt(log x))) by PNT
# The zero sum should capture oscillations in this error

# Let's also test progressively: more zeros -> better correlation
print()
print(f"  Convergence (more zeros -> better correlation with error):")
print(f"  {'# zeros':>8} {'r':>8} {'p':>10}")
print("  " + "-" * 30)

for n_zeros in [1, 3, 5, 10, 15]:
    gammas_sub = GAMMAS[:n_zeros]
    zs = np.zeros(len(sample_xs))
    for x_i, x in enumerate(sample_xs):
        log_x = log(x)
        for g in gammas_sub:
            zs[x_i] += np.cos(g * log_x) / sqrt(x)

    r, p = pearsonr(error, zs)
    print(f"  {n_zeros:>8} {r:>8.4f} {p:>10.2e}")

print()

# ====================================================================
#  TEST 4: RANDOM ZERO CONTROL
# ====================================================================
print("=" * 70)
print("  TEST 4: RANDOM ZERO CONTROL")
print("=" * 70)
print()
print("  Do actual zeta zeros carry more signal than random frequencies?")
print()

# Generate random frequencies matching the range of real zeros
rng = np.random.default_rng(42)

# Control 1: Uniform random in same range
random_uniform = rng.uniform(GAMMAS.min(), GAMMAS.max(), size=len(GAMMAS))

# Control 2: Random frequencies with similar spacing
deltas = np.diff(GAMMAS)
random_deltas = rng.choice(deltas, size=len(GAMMAS)-1, replace=True)
random_spaced = np.cumsum(random_deltas) + GAMMAS[0]
random_spaced = np.concatenate([[GAMMAS[0]], random_spaced])[:len(GAMMAS)]

# Control 3: Multiple random sets
n_random_sets = 100
random_rs = []
for _ in range(n_random_sets):
    rand_gammas = rng.uniform(GAMMAS.min(), GAMMAS.max(), size=len(GAMMAS))
    zs = np.zeros(len(sample_xs))
    for x_i, x in enumerate(sample_xs):
        log_x = log(x)
        for g in rand_gammas:
            zs[x_i] += np.cos(g * log_x) / sqrt(x)
    r_rand, _ = pearsonr(error, zs)
    random_rs.append(r_rand)

random_rs = np.array(random_rs)

# Real zeros correlation
z_real = r_error

# Where does real fall in random distribution?
percentile = np.mean(random_rs >= z_real) if z_real > random_rs.mean() else np.mean(random_rs <= z_real)
z_score = (z_real - random_rs.mean()) / max(random_rs.std(), 1e-9)

print(f"  Real zeros correlation:    {z_real:.4f}")
print(f"  Random zeros mean:         {random_rs.mean():.4f}")
print(f"  Random zeros std:          {random_rs.std():.4f}")
print(f"  z-score:                   {z_score:+.3f}")
print(f"  Percentile of real:        {percentile:.4f}")
print()

if z_score > 2.0:
    print("  Real zeros significantly outperform random frequencies.")
    print("  The specific values of zeta zeros carry genuine spectral signal.")
elif z_score < -2.0:
    print("  Real zeros perform WORSE than random — unexpected.")
else:
    print("  Real zeros are within the random distribution.")
    print("  The correlation comes from having ~15 frequencies, not from")
    print("  their specific values being zeta zeros.")

print()

# Also test: wave correlation with primality for random vs real
wave_real = zeta_wave_array(lattice_n, GAMMAS)
r_real_wave, _ = pearsonr(wave_real, lattice_prime.astype(float))

random_wave_rs = []
for _ in range(50):
    rand_g = rng.uniform(GAMMAS.min(), GAMMAS.max(), size=len(GAMMAS))
    wave_rand = zeta_wave_array(lattice_n, rand_g)
    r_rand, _ = pearsonr(wave_rand, lattice_prime.astype(float))
    random_wave_rs.append(r_rand)

random_wave_rs = np.array(random_wave_rs)
z_wave = (r_real_wave - random_wave_rs.mean()) / max(random_wave_rs.std(), 1e-9)

print(f"  Wave-primality correlation:")
print(f"    Real zeros:    r = {r_real_wave:.6f}")
print(f"    Random zeros:  r = {random_wave_rs.mean():.6f} +/- {random_wave_rs.std():.6f}")
print(f"    z-score:       {z_wave:+.3f}")

if abs(z_wave) < 2.0:
    print("    Real zeros are NOT special for predicting individual primes.")
    print("    Any set of ~15 frequencies gives the same (near-zero) correlation.")

print()

# ====================================================================
#  TEST 5: LOCAL PRIME PROBABILITY MODULATION
# ====================================================================
print("=" * 70)
print("  TEST 5: LOCAL PRIME PROBABILITY MODULATION")
print("=" * 70)
print()
print("  Do zeta-zero waves modulate the probability of primality locally?")
print("  (After removing PNT density)")
print()

# Use lattice points, compute wave, bin by wave value
wave = zeta_wave_array(lattice_n, GAMMAS)
log_n_lat = np.log(lattice_n)
pnt_expected = 2.0 / log_n_lat  # PNT on rails

# Bin by wave value
N_WAVE_BINS = 20
wave_bins = np.linspace(np.percentile(wave, 1), np.percentile(wave, 99), N_WAVE_BINS + 1)
wave_digitized = np.clip(np.digitize(wave, wave_bins) - 1, 0, N_WAVE_BINS - 1)

print(f"  {'Wave bin':>10} {'Count':>7} {'Prime rate':>11} {'PNT expected':>13} {'Residual':>9}")
print("  " + "-" * 55)

residuals_by_bin = []
for i in range(N_WAVE_BINS):
    mask = wave_digitized == i
    count = mask.sum()
    if count < 10:
        continue

    prime_rate = lattice_prime[mask].mean()
    expected = pnt_expected[mask].mean()
    resid = prime_rate - expected
    residuals_by_bin.append(resid)

    bin_lo = wave_bins[i]
    bin_hi = wave_bins[i + 1]
    if count > 100:
        print(f"  [{bin_lo:>+6.2f}, {bin_hi:>+6.2f}] {count:>7} {prime_rate:>11.4f} "
              f"{expected:>13.4f} {resid:>+9.4f}")

# Correlation between wave and residual prime rate
wave_bin_means = np.array([(wave_bins[i] + wave_bins[i+1])/2 for i in range(N_WAVE_BINS)])
valid_bins = [i for i in range(N_WAVE_BINS) if (wave_digitized == i).sum() > 50]
bin_resids = np.array([lattice_prime[wave_digitized == i].mean() - pnt_expected[wave_digitized == i].mean()
                        for i in valid_bins])
bin_centers = np.array([(wave_bins[i] + wave_bins[i+1])/2 for i in valid_bins])

if len(valid_bins) > 3:
    r_mod, p_mod = pearsonr(bin_centers, bin_resids)
    print()
    print(f"  Wave vs residual prime rate: r = {r_mod:.4f}, p = {p_mod:.4f}")

    if abs(r_mod) < 0.1 and p_mod > 0.3:
        print("  No modulation: wave does not affect local prime probability.")
    elif p_mod < 0.05:
        print(f"  Modulation detected (r={r_mod:.3f}), but may be a density artifact.")
    else:
        print("  Weak signal, not statistically significant.")

print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# Plot 1: Spectrum with zeta zero frequencies marked
ax = axes[0, 0]
mask_freq = freqs < 80
ax.plot(freqs[mask_freq], power[mask_freq], 'b-', linewidth=0.5, alpha=0.7)
for i, g in enumerate(GAMMAS):
    if g < 80:
        ax.axvline(x=g, color='red', linewidth=0.5, alpha=0.5, linestyle='--')
ax.set_xlabel("Frequency in log-space")
ax.set_ylabel("Spectral power")
ax.set_title("Prime Density Spectrum (red = zeta zeros)")
ax.grid(True, alpha=0.2)

# Plot 2: Wave vs primality scatter
ax = axes[0, 1]
# Subsample for visibility
idx = np.random.choice(len(lattice_n), min(5000, len(lattice_n)), replace=False)
colors = ['red' if lattice_prime[i] else 'blue' for i in idx]
ax.scatter(wave[idx], log_n_lat[idx], s=1, alpha=0.3, c=colors)
ax.set_xlabel("Zeta wave value")
ax.set_ylabel("log(n)")
ax.set_title("Wave vs log(n) (red=prime, blue=composite)")
ax.grid(True, alpha=0.2)

# Plot 3: Prime counting error vs zero sum
ax = axes[0, 2]
ax.scatter(zero_sum, error, s=10, alpha=0.5, color='steelblue')
ax.set_xlabel("Zero sum (weighted cos)")
ax.set_ylabel("pi(x) - Li(x) error")
ax.set_title(f"Prime Count Error vs Zero Sum (r={r_error:.3f})")
ax.grid(True, alpha=0.2)

# Plot 4: Convergence — more zeros
ax = axes[1, 0]
conv_n = [1, 2, 3, 5, 8, 10, 12, 15]
conv_r = []
for n_z in conv_n:
    gammas_sub = GAMMAS[:n_z]
    zs = np.zeros(len(sample_xs))
    for x_i, x in enumerate(sample_xs):
        for g in gammas_sub:
            zs[x_i] += np.cos(g * log(x)) / sqrt(x)
    r, _ = pearsonr(error, zs)
    conv_r.append(r)

ax.plot(conv_n, conv_r, 'ro-', linewidth=2, markersize=8)
ax.set_xlabel("Number of zeta zeros used")
ax.set_ylabel("Correlation with pi(x) error")
ax.set_title("Convergence: More Zeros -> Better?")
ax.grid(True, alpha=0.2)
ax.axhline(y=0, color='black', linewidth=0.5)

# Plot 5: Real vs random zeros
ax = axes[1, 1]
ax.hist(random_rs, bins=30, color='lightgray', alpha=0.7, label='Random frequencies')
ax.axvline(x=z_real, color='red', linewidth=2, linestyle='--',
           label=f'Real zeros (r={z_real:.3f})')
ax.axvline(x=random_rs.mean(), color='black', linewidth=1, linestyle=':',
           label=f'Random mean ({random_rs.mean():.3f})')
ax.set_xlabel("Correlation with pi(x) error")
ax.set_ylabel("Count")
ax.set_title("Real vs Random Frequencies")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# Plot 6: Wave modulation
ax = axes[1, 2]
if len(valid_bins) > 3:
    ax.bar(range(len(valid_bins)), bin_resids, color='steelblue', alpha=0.7)
    ax.axhline(y=0, color='black', linewidth=1)
    ax.set_xlabel("Wave bin")
    ax.set_ylabel("Residual prime rate (observed - PNT)")
    ax.set_title(f"Local Modulation (r={r_mod if len(valid_bins) > 3 else 0:.3f})")
    ax.grid(True, alpha=0.2, axis='y')

plt.tight_layout()
plt.savefig('experiments/017_zeta_interference/results.png', dpi=150)
print("  Saved: results.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()

print(f"  Test 1 (Spectral): Top peaks at zeta-zero frequencies?")
print(f"    -> Check output above for frequency matches")
print()
print(f"  Test 2 (Wave vs primality): r = {r_wave:.4f}, AUC improvement = {auc_both - auc_k:+.4f}")
print(f"    -> Individual primes: {'no signal' if abs(r_wave) < 0.01 else 'weak signal'}")
print()
print(f"  Test 3 (Error vs zeros): r = {r_error:.4f}")
print(f"    -> Global prime counting: {'established math confirmed' if abs(r_error) > 0.1 else 'weak'}")
print()
print(f"  Test 4 (Real vs random): z = {z_score:+.3f}")
print(f"    -> Zeta zeros specifically: {'genuine' if z_score > 2 else 'within noise'}")
print()
print(f"  Test 5 (Local modulation): r = {r_mod if len(valid_bins) > 3 else 0:.4f}")
print(f"    -> Wave affects local probability: {'no' if abs(r_mod if len(valid_bins) > 3 else 0) < 0.1 else 'maybe'}")
print()

print("  INTERPRETATION:")
print()
if abs(r_error) > 0.1 and z_score > 2:
    print("  Zeta zeros DO affect global prime distribution (established math).")
    print("  The explicit formula is a real spectral decomposition of prime counting.")
    print()
    print("  But individual primes are NOT determined by interference patterns.")
    print("  The wave affects aggregate statistics, not individual outcomes.")
    print("  This is the difference between a population-level law and determinism.")
elif abs(r_error) > 0.1:
    print("  The zero sum correlates with prime counting error, but so do random")
    print("  frequencies. The correlation comes from having oscillatory terms,")
    print("  not from the specific values of zeta zeros.")
else:
    print("  The zero sum does not meaningfully correlate with prime counting error.")
    print("  This may indicate insufficient zeros (15 is small) or that the")
    print("  relationship requires more careful implementation.")

print()
print("  KEY DISTINCTION:")
print("    Zeta zeros constrain GLOBAL statistics (prime counting, error terms)")
print("    Zeta zeros do NOT determine INDIVIDUAL primes (which are 'random')")
print("    This is the difference between statistical mechanics and determinism.")
print()
print("Done.")
