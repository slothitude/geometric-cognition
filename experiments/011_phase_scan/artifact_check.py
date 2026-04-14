"""
Experiment 011b: Artifact Check — Is the Phase Signal Real?
============================================================
The initial scan found "significant" transforms (n^1.0, log(log(n)), etc.)
but these may be artifacts of the non-uniform prime density 1/log(n).

Control 1: Local density correction
  - Expected prime density per bin = mean(1/log(n)) for n in that bin
  - Measure: variance of (observed - expected) density

Control 2: Frequency-matched permutation
  - Shuffle primes only within local n-neighborhoods
  - This preserves the 1/log(n) density gradient

Control 3: Independent phase mapping
  - Map composites only (no primes) to phase — should show same "structure"
    if it's purely a density gradient effect

Control 4: Cancellation test
  - Use n in [N/2, N] only — prime density is nearly uniform there
  - If signal disappears, it was a density artifact
"""

import numpy as np
from math import log, pi, sqrt
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ====================================================================
#  PRIME SIEVE
# ====================================================================
def sieve_of_eratosthenes(N):
    is_prime = np.ones(N, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return is_prime

N = 200000
print("=" * 70)
print("  EXPERIMENT 011b: ARTIFACT CHECK")
print("=" * 70)
print()

is_prime = sieve_of_eratosthenes(N)
nums = np.arange(2, N).astype(np.float64)
primes_mask = is_prime[2:N]

# Top transforms from 011
transforms = {
    "n^1.0":                lambda n: n,
    "n^0.1":                lambda n: n**0.1,
    "log(log(n))":          lambda n: np.log(np.log(n)),
    "log(n^0.5 + 1)":       lambda n: np.log(n**0.5 + 1),
    "log(n) / log(log(n))":  lambda n: np.log(n) / np.log(np.log(n)),
    "log(n)":               lambda n: np.log(n),
}

N_BINS = 100

# ====================================================================
#  CONTROL 1: LOCAL DENSITY CORRECTION
# ====================================================================
print("  CONTROL 1: Expected density correction (1/log(n))")
print("  " + "-" * 60)
print()

for name, f in transforms.items():
    theta = f(nums) % (2 * pi)
    bins = np.linspace(0, 2*pi, N_BINS + 1)
    digitized = np.clip(np.digitize(theta, bins) - 1, 0, N_BINS - 1)

    raw_densities = np.zeros(N_BINS)
    expected_densities = np.zeros(N_BINS)
    residuals = np.zeros(N_BINS)

    for i in range(N_BINS):
        mask = digitized == i
        count = mask.sum()
        if count > 0:
            raw_densities[i] = primes_mask[mask].sum() / count
            # Expected density = average of 1/log(n) for n in this bin
            expected_densities[i] = np.mean(1.0 / np.log(nums[mask]))
            residuals[i] = raw_densities[i] - expected_densities[i]
        else:
            raw_densities[i] = 0
            expected_densities[i] = 0
            residuals[i] = 0

    raw_var = np.var(raw_densities)
    resid_var = np.var(residuals)
    expected_var = np.var(expected_densities)

    reduction = (1 - resid_var / raw_var) * 100 if raw_var > 0 else 0

    print(f"  {name:<25} raw_var={raw_var:.4e}  expected_var={expected_var:.4e}  "
          f"residual_var={resid_var:.4e}  ({reduction:.0f}% explained)")

print()

# ====================================================================
#  CONTROL 2: LOCAL PERMUTATION TEST
# ====================================================================
print("  CONTROL 2: Local permutation (shuffle within n-neighborhoods)")
print("  " + "-" * 60)
print()

BLOCK_SIZE = 1000  # shuffle primes within blocks of 1000 consecutive n's
n_local_perms = 500

for name, f in transforms.items():
    theta = f(nums) % (2 * pi)
    bins = np.linspace(0, 2*pi, N_BINS + 1)
    digitized = np.clip(np.digitize(theta, bins) - 1, 0, N_BINS - 1)

    # Observed
    obs_dens = np.zeros(N_BINS)
    for i in range(N_BINS):
        mask = digitized == i
        count = mask.sum()
        if count > 0:
            obs_dens[i] = primes_mask[mask].sum() / count
    obs_var = np.var(obs_dens)

    # Local permutation
    local_perm_vars = []
    for _ in range(n_local_perms):
        # Shuffle within blocks
        perm_mask = primes_mask.copy()
        for start in range(0, len(perm_mask), BLOCK_SIZE):
            end = min(start + BLOCK_SIZE, len(perm_mask))
            perm_mask[start:end] = np.random.permutation(perm_mask[start:end])

        perm_dens = np.zeros(N_BINS)
        for i in range(N_BINS):
            mask = digitized == i
            count = mask.sum()
            if count > 0:
                perm_dens[i] = perm_mask[mask].sum() / count
        local_perm_vars.append(np.var(perm_dens))

    local_perm_vars = np.array(local_perm_vars)
    p_local = np.mean(local_perm_vars >= obs_var)
    z_local = (obs_var - local_perm_vars.mean()) / max(local_perm_vars.std(), 1e-12)

    print(f"  {name:<25} obs_var={obs_var:.4e}  local_perm_mean={local_perm_vars.mean():.4e}  "
          f"z={z_local:+.2f}  p={p_local:.4f}")

print()

# ====================================================================
#  CONTROL 3: HIGH-RANGE ONLY (n in [N/2, N])
# ====================================================================
print("  CONTROL 3: High range only (n in [N/2, N]) — uniform density")
print("  " + "-" * 60)
print()

nums_high = np.arange(N//2, N).astype(np.float64)
primes_high = is_prime[N//2:N]
high_freq = primes_high.sum() / len(primes_high)

print(f"  Range: [{N//2}, {N}], Prime frequency: {high_freq:.4f}")
print(f"  Full range frequency: {primes_mask.sum()/len(primes_mask):.4f}")
print(f"  Density ratio: {high_freq / (primes_mask.sum()/len(primes_mask)):.2f}x")
print()

for name, f in transforms.items():
    theta = f(nums_high) % (2 * pi)
    bins = np.linspace(0, 2*pi, N_BINS + 1)
    digitized = np.clip(np.digitize(theta, bins) - 1, 0, N_BINS - 1)

    densities = np.zeros(N_BINS)
    for i in range(N_BINS):
        mask = digitized == i
        count = mask.sum()
        if count > 0:
            densities[i] = primes_high[mask].sum() / count

    high_var = np.var(densities)

    # Permutation test on high range
    perm_vars = []
    for _ in range(500):
        perm = np.random.permutation(primes_high)
        perm_dens = np.zeros(N_BINS)
        for i in range(N_BINS):
            mask = digitized == i
            count = mask.sum()
            if count > 0:
                perm_dens[i] = perm[mask].sum() / count
        perm_vars.append(np.var(perm_dens))

    perm_vars = np.array(perm_vars)
    p_val = np.mean(perm_vars >= high_var)
    z = (high_var - perm_vars.mean()) / max(perm_vars.std(), 1e-12)

    sig = "***" if p_val < 0.01 else "**" if p_val < 0.05 else "*" if p_val < 0.1 else ""
    print(f"  {name:<25} var={high_var:.4e}  z={z:+.2f}  p={p_val:.4f} {sig}")

print()

# ====================================================================
#  CONTROL 4: COMPOSITES-ONLY ANALYSIS
# ====================================================================
print("  CONTROL 4: Composites-only phase structure")
print("  (If 'signal' appears for composites too, it's not prime-specific)")
print("  " + "-" * 60)
print()

composites_mask = ~primes_mask

for name, f in transforms.items():
    theta = f(nums) % (2 * pi)
    bins = np.linspace(0, 2*pi, N_BINS + 1)
    digitized = np.clip(np.digitize(theta, bins) - 1, 0, N_BINS - 1)

    comp_densities = np.zeros(N_BINS)
    for i in range(N_BINS):
        mask = digitized == i
        count = mask.sum()
        if count > 0:
            comp_densities[i] = composites_mask[mask].sum() / count

    comp_var = np.var(comp_densities)

    # For comparison: prime density variance from full range
    prime_densities = np.zeros(N_BINS)
    for i in range(N_BINS):
        mask = digitized == i
        count = mask.sum()
        if count > 0:
            prime_densities[i] = primes_mask[mask].sum() / count
    prime_var = np.var(prime_densities)

    print(f"  {name:<25} prime_var={prime_var:.4e}  composite_var={comp_var:.4e}  "
          f"ratio={prime_var/max(comp_var,1e-12):.2f}")

print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Raw vs corrected density for n^1.0
ax = axes[0, 0]
f = transforms["n^1.0"]
theta = f(nums) % (2*pi)
bins = np.linspace(0, 2*pi, N_BINS + 1)
digitized = np.clip(np.digitize(theta, bins) - 1, 0, N_BINS - 1)
raw_dens = np.zeros(N_BINS)
exp_dens = np.zeros(N_BINS)
resid = np.zeros(N_BINS)
for i in range(N_BINS):
    mask = digitized == i
    count = mask.sum()
    if count > 0:
        raw_dens[i] = primes_mask[mask].sum() / count
        exp_dens[i] = np.mean(1.0 / np.log(nums[mask]))
        resid[i] = raw_dens[i] - exp_dens[i]
bin_centers = np.linspace(0, 2*pi, N_BINS)
ax.plot(bin_centers, raw_dens, label='Observed', color='steelblue')
ax.plot(bin_centers, exp_dens, label='Expected (1/log(n))', color='red', linestyle='--')
ax.set_xlabel("Phase")
ax.set_ylabel("Prime density")
ax.set_title("n^1.0: Observed vs Expected Density")
ax.legend()
ax.grid(True, alpha=0.2)

# Plot 2: Residuals for top transforms
ax = axes[0, 1]
for name in ["n^1.0", "log(log(n))", "log(n) / log(log(n))", "log(n)"]:
    f = transforms[name]
    theta = f(nums) % (2*pi)
    digitized = np.clip(np.digitize(theta, bins) - 1, 0, N_BINS - 1)
    res = np.zeros(N_BINS)
    for i in range(N_BINS):
        mask = digitized == i
        count = mask.sum()
        if count > 0:
            obs = primes_mask[mask].sum() / count
            exp = np.mean(1.0 / np.log(nums[mask]))
            res[i] = obs - exp
    ax.plot(bin_centers, res, label=name, alpha=0.8)
ax.axhline(y=0, color='black', linewidth=0.5)
ax.set_xlabel("Phase")
ax.set_ylabel("Density residual (obs - expected)")
ax.set_title("Residuals After 1/log(n) Correction")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# Plot 3: High-range only comparison
ax = axes[1, 0]
nums_high = np.arange(N//2, N).astype(np.float64)
primes_high = is_prime[N//2:N]
for name in ["n^1.0", "log(log(n))", "log(n)"]:
    f = transforms[name]
    theta_h = f(nums_high) % (2*pi)
    digitized_h = np.clip(np.digitize(theta_h, bins) - 1, 0, N_BINS - 1)
    dens = np.zeros(N_BINS)
    for i in range(N_BINS):
        mask = digitized_h == i
        count = mask.sum()
        if count > 0:
            dens[i] = primes_high[mask].sum() / count
    ax.plot(bin_centers, dens, label=name, alpha=0.8)
ax.axhline(y=primes_high.sum()/len(primes_high), color='black', linestyle='--')
ax.set_xlabel("Phase")
ax.set_ylabel("Prime density")
ax.set_title(f"High Range Only (n={N//2}-{N})")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# Plot 4: Variance reduction
ax = axes[1, 1]
names = list(transforms.keys())
raw_vars = []
resid_vars = []
pct_explained = []
for name, f in transforms.items():
    theta = f(nums) % (2*pi)
    digitized = np.clip(np.digitize(theta, bins) - 1, 0, N_BINS - 1)
    raw_d = np.zeros(N_BINS)
    exp_d = np.zeros(N_BINS)
    for i in range(N_BINS):
        mask = digitized == i
        count = mask.sum()
        if count > 0:
            raw_d[i] = primes_mask[mask].sum() / count
            exp_d[i] = np.mean(1.0 / np.log(nums[mask]))
    rv = np.var(raw_d)
    ev = np.var(raw_d - exp_d)
    raw_vars.append(rv)
    resid_vars.append(ev)
    pct_explained.append((1 - ev/rv) * 100 if rv > 0 else 0)

x = np.arange(len(names))
width = 0.35
ax.bar(x - width/2, raw_vars, width, label='Raw variance', color='steelblue')
ax.bar(x + width/2, resid_vars, width, label='Residual variance', color='coral')
ax.set_xticks(x)
ax.set_xticklabels(names, rotation=45, ha='right', fontsize=7)
ax.set_ylabel("Variance")
ax.set_title("Raw vs Corrected Variance")
ax.legend()
ax.grid(True, alpha=0.2, axis='y')

plt.tight_layout()
plt.savefig('experiments/011_phase_scan/artifact_check.png', dpi=150)
print("  Saved: artifact_check.png")

# ====================================================================
#  FINAL VERDICT
# ====================================================================
print()
print("=" * 70)
print("  VERDICT")
print("=" * 70)
print()
print("  Controls applied:")
print("  1. 1/log(n) density correction — removes density gradient")
print("  2. Local permutation — preserves density gradient")
print("  3. High range only — near-uniform density")
print("  4. Composites-only — tests if signal is prime-specific")
print()
print("  If signal disappears under ALL controls, the 'phase clustering'")
print("  is entirely explained by the non-uniform prime density 1/log(n),")
print("  not by genuine phase-space structure of primes.")
print()
print("Done.")
