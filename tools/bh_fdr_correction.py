"""
BH-FDR Multiple Testing Correction
====================================
Applies Benjamini-Hochberg FDR correction to all independent hypotheses
tested tonight across BIST and crypto analyses.

p-value sources:
  BIST short-term  : tools/liquidity_premium_test.py    (Welch t-test, recomputed from t-stats)
  BIST long-term   : tools/long_term_diffusion_cleaned.py (Mann-Whitney, recomputed from U-stats)
  BIST regime x2   : README / extreme_down_regime_regression.py (regression interaction p-vals)
  Crypto volume mom: tools/volume_momentum_significance_test.py (Mann-Whitney)
  Forex carry      : tools/analyze_carry_trade.py (permutation test p-val)

Excluded (no formal p-value):
  - Crypto liquidity quartile  : descriptive medians only, no hypothesis test run
  - Crypto funding rate carry  : descriptive stats only (BTCUSDT ~3.6%/yr), no null hypothesis tested
  - Crypto subperiod P1/P2     : robustness checks on the same hypothesis, not independent

Note on BIST multi-horizon tests (3m, 6m, 12m): these test the SAME underlying hypothesis
(illiquid stocks underperform) at different horizons. They are NOT independent, so including
all three inflates the multiple testing burden relative to the actual family-wise error rate.
We include them as-is (conservative for BH) but flag the dependency below.
"""
import numpy as np
from scipy import stats

# ── Exact p-value computation for tests reported as 0.000 ─────────────────────

# BIST short-term: Welch t-test, large df (~17000)
p_bist_st_q1q3 = float(2 * stats.t.sf(3.363, df=17000))   # Q1 vs Q3
p_bist_st_q1q4 = float(2 * stats.t.sf(5.623, df=17000))   # Q1 vs Q4

# BIST long-term: Mann-Whitney normal approximation (large samples)
def mw_p(U, n1, n2):
    mu    = n1 * n2 / 2
    sigma = np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    z     = (U - mu) / sigma
    return float(2 * stats.norm.sf(abs(z)))

p_bist_lt_1m  = 0.0124                              # directly from script output
p_bist_lt_3m  = mw_p(U=9521059, n1=4195, n2=4171)
p_bist_lt_6m  = mw_p(U=9322216, n1=4050, n2=4031)
p_bist_lt_12m = mw_p(U=8580157, n1=3769, n2=3746)

# Crypto volume momentum: directly from significance_test.py output
p_crypto_vm   = 6.277e-11

# Forex carry: permutation test p-value from analyze_carry_trade.py
p_forex_carry = 0.129

# BIST regime interaction tests (from README / extreme_down_regime_regression.py)
p_bist_regime_macro    = 0.72   # USDTRY/TLREF interaction term
p_bist_regime_illiquid = 0.66   # extreme-down illiquid segment test

# ── Master table ───────────────────────────────────────────────────────────────

tests = [
    # (label, p_value, is_independent_primary, note)
    ("BIST_ST_Q1vsQ3",        p_bist_st_q1q3,       True,  "Welch t-test; Q1 vs Q3 quarterly excess return"),
    ("BIST_ST_Q1vsQ4",        p_bist_st_q1q4,       True,  "Welch t-test; Q1 vs Q4 quarterly excess return"),
    ("BIST_LT_1m_horizon",    p_bist_lt_1m,         True,  "Mann-Whitney; illiquid vs liquid 1m forward"),
    ("BIST_LT_3m_horizon",    p_bist_lt_3m,         False, "Mann-Whitney; SAME hypothesis as LT, 3m horizon [DEPENDENT]"),
    ("BIST_LT_6m_horizon",    p_bist_lt_6m,         False, "Mann-Whitney; SAME hypothesis as LT, 6m horizon [DEPENDENT]"),
    ("BIST_LT_12m_horizon",   p_bist_lt_12m,        False, "Mann-Whitney; SAME hypothesis as LT, 12m horizon [DEPENDENT]"),
    ("BIST_Regime_Macro",     p_bist_regime_macro,  True,  "Regression interaction; USDTRY/TLREF macro regime"),
    ("BIST_Regime_Illiquid",  p_bist_regime_illiquid, True, "Regression; extreme-down illiquid segment"),
    ("Crypto_VolMomentum",    p_crypto_vm,           True,  "Mann-Whitney; rising vs flat volume ratio, 12m excess vs BTC"),
    ("Forex_Carry",           p_forex_carry,         True,  "Permutation test; USDTRY carry trade returns"),
]

labels  = [t[0] for t in tests]
pvals   = np.array([t[1] for t in tests])
is_primary = [t[2] for t in tests]
notes   = [t[3] for t in tests]
m       = len(tests)

# ── BH-FDR correction ─────────────────────────────────────────────────────────
alpha = 0.05

# Sort by p-value ascending
order = np.argsort(pvals)
pvals_sorted = pvals[order]
ranks = np.arange(1, m + 1)

# BH thresholds
bh_thresholds = ranks / m * alpha

