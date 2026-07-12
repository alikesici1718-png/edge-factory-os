"""
Threshold Sensitivity Test -- Volume Momentum Signal
=====================================================
Re-runs flat vs rising comparison at different vol_ratio thresholds.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

PANEL_CSV  = Path(__file__).resolve().parents[1] / "outputs" / "volume_momentum_analysis_panel.csv"
THRESHOLDS = [1.2, 1.3, 1.5, 1.7, 2.0]
SEP        = "=" * 72


def mwu(a, b):
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    rb = 1 - (2 * u) / (len(a) * len(b))
    return p, rb


def main():
    panel = pd.read_csv(PANEL_CSV).dropna(subset=["excess_12m", "vol_ratio"])

    print(SEP)
    print("Threshold Sensitivity Test -- Volume Momentum Signal")
    print(SEP)
    print(f"\n{'Threshold':>10} {'n_flat':>7} {'n_rising':>9} "
          f"{'flat_med':>9} {'rising_med':>11} {'spread':>8} {'p-value':>12} {'r':>7} {'sig?'}")
    print("-" * 88)

    for thr in THRESHOLDS:
        flat   = panel[panel["vol_ratio"] <  thr]["excess_12m"].values
        rising = panel[panel["vol_ratio"] >= thr]["excess_12m"].values
        if len(flat) < 5 or len(rising) < 5:
            print(f"{thr:>10.1f}x  (insufficient data)")
            continue
        p, rb = mwu(flat, rising)
        flat_med   = np.median(flat)   * 100
        rising_med = np.median(rising) * 100
        spread     = flat_med - rising_med
        marker     = "  *" if thr == 1.5 else ""
        sig        = "YES" if p < 0.05 else "NO"
        print(f"{thr:>9.1f}x {len(flat):>7} {len(rising):>9} "
              f"{flat_med:>+8.1f}% {rising_med:>+10.1f}% {spread:>+7.1f}% "
              f"{p:>12.4e} {rb:>+6.3f}  {sig}{marker}")

    print(f"\n  * = original threshold")
    print(f"\n{SEP}")
    print("DIRECTION CHECK: is flat_med > rising_med at every threshold?")
    all_same_dir = True
    for thr in THRESHOLDS:
        flat_med   = np.median(panel[panel["vol_ratio"] <  thr]["excess_12m"]) * 100
        rising_med = np.median(panel[panel["vol_ratio"] >= thr]["excess_12m"]) * 100
        if flat_med <= rising_med:
            all_same_dir = False
            print(f"  REVERSAL at threshold={thr}x  (flat={flat_med:+.1f}%, rising={rising_med:+.1f}%)")
    if all_same_dir:
        print(f"  YES -- flat > rising (same direction) at all {len(THRESHOLDS)} thresholds tested.")
    print(SEP)


if __name__ == "__main__":
    main()
