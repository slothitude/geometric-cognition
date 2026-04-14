"""
Experiment 007: Mobius Twist Dynamics
======================================
Adds the Mobius twist (unwrapped angle + polarity sigma) to both
the log-phase and prime-space encodings. Tests whether topological
structure (sigma flips on winding) preserves factor correlation
under dynamics better than the non-Mobius versions.

Key idea: sigma acts as a topological barrier that resists merging.
Crossing 2*pi flips sigma, so numbers that wind differently
stay separated even when their angles converge.
"""

import torch
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from itertools import combinations

# ---------- Prime utilities ----------
def prime_factors_of(n):
    factors = set()
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.add(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.add(temp)
    return factors

def shared_factor_count(a, b):
    return len(prime_factors_of(a) & prime_factors_of(b))

def sieve(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

def prime_exponents(n, basis):
    result = []
    temp = n
    for p in basis:
        e = 0
        while temp % p == 0 and temp > 0:
            e += 1
            temp //= p
        result.append(float(e))
    return result

# ---------- Distance & correlation ----------
def factor_correlation(numbers, dist_matrix):
    pairs = []
    for i, j in combinations(range(len(numbers)), 2):
        sf = shared_factor_count(numbers[i], numbers[j])
        d = dist_matrix[i, j].item()
        pairs.append((numbers[i], numbers[j], sf, d))
    sf_vals = [sf for _, _, sf, _ in pairs]
    d_vals = [d for _, _, _, d in pairs]
    if np.std(d_vals) < 1e-10:
        return 0.0, pairs
    corr = np.corrcoef(sf_vals, d_vals)[0, 1]
    if np.isnan(corr):
        corr = 0.0
    return corr, pairs

# ====================================================================
#  ENCODING 1: Log-phase + Mobius twist
# ====================================================================
def encode_log_mobius(numbers):
    """Encode with unwrapped angle + initial sigma = +1"""
    x = torch.tensor(numbers, dtype=torch.float32)
    theta_unwrapped = 2 * math.pi * torch.log(x + 1e-8)
    sigma = torch.ones(len(numbers))  # all start positive
    return theta_unwrapped, sigma

def mobius_distance_log(theta_u, sigma, polarity_weight=1.0):
    """
    Distance accounting for both circular distance and polarity mismatch.
    theta_u: unwrapped angles
    sigma: polarities (+1/-1)
    """
    n = len(theta_u)
    # Project to circle for angular distance
    theta = theta_u % (2 * math.pi)

    # Circular distance
    diff = torch.abs(theta.unsqueeze(1) - theta.unsqueeze(0))
    d_theta = torch.minimum(diff, 2 * math.pi - diff)

    # Polarity penalty
    sigma_match = (sigma.unsqueeze(1) * sigma.unsqueeze(0))
    d_sigma = torch.where(sigma_match > 0,
                          torch.zeros_like(sigma_match),
                          torch.ones_like(sigma_match) * math.pi)

    return d_theta + polarity_weight * d_sigma

# ====================================================================
#  ENCODING 2: Prime-space + Mobius twist (per-prime sigma)
# ====================================================================
def encode_prime_mobius(numbers, basis):
    """
    Encode as prime exponent vectors, but track unwrapped angle per
    prime dimension with individual sigmas.
    """
    vectors = torch.tensor([prime_exponents(n, basis) for n in numbers],
                           dtype=torch.float32)
    # Each prime dimension has an unwrapped angle and sigma
    # theta_d = 2*pi * e_d (unwrapped)
    # sigma_d starts at +1
    theta_unwrapped = 2 * math.pi * vectors  # [n, d] unwrapped
    sigma = torch.ones(len(numbers), len(basis))  # all +1
    return vectors, theta_unwrapped, sigma

def mobius_distance_prime(theta_u, sigma, polarity_weight=1.0):
    """
    Per-dimension Mobius distance, summed across prime dimensions.
    """
    n, d = theta_u.shape
    total_dist = torch.zeros(n, n)

    for dim in range(d):
        theta = theta_u[:, dim] % (2 * math.pi)
        diff = torch.abs(theta.unsqueeze(1) - theta.unsqueeze(0))
        d_theta = torch.minimum(diff, 2 * math.pi - diff)

        sigma_match = (sigma[:, dim].unsqueeze(1) * sigma[:, dim].unsqueeze(0))
        d_sigma = torch.where(sigma_match > 0,
                              torch.zeros(n, n),
                              torch.ones(n, n) * math.pi)

        total_dist += d_theta + polarity_weight * d_sigma

    return total_dist

# ====================================================================
#  MOBIUS-AWARE DYNAMICS
# ====================================================================
def evolve_mobius_log(numbers, steps=50, lambda_param=2.5,
                      repel_strength=0.15, lr=0.05, polarity_weight=1.0):
    """Circular dynamics with Mobius twist on log-phase encoding."""
    theta_u, sigma = encode_log_mobius(numbers)
    n = len(numbers)

    corrs = []

    for step in range(steps):
        dist = mobius_distance_log(theta_u, sigma, polarity_weight)
        corr, _ = factor_correlation(numbers, dist)
        corrs.append(corr)

        # Attention (no self)
        dist_ns = dist.clone()
        dist_ns.fill_diagonal_(float('inf'))
        scores = torch.exp(-lambda_param * dist_ns)
        attn = scores / scores.sum(dim=1, keepdim=True)

        # Attraction: weighted average of UNWRAPPED angles
        attracted_theta = attn @ theta_u

        # Repulsion (in angle space)
        theta_circle = theta_u % (2 * math.pi)
        repulsion = torch.zeros(n)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                d_ij = dist[i, j] + 1e-6
                strength = repel_strength / (d_ij ** 2)
                # Direction on circle
                diff = theta_circle[i] - theta_circle[j]
                # Shortest path direction
                if diff > math.pi:
                    diff -= 2 * math.pi
                elif diff < -math.pi:
                    diff += 2 * math.pi
                repulsion[i] += strength * np.sign(diff)

        # Update unwrapped angle
        theta_new = theta_u + lr * ((attracted_theta - theta_u) + repulsion)

        # Guard against NaN
        if torch.isnan(theta_new).any():
            break

        # Check for 2*pi crossings and flip sigma
        for i in range(n):
            k_old = math.floor(theta_u[i].item() / (2 * math.pi))
            k_new = math.floor(theta_new[i].item() / (2 * math.pi))
            if k_new != k_old:
                # Crossed a boundary — flip sigma
                sigma[i] *= (-1) ** abs(k_new - k_old)

        theta_u = theta_new

    final_dist = mobius_distance_log(theta_u, sigma, polarity_weight)
    return theta_u, sigma, corrs, final_dist

def evolve_mobius_prime(numbers, basis, steps=50, lambda_param=2.5,
                         repel_strength=0.15, lr=0.05, polarity_weight=1.0):
    """Prime-space dynamics with per-dimension Mobius twist."""
    vectors, theta_u, sigma = encode_prime_mobius(numbers, basis)
    n, d = theta_u.shape

    corrs = []

    for step in range(steps):
        dist = mobius_distance_prime(theta_u, sigma, polarity_weight)
        corr, _ = factor_correlation(numbers, dist)
        corrs.append(corr)

        # Attention (no self)
        dist_ns = dist.clone()
        dist_ns.fill_diagonal_(float('inf'))
        scores = torch.exp(-lambda_param * dist_ns)
        attn = scores / scores.sum(dim=1, keepdim=True)

        # Attraction: weighted average of unwrapped angles per dimension
        attracted_theta = attn @ theta_u  # [n, d]

        # Repulsion
        repulsion = torch.zeros(n, d)
        for dim in range(d):
            theta_circle = theta_u[:, dim] % (2 * math.pi)
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    d_ij = dist[i, j] + 1e-6
                    strength = repel_strength / (d_ij ** 2)
                    diff = theta_circle[i] - theta_circle[j]
                    if diff > math.pi:
                        diff -= 2 * math.pi
                    elif diff < -math.pi:
                        diff += 2 * math.pi
                    repulsion[i, dim] += strength * np.sign(diff)

        # Update
        theta_new = theta_u + lr * ((attracted_theta - theta_u) + repulsion)

        # Guard against NaN
        if torch.isnan(theta_new).any():
            break

        # Check crossings per dimension
        for i in range(n):
            for dim in range(d):
                k_old = math.floor(theta_u[i, dim].item() / (2 * math.pi))
                k_new = math.floor(theta_new[i, dim].item() / (2 * math.pi))
                if k_new != k_old:
                    sigma[i, dim] *= (-1) ** abs(k_new - k_old)

        theta_u = theta_new

    final_dist = mobius_distance_prime(theta_u, sigma, polarity_weight)
    return theta_u, sigma, corrs, final_dist

# ====================================================================
#  BASELINE: No Mobius (standard log-phase from exp 003)
# ====================================================================
def evolve_standard_log(numbers, steps=50, lambda_param=2.5,
                        repel_strength=0.15, lr=0.05):
    """Standard circular dynamics (no twist) on log-phase."""
    x = torch.tensor(numbers, dtype=torch.float32)
    tau = torch.log(torch.abs(x) + 1e-8)
    theta = (tau % 1.0) * 2 * math.pi
    n = len(numbers)

    def pairwise_circ(th):
        diff = torch.abs(th.unsqueeze(1) - th.unsqueeze(0))
        return torch.minimum(diff, 2 * math.pi - diff)

    corrs = []
    for step in range(steps):
        dist = pairwise_circ(theta)
        corr, _ = factor_correlation(numbers, dist)
        corrs.append(corr)

        dist_ns = dist.clone()
        dist_ns.fill_diagonal_(float('inf'))
        scores = torch.exp(-lambda_param * dist_ns)
        attn = scores / scores.sum(dim=1, keepdim=True)

        cos_part = torch.cos(theta)
        sin_part = torch.sin(theta)
        R_x = attn @ cos_part
        R_y = attn @ sin_part

        theta_attract = torch.atan2(R_y, R_x)

        # Repulsion
        repulsion = torch.zeros(n)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                d_ij = dist[i, j] + 1e-6
                strength = repel_strength / (d_ij ** 2)
                diff = theta[i] - theta[j]
                if diff > math.pi:
                    diff -= 2 * math.pi
                elif diff < -math.pi:
                    diff += 2 * math.pi
                repulsion[i] += strength * np.sign(diff)

        # Update
        delta = lr * (theta_attract - theta + repulsion)
        theta = (theta + delta) % (2 * math.pi)

    final_dist = pairwise_circ(theta)
    return theta, corrs, final_dist

# ====================================================================
#  RUN EXPERIMENTS
# ====================================================================
numbers = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
basis_primes = sieve(17)
steps = 50

print("=" * 70)
print("  EXPERIMENT 007: MOBIUS TWIST DYNAMICS")
print("=" * 70)
print()

# Baseline: standard log-phase (no twist)
print("  Running standard log-phase (baseline)...")
theta_base, corrs_base, dist_base = evolve_standard_log(numbers, steps=steps)
corr_base_final, _ = factor_correlation(numbers, dist_base)
print(f"    Correlation: {corr_base_final:.4f}")
print()

# Mobius log-phase at different polarity weights
print("  Running Mobius log-phase (polarity weight sweep)...")
mobius_log_results = {}
for pw in [0.5, 1.0, 2.0, 4.0]:
    tu, sig, corrs, fd = evolve_mobius_log(numbers, steps=steps,
                                            polarity_weight=pw)
    c, _ = factor_correlation(numbers, fd)
    mobius_log_results[pw] = {"corrs": corrs, "final_corr": c,
                               "theta": tu, "sigma": sig}
    print(f"    pw={pw:.1f}: corr={c:.4f}, sigma_flips={int((sig < 0).sum().item())}")
print()

# Mobius prime-space at different polarity weights
print("  Running Mobius prime-space (polarity weight sweep)...")
mobius_prime_results = {}
for pw in [0.5, 1.0, 2.0]:
    tu, sig, corrs, fd = evolve_mobius_prime(numbers, basis_primes,
                                              steps=steps, polarity_weight=pw)
    c, _ = factor_correlation(numbers, fd)
    n_flips = int((sig < 0).sum().item())
    mobius_prime_results[pw] = {"corrs": corrs, "final_corr": c,
                                 "theta": tu, "sigma": sig}
    print(f"    pw={pw:.1f}: corr={c:.4f}, sigma_flips={n_flips}")
print()

# Static prime-space baseline (from exp 004)
vectors_static = torch.tensor([prime_exponents(n, basis_primes) for n in numbers],
                               dtype=torch.float32)
norms = vectors_static.norm(dim=1, keepdim=True).clamp(min=1e-8)
unit_static = vectors_static / norms
sim = unit_static @ unit_static.t()
sim = torch.clamp(sim, -1 + 1e-7, 1 - 1e-7)
static_dist = torch.acos(sim)
corr_static, _ = factor_correlation(numbers, static_dist)

# ====================================================================
#  RESULTS
# ====================================================================
print("=" * 70)
print("  RESULTS")
print("=" * 70)
print()
print(f"  {'Encoding':<30} {'Corr (start)':>12} {'Corr (end)':>12} {'Status':>12}")
print("  " + "-" * 70)
print(f"  {'Static prime-space':<30} {corr_static:>12.4f} {corr_static:>12.4f} {'BASELINE':>12}")
print(f"  {'Standard log-phase':<30} {corrs_base[0]:>12.4f} {corr_base_final:>12.4f} {'no twist':>12}")
print()

for pw in [0.5, 1.0, 2.0, 4.0]:
    r = mobius_log_results[pw]
    print(f"  {'Mobius log pw='+str(pw):<30} {r['corrs'][0]:>12.4f} "
          f"{r['final_corr']:>12.4f} {'twist':>12}")

print()

for pw in [0.5, 1.0, 2.0]:
    r = mobius_prime_results[pw]
    print(f"  {'Mobius prime pw='+str(pw):<30} {r['corrs'][0]:>12.4f} "
          f"{r['final_corr']:>12.4f} {'twist':>12}")

print()

# Separation analysis for best configs
print("=" * 70)
print("  SEPARATION ANALYSIS")
print("=" * 70)
print()

for label, dist_matrix in [
    ("Standard log-phase", dist_base),
    ("Mobius log pw=2.0", mobius_distance_log(
        mobius_log_results[2.0]["theta"],
        mobius_log_results[2.0]["sigma"], 2.0)),
    ("Mobius prime pw=2.0", mobius_prime_results[2.0].get("final_dist",
        mobius_distance_prime(mobius_prime_results[2.0]["theta"],
                              mobius_prime_results[2.0]["sigma"], 2.0))),
]:
    sf_d = []
    nsf_d = []
    for i, j in combinations(range(len(numbers)), 2):
        d = dist_matrix[i, j].item()
        if shared_factor_count(numbers[i], numbers[j]) > 0:
            sf_d.append(d)
        else:
            nsf_d.append(d)
    sep = np.mean(nsf_d) - np.mean(sf_d) if sf_d and nsf_d else 0
    print(f"  {label:<30}")
    print(f"    Shared-factor dist:   {np.mean(sf_d):.3f}")
    print(f"    No-factor dist:       {np.mean(nsf_d):.3f}")
    print(f"    Separation:           {sep:.3f}")
    print()

# ====================================================================
#  VISUALIZATION
# ====================================================================

# Plot 1: Correlation over time
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(corrs_base, 'k--', label=f"Standard log ({corr_base_final:.3f})", alpha=0.5)
for pw in [0.5, 1.0, 2.0, 4.0]:
    r = mobius_log_results[pw]
    plt.plot(r["corrs"], label=f"Mobius log pw={pw} ({r['final_corr']:.3f})")
plt.axhline(y=corr_static, color='green', linestyle=':', alpha=0.5,
            label=f"Static prime ({corr_static:.3f})")
plt.xlabel("Step")
plt.ylabel("Factor Correlation")
plt.title("Log-Phase: Standard vs Mobius")
plt.legend(fontsize=7)
plt.grid(True, alpha=0.2)

plt.subplot(1, 2, 2)
for pw in [0.5, 1.0, 2.0]:
    r = mobius_prime_results[pw]
    plt.plot(r["corrs"], label=f"Mobius prime pw={pw} ({r['final_corr']:.3f})")
plt.axhline(y=corr_static, color='green', linestyle=':', alpha=0.5,
            label=f"Static prime ({corr_static:.3f})")
plt.xlabel("Step")
plt.ylabel("Factor Correlation")
plt.title("Prime-Space: Mobius Twist")
plt.legend(fontsize=7)
plt.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('experiments/007_mobius_twist/correlation_comparison.png', dpi=150)
print("  Saved: correlation_comparison.png")

# Plot 2: Sigma state visualization
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Log-phase: show final positions colored by sigma
ax = axes[0]
tu = mobius_log_results[2.0]["theta"]
sig = mobius_log_results[2.0]["sigma"]
theta_circle = tu % (2 * math.pi)
colors = ['red' if s < 0 else 'blue' for s in sig.numpy()]
for i, n in enumerate(numbers):
    x = math.cos(theta_circle[i].item())
    y = math.sin(theta_circle[i].item())
    ax.scatter(x, y, s=80, color=colors[i], zorder=5)
    ax.annotate(f"{n}({'-' if sig[i]<0 else '+'})", (x, y),
                textcoords='offset points', xytext=(6, 6), fontsize=8)
t = torch.linspace(0, 2*math.pi, 200)
ax.plot(torch.cos(t), torch.sin(t), 'k--', alpha=0.1)
ax.set_title("Mobius Log-Phase (pw=2.0)\nBlue=+1, Red=-1", fontsize=10)
ax.set_aspect('equal')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)

# Prime-space: show sigma matrix as heatmap
ax = axes[1]
sig_prime = mobius_prime_results[2.0]["sigma"]
im = ax.imshow(sig_prime.numpy(), cmap='RdBu', vmin=-1, vmax=1, aspect='auto')
ax.set_xticks(range(len(basis_primes)))
ax.set_xticklabels([str(p) for p in basis_primes], fontsize=8)
ax.set_yticks(range(len(numbers)))
ax.set_yticklabels([str(n) for n in numbers], fontsize=8)
ax.set_xlabel("Prime dimension")
ax.set_ylabel("Number")
ax.set_title("Sigma Matrix (pw=2.0)\nBlue=+1, Red=-1", fontsize=10)
plt.colorbar(im, ax=ax)

plt.tight_layout()
plt.savefig('experiments/007_mobius_twist/sigma_states.png', dpi=150)
print("  Saved: sigma_states.png")

# ====================================================================
#  SUMMARY
# ====================================================================
print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()

best_log = max(mobius_log_results.values(), key=lambda r: abs(r["final_corr"]))
best_prime = max(mobius_prime_results.values(), key=lambda r: abs(r["final_corr"]))

print(f"  Static prime-space:     {corr_static:.4f}")
print(f"  Standard log-phase:     {corr_base_final:.4f}")
print(f"  Best Mobius log:        {best_log['final_corr']:.4f}")
print(f"  Best Mobius prime:      {best_prime['final_corr']:.4f}")
print()

if abs(best_log["final_corr"]) > abs(corr_base_final) * 1.5:
    print("  RESULT: Mobius twist IMPROVES log-phase factor detection")
elif abs(best_log["final_corr"]) > abs(corr_base_final):
    print("  RESULT: Mobius twist marginally improves log-phase")
else:
    print("  RESULT: Mobius twist does NOT improve log-phase factor detection")

print()

if abs(best_prime["final_corr"]) > abs(corr_static) * 0.5:
    print("  RESULT: Mobius prime-space preserves factor structure under dynamics")
else:
    print("  RESULT: Mobius prime-space does not preserve structure")

print()
print("Done.")
