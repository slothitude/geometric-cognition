"""
Experiment 012: 6k±1 Rail Phase Structure
==========================================
Tests whether primes cluster differently from composites
within the 6k±1 lattice, using k-space phase mappings.

Controls:
- Primes vs composites on SAME rail (same k-range)
- phi vs sqrt(2), e, pi, random constants
- Density gradient correction
- Rail asymmetry test (6k-1 vs 6k+1)
"""

import numpy as np
from math import log, pi, sqrt
from scipy.stats import ks_2samp
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
PHASE_BINS = 50
WINDOW = 0.2  # radians for local density test

CONSTANTS = {
    "phi": (1 + sqrt(5)) / 2,
    "sqrt2": sqrt(2),
    "e": np.e,
    "pi": pi,
}

# Random constants (generated once, fixed seed)
np.random.seed(42)
for i in range(5):
    CONSTANTS[f"rand_{i}"] = np.random.uniform(1.1, 3.9)

print("=" * 70)
print("  EXPERIMENT 012: 6k±1 RAIL PHASE STRUCTURE")
print("=" * 70)
print()

# ====================================================================
#  BUILD 6k±1 LATTICE
# ====================================================================
print("  Building 6k±1 lattice...")

is_prime_arr = sieve(N_MAX + 10)

lattice_n = []
lattice_k = []
lattice_sign = []
lattice_is_prime = []

