#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scans local 1-minute candle CSV files for the ret60_reversal_short candidate (hour-8 UTC, signal_ret60_bps >= 75, 1-minute delay, 720-minute hold) and replays hypothetical trades using an as-of merge, producing a native events CSV with simulated PnL.
Outputs a stamped directory containing the replay CSV and a JSON state file, with live and active-paper trading explicitly blocked.
"""
from __future__ import annotations

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "ret60_reversal_short"
SYMBOL_RE = re.compile(r"([A-Z0-9]{1,25}-USDT-SWAP)")

HOUR_UTC = 8
M_PARAM = 75.0
DELAY_MINUTES = 1
HOLD_MINUTES = 720
NOTIONAL = 50.0
FEE_BPS = 5.0
SPREAD_BPS = 2.0
SLIPPAGE_BPS = 3.0
EXTRA_SLIP_BPS = 0.0

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def infer_symbol(path: Path) -> Optional[str]:
    m = SYMBOL_RE.search(str(path).upper().replace("\\", "/"))
    return m.group(1) if m else None

def robust_time_parse(s: pd.Series) -> pd.Series:
    num = pd.to_numeric(s, errors="coerce")
    if len(num) and num.notna().mean() >= 0.80:
        med = float(num.dropna().median())
        if med > 1e17:
            return pd.to_datetime(num, unit="ns", errors="coerce", utc=True)
        if med > 1e14:
            return pd.to_datetime(num, unit="us", errors="coerce", utc=True)
        if med > 1e11:
            return pd.to_datetime(num, unit="ms", errors="coerce", utc=True)
        if med > 1e8:
            return pd.to_datetime(num, unit="s", errors="coerce", utc=True)
    return pd.to_datetime(s, errors="coerce", utc=True)

def read_candle_file(path: Path, max_rows_per_file: int) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(path)
        if len(df.columns) < 5:
            df2 = pd.read_csv(path, header=None)
            if len(df2.columns) >= 5:
                df = df2
    except Exception:
        return None

    cols = list(df.columns)

    if len(cols) >= 5 and all(str(c).isdigit() for c in cols[:5]):
        time_col = cols[0]
        close_col = cols[4]
    else:
        lower = {str(c).lower(): c for c in cols}
        time_col = lower.get("event_time") or lower.get("timestamp") or lower.get("time") or lower.get("open_time") or cols[0]
        close_col = lower.get("close") or lower.get("c") or lower.get("close_price") or cols[4]

    symbol = infer_symbol(path)
    if not symbol:
        return None

    out = pd.DataFrame()
    out["event_time"] = robust_time_parse(df[time_col])
    out["close"] = pd.to_numeric(df[close_col], errors="coerce")
    out["symbol"] = symbol
    out = out.dropna(subset=["event_time", "close"])
    out = out[out["close"] > 0]
    out = out.sort_values("event_time").drop_duplicates(subset=["event_time"]).reset_index(drop=True)

    if len(out) > max_rows_per_file:
        out = out.tail(max_rows_per_file)

    return out if len(out) >= 1000 else None

def find_files(max_files: int):
    files = []
    for p in WORKSPACE.rglob("*.csv"):
        s = str(p).lower()
        if ("raw\\candles_long_1m" in s or "raw/candles_long_1m" in s) and infer_symbol(p):
            files.append(p)
    return sorted(files)[:max_files]

def replay_symbol(g: pd.DataFrame) -> pd.DataFrame:
    g = g.sort_values("event_time").reset_index(drop=True)

    events = g[g["event_time"].dt.hour == HOUR_UTC][["symbol", "event_time", "close"]].copy()
    if events.empty:
        return pd.DataFrame()

    full = g[["event_time", "close"]].copy().sort_values("event_time")
    full_prior = full.rename(columns={"event_time": "prior_time", "close": "prior_close"})
    full_entry = full.rename(columns={"event_time": "entry_time_match", "close": "entry_reference_price"})
    full_exit = full.rename(columns={"event_time": "exit_time_match", "close": "exit_reference_price"})

    events["target_prior_time"] = events["event_time"] - pd.Timedelta(minutes=60)
    events["planned_entry_time"] = events["event_time"] + pd.Timedelta(minutes=DELAY_MINUTES)
    events["planned_exit_time"] = events["planned_entry_time"] + pd.Timedelta(minutes=HOLD_MINUTES)

    x = pd.merge_asof(
        events.sort_values("target_prior_time"),
        full_prior.sort_values("prior_time"),
        left_on="target_prior_time",
        right_on="prior_time",
        direction="backward",
        tolerance=pd.Timedelta(seconds=90),
    )

    x = x.dropna(subset=["prior_close"])
    if x.empty:
        return pd.DataFrame()

    x["signal_ret60_bps"] = (x["close"] / x["prior_close"] - 1.0) * 10000.0
    x = x[x["signal_ret60_bps"] >= M_PARAM].copy()
    if x.empty:
        return pd.DataFrame()

    x = pd.merge_asof(
        x.sort_values("planned_entry_time"),
        full_entry.sort_values("entry_time_match"),
        left_on="planned_entry_time",
        right_on="entry_time_match",
        direction="backward",
        tolerance=pd.Timedelta(seconds=90),
    )

    x = pd.merge_asof(
        x.sort_values("planned_exit_time"),
        full_exit.sort_values("exit_time_match"),
        left_on="planned_exit_time",
        right_on="exit_time_match",
        direction="backward",
        tolerance=pd.Timedelta(seconds=90),
    )

    x = x.dropna(subset=["entry_reference_price", "exit_reference_price"])
    if x.empty:
        return pd.DataFrame()

    x["gross_return_bps_native"] = (x["entry_reference_price"] / x["exit_reference_price"] - 1.0) * 10000.0
    x["net_return_bps_native"] = x["gross_return_bps_native"] - FEE_BPS - SPREAD_BPS - SLIPPAGE_BPS - EXTRA_SLIP_BPS
    x["gross_pnl_usdt"] = NOTIONAL * x["gross_return_bps_native"] / 10000.0
    x["net_pnl_usdt"] = NOTIONAL * x["net_return_bps_native"] / 10000.0

    out = pd.DataFrame()
    out["event_id"] = x["symbol"].astype(str) + "_" + x["event_time"].astype(str)
    out["candidate_key"] = CANDIDATE
    out["engine_version"] = "ret60_market_replay_v4_merge_asof"
    out["symbol"] = x["symbol"]
    out["side"] = "short"
    out["signal_time_utc"] = x["event_time"].astype(str)
    out["hour_utc"] = HOUR_UTC
    out["signal_ret60_bps"] = x["signal_ret60_bps"]
    out["ret60_rule_passed"] = True
    out["delay_minutes"] = DELAY_MINUTES
    out["planned_entry_time_utc"] = x["planned_entry_time"].astype(str)
    out["actual_paper_entry_time_utc"] = x["entry_time_match"].astype(str)
    out["entry_reference_price"] = x["entry_reference_price"]
    out["hold_minutes"] = HOLD_MINUTES
    out["planned_exit_time_utc"] = x["planned_exit_time"].astype(str)
    out["actual_paper_exit_time_utc"] = x["exit_time_match"].astype(str)
    out["exit_reference_price"] = x["exit_reference_price"]
    out["gross_return_bps_native"] = x["gross_return_bps_native"]
    out["fee_bps_assumption"] = FEE_BPS
    out["spread_bps_at_signal"] = SPREAD_BPS
    out["slippage_bps_assumption"] = SLIPPAGE_BPS
    out["extra_slip_bps"] = EXTRA_SLIP_BPS
    out["net_return_bps_native"] = x["net_return_bps_native"]
    out["gross_pnl_usdt"] = x["gross_pnl_usdt"]
    out["net_pnl_usdt"] = x["net_pnl_usdt"]
    out["notional_usdt"] = NOTIONAL
    out["source_candle_basis"] = "real_local_candles_long_1m_merge_asof"
    out["feature_calculation_version"] = "ret60_merge_asof_v4"
    out["logger_version"] = "ret60_market_replay_v4_merge_asof"
    out["runtime_mode"] = "local_market_candle_replay_merge_asof"
    out["status"] = "CLOSED"

    return out

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--max_files", type=int, default=120)
    ap.add_argument("--max_rows_per_file", type=int, default=50000)
    args = ap.parse_args()

    out_dir = WORKSPACE / "edge_factory_ret60_market_replay_v4_merge_asof" / f"ret60_market_replay_v4_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_trades = []
    audits = []

    files = find_files(args.max_files)

    for p in files:
        g = read_candle_file(p, args.max_rows_per_file)
        if g is None:
            audits.append({"path": str(p), "used": False, "reason": "unreadable/too few rows"})
            continue

        trades = replay_symbol(g)
        audits.append({
            "path": str(p),
            "used": True,
            "symbol": infer_symbol(p),
            "rows": len(g),
            "first_time": str(g["event_time"].min()),
            "last_time": str(g["event_time"].max()),
            "trades": len(trades),
        })

        if not trades.empty:
            all_trades.append(trades)

    if all_trades:
        result = pd.concat(all_trades, ignore_index=True)
    else:
        result = pd.DataFrame()

    native_csv = out_dir / "ret60_shadow_native_events.csv"
    closed_csv = out_dir / "ret60_shadow_closed_trades.csv"

    if not result.empty:
        result.to_csv(native_csv, index=False)
        result.to_csv(closed_csv, index=False)

    summary = {
        "candidate": CANDIDATE,
        "status": "RET60_MARKET_REPLAY_V4_EXECUTED_WITH_SIGNALS" if len(result) else "RET60_MARKET_REPLAY_V4_EXECUTED_NO_SIGNALS",
        "output_dir": str(out_dir),
        "files_checked": len(files),
        "files_used": sum(1 for a in audits if a.get("used")),
        "trade_count": int(len(result)),
        "symbol_count": int(result["symbol"].nunique()) if len(result) else 0,
        "native_csv": str(native_csv),
        "closed_csv": str(closed_csv),
        "net_pnl_sum": float(result["net_pnl_usdt"].sum()) if len(result) else 0.0,
        "net_bps_mean": float(result["net_return_bps_native"].mean()) if len(result) else 0.0,
        "win_rate": float((result["net_pnl_usdt"] > 0).mean()) if len(result) else 0.0,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "RUN_MARKET_REPLAY_DRIFT_MONITOR_V4" if len(result) else "RET60_WATCHLIST_OR_REJECT_NO_SIGNALS",
    }

    (out_dir / "ret60_market_replay_v4_state.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame(audits).to_csv(out_dir / "ret60_market_replay_v4_file_audit.csv", index=False)

    print("EDGE FACTORY RET60 MARKET REPLAY v4 MERGE_ASOF")
    print("=" * 100)
    print(f"output_dir: {out_dir}")
    print(f"status: {summary['status']}")
    print(f"files_checked: {summary['files_checked']}")
    print(f"files_used: {summary['files_used']}")
    print(f"trade_count: {summary['trade_count']}")
    print(f"symbol_count: {summary['symbol_count']}")
    print(f"net_pnl_sum: {summary['net_pnl_sum']}")
    print(f"net_bps_mean: {summary['net_bps_mean']}")
    print(f"win_rate: {summary['win_rate']}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print(f"State: {out_dir / 'ret60_market_replay_v4_state.json'}")
    print(f"Native: {native_csv}")
    print(f"Closed: {closed_csv}")
    print(f"Audit: {out_dir / 'ret60_market_replay_v4_file_audit.csv'}")

if __name__ == "__main__":
    main()
