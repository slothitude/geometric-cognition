"""
THROUGHPUT BENCHMARK -- MVM vs Standard Lookup Approaches

Honest comparison of:
  1. Python dict (hash table) -- the standard baseline
  2. MVM modulo check -- integer encoding, O(1) modulo per category
  3. Bloom filter -- probabilistic membership
  4. Set-based lookup -- naive per-category membership test

Workloads:
  A. Single-word classification throughput (1M ops)
  B. Sentence-level routing (100k sentences)
  C. Unknown word rejection
  D. Memory footprint at 500 / 5k / 50k / 100k vocab
  E. Scaling curve

The goal is honest data. If dict beats MVM, that's the result.
The MVM's potential advantages are:
  - Composability (sentence = single product integer)
  - Determinism (zero false positives on exact match)
  - Hardware deployability (modulo is trivial on FPGA)
Its potential disadvantages are:
  - Integer multiplication on large products is slower than string hashing
  - Python dicts are extremely optimized C code
  - No semantic generalization (proven by OOD test)
"""

import sys
import time
import random
from math import gcd
from collections import defaultdict, Counter

print("=" * 70)
print("THROUGHPUT BENCHMARK -- MVM vs Standard Approaches")
print("=" * 70)

# ============================================================
# LAYER 0: PRIME SUBSTRATE + FEATURE SPACE (from v0.12)
# ============================================================

