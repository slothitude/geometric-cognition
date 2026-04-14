"""
Experiment 013: Log-Spiral Embedding Test
==========================================
Tests whether embedding numbers on a log spiral r=log(k), theta=alpha*log(k)
reveals any prime-specific structure beyond what log(k) already provides.

A log spiral is a reparameterization of log(k) into 2D. If phase failed
(experiments 011-012), the spiral should too — unless genuine 2D geometric
clustering exists.

Tests:
1. Angular KS test (primes vs composites on same rail)
2. Nearest-neighbor clustering in (x,y) space
3. Logistic regression AUC (can spiral coords predict primality?)
4. Permutation test (kill shot)
"""

import numpy as np
from math import log, pi, sqrt
from scipy.stats import ks_2samp
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors
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

CONSTANTS = {
    "phi": (1 + sqrt(5)) / 2,
    "sqrt2": sqrt(2),
    "e": np.e,
    "pi": pi,
}

np.random.seed(42)
for i in range(3):
    CONSTANTS[f"rand_{i}"] = np.random.uniform(1.1, 3.9)

WINDOW = 0.2

print("=" * 70)
print("  EXPERIMENT 013: LOG-SPIRAL EMBEDDING TEST")
print("=" * 70)
print()

# ====================================================================
#  BUILD 6k±1 LATTICE
# ====================================================================
print("  Building 6k±1 lattice...")
is_prime_arr = sieve(N_MAX + 10)

lattice_k = []
lattice_sign = []
lattice_is_prime = []

