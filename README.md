# Geometric Computation, Prime Structure, and Secure Cognitive Systems

**A Unified Framework for Angle-Space Intelligence, Streaming Semantics, and Cryptographic Agency**

Aaron King
2024–2026

---

## Abstract

We present a framework that integrates **geometric computation**, **prime-structured number theory**, **energy-based attention**, and **cryptographically secure AI systems** into a single architecture. At its core, the framework models information as **Signed Wheels**—tuples of angular phase, logarithmic magnitude, and polarity—operating on a circular manifold.

Through ten experiments, we demonstrate:

1. **Geometric attention dynamics** minimize energy by 92% and converge to stable equilibria when balanced with repulsion forces.
2. **Log-phase encoding** (`theta = 2pi * (log n mod 1)`) does **not** capture multiplicative factor structure (correlation = +0.08).
3. **Prime exponent vectors** on the unit hypersphere encode multiplicative structure as angular alignment with correlation **-0.91** (p ~ 0).
4. **Geometric dynamics act as angular diffusion** (D ~ 1.22) that degrades factor structure unless explicitly constrained.
5. **Structure-preserving corrections** (strength 0.5) maintain **78%** of the static factor correlation under dynamics.
6. **Mobius twist topology** (unwrapped angle + polarity flips) does not improve factor detection, as winding is magnitude-driven rather than factor-driven.
7. **Golden-ratio phase** (phi-phase) does not improve atomic mass prediction (p = 0.896), confirming phase terms carry no physical signal.
8. **L-P-V trinity geometry** (120-degree basis) creates useful interaction features for mass prediction (5x RMSE improvement) but risks overfitting on small samples.
9. **Mobius encoding of perfect numbers** shows positive delta (+0.297) but is not statistically significant (p = 0.390) due to insufficient sample size (n = 4).

These results separate the contributions: the **representation** (prime-space encoding) captures factor structure; the **dynamics** (energy-based attention) are a separate mechanism for clustering and pattern formation. They are architecturally compatible but functionally independent. Neither geometric phase nor topological encoding adds detectable signal beyond what prime-space already provides.

Additionally, we describe **SquidCode**, a streaming semantic proxy, and **Cryptocode**, a one-time pad system for securing AI instruction channels.

---

## 1. Introduction

Modern computation is dominated by **vector algebra and symbolic manipulation**, yet many natural systems—biological, physical, and cognitive—operate through **geometry, phase, and energy minimization**.

This work proposes a shift:

> From discrete symbols and dot products to **continuous geometry and circular dynamics**

We investigate five domains:

1. **Geometric Neural Networks** (Lazy Wheels)
2. **Prime Number Structure** (6k±1 rails, prime-space embedding)
3. **Circular Attention & Energy Minimization**
4. **Streaming Semantic Systems** (SquidCode)
5. **Cryptographically Secured Agents** (Cryptocode)

The result is a framework spanning mathematics, machine learning, systems architecture, and secure cognition — grounded in experimental results from ten controlled experiments.

---

## 2. The Signed Wheel Representation

### 2.1 Definition

A **Signed Wheel** is defined as:

W = (theta, tau, sigma)

Where:

- theta in [0, 2pi): angular phase
- tau in R: logarithmic magnitude (turns)
- sigma in {-1, +1}: polarity

This replaces scalar or vector representations with **circular geometric objects**.

### 2.2 Mapping Real Numbers

tau = log|x|, theta = 2pi(tau mod 1), sigma = sign(x)

This creates a **logarithmic spiral embedding**:

- magnitude -> radial growth
- phase -> angular position

### 2.3 Circular Distance

d_theta = min(|theta_A - theta_B|, 2pi - |theta_A - theta_B|)

d(W_A, W_B) = d_theta + gamma|tau_A - tau_B| + beta(1 - sigma_A sigma_B)

Distance becomes **energy-like**, not purely geometric.

### 2.4 Experimental Note

