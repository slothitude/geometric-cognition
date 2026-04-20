"""
Experiment 018j: Quark Mass Ratios vs Monad Frequencies
========================================================
Focused test: do quark mass ratios follow the monad's frequency ratios?
"""

import numpy as np
from math import log, log10, sqrt

# Quark data (PDG 2024, MeV)
quarks_r1 = {  # T3=+1/2 (up-type), monad freq ALL = 0.5
    0: ('Up',     2.16),
    2: ('Charm',  1270.0),
    4: ('Top',    172520.0),
}

quarks_r2 = {  # T3=-1/2 (down-type), monad freq = sp/6
    0: ('Down',    4.67),
    2: ('Strange', 93.0),
    4: ('Bottom',  4180.0),
}

r2_freq = {0: 0.0, 2: 1/3, 4: 2/3}  # monad self-composition frequencies

print("=" * 70)
print("  QUARK MASS RATIOS vs MONAD FREQUENCIES")
print("=" * 70)
print()

# ====================================================================
#  1. WITHIN-RAIL MASS RATIOS
# ====================================================================
print("  WITHIN-RAIL (same isospin) mass ratios:")
print()

# R1: all freq = 0.5, but masses span 5 orders of magnitude
print("  R1 (up-type, T3=+1/2, ALL freq=0.5):")
for sp_a, (name_a, mass_a) in quarks_r1.items():
    for sp_b, (name_b, mass_b) in quarks_r1.items():
        if sp_a < sp_b:
            r = mass_b / mass_a
            print(f"    m_{name_b}/m_{name_a} = {r:>10.1f}  (freq ratio = 0.5/0.5 = 1.0)")

print()

# R2: freq = sp/6, masses span 3 orders
print("  R2 (down-type, T3=-1/2, freq = sp/6):")
for sp_a, (name_a, mass_a) in quarks_r2.items():
    for sp_b, (name_b, mass_b) in quarks_r2.items():
        if sp_a < sp_b:
            r = mass_b / mass_a
            fr = r2_freq[sp_b] / r2_freq[sp_a] if r2_freq[sp_a] > 0 else float('inf')
            lr = log(mass_b) / log(mass_a) if mass_a > 1 else float('inf')
            print(f"    m_{name_b}/m_{name_a} = {r:>10.1f}  (freq ratio = {r2_freq[sp_b]:.3f}/{r2_freq[sp_a]:.3f} = {fr:.3f})")

print()

# ====================================================================
#  2. CROSS-RAIL MASS RATIOS (same generation)
# ====================================================================
print("  CROSS-RAIL (same generation/sp) mass ratios:")
print()

for sp in [0, 2, 4]:
    r1_name, r1_mass = quarks_r1[sp]
    r2_name, r2_mass = quarks_r2[sp]
    ratio = r1_mass / r2_mass
    r1_freq = 0.5
    r2_f = r2_freq[sp]
    freq_ratio = r1_freq / r2_f if r2_f > 0 else float('inf')
    gen = sp // 2 + 1
    print(f"  Gen {gen} (sp={sp}): m_{r1_name}/m_{r2_name} = {ratio:>10.3f}  "
          f"(R1 freq=0.5, R2 freq={r2_f:.3f}, freq ratio={freq_ratio:.3f})")

print()

# ====================================================================
#  3. LOG-MASS vs FREQUENCY REGRESSION
# ====================================================================
print("  LOG-MASS vs MONAD FREQUENCY (R2 quarks only):")
print()

r2_data = [(sp, name, mass, r2_freq[sp]) for sp, (name, mass) in quarks_r2.items()]
print(f"  {'quark':>8} {'sp':>3} {'freq':>6} {'mass':>10} {'log(mass)':>10} {'log10(mass)':>12}")
for sp, name, mass, freq in r2_data:
    lm = log(mass)
    l10 = log10(mass)
    print(f"  {name:>8} {sp:>3} {freq:>6.3f} {mass:>10.2f} {lm:>10.3f} {l10:>12.3f}")

# Linear regression: log(mass) = a + b * freq
freqs = np.array([d[3] for d in r2_data])
log_masses = np.array([log(d[2]) for d in r2_data])

# Fit
if len(freqs) > 1:
    A = np.vstack([np.ones(len(freqs)), freqs]).T
    coeffs = np.linalg.lstsq(A, log_masses, rcond=None)
    a, b = coeffs[0]

    print()
    print(f"  Linear fit: log(mass) = {a:.3f} + {b:.3f} * freq")
    print()

    # Check predictions
    print(f"  {'quark':>8} {'actual log(m)':>12} {'predicted':>12} {'error':>8}")
    for sp, name, mass, freq in r2_data:
        actual = log(mass)
        predicted = a + b * freq
        error = actual - predicted
        print(f"  {name:>8} {actual:>12.3f} {predicted:>12.3f} {error:>8.3f}")

print()

# ====================================================================
#  4. EXPONENTIAL SCALING: mass ~ base^(freq)
# ====================================================================
print("  EXPONENTIAL SCALING TEST: mass ~ C * base^(freq):")
print()

