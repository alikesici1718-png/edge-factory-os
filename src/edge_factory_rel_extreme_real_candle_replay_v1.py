#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

import numpy as np
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "rel_extreme_reversion_short"
SYMBOL_RE = re.compile(r"([A-Z0-9]{1,25})-USDT-SWAP", re.I)

LOOKBACK_HOURS = 6
COIN_THRESHOLD_BPS = 300.0
REL_THRESHOLD_BPS = 600.0
HOLD_HOURS = 24
COST_BPS = 25.0
SIDE = "short"

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

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

def find_candle_files(max_files: Optional[int]) -> list[Path]:
    files = []
    for p in WORKSPACE.rglob("*.csv"):
        s = str(p).lower()
        if ("raw\\candles_long_1m" in s or "raw/candles_long_1m" in s) and infer_symbol(p):
            files.append(p)
    files = sorted(files)
    if max_files:
        files = files[:max_files]
    return files

def read_hourly_close(path: Path, max_rows_per_file: Optional[int]) -> Optional[pd.Series]:
    symbol = infer_symbol(path)
    if not symbol:
        return None

    try:
        df = pd.read_csv(path)
        if len(df.columns) < 5:
            df2 = pd.read_csv(path, header=None)
            if len(df2.columns) >= 5:
                df = df2
    except Exception:
        return None

    if max_rows_per_file and len(df) > max_rows_per_file:
        df = df.tail(max_rows_per_file).copy()

    cols = list(df.columns)

    if len(cols) >= 5 and all(str(c).isdigit() for c in cols[:5]):
        time_col = cols[0]
        close_col = cols[4]
    else:
        lower = {str(c).lower(): c for c in cols}
        time_col = lower.get("event_time") or lower.get("timestamp") or lower.get("time") or lower.get("open_time") or cols[0]
        close_col = lower.get("close") or lower.get("c") or lower.get("close_price") or cols[4]

    tmp = pd.DataFrame()
    tmp["time"] = robust_time_parse(df[time_col])
    tmp["close"] = pd.to_numeric(df[close_col], errors="coerce")
    tmp = tmp.dropna(subset=["time", "close"])
    tmp = tmp[tmp["close"] > 0].copy()

    if len(tmp) < 1000:
        return None

    tmp["hour"] = tmp["time"].dt.floor("h")
    hourly = tmp.sort_values("time").groupby("hour")["close"].last()
    hourly.name = symbol

    if len(hourly) < LOOKBACK_HOURS + HOLD_HOURS + 10:
        return None

    return hourly

def profit_factor(x: pd.Series) -> float:
    y = pd.to_numeric(x, errors="coerce").dropna()
    if y.empty:
        return 0.0
    wins = y[y > 0].sum()
    losses = -y[y < 0].sum()
    if losses <= 0:
        return 999999.0 if wins > 0 else 0.0
    return float(wins / losses)

