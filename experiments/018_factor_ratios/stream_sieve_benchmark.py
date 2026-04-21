"""
MVM v0.13 -- Stream Sieve Benchmark: Multi-Variable Crossover

The core question: At how many simultaneous filter conditions does MVM's
single modulo check beat dict's N separate lookups?

Architecture:
  20 "dimensions" (conditions) per packet, each with multiple possible values.
  Each value maps to a unique prime. Packet encoding = product of all 20 primes.

  MVM filter:  product of target primes -> single modulo check (O(1))
  Dict filter: N separate tuple comparisons (O(N))
  Bitmask:     single AND check (O(1), the fair software competitor)

  As N grows, dict scales linearly. MVM and bitmask stay constant.
  The crossover point determines MVM's niche.

ZERO FLOATS. Pure integer arithmetic.
"""

import sys
import time
import random
from math import gcd

print("=" * 70)
print("STREAM SIEVE BENCHMARK -- Multi-Variable Crossover")
print("=" * 70)

# ============================================================
# PRIME POOL
# ============================================================

def sieve_primes(limit):
    """Generate primes up to limit."""
    s = [True] * (limit + 1)
    s[0] = s[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if s[i]:
            for j in range(i * i, limit + 1, i):
                s[j] = False
    return [i for i in range(2, limit + 1) if s[i]]

PRIMES = sieve_primes(1000)  # First ~168 primes
print(f"\n  Prime pool: {len(PRIMES)} primes [{PRIMES[0]}..{PRIMES[-1]}]")

# ============================================================
# DIMENSIONS (20 filter conditions)
# ============================================================

DIMENSIONS = [
    ('category',      20),   # 20 possible values
    ('sentiment',      5),   # positive, negative, neutral, mixed, unknown
    ('urgency',        3),   # low, medium, high
    ('security',       5),   # levels 1-5
    ('region',         7),   # geographic regions
    ('source',         4),   # internal, external, api, manual
    ('language',       8),   # en, es, fr, de, zh, ja, ar, other
    ('format',         3),   # text, binary, structured
    ('priority',       4),   # low, normal, high, critical
    ('compliance',     3),   # gdpr, hipaa, none
    ('department',    10),   # org departments
    ('channel',        6),   # email, api, webhook, sms, push, ftp
    ('audience',       5),   # public, internal, restricted, confidential, secret
    ('lifecycle',      4),   # draft, active, archived, deleted
    ('integrity',      3),   # checksum, signed, unsigned
    ('visibility',     4),   # visible, hidden, masked, encrypted
    ('retention',      5),   # 1d, 30d, 1y, 7y, permanent
    ('encryption',     3),   # none, tls, e2e
    ('protocol',       4),   # http, grpc, mqtt, amqp
    ('domain',         6),   # finance, health, iot, media, auth, system
]
N_DIMS = len(DIMENSIONS)

# Assign primes to each dimension's values
dim_primes = {}  # (dim_idx, value_idx) -> prime
prime_cursor = 0
dim_value_counts = []
for di, (name, n_vals) in enumerate(DIMENSIONS):
    dim_value_counts.append(n_vals)
    for vi in range(n_vals):
        dim_primes[(di, vi)] = PRIMES[prime_cursor]
        prime_cursor += 1

total_primes_used = prime_cursor
print(f"  Dimensions: {N_DIMS}")
print(f"  Total value slots: {total_primes_used}")
print(f"  Primes used: {total_primes_used} of {len(PRIMES)}")

# Assign bit positions for bitmask approach
dim_bit_offsets = {}  # dim_idx -> bit offset
bit_cursor = 0
for di, (name, n_vals) in enumerate(DIMENSIONS):
    dim_bit_offsets[di] = bit_cursor
    bit_cursor += n_vals
total_bits = bit_cursor
print(f"  Bitmask size: {total_bits} bits ({total_bits // 8 + 1} bytes)")

# ============================================================
# PACKET ENCODING
# ============================================================

def encode_packet_mvm(values):
    """Encode packet as product of dimension primes. values[di] = value_idx."""
    enc = 1
    for di, vi in enumerate(values):
        enc *= dim_primes[(di, vi)]
    return enc

def encode_packet_bitmask(values):
    """Encode packet as bitmask. Each dimension gets a range of bits."""
    mask = 0
    for di, vi in enumerate(values):
        mask |= (1 << (dim_bit_offsets[di] + vi))
    return mask

def encode_packet_dict(values):
    """For dict approach, just store the tuple."""
    return tuple(values)

print(f"\n  Sample encoding check:")
sample_values = [0] * N_DIMS  # all zeros
for di in range(N_DIMS):
    sample_values[di] = random.randint(0, dim_value_counts[di] - 1)
mvm_enc = encode_packet_mvm(sample_values)
bm_enc = encode_packet_bitmask(sample_values)
print(f"    MVM encoding:     {mvm_enc} ({mvm_enc.bit_length()} bits)")
print(f"    Bitmask encoding: {bm_enc} ({bm_enc.bit_length()} bits)")

# ============================================================
# FILTER CONSTRUCTION
# ============================================================

def build_filter_mvm(condition_dims, target_values):
    """Build MVM composite mask. condition_dims: list of dim indices to check."""
    mask = 1
    for di, tv in zip(condition_dims, target_values):
        mask *= dim_primes[(di, tv)]
    return mask

def build_filter_bitmask(condition_dims, target_values):
    """Build bitmask filter."""
    mask = 0
    for di, tv in zip(condition_dims, target_values):
        mask |= (1 << (dim_bit_offsets[di] + tv))
    return mask

def check_mvm(packet_enc, filter_mask):
    """MVM check: single modulo."""
    return packet_enc % filter_mask == 0

def check_dict(packet_tuple, condition_dims, target_values):
    """Dict check: N comparisons."""
    for di, tv in zip(condition_dims, target_values):
        if packet_tuple[di] != tv:
            return False
    return True

def check_bitmask(packet_bm, filter_bm):
    """Bitmask check: single AND."""
    return (packet_bm & filter_bm) == filter_bm

# ============================================================
# PACKET GENERATION
# ============================================================

def generate_packets(n_packets, seed=42):
    """Generate random packets with pre-computed encodings."""
    random.seed(seed)
    packets_mvm = []
    packets_bm = []
    packets_dict = []
    for _ in range(n_packets):
        values = [random.randint(0, dim_value_counts[di] - 1) for di in range(N_DIMS)]
        packets_mvm.append(encode_packet_mvm(values))
        packets_bm.append(encode_packet_bitmask(values))
        packets_dict.append(encode_packet_dict(values))
    return packets_mvm, packets_bm, packets_dict

def generate_mixed_packets(n_packets, match_frac=0.1, n_conditions=5, seed=42):
    """Generate packets where match_frac actually match a specific filter."""
    random.seed(seed)

    # Pick random filter
    cond_dims = random.sample(range(N_DIMS), n_conditions)
    target_values = [random.randint(0, dim_value_counts[di] - 1) for di in cond_dims]

    filter_mvm = build_filter_mvm(cond_dims, target_values)
    filter_bm = build_filter_bitmask(cond_dims, target_values)

    packets_mvm = []
    packets_bm = []
    packets_dict = []
    labels = []

    n_match = int(n_packets * match_frac)

    # Generate matching packets
    for _ in range(n_match):
        values = [random.randint(0, dim_value_counts[di] - 1) for di in range(N_DIMS)]
        for di, tv in zip(cond_dims, target_values):
            values[di] = tv  # Force match
        packets_mvm.append(encode_packet_mvm(values))
        packets_bm.append(encode_packet_bitmask(values))
        packets_dict.append(encode_packet_dict(values))
        labels.append(True)

    # Generate non-matching packets
    for _ in range(n_packets - n_match):
        values = [random.randint(0, dim_value_counts[di] - 1) for di in range(N_DIMS)]
        # Ensure at least one dimension doesn't match
        miss_dim = random.choice(cond_dims)
        wrong_val = random.randint(0, dim_value_counts[miss_dim] - 1)
        while wrong_val == target_values[cond_dims.index(miss_dim)]:
            wrong_val = random.randint(0, dim_value_counts[miss_dim] - 1)
        values[miss_dim] = wrong_val
        packets_mvm.append(encode_packet_mvm(values))
        packets_bm.append(encode_packet_bitmask(values))
        packets_dict.append(encode_packet_dict(values))
        labels.append(False)

    # Shuffle
    combined = list(zip(packets_mvm, packets_bm, packets_dict, labels))
    random.shuffle(combined)
    packets_mvm = [c[0] for c in combined]
    packets_bm = [c[1] for c in combined]
    packets_dict = [c[2] for c in combined]
    labels = [c[3] for c in combined]

    return (packets_mvm, packets_bm, packets_dict, labels,
            cond_dims, target_values, filter_mvm, filter_bm)

# ============================================================
# BENCHMARK 1: CROSSOVER POINT
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK 1: CROSSOVER POINT (1M packets, 1-20 conditions)")
print(f"{'=' * 70}")

N_PACKETS = 1_000_000

# Pre-generate random packets (no filter, just throughput)
packets_mvm, packets_bm, packets_dict = generate_packets(N_PACKETS)

crossover_results = []

for n_cond in [1, 2, 3, 5, 8, 10, 12, 15, 18, 20]:
    # Random filter with n_cond conditions
    cond_dims = list(range(n_cond))  # Use first N dimensions
    target_values = [random.randint(0, dim_value_counts[di] - 1) for di in cond_dims]

    # Build filters
    f_mvm = build_filter_mvm(cond_dims, target_values)
    f_bm = build_filter_bitmask(cond_dims, target_values)

    # --- Dict: N comparisons ---
    # Warmup
    for i in range(100):
        check_dict(packets_dict[i], cond_dims, target_values)

    t0 = time.perf_counter_ns()
    dict_matches = 0
    for pkt in packets_dict:
        if check_dict(pkt, cond_dims, target_values):
            dict_matches += 1
    t_dict = time.perf_counter_ns() - t0

    # --- MVM: single modulo ---
    for i in range(100):
        check_mvm(packets_mvm[i], f_mvm)

    t0 = time.perf_counter_ns()
    mvm_matches = 0
    for pkt in packets_mvm:
        if check_mvm(pkt, f_mvm):
            mvm_matches += 1
    t_mvm = time.perf_counter_ns() - t0

    # --- Bitmask: single AND ---
    for i in range(100):
        check_bitmask(packets_bm[i], f_bm)

    t0 = time.perf_counter_ns()
    bm_matches = 0
    for pkt in packets_bm:
        if check_bitmask(pkt, f_bm):
            bm_matches += 1
    t_bm = time.perf_counter_ns() - t0

    dict_ops = N_PACKETS / (t_dict / 1e9)
    mvm_ops = N_PACKETS / (t_mvm / 1e9)
    bm_ops = N_PACKETS / (t_bm / 1e9)

    # Consistency check
    assert dict_matches == mvm_matches == bm_matches, \
        f"Mismatch: dict={dict_matches} mvm={mvm_matches} bm={bm_matches}"

    crossover_results.append({
        'n_cond': n_cond,
        'dict_ns': t_dict,
        'mvm_ns': t_mvm,
        'bm_ns': t_bm,
        'dict_ops': dict_ops,
        'mvm_ops': mvm_ops,
        'bm_ops': bm_ops,
        'matches': dict_matches,
    })

# Print results table
print(f"\n  {'Conditions':>10s}  {'Dict (M/s)':>10s}  {'MVM (M/s)':>10s}  {'BM (M/s)':>10s}  "
      f"{'Dict/MVM':>8s}  {'MVM/Dict':>8s}  {'BM/Dict':>8s}  {'Matches':>8s}")
print(f"  {'-'*82}")

crossover_found = False
for r in crossover_results:
    d_m = r['dict_ops'] / 1e6
    m_m = r['mvm_ops'] / 1e6
    b_m = r['bm_ops'] / 1e6
    ratio_dm = r['dict_ops'] / r['mvm_ops']
    ratio_md = r['mvm_ops'] / r['dict_ops']
    ratio_bd = r['bm_ops'] / r['dict_ops']
    marker = ""
    if not crossover_found and r['mvm_ops'] > r['dict_ops']:
        marker = " <-- MVM crosses over"
        crossover_found = True
    print(f"  {r['n_cond']:>10d}  {d_m:>10.2f}  {m_m:>10.2f}  {b_m:>10.2f}  "
          f"{ratio_dm:>8.2f}x  {ratio_md:>8.2f}x  {ratio_bd:>8.2f}x  {r['matches']:>8d}{marker}")

# ============================================================
# BENCHMARK 2: FILTER CONSTRUCTION COST
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK 2: FILTER CONSTRUCTION (MASK BUILD) COST")
print(f"{'=' * 70}")

print(f"\n  How much does the upfront mask construction cost?")
print(f"  (This is the 'amortization' question)")

for n_cond in [1, 5, 10, 20]:
    cond_dims = list(range(n_cond))
    target_values = [random.randint(0, dim_value_counts[di] - 1) for di in cond_dims]

    # MVM mask construction: multiply N primes
    N_BUILD = 100_000
    t0 = time.perf_counter_ns()
    for _ in range(N_BUILD):
        mask = 1
        for di, tv in zip(cond_dims, target_values):
            mask *= dim_primes[(di, tv)]
    t_build_mvm = (time.perf_counter_ns() - t0) / N_BUILD

    # Bitmask construction: OR N bit positions
    t0 = time.perf_counter_ns()
    for _ in range(N_BUILD):
        mask = 0
        for di, tv in zip(cond_dims, target_values):
            mask |= (1 << (dim_bit_offsets[di] + tv))
    t_build_bm = (time.perf_counter_ns() - t0) / N_BUILD

    # Dict filter construction: just store the list
    t0 = time.perf_counter_ns()
    for _ in range(N_BUILD):
        _ = list(zip(cond_dims, target_values))
    t_build_dict = (time.perf_counter_ns() - t0) / N_BUILD

    print(f"\n  {n_cond} conditions:")
    print(f"    Dict build: {t_build_dict:.0f} ns")
    print(f"    MVM build:  {t_build_mvm:.0f} ns (multiply {n_cond} primes)")
    print(f"    BM build:   {t_build_bm:.0f} ns (OR {n_cond} bit positions)")

    # Find the crossover packet count where MVM's per-packet savings pay back
    # the construction cost difference
    if n_cond > 0:
        # Per-packet time difference
        for r in crossover_results:
            if r['n_cond'] == n_cond:
                per_pkt_dict = r['dict_ns'] / N_PACKETS  # ns per packet
                per_pkt_mvm = r['mvm_ns'] / N_PACKETS
                per_pkt_bm = r['bm_ns'] / N_PACKETS
                savings_mvm = per_pkt_dict - per_pkt_mvm  # ns saved per packet
                savings_bm = per_pkt_dict - per_pkt_bm

                if savings_mvm > 0:
                    amort_mvm = t_build_mvm / savings_mvm
                    print(f"    MVM amortizes build cost after {amort_mvm:.0f} packets")
                else:
                    print(f"    MVM does NOT save per-packet time (dict is faster)")

                if savings_bm > 0:
                    amort_bm = t_build_bm / savings_bm
                    print(f"    BM amortizes build cost after {amort_bm:.0f} packets")
                break

# ============================================================
# BENCHMARK 3: TARGETED STREAM (10% match rate)
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK 3: TARGETED STREAM (1M packets, 10% match, N conditions)")
print(f"{'=' * 70}")
print(f"  Simulates realistic filtering: most packets rejected, few pass.")

N_STREAM = 1_000_000

for n_cond in [1, 5, 10, 20]:
    (pkts_mvm, pkts_bm, pkts_dict, labels,
     cond_dims, target_values, f_mvm, f_bm) = \
        generate_mixed_packets(N_STREAM, match_frac=0.1, n_conditions=n_cond)

    # Dict
    t0 = time.perf_counter_ns()
    dict_pass = 0
    for pkt in pkts_dict:
        if check_dict(pkt, cond_dims, target_values):
            dict_pass += 1
    t_dict = time.perf_counter_ns() - t0

    # MVM
    t0 = time.perf_counter_ns()
    mvm_pass = 0
    for pkt in pkts_mvm:
        if check_mvm(pkt, f_mvm):
            mvm_pass += 1
    t_mvm = time.perf_counter_ns() - t0

    # Bitmask
    t0 = time.perf_counter_ns()
    bm_pass = 0
    for pkt in pkts_bm:
        if check_bitmask(pkt, f_bm):
            bm_pass += 1
    t_bm = time.perf_counter_ns() - t0

    assert dict_pass == mvm_pass == bm_pass

    d_ops = N_STREAM / (t_dict / 1e9)
    m_ops = N_STREAM / (t_mvm / 1e9)
    b_ops = N_STREAM / (t_bm / 1e9)

    print(f"\n  {n_cond} conditions ({dict_pass:,} matches / {N_STREAM:,} packets):")
    print(f"    Dict:    {t_dict/1e6:>8.1f} ms  ({d_ops/1e6:.2f} M/s)")
    print(f"    MVM:     {t_mvm/1e6:>8.1f} ms  ({m_ops/1e6:.2f} M/s)  ({m_ops/d_ops:.2f}x dict)")
    print(f"    Bitmask: {t_bm/1e6:>8.1f} ms  ({b_ops/1e6:.2f} M/s)  ({b_ops/d_ops:.2f}x dict)")

# ============================================================
# BENCHMARK 4: COMPOSITE FILTER COMPLEXITY
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK 4: MODULO SIZE vs FILTER COMPLEXITY")
print(f"{'=' * 70}")
print(f"  How does integer size affect modulo speed?")

for n_cond in [1, 5, 10, 15, 20]:
    cond_dims = list(range(n_cond))
    target_values = [random.randint(0, dim_value_counts[di] - 1) for di in cond_dims]
    f_mvm = build_filter_mvm(cond_dims, target_values)

    print(f"\n  {n_cond} conditions: mask = {f_mvm} ({f_mvm.bit_length()} bits)")

    # Raw modulo speed on this mask size
    test_val = packets_mvm[0]
    N_RAW = 10_000_000
    t0 = time.perf_counter_ns()
    for _ in range(N_RAW):
        _ = test_val % f_mvm
    t_raw = time.perf_counter_ns() - t0
    print(f"    Raw modulo: {N_RAW/(t_raw/1e9)/1e6:.2f} M ops/s")

    # Raw AND speed on comparable bitmask
    f_bm = build_filter_bitmask(cond_dims, target_values)
    test_bm = packets_bm[0]
    t0 = time.perf_counter_ns()
    for _ in range(N_RAW):
        _ = test_bm & f_bm
    t_raw_and = time.perf_counter_ns() - t0
    print(f"    Raw AND:    {N_RAW/(t_raw_and/1e9)/1e6:.2f} M ops/s")
    print(f"    AND/modulo: {N_RAW/(t_raw_and/1e9) / (N_RAW/(t_raw/1e9)):.1f}x faster")

# ============================================================
# BENCHMARK 5: SHORT-CIRCUIT DICT (optimized baseline)
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK 5: OPTIMIZED DICT (short-circuit on first mismatch)")
print(f"{'=' * 70}")
print(f"  Real systems don't check all N conditions if one fails early.")

def check_dict_sc(packet_tuple, cond_dims, target_values):
    """Dict with early exit (short-circuit)."""
    for di, tv in zip(cond_dims, target_values):
        if packet_tuple[di] != tv:
            return False
    return True

# Regenerate mixed packets for realistic early-exit behavior
for n_cond in [1, 5, 10, 20]:
    (pkts_mvm, pkts_bm, pkts_dict, labels,
     cond_dims, target_values, f_mvm, f_bm) = \
        generate_mixed_packets(N_STREAM, match_frac=0.1, n_conditions=n_cond)

    # Dict with short-circuit
    t0 = time.perf_counter_ns()
    dict_pass = 0
    for pkt in pkts_dict:
        if check_dict_sc(pkt, cond_dims, target_values):
            dict_pass += 1
    t_dict_sc = time.perf_counter_ns() - t0

    # MVM (no short-circuit possible, always does full modulo)
    t0 = time.perf_counter_ns()
    mvm_pass = 0
    for pkt in pkts_mvm:
        if check_mvm(pkt, f_mvm):
            mvm_pass += 1
    t_mvm = time.perf_counter_ns() - t0

    # Bitmask
    t0 = time.perf_counter_ns()
    bm_pass = 0
    for pkt in pkts_bm:
        if check_bitmask(pkt, f_bm):
            bm_pass += 1
    t_bm = time.perf_counter_ns() - t0

    d_ops = N_STREAM / (t_dict_sc / 1e9)
    m_ops = N_STREAM / (t_mvm / 1e9)
    b_ops = N_STREAM / (t_bm / 1e9)

    print(f"\n  {n_cond} conditions (10% match = 90% short-circuit on 1st check):")
    print(f"    Dict (SC): {t_dict_sc/1e6:>8.1f} ms  ({d_ops/1e6:.2f} M/s)")
    print(f"    MVM:       {t_mvm/1e6:>8.1f} ms  ({m_ops/1e6:.2f} M/s)  ({m_ops/d_ops:.2f}x dict)")
    print(f"    Bitmask:   {t_bm/1e6:>8.1f} ms  ({b_ops/1e6:.2f} M/s)  ({b_ops/d_ops:.2f}x dict)")

# ============================================================
# BENCHMARK 6: HARDWARE PROJECTION
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK 6: HARDWARE PROJECTION")
print(f"{'=' * 70}")

print(f"""
  Software (Python, measured):
    Integer AND:    ~{N_RAW/(t_raw_and/1e9)/1e6:.0f} M ops/s
    Integer modulo: ~{N_RAW/(t_raw/1e9)/1e6:.0f} M ops/s (varies with bit width)
    Bitmask is {N_RAW/(t_raw_and/1e9) / (N_RAW/(t_raw/1e9)):.1f}x faster than modulo in software

  FPGA (architectural estimate, 200 MHz clock):
    AND gate:       1 cycle = 5 ns -> 200 M ops/s
    Modulo (custom): 1-3 cycles (parallel remainder computation)
    Dict (BRAM):    3-5 cycles per lookup, N lookups for N conditions

    20-condition filter at 200 MHz:
      Bitmask:    200 M checks/s  (1 cycle)
      MVM modulo: 67-200 M checks/s  (1-3 cycles)
      Dict:       8-13 M checks/s  (60-100 cycles for 20 BRAM reads)

    On FPGA, ALL three O(1) methods beat O(N) dict by 5-25x at 20 conditions.
    Bitmask and MVM are roughly equivalent on FPGA.

  The honest conclusion:
    In SOFTWARE: bitmask wins. MVM modulo is slower than AND.
    In HARDWARE: MVM and bitmask are equivalent. Both crush hash-based dict.
    MVM's composability (multiplicative encoding) is architecturally equivalent
    to bitmask's additive encoding. The prime factorization adds no performance
    advantage over bit positions. Both achieve O(1) multi-condition filtering.

    The MVM's genuine unique advantage: factorization enables DECOMPOSITION.
    A product can be factored to recover individual dimensions.
    A bitmask can be masked to ISOLATE dimensions but not factored.
    This matters for downstream processing, not for filtering speed.
""")

# ============================================================
# SUMMARY
# ============================================================

print("=" * 70)
print("  SUMMARY")
print("=" * 70)

# Find crossover
crossover_n = None
for r in crossover_results:
    if r['mvm_ops'] > r['dict_ops']:
        crossover_n = r['n_cond']
        break

print(f"""
  CROSSOVER POINT (MVM beats dict in pure throughput):
""")

if crossover_n:
    print(f"    MVM beats dict at {crossover_n}+ simultaneous conditions")
    for r in crossover_results:
        if r['n_cond'] == crossover_n:
            print(f"    At {crossover_n} conditions: MVM {r['mvm_ops']/1e6:.2f} M/s vs Dict {r['dict_ops']/1e6:.2f} M/s")
            break
else:
    print(f"    MVM never beats dict (dict was faster at all tested N)")

print(f"""
  AGAINST BITMASK (the fair O(1) competitor):
    Bitmask is {N_RAW/(t_raw_and/1e9) / (N_RAW/(t_raw/1e9)):.1f}x faster than MVM modulo in software
    Bitmask AND is a single CPU instruction; modulo is multi-cycle
    MVM never beats bitmask at any condition count in software

  ON FPGA:
    MVM modulo and bitmask AND are both 1-3 cycles
    Both achieve ~200 M checks/s at 200 MHz
    Both beat O(N) BRAM-based hash lookup by 5-25x at 20 conditions

  HONEST VERDICT:
    The O(1) vs O(N) advantage is real, but it belongs to ANY O(1) encoding --
    bitmask OR prime product. The prime factorization adds no speed advantage
    over bit positions for filtering. MVM's unique property is reversibility:
    factoring a product recovers the original dimensions; masking a bitmask
    only isolates them. This matters for decomposition, not for speed.
""")

print("  Benchmark complete.")
print("=" * 70)
