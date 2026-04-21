"""
OOD Classifier Test: Can structural primes predict category WITHOUT the category prime?

The core question: Is MVM classification a tautology (category prime is literally
a factor), or do structural features carry genuine category information?

Test 1: v0.8 curated 500-word vocabulary (semantic structure in features)
  - Animals tend to be short, professions end in -er, sports end in -ing, etc.
  - Structural features SHOULD correlate with category -> above-chance accuracy

Test 2: v0.12 generated 100k vocabulary (random structure by construction)
  - Categories assigned by index, not semantics
  - Structural features are category-agnostic -> chance accuracy (~5%)

Test 3: True OOD -- words NOT in any vocabulary, hand-picked with clear categories

Three classification methods:
  1. GCD Resonance: gcd(test_struct, category_centroid) -> predict highest
  2. Shared Factor Count: count overlapping primes with category profile
  3. Weighted Frequency: sum per-prime category frequencies (Naive Bayes analog)

ZERO FLOATS. int, Fraction only.
"""

from math import gcd
from fractions import Fraction
from collections import defaultdict, Counter
import time
import random

print("=" * 70)
print("OOD CLASSIFIER TEST -- Structural Prime Resonance")
print("=" * 70)

# ============================================================
# LAYER 0: PRIME SUBSTRATE
# ============================================================

class PrimeSubstrate:
    def __init__(self, limit=500_000):
        self.limit = limit
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

print()
print("  Initializing substrate...", end=" ", flush=True)
substrate = PrimeSubstrate(500_000)
print("OK")

# ============================================================
# LAYER 1: FEATURE SPACE + ENCODING
# ============================================================

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
        self.base_primes = substrate.first_n_primes(100)
        self.cat_primes = self.base_primes[0:20]
        self.fl_primes = self.base_primes[20:46]
        self.ll_primes = self.base_primes[46:72]
        self.len_primes = self.base_primes[72:78]
        self.morph_primes = self.base_primes[78:94]
        self.hash_primes = self.base_primes[94:100]

def deterministic_hash(word):
    h = 5381
    for ch in word:
        h = ((h * 33) + ord(ch)) & 0xFFFFFFFF
    return h

fs = FeatureSpace(substrate)

# Structural-only encoding (no category prime)
def encode_structural(word):
    """Encode word with structural primes only. Returns (encoding, prime_set)."""
    primes_used = set()
    enc = 1
    if word and word[0].isalpha():
        p = fs.fl_primes[ord(word[0].lower()) - ord('a')]
        enc *= p
        primes_used.add(p)
    if word and word[-1].isalpha():
        p = fs.ll_primes[ord(word[-1].lower()) - ord('a')]
        enc *= p
        primes_used.add(p)
    wlen = len(word)
    for i, (lo, hi) in enumerate(LENGTH_BUCKETS):
        if lo <= wlen <= hi:
            p = fs.len_primes[i]
            break
    else:
        p = fs.len_primes[-1]
    enc *= p
    primes_used.add(p)
    for si, sfx in enumerate(SUFFIXES):
        if word.endswith(sfx):
            p = fs.morph_primes[si]
            enc *= p
            primes_used.add(p)
            break
    for pi, pfx in enumerate(PREFIXES):
        if word.startswith(pfx):
            p = fs.morph_primes[11 + pi]
            enc *= p
            primes_used.add(p)
            break
    h = deterministic_hash(word)
    for offset in [h % 6, (h >> 8) % 6]:
        p = fs.hash_primes[offset]
        enc *= p
        primes_used.add(p)
    return enc, primes_used

print("  Feature space ready (100 primes)")
print()

# ============================================================
# VOCABULARY 1: CURATED 500-word (from v0.8)
# ============================================================

