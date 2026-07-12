"""
Volume Momentum -- Multi-Horizon Test (3m, 6m, 12m)
=====================================================
Computes forward excess return vs BTC at 3, 6, and 12 month horizons
for the same flat/rising vol-ratio groups. Runs MWU + placebo at each.
Uses the existing daily OHLCV parquet cache.
"""
from __future__ import annotations
from pathlib import Path
import random
import numpy as np
import pandas as pd
from scipy import stats

CACHE_DIR  = Path(__file__).resolve().parents[1] / "cache" / "liquidity_analysis_daily_ohlcv"
PANEL_CSV  = Path(__file__).resolve().parents[1] / "outputs" / "volume_momentum_analysis_panel.csv"
RATIO_THRESHOLD = 1.5
WINDOW_MONTHS   = 12
HALF            = 6
HORIZONS        = [3, 6, 12]
N_PLACEBO       = 1000
SEED            = 42
SEP             = "=" * 68

SYMBOLS: list[str] = [
    "1INCHUSDT","AAVEUSDT","ADAUSDT","AGLDUSDT","ALGOUSDT","APEUSDT","API3USDT",
    "APTUSDT","ARBUSDT","ARUSDT","ATOMUSDT","AVAXUSDT","AXSUSDT","BANDUSDT",
    "BATUSDT","BCHUSDT","BICOUSDT","BLURUSDT","BNBUSDT","BTCUSDT","CELOUSDT",
    "CFXUSDT","CHZUSDT","COMPUSDT","CRVUSDT","DOGEUSDT","DOTUSDT","DYDXUSDT",
    "EGLDUSDT","ENSUSDT","ETCUSDT","ETHUSDT","ETHWUSDT","FILUSDT","GALAUSDT",
    "GMTUSDT","GMXUSDT","GRTUSDT","ICPUSDT","IMXUSDT","IOSTUSDT","IOTAUSDT",
    "KSMUSDT","LDOUSDT","LINKUSDT","LPTUSDT","LRCUSDT","LTCUSDT","MAGICUSDT",
    "MANAUSDT","MINAUSDT","NEARUSDT","NEOUSDT","ONTUSDT","OPUSDT","ORDIUSDT",
    "PEOPLEUSDT","QTUMUSDT","RSRUSDT","RVNUSDT","SANDUSDT","SNXUSDT","SOLUSDT",
    "STXUSDT","SUIUSDT","SUSHIUSDT","THETAUSDT","TONUSDT","TRBUSDT","TRXUSDT",
    "UMAUSDT","UNIUSDT","USDCUSDT","WOOUSDT","XLMUSDT","XRPUSDT","XTZUSDT",
    "YFIUSDT","YGGUSDT","ZILUSDT","ZRXUSDT",
]


def fwd_ts(t: pd.Timestamp, months: int) -> pd.Timestamp:
    yr = t.year + (t.month - 1 + months) // 12
    mo = (t.month - 1 + months) % 12 + 1
    return pd.Timestamp(yr, mo, 1)


def load_monthly(sym: str) -> pd.Series | None:
    f = CACHE_DIR / f"{sym}_daily.parquet"
    if not f.exists():
        return None
    df = pd.read_parquet(f)[["close"]]
    if df.index.tzinfo is not None:
        df.index = df.index.tz_localize(None)
    monthly = df["close"].resample("MS").last().dropna()
    return monthly


def build_panel() -> pd.DataFrame:
    """Build a panel with vol_ratio + forward excess returns at 3, 6, 12m."""
    # Load existing 12m panel for vol_ratio (already validated)
    base = pd.read_csv(PANEL_CSV)
    base["month"] = pd.to_datetime(base["month"])
    base = base.dropna(subset=["vol_ratio"])

    # Load monthly closes for BTC and all symbols
    btc_close = load_monthly("BTCUSDT")
    sym_closes: dict[str, pd.Series] = {}
    for sym in SYMBOLS:
        s = load_monthly(sym)
        if s is not None:
            sym_closes[sym] = s

    records = []
    for _, row in base.iterrows():
        sym = row["symbol"]
        t   = pd.Timestamp(row["month"])
        if sym not in sym_closes:
            continue
        sc = sym_closes[sym]
        row_dict = {"symbol": sym, "month": t, "vol_ratio": row["vol_ratio"]}
        for h in HORIZONS:
            t_fwd = fwd_ts(t, h)
            if t not in sc.index or t_fwd not in sc.index:
                row_dict[f"excess_{h}m"] = np.nan
                continue
            if btc_close is None or t not in btc_close.index or t_fwd not in btc_close.index:
                row_dict[f"excess_{h}m"] = np.nan
                continue
            sym_ret = np.log(sc[t_fwd] / sc[t])
            btc_ret = np.log(btc_close[t_fwd] / btc_close[t])
            row_dict[f"excess_{h}m"] = sym_ret - btc_ret
        records.append(row_dict)

    return pd.DataFrame(records)


def mwu(a, b):
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    rb = 1 - (2 * u) / (len(a) * len(b))
    return u, p, rb


