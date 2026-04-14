"""
Experiment 008: Does phi-phase improve atomic mass prediction?
==============================================================
Compares three models for predicting atomic mass:

  Model A: scale only  (Z^2/3, Z^2)
  Model B: scale + prime-space alignment
  Model C: scale + prime-space + phi-phase term
  Model D: scale + prime-space + random-phase control

Train: Z=1-20, Test: Z=21-30
Controls for overfitting and false positives.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ====================================================================
#  ATOMIC MASS DATA (u = atomic mass units)
# ====================================================================
# Standard atomic weights for Z=1..30
# From NIST standard atomic weights
atomic_masses = {
    1: 1.008,      # H
    2: 4.0026,     # He
    3: 6.94,       # Li
    4: 9.0122,     # Be
    5: 10.81,      # B
    6: 12.011,     # C
    7: 14.007,     # N
    8: 15.999,     # O
    9: 18.998,     # F
    10: 20.180,    # Ne
    11: 22.990,    # Na
    12: 24.305,    # Mg
    13: 26.982,    # Al
    14: 28.085,    # Si
    15: 30.974,    # P
    16: 32.06,     # S
    17: 35.45,     # Cl
    18: 39.948,    # Ar
    19: 39.098,    # K
    20: 40.078,    # Ca
    21: 44.956,    # Sc
    22: 47.867,    # Ti
    23: 50.942,    # V
    24: 51.996,    # Cr
    25: 54.938,    # Mn
    26: 55.845,    # Fe
    27: 58.933,    # Co
    28: 58.693,    # Ni
    29: 63.546,    # Cu
    30: 65.38,     # Zn
}

# ====================================================================
#  FEATURE COMPUTATION
# ====================================================================
phi = (1 + 5**0.5) / 2

def prime_factors(z):
    """Get prime factorization as dict {prime: exponent}"""
    factors = {}
    d = 2
    n = z
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def prime_vector(z, max_prime=30):
    """Prime exponent vector for z"""
    # Get all primes up to max_prime
    primes = []
    for p in range(2, max_prime + 1):
        is_prime = True
        for i in range(2, int(p**0.5) + 1):
            if p % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(p)

    factors = prime_factors(z)
    vec = np.array([factors.get(p, 0) for p in primes], dtype=float)
    return vec, primes

def structure_alignment(z):
    """Alignment of z's prime vector with a learned basis.
    Use magnitude of prime vector as a simple proxy for complexity."""
    vec, _ = prime_vector(z)
    norm = np.linalg.norm(vec)
    if norm < 1e-10:
        return 0.0
    # Count distinct prime factors (structural complexity)
    n_factors = np.sum(vec > 0)
    # Sum of exponents (multiplicative complexity)
    total_exp = np.sum(vec)
    return n_factors * total_exp

def theta(z):
    """Log-phase angle"""
    return 2 * np.pi * (np.log(z) % 1)

def phi_phase_error(z):
    """Circular distance from golden ratio phase"""
    th = theta(z)
    th_phi = theta(phi)
    diff = th - th_phi
    return 1 - np.cos(diff)

def random_phase_error(z, seed_angle):
    """Control: distance from random angle"""
    th = theta(z)
    diff = th - seed_angle
    return 1 - np.cos(diff)

# ====================================================================
#  BUILD DATASET
# ====================================================================
Z_all = np.arange(1, 31)
masses = np.array([atomic_masses[z] for z in Z_all])

# Features
f_surface = Z_all ** (2/3)   # surface term
f_coulomb = Z_all ** 2        # Coulomb term
f_structure = np.array([structure_alignment(z) for z in Z_all])
f_phi = np.array([phi_phase_error(z) for z in Z_all])

# Multiple random phase controls
np.random.seed(42)
random_angles = np.random.uniform(0, 2 * np.pi, 10)
f_random = np.array([[random_phase_error(z, a) for z in Z_all] for a in random_angles])

# Log of masses (target)
y = np.log(masses)

# ====================================================================
#  TRAIN/TEST SPLIT
# ====================================================================
train_mask = Z_all <= 20
test_mask = Z_all > 20

Z_train, Z_test = Z_all[train_mask], Z_all[test_mask]
y_train, y_test = y[train_mask], y[test_mask]
mass_train, mass_test = masses[train_mask], masses[test_mask]

# ====================================================================
#  MODEL FITTING
# ====================================================================
print("=" * 70)
print("  EXPERIMENT 008: PHI-PHASE MASS PREDICTION")
print("=" * 70)
print()
print(f"  Train: Z=1-20 (n={train_mask.sum()})")
print(f"  Test:  Z=21-30 (n={test_mask.sum()})")
print()

def fit_model(X_train, y_train, X_test, y_test, mass_test, label):
    """Fit linear regression and compute metrics."""
    model = LinearRegression().fit(X_train, y_train)
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # Metrics on log scale
    mse_train = np.mean((y_pred_train - y_train) ** 2)
    mse_test = np.mean((y_pred_test - y_test) ** 2)
    rmse_train = np.sqrt(mse_train)
    rmse_test = np.sqrt(mse_test)

    # Metrics on original scale
    mass_pred_test = np.exp(y_pred_test)
    mae_test = np.mean(np.abs(mass_pred_test - mass_test))
    mape_test = np.mean(np.abs(mass_pred_test - mass_test) / mass_test) * 100

    return {
        "label": label, "model": model, "coef": model.coef_,
        "rmse_train": rmse_train, "rmse_test": rmse_test,
        "mae_test": mae_test, "mape_test": mape_test,
        "y_pred_test": y_pred_test, "mass_pred_test": mass_pred_test,
    }

# Feature matrices
def make_features(Z_idx, features):
    """Build feature matrix from feature arrays."""
    return np.column_stack([f[Z_idx] for f in features])

# Model A: scale only
rA = fit_model(
    np.column_stack([f_surface[train_mask], f_coulomb[train_mask]]),
    y_train,
    np.column_stack([f_surface[test_mask], f_coulomb[test_mask]]),
    y_test, mass_test,
    "A: Scale only (Z^2/3, Z^2)")

# Model B: scale + structure
rB = fit_model(
    np.column_stack([f_surface[train_mask], f_coulomb[train_mask],
                     f_structure[train_mask]]),
    y_train,
    np.column_stack([f_surface[test_mask], f_coulomb[test_mask],
                     f_structure[test_mask]]),
    y_test, mass_test,
    "B: Scale + Structure")

# Model C: scale + structure + phi
rC = fit_model(
    np.column_stack([f_surface[train_mask], f_coulomb[train_mask],
                     f_structure[train_mask], f_phi[train_mask]]),
    y_train,
    np.column_stack([f_surface[test_mask], f_coulomb[test_mask],
                     f_structure[test_mask], f_phi[test_mask]]),
    y_test, mass_test,
    "C: Scale + Structure + phi-phase")

# Model D: scale + structure + random (10 controls)
random_results = []
for i in range(10):
    rD = fit_model(
        np.column_stack([f_surface[train_mask], f_coulomb[train_mask],
                         f_structure[train_mask], f_random[i][train_mask]]),
        y_train,
        np.column_stack([f_surface[test_mask], f_coulomb[test_mask],
                         f_structure[test_mask], f_random[i][test_mask]]),
        y_test, mass_test,
        f"D{i}: Scale + Structure + random-phase")
    random_results.append(rD)

# ====================================================================
#  RESULTS
# ====================================================================
print("=" * 70)
print("  MODEL COMPARISON")
print("=" * 70)
print()
print(f"  {'Model':<40} {'RMSE train':>11} {'RMSE test':>11} "
      f"{'MAE test':>9} {'MAPE test':>10}")
print("  " + "-" * 85)

for r in [rA, rB, rC]:
    print(f"  {r['label']:<40} {r['rmse_train']:>11.4f} {r['rmse_test']:>11.4f} "
          f"{r['mae_test']:>9.3f} {r['mape_test']:>10.2f}%")

print()

# Random control summary
rand_rmses = [r['rmse_test'] for r in random_results]
rand_maes = [r['mae_test'] for r in random_results]
rand_mapes = [r['mape_test'] for r in random_results]

print(f"  Random controls (n=10):")
print(f"    RMSE test: {np.mean(rand_rmses):.4f} +/- {np.std(rand_rmses):.4f}")
print(f"    MAE test:  {np.mean(rand_maes):.3f} +/- {np.std(rand_maes):.3f}")
print(f"    MAPE test: {np.mean(rand_mapes):.2f}% +/- {np.std(rand_mapes):.2f}%")
print()

# ====================================================================
#  STATISTICAL TEST
# ====================================================================
print("=" * 70)
print("  STATISTICAL ANALYSIS")
print("=" * 70)
print()

# 1. Does phi improve over model B?
delta_rmse = rB['rmse_test'] - rC['rmse_test']
delta_mae = rB['mae_test'] - rC['mae_test']
print(f"  phi vs no-phi (C vs B):")
print(f"    Delta RMSE test: {delta_rmse:+.4f} ({'better' if delta_rmse > 0 else 'worse'})")
print(f"    Delta MAE test:  {delta_mae:+.3f} ({'better' if delta_mae > 0 else 'worse'})")
print()

# 2. Is phi coefficient significant?
# Use statsmodels for proper t-test on coefficients
from numpy.linalg import lstsq

X_B_train = np.column_stack([f_surface[train_mask], f_coulomb[train_mask],
                              f_structure[train_mask]])
X_C_train = np.column_stack([f_surface[train_mask], f_coulomb[train_mask],
                              f_structure[train_mask], f_phi[train_mask]])

# Add intercept
X_B_i = np.column_stack([np.ones(X_B_train.shape[0]), X_B_train])
X_C_i = np.column_stack([np.ones(X_C_train.shape[0]), X_C_train])

# Fit C with stats for coefficient test
beta_C, residuals, rank, sv = lstsq(X_C_i, y_train, rcond=None)
n_train = X_C_i.shape[0]
p_C = X_C_i.shape[1]
mse_C = np.sum((y_train - X_C_i @ beta_C) ** 2) / (n_train - p_C)
var_beta = mse_C * np.linalg.inv(X_C_i.T @ X_C_i).diagonal()
se_beta = np.sqrt(np.abs(var_beta))
t_stats = beta_C / (se_beta + 1e-10)

feature_names_C = ['intercept', 'Z^(2/3)', 'Z^2', 'structure', 'phi-phase']

print(f"  Model C coefficients:")
print(f"  {'Feature':<15} {'Coef':>10} {'SE':>10} {'t-stat':>10} {'p-value':>12}")
print("  " + "-" * 60)
for i, name in enumerate(feature_names_C):
    p_val = 2 * (1 - stats.t.cdf(abs(t_stats[i]), n_train - p_C))
    print(f"  {name:<15} {beta_C[i]:>10.6f} {se_beta[i]:>10.6f} "
          f"{t_stats[i]:>10.4f} {p_val:>12.6f}")

print()

# 3. Is phi better than random?
phi_rmse = rC['rmse_test']
z_score = (phi_rmse - np.mean(rand_rmses)) / (np.std(rand_rmses) + 1e-10)
p_vs_random = stats.norm.cdf(z_score)

print(f"  phi vs random controls:")
print(f"    phi RMSE:    {phi_rmse:.4f}")
print(f"    random mean: {np.mean(rand_rmses):.4f}")
print(f"    z-score:     {z_score:.4f}")
print(f"    p-value:     {p_vs_random:.4f}")
if p_vs_random > 0.05:
    print(f"    phi is NOT significantly different from random")
else:
    print(f"    phi IS significantly different from random")
print()

# 4. Permutation test: shuffle phi labels
n_perms = 1000
perm_deltas = []
for _ in range(n_perms):
    perm_idx = np.random.permutation(len(f_phi))
    f_phi_perm = f_phi[perm_idx]

    X_perm = np.column_stack([f_surface[train_mask], f_coulomb[train_mask],
                               f_structure[train_mask], f_phi_perm[train_mask]])
    X_perm_test = np.column_stack([f_surface[test_mask], f_coulomb[test_mask],
                                    f_structure[test_mask], f_phi_perm[test_mask]])

    m_perm = LinearRegression().fit(X_perm, y_train)
    rmse_perm = np.sqrt(np.mean((m_perm.predict(X_perm_test) - y_test) ** 2))
    perm_deltas.append(rmse_perm)

perm_deltas = np.array(perm_deltas)
perm_p = np.mean(perm_deltas <= phi_rmse)

print(f"  Permutation test (n={n_perms}):")
print(f"    phi RMSE: {phi_rmse:.4f}")
print(f"    Permutation mean: {np.mean(perm_deltas):.4f}")
print(f"    p-value: {perm_p:.4f}")
if perm_p > 0.05:
    print(f"    phi is NOT significant under permutation test")
else:
    print(f"    phi IS significant under permutation test")
print()

# ====================================================================
#  VISUALIZATION
# ====================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Actual vs Predicted (test set)
ax = axes[0, 0]
ax.scatter(Z_test, mass_test, s=80, color='black', label='Actual', zorder=5)
ax.plot(Z_test, rA['mass_pred_test'], 'r--o', label=f"A: Scale (MAPE={rA['mape_test']:.1f}%)", markersize=5)
ax.plot(Z_test, rB['mass_pred_test'], 'b--s', label=f"B: +Structure (MAPE={rB['mape_test']:.1f}%)", markersize=5)
ax.plot(Z_test, rC['mass_pred_test'], 'g--^', label=f"C: +phi (MAPE={rC['mape_test']:.1f}%)", markersize=5)
ax.set_xlabel("Z")
ax.set_ylabel("Atomic Mass (u)")
ax.set_title("Test Set: Actual vs Predicted (Z=21-30)")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# Plot 2: Residuals
ax = axes[0, 1]
for r, color, marker in [(rA, 'red', 'o'), (rB, 'blue', 's'), (rC, 'green', '^')]:
    residuals_pct = (r['mass_pred_test'] - mass_test) / mass_test * 100
    ax.plot(Z_test, residuals_pct, color=color, marker=marker, linestyle='--',
            label=r['label'].split(':')[0], markersize=6)
ax.axhline(y=0, color='black', linewidth=0.5)
ax.set_xlabel("Z")
ax.set_ylabel("Prediction Error (%)")
ax.set_title("Test Set Residuals")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

# Plot 3: phi feature values
ax = axes[1, 0]
ax.bar(Z_all, f_phi, color='steelblue', alpha=0.7)
ax.axvline(x=20.5, color='red', linestyle='--', alpha=0.5, label='Train/Test split')
ax.set_xlabel("Z")
ax.set_ylabel("phi-phase error")
ax.set_title("phi-phase Feature Values by Z")
ax.legend()
ax.grid(True, alpha=0.2)

# Plot 4: Random control distribution
ax = axes[1, 1]
ax.hist(rand_rmses, bins=10, color='gray', alpha=0.7, label='Random phases')
ax.axvline(x=phi_rmse, color='green', linewidth=2, label=f'phi (RMSE={phi_rmse:.4f})')
ax.axvline(x=rB['rmse_test'], color='blue', linewidth=2, label=f'No phase (RMSE={rB["rmse_test"]:.4f})')
ax.set_xlabel("Test RMSE")
ax.set_ylabel("Count")
ax.set_title("phi vs Random Phase Controls")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/008_mass_prediction/results.png', dpi=150)
print("  Saved: results.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print(f"  Model A (scale only):        RMSE test = {rA['rmse_test']:.4f}, MAPE = {rA['mape_test']:.2f}%")
print(f"  Model B (+ structure):       RMSE test = {rB['rmse_test']:.4f}, MAPE = {rB['mape_test']:.2f}%")
print(f"  Model C (+ phi-phase):       RMSE test = {rC['rmse_test']:.4f}, MAPE = {rC['mape_test']:.2f}%")
print(f"  Random controls (mean):      RMSE test = {np.mean(rand_rmses):.4f}")
print()

if abs(delta_rmse) < 0.001:
    print("  RESULT: phi-phase adds NO meaningful improvement to mass prediction")
elif delta_rmse > 0 and perm_p < 0.05:
    print("  RESULT: phi-phase SIGNIFICANTLY improves mass prediction")
elif delta_rmse > 0:
    print("  RESULT: phi-phase marginally improves prediction (not significant)")
else:
    print("  RESULT: phi-phase WORSENS prediction")

print()
print("Done.")
