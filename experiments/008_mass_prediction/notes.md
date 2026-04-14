# Experiment 008: phi-Phase Mass Prediction — Results

## Conclusion: PHI-PHASE DOES NOT SIGNIFICANTLY IMPROVE MASS PREDICTION

### Key Findings

- phi coefficient: t=-0.133, **p=0.896** (completely non-significant)
- phi vs random controls: z=-0.61, **p=0.271** (indistinguishable from random)
- Permutation test (n=1000): **p=0.267** (not significant)
- phi RMSE (1.025) sits WITHIN the random control distribution (1.041 +/- 0.027)

### Model Comparison

| Model | RMSE test | MAPE test |
|-------|-----------|-----------|
| Scale only (Z^2/3, Z^2) | 1.069 | 57.96% |
| + Prime structure | 1.065 | 57.94% |
| + phi-phase | 1.025 | 56.83% |
| + Random phase (mean) | 1.041 | 57.19% |

The phi improvement (0.04 RMSE) is within the random control range.
The scale terms (Z^2/3, Z^2) carry all the predictive power (p=0.000002, p=0.003).
Prime structure adds nothing (p=0.817).
phi-phase adds nothing (p=0.896).

### What This Means

Atomic mass is well-described by surface (Z^2/3) and Coulomb (Z^2) terms.
Neither prime structure nor golden-ratio phase contribute detectable signal.
The models are also quite poor overall (~57% MAPE), suggesting linear regression
on these features is inadequate for nuclear mass prediction regardless.
The semi-empirical mass formula requires additional terms (pairing, asymmetry)
that are not captured by prime factorization or geometric phase.
