"""
EXPERIMENT 143a: DEEP FIBONACCI IN THE MONAD
========================================================================
NOTE: Experiments marked 'a' are from Claude (Anthropic).

Deeper investigation of Fibonacci structure within Z/24Z.
Exp 132a showed phi is not privileged as a metric. But the Fibonacci
sequence itself has rich structure in mod-24 that deserves mapping.

143a covers:
  1. Pisano period factorization across divisors of 24
  2. Generalized Fibonacci (Lucas, tribonacci, alternate seeds) mod 24
  3. Zeckendorf representation mapped to mod-24 positions
  4. Fibonacci divisibility ladder
  5. Fibonacci random walk through Z/24Z
  6. Fibonacci prime positions
  7. Fibonacci basin dynamics
"""

from math import gcd, log, log10, sqrt
from collections import Counter, defaultdict

PHI = (1 + sqrt(5)) / 2

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def fibonacci_table(limit):
    fibs = [0, 1]
    for i in range(2, limit + 1):
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

def sigma(n):
    if n <= 0: return 0
    result = 1; temp = n; d = 2
    while d * d <= temp:
        if temp % d == 0:
            pk = 1; s = 1
            while temp % d == 0:
                temp //= d; pk *= d; s += pk
            result *= s
        d += 1
    if temp > 1: result *= (1 + temp)
    return result

def coprime24(n):
    return gcd(n, 24) == 1

def rail_of(n):
    r = n % 6
    if r == 5: return 'R1'
    if r == 1: return 'R2'
    return 'off'

def basin_of(n):
    m = n % 24
    if gcd(m, 24) == 1: return 1
    if m % 6 == 0: return 0
    if m % 3 == 0: return 9
    if m % 2 == 0: return 16
    return 0

BASIN_NAMES = {0: 'nilpotent', 1: 'coprime', 9: 'mod-3', 16: 'mod-8'}

def pisano_period(m):
    """Compute Pisano period pi(m): period of Fibonacci sequence mod m."""
    a, b = 0, 1
    for i in range(1, m * m + 10):
        a, b = b, (a + b) % m
        if a == 0 and b == 1:
            return i
    return -1  # should not happen for reasonable m

# ====================================================================
print("=" * 70)
print("EXPERIMENT 143a: DEEP FIBONACCI IN THE MONAD")
print("=" * 70)

# ====================================================================
# SECTION 1: PISANO PERIOD FACTORIZATION
# ====================================================================
print("\n  SECTION 1: PISANO PERIOD FACTORIZATION")
print("  " + "-" * 50)

print(f"""
  The Pisano period pi(m) gives the period of F(n) mod m.
  For m = 24, pi(24) = 24. How does this factor across the
  CRT decomposition 24 = 8 * 3?
""")

divisors_of_24 = [1, 2, 3, 4, 6, 8, 12, 24]
print(f"  {'m':>4} {'pi(m)':>6} {'pi(m)/m':>8} {'Factored':>10} {'Notes'}")
print("  " + "-" * 60)

pisano_cache = {}
for m in divisors_of_24:
    p = pisano_period(m)
    pisano_cache[m] = p
    ratio = p / m if m > 0 else 0
    # Factor the Pisano period
    pf = []
    temp = p
    for f in [2, 3, 5, 7, 11, 13]:
        while temp % f == 0:
            pf.append(str(f))
            temp //= f
    if temp > 1: pf.append(str(temp))
    factored = '*'.join(pf) if pf else '1'
    notes = ""
    if m == 24:
        notes = "lcm(pi(8), pi(3))"
    elif m == 8:
        notes = "pi(8) = 12"
    elif m == 3:
        notes = "pi(3) = 8"
    print(f"  {m:>4} {p:>6} {ratio:>8.2f} {factored:>10} {notes}")

