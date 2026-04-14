"""
Experiment 016: EXOR Field Test (Local Composite Density as Prime Predictor)
=============================================================================
Tests whether the local density of composite factorizations around a lattice
point n predicts whether n is prime — WITHOUT checking n's own factorizations.

The key distinction from experiment 015:
  - Exp 015: coverage(n) = can n be factored? → CIRCULAR (IS the definition)
  - Exp 016: field(n) = how many composites exist NEAR n? → NON-CIRCULAR

If composites create an "exclusion field", then primes should sit in
LOW-field regions (sparse composite neighborhoods).

Null hypothesis: field values for primes and composites differ only
due to the PNT density gradient (both decrease with k).
"""

import numpy as np
from math import log, pi, sqrt
from scipy.stats import mannwhitneyu, pearsonr, ks_2samp
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
print("  EXPERIMENT 016: EXOR FIELD TEST")
print("=" * 70)
print()

is_prime_arr = sieve(N_MAX + 10)

# ====================================================================
#  BUILD 6k+/-1 LATTICE
# ====================================================================
K_MAX = N_MAX // 6 + 1

lattice_k = []
lattice_sign = []
lattice_n = []

for k in range(1, K_MAX + 1):
    for sign in (-1, +1):
        n = 6 * k + sign
        if n < 5 or n > N_MAX:
            continue
        lattice_k.append(k)
        lattice_sign.append(sign)
        lattice_n.append(n)

lattice_k = np.array(lattice_k, dtype=np.float64)
lattice_sign = np.array(lattice_sign)
lattice_n = np.array(lattice_n)
lattice_prime = is_prime_arr[lattice_n]
log_n = np.log(lattice_n)

print(f"  Lattice points: {len(lattice_n)}")
print(f"  Primes: {lattice_prime.sum()}")
print(f"  Composites: {(~lattice_prime).sum()}")
print()

# ====================================================================
#  STEP 1: COMPUTE COMPOSITE MULTIPLICITY
# ====================================================================
# multiplicity(n) = number of distinct (a,b) pairs on 6k+/-1 lattice
#                   with a <= b, a >= 5, a*b = n
# This is the "how many ways to construct n" metric.

print("  Step 1: Computing composite multiplicities...")
t0 = time.time()

multiplicity = np.zeros(N_MAX + 1, dtype=np.int32)

# Build sorted list of lattice numbers for iteration
lattice_sorted = sorted(set(lattice_n))

for i, a in enumerate(lattice_sorted):
    if a * a > N_MAX:
        break
    for j in range(i, len(lattice_sorted)):
        b = lattice_sorted[j]
        n = a * b
        if n > N_MAX:
            break
        multiplicity[n] += 1

elapsed = time.time() - t0
print(f"  Done in {elapsed:.1f}s")
print()

# ====================================================================
#  STEP 2: BUILD EXOR FIELD
# ====================================================================
# field(n) = sum of multiplicity(m) for all lattice numbers m
#            within log-space distance d of log(n)
#
# This measures "how much composite structure exists near n" in the
# multiplicative geometry. Crucially, it does NOT use multiplicity(n)
# itself — it looks at the NEIGHBORHOOD.

print("  Step 2: Building EXOR field (log-space neighborhood sums)...")

# Sort lattice by log(n) for efficient windowing
sort_idx = np.argsort(log_n)
log_sorted = log_n[sort_idx]
k_sorted = lattice_k[sort_idx]
n_sorted = lattice_n[sort_idx]
prime_sorted = lattice_prime[sort_idx]
mult_sorted = multiplicity[n_sorted]

# Test multiple window sizes (in log-space)
WINDOWS = [0.05, 0.1, 0.2, 0.5, 1.0]

field_results = {}