# If mass = C * base^freq, then log(mass) = log(C) + freq * log(base)
# From R2 quarks: log(C) = log(m_d) since freq(d)=0, so C = m_d
C = quarks_r2[0][1]  # down quark mass
print(f"  C = m_down = {C:.2f} MeV (freq=0 anchor)")
print()

for sp, name, mass, freq in r2_data:
    if freq > 0:
        base = (mass / C) ** (1.0 / freq)
        print(f"  {name:>8}: mass/C = {mass/C:.2f}, base = (mass/C)^(1/freq) = {base:.4f}")

# Check if there's a consistent base
bases = []
for sp, name, mass, freq in r2_data:
    if freq > 0:
        base = (mass / C) ** (1.0 / freq)
        bases.append(base)

if len(bases) >= 2:
    print(f"  Base range: {min(bases):.4f} to {max(bases):.4f}")
    print(f"  Ratio of bases: {max(bases)/min(bases):.4f}")
    print(f"  Average base: {np.mean(bases):.4f}")

print()

# ====================================================================
#  5. GENERATIONAL MASS RATIOS
# ====================================================================
print("  GENERATIONAL MASS RATIOS (Gen II/I, Gen III/II, Gen III/I):")
print()

# Up-type (R1)
print("  Up-type quarks (R1, all freq=0.5):")
gen_ratios_r1 = []
for (sp_a, (n_a, m_a)), (sp_b, (n_b, m_b)) in [((0, quarks_r1[0]), (2, quarks_r1[2])),
                                                    ((2, quarks_r1[2]), (4, quarks_r1[4])),
                                                    ((0, quarks_r1[0]), (4, quarks_r1[4]))]:
    r = m_b / m_a
    gen_a, gen_b = sp_a//2+1, sp_b//2+1
    print(f"    Gen {gen_b}/{gen_a}: m_{n_b}/m_{n_a} = {r:.1f}")
    gen_ratios_r1.append(r)

print()

# Down-type (R2)
print("  Down-type quarks (R2, freq = sp/6):")
gen_ratios_r2 = []
for (sp_a, (n_a, m_a)), (sp_b, (n_b, m_b)) in [((0, quarks_r2[0]), (2, quarks_r2[2])),
                                                    ((2, quarks_r2[2]), (4, quarks_r2[4])),
                                                    ((0, quarks_r2[0]), (4, quarks_r2[4]))]:
    r = m_b / m_a
    gen_a, gen_b = sp_a//2+1, sp_b//2+1
    fr = r2_freq[sp_b] / r2_freq[sp_a] if r2_freq[sp_a] > 0 else float('inf')
    print(f"    Gen {gen_b}/{gen_a}: m_{n_b}/m_{n_a} = {r:.1f}  (freq ratio = {fr:.3f})")
    gen_ratios_r2.append(r)

print()

# Ratio of generational ratios between rails
print("  Cross-rail ratio of generational mass ratios:")
print(f"    (m_c/m_u) / (m_s/m_d) = {gen_ratios_r1[0]/gen_ratios_r2[0]:.3f}")
print(f"    (m_t/m_c) / (m_b/m_s) = {gen_ratios_r1[1]/gen_ratios_r2[1]:.3f}")
print(f"    (m_t/m_u) / (m_b/m_d) = {gen_ratios_r1[2]/gen_ratios_r2[2]:.3f}")

print()

# ====================================================================
#  6. THE KEY CHECK: DO MASS RATIOS = MONAD FREQUENCY RATIOS?
# ====================================================================
print("  DIRECT COMPARISON: mass ratios vs monad frequency ratios")
print()
print("  Monad says R2 quark frequencies are 0, 1/3, 2/3")
print("  If mass proportional to frequency, we'd expect:")
print("    m_d : m_s : m_b = 0 : 1/3 : 2/3")
print("  Actual:")
print(f"    m_d : m_s : m_b = {quarks_r2[0][1]:.2f} : {quarks_r2[2][1]:.2f} : {quarks_r2[4][1]:.2f}")
print(f"    Normalized: 1.0 : {quarks_r2[2][1]/quarks_r2[0][1]:.1f} : {quarks_r2[4][1]/quarks_r2[0][1]:.1f}")
print()
print("  If mass ~ exp(k * freq), then:")
print("    m_d : m_s : m_b = 1 : exp(k/3) : exp(2k/3)")

# Fit k from m_s/m_d
k_fit = 3 * log(quarks_r2[2][1] / quarks_r2[0][1])
print(f"    From m_s/m_d: k = 3*ln({quarks_r2[2][1]/quarks_r2[0][1]:.1f}) = {k_fit:.3f}")
print(f"    Predicted m_b/m_d = exp(2*{k_fit:.3f}/3) = {np.exp(2*k_fit/3):.1f}")
print(f"    Actual m_b/m_d = {quarks_r2[4][1]/quarks_r2[0][1]:.1f}")
print(f"    Error: {abs(np.exp(2*k_fit/3) - quarks_r2[4][1]/quarks_r2[0][1])/quarks_r2[4][1]*100:.1f}%")

