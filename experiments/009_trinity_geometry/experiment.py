"""
Experiment 009: L-P-V Trinity Geometry for Mass Prediction
============================================================
Tests whether a 120-degree symmetric basis (Light, Pressure, Volume)
improves atomic mass prediction over flat scale terms.

The trinity vector T(Z) = L*e_L + P*e_P + V*e_V lives in 3D with
120-degree separation between axes. We test:
  - |T(Z)| as a combined energy term
  - Individual projections onto each axis
  - Cross terms (L*P, P*V, V*L interactions)

Compared against baseline from experiment 008.
Same train/test split: Z=1-20 train, Z=21-30 test.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ====================================================================
#  ATOMIC MASS DATA
# ====================================================================
atomic_masses = {
    1: 1.008, 2: 4.0026, 3: 6.94, 4: 9.0122, 5: 10.81,
    6: 12.011, 7: 14.007, 8: 15.999, 9: 18.998, 10: 20.180,
    11: 22.990, 12: 24.305, 13: 26.982, 14: 28.085, 15: 30.974,
    16: 32.06, 17: 35.45, 18: 39.948, 19: 39.098, 20: 40.078,
    21: 44.956, 22: 47.867, 23: 50.942, 24: 51.996, 25: 54.938,
    26: 55.845, 27: 58.933, 28: 58.693, 29: 63.546, 30: 65.38,
}

# ====================================================================
#  TRINITY BASIS (120-degree symmetry)
# ====================================================================
e_L = np.array([1.0, 0.0, 0.0])
e_P = np.array([-0.5, np.sqrt(3)/2, 0.0])
e_V = np.array([-0.5, -np.sqrt(3)/2, 0.0])

# Verify 120-degree separation
print("Basis verification:")
print(f"  e_L . e_P = {e_L @ e_P:.4f} (should be -0.5)")
print(f"  e_P . e_V = {e_P @ e_V:.4f} (should be -0.5)")
print(f"  e_V . e_L = {e_V @ e_L:.4f} (should be -0.5)")
print()

# ====================================================================
#  PHYSICAL SCALING FUNCTIONS
# ====================================================================
def L_func(Z):
    """Light/radiation/temperature: proportional to T^4
    Use nuclear temperature proxy ~ Z^0.5 (binding energy per nucleon scaling)"""
    return Z ** 0.5

def P_func(Z):
    """Pressure: nuclear Coulomb ~ Z^2"""
    return Z ** 2

def V_func(Z):
    """Volume: electron shell / nuclear surface ~ Z^(2/3)"""
    return Z ** (2/3)

def trinity_vector(Z):
    """Compute T(Z) = L*e_L + P*e_P + V*e_V"""
    L = L_func(Z)
    P = P_func(Z)
    V = V_func(Z)
    return L * e_L + P * e_P + V * e_V

def trinity_magnitude(Z):
    """|T(Z)|"""
    return np.linalg.norm(trinity_vector(Z))

# ====================================================================
#  BUILD DATASET
# ====================================================================
Z_all = np.arange(1, 31)
masses = np.array([atomic_masses[z] for z in Z_all])
y = np.log(masses)

# Standard features (from exp 008)
f_z23 = Z_all ** (2/3)
f_z2 = Z_all ** 2

# Trinity features
T_vecs = np.array([trinity_vector(z) for z in Z_all])
f_T_mag = np.array([trinity_magnitude(z) for z in Z_all])
f_T_x = T_vecs[:, 0]
f_T_y = T_vecs[:, 1]
f_T_z = T_vecs[:, 2]

# Projections onto individual axes
f_proj_L = np.array([trinity_vector(z) @ e_L for z in Z_all])
f_proj_P = np.array([trinity_vector(z) @ e_P for z in Z_all])
f_proj_V = np.array([trinity_vector(z) @ e_V for z in Z_all])

# Individual scaling terms
f_L = np.array([L_func(z) for z in Z_all])
f_P = np.array([P_func(z) for z in Z_all])
f_V = np.array([V_func(z) for z in Z_all])

# Cross terms
f_LP = f_L * f_P
f_PV = f_P * f_V
f_VL = f_V * f_L

# ====================================================================
#  TRAIN/TEST SPLIT
# ====================================================================
train = Z_all <= 20
test = Z_all > 20

y_train, y_test = y[train], y[test]
mass_test = masses[test]

# ====================================================================
#  MODEL FITTING
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 009: L-P-V TRINITY GEOMETRY")
print("=" * 70)
print()

def fit_and_eval(X_tr, y_tr, X_te, y_te, mass_te, label):
    model = LinearRegression().fit(X_tr, y_tr)
    pred_tr = model.predict(X_tr)
    pred_te = model.predict(X_te)
    mass_pred = np.exp(pred_te)
    rmse_tr = np.sqrt(np.mean((pred_tr - y_tr)**2))
    rmse_te = np.sqrt(np.mean((pred_te - y_te)**2))
    mae_te = np.mean(np.abs(mass_pred - mass_te))
    mape_te = np.mean(np.abs(mass_pred - mass_te) / mass_te) * 100
    return {
        "label": label, "model": model, "coef": model.coef_,
        "rmse_train": rmse_tr, "rmse_test": rmse_te,
        "mae_test": mae_te, "mape_test": mape_te,
        "mass_pred": mass_pred,
    }

def make(mask, *features):
    return np.column_stack([f[mask] for f in features])

models = {}

# --- Baseline models (from exp 008) ---
models["A: Flat scale"] = fit_and_eval(
    make(train, f_z23, f_z2), y_train,
    make(test, f_z23, f_z2), y_test, mass_test,
    "A: Flat scale (Z^2/3, Z^2)")

# --- Trinity magnitude model ---
models["B: |T(Z)| only"] = fit_and_eval(
    make(train, f_T_mag), y_train,
    make(test, f_T_mag), y_test, mass_test,
    "B: |T(Z)| only")

# --- Trinity + flat scale ---
models["C: Flat + |T|"] = fit_and_eval(
    make(train, f_z23, f_z2, f_T_mag), y_train,
    make(test, f_z23, f_z2, f_T_mag), y_test, mass_test,
    "C: Flat scale + |T(Z)|")

# --- Trinity vector components ---
models["D: T components"] = fit_and_eval(
    make(train, f_T_x, f_T_y), y_train,
    make(test, f_T_x, f_T_y), y_test, mass_test,
    "D: T(Z) vector (x, y)")

# --- Full trinity: components + magnitude ---
models["E: Full trinity"] = fit_and_eval(
    make(train, f_T_x, f_T_y, f_T_mag), y_train,
    make(test, f_T_x, f_T_y, f_T_mag), y_test, mass_test,
    "E: T(Z) full (x, y, |T|)")

# --- Individual L, P, V (without geometry) ---
models["F: L, P, V flat"] = fit_and_eval(
    make(train, f_L, f_P, f_V), y_train,
    make(test, f_L, f_P, f_V), y_test, mass_test,
    "F: L, P, V as flat features")

# --- Projections onto trinity axes ---
models["G: Axis projections"] = fit_and_eval(
    make(train, f_proj_L, f_proj_P, f_proj_V), y_train,
    make(test, f_proj_L, f_proj_P, f_proj_V), y_test, mass_test,
    "G: T(Z) projected onto e_L, e_P, e_V")

# --- Cross terms ---
models["H: Cross terms"] = fit_and_eval(
    make(train, f_LP, f_PV, f_VL), y_train,
    make(test, f_LP, f_PV, f_VL), y_test, mass_test,
    "H: L*P, P*V, V*L cross terms")

# --- Kitchen sink ---
models["I: All combined"] = fit_and_eval(
    make(train, f_z23, f_z2, f_T_x, f_T_y, f_T_mag, f_proj_L, f_proj_P, f_proj_V),
    y_train,
    make(test, f_z23, f_z2, f_T_x, f_T_y, f_T_mag, f_proj_L, f_proj_P, f_proj_V),
    y_test, mass_test,
    "I: All features combined")

# ====================================================================
#  RESULTS
# ====================================================================
print(f"  {'Model':<25} {'RMSE tr':>9} {'RMSE te':>9} {'MAE te':>8} {'MAPE te':>9}")
print("  " + "-" * 65)

# Sort by test RMSE (lower is better)
sorted_models = sorted(models.items(), key=lambda x: x[1]["rmse_test"])
for name, r in sorted_models:
    print(f"  {r['label']:<25} {r['rmse_train']:>9.4f} {r['rmse_test']:>9.4f} "
          f"{r['mae_test']:>8.3f} {r['mape_test']:>9.2f}%")

print()

# ====================================================================
#  STATISTICAL ANALYSIS
# ====================================================================
print("=" * 70)
print("  STATISTICAL ANALYSIS")
print("=" * 70)
print()

# Compare best trinity model vs flat baseline
baseline = models["A: Flat scale"]
best_trinity_name = min(
    [(n, r) for n, r in models.items() if "Flat scale" not in n and "flat" not in n.lower()],
    key=lambda x: x[1]["rmse_test"]
)
best_name, best = best_trinity_name

delta_rmse = baseline["rmse_test"] - best["rmse_test"]
delta_mape = baseline["mape_test"] - best["mape_test"]
print(f"  Baseline (A): RMSE={baseline['rmse_test']:.4f}, MAPE={baseline['mape_test']:.2f}%")
print(f"  Best trinity ({best_name}): RMSE={best['rmse_test']:.4f}, MAPE={best['mape_test']:.2f}%")
print(f"  Improvement: RMSE {delta_rmse:+.4f}, MAPE {delta_mape:+.2f}%")
print()

# Coefficient analysis for best model
X_best_train = make(train, *([f_T_x, f_T_y] if "components" in best_name or "full" in best_name.lower()
                              else [f_T_mag]))
# Actually let me check which features the best model uses
best_features = best["model"].n_features_in_
print(f"  Best model uses {best_features} features")
print(f"  Coefficients: {best['coef']}")
print()

# Paired t-test on residuals
resid_baseline = baseline["mass_pred"] - mass_test
resid_best = best["mass_pred"] - mass_test
t_stat, p_val = stats.ttest_rel(np.abs(resid_baseline), np.abs(resid_best))
print(f"  Paired t-test on |residuals|:")
print(f"    t = {t_stat:.4f}, p = {p_val:.4f}")
if p_val < 0.05:
    print(f"    SIGNIFICANT difference")
else:
    print(f"    NOT significant")
print()

# Permutation test for trinity magnitude
n_perms = 1000
perm_rmse = []
for _ in range(n_perms):
    perm = np.random.permutation(len(f_T_mag))
    X_perm = np.column_stack([f_z23[train], f_z2[train], f_T_mag[perm][train]])
    X_perm_te = np.column_stack([f_z23[test], f_z2[test], f_T_mag[perm][test]])
    m = LinearRegression().fit(X_perm, y_train)
    rmse = np.sqrt(np.mean((m.predict(X_perm_te) - y_test)**2))
    perm_rmse.append(rmse)

perm_rmse = np.array(perm_rmse)
trinity_rmse = models["C: Flat + |T|"]["rmse_test"]
p_perm = np.mean(perm_rmse <= trinity_rmse)

print(f"  Permutation test for |T(Z)| (n={n_perms}):")
print(f"    |T| RMSE: {trinity_rmse:.4f}")
print(f"    Perm mean: {np.mean(perm_rmse):.4f}")
print(f"    p-value: {p_perm:.4f}")
if p_perm < 0.05:
    print(f"    |T(Z)| IS significant")
else:
    print(f"    |T(Z)| is NOT significant")
print()

# ====================================================================
#  CORRELATION ANALYSIS: trinity features vs mass
# ====================================================================
print("=" * 70)
print("  FEATURE CORRELATIONS WITH log(MASS)")
print("=" * 70)
print()

feature_names = [
    ("Z^(2/3)", f_z23), ("Z^2", f_z2),
    ("L(Z) = Z^0.5", f_L), ("P(Z) = Z^2", f_P), ("V(Z) = Z^(2/3)", f_V),
    ("|T(Z)|", f_T_mag),
    ("T_x", f_T_x), ("T_y", f_T_y),
    ("proj_L", f_proj_L), ("proj_P", f_proj_P), ("proj_V", f_proj_V),
    ("L*P", f_LP), ("P*V", f_PV), ("V*L", f_VL),
]

for name, feat in feature_names:
    r, p = stats.pearsonr(feat, y)
    print(f"  {name:<18} r={r:>8.4f}  p={p:.2e}")

print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Actual vs Predicted
ax = axes[0, 0]
ax.scatter(Z_all[test], mass_test, s=80, color='black', label='Actual', zorder=5)
for name in ["A: Flat scale", "D: T components", "E: Full trinity"]:
    r = models[name]
    ax.plot(Z_all[test], r["mass_pred"], '--', label=f"{name} ({r['mape_test']:.1f}%)", markersize=5)
ax.set_xlabel("Z")
ax.set_ylabel("Atomic Mass (u)")
ax.set_title("Test Set Predictions (Z=21-30)")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

# Plot 2: Trinity space visualization
ax = axes[0, 1]
# Plot the basis vectors
for vec, label, color in [(e_L, "L (Z^0.5)", "red"),
                           (e_P, "P (Z^2)", "blue"),
                           (e_V, "V (Z^(2/3))", "green")]:
    ax.annotate("", xy=(vec[0]*2, vec[1]*2), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color=color, lw=2))
    ax.text(vec[0]*2.2, vec[1]*2.2, label, color=color, fontsize=9, ha='center')

# Plot T(Z) for each Z
for z in Z_all:
    tv = trinity_vector(z)
    alpha = 0.3 if z <= 20 else 0.9
    size = 20 if z <= 20 else 50
    ax.scatter(tv[0], tv[1], s=size, alpha=alpha, color='steelblue', zorder=5)
    if z > 20:
        ax.annotate(str(z), (tv[0], tv[1]), textcoords='offset points',
                    xytext=(5, 5), fontsize=7)

circle = plt.Circle((0, 0), 0.1, fill=False, color='gray', linestyle='--', alpha=0.3)
ax.add_patch(circle)
ax.set_aspect('equal')
ax.set_title("Trinity Space (120 deg basis)")
ax.set_xlim(-5, 3)
ax.set_ylim(-4, 4)
ax.grid(True, alpha=0.2)

# Plot 3: Model comparison bar chart
ax = axes[1, 0]
names_short = [n.split(":")[0] for n in [k for k, _ in sorted_models]]
rmses = [v["rmse_test"] for _, v in sorted_models]
colors = ['steelblue' if 'Flat' in v["label"] else 'coral' for _, v in sorted_models]
ax.barh(range(len(names_short)), rmses, color=colors)
ax.set_yticks(range(len(names_short)))
ax.set_yticklabels([v["label"] for _, v in sorted_models], fontsize=7)
ax.set_xlabel("Test RMSE (lower = better)")
ax.set_title("Model Comparison")
ax.grid(True, alpha=0.2, axis='x')

# Plot 4: Residual comparison
ax = axes[1, 1]
for name in ["A: Flat scale", "D: T components", "E: Full trinity"]:
    r = models[name]
    resid = (r["mass_pred"] - mass_test) / mass_test * 100
    ax.plot(Z_all[test], resid, '--', label=name, markersize=5)
ax.axhline(y=0, color='black', linewidth=0.5)
ax.set_xlabel("Z")
ax.set_ylabel("Error (%)")
ax.set_title("Test Set Residuals")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/009_trinity_geometry/results.png', dpi=150)
print("  Saved: results.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()

for name, r in sorted_models:
    print(f"  {r['label']:<25} RMSE={r['rmse_test']:.4f}  MAPE={r['mape_test']:.2f}%")

print()
if abs(delta_rmse) > 0.05 and p_val < 0.05:
    print("  RESULT: Trinity geometry SIGNIFICANTLY improves mass prediction")
elif abs(delta_rmse) > 0.02:
    print("  RESULT: Trinity geometry shows marginal improvement (not significant)")
else:
    print("  RESULT: Trinity geometry adds NO meaningful improvement")
    print("  L(Z), P(Z), V(Z) are just Z-power functions in a rotated basis")
    print("  The 120-degree geometry doesn't create new information")

print()
print("Done.")
