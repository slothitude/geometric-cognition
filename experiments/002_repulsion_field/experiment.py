import torch
import torch.nn as nn
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---------- Encoding ----------
def encode(x):
    x = torch.tensor(x, dtype=torch.float32)
    tau = torch.log(torch.abs(x) + 1e-8)
    theta = (tau % 1.0) * 2 * math.pi
    return theta, tau

# ---------- Distances ----------
def angular_distance(a, b):
    diff = torch.abs(a - b)
    return torch.minimum(diff, 2 * math.pi - diff)

def pairwise_angular(theta):
    return angular_distance(theta.unsqueeze(1), theta.unsqueeze(0))

def pairwise_tau(tau):
    return torch.abs(tau.unsqueeze(1) - tau.unsqueeze(0))

# ---------- Energy Functions ----------
def attraction_energy(theta, tau, gamma=0.3):
    d_theta = pairwise_angular(theta)
    d_tau = pairwise_tau(tau)
    return (d_theta + gamma * d_tau).sum()

def repulsion_energy(theta, alpha=1.0, epsilon=0.1):
    d_theta = pairwise_angular(theta)
    # Repulsion: inversely proportional to distance, stronger when close
    repel = alpha / (d_theta + epsilon)
    # Remove self-pairs
    n = theta.shape[0]
    mask = ~torch.eye(n, dtype=torch.bool)
    return repel[mask].sum()

def total_energy(theta, tau, attract_weight=1.0, repel_weight=0.5, gamma=0.3, epsilon=0.1):
    return attract_weight * attraction_energy(theta, tau, gamma) \
         - repel_weight * repulsion_energy(theta, repel_weight, epsilon)

# ---------- Geometric Attention with Repulsion ----------
class GeometricField(nn.Module):
    def __init__(self, lambda_attract=2.5, repel_strength=0.15, friction=0.0):
        super().__init__()
        self.lambda_attract = lambda_attract
        self.repel_strength = repel_strength
        self.friction = friction

    def forward(self, theta, tau):
        n = theta.shape[0]
        d_theta = pairwise_angular(theta)
        d_tau = pairwise_tau(tau)

        # --- Attraction (attention) ---
        dist = d_theta + 0.3 * d_tau
        dist_no_self = dist.clone()
        dist_no_self.fill_diagonal_(float('inf'))
        scores = torch.exp(-self.lambda_attract * dist_no_self)
        attn = scores / scores.sum(dim=1, keepdim=True)

        # Attraction force: move toward attention-weighted center
        cos_part = torch.cos(theta)
        sin_part = torch.sin(theta)
        R_x = attn @ cos_part
        R_y = attn @ sin_part
        theta_attract = torch.atan2(R_y, R_x)

        # --- Repulsion force ---
        # Push away from neighbors that are too close
        epsilon = 0.1
        repel_force_x = torch.zeros(n)
        repel_force_y = torch.zeros(n)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                d = d_theta[i, j] + epsilon
                # Repulsion direction: away from j, strength inversely proportional to d^2
                strength = self.repel_strength / (d * d)
                dx = torch.cos(theta[i]) - torch.cos(theta[j])
                dy = torch.sin(theta[i]) - torch.sin(theta[j])
                norm = torch.sqrt(dx*dx + dy*dy) + 1e-8
                repel_force_x[i] += strength * dx / norm
                repel_force_y[i] += strength * dy / norm

        # Combined force
        force_x = R_x + repel_force_x
        force_y = R_y + repel_force_y
        theta_out = torch.atan2(force_y, force_x)

        # Tau follows attention only (repulsion is angular)
        tau_out = attn @ tau

        return theta_out, tau_out, attn

# ---------- Run Experiment ----------
def run_experiment(numbers, lambda_attract, repel_strength, friction, steps, label):
    theta, tau = encode(numbers)
    model = GeometricField(lambda_attract, repel_strength, friction)

    theta_history = [theta.clone()]
    tau_history = [tau.clone()]

    attract_e = [attraction_energy(theta, tau).item()]
    repel_e = [repulsion_energy(theta, alpha=repel_strength).item()]
    total_e = [attract_e[-1] - repel_e[-1]]

    for step in range(steps):
        theta, tau, _ = model(theta, tau)
        theta_history.append(theta.clone())
        tau_history.append(tau.clone())
        attract_e.append(attraction_energy(theta, tau).item())
        repel_e.append(repulsion_energy(theta, alpha=repel_strength).item())
        total_e.append(attract_e[-1] - repel_e[-1])

    return theta_history, tau_history, attract_e, repel_e, total_e

# ---------- Data ----------
numbers = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

# ---------- Parameter Sweep ----------
configs = [
    {"lambda_attract": 2.5, "repel_strength": 0.0,  "friction": 0.0, "label": "Pure Attraction (baseline)"},
    {"lambda_attract": 2.5, "repel_strength": 0.05, "friction": 0.0, "label": "Weak Repulsion"},
    {"lambda_attract": 2.5, "repel_strength": 0.15, "friction": 0.0, "label": "Medium Repulsion"},
    {"lambda_attract": 2.5, "repel_strength": 0.40, "friction": 0.0, "label": "Strong Repulsion"},
]

steps = 50

print("=" * 70)
print("  REPULSION FIELD EXPERIMENT")
print("=" * 70)
print()