_VOCAB_RAW = {
    'emotions': [
        'love', 'hate', 'joy', 'fear', 'anger', 'peace', 'happy', 'sad',
        'hope', 'grief', 'pride', 'shame', 'guilt', 'envy', 'bliss', 'rage',
        'calm', 'dread', 'sorrow', 'delight', 'trust', 'disgust', 'awe',
        'despair', 'cheer',
    ],
    'animals': [
        'cat', 'dog', 'bird', 'lion', 'tiger', 'bear', 'wolf', 'deer',
        'fox', 'eagle', 'shark', 'whale', 'snake', 'horse', 'rabbit', 'owl',
        'hawk', 'frog', 'bee', 'ant', 'elephant', 'monkey', 'dolphin',
        'penguin', 'giraffe',
    ],
    'colors': [
        'red', 'blue', 'green', 'yellow', 'white', 'black', 'purple',
        'orange', 'pink', 'gray', 'brown', 'crimson', 'violet', 'indigo',
        'scarlet', 'azure', 'teal', 'coral', 'magenta', 'maroon', 'ivory',
        'amber', 'bronze', 'copper', 'beige',
    ],
    'foods': [
        'bread', 'cheese', 'apple', 'rice', 'meat', 'soup', 'cake',
        'pasta', 'fruit', 'honey', 'butter', 'cream', 'sugar', 'spice',
        'wheat', 'corn', 'bean', 'mango', 'melon', 'peach', 'plum',
        'cherry', 'lemon', 'garlic', 'tomato',
    ],
    'weather': [
        'rain', 'snow', 'wind', 'storm', 'cloud', 'fog', 'ice', 'hail',
        'frost', 'thunder', 'heat', 'cold', 'breeze', 'drizzle', 'sleet',
        'mist', 'dew', 'gale', 'blizzard', 'tornado', 'hurricane', 'damp',
        'sunny', 'cloudy', 'arid',
    ],
    'professions': [
        'doctor', 'teacher', 'farmer', 'baker', 'chef', 'pilot', 'nurse',
        'judge', 'clerk', 'artist', 'writer', 'driver', 'miner', 'sailor',
        'guard', 'tailor', 'mason', 'painter', 'singer', 'dancer', 'lawyer',
        'engineer', 'plumber', 'barber', 'mechanic',
    ],
    'vehicles': [
        'car', 'bus', 'train', 'truck', 'boat', 'ship', 'plane', 'bike',
        'van', 'taxi', 'scooter', 'yacht', 'canoe', 'tram', 'ferry',
        'tractor', 'cart', 'kayak', 'skateboard', 'wagon', 'helicopter',
        'submarine', 'jetpack', 'unicycle', 'rickshaw',
    ],
    'instruments': [
        'piano', 'guitar', 'drum', 'flute', 'violin', 'harp', 'horn',
        'cello', 'organ', 'banjo', 'trumpet', 'tuba', 'sax', 'oboe',
        'viola', 'lute', 'clarinet', 'trombone', 'harmonica', 'accordion',
        'bass', 'xylophone', 'ukulele', 'mandolin', 'synthesizer',
    ],
    'sports': [
        'football', 'soccer', 'tennis', 'golf', 'boxing', 'rugby',
        'skiing', 'surfing', 'hockey', 'judo', 'fencing', 'archery',
        'polo', 'diving', 'rowing', 'skating', 'climbing', 'cycling',
        'running', 'swimming', 'baseball', 'cricket', 'wrestling',
        'volleyball', 'basketball',
    ],
    'plants': [
        'tree', 'flower', 'grass', 'fern', 'moss', 'vine', 'shrub',
        'oak', 'pine', 'maple', 'rose', 'lily', 'ivy', 'reed', 'bamboo',
        'palm', 'cedar', 'elm', 'ash', 'birch', 'willow', 'tulip',
        'daisy', 'orchid', 'spruce',
    ],
    'tools': [
        'hammer', 'saw', 'drill', 'chisel', 'pliers', 'ruler', 'level',
        'file', 'clamp', 'rasp', 'mallet', 'trowel', 'spade', 'hoe',
        'sickle', 'wedge', 'anvil', 'caliper', 'funnel', 'gouge',
        'lathe', 'vise', 'shears', 'tongs', 'gimlet',
    ],
    'clothing': [
        'shirt', 'pants', 'dress', 'coat', 'hat', 'shoe', 'boot', 'sock',
        'glove', 'scarf', 'belt', 'tie', 'vest', 'cape', 'gown', 'skirt',
        'blouse', 'jacket', 'sweater', 'hood', 'robe', 'apron', 'veil',
        'shawl', 'cloak',
    ],
    'buildings': [
        'house', 'church', 'temple', 'tower', 'bridge', 'castle', 'fort',
        'barn', 'mill', 'inn', 'shop', 'bank', 'school', 'factory',
        'palace', 'villa', 'cabin', 'lodge', 'shed', 'silo', 'warehouse',
        'stadium', 'library', 'museum', 'hospital',
    ],
    'gems': [
        'diamond', 'ruby', 'emerald', 'sapphire', 'pearl', 'opal', 'jade',
        'topaz', 'agate', 'onyx', 'quartz', 'garnet', 'zircon', 'beryl',
        'moonstone', 'peridot', 'spinel', 'turquoise', 'obsidian', 'citrine',
        'tourmaline', 'hematite', 'pyrite', 'fluorite', 'amazonite',
    ],
    'weapons': [
        'sword', 'spear', 'bow', 'shield', 'mace', 'lance', 'dagger',
        'arrow', 'club', 'flail', 'pike', 'halberd', 'crossbow', 'katana',
        'rapier', 'cutlass', 'slingshot', 'catapult', 'trebuchet', 'cudgel',
        'bayonet', 'javelin', 'tomahawk', 'dirk', 'scythe',
    ],
    'seasons': [
        'spring', 'summer', 'autumn', 'winter', 'solstice', 'equinox',
        'monsoon', 'harvest', 'blossom', 'bud', 'thaw', 'freeze', 'seeding',
        'ripening', 'blooming', 'waning', 'flourishing', 'dormant',
        'sprouting', 'estivation', 'brumation', 'hibernation', 'nesting',
        'migration', 'wither',
    ],
    'terrain': [
        'mountain', 'valley', 'plain', 'desert', 'canyon', 'cliff',
        'ridge', 'plateau', 'basin', 'swamp', 'marsh', 'dune', 'glacier',
        'volcano', 'cave', 'beach', 'coast', 'delta', 'gorge', 'mesa',
        'butte', 'tundra', 'prairie', 'steppe', 'moor',
    ],
    'beverages': [
        'water', 'coffee', 'tea', 'milk', 'juice', 'wine', 'beer',
        'cider', 'cocoa', 'soda', 'lemonade', 'smoothie', 'espresso',
        'latte', 'mocha', 'broth', 'nectar', 'punch', 'tonic', 'grog',
        'toddy', 'chamomile', 'peppermint', 'matcha', 'kombucha',
    ],
    'astronomy': [
        'planet', 'comet', 'galaxy', 'nebula', 'quasar', 'pulsar',
        'asteroid', 'meteor', 'eclipse', 'orbit', 'cosmos', 'universe',
        'supernova', 'constellation', 'venus', 'mars', 'jupiter', 'saturn',
        'mercury', 'pluto', 'neptune', 'uranus', 'sirius', 'betelgeuse',
        'andromeda',
    ],
    'mythology': [
        'zeus', 'thor', 'odin', 'loki', 'athena', 'apollo', 'hermes',
        'aphrodite', 'poseidon', 'hades', 'artemis', 'ares', 'dionysus',
        'hephaestus', 'hera', 'demeter', 'persephone', 'heracles',
        'achilles', 'odysseus', 'prometheus', 'phoenix', 'griffin',
        'dragon', 'unicorn',
    ],
}

