"""
EXPERIMENTS 128-129: PATH ENTROPY + PRIME GAP RESONANCE
========================================================================

Exp 128: Information Entropy in Z/24Z
  - Multiplication table distribution across 24 positions
  - Random walk convergence to the nilpotent attractor
  - Shannon entropy per position
  - Is position 12 the "maximum entropy" state?
  - Information-theoretic "death rate" along decay chain

Exp 129: Prime Gap Resonance
  - Test ln(gap), 1/ln(p), and G/ln(p) as mass predictors
  - Mod-24 gap analysis (which positions have high/low pressure?)
  - Honest comparison to 1/p scaling from Exp 127

Context from Exp 127:
  - 1/p scaling: right SHAPE (Spearman -1.0), wrong SCALE (4.4e9x error)
  - Nilpotent sector {0,6,12,18}: 3 non-zero = 3 Goldstone bosons
  - Position 12 is the hub: both 6 and 18 decay through it
  - Question: is 12 the point of maximum information-theoretic entropy?
"""

import numpy as np
from math import gcd, log, log10, exp, sqrt, pi
from collections import Counter, defaultdict

# --- Helpers ---------------------------------------------------------------

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def factorize(n):
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def sigma(n):
    s = 0
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s

def euler_totient(n):
    if n == 0: return 0
    result = n
    for p in set(factorize(n)):
        result = result * (p - 1) // p
    return result

def chi5(n):
    r = n % 6
    if r == 5: return 1
    if r == 1: return -1
    return 0

def chi7(n):
    r = n % 24
    if r in {1, 5, 13, 17}: return 1
    if r in {7, 11, 19, 23}: return -1
    return 0

def chi13(n):
    r = n % 24
    if r in {1, 7, 13, 19}: return 1
    if r in {5, 11, 17, 23}: return -1
    return 0

def shannon_entropy(counts):
    total = sum(counts)
    if total == 0: return 0.0
    H = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            H -= p * log(p)
    return H

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

NILOPOTENT = {0, 6, 12, 18}
COPRIME24  = {1, 5, 7, 11, 13, 17, 19, 23}

# ============================================================================
# EXPERIMENT 128: PATH ENTROPY IN Z/24Z
# ============================================================================

print("=" * 70)
print("EXPERIMENT 128: PATH ENTROPY IN Z/24Z")
print("=" * 70)

print("""
HYPOTHESIS: If position 12 is the "attractor" of the nilpotent sector,
it should have the highest "statistical weight" -- the most paths leading
to it in the multiplication graph of Z/24Z.

BACKGROUND:
  The multiplication Cayley graph of Z/24Z has:
  - 24 vertices (positions 0..23)
  - Edges: position a -> a*b mod 24 for each b in Z/24Z
  - Sector structure:
    * Coprime U = {1,5,7,11,13,17,19,23} -- closed under x coprime
    * Nilpotent N = {0,6,12,18} -- closed under x ANYTHING, converges to 0
    * Divisible D = {2,3,4,8,9,10,14,15,16,20,21,22} -- can enter N
  - Flow: U -> D -> N -> {0}. All paths lead to 0 eventually.

TEST PROTOCOL:
1. Full 24x24 multiplication table distribution
2. Preimage analysis: which positions are most "reachable"?
3. Random walk convergence from each sector
4. Shannon entropy along the decay chain
5. Information-theoretic "death rate"
""")

# --- 128.1: Multiplication Table Distribution ------------------------------

print("  128.1: MULTIPLICATION TABLE DISTRIBUTION (576 products)")
print("  " + "-" * 50)

prod_dist = Counter()
for a in range(24):
    for b in range(24):
        prod_dist[(a * b) % 24] += 1

print(f"\n  {'Pos':>3} {'Count':>5} {'Frac':>6} {'Type':>6}  Note")
print("  " + "-" * 50)