for w in WINDOWS:
    print(f"    Window = {w:.2f} ...", end="", flush=True)
    t0 = time.time()

    field = np.zeros(len(lattice_n), dtype=np.float64)

    for i in range(len(log_sorted)):
        # Find all points within log-space distance w of point i
        lo = log_sorted[i] - w
        hi = log_sorted[i] + w

        # Binary search for window bounds
        left = np.searchsorted(log_sorted, lo)
        right = np.searchsorted(log_sorted, hi)

        # Sum multiplicities in window, EXCLUDING self
        if right - left > 1:
            field[sort_idx[i]] = np.sum(mult_sorted[left:right]) - mult_sorted[i]
        else:
            field[sort_idx[i]] = 0

    elapsed = time.time() - t0
    field_results[w] = field
    print(f" done ({elapsed:.1f}s)")

print()

# ====================================================================
#  TEST 1: FIELD DISTRIBUTION — PRIMES vs COMPOSITES
# ====================================================================
print("=" * 70)
print("  TEST 1: EXOR FIELD — PRIMES vs COMPOSITES")
print("=" * 70)
print()

print(f"  {'Window':>8} {'Prime mean':>11} {'Comp mean':>10} {'Ratio':>7} "
      f"{'MW p-val':>9}")
print("  " + "-" * 55)

for w in WINDOWS:
    field = field_results[w]
    pf = field[lattice_prime]
    cf = field[~lattice_prime]

    pm, cm = pf.mean(), cf.mean()
    ratio = pm / max(cm, 1e-10)

    U, p = mannwhitneyu(pf, cf, alternative='less')

    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  {w:>8.2f} {pm:>11.2f} {cm:>10.2f} {ratio:>7.3f} {p:>9.2e} {sig}")

print()

# ====================================================================
#  TEST 2: DENSITY-CORRECTED ANALYSIS
# ====================================================================
print("=" * 70)
print("  TEST 2: DENSITY-CORRECTED (within k-bins)")
print("=" * 70)
print()

# The field correlates with k (smaller k = fewer composites nearby = lower field).
# We correct by comparing primes vs composites WITHIN the same k-range.

N_K_BINS = 50
k_bins = np.linspace(lattice_k.min(), lattice_k.max(), N_K_BINS + 1)
k_digitized = np.clip(np.digitize(lattice_k, k_bins) - 1, 0, N_K_BINS - 1)

for w in [0.1, 0.5]:  # test two representative windows
    field = field_results[w]

    print(f"  Window = {w:.2f}:")
    print(f"    {'k-bin range':>20} {'Prime field':>12} {'Comp field':>12} {'Diff':>8} {'p':>9}")
    print("    " + "-" * 65)

    significant_bins = 0
    total_bins = 0

    for i in range(N_K_BINS):
        mask = k_digitized == i
        count = mask.sum()
        if count < 20:
            continue

        pf = field[mask & lattice_prime]
        cf = field[mask & (~lattice_prime)]

        if len(pf) < 5 or len(cf) < 5:
            continue

        total_bins += 1
        pm, cm = pf.mean(), cf.mean()
        diff = pm - cm

        if len(pf) > 0 and len(cf) > 0:
            try:
                U, p = mannwhitneyu(pf, cf, alternative='less')
            except:
                p = 1.0

            if p < 0.05:
                significant_bins += 1

            # Show a few representative bins
            k_lo = k_bins[i]
            k_hi = k_bins[i + 1]
            if i % 10 == 0:
                print(f"    [{k_lo:>7.0f}, {k_hi:>7.0f}]  {pm:>12.2f} {cm:>12.2f} "
                      f"{diff:>+8.2f} {p:>9.4f}")

    print(f"    Significant bins: {significant_bins}/{total_bins} "
          f"({significant_bins/max(total_bins,1)*100:.1f}%)")
    print()

# ====================================================================
#  TEST 3: PREDICTIVE VALUE — LOGISTIC REGRESSION
# ====================================================================
print("=" * 70)
print("  TEST 3: PREDICTIVE VALUE (AUC with field + k vs k alone)")
print("=" * 70)
print()

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

