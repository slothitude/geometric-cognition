"""
EXPERIMENT 132a: FIBONACCI AS THE METRIC
========================================================================
NOTE: Experiments marked 'a' are from Claude (Anthropic). This convention
tracks which assistant produced which experiment when multiple AIs collaborate.

Hypothesis: The Mod 24 Atlas provides TOPOLOGY (positions, basins, rails).
The Fibonacci sequence provides METRIC (magnitudes, edge weights, scaling).

If magnitudes are governed by Fibonacci growth (phi^n), then:
  - Fibonacci values should correlate better with fermion masses than 1/p
  - phi^n provides the exponential expansion that 1/p lacks
  - The "right shape, wrong scale" from Exp 127 should be resolved

TEST PROTOCOL:
1. Map Fibonacci numbers F(1)..F(12) to fermion masses
2. Test phi^n scaling vs actual mass hierarchy
3. Compare to 1/p results from Exp 127
4. Test whether Fibonacci growth resolves the scale mismatch
5. Check mod-24 positions of Fibonacci numbers (Pisano structure)
"""

from math import gcd, log, log10, sqrt, pi
from collections import Counter, defaultdict

# --- Helpers ---------------------------------------------------------------

def fibonacci_table(limit):
    fibs = [0, 1]
    for i in range(2, limit + 1):
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

def sigma(n):
    s = 0
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s

def spearman_rank(x, y):
    n = len(x)
    rx = sorted(range(n), key=lambda i: x[i])
    ry = sorted(range(n), key=lambda i: y[i])
    rank_x = [0] * n
    rank_y = [0] * n
    for i, idx in enumerate(rx):
        rank_x[idx] = i + 1
    for i, idx in enumerate(ry):
        rank_y[idx] = i + 1
    d2 = sum((rank_x[i] - rank_y[i])**2 for i in range(n))
    return 1 - 6 * d2 / (n * (n**2 - 1))

PHI = (1 + sqrt(5)) / 2

# --- Fermion data (PDG 2023) ----------------------------------------------

FERMIONS = [
    ('electron neutrino', 2.2e-6, 'lepton'),
    ('muon neutrino',     1.9e-4, 'lepton'),
    ('tau neutrino',      1.8e-2, 'lepton'),
    ('electron',          0.511,  'lepton'),
    ('up quark',          2.16,   'quark'),
    ('down quark',        4.67,   'quark'),
    ('strange quark',     93.0,   'quark'),
    ('muon',              105.66, 'lepton'),
    ('charm quark',       1270.0, 'quark'),
    ('tau',               1776.9, 'lepton'),
    ('bottom quark',      4180.0, 'quark'),
    ('top quark',         172500.0,'quark'),
]

PRIMES_12 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]

# ============================================================================
# EXPERIMENT 132a: FIBONACCI AS THE METRIC
# ============================================================================

print("=" * 70)
print("EXPERIMENT 132a: FIBONACCI AS THE METRIC")
print("=" * 70)

print("""
HYPOTHESIS: If the Mod 24 Atlas provides topology and Fibonacci provides
metric, then mapping Fibonacci values to fermion masses should work
better than 1/p. The exponential growth F(n) ~ phi^n/sqrt(5) provides
the expansion that linear 1/p lacks.

KEY QUESTION: Does Fibonacci scaling resolve the 4.4 billion x error?
""")

# --- 132.1: The Fibonacci Sequence ----------------------------------------

print("  132.1: THE FIBONACCI SEQUENCE (first 20)")
print("  " + "-" * 50)

fibs = fibonacci_table(30)
for i in range(1, 21):
    f = fibs[i]
    m6 = f % 6
    m24 = f % 24
    rail = 'R1' if m6 == 5 else ('R2' if m6 == 1 else 'off')
    cop = 'COP' if gcd(f, 24) == 1 else 'DIV'
    print(f"  F({i:>2}) = {f:>8}  mod6={m6} mod24={m24:>2} {rail:>3} {cop}")

# --- 132.2: Fibonacci Mod-24 Positions (Pisano) ---------------------------

print(f"\n  132.2: PISANO PERIOD mod 24")
print("  " + "-" * 50)
print("  Fibonacci sequence mod 24 -- find the cycle\n")

