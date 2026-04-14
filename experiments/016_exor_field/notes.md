# Experiment 016: EXOR Field Test — Results

## Conclusion: COMPOSITE FIELDS ADD NOTHING BEYOND PNT

### Key Findings

**Raw comparison (uncorrected):**
- Primes have ~93-95% the field value of composites across all window sizes
- Highly "significant" by Mann-Whitney (p < 1e-22)
- BUT: this is 100% the density gradient (primes concentrate at small k)

**Density-corrected (within k-bins):**
- Only 1/50 k-bins significant at p=0.05 — exactly chance level (2%)
- First k-bin shows a tiny signal (p=0.0002) because small-k region has
  very few numbers and the density gradient is steepest there
- All other bins: p > 0.26

**AUC (predictive value):**
- k-only AUC: 0.5337 (density gradient baseline)
- k + field AUC: 0.5336 (IMPROVEMENT: -0.0001)
- Adding the field actually makes prediction WORSE
- Field-only AUC: 0.5304-0.5332 (just the density gradient leaking through)

**Permutation test (shuffling within k-bins):**
- Window 0.10: z=+1.058, p=0.148
- Window 0.50: z=+0.545, p=0.299
- NOT significant. The field carries no prime-specific signal.

**Effect sizes:**
- Mean Cohen's d: +0.005 (essentially zero)
- 0% of k-bins have |d| > 0.2
- 40% of bins have d < 0 (primes slightly higher field — opposite of predicted)

### What This Proves

The "composite exclusion field" hypothesis is falsified:

1. Composites do NOT create detectable spatial fields in log-space
2. Primes do NOT sit in low-composite-density regions beyond what PNT explains
3. The apparent raw signal (primes in lower-field areas) is 100% explained by
   the density gradient (primes are denser at small k, where everything has lower field)
4. Adding field information to k makes prediction WORSE, not better

### Why the Raw Signal Exists

Primes are more common at small n, where both the field values and prime density
are higher. When you pool across all k values, primes appear to have lower field
values — but this is because the prime-rich region (small k) also has lower field
values for everything. Within any fixed k-range, primes and composites have
identical field values.

### The Core Insight

Multiplication is combinatorial, not wave-like. The structure of composites
does not create interference patterns or exclusion fields. A number's primality
is determined by whether IT specifically can be factored, not by the ambient
density of composites in its neighborhood.

### Relation to Previous Experiments

- Exp 015: Coverage IS primality (circular)
- Exp 016: Coverage NEIGHBORS don't predict primality (non-circular, null result)
- Together: composites explain primes only through exact factorization,
  not through spatial proximity or field effects
