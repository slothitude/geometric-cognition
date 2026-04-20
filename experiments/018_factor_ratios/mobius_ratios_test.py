"""
Experiment 018h: Möbius Ratios in the 12-Rail Monad
====================================================
The Z2 sign rule (R1xR1->R2, R2xR2->R2, R1xR2->R1) creates a Mobius
half-twist in the monad. This test finds the exact ratios embedded in
the 12-position circle under the Mobius topology.

Key questions:
1. What are the self-composition orbits on the 12-circle?
2. What is the angular sweep ratio between R1 and R2 powers?
3. Where does the Mobius half-twist appear numerically?
4. Are there golden ratios or self-similar patterns?
5. What is the attractor structure?
"""

import numpy as np
from math import gcd, pi, sqrt

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
    rail = get_rail(n)
    if rail == 0: return -1
    k = rail_k(n)
    sp = k % 6
    if rail == -1: return sp
    else: return sp + 6

def compose_12(pos_a, pos_b):
    """Compose two 12-positions: (rail_a, sp_a) * (rail_b, sp_b)"""
    rail_a = -1 if pos_a < 6 else +1
    sp_a = pos_a % 6
    rail_b = -1 if pos_b < 6 else +1
    sp_b = pos_b % 6

    if rail_a == -1 and rail_b == -1:  # R1xR1 -> R2
        sp_out = (-sp_a - sp_b) % 6
        rail_out = +1
    elif rail_a == +1 and rail_b == +1:  # R2xR2 -> R2
        sp_out = (sp_a + sp_b) % 6
        rail_out = +1
    else:  # R1xR2 or R2xR1 -> R1
        if rail_a == -1:  # a is R1, b is R2
            sp_out = (sp_a - sp_b) % 6
        else:  # a is R2, b is R1
            sp_out = (sp_b - sp_a) % 6
        rail_out = -1

    return sp_out if rail_out == -1 else sp_out + 6

def angle_of(pos):
    """Position to angle in degrees."""
    return pos * 30.0

def angle_step(from_pos, to_pos):
    """Shortest angular step from one position to another."""
    diff = (to_pos - from_pos) * 30.0
    if diff > 180: diff -= 360
    if diff < -180: diff += 360
    return diff

def angle_step_positive(from_pos, to_pos):
    """Always-positive angular step (accumulating full revolutions)."""
    diff = (to_pos - from_pos) * 30.0
    if diff < 0: diff += 360
    return diff

print("=" * 70)
print("  EXPERIMENT 018h: MOBIUS RATIOS IN THE 12-RAIL MONAD")
print("=" * 70)
print()

# ====================================================================
#  TEST 1: SELF-COMPOSITION ORBITS (p^n on the 12-circle)
# ====================================================================
print("=" * 70)
print("  TEST 1: SELF-COMPOSITION ORBITS (powers of each position)")
print("=" * 70)
print()

print("  For each starting position, trace p^1, p^2, p^3, ... on the monad.")
print()

for start in range(12):
    rail_str = "R1" if start < 6 else "R2"
    sp = start % 6
    orbit = [start]
    pos = start
    for _ in range(24):
        pos = compose_12(pos, start)
        orbit.append(pos)
        if pos == start and len(orbit) > 1:
            break

    period = len(orbit) - 1
    angles = [angle_of(p) for p in orbit]

    # Total angular sweep (positive direction)
    total_angle = sum(angle_step_positive(orbit[i], orbit[i+1]) for i in range(period))
    revolutions = total_angle / 360.0

    # Angular steps in orbit
    steps = [angle_step(orbit[i], orbit[i+1]) for i in range(period)]

    orbit_str = " -> ".join(f"{p:>2}" for p in orbit[:period+1])
    print(f"  {rail_str}(sp={sp}) pos {start:>2}: period={period}, "
          f"revolutions={revolutions:.1f}, total_angle={total_angle:.0f}deg")
    print(f"    orbit: {orbit_str}")

    # Show angular steps
    step_strs = []
    for s in steps:
        step_strs.append(f"{s:>+6.0f}")
    print(f"    steps: {''.join(step_strs)}")
    print()