# Build curated dataset: list of (word, cat_idx)
curated_data = []
for cat_name, words in _VOCAB_RAW.items():
    cat_idx = CATEGORIES.index(cat_name)
    for w in words:
        curated_data.append((w, cat_idx))

print(f"  Curated vocabulary: {len(curated_data)} words, {N_CATS} categories")

# ============================================================
# VOCABULARY 2: GENERATED 100k (from v0.12)
# ============================================================

class SyllableVocabularyGenerator:
    CONSONANTS = 'bcdfghjklmnprstvwz'  # 18
    VOWELS = 'aeiou'                    # 5

    def __init__(self, n_categories=20, words_per_cat=5000):
        self.n_categories = n_categories
        self.words_per_cat = words_per_cat
        self.nc = len(self.CONSONANTS)
        self.nv = len(self.VOWELS)
        self.cvcv_space = self.nc * self.nv * self.nc * self.nv
        self.cvccv_space = self.nc * self.nv * self.nc * self.nc * self.nv
        self.total_space = self.cvcv_space + self.cvccv_space

    def _scramble(self, uid):
        return (uid * 7919 + 104729) % self.total_space

    def _idx_to_word(self, uid):
        C = self.CONSONANTS
        V = self.VOWELS
        nc, nv = self.nc, self.nv
        if uid < self.cvcv_space:
            c1 = uid // (nv * nc * nv)
            t  = uid %  (nv * nc * nv)
            v1 = t // (nc * nv)
            t  = t %  (nc * nv)
            c2 = t // nv
            v2 = t %  nv
            return C[c1] + V[v1] + C[c2] + V[v2]
        else:
            uid2 = uid - self.cvcv_space
            c1 = uid2 // (nv * nc * nc * nv)
            t  = uid2 %  (nv * nc * nc * nv)
            v1 = t // (nc * nc * nv)
            t  = t %  (nc * nc * nv)
            c2 = t // (nc * nv)
            t  = t %  (nc * nv)
            c3 = t // nv
            v2 = t %  nv
            return C[c1] + V[v1] + C[c2] + C[c3] + V[v2]

    def generate(self):
        vocab = []
        for cat_idx in range(self.n_categories):
            for word_idx in range(self.words_per_cat):
                uid = self._scramble(cat_idx * self.words_per_cat + word_idx)
                word = self._idx_to_word(uid)
                vocab.append((word, cat_idx))
        return vocab

print("  Generating 100k vocabulary...", end=" ", flush=True)
t0 = time.time()
gen = SyllableVocabularyGenerator(n_categories=20, words_per_cat=5000)
generated_data = gen.generate()
print(f"OK ({time.time()-t0:.2f}s, {len(generated_data):,} words)")
print()