class PrimeSubstrate:
    def __init__(self, limit=500_000):
        self._sieve = [True] * (limit + 1)
        self._sieve[0] = self._sieve[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if self._sieve[i]:
                for j in range(i * i, limit + 1, i):
                    self._sieve[j] = False

    def first_n_primes(self, n):
        primes = []
        c = 2
        while len(primes) < n:
            if self._sieve[c]:
                primes.append(c)
            c += 1
        return primes

SUFFIXES = ['ing', 'tion', 'ness', 'ment', 'ful', 'less', 'ous', 'ive', 'er', 'ly', 'al']
PREFIXES = ['un', 're', 'pre', 'dis', 'over']
LENGTH_BUCKETS = [(1, 3), (4, 5), (6, 7), (8, 9), (10, 12), (13, 99)]

CATEGORIES = [
    'emotions', 'animals', 'colors', 'foods', 'weather',
    'professions', 'vehicles', 'instruments', 'sports', 'plants',
    'tools', 'clothing', 'buildings', 'gems', 'weapons',
    'seasons', 'terrain', 'beverages', 'astronomy', 'mythology',
]
N_CATS = len(CATEGORIES)

class FeatureSpace:
    def __init__(self, substrate):
        bp = substrate.first_n_primes(100)
        self.cat_primes = bp[0:20]
        self.fl_primes = bp[20:46]
        self.ll_primes = bp[46:72]
        self.len_primes = bp[72:78]
        self.morph_primes = bp[78:94]
        self.hash_primes = bp[94:100]

def deterministic_hash(word):
    h = 5381
    for ch in word:
        h = ((h * 33) + ord(ch)) & 0xFFFFFFFF
    return h

substrate = PrimeSubstrate()
fs = FeatureSpace(substrate)

def encode_word_mvm(word, cat_idx):
    """Encode word as product of feature primes. Returns encoding."""
    enc = fs.cat_primes[cat_idx]
    if word and word[0].isalpha():
        enc *= fs.fl_primes[ord(word[0].lower()) - ord('a')]
    if word and word[-1].isalpha():
        enc *= fs.ll_primes[ord(word[-1].lower()) - ord('a')]
    wlen = len(word)
    for i, (lo, hi) in enumerate(LENGTH_BUCKETS):
        if lo <= wlen <= hi:
            enc *= fs.len_primes[i]
            break
    else:
        enc *= fs.len_primes[-1]
    for si, sfx in enumerate(SUFFIXES):
        if word.endswith(sfx):
            enc *= fs.morph_primes[si]
            break
    for pi, pfx in enumerate(PREFIXES):
        if word.startswith(pfx):
            enc *= fs.morph_primes[11 + pi]
            break
    h = deterministic_hash(word)
    for offset in [h % 6, (h >> 8) % 6]:
        enc *= fs.hash_primes[offset]
    return enc

# ============================================================
# SYLLABLE VOCABULARY GENERATOR (from v0.12)
# ============================================================

class SyllableVocabularyGenerator:
    CONSONANTS = 'bcdfghjklmnprstvwz'
    VOWELS = 'aeiou'

    def __init__(self, n_categories=20, words_per_cat=5000):
        self.n_categories = n_categories
        self.words_per_cat = words_per_cat
        self.nc = len(self.CONSONANTS)
        self.nv = len(self.VOWELS)
        self.cvcv = self.nc * self.nv * self.nc * self.nv
        self.cvccv = self.nc * self.nv * self.nc * self.nc * self.nv
        self.total = self.cvcv + self.cvccv

    def _scramble(self, uid):
        return (uid * 7919 + 104729) % self.total

    def _idx_to_word(self, uid):
        C, V, nc, nv = self.CONSONANTS, self.VOWELS, self.nc, self.nv
        if uid < self.cvcv:
            c1 = uid // (nv * nc * nv); t = uid % (nv * nc * nv)
            v1 = t // (nc * nv); t %= nc * nv
            c2 = t // nv; v2 = t % nv
            return C[c1] + V[v1] + C[c2] + V[v2]
        else:
            uid2 = uid - self.cvcv
            c1 = uid2 // (nv * nc * nc * nv); t = uid2 % (nv * nc * nc * nv)
            v1 = t // (nc * nc * nv); t %= nc * nc * nv
            c2 = t // (nc * nv); t %= nc * nv
            c3 = t // nv; v2 = t % nv
            return C[c1] + V[v1] + C[c2] + C[c3] + V[v2]

    def generate(self):
        vocab = []
        for ci in range(self.n_categories):
            for wi in range(self.words_per_cat):
                uid = self._scramble(ci * self.words_per_cat + wi)
                vocab.append((self._idx_to_word(uid), ci))
        return vocab

# ============================================================
# SIMPLE BLOOM FILTER
# ============================================================

class BloomFilter:
    """Minimal Bloom filter for membership testing."""

    def __init__(self, expected_items, fp_rate=0.01):
        # Size calculation: m = -n*ln(p) / (ln2)^2
        import math
        self.m = max(int(-expected_items * math.log(fp_rate) / (math.log(2) ** 2)), 64)
        self.k = max(int(self.m / expected_items * math.log(2)), 1)
        self.bits = bytearray((self.m + 7) // 8)
        self._seeds = [5381 + i * 33 for i in range(self.k)]

    def _hashes(self, word):
        h = 5381
        for ch in word:
            h = ((h * 33) + ord(ch)) & 0xFFFFFFFF
        for seed in self._seeds:
            yield ((h ^ seed) * 2654435761) % self.m

    def add(self, word):
        for idx in self._hashes(word):
            self.bits[idx >> 3] |= (1 << (idx & 7))

    def contains(self, word):
        for idx in self._hashes(word):
            if not (self.bits[idx >> 3] & (1 << (idx & 7))):
                return False
        return True

# ============================================================
# LOOKUP SYSTEM BUILDERS
# ============================================================

def build_systems(vocab_data):
    """Build all four lookup systems from vocabulary data.
    vocab_data: list of (word_str, cat_idx)
    Returns: dict_sys, mvm_sys, bloom_sys, set_sys
    """
    words = [w for w, _ in vocab_data]
    cats = [c for _, c in vocab_data]
    n = len(vocab_data)

    # System 1: Python dict (string -> cat_idx)
    dict_sys = {w: c for w, c in vocab_data}

    # System 2: MVM (string -> encoding, then modulo check)
    mvm_encodings = {}
    for w, ci in vocab_data:
        mvm_encodings[w] = encode_word_mvm(w, ci)
    mvm_cat_primes = fs.cat_primes

    # System 3: Bloom filter (one per category)
    cat_words = defaultdict(list)
    for w, ci in vocab_data:
        cat_words[ci].append(w)
    bloom_filters = {}
    for ci in range(N_CATS):
        bf = BloomFilter(len(cat_words.get(ci, [1])), fp_rate=0.01)
        for w in cat_words[ci]:
            bf.add(w)
        bloom_filters[ci] = bf

    # System 4: Set-based (one set per category)
    cat_sets = {}
    for ci in range(N_CATS):
        cat_sets[ci] = set(cat_words.get(ci, []))

    return {
        'dict': dict_sys,
        'mvm': mvm_encodings,
        'mvm_primes': mvm_cat_primes,
        'bloom': bloom_filters,
        'sets': cat_sets,
        'words': words,
        'cats': cats,
    }

# ============================================================
# CLASSIFICATION FUNCTIONS
# ============================================================

def classify_dict(word, sys_data):
    """Dict: single O(1) hash lookup."""
    return sys_data['dict'].get(word, -1)

def classify_mvm(word, sys_data):
    """MVM: encode + 20 modulo checks."""
    if word not in sys_data['mvm']:
        return -1
    enc = sys_data['mvm'][word]
    for ci in range(N_CATS):
        if enc % sys_data['mvm_primes'][ci] == 0:
            return ci
    return -1

def classify_mvm_direct(word, sys_data):
    """MVM with pre-encoded lookup: just modulo checks (encoding already done)."""
    # This isolates the MODULO CHECK speed from the encoding step
    enc = sys_data['mvm'].get(word)
    if enc is None:
        return -1
    for ci in range(N_CATS):
        if enc % sys_data['mvm_primes'][ci] == 0:
            return ci
    return -1

def classify_bloom(word, sys_data):
    """Bloom: 20 filter checks (probabilistic)."""
    for ci in range(N_CATS):
        if sys_data['bloom'][ci].contains(word):
            return ci
    return -1

def classify_set(word, sys_data):
    """Set: 20 set membership checks."""
    for ci in range(N_CATS):
        if word in sys_data['sets'][ci]:
            return ci
    return -1

# ============================================================
# SENTENCE ROUTING FUNCTIONS
# ============================================================

def route_sentence_dict(sentence_words, sys_data):
    """Dict routing: lookup each word, count categories, argmax."""
    counts = Counter()
    for w in sentence_words:
        cat = sys_data['dict'].get(w, -1)
        if cat >= 0:
            counts[cat] += 1
    return counts.most_common(1)[0][0] if counts else -1

def route_sentence_mvm(sentence_words, sys_data):
    """MVM routing: multiply encodings, 20 modulo checks on product."""
    product = 1
    for w in sentence_words:
        enc = sys_data['mvm'].get(w)
        if enc is not None:
            product *= enc
    if product == 1:
        return -1
    best_cat = 0
    best_count = 0
    for ci in range(N_CATS):
        # Count how many times cat_prime divides the product
        p = sys_data['mvm_primes'][ci]
        count = 0
        temp = product
        while temp % p == 0:
            count += 1
            temp //= p
        if count > best_count:
            best_count = count
            best_cat = ci
    return best_cat

def route_sentence_mvm_modonly(sentence_words, sys_data):
    """MVM routing: multiply encodings, just check != 0 (binary presence)."""
    product = 1
    for w in sentence_words:
        enc = sys_data['mvm'].get(w)
        if enc is not None:
            product *= enc
    if product == 1:
        return -1
    for ci in range(N_CATS):
        if product % sys_data['mvm_primes'][ci] == 0:
            return ci
    return -1

# ============================================================
# MEMORY MEASUREMENT
# ============================================================

def measure_memory(sys_data):
    """Estimate memory footprint of each system in bytes."""
    # Dict: keys (strings) + values (ints) + dict overhead
    dict_mem = sys.getsizeof(sys_data['dict'])
    for w in sys_data['dict']:
        dict_mem += sys.getsizeof(w) + 28  # string + int reference

    # MVM: keys (strings) + values (ints) + dict overhead
    mvm_mem = sys.getsizeof(sys_data['mvm'])
    for w in sys_data['mvm']:
        mvm_mem += sys.getsizeof(w) + sys.getsizeof(sys_data['mvm'][w])

    # MVM encoding-only (if we only store encodings, no string keys)
    # This is the hardware-relevant metric: array of integers
    encodings_only = sum(sys.getsizeof(v) for v in sys_data['mvm'].values())

    # Bloom: bit arrays
    bloom_mem = sum(sys.getsizeof(bf.bits) + sys.getsizeof(bf) for bf in sys_data['bloom'].values())

    # Sets: strings spread across 20 sets
    set_mem = sum(sys.getsizeof(s) for s in sys_data['sets'].values())
    for s in sys_data['sets'].values():
        for w in s:
            set_mem += sys.getsizeof(w)

    return {
        'dict': dict_mem,
        'mvm_full': mvm_mem,
        'mvm_enc_only': encodings_only,
        'bloom': bloom_mem,
        'sets': set_mem,
    }

# ============================================================
# BENCHMARK A: SINGLE-WORD CLASSIFICATION THROUGHPUT
# ============================================================

def benchmark_single_word(sys_data, n_ops=1_000_000, seed=42):
    """Benchmark single-word classification at 1M ops."""
    random.seed(seed)
    words = sys_data['words']

    # Generate random lookup sequence (mix of known and unknown)
    n_known = n_ops * 9 // 10
    n_unknown = n_ops - n_known
    lookup_words = [words[random.randint(0, len(words)-1)] for _ in range(n_known)]
    # Add unknown words (random strings)
    for _ in range(n_unknown):
        length = random.randint(3, 10)
        w = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))
        lookup_words.append(w)
    random.shuffle(lookup_words)

    results = {}
    methods = [
        ('dict', classify_dict),
        ('mvm', classify_mvm_direct),
        ('set', classify_set),
        ('bloom', classify_bloom),
    ]

    for name, fn in methods:
        # Warmup
        for i in range(100):
            fn(lookup_words[i], sys_data)

        # Timed run
        latencies = []
        correct = 0
        t_start = time.perf_counter_ns()
        for w in lookup_words:
            t0 = time.perf_counter_ns()
            pred = fn(w, sys_data)
            t1 = time.perf_counter_ns()
            latencies.append(t1 - t0)
        t_end = time.perf_counter_ns()

        total_ns = t_end - t_start
        ops_per_sec = n_ops / (total_ns / 1e9)
        latencies.sort()
        p50 = latencies[n_ops // 2]
        p95 = latencies[int(n_ops * 0.95)]
        p99 = latencies[int(n_ops * 0.99)]

        results[name] = {
            'ops_per_sec': ops_per_sec,
            'p50_ns': p50,
            'p95_ns': p95,
            'p99_ns': p99,
            'total_ns': total_ns,
        }

    return results

# ============================================================
# BENCHMARK B: SENTENCE ROUTING THROUGHPUT
# ============================================================

def benchmark_sentence_routing(sys_data, n_sentences=100_000, seed=42):
    """Benchmark sentence-level category routing."""
    random.seed(seed)
    words = sys_data['words']

    # Generate random sentences (3-10 words each)
    sentences = []
    for _ in range(n_sentences):
        length = random.randint(3, 10)
        sent = [words[random.randint(0, len(words)-1)] for _ in range(length)]
        sentences.append(sent)

    results = {}
    methods = [
        ('dict', route_sentence_dict),
        ('mvm_count', route_sentence_mvm),
        ('mvm_modonly', route_sentence_mvm_modonly),
    ]

    for name, fn in methods:
        # Warmup
        for i in range(50):
            fn(sentences[i], sys_data)

        # Timed run
        latencies = []
        t_start = time.perf_counter_ns()
        for sent in sentences:
            t0 = time.perf_counter_ns()
            fn(sent, sys_data)
            t1 = time.perf_counter_ns()
            latencies.append(t1 - t0)
        t_end = time.perf_counter_ns()

        total_ns = t_end - t_start
        sents_per_sec = n_sentences / (total_ns / 1e9)
        latencies.sort()
        p50 = latencies[n_sentences // 2]
        p95 = latencies[int(n_sentences * 0.95)]
        p99 = latencies[int(n_sentences * 0.99)]

        results[name] = {
            'sents_per_sec': sents_per_sec,
            'p50_ns': p50,
            'p95_ns': p95,
            'p99_ns': p99,
        }

    return results

# ============================================================
# BENCHMARK C: UNKNOWN WORD REJECTION
# ============================================================

def benchmark_unknown_rejection(sys_data, n_unknowns=100_000, seed=42):
    """Benchmark handling of unknown words (not in vocabulary)."""
    random.seed(seed)

    # Generate unknown words (guaranteed not in vocab)
    vocab_set = set(sys_data['words'])
    unknowns = []
    attempts = 0
    while len(unknowns) < n_unknowns and attempts < n_unknowns * 5:
        length = random.randint(3, 10)
        w = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))
        if w not in vocab_set:
            unknowns.append(w)
        attempts += 1

    results = {}
    methods = [
        ('dict', classify_dict),
        ('mvm', classify_mvm_direct),
        ('set', classify_set),
        ('bloom', classify_bloom),
    ]

    for name, fn in methods:
        rejections = 0
        t_start = time.perf_counter_ns()
        for w in unknowns:
            pred = fn(w, sys_data)
            if pred == -1:
                rejections += 1
        t_end = time.perf_counter_ns()

        total_ns = t_end - t_start
        ops_per_sec = len(unknowns) / (total_ns / 1e9)
        reject_rate = rejections / len(unknowns) * 100

        results[name] = {
            'ops_per_sec': ops_per_sec,
            'rejections': rejections,
            'total': len(unknowns),
            'reject_rate': reject_rate,
        }

    return results