results = []
for cfg in configs:
    r = run_experiment(numbers, cfg["lambda_attract"], cfg["repel_strength"],
                       cfg["friction"], steps, cfg["label"])
    results.append((cfg, r))
    theta_h = r[0]
    attract_e = r[2]
    repel_e = r[3]
    total_e = r[4]

    # Check unique final positions
    final_theta = theta_h[-1]
    rounded = torch.round(final_theta * 100) / 100
    unique = len(torch.unique(rounded))

    # Spread (mean pairwise angular distance)
    final_dist = pairwise_angular(final_theta)
    n = final_theta.shape[0]
    mask = ~torch.eye(n, dtype=torch.bool)
    spread = final_dist[mask].mean().item()

    print(f"  {cfg['label']}")
    print(f"    Attract E: {attract_e[0]:.1f} -> {attract_e[-1]:.1f}  ({(attract_e[-1]-attract_e[0])/attract_e[0]*100:+.1f}%)")
    print(f"    Repel E:   {repel_e[0]:.2f} -> {repel_e[-1]:.2f}")
    print(f"    Unique positions: {unique}/{n}")
    print(f"    Mean spread: {math.degrees(spread):.1f} deg")
    print()

# ---------- Visualization ----------
fig, axes = plt.subplots(2, 2, figsize=(14, 14))

t = torch.linspace(0, 2 * math.pi, 200)
colors = plt.cm.tab20(np.linspace(0, 1, len(numbers)))

for ax, (cfg, r) in zip(axes.flat, results):
    theta_h, tau_h, attract_e, repel_e, total_e = r

    # Plot trajectories on unit circle
    ax.plot(torch.cos(t), torch.sin(t), 'k--', alpha=0.1)

    for i, n in enumerate(numbers):
        thetas = torch.stack([th[i] for th in theta_h])
        xs = torch.cos(thetas).numpy()
        ys = torch.sin(thetas).numpy()
        ax.plot(xs, ys, '-', color=colors[i], alpha=0.4, linewidth=1)
        ax.scatter(xs[0], ys[0], color=colors[i], s=50, zorder=5, marker='o')
        ax.scatter(xs[-1], ys[-1], color=colors[i], s=50, zorder=5, marker='x')

    ax.set_title(cfg['label'], fontsize=10)
    ax.set_aspect('equal')
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)

plt.suptitle("Repulsion Field Sweep (o=start, x=end)", fontsize=14)
plt.tight_layout()
plt.savefig('experiments/002_repulsion_field/trajectories_sweep.png', dpi=150)
print("  Saved: trajectories_sweep.png")

# ---------- Energy Curves ----------
fig, axes = plt.subplots(2, 2, figsize=(14, 8))

for ax, (cfg, r) in zip(axes.flat, results):
    theta_h, tau_h, attract_e, repel_e, total_e = r
    ax.plot(attract_e, label='Attraction', color='blue')
    ax.plot(total_e, label='Total (attract - repel)', color='green')
    ax.set_title(cfg['label'], fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.2)

plt.suptitle("Energy Curves", fontsize=14)
plt.tight_layout()
plt.savefig('experiments/002_repulsion_field/energy_curves.png', dpi=150)
print("  Saved: energy_curves.png")

# ---------- Detailed Analysis: Best Config ----------
# Pick the medium repulsion config for deep analysis
cfg, r = results[2]  # Medium Repulsion
theta_h = r[0]
final_theta = theta_h[-1]

# Cluster analysis
print()
print("=" * 70)
print("  CLUSTER ANALYSIS (Medium Repulsion)")
print("=" * 70)
print()

# Group by angular proximity
d = pairwise_angular(final_theta)
threshold = math.radians(20)  # 20 degree threshold

visited = set()
clusters = []
for i in range(len(numbers)):
    if i in visited:
        continue
    cluster = [i]
    visited.add(i)
    for j in range(i+1, len(numbers)):
        if j not in visited and d[i, j] < threshold:
            cluster.append(j)
            visited.add(j)
    clusters.append(cluster)

for ci, cluster in enumerate(clusters):
    members = [numbers[i] for i in cluster]
    primes = [n for n in members if n in [5, 7, 11, 13, 17]]
    composites = [n for n in members if n not in primes]
    angles = [math.degrees(final_theta[i].item()) for i in cluster]
    print(f"  Cluster {ci+1}: {members}")
    print(f"    Angles: [{', '.join(f'{a:.1f}' for a in angles)}]")
    print(f"    Primes: {primes}, Composites: {composites}")
    print()

# ---------- Phase Locking Detection ----------
print("=" * 70)
print("  PHASE LOCKING ANALYSIS")
print("=" * 70)
print()

theta_h = r[0]
# Check if any pairs synchronize over time
n = len(numbers)
lock_pairs = []
for i in range(n):
    for j in range(i+1, n):
        d_start = angular_distance(theta_h[0][i:i+1], theta_h[0][j:j+1]).item()
        d_end = angular_distance(theta_h[-1][i:i+1], theta_h[-1][j:j+1]).item()
        if d_start > math.radians(10) and d_end < math.radians(5):
            lock_pairs.append((numbers[i], numbers[j], math.degrees(d_start), math.degrees(d_end)))

if lock_pairs:
    print("  Phase-locked pairs (started >10 deg apart, ended <5 deg):")
    for a, b, ds, de in lock_pairs:
        print(f"    {a} <-> {b}: {ds:.1f} -> {de:.1f} deg")
else:
    print("  No phase locking detected")

print()
print("Done.")
