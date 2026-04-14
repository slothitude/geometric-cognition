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

# ---------- Distance ----------
def angular_distance(a, b):
    diff = torch.abs(a - b)
    return torch.minimum(diff, 2 * math.pi - diff)

def wheel_distance(theta, tau):
    d_theta = angular_distance(theta.unsqueeze(1), theta.unsqueeze(0))
    d_tau = torch.abs(tau.unsqueeze(1) - tau.unsqueeze(0))
    return d_theta + 0.3 * d_tau

# ---------- Energy ----------
def compute_energy(theta, tau):
    dist = wheel_distance(theta, tau)
    return dist.sum().item()

# ---------- Geometric Attention (no self-attention) ----------
class GeometricAttention(nn.Module):
    def __init__(self, lambda_param=2.0):
        super().__init__()
        self.lambda_param = lambda_param

    def forward(self, theta, tau):
        dist = wheel_distance(theta, tau)
        # Remove self-attention
        dist.fill_diagonal_(float('inf'))
        scores = torch.exp(-self.lambda_param * dist)
        attn = scores / scores.sum(dim=1, keepdim=True)
        cos_part = torch.cos(theta)
        sin_part = torch.sin(theta)
        R_x = attn @ cos_part
        R_y = attn @ sin_part
        theta_out = torch.atan2(R_y, R_x)
        tau_out = attn @ tau
        return theta_out, tau_out, attn

# ---------- Data ----------
numbers = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
theta, tau = encode(numbers)

# ---------- Model ----------
model = GeometricAttention(lambda_param=2.5)

# ---------- Simulation ----------
steps = 25
theta_history = [theta.clone()]
tau_history = [tau.clone()]
energy_history = [compute_energy(theta, tau)]

for step in range(steps):
    theta_new, tau_new, _ = model(theta, tau)
    theta = theta_new
    tau = tau_new
    theta_history.append(theta.clone())
    tau_history.append(tau.clone())
    energy_history.append(compute_energy(theta, tau))

# ---------- Results ----------
print("=" * 60)
print("  GEOMETRIC ENERGY DYNAMICS EXPERIMENT")
print("=" * 60)
print()
print(f"  Input numbers: {numbers}")
print(f"  Steps: {steps}")
print(f"  lambda: {model.lambda_param}")
print(f"  Self-attention: DISABLED")
print()

# Energy analysis
e_start = energy_history[0]
e_end = energy_history[-1]
e_min = min(energy_history)
e_min_step = energy_history.index(e_min)
delta = e_end - e_start

print(f"  Energy start:  {e_start:.4f}")
print(f"  Energy end:    {e_end:.4f}")
print(f"  Energy min:    {e_min:.4f} (step {e_min_step})")
print(f"  Delta:         {delta:+.4f} ({delta/e_start*100:+.2f}%)")
print()

# Check convergence
diffs = [abs(energy_history[i+1] - energy_history[i]) for i in range(len(energy_history)-1)]
print(f"  Max step delta:  {max(diffs):.6f}")
print(f"  Final step delta: {diffs[-1]:.6f}")
print()

if e_end < e_start:
    print("  RESULT: Energy DECREASED - system is minimizing energy")
elif e_end > e_start:
    print("  RESULT: Energy INCREASED - system is diverging")
else:
    print("  RESULT: Energy UNCHANGED")

if diffs[-1] < 0.01:
    print("  STATUS: CONVERGED (final delta < 0.01)")
elif diffs[-1] < diffs[0] * 0.1:
    print("  STATUS: CONVERGING (delta shrinking)")
else:
    print("  STATUS: Still evolving")

print()

# Track individual points
print("  Point movement (theta, degrees):")
print(f"  {'Num':>4} {'Step 0':>10} {'Step 25':>10} {'Delta':>10}")
print("  " + "-" * 38)
for i, n in enumerate(numbers):
    t0 = theta_history[0][i].item()
    tf = theta_history[-1][i].item()
    d = angular_distance(
        theta_history[0][i:i+1], theta_history[-1][i:i+1]
    ).item()
    print(f"  {n:>4} {math.degrees(t0):>10.2f} {math.degrees(tf):>10.2f} {math.degrees(d):>10.2f}")

print()

# ---------- Plot 1: Energy ----------
plt.figure(figsize=(8, 4))
plt.plot(energy_history, 'b-o', markersize=4)
plt.title("Energy Over Time", fontsize=14)
plt.xlabel("Step")
plt.ylabel("Total Energy")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('experiments/001_energy_dynamics/energy.png', dpi=150)
print("  Saved: energy.png")

# ---------- Plot 2: Evolution ----------
fig, axes = plt.subplots(1, 4, figsize=(16, 4))
snapshot_steps = [0, 5, 10, 24]
t = torch.linspace(0, 2 * math.pi, 200)

for ax, step in zip(axes, snapshot_steps):
    th = theta_history[step]
    x = torch.cos(th)
    y = torch.sin(th)
    ax.scatter(x, y, s=60, zorder=5)
    ax.plot(torch.cos(t), torch.sin(t), 'k--', alpha=0.15)
    for i, n in enumerate(numbers):
        ax.annotate(str(n), (x[i], y[i]), textcoords='offset points',
                    xytext=(5, 5), fontsize=7)
    ax.set_title(f"Step {step}", fontsize=11)
    ax.set_aspect('equal')
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)

plt.suptitle("Geometric Evolution Over Time", fontsize=14)
plt.tight_layout()
plt.savefig('experiments/001_energy_dynamics/evolution.png', dpi=150)
print("  Saved: evolution.png")

# ---------- Plot 3: Full trajectory ----------
plt.figure(figsize=(8, 8))
t = torch.linspace(0, 2 * math.pi, 200)
plt.plot(torch.cos(t), torch.sin(t), 'k--', alpha=0.1)

colors = plt.cm.viridis(np.linspace(0, 1, len(numbers)))
for i, n in enumerate(numbers):
    thetas = torch.stack([th[i] for th in theta_history])
    xs = torch.cos(thetas).numpy()
    ys = torch.sin(thetas).numpy()
    plt.plot(xs, ys, '-', color=colors[i], alpha=0.5, linewidth=1.5)
    plt.scatter(xs[0], ys[0], color=colors[i], s=80, zorder=5, marker='o')
    plt.scatter(xs[-1], ys[-1], color=colors[i], s=80, zorder=5, marker='x')
    plt.annotate(str(n), (xs[0], ys[0]), textcoords='offset points',
                 xytext=(6, 6), fontsize=8, color=colors[i])

plt.title("Full Trajectories (o=start, x=end)", fontsize=14)
plt.gca().set_aspect('equal')
plt.tight_layout()
plt.savefig('experiments/001_energy_dynamics/trajectories.png', dpi=150)
print("  Saved: trajectories.png")
print()
print("Done.")