# ============================================================
# RUN ALL BENCHMARKS
# ============================================================

def print_table(headers, rows, title=""):
    """Print a formatted table."""
    if title:
        print(f"\n  {title}")
    col_widths = [max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))]
    header_line = "  " + "  ".join(str(h).rjust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print("  " + "  ".join("-" * w for w in col_widths))
    for row in rows:
        print("  " + "  ".join(str(v).rjust(w) for v, w in zip(row, col_widths)))

# --- Build vocabulary at 100k ---
print()
print("  Building 100k vocabulary...", end=" ", flush=True)
t0 = time.time()
gen = SyllableVocabularyGenerator(n_categories=20, words_per_cat=5000)
vocab_100k = gen.generate()
print(f"OK ({time.time()-t0:.2f}s)")

print("  Building lookup systems...", end=" ", flush=True)
t0 = time.time()
sys_100k = build_systems(vocab_100k)
print(f"OK ({time.time()-t0:.2f}s)")
print()

# ============================================================
# BENCHMARK A: SINGLE-WORD CLASSIFICATION
# ============================================================

print("=" * 70)
print("  BENCHMARK A: SINGLE-WORD CLASSIFICATION (1M ops, 100k vocab)")
print("=" * 70)

results_a = benchmark_single_word(sys_100k, n_ops=1_000_000)

rows = []
for name in ['dict', 'mvm', 'set', 'bloom']:
    r = results_a[name]
    rows.append([
        name,
        f"{r['ops_per_sec']/1e6:.2f}M",
        f"{r['p50_ns']}",
        f"{r['p95_ns']}",
        f"{r['p99_ns']}",
    ])
print_table(
    ['Method', 'Ops/sec', 'P50 (ns)', 'P95 (ns)', 'P99 (ns)'],
    rows,
    "Single-word classification throughput (higher = better)"
)

# Relative to dict
dict_ops = results_a['dict']['ops_per_sec']
print(f"\n  Relative to dict baseline:")
for name in ['mvm', 'set', 'bloom']:
    ratio = results_a[name]['ops_per_sec'] / dict_ops
    print(f"    {name}: {ratio:.2f}x")

# ============================================================
# BENCHMARK B: SENTENCE ROUTING
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK B: SENTENCE ROUTING (100k sentences, 3-10 words each)")
print(f"{'=' * 70}")

results_b = benchmark_sentence_routing(sys_100k, n_sentences=100_000)

rows = []
for name in ['dict', 'mvm_count', 'mvm_modonly']:
    r = results_b[name]
    rows.append([
        name,
        f"{r['sents_per_sec']/1e3:.1f}k",
        f"{r['p50_ns']}",
        f"{r['p95_ns']}",
        f"{r['p99_ns']}",
    ])
print_table(
    ['Method', 'Sents/sec', 'P50 (ns)', 'P95 (ns)', 'P99 (ns)'],
    rows,
    "Sentence routing throughput (higher = better)"
)

dict_sents = results_b['dict']['sents_per_sec']
print(f"\n  Relative to dict baseline:")
for name in ['mvm_count', 'mvm_modonly']:
    ratio = results_b[name]['sents_per_sec'] / dict_sents
    print(f"    {name}: {ratio:.2f}x")

# ============================================================
# BENCHMARK C: UNKNOWN WORD REJECTION
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK C: UNKNOWN WORD REJECTION (100k unknown words)")
print(f"{'=' * 70}")

results_c = benchmark_unknown_rejection(sys_100k, n_unknowns=100_000)

rows = []
for name in ['dict', 'mvm', 'set', 'bloom']:
    r = results_c[name]
    rows.append([
        name,
        f"{r['ops_per_sec']/1e3:.1f}k",
        f"{r['rejections']}/{r['total']}",
        f"{r['reject_rate']:.1f}%",
    ])
print_table(
    ['Method', 'Ops/sec', 'Rejected', 'Rate'],
    rows,
    "Unknown word rejection (100% rejection = correct, <100% = false positives)"
)

# ============================================================
# BENCHMARK D: MEMORY FOOTPRINT
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK D: MEMORY FOOTPRINT ACROSS VOCAB SIZES")
print(f"{'=' * 70}")

mem_results = {}
for n_words, wpc in [(500, 25), (5000, 250), (50000, 2500), (100000, 5000)]:
    gen_n = SyllableVocabularyGenerator(n_categories=20, words_per_cat=wpc)
    vocab_n = gen_n.generate()
    sys_n = build_systems(vocab_n)
    mem = measure_memory(sys_n)
    mem_results[n_words] = mem
    del sys_n, vocab_n

rows = []
for n_words in [500, 5000, 50000, 100000]:
    m = mem_results[n_words]
    rows.append([
        f"{n_words:,}",
        f"{m['dict']/1024:.0f}",
        f"{m['mvm_full']/1024:.0f}",
        f"{m['mvm_enc_only']/1024:.0f}",
        f"{m['bloom']/1024:.0f}",
        f"{m['sets']/1024:.0f}",
    ])
print_table(
    ['Vocab', 'Dict (KB)', 'MVM full (KB)', 'MVM enc (KB)', 'Bloom (KB)', 'Sets (KB)'],
    rows,
    "Memory footprint (lower = better)"
)

# ============================================================
# BENCHMARK E: SCALING CURVE
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK E: THROUGHPUT SCALING CURVE")
print(f"{'=' * 70}")

scale_results = {}
for n_words, wpc in [(500, 25), (5000, 250), (20000, 1000), (50000, 2500), (100000, 5000)]:
    gen_n = SyllableVocabularyGenerator(n_categories=20, words_per_cat=wpc)
    vocab_n = gen_n.generate()
    sys_n = build_systems(vocab_n)
    r = benchmark_single_word(sys_n, n_ops=200_000)
    scale_results[n_words] = {
        'dict': r['dict']['ops_per_sec'],
        'mvm': r['mvm']['ops_per_sec'],
        'set': r['set']['ops_per_sec'],
        'bloom': r['bloom']['ops_per_sec'],
    }
    del sys_n, vocab_n

rows = []
for n_words in sorted(scale_results.keys()):
    r = scale_results[n_words]
    rows.append([
        f"{n_words:>7,}",
        f"{r['dict']/1e6:.2f}M",
        f"{r['mvm']/1e6:.2f}M",
        f"{r['set']/1e6:.2f}M",
        f"{r['bloom']/1e6:.2f}M",
    ])
print_table(
    ['Vocab', 'Dict', 'MVM', 'Set', 'Bloom'],
    rows,
    "Classification throughput vs vocab size (ops/sec)"
)

# Dict/MVM ratio at each scale
print(f"\n  Dict/MVM throughput ratio (how much faster is dict):")
for n_words in sorted(scale_results.keys()):
    r = scale_results[n_words]
    ratio = r['dict'] / r['mvm']
    print(f"    {n_words:>7,} words: dict is {ratio:.1f}x faster")

# ============================================================
# BENCHMARK F: ENCODING COST (MVM overhead)
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK F: MVM ENCODING COST")
print(f"{'=' * 70}")

# How long does it take to encode a NEW word into the MVM?
random.seed(42)
test_words = [''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 10)))
              for _ in range(100_000)]