for k in range(1, N_MAX // 6 + 2):
    for sign in (-1, +1):
        n = 6 * k + sign
        if n < 5 or n > N_MAX:
            continue
        lattice_k.append(k)
        lattice_sign.append(sign)
        lattice_is_prime.append(is_prime_arr[n])

lattice_k = np.array(lattice_k, dtype=np.float64)
lattice_sign = np.array(lattice_sign)
lattice_is_prime = np.array(lattice_is_prime)

rail_minus = lattice_sign == -1
rail_plus = lattice_sign == +1

print(f"  Total: {len(lattice_k)}, Primes: {lattice_is_prime.sum()}, "
      f"Comps: {(~lattice_is_prime).sum()}")
print()

# ====================================================================
#  SPIRAL EMBEDDING
# ====================================================================
def spiral_embed(k_vals, alpha):
    k = np.array(k_vals, dtype=np.float64)
    r = np.log(k)
    theta = alpha * r
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return r, theta % (2 * pi), x, y

def angular_density(theta, window=WINDOW):
    return np.mean((theta < window) | (theta > 2 * pi - window))

def nn_cluster_score(xy, sample=3000):
    """Mean NN distance (lower = more clustered). Subsample for speed."""
    if len(xy) > sample:
        idx = np.random.choice(len(xy), sample, replace=False)
        xy = xy[idx]
    nbrs = NearestNeighbors(n_neighbors=2).fit(xy)
    d, _ = nbrs.kneighbors(xy)
    return d[:, 1].mean()

def compute_auc(r, theta, labels):
    X = np.vstack([r, theta]).T
    y = np.array(labels)
    clf = LogisticRegression(max_iter=300, solver='lbfgs')
    clf.fit(X, y)
    probs = clf.predict_proba(X)[:, 1]
    return roc_auc_score(y, probs)

# ====================================================================
#  EXPERIMENT 1: BASELINE (alpha=1.0)
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 1: BASELINE (theta = log k, no scaling)")
print("=" * 70)
print()

for rail_name, rail_mask in [("6k-1", rail_minus), ("6k+1", rail_plus)]:
    k_vals = lattice_k[rail_mask]
    pm = lattice_is_prime[rail_mask]

    rp, thp, xp, yp = spiral_embed(k_vals[pm], alpha=1.0)
    rc, thc, xc, yc = spiral_embed(k_vals[~pm], alpha=1.0)

    ks_stat, pval = ks_2samp(thp, thc)
    dens_ratio = angular_density(thp) / max(angular_density(thc), 1e-10)

    print(f"  Rail {rail_name}: KS={ks_stat:.4f} p={pval:.4f} dens_ratio={dens_ratio:.3f}")

print()

# ====================================================================
#  EXPERIMENT 2: CONSTANT BAKE-OFF
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 2: CONSTANT BAKE-OFF (spiral alpha)")
print("=" * 70)
print()

print(f"  {'Constant':<10} {'Rail':<6} {'KS stat':>8} {'p-value':>8} "
      f"{'Dens ratio':>11} {'Cluster ratio':>14}")
print("  " + "-" * 65)

bakeoff_results = []

for cname, alpha in CONSTANTS.items():
    for rail_name, rail_mask in [("6k-1", rail_minus), ("6k+1", rail_plus)]:
        k_vals = lattice_k[rail_mask]
        pm = lattice_is_prime[rail_mask]

        rp, thp, xp, yp = spiral_embed(k_vals[pm], alpha)
        rc, thc, xc, yc = spiral_embed(k_vals[~pm], alpha)

        ks_stat, pval = ks_2samp(thp, thc)
        dr = angular_density(thp) / max(angular_density(thc), 1e-10)

        # Clustering: sample for speed
        np.random.seed(42)
        cp = nn_cluster_score(np.column_stack([xp, yp]), sample=2000)
        cc = nn_cluster_score(np.column_stack([xc, yc]), sample=2000)
        cr = cc / max(cp, 1e-10)  # >1 means primes more clustered

        bakeoff_results.append({
            "constant": cname, "rail": rail_name,
            "ks": ks_stat, "pval": pval, "dens_ratio": dr, "cluster_ratio": cr,
        })

        sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
        print(f"  {cname:<10} {rail_name:<6} {ks_stat:>8.4f} {pval:>8.4f} "
              f"{dr:>11.3f} {cr:>14.3f} {sig}")

print()

# Check phi
phi_cr = [r["cluster_ratio"] for r in bakeoff_results if r["constant"] == "phi"]
other_cr = [r["cluster_ratio"] for r in bakeoff_results if r["constant"] not in ("phi",)]
phi_ks = [r["ks"] for r in bakeoff_results if r["constant"] == "phi"]
other_ks = [r["ks"] for r in bakeoff_results if r["constant"] not in ("phi",)]

print(f"  phi avg cluster ratio: {np.mean(phi_cr):.3f}")
print(f"  other avg cluster ratio: {np.mean(other_cr):.3f}")
print(f"  phi avg KS: {np.mean(phi_ks):.4f}")
print(f"  other avg KS: {np.mean(other_ks):.4f}")
print()

# ====================================================================
#  EXPERIMENT 3: PREDICTABILITY (AUC)
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 3: CAN SPIRAL COORDS PREDICT PRIMALITY? (AUC)")
print("=" * 70)
print()

print(f"  {'Constant':<10} {'Rail':<6} {'AUC':>8}")
print("  " + "-" * 30)

auc_results = []

for cname, alpha in CONSTANTS.items():
    for rail_name, rail_mask in [("6k-1", rail_minus), ("6k+1", rail_plus)]:
        k_vals = lattice_k[rail_mask]
        pm = lattice_is_prime[rail_mask]

        rp, thp, *_ = spiral_embed(k_vals[pm], alpha)
        rc, thc, *_ = spiral_embed(k_vals[~pm], alpha)

        r = np.concatenate([rp, rc])
        th = np.concatenate([thp, thc])
        y = np.array([1] * len(rp) + [0] * len(rc))

        auc = compute_auc(r, th, y)
        auc_results.append({"constant": cname, "rail": rail_name, "auc": auc})

        print(f"  {cname:<10} {rail_name:<6} {auc:>8.4f}")

print()

# ====================================================================
#  EXPERIMENT 4: PERMUTATION TEST (KILL SHOT)
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 4: PERMUTATION TEST (AUC)")
print("=" * 70)
print()

rng = np.random.default_rng(42)
n_perms = 100

for cname, alpha in [("phi", CONSTANTS["phi"]), ("sqrt2", CONSTANTS["sqrt2"]),
                      ("pi", CONSTANTS["pi"]), ("rand_0", CONSTANTS["rand_0"])]:
    for rail_name, rail_mask in [("6k-1", rail_minus)]:
        k_vals = lattice_k[rail_mask]
        pm = lattice_is_prime[rail_mask]

        rp, thp, *_ = spiral_embed(k_vals[pm], alpha)
        rc, thc, *_ = spiral_embed(k_vals[~pm], alpha)

        r = np.concatenate([rp, rc])
        th = np.concatenate([thp, thc])
        y = np.array([1] * len(rp) + [0] * len(rc))

        real_auc = compute_auc(r, th, y)

        null_aucs = []
        for i in range(n_perms):
            y_perm = rng.permutation(y)
            null_aucs.append(compute_auc(r, th, y_perm))

        null_aucs = np.array(null_aucs)
        z = (real_auc - null_aucs.mean()) / max(null_aucs.std(), 1e-9)
        p = np.mean(null_aucs >= real_auc)

        print(f"  {cname:<10} {rail_name}: real AUC={real_auc:.4f}  "
              f"null mean={null_aucs.mean():.4f}  z={z:+.3f}  p={p:.4f}")

print()

# ====================================================================
#  EXPERIMENT 5: CONTROL — AUC USING ONLY r (no theta)
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 5: CONTROL — AUC using r=log(k) ONLY (no theta)")
print("=" * 70)
print()

for rail_name, rail_mask in [("6k-1", rail_minus)]:
    k_vals = lattice_k[rail_mask]
    pm = lattice_is_prime[rail_mask]

    rp = np.log(k_vals[pm])
    rc = np.log(k_vals[~pm])

    r = np.concatenate([rp, rc])
    y = np.array([1] * len(rp) + [0] * len(rc))

    # Just r (magnitude) alone
    X_r = r.reshape(-1, 1)
    clf = LogisticRegression(max_iter=300).fit(X_r, y)
    auc_r_only = roc_auc_score(y, clf.predict_proba(X_r)[:, 1])

    print(f"  AUC using only r=log(k): {auc_r_only:.4f}")
    print(f"  (This is the density gradient — anything above 0.5 is just that)")
    print()

# Compare: theta adds nothing beyond r
    best_auc_with_theta = max(
        r["auc"] for r in auc_results
        if r["constant"] == "phi" and r["rail"] == rail_name
    )
    print(f"  Best AUC with phi + theta: {best_auc_with_theta:.4f}")
    print(f"  Improvement from theta: {best_auc_with_theta - auc_r_only:+.4f}")

print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Spiral visualization (subsample)
ax = axes[0, 0]
np.random.seed(42)
idx = np.random.choice(len(lattice_k[rail_minus]), 3000, replace=False)
k_sub = lattice_k[rail_minus][idx]
pm_sub = lattice_is_prime[rail_minus][idx]

for alpha, name in [(CONSTANTS["phi"], "phi"), (CONSTANTS["sqrt2"], "sqrt2")]:
    r_all, th_all, x_all, y_all = spiral_embed(k_sub, alpha)
    prime_x = x_all[pm_sub]
    prime_y = y_all[pm_sub]
    comp_x = x_all[~pm_sub]
    comp_y = y_all[~pm_sub]

    ax.scatter(comp_x, comp_y, s=0.5, alpha=0.2, color='blue', label=f'Comps ({name})')
    ax.scatter(prime_x, prime_y, s=0.5, alpha=0.3, color='red', label=f'Primes ({name})')

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Spiral Embedding (6k-1 rail, 3k points)")
ax.legend(fontsize=6, markerscale=5)
ax.grid(True, alpha=0.2)

# Plot 2: AUC comparison
ax = axes[0, 1]
const_names = list(CONSTANTS.keys())
auc_6k1 = [r["auc"] for r in auc_results if r["rail"] == "6k-1"]
colors = ['gold' if n == 'phi' else 'steelblue' for n in const_names]
ax.bar(range(len(const_names)), auc_6k1, color=colors)
ax.set_xticks(range(len(const_names)))
ax.set_xticklabels(const_names, rotation=45, fontsize=8)
ax.axhline(y=0.5, color='black', linestyle='--', label='Random (0.5)')
ax.set_ylabel("AUC")
ax.set_title("Can Spiral Coords Predict Primality? (6k-1)")
ax.legend()
ax.grid(True, alpha=0.2, axis='y')

# Plot 3: Cluster ratio comparison
ax = axes[1, 0]
cr_vals = [r["cluster_ratio"] for r in bakeoff_results if r["rail"] == "6k-1"]
colors = ['gold' if r["constant"] == "phi" else 'steelblue'
          for r in bakeoff_results if r["rail"] == "6k-1"]
ax.bar(range(len(cr_vals)), cr_vals, color=colors)
ax.set_xticks(range(len(cr_vals)))
ax.set_xticklabels([r["constant"] for r in bakeoff_results if r["rail"] == "6k-1"],
                    rotation=45, fontsize=8)
ax.axhline(y=1.0, color='black', linestyle='--', label='No effect')
ax.set_ylabel("Cluster ratio (comps_nn / primes_nn)")
ax.set_title("Clustering: Are Primes More Clustered in Spiral Space? (6k-1)")
ax.legend()
ax.grid(True, alpha=0.2, axis='y')

# Plot 4: Permutation AUC distribution
ax = axes[1, 1]
# Re-run phi permutation for visualization
alpha = CONSTANTS["phi"]
k_vals = lattice_k[rail_minus]
pm = lattice_is_prime[rail_minus]
rp, thp, *_ = spiral_embed(k_vals[pm], alpha)
rc, thc, *_ = spiral_embed(k_vals[~pm], alpha)
r = np.concatenate([rp, rc])
th = np.concatenate([thp, thc])
y = np.array([1] * len(rp) + [0] * len(rc))
real_auc = compute_auc(r, th, y)

null_aucs = []
rng = np.random.default_rng(42)
for _ in range(100):
    y_perm = rng.permutation(y)
    null_aucs.append(compute_auc(r, th, y_perm))

ax.hist(null_aucs, bins=30, color='lightgray', alpha=0.7, label='Permuted AUC')
ax.axvline(x=real_auc, color='red', linewidth=2, linestyle='--',
           label=f'Real AUC = {real_auc:.4f}')
ax.axvline(x=np.mean(null_aucs), color='black', linewidth=1, linestyle=':',
           label=f'Null mean = {np.mean(null_aucs):.4f}')
ax.set_xlabel("AUC")
ax.set_ylabel("Count")
ax.set_title("phi AUC vs Permuted Labels (6k-1)")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/013_spiral_embedding/results.png', dpi=150)
print("  Saved: results.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()

phi_aucs = [r["auc"] for r in auc_results if r["constant"] == "phi"]
other_aucs = [r["auc"] for r in auc_results if r["constant"] not in ("phi",)]

print(f"  phi avg AUC:     {np.mean(phi_aucs):.4f}")
print(f"  other avg AUC:   {np.mean(other_aucs):.4f}")
print()

best_const = min(auc_results, key=lambda r: abs(r["auc"] - 0.5))
worst_const = max(auc_results, key=lambda r: abs(r["auc"] - 0.5))

print(f"  Most predictable: {best_const['constant']} ({best_const['rail']}) AUC={best_const['auc']:.4f}")
print(f"  Least predictable: {worst_const['constant']} ({worst_const['rail']}) AUC={worst_const['auc']:.4f}")
print()

print("  VERDICT:")
if abs(np.mean(phi_aucs) - 0.5) < 0.02:
    print("  AUC ≈ 0.5 for ALL constants. Spiral coordinates cannot predict")
    print("  primality. The log-spiral is just a 2D reparameterization of")
    print("  log(k) — no new information is created by the spiral geometry.")
else:
    print(f"  phi AUC = {np.mean(phi_aucs):.4f}. Some predictability detected.")
    print("  Check permutation test to verify it's not the density gradient.")

print()
print("Done.")