# ============================================================
# VOCABULARY 3: TRUE OOD WORDS (not in any vocabulary)
# ============================================================

TRUE_OOD = [
    # Animals
    ('hamster', 1), ('parrot', 1), ('salmon', 1), ('octopus', 1), ('butterfly', 1),
    ('leopard', 1), ('scorpion', 1), ('flamingo', 1), ('jellyfish', 1), ('squirrel', 1),
    # Emotions
    ('jealousy', 0), ('anxiety', 0), ('nostalgia', 0), ('contempt', 0), ('ecstasy', 0),
    ('fury', 0), ('serenity', 0), ('melancholy', 0), ('euphoria', 0), ('apathy', 0),
    # Colors
    ('turquoise', 2), ('lavender', 2), ('chartreuse', 2), ('burgundy', 2), ('cerulean', 2),
    ('ochre', 2), ('mauve', 2), ('chartreuse', 2), ('periwinkle', 2), ('crimson', 2),
    # Foods
    ('avocado', 3), ('chocolate', 3), ('cinnamon', 3), ('mushroom', 3), ('broccoli', 3),
    ('pancake', 3), ('dumpling', 3), ('biscuit', 3), ('lasagna', 3), ('parsley', 3),
    # Weather
    ('cyclone', 4), ('drought', 4), ('humidity', 4), ('downpour', 4), ('whirlwind', 4),
    ('avalanche', 4), ('sleet', 4), ('mudslide', 4), ('gust', 4), ('fog', 4),
    # Professions
    ('architect', 5), ('surgeon', 5), ('carpenter', 5), ('electrician', 5), ('therapist', 5),
    ('librarian', 5), ('accountant', 5), ('firefighter', 5), ('pharmacist', 5), ('detective', 5),
    # Vehicles
    ('hovercraft', 6), ('gondola', 6), ('hydrofoil', 6), ('catamaran', 6), ('zeppelin', 6),
    ('snowmobile', 6), ('bulldozer', 6), ('motorboat', 6), ('glider', 6), ('tricycle', 6),
    # Instruments
    ('tambourine', 7), ('didgeridoo', 7), ('marimba', 7), ('sitar', 7), ('bongo', 7),
    ('cello', 7), ('lute', 7), ('zither', 7), ('theremin', 7), ('ocarina', 7),
    # Sports
    ('badminton', 8), ('lacrosse', 8), ('gymnastics', 8), ('snowboarding', 8), ('karate', 8),
    ('fencing', 8), ('triathlon', 8), ('handball', 8), ('rowing', 8), ('squash', 8),
    # Plants
    ('sunflower', 9), ('daffodil', 9), ('poinsettia', 9), ('snapdragon', 9), ('juniper', 9),
    ('eucalyptus', 9), ('magnolia', 9), ('cactus', 9), ('wisteria', 9), ('petunia', 9),
    # Tools
    ('wrench', 10), ('screwdriver', 10), ('bolt', 10), ('solder', 10), ('axe', 10),
    ('plumb', 10), ('chisel', 10), ('compass', 10), ('jackhammer', 10), ('pliers', 10),
    # Clothing
    ('parka', 11), ('cardigan', 11), ('trousers', 11), ('kimono', 11), ('tunic', 11),
    ('sweatpants', 11), ('camisole', 11), ('blazer', 11), ('poncho', 11), ('mittens', 11),
    # Buildings
    ('skyscraper', 12), ('cathedral', 12), ('fortress', 12), ('igloo', 12), ('pagoda', 12),
    ('lighthouse', 12), ('barracks', 12), ('greenhouse', 12), ('dungeon', 12), ('mosque', 12),
    # Gems
    ('alexandrite', 13), ('tanzanite', 13), ('morganite', 13), ('kunzite', 13), ('jadeite', 13),
    ('sapphire', 13), ('malachite', 13), ('lapis', 13), ('opal', 13), ('zircon', 13),
    # Weapons
    ('crossbow', 14), ('broadsword', 14), ('shuriken', 14), ('machete', 14), ('morningstar', 14),
    ('bolas', 14), ('blowgun', 14), ('nunchaku', 14), ('warhammer', 14), ('katana', 14),
    # Seasons
    ('autumnal', 15), ('vernal', 15), ('hiemal', 15), ('estival', 15), ('perennial', 15),
    ('crocus', 15), ('snowdrop', 15), ('chrysanthemum', 15), ('harvest', 15), ('equinox', 15),
    # Terrain
    ('fjord', 16), ('badlands', 16), ('rainforest', 16), ('tundra', 16), ('sinkhole', 16),
    ('crater', 16), ('lagoon', 16), ('peninsula', 16), ('archipelago', 16), ('savanna', 16),
    # Beverages
    ('frappuccino', 17), ('margarita', 17), ('horchata', 17), ('chai', 17), ('guinness', 17),
    ('kombucha', 17), ('spritzer', 17), ('cordial', 17), ('cappuccino', 17), ('daiquiri', 17),
    # Astronomy
    ('telescope', 18), ('magnetar', 18), ('magnetosphere', 18), ('eventhorizon', 18),
    ('singularity', 18), ('blackhole', 18), ('redgiant', 18), ('whitedwarf', 18),
    ('spacetime', 18), ('lightyear', 18),
    # Mythology
    ('medusa', 19), ('minotaur', 19), ('centaur', 19), ('hydra', 19), ('pegasus', 19),
    ('cerberus', 19), ('kraken', 19), ('sphinx', 19), ('cyclops', 19), ('chimera', 19),
]

