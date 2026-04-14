# Experiment 014: Radial Structure of Primes — Results

## Conclusion: PNT IS THE ENTIRE STORY (SNR = 1.1)

### Key Findings

**Density fit:**
- Correlation r = 0.982 (2/log(n) explains 96.5% of density variance)
- Residual SNR = 1.10 (within binomial noise)
- PNT explains prime density on 6k±1 rails completely

**Gap distribution:**
- NOT exponential when pooled across [5, 10^6] — but this is expected
- The density gradient means gap sizes vary by ~1000x across the range
- Pooling different density regimes creates apparent non-exponentiality
- This is a pooling artifact, not genuine structure

**Gap autocorrelation:**
- Significant at all lags (lag-1: r=+0.65)
- BUT: this is the density gradient artifact
- Consecutive primes from the same n-region have similar gaps
- Not genuine gap correlation beyond the density law

**Twin primes:**
- 8168 pairs (6k-1, 6k+1) observed
- Observed/predicted (Hardy-Littlewood) = 1.181
- Twin prime clustering is the one genuine deviation from Cramér randomness
- Well-understood analytically

### What This Means

The prime number theorem (2/log(n) on rails) is the complete description of
prime density. Residuals are within statistical noise. All apparent "structure"
in gaps and autocorrelations comes from pooling across density gradients.

The only genuine non-random structure is twin prime clustering, captured by
the Hardy-Littlewood conjecture. This is established analytic number theory,
not a new discovery.

### Relation to Previous Experiments

Experiments 011-013 showed that NO phase, spiral, or geometric embedding
carries prime-specific signal. Experiment 014 confirms WHY: the density
law 2/log(n) is the complete story. There is no hidden geometric structure
for any phase or spiral encoding to detect.