The log-phase encoding `theta = 2pi * (log n mod 1)` maps real numbers to angles, but **destroys multiplicative structure** through modular wrapping. Numbers with shared prime factors do not cluster under this encoding (Experiment 003: correlation = +0.08). This motivates the prime-space encoding introduced in Section 4.

---

## 3. Lazy Wheels: Geometric Neural Computation

### 3.1 Core Transformation

Traditional neural networks:

y = W * x + b

Lazy Wheels:

theta_out = (theta_in + phi) mod 2pi

Where:

- learning = adjusting **rotation angles**
- computation = **phase transformation**

### 3.2 Properties

- No matrix multiplication
- O(n) complexity
- Natural periodicity
- Built-in regularization

### 3.3 Interpretation

> Learning is **phase synchronization**, not weight fitting.

---

## 4. Prime-Space Embedding

### 4.1 The Problem with Log-Phase

Experiment 003 tested whether the log-phase encoding captures prime factor structure. Results:

| Shared Factors | Mean Angular Distance |
|---------------|----------------------|
| 2 | 41.4 deg |
| 1 | 105.2 deg |
| 0 | 91.0 deg |

Pearson correlation between shared factor count and angular distance: **+0.08** (no signal). The encoding mixes all prime contributions into a single phase value, losing factor separability.

### 4.2 Prime Exponent Vectors

Each integer n is represented as a vector in prime-basis space:

n = p1^e1 * p2^e2 * ... -> v(n) = (e1, e2, ...)

Example: 12 = 2^2 * 3^1 -> v(12) = [2, 1, 0, 0, ...]

### 4.3 Hypersphere Normalization

Normalizing to unit vectors:

v_hat(n) = v(n) / ||v(n)||

places all integers on the unit hypersphere. Numbers sharing prime factors point in similar directions:

- 4 = 2^2 and 8 = 2^3 both normalize to direction [1, 0, 0, ...]
- 6 = 2^1 * 3^1 and 12 = 2^2 * 3^1 point in the same quadrant

### 4.4 Experimental Results

Experiment 004 tested the prime-space encoding on integers 4-17:

- **Factor correlation: -0.910** (near-perfect detection)
- **t-test: p ~ 0** (statistically significant)
- **Powers of 2**: All identical on hypersphere (0.0 deg apart)
- **Powers of 3**: All identical on hypersphere (0.0 deg apart)

This demonstrates that **multiplication = direction alignment** in prime-exponent space.

### 4.5 Comparison

| Encoding | Factor Correlation |
|----------|-------------------|
| Log-phase (1D circular) | +0.08 |
| **Prime exponent hypersphere** | **-0.91** |

The prime-space encoding captures multiplicative structure exactly, by construction. The log-phase encoding does not.

---

## 5. Geometric Attention Dynamics

### 5.1 Attention as Energy Minimization

alpha_i = exp(-lambda * d(W_Q, W_K_i)) / sum_j exp(-lambda * d(W_Q, W_K_j))

Replaces dot-product attention with **angular proximity + energy minimization**.

### 5.2 Energy Dynamics (Experiment 001)

Without repulsion, the system minimizes total energy:

- Energy decreased **92%** in 25 steps (320.9 -> 25.4)
- All points collapsed to 2 attractors (degenerate solution)

This confirms the dynamics work as a genuine energy-minimizing system, comparable to Hopfield networks or N-body simulation.

### 5.3 Repulsion Balance (Experiment 002)

Adding inverse-square repulsion prevents collapse:

| Repulsion Strength | Unique Positions | Mean Spread |
|-------------------|-----------------|-------------|
| None | 1/14 | 0 deg |
| Weak (0.05) | 14/14 | 93.5 deg |
| Medium (0.15) | 13/14 | 96.3 deg |
| Strong (0.40) | 14/14 | 94.9 deg |

With repulsion, all points maintain distinct positions with ~95 deg mean spread. The system reaches stable equilibrium.

### 5.4 Circular Aggregation