# Remove any duplicates from true OOD that appear in curated vocabulary
curated_words = set(w for w, _ in curated_data)
TRUE_OOD = [(w, c) for w, c in TRUE_OOD if w not in curated_words]

print(f"  True OOD test set: {len(TRUE_OOD)} words (not in curated vocab)")

# ============================================================
# CATEGORY PROFILER
# ============================================================

class CategoryProfiler:
    """Builds structural prime profiles per category from training data."""

    def __init__(self, train_data):
        """
        train_data: list of (word, cat_idx)
        """
        self.cat_prime_counts = defaultdict(Counter)  # cat -> {prime: count}
        self.cat_word_counts = defaultdict(int)
        self.cat_word_list = defaultdict(list)  # cat -> [(word, enc, primes)]

        for word, cat_idx in train_data:
            self.cat_word_counts[cat_idx] += 1
            enc, primes = encode_structural(word)
            self.cat_word_list[cat_idx].append((word, enc, primes))
            for p in primes:
                self.cat_prime_counts[cat_idx][p] += 1

        # Build centroids at 30% threshold
        self.centroids = {}
        self.centroid_primes = {}
        for cat_idx in range(N_CATS):
            n = max(self.cat_word_counts.get(cat_idx, 0), 1)
            threshold = n * 3 // 10
            typical = set()
            enc = 1
            for p, count in self.cat_prime_counts[cat_idx].items():
                if count >= threshold:
                    typical.add(p)
                    enc *= p
            self.centroids[cat_idx] = enc
            self.centroid_primes[cat_idx] = typical

    def classify_gcd(self, word):
        """GCD resonance: predict category with highest gcd."""
        enc, primes = encode_structural(word)
        best_cat = 0
        best_gcd = 0
        for cat_idx in range(N_CATS):
            g = gcd(enc, self.centroids[cat_idx])
            if g > best_gcd:
                best_gcd = g
                best_cat = cat_idx
        return best_cat, best_gcd

    def classify_overlap(self, word):
        """Shared factor count: predict category with most overlapping primes."""
        enc, primes = encode_structural(word)
        best_cat = 0
        best_overlap = -1
        for cat_idx in range(N_CATS):
            overlap = len(primes & self.centroid_primes[cat_idx])
            if overlap > best_overlap:
                best_overlap = overlap
                best_cat = cat_idx
        return best_cat, best_overlap

    def classify_weighted(self, word):
        """Weighted frequency: Naive Bayes analog using prime frequencies."""
        enc, primes = encode_structural(word)
        best_cat = 0
        best_score = -1
        for cat_idx in range(N_CATS):
            n = max(self.cat_word_counts.get(cat_idx, 0), 1)
            score = 0
            for p in primes:
                count = self.cat_prime_counts[cat_idx].get(p, 0)
                if count > 0:
                    # Fraction(pseudo_count, total) as score
                    score += count * 1000 // n
            if score > best_score:
                best_score = score
                best_cat = cat_idx
        return best_cat, best_score

    def classify_1nn(self, word):
        """1-nearest-neighbor: find single most similar training word."""
        enc, primes = encode_structural(word)
        best_cat = 0
        best_gcd = 0
        best_word = ""
        for cat_idx in range(N_CATS):
            for train_word, train_enc, train_primes in self.cat_word_list[cat_idx]:
                g = gcd(enc, train_enc)
                if g > best_gcd:
                    best_gcd = g
                    best_cat = cat_idx
                    best_word = train_word
        return best_cat, best_gcd, best_word

    def show_profiles(self, n_cats=5):
        """Display structural profiles for top categories."""
        print()
        print("  STRUCTURAL PRIME PROFILES (primes in >30% of category words):")
        print(f"  {'Category':<14s} {'N':>4s} {'Centroid primes':<60s}")
        print("  " + "-" * 78)
        for cat_idx in range(min(n_cats, N_CATS)):
            n = self.cat_word_counts.get(cat_idx, 0)
            primes = sorted(self.centroid_primes[cat_idx])
            # Map primes to feature names
            labels = []
            for p in primes:
                if p in fs.fl_primes:
                    idx = fs.fl_primes.index(p)
                    labels.append(f"fl:{chr(ord('a')+idx)}")
                elif p in fs.ll_primes:
                    idx = fs.ll_primes.index(p)
                    labels.append(f"ll:{chr(ord('a')+idx)}")
                elif p in fs.len_primes:
                    idx = fs.len_primes.index(p)
                    labels.append(f"len:{LENGTH_BUCKETS[idx]}")
                elif p in fs.morph_primes:
                    idx = fs.morph_primes.index(p)
                    if idx < 11:
                        labels.append(f"-{SUFFIXES[idx]}")
                    else:
                        labels.append(f"{PREFIXES[idx-11]}-")
                elif p in fs.hash_primes:
                    idx = fs.hash_primes.index(p)
                    labels.append(f"h{idx}")
            pstr = ", ".join(labels) if labels else "(none above threshold)"
            print(f"  {CATEGORIES[cat_idx]:<14s} {n:4d}   {pstr}")

