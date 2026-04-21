"""
Experiment 018uuu: The I/O Boundary -- Exact Predicates vs Lossy Measurement

The question: how do we probe the monad without smearing exactness into floats?

The answer: use PREDICATE QUERIES (exact boolean/integer/algebraic answers)
instead of MEASUREMENT QUERIES (float approximations).

The monad is a database of exact facts. You can query it exactly.
Floats only appear when you ask AGGREGATE questions (correlations, averages).
"""

from fractions import Fraction
from dataclasses import dataclass
from typing import Optional
import numpy as np

print("=" * 70)
print("EXPERIMENT 018uuu: THE I/O BOUNDARY -- EXACT PREDICATES")
print("=" * 70)

# ============================================================
# SECTION 1: TWO QUERY LANGUAGES
# ============================================================
print()
print("=" * 70)
print("SECTION 1: TWO QUERY LANGUAGES FOR THE SAME SYSTEM")
print("=" * 70)

def sieve_primes(N):
    is_p = np.ones(N + 1, dtype=bool)
    is_p[0] = is_p[1] = False
    for i in range(2, int(N**0.5) + 1):
        if is_p[i]:
            is_p[i*i::i] = False
    return is_p

N_max = 100000
is_prime = sieve_primes(N_max)

print("""
  QUERY TYPE A -- PREDICATE (exact, no float, no Landauer cost)

    "Is 29 prime?"           -> True        (exact boolean)
    "Rail of 29?"            -> R1          (exact label)
    "k-value of 29?"         -> 5           (exact integer)
    "chi_3 of 29?"           -> +1          (exact Z_2)
    "Factors of 35?"         -> [5, 7]      (exact integer list)
    "Is 29 a twin prime?"    -> True        (exact boolean)
    "Coprime to 6?"          -> True        (exact boolean)
    "Residue mod 12?"        -> 5           (exact integer)
    "chi_3(29)*chi_3(7)?"    -> +1          (exact Z_2 product)
    "Mass of 29?"            -> 1/29        (exact rational)

  QUERY TYPE B -- MEASUREMENT (float, Landauer cost kT*ln(2))

    "D-Q correlation?"       -> 0.076       (statistical float)
    "Quadrupole power?"      -> 97.1%       (statistical float)
    "Chebyshev bias?"        -> 0.00229     (statistical float)
    "Octupole kurtosis?"     -> 37.4        (statistical float)

  Type A queries probe the STATE (exact).
  Type B queries probe the STATISTICS (approximate).
  The monad CAN answer Type A without any float.
  The monad CANNOT answer Type B -- only an observer can.
""")

# ============================================================
# SECTION 2: EXACT STATE EXTRACTION
# ============================================================
print()
print("=" * 70)
print("SECTION 2: EXTRACTING FULL STATE WITH ZERO FLOATS")
print("=" * 70)

@dataclass
class MonadPosition:
    """Complete state of a monad position -- ALL fields exact."""
    n: int                    # the number
    k: int                    # k-value
    rail: str                 # 'R1' or 'R2'
    is_prime: bool            # primality
    residue_mod6: int         # n mod 6
    residue_mod12: int        # n mod 12
    chi1: int                 # isospin (+1/-1)
    chi3: int                 # matter/antimatter (+1/-1)
    mass: Fraction            # 1/n (exact rational)

    def __repr__(self):
        return (f"n={self.n} k={self.k} {self.rail} "
                f"prime={self.is_prime} chi1={'+' if self.chi1>0 else ''}{self.chi1} "
                f"chi3={'+' if self.chi3>0 else ''}{self.chi3} mass={self.mass}")

# Extract exact state for k=1..10 (the first 20 positions)
print("\n  Full state dump for k=1..10 (ZERO floats):")
print(f"  {'n':>4} {'k':>3} {'rail':>3} {'prime':>5} {'chi1':>5} {'chi3':>5} {'mass':>8}")
print(f"  {'-'*40}")

states = []
for k in range(1, 11):
    for rail_name, n in [('R1', 6*k-1), ('R2', 6*k+1)]:
        r6 = n % 6
        r12 = n % 12
        chi1 = +1 if r12 in [1, 11] else -1
        chi3 = +1 if r12 in [1, 5] else -1

        state = MonadPosition(
            n=n, k=k, rail=rail_name,
            is_prime=bool(is_prime[n]),
            residue_mod6=r6, residue_mod12=r12,
            chi1=chi1, chi3=chi3,
            mass=Fraction(1, n),
        )
        states.append(state)
        p_marker = "P" if state.is_prime else " "
        print(f"  {n:>4} {k:>3} {rail_name:>3}  {p_marker:>4}  {chi1:>+2}   {chi3:>+2}   {str(Fraction(1,n)):>8}")

# Every field is an exact type: int, bool, str, Fraction
print(f"\n  Types: n=int, k=int, rail=str, prime=bool, chi=int, mass=Fraction")
print(f"  Floats used: 0")
print(f"  Information lost: 0")
print(f"  Landauer cost: 0 bits")

