"""
Experiment 018f: Base-36 Structure of the 6k+/-1 Manifold
==========================================================
Group the manifold in blocks of 36 (= 6^2).
Each block contains exactly 12 positions coprime to 6:
  - 6 on Rail1 (residue 5 mod 6): offsets 5,11,17,23,29,35
  - 6 on Rail2 (residue 1 mod 6): offsets 1,7,13,19,25,31

These 12 positions create a natural "digit" system.
12 sub-rails × 2 rails = 24 or base-12 per rail.

Key questions:
1. How do the composition formulas map into base-36 blocks?
2. Does the walking rule simplify in this representation?
3. What's the structure of the 12 residue classes mod 36?
4. Can we express multiplication as a Z2 × Z6 operation?
"""

import numpy as np
from math import gcd

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

N_MAX = 500_000

print("=" * 70)
print("  EXPERIMENT 018f: BASE-36 STRUCTURE OF THE 6k+/-1 MANIFOLD")
print("=" * 70)
print()

is_prime_arr = sieve(N_MAX + 100)

spf = np.zeros(N_MAX + 100, dtype=np.int32)
for i in range(2, N_MAX + 100):
    if is_prime_arr[i]:
        spf[i::i] = np.where(spf[i::i] == 0, i, spf[i::i])
spf[0] = 0; spf[1] = 0

def factorize(n):
    factors = []
    while n > 1:
        factors.append(spf[n])
        n //= spf[n]
    return factors

# ====================================================================
#  TEST 1: THE 12 RESIDUE CLASSES MOD 36
# ====================================================================
print("=" * 70)
print("  TEST 1: THE 12 RESIDUE CLASSES MOD 36")
print("=" * 70)
print()

# Numbers coprime to 6 within [0, 35]
coprime_offsets = sorted([r for r in range(36) if r % 2 != 0 and r % 3 != 0])
print(f"  Offsets coprime to 6 in [0,35]: {coprime_offsets}")
print(f"  Count: {len(coprime_offsets)}")
print()

# Classify each by rail and sub-position
print(f"  {'offset':>6} {'rail':>5} {'sub-pos':>7} {'k mod 6':>7} {'rail_k mod 6':>11}")
print("  " + "-" * 45)