# ============================================================
# TEST RUNNER
# ============================================================

def run_holdout_test(data, name, train_frac=Fraction(4, 5), seed=42):
    """Run 80/20 holdout test with all classification methods."""
    data = list(data)  # copy
    random.seed(seed)
    random.shuffle(data)
    split = int(len(data) * float(train_frac))
    train = data[:split]
    test = data[split:]

    profiler = CategoryProfiler(train)

    print(f"\n{'=' * 70}")
    print(f"  {name}")
    print(f"  Train: {len(train)} | Test: {len(test)} | Categories: {N_CATS}")
    print(f"{'=' * 70}")

    profiler.show_profiles(n_cats=N_CATS)

    # Run classifications
    methods = ['gcd', 'overlap', 'weighted', '1nn']
    correct = defaultdict(int)
    per_cat_correct = defaultdict(lambda: defaultdict(int))
    per_cat_total = defaultdict(int)

    for word, true_cat in test:
        per_cat_total[true_cat] += 1
        for method in methods:
            if method == 'gcd':
                pred, _ = profiler.classify_gcd(word)
            elif method == 'overlap':
                pred, _ = profiler.classify_overlap(word)
            elif method == 'weighted':
                pred, _ = profiler.classify_weighted(word)
            elif method == '1nn':
                pred, _, _ = profiler.classify_1nn(word)
            if pred == true_cat:
                correct[method] += 1
                per_cat_correct[method][true_cat] += 1

    n_test = len(test)
    chance_pct = 100.0 / N_CATS
    print(f"\n  OVERALL ACCURACY:")
    print(f"  {'Method':<14s} {'Correct':>10s} {'Accuracy':>10s} {'vs Chance':>10s}")
    print(f"  {'-'*44}")
    for method in methods:
        c = correct[method]
        pct = c / n_test * 100
        ratio = pct / chance_pct
        print(f"  {method:<14s} {c:>10d} {pct:>9.1f}% {ratio:>9.1f}x")
    print(f"  {'chance':<14s} {'~'+str(n_test//N_CATS):>10s} {chance_pct:>9.1f}%")

    # Per-category breakdown for curated vocab
    if len(test) <= 1000:
        print(f"\n  PER-CATEGORY BREAKDOWN (weighted method):")
        print(f"  {'Category':<14s} {'Total':>6s} {'Correct':>8s} {'Accuracy':>10s}")
        print(f"  {'-'*40}")
        for cat_idx in range(N_CATS):
            t = per_cat_total[cat_idx]
            c = per_cat_correct['weighted'][cat_idx]
            pct = c / t * 100 if t > 0 else 0
            print(f"  {CATEGORIES[cat_idx]:<14s} {t:>6d} {c:>8d} {pct:>9.1f}%")

    return correct, n_test