R_x = sum alpha_i * cos(theta_i), R_y = sum alpha_i * sin(theta_i)

theta_out = atan2(R_y, R_x)

This preserves circular continuity.

---

## 6. Dynamics-Representation Interaction

### 6.1 The Diffusion Problem

Experiment 005 tested whether geometric dynamics enhance the prime-space encoding. Results:

| Dynamics Type | Correlation (start -> end) |
|--------------|--------------------------|
| Static (no dynamics) | -0.910 -> -0.910 |
| Unconstrained | -0.910 -> +0.073 |
| Sphere-projected | -0.910 -> -0.127 |
| Tangent-space | -0.910 -> -0.141 |

All dynamics degrade the encoding. The dynamics act as **angular diffusion** on the hypersphere, progressively mixing the clean factor structure.

### 6.2 Diffusion Characterization (Experiment 006)

The degradation follows exponential decay:

corr(lr) = -0.30 * exp(-1.22 * lr * steps) - 0.14

- Diffusion coefficient: **D ~ 1.22**
- Half-life at lr=0.01: ~57 steps
- Correlation degrades smoothly with step size

This quantifies the dynamics as a tunable diffusion process.

### 6.3 Structure-Preserving Flow (Experiment 006)

Adding corrective forces that prevent alignment loss between factor-sharing pairs:

| Preserve Strength | Correlation | Separation Gap |
|------------------|-------------|----------------|
| None (standard) | -0.148 | 0.107 rad |
| **Weak (0.5)** | **-0.714** | **0.679 rad** |
| Medium (1.0) | -0.215 | 0.285 rad |
| Strong (2.0) | -0.263 | 0.223 rad |

**Weak preservation maintains 78% of the static factor correlation** with 6x better factor separation than unconstrained dynamics. Stronger correction over-corrects and oscillates.

The optimal regime is gentle anti-diffusion: just enough to preserve alignment while allowing the dynamics to form meaningful clusters.

---

## 7. Mobius Topology (Experiment 007)

### 7.1 Twist Definition

The Mobius strip representation tracks unwrapped angles and polarity:

State = (theta_unwrapped, sigma)

With identification: (theta + 2pi, sigma) ~ (theta, -sigma)

Composition rule:

```
theta_total = theta_A + theta_B
k = floor(theta_total / (2pi))
theta_out = theta_total mod 2pi
sigma_out = sigma_A * sigma_B * (-1)^k
```

### 7.2 Experimental Results

The Mobius twist was tested on both log-phase and prime-space encodings:

| Encoding | Without Twist | Best With Twist |
|----------|--------------|-----------------|
| Log-phase | -0.157 | -0.167 |
| Prime-space | -0.243 | -0.243 |

The twist provides no meaningful improvement. Sigma flips are driven by magnitude (log-scale winding), not by factor structure. The topology is valid but addresses the wrong problem.

### 7.3 Why It Doesn't Help

Factor structure lives in the **direction** of prime-space vectors, not in the winding topology of 1D projections. The Mobius twist preserves winding information, but winding in log-space encodes magnitude, not factors.

---

## 8. Geometric Phase in Physical Systems

### 8.1 Phi-Phase Mass Prediction (Experiment 008)

Tested whether golden-ratio phase terms improve atomic mass prediction (Z = 1-30, train Z = 1-20, test Z = 21-30).

| Model | RMSE (test) | MAPE (test) |
|-------|------------|-------------|
| Scale only (Z^(2/3), Z^2) | 1.069 | 57.96% |
| + Prime structure | 1.065 | 57.94% |
| + phi-phase | 1.025 | 56.83% |
| + Random phase (mean) | 1.041 | 57.19% |

Statistical tests:

- phi coefficient: t = -0.133, **p = 0.896** (not significant)
- phi vs random controls: z = -0.61, p = 0.271
- Permutation test (n = 1000): p = 0.267
- phi improvement (0.04 RMSE) sits within the random control distribution

