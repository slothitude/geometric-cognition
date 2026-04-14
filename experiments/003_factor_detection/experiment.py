"""
Experiment 003: Factor Detection via Geometric Dynamics
=======================================================
Tests whether shared prime factors produce phase alignment
beyond what magnitude proximity alone would predict.

Tests:
  A - Prime powers (2^n, 3^n) — do they form phase-locked chains?
  B - Factor similarity vs angular proximity correlation
  C - Random baseline (same magnitude, no shared factors)
  D - Magnitude-stripped (pure fractional log-phase, no tau)
"""

import torch
import torch.nn as nn
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations
from collections import defaultdict

# ---------- Core Modules (from 002) ----------
def encode(x):
    x = torch.tensor(x, dtype=torch.float32)
    tau = torch.log(torch.abs(x) + 1e-8)
    theta = (tau % 1.0) * 2 * math.pi
    return theta, tau

def encode_phase_only(x):
    """Magnitude-stripped encoding: only fractional log phase"""
    x = torch.tensor(x, dtype=torch.float32)
    tau = torch.log(torch.abs(x) + 1e-8)
    theta = (tau % 1.0) * 2 * math.pi
    return theta, torch.zeros_like(tau)  # zero tau removes magnitude bias

def angular_distance(a, b):
    diff = torch.abs(a - b)
    return torch.minimum(diff, 2 * math.pi - diff)

def pairwise_angular(theta):
    return angular_distance(theta.unsqueeze(1), theta.unsqueeze(0))

class GeometricField(nn.Module):
    def __init__(self, lambda_attract=2.5, repel_strength=0.15):
        super().__init__()
        self.lambda_attract = lambda_attract
        self.repel_strength = repel_strength

    def forward(self, theta, tau):
        n = theta.shape[0]
        d_theta = pairwise_angular(theta)
        d_tau = torch.abs(tau.unsqueeze(1) - tau.unsqueeze(0))
        dist = d_theta + 0.3 * d_tau
        dist_no_self = dist.clone()
        dist_no_self.fill_diagonal_(float('inf'))
        scores = torch.exp(-self.lambda_attract * dist_no_self)
        attn = scores / scores.sum(dim=1, keepdim=True)

        cos_part = torch.cos(theta)
        sin_part = torch.sin(theta)
        R_x = attn @ cos_part
        R_y = attn @ sin_part

        epsilon = 0.1
        repel_force_x = torch.zeros(n)
        repel_force_y = torch.zeros(n)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                d = d_theta[i, j] + epsilon
                strength = self.repel_strength / (d * d)
                dx = torch.cos(theta[i]) - torch.cos(theta[j])
                dy = torch.sin(theta[i]) - torch.sin(theta[j])
                norm = torch.sqrt(dx*dx + dy*dy) + 1e-8
                repel_force_x[i] += strength * dx / norm
                repel_force_y[i] += strength * dy / norm

        force_x = R_x + repel_force_x
        force_y = R_y + repel_force_y
        theta_out = torch.atan2(force_y, force_x)
        tau_out = attn @ tau
        return theta_out, tau_out, attn

def run_dynamics(numbers, steps=50, phase_only=False, lambda_attract=2.5, repel_strength=0.15):
    if phase_only:
        theta, tau = encode_phase_only(numbers)
    else:
        theta, tau = encode(numbers)
    model = GeometricField(lambda_attract, repel_strength)
    for _ in range(steps):
        theta, tau, _ = model(theta, tau)
    return theta, tau

def prime_factors(n):
    """Return set of prime factors"""
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors

def shared_factor_count(a, b):
    return len(prime_factors(a) & prime_factors(b))

# ====================================================================
#  TEST A: Prime Power Chains
# ====================================================================
print("=" * 70)
print("  TEST A: Prime Power Chains")
print("=" * 70)
print()

powers_of_2 = [2, 4, 8, 16, 32, 64]
powers_of_3 = [3, 9, 27, 81]
mixed = [2, 3, 4, 6, 8, 9, 12, 16, 24, 27, 32, 48, 64, 81]

for label, nums in [("2^n", powers_of_2), ("3^n", powers_of_3), ("mixed", mixed)]:
    theta_final, _ = run_dynamics(nums, steps=50, phase_only=True, repel_strength=0.10)
    print(f"  {label}: {nums}")
    print(f"  Final angles (deg):", end="")
    for i, n in enumerate(nums):
        print(f"  {n}:{math.degrees(theta_final[i].item()):.1f}", end="")
    print()

    # Check pairwise alignment within the group
    d = pairwise_angular(theta_final)
    n = len(nums)
    mask = ~torch.eye(n, dtype=torch.bool)
    mean_d = d[mask].mean().item()
    print(f"  Mean pairwise distance: {math.degrees(mean_d):.1f} deg")
    print()