# ====================================================================
#  TEST 2: THE MOBIUS RATIO — R1 vs R2 ANGULAR SWEEP
# ====================================================================
print("=" * 70)
print("  TEST 2: THE MOBIUS RATIO — R1 vs R2 ANGULAR VELOCITY")
print("=" * 70)
print()

r1_revolutions = []
r2_revolutions = []

for start in range(12):
    orbit = [start]
    pos = start
    for _ in range(24):
        pos = compose_12(pos, start)
        orbit.append(pos)
        if pos == start and len(orbit) > 1:
            break

    period = len(orbit) - 1
    total_angle = sum(angle_step_positive(orbit[i], orbit[i+1]) for i in range(period))
    revolutions = total_angle / 360.0

    if start < 6:
        r1_revolutions.append((start, revolutions, period))
    else:
        r2_revolutions.append((start, revolutions, period))

print("  R1 orbits (self-composition):")
for pos, rev, per in r1_revolutions:
    print(f"    pos {pos} (sp={pos}): {rev:.1f} revolutions in {per} steps = {rev/per:.2f} rev/step")
print()

print("  R2 orbits (self-composition):")
for pos, rev, per in r2_revolutions:
    print(f"    pos {pos} (sp={pos%6}): {rev:.1f} revolutions in {per} steps = {rev/per:.2f} rev/step")
print()

# The Mobius ratio
r1_avg = np.mean([r for _, r, _ in r1_revolutions])
r2_avg = np.mean([r for _, r, _ in r2_revolutions])
if r2_avg > 0:
    ratio = r1_avg / r2_avg
    print(f"  R1 avg revolutions: {r1_avg:.2f}")
    print(f"  R2 avg revolutions: {r2_avg:.2f}")
    print(f"  MOBIUS RATIO (R1/R2): {ratio:.2f}")
    print()

# ====================================================================
#  TEST 3: MOBIUS IDENTIFICATION — POSITION i AND i+6
# ====================================================================
print("=" * 70)
print("  TEST 3: MOBIUS IDENTIFICATION (pos i <-> pos i+6)")
print("=" * 70)
print()
print("  On a Mobius strip, opposite edges are identified with a twist.")
print("  In the monad, pos i (R1) and pos i+6 (R2) share the same sp.")
print("  The Z2 rule flips between them: R1xR1 -> R2 (adds 6).")
print()

print(f"  {'R1_pos':>6} {'R2_pos':>6} {'sp':>3} {'R1_angle':>9} {'R2_angle':>9} {'delta':>7} {'R1_rev':>7} {'R2_rev':>7} {'ratio':>6}")
print("  " + "-" * 70)

for sp in range(6):
    r1_pos = sp
    r2_pos = sp + 6

    # Compute revolutions for each
    for start in [r1_pos, r2_pos]:
        orbit = [start]
        pos = start
        for _ in range(24):
            pos = compose_12(pos, start)
            orbit.append(pos)
            if pos == start and len(orbit) > 1:
                break
        period = len(orbit) - 1
        total_angle = sum(angle_step_positive(orbit[i], orbit[i+1]) for i in range(period))
        if start == r1_pos:
            r1_rev = total_angle / 360.0
            r1_per = period
        else:
            r2_rev = total_angle / 360.0
            r2_per = period

    ratio = r1_rev / r2_rev if r2_rev > 0 else float('inf')
    delta = angle_of(r2_pos) - angle_of(r1_pos)
    print(f"  {r1_pos:>6} {r2_pos:>6} {sp:>3} {angle_of(r1_pos):>8.0f}deg {angle_of(r2_pos):>8.0f}deg {delta:>6.0f}deg "
          f"{r1_rev:>6.1f}/{r1_per} {r2_rev:>6.1f}/{r2_per} {ratio:>6.2f}")

print()

# ====================================================================
#  TEST 4: POWER SPECTRA — ACTUAL PRIME POWERS ON THE MONAD
# ====================================================================
print("=" * 70)
print("  TEST 4: PRIME POWER ORBITS ON THE MONAD")
print("=" * 70)
print()