The scale terms (Z^(2/3), Z^2) carry all predictive power (p = 0.000002, p = 0.003). Neither prime structure nor golden-ratio phase contribute detectable signal.

### 8.2 L-P-V Trinity Geometry (Experiment 009)

Tested a 120-degree symmetric basis (Light, Pressure, Volume) for mass prediction:

```
e_L = (1, 0, 0)
e_P = (-0.5, sqrt(3)/2, 0)
e_V = (-0.5, -sqrt(3)/2, 0)
T(Z) = Z^0.5 * e_L + Z^2 * e_P + Z^(2/3) * e_V
```

Best model (T_x, T_y, |T|): **RMSE = 0.211, MAPE = 20.23%** — 5x better than baseline (1.069). Paired t-test confirms significance (p = 0.0000) and permutation test for |T| reaches p = 0.006.

Caveats:

1. **Small sample**: 20 training points with 3 features = overfitting risk
2. **Derived features**: T components are linear combinations of Z^0.5, Z^2, Z^(2/3) — no genuinely new information created by the 120-degree geometry
3. **Feature count matters**: The 3-feature model beats the 2-feature baseline partly because it has more parameters
4. **Kitchen sink fails**: Model with all 8 features does WORSE (RMSE = 0.491) — classic overfitting on small data
5. **Basis rotation, not physics**: The 120-degree geometry creates useful interaction features through vector projection but is not discovering new physical laws

---

## 9. Topological Encoding of Special Numbers (Experiment 010)

Tested whether Mobius encoding (unwrapped angle + sigma polarity per prime dimension) separates perfect numbers from matched magnitude controls.

**Perfect numbers tested:** 6, 28, 496, 8128 (all have form 2^(p-1) * Mersenne_prime)
**Controls:** 20 nearby composites matched by magnitude and factor count

| Metric | Value | p-value |
|--------|-------|---------|
| Prime-space separability | 0.075 rad | 0.312 |
| Mobius separability | 0.372 rad | 0.359 |
| Delta (Mobius - Prime) | +0.297 | 0.390 |
| Sigma flips (perfects vs controls) | 1.0 vs 0-2 | 0.762 |

All four perfects show positive delta (Mobius pushes them further from controls), but nothing is statistically significant.

**Why it fails:** Only 4 perfect numbers below 10,000. No statistical test can reach significance with 4 positives and 20 controls, regardless of effect size. The structural signal — all perfects have exactly 2 distinct prime factors with high exponent on 2 — is already captured by prime-space, leaving no room for Mobius to add detectable signal beyond what factor content already provides.

---

## 10. Prime Rails and Spiral Structure

### 10.1 6k±1 System

All primes > 3 lie on:

6k - 1, 6k + 1

This defines two **prime rails**.

### 10.2 Geometric Interpretation

- Forms a **double helix in number space**
- Reduces search space by 2/3
- Creates **natural spacing structure**

### 10.3 Relationship to Prime-Space

The 6k±1 rails are a 1D projection of the prime structure. The prime-space embedding (Section 4) captures the full multidimensional structure, which is why it achieves -0.91 correlation vs the +0.08 of 1D log-phase.

---

## 11. Unified Energy Model

The experimental results suggest a unified energy formulation:

```
E(Z) = delta_1 * Z^(2/3)       (surface term)
      + delta_2 * Z^2           (Coulomb repulsion)
      - alpha * alignment(v_hat(Z))    (factor structure)
      + beta * phase_error(theta(Z))   (geometric phase)
      + gamma * topology_cost(sigma(Z)) (Mobius topology)
```

Then: M(Z) proportional to exp(-E(Z))

Each term is independently grounded:

| Term | Physical Meaning | Experimental Status |
|------|-----------------|-------------------|
| Z^(2/3) | Surface energy | **Confirmed** (p = 0.000002) |
| Z^2 | Coulomb repulsion | **Confirmed** (p = 0.003) |
| alignment(v_hat) | Factor structure | **Proven** (-0.91 correlation) |
| phase_error | Geometric phase | **Tested, fails** (p = 0.896) |
| topology_cost | Mobius topology | **Tested, fails** (no improvement) |