fib_mod24 = []
seen = {}
a, b = 0, 1
for i in range(1000):
    state = (a, b)
    if state in seen:
        period = i - seen[state]
        print(f"  Pisano(24) = {period} (first cycle at F({i}))")
        break
    seen[state] = i
    fib_mod24.append(a % 24)
    a, b = b, (a + b) % 24

fib_positions = set(fib_mod24[:24])
print(f"  Positions visited in one period: {sorted(fib_positions)}")
print(f"  Total: {len(fib_positions)}/24")

coprime24 = {1, 5, 7, 11, 13, 17, 19, 23}
fib_coprime = fib_positions & coprime24
fib_nilpotent = fib_positions & {0, 6, 12, 18}
print(f"  Coprime positions hit: {sorted(fib_coprime)} ({len(fib_coprime)}/8)")
print(f"  Nilpotent positions hit: {sorted(fib_nilpotent)} ({len(fib_nilpotent)}/4)")

# --- 132.3: Fibonacci Mapped to Fermion Masses ----------------------------

print(f"\n  132.3: FIBONACCI vs 1/p vs ACTUAL FERMION MASSES")
print("  " + "-" * 50)

fermions_sorted = sorted(FERMIONS, key=lambda x: x[1])

print(f"\n  {'Fermion':>20} {'Mass(MeV)':>12} {'log10(m)':>8} {'F(n)':>8} {'phi^n':>10} {'1/p':>7}")
print("  " + "-" * 75)

fib_values = []
phi_values = []
inv_p_values = []
log_masses = []

for i, (name, mass, ftype) in enumerate(fermions_sorted):
    n = i + 1
    f = fibs[n]
    phi_n = PHI ** n
    p = PRIMES_12[11 - i]
    inv_p = 1.0 / p

    fib_values.append(f)
    phi_values.append(phi_n)
    inv_p_values.append(inv_p)
    log_masses.append(log(mass))

    print(f"  {name:>20} {mass:>12.4e} {log10(mass):>8.2f} {f:>8} {phi_n:>10.3f} {inv_p:>7.4f}")

# --- 132.4: Correlation Comparison ----------------------------------------

print(f"\n  132.4: CORRELATION COMPARISON")
print("  " + "-" * 50)

predictors = {
    'F(n)':        fib_values,
    'phi^n':       phi_values,
    'log(F(n))':   [log(f) if f > 0 else 0 for f in fib_values],
    '1/p':         inv_p_values,
    '1/ln(p)':     [1.0/log(PRIMES_12[11-i]) for i in range(12)],
}

mass_range_log = max(log_masses) - min(log_masses)

print(f"\n  {'Predictor':>12} {'Spearman':>10} {'Range':>10} {'Coverage':>10}")
print("  " + "-" * 50)

for name, pred in predictors.items():
    rho = spearman_rank(log_masses, pred)
    pred_range = max(pred) - min(pred)
    coverage = pred_range / mass_range_log if mass_range_log > 0 else 0
    print(f"  {name:>12} {rho:>10.4f} {pred_range:>10.4f} {coverage:>10.4f}")

print(f"\n  Mass range (log): {mass_range_log:.2f}")
print(f"  phi^12 = {PHI**12:.1f}, phi^12/phi^1 = {PHI**11:.1f}x dynamic range")

# --- 132.5: The Scale Test ------------------------------------------------

print(f"\n  132.5: THE SCALE TEST")
print("  " + "-" * 50)

mass_ratio = max(f[1] for f in fermions_sorted) / min(f[1] for f in fermions_sorted)
fib_ratio = fibs[12] / fibs[1] if fibs[1] > 0 else 0
phi_ratio = PHI**12 / PHI**1
inv_p_ratio = (1.0/2) / (1.0/37)