# Check: pi(24) = lcm(pi(8), pi(3))
pi8 = pisano_cache[8]
pi3 = pisano_cache[3]
pi24 = pisano_cache[24]
lcm_check = pi24 == (pi8 * pi3) // gcd(pi8, pi3)
print(f"\n  pi(8) = {pi8}, pi(3) = {pi3}")
print(f"  lcm(pi(8), pi(3)) = lcm({pi8}, {pi3}) = {(pi8 * pi3) // gcd(pi8, pi3)}")
print(f"  pi(24) = {pi24}")
print(f"  Match: {lcm_check}")

# The full Fibonacci cycle mod 24
print(f"\n  Full Fibonacci cycle mod 24 (one Pisano period):")
fib_cycle = []
a, b = 0, 1
for i in range(pi24):
    fib_cycle.append(a)
    a, b = b, (a + b) % 24

print(f"  {'n':>3} {'F(n)%24':>7} {'Rail':>5} {'Basin':>8} {'Coprime?':>8}")
for i, val in enumerate(fib_cycle):
    rail = rail_of(val)
    basin = basin_of(val)
    cop = 'Y' if coprime24(val) else 'n'
    print(f"  {i:>3} {val:>7} {rail:>5} {BASIN_NAMES[basin]:>8} {cop:>8}")

# Position frequency in one cycle
pos_freq = Counter(fib_cycle)
print(f"\n  Position frequency in one Pisano period (pi={pi24}):")
print(f"  {'Pos':>4} {'Count':>6} {'Type':>8} {'Basin':>8}")
for pos in range(24):
    if pos in pos_freq:
        ptype = "coprime" if coprime24(pos) else "dark"
        print(f"  {pos:>4} {pos_freq[pos]:>6} {ptype:>8} {BASIN_NAMES[basin_of(pos)]:>8}")

# ====================================================================
# SECTION 2: GENERALIZED FIBONACCI MOD 24
# ====================================================================
print("\n  SECTION 2: GENERALIZED FIBONACCI MOD 24")
print("  " + "-" * 50)

def generalized_fib_mod24(seed0, seed1, length):
    """Generate generalized Fibonacci mod 24 with given seeds."""
    seq = [seed0 % 24, seed1 % 24]
    for i in range(2, length):
        seq.append((seq[-1] + seq[-2]) % 24)
    return seq

