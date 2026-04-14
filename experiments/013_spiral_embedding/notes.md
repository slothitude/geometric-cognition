# Experiment 013: Log-Spiral Embedding — Results

## Conclusion: SPIRAL GEOMETRY ADDS ZERO INFORMATION

### Key Findings

**AUC (all constants identical):**
- 6k-1 rail: AUC = 0.5359 for ALL constants (phi, sqrt2, e, pi, random)
- 6k+1 rail: AUC = 0.5316 for ALL constants
- phi avg AUC: 0.5337, other avg AUC: 0.5338 (identical)

**The kill shot (Experiment 5):**
- AUC using only r=log(k): 0.5359
- AUC using r + theta (phi): 0.5359
- Improvement from theta: +0.0000

**Clustering:**
- All cluster ratios ~0.85 (primes slightly more clustered)
- This is because primes concentrate at small k where log-space is dense
- phi (0.855) is actually slightly LESS clustered than average (0.868)

**Permutation test:**
- Real AUC = 0.5359, null mean = 0.503
- The 0.033 gap is entirely the r=log(k) density gradient
- Theta contributes nothing to this gap

### What This Proves

1. A log-spiral embedding r=log(k), theta=alpha*log(k) is a reparameterization
   of a single variable (log k) into 2D polar coordinates
2. The angular component theta carries literally zero information about primality
3. All predictability (AUC 0.5359 vs 0.5 random) comes from the radial component
   r=log(k), which encodes the density gradient (primes are denser at small k)
4. phi has no special status — all constants produce identical results
5. The spiral geometry creates no new information. It is a coordinate transform.

### Why This Is the Definitive Answer

Experiment 011 tested 1D phase. Experiment 012 tested phase within 6k±1 rails.
Experiment 013 tests the full 2D spiral embedding. In ALL cases:
- No constant (including phi) carries prime-specific signal
- The density gradient explains all apparent structure
- The geometric reparameterization creates no new information

The hypothesis "geometric phase/spiral embeddings carry information about
prime structure" is falsified across three independent experiments with
increasingly sophisticated controls.