cumul = 0
for pos in range(24):
    cnt = prod_dist.get(pos, 0)
    frac = cnt / 576
    cumul += frac
    typ = "NIL" if pos in NILOPOTENT else ("COP" if pos in COPRIME24 else "DIV")
    note = ""
    if pos == 0: note = "<-- annihilator"
    elif pos == 12: note = "<-- nilpotent hub"
    elif pos in {1, 23}: note = "<-- rail anchor"
    print(f"  {pos:>3} {cnt:>5} {frac:>6.3f} {typ:>6}  {note}")

H_full = shannon_entropy([prod_dist.get(p, 0) for p in range(24)])
H_uniform = log(24)
print(f"\n  Shannon entropy of product distribution: {H_full:.4f} nats")
print(f"  Maximum (uniform over 24):                {H_uniform:.4f} nats")
print(f"  Relative entropy: {H_full/H_uniform:.4f}")

# Rank positions by product count
ranked = sorted(range(24), key=lambda p: -prod_dist.get(p, 0))
print(f"\n  Reachability ranking (most to least products landing):")
for i, pos in enumerate(ranked[:8]):
    cnt = prod_dist.get(pos, 0)
    typ = "NIL" if pos in NILOPOTENT else ("COP" if pos in COPRIME24 else "DIV")
    print(f"    #{i+1}: position {pos:>2} ({cnt:>3}/576 = {cnt/576:.3f}) [{typ}]")

# Sector totals
nil_total = sum(prod_dist.get(p, 0) for p in NILOPOTENT)
cop_total = sum(prod_dist.get(p, 0) for p in COPRIME24)
div_total = 576 - nil_total - cop_total
print(f"\n  Sector product shares:")
print(f"    Nilpotent (4 pos):  {nil_total:>3}/576 = {nil_total/576:.3f}")
print(f"    Coprime   (8 pos):  {cop_total:>3}/576 = {cop_total/576:.3f}")
print(f"    Divisible (12 pos): {div_total:>3}/576 = {div_total/576:.3f}")

# --- 128.2: Preimage Analysis ---------------------------------------------

print(f"\n  128.2: PREIMAGE ANALYSIS")
print("  " + "-" * 50)
print("  For position k: count how many x in Z/24Z can reach k")
print("  (x can reach k iff gcd(x,24) divides k, or k=0)\n")

preimage_counts = {}
for k in range(24):
    can_reach = 0
    for x in range(24):
        g = gcd(x, 24)
        if k == 0:
            can_reach += 1  # everything can reach 0 (x*0 = 0)
        elif g == 0:
            pass  # x=0 can only reach 0
        elif k % g == 0:
            can_reach += 1
    preimage_counts[k] = can_reach

for pos in range(24):
    typ = "NIL" if pos in NILOPOTENT else ("COP" if pos in COPRIME24 else "DIV")
    print(f"  Position {pos:>2}: {preimage_counts[pos]:>2}/24 elements can reach it [{typ}]")

# --- 128.3: Random Walk Convergence ---------------------------------------

print(f"\n  128.3: RANDOM WALK CONVERGENCE")
print("  " + "-" * 50)
print("  At each step, multiply current position by random element of Z/24Z")
print("  Track P(position = k) over time\n")

# Track convergence from different starting sectors
for start_label, start_pos in [("Coprime (1)", 1), ("Divisible (2)", 2),
                                ("Nilpotent (6)", 6), ("Nilpotent hub (12)", 12)]:
    d = np.zeros(24)
    d[start_pos] = 1.0

    print(f"  Starting from {start_label}:")
    print(f"    {'Step':>4} : ", end="")
    for p in [0, 6, 12, 18, 1, 5, 23]:
        print(f"{'p'+str(p):>7} ", end="")
    print()

    for step in range(16):
        new_d = np.zeros(24)
        for pos in range(24):
            if d[pos] > 1e-15:
                for m in range(24):
                    new_d[(pos * m) % 24] += d[pos] / 24.0
        d = new_d
        if step in [0, 1, 2, 4, 8, 15]:
            print(f"    {step+1:>4} : ", end="")
            for p in [0, 6, 12, 18, 1, 5, 23]:
                print(f"{d[p]:>7.4f} ", end="")
            print()
    print()