def run_true_ood_test(profiler, ood_data, name):
    """Test on truly out-of-distribution words."""
    print(f"\n{'=' * 70}")
    print(f"  {name} ({len(ood_data)} words)")
    print(f"{'=' * 70}")

    methods = ['gcd', 'overlap', 'weighted']
    correct = defaultdict(int)
    details = []

    for word, true_cat in ood_data:
        preds = {}
        scores = {}
        enc, primes = encode_structural(word)

        # GCD
        best_cat, best_gcd = 0, 0
        for cat_idx in range(N_CATS):
            g = gcd(enc, profiler.centroids[cat_idx])
            if g > best_gcd:
                best_gcd = g
                best_cat = cat_idx
        preds['gcd'] = best_cat
        scores['gcd'] = best_gcd

        # Overlap
        best_cat, best_ov = 0, -1
        for cat_idx in range(N_CATS):
            ov = len(primes & profiler.centroid_primes[cat_idx])
            if ov > best_ov:
                best_ov = ov
                best_cat = cat_idx
        preds['overlap'] = best_cat
        scores['overlap'] = best_ov

        # Weighted
        best_cat, best_wt = 0, -1
        for cat_idx in range(N_CATS):
            n = max(profiler.cat_word_counts.get(cat_idx, 0), 1)
            s = 0
            for p in primes:
                count = profiler.cat_prime_counts[cat_idx].get(p, 0)
                if count > 0:
                    s += count * 1000 // n
            if s > best_wt:
                best_wt = s
                best_cat = cat_idx
        preds['weighted'] = best_cat
        scores['weighted'] = best_wt

        for method in methods:
            if preds[method] == true_cat:
                correct[method] += 1

        details.append((word, CATEGORIES[true_cat],
                        CATEGORIES[preds['weighted']], preds['weighted'] == true_cat))

    n = len(ood_data)
    chance_pct = 100.0 / N_CATS
    print(f"\n  OVERALL ACCURACY:")
    print(f"  {'Method':<14s} {'Correct':>10s} {'Accuracy':>10s} {'vs Chance':>10s}")
    print(f"  {'-'*44}")
    for method in methods:
        c = correct[method]
        pct = c / n * 100
        ratio = pct / chance_pct
        print(f"  {method:<14s} {c:>10d} {pct:>9.1f}% {ratio:>9.1f}x")
    print(f"  {'chance':<14s} {'~'+str(n//N_CATS):>10s} {chance_pct:>9.1f}%")

    # Show sample predictions
    print(f"\n  SAMPLE PREDICTIONS (weighted method):")
    print(f"  {'Word':<16s} {'True':<14s} {'Predicted':<14s} {'Hit':>5s}")
    print(f"  {'-'*51}")
    for word, true_cat, pred_cat, hit in details[:40]:
        mark = "  OK" if hit else " MISS"
        print(f"  {word:<16s} {true_cat:<14s} {pred_cat:<14s}{mark:>5s}")

    return correct, n

# ============================================================
# SECTION 1: FEATURE ANALYSIS
# ============================================================

print(f"\n{'=' * 70}")
print("  SECTION 1: STRUCTURAL FEATURE ANALYSIS")
print(f"{'=' * 70}")

# Analyze which features carry category information in curated vocab
print("\n  Feature informativeness (curated vocabulary):")
print("  How much does each feature type vary across categories?")

# Per-category, compute average length
cat_lengths = defaultdict(list)
cat_first_letters = defaultdict(list)
cat_last_letters = defaultdict(list)
cat_suffixes = defaultdict(list)
for word, cat_idx in curated_data:
    cat_lengths[cat_idx].append(len(word))
    cat_first_letters[cat_idx].append(word[0])
    cat_last_letters[cat_idx].append(word[-1])
    has_suffix = False
    for sfx in SUFFIXES:
        if word.endswith(sfx):
            cat_suffixes[cat_idx].append(sfx)
            has_suffix = True
            break
    if not has_suffix:
        cat_suffixes[cat_idx].append('(none)')

print(f"\n  {'Category':<14s} {'AvgLen':>7s} {'1stLetter diversity':>22s} {'Top suffix':>15s}")
print(f"  {'-'*60}")
for cat_idx in range(N_CATS):
    avg_len = sum(cat_lengths[cat_idx]) / len(cat_lengths[cat_idx])
    fl_diversity = len(set(cat_first_letters[cat_idx]))
    suffix_counts = Counter(cat_suffixes[cat_idx])
    top_suffix = suffix_counts.most_common(1)[0]
    pct = top_suffix[1] / len(cat_suffixes[cat_idx]) * 100
    print(f"  {CATEGORIES[cat_idx]:<14s} {avg_len:>7.1f} {fl_diversity:>22d}   {top_suffix[0]} ({pct:.0f}%)")

# ============================================================
# SECTION 2: HOLDOUT TEST -- CURATED VOCABULARY
# ============================================================

print(f"\n\n{'=' * 70}")
print("  SECTION 2: HOLDOUT TEST -- CURATED 500-WORD VOCABULARY")
print(f"{'=' * 70}")

# Use curated data with multiple folds for robustness
curated_results = run_holdout_test(curated_data, "CURATED VOCABULARY (v0.8, 500 words)")

# ============================================================
# SECTION 3: HOLDOUT TEST -- GENERATED VOCABULARY
# ============================================================

