"""
Liquidity Quartile Analysis — 81-symbol universe
=================================================
For each calendar month, compute trailing-3-month average daily quote volume
per symbol, assign volume quartile (Q1=least liquid, Q4=most liquid), then
measure 6- and 12-month forward excess return vs BTC.

Data: Binance USDM futures daily OHLCV via public REST API (no auth required).
Date range: 2022-01-01 → 2025-06-30 (covers 12-month forward through 2024-06)
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

# ── Config ──────────────────────────────────────────────────────────────────
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

START_DATE = "2022-01-01"  # need 3-month lookback before first measurement month
END_DATE   = "2025-06-30"  # need 12-month forward through mid-2025

BASE_URL   = "https://fapi.binance.com"
KLINES_EP  = "/fapi/v1/klines"
LIMIT      = 1500  # max candles per request

CACHE_DIR  = Path(__file__).resolve().parents[1] / "cache" / "liquidity_analysis_daily_ohlcv"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"

TRAILING_MONTHS = 3
FORWARD_PERIODS = [6, 12]

# ── Helpers ──────────────────────────────────────────────────────────────────

def _ts_ms(date_str: str) -> int:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def fetch_daily_ohlcv(symbol: str, start: str, end: str) -> pd.DataFrame:
    """Download daily klines from Binance futures, page through if needed."""
    cache_file = CACHE_DIR / f"{symbol}_daily.parquet"
    if cache_file.exists():
        df = pd.read_parquet(cache_file)
        if not df.empty:
            start_ts = pd.Timestamp(start, tz="UTC")
            end_ts   = pd.Timestamp(end,   tz="UTC")
            idx_min  = df.index.min()
            idx_max  = df.index.max()
            # normalize tz for comparison
            if idx_min.tzinfo is None:
                idx_min = idx_min.tz_localize("UTC")
                idx_max = idx_max.tz_localize("UTC")
            if idx_min <= start_ts and idx_max >= end_ts:
                return df

    rows = []
    start_ms = _ts_ms(start)
    end_ms   = _ts_ms(end) + 86_400_000  # inclusive

    while start_ms < end_ms:
        params = {
            "symbol":    symbol,
            "interval":  "1d",
            "startTime": start_ms,
            "endTime":   end_ms - 1,
            "limit":     LIMIT,
        }
        resp = requests.get(BASE_URL + KLINES_EP, params=params, timeout=30)
        if resp.status_code == 400:
            # symbol may not have existed yet; return empty
            break
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        rows.extend(data)
        last_open_ms = data[-1][0]
        if last_open_ms == start_ms:
            break  # no progress
        start_ms = last_open_ms + 1
        time.sleep(0.05)  # gentle rate limit

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=[
        "open_time","open","high","low","close","volume",
        "close_time","quote_volume","num_trades",
        "taker_buy_base","taker_buy_quote","ignore",
    ])
    df["date"]         = pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.normalize()
    df["close"]        = df["close"].astype(float)
    df["quote_volume"] = df["quote_volume"].astype(float)
    df = df.set_index("date")[["close", "quote_volume"]].sort_index()
    df = df[~df.index.duplicated(keep="last")]

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_file)
    return df


# ── Core analysis ────────────────────────────────────────────────────────────

def build_monthly_panel(symbols: list[str], start: str, end: str) -> pd.DataFrame:
    """Return monthly DataFrame with columns: symbol, month, avg_volume, close."""
    records = []
    for i, sym in enumerate(symbols, 1):
        print(f"  [{i:>2}/{len(symbols)}] {sym}", end="", flush=True)
        try:
            df = fetch_daily_ohlcv(sym, start, end)
        except Exception as e:
            print(f" ERROR: {e}")
            continue
        if df.empty:
            print(" (no data)")
            continue

        # monthly last close and monthly avg daily quote volume
        monthly_close  = df["close"].resample("MS").last()
        monthly_volume = df["quote_volume"].resample("MS").mean()

        for month, vol in monthly_volume.items():
            close = monthly_close.get(month)
            if close is None or np.isnan(vol):
                continue
            records.append({"symbol": sym, "month": month, "avg_daily_vol": vol, "close": float(close)})
        print(f" {len(df)} days")

    return pd.DataFrame(records)


def compute_trailing_volume(panel: pd.DataFrame, n_months: int) -> pd.DataFrame:
    """For each symbol-month, compute trailing n-month average of avg_daily_vol."""
    panel = panel.sort_values(["symbol", "month"])
    panel["trail_vol"] = (
        panel.groupby("symbol")["avg_daily_vol"]
        .transform(lambda x: x.rolling(n_months, min_periods=n_months).mean())
    )
    return panel.dropna(subset=["trail_vol"])


def assign_quartiles(panel: pd.DataFrame) -> pd.DataFrame:
    """For each month, assign volume quartile (Q1=bottom 25%, Q4=top 25%)."""
    def _assign_q(g: pd.Series) -> pd.Series:
        try:
            return pd.qcut(g, 4, labels=[1, 2, 3, 4]).astype(float)
        except ValueError:
            return pd.Series(np.nan, index=g.index)

    panel["quartile"] = panel.groupby("month")["trail_vol"].transform(
        lambda g: _assign_q(g)
    )
    return panel.dropna(subset=["quartile"])


def compute_forward_returns(panel: pd.DataFrame, months_fwd: int) -> pd.Series:
    """Compute log return from month T to month T+months_fwd for each symbol-month."""
    close_map = panel.set_index(["symbol", "month"])["close"]

    def _fwd(row):
        t = row["month"]
        # compute target month-start, preserving timezone
        yr  = t.year + (t.month - 1 + months_fwd) // 12
        mo  = (t.month - 1 + months_fwd) % 12 + 1
        tz  = t.tzinfo
        t_fwd = pd.Timestamp(yr, mo, 1, tz=tz) if tz else pd.Timestamp(yr, mo, 1)
        key = (row["symbol"], t_fwd)
        if key in close_map.index:
            return np.log(close_map[key] / row["close"])
        return np.nan

    return panel.apply(_fwd, axis=1)


def run_analysis(panel: pd.DataFrame) -> dict:
    results = {}
    # BTC series
    btc = panel[panel["symbol"] == "BTCUSDT"].set_index("month")["close"]

    for fwd in FORWARD_PERIODS:
        panel[f"ret_{fwd}m"] = compute_forward_returns(panel, fwd)

        # BTC return for same horizon
        def btc_ret(row):
            t0 = row["month"]
            yr  = t0.year + (t0.month - 1 + fwd) // 12
            mo  = (t0.month - 1 + fwd) % 12 + 1
            tz  = t0.tzinfo
            t1  = pd.Timestamp(yr, mo, 1, tz=tz) if tz else pd.Timestamp(yr, mo, 1)
            if t0 in btc.index and t1 in btc.index:
                return np.log(btc[t1] / btc[t0])
            return np.nan

        panel[f"btc_ret_{fwd}m"] = panel.apply(btc_ret, axis=1)
        panel[f"excess_{fwd}m"]  = panel[f"ret_{fwd}m"] - panel[f"btc_ret_{fwd}m"]

        summary = (
            panel.dropna(subset=[f"excess_{fwd}m"])
            .groupby("quartile")[f"excess_{fwd}m"]
            .agg(median="median", count="count", mean="mean")
            .reset_index()
        )
        summary[["median", "mean"]] = summary[["median", "mean"]].map(
            lambda x: round(x * 100, 2)  # convert to pct
        )
        results[f"{fwd}m"] = summary
    return results, panel


def main():
    print("=" * 60)
    print("Liquidity Quartile Analysis — 81-symbol universe")
    print("=" * 60)
    print(f"\nDownloading daily OHLCV ({START_DATE} to {END_DATE}) ...")
    panel_raw = build_monthly_panel(SYMBOLS, START_DATE, END_DATE)

    print(f"\nMonthly records before filtering: {len(panel_raw)}")

    panel = compute_trailing_volume(panel_raw, TRAILING_MONTHS)
    print(f"Monthly records after trailing-vol filter ({TRAILING_MONTHS}m): {len(panel)}")

    panel = assign_quartiles(panel)
    print(f"Monthly records after quartile assignment: {len(panel)}")

    results, panel_full = run_analysis(panel)

    # ── Print results ────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("RESULTS: Median excess return vs BTC by volume quartile")
    print("(Q1=least liquid, Q4=most liquid; returns in %)")
    print("=" * 60)

    for horizon, df in results.items():
        print(f"\n{horizon} forward excess return:")
        print(df.to_string(index=False))

    # ── Save outputs ─────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUTPUT_DIR / "liquidity_quartile_analysis_results.csv"
    combined = []
    for horizon, df in results.items():
        df = df.copy()
        df["horizon"] = horizon
        combined.append(df)
    pd.concat(combined).to_csv(out_csv, index=False)
    print(f"\nResults saved to: {out_csv}")

    # Save full panel
    panel_csv = OUTPUT_DIR / "liquidity_quartile_analysis_panel.csv"
    panel_full.to_csv(panel_csv, index=False)
    print(f"Full panel saved to: {panel_csv}")


if __name__ == "__main__":
    main()