def placebo(panel: pd.DataFrame, col: str, n: int = N_PLACEBO) -> float:
    """Return fraction of placebo runs significant at p<0.05."""
    rng      = random.Random(SEED)
    all_ret  = panel[col].values.copy()
    all_rat  = panel["vol_ratio"].values.copy()
    n_sig    = 0
    for _ in range(n):
        shuf = all_rat.copy()
        rng.shuffle(shuf)
        flat_p   = all_ret[shuf <  RATIO_THRESHOLD]
        rising_p = all_ret[shuf >= RATIO_THRESHOLD]
        if len(flat_p) < 2 or len(rising_p) < 2:
            continue
        _, p_p, _ = mwu(flat_p, rising_p)
        if p_p < 0.05:
            n_sig += 1
    return n_sig / n * 100


def main():
    print(SEP)
    print("Volume Momentum -- Multi-Horizon Test  (3m / 6m / 12m)")
    print(SEP)

    print("\nBuilding multi-horizon panel...")
    panel = build_panel()
    print(f"Panel rows: {len(panel)}  |  symbols: {panel['symbol'].nunique()}")

    results = {}

    for h in HORIZONS:
        col = f"excess_{h}m"
        sub = panel.dropna(subset=[col, "vol_ratio"])
        flat   = sub.loc[sub["vol_ratio"] <  RATIO_THRESHOLD, col].values
        rising = sub.loc[sub["vol_ratio"] >= RATIO_THRESHOLD, col].values

        u, p, rb = mwu(flat, rising)
        pct_sig_placebo = placebo(sub, col)
        spread = (np.median(flat) - np.median(rising)) * 100

        results[h] = dict(
            n_flat=len(flat), n_rising=len(rising),
            flat_med=np.median(flat)*100, rising_med=np.median(rising)*100,
            spread=spread, p=p, rb=rb,
            pct_sig_placebo=pct_sig_placebo,
        )

        print(f"\n{'-'*60}")
        print(f"Horizon: {h}m  (n_flat={len(flat)}, n_rising={len(rising)})")
        print(f"  Flat   median: {np.median(flat)*100:>+7.2f}%")
        print(f"  Rising median: {np.median(rising)*100:>+7.2f}%")
        print(f"  Spread       : {spread:>+7.2f} ppt")
        print(f"  MWU p={p:.4e}  rank-biserial r={rb:+.4f}")
        print(f"  Placebo % sig: {pct_sig_placebo:.1f}%  (expected ~5% by chance)")
        print(f"  Significant  : {'YES' if p < 0.05 else 'NO'}")

    # ── Comparative table ─────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("COMPARATIVE SUMMARY: Effect by Horizon")
    print(SEP)
    print(f"\n  {'Horizon':>8} {'n_flat':>7} {'n_rising':>9} {'flat_med':>9} "
          f"{'rising_med':>11} {'spread':>8} {'p-value':>12} {'r':>7} "
          f"{'placebo%':>9} {'sig?'}")
    print(f"  {'-'*94}")
    for h in HORIZONS:
        r = results[h]
        sig = "YES" if r['p'] < 0.05 else "NO"
        print(f"  {h:>7}m {r['n_flat']:>7} {r['n_rising']:>9} "
              f"{r['flat_med']:>+8.2f}% {r['rising_med']:>+10.2f}% "
              f"{r['spread']:>+7.2f}% {r['p']:>12.4e} {r['rb']:>+6.3f} "
              f"{r['pct_sig_placebo']:>8.1f}%  {sig}")

    print(f"\n  Note: placebo% = fraction of 1000 label-shuffled runs reaching p<0.05")
    print(f"        (expected ~5% under null; real signal if real is far below 5%)")

    # ── Strongest horizon ─────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("VERDICT")
    print(SEP)
    strongest = min(results, key=lambda h: results[h]['p'])
    widest    = max(results, key=lambda h: results[h]['spread'])
    print(f"\n  Strongest p-value : {strongest}m horizon  (p={results[strongest]['p']:.2e})")
    print(f"  Widest spread     : {widest}m horizon    (spread={results[widest]['spread']:+.1f} ppt)")
    sig_all = all(results[h]['p'] < 0.05 for h in HORIZONS)
    dir_all = all(results[h]['spread'] > 0 for h in HORIZONS)
    print(f"\n  Significant at all horizons tested: {'YES' if sig_all else 'NO'}")
    print(f"  Correct direction  at all horizons: {'YES' if dir_all else 'NO'}")
    if sig_all and dir_all:
        spread_3  = results[3]['spread']
        spread_6  = results[6]['spread']
        spread_12 = results[12]['spread']
        if spread_12 > spread_6 > spread_3:
            print("  Spread grows monotonically with horizon -- effect accumulates over time.")
        elif spread_3 > spread_6 > spread_12:
            print("  Spread shrinks with horizon -- effect is strongest short-term, mean-reverts.")
        else:
            print(f"  Spread: 3m={spread_3:+.1f}%  6m={spread_6:+.1f}%  12m={spread_12:+.1f}%")


if __name__ == "__main__":
    main()
