"""
Pilot study testing whether large aggressive buy orders (top 5% by size, buyer-initiated) predict
subsequent positive price movements on Binance perpetual futures (BTCUSDT, ETHUSDT, SOLUSDT,
BNBUSDT, XRPUSDT) over 1-3-6 hour horizons using Lee-Radhakrishna-style size classification;
downloads aggTrades data from Binance and outputs regression results with cost-adjusted metrics.
"""
# ON-TAAHHUT: Lee-Radhakrishna tarzi buyukluk siniflandirmasi.
# Hipotez: Bir sembolde belirli bir zaman penceresinde "buyuk islem" (ust %5 boyut,
# is_buyer_maker=False yani agresif alim) net akisi pozitifse, sonraki saatlerde
# fiyat ayni yonde hareket etmeye devam eder (kurumsal bilgi avantaji).
# Beklenen yon: pozitif. Beklenen buyukluk: mutevazi.
# Beklenen sonuc: yon dogru cikabilir ama maliyet sonrasi muhtemelen yine negatif kalir.
# Bu tek seferlik bir pilottur.

import io
import time
import zipfile
import urllib.request
import urllib.error
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# ---------------------------------------------------------------------------
# KONFIGÜRASYON
# ---------------------------------------------------------------------------
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
START_DATE = date(2026, 4, 1)
END_DATE = date(2026, 7, 6)

LARGE_TRADE_PCTL = 0.95          # ust %5 = "buyuk islem"
HORIZONS_H = [1, 3, 6]          # forward return horizon (saat)
TAKER_FEE_BPS = 4.5             # round-trip Binance perpetual taker fee

CACHE_DIR = Path(__file__).parent / "outputs" / "_aggtrades_pilot_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://data.binance.vision/data/futures/um/daily/aggTrades/{sym}/{sym}-aggTrades-{d}.zip"
REQUEST_DELAY = 0.4              # saniye

AGGTRADE_COLS = [
    "agg_trade_id", "price", "quantity",
    "first_trade_id", "last_trade_id",
    "transact_time", "is_buyer_maker",
]


# ---------------------------------------------------------------------------
# VERİ YÜKLEME / İNDİRME
# ---------------------------------------------------------------------------
def local_zip(sym: str, d: date) -> Path:
    return CACHE_DIR / sym / f"{sym}-aggTrades-{d}.zip"


def download_zip(sym: str, d: date) -> bytes | None:
    url = BASE_URL.format(sym=sym, d=d)
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "institutional-size-pilot/0.1"}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None          # o gun veri yok (tatil vs.)
        raise
    except Exception as e:
        print(f"  WARN: {sym} {d} indirilemedi: {e}")
        return None


def load_day(sym: str, d: date) -> pd.DataFrame | None:
    path = local_zip(sym, d)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        data = download_zip(sym, d)
        if data is None:
            return None
        path.write_bytes(data)
        time.sleep(REQUEST_DELAY)

    try:
        with zipfile.ZipFile(path) as zf:
            csv_name = zf.namelist()[0]
            with zf.open(csv_name) as f:
                df = pd.read_csv(f, header=0, names=AGGTRADE_COLS, skiprows=1,
                                 dtype={"agg_trade_id": "int64", "price": "float64",
                                        "quantity": "float64", "first_trade_id": "int64",
                                        "last_trade_id": "int64", "transact_time": "int64",
                                        "is_buyer_maker": "bool"})
        df["transact_time"] = pd.to_datetime(df["transact_time"].astype("int64"), unit="ms", utc=True)
        df["price"] = df["price"].astype(float)
        df["quantity"] = df["quantity"].astype(float)
        df["is_buyer_maker"] = df["is_buyer_maker"].astype(bool)
        return df
    except Exception as e:
        print(f"  WARN: {sym} {d} okunamadi: {e}")
        path.unlink(missing_ok=True)   # bozuk dosyayi sil
        return None


def load_symbol(sym: str) -> pd.DataFrame:
    days = []
    d = START_DATE
    while d <= END_DATE:
        days.append(d)
        d += timedelta(days=1)

    frames = []
    for i, day in enumerate(days):
        if i % 10 == 0:
            print(f"  {sym}: {day} ({i+1}/{len(days)})")
        df = load_day(sym, day)
        if df is not None:
            frames.append(df)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# SINYAL HESAPLAMA