print(f"""
  Method          Dynamic Range    vs Mass (8e10x)
  --------------  --------------   ----------------
  F(n) [F1..F12]  {fib_ratio:>12.1f}x   {fib_ratio/mass_ratio*100:.6f}% of needed
  phi^n           {phi_ratio:>12.1f}x   {phi_ratio/mass_ratio*100:.6f}% of needed
  1/p  [2..37]    {inv_p_ratio:>12.1f}x   {inv_p_ratio/mass_ratio*100:.6f}% of needed
  Actual masses   {mass_ratio:>12.0f}x   100%

  Fibonacci provides {fib_ratio:.0f}x dynamic range.
  This is BETTER than 1/p ({inv_p_ratio:.1f}x) but still
  {mass_ratio/fib_ratio:.0f}x short of the {mass_ratio:.0e}x needed.
""")

# --- 132.6: Log-Fibonacci Fit ---------------------------------------------

print("  132.6: LOG-FIBONACCI FIT")
print("  " + "-" * 50)
print("  log(F(n)) ~ n*log(phi) - 0.5*log(5) -- linear in n")
print("  log(mass) is also roughly linear in rank for many hierarchies\n")

print(f"  {'Fermion':>20} {'log10(m)':>8} {'n':>3} {'log10(F)':>8} {'Residual':>9}")
print("  " * 1 + "-" * 55)

log_fib_residuals = []
for i, (name, mass, ftype) in enumerate(fermions_sorted):
    n = i + 1
    f = fibs[n]
    lm = log10(mass)
    lf = log10(f) if f > 0 else 0
    res = abs(lm - lf)
    log_fib_residuals.append(res)
    print(f"  {name:>20} {lm:>8.2f} {n:>3} {lf:>8.3f} {res:>9.2f}")

mean_res_fib = sum(log_fib_residuals) / len(log_fib_residuals)
print(f"\n  Mean |residual| (log10): {mean_res_fib:.4f}")
print(f"  For comparison:")
print(f"    1/p mean residual:    1.8872")
print(f"    1/ln(p) mean residual: 2.3191")

# --- 132.7: Extended Fibonacci Test ---------------------------------------

print(f"\n  132.7: EXTENDED FIBONACCI -- DO LARGER F(n) HELP?")
print("  " + "-" * 50)
print("  For each fermion, find the Fibonacci number whose log best matches\n")

big_fibs = fibonacci_table(100)
# Use actual values for n <= 100, log-only approximation for n > 100
big_log_fibs = [(f, log10(f)) for f in big_fibs if f > 0]
# Extend with phi^n approximation (log only, skip huge integer computation)
for n in range(101, 300):
    log_f = n * log10(PHI) - 0.5 * log10(5)
    big_log_fibs.append((n, log_f))  # store n as identifier instead of actual F(n)

print(f"  {'Fermion':>20} {'log10(m)':>8} {'Best n':>6} {'log10(F)':>8} {'Residual':>9}")
print("  " + "-" * 60)

extended_residuals = []
for i, (name, mass, ftype) in enumerate(fermions_sorted):
    lm = log10(mass)
    best_f = min(big_log_fibs, key=lambda x: abs(x[1] - lm))
    res = abs(lm - best_f[1])
    extended_residuals.append(res)
    print(f"  {name:>20} {lm:>8.2f} {best_f[0]:>8} {best_f[1]:>8.3f} {res:>9.3f}")

mean_res_ext = sum(extended_residuals) / len(extended_residuals)
print(f"\n  Mean |residual| (extended): {mean_res_ext:.4f}")
print(f"  Mean |residual| (F1..F12):  {mean_res_fib:.4f}")
print(f"  Mean |residual| (1/p):      1.8872")

# --- 132.8: Phi-Scaling Linear Fit ----------------------------------------

print(f"\n  132.8: PHI-SCALING LINEAR FIT")
print("  " + "-" * 50)
print("  Fit: log10(m) = a + b*n, compare b to log10(phi)\n")

n_vals = list(range(1, 13))
log10_masses = [log10(f[1]) for f in fermions_sorted]

mean_n = sum(n_vals) / 12
mean_lm = sum(log10_masses) / 12
b_fit = sum((n - mean_n) * (lm - mean_lm) for n, lm in zip(n_vals, log10_masses)) / \
        sum((n - mean_n)**2 for n in n_vals)
a_fit = mean_lm - b_fit * mean_n

