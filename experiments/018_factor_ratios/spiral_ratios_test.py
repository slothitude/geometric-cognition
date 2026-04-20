"""
Experiment 018g: The 12x30 Spiral — Angular Ratios on the Manifold
==================================================================
The 12 positions (2 rails x 6 sub-positions) map to a 12-hour circle,
each 30 degrees apart. Every prime creates a spiral on this circle.

The angular step of prime p = sp_p x 30 degrees per walk-step.
The sp composition rules ARE wave interference:
  R2xR2: sp = (a+b) mod 6  — constructive interference
  R1xR1: sp = (-a-b) mod 6 — destructive interference (phase flip)
  R1xR2: sp = (a-b) mod 6  — heterodyne (difference frequency)

The ratios between angular velocities are musical intervals.
"""

import numpy as np
from math import gcd, pi

def sieve(N):
    is_prime = np.ones(N, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return is_prime

def get_rail(n):
    if n % 2 == 0 or n % 3 == 0: return 0
    r = n % 6
    return 1 if r == 1 else (-1 if r == 5 else 0)

def rail_k(n):
    rail = get_rail(n)
    if rail == -1: return (n + 1) // 6
    elif rail == +1: return (n - 1) // 6
    return 0

def to_pos12(n):
    """Map n to position 0-11 on the 12-hour circle.
    0-5 = R1(sp=0..5), 6-11 = R2(sp=0..5)"""
    rail = get_rail(n)
    if rail == 0: return -1
    k = rail_k(n)
    sp = k % 6
    if rail == -1: return sp        # R1: positions 0-5
    else: return sp + 6             # R2: positions 6-11

def pos12_to_angle(pos):
    """Position 0-11 to angle in degrees."""
    return pos * 30.0

N_MAX = 500_000

print("=" * 70)
print("  EXPERIMENT 018g: THE 12x30 SPIRAL — ANGULAR RATIOS")
print("=" * 70)
print()

is_prime_arr = sieve(N_MAX + 100)

# ====================================================================
#  TEST 1: PRIME ANGULAR FREQUENCIES
# ====================================================================
print("=" * 70)
print("  TEST 1: PRIME ANGULAR FREQUENCIES")
print("=" * 70)
print()
print("  Each prime p has angular step = sp_p x 30 deg per walk-step.")
print("  sp_p = k_p mod 6 = its angular velocity class.")
print()
print(f"  {'prime':>5} {'k':>4} {'sp':>3} {'angle/step':>11} {'period':>7} {'musical':>12} {'pos12':>5} {'deg':>5}")
print("  " + "-" * 60)

rail_primes = [p for p in range(5, 150) if is_prime_arr[p] and get_rail(p) != 0]

for p in rail_primes[:30]:
    k = rail_k(p)
    sp = k % 6
    angle_step = sp * 30
    period = 6 // gcd(sp, 6) if sp > 0 else 1
    pos = to_pos12(p)
    deg = pos12_to_angle(pos)

    # Musical interval names
    ratio_str = f"{sp}:6"
    if sp == 0: interval = "stationary"
    elif sp == 1: interval = "1/6 (minor 3rd up)"
    elif sp == 2: interval = "1/3 (major 3rd)"
    elif sp == 3: interval = "1/2 (tritone)"
    elif sp == 4: interval = "2/3 (major 3rd dn)"
    elif sp == 5: interval = "5/6 (minor 3rd dn)"
    else: interval = "?"

    print(f"  {p:>5} {k:>4} {sp:>3} {angle_step:>9}deg {period:>7} {interval:>18} {pos:>5} {deg:>5.0f}deg")

print()

# ====================================================================
#  TEST 2: THE 6 SPIRAL CLASSES
# ====================================================================
print("=" * 70)
print("  TEST 2: THE 6 SPIRAL CLASSES (sp = 0..5)")
print("=" * 70)
print()

for sp_class in range(6):
    primes_in_class = [p for p in rail_primes if rail_k(p) % 6 == sp_class]
    period = 6 // gcd(sp_class, 6) if sp_class > 0 else 1
    direction = "CW" if sp_class <= 3 else "CCW"
    if sp_class == 0: direction = "---"
    angle_per_step = sp_class * 30

    print(f"  sp={sp_class}: {len(primes_in_class)} primes, "
          f"angle/step={angle_per_step}deg, period={period} steps, "
          f"direction={direction}")
    print(f"    First 10: {primes_in_class[:10]}")
    print()

# ====================================================================
#  TEST 3: SPIRAL VISUALIZATION — WALKING TRAJECTORIES
# ====================================================================
print("=" * 70)
print("  TEST 3: SPIRAL TRAJECTORIES ON THE 12-HOUR CIRCLE")
print("=" * 70)
print()

spf = np.zeros(N_MAX + 100, dtype=np.int32)
for i in range(2, N_MAX + 100):
    if is_prime_arr[i]:
        spf[i::i] = np.where(spf[i::i] == 0, i, spf[i::i])

def factorize(n):
    factors = []
    while n > 1:
        factors.append(spf[n])
        n //= spf[n]
    return factors

# Walk along prime p's chain and record angular positions
for p in [5, 7, 11, 13, 17, 19, 23]:
    k = rail_k(p)
    sp_p = k % 6
    pos = to_pos12(p)

    trajectory = [pos]
    angles = [pos * 30.0]

    for step in range(12):
        k_new = k + p
        n_r1 = 6 * k_new - 1
        n_r2 = 6 * k_new + 1
        for candidate in [n_r1, n_r2]:
            if candidate % p == 0 and candidate <= N_MAX and candidate >= p:
                pos_new = to_pos12(candidate)
                trajectory.append(pos_new)
                angles.append(pos_new * 30.0)
                k = k_new
                break

    print(f"  p={p:>2} (sp={sp_p}): angular trajectory (first 13 positions):")
    pos_str = " -> ".join(f"{t:>2}" for t in trajectory[:13])
    ang_str = " -> ".join(f"{a:>5.0f}" for a in angles[:13])
    print(f"    positions: {pos_str}")
    print(f"    angles:    {ang_str}")

    # Compute angular differences (the "step" in 12-space)
    diffs = []
    for i in range(1, len(trajectory)):
        d = trajectory[i] - trajectory[i-1]
        # Normalize to [-6, +6]
        if d > 6: d -= 12
        if d < -6: d += 12
        diffs.append(d)
    print(f"    steps:     {diffs[:12]}")
    print()

# ====================================================================
#  TEST 4: ANGULAR RATIOS BETWEEN PRIMES — THE MUSICAL STRUCTURE
# ====================================================================
print("=" * 70)
print("  TEST 4: ANGULAR RATIOS — THE MUSICAL STRUCTURE")
print("=" * 70)
print()
print("  The angular step of each prime in 30-degree units IS its")
print("  frequency ratio relative to the fundamental (1 full revolution).")
print()
print("  Ratio of angular steps sp_a : sp_b gives the frequency ratio")
print("  between two prime spirals.")
print()

# Build ratio table for first few primes
small_primes = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
print(f"  Angular step ratio table (sp_a / sp_b):")
print(f"  {'':>5}", end="")
for p in small_primes:
    print(f" {p:>5}", end="")
print()
print("  " + "-" * (5 + 6 * len(small_primes)))

for pa in small_primes:
    sp_a = rail_k(pa) % 6
    print(f"  {pa:>5}", end="")
    for pb in small_primes:
        sp_b = rail_k(pb) % 6
        if sp_b == 0:
            ratio_str = "  ---"
        else:
            g = gcd(sp_a, sp_b)
            ratio_str = f"  {sp_a//g}:{sp_b//g}"
        print(f"{ratio_str:>6}", end="")
    print()

print()

# ====================================================================
#  TEST 5: INTERFERENCE — COMPOSITION AS WAVE MIXING
# ====================================================================
print("=" * 70)
print("  TEST 5: COMPOSITION = WAVE INTERFERENCE")
print("=" * 70)
print()
print("  The sp composition rules are EXACTLY wave interference:")
print()
print("  R2 x R2: sp_N = (a + b) mod 6   = CONSTRUCTIVE (frequencies ADD)")
print("  R1 x R1: sp_N = (-a - b) mod 6  = DESTRUCTIVE (phase INVERTED)")
print("  R1 x R2: sp_N = (a - b) mod 6   = HETERODYNE (DIFFERENCE freq)")
print()
print("  In angle space (multiplying by 30 deg):")
print("  R2 x R2: theta_N = (theta_a + theta_b) mod 180deg  [constructive]")
print("  R1 x R1: theta_N = -(theta_a + theta_b) mod 180deg [destructive]")
print("  R1 x R2: theta_N = (theta_a - theta_b) mod 180deg  [heterodyne]")
print()

# Verify with examples
print("  Examples:")
examples = [
    (5, 11, "R1xR1"),   # sp 1,2 -> R2 sp=(-1-2)%6=3
    (5, 7, "R1xR2"),    # sp 1,1 -> R1 sp=(1-1)%6=0
    (7, 13, "R2xR2"),   # sp 1,2 -> R2 sp=(1+2)%6=3
    (11, 17, "R1xR1"),  # sp 2,3 -> R2 sp=(-2-3)%6=1
    (13, 19, "R2xR2"),  # sp 2,3 -> R2 sp=(2+3)%6=5
    (5, 13, "R1xR2"),   # sp 1,2 -> R1 sp=(1-2)%6=5
]

for p1, p2, comp_type in examples:
    n = p1 * p2
    sp1 = rail_k(p1) % 6
    sp2 = rail_k(p2) % 6
    r1 = get_rail(p1)
    r2 = get_rail(p2)
    pos_n = to_pos12(n)
    sp_n = pos_n % 6 if pos_n < 6 else pos_n - 6

    if comp_type == "R1xR1":
        expected = (-sp1 - sp2) % 6
        intf = "destructive"
    elif comp_type == "R2xR2":
        expected = (sp1 + sp2) % 6
        intf = "constructive"
    else:
        if r1 == -1:
            expected = (sp1 - sp2) % 6
        else:
            expected = (sp2 - sp1) % 6
        intf = "heterodyne"

    angle1 = sp1 * 30
    angle2 = sp2 * 30
    angle_n = expected * 30
    pos_n_actual = to_pos12(n)
    angle_actual = pos12_to_angle(pos_n_actual)

    print(f"  {p1:>2}(sp={sp1},{angle1}deg) x {p2:>2}(sp={sp2},{angle2}deg) "
          f"= {n:>4} [{comp_type}, {intf}]")
    print(f"    Expected: sp={expected}, angle={angle_n}deg | "
          f"Actual: pos={pos_n_actual}, angle={angle_actual}deg")

print()

# ====================================================================
#  TEST 6: SPIRAL RESONANCE — WHERE CHAINS INTERSECT
# ====================================================================
print("=" * 70)
print("  TEST 6: SPIRAL RESONANCE — CHAIN INTERSECTION ANGLES")
print("=" * 70)
print()
print("  At a composite N = p x q, two spirals intersect.")
print("  The angular relationship between them determines the 'harmony'.")
print()

# For each semiprime, compute the angular ratio of its factors
print(f"  {'N':>6} {'p1':>3} {'p2':>3} {'sp1':>3} {'sp2':>3} {'ratio':>7} "
      f"{'N_pos':>5} {'N_deg':>6} {'type':>7} {'harmonic':>10}")
print("  " + "-" * 65)

harmonic_names = {
    (1, 1): "unison", (1, 2): "octave", (2, 1): "octave",
    (1, 3): "12th", (3, 1): "12th", (2, 3): "5th", (3, 2): "5th",
    (1, 4): "15th", (4, 1): "15th", (3, 4): "4th", (4, 3): "4th",
    (1, 5): "M7", (5, 1): "M7", (2, 5): "M3", (5, 2): "M3",
    (3, 5): "M6", (5, 3): "M6", (4, 5): "m2", (5, 4): "m2",
    (0, 1): "root", (1, 0): "root", (0, 0): "unison",
}

count = 0
for n in range(25, 1000):
    if get_rail(n) == 0 or is_prime_arr[n]: continue
    factors = factorize(n)
    if len(factors) != 2: continue
    unique = set(factors)
    if len(unique) != 2: continue
    p1, p2 = sorted(factors)
    r1, r2 = get_rail(p1), get_rail(p2)
    if r1 == 0 or r2 == 0: continue

    sp1 = rail_k(p1) % 6
    sp2 = rail_k(p2) % 6
    g = gcd(sp1, sp2) if sp1 > 0 and sp2 > 0 else max(sp1, sp2)
    if g == 0: g = 1
    ratio = (sp1 // g, sp2 // g) if g > 0 else (0, 0)
    if ratio == (0, 0): ratio = (0, 0)
    ratio_str = f"{sp1}:{sp2}"

    pos_n = to_pos12(n)
    deg_n = pos12_to_angle(pos_n)

    if r1 == r2:
        if r1 == -1:
            comp_type = "R1xR1"
        else:
            comp_type = "R2xR2"
    else:
        comp_type = "R1xR2"

    harmonic = harmonic_names.get(tuple(sorted(ratio)), f"{ratio[0]}:{ratio[1]}")

    print(f"  {n:>6} {p1:>3} {p2:>3} {sp1:>3} {sp2:>3} {ratio_str:>7} "
          f"{pos_n:>5} {deg_n:>5.0f}deg {comp_type:>7} {harmonic:>10}")
    count += 1
    if count >= 25: break

print()

# ====================================================================
#  TEST 7: THE 30-DEGREE GRID — FULL ANGULAR MAP
# ====================================================================
print("=" * 70)
print("  TEST 7: THE 30-DEGREE GRID — FULL ANGULAR MAP")
print("=" * 70)
print()
print("  Mapping the first primes onto the 12-position, 30-degree circle:")
print()

print("  Position  Rail  SP  Angle  Primes at this position (first 8)")
print("  " + "-" * 65)

for pos in range(12):
    rail = -1 if pos < 6 else +1
    sp = pos % 6
    angle = pos * 30
    rail_str = "R1" if rail == -1 else "R2"

    primes_at_pos = []
    for p in rail_primes:
        if to_pos12(p) == pos:
            primes_at_pos.append(p)
        if len(primes_at_pos) >= 8:
            break

    print(f"  {pos:>8} {rail_str:>4} {sp:>3} {angle:>4}deg  {primes_at_pos}")

print()

# ====================================================================
#  TEST 8: SPIRAL CLOSURE — PERIODS AND RESONANCES
# ====================================================================
print("=" * 70)
print("  TEST 8: SPIRAL CLOSURE AND RESONANCE PERIODS")
print("=" * 70)
print()
print("  How many walk-steps until a prime's spiral returns to its")
print("  starting position on the 12-hour circle?")
print()
print("  Period in 12-space = lcm(period_in_sp, period_in_rail)")
print("  sp period = 6/gcd(sp, 6)")
print("  rail period: for R1 prime walking, products alternate R1/R2/R1/R2...")
print("    Actually need to think about this more carefully.")
print()

# Empirically measure the period
print(f"  {'prime':>5} {'sp':>3} {'sp_per':>6} {'12-period':>9} {'total_angle':>12} {'revolutions':>11}")
print("  " + "-" * 55)

for p in rail_primes[:20]:
    k = rail_k(p)
    start_pos = to_pos12(p)
    sp_p = k % 6
    sp_period = 6 // gcd(sp_p, 6) if sp_p > 0 else 1

    # Walk until we return to start_pos
    pos = start_pos
    period_12 = 0
    for step in range(100):
        k_new = k + p
        n_r1 = 6 * k_new - 1
        n_r2 = 6 * k_new + 1
        for candidate in [n_r1, n_r2]:
            if candidate % p == 0 and candidate <= N_MAX:
                pos = to_pos12(candidate)
                k = k_new
                break
        period_12 += 1
        if pos == start_pos:
            break

    total_angle = period_12 * sp_p * 30
    revolutions = total_angle / 360.0

    print(f"  {p:>5} {sp_p:>3} {sp_period:>6} {period_12:>9} {total_angle:>10}deg {revolutions:>10.1f}x")

print()

# ====================================================================
#  TEST 9: ANGULAR DISTRIBUTION OF PRIMES
# ====================================================================
print("=" * 70)
print("  TEST 9: ANGULAR DISTRIBUTION OF PRIMES")
print("=" * 70)
print()

# Count primes at each angular position
prime_counts = np.zeros(12, dtype=int)
for p in rail_primes:
    pos = to_pos12(p)
    if 0 <= pos < 12:
        prime_counts[pos] += 1

total_primes = prime_counts.sum()
print(f"  Distribution of {total_primes} primes across 12 angular positions:")
print()

for pos in range(12):
    rail_str = "R1" if pos < 6 else "R2"
    sp = pos % 6
    angle = pos * 30
    bar = "#" * int(50 * prime_counts[pos] / max(prime_counts))
    print(f"  pos {pos:>2} ({rail_str},sp={sp}) {angle:>3}deg: "
          f"{prime_counts[pos]:>4} {bar}")

print()

# Chi-squared test for uniformity
expected = total_primes / 12
chi2 = np.sum((prime_counts - expected)**2 / expected)
print(f"  Expected per position: {expected:.1f}")
print(f"  Chi-squared: {chi2:.2f} (df=11, critical at 0.05: 19.68)")
print(f"  Uniform distribution: {'YES' if chi2 < 19.68 else 'NO'}")
print()

# ====================================================================
#  TEST 10: THE GOLDEN RATIO IN THE SPIRAL
# ====================================================================
print("=" * 70)
print("  TEST 10: RATIOS IN COMPOSITE ANGULAR POSITIONS")
print("=" * 70)
print()
print("  When two spirals (p, q) intersect at N = p x q,")
print("  the angular position of N relative to p and q reveals")
print("  the interference pattern.")
print()

# For each composition type, map the angular relationship
print("  R2xR2 (constructive): angle_N = (angle_p + angle_q) mod 180 + 180")
print("  R1xR1 (destructive):  angle_N = -(angle_p + angle_q) mod 180 + 180")
print("  R1xR2 (heterodyne):   angle_N = (angle_p - angle_q) mod 180")
print()

# Verify the angular composition rules
correct_constructive = 0
correct_destructive = 0
correct_heterodyne = 0
total_constructive = 0
total_destructive = 0
total_heterodyne = 0

for n in range(25, N_MAX + 1):
    if get_rail(n) == 0 or is_prime_arr[n]: continue
    factors = factorize(n)
    if len(factors) != 2: continue
    unique = set(factors)
    if len(unique) != 2: continue
    p1, p2 = sorted(factors)
    r1, r2 = get_rail(p1), get_rail(p2)
    if r1 == 0 or r2 == 0: continue

    sp1 = rail_k(p1) % 6
    sp2 = rail_k(p2) % 6
    pos_n = to_pos12(n)
    sp_n = pos_n % 6 if pos_n < 6 else pos_n - 6
    rail_n = get_rail(n)

    if r1 == -1 and r2 == -1:  # R1xR1 -> R2 (destructive)
        expected_sp = (-sp1 - sp2) % 6
        expected_rail = +1
        if sp_n == expected_sp and rail_n == expected_rail:
            correct_destructive += 1
        total_destructive += 1
    elif r1 == +1 and r2 == +1:  # R2xR2 -> R2 (constructive)
        expected_sp = (sp1 + sp2) % 6
        expected_rail = +1
        if sp_n == expected_sp and rail_n == expected_rail:
            correct_constructive += 1
        total_constructive += 1
    else:  # R1xR2 -> R1 (heterodyne)
        if r1 == -1:
            expected_sp = (sp1 - sp2) % 6
        else:
            expected_sp = (sp2 - sp1) % 6
        expected_rail = -1
        if sp_n == expected_sp and rail_n == expected_rail:
            correct_heterodyne += 1
        total_heterodyne += 1

print(f"  Constructive (R2xR2): {correct_constructive}/{total_constructive} "
      f"({100*correct_constructive/max(total_constructive,1):.1f}%)")
print(f"  Destructive  (R1xR1): {correct_destructive}/{total_destructive} "
      f"({100*correct_destructive/max(total_destructive,1):.1f}%)")
print(f"  Heterodyne  (R1xR2): {correct_heterodyne}/{total_heterodyne} "
      f"({100*correct_heterodyne/max(total_heterodyne,1):.1f}%)")
print()

# ====================================================================
#  TEST 11: PHASE ANGLE OF COMPOSITES
# ====================================================================
print("=" * 70)
print("  TEST 11: PHASE ANGLE HISTOGRAM OF COMPOSITES")
print("=" * 70)
print()

# Histogram of composite angular positions
comp_angles = np.zeros(12, dtype=int)
prime_angles = np.zeros(12, dtype=int)

for n in range(5, N_MAX + 1):
    if get_rail(n) == 0: continue
    pos = to_pos12(n)
    if pos < 0 or pos >= 12: continue
    if is_prime_arr[n]:
        prime_angles[pos] += 1
    else:
        comp_angles[pos] += 1

print(f"  {'pos':>3} {'angle':>5} {'primes':>7} {'composites':>10} {'density':>8}")
print("  " + "-" * 40)

for pos in range(12):
    total = prime_angles[pos] + comp_angles[pos]
    density = prime_angles[pos] / total * 100 if total > 0 else 0
    angle = pos * 30
    print(f"  {pos:>3} {angle:>4}deg {prime_angles[pos]:>7} {comp_angles[pos]:>10} "
          f"{density:>7.1f}%")

print()

# ====================================================================
#  TEST 12: THE GOLDEN ANGLE AND SPIRAL RATIOS
# ====================================================================
print("=" * 70)
print("  TEST 12: SPIRAL STEP RATIOS AND GOLDEN ANGLE")
print("=" * 70)
print()
print("  The angular step ratios between consecutive primes reveal")
print("  the underlying harmonic structure.")
print()

# For consecutive primes, compute the angular step ratio
print("  Consecutive prime angular steps (sp values):")
print(f"  {'prime':>5} {'sp':>3} {'angle':>5} {'ratio to prev':>14}")
print("  " + "-" * 35)

prev_sp = None
for p in rail_primes[:20]:
    sp = rail_k(p) % 6
    angle = sp * 30

    if prev_sp is not None and prev_sp > 0 and sp > 0:
        g = gcd(prev_sp, sp)
        ratio_str = f"{prev_sp//g}:{sp//g}"
    elif prev_sp is not None:
        ratio_str = f"{prev_sp}:{sp}"
    else:
        ratio_str = "---"

    print(f"  {p:>5} {sp:>3} {angle:>4}deg {ratio_str:>14}")
    prev_sp = sp

print()

# The key ratios that appear
print("  Frequency of sp values among rail primes up to 10000:")
sp_counts = np.zeros(6, dtype=int)
for p in range(5, 10001):
    if is_prime_arr[p] and get_rail(p) != 0:
        sp_counts[rail_k(p) % 6] += 1

total = sp_counts.sum()
for sp in range(6):
    angle = sp * 30
    pct = 100 * sp_counts[sp] / total
    bar = "#" * int(pct * 2)
    print(f"    sp={sp} ({angle:>3}deg): {sp_counts[sp]:>5} primes ({pct:>5.1f}%) {bar}")

print()

# ====================================================================
#  SUMMARY
# ====================================================================
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print("  THE 12 x 30 SPIRAL:")
print("  - 12 positions on a circle, 30 degrees apart")
print("  - 2 rails (R1/R2) x 6 sub-positions = clock face")
print("  - Every prime creates a spiral with angular step = sp x 30 deg")
print()
print("  THE WAVE INTERFERENCE PATTERN:")
print("  - R2 x R2: CONSTRUCTIVE — angles ADD (sp_a + sp_b mod 6)")
print("  - R1 x R1: DESTRUCTIVE — angles INVERT (-sp_a - sp_b mod 6)")
print("  - R1 x R2: HETERODYNE — angles DIFFERENCE (sp_a - sp_b mod 6)")
print()
print("  THE MUSICAL RATIOS:")
print("  - sp=0: stationary (0 deg)")
print("  - sp=1: 30 deg/step = 1:6 ratio = minor third")
print("  - sp=2: 60 deg/step = 1:3 ratio = major third")
print("  - sp=3: 90 deg/step = 1:2 ratio = tritone")
print("  - sp=4: 120 deg/step = 2:3 ratio = perfect fifth")
print("  - sp=5: 150 deg/step = 5:6 ratio = minor third (reversed)")
print()
print("  The 12-position circle is the chromatic scale.")
print("  The 6 sp values are the whole-tone scale.")
print("  The 2 rails are the two whole-tone scales that make a chromatic.")
print()
print("  COMPOSITION IS WAVE INTERFERENCE ON THIS CIRCLE.")
print("  FACTORIZATION IS FINDING WHICH WAVES INTERFERED TO PRODUCE N.")
print()
print("Done.")