for w in [0.1, 0.2, 0.5]:
    field = field_results[w]

    y = lattice_prime.astype(int)

    # Model 1: k only (density gradient baseline)
    X_k = lattice_k.reshape(-1, 1)
    clf_k = LogisticRegression(max_iter=300, solver='lbfgs')
    clf_k.fit(X_k, y)
    auc_k = roc_auc_score(y, clf_k.predict_proba(X_k)[:, 1])

    # Model 2: k + field
    X_kf = np.column_stack([lattice_k, field])
    clf_kf = LogisticRegression(max_iter=300, solver='lbfgs')
    clf_kf.fit(X_kf, y)
    auc_kf = roc_auc_score(y, clf_kf.predict_proba(X_kf)[:, 1])

    # Model 3: field only (no k)
    X_f = field.reshape(-1, 1)
    clf_f = LogisticRegression(max_iter=300, solver='lbfgs')
    clf_f.fit(X_f, y)
    auc_f = roc_auc_score(y, clf_f.predict_proba(X_f)[:, 1])

    improvement = auc_kf - auc_k

    print(f"  Window {w:.2f}:")
    print(f"    AUC (k only):          {auc_k:.4f}")
    print(f"    AUC (field only):      {auc_f:.4f}")
    print(f"    AUC (k + field):       {auc_kf:.4f}")
    print(f"    Improvement from field: {improvement:+.4f}")
    print()

# ====================================================================
#  TEST 4: PERMUTATION TEST (within k-bins)
# ====================================================================
print("=" * 70)
print("  TEST 4: PERMUTATION TEST (shuffle labels within k-bins)")
print("=" * 70)
print()

rng = np.random.default_rng(42)
n_perms = 1000

for w in [0.1, 0.5]:
    field = field_results[w]

    # Compute observed mean difference (prime - composite field) within bins
    obs_diffs = []
    for i in range(N_K_BINS):
        mask = k_digitized == i
        pf = field[mask & lattice_prime]
        cf = field[mask & (~lattice_prime)]
        if len(pf) > 5 and len(cf) > 5:
            obs_diffs.append(pf.mean() - cf.mean())

    obs_mean_diff = np.mean(obs_diffs)

    # Permutation
    perm_diffs = []
    for _ in range(n_perms):
        perm_prime = lattice_prime.copy()
        for i in range(N_K_BINS):
            mask = k_digitized == i
            idx = np.where(mask)[0]
            if len(idx) > 1:
                perm_prime[idx] = rng.permutation(perm_prime[idx])

        pd = []
        for i in range(N_K_BINS):
            mask = k_digitized == i
            pf = field[mask & perm_prime]
            cf = field[mask & (~perm_prime)]
            if len(pf) > 5 and len(cf) > 5:
                pd.append(pf.mean() - cf.mean())

        perm_diffs.append(np.mean(pd))

    perm_diffs = np.array(perm_diffs)
    z = (obs_mean_diff - perm_diffs.mean()) / max(perm_diffs.std(), 1e-9)

    if obs_mean_diff < perm_diffs.mean():
        p_perm = np.mean(perm_diffs <= obs_mean_diff)
    else:
        p_perm = np.mean(perm_diffs >= obs_mean_diff)

    print(f"  Window {w:.2f}:")
    print(f"    Observed mean diff (prime - comp field): {obs_mean_diff:+.4f}")
    print(f"    Permutation mean diff:                    {perm_diffs.mean():+.4f}")
    print(f"    z-score: {z:+.3f}")
    print(f"    p-value: {p_perm:.4f}")

    if p_perm < 0.05 and obs_mean_diff < 0:
        print("    SIGNIFICANT: Primes sit in lower-field regions (beyond density)")
    elif p_perm < 0.05 and obs_mean_diff > 0:
        print("    SIGNIFICANT but POSITIVE: Primes in HIGHER-field regions??")
    else:
        print("    NOT significant: Field adds nothing beyond density gradient")

    print()

# ====================================================================
#  TEST 5: FIELD AT PRIME vs COMPOSITE NEIGHBORS
# ====================================================================
print("=" * 70)
print("  TEST 5: FIELD VALUES AT PRIME vs COMPOSITE NEIGHBORS")
print("=" * 70)
print()
print("  Within the same k-bin, do primes have systematically different")
print("  field values than their composite neighbors?")
print()

# For each k-bin with enough data, compute effect size (Cohen's d)
w = 0.2
field = field_results[w]