# Find last k where p(k) <= (k/m)*alpha
sig_mask_sorted = pvals_sorted <= bh_thresholds
if sig_mask_sorted.any():
    last_sig = np.where(sig_mask_sorted)[0].max()
    reject_sorted = np.zeros(m, dtype=bool)
    reject_sorted[:last_sig + 1] = True
else:
    reject_sorted = np.zeros(m, dtype=bool)

# BH-adjusted q-values: q_i = min over j>=i of (p_j * m / j)
q_sorted = np.minimum.accumulate((pvals_sorted * m / ranks)[::-1])[::-1]
q_sorted = np.minimum(q_sorted, 1.0)

# Map back to original order
reject = reject_sorted[np.argsort(order)]
q_vals = q_sorted[np.argsort(order)]

# ── Report ─────────────────────────────────────────────────────────────────────

SEP = "=" * 72

print(SEP)
print("BH-FDR Multiple Testing Correction -- All Tonight's Hypotheses")
print(SEP)

print(f"\nTotal tests in family:  {m}")
print(f"  - Primary independent hypotheses: {sum(is_primary)}")
print(f"  - Dependent multi-horizon checks: {sum(not p for p in is_primary)}")
print(f"  (All {m} included in correction — conservative choice)")
print(f"\nalpha = {alpha}  |  Method: Benjamini-Hochberg (FDR)\n")

print(f"{'Rank':<5} {'Label':<26} {'p-value':>12} {'BH thresh':>10} {'q-value':>10} {'Reject?':<8} {'Primary?'}")
print("-" * 85)

for rank_i, idx in enumerate(order, 1):
    lbl      = labels[idx]
    pv       = pvals[idx]
    qv       = q_vals[idx]
    thresh   = rank_i / m * alpha
    rej      = reject[idx]
    primary  = "YES" if is_primary[idx] else "no (dep)"
    rej_str  = "REJECT" if rej else "retain"
    print(f"{rank_i:<5} {lbl:<26} {pv:>12.3e} {thresh:>10.4f} {qv:>10.4f}  {rej_str:<8} {primary}")

print(SEP)
print("\nSUMMARY BY HYPOTHESIS CATEGORY\n")

categories = [
    ("BIST Short-Term Liquidity Premium",
     ["BIST_ST_Q1vsQ3", "BIST_ST_Q1vsQ4"]),
    ("BIST Long-Term Liquidity Premium",
     ["BIST_LT_1m_horizon", "BIST_LT_3m_horizon", "BIST_LT_6m_horizon", "BIST_LT_12m_horizon"]),
    ("BIST Regime Robustness (x2)",
     ["BIST_Regime_Macro", "BIST_Regime_Illiquid"]),
    ("Crypto Volume Momentum",
     ["Crypto_VolMomentum"]),
    ("Forex Carry",
     ["Forex_Carry"]),
]

for cat_name, cat_labels in categories:
    idxs = [labels.index(l) for l in cat_labels if l in labels]
    print(f"  {cat_name}")
    for i in idxs:
        r = "REJECT H0 (significant)" if reject[i] else "retain H0 (not significant)"
        dep = " [DEPENDENT]" if not is_primary[i] else ""
        print(f"    {labels[i]:<26}  p={pvals[i]:.3e}  q={q_vals[i]:.4f}  => {r}{dep}")
    print()

# Focus on crypto volume momentum
vm_idx = labels.index("Crypto_VolMomentum")
print(SEP)
print("FOCUS: Crypto Volume Momentum Signal\n")
print(f"  Raw p-value       : {pvals[vm_idx]:.4e}")
print(f"  BH q-value        : {q_vals[vm_idx]:.4e}")
print(f"  BH threshold (k/m*alpha): {(order.tolist().index(vm_idx) + 1) / m * alpha:.4f}")
print(f"  Survives FDR=5%?  : {'YES' if reject[vm_idx] else 'NO'}")
print()
if reject[vm_idx]:
    print("  VERDICT: The crypto volume-momentum finding SURVIVES Benjamini-Hochberg")
    print("  FDR correction at alpha=0.05, even within a 10-test family that includes")
    print("  3 dependent multi-horizon BIST tests (which increase the penalty).")
    print()
    print("  The p-value (6.3e-11) is so far below the BH threshold that even if we")
    print("  doubled the number of tests (20-test family), the finding would still survive.")
    print()
    margin = pvals[vm_idx] / q_vals[vm_idx]
    rank_vm = order.tolist().index(vm_idx) + 1
    bh_thresh_vm = rank_vm / m * alpha
    print(f"  Safety margin: p = {pvals[vm_idx]:.2e} vs BH threshold = {bh_thresh_vm:.4f}")
    print(f"  That is {bh_thresh_vm / pvals[vm_idx]:.1e}x below the rejection threshold.")

print()
print("EXCLUDED FROM CORRECTION (no formal p-value available):")
print("  - Crypto liquidity quartile : descriptive analysis only (no MWU run)")
print("  - Crypto funding rate carry : descriptive stats only (no null hypothesis test)")
print("  - Crypto subperiod P1/P2    : robustness checks on the same hypothesis")
print()
print(SEP)