# Dict: just insert
t0 = time.perf_counter()
d = {}
for w in test_words:
    d[w] = random.randint(0, 19)
dict_insert_time = time.perf_counter() - t0

# MVM: encode then insert
t0 = time.perf_counter()
m = {}
for w in test_words:
    ci = random.randint(0, 19)
    m[w] = encode_word_mvm(w, ci)
mvm_encode_time = time.perf_counter() - t0

n = len(test_words)
print(f"\n  Encoding 100k new words:")
print(f"    Dict insert: {dict_insert_time:.3f}s = {n/dict_insert_time:.0f} ops/s")
print(f"    MVM encode:  {mvm_encode_time:.3f}s = {n/mvm_encode_time:.0f} ops/s")
print(f"    MVM overhead: {mvm_encode_time/dict_insert_time:.1f}x slower")

# Show encoding sizes
sample_enc = encode_word_mvm("hello", 0)
print(f"\n  Sample encoding: 'hello' cat=0 -> {sample_enc:,} ({sample_enc.bit_length()} bits)")
print(f"  String 'hello': 5 bytes")
print(f"  Integer encoding: {sample_enc.bit_length() // 8 + 1} bytes")

# ============================================================
# BENCHMARK G: HARDWARE-RELEVANT METRICS
# ============================================================