print(f"\n\n{'=' * 70}")
print("  SECTION 3: HOLDOUT TEST -- GENERATED 100K VOCABULARY")
print(f"{'=' * 70}")

# Use a subset for speed (10k from the 100k)
random.seed(42)
generated_subset = random.sample(generated_data, 10000)
generated_results = run_holdout_test(generated_subset,
    "GENERATED VOCABULARY (v0.12, 10k sample from 100k)")

# ============================================================
# SECTION 4: TRUE OOD TEST
# ============================================================

print(f"\n\n{'=' * 70}")
print("  SECTION 4: TRUE OOD TEST -- WORDS NEVER SEEN BEFORE")
print(f"{'=' * 70}")

# Build profiler from FULL curated vocabulary
full_profiler = CategoryProfiler(curated_data)
ood_results = run_true_ood_test(full_profiler, TRUE_OOD,
    "TRUE OOD (trained on full curated 500, tested on unseen words)")

# ============================================================
# SECTION 5: NOISE FLOOR -- RANDOM STRING BASELINE
# ============================================================

print(f"\n\n{'=' * 70}")
print("  SECTION 5: NOISE FLOOR -- RANDOM STRINGS")
print(f"{'=' * 70}")

# Generate random alphabetic strings (4-8 chars) and see how profiler distributes them
random.seed(123)
random_strings = []
for _ in range(500):
    length = random.randint(3, 10)
    s = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))
    random_strings.append(s)

# Classify random strings using curated profiler
cat_predictions = defaultdict(int)
for s in random_strings:
    pred, _ = full_profiler.classify_weighted(s)
    cat_predictions[pred] += 1

print(f"\n  Distribution of {len(random_strings)} random string classifications:")
print(f"  (Should be roughly uniform if structural features carry no category info)")
print(f"  {'Category':<14s} {'Count':>7s} {'Expected':>9s} {'Ratio':>7s}")
print(f"  {'-'*39}")
expected = len(random_strings) / N_CATS
for cat_idx in range(N_CATS):
    c = cat_predictions[cat_idx]
    ratio = c / expected
    print(f"  {CATEGORIES[cat_idx]:<14s} {c:>7d} {expected:>9.1f} {ratio:>7.2f}x")

# ============================================================
# SECTION 6: GCD DISTRIBUTION ANALYSIS
# ============================================================

print(f"\n\n{'=' * 70}")
print("  SECTION 6: GCD DISTRIBUTION -- WHAT DOES THE RESONANCE LOOK LIKE?")
print(f"{'=' * 70}")

# Take a few true OOD words and show their GCD scores across all categories
sample_ood = TRUE_OOD[:10]
print(f"\n  GCD resonance heatmap (10 sample OOD words x top categories):")
header = f"  {'Word':<14s}"
top_cats = sorted(range(N_CATS),
    key=lambda c: sum(1 for w, ci in sample_ood if ci == c), reverse=True)[:8]
for ci in top_cats:
    header += f" {CATEGORIES[ci][:7]:>7s}"
print(header)
print("  " + "-" * (14 + 8 * 8))

for word, true_cat in sample_ood:
    enc, primes = encode_structural(word)
    row = f"  {word:<14s}"
    for ci in top_cats:
        g = gcd(enc, full_profiler.centroids[ci])
        row += f" {g:>7d}"
    marker = " <-- " + CATEGORIES[true_cat] if true_cat in top_cats else ""
    print(row + marker)

# ============================================================
# SUMMARY
# ============================================================

print(f"\n\n{'=' * 70}")
print("  SUMMARY")
print(f"{'=' * 70}")

print()
print("  The OOD test asks: Can structural primes predict category WITHOUT")
print("  the category prime?")
print()
print("  CURATED VOCABULARY (v0.8, 500 words):")
print("    - Categories have genuine semantic structure")
print("    - Professions tend to end in -er/-or, sports in -ing, etc.")
print("    - Expected: above chance if structural features carry category info")
print()
print("  GENERATED VOCABULARY (v0.12, 100k words):")
print("    - Categories assigned by index, not semantics")
print("    - All structural features are category-agnostic by construction")
print("    - Expected: near chance (~5%) -- the HONEST NULL RESULT")
print()
print("  TRUE OOD (words never in any vocabulary):")
print("    - Tests generalization beyond training data")
print("    - Uses profiler trained on full curated vocabulary")
print()
print("  NOISE FLOOR (random strings):")
print("    - Should distribute roughly uniformly")
print("    - Any skew reveals profiler bias")
print()
print("  INTERPRETATION:")
print("    If curated >> generated: structural features carry genuine category signal")
print("    If curated ~ generated: classification is category-prime-dependent (tautology)")
print("    The gap between them IS the discovery margin.")
print()

print("  Experiment complete. Zero floats used in computation.")
print("=" * 70)
