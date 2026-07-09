"""
Live paper logger for the impulse/event-long strategy family that polls OKX 1-minute candles,
detects impulse-long signals based on finalist strategies from robust_strict_best_by_coin.csv,
and simulates paper trade entries/exits without placing real orders.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import numpy as np
import pandas as pd


# =============================================================================
# IMPULSE / EVENT-LONG - REALISTIC LIVE PAPER LOGGER
# =============================================================================
#
# REAL ORDERS: NO
#
# Purpose:
#   Live-paper logger for the first family: impulse / event-long.
#
# Signal per coin:
#   retL >= move_bps
#   ret1 >= 0
#   ret3 >= 0
#
# Execution:
#   entry candle = signal_time + configured delay
#   long entry price = raw_entry_close * (1 + entry_slip_bps/10000)
#   exit:
#       - stop if low <= raw_entry_close * (1 - sl_bps/10000)
#       - otherwise fixed hold exit
#   long time exit price = raw_exit_close * (1 - exit_slip_bps/10000)
#   long stop exit price = stop_px * (1 - stop_slip_bps/10000)
#
# Output:
#   heartbeat.csv
#   signals.csv
#   pending_entries.csv
#   open_positions.csv
#   closed_trades.csv
#   rejected_entries.csv
#   errors.csv
#   state.json
# =============================================================================


API_BASE = "https://www.okx.com"
CANDLES_ENDPOINT = "/api/v5/market/candles"


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
}

DEFAULT_COINS = ",".join(FALLBACK_STRATEGIES.keys())


def utc_now() -> pd.Timestamp:
    return pd.Timestamp.now(tz="UTC")


def iso(ts: Any) -> str:
    if ts is None or pd.isna(ts):
        return ""
    return pd.Timestamp(ts).tz_convert("UTC").isoformat().replace("+00:00", "Z")


def append_csv(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            w.writeheader()
        w.writerow(row)


def write_csv_rows(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def read_csv_records(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        return pd.read_csv(path).fillna("").to_dict("records")
    except Exception:
        return []


def parse_strategy(coin: str, strategy: str) -> dict:
    m = re.search(
        r"_L(?P<L>\d+)_move(?P<move>\d+)_(?P<exit>fixed|sl\d+)_h(?P<hold>\d+)_d(?P<delay>\d+)_c(?P<cost>[\d.]+)",
        str(strategy),
    )
    if not m:
        raise ValueError(f"Cannot parse strategy for {coin}: {strategy}")

    gd = m.groupdict()
    exit_name = gd["exit"]
    sl = None if exit_name == "fixed" else float(exit_name.replace("sl", ""))

    return {
        "coin": coin.upper(),
        "inst_id": f"{coin.upper()}-USDT-SWAP",
        "strategy": str(strategy),
        "L": int(gd["L"]),
        "move_bps": float(gd["move"]),
        "sl_bps": sl,
        "hold_minutes": int(gd["hold"]),
        "delay_minutes": int(gd["delay"]),
        "strategy_cost_bps": float(gd["cost"]),
    }


def load_strategies(robust_dir: Path, coins: list[str], selection: str) -> dict[str, dict]:
    coins = [c.upper().strip() for c in coins if c.strip()]
    out: dict[str, dict] = {}

    if selection == "fallback":
        for coin in coins:
            if coin in FALLBACK_STRATEGIES:
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

    if path.exists():
        try:
            df = pd.read_csv(path)
            if "coin" in df.columns and strategy_col in df.columns:
                df["coin"] = df["coin"].astype(str).str.upper()
                df = df[df["coin"].isin(coins)]
                for _, row in df.iterrows():
                    coin = str(row["coin"]).upper()
                    if pd.notna(row[strategy_col]):
                        out[coin] = parse_strategy(coin, str(row[strategy_col]))
        except Exception:
            pass

    for coin in coins:
        if coin not in out and coin in FALLBACK_STRATEGIES:
            out[coin] = parse_strategy(coin, FALLBACK_STRATEGIES[coin])

    return out


def okx_fetch_1m_candles(inst_id: str, limit: int, retries: int = 3, sleep_sec: float = 0.2) -> pd.DataFrame:
    params = {"instId": inst_id, "bar": "1m", "limit": str(limit)}
    url = f"{API_BASE}{CANDLES_ENDPOINT}?{urlencode(params)}"
    last_err = None

    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers={"User-Agent": "edge-lab-impulse-paper-logger/1.0", "Accept": "application/json"})
            with urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
            js = json.loads(raw)

            if str(js.get("code")) != "0":
                raise RuntimeError(f"OKX code={js.get('code')} msg={js.get('msg')} body={js}")

            data = js.get("data", [])
            if not data:
                return pd.DataFrame()

            rows = []
            for r in data:
                # OKX: [ts,o,h,l,c,vol,volCcy,volCcyQuote,confirm]
                if len(r) < 8:
                    continue
                rows.append({
                    "ts": pd.to_numeric(r[0], errors="coerce"),
                    "open": pd.to_numeric(r[1], errors="coerce"),
                    "high": pd.to_numeric(r[2], errors="coerce"),
                    "low": pd.to_numeric(r[3], errors="coerce"),
                    "close": pd.to_numeric(r[4], errors="coerce"),
                    "vol": pd.to_numeric(r[5], errors="coerce") if len(r) > 5 else np.nan,
                    "volCcy": pd.to_numeric(r[6], errors="coerce") if len(r) > 6 else np.nan,
                    "volCcyQuote": pd.to_numeric(r[7], errors="coerce") if len(r) > 7 else np.nan,
                    "confirm": str(r[8]) if len(r) > 8 else "1",
                })

            df = pd.DataFrame(rows)
            if df.empty:
                return df

            df["time"] = pd.to_datetime(df["ts"], unit="ms", utc=True, errors="coerce")
            for c in ["open", "high", "low", "close", "vol", "volCcy", "volCcyQuote"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")

            df = (
                df.dropna(subset=["time", "open", "high", "low", "close"])
                .drop_duplicates("time")
                .sort_values("time")
                .reset_index(drop=True)
            )

            # Keep only closed candles.
            df = df.loc[df["confirm"].astype(str) == "1"].copy()

            if "volCcyQuote" not in df.columns or df["volCcyQuote"].isna().all():
                if "volCcy" in df.columns and not df["volCcy"].isna().all():
                    df["volCcyQuote"] = df["volCcy"] * df["close"]
                else:
                    df["volCcyQuote"] = df["vol"] * df["close"]

            close = df["close"].astype(float)
            open_ = df["open"].replace(0, np.nan).astype(float)
            df["ret1_bps"] = close.pct_change() * 10000.0
            for L in [3, 5, 10]:
                df[f"ret{L}_bps"] = (close / close.shift(L) - 1.0) * 10000.0
            df["range_bps"] = (df["high"] - df["low"]) / open_ * 10000.0
            return df.reset_index(drop=True)

        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, RuntimeError) as e:
            last_err = repr(e)
            time.sleep(sleep_sec * attempt * 2)

    raise RuntimeError(f"OKX fetch failed for {inst_id}. Last error: {last_err}")


@dataclass
class PendingEntry:
    signal_id: str
    inst_id: str
    coin: str
    strategy: str
    signal_time: str
    target_entry_time: str
    planned_exit_time: str
    L: int
    move_bps: float
    sl_bps: str
    hold_minutes: int
    delay_minutes: int
    strategy_cost_bps: float
    signal_close: float
    signal_retL_bps: float
    signal_ret1_bps: float
    signal_ret3_bps: float
    signal_vol_quote: float
    signal_range_bps: float
    created_at: str


@dataclass
class OpenPosition:
    position_id: str
    inst_id: str
    coin: str
    strategy: str
    signal_id: str
    signal_time: str
    entry_time: str
    planned_exit_time: str
    L: int
    move_bps: float
    sl_bps: str
    hold_minutes: int
    delay_minutes: int
    strategy_cost_bps: float
    raw_entry_close: float
    entry_price: float
    stop_px: str
    notional: float
    equity_before: float
    signal_close: float
    signal_retL_bps: float
    signal_ret1_bps: float
    signal_ret3_bps: float
    signal_vol_quote: float
    signal_range_bps: float
    entry_vol_quote: float
    entry_range_bps: float
    entry_slip_bps: float
    exit_slip_bps: float
    stop_slip_bps: float
    stress_extra_bps: float


class ImpulsePaperLogger:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.out_dir = Path(args.out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        coins = [x.strip().upper() for x in args.coins.split(",") if x.strip()]
        exclude = {x.strip().upper() for x in args.exclude_coins.split(",") if x.strip()}
        coins = [c for c in coins if c not in exclude]

        self.strategies = load_strategies(Path(args.robust_dir), coins, args.selection)
        self.coins = sorted(self.strategies.keys())

        self.signals_path = self.out_dir / "signals.csv"
        self.pending_path = self.out_dir / "pending_entries.csv"
        self.open_path = self.out_dir / "open_positions.csv"
        self.closed_path = self.out_dir / "closed_trades.csv"
        self.rejected_path = self.out_dir / "rejected_entries.csv"
        self.heartbeat_path = self.out_dir / "heartbeat.csv"
        self.errors_path = self.out_dir / "errors.csv"
        self.state_path = self.out_dir / "state.json"
        self.config_path = self.out_dir / "strategy_config.json"

        self.pending: dict[str, PendingEntry] = {}
        self.open_positions: dict[str, OpenPosition] = {}
        self.seen_signal_ids: set[str] = set()

        self.equity = float(args.start_equity)
        self.closed_count = 0
        self.errors = 0

        self.config_path.write_text(json.dumps(self.strategies, indent=2), encoding="utf-8")
        self.load_state()

    def load_state(self) -> None:
        for r in read_csv_records(self.signals_path):
            sid = str(r.get("signal_id", ""))
            if sid:
                self.seen_signal_ids.add(sid)

        for r in read_csv_records(self.pending_path):
            try:
                if str(r.get("status", "pending")) not in {"", "pending"}:
                    continue
                p = PendingEntry(
                    signal_id=str(r["signal_id"]),
                    inst_id=str(r["inst_id"]),
                    coin=str(r["coin"]),
                    strategy=str(r["strategy"]),
                    signal_time=str(r["signal_time"]),
                    target_entry_time=str(r["target_entry_time"]),
                    planned_exit_time=str(r["planned_exit_time"]),
                    L=int(r["L"]),
                    move_bps=float(r["move_bps"]),
                    sl_bps=str(r.get("sl_bps", "")),
                    hold_minutes=int(r["hold_minutes"]),
                    delay_minutes=int(r["delay_minutes"]),
                    strategy_cost_bps=float(r["strategy_cost_bps"]),
                    signal_close=float(r["signal_close"]),
                    signal_retL_bps=float(r["signal_retL_bps"]),
                    signal_ret1_bps=float(r["signal_ret1_bps"]),
                    signal_ret3_bps=float(r["signal_ret3_bps"]),
                    signal_vol_quote=float(r["signal_vol_quote"]),
                    signal_range_bps=float(r["signal_range_bps"]),
                    created_at=str(r.get("created_at", "")),
                )
                self.pending[p.signal_id] = p
                self.seen_signal_ids.add(p.signal_id)
            except Exception:
                continue

        for r in read_csv_records(self.open_path):
            try:
                pos = OpenPosition(
                    position_id=str(r["position_id"]),
                    inst_id=str(r["inst_id"]),
                    coin=str(r["coin"]),
                    strategy=str(r["strategy"]),
                    signal_id=str(r["signal_id"]),
                    signal_time=str(r["signal_time"]),
                    entry_time=str(r["entry_time"]),
                    planned_exit_time=str(r["planned_exit_time"]),
                    L=int(r["L"]),
                    move_bps=float(r["move_bps"]),
                    sl_bps=str(r.get("sl_bps", "")),
                    hold_minutes=int(r["hold_minutes"]),
                    delay_minutes=int(r["delay_minutes"]),
                    strategy_cost_bps=float(r["strategy_cost_bps"]),
                    raw_entry_close=float(r["raw_entry_close"]),
                    entry_price=float(r["entry_price"]),
                    stop_px=str(r.get("stop_px", "")),
                    notional=float(r["notional"]),
                    equity_before=float(r["equity_before"]),
                    signal_close=float(r["signal_close"]),
                    signal_retL_bps=float(r["signal_retL_bps"]),
                    signal_ret1_bps=float(r["signal_ret1_bps"]),
                    signal_ret3_bps=float(r["signal_ret3_bps"]),
                    signal_vol_quote=float(r["signal_vol_quote"]),
                    signal_range_bps=float(r["signal_range_bps"]),
                    entry_vol_quote=float(r["entry_vol_quote"]),
                    entry_range_bps=float(r["entry_range_bps"]),
                    entry_slip_bps=float(r["entry_slip_bps"]),
                    exit_slip_bps=float(r["exit_slip_bps"]),
                    stop_slip_bps=float(r["stop_slip_bps"]),
                    stress_extra_bps=float(r["stress_extra_bps"]),
                )
                self.open_positions[pos.position_id] = pos
            except Exception:
                continue

        closed = read_csv_records(self.closed_path)
        self.closed_count = len(closed)
        if closed:
            try:
                self.equity = float(closed[-1]["equity_after"])
            except Exception:
                pass

    def save_state(self) -> None:
        pending_rows = []
        for p in self.pending.values():
            row = asdict(p)
            row["status"] = "pending"
            pending_rows.append(row)

        write_csv_rows(self.pending_path, pending_rows, fieldnames=[
            "status", "signal_id", "inst_id", "coin", "strategy", "signal_time",
            "target_entry_time", "planned_exit_time", "L", "move_bps", "sl_bps",
            "hold_minutes", "delay_minutes", "strategy_cost_bps", "signal_close",
            "signal_retL_bps", "signal_ret1_bps", "signal_ret3_bps",
            "signal_vol_quote", "signal_range_bps", "created_at",
        ])

        open_rows = [asdict(p) for p in self.open_positions.values()]
        write_csv_rows(self.open_path, open_rows, fieldnames=[
            "position_id", "inst_id", "coin", "strategy", "signal_id", "signal_time",
            "entry_time", "planned_exit_time", "L", "move_bps", "sl_bps",
            "hold_minutes", "delay_minutes", "strategy_cost_bps", "raw_entry_close",
            "entry_price", "stop_px", "notional", "equity_before", "signal_close",
            "signal_retL_bps", "signal_ret1_bps", "signal_ret3_bps",
            "signal_vol_quote", "signal_range_bps", "entry_vol_quote",
            "entry_range_bps", "entry_slip_bps", "exit_slip_bps",
            "stop_slip_bps", "stress_extra_bps",
        ])

        self.state_path.write_text(json.dumps({
            "updated_at": iso(utc_now()),
            "equity": self.equity,
            "pending": len(self.pending),
            "open": len(self.open_positions),
            "closed_count": self.closed_count,
            "errors": self.errors,
            "coins": self.coins,
        }, indent=2), encoding="utf-8")

    def log_error(self, where: str, inst_id: str, e: Exception) -> None:
        self.errors += 1
        append_csv(self.errors_path, {
            "log_time": iso(utc_now()),
            "where": where,
            "inst_id": inst_id,
            "error_type": type(e).__name__,
            "error": str(e),
        })

    def get_candle_at(self, df: pd.DataFrame, target: pd.Timestamp) -> pd.Series | None:
        target = pd.Timestamp(target).tz_convert("UTC")
        m = df["time"] == target
        if not m.any():
            return None
        return df.loc[m].iloc[-1]

    def scan_coin_for_signals(self, coin: str) -> None:
        sp = self.strategies[coin]
        try:
            df = okx_fetch_1m_candles(sp["inst_id"], limit=self.args.candle_limit, sleep_sec=self.args.request_sleep)
        except Exception as e:
            self.log_error("scan_fetch", sp["inst_id"], e)
            return

        if df.empty or len(df) < 20:
            return

        L = int(sp["L"])
        ret_col = f"ret{L}_bps"
        if ret_col not in df.columns:
            return

        now = utc_now()
        min_time = now - pd.Timedelta(minutes=self.args.signal_backfill_minutes)

        sig_rows = df.loc[
            (df["time"] >= min_time)
            & (df[ret_col] >= float(sp["move_bps"]))
            & (df["ret1_bps"] >= 0)
            & (df["ret3_bps"] >= 0)
        ].copy()

        if sig_rows.empty:
            return

        for _, sig in sig_rows.iterrows():
            sig_time = pd.Timestamp(sig["time"]).tz_convert("UTC")
            signal_id = f"{coin}_{sp['strategy']}_{sig_time.strftime('%Y%m%dT%H%M%SZ')}"

            if signal_id in self.seen_signal_ids:
                continue

            self.seen_signal_ids.add(signal_id)

            signal_close = float(sig["close"])
            signal_vol = float(sig.get("volCcyQuote", np.nan))
            signal_range = float(sig.get("range_bps", np.nan))

            if not np.isfinite(signal_vol) or signal_vol < self.args.min_signal_vol_quote:
                append_csv(self.rejected_path, {
                    "type": "signal_reject",
                    "reason": "low_signal_vol_quote",
                    "log_time": iso(now),
                    "signal_id": signal_id,
                    "coin": coin,
                    "signal_time": iso(sig_time),
                    "signal_vol_quote": signal_vol,
                    "signal_range_bps": signal_range,
                    "signal_retL_bps": float(sig[ret_col]),
                })
                continue

            if np.isfinite(signal_range) and signal_range > self.args.max_signal_range_bps:
                append_csv(self.rejected_path, {
                    "type": "signal_reject",
                    "reason": "high_signal_range_bps",
                    "log_time": iso(now),
                    "signal_id": signal_id,
                    "coin": coin,
                    "signal_time": iso(sig_time),
                    "signal_vol_quote": signal_vol,
                    "signal_range_bps": signal_range,
                    "signal_retL_bps": float(sig[ret_col]),
                })
                continue

            target_entry_time = sig_time + pd.Timedelta(minutes=int(sp["delay_minutes"]))
            planned_exit_time = target_entry_time + pd.Timedelta(minutes=int(sp["hold_minutes"]))
            sl_str = "" if sp["sl_bps"] is None else str(float(sp["sl_bps"]))

            p = PendingEntry(
                signal_id=signal_id,
                inst_id=sp["inst_id"],
                coin=coin,
                strategy=sp["strategy"],
                signal_time=iso(sig_time),
                target_entry_time=iso(target_entry_time),
                planned_exit_time=iso(planned_exit_time),
                L=int(sp["L"]),
                move_bps=float(sp["move_bps"]),
                sl_bps=sl_str,
                hold_minutes=int(sp["hold_minutes"]),
                delay_minutes=int(sp["delay_minutes"]),
                strategy_cost_bps=float(sp["strategy_cost_bps"]),
                signal_close=signal_close,
                signal_retL_bps=float(sig[ret_col]),
                signal_ret1_bps=float(sig["ret1_bps"]),
                signal_ret3_bps=float(sig["ret3_bps"]),
                signal_vol_quote=signal_vol,
                signal_range_bps=signal_range,
                created_at=iso(now),
            )

            self.pending[p.signal_id] = p
            append_csv(self.signals_path, {"type": "signal_pending_long", **asdict(p)})

            print(
                f"[SIGNAL] {coin} {iso(sig_time)} retL={p.signal_retL_bps:.1f} "
                f"entry={p.target_entry_time} hold={p.hold_minutes}"
            )

    def process_pending(self, p: PendingEntry) -> None:
        target_entry = pd.Timestamp(p.target_entry_time).tz_convert("UTC")
        now = utc_now()

        if now < target_entry + pd.Timedelta(minutes=1):
            return

        try:
            df = okx_fetch_1m_candles(p.inst_id, limit=self.args.candle_limit, sleep_sec=self.args.request_sleep)
        except Exception as e:
            self.log_error("pending_fetch", p.inst_id, e)
            return

        entry = self.get_candle_at(df, target_entry)
        if entry is None:
            return

        raw_entry = float(entry["close"])
        entry_vol = float(entry.get("volCcyQuote", np.nan))
        entry_range = float(entry.get("range_bps", np.nan))

        if not np.isfinite(entry_vol) or entry_vol < self.args.min_entry_vol_quote:
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "low_entry_vol_quote",
                "log_time": iso(now),
                **asdict(p),
                "raw_entry_close": raw_entry,
                "entry_vol_quote": entry_vol,
                "entry_range_bps": entry_range,
            })
            self.pending.pop(p.signal_id, None)
            return

        if np.isfinite(entry_range) and entry_range > self.args.max_entry_range_bps:
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "high_entry_range_bps",
                "log_time": iso(now),
                **asdict(p),
                "raw_entry_close": raw_entry,
                "entry_vol_quote": entry_vol,
                "entry_range_bps": entry_range,
            })
            self.pending.pop(p.signal_id, None)
            return

        if len(self.open_positions) >= self.args.max_positions:
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "max_positions",
                "log_time": iso(now),
                **asdict(p),
                "raw_entry_close": raw_entry,
                "entry_vol_quote": entry_vol,
                "entry_range_bps": entry_range,
                "open_positions": len(self.open_positions),
            })
            self.pending.pop(p.signal_id, None)
            return

        if any(pos.coin == p.coin for pos in self.open_positions.values()):
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "same_coin_overlap",
                "log_time": iso(now),
                **asdict(p),
                "raw_entry_close": raw_entry,
                "entry_vol_quote": entry_vol,
                "entry_range_bps": entry_range,
                "open_positions": len(self.open_positions),
            })
            self.pending.pop(p.signal_id, None)
            return

        entry_price = raw_entry * (1.0 + self.args.entry_slip_bps / 10000.0)
        sl_val = None if p.sl_bps == "" else float(p.sl_bps)
        stop_px = "" if sl_val is None else str(raw_entry * (1.0 - sl_val / 10000.0))
        notional = self.equity * self.args.paper_fraction
        position_id = f"{p.coin}_{p.strategy}_{target_entry.strftime('%Y%m%dT%H%M%SZ')}"

        pos = OpenPosition(
            position_id=position_id,
            inst_id=p.inst_id,
            coin=p.coin,
            strategy=p.strategy,
            signal_id=p.signal_id,
            signal_time=p.signal_time,
            entry_time=iso(target_entry),
            planned_exit_time=p.planned_exit_time,
            L=p.L,
            move_bps=p.move_bps,
            sl_bps=p.sl_bps,
            hold_minutes=p.hold_minutes,
            delay_minutes=p.delay_minutes,
            strategy_cost_bps=p.strategy_cost_bps,
            raw_entry_close=raw_entry,
            entry_price=entry_price,
            stop_px=stop_px,
            notional=notional,
            equity_before=self.equity,
            signal_close=p.signal_close,
            signal_retL_bps=p.signal_retL_bps,
            signal_ret1_bps=p.signal_ret1_bps,
            signal_ret3_bps=p.signal_ret3_bps,
            signal_vol_quote=p.signal_vol_quote,
            signal_range_bps=p.signal_range_bps,
            entry_vol_quote=entry_vol,
            entry_range_bps=entry_range,
            entry_slip_bps=self.args.entry_slip_bps,
            exit_slip_bps=self.args.exit_slip_bps,
            stop_slip_bps=self.args.stop_slip_bps,
            stress_extra_bps=self.args.stress_extra_bps,
        )

        self.open_positions[position_id] = pos
        self.pending.pop(p.signal_id, None)
        append_csv(self.signals_path, {"type": "open_long", **asdict(pos)})

        print(
            f"[OPEN] {p.coin} entry={iso(target_entry)} raw={raw_entry:.10g} "
            f"entry_price={entry_price:.10g} notional={notional:.2f} exit={p.planned_exit_time}"
        )

    def process_exit(self, pos: OpenPosition) -> None:
        now = utc_now()
        entry_time = pd.Timestamp(pos.entry_time).tz_convert("UTC")
        planned_exit = pd.Timestamp(pos.planned_exit_time).tz_convert("UTC")

        try:
            df = okx_fetch_1m_candles(pos.inst_id, limit=self.args.candle_limit, sleep_sec=self.args.request_sleep)
        except Exception as e:
            self.log_error("exit_fetch", pos.inst_id, e)
            return

        if df.empty:
            return

        exit_reason = None
        exit_time = None
        raw_exit = None

        stop_px = None if pos.stop_px == "" else float(pos.stop_px)

        # Stop can happen after entry once candles are closed.
        if stop_px is not None:
            check = df.loc[(df["time"] > entry_time) & (df["time"] <= now - pd.Timedelta(minutes=1))].copy()
            hit = check.loc[check["low"].astype(float) <= stop_px]
            if not hit.empty:
                row = hit.iloc[0]
                exit_reason = "stop"
                exit_time = pd.Timestamp(row["time"]).tz_convert("UTC")
                raw_exit = stop_px

        # Time exit if no stop.
        if exit_reason is None:
            if now < planned_exit + pd.Timedelta(minutes=1):
                return
            row = self.get_candle_at(df, planned_exit)
            if row is None:
                return
            exit_reason = "time"
            exit_time = planned_exit
            raw_exit = float(row["close"])

        if exit_reason == "stop":
            exit_price = float(raw_exit) * (1.0 - pos.stop_slip_bps / 10000.0)
        else:
            exit_price = float(raw_exit) * (1.0 - pos.exit_slip_bps / 10000.0)

        gross_ret = exit_price / pos.entry_price - 1.0
        realistic_net_ret = gross_ret - pos.strategy_cost_bps / 10000.0
        stress_net_ret = realistic_net_ret - pos.stress_extra_bps / 10000.0

        pnl = pos.notional * realistic_net_ret
        stress_pnl = pos.notional * stress_net_ret
        equity_before = self.equity
        self.equity += pnl
        self.closed_count += 1

        hold_actual = (pd.Timestamp(exit_time) - entry_time).total_seconds() / 60.0

        append_csv(self.closed_path, {
            "close_id": f"close_{pos.position_id}_{pd.Timestamp(exit_time).strftime('%Y%m%dT%H%M%SZ')}",
            "position_id": pos.position_id,
            "inst_id": pos.inst_id,
            "coin": pos.coin,
            "strategy": pos.strategy,
            "signal_id": pos.signal_id,
            "signal_time": pos.signal_time,
            "entry_time": pos.entry_time,
            "exit_time": iso(exit_time),
            "planned_exit_time": pos.planned_exit_time,
            "exit_reason": exit_reason,
            "hold_minutes_actual": hold_actual,
            "L": pos.L,
            "move_bps": pos.move_bps,
            "sl_bps": pos.sl_bps,
            "raw_entry_close": pos.raw_entry_close,
            "raw_exit_close": raw_exit,
            "entry_price": pos.entry_price,
            "exit_price": exit_price,
            "entry_slip_bps": pos.entry_slip_bps,
            "exit_slip_bps": pos.exit_slip_bps,
            "stop_slip_bps": pos.stop_slip_bps,
            "strategy_cost_bps": pos.strategy_cost_bps,
            "stress_extra_bps": pos.stress_extra_bps,
            "gross_ret": gross_ret,
            "realistic_net_ret": realistic_net_ret,
            "stress_net_ret": stress_net_ret,
            "notional": pos.notional,
            "pnl": pnl,
            "stress_pnl": stress_pnl,
            "equity_before": equity_before,
            "equity_after": self.equity,
            "signal_close": pos.signal_close,
            "signal_retL_bps": pos.signal_retL_bps,
            "signal_ret1_bps": pos.signal_ret1_bps,
            "signal_ret3_bps": pos.signal_ret3_bps,
            "signal_vol_quote": pos.signal_vol_quote,
            "signal_range_bps": pos.signal_range_bps,
            "entry_vol_quote": pos.entry_vol_quote,
            "entry_range_bps": pos.entry_range_bps,
        })

        self.open_positions.pop(pos.position_id, None)

        print(
            f"[CLOSE] {pos.coin} {exit_reason} exit={iso(exit_time)} "
            f"net={realistic_net_ret:.4f} pnl={pnl:.4f} equity={self.equity:.2f}"
        )

    def run_once(self) -> None:
        for p in list(self.pending.values()):
            self.process_pending(p)

        for pos in list(self.open_positions.values()):
            self.process_exit(pos)

        for i, coin in enumerate(self.coins, 1):
            self.scan_coin_for_signals(coin)
            time.sleep(self.args.request_sleep)

        for p in list(self.pending.values()):
            self.process_pending(p)

        self.write_heartbeat()
        self.save_state()
        self.print_status()

    def write_heartbeat(self) -> None:
        append_csv(self.heartbeat_path, {
            "log_time": iso(utc_now()),
            "equity": self.equity,
            "open_positions": len(self.open_positions),
            "pending_entries": len(self.pending),
            "closed_count": self.closed_count,
            "errors": self.errors,
            "coins": len(self.coins),
            "strategy_family": "impulse_event_long",
        })

    def print_status(self) -> None:
        print(
            f"[{iso(utc_now())}] equity={self.equity:.2f} "
            f"open={len(self.open_positions)} pending={len(self.pending)} "
            f"closed={self.closed_count} errors={self.errors}"
        )

    def run_forever(self) -> None:
        print("=" * 90)
        print("IMPULSE / EVENT-LONG - REALISTIC LIVE PAPER LOGGER")
        print("=" * 90)
        print("REAL ORDERS: NO")
        print("OKX endpoint:", f"{API_BASE}{CANDLES_ENDPOINT}")
        print("out_dir:", self.out_dir)
        print("coins:", len(self.coins), ",".join(self.coins))
        print("settings:")
        print("  start_equity=", self.args.start_equity)
        print("  paper_fraction=", self.args.paper_fraction)
        print("  max_positions=", self.args.max_positions)
        print("  min_signal_vol_quote=", self.args.min_signal_vol_quote)
        print("  min_entry_vol_quote=", self.args.min_entry_vol_quote)
        print("  max_signal_range_bps=", self.args.max_signal_range_bps)
        print("  max_entry_range_bps=", self.args.max_entry_range_bps)
        print("  entry_slip_bps=", self.args.entry_slip_bps)
        print("  exit_slip_bps=", self.args.exit_slip_bps)
        print("  stop_slip_bps=", self.args.stop_slip_bps)
        print("  stress_extra_bps=", self.args.stress_extra_bps)
        print("loaded strategies:")
        for c in self.coins:
            sp = self.strategies[c]
            print(f"  {c}: L={sp['L']} move={sp['move_bps']} sl={sp['sl_bps']} hold={sp['hold_minutes']} d={sp['delay_minutes']} c={sp['strategy_cost_bps']}")
        print("=" * 90)

        while True:
            try:
                self.run_once()
            except KeyboardInterrupt:
                self.save_state()
                print("\nStopped by user. State saved.")
                raise
            except Exception as e:
                self.log_error("main_loop", "", e)
                self.save_state()
                print(f"[ERROR] {type(e).__name__}: {e}")

            time.sleep(self.args.poll_seconds)

    def save_state(self) -> None:
        # Re-defined intentionally? No. Kept as class method above.
        pending_rows = []
        for p in self.pending.values():
            row = asdict(p)
            row["status"] = "pending"
            pending_rows.append(row)

        write_csv_rows(self.pending_path, pending_rows, fieldnames=[
            "status", "signal_id", "inst_id", "coin", "strategy", "signal_time",
            "target_entry_time", "planned_exit_time", "L", "move_bps", "sl_bps",
            "hold_minutes", "delay_minutes", "strategy_cost_bps", "signal_close",
            "signal_retL_bps", "signal_ret1_bps", "signal_ret3_bps",
            "signal_vol_quote", "signal_range_bps", "created_at",
        ])

        open_rows = [asdict(p) for p in self.open_positions.values()]
        write_csv_rows(self.open_path, open_rows, fieldnames=[
            "position_id", "inst_id", "coin", "strategy", "signal_id", "signal_time",
            "entry_time", "planned_exit_time", "L", "move_bps", "sl_bps",
            "hold_minutes", "delay_minutes", "strategy_cost_bps", "raw_entry_close",
            "entry_price", "stop_px", "notional", "equity_before", "signal_close",
            "signal_retL_bps", "signal_ret1_bps", "signal_ret3_bps",
            "signal_vol_quote", "signal_range_bps", "entry_vol_quote",
            "entry_range_bps", "entry_slip_bps", "exit_slip_bps",
            "stop_slip_bps", "stress_extra_bps",
        ])

        self.state_path.write_text(json.dumps({
            "updated_at": iso(utc_now()),
            "equity": self.equity,
            "pending": len(self.pending),
            "open": len(self.open_positions),
            "closed_count": self.closed_count,
            "errors": self.errors,
            "coins": self.coins,
        }, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Live paper logger for impulse/event-long family.")
    ap.add_argument("--robust_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\finalist_impulse_robustness")
    ap.add_argument("--out_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\live_impulse_event_long_paper")
    ap.add_argument("--coins", default=DEFAULT_COINS)
    ap.add_argument("--exclude_coins", default="")
    ap.add_argument("--selection", choices=["strict", "cost", "fallback"], default="strict")

    ap.add_argument("--start_equity", type=float, default=1000.0)
    ap.add_argument("--paper_fraction", type=float, default=0.05)
    ap.add_argument("--max_positions", type=int, default=3)

    ap.add_argument("--min_signal_vol_quote", type=float, default=100000.0)
    ap.add_argument("--min_entry_vol_quote", type=float, default=100000.0)
    ap.add_argument("--max_signal_range_bps", type=float, default=1000.0)
    ap.add_argument("--max_entry_range_bps", type=float, default=1000.0)

    ap.add_argument("--entry_slip_bps", type=float, default=25.0)
    ap.add_argument("--exit_slip_bps", type=float, default=25.0)
    ap.add_argument("--stop_slip_bps", type=float, default=75.0)
    ap.add_argument("--stress_extra_bps", type=float, default=50.0)

    ap.add_argument("--candle_limit", type=int, default=700)
    ap.add_argument("--signal_backfill_minutes", type=int, default=20)
    ap.add_argument("--request_sleep", type=float, default=0.05)
    ap.add_argument("--poll_seconds", type=float, default=60.0)
    args = ap.parse_args()

    logger = ImpulsePaperLogger(args)
    logger.run_forever()


if __name__ == "__main__":
    main()
