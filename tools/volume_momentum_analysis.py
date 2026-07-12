"""
Volume Momentum Analysis -- 81-symbol Binance USDM universe
============================================================
For each symbol-month, compute the trailing 12-month volume change ratio:
  ratio = avg_daily_vol(last 6 months) / avg_daily_vol(first 6 months)
         of the trailing 12-month window

Split symbols into:
  - "volume rising"  : ratio >= 1.5
  - "flat/declining" : ratio <  1.5

Then measure 12-month forward excess return vs BTC for each group.
Report median and observation count. No significance testing.

Uses cached parquet files from liquidity_quartile_analysis.py.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CACHE_DIR  = Path(__file__).resolve().parents[1] / "cache" / "liquidity_analysis_daily_ohlcv"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"

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

RATIO_THRESHOLD  = 1.5   # >= 1.5x = "volume rising"
FORWARD_MONTHS   = 12
WINDOW_MONTHS    = 12    # trailing window for ratio
HALF             = WINDOW_MONTHS // 2  # 6 months each half


# ── Load data ────────────────────────────────────────────────────────────────

def load_symbol(sym: str) -> pd.DataFrame | None:
    p = CACHE_DIR / f"{sym}_daily.parquet"
    if not p.exists():
        return None
    df = pd.read_parquet(p)
    # ensure tz-naive UTC-normalised index
    if df.index.tzinfo is not None:
        df.index = df.index.tz_convert("UTC").tz_localize(None)
    df = df.sort_index()
    return df


def build_monthly_panel() -> pd.DataFrame:
    """Monthly close + avg_daily_vol per symbol, UTC-naive timestamps."""
    records = []
    for sym in SYMBOLS:
        df = load_symbol(sym)
        if df is None or df.empty:
            continue
        monthly_close = df["close"].resample("MS").last()
        monthly_vol   = df["quote_volume"].resample("MS").mean()
        for month in monthly_vol.index:
            v = monthly_vol.get(month)
            c = monthly_close.get(month)
            if v is None or c is None or np.isnan(v) or np.isnan(c):
                continue
            records.append({"symbol": sym, "month": month,
                            "avg_daily_vol": float(v), "close": float(c)})
    return pd.DataFrame(records)


# ── Volume ratio ─────────────────────────────────────────────────────────────

def compute_volume_ratio(panel: pd.DataFrame) -> pd.DataFrame:
    """
    For month T, ratio = mean(vol[T-5..T]) / mean(vol[T-11..T-6])
    Requires 12 months of prior data; skips if insufficient.
    """
    panel = panel.sort_values(["symbol", "month"]).copy()

    def _ratio(g: pd.DataFrame) -> pd.Series:
        vols = g["avg_daily_vol"].values
        n    = len(vols)
        ratios = []
        for i in range(n):
            # need 12 months before and including T
            if i < WINDOW_MONTHS - 1:
                ratios.append(np.nan)
                continue
            recent  = vols[i - HALF + 1 : i + 1]          # last 6 months incl. T
            earlier = vols[i - WINDOW_MONTHS + 1 : i - HALF + 1]  # prior 6 months
            if len(recent) < HALF or len(earlier) < HALF:
                ratios.append(np.nan)
                continue
            early_mean = earlier.mean()
            if early_mean <= 0:
                ratios.append(np.nan)
                continue
            ratios.append(recent.mean() / early_mean)
        return pd.Series(ratios, index=g.index)

    panel["vol_ratio"] = panel.groupby("symbol", group_keys=False).apply(_ratio)
    return panel.dropna(subset=["vol_ratio"])


# ── Forward returns ──────────────────────────────────────────────────────────

def compute_forward_returns(panel: pd.DataFrame, months_fwd: int) -> pd.Series:
    close_map = panel.set_index(["symbol", "month"])["close"]

    def _fwd(row):
        t  = row["month"]
        yr = t.year + (t.month - 1 + months_fwd) // 12
        mo = (t.month - 1 + months_fwd) % 12 + 1
        t_fwd = pd.Timestamp(yr, mo, 1)
        key   = (row["symbol"], t_fwd)
        if key in close_map.index:
            return np.log(close_map[key] / row["close"])
        return np.nan

    return panel.apply(_fwd, axis=1)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Volume Momentum Analysis -- 81-symbol universe")
    print("=" * 60)

    print("\nBuilding monthly panel from cache...")
    panel = build_monthly_panel()
    print(f"  Raw monthly records: {len(panel)}")

    print("Computing trailing 12-month volume ratios...")
    panel = compute_volume_ratio(panel)
    print(f"  Records with valid ratio: {len(panel)}")

    # Label groups
    panel["group"] = panel["vol_ratio"].apply(
        lambda r: "rising (>=1.5x)" if r >= RATIO_THRESHOLD else "flat/declining (<1.5x)"
    )
    dist = panel["group"].value_counts()
    print(f"\n  Group distribution:")
    for g, cnt in dist.items():
        print(f"    {g}: {cnt}")

    print(f"\nComputing {FORWARD_MONTHS}-month forward excess returns vs BTC...")
    panel["ret_12m"] = compute_forward_returns(panel, FORWARD_MONTHS)

    # BTC return for the same horizon
    btc = panel[panel["symbol"] == "BTCUSDT"].set_index("month")["close"]

    def _btc_ret(row):
        t0 = row["month"]
        yr = t0.year + (t0.month - 1 + FORWARD_MONTHS) // 12
        mo = (t0.month - 1 + FORWARD_MONTHS) % 12 + 1
        t1 = pd.Timestamp(yr, mo, 1)
        if t0 in btc.index and t1 in btc.index:
            return np.log(btc[t1] / btc[t0])
        return np.nan

    panel["btc_ret_12m"] = panel.apply(_btc_ret, axis=1)
    panel["excess_12m"]  = panel["ret_12m"] - panel["btc_ret_12m"]

    panel_clean = panel.dropna(subset=["excess_12m"])

    # ── Results ──────────────────────────────────────────────────────────────
    summary = (
        panel_clean.groupby("group")["excess_12m"]
        .agg(
            median="median",
            mean="mean",
            count="count",
            pct25=lambda x: x.quantile(0.25),
            pct75=lambda x: x.quantile(0.75),
        )
        .reset_index()
    )
    for col in ["median", "mean", "pct25", "pct75"]:
        summary[col] = (summary[col] * 100).round(2)

    print("\n" + "=" * 60)
    print("RESULTS: 12-month forward excess return vs BTC")
    print(f"Ratio threshold: {RATIO_THRESHOLD}x  |  returns in %")
    print("=" * 60)
    print(summary.to_string(index=False))

    # Also break down by ratio quintile for more granularity
    panel_r = panel_clean.copy()
    panel_r["ratio_bin"] = pd.cut(
        panel_r["vol_ratio"],
        bins=[0, 0.5, 1.0, 1.5, 2.5, 5.0, np.inf],
        labels=["<0.5x", "0.5-1x", "1-1.5x", "1.5-2.5x", "2.5-5x", ">5x"],
    )
    detail = (
        panel_r.dropna(subset=["ratio_bin"])
        .groupby("ratio_bin", observed=True)["excess_12m"]
        .agg(median="median", count="count")
        .reset_index()
    )
    detail["median"] = (detail["median"] * 100).round(2)
    print("\nBy ratio bin (granular view):")
    print(detail.to_string(index=False))

    # ── Save ─────────────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / "volume_momentum_analysis_results.csv"
    summary.to_csv(out, index=False)
    detail_out = OUTPUT_DIR / "volume_momentum_analysis_detail.csv"
    detail.to_csv(detail_out, index=False)

    # Save panel with ratio for further use
    panel_out = OUTPUT_DIR / "volume_momentum_analysis_panel.csv"
    panel_clean[["symbol","month","vol_ratio","group","ret_12m","btc_ret_12m","excess_12m"]].to_csv(panel_out, index=False)

    print(f"\nSaved: {out}")
    print(f"Saved: {detail_out}")
    print(f"Saved: {panel_out}")


if __name__ == "__main__":
    main()