effect_sizes = []
for i in range(N_K_BINS):
    mask = k_digitized == i
    pf = field[mask & lattice_prime]
    cf = field[mask & (~lattice_prime)]

    if len(pf) < 10 or len(cf) < 10:
        continue

    pooled_std = sqrt((pf.var() * (len(pf)-1) + cf.var() * (len(cf)-1))
                      / max(len(pf) + len(cf) - 2, 1))
    d = (pf.mean() - cf.mean()) / max(pooled_std, 1e-10)
    effect_sizes.append(d)

effect_sizes = np.array(effect_sizes)

print(f"  Window = {w:.2f}:")
print(f"  Mean Cohen's d: {effect_sizes.mean():+.4f}")
print(f"  Median Cohen's d: {np.median(effect_sizes):+.4f}")
print(f"  Std of d: {effect_sizes.std():.4f}")
print(f"  Fraction d < 0: {(effect_sizes < 0).mean()*100:.1f}%")
print(f"  Fraction d < -0.2: {(effect_sizes < -0.2).mean()*100:.1f}%")
print(f"  Fraction d > +0.2: {(effect_sizes > 0.2).mean()*100:.1f}%")
print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

w_main = 0.2
field = field_results[w_main]

# Plot 1: Field distribution (primes vs composites)
ax = axes[0, 0]
pf = field[lattice_prime]
cf = field[~lattice_prime]
bins_hist = np.linspace(0, max(pf.max(), cf.max()), 80)
ax.hist(cf, bins=bins_hist, density=True, alpha=0.5, color='blue', label='Composites')
ax.hist(pf, bins=bins_hist, density=True, alpha=0.5, color='red', label='Primes')
ax.set_xlabel("EXOR field value")
ax.set_ylabel("Density")
ax.set_title(f"Field Distribution (window={w_main})")
ax.legend()
ax.grid(True, alpha=0.2)

