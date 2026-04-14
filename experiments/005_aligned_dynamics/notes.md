# Experiment 005: Structure-Preserving Dynamics — Results

## Conclusion: DYNAMICS DEGRADE ENCODING, EVEN WITH SPHERE CONSTRAINTS

### Key Findings

- Static encoding: -0.910 correlation (near-perfect factor detection)
- Unconstrained dynamics: +0.073 (destroyed)
- Sphere-projected: -0.127 (mostly destroyed)
- Tangent-space: -0.141 (mostly destroyed)
- Best parameter sweep: -0.299 (significantly degraded)

Sphere constraints help (maintain sign, partial separation) but
cannot prevent degradation. Slower learning rates preserve more
structure, suggesting the dynamics are inherently destructive.

### What This Means

The prime-space encoding is self-contained. It doesn't benefit from
iterative dynamics — the signal is already maximal at the static
level. The attention + repulsion system serves a different purpose
(clustering, pattern formation) that is orthogonal to factor detection.

### The Two Independent Contributions

1. **Prime-space encoding** (-0.910 correlation) — a static
   representation where multiplication = direction alignment

2. **Energy-based geometric dynamics** (experiments 001-002) —
   a system for energy minimization, convergence, and equilibrium

They are architecturally compatible but functionally independent.
Neither enhances the other.

### Recommendation

Stop trying to make dynamics enhance factor detection. Instead:
- Use the encoding as-is for factor-aware representations
- Use the dynamics separately for pattern formation / clustering tasks
- The combined system could be useful where both are needed independently