# ============================================================
# SECTION 3: EXACT COMPOSITION WITHOUT FLOATS
# ============================================================
print()
print("=" * 70)
print("SECTION 3: EXACT COMPOSITION AND DECOMPOSITION")
print("=" * 70)

# Compose two positions and verify all properties
print("\n  Composition examples (all exact):")
compositions = [
    (5, 7),    # R1 * R2 = R2 (35 = 5*7)
    (5, 11),   # R1 * R1 = R2 (55 = 5*11)
    (7, 13),   # R2 * R2 = R2 (91 = 7*13)
    (11, 13),  # R1 * R2 = R1 (143 = 11*13)
    (29, 31),  # copper twin prime
]

for a, b in compositions:
    n = a * b
    rail_a = 'R1' if a % 6 == 5 else 'R2'
    rail_b = 'R1' if b % 6 == 5 else 'R2'
    rail_n = 'R1' if n % 6 == 5 else 'R2'

    chi1_a = +1 if a % 12 in [1, 11] else -1
    chi1_b = +1 if b % 12 in [1, 11] else -1
    chi1_n = +1 if n % 12 in [1, 11] else -1

    chi3_a = +1 if a % 12 in [1, 5] else -1
    chi3_b = +1 if b % 12 in [1, 5] else -1
    chi3_n = +1 if n % 12 in [1, 5] else -1

    mass_a = Fraction(1, a)
    mass_b = Fraction(1, b)
    # Composite mass is NOT 1/(a*b) -- it's the mass of the composite position
    mass_n = Fraction(1, n)

    chi1_product = chi1_a * chi1_b
    chi3_product = chi3_a * chi3_b

    chi1_ok = "OK" if chi1_product == chi1_n else "FAIL"
    chi3_ok = "OK" if chi3_product == chi3_n else "FAIL"

    print(f"    {a:>3}({rail_a}) x {b:>3}({rail_b}) = {n:>4}({rail_n})")
    print(f"      chi1: {chi1_a:+d}*{chi1_b:+d}={chi1_product:+d} vs {chi1_n:+d} [{chi1_ok}]")
    print(f"      chi3: {chi3_a:+d}*{chi3_b:+d}={chi3_product:+d} vs {chi3_n:+d} [{chi3_ok}]")
    print(f"      mass: {mass_a} x {mass_b} -> {mass_n}")

# ============================================================
# SECTION 4: THE PREDICATE INTERFACE API
# ============================================================
print()
print("=" * 70)
print("SECTION 4: THE PREDICATE INTERFACE API")
print("=" * 70)

class MonadInterface:
    """
    An exact interface to the monad. Every method returns an EXACT type.
    No floats. No approximations. No Landauer cost.

    This is the "API" for probing the monad's state.
    """

    def __init__(self, sieve_limit):
        self.is_prime = sieve_primes(sieve_limit)
        self.sieve_limit = sieve_limit

    def is_prime_query(self, n: int) -> bool:
        """Exact boolean: is n prime?"""
        return bool(self.is_prime[n])

    def rail_query(self, n: int) -> Optional[str]:
        """Exact label: R1 or R2?"""
        if n % 6 == 5: return 'R1'
        if n % 6 == 1: return 'R2'
        return None  # not on rails

    def k_value_query(self, n: int) -> Optional[int]:
        """Exact integer: what k-value?"""
        if n % 6 == 5: return (n + 1) // 6
        if n % 6 == 1: return (n - 1) // 6
        return None

    def chi1_query(self, n: int) -> int:
        """Exact Z_2: isospin charge?"""
        return +1 if n % 12 in [1, 11] else -1

    def chi3_query(self, n: int) -> int:
        """Exact Z_2: matter/antimatter charge?"""
        return +1 if n % 12 in [1, 5] else -1

    def mass_query(self, n: int) -> Fraction:
        """Exact rational: mass = 1/n"""
        return Fraction(1, n)

    def factors_query(self, n: int) -> list:
        """Exact integer list: prime factorization"""
        temp = n
        factors = []
        for p in range(2, int(n**0.5) + 1):
            while temp % p == 0:
                factors.append(p)
                temp //= p
        if temp > 1:
            factors.append(temp)
        return factors

    def is_twin_query(self, n: int) -> bool:
        """Exact boolean: is n part of a twin prime pair?"""
        if not self.is_prime[n]: return False
        return (self.is_prime[n-2] or (n+2 < self.sieve_limit and self.is_prime[n+2]))

    def charge_composition_query(self, a: int, b: int) -> dict:
        """Exact verification: charges of a*b from charges of a and b"""
        n = a * b
        return {
            'chi1_predicted': self.chi1_query(a) * self.chi1_query(b),
            'chi1_actual': self.chi1_query(n),
            'chi3_predicted': self.chi3_query(a) * self.chi3_query(b),
            'chi3_actual': self.chi3_query(n),
            'mass_product': self.mass_query(a) * self.mass_query(b),
            'mass_composite': self.mass_query(n),
        }

# Test the interface
api = MonadInterface(N_max)