# ====================================================================
#  TEST B: Factor Similarity vs Angular Proximity
# ====================================================================
print("=" * 70)
print("  TEST B: Factor Similarity vs Final Angular Distance")
print("=" * 70)
print()

test_numbers = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
theta_final, _ = run_dynamics(test_numbers, steps=50, phase_only=True, repel_strength=0.15)
d_final = pairwise_angular(theta_final)

# Collect pairwise stats
pairs = []
for i, j in combinations(range(len(test_numbers)), 2):
    a, b = test_numbers[i], test_numbers[j]
    sf = shared_factor_count(a, b)
    ang_d = math.degrees(d_final[i, j].item())
    pairs.append((a, b, sf, ang_d))

# Group by shared factor count
by_sf = defaultdict(list)
for a, b, sf, d in pairs:
    by_sf[sf].append(d)

print(f"  {'Shared Factors':>15} {'Mean Dist (deg)':>16} {'N pairs':>8} {'Examples':>30}")
print("  " + "-" * 75)
for sf in sorted(by_sf.keys(), reverse=True):
    dists = by_sf[sf]
    examples = [(a, b) for a, b, s, _ in pairs if s == sf][:3]
    ex_str = ", ".join(f"{a}-{b}" for a, b in examples)
    print(f"  {sf:>15} {np.mean(dists):>16.1f} {len(dists):>8} {ex_str:>30}")

print()

# Correlation
sf_scores = [sf for _, _, sf, _ in pairs]
ang_dists = [d for _, _, _, d in pairs]
corr = np.corrcoef(sf_scores, ang_dists)[0, 1]
print(f"  Pearson correlation (shared factors vs angular distance): {corr:.4f}")
print(f"  (Negative = more shared factors -> closer in angle)")
print()

# ====================================================================
#  TEST C: Random Baseline
# ====================================================================
print("=" * 70)
print("  TEST C: Random Baseline (factor-correlation control)")
print("=" * 70)
print()

# Generate random numbers with similar magnitude distribution
np.random.seed(42)
# Use primes > 17 (no shared factors with the test set, similar range)
random_numbers = [19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73]
theta_rand, _ = run_dynamics(random_numbers, steps=50, phase_only=True, repel_strength=0.15)
d_rand = pairwise_angular(theta_rand)

pairs_rand = []
for i, j in combinations(range(len(random_numbers)), 2):
    a, b = random_numbers[i], random_numbers[j]
    sf = shared_factor_count(a, b)
    ang_d = math.degrees(d_rand[i, j].item())
    pairs_rand.append((a, b, sf, ang_d))

# All random primes share 0 factors — check mean distance
rand_dists = [d for _, _, _, d in pairs_rand]
sf_rand = [sf for _, _, sf, _ in pairs_rand]
corr_rand = np.corrcoef(sf_rand, rand_dists)[0, 1]

print(f"  Random primes (no shared factors): {random_numbers}")
print(f"  Mean pairwise distance: {np.mean(rand_dists):.1f} deg")
print(f"  Std pairwise distance: {np.std(rand_dists):.1f} deg")
print(f"  Correlation (should be ~0 since all sf=0): {corr_rand:.4f}")
print()

# Compare: test set vs random
test_dists = [d for _, _, _, d in pairs]
print(f"  Test set mean distance: {np.mean(test_dists):.1f} deg")
print(f"  Test set std distance: {np.std(test_dists):.1f} deg")
print()
print(f"  Test set (with shared factors) std: {np.std(test_dists):.1f}")
print(f"  Random primes (no shared factors) std: {np.std(rand_dists):.1f}")
print(f"  If test set has LOWER std -> structure is emerging")
print()

# ====================================================================
#  TEST D: Magnitude-stripped vs Full encoding
# ====================================================================
print("=" * 70)
print("  TEST D: Phase-Only vs Full Encoding")
print("=" * 70)
print()

theta_full, _ = run_dynamics(test_numbers, steps=50, phase_only=False, repel_strength=0.15)
theta_phase, _ = run_dynamics(test_numbers, steps=50, phase_only=True, repel_strength=0.15)

d_full = pairwise_angular(theta_full)
d_phase = pairwise_angular(theta_phase)

pairs_full = []
pairs_phase = []
for i, j in combinations(range(len(test_numbers)), 2):
    a, b = test_numbers[i], test_numbers[j]
    sf = shared_factor_count(a, b)
    pairs_full.append((sf, math.degrees(d_full[i, j].item())))
    pairs_phase.append((sf, math.degrees(d_phase[i, j].item())))

corr_full = np.corrcoef([sf for sf, _ in pairs_full], [d for _, d in pairs_full])[0, 1]
corr_phase = np.corrcoef([sf for sf, _ in pairs_phase], [d for _, d in pairs_phase])[0, 1]