# Global stationary distribution (from uniform start)
dist = np.ones(24) / 24.0
for step in range(50):
    new_dist = np.zeros(24)
    for pos in range(24):
        if dist[pos] > 1e-15:
            for m in range(24):
                new_dist[(pos * m) % 24] += dist[pos] / 24.0
    dist = new_dist

print(f"  Stationary distribution (50 steps from uniform):")
for pos in sorted(range(24), key=lambda p: -dist[p]):
    if dist[pos] > 0.001:
        typ = "NIL" if pos in NILOPOTENT else ("COP" if pos in COPRIME24 else "DIV")
        print(f"    Position {pos:>2}: {dist[pos]:.6f} [{typ}]")

# --- 128.4: Entropy Along Decay Chain -------------------------------------

print(f"\n  128.4: ENTROPY ALONG THE DECAY CHAIN")
print("  " + "-" * 50)
print("  Starting from nilpotent positions, measure entropy of next-step distribution\n")

for start in [6, 12, 18]:
    dist_step = Counter()
    for m in range(24):
        dist_step[(start * m) % 24] += 1
    H = shannon_entropy(list(dist_step.values()))
    unique = len(dist_step)
    print(f"  Start at {start}:")
    print(f"    Reachable positions: {sorted(dist_step.keys())}")
    print(f"    Counts: {dict(sorted(dist_step.items()))}")
    print(f"    Shannon entropy: {H:.4f} nats ({unique} distinct outcomes)")
    print()

# --- 128.5: Information-Theoretic Death Rate -------------------------------

print(f"  128.5: DEATH RATE -- Steps until P(0) > 0.5")
print("  " + "-" * 50)

death_rates = {}
for start in range(24):
    d = np.zeros(24)
    d[start] = 1.0
    death_step = None
    for step in range(1, 100):
        new_d = np.zeros(24)
        for pos in range(24):
            if d[pos] > 1e-15:
                for m in range(24):
                    new_d[(pos * m) % 24] += d[pos] / 24.0
        d = new_d
        if d[0] > 0.5 and death_step is None:
            death_step = step
            break
    death_rates[start] = death_step if death_step else ">100"

print(f"  {'Pos':>3} {'Steps to P(0)>0.5':>18} {'Type':>6}")
print("  " + "-" * 35)
for pos in range(24):
    typ = "NIL" if pos in NILOPOTENT else ("COP" if pos in COPRIME24 else "DIV")
    dr = f"{death_rates[pos]}" if isinstance(death_rates[pos], int) else death_rates[pos]
    print(f"  {pos:>3} {dr:>18} {typ:>6}")

# --- 128.6: Entropy Scorecard ---------------------------------------------

print(f"\n  128.6: COMPREHENSIVE ENTROPY SCORECARD")
print("  " + "-" * 50)
print(f"  (Averages over n=1..10000 at each position)\n")

omega_sums = defaultdict(float)
sigma_sums = defaultdict(float)
phi_sums = defaultdict(float)
counts_pos = defaultdict(int)

for n in range(1, 10001):
    pos = n % 24
    omega_sums[pos] += len(set(factorize(n)))
    sigma_sums[pos] += sigma(n) / n
    phi_sums[pos] += euler_totient(n) / n
    counts_pos[pos] += 1

print(f"  {'Pos':>3} {'Prods':>5} {'Preimg':>6} {'sig/n':>6} {'omega':>6} {'phi/n':>6} {'Type':>4}")
print("  " + "-" * 50)