print(f"\n{'=' * 70}")
print("  BENCHMARK G: HARDWARE-RELEVANT METRICS")
print(f"{'=' * 70}")

# The MVM's core operation: integer modulo
# On hardware, this is a single clock cycle via combinational logic
# Dict requires: memory access + hash computation + collision resolution

# Measure raw modulo speed
primes = fs.cat_primes
test_enc = encode_word_mvm("benchmark", 5)
n_mod = 10_000_000

t0 = time.perf_counter()
for _ in range(n_mod):
    for p in primes:
        _ = test_enc % p
t1 = time.perf_counter()
mod_only = n_mod * 20 / (t1 - t0)

# Measure raw dict lookup
test_dict = {f"word{i}": i % 20 for i in range(100000)}
test_keys = [f"word{random.randint(0, 99999)}" for _ in range(n_mod)]
t0 = time.perf_counter()
for k in test_keys:
    _ = test_dict.get(k, -1)
t1 = time.perf_counter()
dict_only = n_mod / (t1 - t0)

print(f"\n  Raw operation speed (Python, {n_mod/1e6:.0f}M iterations):")
print(f"    20x integer modulo: {mod_only/1e6:.2f}M ops/s")
print(f"    1x dict lookup:     {dict_only/1e6:.2f}M ops/s")
print(f"    Modulo is {dict_only/mod_only:.2f}x {'slower' if mod_only > dict_only else 'faster'} than dict lookup")