print(f"  Full encoding correlation:   {corr_full:.4f}")
print(f"  Phase-only correlation:      {corr_phase:.4f}")
print(f"  (More negative = stronger factor detection)")
print()

# ====================================================================
#  VISUALIZATION
# ====================================================================

# Plot 1: Prime power chains
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
t = torch.linspace(0, 2 * math.pi, 200)

for ax, (label, nums) in zip(axes, [("2^n", powers_of_2), ("3^n", powers_of_3), ("mixed", mixed)]):
    theta_f, _ = run_dynamics(nums, steps=50, phase_only=True, repel_strength=0.10)
    ax.plot(torch.cos(t), torch.sin(t), 'k--', alpha=0.1)
    colors = plt.cm.Set1(np.linspace(0, 1, len(nums)))
    for i, n in enumerate(nums):
        x = torch.cos(theta_f[i]).item()
        y = torch.sin(theta_f[i]).item()
        ax.scatter(x, y, s=80, color=colors[i], zorder=5)
        ax.annotate(str(n), (x, y), textcoords='offset points', xytext=(6, 6), fontsize=9)
    ax.set_title(f"Prime Powers: {label}", fontsize=12)
    ax.set_aspect('equal')
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)

plt.suptitle("Test A: Do prime powers form phase-locked chains?", fontsize=14)
plt.tight_layout()
plt.savefig('experiments/003_factor_detection/prime_powers.png', dpi=150)
print("  Saved: prime_powers.png")

# Plot 2: Factor similarity scatter
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

sf_vals = [sf for _, _, sf, _ in pairs]
dist_vals = [d for _, _, _, d in pairs]

ax = axes[0]
ax.scatter(sf_vals, dist_vals, alpha=0.5, s=20)
# Add jitter for visibility
ax.set_xlabel("Shared Prime Factors")
ax.set_ylabel("Final Angular Distance (deg)")
ax.set_title(f"Test Set (corr={corr:.3f})")
ax.grid(True, alpha=0.2)

sf_r = [sf for _, _, sf, _ in pairs_rand]
dist_r = [d for _, _, _, d in pairs_rand]

ax = axes[1]
ax.scatter(sf_r, dist_r, alpha=0.5, s=20, color='orange')
ax.set_xlabel("Shared Prime Factors (all 0 for primes)")
ax.set_ylabel("Final Angular Distance (deg)")
ax.set_title(f"Random Primes Control (corr={corr_rand:.3f})")
ax.grid(True, alpha=0.2)

plt.suptitle("Test B+C: Shared Factors vs Angular Distance", fontsize=14)
plt.tight_layout()
plt.savefig('experiments/003_factor_detection/factor_correlation.png', dpi=150)
print("  Saved: factor_correlation.png")

# Plot 3: Full vs Phase-only comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, (theta_f, title, corr_val) in zip(axes, [
    (theta_full, f"Full Encoding (corr={corr_full:.3f})", corr_full),
    (theta_phase, f"Phase-Only (corr={corr_phase:.3f})", corr_phase),
]):
    ax.plot(torch.cos(t), torch.sin(t), 'k--', alpha=0.1)
    # Color by number of prime factors
    for i, n in enumerate(test_numbers):
        nf = len(prime_factors(n))
        x = torch.cos(theta_f[i]).item()
        y = torch.sin(theta_f[i]).item()
        color = ['red', 'blue', 'green', 'purple'][min(nf-1, 3)]
        ax.scatter(x, y, s=80, color=color, zorder=5)
        ax.annotate(str(n), (x, y), textcoords='offset points', xytext=(6, 6), fontsize=9)
    ax.set_title(title, fontsize=11)
    ax.set_aspect('equal')
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)

# Legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='red', label='1 factor (prime)'),
    Patch(facecolor='blue', label='2 factors'),
    Patch(facecolor='green', label='3 factors'),
    Patch(facecolor='purple', label='4+ factors'),
]
axes[1].legend(handles=legend_elements, loc='lower right', fontsize=8)

plt.suptitle("Test D: Full vs Phase-Only Encoding", fontsize=14)
plt.tight_layout()
plt.savefig('experiments/003_factor_detection/encoding_comparison.png', dpi=150)
print("  Saved: encoding_comparison.png")

print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print(f"  Factor detection correlation:  {corr:.4f}")
print(f"  Random baseline correlation:   {corr_rand:.4f}")
print(f"  Full encoding correlation:     {corr_full:.4f}")
print(f"  Phase-only correlation:        {corr_phase:.4f}")
print()
if abs(corr) > 0.15:
    print("  SIGNAL DETECTED: Shared factors correlate with angular proximity")
else:
    print("  WEAK SIGNAL: Factor correlation is marginal")
    print("  Structure is mostly driven by log-phase proximity")
print()
print("Done.")
