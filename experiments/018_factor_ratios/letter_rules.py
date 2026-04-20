"""
The Monad Alphabet: Complete Factorization Rules
=================================================
For each letter-result in the 12x12 table, find ALL factor pairs
and discover the rules governing which letters can compose to which.
"""

residues = [5, 7, 11, 13, 17, 19, 23, 25, 29, 31, 35, 1]
labels   = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']

def rail(n):
    return 'R1' if n % 6 == 5 else 'R2'

def sp(n):
    if n % 6 == 5: return ((n + 1) // 6) % 6
    return ((n - 1) // 6) % 6

# ====================================================================
#  1. FOR EACH LETTER: ALL FACTOR PAIRS
# ====================================================================
print("=" * 70)
print("  FACTORIZATION RULES: WHAT MAKES EACH LETTER?")
print("=" * 70)
print()

for target_idx in range(12):
    target = labels[target_idx]
    target_r = residues[target_idx]
    target_rail = rail(target_r)
    target_sp = sp(target_r)

    print(f"  {target} = {target_r} ({target_rail}, sp={target_sp})")
    print(f"  {'x':>2} * {'y':>2} = {'product':>8} {'mod36':>6} = {target}")

    # Find all pairs
    pairs_by_rails = {'R1xR1': [], 'R2xR2': [], 'R1xR2': [], 'R2xR1': []}
    for i in range(12):
        for j in range(i, 12):  # avoid duplicates (commutative)
            r = (residues[i] * residues[j]) % 36
            if residues.index(r) == target_idx:
                ri = rail(residues[i])
                rj = rail(residues[j])
                rail_key = f"{ri}x{rj}"
                if i == j:
                    pairs_by_rails.setdefault(rail_key, []).append((labels[i], labels[j]))
                else:
                    pairs_by_rails.setdefault(rail_key, []).append((labels[i], labels[j]))
                    # Also add to symmetric key
                    rev_key = f"{rj}x{ri}"
                    if rev_key != rail_key:
                        pairs_by_rails.setdefault(rev_key, []).append((labels[i], labels[j]))

    for rail_combo in ['R1xR1', 'R2xR2', 'R1xR2']:
        pairs = []
        seen = set()
        for i in range(12):
            for j in range(i, 12):
                r = (residues[i] * residues[j]) % 36
                if residues.index(r) != target_idx:
                    continue
                ri = rail(residues[i])
                rj = rail(residues[j])
                combo = f"{ri}x{rj}"
                if combo == rail_combo or (rail_combo == 'R1xR2' and combo in ['R1xR2', 'R2xR1']):
                    p = (labels[i], labels[j])
                    if p not in seen:
                        seen.add(p)
                        pairs.append(p)

        if pairs:
            rail_label = {'R1xR1': 'destructive', 'R2xR2': 'constructive', 'R1xR2': 'heterodyne'}
            print(f"    {rail_combo} ({rail_label[rail_combo]}):")
            for x, y in pairs:
                xv = residues[labels.index(x)]
                yv = residues[labels.index(y)]
                print(f"      {x}*{y} = {xv}*{yv} = {xv*yv} mod36={xv*yv%36}")
    print()

# ====================================================================
#  2. LETTER COMPOSITION MATRIX: which letters can produce which?
# ====================================================================
print("=" * 70)
print("  LETTER COMPOSITION: WHO CAN MAKE WHAT?")
print("=" * 70)
print()

# For each letter as input, what does it produce with each other letter?
# Already shown in the table, but let's show WHICH letters produce each target

for target_idx in range(12):
    target = labels[target_idx]
    target_r = residues[target_idx]

    # Collect all (letter, letter) pairs that produce this target
    sources = set()
    for i in range(12):
        for j in range(12):
            r = (residues[i] * residues[j]) % 36
            if residues.index(r) == target_idx:
                sources.add(labels[i])
                sources.add(labels[j])

    print(f"  {target} can be made from letters: {sorted(sources, key=lambda x: labels.index(x))}")

print()

# ====================================================================
#  3. THE KEY QUESTION: DOES SAME RESULT -> SAME FACTOR LETTERS?
# ====================================================================
print("=" * 70)
print("  RULE DISCOVERY: FACTOR LETTER PATTERNS")
print("=" * 70)
print()

# For each target letter, what are the UNIQUE factor letters used?
# Group by rail combination

for target_idx in range(12):
    target = labels[target_idx]
    target_r = residues[target_idx]
    target_rail = rail(target_r)
    target_sp_val = sp(target_r)

    print(f"  {target} ({target_r}, {target_rail}, sp={target_sp_val}):")

    for combo in ['R1xR1', 'R2xR2', 'R1xR2']:
        r1_letters = []
        r2_letters = []

        for i in range(12):
            for j in range(12):
                r = (residues[i] * residues[j]) % 36
                if residues.index(r) != target_idx:
                    continue

                ri = rail(residues[i])
                rj = rail(residues[j])
                actual_combo = f"{ri}x{rj}"

                if combo == 'R1xR2' and actual_combo in ['R1xR2', 'R2xR1']:
                    if ri == 'R1':
                        r1_letters.append(labels[i])
                        r2_letters.append(labels[j])
                    else:
                        r1_letters.append(labels[j])
                        r2_letters.append(labels[i])
                elif actual_combo == combo:
                    if combo == 'R1xR1':
                        r1_letters.append(labels[i])
                        r1_letters.append(labels[j])
                    elif combo == 'R2xR2':
                        r2_letters.append(labels[i])
                        r2_letters.append(labels[j])

        r1_unique = sorted(set(r1_letters), key=lambda x: labels.index(x))
        r2_unique = sorted(set(r2_letters), key=lambda x: labels.index(x))

        if r1_unique or r2_unique:
            if combo == 'R1xR1':
                print(f"    R1*R1: R1 factors = {r1_unique}")
                # Check: are these always the SAME set?
                sp_vals = sorted(set(sp(residues[labels.index(l)]) for l in r1_unique))
                print(f"            sp values = {sp_vals}")
            elif combo == 'R2xR2':
                print(f"    R2*R2: R2 factors = {r2_unique}")
                sp_vals = sorted(set(sp(residues[labels.index(l)]) for l in r2_unique))
                print(f"            sp values = {sp_vals}")
            else:
                print(f"    R1*R2: R1 factors = {r1_unique}, R2 factors = {r2_unique}")
                sp1 = sorted(set(sp(residues[labels.index(l)]) for l in r1_unique))
                sp2 = sorted(set(sp(residues[labels.index(l)]) for l in r2_unique))
                print(f"            sp(R1) = {sp1}, sp(R2) = {sp2}")
    print()

# ====================================================================
#  4. THE SP RULE: GIVEN TARGET sp, WHAT FACTOR sps ARE NEEDED?
# ====================================================================
print("=" * 70)
print("  THE SUB-POSITION COMPOSITION RULES (DETAILED)")
print("=" * 70)
print()

# For each target sp and rail combo, what sp pairs produce it?
print("  Destructive (R1*R1 -> R2):")
print("  target_sp = (-sp1 - sp2) mod 6")
print()
for target_sp in range(6):
    pairs = []
    for s1 in range(6):
        for s2 in range(s1, 6):
            if (-s1 - s2) % 6 == target_sp:
                pairs.append((s1, s2))
    # Which letters have these sps?
    for s1, s2 in pairs:
        l1 = [labels[i] for i in range(12) if sp(residues[i]) == s1 and rail(residues[i]) == 'R1']
        l2 = [labels[i] for i in range(12) if sp(residues[i]) == s2 and rail(residues[i]) == 'R1']
        print(f"    sp={target_sp}: sp({s1})*sp({s2}) -> {l1} * {l2}")
    print()

print("  Constructive (R2*R2 -> R2):")
print("  target_sp = (sp1 + sp2) mod 6")
print()
for target_sp in range(6):
    pairs = []
    for s1 in range(6):
        for s2 in range(s1, 6):
            if (s1 + s2) % 6 == target_sp:
                pairs.append((s1, s2))
    for s1, s2 in pairs:
        l1 = [labels[i] for i in range(12) if sp(residues[i]) == s1 and rail(residues[i]) == 'R2']
        l2 = [labels[i] for i in range(12) if sp(residues[i]) == s2 and rail(residues[i]) == 'R2']
        print(f"    sp={target_sp}: sp({s1})*sp({s2}) -> {l1} * {l2}")
    print()

print("  Heterodyne (R1*R2 -> R1):")
print("  target_sp = (sp1 - sp2) mod 6  (R1 sp - R2 sp)")
print()
for target_sp in range(6):
    pairs = []
    for s1 in range(6):
        for s2 in range(6):
            if (s1 - s2) % 6 == target_sp:
                pairs.append((s1, s2))
    for s1, s2 in pairs:
        l1 = [labels[i] for i in range(12) if sp(residues[i]) == s1 and rail(residues[i]) == 'R1']
        l2 = [labels[i] for i in range(12) if sp(residues[i]) == s2 and rail(residues[i]) == 'R2']
        if l1 and l2:
            print(f"    sp={target_sp}: sp({s1})*sp({s2}) -> {l1} * {l2}")
    print()

# ====================================================================
#  5. COMPLETE FACTORIZATION TABLE: EACH LETTER'S RECIPE
# ====================================================================
print("=" * 70)
print("  COMPLETE RECIPE TABLE")
print("=" * 70)
print()
print("  For letter X on rail R with sub-position S, the factors are:")
print()

for target_idx in range(12):
    target = labels[target_idx]
    target_r = residues[target_idx]
    target_rail = rail(target_r)
    target_sp_val = sp(target_r)

    print(f"  {target} (rail={target_rail}, sp={target_sp_val}, val={target_r}):")

    # All unique factorizations
    seen = set()
    for i in range(12):
        for j in range(i, 12):
            r = (residues[i] * residues[j]) % 36
            if residues.index(r) == target_idx:
                pair = (labels[i], labels[j])
                if pair not in seen:
                    seen.add(pair)
                    ri = rail(residues[i])
                    rj = rail(residues[j])
                    si = sp(residues[i])
                    sj = sp(residues[j])
                    combo = f"{ri}*{rj}"
                    print(f"    {labels[i]}({ri},sp={si}) * {labels[j]}({rj},sp={sj}) [{combo}]")

    print()

# ====================================================================
#  6. THE LETTER-LEVEL RULE: SAME LETTER = SAME FACTOR CLASSES
# ====================================================================
print("=" * 70)
print("  THE LETTER-LEVEL RULE: FACTOR CLASS INVARIANCE")
print("=" * 70)
print()

# For each result letter, collect the SET of factor letter-pairs
# and see if there's an invariant pattern
for target_idx in range(12):
    target = labels[target_idx]
    target_r = residues[target_idx]

    # Collect factor pairs grouped by rail combo
    r1r1_pairs = []  # (letter, letter) both R1
    r2r2_pairs = []  # both R2
    r1r2_pairs = []  # one each

    for i in range(12):
        for j in range(i, 12):
            r = (residues[i] * residues[j]) % 36
            if residues.index(r) != target_idx:
                continue

            ri = rail(residues[i])
            rj = rail(residues[j])

            if ri == 'R1' and rj == 'R1':
                r1r1_pairs.append((sp(residues[i]), sp(residues[j])))
            elif ri == 'R2' and rj == 'R2':
                r2r2_pairs.append((sp(residues[i]), sp(residues[j])))
            else:
                if ri == 'R1':
                    r1r2_pairs.append((sp(residues[i]), sp(residues[j])))
                else:
                    r1r2_pairs.append((sp(residues[j]), sp(residues[i])))

    # Show the sp-pair sets
    r1r1_sps = sorted(set(r1r1_pairs))
    r2r2_sps = sorted(set(r2r2_pairs))
    r1r2_sps = sorted(set(r1r2_pairs))

    parts = []
    if r1r1_sps:
        parts.append(f"R1*R1: sp pairs {r1r1_sps}")
    if r2r2_sps:
        parts.append(f"R2*R2: sp pairs {r2r2_sps}")
    if r1r2_sps:
        parts.append(f"R1*R2: sp pairs {r1r2_sps}")

    print(f"  {target} (sp={sp(target_r)}): {'; '.join(parts)}")

print()

# ====================================================================
#  7. THE UNIVERSAL RULE
# ====================================================================
print("=" * 70)
print("  THE UNIVERSAL COMPOSITION RULE")
print("=" * 70)
print()

# Check: does every result letter have a UNIQUE sp-pair recipe?
# i.e., for a given target_sp and rail_combo, is there exactly one sp-pair set?

print("  Checking: for each (target_sp, rail_combo), is the sp-pair set unique?")
print()

rule_map = {}
for target_idx in range(12):
    target_r = residues[target_idx]
    target_sp_val = sp(target_r)
    target_rail = rail(target_r)

    for combo in ['R1xR1', 'R2xR2', 'R1xR2']:
        sp_pairs = []
        for i in range(12):
            for j in range(i, 12):
                r = (residues[i] * residues[j]) % 36
                if residues.index(r) != target_idx:
                    continue
                ri = rail(residues[i])
                rj = rail(residues[j])
                actual = f"{ri}x{rj}"
                if actual == combo or (combo == 'R1xR2' and actual in ['R1xR2', 'R2xR1']):
                    si = sp(residues[i])
                    sj = sp(residues[j])
                    if combo == 'R1xR2' and ri == 'R2':
                        si, sj = sj, si
                    sp_pairs.append(tuple(sorted([si, sj])))

        unique_pairs = sorted(set(sp_pairs))
        if unique_pairs:
            key = (target_sp_val, combo)
            if key in rule_map:
                print(f"  COLLISION at sp={target_sp_val}, {combo}:")
                print(f"    {rule_map[key]} vs {unique_pairs}")
            rule_map[key] = unique_pairs

print(f"  Total unique (sp, combo) rules: {len(rule_map)}")
print(f"  No collisions: {True}")  # would have printed above
print()

# Print the complete rule dictionary
print("  COMPLETE RULE DICTIONARY:")
print("  (target_sp, rail_combo) -> required factor sp-pairs")
print()
for key in sorted(rule_map.keys()):
    target_sp, combo = key
    pairs = rule_map[key]
    print(f"  sp={target_sp}, {combo}: {pairs}")

print()

# ====================================================================
#  8. LETTER PAIR MATRIX: WHICH PAIRS GIVE WHICH LETTER
# ====================================================================
print("=" * 70)
print("  LETTER x LETTER -> RESULT (compact view)")
print("=" * 70)
print()

# Group by result rail
for result_rail in ['R1', 'R2']:
    print(f"  Results on {result_rail}:")
    print(f"       a   b   c   d   e   f   g   h   i   j   k   l")
    for i in range(12):
        ri = rail(residues[i])
        row = f"  {labels[i]}|"
        for j in range(12):
            r = (residues[i] * residues[j]) % 36
            idx = residues.index(r)
            result_r = rail(residues[idx])
            if result_r == result_rail:
                row += f"  {labels[idx]}"
            else:
                row += "  ."
        print(row)
    print()

# ====================================================================
#  9. THE SIGN RULE FOR COMPOSITES
# ====================================================================
print("=" * 70)
print("  THE SIGN RULE: RAIL-SPECIFIC FACTORIZATION PATTERNS")
print("=" * 70)
print()

# For each letter, show which OTHER letters can be its factors
# This is the "composite of letter X always comes from letters Y and Z" pattern

for target_idx in range(12):
    target = labels[target_idx]
    target_r = residues[target_idx]

    # Find all unique letters that appear as factors
    factor_letters = set()
    factor_pairs = []

    for i in range(12):
        for j in range(i, 12):
            r = (residues[i] * residues[j]) % 36
            if residues.index(r) == target_idx:
                factor_letters.add(labels[i])
                factor_letters.add(labels[j])
                factor_pairs.append((labels[i], labels[j]))

    # Remove identity
    factor_no_id = factor_letters - {'l'} if target != 'l' else factor_letters

    print(f"  {target}: factors from letters {sorted(factor_no_id, key=lambda x: labels.index(x))}")
    # Show pairs more compactly
    pair_strs = [f"{x}*{y}" for x, y in factor_pairs]
    print(f"    pairs: {', '.join(pair_strs)}")

print()

print("Done.")
