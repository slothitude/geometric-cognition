# Experiment 011: Phase Transform Scan — Results

## Conclusion: NO PHASE TRANSFORM CARRIES PRIME-SPECIFIC SIGNAL

### Key Findings (Initial Scan)

16 transforms tested on 200,000 integers. 5 survived Bonferroni correction:
- n^1.0: z=+23.81 (p=0.0000)
- n^0.1: z=+7.66 (p=0.0000)
- log(log(n)): z=+4.50 (p=0.0000)
- log(n^0.5+1): z=+4.47 (p=0.0000)
- log(n)/log(log(n)): z=+4.45 (p=0.0000)

### Artifact Check (4 Controls)

**Control 1 — 1/log(n) density correction:**
- n^0.1: 92% of variance explained by density gradient
- log(n)/log(log(n)): 98% explained
- log(log(n)): 56% explained
- n^1.0: 0% explained (something else is happening)

**Control 2 — Local permutation (shuffles within n-neighborhoods):**
- n^1.0: z=+22.03 (signal survives)
- n^0.1: z=+4.14 (survives but weakened)
- All others: reduced or eliminated

**Control 3 — High range only (n in [100000, 200000], near-uniform density):**
- n^1.0: z=+19.27 (signal SURVIVES)
- ALL other transforms: z < 1.05 (signal DISAPPEARS)

**Control 4 — Composites-only (tests if signal is prime-specific):**
- n^1.0: prime_var / composite_var = 1.00 (identical signal for composites!)
- All transforms show ratio near 1.0

### What's Actually Happening

The "signal" in n^1.0 survives all controls but appears identically for composites.
This means it's a structural artifact of the n mod 2pi mapping, not prime-specific.

The signal in slow-growth transforms (n^0.1, log(log(n)), etc.) is entirely
explained by the 1/log(n) prime density gradient mapping to specific phase regions.

### Final Answer

**No transform f(n) -> theta = f(n) mod 2pi causes primes to cluster in phase
space beyond what is explained by:**
1. The non-uniform prime density 1/log(n) (affects slow-growth transforms)
2. Structural artifacts of the integer-to-phase mapping (affects n^1.0)

**Golden-ratio scaled log** (log(n)*phi) performs identically to log(n)*sqrt(2) and
log(n)*e — phi has no special status among multiplicative constants.

### Implications for R = m*phi^2 Theory

Any theory claiming golden-ratio phase carries signal about primes must explain:
1. Why phi shows no advantage over sqrt(2), pi, or e as a phase scaling
2. Why no phase transform shows prime-specific clustering (composites show same signal)
3. Why apparent clustering disappears after density-gradient correction
