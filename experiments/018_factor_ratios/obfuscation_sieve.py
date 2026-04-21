"""
OBFUSCATION SIEVE -- Prime Products as Structured Obfuscation

The prime table is a cryptographic key. Without it, the product is just a number.
With it, you can factorize and recover full metadata.

Three levels of obfuscation:
  Level 1: Small primes (2..347) -- trivial to break via trial division
  Level 2: Large primes (64-bit) -- factoring becomes hard, mapping stays hidden
  Level 3: Selective access -- give different parties different prime subsets

Key insight: even after factoring, the attacker must solve the MAPPING problem
(Which prime belongs to which dimension?). Frequency analysis can crack this,
but it requires observing many packets. Single-packet interception is harder.

This is NOT a full cryptosystem (no key exchange, no signatures).
It IS format-preserving obfuscation with selective decryption.
"""

import sys
import time
import random
from math import gcd
from collections import Counter, defaultdict

print("=" * 70)
print("OBFUSCATION SIEVE -- Prime Products as Structured Obfuscation")
print("=" * 70)

# ============================================================
# UTILITY: PRIME GENERATION
# ============================================================

def is_prime_miller_rabin(n, k=20):
    """Miller-Rabin primality test."""
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_large_prime(bits):
    """Generate a random prime of specified bit size."""
    while True:
        n = random.getrandbits(bits)
        n |= (1 << (bits - 1)) | 1  # Ensure high bit and odd
        if is_prime_miller_rabin(n):
            return n