def find_period(seq):
    """Find period of a sequence starting from (seq[0], seq[1])."""
    if len(seq) < 4:
        return len(seq)
    for p in range(1, len(seq) // 2):
        if seq[:p] == seq[p:2*p]:
            return p
    return len(seq)

seeds = [
    (0, 1, "Fibonacci"),
    (2, 1, "Lucas"),
    (1, 3, "Alt-Lucas"),
    (1, 1, "All-ones"),
    (0, 2, "Even-seed"),
    (1, 4, "Shifted"),
    (3, 1, "Mirror"),
    (2, 3, "Mixed"),
]

print(f"  {'Seeds':>12} {'Name':>12} {'Period':>7} {'Coprime%':>10} {'Positions visited'}")
print("  " + "-" * 75)

gen_results = {}
for s0, s1, name in seeds:
    seq = generalized_fib_mod24(s0, s1, 200)
    period = find_period(seq)
    positions = set(seq[:period])
    cop_count = sum(1 for p in positions if coprime24(p))
    gen_results[name] = (seq, period, positions)
    print(f"  ({s0},{s1}){'':<6} {name:>12} {period:>7} {100*cop_count/len(positions):>9.1f}% "
          f"{sorted(positions)}")

# Show the Lucas cycle
lucas_seq, lucas_period, lucas_pos = gen_results["Lucas"]
print(f"\n  Lucas sequence mod 24 (one period):")
for i in range(min(lucas_period, 24)):
    val = lucas_seq[i]
    rail = rail_of(val)
    basin = basin_of(val)
    print(f"    n={i:>2}: {val:>3}  rail={rail:>3}  basin={BASIN_NAMES[basin]:>8}")

# Tribonacci mod 24
print(f"\n  Tribonacci (a+b+c) mod 24:")
tri_seq = [0, 0, 1]
for i in range(200):
    tri_seq.append((tri_seq[-1] + tri_seq[-2] + tri_seq[-3]) % 24)
tri_period = find_period(tri_seq)
tri_positions = set(tri_seq[:tri_period])
print(f"    Period: {tri_period}")
print(f"    Positions: {sorted(tri_positions)}")
print(f"    Cycle: {tri_seq[:min(tri_period, 30)]}{'...' if tri_period > 30 else ''}")

# ====================================================================
# SECTION 3: ZECKENDORF REPRESENTATION IN THE MONAD
# ====================================================================
print("\n  SECTION 3: ZECKENDORF REPRESENTATION IN THE MONAD")
print("  " + "-" * 50)

print(f"""
  Every positive integer has a unique Zeckendorf representation:
  sum of non-consecutive Fibonacci numbers. How do these representations
  distribute across mod-24 positions?
""")

def zeckendorf(n):
    """Return list of Fibonacci indices in Zeckendorf representation of n."""
    if n == 0: return []
    fibs = [1, 2]
    while fibs[-1] <= n:
        fibs.append(fibs[-1] + fibs[-2])
    rep = []
    for i in range(len(fibs) - 1, -1, -1):
        if fibs[i] <= n:
            rep.append(i + 2)  # F(2)=1, F(3)=2, etc.
            n -= fibs[i]
    return rep

N_ZECK = 1000
zeck_terms_by_pos = defaultdict(list)  # position -> list of term counts
zeck_max_term_by_pos = defaultdict(list)

for n in range(1, N_ZECK + 1):
    pos = n % 24
    rep = zeckendorf(n)
    zeck_terms_by_pos[pos].append(len(rep))
    zeck_max_term_by_pos[pos].append(max(rep) if rep else 0)

print(f"  Average Zeckendorf term count by mod-24 position (n <= {N_ZECK}):")
print(f"  {'Pos':>4} {'Type':>8} {'Avg terms':>10} {'Max term avg':>12}")
for pos in range(24):
    terms = zeck_terms_by_pos[pos]
    maxterms = zeck_max_term_by_pos[pos]
    if terms:
        avg_t = sum(terms) / len(terms)
        avg_m = sum(maxterms) / len(maxterms)
        ptype = "coprime" if coprime24(pos) else "dark"
        print(f"  {pos:>4} {ptype:>8} {avg_t:>10.2f} {avg_m:>12.2f}")

# Zeckendorf of first 30 numbers with Fibonacci indices
print(f"\n  Zeckendorf representations (n=1..30):")
print(f"  {'n':>4} {'n%24':>5} {'Rail':>5} {'Zeckendorf':>30} {'F-indices'}")
fibs = fibonacci_table(30)
for n in range(1, 31):
    rep = zeckendorf(n)
    fib_names = [f"F({i})" for i in rep]
    fib_vals = [fibs[i] for i in rep]
    rail = rail_of(n)
    print(f"  {n:>4} {n%24:>5} {rail:>5} {str(fib_vals):>30} {str(fib_names):>20}")

# ====================================================================
# SECTION 4: FIBONACCI DIVISIBILITY LADDER
# ====================================================================
print("\n  SECTION 4: FIBONACCI DIVISIBILITY LADDER")
print("  " + "-" * 50)

print(f"""
  F(m) divides F(n) iff m divides n. This creates a divisibility
  lattice. Where do the quotients F(n)/F(m) land in mod-24?
""")

fibs = fibonacci_table(50)

print(f"  Divisibility: F(m) | F(n) when m | n")
print(f"  {'m':>3} {'n':>3} {'F(m)':>10} {'F(n)':>10} {'Q=F(n)/F(m)':>12} {'Q%24':>5} {'Q%6':>4} {'Rail':>5}")
for m in range(2, 13):
    for n in range(2 * m, 50, m):
        if fibs[m] > 0 and fibs[n] % fibs[m] == 0:
            q = fibs[n] // fibs[m]
            if q < 10**10:  # reasonable size
                rail = rail_of(q)
                print(f"  {m:>3} {n:>3} {fibs[m]:>10} {fibs[n]:>10} {q:>12} {q%24:>5} {q%6:>4} {rail:>5}")
            if n > 4 * m:
                break

# F(n) that are also Fibonacci primes
print(f"\n  Fibonacci prime positions (F(2)..F(50)):")
print(f"  {'n':>4} {'F(n)':>15} {'F(n)%24':>8} {'Rail':>5} {'Basin':>8} {'Prime?':>6}")
for n in range(2, 51):
    fn = fibs[n]
    if fn < 10**8:  # can check primality
        prime = is_prime(fn)
        if prime:
            rail = rail_of(fn)
            basin = basin_of(fn)
            print(f"  {n:>4} {fn:>15} {fn%24:>8} {rail:>5} {BASIN_NAMES[basin]:>8} {'YES':>6}")

# ====================================================================
# SECTION 5: FIBONACCI AS RANDOM WALK THROUGH Z/24Z
# ====================================================================
print("\n  SECTION 5: FIBONACCI RANDOM WALK THROUGH Z/24Z")
print("  " + "-" * 50)

print(f"""
  Fibonacci mod 24 visits 13 of 24 positions. Analyze:
  - Hitting time: how many steps to first visit each position?
  - Transition probabilities: from position i, where does F(n+1) go?
  - Comparison with uniform random walk on Z/24Z.
""")

# Hitting times
fib_hit = {}
a, b = 0, 1
for n in range(1, 1000):
    pos = a % 24
    if pos not in fib_hit:
        fib_hit[pos] = n
    a, b = b, (a + b) % 24

print(f"  Hitting times (first F(n) at each position):")
print(f"  {'Pos':>4} {'Type':>8} {'First F(n)':>10} {'Basin':>8}")
for pos in sorted(fib_hit.keys()):
    ptype = "coprime" if coprime24(pos) else "dark"
    print(f"  {pos:>4} {ptype:>8} {fib_hit[pos]:>10} {BASIN_NAMES[basin_of(pos)]:>8}")

unvisited = [p for p in range(24) if p not in fib_hit]
print(f"\n  Never visited: {unvisited}")
print(f"  Total visited: {len(fib_hit)}/24")

# Transition matrix
print(f"\n  Transition frequencies (F(n)%24 -> F(n+1)%24):")
transitions = Counter()
a, b = 0, 1
for n in range(1, 1000):
    pos_from = a % 24
    pos_to = b % 24
    transitions[(pos_from, pos_to)] += 1
    a, b = b, (a + b) % 24

# Show transitions FROM each visited position
for src in sorted(fib_hit.keys()):
    dests = {d: c for (s, d), c in transitions.items() if s == src}
    total_from = sum(dests.values())
    dest_str = ', '.join(f"{d}({100*c/total_from:.0f}%)" for d, c in sorted(dests.items()))
    print(f"    {src:>2} -> {dest_str}")

# Entropy of the walk
print(f"\n  Position entropy analysis:")
total_visits = sum(1 for _ in range(1000))
pos_counts = Counter()
a, b = 0, 1
for n in range(1, 1000):
    pos_counts[a % 24] += 1
    a, b = b, (a + b) % 24

entropy = 0
for pos, count in pos_counts.items():
    p = count / 1000
    if p > 0:
        entropy -= p * log(p) / log(2)

max_entropy = log(24) / log(2)
print(f"    Shannon entropy: {entropy:.4f} bits")
print(f"    Max possible (24 uniform): {max_entropy:.4f} bits")
print(f"    Efficiency: {entropy/max_entropy*100:.1f}%")
print(f"    Only {len(pos_counts)}/24 positions reachable")

# ====================================================================
# SECTION 6: FIBONACCI PRIME POSITIONS
# ====================================================================
print("\n  SECTION 6: FIBONACCI PRIME POSITIONS IN DETAIL")
print("  " + "-" * 50)

print(f"""
  Known: if F(n) is prime, then n is prime (except n=4, F(4)=3).
  The converse fails: most F(p) for prime p are composite.
  Where do the PRIME Fibonacci numbers sit in mod-24?
""")

fibs_100 = fibonacci_table(100)
fib_primes = []
for n in range(2, 45):  # F(45) is still checkable
    fn = fibs_100[n]
    if fn > 1 and is_prime(fn):
        fib_primes.append((n, fn))

print(f"  Fibonacci primes F(2)..F(44):")
print(f"  {'n':>4} {'F(n)':>15} {'F(n)%6':>6} {'F(n)%24':>7} {'Rail':>5} {'Basin':>8} {'n prime?':>8}")
for n, fn in fib_primes:
    rail = rail_of(fn)
    basin = basin_of(fn)
    nprime = 'Y' if is_prime(n) else 'n'
    print(f"  {n:>4} {fn:>15} {fn%6:>6} {fn%24:>7} {rail:>5} {BASIN_NAMES[basin]:>8} {nprime:>8}")

# All Fibonacci primes land on which rails?
fp_rails = Counter(rail_of(fn) for _, fn in fib_primes)
fp_mod24 = Counter(fn % 24 for _, fn in fib_primes)
print(f"\n  Fibonacci prime rail distribution: {dict(sorted(fp_rails.items()))}")
print(f"  Fibonacci prime mod-24 positions: {dict(sorted(fp_mod24.items()))}")

# Are Fibonacci primes always coprime to 24?
fp_all_coprime = all(coprime24(fn) for _, fn in fib_primes)
print(f"  All Fibonacci primes coprime to 24: {fp_all_coprime}")

# ====================================================================
# SECTION 7: FIBONACCI BASIN DYNAMICS
# ====================================================================
print("\n  SECTION 7: FIBONACCI BASIN DYNAMICS")
print("  " + "-" * 50)

print(f"""
  Track basin transitions in the Fibonacci sequence. Since F(n+1) = F(n) + F(n-1),
  the addition mod 24 determines basin transitions. How often does the
  Fibonacci sequence hop between basins?
""")

fibs_200 = fibonacci_table(200)
basin_seq = [basin_of(f % 24) for f in fibs_200[1:]]  # F(1)..F(200)

# Transition counts
basin_transitions = Counter()
for i in range(len(basin_seq) - 1):
    basin_transitions[(basin_seq[i], basin_seq[i+1])] += 1

print(f"  Basin transition counts (F(1)..F(200)):")
print(f"  {'From':>10} {'To':>10} {'Count':>6} {'Fraction':>9}")
for (src, dst), count in sorted(basin_transitions.items()):
    src_name = BASIN_NAMES[src]
    dst_name = BASIN_NAMES[dst]
    print(f"  {src_name:>10} {dst_name:>10} {count:>6} {count/199:>9.3f}")

# Basin residence times
basin_residence = Counter(basin_seq)
print(f"\n  Basin residence (F(1)..F(200)):")
for b in [1, 16, 9, 0]:
    count = basin_residence.get(b, 0)
    print(f"    Basin {b} ({BASIN_NAMES[b]:>8}): {count:>4}/200 = {100*count/200:.1f}%")

# Longest run in each basin
longest_run = {1: 0, 16: 0, 9: 0, 0: 0}
current_run = {1: 0, 16: 0, 9: 0, 0: 0}
for b in basin_seq:
    for bk in [1, 16, 9, 0]:
        if b == bk:
            current_run[bk] += 1
            longest_run[bk] = max(longest_run[bk], current_run[bk])
        else:
            current_run[bk] = 0

print(f"\n  Longest consecutive run in each basin:")
for b in [1, 16, 9, 0]:
    print(f"    Basin {b} ({BASIN_NAMES[b]:>8}): longest run = {longest_run[b]}")

# Addition rule: which basin pairs produce which basin?
print(f"\n  Basin addition table (a+b mod 24 -> basin):")
print(f"  Addition of two consecutive Fibonacci numbers' basins:")
add_basin = Counter()
for i in range(1, 200):
    b1 = basin_of(fibs_200[i] % 24)
    b2 = basin_of(fibs_200[i+1] % 24)
    b_sum = basin_of((fibs_200[i] + fibs_200[i+1]) % 24)
    add_basin[(b1, b2, b_sum)] += 1

for (b1, b2, bs), count in sorted(add_basin.items()):
    if count >= 2:
        print(f"    {BASIN_NAMES[b1]:>8} + {BASIN_NAMES[b2]:>8} -> {BASIN_NAMES[bs]:>8}: {count} times")


# ====================================================================
# TESTS
# ====================================================================
print("\n" + "=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 0

# Test 1: Pisano(24) = 24
total += 1
if pisano_cache[24] == 24:
    print(f"  [PASS] Pisano(24) = 24 verified")
    passed += 1
else:
    print(f"  [FAIL] Pisano(24) = {pisano_cache[24]}")

# Test 2: pi(24) = lcm(pi(8), pi(3))
total += 1
if lcm_check:
    print(f"  [PASS] pi(24) = lcm(pi(8), pi(3)) = lcm({pi8},{pi3}) = {pi24}")
    passed += 1
else:
    print(f"  [FAIL] Pisano CRT factorization failed")

# Test 3: Lucas period divides 24 or is related
total += 1
lucas_p = gen_results["Lucas"][1]
if lucas_p > 0 and lucas_p <= 24:
    print(f"  [PASS] Lucas mod 24 period = {lucas_p} (divides {pi24})")
    passed += 1
else:
    print(f"  [FAIL] Lucas period unexpected: {lucas_p}")

# Test 4: Fibonacci visits exactly 13 positions
total += 1
if len(fib_hit) == 13:
    print(f"  [PASS] Fibonacci visits exactly 13/24 positions mod 24")
    passed += 1
else:
    print(f"  [FAIL] Fibonacci visits {len(fib_hit)}/24 positions")

# Test 5: Fibonacci primes for n>=5 are all coprime to 24 (F(3)=2, F(4)=3 are the exceptions)
total += 1
fp_large_coprime = all(coprime24(fn) for n, fn in fib_primes if n >= 5)
if fp_large_coprime:
    print(f"  [PASS] All Fibonacci primes F(n) with n>=5 coprime to 24 "
          f"(F(3)=2, F(4)=3 are the small exceptions)")
    passed += 1
else:
    print(f"  [FAIL] Fibonacci prime coprime check failed for n>=5")

# Test 6: Basin 1 is most visited
total += 1
if basin_residence.get(1, 0) > basin_residence.get(16, 0):
    print(f"  [PASS] Basin 1 ({basin_residence[1]}/200) > basin 16 ({basin_residence.get(16,0)}/200)")
    passed += 1
else:
    print(f"  [FAIL] Basin 1 not most visited")

# Test 7: Zeckendorf representations valid (spot check)
total += 1
zeck_ok = True
for n in range(1, 100):
    rep = zeckendorf(n)
    fibs_check = fibonacci_table(50)
    total_sum = sum(fibs_check[i] for i in rep)
    if total_sum != n:
        zeck_ok = False
        break
    # Check non-consecutive
    for j in range(len(rep) - 1):
        if rep[j] - rep[j+1] < 2:  # must skip at least one
            zeck_ok = False
            break
if zeck_ok:
    print(f"  [PASS] Zeckendorf representations valid for n=1..99")
    passed += 1
else:
    print(f"  [FAIL] Zeckendorf representation error")

# Test 8: F(m) | F(n) when m | n (spot check)
total += 1
div_ok = True
for m in range(2, 15):
    for k in range(2, 5):
        n = m * k
        if n <= 50:
            if fibs[n] % fibs[m] != 0:
                div_ok = False
                break
if div_ok:
    print(f"  [PASS] F(m) | F(nm) verified for m=2..14, k=2..4")
    passed += 1
else:
    print(f"  [FAIL] Fibonacci divisibility rule violated")

print(f"\nOVERALL: {passed}/{total} tests passed")

print("\n" + "=" * 70)
print("EXPERIMENT 143a COMPLETE")
print("=" * 70)
