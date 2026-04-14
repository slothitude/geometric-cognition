# Experiment 012: 6k±1 Rail Phase Structure — Results

## Conclusion: NO PHASE SIGNAL WITHIN THE PRIME RAILS

### Key Findings

**Constant bake-off:**
- phi avg KS stat: 0.0264
- Other constants avg KS stat: 0.0264
- **phi = exactly 1.00x average** — no special status whatsoever
- sqrt2 actually has the highest KS stat (0.0415), not phi
- ALL 18 constant/rail combinations are "significant" (p<0.05) — but this is
  the density gradient leaking through, not phase structure

**Local permutation (controls for density gradient):**
- ALL constants have z < 0 (worse than random)
- phi: z = -1.39, p = 0.946
- The observed variance is LOWER than shuffled labels — no real signal

**Density gradient explains:**
- phi: 77-79% of raw variance
- sqrt2: 67%
- pi: 47-65%
- Residuals are noise

**Rail asymmetry:**
- All KS stats < 0.006, all p > 0.99
- 6k-1 and 6k+1 rails are completely symmetric
- No helical structure detected in any constant's phase space

### What This Proves

The initial "significance" (all p<0.05 in Experiment 2) comes entirely from:
1. Large sample sizes (9k primes, 24k composites per rail) detecting the
   tiny density gradient effect
2. The 2/log(6k) prime density on rails varying with k
3. Phase bins at different log(k) values having different base densities

After controlling for the density gradient (local permutation), every constant
shows zero or negative signal. phi is exactly average among all tested constants.

### Why the 6k±1 Frame Was Better (But Still Negative)

The lattice framing correctly isolates the prime-containing rails, removing
contamination from multiples of 2 and 3. This is the right experimental design.
But even within this cleaner frame, phase carries no information about whether
a lattice point is prime or composite.
