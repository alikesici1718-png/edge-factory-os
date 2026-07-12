"""
Volume Momentum x Size Interaction Test
=========================================
For each symbol, compute average daily quote volume as a size proxy.
Split 81 symbols into large/mid/small terciles.
Within each size group, run flat vs rising-volume Mann-Whitney comparison.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

PANEL_CSV  = Path(__file__).resolve().parents[1] / "outputs" / "volume_momentum_analysis_panel.csv"
CACHE_DIR  = Path(__file__).resolve().parents[1] / "cache" / "liquidity_analysis_daily_ohlcv"
RATIO_THRESHOLD = 1.5
SEP = "=" * 68


def mwu(a, b):
    if len(a) < 5 or len(b) < 5:
        return np.nan, np.nan
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    rb = 1 - (2 * u) / (len(a) * len(b))
    return p, rb


def main():
    print(SEP)
    print("Volume Momentum x Size Interaction Test")
    print(SEP)

    # ── Step 1: Compute per-symbol average daily quote volume ─────────────────
    print("\nComputing per-symbol average daily quote volume...")
    sym_avg_vol = {}
    missing = []
    for f in sorted(CACHE_DIR.glob("*_daily.parquet")):
        sym = f.stem.replace("_daily", "")
        df  = pd.read_parquet(f)
        if "quote_volume" not in df.columns or df.empty:
            missing.append(sym)
            continue
        sym_avg_vol[sym] = float(df["quote_volume"].mean())

    if missing:
        print(f"  Symbols with no volume data: {missing}")

    vol_series = pd.Series(sym_avg_vol).sort_values(ascending=False)
    print(f"  Symbols with volume data: {len(vol_series)}")
    print(f"\n  Volume range:")
    print(f"    Max  : {vol_series.max():>18,.0f} USDT/day  ({vol_series.idxmax()})")
    print(f"    Min  : {vol_series.min():>18,.0f} USDT/day  ({vol_series.idxmin()})")
    print(f"    P33  : {vol_series.quantile(0.333):>18,.0f} USDT/day")
    print(f"    P67  : {vol_series.quantile(0.667):>18,.0f} USDT/day")

    # Tercile split
    p33 = vol_series.quantile(1/3)
    p67 = vol_series.quantile(2/3)

    def size_label(v):
        if v >= p67: return "Large"
        if v >= p33: return "Mid"
        return "Small"

    sym_size = vol_series.apply(size_label)
    size_counts = sym_size.value_counts()
    print(f"\n  Tercile assignment:")
    for label in ["Large", "Mid", "Small"]:
        n = size_counts.get(label, 0)
        threshold = p67 if label == "Large" else p33
        syms = sorted(sym_size[sym_size == label].index.tolist())
        print(f"    {label:5s} (n={n:2d}): {', '.join(syms[:6])}{'...' if len(syms) > 6 else ''}")

    # ── Step 2: Load panel and merge size labels ──────────────────────────────
    panel = pd.read_csv(PANEL_CSV).dropna(subset=["excess_12m", "vol_ratio"])
    panel["size"] = panel["symbol"].map(sym_size)

    unmapped = panel["size"].isna().sum()
    if unmapped:
        print(f"\n  WARNING: {unmapped} panel rows have no size label (dropped).")
    panel = panel.dropna(subset=["size"])

    print(f"\n  Panel rows by size group:")
    for label in ["Large", "Mid", "Small"]:
        sub = panel[panel["size"] == label]
        print(f"    {label:5s}: {len(sub):>5} rows  "
              f"({sub['symbol'].nunique()} symbols, "
              f"{(sub['vol_ratio'] >= RATIO_THRESHOLD).sum()} rising obs)")

    # ── Step 3: MWU within each size group ────────────────────────────────────
    print(f"\n{SEP}")
    print("RESULTS BY SIZE GROUP")
    print(SEP)

    results = {}
    for label in ["Large", "Mid", "Small"]:
        sub    = panel[panel["size"] == label]
        flat   = sub.loc[sub["vol_ratio"] <  RATIO_THRESHOLD, "excess_12m"].values
        rising = sub.loc[sub["vol_ratio"] >= RATIO_THRESHOLD, "excess_12m"].values

        p, rb  = mwu(flat, rising)
        flat_med   = np.median(flat)   * 100 if len(flat)   > 0 else np.nan
        rising_med = np.median(rising) * 100 if len(rising) > 0 else np.nan
        spread     = flat_med - rising_med if not (np.isnan(flat_med) or np.isnan(rising_med)) else np.nan

        results[label] = dict(flat_med=flat_med, rising_med=rising_med,
                               spread=spread, p=p, rb=rb,
                               n_flat=len(flat), n_rising=len(rising))

        sig = "SIGNIFICANT" if (not np.isnan(p) and p < 0.05) else "not significant"
        print(f"\n  {label} cap (n_flat={len(flat)}, n_rising={len(rising)})")
        print(f"    Flat   median: {flat_med:>+7.1f}%")
        print(f"    Rising median: {rising_med:>+7.1f}%")
        print(f"    Spread       : {spread:>+7.1f} ppt")
        if not np.isnan(p):
            print(f"    MWU p={p:.4e}  r={rb:+.3f}  [{sig}]")
        else:
            print(f"    MWU: insufficient data")

    # ── Summary table ─────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("SUMMARY TABLE")
    print(SEP)
    print(f"\n  {'Group':<8} {'n_flat':>7} {'n_rising':>9} {'flat_med':>9} "
          f"{'rising_med':>11} {'spread':>8} {'p-value':>12} {'r':>7} {'sig?'}")
    print(f"  {'-'*82}")

    # Also show full-period baseline
    flat_all   = panel[panel["vol_ratio"] <  RATIO_THRESHOLD]["excess_12m"].values
    rising_all = panel[panel["vol_ratio"] >= RATIO_THRESHOLD]["excess_12m"].values
    p_all, rb_all = mwu(flat_all, rising_all)
    print(f"  {'All':8s} {len(flat_all):>7} {len(rising_all):>9} "
          f"{np.median(flat_all)*100:>+8.1f}% {np.median(rising_all)*100:>+10.1f}% "
          f"{(np.median(flat_all)-np.median(rising_all))*100:>+7.1f}% "
          f"{p_all:>12.4e} {rb_all:>+6.3f}  {'YES' if p_all < 0.05 else 'NO'}  (baseline)")

    for label in ["Large", "Mid", "Small"]:
        r = results[label]
        p_str = f"{r['p']:.4e}" if not np.isnan(r['p']) else "n/a"
        rb_str = f"{r['rb']:+.3f}" if not np.isnan(r['p']) else "n/a"
        sig = "YES" if (not np.isnan(r['p']) and r['p'] < 0.05) else "NO"
        print(f"  {label:8s} {r['n_flat']:>7} {r['n_rising']:>9} "
              f"{r['flat_med']:>+8.1f}% {r['rising_med']:>+10.1f}% "
              f"{r['spread']:>+7.1f}% {p_str:>12} {rb_str:>7}  {sig}")

    # ── Interpretation ────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("INTERPRETATION")
    print(SEP)
    sig_groups = [l for l in ["Large", "Mid", "Small"]
                  if not np.isnan(results[l]['p']) and results[l]['p'] < 0.05]
    dir_groups = [l for l in ["Large", "Mid", "Small"]
                  if not np.isnan(results[l]['spread']) and results[l]['spread'] > 0]
    print(f"\n  Significant at p<0.05: {sig_groups if sig_groups else 'none'}")
    print(f"  Correct direction (flat > rising): {dir_groups}")

    if len(dir_groups) == 3:
        print("\n  Direction is CONSISTENT across all three size groups.")
    elif len(dir_groups) == 0:
        print("\n  Direction REVERSES in all groups -- unexpected.")
    else:
        print(f"\n  Direction is MIXED -- present in {dir_groups}, absent/reversed elsewhere.")

    spreads = {l: results[l]['spread'] for l in ["Large", "Mid", "Small"]
               if not np.isnan(results[l]['spread'])}
    if spreads:
        strongest = max(spreads, key=spreads.get)
        weakest   = min(spreads, key=spreads.get)
        print(f"\n  Strongest spread: {strongest} ({spreads[strongest]:+.1f} ppt)")
        print(f"  Weakest  spread: {weakest}  ({spreads[weakest]:+.1f} ppt)")


if __name__ == "__main__":
    main()
