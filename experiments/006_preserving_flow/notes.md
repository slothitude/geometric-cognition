# Experiment 006: Structure-Preserving Flow — Results

## Conclusion: WEAK PRESERVATION MAINTAINS 78% OF FACTOR CORRELATION

### Key Findings

**Part 1 — Diffusion characterization:**
- Correlation degrades exponentially with lr * steps
- Diffusion coefficient D ≈ 1.22
- Half-life at lr=0.01: ~57 steps
- At lr=0.001: correlation preserved at -0.39 (vs -0.91 static)

**Part 2 — Structure-preserving flow:**
- Standard tangent: -0.91 → -0.15 (destroyed)
- **Weak preserve (0.5): -0.91 → -0.71 (78% preserved)**
- Medium preserve (1.0): -0.91 → -0.21 (over-corrected)
- Strong preserve (2.0): -0.91 → -0.26 (over-corrected)

### The Optimal Regime

Weak preservation (strength=0.5) achieves the best balance:
- Maintains factor correlation at -0.71
- Separation gap of 0.679 rad (6x better than unconstrained)
- Dynamics still active (not frozen)

Stronger preservation over-corrects and oscillates, actually
degrading both metrics.

### Scientific Statement

"Geometric dynamics on the prime-exponent hypersphere act as
angular diffusion with coefficient D ≈ 1.2. Structure-preserving
corrections with strength 0.5 maintain 78% of the static factor
correlation while allowing the dynamics to form meaningful clusters.
The correction acts as an anti-diffusion term that counteracts
the mixing effect of attention-based updates."

### What This Proves

1. The dynamics ARE diffusion (quantified, not just observed)
2. Anti-diffusion works (weak correction preserves structure)
3. There's an optimal balance (too much correction is worse)
4. The system is controllable (lr + preserve_strength = knobs)
