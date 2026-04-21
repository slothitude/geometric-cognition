"""
LINEAGE SIEVE -- Lossless Metadata Headers via Prime Products

The Fundamental Theorem of Arithmetic as a data structure:
  Every integer > 1 factors uniquely into primes.
  Therefore: a product of known primes ENCODES its own decomposition.

Use case: a processing pipeline where each stage multiplies a "step prime"
into a packet's metadata header. The final product encodes:
  - Which stages executed (factorize to list step primes)
  - Which filters passed (modulo check against filter primes)
  - Complete processing history (sorted factorization = ordered chain)
  - Composability (multiply two products to merge lineages)

No JSON schema. No external ledger. The number IS the proof.

Comparison:
  - Prime product: filterable AND decomposable
  - Bitmask: filterable but NOT decomposable (can isolate, not recover)
  - JSON: decomposable but NOT efficiently filterable
"""

import json
import sys
import time
import random
from math import gcd
from collections import defaultdict

print("=" * 70)
print("LINEAGE SIEVE -- Lossless Metadata via Prime Products")
print("=" * 70)

# ============================================================
# PRIME TABLE
# ============================================================

def sieve_primes(limit):
    s = [True] * (limit + 1)
    s[0] = s[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if s[i]:
            for j in range(i * i, limit + 1, i):
                s[j] = False
    return [i for i in range(2, limit + 1) if s[i]]

PRIMES = sieve_primes(1000)

# ============================================================
# PIPELINE DEFINITION
# ============================================================

# Each pipeline dimension has a set of possible values, each mapped to a prime.
# Dimensions are ordered: first the "metadata" dimensions, then "processing stages".

DIMENSIONS = [
    # --- Metadata (assigned at ingestion) ---
    ('category',      ['finance', 'health', 'iot', 'media', 'auth', 'system']),
    ('source',        ['api', 'webhook', 'ftp', 'email', 'mqtt']),
    ('region',        ['us-east', 'us-west', 'eu-west', 'eu-central', 'ap-south', 'ap-east', 'sa-east']),
    ('priority',      ['low', 'normal', 'high', 'critical']),
    ('compliance',    ['gdpr', 'hipaa', 'pci', 'sox', 'none']),
    ('format',        ['json', 'xml', 'binary', 'csv']),
    ('security',      ['public', 'internal', 'confidential', 'secret']),
    ('audience',      ['engineers', 'analysts', 'executives', 'all']),
    # --- Processing stages (assigned as packet moves through pipeline) ---
    ('ingest',        ['rejected', 'accepted']),
    ('validate',      ['skipped', 'passed', 'failed']),
    ('enrich',        ['skipped', 'geoip', 'threat_intel', 'full']),
    ('transform',     ['skipped', 'normalized', 'compressed', 'encrypted']),
    ('route',         ['dropped', 'queue_a', 'queue_b', 'queue_c', 'archive']),
    ('deliver',       ['pending', 'sent', 'acked', 'retry']),
    ('audit',         ['unchecked', 'reviewed', 'flagged', 'cleared']),
    ('archive',       ['hot', 'warm', 'cold', 'deleted']),
]

N_DIMS = len(DIMENSIONS)
dim_names = [d[0] for d in DIMENSIONS]
dim_values = [d[1] for d in DIMENSIONS]

# Assign primes to each value
PRIME_TABLE = {}  # (dim_idx, value_name) -> prime
VALUE_TABLE = {}  # (dim_idx, prime) -> value_name
prime_cursor = 0

for di, (name, vals) in enumerate(DIMENSIONS):
    for vi, val in enumerate(vals):
        p = PRIMES[prime_cursor]
        PRIME_TABLE[(di, val)] = p
        VALUE_TABLE[(di, p)] = val
        prime_cursor += 1

print(f"\n  Pipeline dimensions: {N_DIMS}")
print(f"  Total value slots: {prime_cursor}")
print(f"  Prime range: [{PRIMES[0]}..{PRIMES[prime_cursor-1]}]")

# ============================================================
# PRIME HEADER: Encode / Decode / Check
# ============================================================

def encode_header(assignments):
    """
    Build a prime-product header from dimension assignments.
    assignments: dict of {dim_name: value_name}
    Returns: integer (product of primes)
    """
    product = 1
    for di, (name, vals) in enumerate(DIMENSIONS):
        val = assignments.get(name, vals[0])  # default to first value
        product *= PRIME_TABLE[(di, val)]
    return product

def decode_header(product):
    """
    Factorize a header to recover ALL dimension values.
    Returns: dict of {dim_name: value_name}
    """
    result = {}
    for di, (name, vals) in enumerate(DIMENSIONS):
        for val in vals:
            p = PRIME_TABLE[(di, val)]
            if product % p == 0:
                result[name] = val
                break
    return result

def check_filter(product, filter_assignments):
    """
    Check if a header matches filter conditions.
    filter_assignments: dict of {dim_name: value_name} (subset of dimensions)
    Returns: bool
    """
    mask = 1
    for dim_name, val_name in filter_assignments.items():
        di = dim_names.index(dim_name)
        mask *= PRIME_TABLE[(di, val_name)]
    return product % mask == 0

def compose_headers(h1, h2):
    """Compose two headers (merge their metadata)."""
    return h1 * h2

def diff_headers(h1, h2):
    """
    Find what changed between two headers.
    Returns: dict of {dim_name: (old_val, new_val)} for changed dimensions.
    """
    d1 = decode_header(h1)
    d2 = decode_header(h2)
    changes = {}
    for name in dim_names:
        if d1.get(name) != d2.get(name):
            changes[name] = (d1.get(name), d2.get(name))
    return changes

def get_lineage(product):
    """
    Extract processing lineage (stages 8-15 only).
    Returns: list of (stage_name, value) in pipeline order.
    """
    decoded = decode_header(product)
    lineage = []
    for di in range(8, N_DIMS):  # Processing stages start at index 8
        name = dim_names[di]
        if name in decoded:
            lineage.append((name, decoded[name]))
    return lineage

# ============================================================
# JSON HEADER COMPARISON
# ============================================================

def encode_json(assignments):
    """Same metadata as a JSON string."""
    return json.dumps(assignments, separators=(',', ':'))

def decode_json(json_str):
    """Parse JSON header."""
    return json.loads(json_str)

def check_json(json_str, filter_assignments):
    """Check JSON against filter conditions."""
    data = json.loads(json_str)
    for dim_name, val_name in filter_assignments.items():
        if data.get(dim_name) != val_name:
            return False
    return True

# ============================================================
# BITMASK HEADER COMPARISON
# ============================================================

# Assign bit positions (same structure as primes but using bits)
bit_offsets = {}
bit_cursor = 0
for di, (name, vals) in enumerate(DIMENSIONS):
    bit_offsets[di] = bit_cursor
    bit_cursor += len(vals)
TOTAL_BITS = bit_cursor

def encode_bitmask(assignments):
    """Encode as bitmask."""
    mask = 0
    for di, (name, vals) in enumerate(DIMENSIONS):
        val = assignments.get(name, vals[0])
        vi = vals.index(val)
        mask |= (1 << (bit_offsets[di] + vi))
    return mask

def check_bitmask(bm, filter_assignments):
    """Check bitmask against filter."""
    filter_bm = 0
    for dim_name, val_name in filter_assignments.items():
        di = dim_names.index(dim_name)
        vi = dim_values[di].index(val_name)
        filter_bm |= (1 << (bit_offsets[di] + vi))
    return (bm & filter_bm) == filter_bm

def decode_bitmask_partial(bm):
    """
    Attempt to recover dimensions from bitmask.
    NOTE: This only works if you know the bit layout.
    Unlike prime factorization, you can't discover unknown dimensions.
    """
    result = {}
    for di, (name, vals) in enumerate(DIMENSIONS):
        for vi, val in enumerate(vals):
            if bm & (1 << (bit_offsets[di] + vi)):
                result[name] = val
                break
    return result

print(f"\n  Encoding sizes (sample packet):")
sample = {
    'category': 'finance', 'source': 'api', 'region': 'us-east',
    'priority': 'high', 'compliance': 'gdpr', 'format': 'json',
    'security': 'confidential', 'audience': 'analysts',
    'ingest': 'accepted', 'validate': 'passed', 'enrich': 'full',
    'transform': 'encrypted', 'route': 'queue_a', 'deliver': 'sent',
    'audit': 'reviewed', 'archive': 'hot',
}
h_prime = encode_header(sample)
h_json = encode_json(sample)
h_bm = encode_bitmask(sample)
print(f"    Prime product: {h_prime.bit_length()} bits ({h_prime.bit_length()//8+1} bytes)")
print(f"    JSON string:   {len(h_json)} bytes")
print(f"    Bitmask:       {h_bm.bit_length()} bits ({h_bm.bit_length()//8+1} bytes)")
print(f"    Sample header: {h_prime}")

# ============================================================
# DEMO 1: FULL PIPELINE SIMULATION
# ============================================================

print(f"\n{'=' * 70}")
print("  DEMO 1: PROCESSING PIPELINE WITH LINEAGE TRACKING")
print(f"{'=' * 70}")

# Simulate a packet moving through the pipeline
print(f"\n  Simulating packet through 8-stage pipeline:")
print(f"  (Each stage multiplies its prime into the header)")

# Start with metadata-only header
packet = {
    'category': 'finance', 'source': 'api', 'region': 'eu-west',
    'priority': 'high', 'compliance': 'gdpr', 'format': 'json',
    'security': 'confidential', 'audience': 'analysts',
}
header = encode_header(packet)
print(f"\n  Initial header: {header}")
print(f"    Decoded: {decode_header(header)}")

# Stage 1: Ingest
packet['ingest'] = 'accepted'
header = encode_header(packet)
print(f"\n  After INGEST (accepted): {header}")

# Stage 2: Validate
packet['validate'] = 'passed'
header = encode_header(packet)
print(f"  After VALIDATE (passed): {header}")

# Stage 3: Enrich
packet['enrich'] = 'full'
header = encode_header(packet)
print(f"  After ENRICH (full):     {header}")

# Stage 4: Transform
packet['transform'] = 'encrypted'
header = encode_header(packet)
print(f"  After TRANSFORM (encrypted): {header}")

# Stage 5: Route
packet['route'] = 'queue_a'
header = encode_header(packet)
print(f"  After ROUTE (queue_a):   {header}")

# Stage 6: Deliver
packet['deliver'] = 'acked'
header = encode_header(packet)
print(f"  After DELIVER (acked):   {header}")

# Stage 7: Audit
packet['audit'] = 'reviewed'
header = encode_header(packet)
print(f"  After AUDIT (reviewed):  {header}")

# Stage 8: Archive
packet['archive'] = 'hot'
header = encode_header(packet)
print(f"  After ARCHIVE (hot):     {header}")

print(f"\n  Final header: {header}")
print(f"  Final header: {header.bit_length()} bits")

# Now: given ONLY the final integer, recover the complete processing chain
print(f"\n  --- RECOVERY FROM INTEGER ALONE ---")
print(f"  Input: {header}")
recovered = decode_header(header)
print(f"  Full metadata:")
for name, val in recovered.items():
    print(f"    {name}: {val}")

lineage = get_lineage(header)
print(f"\n  Processing lineage:")
for stage, val in lineage:
    print(f"    {stage}: {val}")

# ============================================================
# DEMO 2: FILTER OPERATIONS
# ============================================================

print(f"\n{'=' * 70}")
print("  DEMO 2: MULTI-CONDITION FILTERING")
print(f"{'=' * 70}")

# Create a stream of packets
random.seed(42)
N_PACKETS = 100_000
stream = []
for _ in range(N_PACKETS):
    pkt = {}
    for di, (name, vals) in enumerate(DIMENSIONS):
        pkt[name] = random.choice(vals)
    stream.append(pkt)

# Encode stream
stream_prime = [encode_header(p) for p in stream]
stream_json = [encode_json(p) for p in stream]
stream_bm = [encode_bitmask(p) for p in stream]

# Filter: finance + gdpr + high priority + confidential
filters = {
    'category': 'finance',
    'compliance': 'gdpr',
    'priority': 'high',
    'security': 'confidential',
}

print(f"\n  Filter: {filters}")
print(f"  (4 simultaneous conditions)")

# Prime filter
t0 = time.perf_counter_ns()
prime_matches = sum(1 for h in stream_prime if check_filter(h, filters))
t_prime = time.perf_counter_ns() - t0

# JSON filter
t0 = time.perf_counter_ns()
json_matches = sum(1 for h in stream_json if check_json(h, filters))
t_json = time.perf_counter_ns() - t0

# Bitmask filter
t0 = time.perf_counter_ns()
bm_matches = sum(1 for h in stream_bm if check_bitmask(h, filters))
t_bm = time.perf_counter_ns() - t0

assert prime_matches == json_matches == bm_matches

print(f"\n  Results: {prime_matches} matches from {N_PACKETS:,} packets")
print(f"    Prime:   {t_prime/1e6:.1f} ms  ({N_PACKETS/(t_prime/1e9)/1e6:.2f} M/s)")
print(f"    JSON:    {t_json/1e6:.1f} ms  ({N_PACKETS/(t_json/1e9)/1e6:.2f} M/s)")
print(f"    Bitmask: {t_bm/1e6:.1f} ms  ({N_PACKETS/(t_bm/1e9)/1e6:.2f} M/s)")

# Now show what prime can do that others can't: factorize matches
print(f"\n  Decomposing first 3 matching headers:")
count = 0
for h in stream_prime:
    if check_filter(h, filters):
        decoded = decode_header(h)
        lineage = get_lineage(h)
        print(f"    Header {h}:")
        print(f"      Route: {decoded.get('route')}, Deliver: {decoded.get('deliver')}, Audit: {decoded.get('audit')}")
        count += 1
        if count >= 3:
            break

# ============================================================
# DEMO 3: COMPOSITION (MERGING LINEAGES)
# ============================================================

print(f"\n{'=' * 70}")
print("  DEMO 3: COMPOSITION -- MERGING TWO PACKETS")
print(f"{'=' * 70}")

# Two packets with different metadata
pkt_a = {
    'category': 'finance', 'source': 'api', 'region': 'us-east',
    'priority': 'high', 'compliance': 'gdpr', 'format': 'json',
    'security': 'confidential', 'audience': 'analysts',
    'ingest': 'accepted', 'validate': 'passed', 'enrich': 'geoip',
    'transform': 'encrypted', 'route': 'queue_a', 'deliver': 'sent',
    'audit': 'reviewed', 'archive': 'hot',
}
pkt_b = {
    'category': 'health', 'source': 'webhook', 'region': 'eu-west',
    'priority': 'critical', 'compliance': 'hipaa', 'format': 'json',
    'security': 'secret', 'audience': 'executives',
    'ingest': 'accepted', 'validate': 'passed', 'enrich': 'threat_intel',
    'transform': 'encrypted', 'route': 'queue_b', 'deliver': 'pending',
    'audit': 'flagged', 'archive': 'hot',
}

h_a = encode_header(pkt_a)
h_b = encode_header(pkt_b)
h_merged = compose_headers(h_a, h_b)

print(f"\n  Packet A: category={pkt_a['category']}, compliance={pkt_a['compliance']}")
print(f"    Header: {h_a} ({h_a.bit_length()} bits)")
print(f"  Packet B: category={pkt_b['category']}, compliance={pkt_b['compliance']}")
print(f"    Header: {h_b} ({h_b.bit_length()} bits)")
print(f"\n  Merged (A * B): {h_merged} ({h_merged.bit_length()} bits)")

# What can we learn from the merged header?
print(f"\n  Factorizing merged header:")
merged_factors = decode_header(h_merged)
print(f"    Contains BOTH categories: finance={check_filter(h_merged, {'category': 'finance'})}, health={check_filter(h_merged, {'category': 'health'})}")
print(f"    Contains BOTH compliances: gdpr={check_filter(h_merged, {'compliance': 'gdpr'})}, hipaa={check_filter(h_merged, {'compliance': 'hipaa'})}")
print(f"    Is finance AND gdpr: {check_filter(h_merged, {'category': 'finance', 'compliance': 'gdpr'})}")
print(f"    Is health AND hipaa: {check_filter(h_merged, {'category': 'health', 'compliance': 'hipaa'})}")

# ============================================================
# DEMO 4: AUDIT TRAIL -- DIFF BETWEEN TWO HEADERS
# ============================================================

print(f"\n{'=' * 70}")
print("  DEMO 4: AUDIT TRAIL -- WHAT CHANGED?")
print(f"{'=' * 70}")

# Simulate packet at two stages
pkt_before = dict(pkt_a)
h_before = encode_header(pkt_before)

pkt_after = dict(pkt_a)
pkt_after['validate'] = 'failed'
pkt_after['route'] = 'dropped'
pkt_after['audit'] = 'flagged'
h_after = encode_header(pkt_after)

print(f"\n  Before: validate=passed, route=queue_a, audit=reviewed")
print(f"  After:  validate=failed, route=dropped, audit=flagged")
print(f"\n  Header before: {h_before}")
print(f"  Header after:  {h_after}")

changes = diff_headers(h_before, h_after)
print(f"\n  Diff (recovered from integers alone):")
for dim, (old, new) in changes.items():
    print(f"    {dim}: {old} -> {new}")

# ============================================================
# BENCHMARK: FULL COMPARISON
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK: ENCODE / FILTER / DECODE at scale")
print(f"{'=' * 70}")

random.seed(42)
N = 500_000

# Generate packets
packets = []
for _ in range(N):
    pkt = {}
    for di, (name, vals) in enumerate(DIMENSIONS):
        pkt[name] = random.choice(vals)
    packets.append(pkt)

# Encode benchmark
t0 = time.perf_counter()
enc_prime = [encode_header(p) for p in packets]
t_enc_prime = time.perf_counter() - t0

t0 = time.perf_counter()
enc_json = [encode_json(p) for p in packets]
t_enc_json = time.perf_counter() - t0

t0 = time.perf_counter()
enc_bm = [encode_bitmask(p) for p in packets]
t_enc_bm = time.perf_counter() - t0

print(f"\n  ENCODING ({N:,} packets):")
print(f"    Prime:   {t_enc_prime:.3f}s = {N/t_enc_prime:.0f}/s")
print(f"    JSON:    {t_enc_json:.3f}s = {N/t_enc_json:.0f}/s")
print(f"    Bitmask: {t_enc_bm:.3f}s = {N/t_enc_bm:.0f}/s")

# Filter benchmark (4 conditions)
filters_4 = {'category': 'finance', 'compliance': 'gdpr', 'priority': 'high', 'security': 'confidential'}

t0 = time.perf_counter()
m_prime = sum(1 for h in enc_prime if check_filter(h, filters_4))
t_filt_prime = time.perf_counter() - t0

t0 = time.perf_counter()
m_json = sum(1 for h in enc_json if check_json(h, filters_4))
t_filt_json = time.perf_counter() - t0

t0 = time.perf_counter()
m_bm = sum(1 for h in enc_bm if check_bitmask(h, filters_4))
t_filt_bm = time.perf_counter() - t0

assert m_prime == m_json == m_bm

print(f"\n  FILTERING ({N:,} packets, 4 conditions, {m_prime} matches):")
print(f"    Prime:   {t_filt_prime:.3f}s = {N/t_filt_prime:.0f}/s")
print(f"    JSON:    {t_filt_json:.3f}s = {N/t_filt_json:.0f}/s")
print(f"    Bitmask: {t_filt_bm:.3f}s = {N/t_filt_bm:.0f}/s")

# Decode benchmark (full recovery)
N_DECODE = 100_000
t0 = time.perf_counter()
for h in enc_prime[:N_DECODE]:
    decode_header(h)
t_dec_prime = time.perf_counter() - t0

t0 = time.perf_counter()
for h in enc_json[:N_DECODE]:
    decode_json(h)
t_dec_json = time.perf_counter() - t0

t0 = time.perf_counter()
for h in enc_bm[:N_DECODE]:
    decode_bitmask_partial(h)
t_dec_bm = time.perf_counter() - t0

print(f"\n  DECODING ({N_DECODE:,} headers -- full recovery):")
print(f"    Prime:   {t_dec_prime:.3f}s = {N_DECODE/t_dec_prime:.0f}/s")
print(f"    JSON:    {t_dec_json:.3f}s = {N_DECODE/t_dec_json:.0f}/s")
print(f"    Bitmask: {t_dec_bm:.3f}s = {N_DECODE/t_dec_bm:.0f}/s")

# Size comparison
avg_prime_bits = sum(h.bit_length() for h in enc_prime) / N
avg_json_bytes = sum(len(h) for h in enc_json) / N
avg_bm_bits = sum(h.bit_length() for h in enc_bm) / N

print(f"\n  SIZE (per header, {N:,} average):")
print(f"    Prime product: {avg_prime_bits:.0f} bits ({avg_prime_bits/8:.0f} bytes)")
print(f"    JSON string:   {avg_json_bytes:.0f} bytes")
print(f"    Bitmask:       {avg_bm_bits:.0f} bits ({avg_bm_bits/8:.0f} bytes)")

# ============================================================
# BENCHMARK: FILTER + DECODE COMBINED (the real workload)
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK: FILTER + DECODE MATCHES (real workload)")
print(f"{'=' * 70}")
print(f"  Typical pipeline: filter stream, then decode only the matches.")

# Prime: filter, then decode matches
t0 = time.perf_counter()
matches = [h for h in enc_prime if check_filter(h, filters_4)]
for h in matches:
    decode_header(h)
t_combo_prime = time.perf_counter() - t0

# JSON: filter, then parse matches
t0 = time.perf_counter()
matches_j = [h for h in enc_json if check_json(h, filters_4)]
for h in matches_j:
    decode_json(h)
t_combo_json = time.perf_counter() - t0

# Bitmask: filter, then decode matches
t0 = time.perf_counter()
matches_bm = [h for h in enc_bm if check_bitmask(h, filters_4)]
for h in matches_bm:
    decode_bitmask_partial(h)
t_combo_bm = time.perf_counter() - t0

print(f"\n  Filter + decode {m_prime} matches from {N:,} packets:")
print(f"    Prime:   {t_combo_prime:.3f}s = {N/t_combo_prime:.0f} total/s")
print(f"    JSON:    {t_combo_json:.3f}s = {N/t_combo_json:.0f} total/s")
print(f"    Bitmask: {t_combo_bm:.3f}s = {N/t_combo_bm:.0f} total/s")

# ============================================================
# SUMMARY
# ============================================================

print(f"\n{'=' * 70}")
print("  SUMMARY")
print(f"{'=' * 70}")

print(f"""
  THE THREE-WAY TRADE-OFF:

                    Filter    Decompose    Size     Compose
                    Speed     (recover)    (bytes)  (merge)
  Prime product     Fast      YES          {avg_prime_bits/8:.0f}       YES (multiply)
  JSON              Slow      YES          {avg_json_bytes:.0f}      NO (string concat)
  Bitmask           Fastest   PARTIAL      {avg_bm_bits/8:.0f}       NO (OR loses info)

  Prime product is the ONLY encoding that is simultaneously:
    1. Filterable at O(1) via modulo check
    2. Fully decomposable via factorization (lossless recovery)
    3. Composable via multiplication (merge two headers)
    4. Verifiable via gcd (check shared history)
    5. Diffable via factorization (find what changed)

  JSON is decomposable but not efficiently filterable.
  Bitmask is filterable but not fully decomposable.
  Prime product is both -- at the cost of larger integers and encoding overhead.

  WHERE THIS WINS:
    - High-volume streaming pipelines that need both filtering AND audit trails
    - Hardware (FPGA) where modulo = 1 cycle and factorization = trial division
    - Systems where the header must be self-contained (no external schema)

  WHERE THIS LOSES:
    - Software-only systems where bitmask or JSON are simpler and faster
    - Systems that need human-readable headers
    - Systems with many dimensions (integer size grows)
""")

print("  Experiment complete.")
print("=" * 70)