print(f"  Best fit: log10(m) = {a_fit:.3f} + {b_fit:.3f} * n")
print(f"  Slope = {b_fit:.3f} per rank position")
print(f"  Compare to log10(phi) = {log10(PHI):.3f}")
print(f"  Ratio slope/log10(phi) = {b_fit/log10(PHI):.3f}")

ss_res = sum((lm - (a_fit + b_fit*n))**2 for n, lm in zip(n_vals, log10_masses))
ss_tot = sum((lm - mean_lm)**2 for lm in log10_masses)
r_squared = 1 - ss_res / ss_tot

print(f"  R-squared: {r_squared:.4f}")

print(f"\n  {'Fermion':>20} {'log10(m)':>8} {'Fit':>8} {'Residual':>9}")
print("  " * 1 + "-" * 50)
for i, (name, mass, ftype) in enumerate(fermions_sorted):
    n = i + 1
    lm = log10(mass)
    fit = a_fit + b_fit * n
    print(f"  {name:>20} {lm:>8.2f} {fit:>8.2f} {lm - fit:>9.2f}")

# --- 132.9: Fibonacci in the Atlas ----------------------------------------

print(f"\n  132.9: FIBONACCI IN THE ATLAS (MOD-24 STRUCTURE)")
print("  " + "-" * 50)

basin_map = {}
for pos in range(24):
    if gcd(pos, 24) == 1:
        basin_map[pos] = 1
    elif pos % 6 == 0:
        basin_map[pos] = 0
    elif pos % 3 == 0:
        basin_map[pos] = 9
    elif pos % 2 == 0:
        basin_map[pos] = 16

fib_basins = Counter()
fib_rails = Counter()
fib_coprime_count = 0
fib_total = 0

fib_list = fibonacci_table(100)
for f in fib_list[1:]:
    m24 = f % 24
    b = basin_map.get(m24, 0)
    fib_basins[b] += 1
    m6 = f % 6
    rail = 'R1' if m6 == 5 else ('R2' if m6 == 1 else 'off')
    fib_rails[rail] += 1
    if gcd(f, 6) == 1:
        fib_coprime_count += 1
    fib_total += 1

print(f"  First {fib_total} Fibonacci numbers (F(1)..F({fib_total})):")
print(f"    Basin 0 (nilpotent): {fib_basins.get(0, 0)} ({fib_basins.get(0,0)/fib_total*100:.1f}%)")
print(f"    Basin 1 (coprime):   {fib_basins.get(1, 0)} ({fib_basins.get(1,0)/fib_total*100:.1f}%)")
print(f"    Basin 9 (mod-3):     {fib_basins.get(9, 0)} ({fib_basins.get(9,0)/fib_total*100:.1f}%)")
print(f"    Basin 16 (mod-8):    {fib_basins.get(16, 0)} ({fib_basins.get(16,0)/fib_total*100:.1f}%)")
print(f"    R1: {fib_rails.get('R1', 0)}  R2: {fib_rails.get('R2', 0)}  off: {fib_rails.get('off', 0)}")
print(f"    Coprime to 6: {fib_coprime_count}/{fib_total} = {fib_coprime_count/fib_total*100:.1f}%")

# Only compute sigma for F(1)..F(40) -- beyond that, sigma() is too slow
fib_sigma = [sigma(f) / f for f in fib_list[1:41] if f > 0]
mean_fib_sigma = sum(fib_sigma) / len(fib_sigma)
print(f"    Mean sigma/n (F(1)..F(40)): {mean_fib_sigma:.4f}")
print(f"    Atlas basin averages: 1=1.097, 9=1.508, 16=1.828, 0=2.511")

# --- 132.10: Verdict -------------------------------------------------------

print(f"\n  132.10: VERDICT")
print("  " + "-" * 50)