for k in range(1, N_MAX // 6 + 2):
    for sign in (-1, +1):
        n = 6 * k + sign
        if n > N_MAX or n < 5:
            continue
        lattice_n.append(n)
        lattice_k.append(k)
        lattice_sign.append(sign)
        lattice_is_prime.append(is_prime_arr[n])

lattice_n = np.array(lattice_n)
lattice_k = np.array(lattice_k, dtype=np.float64)
lattice_sign = np.array(lattice_sign)
lattice_is_prime = np.array(lattice_is_prime)

print(f"  Total lattice points: {len(lattice_n)}")
print(f"  Primes: {lattice_is_prime.sum()}")
print(f"  Composites: {(~lattice_is_prime).sum()}")
print()

# Split by rail
rail_minus = lattice_sign == -1  # 6k-1
rail_plus = lattice_sign == +1   # 6k+1

print(f"  6k-1 rail: {rail_minus.sum()} points ({lattice_is_prime[rail_minus].sum()} primes)")
print(f"  6k+1 rail: {rail_plus.sum()} points ({lattice_is_prime[rail_plus].sum()} primes)")
print()

# ====================================================================
#  PHASE COMPUTATION
# ====================================================================
def compute_phase(k_vals, constant=None):
    theta = np.log(k_vals)
    if constant is not None:
        theta = theta * constant
    return np.mod(theta, 2 * pi)

def local_density(phases, window=WINDOW):
    return np.mean((phases < window) | (phases > 2 * pi - window))

# ====================================================================
#  EXPERIMENT 1: BASELINE — log(k) only, no constant
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 1: BASELINE — log(k) phase, NO constant")
print("=" * 70)
print()

for rail_name, rail_mask in [("6k-1", rail_minus), ("6k+1", rail_plus)]:
    k_vals = lattice_k[rail_mask]
    prime_mask = lattice_is_prime[rail_mask]
    comp_mask = ~prime_mask

    phase_p = compute_phase(k_vals[prime_mask])
    phase_c = compute_phase(k_vals[comp_mask])

    ks_stat, pval = ks_2samp(phase_p, phase_c)
    dens_p = local_density(phase_p)
    dens_c = local_density(phase_c)
    ratio = dens_p / max(dens_c, 1e-10)

    print(f"  Rail {rail_name}:")
    print(f"    Primes: {prime_mask.sum()}, Composites: {comp_mask.sum()}")
    print(f"    KS stat: {ks_stat:.4f}, p={pval:.4f}")
    print(f"    Local density (primes): {dens_p:.4f}")
    print(f"    Local density (comps):  {dens_c:.4f}")
    print(f"    Density ratio: {ratio:.3f}")
    print()

# ====================================================================
#  EXPERIMENT 2: CONSTANT BAKE-OFF
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 2: CONSTANT BAKE-OFF (primes vs composites)")
print("=" * 70)
print()

print(f"  {'Constant':<10} {'Rail':<6} {'KS stat':>8} {'p-value':>8} {'Dens ratio':>11}")
print("  " + "-" * 50)

all_results = []

for cname, cval in CONSTANTS.items():
    for rail_name, rail_mask in [("6k-1", rail_minus), ("6k+1", rail_plus)]:
        k_vals = lattice_k[rail_mask]
        prime_mask = lattice_is_prime[rail_mask]
        comp_mask = ~prime_mask

        phase_p = compute_phase(k_vals[prime_mask], cval)
        phase_c = compute_phase(k_vals[comp_mask], cval)

        ks_stat, pval = ks_2samp(phase_p, phase_c)
        dens_p = local_density(phase_p)
        dens_c = local_density(phase_c)
        ratio = dens_p / max(dens_c, 1e-10)

        sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
        print(f"  {cname:<10} {rail_name:<6} {ks_stat:>8.4f} {pval:>8.4f} {ratio:>11.3f} {sig}")

        all_results.append({
            "constant": cname, "rail": rail_name,
            "ks_stat": ks_stat, "pval": pval, "ratio": ratio,
        })

print()

# Check if phi stands out
phi_ks = [r["ks_stat"] for r in all_results if r["constant"] == "phi"]
other_ks = [r["ks_stat"] for r in all_results if r["constant"] not in ("phi",)]
print(f"  phi avg KS:     {np.mean(phi_ks):.4f}")
print(f"  other avg KS:   {np.mean(other_ks):.4f}")
print(f"  phi vs other:   {np.mean(phi_ks)/np.mean(other_ks):.2f}x")
print()

# ====================================================================
#  EXPERIMENT 3: RAIL ASYMMETRY
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 3: RAIL ASYMMETRY (6k-1 vs 6k+1)")
print("=" * 70)
print()

# Primes on each rail
p_minus = lattice_k[rail_minus & lattice_is_prime]
p_plus = lattice_k[rail_plus & lattice_is_prime]

print(f"  Primes on 6k-1: {len(p_minus)}")
print(f"  Primes on 6k+1: {len(p_plus)}")
print()

print(f"  {'Constant':<10} {'KS stat':>8} {'p-value':>8}")
print("  " + "-" * 30)

for cname, cval in list(CONSTANTS.items())[:6]:  # skip some randoms for clarity
    phase_minus = compute_phase(p_minus, cval)
    phase_plus = compute_phase(p_plus, cval)
    ks_stat, pval = ks_2samp(phase_minus, phase_plus)
    sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
    print(f"  {cname:<10} {ks_stat:>8.4f} {pval:>8.4f} {sig}")

print()

# ====================================================================
#  EXPERIMENT 4: DENSITY-GRADIENT CONTROL
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 4: DENSITY GRADIENT CONTROL")
print("=" * 70)
print()
print("  Prime density on rails = ~2/log(6k). Binning by log(k) phase")
print("  means bins at different k have different base density.")
print("  We correct for this and test residuals.")
print()

for cname, cval in [("none", None), ("phi", CONSTANTS["phi"]),
                     ("sqrt2", CONSTANTS["sqrt2"]), ("pi", CONSTANTS["pi"])]:
    for rail_name, rail_mask in [("6k-1", rail_minus), ("6k+1", rail_plus)]:
        k_vals = lattice_k[rail_mask]
        prime_mask = lattice_is_prime[rail_mask]

        if cval is None:
            theta = compute_phase(k_vals)
        else:
            theta = compute_phase(k_vals, cval)

        bins = np.linspace(0, 2*pi, PHASE_BINS + 1)
        digitized = np.clip(np.digitize(theta, bins) - 1, 0, PHASE_BINS - 1)

        raw_dens = np.zeros(PHASE_BINS)
        exp_dens = np.zeros(PHASE_BINS)
        for i in range(PHASE_BINS):
            mask = digitized == i
            count = mask.sum()
            if count > 0:
                raw_dens[i] = prime_mask[mask].sum() / count
                # Expected density on rail: ~2/log(6k) by Dirichlet
                exp_dens[i] = np.mean(2.0 / np.log(6 * k_vals[mask]))

        raw_var = np.var(raw_dens)
        resid_var = np.var(raw_dens - exp_dens)
        pct = (1 - resid_var / raw_var) * 100 if raw_var > 0 else 0

        if rail_name == "6k-1":  # print once per constant-rail combo
            c_label = cname if cname != "none" else "log(k)"
            print(f"  {c_label:<8} {rail_name}  raw_var={raw_var:.4e}  "
                  f"resid_var={resid_var:.4e}  gradient explains {pct:.0f}%")

    # 6k+1 line
    k_vals = lattice_k[rail_plus]
    prime_mask = lattice_is_prime[rail_plus]
    if cval is None:
        theta = compute_phase(k_vals)
    else:
        theta = compute_phase(k_vals, cval)
    bins_arr = np.linspace(0, 2*pi, PHASE_BINS + 1)
    digitized = np.clip(np.digitize(theta, bins_arr) - 1, 0, PHASE_BINS - 1)
    raw_dens = np.zeros(PHASE_BINS)
    exp_dens = np.zeros(PHASE_BINS)
    for i in range(PHASE_BINS):
        mask = digitized == i
        count = mask.sum()
        if count > 0:
            raw_dens[i] = prime_mask[mask].sum() / count
            exp_dens[i] = np.mean(2.0 / np.log(6 * k_vals[mask]))
    raw_var = np.var(raw_dens)
    resid_var = np.var(raw_dens - exp_dens)
    pct = (1 - resid_var / raw_var) * 100 if raw_var > 0 else 0
    c_label = cname if cname != "none" else "log(k)"
    print(f"  {c_label:<8} 6k+1  raw_var={raw_var:.4e}  "
          f"resid_var={resid_var:.4e}  gradient explains {pct:.0f}%")

print()

# ====================================================================
#  EXPERIMENT 5: LOCAL PERMUTATION (shuffle k-neighborhoods)
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 5: LOCAL PERMUTATION (within k-neighborhoods)")
print("=" * 70)
print()

for cname, cval in [("log(k)", None), ("phi", CONSTANTS["phi"]),
                     ("sqrt2", CONSTANTS["sqrt2"]), ("pi", CONSTANTS["pi"])]:
    for rail_name, rail_mask in [("6k-1", rail_minus)]:
        k_vals = lattice_k[rail_mask]
        prime_mask = lattice_is_prime[rail_mask]

        if cval is None:
            theta = compute_phase(k_vals)
        else:
            theta = compute_phase(k_vals, cval)

        bins = np.linspace(0, 2*pi, PHASE_BINS + 1)
        digitized = np.clip(np.digitize(theta, bins) - 1, 0, PHASE_BINS - 1)

        # Observed
        obs_dens = np.zeros(PHASE_BINS)
        for i in range(PHASE_BINS):
            mask = digitized == i
            count = mask.sum()
            if count > 0:
                obs_dens[i] = prime_mask[mask].sum() / count
        obs_var = np.var(obs_dens)

        # Local permutation
        n_perms = 500
        block_size = 500
        perm_vars = []
        for _ in range(n_perms):
            perm = prime_mask.copy()
            for start in range(0, len(perm), block_size):
                end = min(start + block_size, len(perm))
                perm[start:end] = np.random.permutation(perm[start:end])
            perm_dens = np.zeros(PHASE_BINS)
            for i in range(PHASE_BINS):
                mask = digitized == i
                count = mask.sum()
                if count > 0:
                    perm_dens[i] = perm[mask].sum() / count
            perm_vars.append(np.var(perm_dens))

        perm_vars = np.array(perm_vars)
        p_val = np.mean(perm_vars >= obs_var)
        z = (obs_var - perm_vars.mean()) / max(perm_vars.std(), 1e-12)

        print(f"  {cname:<8} {rail_name}  z={z:+.2f}  p={p_val:.4f}  "
              f"obs={obs_var:.4e}  perm={perm_vars.mean():.4e}")

print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Prime vs composite phase distributions (baseline)
ax = axes[0, 0]
for rail_name, rail_mask, color in [("6k-1", rail_minus, 'red'), ("6k+1", rail_plus, 'blue')]:
    k_vals = lattice_k[rail_mask]
    prime_mask = lattice_is_prime[rail_mask]
    phase_p = compute_phase(k_vals[prime_mask])
    phase_c = compute_phase(k_vals[~prime_mask])
    ax.hist(phase_p, bins=50, density=True, alpha=0.5, color=color,
            label=f'Primes {rail_name}', histtype='step', linewidth=2)
    ax.hist(phase_c, bins=50, density=True, alpha=0.3, color=color,
            label=f'Comps {rail_name}', histtype='step', linewidth=1, linestyle='--')
ax.set_xlabel("Phase (log(k))")
ax.set_ylabel("Density")
ax.set_title("Prime vs Composite Phase (baseline, no constant)")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# Plot 2: Density by phase bin for different constants
ax = axes[0, 1]
bin_centers = np.linspace(0, 2*pi, PHASE_BINS)
for cname, cval in [("phi", CONSTANTS["phi"]), ("sqrt2", CONSTANTS["sqrt2"]),
                     ("pi", CONSTANTS["pi"]), ("rand_0", CONSTANTS["rand_0"])]:
    k_vals = lattice_k[rail_minus]
    prime_mask = lattice_is_prime[rail_minus]
    theta = compute_phase(k_vals, cval)
    bins_arr = np.linspace(0, 2*pi, PHASE_BINS + 1)
    digitized = np.clip(np.digitize(theta, bins_arr) - 1, 0, PHASE_BINS - 1)
    densities = np.zeros(PHASE_BINS)
    for i in range(PHASE_BINS):
        mask = digitized == i
        count = mask.sum()
        if count > 0:
            densities[i] = prime_mask[mask].sum() / count
    lw = 2 if cname == "phi" else 1
    ax.plot(bin_centers, densities, linewidth=lw, alpha=0.7, label=cname)

overall = lattice_is_prime[rail_minus].sum() / rail_minus.sum()
ax.axhline(y=overall, color='black', linestyle=':', label=f'Expected ({overall:.4f})')
ax.set_xlabel("Phase bin")
ax.set_ylabel("Prime density")
ax.set_title("6k-1 Rail: Density by Phase (different constants)")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# Plot 3: Rail comparison (primes only)
ax = axes[1, 0]
for cname, cval in [("phi", CONSTANTS["phi"]), ("sqrt2", CONSTANTS["sqrt2"])]:
    for rail_name, rail_mask, ls in [("6k-1", rail_minus, '-'), ("6k+1", rail_plus, '--')]:
        k_vals = lattice_k[rail_mask & lattice_is_prime]
        theta = compute_phase(k_vals, cval)
        ax.hist(theta, bins=50, density=True, alpha=0.4,
                label=f'{cname} {rail_name}', histtype='step', linewidth=2, linestyle=ls)
ax.set_xlabel("Phase")
ax.set_ylabel("Density")
ax.set_title("Rail Asymmetry: Prime Phase Distributions")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# Plot 4: Residuals after density correction
ax = axes[1, 1]
for cname, cval in [("phi", CONSTANTS["phi"]), ("sqrt2", CONSTANTS["sqrt2"]), ("pi", CONSTANTS["pi"])]:
    k_vals = lattice_k[rail_minus]
    prime_mask = lattice_is_prime[rail_minus]
    theta = compute_phase(k_vals, cval)
    bins_arr = np.linspace(0, 2*pi, PHASE_BINS + 1)
    digitized = np.clip(np.digitize(theta, bins_arr) - 1, 0, PHASE_BINS - 1)
    residuals = np.zeros(PHASE_BINS)
    for i in range(PHASE_BINS):
        mask = digitized == i
        count = mask.sum()
        if count > 0:
            obs = prime_mask[mask].sum() / count
            exp = np.mean(2.0 / np.log(6 * k_vals[mask]))
            residuals[i] = obs - exp
    ax.plot(bin_centers, residuals, label=cname, alpha=0.8)
ax.axhline(y=0, color='black', linewidth=0.5)
ax.set_xlabel("Phase bin")
ax.set_ylabel("Residual (observed - expected)")
ax.set_title("6k-1: Residuals After 2/log(6k) Correction")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/012_6k_rails/results.png', dpi=150)
print("  Saved: results.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()

# Find best constant by KS stat (primes vs composites)
best_result = min(all_results, key=lambda r: r["pval"])
print(f"  Best constant: {best_result['constant']} on {best_result['rail']}")
print(f"    KS stat: {best_result['ks_stat']:.4f}, p={best_result['pval']:.4f}")
print()

# Count significant
n_sig = sum(1 for r in all_results if r["pval"] < 0.05)
n_total = len(all_results)
print(f"  Significant (p<0.05): {n_sig}/{n_total}")
print()

# Rail balance
minus_primes = lattice_is_prime[rail_minus].sum()
plus_primes = lattice_is_prime[rail_plus].sum()
print(f"  Rail balance: 6k-1 has {minus_primes} primes, 6k+1 has {plus_primes} primes")
print(f"  Ratio: {minus_primes/plus_primes:.3f} (Chebyshev bias: 6k-1 slightly favored)")
print()

print("  VERDICT:")
if n_sig == 0:
    print("  No constant shows primes clustering differently from composites")
    print("  in k-space phase within the 6k±1 lattice. Phase is irrelevant.")
elif best_result["constant"] == "phi" and best_result["pval"] < 0.01:
    print("  phi shows significant prime-composite separation in k-space.")
    print("  This is genuine structure worth investigating.")
else:
    print(f"  {best_result['constant']} (not phi) shows best separation.")
    print("  phi has no special status among constants.")

print()
print("Done.")
