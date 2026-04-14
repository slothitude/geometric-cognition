# Experiment 015: Composite Coverage vs Prime Survival — Results

## Conclusion: CIRCULAR — Coverage IS the Definition of Primality

### Key Findings

**The tautology:**
- Coverage(k, sign) = number of lattice factorizations of 6k+sign
- Coverage=0 means "no lattice factorization exists" = prime BY DEFINITION
- Coverage>0 means "at least one factorization exists" = composite BY DEFINITION
- 100.0% of primes have coverage=0, 0.0% of composites have coverage=0

**Mann-Whitney U = 0 (p = 0):**
- Perfect separation — but this is trivial because coverage partitions the dataset
- into {primes} and {composites} with zero overlap

**Permutation test: z = +0.000, p = 1.000:**
- Shuffling labels within k-bins changes nothing
- The "correlation" between coverage and primality is 100% explained by the definitional relationship

**Local suppression (Test 5) shows the OPPOSITE of predicted:**
- Prime rate (low neighbor cov): 0.2344
- Prime rate (high neighbor cov): 0.3048
- High-coverage neighbors → MORE primes, not fewer
- This is because coverage increases with k (density gradient), and
  small-k regions have more primes AND lower coverage

**Density-corrected analysis:**
- r = -0.861 between coverage and residual prime rate
- This appears significant, but the permutation test (p=1.000) confirms it's
  an artifact of coverage being a monotonic function of k

### Why This Is Circular

The experiment asks "does the number of ways to factor n predict whether n is prime?"
This is equivalent to asking "does n being factorable predict whether n is prime?"
The answer is trivially yes — that IS what prime means.

The "composite coverage field" at position k is just a sieve output.
It contains exactly the same information as the primality test itself.
No spatial or geometric structure is being detected.

### The One Non-Trivial Test (Test 5)

Test 5 tried to break the circularity by asking: "does coverage at position k
predict primality at NEIGHBORING positions k±1?" This would be non-circular
because the factorizations of 6(k±1)±1 are different from those of 6k±1.

Result: primes are actually MORE common in high-coverage neighborhoods,
not less. This is the density gradient artifact (small k = more primes = fewer
composites = lower coverage).

After PNT correction: low-coverage neighborhoods show +0.048 residual,
high-coverage neighborhoods show +0.130 residual. Both positive (more primes
than expected by PNT alone), but no suppression effect.

### What This Means

The composite coverage idea, while intuitively appealing, reduces to:
"primes are numbers that can't be factored." This is a tautology.

For a non-circular version, we would need to test whether the SPATIAL PATTERN
of composites (not their existence at a specific point) predicts primality
at nearby points. Test 5 attempted this and found no signal beyond PNT.

### Relation to Previous Experiments

Experiments 011-014 showed that no phase, spiral, or geometric encoding
carries prime-specific signal. Experiment 015 shows that the "composite
coverage field" doesn't either — the apparent signal is the definition of
primality restated in geometric language.