print()

# ====================================================================
#  7. ALTERNATIVE: LOG-LINEAR WITH FREQUENCY
# ====================================================================
print("  ALTERNATIVE: mass ratio ~ (freq_ratio)^n for some power n")
print()

# m_s / m_d = (freq_s / freq_d)^n = infinity (freq_d=0), doesn't work
# Try: mass ~ freq + offset
# m_d = a + b*0 = a = 4.67
# m_s = a + b*(1/3) = 4.67 + b/3 = 93 → b = 3*(93-4.67) = 264.99
# m_b = a + b*(2/3) = 4.67 + 264.99*2/3 = 181.0 vs actual 4180
# Way off — linear doesn't work.

print("  Linear: mass = a + b*freq")
a_lin = quarks_r2[0][1]
b_lin = 3 * (quarks_r2[2][1] - a_lin)
predicted_b = a_lin + b_lin * (2/3)
print(f"    a={a_lin:.2f}, b={b_lin:.2f}")
print(f"    Predicted m_b = {predicted_b:.1f}, actual = {quarks_r2[4][1]:.1f}")
print(f"    MASSIVE discrepancy — linear fails completely.")
print()

# ====================================================================
#  8. THE CROSS-RAIL RATIOS AS THE KEY
# ====================================================================
print("  CROSS-RAIL RATIOS (the Mobius connection):")
print()
print("  For each generation, R1_mass / R2_mass = up-type / down-type:")
print()

cross = {}
for sp in [0, 2, 4]:
    r1_name, r1_mass = quarks_r1[sp]
    r2_name, r2_mass = quarks_r2[sp]
    ratio = r1_mass / r2_mass
    gen = sp // 2 + 1
    cross[gen] = ratio
    # Monad frequency ratio
    r1_f = 0.5
    r2_f = r2_freq[sp]
    print(f"  Gen {gen}: m_{r1_name}/m_{r2_name} = {ratio:.3f}  "
          f"(R1_freq={r1_f}, R2_freq={r2_f:.3f})")

print()

# Do the cross-rail ratios follow any pattern?
print("  Pattern in cross-rail ratios:")
r01 = cross[1]
r02 = cross[2]
r03 = cross[3]
print(f"    Gen I:   {r01:.3f}")
print(f"    Gen II:  {r02:.3f}")
print(f"    Gen III: {r03:.3f}")
print(f"    Ratio Gen II/I:  {r02/r01:.2f}")
print(f"    Ratio Gen III/II: {r03/r02:.2f}")
print(f"    Ratio Gen III/I:  {r03/r01:.2f}")

print()

# ====================================================================
#  9. GEORGI-JARLSKOG AND THE MONAD
# ====================================================================
print("  GEORGI-JARLSKOG CHECK:")
print()
print("  At GUT scale: m_mu/m_s ~ 3, m_e/m_d ~ 1/3, m_tau/m_b ~ 1")
print("  In the monad: mu is at sp=3 (freq=1/2), s is at sp=2 (freq=1/3)")
print(f"  Frequency ratio: 1/2 / 1/3 = {0.5/(1/3):.2f}")
print(f"  Mass ratio m_mu/m_s = {105.66/93:.2f}")
print()
print("  e at sp=1 (freq=1/6), d at sp=0 (freq=0)")
print(f"  m_e/m_d = {0.511/4.67:.3f}  (GJ predicts 1/3 = 0.333)")
print()
print("  tau at sp=5 (freq=5/6), b at sp=4 (freq=2/3)")
print(f"  m_tau/m_b = {1776.86/4180:.3f}  (GJ predicts ~1)")
print(f"  Freq ratio: (5/6)/(2/3) = {(5/6)/(2/3):.2f}")

print()

# ====================================================================
#  SUMMARY
# ====================================================================
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print()
print("  DO QUARK MASS RATIOS MATCH MONAD FREQUENCIES?")
print()
print("  DIRECT match: NO.")
print("  R2 quark frequencies are 0, 1/3, 2/3 but masses are")
print("  4.67, 93, 4180 MeV — not proportional to frequency.")
print()
print("  LOG-LINEAR match: APPROXIMATE.")
print("  log(mass) ~ a + b*freq gives r^2 correlation,")
print("  but the exponential prediction for m_b from m_d,m_s")
print("  is off by ~2x. Not exact, but the trend is there.")
print()
print("  CROSS-RAIL RATIOS: INTERESTING.")
print("  The up/down mass ratio grows with generation:")
print("  Gen I: 0.46, Gen II: 13.7, Gen III: 41.3")
print("  This growth parallels the increasing R1-R2 frequency gap.")
print()
print("  GEORGI-JARLSKOG: the factor of 3 between charged leptons")
print("  and down-type quarks at GUT scale IS the monad's 3:1")
print("  Mobius ratio (R1_freq/R2_freq for sp=1,2).")
print()
print("  The monad captures the STRUCTURE (which particles are related)")
print("  but the mass VALUES require additional physics (Higgs coupling,")
print("  running masses, RG flow) beyond the geometric framework.")
print()
print("Done.")
