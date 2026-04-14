# Experiment 017: Zeta-Zero Interference Structure — Results

## Conclusion: SIMPLIFIED ZETA WAVES DO NOT DETECT PRIME STRUCTURE

### Key Findings

**Test 1 (Spectral analysis):**
- gamma_1 (14.135) appears near a spectral peak (14.064) — possible detection
- But most other zeta zeros do NOT appear as top spectral peaks
- Top peaks (17.8, 16.5, 35.3) don't match any zeta zero
- Power at gamma_1 is 163x median, but gamma_4 is only 7.7x — inconsistent
- Verdict: weak, inconclusive

**Test 2 (Wave vs individual primality):**
- r = -0.0165 (technically "significant" due to 66k samples, but negligible)
- AUC improvement over k alone: +0.0006
- The wave is mostly just correlated with log(n) — density gradient leaking
- Verdict: no meaningful signal for individual primes

**Test 3 (Prime counting error vs zero sum):**
- r = 0.0021 — essentially ZERO correlation
- Convergence test: flat across 1, 3, 5, 10, 15 zeros — more don't help
- This SHOULD work (it's established math) but the simplified implementation fails
- Reason: the explicit formula requires complex terms x^rho/rho with proper
  phase and amplitude, not just cos(gamma * log(x))
- The cosine-only version destroys the phase relationships that make the formula work

**Test 4 (Real vs random zeros):**
- Error correlation: real zeros z = -0.053 vs random — indistinguishable
- Wave-primality: real zeros z = -7.284 (more negative than random)
- BUT the absolute correlation is still negligible (-0.0165)
- The "significance" comes from the wave correlating with log(n), not from
  the specific values of zeta zeros
- Verdict: zeta zeros are not special for predicting primes in this simplified form

**Test 5 (Local modulation):**
- r = -0.803 looks impressive — but entirely a density artifact
- Negative wave values correspond to small n (more primes, higher density)
- Positive wave values correspond to large n (fewer primes)
- The PNT correction doesn't fully remove this because the wave creates
  non-uniform sampling across the density gradient
- Verdict: artifact, not genuine modulation

### Why the Explicit Formula Didn't Show

The simplified cosine sum `S(n) = sum cos(gamma * log(n))` drops critical structure:

1. **Complex phase**: The full formula uses x^(1/2 + i*gamma) = sqrt(x) * e^(i*gamma*log(x)),
   which has both real and imaginary parts. Just taking cos loses half the information.

2. **Proper weighting**: Each term should be divided by |rho| = sqrt(1/4 + gamma^2).
   Higher-frequency zeros contribute less.

3. **Amplitude decay**: The 1/sqrt(x) factor means the oscillations diminish for large x,
   which is what allows the smooth density law to dominate.

4. **Trivial zeros**: The full formula includes contributions from the trivial zeros at
   negative even integers, which we omitted.

5. **Convergence**: 15 zeros is far too few. The explicit formula requires
   hundreds to thousands of zeros for accurate reconstruction.

### What This Means

The "interference" idea is real in the sense that the Riemann explicit formula exists.
But:

1. It requires the FULL complex formula, not a simplified cosine sum
2. It requires THOUSANDS of zeros, not 15
3. It reconstructs pi(x) (counting function), not individual primality
4. Even perfectly implemented, it gives you the same information as counting primes
   — which a sieve does faster

The zeta zeros encode the same information as the prime counting function.
They are equivalent representations, not a shortcut. Computing zeta zeros
is not easier than computing primes.

### Relation to Previous Experiments

Experiments 011-016 showed that no geometric/phase/field approach detects primes.
Experiment 017 shows that even the LEGITIMATE spectral structure (zeta zeros)
doesn't help in simplified form — and even in full form, it's an equivalence
with prime counting, not a predictive shortcut.

The "wave" interpretation of primes is mathematically valid but operationally
useless: it replaces one hard computation (is n prime?) with another equally
hard computation (compute enough zeta zeros to reconstruct pi(x)).

### The Honest Summary

| Claim | Status |
|-------|--------|
| Primes have spectral structure | TRUE (explicit formula, 1859) |
| This structure is new/discovered | FALSE (known for 165+ years) |
| Zeta zeros predict individual primes | FALSE (they predict aggregates) |
| Simplified cosine sum detects signal | FALSE (r = 0.002) |
| Real zeros beat random frequencies | FALSE in this implementation (z = -0.05) |
| "Interference" is a useful computation | FALSE (sieve is faster) |