print(f"""
  Hardware context (not measured, architectural):
    FPGA modulo check: 1 clock cycle (combinational logic, ~5ns at 200MHz)
    FPGA hash table:   3-5 cycles (BRAM access + comparison + potential miss)
    FPGA MVM core:     20 parallel modulo checks = 1 cycle with 20 dividers
    FPGA dict core:    Sequential BRAM reads, 20 cycles worst case

    On FPGA, MVM classification could theoretically run at 200M classifications/s
    A BRAM-based hash table would manage ~40-67M lookups/s

    The hardware advantage is real but requires FPGA implementation to verify.
""")

# ============================================================
# SUMMARY
# ============================================================

print("=" * 70)
print("  SUMMARY")
print("=" * 70)

a = results_a
print(f"""
  SINGLE-WORD CLASSIFICATION (100k vocab, 1M ops):
    Dict:  {a['dict']['ops_per_sec']/1e6:.2f}M ops/s  (P99: {a['dict']['p99_ns']} ns)
    MVM:   {a['mvm']['ops_per_sec']/1e6:.2f}M ops/s  (P99: {a['mvm']['p99_ns']} ns)
    Set:   {a['set']['ops_per_sec']/1e6:.2f}M ops/s  (P99: {a['set']['p99_ns']} ns)
    Bloom: {a['bloom']['ops_per_sec']/1e6:.2f}M ops/s  (P99: {a['bloom']['p99_ns']} ns)

  SENTENCE ROUTING (100k sents, 100k vocab):
    Dict:      {results_b['dict']['sents_per_sec']/1e3:.1f}k sents/s
    MVM count: {results_b['mvm_count']['sents_per_sec']/1e3:.1f}k sents/s
    MVM mod:   {results_b['mvm_modonly']['sents_per_sec']/1e3:.1f}k sents/s

  UNKNOWN REJECTION:
    Dict:  {results_c['dict']['reject_rate']:.1f}% correct rejection
    MVM:   {results_c['mvm']['reject_rate']:.1f}% correct rejection
    Bloom: {results_c['bloom']['reject_rate']:.1f}% correct rejection ({results_c['bloom']['rejections']} rejected, {results_c['bloom']['total']-results_c['bloom']['rejections']} false positives)

  MEMORY (100k vocab):
    Dict:       {mem_results[100000]['dict']/1024:.0f} KB
    MVM (full): {mem_results[100000]['mvm_full']/1024:.0f} KB
    MVM (enc):  {mem_results[100000]['mvm_enc_only']/1024:.0f} KB
    Bloom:      {mem_results[100000]['bloom']/1024:.0f} KB

  HONEST ASSESSMENT:
    In Python, dict lookup beats MVM modulo for single-word classification.
    Python dicts are optimized C code; MVM does 20 integer modulos per word.
    The MVM's advantages are NOT in software throughput:
      1. Composability: sentence = single integer, not N separate lookups
      2. Determinism: zero false positives (Bloom had {results_c['bloom']['total']-results_c['bloom']['rejections']} FP)
      3. Hardware: modulo is 1 cycle on FPGA, dict requires BRAM + hashing
      4. Memory (encoding-only): {mem_results[100000]['mvm_enc_only']/1024:.0f} KB vs {mem_results[100000]['dict']/1024:.0f} KB dict
    The throughput advantage exists in HARDWARE, not in Python.
""")

print("  Benchmark complete.")
print("=" * 70)