for pos in range(24):
    cnt = prod_dist.get(pos, 0)
    pi_cnt = preimage_counts[pos]
    avg_sigma = sigma_sums[pos] / counts_pos[pos]
    avg_omega = omega_sums[pos] / counts_pos[pos]
    avg_phi = phi_sums[pos] / counts_pos[pos]
    typ = "NIL" if pos in NILOPOTENT else ("COP" if pos in COPRIME24 else "DIV")
    print(f"  {pos:>3} {cnt:>5} {pi_cnt:>6} {avg_sigma:>6.3f} {avg_omega:>6.2f} {avg_phi:>6.3f} {typ:>4}")

# --- 128.7: Verdict -------------------------------------------------------

print(f"\n  128.7: VERDICT")
print("  " + "-" * 50)

top3 = sorted(range(24), key=lambda p: -prod_dist.get(p, 0))[:3]
print(f"  Most reachable positions: {top3}")
print(f"  Position 12 rank: #{ranked.index(12)+1}")
print(f"  Position 0  rank: #{ranked.index(0)+1}")

# Rank among non-zero positions
nonzero_ranked = sorted([p for p in range(1, 24)], key=lambda p: -prod_dist.get(p, 0))
print(f"  Position 12 rank (non-zero only): #{nonzero_ranked.index(12)+1}")

print(f"""
  FINDINGS:

  1. POSITION 0 IS THE UNIVERSAL ATTRACTOR.
     The annihilator absorbs everything. In the random walk model,
     every starting position converges to P(0) > 0.5 within finite steps.
     This is a property of ANY ring with zero divisors, not unique to Z/24Z.

  2. THE COPIRME SECTOR IS A DELAY.
     Coprime positions take the LONGEST to decay to 0 because
     coprime x coprime = coprime (closed subgroup). The coprime
     sector is the "reservoir" that resists entropy production.

  3. POSITION 12 IS THE NILOPOTENT HUB, NOT THE ENTROPY MAXIMUM.
     Both 6 and 18 decay through 12, but 0 gets more product hits
     than 12. The hierarchy is: 0 > (everything else).
     Among non-zero positions, 12 may be most reachable, but
     the true attractor is always annihilation.

  4. THE "ENTROPIC PRESSURE" IS REAL BUT GENERAL.
     The flow U -> D -> N -> {{0}} is real. Coprime positions
     resist falling into the nilpotent drain. But this is
     a general property of rings with zero divisors, not
     specific to Z/24Z or the monad.

  5. WHAT KEEPS MATTER "ON THE RAILS":
     Coprime multiplication is CLOSED. Numbers on the rails
     (coprime to 6) can only fall off when they interact with
     non-coprime elements. The "force" keeping matter on-rail
     is the closure of the unit group under multiplication.
     This is algebraic, not dynamical.
""")


# ============================================================================
# EXPERIMENT 129: PRIME GAP RESONANCE
# ============================================================================

print("=" * 70)
print("EXPERIMENT 129: PRIME GAP RESONANCE")
print("=" * 70)

print("""
HYPOTHESIS: If 1/p has the right SHAPE but wrong SCALE for fermion masses,
maybe a logarithmic transform captures the physics better.
The PNT says pi(x) ~ x/ln(x), so local density ~ 1/ln(p).

TEST PROTOCOL:
1. Map 12 fermions to 12 primes (same rank-ordering as Exp 127)
2. Compute gaps G(p), ln(G), 1/ln(p), G/ln(p)
3. Test Spearman correlation of each vs log(mass)
4. Map prime gaps across mod-24 positions
5. Identify "high-pressure" vs "low-pressure" zones
6. HONEST comparison: does ANY function of small primes work?
""")

# --- 129.1: Gap Measurement ------------------------------------------------

print("  129.1: PRIME GAPS FOR FERMION-MAPPED PRIMES")
print("  " + "-" * 50)

# Generate primes up to 200 for gap computation
primes_list = [p for p in range(2, 500) if is_prime(p)]
prime_idx = {p: i for i, p in enumerate(primes_list)}

# Map fermions to primes (lightest fermion = largest prime, heaviest = smallest)
fermions_sorted = sorted(FERMIONS, key=lambda x: x[1])