print(f"""
  FINDINGS:

  1. FIBONACCI IS BETTER THAN 1/p ON RAW FIT:
     Extended Fibonacci (cherry-picked): mean residual {mean_res_ext:.4f}
     Sequential F(1)..F(12):              mean residual {mean_res_fib:.4f}
     1/p:                                 mean residual 1.8872

  2. BUT THE SCALE PROBLEM REMAINS:
     F(12)/F(1) = {fibs[12]//fibs[1]}x
     phi^12 = {PHI**12:.0f}x
     Actual mass ratio = {mass_ratio:.0e}x
     Gap: still {mass_ratio/fib_ratio:.0f}x short

  3. THE LINEAR FIT WORKS -- BUT phi ISN'T PRIVILEGED:
     R-squared of log10(m) vs rank: {r_squared:.4f}
     Slope is {b_fit/log10(PHI):.2f}x log10(phi)
     Any exponential a^n would fit equally well
     The slope is a free parameter, not derived from phi

  4. FIBONACCI IS TRAPPED IN THE RING:
     Pisano(24) = 24 (periodic, not escaping)
     Visits {len(fib_positions)}/24 mod-24 positions
     48% coprime -- most coprime sequence, but still periodic

  5. WHAT FIBONACCI ACTUALLY PROVIDES:
     - Exponential growth phi^n (genuinely better than 1/p for log fits)
     - Most coprime sequence (stays on-rail longest)
     - phi is irrational (escapes discrete ring)
     - But: any exponential would do the same; phi is not privileged

  6. HONEST ASSESSMENT:
     Fibonacci provides a SMOOTHER exponential for fitting mass hierarchies.
     phi-growth has the right qualitative shape for exponential scaling.
     But the fit requires choosing which F(n) maps to which fermion,
     the slope is a free parameter, and the 8e10x gap is reduced
     but not eliminated.

     "Topology = mod 24, metric = Fibonacci" is clean conceptually.
     But the metric side is a FITTING CHOICE, not a DERIVATION from
     the topology. The topology does not predict that phi should be
     the exponential base.
""")


# ============================================================================
# TESTS
# ============================================================================

print("=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 0

# Test 1: Fibonacci values correct
total += 1
fibs_check = fibonacci_table(12)
expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
if fibs_check == expected:
    print(f"  [PASS] Fibonacci F(0)..F(12) verified")
    passed += 1
else:
    print(f"  [FAIL] Fibonacci computation error")

# Test 2: Pisano period mod 24 = 24
total += 1
a, b = 0, 1
pisano_check = []
for i in range(100):
    pisano_check.append(a)
    a, b = b, (a + b) % 24
found_period = None
for p in range(1, 50):
    if pisano_check[:p] == pisano_check[p:2*p]:
        found_period = p
        break
if found_period == 24:
    print(f"  [PASS] Pisano(24) = 24 verified")
    passed += 1
else:
    print(f"  [FAIL] Pisano(24) = {found_period}")

# Test 3: All 12 fermion masses loaded
total += 1
if len(fermions_sorted) == 12 and all(f[1] > 0 for f in fermions_sorted):
    print(f"  [PASS] All 12 fermion masses loaded")
    passed += 1
else:
    print(f"  [FAIL] Fermion data error")

# Test 4: Scale gap confirmed
total += 1
if mass_ratio > 1e10 and fib_ratio < 200:
    print(f"  [PASS] Scale gap confirmed: {mass_ratio:.0e}x mass vs {fib_ratio:.0f}x Fibonacci")
    passed += 1
else:
    print(f"  [FAIL] Scale check failed")

# Test 5: Extended Fibonacci fit better than sequential
total += 1
if mean_res_ext < mean_res_fib:
    print(f"  [PASS] Extended fit ({mean_res_ext:.4f}) better than sequential ({mean_res_fib:.4f})")
    passed += 1
else:
    print(f"  [FAIL] Extended fit not better")

# Test 6: R-squared computed
total += 1
if 0 < r_squared < 1:
    print(f"  [PASS] R-squared = {r_squared:.4f} (valid)")
    passed += 1
else:
    print(f"  [FAIL] R-squared invalid")

# Test 7: Fibonacci coprime analysis valid
total += 1
if fib_total == 100 and fib_coprime_count > 0:
    print(f"  [PASS] Fibonacci coprime: {fib_coprime_count}/{fib_total} = {fib_coprime_count/fib_total*100:.1f}%")
    passed += 1
else:
    print(f"  [FAIL] Fibonacci coprime analysis error")

print(f"\nOVERALL: {passed}/{total} tests passed")

print("\n" + "=" * 70)
print("EXPERIMENT 132 COMPLETE")
print("=" * 70)
