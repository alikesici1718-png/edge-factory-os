"""
Volume Momentum -- Yearly Breakdown (2022-2025)
================================================
For each calendar year in the panel, compute flat vs rising group
medians, spread, and MWU. Flags years with thin data.
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

PANEL_CSV  = Path(__file__).resolve().parents[1] / "outputs" / "volume_momentum_analysis_panel.csv"
OUT_PNG    = Path(__file__).resolve().parents[1] / "artifacts" / "visualizations" / "volume_momentum_yearly_spread.png"
RATIO_THRESHOLD = 1.5
MIN_OBS    = 10     # flag years below this per group
SEP        = "=" * 64


def mwu(a, b):
    if len(a) < 5 or len(b) < 5:
        return np.nan, np.nan
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    rb = 1 - (2 * u) / (len(a) * len(b))
    return p, rb


def main():
    print(SEP)
    print("Volume Momentum -- Yearly Breakdown")
    print(SEP)

    panel = pd.read_csv(PANEL_CSV)
    panel["month"] = pd.to_datetime(panel["month"])
    panel = panel.dropna(subset=["excess_12m", "vol_ratio"])
    panel["year"] = panel["month"].dt.year

    years = sorted(panel["year"].unique())
    print(f"\nPanel range: {panel['month'].min().date()} to {panel['month'].max().date()}")
    print(f"Years with data: {years}\n")

    results = {}
    for yr in years:
        sub    = panel[panel["year"] == yr]
        flat   = sub.loc[sub["vol_ratio"] <  RATIO_THRESHOLD, "excess_12m"].values
        rising = sub.loc[sub["vol_ratio"] >= RATIO_THRESHOLD, "excess_12m"].values
        months_present = sorted(sub["month"].dt.month.unique())
        n_months = len(sub["month"].unique())

        thin = len(flat) < MIN_OBS or len(rising) < MIN_OBS
        p, rb = mwu(flat, rising)
        flat_med   = np.median(flat)   * 100 if len(flat)   > 0 else np.nan
        rising_med = np.median(rising) * 100 if len(rising) > 0 else np.nan
        spread     = flat_med - rising_med if not (np.isnan(flat_med) or np.isnan(rising_med)) else np.nan

        results[yr] = dict(
            n_flat=len(flat), n_rising=len(rising), n_months=n_months,
            flat_med=flat_med, rising_med=rising_med, spread=spread,
            p=p, rb=rb, thin=thin,
        )

        sig_str  = ""
        if not np.isnan(p):
            sig_str = f"  p={p:.3e}  r={rb:+.3f}  {'[SIG]' if p < 0.05 else '[n.s.]'}"
        thin_str = "  *** THIN DATA ***" if thin else ""
        print(f"  {yr}  months={n_months:2d}  n_flat={len(flat):3d}  n_rising={len(rising):3d}"
              f"  flat={flat_med:>+7.1f}%  rising={rising_med:>+7.1f}%  spread={spread:>+6.1f}%"
              f"{sig_str}{thin_str}")

    # ── Summary table ─────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("SUMMARY TABLE")
    print(SEP)
    print(f"\n  {'Year':>5} {'months':>7} {'n_flat':>7} {'n_rising':>9} "
          f"{'flat_med':>9} {'rising_med':>11} {'spread':>8} {'p-value':>12} {'r':>7} {'sig?':<6} {'thin?'}")
    print(f"  {'-'*96}")
    for yr, r in results.items():
        p_str  = f"{r['p']:.3e}"  if not np.isnan(r['p']) else "n/a"
        rb_str = f"{r['rb']:+.3f}" if not np.isnan(r['p']) else "n/a"
        sig    = "YES" if (not np.isnan(r['p']) and r['p'] < 0.05) else ("n/a" if np.isnan(r['p']) else "no")
        thin   = "YES" if r['thin'] else "-"
        print(f"  {yr:>5} {r['n_months']:>7} {r['n_flat']:>7} {r['n_rising']:>9} "
              f"{r['flat_med']:>+8.1f}% {r['rising_med']:>+10.1f}% {r['spread']:>+7.1f}% "
              f"{p_str:>12} {rb_str:>7} {sig:<6} {thin}")

    # ── Direction check ───────────────────────────────────────────────────────
    valid = {yr: r for yr, r in results.items() if not np.isnan(r['spread'])}
    pos_dir = [yr for yr, r in valid.items() if r['spread'] > 0]
    neg_dir = [yr for yr, r in valid.items() if r['spread'] <= 0]
    print(f"\n  Years with correct direction (flat > rising): {pos_dir}")
    if neg_dir:
        print(f"  Years with REVERSED direction              : {neg_dir}")
    else:
        print(f"  No year shows a direction reversal.")

    # ── Chart ─────────────────────────────────────────────────────────────────
    BG = "#f9f9f9"
    fig, ax = plt.subplots(figsize=(9, 5.5), facecolor=BG)
    ax.set_facecolor(BG)

    yr_list    = [yr for yr in years if not np.isnan(results[yr]['spread'])]
    spreads    = [results[yr]['spread'] for yr in yr_list]
    thin_flags = [results[yr]['thin']   for yr in yr_list]
    sig_flags  = [not np.isnan(results[yr]['p']) and results[yr]['p'] < 0.05 for yr in yr_list]

    bar_colors = []
    for s, thin, sig in zip(spreads, thin_flags, sig_flags):
        if thin:
            bar_colors.append("#b0bec5")     # grey = thin data
        elif s > 0:
            bar_colors.append("#43a047")     # green = flat > rising (correct dir)
        else:
            bar_colors.append("#e53935")     # red = reversal

    bars = ax.bar(yr_list, spreads, color=bar_colors, width=0.55,
                  edgecolor="white", linewidth=0.8, zorder=3)
    ax.axhline(0, color="#424242", linewidth=1.2, zorder=4)

    for bar, yr, sp, thin, sig in zip(bars, yr_list, spreads, thin_flags, sig_flags):
        label = f"{sp:+.1f}%"
        if thin:
            label += "\n(thin)"
        elif sig:
            label += "\n*"
        va  = "bottom" if sp >= 0 else "top"
        ypos = sp + (0.5 if sp >= 0 else -0.5)
        ax.text(bar.get_x() + bar.get_width()/2, ypos, label,
                ha="center", va=va, fontsize=9,
                fontweight="bold" if sig else "normal",
                color="#212121")

    ax.set_xticks(yr_list)
    ax.set_xticklabels([str(y) for y in yr_list], fontsize=11)
    ax.set_ylabel("Spread: flat median - rising median (ppt)", fontsize=10)
    ax.yaxis.grid(True, color="#e0e0e0", linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#43a047", label="Correct direction (flat > rising), p<0.05 = *"),
        Patch(facecolor="#e53935", label="Direction reversal"),
        Patch(facecolor="#b0bec5", label="Thin data (<10 obs in one group)"),
    ]
    ax.legend(handles=legend_elements, fontsize=8.5, loc="lower right",
              framealpha=0.9, edgecolor="#ccc")

    ax.set_title(
        "Volume Momentum Reversal: Spread by Calendar Year\n"
        "Spread = flat/declining group median minus rising-volume group median (12m excess vs BTC)",
        fontsize=11, fontweight="bold", color="#212121", pad=8,
    )
    fig.text(0.5, 0.01,
             "Data: Binance USDM futures, 81 symbols, 2022-2025  |  "
             "Source: tools/yearly_breakdown_test.py",
             ha="center", fontsize=8, color="#9e9e9e", fontstyle="italic")

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(OUT_PNG, dpi=150, bbox_inches="tight", facecolor=BG)
    print(f"\nChart saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