def sieve(N):
    is_prime = np.ones(N, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return is_prime

is_prime_arr = sieve(200000)

rail_primes = [p for p in range(5, 200) if is_prime_arr[p] and get_rail(p) != 0]

print("  Actual prime power trajectories:")
print()

for p in rail_primes[:12]:
    start_pos = to_pos12(p)
    sp = rail_k(p) % 6
    rail = get_rail(p)
    rail_str = "R1" if rail == -1 else "R2"

    # Compute powers
    powers = [p]
    n = p
    for _ in range(8):
        n *= p
        if n > 200000:
            break
        powers.append(n)

    positions = [to_pos12(n) for n in powers]
    angles = [angle_of(pos) for pos in positions]

    # Find period
    period = len(positions)
    for i in range(1, len(positions)):
        if positions[i] == positions[0]:
            period = i
            break

    # Total angle per period
    total_angle = sum(angle_step_positive(positions[i], positions[i+1]) for i in range(min(period, len(positions)-1)))
    revolutions = total_angle / 360.0

    pos_str = " -> ".join(f"{pos:>2}" for pos in positions[:min(7, len(positions))])
    print(f"  {p:>3} ({rail_str},sp={sp}): period={period}, rev={revolutions:.1f}, "
          f"orbit: {pos_str}")

print()

# ====================================================================
#  TEST 5: THE ATTRACTOR STRUCTURE — FIXED POINTS AND CYCLES
# ====================================================================
print("=" * 70)
print("  TEST 5: ATTRACTORS — FIXED POINTS AND CYCLES IN 12-SPACE")
print("=" * 70)
print()

# For each pair of positions, compute the composition
# Find all closed orbits under repeated composition with a fixed partner
print("  Composition with fixed partner q: p -> p*q -> p*q*q -> ...")
print()

for q in range(12):
    rail_q = "R1" if q < 6 else "R2"
    sp_q = q % 6

    orbits = {}
    for start in range(12):
        pos = start
        visited = [pos]
        for _ in range(24):
            pos = compose_12(pos, q)
            if pos in visited:
                idx = visited.index(pos)
                cycle = visited[idx:]
                orbits[start] = cycle
                break
            visited.append(pos)

    # Classify orbits
    fixed = [s for s, c in orbits.items() if len(c) == 1]
    cycles_2 = [s for s, c in orbits.items() if len(c) == 2]
    cycles_3 = [s for s, c in orbits.items() if len(c) == 3]
    cycles_6 = [s for s, c in orbits.items() if len(c) == 6]
    other = [s for s, c in orbits.items() if len(c) not in [1, 2, 3, 6]]

    print(f"  q={q:>2} ({rail_q},sp={sp_q}): fixed={fixed}, 2-cycles={len(cycles_2)}, "
          f"3-cycles={len(cycles_3)}, 6-cycles={len(cycles_6)}, other={other}")

print()

# ====================================================================
#  TEST 6: THE FULL 12x12 COMPOSITION MATRIX AS TRANSFORMATIONS
# ====================================================================
print("=" * 70)
print("  TEST 6: THE 12x12 COMPOSITION AS ANGULAR TRANSFORMS")
print("=" * 70)
print()

# Each row of the 12x12 table is a permutation/transformation
# Compute the angular displacement each position causes
print("  Angular displacement caused by composing with each position:")
print(f"  {'pos':>3} {'rail':>4} {'sp':>3} {'displacements (deg)':>60}")
print("  " + "-" * 75)

for q in range(12):
    rail_q = "R1" if q < 6 else "R2"
    sp_q = q % 6

    displacements = []
    for p in range(12):
        result = compose_12(p, q)
        disp = angle_step(p, result)
        displacements.append(disp)

    disp_str = " ".join(f"{d:>+4.0f}" for d in displacements)
    print(f"  {q:>3} {rail_q:>4} {sp_q:>3} {disp_str}")

print()

# ====================================================================
#  TEST 7: EIGENFREQUENCIES — ORBITAL FREQUENCY RATIOS
# ====================================================================
print("=" * 70)
print("  TEST 7: EIGENFREQUENCIES AND HARMONIC RATIOS")
print("=" * 70)
print()

# For each position, compute its "frequency" = revolutions per step
# under self-composition
print("  Frequency table (revolutions per self-composition step):")
print()

frequencies = {}
for start in range(12):
    orbit = [start]
    pos = start
    for _ in range(24):
        pos = compose_12(pos, start)
        orbit.append(pos)
        if pos == start and len(orbit) > 1:
            break
    period = len(orbit) - 1
    total_angle = sum(angle_step_positive(orbit[i], orbit[i+1]) for i in range(period))
    freq = total_angle / (360.0 * period)
    frequencies[start] = freq

print(f"  {'pos':>3} {'rail':>4} {'sp':>3} {'freq (rev/step)':>16} {'ratio to R2(sp=0)':>18}")
print("  " + "-" * 50)

ref_freq = frequencies[6]  # R2, sp=0 as reference

for start in range(12):
    rail_str = "R1" if start < 6 else "R2"
    sp = start % 6
    f = frequencies[start]
    ratio = f / ref_freq if ref_freq > 0 else float('inf')
    print(f"  {start:>3} {rail_str:>4} {sp:>3} {f:>16.4f} {ratio:>18.4f}")

print()

# Frequency ratios between all pairs
print("  Frequency ratios between positions (simplified):")
freq_ratios = {}
for a in range(12):
    for b in range(a+1, 12):
        if frequencies[a] > 0 and frequencies[b] > 0:
            r = frequencies[a] / frequencies[b]
            # Try to express as simple fraction
            for denom in range(1, 13):
                numer = round(r * denom)
                if abs(r - numer/denom) < 0.01 and numer > 0:
                    g = gcd(numer, denom)
                    key = f"{numer//g}:{denom//g}"
                    if key not in freq_ratios:
                        freq_ratios[key] = []
                    freq_ratios[key].append((a, b))
                    break

for ratio, pairs in sorted(freq_ratios.items(), key=lambda x: -len(x[1])):
    if len(pairs) >= 2:
        print(f"    Ratio {ratio}: {len(pairs)} pairs, e.g. {pairs[:5]}")

print()

# ====================================================================
#  TEST 8: MOBIUS TWIST AS DOUBLE COVER
# ====================================================================
print("=" * 70)
print("  TEST 8: THE MOBIUS DOUBLE COVER")
print("=" * 70)
print()
print("  On a Mobius strip, you must traverse TWICE to return to start.")
print("  Check: does composing with the 'opposite' position (i+6)")
print("  require 2 traversals to return?")
print()

for start in range(6):
    opposite = start + 6

    # Walk by composing with opposite repeatedly
    pos = start
    trajectory = [pos]
    for _ in range(24):
        pos = compose_12(pos, opposite)
        trajectory.append(pos)
        if pos == start:
            break

    period = len(trajectory) - 1
    total_angle = sum(angle_step_positive(trajectory[i], trajectory[i+1]) for i in range(period))
    rev = total_angle / 360.0

    traj_str = " -> ".join(f"{t:>2}" for t in trajectory)
    print(f"  Start {start}, walk by +{opposite}: period={period}, rev={rev:.1f}")
    print(f"    {traj_str}")

print()

# ====================================================================
#  TEST 9: SELF-SIMILARITY AND SCALING RATIOS
# ====================================================================
print("=" * 70)
print("  TEST 9: SELF-SIMILARITY IN THE COMPOSITION TABLE")
print("=" * 70)
print()

# Check if the composition table has self-similar structure
# Compare blocks: does the R1xR1 block relate to the R2xR2 block?
print("  R1xR1 results (positions 0-5 composed with 0-5):")
r1r1 = np.zeros((6, 6), dtype=int)
for i in range(6):
    for j in range(6):
        r1r1[i][j] = compose_12(i, j)
        print(f"  {r1r1[i][j]:>3}", end="")
    print()

print()
print("  R2xR2 results (positions 6-11 composed with 6-11):")
r2r2 = np.zeros((6, 6), dtype=int)
for i in range(6):
    for j in range(6):
        r2r2[i][j] = compose_12(i+6, j+6)
        print(f"  {r2r2[i][j]:>3}", end="")
    print()

print()
print("  R1xR2 results (positions 0-5 composed with 6-11):")
r1r2 = np.zeros((6, 6), dtype=int)
for i in range(6):
    for j in range(6):
        r1r2[i][j] = compose_12(i, j+6)
        print(f"  {r1r2[i][j]:>3}", end="")
    print()

print()

# Check self-similarity: offset R1xR1 by 6 and compare to R2xR2
print("  Self-similarity check: R1xR1 + 6 vs R2xR2:")
match = 0
total = 36
for i in range(6):
    for j in range(6):
        if r1r1[i][j] + 6 == r2r2[i][j]:
            match += 1

print(f"    {match}/{total} entries match (R1xR1 + 6 == R2xR2)")

# Check: R1xR2 compared to R1xR1 offset pattern
print()
print("  R1xR2 compared to shifted R1xR1:")
match2 = 0
for i in range(6):
    for j in range(6):
        # R1xR1 gives R2 positions, R1xR2 gives R1 positions
        # Check if there's a consistent offset
        pass

# Instead, check angular displacement patterns
print()
print("  Angular displacement patterns:")
print("  R1xR1 angular steps from (i,0) to (i,j):")
for i in range(6):
    steps = []
    for j in range(6):
        result = compose_12(i, j)
        steps.append(angle_step(i, result))
    print(f"    sp={i}: {steps}")

print("  R2xR2 angular steps from (i+6,6) to (i+6,j+6):")
for i in range(6):
    steps = []
    for j in range(6):
        result = compose_12(i+6, j+6)
        steps.append(angle_step(i+6, result))
    print(f"    sp={i}: {steps}")

print()

# ====================================================================
#  TEST 10: THE GOLDEN RATIO IN THE MONAD
# ====================================================================
print("=" * 70)
print("  TEST 10: GOLDEN RATIO AND SPECIAL RATIOS")
print("=" * 70)
print()

phi = (1 + sqrt(5)) / 2  # Golden ratio
print(f"  Golden ratio phi = {phi:.6f}")
print()

# Check if any orbit ratios approximate phi
print("  Checking all orbit period ratios for golden ratio proximity:")
golden_pairs = []
for a in range(12):
    orbit_a = [a]
    pos = a
    for _ in range(24):
        pos = compose_12(pos, a)
        orbit_a.append(pos)
        if pos == a: break
    period_a = len(orbit_a) - 1
    total_a = sum(angle_step_positive(orbit_a[i], orbit_a[i+1]) for i in range(period_a))

    for b in range(a+1, 12):
        orbit_b = [b]
        pos = b
        for _ in range(24):
            pos = compose_12(pos, b)
            orbit_b.append(pos)
            if pos == b: break
        period_b = len(orbit_b) - 1
        total_b = sum(angle_step_positive(orbit_b[i], orbit_b[i+1]) for i in range(period_b))

        if total_a > 0 and total_b > 0:
            r = total_a / total_b
            if abs(r - phi) < 0.1 or abs(r - 1/phi) < 0.1 or abs(r - phi**2) < 0.1:
                golden_pairs.append((a, b, r, total_a, total_b))

if golden_pairs:
    print(f"  Found {len(golden_pairs)} pairs near golden ratio:")
    for a, b, r, ta, tb in golden_pairs:
        print(f"    pos {a} vs pos {b}: ratio = {r:.4f} (phi={phi:.4f}, 1/phi={1/phi:.4f})")
else:
    print("  No pairs near golden ratio found in angular sweep ratios.")

print()

# Check Fibonacci-like patterns in composition sequences
print("  Fibonacci-like sequences under composition:")
# Start with two positions, compose to get the next (like Fibonacci)
# F(n) = F(n-1) * F(n-2) in monad multiplication
for seed_a, seed_b in [(1, 7), (0, 6), (1, 2), (0, 1)]:
    seq = [seed_a, seed_b]
    for _ in range(15):
        next_pos = compose_12(seq[-1], seq[-2])
        seq.append(next_pos)
        if len(seq) > 4 and seq[-2:] == seq[2:4]:
            break

    period = None
    for i in range(2, len(seq)):
        if seq[i] == seq[0] and seq[i+1] == seq[1] if i+1 < len(seq) else False:
            period = i
            break

    seq_str = " -> ".join(f"{s:>2}" for s in seq[:12])
    ra = "R1" if seed_a < 6 else "R2"
    rb = "R1" if seed_b < 6 else "R2"
    print(f"  ({ra}{seed_a%6}, {rb}{seed_b%6}): {seq_str}")

print()

# ====================================================================
#  TEST 11: THE MOBIUS TWIST ANGLE
# ====================================================================
print("=" * 70)
print("  TEST 11: THE MOBIUS TWIST ANGLE")
print("=" * 70)
print()
print("  The Z2 rule creates a phase inversion: R1 x R1 -> R2")
print("  In angular terms: R1(sp=a) x R1(sp=b) -> R2(sp=(-a-b)%6)")
print("  The twist is the angular displacement from 'expected' to 'actual'")
print()

# For same-sp composition, the 'naive' angle would be a+a=2a
# But R1xR1 gives (-a-a)%6 = -2a mod 6
# The twist = actual - naive = (-2a - 2a) mod 6 = -4a mod 6
print("  Twist angle for R1 self-composition (pos x pos):")
for sp in range(6):
    naive_sp = (sp + sp) % 6  # What you'd get if rails added normally
    actual_sp = (-sp - sp) % 6  # What R1xR1 actually gives
    twist = (actual_sp - naive_sp) % 6
    twist_angle = twist * 30
    print(f"    sp={sp}: naive_sp={naive_sp}, actual_sp={actual_sp}, "
          f"twist={twist} positions = {twist_angle}deg")

print()

# For R2, the twist is 0 (constructive, no phase inversion)
print("  For R2 self-composition (no twist):")
for sp in range(6):
    naive_sp = (sp + sp) % 6
    actual_sp = (sp + sp) % 6
    twist = (actual_sp - naive_sp) % 6
    print(f"    sp={sp}: naive={naive_sp}, actual={actual_sp}, twist={twist}")

print()

# ====================================================================
#  TEST 12: THE THREE-FOLD PATTERN
# ====================================================================
print("=" * 70)
print("  TEST 12: THE THREE-FOLD PATTERN IN THE MONAD")
print("=" * 70)
print()
print("  The composition table maps 12 positions to 3 attractors")
print("  under self-composition. What is the structure of these 3?")
print()

# The three attractor positions under self-composition
attractors = set()
for start in range(12):
    pos = start
    for _ in range(20):
        pos = compose_12(pos, start)
    attractors.add(pos)

print(f"  Attractor positions: {sorted(attractors)}")
print(f"  Attractor angles: {[angle_of(a) for a in sorted(attractors)]}")
print()

# Angular ratios between attractors
attr_sorted = sorted(attractors)
if len(attr_sorted) >= 2:
    for i in range(len(attr_sorted)):
        for j in range(i+1, len(attr_sorted)):
            a1 = angle_of(attr_sorted[i])
            a2 = angle_of(attr_sorted[j])
            delta = a2 - a1
            ratio = a2 / a1 if a1 > 0 else float('inf')
            print(f"  Attractor {attr_sorted[i]} ({a1:.0f}deg) vs "
                  f"{attr_sorted[j]} ({a2:.0f}deg): "
                  f"delta={delta:.0f}deg, ratio={ratio:.3f}")

print()

# ====================================================================
#  SUMMARY
# ====================================================================
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()

# Collect all the key ratios found
print("  KEY RATIOS IN THE MOBIUS MONAD:")
print()

# Compute R1 vs R2 average frequency
r1_freqs = [frequencies[i] for i in range(6)]
r2_freqs = [frequencies[i] for i in range(6, 12)]
r1_avg_f = np.mean(r1_freqs)
r2_avg_f = np.mean(r2_freqs)

print(f"  1. R1 self-composition angular velocity: {r1_avg_f:.3f} rev/step")
print(f"  2. R2 self-composition angular velocity: {r2_avg_f:.3f} rev/step")
if r2_avg_f > 0:
    print(f"  3. MOBIUS RATIO (R1/R2): {r1_avg_f/r2_avg_f:.3f}")
print()
print("  The Mobius half-twist (Z2 sign flip) causes R1 positions to")
print("  spiral at a DIFFERENT rate than R2 positions under self-composition.")
print("  This ratio IS the Mobius topology encoded in the monad.")
print()
print("Done.")
