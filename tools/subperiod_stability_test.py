"""
Subperiod Stability Test -- Volume Momentum Signal
===================================================
Splits 2022-2025 into two equal halves and repeats
flat/declining vs rising-volume comparison in each.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

PANEL_CSV = Path(__file__).resolve().parents[1] / "outputs" / "volume_momentum_analysis_panel.csv"
RATIO_THRESHOLD = 1.5
SEP = "-" * 60


def mwu_summary(a: np.ndarray, b: np.ndarray) -> dict:
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    rb = 1 - (2 * u) / (len(a) * len(b))
    return {"U": u, "p": p, "rank_biserial": rb, "sig": p < 0.05}


def report_period(label: str, sub: pd.DataFrame) -> None:
    sub = sub.dropna(subset=["excess_12m"])
    flat   = sub.loc[sub["vol_ratio"] <  RATIO_THRESHOLD, "excess_12m"].values
    rising = sub.loc[sub["vol_ratio"] >= RATIO_THRESHOLD, "excess_12m"].values

    print(f"\n  {label}")
    print(f"  {'Group':<22} {'n':>5}  {'median':>8}  {'mean':>8}  {'IQR q25':>8}  {'IQR q75':>8}")
    print(f"  {'-'*68}")

    for name, arr in [("flat/declining (<1.5x)", flat), ("rising (>=1.5x)", rising)]:
        if len(arr) < 5:
            print(f"  {name:<22}  n={len(arr):>3}  (insufficient data)")
            continue
        q25, q75 = np.percentile(arr, [25, 75])
        print(f"  {name:<22} {len(arr):>5}  {np.median(arr)*100:>+7.1f}%  "
              f"{np.mean(arr)*100:>+7.1f}%  {q25*100:>+7.1f}%  {q75*100:>+7.1f}%")

    if len(flat) >= 5 and len(rising) >= 5:
        r = mwu_summary(flat, rising)
        sig_str = "SIGNIFICANT" if r["sig"] else "not significant"
        print(f"\n  Mann-Whitney U={r['U']:,.0f}  p={r['p']:.3e}  "
              f"rank-biserial r={r['rank_biserial']:+.3f}  [{sig_str}]")
        spread = (np.median(flat) - np.median(rising)) * 100
        print(f"  Spread (flat - rising): {spread:+.1f} pct pts")
    else:
        print("  (skipping MWU -- insufficient observations in one group)")


def main():
    print("=" * 60)
    print("Subperiod Stability Test -- Volume Momentum Signal")
    print("=" * 60)

    panel = pd.read_csv(PANEL_CSV)
    panel["month"] = pd.to_datetime(panel["month"])
    panel = panel.dropna(subset=["excess_12m", "vol_ratio"])

    # Date range
    mn = panel["month"].min()
    mx = panel["month"].max()
    mid = mn + (mx - mn) / 2
    print(f"\n  Full panel: {mn.date()} to {mx.date()}  (n={len(panel)})")
    print(f"  Split point: {mid.date()}")

    p1_label = f"Period 1: {mn.date()} -- {mid.date()}"
    p2_label = f"Period 2: {mid.date()} -- {mx.date()}"

    p1 = panel[panel["month"] <= mid]
    p2 = panel[panel["month"] >  mid]

    print(f"\n  P1 observations (all groups): {len(p1)}")
    print(f"  P2 observations (all groups): {len(p2)}")

    print(f"\n{SEP}")
    print("RESULTS BY SUBPERIOD")
    print(SEP)

    report_period(p1_label, p1)
    report_period(p2_label, p2)

    print(f"\n{SEP}")
    print("FULL PERIOD (reference)")
    print(SEP)
    report_period("Full 2022-2025", panel)

    # Direction consistency check
    print(f"\n{'='*60}")
    print("CONSISTENCY CHECK")
    print("="*60)

    results = {}
    for label, sub in [("P1", p1), ("P2", p2), ("Full", panel)]:
        sub = sub.dropna(subset=["excess_12m"])
        flat   = sub.loc[sub["vol_ratio"] <  RATIO_THRESHOLD, "excess_12m"].values
        rising = sub.loc[sub["vol_ratio"] >= RATIO_THRESHOLD, "excess_12m"].values
        if len(flat) < 5 or len(rising) < 5:
            results[label] = None
            continue
        r = mwu_summary(flat, rising)
        results[label] = {
            "flat_med":   np.median(flat)   * 100,
            "rising_med": np.median(rising) * 100,
            "spread":     (np.median(flat) - np.median(rising)) * 100,
            "p":          r["p"],
            "sig":        r["sig"],
            "rb":         r["rank_biserial"],
        }

    print(f"\n  {'Period':<8}  {'flat med':>9}  {'rising med':>11}  {'spread':>8}  {'p-value':>10}  {'sig?':<5}  {'r':>6}")
    print(f"  {'-'*70}")
    for lbl, r in results.items():
        if r is None:
            print(f"  {lbl:<8}  (insufficient data)")
            continue
        print(f"  {lbl:<8}  {r['flat_med']:>+8.1f}%  {r['rising_med']:>+10.1f}%  "
              f"{r['spread']:>+7.1f}%  {r['p']:>10.3e}  {'YES' if r['sig'] else 'no':<5}  {r['rb']:>+6.3f}")

    # Verdict
    sigs  = [r["sig"]   for r in results.values() if r]
    signs = [r["spread"] > 0 for r in results.values() if r]
    print()
    if all(sigs):
        print("  VERDICT: Effect is significant in BOTH subperiods and the full period.")
    elif any(sigs):
        print("  VERDICT: Effect is significant in some but not all subperiods.")
    else:
        print("  VERDICT: Effect is not significant in either subperiod.")

    if all(signs):
        print("  Direction (flat > rising): CONSISTENT across both subperiods.")
    elif not any(signs):
        print("  Direction: reversed in both subperiods -- unexpected.")
    else:
        print("  Direction: INCONSISTENT -- reverses between subperiods.")


if __name__ == "__main__":
    main()