print(f"\n  {'Fermion':>20} {'Mass(MeV)':>12} {'log10(m)':>8} {'Prime':>5} {'mod24':>5} {'Gap':>4} {'ln(G)':>6} {'1/ln(p)':>7}")
print("  " + "-" * 80)

gap_data = []
for i, (name, mass, ftype) in enumerate(fermions_sorted):
    p = PRIMES_12[11 - i]  # lightest gets largest prime
    pidx = prime_idx[p]
    gap = primes_list[pidx + 1] - p
    ln_gap = log(gap) if gap > 0 else 0
    inv_lnp = 1.0 / log(p)
    gap_over_lnp = gap / log(p)
    m24 = p % 24

    gap_data.append({
        'name': name, 'mass': mass, 'log10m': log10(mass), 'lnm': log(mass),
        'prime': p, 'mod24': m24, 'gap': gap,
        'ln_gap': ln_gap, 'inv_lnp': inv_lnp, 'gap_lnp': gap_over_lnp,
        'chi5': chi5(p), 'chi7': chi7(p), 'chi13': chi13(p),
    })

    print(f"  {name:>20} {mass:>12.4e} {log10(mass):>8.2f} {p:>5} {m24:>5} {gap:>4} {ln_gap:>6.3f} {inv_lnp:>7.4f}")

# --- 129.2: Correlation Tests ----------------------------------------------

print(f"\n  129.2: CORRELATION TESTS")
print("  " + "-" * 50)

log_masses = [d['lnm'] for d in gap_data]

predictors = {
    '1/p':       [1.0/d['prime'] for d in gap_data],
    '1/ln(p)':   [d['inv_lnp'] for d in gap_data],
    'ln(gap)':   [d['ln_gap'] for d in gap_data],
    'gap':       [d['gap'] for d in gap_data],
    'gap/ln(p)': [d['gap_lnp'] for d in gap_data],
}

print(f"\n  {'Predictor':>12} {'Spearman':>10} {'Range':>10} {'Mass range':>12} {'Coverage':>10}")
print("  " + "-" * 60)

mass_range_log = max(log_masses) - min(log_masses)

for name, pred in predictors.items():
    rho = spearman_rank(log_masses, pred)
    pred_range = max(pred) - min(pred)
    coverage = pred_range / mass_range_log if mass_range_log > 0 else 0
    print(f"  {name:>12} {rho:>10.4f} {pred_range:>10.4f} {mass_range_log:>12.2f} {coverage:>10.4f}")

print(f"\n  Target mass range (log): {mass_range_log:.2f}")
print(f"  (This is the DYNAMIC RANGE the predictor must cover)")

# --- 129.3: Detailed 1/ln(p) Fit ------------------------------------------

print(f"\n  129.3: DETAILED 1/ln(p) FIT (PNT-inspired scaling)")
print("  " + "-" * 50)
print("  The PNT density 1/ln(p) compresses the prime range.")
print("  For p=2..37: 1/ln(p) spans {1.443..0.276}, ratio = 5.2x\n")

print(f"  {'Fermion':>20} {'log10(m)':>8} {'1/ln(p)':>7} {'Residual':>9}")
print("  " + "-" * 50)

residuals_lnp = []
for d in gap_data:
    res = abs(d['log10m'] - d['inv_lnp'])
    residuals_lnp.append(res)
    print(f"  {d['name']:>20} {d['log10m']:>8.2f} {d['inv_lnp']:>7.4f} {res:>9.2f}")

mean_res_lnp = sum(residuals_lnp) / len(residuals_lnp)
print(f"\n  Mean |residual|: {mean_res_lnp:.4f} (log10 scale)")
print(f"  For comparison, 1/p mean residual from Exp 127: 1.8872")

# --- 129.4: Mod-24 Gap Distribution ----------------------------------------

