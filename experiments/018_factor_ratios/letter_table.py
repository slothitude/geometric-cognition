"""
The Monad Alphabet: 12-letter multiplication table.
a=5, b=7, c=11, d=13, e=17, f=19, g=23, h=25, i=29, j=31, k=35, l=1
Values are residues coprime to 6, mod 36. l=1 is the identity.
"""

residues = [5, 7, 11, 13, 17, 19, 23, 25, 29, 31, 35, 1]
labels   = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']

# Verify closure
for i in range(12):
    for j in range(12):
        r = (residues[i] * residues[j]) % 36
        assert r in residues, f"Not closed: {residues[i]}*{residues[j]}={residues[i]*residues[j]}, mod 36={r}"

# Verify user examples
print("User examples:")
print(f"  a*b = {labels[residues.index(35 % 36)]}  (5*7=35)  expected k")
print(f"  b*d = {labels[residues.index(91 % 36)]}  (7*13=91)  expected f")
print()

# ====================================================================
#  THE FULL TABLE
# ====================================================================
print("=" * 64)
print("  THE MONAD ALPHABET: 12-LETTER MULTIPLICATION TABLE")
print("=" * 64)
print()
print("  a=5  b=7  c=11  d=13  e=17  f=19  g=23  h=25  i=29  j=31  k=35  l=1")
print()
print("  (l=1 is the identity: x*l = x for all x)")
print()
print("       a   b   c   d   e   f   g   h   i   j   k   l")
print("   " + "---" * 18)
for i in range(12):
    row = f"  {labels[i]}|"
    for j in range(12):
        r = (residues[i] * residues[j]) % 36
        idx = residues.index(r)
        row += f"  {labels[idx]}"
    print(row)

print()

# ====================================================================
#  RAIL STRUCTURE
# ====================================================================
print("  RAIL STRUCTURE:")
print()
print("  R1 (6k-1): b=5  d=11 f=17 h=23 j=29 l=35")
print("  R2 (6k+1): a=1  c=7  e=13 g=19 i=25 k=31  [wait...]")

# Actually let me show the rail membership correctly
print()
print("  R1 (6k-1): b=5, d=11, f=17, h=23, j=29, l=35")
print("  R2 (6k+1): a=1, c=7, e=13, g=19, i=25, k=31")

# Hmm wait, a=5 not 1. Let me redo:
# a=5: 5 mod 6 = 5 -> R1
# b=7: 7 mod 6 = 1 -> R2
# c=11: 11 mod 6 = 5 -> R1
# d=13: 13 mod 6 = 1 -> R2
# e=17: 17 mod 6 = 5 -> R1
# f=19: 19 mod 6 = 1 -> R2
# g=23: 23 mod 6 = 5 -> R1
# h=25: 25 mod 6 = 1 -> R2
# i=29: 29 mod 6 = 5 -> R1
# j=31: 31 mod 6 = 1 -> R2
# k=35: 35 mod 6 = 5 -> R1
# l=1:  1 mod 6 = 1 -> R2

print()
print("  R1 (6k-1): a=5, c=11, e=17, g=23, i=29, k=35")
print("  R2 (6k+1): b=7, d=13, f=19, h=25, j=31, l=1")
print()

# ====================================================================
#  INTERFERENCE RULES
# ====================================================================
print("  INTERFERENCE RULES (composing any two positions):")
print()
print("  R1 x R1 -> R2: destructive  (a*c=g, c*e=i, a*e=k)")
print("  R2 x R2 -> R2: constructive (b*d=f, d*f=h, b*f=j)")
print("  R1 x R2 -> R1: heterodyne   (a*b=k, c*d=j, e*f=l)")
print()

# Verify interference examples
examples = [
    ("a*c", 5, 11, "R1", "R1"),   # -> R2
    ("c*e", 11, 17, "R1", "R1"),   # -> R2
    ("a*e", 5, 17, "R1", "R1"),    # -> R2
    ("b*d", 7, 13, "R2", "R2"),    # -> R2
    ("d*f", 13, 19, "R2", "R2"),   # -> R2
    ("b*f", 7, 19, "R2", "R2"),    # -> R2
    ("a*b", 5, 7, "R1", "R2"),     # -> R1
    ("c*d", 11, 13, "R1", "R2"),   # -> R1
    ("e*f", 17, 19, "R1", "R2"),   # -> R1
]

print(f"  {'expr':>5} {'=':>2} {'product':>8} {'mod 36':>7} {'result':>7} {'rail':>5}")
for name, r1, r2, rail1, rail2 in examples:
    prod = r1 * r2
    r = prod % 36
    idx = residues.index(r)
    result_label = labels[idx]
    result_rail = "R1" if residues[idx] % 6 == 5 else "R2"

    if rail1 == "R1" and rail2 == "R1":
        expected_rail = "R2"
    elif rail1 == "R2" and rail2 == "R2":
        expected_rail = "R2"
    else:
        expected_rail = "R1"

    check = "OK" if result_rail == expected_rail else "ERR"
    print(f"  {name:>5}  = {prod:>8} {r:>7} = {result_label:>5}({r})  {result_rail:>5} {check}")

print()

# ====================================================================
#  NOTABLE PATTERNS
# ====================================================================
print("  NOTABLE PATTERNS:")
print()
print("  Identity:  x*l = x  and  l*x = x  for all x  (l=1)")
print("  Self-inverse: x*x gives:")