# ---------------------------------------------------------------------------
def compute_hourly_panel(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hour"] = df["transact_time"].dt.floor("1h")

    rows = []
    for hour, grp in df.groupby("hour"):
        total_qty = grp["quantity"].sum()
        if total_qty == 0:
            continue

        # Buyuk islem esigi: o saatin ust %5'i
        q95 = grp["quantity"].quantile(LARGE_TRADE_PCTL)
        large = grp[grp["quantity"] >= q95]

        buy_large = large[~large["is_buyer_maker"]]["quantity"].sum()   # agresif alim
        sell_large = large[large["is_buyer_maker"]]["quantity"].sum()    # agresif satim
        net_large_flow = buy_large - sell_large
        net_large_flow_norm = net_large_flow / total_qty

        # Fiyat: saatin ilk ve son fiyati
        first_price = grp["price"].iloc[0]
        last_price = grp["price"].iloc[-1]

        rows.append({
            "hour": hour,
            "net_large_flow_norm": net_large_flow_norm,
            "last_price": last_price,
            "first_price": first_price,
            "total_qty": total_qty,
        })

    panel = pd.DataFrame(rows).sort_values("hour").reset_index(drop=True)
    return panel


def add_forward_returns(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.copy()
    for h in HORIZONS_H:
        fwd = panel["last_price"].shift(-h) / panel["last_price"] - 1
        panel[f"fwd_{h}h"] = fwd
    return panel


# ---------------------------------------------------------------------------
# REGRESYON
# ---------------------------------------------------------------------------
def run_regressions(panel: pd.DataFrame, sym: str) -> list[dict]:
    results = []
    signal_std = panel["net_large_flow_norm"].std()

    for h in HORIZONS_H:
        dep = f"fwd_{h}h"
        sub = panel[["net_large_flow_norm", dep]].dropna()
        if len(sub) < 30:
            continue

        model = smf.ols(f"{dep} ~ net_large_flow_norm", data=sub).fit()
        coef = model.params["net_large_flow_norm"]
        tstat = model.tvalues["net_large_flow_norm"]
        pval = model.pvalues["net_large_flow_norm"]

        # 1 std sapmalik signal degisimi icin etki (bps)
        effect_bps = coef * signal_std * 10000
        net_effect_bps = effect_bps - TAKER_FEE_BPS

        results.append({
            "symbol": sym,
            "horizon": f"{h}h",
            "n": len(sub),
            "coef": coef,
            "tstat": tstat,
            "pval": pval,
            "effect_bps_1std": effect_bps,
            "net_effect_bps_1std": net_effect_bps,
        })
    return results


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("Institutional Size Classification Pilot")
    print(f"Semboller: {SYMBOLS}")
    print(f"Pencere  : {START_DATE} -> {END_DATE}")
    print(f"Buyuk islem esigi: ust %{(1-LARGE_TRADE_PCTL)*100:.0f}")
    print(f"Taker fee: {TAKER_FEE_BPS} bps round-trip")
    print("=" * 70)

    all_results = []
    total_obs = 0

    for sym in SYMBOLS:
        print(f"\n[{sym}] Veri yukleniyor...")
        raw = load_symbol(sym)
        if raw.empty:
            print(f"  UYARI: {sym} icin veri yok, atlanıyor")
            continue
        print(f"  {sym}: {len(raw):,} adet aggTrade yuklendi")

        panel = compute_hourly_panel(raw)
        panel = add_forward_returns(panel)
        total_obs += len(panel)
        print(f"  {sym}: {len(panel)} saatlik gozlem")

        sym_results = run_regressions(panel, sym)
        all_results.extend(sym_results)

    # ---------------------------------------------------------------------------
    # RAPOR
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("REGRESYON SONUCLARI")
    print(f"Toplam saatlik gozlem (tum semboller): ~{total_obs:,}")
    print(f"Model: fwd_return ~ net_large_flow_norm (sabit terimli OLS)")
    print(f"net_large_flow_norm = (buyuk_agresif_alim - buyuk_agresif_satim) / toplam_hacim")
    print("=" * 70)

    header = f"{'Sembol':<10} {'Horizon':<8} {'N':>7} {'Katsayi':>12} {'t-stat':>8} {'p-value':>9} {'Etki(bps/1std)':>16} {'NetEtki(bps)':>14}"
    print(header)
    print("-" * len(header))

    for r in all_results:
        print(
            f"{r['symbol']:<10} {r['horizon']:<8} {r['n']:>7,} "
            f"{r['coef']:>12.6f} {r['tstat']:>8.3f} {r['pval']:>9.4f} "
            f"{r['effect_bps_1std']:>16.2f} {r['net_effect_bps_1std']:>14.2f}"
        )

    print("=" * 70)
    print(f"Not: Etki = katsayi x signal_std x 10000. Net = Etki - {TAKER_FEE_BPS} bps.")


if __name__ == "__main__":
    main()
