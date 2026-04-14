# Experiment 009: L-P-V Trinity Geometry — Results

## Conclusion: TRINITY MODEL IS BEST BUT OVERFITTING IS A RISK

### Key Findings

- Model E (T_x, T_y, |T|): RMSE=0.211, MAPE=20.23% — 5x better than baseline
- Baseline (Z^2/3, Z^2): RMSE=1.069, MAPE=57.96%
- Paired t-test: p=0.0000 (significant)
- Permutation test for |T|: p=0.006 (significant)

### Why It Works

T_x = Z^0.5 - 0.5*Z^2 - 0.5*Z^(2/3)  (mixes all three scalings)
T_y = (sqrt(3)/2)*Z^2 - (sqrt(3)/2)*Z^(2/3)  (encodes Z^2 vs Z^(2/3) difference)
|T| = magnitude of the combined vector

The 120-degree geometry creates interaction terms between the three
power-law scalings (Z^0.5, Z^2, Z^(2/3)) through the vector projection.
This is more expressive than using them independently.

### Honest Caveats

1. **Small sample**: 20 training points, 3-9 features = overfitting risk
2. **Same power laws**: T components are linear combinations of Z^0.5, Z^2, Z^(2/3)
   — no genuinely new information is created by the 120-degree geometry
3. **Feature count matters**: Model E (3 features) vs baseline (2 features)
4. **Model I (all 8 features) does WORSE** (0.491) than E (0.211) — classic
   overfitting with too many features on small data

### Verdict

The trinity geometry is a clever basis rotation that creates useful
interaction features, but it's not discovering new physics. With proper
cross-validation on more elements, the advantage would likely shrink.
The 120-degree symmetry is aesthetically pleasing but the model is
exploiting the linear algebra of the basis, not a physical law.
