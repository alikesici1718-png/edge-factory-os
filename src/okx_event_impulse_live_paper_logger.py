"""
Live paper logger for the event-impulse-long portfolio on OKX that polls 1-minute candles via
the OKX REST API, detects impulse-long signals from finalist strategies loaded from
robust_strict_best_by_coin.csv, and simulates paper trade entries and exits with backtest-delay
realism without placing real orders.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import requests


# =============================================================================
# Event Impulse Long Portfolio - OKX Live Paper Logger
# =============================================================================
#
# This script DOES NOT place real orders.
# It uses OKX public market candles only.
#
# Core behavior:
# - Load finalist strategies from robust_strict_best_by_coin.csv.
# - Poll OKX 1m candles.
# - Detect impulse-long signals on confirmed closed candles.
# - Respect backtest delay: signal -> pending entry -> entry after delay candle closes.
# - Apply execution filters at entry:
#     min entry vol_quote
#     max entry candle range
# - Maintain max portfolio open positions.
# - Track paper exits by fixed hold and optional stop loss.
# - Persist pending entries, open positions, closed trades, and event logs.
#
# Default coin set excludes lower-liquidity APE/ENJ at first.
# You can include them with --coins.
# =============================================================================


DEFAULT_CORE_COINS = [
    "MOODENG", "VIRTUAL", "ORDI", "H", "FIL",
    "ONT", "AXS", "ZK", "PIEVERSE", "PYTH",
]

FALLBACK_STRATEGIES = {
    "MOODENG": "MOODENG_robust_impulse_L3_move300_fixed_h240_d1_c25",
    "VIRTUAL": "VIRTUAL_robust_impulse_L3_move200_fixed_h360_d2_c25",
    "ORDI": "ORDI_robust_impulse_L5_move350_sl500_h480_d1_c25",
    "H": "H_robust_impulse_L5_move700_fixed_h360_d1_c25",
    "FIL": "FIL_robust_impulse_L3_move250_sl300_h360_d1_c25",
    "ONT": "ONT_robust_impulse_L3_move350_sl800_h240_d1_c25",
    "AXS": "AXS_robust_impulse_L3_move300_sl300_h360_d1_c25",
    "ZK": "ZK_robust_impulse_L10_move500_sl1000_h480_d2_c25",
    "PIEVERSE": "PIEVERSE_robust_impulse_L3_move450_sl300_h240_d1_c25",
    "PYTH": "PYTH_robust_impulse_L3_move300_fixed_h480_d1_c25",
    "APE": "APE_robust_impulse_L3_move200_sl300_h360_d2_c25",
    "ENJ": "ENJ_robust_impulse_L3_move150_fixed_h480_d1_c25",
}

OKX_CANDLES_URL = "https://www.okx.com/api/v5/market/candles"


@dataclass
class StrategyParams:
    coin: str
    inst_id: str
    strategy: str
    L: int
    move_bps: float
    sl_bps: Optional[float]
    hold: int
    delay: int
    cost_bps: float


def utc_now() -> pd.Timestamp:
    return pd.Timestamp.now(tz="UTC")


def safe_iso(ts) -> str:
    if pd.isna(ts):
        return ""
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_strategy(coin: str, strategy: str) -> StrategyParams:
    m = re.search(
        r"_L(?P<L>\d+)_move(?P<move>\d+)_(?P<exit>fixed|sl\d+)_h(?P<hold>\d+)_d(?P<delay>\d+)_c(?P<cost>[\d.]+)",
        strategy,
    )
    if not m:
        raise ValueError(f"Cannot parse strategy for {coin}: {strategy}")

    gd = m.groupdict()
    exit_name = gd["exit"]
    sl = None if exit_name == "fixed" else float(exit_name.replace("sl", ""))

    return StrategyParams(
        coin=coin,
        inst_id=f"{coin}-USDT-SWAP",
        strategy=strategy,
        L=int(gd["L"]),
        move_bps=float(gd["move"]),
        sl_bps=sl,
        hold=int(gd["hold"]),
        delay=int(gd["delay"]),
        cost_bps=float(gd["cost"]),
    )


def load_strategies(robust_dir: Path, coins: list[str], selection: str) -> dict[str, StrategyParams]:
    """
    selection:
    - strict => robust_strict_best_by_coin.csv, strategy column
    - cost   => robust_cost_best_by_coin.csv, strategy_25 column
    - fallback => hardcoded strategies
    """
    coins = [c.upper() for c in coins]
    out = {}

    if selection == "fallback":
        for coin in coins:
            if coin not in FALLBACK_STRATEGIES:
                raise ValueError(f"No fallback strategy for {coin}")
            out[coin] = parse_strategy(coin, FALLBACK_STRATEGIES[coin])
        return out

    if selection == "strict":
        path = robust_dir / "robust_strict_best_by_coin.csv"
        strategy_col = "strategy"
    elif selection == "cost":
        path = robust_dir / "robust_cost_best_by_coin.csv"
        strategy_col = "strategy_25"
    else:
        raise ValueError(selection)

    if not path.exists():
        print(f"[WARN] {path} not found; using fallback strategies")
        return load_strategies(robust_dir, coins, "fallback")

    df = pd.read_csv(path)
    df["coin"] = df["coin"].astype(str).str.upper()
    df = df[df["coin"].isin(coins)].copy()

    for _, row in df.iterrows():
        coin = str(row["coin"]).upper()
        if strategy_col not in row or pd.isna(row[strategy_col]):
            continue
        out[coin] = parse_strategy(coin, str(row[strategy_col]))

    missing = [c for c in coins if c not in out]
    if missing:
        print(f"[WARN] Missing strategies in {path.name}: {missing}; using fallback for missing")
        for coin in missing:
            if coin not in FALLBACK_STRATEGIES:
                raise ValueError(f"No strategy for {coin}")
            out[coin] = parse_strategy(coin, FALLBACK_STRATEGIES[coin])

    return out


def ensure_csv(path: Path, fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()


def append_csv(path: Path, row: dict, fields: list[str]) -> None:
    ensure_csv(path, fields)
    clean = {k: row.get(k, "") for k in fields}
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writerow(clean)


def read_table(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def write_table_atomic(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


def okx_fetch_candles(inst_id: str, limit: int, retries: int = 5, timeout: int = 20) -> pd.DataFrame:
    params = {
        "instId": inst_id,
        "bar": "1m",
        "limit": str(limit),
    }

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(OKX_CANDLES_URL, params=params, timeout=timeout)
            if r.status_code in {429, 500, 502, 503, 504}:
                wait = min(2 * attempt, 20)
                print(f"[WARN] {inst_id} HTTP {r.status_code}; sleep {wait}s")
                time.sleep(wait)
                continue
            r.raise_for_status()
            js = r.json()
            if js.get("code") != "0":
                raise RuntimeError(f"OKX code={js.get('code')} msg={js.get('msg')}")

            data = js.get("data", [])
            if not data:
                return pd.DataFrame()

            # OKX candles are usually newest first.
            cols = ["ts", "open", "high", "low", "close", "vol", "volCcy", "volCcyQuote", "confirm"]
            rows = []
            for row in data:
                if len(row) < 9:
                    continue
                rows.append(row[:9])

            df = pd.DataFrame(rows, columns=cols)
            for c in cols:
                df[c] = pd.to_numeric(df[c], errors="coerce")

            df["time"] = pd.to_datetime(df["ts"], unit="ms", utc=True, errors="coerce")
            df = (
                df.dropna(subset=["time", "open", "high", "low", "close"])
                .drop_duplicates("time")
                .sort_values("time")
                .reset_index(drop=True)
            )

            # Keep confirmed candles only for signal/entry/exit.
            df["confirm"] = pd.to_numeric(df["confirm"], errors="coerce").fillna(0).astype(int)
            return df

        except Exception as e:
            last_err = e
            wait = min(2 * attempt, 20)
            print(f"[WARN] {inst_id} candle fetch failed attempt {attempt}: {type(e).__name__}: {e}; sleep {wait}s")
            time.sleep(wait)

    raise RuntimeError(f"Failed to fetch candles for {inst_id}: {last_err}")


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    close = x["close"]
    x["ret1_bps"] = close.pct_change() * 10000.0
    for L in [3, 5, 10]:
        x[f"ret{L}_bps"] = (close / close.shift(L) - 1.0) * 10000.0
    x["range_bps"] = (x["high"] - x["low"]) / x["open"].replace(0, np.nan) * 10000.0
    return x


class PaperLogger:
    EVENT_FIELDS = [
        "event_time", "event_type", "coin", "inst_id", "strategy", "message",
        "signal_time", "target_entry_time", "entry_time", "exit_time",
        "price", "entry_price", "exit_price", "net_ret", "gross_ret",
        "vol_quote", "range_bps", "reason", "equity", "open_positions",
    ]

    PENDING_FIELDS = [
        "coin", "inst_id", "strategy", "signal_time", "target_entry_time",
        "L", "move_bps", "sl_bps", "hold", "delay", "cost_bps",
        "signal_close", "signal_retL_bps", "signal_ret1_bps", "signal_ret3_bps",
        "created_at",
    ]

    OPEN_FIELDS = [
        "coin", "inst_id", "strategy", "signal_time", "entry_time", "scheduled_exit_time",
        "entry_price", "stop_price", "L", "move_bps", "sl_bps", "hold", "delay", "cost_bps",
        "entry_vol_quote", "entry_range_bps", "notional", "equity_at_entry", "created_at",
        "last_checked_candle",
    ]

    CLOSED_FIELDS = [
        "coin", "inst_id", "strategy", "signal_time", "entry_time", "exit_time",
        "entry_price", "exit_price", "gross_ret", "net_ret", "reason",
        "sl_bps", "hold", "delay", "cost_bps", "entry_vol_quote", "entry_range_bps",
        "notional", "pnl", "equity_after_exit", "closed_at",
    ]

    HEARTBEAT_FIELDS = [
        "time", "equity", "open_positions", "pending_entries", "closed_trades",
        "loop_seconds", "message",
    ]

    SNAPSHOT_FIELDS = [
        "time", "coin", "inst_id", "last_candle_time", "close",
        "ret1_bps", "ret3_bps", "retL_bps", "L", "move_bps",
        "vol_quote", "range_bps", "signal_now", "status",
    ]

    def __init__(self, args, strategies: dict[str, StrategyParams]):
        self.args = args
        self.strategies = strategies
        self.out_dir = Path(args.out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.events_path = self.out_dir / "paper_events.csv"
        self.pending_path = self.out_dir / "pending_entries.csv"
        self.open_path = self.out_dir / "open_positions.csv"
        self.closed_path = self.out_dir / "closed_trades.csv"
        self.heartbeat_path = self.out_dir / "heartbeat.csv"
        self.snapshot_path = self.out_dir / "latest_snapshot.csv"
        self.config_path = self.out_dir / "config.json"

        self.equity = float(args.start_equity)

        self.pending = read_table(self.pending_path)
        self.open_positions = read_table(self.open_path)
        self.closed = read_table(self.closed_path)

        self._normalize_state_tables()

        if len(self.closed):
            # Rebuild equity from closed trades.
            try:
                self.equity = float(args.start_equity + pd.to_numeric(self.closed["pnl"], errors="coerce").fillna(0).sum())
            except Exception:
                pass

        self.last_signal_time: dict[str, pd.Timestamp] = {}
        self._load_last_signal_times()

        ensure_csv(self.events_path, self.EVENT_FIELDS)
        ensure_csv(self.heartbeat_path, self.HEARTBEAT_FIELDS)
        ensure_csv(self.closed_path, self.CLOSED_FIELDS)

        self._write_config()

    def _write_config(self) -> None:
        config = {
            "created_at": safe_iso(utc_now()),
            "coins": list(self.strategies.keys()),
            "strategies": {k: asdict(v) for k, v in self.strategies.items()},
            "args": vars(self.args),
            "note": "PUBLIC DATA PAPER LOGGER ONLY. DOES NOT SEND ORDERS.",
        }
        self.config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    def _normalize_state_tables(self) -> None:
        if self.pending.empty:
            self.pending = pd.DataFrame(columns=self.PENDING_FIELDS)
        if self.open_positions.empty:
            self.open_positions = pd.DataFrame(columns=self.OPEN_FIELDS)
        if self.closed.empty:
            self.closed = pd.DataFrame(columns=self.CLOSED_FIELDS)

        for col in self.PENDING_FIELDS:
            if col not in self.pending.columns:
                self.pending[col] = np.nan
        self.pending = self.pending[self.PENDING_FIELDS].copy()

        for col in self.OPEN_FIELDS:
            if col not in self.open_positions.columns:
                self.open_positions[col] = np.nan
        self.open_positions = self.open_positions[self.OPEN_FIELDS].copy()

        for col in self.CLOSED_FIELDS:
            if col not in self.closed.columns:
                self.closed[col] = np.nan
        self.closed = self.closed[self.CLOSED_FIELDS].copy()

    def _load_last_signal_times(self) -> None:
        candidates = []
        if len(self.pending):
            candidates.append(self.pending[["coin", "signal_time"]].copy())
        if len(self.open_positions):
            candidates.append(self.open_positions[["coin", "signal_time"]].copy())
        if len(self.closed):
            candidates.append(self.closed[["coin", "signal_time"]].copy())

        if not candidates:
            return

        all_sig = pd.concat(candidates, ignore_index=True)
        all_sig["signal_time"] = pd.to_datetime(all_sig["signal_time"], utc=True, errors="coerce")
        all_sig = all_sig.dropna(subset=["coin", "signal_time"])
        for coin, g in all_sig.groupby("coin"):
            self.last_signal_time[str(coin).upper()] = g["signal_time"].max()

    def log_event(self, event_type: str, coin: str = "", message: str = "", **kwargs) -> None:
        sp = self.strategies.get(coin)
        row = {
            "event_time": safe_iso(utc_now()),
            "event_type": event_type,
            "coin": coin,
            "inst_id": sp.inst_id if sp else kwargs.get("inst_id", ""),
            "strategy": sp.strategy if sp else kwargs.get("strategy", ""),
            "message": message,
            "equity": self.equity,
            "open_positions": len(self.open_positions),
        }
        row.update(kwargs)
        append_csv(self.events_path, row, self.EVENT_FIELDS)

    def save_state(self) -> None:
        write_table_atomic(self.pending_path, self.pending)
        write_table_atomic(self.open_path, self.open_positions)

    def has_coin_active(self, coin: str) -> bool:
        coin = coin.upper()
        if len(self.pending) and (self.pending["coin"].astype(str).str.upper() == coin).any():
            return True
        if len(self.open_positions) and (self.open_positions["coin"].astype(str).str.upper() == coin).any():
            return True
        return False

    def portfolio_open_count(self) -> int:
        return int(len(self.open_positions))

    def closed_candles(self, df: pd.DataFrame) -> pd.DataFrame:
        x = df[df["confirm"] == 1].copy()
        return x.sort_values("time").reset_index(drop=True)

    def process_coin(self, sp: StrategyParams) -> dict:
        df = okx_fetch_candles(sp.inst_id, limit=int(self.args.candle_limit))
        closed = self.closed_candles(df)

        if len(closed) < max(20, sp.L + 5):
            self.log_event("WARN", sp.coin, f"Not enough closed candles: {len(closed)}")
            return {"coin": sp.coin, "status": "not_enough_candles"}

        x = add_features(closed)
        last = x.iloc[-1]
        last_time = pd.Timestamp(last["time"])

        retL_col = f"ret{sp.L}_bps"
        retL = float(last.get(retL_col, np.nan))
        ret1 = float(last.get("ret1_bps", np.nan))
        ret3 = float(last.get("ret3_bps", np.nan))
        vol_quote = float(last.get("volCcyQuote", np.nan))
        range_bps = float(last.get("range_bps", np.nan))
        close_px = float(last["close"])

        signal_now = (
            np.isfinite(retL) and np.isfinite(ret1) and np.isfinite(ret3)
            and retL >= sp.move_bps
            and ret1 >= 0
            and ret3 >= 0
        )

        status = "no_signal"

        # Manage entries and exits first, using fresh candles.
        self.process_pending_for_coin(sp, x)
        self.process_open_for_coin(sp, x)

        # Signal creation after state processing.
        if signal_now:
            status = "signal_condition"

            last_seen = self.last_signal_time.get(sp.coin)
            if last_seen is not None and last_time <= last_seen:
                status = "duplicate_signal"
            elif self.has_coin_active(sp.coin):
                status = "coin_active_reject"
                self.log_event(
                    "SIGNAL_REJECT",
                    sp.coin,
                    "Signal rejected because coin already pending/open",
                    signal_time=safe_iso(last_time),
                    price=close_px,
                    vol_quote=vol_quote,
                    range_bps=range_bps,
                )
            elif self.portfolio_open_count() >= int(self.args.max_positions):
                status = "portfolio_full_reject"
                self.log_event(
                    "SIGNAL_REJECT",
                    sp.coin,
                    "Signal rejected because portfolio max_positions is full",
                    signal_time=safe_iso(last_time),
                    price=close_px,
                    vol_quote=vol_quote,
                    range_bps=range_bps,
                )
            else:
                target_entry_time = last_time + pd.Timedelta(minutes=sp.delay)
                row = {
                    "coin": sp.coin,
                    "inst_id": sp.inst_id,
                    "strategy": sp.strategy,
                    "signal_time": safe_iso(last_time),
                    "target_entry_time": safe_iso(target_entry_time),
                    "L": sp.L,
                    "move_bps": sp.move_bps,
                    "sl_bps": "" if sp.sl_bps is None else sp.sl_bps,
                    "hold": sp.hold,
                    "delay": sp.delay,
                    "cost_bps": sp.cost_bps,
                    "signal_close": close_px,
                    "signal_retL_bps": retL,
                    "signal_ret1_bps": ret1,
                    "signal_ret3_bps": ret3,
                    "created_at": safe_iso(utc_now()),
                }
                self.pending = pd.concat([self.pending, pd.DataFrame([row])], ignore_index=True)
                self.last_signal_time[sp.coin] = last_time
                self.save_state()
                status = "pending_created"
                self.log_event(
                    "SIGNAL_PENDING",
                    sp.coin,
                    "Signal accepted into pending-entry queue",
                    signal_time=safe_iso(last_time),
                    target_entry_time=safe_iso(target_entry_time),
                    price=close_px,
                    vol_quote=vol_quote,
                    range_bps=range_bps,
                )

        return {
            "time": safe_iso(utc_now()),
            "coin": sp.coin,
            "inst_id": sp.inst_id,
            "last_candle_time": safe_iso(last_time),
            "close": close_px,
            "ret1_bps": ret1,
            "ret3_bps": ret3,
            "retL_bps": retL,
            "L": sp.L,
            "move_bps": sp.move_bps,
            "vol_quote": vol_quote,
            "range_bps": range_bps,
            "signal_now": signal_now,
            "status": status,
        }

    def process_pending_for_coin(self, sp: StrategyParams, x: pd.DataFrame) -> None:
        if self.pending.empty:
            return

        p = self.pending.copy()
        p["coin_u"] = p["coin"].astype(str).str.upper()
        coin_mask = p["coin_u"] == sp.coin.upper()
        if not coin_mask.any():
            return

        pending_idx = p[coin_mask].index.tolist()
        remove_idx = []

        for idx in pending_idx:
            row = self.pending.loc[idx].to_dict()
            target_entry_time = pd.to_datetime(row["target_entry_time"], utc=True, errors="coerce")
            signal_time = pd.to_datetime(row["signal_time"], utc=True, errors="coerce")

            if pd.isna(target_entry_time):
                remove_idx.append(idx)
                self.log_event("PENDING_DROP", sp.coin, "Invalid target_entry_time", signal_time=row.get("signal_time", ""))
                continue

            # We need target entry candle to be closed and present.
            candidates = x[x["time"] >= target_entry_time]
            if candidates.empty:
                continue

            entry_candle = candidates.iloc[0]
            entry_time = pd.Timestamp(entry_candle["time"])

            if entry_time < target_entry_time:
                continue

            entry_price = float(entry_candle["close"])
            entry_vol_quote = float(entry_candle.get("volCcyQuote", np.nan))
            entry_range_bps = float(entry_candle.get("range_bps", np.nan))

            if self.portfolio_open_count() >= int(self.args.max_positions):
                remove_idx.append(idx)
                self.log_event(
                    "ENTRY_REJECT",
                    sp.coin,
                    "Pending entry rejected because portfolio max_positions is full",
                    signal_time=safe_iso(signal_time),
                    target_entry_time=safe_iso(target_entry_time),
                    entry_time=safe_iso(entry_time),
                    price=entry_price,
                    vol_quote=entry_vol_quote,
                    range_bps=entry_range_bps,
                    reason="max_positions",
                )
                continue

            if entry_vol_quote < float(self.args.min_entry_vol_quote):
                remove_idx.append(idx)
                self.log_event(
                    "ENTRY_REJECT",
                    sp.coin,
                    f"Entry rejected by min volume filter {self.args.min_entry_vol_quote}",
                    signal_time=safe_iso(signal_time),
                    target_entry_time=safe_iso(target_entry_time),
                    entry_time=safe_iso(entry_time),
                    price=entry_price,
                    vol_quote=entry_vol_quote,
                    range_bps=entry_range_bps,
                    reason="low_volume",
                )
                continue

            if entry_range_bps > float(self.args.max_entry_range_bps):
                remove_idx.append(idx)
                self.log_event(
                    "ENTRY_REJECT",
                    sp.coin,
                    f"Entry rejected by max range filter {self.args.max_entry_range_bps}",
                    signal_time=safe_iso(signal_time),
                    target_entry_time=safe_iso(target_entry_time),
                    entry_time=safe_iso(entry_time),
                    price=entry_price,
                    vol_quote=entry_vol_quote,
                    range_bps=entry_range_bps,
                    reason="wide_range",
                )
                continue

            scheduled_exit_time = entry_time + pd.Timedelta(minutes=sp.hold)
            stop_price = "" if sp.sl_bps is None else entry_price * (1.0 - float(sp.sl_bps) / 10000.0)
            notional = self.equity * float(self.args.paper_fraction)

            open_row = {
                "coin": sp.coin,
                "inst_id": sp.inst_id,
                "strategy": sp.strategy,
                "signal_time": safe_iso(signal_time),
                "entry_time": safe_iso(entry_time),
                "scheduled_exit_time": safe_iso(scheduled_exit_time),
                "entry_price": entry_price,
                "stop_price": stop_price,
                "L": sp.L,
                "move_bps": sp.move_bps,
                "sl_bps": "" if sp.sl_bps is None else sp.sl_bps,
                "hold": sp.hold,
                "delay": sp.delay,
                "cost_bps": sp.cost_bps,
                "entry_vol_quote": entry_vol_quote,
                "entry_range_bps": entry_range_bps,
                "notional": notional,
                "equity_at_entry": self.equity,
                "created_at": safe_iso(utc_now()),
                "last_checked_candle": safe_iso(entry_time),
            }
            self.open_positions = pd.concat([self.open_positions, pd.DataFrame([open_row])], ignore_index=True)
            remove_idx.append(idx)

            self.log_event(
                "ENTRY_OPEN",
                sp.coin,
                "Paper position opened",
                signal_time=safe_iso(signal_time),
                target_entry_time=safe_iso(target_entry_time),
                entry_time=safe_iso(entry_time),
                price=entry_price,
                entry_price=entry_price,
                vol_quote=entry_vol_quote,
                range_bps=entry_range_bps,
                reason="entry",
            )

        if remove_idx:
            self.pending = self.pending.drop(index=remove_idx).reset_index(drop=True)
            self.save_state()

    def process_open_for_coin(self, sp: StrategyParams, x: pd.DataFrame) -> None:
        if self.open_positions.empty:
            return

        op = self.open_positions.copy()
        op["coin_u"] = op["coin"].astype(str).str.upper()
        coin_mask = op["coin_u"] == sp.coin.upper()
        if not coin_mask.any():
            return

        open_idx = op[coin_mask].index.tolist()
        remove_idx = []

        for idx in open_idx:
            row = self.open_positions.loc[idx].to_dict()
            entry_time = pd.to_datetime(row["entry_time"], utc=True, errors="coerce")
            scheduled_exit_time = pd.to_datetime(row["scheduled_exit_time"], utc=True, errors="coerce")
            last_checked = pd.to_datetime(row.get("last_checked_candle", ""), utc=True, errors="coerce")

            entry_price = float(row["entry_price"])
            notional = float(row["notional"])
            cost_bps = float(row["cost_bps"])
            stop_raw = row.get("stop_price", "")
            stop_price = None
            try:
                if str(stop_raw).strip() != "":
                    stop_price = float(stop_raw)
            except Exception:
                stop_price = None

            if pd.isna(entry_time) or pd.isna(scheduled_exit_time):
                continue

            # Use candles after last checked if possible. This prevents repeat stop checks.
            check_start = entry_time
            if pd.notna(last_checked):
                check_start = max(entry_time, last_checked)

            candles = x[x["time"] > check_start].copy()
            if candles.empty:
                continue

            exit_reason = None
            exit_time = None
            exit_price = None

            for _, c in candles.iterrows():
                c_time = pd.Timestamp(c["time"])

                # Stop first.
                if stop_price is not None and float(c["low"]) <= stop_price:
                    exit_reason = "stop"
                    exit_time = c_time
                    exit_price = stop_price
                    break

                # Scheduled hold exit.
                if c_time >= scheduled_exit_time:
                    exit_reason = "time"
                    exit_time = c_time
                    exit_price = float(c["close"])
                    break

            # Update last checked if still open.
            if exit_reason is None:
                latest_time = pd.Timestamp(candles["time"].max())
                self.open_positions.loc[idx, "last_checked_candle"] = safe_iso(latest_time)
                continue

            gross_ret = float(exit_price) / entry_price - 1.0
            net_ret = gross_ret - cost_bps / 10000.0
            pnl = notional * net_ret
            self.equity += pnl

            closed_row = {
                "coin": sp.coin,
                "inst_id": sp.inst_id,
                "strategy": sp.strategy,
                "signal_time": row.get("signal_time", ""),
                "entry_time": safe_iso(entry_time),
                "exit_time": safe_iso(exit_time),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "reason": exit_reason,
                "sl_bps": row.get("sl_bps", ""),
                "hold": row.get("hold", ""),
                "delay": row.get("delay", ""),
                "cost_bps": cost_bps,
                "entry_vol_quote": row.get("entry_vol_quote", ""),
                "entry_range_bps": row.get("entry_range_bps", ""),
                "notional": notional,
                "pnl": pnl,
                "equity_after_exit": self.equity,
                "closed_at": safe_iso(utc_now()),
            }

            append_csv(self.closed_path, closed_row, self.CLOSED_FIELDS)
            remove_idx.append(idx)

            self.log_event(
                "EXIT_CLOSE",
                sp.coin,
                f"Paper position closed by {exit_reason}",
                signal_time=row.get("signal_time", ""),
                entry_time=safe_iso(entry_time),
                exit_time=safe_iso(exit_time),
                price=exit_price,
                entry_price=entry_price,
                exit_price=exit_price,
                gross_ret=gross_ret,
                net_ret=net_ret,
                reason=exit_reason,
            )

        if remove_idx:
            self.open_positions = self.open_positions.drop(index=remove_idx).reset_index(drop=True)
            self.save_state()

    def heartbeat(self, loop_seconds: float, message: str = "") -> None:
        closed_count = 0
        if self.closed_path.exists():
            try:
                closed_count = max(0, len(pd.read_csv(self.closed_path)))
            except Exception:
                closed_count = 0

        row = {
            "time": safe_iso(utc_now()),
            "equity": self.equity,
            "open_positions": len(self.open_positions),
            "pending_entries": len(self.pending),
            "closed_trades": closed_count,
            "loop_seconds": loop_seconds,
            "message": message,
        }
        append_csv(self.heartbeat_path, row, self.HEARTBEAT_FIELDS)

    def run_once(self) -> None:
        t0 = time.time()
        snapshots = []

        for coin, sp in self.strategies.items():
            try:
                snap = self.process_coin(sp)
                snapshots.append(snap)
                print(
                    f"[{safe_iso(utc_now())}] {coin:<9} "
                    f"status={snap.get('status')} "
                    f"last={snap.get('last_candle_time')} "
                    f"retL={snap.get('retL_bps', np.nan):.1f} "
                    f"move={snap.get('move_bps')} "
                    f"open={len(self.open_positions)} pending={len(self.pending)} equity={self.equity:.2f}"
                )
            except Exception as e:
                msg = f"{type(e).__name__}: {e}"
                print(f"[ERROR] {coin}: {msg}")
                self.log_event("ERROR", coin, msg)

            time.sleep(float(self.args.per_coin_sleep_sec))

        if snapshots:
            df = pd.DataFrame(snapshots)
            for col in self.SNAPSHOT_FIELDS:
                if col not in df.columns:
                    df[col] = ""
            write_table_atomic(self.snapshot_path, df[self.SNAPSHOT_FIELDS])

        self.save_state()
        self.heartbeat(time.time() - t0, "loop_done")

    def run_forever(self) -> None:
        print("=" * 100)
        print("EVENT IMPULSE LONG PORTFOLIO - LIVE PAPER LOGGER")
        print("NO REAL ORDERS. PUBLIC OKX CANDLES ONLY.")
        print("out:", self.out_dir)
        print("coins:", ",".join(self.strategies.keys()))
        print("max_positions:", self.args.max_positions)
        print("paper_fraction:", self.args.paper_fraction)
        print("min_entry_vol_quote:", self.args.min_entry_vol_quote)
        print("max_entry_range_bps:", self.args.max_entry_range_bps)
        print("=" * 100)

        while True:
            loop_start = time.time()
            try:
                self.run_once()
            except KeyboardInterrupt:
                print("\nStopped by user.")
                self.heartbeat(time.time() - loop_start, "stopped_by_user")
                break
            except Exception as e:
                print(f"[LOOP ERROR] {type(e).__name__}: {e}")
                self.log_event("LOOP_ERROR", "", f"{type(e).__name__}: {e}")
                self.heartbeat(time.time() - loop_start, "loop_error")

            sleep_left = max(1.0, float(self.args.loop_sleep_sec) - (time.time() - loop_start))
            print(f"[SLEEP] {sleep_left:.1f}s\n")
            time.sleep(sleep_left)


def main() -> None:
    ap = argparse.ArgumentParser(description="OKX event impulse long live paper logger. Public data only; no real orders.")
    ap.add_argument("--robust_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\finalist_impulse_robustness")
    ap.add_argument("--out_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\live_event_impulse_paper")
    ap.add_argument("--coins", default=",".join(DEFAULT_CORE_COINS))
    ap.add_argument("--selection", choices=["strict", "cost", "fallback"], default="strict")
    ap.add_argument("--max_positions", type=int, default=3)
    ap.add_argument("--paper_fraction", type=float, default=0.05)
    ap.add_argument("--start_equity", type=float, default=1000.0)
    ap.add_argument("--min_entry_vol_quote", type=float, default=100000.0)
    ap.add_argument("--max_entry_range_bps", type=float, default=1000.0)
    ap.add_argument("--candle_limit", type=int, default=300)
    ap.add_argument("--loop_sleep_sec", type=float, default=60.0)
    ap.add_argument("--per_coin_sleep_sec", type=float, default=0.15)
    ap.add_argument("--once", action="store_true", help="Run one polling loop and exit.")

    args = ap.parse_args()

    coins = [c.strip().upper() for c in args.coins.split(",") if c.strip()]
    strategies = load_strategies(Path(args.robust_dir), coins, args.selection)

    logger = PaperLogger(args, strategies)

    if args.once:
        logger.run_once()
    else:
        logger.run_forever()


if __name__ == "__main__":
    main()