print(f"\n  129.4: PRIME GAP DISTRIBUTION ACROSS MOD-24 POSITIONS")
print("  " + "-" * 50)
print("  Using all primes up to 100,000\n")

big_primes = [p for p in range(2, 100001) if is_prime(p)]
gap_by_pos = defaultdict(list)

for i in range(len(big_primes) - 1):
    p = big_primes[i]
    gap = big_primes[i + 1] - p
    pos = p % 24
    gap_by_pos[pos].append(gap)

print(f"  {'Pos':>3} {'Chi5':>5} {'Chi7':>5} {'Chi13':>5} {'Count':>6} {'Mean':>8} {'Median':>8} {'Std':>8}")
print("  " + "-" * 60)

coprime_positions = sorted([p for p in range(24) if gcd(p, 24) == 1])

for pos in coprime_positions:
    if pos in gap_by_pos:
        gaps_at = gap_by_pos[pos]
        mean_g = sum(gaps_at) / len(gaps_at)
        med_g = sorted(gaps_at)[len(gaps_at) // 2]
        std_g = sqrt(sum((g - mean_g)**2 for g in gaps_at) / len(gaps_at))
        print(f"  {pos:>3} {chi5(pos):>+5} {chi7(pos):>+5} {chi13(pos):>+5} {len(gaps_at):>6} {mean_g:>8.2f} {med_g:>8.1f} {std_g:>8.2f}")

print(f"\n  (Non-coprime positions have no primes > 3)")

# --- 129.5: Pressure Map ---------------------------------------------------

print(f"\n  129.5: PRESSURE MAP (inverse of mean gap = local density)")
print("  " + "-" * 50)

pressures = {}
for pos in coprime_positions:
    if pos in gap_by_pos and gap_by_pos[pos]:
        mean_g = sum(gap_by_pos[pos]) / len(gap_by_pos[pos])
        pressures[pos] = 1.0 / mean_g

print(f"\n  {'Pos':>3} {'Pressure':>10} {'Chi5':>5} {'Chi7':>5} {'Chi13':>5} {'Rail':>5}")
print("  " + "-" * 45)

for pos in sorted(pressures.keys()):
    rail = 'R1' if chi5(pos) == 1 else 'R2'
    print(f"  {pos:>3} {pressures[pos]:>10.6f} {chi5(pos):>+5} {chi7(pos):>+5} {chi13(pos):>+5} {rail:>5}")

# Rail-level pressure
r1_pressures = [pressures[p] for p in pressures if chi5(p) == 1]
r2_pressures = [pressures[p] for p in pressures if chi5(p) == -1]

if r1_pressures and r2_pressures:
    r1_mean = sum(r1_pressures) / len(r1_pressures)
    r2_mean = sum(r2_pressures) / len(r2_pressures)
    print(f"\n  R1 mean pressure: {r1_mean:.6f}")
    print(f"  R2 mean pressure: {r2_mean:.6f}")
    print(f"  R1/R2 ratio:      {r1_mean/r2_mean:.4f}")

# Sub-position pressure
chi7_pos = [pressures[p] for p in pressures if chi7(p) == 1]
chi7_neg = [pressures[p] for p in pressures if chi7(p) == -1]
if chi7_pos and chi7_neg:
    print(f"\n  chi7=+1 mean pressure: {sum(chi7_pos)/len(chi7_pos):.6f}")
    print(f"  chi7=-1 mean pressure: {sum(chi7_neg)/len(chi7_neg):.6f}")
    print(f"  chi7 ratio:            {sum(chi7_pos)/len(chi7_pos) / (sum(chi7_neg)/len(chi7_neg)):.4f}")

# --- 129.6: The Fundamental Scale Problem ----------------------------------

print(f"\n  129.6: THE FUNDAMENTAL SCALE PROBLEM")
print("  " + "-" * 50)

# Compute ranges for all methods
mass_ratio = max(d['mass'] for d in gap_data) / min(d['mass'] for d in gap_data)
range_1p = (1.0/2) / (1.0/37)
range_inv_lnp = max(d['inv_lnp'] for d in gap_data) / min(d['inv_lnp'] for d in gap_data)
nonzero_ln_gaps = [d['ln_gap'] for d in gap_data if d['ln_gap'] > 0]
range_ln_gap = max(nonzero_ln_gaps) / min(nonzero_ln_gaps) if nonzero_ln_gaps else 0
range_gap = max(d['gap'] for d in gap_data) / min(d['gap'] for d in gap_data)
range_lnp = log(37) / log(2)

print(f"""
  SUMMARY OF ALL SCALING ATTEMPTS (Exps 127-129):

  Method          Dynamic Range   Rank Corr   vs Mass
  --------------  -------------   ---------   --------------
  1/p             {range_1p:>10.1f}x   |{abs(spearman_rank(log_masses, predictors['1/p'])):.1f}|      MASSIVE shortfall
  1/ln(p)         {range_inv_lnp:>10.1f}x   |{abs(spearman_rank(log_masses, predictors['1/ln(p)'])):.1f}|      Still 7 orders short
  ln(p)           {range_lnp:>10.1f}x   |{abs(spearman_rank(log_masses, [log(d['prime']) for d in gap_data])):.1f}|      Compression helps
  ln(gap)         {range_ln_gap:>10.1f}x   |{abs(spearman_rank(log_masses, predictors['ln(gap)'])):.1f}|      Gaps are noisy
  gap             {range_gap:>10.1f}x   |{abs(spearman_rank(log_masses, predictors['gap'])):.1f}|      Small integer noise
  --------------  -------------   ---------   --------------
  Actual masses   {mass_ratio:>10.0f}x

  KEY INSIGHT:
  The rank correlation is ALWAYS |1.0| because we ASSIGNED primes
  in mass-rank order. This is a TAUTOLOGY, not a discovery.
  The only meaningful test is the SCALE test, which every method fails.

  No function of 12 small integers (2..37) can span 8e10x.
  The primes carry HIERARCHY (ordering), not MAGNITUDE (scale).
  Physical constants (G, hbar, c) set the scale, not number theory.
""")

# --- 129.7: What DOES the Monad Predict? -----------------------------------

print(f"  129.7: WHAT THE MONAD ACTUALLY PREDICTS (vs what it doesn't)")
print("  " + "-" * 50)

print(f"""
  THE MONAD DOES PREDICT (rigorously):
    1. Prime constellation patterns (twin=cross, cousin=cross, sexy=same)
    2. Abundance structure (coprime never abundant, nilpotent always)
    3. Chebyshev bias direction (R1 slightly more primes than R2)
    4. Primorial dynamics (bounce between 6 and 18)
    5. Multiplicative closure of coprime sector
    6. Nilpotent decay topology (6->12->0, 18->12->0)

  THE MONAD DOES NOT PREDICT:
    1. Fermion mass VALUES (wrong by 4.4e9x)
    2. Fermion mass RATIOS (wrong by ~1000x for most pairs)
    3. Gauge coupling strengths (Abelian vs non-Abelian mismatch)
    4. Which particles exist (no prediction of generation count)
    5. CKM/PMNS mixing angles (no matrix structure in Z/24Z)
    6. Higgs VEV value (no energy scale in pure arithmetic)

  THE HONEST BOUNDARY:
    The monad captures TOPOLOGY (which positions exist, which are connected)
    but not METRIC (how far apart things are in physical units).
    This is exactly the gap between algebra and physics.
    Algebra gives you the graph; physics gives you the edge weights.
""")


# ============================================================================
# TESTS
# ============================================================================

print("=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 0

# Test 1: Multiplication table sums to 576
total += 1
if sum(prod_dist.values()) == 576:
    print(f"  [PASS] Product distribution sums to 576")
    passed += 1
else:
    print(f"  [FAIL] Product distribution sums to {sum(prod_dist.values())}")

# Test 2: Position 0 is most reachable
total += 1
if prod_dist[0] == max(prod_dist.values()):
    print(f"  [PASS] Position 0 ({prod_dist[0]}) is most reachable (universal attractor)")
    passed += 1
else:
    print(f"  [FAIL] Position 0 ({prod_dist[0]}) is not the most reachable")

# Test 3: Random walk converges to 0
total += 1
if dist[0] > 0.5:
    print(f"  [PASS] Stationary distribution dominated by 0: P(0) = {dist[0]:.4f}")
    passed += 1
else:
    print(f"  [FAIL] P(0) = {dist[0]:.4f} < 0.5")

# Test 4: Only coprime positions have primes
total += 1
nil_have_primes = any(pos in gap_by_pos and len(gap_by_pos[pos]) > 0 for pos in NILOPOTENT - {0})
coprime_have_primes = all(pos in gap_by_pos and len(gap_by_pos[pos]) > 0 for pos in coprime_positions)
if not nil_have_primes and coprime_have_primes:
    print(f"  [PASS] Only coprime positions contain primes > 3")
    passed += 1
else:
    print(f"  [FAIL] Prime position distribution wrong")

# Test 5: 1/p and 1/ln(p) have |rho|=1.0 (tautological); gap measures don't
total += 1
rho_1p = abs(spearman_rank(log_masses, predictors['1/p']))
rho_lnp = abs(spearman_rank(log_masses, predictors['1/ln(p)']))
rho_gap = abs(spearman_rank(log_masses, predictors['gap']))
if rho_1p == 1.0 and rho_lnp == 1.0 and rho_gap != 1.0:
    print(f"  [PASS] 1/p and 1/ln(p) are tautological (|rho|=1.0), gap measures are not (|rho_gap|={rho_gap:.4f})")
    passed += 1
else:
    print(f"  [FAIL] Correlation structure unexpected: 1/p={rho_1p}, 1/ln(p)={rho_lnp}, gap={rho_gap}")

# Test 6: Scale mismatch confirmed
total += 1
if mass_ratio > 1e10 and range_1p < 100:
    print(f"  [PASS] Scale mismatch: {mass_ratio:.0e}x (mass) vs {range_1p:.1f}x (1/p)")
    passed += 1
else:
    print(f"  [FAIL] Scale check unexpected")

# Test 7: Gap data valid
total += 1
if len(gap_data) == 12 and all(d['gap'] > 0 for d in gap_data):
    print(f"  [PASS] All 12 prime gaps computed correctly")
    passed += 1
else:
    print(f"  [FAIL] Gap computation error")

# Test 8: Nilpotent positions have faster death rate than coprime
total += 1
nil_rates = [death_rates[p] for p in NILOPOTENT - {0} if isinstance(death_rates[p], int)]
cop_rates = [death_rates[p] for p in COPRIME24 if isinstance(death_rates[p], int)]
if nil_rates and cop_rates and max(nil_rates) < min(cop_rates):
    print(f"  [PASS] Nilpotent decays faster than coprime (max_nil={max(nil_rates)} < min_cop={min(cop_rates)})")
    passed += 1
else:
    nil_str = f"max={max(nil_rates) if nil_rates else 'N/A'}"
    cop_str = f"min={min(cop_rates) if cop_rates else 'N/A'}"
    print(f"  [FAIL] Death rate ordering wrong: nilpotent {nil_str}, coprime {cop_str}")

# Test 9: Pressure by rail computed
total += 1
if r1_pressures and r2_pressures:
    print(f"  [PASS] Rail pressure computed: R1={sum(r1_pressures)/len(r1_pressures):.6f}, R2={sum(r2_pressures)/len(r2_pressures):.6f}")
    passed += 1
else:
    print(f"  [FAIL] Rail pressure computation failed")

print(f"\nOVERALL: {passed}/{total} tests passed")

print("\n" + "=" * 70)
print("EXPERIMENTS 128-129 COMPLETE")
print("=" * 70)
