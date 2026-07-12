"""
Outlier Robustness Test -- Volume Momentum Signal
==================================================
Remove the 10 worst-performing observations from the rising-volume group
and re-run Mann-Whitney to check whether the signal is driven by a handful
of extreme outliers.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

PANEL_CSV       = Path(__file__).resolve().parents[1] / "outputs" / "volume_momentum_analysis_panel.csv"
RATIO_THRESHOLD = 1.5
N_DROP          = 10
SEP             = "=" * 60


def mwu(a, b):
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    rb = 1 - (2 * u) / (len(a) * len(b))
    return u, p, rb


def main():
    panel = pd.read_csv(PANEL_CSV)
    panel = panel.dropna(subset=["excess_12m", "vol_ratio"])

    flat   = panel[panel["vol_ratio"] <  RATIO_THRESHOLD].copy()
    rising = panel[panel["vol_ratio"] >= RATIO_THRESHOLD].copy()

    print(SEP)
    print("Outlier Robustness Test -- Volume Momentum Signal")
    print(SEP)

    # ── Baseline ──────────────────────────────────────────────────────────────
    u0, p0, rb0 = mwu(flat["excess_12m"].values, rising["excess_12m"].values)
    print(f"\nBaseline (full rising group, n={len(rising)}):")
    print(f"  Flat   median : {np.median(flat['excess_12m'])*100:+.2f}%  (n={len(flat)})")
    print(f"  Rising median : {np.median(rising['excess_12m'])*100:+.2f}%  (n={len(rising)})")
    print(f"  MWU  p={p0:.4e}  rank-biserial r={rb0:+.4f}")

    # ── Worst 10 observations in rising group ─────────────────────────────────
    rising_sorted = rising.sort_values("excess_12m")
    worst10 = rising_sorted.head(N_DROP)[["symbol", "month", "vol_ratio", "excess_12m"]].copy()

    print(f"\n{SEP}")
    print(f"Worst {N_DROP} observations in rising-volume group (by excess_12m):")
    print(f"{SEP}")
    print(f"  {'Symbol':<14} {'Month':<12} {'vol_ratio':>9} {'excess_12m':>12}")
    print(f"  {'-'*52}")
    for _, row in worst10.iterrows():
        print(f"  {row['symbol']:<14} {str(row['month'])[:10]:<12} "
              f"{row['vol_ratio']:>9.2f}x {row['excess_12m']*100:>+11.1f}%")

    # Symbol frequency in worst 10
    sym_counts = worst10["symbol"].value_counts()
    multi = sym_counts[sym_counts > 1]
    if not multi.empty:
        print(f"\n  Symbols appearing more than once in worst 10:")
        for sym, cnt in multi.items():
            print(f"    {sym}: {cnt} observations")
    else:
        print(f"\n  All 10 observations are from distinct symbols.")

    # ── Trimmed test ──────────────────────────────────────────────────────────
    rising_trimmed = rising_sorted.iloc[N_DROP:]  # drop worst 10 rows

    u1, p1, rb1 = mwu(flat["excess_12m"].values, rising_trimmed["excess_12m"].values)

    print(f"\n{SEP}")
    print(f"After removing worst {N_DROP} rising observations (n_rising={len(rising_trimmed)}):")
    print(f"{SEP}")
    print(f"  Flat   median : {np.median(flat['excess_12m'])*100:+.2f}%  (n={len(flat)})")
    print(f"  Rising median : {np.median(rising_trimmed['excess_12m'])*100:+.2f}%  (n={len(rising_trimmed)})")
    print(f"  MWU  p={p1:.4e}  rank-biserial r={rb1:+.4f}")

    sig_before = p0 < 0.05
    sig_after  = p1 < 0.05
    shift_med  = (np.median(rising_trimmed["excess_12m"]) - np.median(rising["excess_12m"])) * 100

    print(f"\n  Median shift after trimming: {shift_med:+.2f} pct pts")
    print(f"  Significant before: {'YES' if sig_before else 'NO'}  |  After: {'YES' if sig_after else 'NO'}")

    print(f"\n{SEP}")
    print("VERDICT")
    print(SEP)
    if sig_after:
        print(f"\n  Signal SURVIVES removal of the {N_DROP} worst outliers.")
        print(f"  p drops from {p0:.2e} to {p1:.2e} -- still well below 0.05.")
        print(f"  The effect is NOT driven by a handful of extreme observations.")
        print(f"  Rank-biserial r shifts from {rb0:+.3f} to {rb1:+.3f} (small change).")
    else:
        print(f"\n  Signal DISAPPEARS after removing the {N_DROP} worst outliers.")
        print(f"  p jumps from {p0:.2e} to {p1:.2e} -- the result WAS outlier-driven.")

    # ── Escalating trim ───────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("Escalating trim sensitivity (how many must be removed to kill significance):")
    print(SEP)
    print(f"  {'N removed':>10}  {'n_rising':>9}  {'rising med':>11}  {'p-value':>12}  {'sig?'}")
    print(f"  {'-'*60}")
    for n_drop in [0, 5, 10, 20, 30, 50]:
        r_trim = rising_sorted.iloc[n_drop:]
        if len(r_trim) < 10:
            break
        u_t, p_t, _ = mwu(flat["excess_12m"].values, r_trim["excess_12m"].values)
        med_t = np.median(r_trim["excess_12m"]) * 100
        sig_t = "YES" if p_t < 0.05 else "NO"
        print(f"  {n_drop:>10}  {len(r_trim):>9}  {med_t:>+10.2f}%  {p_t:>12.4e}  {sig_t}")


if __name__ == "__main__":
    main()