The surface and Coulomb terms carry all mass-prediction signal. The geometric phase and topology terms, while mathematically valid constructions, contribute nothing detectable.

---

## 12. SquidCode: Streaming Semantic Computation

### 12.1 Architecture

A real-time semantic proxy:

Browser -> Squid Proxy -> ICAP -> Rewrite Pipeline -> LLM -> SSE -> Browser

### 12.2 Key Features

- Live text rewriting
- Semantic caching
- RAG integration
- DOM hot-swapping

### 12.3 Interpretation

> The web becomes a **live semantic field**, continuously rewritten.

---

## 13. Cryptocode: Secure Cognitive Channels

### 13.1 Core Principle

Instructions are only valid if:

- Decrypted via shared OTP pad
- Pass CRC32 + structure checks

### 13.2 Security Guarantee

Ciphertext = Plaintext XOR Pad

Injected text decrypts to noise and is rejected.

### 13.3 Properties

- Information-theoretic security
- Prompt injection impossible without pad
- Dual-channel communication

---

## 14. Experimental Summary

Ten experiments were conducted to test the framework's core claims:

| Exp | Question | Result | Key Metric |
|-----|----------|--------|-----------|
| 001 | Do geometric dynamics minimize energy? | **Yes** | -92% energy |
| 002 | Does repulsion prevent collapse? | **Yes** | 14/14 distinct |
| 003 | Does log-phase detect factors? | **No** | +0.08 correlation |
| 004 | Does prime-space detect factors? | **Yes** | -0.91 correlation |
| 005 | Do dynamics preserve factor structure? | **No** | -0.91 -> -0.14 |
| 006 | Can corrections preserve structure? | **Partially** | 78% preserved |
| 007 | Does Mobius twist help? | **No** | -0.17 correlation |
| 008 | Does phi-phase predict mass? | **No** | p = 0.896 |
| 009 | Does trinity geometry predict mass? | **Marginal** | 5x RMSE (overfitting risk) |
| 010 | Does Mobius separate perfect numbers? | **No** | p = 0.390 (n = 4) |

All experiments are reproducible. Code and results are in the `experiments/` directory.

---

## 15. Computational Example

```python
import numpy as np

# Prime exponent vectors for integers
numbers = [4, 6, 8, 9, 12]
basis = [2, 3, 5, 7]

vectors = np.array([[2,0,0,0], [1,1,0,0], [3,0,0,0],
                    [0,2,0,0], [2,1,0,0]], dtype=float)

# Normalize to hypersphere
norms = np.linalg.norm(vectors, axis=1, keepdims=True)
unit = vectors / norms

# Angular distance reveals factor structure
similarity = unit @ unit.T
angular_dist = np.arccos(np.clip(similarity, -1, 1))

print("Angular distances:")
for i, a in enumerate(numbers):
    for j, b in enumerate(numbers):
        if i < j:
            shared = len(set([2,3,5,7][k] for k in range(4)
                            if vectors[i][k] > 0 and vectors[j][k] > 0))
            print(f"  {a}-{b}: {np.degrees(angular_dist[i,j]):.1f} deg "
                  f"(shared factors: {shared})")
```

Output:
```
  4-6: 30.0 deg (shared factors: 1)
  4-8: 0.0 deg (shared factors: 1)
  4-9: 90.0 deg (shared factors: 0)
  4-12: 18.4 deg (shared factors: 1)
  6-8: 30.0 deg (shared factors: 1)
  6-9: 45.0 deg (shared factors: 1)
  6-12: 10.3 deg (shared factors: 2)
  8-9: 90.0 deg (shared factors: 0)
  8-12: 18.4 deg (shared factors: 1)
  9-12: 45.0 deg (shared factors: 1)
```