for i in range(12):
    r = (residues[i] * residues[i]) % 36
    idx = residues.index(r)
    print(f"    {labels[i]}*{labels[i]} = {labels[idx]}  ({residues[i]}^2 = {residues[i]**2}, mod 36 = {r})")

print()

# Commutativity check
print("  Commutativity: x*y = y*x?")
noncomm = 0
for i in range(12):
    for j in range(12):
        r1 = (residues[i] * residues[j]) % 36
        r2 = (residues[j] * residues[i]) % 36
        if r1 != r2:
            noncomm += 1
print(f"  Non-commutative pairs: {noncomm} (multiplication IS commutative)")
print()

# Rows as "spells"
print("  EACH ROW IS A PERMUTATION (every letter appears exactly once):")
for i in range(12):
    row_letters = []
    for j in range(12):
        r = (residues[i] * residues[j]) % 36
        idx = residues.index(r)
        row_letters.append(labels[idx])
    unique = len(set(row_letters))
    print(f"    {labels[i]}: {''.join(row_letters)}  ({unique} unique)")

print()

# ====================================================================
#  THE Z2 RAIL RULE
# ====================================================================
print("  Z2 RAIL RULE:")
print()
print("  R1 x R1 = R2: a,c,e,g,i,k combine to give R2 result")
print("  R2 x R2 = R2: b,d,f,h,j,l combine to give R2 result")
print("  R1 x R2 = R1: mixed gives R1 result")
print()

# Verify Z2
z2_ok = True
for i in range(12):
    for j in range(12):
        ri = "R1" if residues[i] % 6 == 5 else "R2"
        rj = "R1" if residues[j] % 6 == 5 else "R2"
        prod = (residues[i] * residues[j]) % 36
        idx = residues.index(prod)
        rk = "R1" if residues[idx] % 6 == 5 else "R2"

        if ri == "R1" and rj == "R1":
            expected = "R2"
        elif ri == "R2" and rj == "R2":
            expected = "R2"
        else:
            expected = "R1"

        if rk != expected:
            z2_ok = False
            print(f"  Z2 FAIL: {labels[i]}({ri}) * {labels[j]}({rj}) = {labels[idx]}({rk}), expected {expected}")

print(f"  Z2 rule verified for ALL 144 entries: {z2_ok}")
print()

# ====================================================================
#  SUB-POSITION RULES
# ====================================================================
print("  SUB-POSITION INTERFERENCE (sp values mod 6):")
print()
print("  R1 x R1 -> R2: sp = (-sp1 - sp2) mod 6  (destructive)")
print("  R2 x R2 -> R2: sp = (sp1 + sp2) mod 6   (constructive)")
print("  R1 x R2 -> R1: sp = (sp1 - sp2) mod 6   (heterodyne)")
print()

def get_sp(n):
    """Sub-position: sp = k mod 6 where n = 6k±1."""
    if n % 6 == 5:  # R1: n = 6k-1 -> k = (n+1)/6
        return ((n + 1) // 6) % 6
    else:  # R2: n = 6k+1 -> k = (n-1)/6
        return ((n - 1) // 6) % 6

# Verify sub-position rules
sp_ok = True
for i in range(12):
    for j in range(12):
        n1, n2 = residues[i], residues[j]
        sp1, sp2 = get_sp(n1), get_sp(n2)
        r1 = "R1" if n1 % 6 == 5 else "R2"
        r2 = "R1" if n2 % 6 == 5 else "R2"

        prod = (n1 * n2) % 36
        idx = residues.index(prod)
        actual_sp = get_sp(residues[idx])

        if r1 == "R1" and r2 == "R1":
            pred_sp = (-sp1 - sp2) % 6
        elif r1 == "R2" and r2 == "R2":
            pred_sp = (sp1 + sp2) % 6
        else:
            if r1 == "R1":
                pred_sp = (sp1 - sp2) % 6
            else:
                pred_sp = (sp2 - sp1) % 6

        if actual_sp != pred_sp:
            sp_ok = False
            print(f"  SP FAIL: {labels[i]}*{labels[j]} ({n1}*{n2})")
            print(f"    rails: {r1}x{r2}, sp1={sp1}, sp2={sp2}")
            print(f"    predicted sp={pred_sp}, actual sp={actual_sp} (residue {residues[idx]})")

print(f"  Sub-position rules verified for ALL 144 entries: {sp_ok}")
print()

# ====================================================================
#  THE COMPLETE ANNOTATED TABLE
# ====================================================================
print("=" * 64)
print("  COMPLETE ANNOTATED TABLE")
print("=" * 64)
print()
print("  Position:  a    b    c    d    e    f    g    h    i    j    k    l")
print("  Residue:   5    7   11   13   17   19   23   25   29   31   35    1")
print("  Rail:     R1   R2   R1   R2   R1   R2   R1   R2   R1   R2   R1   R2")
print("  Sub-pos:   1    1    2    2    3    3    4    4    5    5    0    0")
print()
print("       a   b   c   d   e   f   g   h   i   j   k   l")
print("   " + "---" * 18)
for i in range(12):
    row = f"  {labels[i]}|"
    for j in range(12):
        r = (residues[i] * residues[j]) % 36
        idx = residues.index(r)
        row += f"  {labels[idx]}"
    print(row)

print()
print("Done.")
