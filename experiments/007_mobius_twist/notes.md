# Experiment 007: Mobius Twist — Results

## Conclusion: NO MEANINGFUL IMPROVEMENT FROM TWIST

The Mobius twist (unwrapped angle + sigma polarity flips on winding)
does not improve factor detection or structure preservation.

### Key Findings

- Best Mobius log-phase: -0.167 vs standard -0.157 (marginal, noise-level)
- Best Mobius prime-space: -0.243 (worse than static -0.910)
- Sigma flips occur (5-35 per config) but are randomly distributed
- Winding in log-space is magnitude-driven, not factor-driven

### Why It Doesn't Work

The Mobius twist tracks topological winding: how many times a number's
angle wraps around 2*pi. But this wrapping is determined by the number's
magnitude (log scale), not its factor structure. So sigma flips are
correlated with magnitude, not with factors.

The twist is a valid topological construction, but it solves the wrong
problem. Factor structure lives in the DIRECTION of prime-space vectors,
not in the winding topology of 1D projections.

### Project Status

The Mobius twist is the third approach tried for enhancing factor
detection under dynamics:

1. Standard dynamics (005): destroys structure
2. Structure-preserving flow (006): preserves 78% with weak correction
3. Mobius twist (007): no improvement

The structure-preserving flow (006) remains the best result.
The prime-space encoding (004) remains the real contribution.