# Plot 2: Field vs k (density gradient)
ax = axes[0, 1]
# Bin by k and show mean field
unique_ks = np.unique(lattice_k.astype(int))
k_vals = []
pf_vals = []
cf_vals = []
for k in unique_ks[::max(1, len(unique_ks)//200)]:
    mask = lattice_k == k
    pmask = mask & lattice_prime
    cmask = mask & (~lattice_prime)
    if pmask.sum() > 0 and cmask.sum() > 0:
        k_vals.append(k)
        pf_vals.append(field[pmask].mean())
        cf_vals.append(field[cmask].mean())

if k_vals:
    ax.plot(k_vals, pf_vals, 'r-', linewidth=0.5, alpha=0.5, label='Primes')
    ax.plot(k_vals, cf_vals, 'b-', linewidth=0.5, alpha=0.5, label='Composites')
    ax.set_xlabel("k")
    ax.set_ylabel("Mean field value")
    ax.set_title("Field vs k (density gradient)")
    ax.legend()
    ax.grid(True, alpha=0.2)

# Plot 3: AUC comparison
ax = axes[0, 2]
auc_data = []
for w in WINDOWS:
    field_w = field_results[w]
    y = lattice_prime.astype(int)
    X_kf = np.column_stack([lattice_k, field_w])
    clf = LogisticRegression(max_iter=300, solver='lbfgs').fit(X_kf, y)
    auc_kf = roc_auc_score(y, clf.predict_proba(X_kf)[:, 1])

    X_k = lattice_k.reshape(-1, 1)
    auc_k = roc_auc_score(y, LogisticRegression(max_iter=300, solver='lbfgs')
                          .fit(X_k, y).predict_proba(X_k)[:, 1])

    auc_data.append((w, auc_k, auc_kf))

bars_k = ax.bar([i - 0.15 for i in range(len(WINDOWS))],
                [d[1] for d in auc_data], width=0.3, color='steelblue', label='k only')
bars_kf = ax.bar([i + 0.15 for i in range(len(WINDOWS))],
                 [d[2] for d in auc_data], width=0.3, color='coral', label='k + field')
ax.set_xticks(range(len(WINDOWS)))
ax.set_xticklabels([f"{w:.2f}" for w in WINDOWS])
ax.set_xlabel("Log-space window")
ax.set_ylabel("AUC")
ax.set_title("Predictive Value: k vs k+field")
ax.legend()
ax.grid(True, alpha=0.2, axis='y')

# Plot 4: Effect sizes by k-bin
ax = axes[1, 0]
if len(effect_sizes) > 0:
    ax.hist(effect_sizes, bins=30, color='steelblue', alpha=0.7)
    ax.axvline(x=0, color='black', linewidth=1)
    ax.axvline(x=effect_sizes.mean(), color='red', linewidth=2, linestyle='--',
               label=f'Mean d={effect_sizes.mean():+.3f}')
    ax.set_xlabel("Cohen's d (prime - composite field)")
    ax.set_ylabel("Count (k-bins)")
    ax.set_title("Effect Size Distribution Across k-bins")
    ax.legend()
    ax.grid(True, alpha=0.2)

# Plot 5: Permutation test
ax = axes[1, 1]
# Use last computed permutation results
ax.hist(perm_diffs, bins=40, color='lightgray', alpha=0.7, label='Permuted')
ax.axvline(x=obs_mean_diff, color='red', linewidth=2, linestyle='--',
           label=f'Observed={obs_mean_diff:+.4f}')
ax.axvline(x=perm_diffs.mean(), color='black', linewidth=1, linestyle=':',
           label=f'Null mean={perm_diffs.mean():+.4f}')
ax.set_xlabel("Mean diff (prime - comp field)")
ax.set_ylabel("Count")
ax.set_title("Permutation Test")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# Plot 6: Field heatmap (field vs k and sign)
ax = axes[1, 2]
w = 0.2
field = field_results[w]
# Average field by k and rail
k_range = np.arange(1, min(500, K_MAX))
minus_field = []
plus_field = []
for k in k_range:
    mask_m = (lattice_k == k) & (lattice_sign == -1)
    mask_p = (lattice_k == k) & (lattice_sign == +1)
    if mask_m.any():
        minus_field.append(field[mask_m].mean())
    else:
        minus_field.append(0)
    if mask_p.any():
        plus_field.append(field[mask_p].mean())
    else:
        plus_field.append(0)

ax.plot(k_range, minus_field, 'b-', linewidth=0.8, alpha=0.7, label='6k-1')
ax.plot(k_range, plus_field, 'r-', linewidth=0.8, alpha=0.7, label='6k+1')
ax.set_xlabel("k")
ax.set_ylabel("Mean EXOR field")
ax.set_title("Field by Rail (first 500 k)")
ax.legend()
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/016_exor_field/results.png', dpi=150)
print("  Saved: results.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()

# Gather key results
w_best = WINDOWS[0]
for w in WINDOWS:
    field_w = field_results[w]
    pf = field_w[lattice_prime]
    cf = field_w[~lattice_prime]
    print(f"  Window {w:.2f}: prime_mean={pf.mean():.2f}, comp_mean={cf.mean():.2f}, "
          f"ratio={pf.mean()/max(cf.mean(),1e-10):.3f}")

print()
print(f"  Effect size (Cohen's d): mean={effect_sizes.mean():+.4f}, "
      f"median={np.median(effect_sizes):+.4f}")
print(f"  AUC improvement from field: max={max(d[2]-d[1] for d in auc_data):+.4f}")
print()

if abs(effect_sizes.mean()) < 0.1 and p_perm > 0.1:
    print("  RESULT: The EXOR field adds NOTHING beyond the density gradient.")
    print("  Composite neighborhoods do not create detectable exclusion fields.")
    print("  Primes are not spatially separated from composites in log-space")
    print("  beyond what PNT already explains. Multiplication is combinatorial,")
    print("  not wave-like.")
elif p_perm < 0.05 and effect_sizes.mean() < -0.2:
    print("  RESULT: Weak signal detected — primes may sit in slightly lower-field")
    print("  regions. But this needs rigorous interpretation.")
else:
    print(f"  RESULT: Marginal (d={effect_sizes.mean():+.3f}, p_perm={p_perm:.4f}).")
    print("  Any signal is weak and likely explained by density gradient artifacts.")

print()
print("Done.")