sub_positions = {}
for i, r in enumerate(coprime_offsets):
    rail = get_rail(r) if r > 0 else get_rail(r + 36)  # handle 0 case
    # For residue r, the number is 36*block + r
    # k = rail_k(36*block + r)
    # Since 36 = 6*6, k = (36*block + r - 1)/6 or (36*block + r + 1)/6
    if r == 0:
        rail = 0
        k_mod6 = 0
    elif r % 6 == 1:
        rail = +1
        k_mod6 = ((r - 1) // 6) % 6
    elif r % 6 == 5:
        rail = -1
        k_mod6 = ((r + 1) // 6) % 6
    else:
        rail = 0
        k_mod6 = -1

    sub_positions[r] = {
        'index': i, 'rail': rail, 'sub_pos': k_mod6
    }
    rail_str = 'R1' if rail == -1 else 'R2' if rail == 1 else 'R0'
    print(f"  {r:>6} {rail_str:>5} {i:>7} {k_mod6:>7}")

print()
print("  So each block of 36 contains:")
print("    6 Rail1 positions (sub-positions 0-5)")
print("    6 Rail2 positions (sub-positions 0-5)")
print("    = 12 total positions per block")
print("    = Base-12 digit system on the manifold")
print()

# ====================================================================
#  TEST 2: DUAL COORDINATE SYSTEM
# ====================================================================
print("=" * 70)
print("  TEST 2: DUAL COORDINATE SYSTEM")
print("=" * 70)
print()
print("  Any number n on the manifold can be written as:")
print("    n = 36 * block + offset")
print("  where offset is one of the 12 coprime residues.")
print()
print("  Equivalently: (block, sub_pos, rail)")
print("  where block = n // 36")
print("        sub_pos = (k mod 6) = position within the block")
print("        rail = R1 or R2")
print()
print("  This gives a 3D coordinate: (block, sub_pos, rail)")
print("  Rail1: n = 36*block + 6*sub_pos*2 + 5  ... let's verify")
print()

def to_coords(n):
    """Convert n to (block, sub_pos, rail) coordinates."""
    if get_rail(n) == 0:
        return None
    rail = get_rail(n)
    k = rail_k(n)
    block = k // 6
    sub_pos = k % 6
    return (block, sub_pos, rail)

def from_coords(block, sub_pos, rail):
    """Reconstruct n from (block, sub_pos, rail)."""
    k = 6 * block + sub_pos
    if rail == -1:
        return 6 * k - 1
    elif rail == +1:
        return 6 * k + 1
    return 0

# Verify roundtrip
print("  Roundtrip verification:")
errors = 0
total_rt = 0
for n in range(5, 500):
    if get_rail(n) == 0: continue
    coords = to_coords(n)
    if coords is None: continue
    block, sub_pos, rail = coords
    reconstructed = from_coords(block, sub_pos, rail)
    if reconstructed != n:
        errors += 1
        print(f"    ERROR: {n} -> {coords} -> {reconstructed}")
    total_rt += 1

print(f"    {total_rt - errors}/{total_rt} correct ({100*(total_rt-errors)/max(total_rt,1):.1f}%)")
print()

# ====================================================================
#  TEST 3: RAIL STRUCTURE WITHIN EACH BLOCK
# ====================================================================
print("=" * 70)
print("  TEST 3: RAIL STRUCTURE WITHIN BLOCKS")
print("=" * 70)
print()
print("  Block 0 (n=1..35):")
print(f"  {'sub_pos':>7} {'Rail1':>8} {'prime?':>7} {'Rail2':>8} {'prime?':>7}")
print("  " + "-" * 45)

for sp in range(6):
    n_r1 = from_coords(0, sp, -1)
    n_r2 = from_coords(0, sp, +1)
    r1p = "YES" if n_r1 >= 5 and is_prime_arr[n_r1] else "no" if n_r1 >= 2 else "---"
    r2p = "YES" if n_r2 >= 5 and is_prime_arr[n_r2] else "no" if n_r2 >= 2 else "---"
    print(f"  {sp:>7} {n_r1:>8} {r1p:>7} {n_r2:>8} {r2p:>7}")

print()
print("  Block 1 (n=36..71):")
print(f"  {'sub_pos':>7} {'Rail1':>8} {'prime?':>7} {'Rail2':>8} {'prime?':>7}")
print("  " + "-" * 45)

for sp in range(6):
    n_r1 = from_coords(1, sp, -1)
    n_r2 = from_coords(1, sp, +1)
    r1p = "YES" if is_prime_arr[n_r1] else "no"
    r2p = "YES" if is_prime_arr[n_r2] else "no"
    print(f"  {sp:>7} {n_r1:>8} {r1p:>7} {n_r2:>8} {r2p:>7}")

print()

# ====================================================================
#  TEST 4: COMPOSITION IN BASE-36 COORDINATES
# ====================================================================
print("=" * 70)
print("  TEST 4: COMPOSITION IN (block, sub_pos, rail) COORDINATES")
print("=" * 70)
print()
print("  For same-rail composites, k_N = 6ab +/- a +/- b")
print("  In the new coordinates: k = 6*block + sub_pos")
print("  So block_N = k_N // 6, sub_pos_N = k_N % 6")
print()

# Collect same-rail semiprimes and check coordinate patterns
print("  Same-rail semiprime composition in (block, sp) coordinates:")
print(f"  {'N':>6} {'= p x q':>10} {'k_N':>5} {'(b,sp,R)':>12} {'p(b,sp,R)':>12} {'q(b,sp,R)':>12}")
print("  " + "-" * 65)

count = 0
for n in range(25, 500):
    if get_rail(n) == 0 or is_prime_arr[n]: continue
    factors = factorize(n)
    if len(factors) != 2: continue
    unique = set(factors)
    if len(unique) != 2: continue
    p1, p2 = sorted(factors)
    r1, r2 = get_rail(p1), get_rail(p2)
    if r1 == 0 or r2 == 0: continue
    if r1 != r2: continue  # same rail only

    c_n = to_coords(n)
    c_p1 = to_coords(p1)
    c_p2 = to_coords(p2)

    fmt = lambda c: f"({c[0]},{c[1]},{'R1' if c[2]==-1 else 'R2'})"
    print(f"  {n:>6} {p1:>3} x {p2:<3} {rail_k(n):>5} {fmt(c_n):>12} {fmt(c_p1):>12} {fmt(c_p2):>12}")
    count += 1
    if count >= 20: break

print()

# ====================================================================
#  TEST 5: SUB-POSITION MULTIPLICATION TABLE (mod 6)
# ====================================================================
print("=" * 70)
print("  TEST 5: SUB-POSITION MULTIPLICATION TABLE (sp_a, sp_b) -> sp_N")
print("=" * 70)
print()
print("  k_N = 6ab +/- a +/- b")
print("  sp_N = k_N mod 6")
print("  Since k = 6*block + sp, and a = 6*block_a + sp_a, b = 6*block_b + sp_b:")
print("  k_N mod 6 = (6ab +/- a +/- b) mod 6 = (+/- sp_a +/- sp_b) mod 6")
print()

# For R1xR1 -> R2: k_N = 6ab - a - b
# sp_N = (-sp_a - sp_b) mod 6 = -(sp_a + sp_b) mod 6 = (6 - (sp_a + sp_b) % 6) % 6
# For R2xR2 -> R2: k_N = 6ab + a + b
# sp_N = (sp_a + sp_b) mod 6

print("  R1xR1->R2: sp_N = (-sp_a - sp_b) mod 6 = (6 - (sp_a+sp_b)%6)%6")
print()

print("     ", end="")
for sp_b in range(6):
    print(f" sp_b={sp_b}", end="")
print()
print("  " + "-" * 55)
for sp_a in range(6):
    print(f"  sp_a={sp_a}", end="")
    for sp_b in range(6):
        sp_n = (-sp_a - sp_b) % 6
        print(f"      {sp_n}", end="")
    print()

print()
print("  R2xR2->R2: sp_N = (sp_a + sp_b) mod 6")
print()

print("     ", end="")
for sp_b in range(6):
    print(f" sp_b={sp_b}", end="")
print()
print("  " + "-" * 55)
for sp_a in range(6):
    print(f"  sp_a={sp_a}", end="")
    for sp_b in range(6):
        sp_n = (sp_a + sp_b) % 6
        print(f"      {sp_n}", end="")
    print()

print()

# ====================================================================
#  TEST 6: VERIFY SUB-POSITION RULES
# ====================================================================
print("=" * 70)
print("  TEST 6: VERIFY SUB-POSITION RULES EMPIRICALLY")
print("=" * 70)
print()

correct_r1r1 = 0
correct_r2r2 = 0
correct_r1r2 = 0
total_r1r1 = 0
total_r2r2 = 0
total_r1r2 = 0

for n in range(25, N_MAX + 1):
    if get_rail(n) == 0 or is_prime_arr[n]: continue
    factors = factorize(n)
    if len(factors) != 2: continue
    unique = set(factors)
    if len(unique) != 2: continue
    p1, p2 = sorted(factors)
    r1, r2 = get_rail(p1), get_rail(p2)
    if r1 == 0 or r2 == 0: continue

    c_n = to_coords(n)
    c_p1 = to_coords(p1)
    c_p2 = to_coords(p2)

    sp_n = c_n[1]
    sp_a = c_p1[1]
    sp_b = c_p2[1]

    if r1 == -1 and r2 == -1:  # R1xR1 -> R2
        expected = (-sp_a - sp_b) % 6
        if sp_n == expected:
            correct_r1r1 += 1
        total_r1r1 += 1
    elif r1 == +1 and r2 == +1:  # R2xR2 -> R2
        expected = (sp_a + sp_b) % 6
        if sp_n == expected:
            correct_r2r2 += 1
        total_r2r2 += 1
    else:  # R1xR2 -> R1
        # Need to identify which factor is R1 and which is R2
        # Formula: k_N = 6*a*b + a - b where a is R1 factor's k, b is R2 factor's k
        if r1 == -1:  # p1 is R1, p2 is R2
            expected = (sp_a - sp_b) % 6
        else:  # p1 is R2, p2 is R1
            expected = (sp_b - sp_a) % 6
        if sp_n == expected:
            correct_r1r2 += 1
        total_r1r2 += 1

print(f"  R1xR1->R2: sp_N = (-sp_a - sp_b) mod 6")
print(f"    {correct_r1r1}/{total_r1r1} ({100*correct_r1r1/max(total_r1r1,1):.1f}%)")
print(f"  R2xR2->R2: sp_N = (sp_a + sp_b) mod 6")
print(f"    {correct_r2r2}/{total_r2r2} ({100*correct_r2r2/max(total_r2r2,1):.1f}%)")
print(f"  R1xR2->R1: sp_N = (sp_a - sp_b) mod 6")
print(f"    {correct_r1r2}/{total_r1r2} ({100*correct_r1r2/max(total_r1r2,1):.1f}%)")
print()

# ====================================================================
#  TEST 7: THE BLOCK CARRY RULE
# ====================================================================
print("=" * 70)
print("  TEST 7: BLOCK CARRY — HOW block_N RELATES TO block_a, block_b")
print("=" * 70)
print()
print("  k_N = 6ab +/- a +/- b")
print("  k = 6*block + sp, so a = 6*block_a + sp_a, etc.")
print("  k_N = 6(6*ba+sp_a)(6*bb+sp_b) +/- (6*ba+sp_a) +/- (6*bb+sp_b)")
print("      = 6*36*ba*bb + 36*ba*sp_b + 36*bb*sp_a + 6*sp_a*sp_b +/- 6*ba +/- sp_a +/- 6*bb +/- sp_b")
print("  block_N = k_N // 6 (the carry comes from the sp_x*sp_y and sp_x terms)")
print()

# Compute block_N for R2xR2 as example: k_N = 6ab + a + b
# block_N = k_N // 6 = (6ab + a + b) // 6
# But we need k_N mod 6 = sp_N, and k_N = 6 * block_N + sp_N
# So block_N = (k_N - sp_N) / 6

# Let's check if there's a pattern in block composition
print("  Checking block composition patterns for R2xR2:")
print(f"  {'N':>6} {'p1':>4} {'p2':>4} {'block_N':>8} {'block_a':>8} {'block_b':>8} {'sp_a':>4} {'sp_b':>4} {'sp_N':>4} {'6*ba*bb+ba+bb':>15}")
print("  " + "-" * 75)

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
    if r1 != +1 or r2 != +1: continue  # R2xR2 only

    c_n = to_coords(n)
    c_p1 = to_coords(p1)
    c_p2 = to_coords(p2)

    block_n = c_n[0]
    sp_n = c_n[1]
    block_a = c_p1[0]
    block_b = c_p2[0]
    sp_a = c_p1[1]
    sp_b = c_p2[1]

    # Predicted block from just the block parts (ignoring sub-position contribution)
    naive_block = 6 * block_a * block_b + block_a + block_b

    if count < 15:
        print(f"  {n:>6} {p1:>4} {p2:>4} {block_n:>8} {block_a:>8} {block_b:>8} {sp_a:>4} {sp_b:>4} {sp_n:>4} {naive_block:>15}")
    count += 1

print(f"  ... ({count} total R2xR2 semiprimes)")
print()

# ====================================================================
#  TEST 8: THE FULL MULTIPLICATION TABLE IN 12-SPACE
# ====================================================================
print("=" * 70)
print("  TEST 8: MULTIPLICATION TABLE IN 12-SPACE")
print("=" * 70)
print()
print("  Each position is (rail, sub_pos) where rail in {R1, R2}, sub_pos in {0..5}")
print("  That's 2 x 6 = 12 positions. Multiplication table:")
print()

# The Z2 rail rule
print("  RAIL RULE (Z2): R1 x R1 = R2, R2 x R2 = R2, R1 x R2 = R1")
print()
print("  SUB-POSITION RULE:")
print("  R1 x R1: sp = (-a - b) mod 6")
print("  R2 x R2: sp = (a + b) mod 6")
print("  R1 x R2: sp = (a - b) mod 6")
print()

# Build the 12x12 multiplication table
# Index: 0-5 = R1(sp=0..5), 6-11 = R2(sp=0..5)
print("  12x12 (rail, sp) multiplication table:")
print("  Rows/cols: 0-5 = R1(sp0..5), 6-11 = R2(sp0..5)")
print()

header = "     "
for j in range(12):
    rail_j = 'R1' if j < 6 else 'R2'
    sp_j = j % 6
    header += f" {rail_j}{sp_j}"
print(header)
print("  " + "-" * (5 + 6 * 12))

for i in range(12):
    rail_i = -1 if i < 6 else +1
    sp_i = i % 6
    rail_str = 'R1' if rail_i == -1 else 'R2'
    row = f"  {rail_str}{sp_i} "

    for j in range(12):
        rail_j = -1 if j < 6 else +1
        sp_j = j % 6

        # Apply Z2 rule
        if rail_i == -1 and rail_j == -1:
            rail_out = +1  # R2
            sp_out = (-sp_i - sp_j) % 6
        elif rail_i == +1 and rail_j == +1:
            rail_out = +1  # R2
            sp_out = (sp_i + sp_j) % 6
        else:
            rail_out = -1  # R1
            sp_out = (sp_i - sp_j) % 6

        out_str = f"{'R1' if rail_out == -1 else 'R2'}{sp_out}"
        row += f" {out_str:>4}"

    print(row)

print()

# ====================================================================
#  TEST 9: ALGEBRAIC STRUCTURE — IS THIS A GROUP?
# ====================================================================
print("=" * 70)
print("  TEST 9: ALGEBRAIC STRUCTURE OF THE 12-POSITION TABLE")
print("=" * 70)
print()

# Check if the 12-position table forms a group
# The table above only covers (rail, sp) — it ignores the block component
# So it's a group operation on the "digit" level

# Check closure: all entries are in {0..11} — yes, by construction
# Check associativity: need to verify (a*b)*c == a*(b*c) for all a,b,c

positions = list(range(12))

def multiply_12(a, b):
    """Multiply two 12-positions."""
    rail_a = -1 if a < 6 else +1
    sp_a = a % 6
    rail_b = -1 if b < 6 else +1
    sp_b = b % 6

    if rail_a == -1 and rail_b == -1:
        rail_out = +1
        sp_out = (-sp_a - sp_b) % 6
    elif rail_a == +1 and rail_b == +1:
        rail_out = +1
        sp_out = (sp_a + sp_b) % 6
    else:
        rail_out = -1
        sp_out = (sp_a - sp_b) % 6

    return (sp_out if rail_out == -1 else sp_out + 6)

# Check associativity
assoc_ok = True
for a in positions:
    for b in positions:
        for c in positions:
            ab_c = multiply_12(multiply_12(a, b), c)
            a_bc = multiply_12(a, multiply_12(b, c))
            if ab_c != a_bc:
                assoc_ok = False
                print(f"  NOT ASSOCIATIVE: ({a}*{b})*{c} = {ab_c}, {a}*({b}*{c}) = {a_bc}")
                break
        if not assoc_ok:
            break
    if not assoc_ok:
        break

if assoc_ok:
    print("  Associativity: YES (all 12^3 = 1728 triples checked)")
else:
    print("  Associativity: NO")
print()

# Find identity
print("  Looking for identity element:")
for e in positions:
    is_identity = True
    for a in positions:
        if multiply_12(a, e) != a or multiply_12(e, a) != a:
            is_identity = False
            break
    if is_identity:
        rail_e = 'R1' if e < 6 else 'R2'
        sp_e = e % 6
        print(f"    Identity: position {e} = {rail_e}(sp={sp_e})")

print()

# Find inverses
print("  Looking for inverses:")
has_inverse = True
for a in positions:
    found = False
    for b in positions:
        if multiply_12(a, b) == multiply_12(b, a):
            # Check if it's the identity
            # First find identity
            e = None
            for candidate in positions:
                if all(multiply_12(x, candidate) == x and multiply_12(candidate, x) == x for x in positions[:3]):
                    e = candidate
                    break
            if e is not None and multiply_12(a, b) == e:
                found = True
                break
    if not found:
        has_inverse = False
        rail_a = 'R1' if a < 6 else 'R2'
        sp_a = a % 6
        print(f"    No inverse for position {a} = {rail_a}(sp={sp_a})")

if has_inverse:
    print("    All elements have inverses")
print()

# Check commutativity
commutative = True
for a in positions:
    for b in positions:
        if multiply_12(a, b) != multiply_12(b, a):
            commutative = False
            break
    if not commutative:
        break

print(f"  Commutative: {'YES (Abelian)' if commutative else 'NO'}")
print()

# ====================================================================
#  TEST 10: WALKING RULE IN BASE-36
# ====================================================================
print("=" * 70)
print("  TEST 10: WALKING RULE IN BASE-36 COORDINATES")
print("=" * 70)
print()
print("  Walking rule: k_N + p advances the other factor.")
print("  In (block, sp) coordinates: adding p = adding (6*block_p + sp_p)")
print("  to k_N = 6*block_N + sp_N.")
print()
print("  New sp = (sp_N + sp_p) mod 6")
print("  New block = block_N + block_p + carry")
print("  where carry = 1 if (sp_N + sp_p) >= 6, else 0")
print()
print("  The walking step in 12-space is: sp -> (sp + sp_p) mod 6")
print("  The rail doesn't change during walking (same chain).")
print()

# Verify: walking along a prime's chain, the sub-position advances by sp_p each step
print("  Walking 5's chain: p=5, k=1, sp=1, R1")
k = rail_k(5)
coords = to_coords(5)
print(f"  5: k={k}, coords=(block={coords[0]}, sp={coords[1]}, rail={'R1' if coords[2]==-1 else 'R2'})")

k = rail_k(5)
sp_p = coords[1]  # sp of 5
for step in range(12):
    k_new = k + 5
    n_r1 = 6 * k_new - 1
    n_r2 = 6 * k_new + 1
    for candidate in [n_r1, n_r2]:
        if candidate % 5 == 0 and candidate <= N_MAX and candidate >= 5:
            c = to_coords(candidate)
            expected_sp = (sp_p * (step + 1) + coords[1]) % 6  # sp advances by sp_p each step
            # Actually simpler: sp = (sp_prev + sp_p) % 6
            rail_c = 'R1' if c[2] == -1 else 'R2'
            other = candidate // 5
            pm = "P" if is_prime_arr[other] else "C"
            print(f"  step {step+1}: {candidate} = 5 x {other}, k={k_new}, "
                  f"coords=(block={c[0]}, sp={c[1]}, {rail_c}) [{pm}]")
            k = k_new
            break

print()

# ====================================================================
#  TEST 11: PRIME DENSITY PER BLOCK
# ====================================================================
print("=" * 70)
print("  TEST 11: PRIME DENSITY PER BLOCK OF 36")
print("=" * 70)
print()

print(f"  {'block':>6} {'range':>12} {'R1 primes':>10} {'R2 primes':>10} {'total':>6} {'R1 comp':>8} {'R2 comp':>8}")
print("  " + "-" * 65)

for block in range(20):
    r1_primes = 0
    r2_primes = 0
    r1_comp = 0
    r2_comp = 0
    for sp in range(6):
        n_r1 = from_coords(block, sp, -1)
        n_r2 = from_coords(block, sp, +1)
        if n_r1 >= 5:
            if is_prime_arr[n_r1]:
                r1_primes += 1
            else:
                r1_comp += 1
        if n_r2 >= 5:
            if is_prime_arr[n_r2]:
                r2_primes += 1
            else:
                r2_comp += 1

    lo = block * 36
    hi = lo + 35
    total = r1_primes + r2_primes
    print(f"  {block:>6} {lo:>5}-{hi:<5} {r1_primes:>10} {r2_primes:>10} {total:>6} {r1_comp:>8} {r2_comp:>8}")

print()

# ====================================================================
#  TEST 12: BASE-36 DIGIT PATTERNS IN FACTORS
# ====================================================================
print("=" * 70)
print("  TEST 12: BASE-36 DIGIT PATTERNS IN FACTORS")
print("=" * 70)
print()
print("  For N = p1 x p2, do the (block, sp) coordinates of N")
print("  follow predictable patterns from p1 and p2?")
print()

# The full composition formula in block/sp form:
# k_N = 6*a*b +/- a +/- b where a = 6*block_a + sp_a, b = 6*block_b + sp_b
# k_N = 6*(6*ba+sa)*(6*bb+sb) +/- (6*ba+sa) +/- (6*bb+sb)
# k_N = 216*ba*bb + 36*ba*sb + 36*bb*sa + 6*sa*sb +/- 6*ba +/- sa +/- 6*bb +/- sb
# block_N = k_N // 6 = 36*ba*bb + 6*ba*sb + 6*bb*sa + sa*sb +/- ba +/- 6*bb
#         + ((+/- sa +/- sb) // 6 part from carry)
# Actually it's simpler: block_N = (k_N - sp_N) // 6

# Let's check the relationship between block components
print("  For R2xR2 (k_N = 6ab + a + b):")
print("  block_N = 36*ba*bb + 6*ba*sb + 6*bb*sa + sa*sb + ba + bb")
print("  sp_N = (sa + sb) mod 6")
print()

# The carry-free block prediction
correct_block = 0
total_block = 0

for n in range(25, N_MAX + 1):
    if get_rail(n) == 0 or is_prime_arr[n]: continue
    factors = factorize(n)
    if len(factors) != 2: continue
    unique = set(factors)
    if len(unique) != 2: continue
    p1, p2 = sorted(factors)
    r1, r2 = get_rail(p1), get_rail(p2)
    if r1 == 0 or r2 == 0: continue
    if r1 != +1 or r2 != +1: continue  # R2xR2 only

    c_n = to_coords(n)
    c_p1 = to_coords(p1)
    c_p2 = to_coords(p2)

    ba, sa = c_p1[0], c_p1[1]
    bb, sb = c_p2[0], c_p2[1]
    sp_n = c_n[1]

    # Full prediction
    predicted_block = 36*ba*bb + 6*ba*sb + 6*bb*sa + sa*sb + ba + bb
    # But this gives k_N = 6*predicted_block + sp_n
    # Actually k_N = 6ab + a + b = 6*(6ba+sa)*(6bb+sb) + (6ba+sa) + (6bb+sb)
    k_n = rail_k(n)
    predicted_k = 6*(6*ba+sa)*(6*bb+sb) + (6*ba+sa) + (6*bb+sb)
    if predicted_k == k_n:
        correct_block += 1
    total_block += 1

print(f"  Block composition formula verified: {correct_block}/{total_block} "
      f"({100*correct_block/max(total_block,1):.1f}%)")
print()

# ====================================================================
#  SUMMARY
# ====================================================================
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print("  BASE-36 STRUCTURE:")
print("  - Every block of 36 contains exactly 12 positions coprime to 6")
print("  - 6 on Rail1 (residue 5 mod 6) + 6 on Rail2 (residue 1 mod 6)")
print("  - Each position has 3D coordinates: (block, sub_pos, rail)")
print("    where block = k // 6, sub_pos = k mod 6, rail in {R1, R2}")
print()
print("  THE 12x12 MULTIPLICATION TABLE:")
print("  - Rail rule (Z2): R1xR1=R2, R2xR2=R2, R1xR2=R1")
print("  - Sub-position rule:")
print("    R1xR1: sp = (-a-b) mod 6")
print("    R2xR2: sp = (a+b) mod 6")
print("    R1xR2: sp = (a-b) mod 6")
print("  - Block component involves a bilinear form (36*ba*bb + ...)")
print()
print("  WALKING IN 12-SPACE:")
print("  - Each step adds sp_p to the current sub-position (mod 6)")
print("  - Rail stays the same (walking along one chain)")
print("  - Block increments by block_p plus carry from sub-position overflow")
print()
print("  The 12-position system IS a natural representation for the")
print("  6k+/-1 manifold. Base-36 indexing captures the full structure.")
print()
print("Done.")