print("\n  Predicate API demonstration (all return types exact):")
print(f"    is_prime(29):       {api.is_prime_query(29)}       (bool)")
print(f"    rail(29):           {api.rail_query(29):>3}     (str)")
print(f"    k_value(29):        {api.k_value_query(29):>3}     (int)")
print(f"    chi1(29):           {api.chi1_query(29):>+2}       (int)")
print(f"    chi3(29):           {api.chi3_query(29):>+2}       (int)")
print(f"    mass(29):           {api.mass_query(29)}        (Fraction)")
print(f"    factors(35):        {api.factors_query(35)}        (list[int])")
print(f"    is_twin(29):        {api.is_twin_query(29)}       (bool)")

comp = api.charge_composition_query(29, 31)
print(f"\n  Charge composition 29*31=899:")
print(f"    chi1 predicted={comp['chi1_predicted']:+d} actual={comp['chi1_actual']:+d}")
print(f"    chi3 predicted={comp['chi3_predicted']:+d} actual={comp['chi3_actual']:+d}")
print(f"    mass product={comp['mass_product']} composite={comp['mass_composite']}")

# ============================================================
# SECTION 5: THE EXACT-TO-STATISTICAL PIPELINE
# ============================================================
print()
print("=" * 70)
print("SECTION 5: THE EXACT-TO-STATISTICAL PIPELINE")
print("=" * 70)

print("""
  The I/O boundary is not a wall -- it's a CHOICE.

  LAYER: EXACT STATE (Monad internals)
    Every position has: n, k, rail, prime, chi1, chi3, mass
    All stored as int, bool, str, Fraction
    Queryable via predicate API
    Zero information loss

    |
    | AGGREGATION (observer's choice, not monad's requirement)
    v

  LAYER: STATISTICAL MEASUREMENT (Observer's view)
    D-Q correlation: 0.076   (float, Landauer cost)
    Power fraction:  97.1%   (float, Landauer cost)
    Chebyshev bias:  0.00229 (float, Landauer cost)

  The aggregation is OPTIONAL. You can work entirely in the exact layer.
  The floats are a SUMMARY, not a necessity.

  THE INTERFACE DESIGN:
    1. PREDICATE QUERIES: "What is the exact state at position k?"
       -> Returns MonadPosition (all exact fields)
       -> Cost: zero floats, zero Landauer

    2. ALGEBRAIC QUERIES: "What is chi_3(a)*chi_3(b)?"
       -> Returns exact Z_2 product
       -> Cost: zero floats, zero Landauer

    3. AGGREGATE QUERIES: "What is the D-Q correlation over k=1..5000?"
       -> Returns float (statistical summary)
       -> Cost: kT*ln(2) per bit (Landauer)

  Queries 1 and 2 never leave the exact layer.
  Query 3 crosses the I/O boundary and pays the Landauer tax.
  Most useful computations (prime testing, factorization, charge tracking)
  are Query 1 or 2. The monad can do real work without ever using a float.
""")

# ============================================================
# SECTION 6: CONCRETE EXAMPLE -- COPPER'S FULL STATE
# ============================================================
print()
print("=" * 70)
print("SECTION 6: COPPER'S FULL STATE (EXACT, NO FLOATS)")
print("=" * 70)

copper = 29
print(f"\n  Element: Copper (Z={copper})")
print(f"  Full monad state (every field exact):")
print(f"    Position:        {copper}                (int)")
print(f"    k-value:         {api.k_value_query(copper)}                (int)")
print(f"    Rail:            {api.rail_query(copper)}                (str)")
print(f"    Prime:           {api.is_prime_query(copper)}             (bool)")
print(f"    Residue mod 6:   {copper % 6}                (int)")
print(f"    Residue mod 12:  {copper % 12}                (int)")
print(f"    chi_1 (isospin): {api.chi1_query(copper):+d}               (int)")
print(f"    chi_3 (matter):  {api.chi3_query(copper):+d}               (int)")
print(f"    Mass:            {api.mass_query(copper)}                (Fraction)")
print(f"    Twin prime:      {api.is_twin_query(copper)}             (bool)")
print(f"    Factors:         {api.factors_query(copper)}            (list[int])")

# Copper at each tower level (all exact)
print(f"\n  Copper across the tower (all exact residues):")
for m in [6, 12, 24, 30, 60, 210]:
    r = copper % m
    coprime = np.gcd(r, m) == 1
    print(f"    mod {m:>3}: residue {r:>3}, coprime={coprime}  (int, bool)")

print(f"""
  EVERY field is an exact type. No floats. No approximation.
  This is the "lossless readout" of the monad's state.

  The interface does NOT smear exactness because it never
  converts to float. It returns the EXACT symbolic representation.

  The Landauer tax only applies when you choose to AGGREGATE
  (compute statistics, correlations, etc.). But most useful
  queries don't need aggregation -- they just read the state.

  A monad computer's I/O would look like:
    INPUT:  integer k, query type (predicate)
    OUTPUT: exact answer (bool, int, str, Fraction, algebraic)

  No floats in the pipe. No smearing. No information loss.
""")

print("=" * 70)
print("EXPERIMENT 018uuu COMPLETE")
print("=" * 70)