def max_drawdown_proxy(x: pd.Series) -> float:
    y = pd.to_numeric(x, errors="coerce").fillna(0.0)
    eq = y.cumsum()
    dd = eq - eq.cummax()
    return float(dd.min()) if len(dd) else 0.0

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--max_files", type=int, default=0, help="0 = all files")
    ap.add_argument("--max_rows_per_file", type=int, default=0, help="0 = all rows")
    ap.add_argument("--market_method", choices=["median", "mean"], default="median")
    ap.add_argument("--dry_run", action="store_true")
    args = ap.parse_args()

    out_dir = WORKSPACE / "edge_factory_rel_extreme_real_candle_replay_v1" / f"rel_extreme_real_replay_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_exact_rule_contract_v1", "rel_extreme_rule_contract_")
    contract_path = contract_dir / "rel_extreme_rule_contract.json" if contract_dir else None
    contract = read_json(contract_path)

    if contract.get("contract_status") != "REL_EXTREME_RULE_CONTRACT_CONFIRMED_FOR_MARKET_REPLAY":
        raise SystemExit("rel_extreme rule contract not confirmed; run exact rule contract first")

    max_files = None if args.max_files == 0 else args.max_files
    max_rows = None if args.max_rows_per_file == 0 else args.max_rows_per_file

    files = find_candle_files(max_files=max_files)

    series = []
    audit_rows = []

    for p in files:
        sym = infer_symbol(p)
        s = read_hourly_close(p, max_rows)
        if s is None:
            audit_rows.append({
                "path": str(p),
                "symbol": sym,
                "used": False,
                "reason": "unreadable_or_too_few_hourly_rows",
            })
            continue

        series.append(s)
        audit_rows.append({
            "path": str(p),
            "symbol": sym,
            "used": True,
            "hourly_rows": int(len(s)),
            "first_hour": str(s.index.min()),
            "last_hour": str(s.index.max()),
        })

    audit_df = pd.DataFrame(audit_rows)
    audit_df.to_csv(out_dir / "rel_extreme_real_candle_file_audit.csv", index=False)

    if not series:
        raise SystemExit("no usable candle files")

    close = pd.concat(series, axis=1, sort=True).sort_index()
    close = close.dropna(axis=1, how="all")

    # Multiple candle files may resolve to the same symbol column.
    # If duplicate symbol columns exist, collapse them into one symbol using the latest non-null value.
    if close.columns.duplicated().any():
        close = close.T.groupby(level=0).last().T
        close = close.sort_index()

    coin_ret = (close / close.shift(LOOKBACK_HOURS) - 1.0) * 10000.0

    if args.market_method == "median":
        market_ret = coin_ret.median(axis=1, skipna=True)
    else:
        market_ret = coin_ret.mean(axis=1, skipna=True)

    rel_ret = coin_ret.sub(market_ret, axis=0)

    # Entry is at signal hour close. Exit is +24h close.
    exit_close = close.shift(-HOLD_HOURS)

    # Short return in bps:
    gross_bps = (close / exit_close - 1.0) * 10000.0
    net_bps = gross_bps - COST_BPS

    signal_mask = (coin_ret >= COIN_THRESHOLD_BPS) & (rel_ret >= REL_THRESHOLD_BPS)

    records = []
    for sym in signal_mask.columns:
        mask_obj = signal_mask[sym]

        # Safety: if duplicate columns somehow survived, reduce DataFrame mask to row-wise any.
        if isinstance(mask_obj, pd.DataFrame):
            mask_series = mask_obj.fillna(False).any(axis=1)
        else:
            mask_series = mask_obj.fillna(False)

        idx = signal_mask.index[mask_series.astype(bool)]
        if len(idx) == 0:
            continue

        tmp = pd.DataFrame({
            "candidate": CANDIDATE,
            "variant_key": contract.get("variant_key"),
            "symbol": sym,
            "side": SIDE,
            "signal_time": idx,
            "entry_time": idx,
            "exit_time": idx + pd.Timedelta(hours=HOLD_HOURS),
            "entry_close": close.loc[idx, sym].values,
            "exit_close": exit_close.loc[idx, sym].values,
            "coin_ret6_bps": coin_ret.loc[idx, sym].values,
            "market_ret6_bps": market_ret.loc[idx].values,
            "rel_ret_bps": rel_ret.loc[idx, sym].values,
            "gross_return_bps": gross_bps.loc[idx, sym].values,
            "cost_bps": COST_BPS,
            "net_return_bps": net_bps.loc[idx, sym].values,
        })

        records.append(tmp)

    if records:
        trades = pd.concat(records, ignore_index=True)
    else:
        trades = pd.DataFrame()

    if not trades.empty:
        trades = trades.dropna(subset=["entry_close", "exit_close", "net_return_bps"]).copy()
        trades["gross_return_pct"] = trades["gross_return_bps"] / 100.0
        trades["net_return_pct"] = trades["net_return_bps"] / 100.0
        trades["net_pnl_usdt_50_notional"] = 50.0 * trades["net_return_bps"] / 10000.0
        trades = trades.sort_values(["signal_time", "symbol"]).reset_index(drop=True)

    trades_path = out_dir / "rel_extreme_real_candle_replay_trades.csv"
    if not trades.empty:
        trades.to_csv(trades_path, index=False)

    by_symbol = pd.DataFrame()
    by_month = pd.DataFrame()

    if not trades.empty:
        by_symbol = (
            trades.groupby("symbol")
            .agg(
                trades=("net_return_bps", "count"),
                net_bps_sum=("net_return_bps", "sum"),
                net_bps_mean=("net_return_bps", "mean"),
                win_rate=("net_return_bps", lambda x: float((x > 0).mean())),
                pf=("net_return_bps", profit_factor),
            )
            .reset_index()
            .sort_values("net_bps_sum", ascending=False)
        )
        by_symbol.to_csv(out_dir / "rel_extreme_real_candle_replay_by_symbol.csv", index=False)

        t = trades.copy()
        t["month"] = pd.to_datetime(t["signal_time"], utc=True).dt.to_period("M").astype(str)
        by_month = (
            t.groupby("month")
            .agg(
                trades=("net_return_bps", "count"),
                net_bps_sum=("net_return_bps", "sum"),
                net_bps_mean=("net_return_bps", "mean"),
                win_rate=("net_return_bps", lambda x: float((x > 0).mean())),
                pf=("net_return_bps", profit_factor),
            )
            .reset_index()
            .sort_values("month")
        )
        by_month.to_csv(out_dir / "rel_extreme_real_candle_replay_by_month.csv", index=False)

    trade_count = int(len(trades))
    symbol_count = int(trades["symbol"].nunique()) if trade_count else 0
    net_bps_sum = float(trades["net_return_bps"].sum()) if trade_count else 0.0
    net_bps_mean = float(trades["net_return_bps"].mean()) if trade_count else 0.0
    win_rate = float((trades["net_return_bps"] > 0).mean()) if trade_count else 0.0
    pf = profit_factor(trades["net_return_bps"]) if trade_count else 0.0
    dd_proxy = max_drawdown_proxy(trades["net_return_bps"]) if trade_count else 0.0

    if trade_count == 0:
        status = "REL_EXTREME_REAL_REPLAY_NO_SIGNALS"
        next_action = "REJECT_OR_REWORK_RULE"
    elif net_bps_sum <= 0 or pf < 1.05:
        status = "REL_EXTREME_REAL_REPLAY_FAIL_NEGATIVE_OR_WEAK"
        next_action = "REJECT_OR_WATCHLIST"
    elif symbol_count < 20:
        status = "REL_EXTREME_REAL_REPLAY_WEAK_SYMBOL_BREADTH"
        next_action = "WATCHLIST_NEEDS_BREADTH_REVIEW"
    else:
        status = "REL_EXTREME_REAL_REPLAY_PASS_FOR_OOS_REVIEW"
        next_action = "RUN_TIME_OOS_AND_ROBUSTNESS_GATES"

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "contract_path": str(contract_path),
        "output_dir": str(out_dir),
        "status": status,
        "market_method": args.market_method,
        "files_scanned": len(files),
        "files_used": int(audit_df["used"].sum()) if len(audit_df) else 0,
        "close_shape_rows": int(close.shape[0]),
        "close_shape_symbols": int(close.shape[1]),
        "trade_count": trade_count,
        "symbol_count": symbol_count,
        "net_bps_sum": net_bps_sum,
        "net_bps_mean": net_bps_mean,
        "win_rate": win_rate,
        "profit_factor": pf,
        "drawdown_proxy_bps": dd_proxy,
        "trades_csv": str(trades_path),
        "by_symbol_csv": str(out_dir / "rel_extreme_real_candle_replay_by_symbol.csv"),
        "by_month_csv": str(out_dir / "rel_extreme_real_candle_replay_by_month.csv"),
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": next_action,
        "warnings": [
            "This is independent real local candle replay, not paper/live permission.",
            "Market return is reconstructed as cross-sectional median/mean from available hourly returns.",
            "Any pass still requires time-OOS, robustness, and shadow/paper gates.",
        ],
    }

    write_json(out_dir / "rel_extreme_real_candle_replay_state.json", state)

    print("EDGE FACTORY REL EXTREME REAL CANDLE REPLAY v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"status: {status}")
    print(f"market_method: {args.market_method}")
    print(f"files_scanned: {len(files)}")
    print(f"files_used: {state['files_used']}")
    print(f"close_shape: {close.shape[0]} hours x {close.shape[1]} symbols")
    print(f"trade_count: {trade_count}")
    print(f"symbol_count: {symbol_count}")
    print(f"net_bps_sum: {net_bps_sum}")
    print(f"net_bps_mean: {net_bps_mean}")
    print(f"win_rate: {win_rate}")
    print(f"profit_factor: {pf}")
    print(f"drawdown_proxy_bps: {dd_proxy}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    if not trades.empty:
        print("TOP SYMBOLS")
        print("-" * 100)
        print(by_symbol.head(20).to_string(index=False))
        print()
        print("MONTHLY")
        print("-" * 100)
        print(by_month.to_string(index=False))
        print()
    print(f"State  : {out_dir / 'rel_extreme_real_candle_replay_state.json'}")
    print(f"Trades : {trades_path}")
    print(f"Audit  : {out_dir / 'rel_extreme_real_candle_file_audit.csv'}")

if __name__ == "__main__":
    main()
