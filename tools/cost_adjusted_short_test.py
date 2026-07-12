"""
Cost-Adjusted Short Test -- Volume Momentum Strategy
=====================================================
For the "rising volume" (>=1.5x ratio) group, compute net return of a short
position that captures the excess-return signal, after:
  1. Round-trip trading fee (entry + exit)
  2. Cumulative 12-month funding rate (collected or paid by short)

Data sources:
  - Volume momentum panel:  outputs/volume_momentum_analysis_panel.csv
  - Funding rates:          downloaded from Binance USDM futures API
                            GET /fapi/v1/fundingRate (public, no auth)
  - Fee assumptions:        Binance/OKX maker fee = 0.02%, taker = 0.05%
                            Round-trip used: 0.10% (2x taker, conservative)
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

PANEL_CSV  = Path(__file__).resolve().parents[1] / "outputs" / "volume_momentum_analysis_panel.csv"
CACHE_DIR  = Path(__file__).resolve().parents[1] / "cache" / "funding_rate_daily_cache"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"

BASE_URL      = "https://fapi.binance.com"
FUNDING_EP    = "/fapi/v1/fundingRate"

RATIO_THRESHOLD   = 1.5
ROUND_TRIP_FEE    = 0.001        # 0.10% round-trip (conservative taker both sides)
FORWARD_MONTHS    = 12
HOURS_PER_PERIOD  = 8            # Binance standard
PERIODS_PER_DAY   = 3
PERIODS_PER_YEAR  = PERIODS_PER_DAY * 365

SEP = "-" * 60

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


# ── Funding rate download ─────────────────────────────────────────────────────

def _ts_ms(date_str: str) -> int:
    return int(pd.Timestamp(date_str, tz="UTC").timestamp() * 1000)


def fetch_funding_rates(symbol: str, start: str, end: str) -> pd.DataFrame:
    cache = CACHE_DIR / f"{symbol}_funding.parquet"
    if cache.exists():
        df = pd.read_parquet(cache)
        if not df.empty:
            idx_min = df.index.min()
            idx_max = df.index.max()
            if hasattr(idx_min, "tzinfo") and idx_min.tzinfo is None:
                idx_min = idx_min.tz_localize("UTC")
                idx_max = idx_max.tz_localize("UTC")
            s_ts = pd.Timestamp(start, tz="UTC")
            e_ts = pd.Timestamp(end,   tz="UTC")
            if idx_min <= s_ts and idx_max >= e_ts:
                return df

    rows = []
    start_ms = _ts_ms(start)
    end_ms   = _ts_ms(end)

    while start_ms < end_ms:
        params = {
            "symbol":    symbol,
            "startTime": start_ms,
            "endTime":   end_ms,
            "limit":     1000,
        }
        resp = requests.get(BASE_URL + FUNDING_EP, params=params, timeout=30)
        if resp.status_code == 400:
            break
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        rows.extend(data)
        last_ms = int(data[-1]["fundingTime"])
        if last_ms <= start_ms:
            break
        start_ms = last_ms + 1
        time.sleep(0.05)

    if not rows:
        return pd.DataFrame(columns=["funding_rate"])

    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["fundingTime"].astype(int), unit="ms", utc=True)
    df["funding_rate"] = df["fundingRate"].astype(float)
    df = df.set_index("time")[["funding_rate"]].sort_index()
    df = df[~df.index.duplicated(keep="last")]

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache)
    return df


def build_monthly_avg_funding(symbols: list[str], start: str, end: str) -> pd.DataFrame:
    records = []
    for i, sym in enumerate(symbols, 1):
        print(f"  [{i:>2}/{len(symbols)}] {sym}", end="", flush=True)
        try:
            df = fetch_funding_rates(sym, start, end)
        except Exception as e:
            print(f" ERROR: {e}")
            continue
        if df.empty:
            print(" (no data)")
            continue
        # Monthly sum of funding rates (each rate applies to one 8h period)
        monthly = df["funding_rate"].resample("MS").agg(
            sum_rate="sum",
            count="count",
        )
        for month, row in monthly.iterrows():
            if row["count"] > 0:
                records.append({
                    "symbol":      sym,
                    "month":       month.tz_localize(None),  # strip tz for join
                    "monthly_sum_funding": float(row["sum_rate"]),
                    "monthly_n_periods":   int(row["count"]),
                })
        print(f" {len(df)} periods")

    return pd.DataFrame(records)


# ── Cost computation ──────────────────────────────────────────────────────────

def compute_12m_funding_sum(panel: pd.DataFrame, monthly_funding: pd.DataFrame) -> pd.Series:
    """
    For each observation (symbol, month T), sum funding rates over months T to T+11.
    Positive sum = shorts RECEIVE (positive funding means longs pay shorts).
    """
    fund_map = monthly_funding.set_index(["symbol", "month"])["monthly_sum_funding"]

    def _sum(row):
        sym = row["symbol"]
        t0  = pd.Timestamp(row["month"])
        total = 0.0
        found = 0
        for m_offset in range(FORWARD_MONTHS):
            yr  = t0.year + (t0.month - 1 + m_offset) // 12
            mo  = (t0.month - 1 + m_offset) % 12 + 1
            key = (sym, pd.Timestamp(yr, mo, 1))
            if key in fund_map.index:
                total += fund_map[key]
                found += 1
        if found < FORWARD_MONTHS * 0.8:   # require >=80% months covered
            return np.nan
        return total

    return panel.apply(_sum, axis=1)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(SEP)
    print("Cost-Adjusted Short Test -- Volume Momentum Strategy")
    print(SEP)

    panel = pd.read_csv(PANEL_CSV)
    panel = panel.dropna(subset=["excess_12m", "vol_ratio"])
    rising = panel[panel["vol_ratio"] >= RATIO_THRESHOLD].copy()
    flat   = panel[panel["vol_ratio"] <  RATIO_THRESHOLD].copy()

    print(f"\nPanel loaded: rising n={len(rising)}, flat n={len(flat)}")

    # Date range needed: earliest month in panel to latest+12
    min_date = pd.Timestamp(panel["month"].min())
    max_date = pd.Timestamp(panel["month"].max()) + pd.DateOffset(months=13)
    start_str = min_date.strftime("%Y-%m-%d")
    end_str   = max_date.strftime("%Y-%m-%d")
    print(f"Funding rate download range: {start_str} to {end_str}")

    print("\nDownloading funding rates...")
    monthly_funding = build_monthly_avg_funding(SYMBOLS, start_str, end_str)
    print(f"\nMonthly funding records: {len(monthly_funding)}")
    print(f"Symbols with data: {monthly_funding['symbol'].nunique()}")

    # Global funding rate stats across all symbols/months
    print("\nFunding rate summary (per funding period = 8h):")
    all_rates = monthly_funding["monthly_sum_funding"] / monthly_funding["monthly_n_periods"]
    print(f"  Per-period mean  : {all_rates.mean()*100:+.4f}%")
    print(f"  Per-period median: {all_rates.median()*100:+.4f}%")
    print(f"  Annual equivalent: {all_rates.mean() * PERIODS_PER_YEAR * 100:+.2f}%")
    positive_pct = (all_rates > 0).mean() * 100
    print(f"  % positive periods: {positive_pct:.1f}%  (shorts receive when positive)")

    # ── Adim 1: Brut getiri ────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("ADIM 1: Brut getiri (kisa pozisyon, BTC'ye gore)")
    print(SEP)

    # Short position: profit = -excess_12m (if symbol falls relative to BTC, short profits)
    rising["gross_short_ret"] = -rising["excess_12m"]
    flat["gross_short_ret"]   = -flat["excess_12m"]

    gross_rising = rising["gross_short_ret"].dropna()
    gross_flat   = flat["gross_short_ret"].dropna()

    print(f"  Rising (short target): median brut  = {gross_rising.median()*100:+.2f}%  n={len(gross_rising)}")
    print(f"  Flat   (long target):  median brut  = {gross_flat.median()*100:+.2f}%  n={len(gross_flat)}")

    # ── Adim 2: Fee maliyeti ───────────────────────────────────────────────
    print(f"\n{SEP}")
    print(f"ADIM 2: Round-trip fee  ({ROUND_TRIP_FEE*100:.2f}%)")
    print(SEP)
    print(f"  Varsayim: Binance/OKX taker fee 0.05% her iki taraf = 0.10% toplam")
    print(f"  Etki:     brut getiriden dogrudan dusulur")

    fee_cost = ROUND_TRIP_FEE  # sabit, her gozlem icin ayni

    # ── Adim 3: Funding rate ───────────────────────────────────────────────
    print(f"\n{SEP}")
    print("ADIM 3: 12 aylik birikimli funding rate")
    print(SEP)

    rising_fund = compute_12m_funding_sum(rising, monthly_funding)
    flat_fund   = compute_12m_funding_sum(flat,   monthly_funding)

    rising["funding_12m"] = rising_fund.values
    flat["funding_12m"]   = flat_fund.values

    r_valid = rising.dropna(subset=["funding_12m"])
    f_valid = flat.dropna(subset=["funding_12m"])

    if len(r_valid) > 0:
        print(f"  Rising group funding coverage: {len(r_valid)}/{len(rising)} obs")
        fund_med_r = r_valid["funding_12m"].median()
        fund_mean_r = r_valid["funding_12m"].mean()
        print(f"  Median 12m cumulative funding (short receives if +): {fund_med_r*100:+.4f}%")
        print(f"  Mean   12m cumulative funding                      : {fund_mean_r*100:+.4f}%")
        pct_pos = (r_valid["funding_12m"] > 0).mean() * 100
        print(f"  % observations where funding > 0 (short profits)   : {pct_pos:.1f}%")
    else:
        print("  WARNING: No funding data coverage for rising group -- using global estimate")
        # Fallback: use global mean annualized
        global_annual_funding = all_rates.mean() * PERIODS_PER_YEAR
        fund_med_r  = global_annual_funding
        fund_mean_r = global_annual_funding
        print(f"  Fallback: global mean annual funding = {global_annual_funding*100:+.2f}%")
        r_valid = rising.copy()
        r_valid["funding_12m"] = fund_med_r

    # ── Adim 4: Net sonuc ─────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("ADIM 4: Net sonuc (brut - fee + funding)")
    print(SEP)

    r_valid = r_valid.dropna(subset=["gross_short_ret", "funding_12m"])

    r_valid["net_ret"] = r_valid["gross_short_ret"] - fee_cost + r_valid["funding_12m"]

    net_med  = r_valid["net_ret"].median()
    net_mean = r_valid["net_ret"].mean()
    net_pct25 = r_valid["net_ret"].quantile(0.25)
    net_pct75 = r_valid["net_ret"].quantile(0.75)
    pct_positive = (r_valid["net_ret"] > 0).mean() * 100

    print(f"\n  Gozlem sayisi        : {len(r_valid)}")
    print(f"  Brut medyan (short)  : {r_valid['gross_short_ret'].median()*100:+.2f}%")
    print(f"  - Round-trip fee     : -{fee_cost*100:.2f}%")
    print(f"  + Funding (medyan)   : {r_valid['funding_12m'].median()*100:+.4f}%")
    print(f"  = NET medyan         : {net_med*100:+.2f}%")
    print(f"    NET ortalama       : {net_mean*100:+.2f}%")
    print(f"    NET IQR            : [{net_pct25*100:+.1f}%, {net_pct75*100:+.1f}%]")
    print(f"    % net pozitif      : {pct_positive:.1f}%")

    print(f"\n{'='*60}")
    print("OZET")
    print("="*60)
    if net_med > 0:
        print(f"  NET medyan +{net_med*100:.1f}% -- maliyet ve funding sonrasi hala POZITIF")
    else:
        print(f"  NET medyan {net_med*100:.1f}% -- maliyet ve funding sonrasi NEGATIF")
    print(f"  Fee etkisi: kucuk ({fee_cost*100:.2f}%), 12 aylik gross getiriye gore ihmal edilebilir")

    # Funding net pozitif mi negatif mi etki?
    fund_contribution = r_valid["funding_12m"].median()
    if fund_contribution > 0:
        print(f"  Funding etkisi: SHORT lehine (+{fund_contribution*100:.2f}%), maliyeti dusuruyor")
    else:
        print(f"  Funding etkisi: SHORT aleyhine ({fund_contribution*100:.2f}%), maliyeti artiriyor")

    print(f"\n  NOT: IQR genisligi [{net_pct25*100:+.1f}%, {net_pct75*100:+.1f}%] -- bireysel")
    print(f"  islem bazinda yuksek varyans devam ediyor. Portfoy seviyesinde anlamli,")
    print(f"  tek sembol bazinda guvenilir degil.")

    # Save
    out = OUTPUT_DIR / "cost_adjusted_short_results.csv"
    summary = pd.DataFrame([{
        "gross_median_pct":    r_valid["gross_short_ret"].median() * 100,
        "fee_cost_pct":        fee_cost * 100,
        "funding_median_pct":  r_valid["funding_12m"].median() * 100,
        "net_median_pct":      net_med * 100,
        "net_mean_pct":        net_mean * 100,
        "net_iqr_q25":         net_pct25 * 100,
        "net_iqr_q75":         net_pct75 * 100,
        "pct_net_positive":    pct_positive,
        "n_obs":               len(r_valid),
    }])
    summary.to_csv(out, index=False)
    print(f"\nSonuclar kaydedildi: {out}")


if __name__ == "__main__":
    main()