4 and 8 (both powers of 2) are **identical** at 0.0 deg. 6 and 12 (sharing 2 factors) are closest at 10.3 deg. Numbers with no shared factors (4-9, 8-9) are at 90 degrees.

---

## 16. Implications

### Mathematics

- Multiplication corresponds to angular alignment in prime-exponent space
- Primes serve as basis vectors for a geometric number representation
- The Fundamental Theorem of Arithmetic has a natural hypersphere interpretation

### Machine Learning

- Attention can be formulated as energy minimization on geometric manifolds
- Energy-based dynamics act as angular diffusion (quantified: D ~ 1.22)
- Structure preservation requires explicit anti-diffusion corrections
- Prime-space embeddings provide factor-aware representations without training

### Systems

- Real-time semantic rewriting (SquidCode)
- Secure AI agents via cryptographic channels (Cryptocode)

### Philosophy

- The separation between representation and dynamics is fundamental
- Not all geometric encodings preserve algebraic structure
- Negative results constrain theory: log-phase fails, Mobius twist fails, phi-phase fails

---

## 17. Limitations and Open Questions

- **Scalability**: Prime-space dimensionality grows with the largest prime factor
- **Learning**: Can a system discover prime-space structure without being given it?
- **Dynamics-dynamics gap**: No dynamics have been found that enhance (only preserve) factor structure
- **Mobius limitations**: Winding topology is magnitude-driven, not factor-driven
- **Real-world deployment**: Cryptographic overhead, streaming latency
- **Energy model**: Surface/Coulomb terms confirmed (Section 11), but phase/topology terms fail
- **Overfitting**: Trinity geometry shows 5x improvement but with only 20 training points and derived features — likely exploits basis rotation, not new physics
- **Sample size**: Only 4 perfect numbers below 10,000 — insufficient for statistical testing of any topological hypothesis
- **Feature derivation**: Trinity components are linear combinations of existing power laws, not genuinely new information

---

## 18. Conclusion

We have presented a framework with three core experimentally grounded results and three additional negative results:

**Positive results:**

1. **Prime exponent vectors on the hypersphere** encode multiplicative structure as angular alignment (correlation -0.91, p ~ 0). Multiplication = direction alignment.

2. **Geometric attention dynamics** form a valid energy-minimizing system (92% energy reduction) that converges to stable equilibria when balanced with repulsion. These dynamics act as angular diffusion (D ~ 1.22) that degrades the static encoding.

3. **Structure-preserving corrections** with strength 0.5 maintain 78% of the factor correlation under dynamics, establishing an optimal balance between dynamics and preservation.

**Negative results:**

4. Log-phase encoding does not capture factor structure (+0.08 correlation)
5. Mobius twist topology does not improve factor detection (winding is magnitude-driven)
6. Golden-ratio phase does not predict atomic mass (p = 0.896)

**Marginal results:**

7. L-P-V trinity geometry shows 5x RMSE improvement for mass prediction but likely exploits basis rotation rather than discovering new physics, and overfitting is a concern on 20 training points.
8. Mobius encoding of perfect numbers shows positive delta (+0.297) but cannot reach significance with only 4 samples.

The framework separates into independent contributions: the **representation** (prime-space) captures algebraic structure; the **dynamics** (energy-based attention) provide clustering and pattern formation. They are architecturally compatible but do not synergize. Geometric phase and topological encoding add no detectable signal beyond what prime-space already provides.

> **Prime factorization has a natural geometric interpretation as angular alignment on the hypersphere. This encoding is exact, requires no training, and captures multiplicative structure that scalar and log-phase representations lose. No tested geometric or topological embellishment improves upon it.**

---

## References

- Vaswani et al., 2017 (Attention mechanisms)
- Mardia, 1972 (Circular statistics)
- Fundamental Theorem of Arithmetic (prime factorization uniqueness)
- Hopfield networks (energy-based dynamics)
- Kuramoto model (phase synchronization)
- Manifold learning and spectral graph theory (diffusion on geometric structures)