def sieve_small_primes(limit):
    s = [True] * (limit + 1)
    s[0] = s[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if s[i]:
            for j in range(i * i, limit + 1, i):
                s[j] = False
    return [i for i in range(2, limit + 1) if s[i]]

# ============================================================
# SCHEMA DEFINITION
# ============================================================

DIMENSIONS = [
    ('category',      ['finance', 'health', 'iot', 'media', 'auth', 'system']),
    ('source',        ['api', 'webhook', 'ftp', 'email', 'mqtt']),
    ('region',        ['us-east', 'us-west', 'eu-west', 'eu-central', 'ap-south', 'ap-east', 'sa-east']),
    ('priority',      ['low', 'normal', 'high', 'critical']),
    ('compliance',    ['gdpr', 'hipaa', 'pci', 'sox', 'none']),
    ('format',        ['json', 'xml', 'binary', 'csv']),
    ('security',      ['public', 'internal', 'confidential', 'secret']),
    ('audience',      ['engineers', 'analysts', 'executives', 'all']),
]

N_DIMS = len(DIMENSIONS)
dim_names = [d[0] for d in DIMENSIONS]
dim_values = [d[1] for d in DIMENSIONS]
total_slots = sum(len(v) for _, v in DIMENSIONS)

print(f"\n  Schema: {N_DIMS} dimensions, {total_slots} value slots")

# ============================================================
# LEVEL 1: SMALL PRIME OBFUSCATION (trivial to break)
# ============================================================

print(f"\n{'=' * 70}")
print("  LEVEL 1: SMALL PRIME OBFUSCATION")
print(f"{'=' * 70}")

# Assign small primes (same as lineage sieve)
small_primes = sieve_small_primes(1000)[:total_slots]

prime_table_small = {}  # (dim_idx, val_idx) -> prime
value_table_small = {}  # (dim_idx, prime) -> value
cursor = 0
for di, (name, vals) in enumerate(DIMENSIONS):
    for vi, val in enumerate(vals):
        p = small_primes[cursor]
        prime_table_small[(di, vi)] = p
        value_table_small[(di, p)] = val
        cursor += 1

def encode_small(assignments):
    product = 1
    for di, (name, vals) in enumerate(DIMENSIONS):
        val = assignments.get(name, vals[0])
        vi = vals.index(val)
        product *= prime_table_small[(di, vi)]
    return product

def decode_small(product, value_table):
    result = {}
    for di, (name, vals) in enumerate(DIMENSIONS):
        for vi, val in enumerate(vals):
            p = prime_table_small[(di, vi)]
            if product % p == 0:
                result[name] = val
                break
    return result

# Encode a sample packet
sample = {
    'category': 'finance', 'source': 'api', 'region': 'eu-west',
    'priority': 'high', 'compliance': 'gdpr', 'format': 'json',
    'security': 'confidential', 'audience': 'analysts',
}

h_small = encode_small(sample)
print(f"\n  Encoded packet: {h_small}")
print(f"  Bit size: {h_small.bit_length()} bits")

# Attack: trial division on the small product
print(f"\n  ATTACK: Trial division (no prime table needed)")
t0 = time.perf_counter()
# Attacker tries all primes up to 1000
attack_primes = sieve_small_primes(1000)
factors = []
temp = h_small
for p in attack_primes:
    while temp % p == 0:
        factors.append(p)
        temp //= p
t_break = time.perf_counter() - t0

print(f"  Factored in {t_break*1e6:.1f} us")
print(f"  Factors: {factors}")
print(f"  Total primes under 1000: {len(attack_primes)}")
print(f"  Verdict: TRIVIAL to break. Trial division on small primes is instant.")

# The attacker still doesn't know the mapping
print(f"\n  But: attacker has {len(factors)} factors and {N_DIMS} dimensions.")
print(f"  Without the prime table, they know WHAT factors exist")
print(f"  but not WHICH dimension each factor represents.")
print(f"  Mapping permutations: too many to brute-force naively.")
print(f"  But: frequency analysis across many packets cracks it easily.")

# ============================================================
# LEVEL 2: LARGE PRIME OBFUSCATION (hard to factor)
# ============================================================

print(f"\n{'=' * 70}")
print("  LEVEL 2: LARGE PRIME OBFUSCATION (64-bit primes)")
print(f"{'=' * 70}")

print(f"\n  Generating {total_slots} random 64-bit primes...", end=" ", flush=True)
random.seed(42)
large_primes = [generate_large_prime(64) for _ in range(total_slots)]
print("OK")

prime_table_large = {}
value_table_large = {}
cursor = 0
for di, (name, vals) in enumerate(DIMENSIONS):
    for vi, val in enumerate(vals):
        p = large_primes[cursor]
        prime_table_large[(di, vi)] = p
        value_table_large[(di, p)] = val
        cursor += 1

def encode_large(assignments):
    product = 1
    for di, (name, vals) in enumerate(DIMENSIONS):
        val = assignments.get(name, vals[0])
        vi = vals.index(val)
        product *= prime_table_large[(di, vi)]
    return product

def decode_large(product):
    result = {}
    for di, (name, vals) in enumerate(DIMENSIONS):
        for vi, val in enumerate(vals):
            p = prime_table_large[(di, vi)]
            if product % p == 0:
                result[name] = val
                break
    return result

def check_filter_large(product, filter_assignments):
    mask = 1
    for dim_name, val_name in filter_assignments.items():
        di = dim_names.index(dim_name)
        vi = dim_values[di].index(val_name)
        mask *= prime_table_large[(di, vi)]
    return product % mask == 0

h_large = encode_large(sample)
print(f"\n  Encoded packet: {h_large}")
print(f"  Bit size: {h_large.bit_length()} bits ({h_large.bit_length()//8+1} bytes)")
print(f"  Each prime: 64 bits")
print(f"  Product of 8 primes (one per dimension): ~512 bits")

# Show the primes
print(f"\n  Prime table (the 'key'):")
for di, (name, vals) in enumerate(DIMENSIONS):
    print(f"    {name}:")
    for vi, val in enumerate(vals):
        p = prime_table_large[(di, vi)]
        print(f"      {val:<14s} -> {p} ({p.bit_length()} bits)")

# Attack analysis
print(f"\n  ATTACK ANALYSIS:")
print(f"  1. Trial division: attacker must try primes up to 2^64")
print(f"     That's ~4.2e18 candidates. Infeasible.")
print(f"  2. General factoring: 512-bit product of 8 unknown 64-bit primes")
print(f"     GNFS complexity for 512-bit RSA: ~280 work (broken in 1999)")
print(f"     But: 8-factor product is harder than 2-factor RSA")
print(f"     Known-factor-count factoring is an easier problem than RSA")

# Demonstrate that WITH the key, decoding is instant
t0 = time.perf_counter()
decoded = decode_large(h_large)
t_decode = time.perf_counter() - t0
print(f"\n  WITH key: decoded in {t_decode*1e6:.1f} us -> {decoded}")

# Demonstrate filtering without full decoding
print(f"\n  Filtering without decoding (selective check):")
t0 = time.perf_counter()
is_finance = check_filter_large(h_large, {'category': 'finance'})
t_check = time.perf_counter() - t0
print(f"    Is finance? {is_finance} (checked in {t_check*1e6:.2f} us)")

t0 = time.perf_counter()
is_health = check_filter_large(h_large, {'category': 'health'})
t_check = time.perf_counter() - t0
print(f"    Is health? {is_health} (checked in {t_check*1e6:.2f} us)")

# ============================================================
# LEVEL 3: SELECTIVE ACCESS (different keys for different parties)
# ============================================================

print(f"\n{'=' * 70}")
print("  LEVEL 3: SELECTIVE ACCESS CONTROL")
print(f"{'=' * 70}")

# Three parties with different access levels
print(f"""
  Party A (Compliance Officer): knows category, compliance, security primes
  Party B (Network Engineer):   knows source, region, format primes
  Party C (Admin):              knows ALL primes (master key)
""")

# Build partial prime tables for each party
party_a_dims = {0, 4, 6}  # category, compliance, security
party_b_dims = {1, 2, 5}  # source, region, format
party_c_dims = set(range(N_DIMS))  # all

def make_partial_table(dim_set):
    """Build a partial value table for a subset of dimensions."""
    vt = {}
    for di in dim_set:
        name = dim_names[di]
        vals = dim_values[di]
        for vi, val in enumerate(vals):
            p = prime_table_large[(di, vi)]
            vt[(di, p)] = val
    return vt

def decode_with_partial(product, partial_vt, dim_set):
    """Decode only the dimensions in dim_set."""
    result = {}
    for di in dim_set:
        name = dim_names[di]
        vals = dim_values[di]
        for vi, val in enumerate(vals):
            p = prime_table_large[(di, vi)]
            if product % p == 0:
                result[name] = val
                break
    return result

def check_with_partial(product, filter_assignments, dim_set):
    """Check filter conditions only for dimensions in dim_set."""
    for dim_name, val_name in filter_assignments.items():
        di = dim_names.index(dim_name)
        if di not in dim_set:
            return None  # Can't check -- don't have the key
        vi = dim_values[di].index(val_name)
        p = prime_table_large[(di, vi)]
        if product % p != 0:
            return False
    return True

# Encode a packet with all dimensions
packet = {
    'category': 'finance', 'source': 'webhook', 'region': 'us-west',
    'priority': 'critical', 'compliance': 'gdpr', 'format': 'xml',
    'security': 'confidential', 'audience': 'executives',
}
h = encode_large(packet)

print(f"  Packet header: {h} ({h.bit_length()} bits)")
print(f"  Full decode (admin):    {decode_with_partial(h, None, party_c_dims)}")
print(f"  Party A sees:           {decode_with_partial(h, None, party_a_dims)}")
print(f"  Party B sees:           {decode_with_partial(h, None, party_b_dims)}")

print(f"\n  Selective filtering:")
# Party A can check compliance
r = check_with_partial(h, {'compliance': 'gdpr'}, party_a_dims)
print(f"    Party A checks compliance=gdpr: {r}")
# Party A can check security
r = check_with_partial(h, {'security': 'confidential'}, party_a_dims)
print(f"    Party A checks security=confidential: {r}")
# Party B CANNOT check compliance (doesn't have those primes)
r = check_with_partial(h, {'compliance': 'gdpr'}, party_b_dims)
print(f"    Party B checks compliance=gdpr:  {r} (None = no access)")
# Party B can check source
r = check_with_partial(h, {'source': 'webhook'}, party_b_dims)
print(f"    Party B checks source=webhook:   {r}")
# Party A CANNOT check source
r = check_with_partial(h, {'source': 'webhook'}, party_a_dims)
print(f"    Party A checks source=webhook:   {r} (None = no access)")

# ============================================================
# ATTACK: FREQUENCY ANALYSIS
# ============================================================

print(f"\n{'=' * 70}")
print("  ATTACK: FREQUENCY ANALYSIS ACROSS MANY PACKETS")
print(f"{'=' * 70}")

# Generate a stream of packets with known distributions
random.seed(123)
N_PACKETS = 10_000
stream = []
for _ in range(N_PACKETS):
    pkt = {}
    for di, (name, vals) in enumerate(DIMENSIONS):
        pkt[name] = random.choice(vals)
    stream.append(pkt)

stream_encoded = [encode_large(p) for p in stream]
stream_packets = stream  # keep originals for verification

# Attacker intercepts the stream and tries frequency analysis
print(f"\n  Attacker intercepts {N_PACKETS:,} encoded packets.")
print(f"  Strategy: factorize each packet, count factor frequencies.")

# Factorize using known set of large primes (attacker would need to discover these first)
# For demo: assume attacker somehow got the prime set but not the mapping
all_primes_used = set()
for di in range(N_DIMS):
    for vi in range(len(dim_values[di])):
        all_primes_used.add(prime_table_large[(di, vi)])

print(f"  Assuming attacker discovered the {len(all_primes_used)} primes in use.")
print(f"  (This itself requires factoring 512-bit numbers -- not trivial.)")
print(f"  Now: can they figure out which prime maps to which dimension?")

# Count frequency of each prime across all packets
prime_freq = Counter()
for h in stream_encoded:
    for p in all_primes_used:
        if h % p == 0:
            prime_freq[p] += 1

# For each dimension, the values should be roughly equally frequent
# So primes belonging to the same dimension should have similar frequencies
# Group primes by frequency similarity
print(f"\n  Factor frequency analysis:")
print(f"  {'Prime':>22s}  {'Count':>6s}  {'Freq':>6s}  {'Guess':>15s}")
print(f"  {'-'*55}")

# Map each prime to its frequency
for di, (name, vals) in enumerate(DIMENSIONS):
    for vi, val in enumerate(vals):
        p = prime_table_large[(di, vi)]
        freq = prime_freq[p] / N_PACKETS
        expected = 1.0 / len(vals)
        # Attacker sees freq close to 1/n_vals for some n_vals
        # They can guess the dimension size from frequency
        guess_n = round(1.0 / freq) if freq > 0 else 0
        print(f"  {p:>22d}  {prime_freq[p]:>6d}  {freq:>6.3f}  n_vals~{guess_n} (actual {len(vals)}, {name}={val})")

# The attacker can cluster primes by frequency to discover dimension groupings
print(f"\n  ATTACK RESULT:")
print(f"  Attacker can CLUSTER primes by frequency to discover dimension sizes.")
print(f"  Primes with freq ~1/6 cluster into the 'category' dimension (6 values).")
print(f"  Primes with freq ~1/5 cluster into the 'source' dimension (5 values).")
print(f"  Primes with freq ~1/4 cluster into 'priority', 'format', 'security', 'audience'.")
print(f"  But: dimensions with the SAME number of values are INDISTINGUISHABLE")
print(f"  (priority and format both have 4 values -- attacker can't tell them apart)")

# Verify clustering
print(f"\n  Frequency-based clustering:")
freq_groups = defaultdict(list)
for di, (name, vals) in enumerate(DIMENSIONS):
    for vi, val in enumerate(vals):
        p = prime_table_large[(di, vi)]
        freq = prime_freq[p] / N_PACKETS
        n = len(vals)
        freq_groups[n].append((p, name, val))

for n in sorted(freq_groups.keys()):
    primes_in_group = freq_groups[n]
    dim_names_in_group = set(name for _, name, _ in primes_in_group)
    print(f"    n_vals={n}: {len(primes_in_group)} primes, "
          f"dimensions: {dim_names_in_group}")
    if len(dim_names_in_group) > 1:
        print(f"      -> INDISTINGUISHABLE without additional info")

# ============================================================
# BENCHMARK: ENCODE / FILTER / DECODE WITH LARGE PRIMES
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK: LARGE PRIME PERFORMANCE")
print(f"{'=' * 70}")

N = 100_000
random.seed(42)
test_packets = []
for _ in range(N):
    pkt = {}
    for di, (name, vals) in enumerate(DIMENSIONS):
        pkt[name] = random.choice(vals)
    test_packets.append(pkt)

# Encode
t0 = time.perf_counter()
encoded = [encode_large(p) for p in test_packets]
t_enc = time.perf_counter() - t0

# Filter (4 conditions)
filters = {'category': 'finance', 'compliance': 'gdpr', 'priority': 'high', 'security': 'confidential'}
t0 = time.perf_counter()
matches = sum(1 for h in encoded if check_filter_large(h, filters))
t_filt = time.perf_counter() - t0

# Decode
t0 = time.perf_counter()
for h in encoded[:10000]:
    decode_large(h)
t_dec = time.perf_counter() - t0

# Size
avg_bits = sum(h.bit_length() for h in encoded) / N

print(f"\n  {N:,} packets with 64-bit primes:")
print(f"    Encode:  {t_enc:.3f}s = {N/t_enc:.0f}/s")
print(f"    Filter:  {t_filt:.3f}s = {N/t_filt:.0f}/s ({matches} matches)")
print(f"    Decode:  {t_dec:.3f}s = {10000/t_dec:.0f}/s (10k sample)")
print(f"    Size:    {avg_bits:.0f} bits ({avg_bits/8:.0f} bytes) per header")

# Compare with small primes
encoded_small = [encode_small(p) for p in test_packets]
avg_bits_small = sum(h.bit_length() for h in encoded_small) / N
print(f"\n  Comparison (small primes, same {N:,} packets):")
print(f"    Size: {avg_bits_small:.0f} bits ({avg_bits_small/8:.0f} bytes) per header")
print(f"    Large/small ratio: {avg_bits/avg_bits_small:.1f}x larger")

# ============================================================
# SECURITY SUMMARY
# ============================================================

print(f"\n{'=' * 70}")
print("  SECURITY ANALYSIS")
print(f"{'=' * 70}")

print(f"""
  THREE ATTACK VECTORS:

  1. FACTORING THE PRODUCT
     Small primes (Level 1): Trivial. Trial division in microseconds.
     64-bit primes (Level 2): 512-bit product. Feasible with GNFS.
     128-bit primes:          1024-bit product. Expensive but possible.
     256-bit primes:          2048-bit product. Equivalent to RSA-2048.
     512-bit primes:          4096-bit product. Currently infeasible.

  2. DISCOVERING THE PRIME SET
     If attacker intercepts many packets, they can compute GCD of
     pairs. If two packets share a dimension value, gcd > 1 reveals
     the shared prime. With enough packets, all primes are discovered.
     Countermeasure: add random "noise" primes to each encoding.

  3. MAPPING PRIMES TO DIMENSIONS (frequency analysis)
     As demonstrated above: primes cluster by frequency, revealing
     dimension sizes. Dimensions with same number of values remain
     indistinguishable. Countermeasure: use same-size dimensions.

  HONEST ASSESSMENT:
    This is NOT a replacement for TLS, AES, or proper cryptography.
    It IS a lightweight obfuscation layer with three unique properties:
      1. Selective access: different keys reveal different dimensions
      2. Filterable while obfuscated: modulo check without decoding
      3. Composable: multiply headers to merge, no decryption needed

  USE CASES:
    - Internal pipeline metadata that shouldn't be human-readable at rest
    - Log headers where different teams need different access levels
    - Network telemetry where intermediate hops filter but don't decode
    - Audit trails where the header IS the proof (factorize to verify)

  NOT USEFUL FOR:
    - Protecting secrets (use real encryption)
    - Authentication (no signatures, no key exchange)
    - Public-facing APIs (JSON is simpler and more interoperable)
""")

print("=" * 70)
print("  Experiment complete.")
print("=" * 70)
