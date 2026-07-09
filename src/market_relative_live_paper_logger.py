"""
Live paper logger for the market_relative_extreme_reversion_short strategy family that polls OKX
1-hour candles, detects coins whose 6-hour return exceeds the market median by at least 600 bps,
and logs simulated short entries/exits to the MASTER_UPPER_SYSTEM paper run directory without
placing real orders.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import numpy as np
import pandas as pd
from sizing_contract_runtime import resolve_family_notional


# =============================================================================
# MARKET-RELATIVE EXTREME REVERSION SHORT - LIVE PAPER LOGGER
# =============================================================================
#
# REAL ORDERS: NO
#
# Family 4:
#   market_relative_extreme_reversion_short
#
# Signal, based on 1H closed candles:
#   L = 6 hours
#   coin_ret6h - market_median_ret6h >= 600 bps
#   coin_ret6h >= 300 bps
#   side = short
#   entry_delay = 2 hourly bars
#   hold = 24 hourly bars
#
# Market proxy:
#   median ret6h across the auto-discovered OKX swap universe.
#
# Execution:
#   signal candle is closed 1H candle at signal_time
#   target entry candle = signal_time + entry_delay_hours
#   entry uses close of target entry candle once confirmed
#   exit uses close of entry_time + hold_hours candle once confirmed
#
# Paper pricing:
#   short entry price = raw_entry_close * (1 - entry_slip_bps/10000)
#   short exit price  = raw_exit_close  * (1 + exit_slip_bps/10000)
#   gross_ret = entry_price / exit_price - 1
#   realistic_net_ret = gross_ret - fee_bps_total/10000
#   stress_net_ret = realistic_net_ret - stress_extra_bps/10000
#
# Optional global gate:
#   If --require_global_gate is set, this logger will only open pending entries
#   if global_gate_decisions.csv says ALLOW for this signal_id.
#
# Files:
#   heartbeat.csv
#   market_snapshot.csv
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


def discover_coins(base: Path, start: str, end: str, coins_arg: str, exclude: set[str]) -> list[str]:
    if coins_arg.strip().upper() not in {"AUTO", "ALL", "ALL_EXISTING"}:
        return sorted({x.strip().upper() for x in coins_arg.split(",") if x.strip()} - exclude)

    coins = []
    for d in base.iterdir():
        if not d.is_dir() or d.name.startswith("_"):
            continue
        coin = d.name.upper()
        if coin in exclude:
            continue

        inst = f"{coin}-USDT-SWAP"
        exact = d / "raw" / "candles_long_1m" / f"{inst}_1m_{start}_{end}.csv"
        if exact.exists() and exact.stat().st_size > 0:
            coins.append(coin)
            continue

        files = sorted((d / "raw").glob(f"**/{inst}_1m_*.csv"))
        files = [p for p in files if p.exists() and p.stat().st_size > 0]
        if files:
            coins.append(coin)

    return sorted(set(coins))


def okx_fetch_1h_candles(inst_id: str, limit: int = 120, retries: int = 3, sleep_sec: float = 0.15) -> pd.DataFrame:
    params = {"instId": inst_id, "bar": "1H", "limit": str(limit)}
    url = f"{API_BASE}{CANDLES_ENDPOINT}?{urlencode(params)}"
    last_err = None

    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers={"User-Agent": "edge-lab-market-relative-paper-logger/1.0", "Accept": "application/json"})
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
                # OKX candles: [ts,o,h,l,c,vol,volCcy,volCcyQuote,confirm]
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

            # Keep only confirmed/closed hourly candles.
            df = df.loc[df["confirm"].astype(str) == "1"].copy()

            if "volCcyQuote" not in df.columns or df["volCcyQuote"].isna().all():
                if "volCcy" in df.columns and not df["volCcy"].isna().all():
                    df["volCcyQuote"] = df["volCcy"] * df["close"]
                else:
                    df["volCcyQuote"] = df["vol"] * df["close"]

            df["range_bps"] = (df["high"] - df["low"]) / df["open"].replace(0, np.nan) * 10000.0
            df["ret6_bps"] = (df["close"] / df["close"].shift(6) - 1.0) * 10000.0
            return df.reset_index(drop=True)

        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, RuntimeError) as e:
            last_err = repr(e)
            time.sleep(sleep_sec * attempt * 2)

    raise RuntimeError(f"OKX 1H fetch failed for {inst_id}. Last error: {last_err}")


@dataclass
class PendingEntry:
    signal_id: str
    inst_id: str
    coin: str
    strategy: str
    family_key: str
    signal_time: str
    target_entry_time: str
    planned_exit_time: str
    L_hours: int
    rel_threshold_bps: float
    coin_threshold_bps: float
    hold_hours: int
    entry_delay_hours: int
    signal_close: float
    coin_ret_bps: float
    market_ret_bps: float
    rel_ret_bps: float
    signal_vol_quote: float
    signal_range_bps: float
    created_at: str


@dataclass
class OpenPosition:
    position_id: str
    inst_id: str
    coin: str
    strategy: str
    family_key: str
    signal_id: str
    signal_time: str
    entry_time: str
    planned_exit_time: str
    L_hours: int
    rel_threshold_bps: float
    coin_threshold_bps: float
    hold_hours: int
    entry_delay_hours: int
    raw_entry_close: float
    entry_price: float
    notional: float
    equity_before: float
    signal_close: float
    coin_ret_bps: float
    market_ret_bps: float
    rel_ret_bps: float
    signal_vol_quote: float
    signal_range_bps: float
    entry_vol_quote: float
    entry_range_bps: float
    entry_slip_bps: float
    exit_slip_bps: float
    fee_bps_total: float
    stress_extra_bps: float


class MarketRelativePaperLogger:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.base_dir = Path(args.base_dir)
        self.out_dir = Path(args.out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.strategy = "market_relative_extreme_reversion_short_L6_rel600_coin300_hold24"
        self.family_key = "market_relative_short"

        self.signals_path = self.out_dir / "signals.csv"
        self.snapshot_path = self.out_dir / "market_snapshot.csv"
        self.pending_path = self.out_dir / "pending_entries.csv"
        self.open_path = self.out_dir / "open_positions.csv"
        self.closed_path = self.out_dir / "closed_trades.csv"
        self.rejected_path = self.out_dir / "rejected_entries.csv"
        self.errors_path = self.out_dir / "errors.csv"
        self.heartbeat_path = self.out_dir / "heartbeat.csv"
        self.state_path = self.out_dir / "state.json"

        exclude = {x.strip().upper() for x in args.exclude.split(",") if x.strip()}
        self.coins = discover_coins(self.base_dir, args.start, args.end, args.coins, exclude)

        self.pending: dict[str, PendingEntry] = {}
        self.open_positions: dict[str, OpenPosition] = {}
        self.seen_signal_ids: set[str] = set()

        self.equity = float(args.start_equity)
        self.closed_count = 0
        self.errors = 0
        self.last_full_scan_target_time = ""

        self.load_state()

    def load_state(self) -> None:
        for r in read_csv_records(self.signals_path):
            sid = str(r.get("signal_id", ""))
            if sid:
                self.seen_signal_ids.add(sid)

        for r in read_csv_records(self.pending_path):
            try:
                if str(r.get("status", "pending")) not in {"pending", ""}:
                    continue
                p = PendingEntry(
                    signal_id=str(r["signal_id"]),
                    inst_id=str(r["inst_id"]),
                    coin=str(r["coin"]),
                    strategy=str(r.get("strategy", self.strategy)),
                    family_key=str(r.get("family_key", self.family_key)),
                    signal_time=str(r["signal_time"]),
                    target_entry_time=str(r["target_entry_time"]),
                    planned_exit_time=str(r["planned_exit_time"]),
                    L_hours=int(r.get("L_hours", self.args.L_hours)),
                    rel_threshold_bps=float(r.get("rel_threshold_bps", self.args.rel_threshold_bps)),
                    coin_threshold_bps=float(r.get("coin_threshold_bps", self.args.coin_threshold_bps)),
                    hold_hours=int(r.get("hold_hours", self.args.hold_hours)),
                    entry_delay_hours=int(r.get("entry_delay_hours", self.args.entry_delay_hours)),
                    signal_close=float(r["signal_close"]),
                    coin_ret_bps=float(r["coin_ret_bps"]),
                    market_ret_bps=float(r["market_ret_bps"]),
                    rel_ret_bps=float(r["rel_ret_bps"]),
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
                    strategy=str(r.get("strategy", self.strategy)),
                    family_key=str(r.get("family_key", self.family_key)),
                    signal_id=str(r["signal_id"]),
                    signal_time=str(r["signal_time"]),
                    entry_time=str(r["entry_time"]),
                    planned_exit_time=str(r["planned_exit_time"]),
                    L_hours=int(r.get("L_hours", self.args.L_hours)),
                    rel_threshold_bps=float(r.get("rel_threshold_bps", self.args.rel_threshold_bps)),
                    coin_threshold_bps=float(r.get("coin_threshold_bps", self.args.coin_threshold_bps)),
                    hold_hours=int(r.get("hold_hours", self.args.hold_hours)),
                    entry_delay_hours=int(r.get("entry_delay_hours", self.args.entry_delay_hours)),
                    raw_entry_close=float(r["raw_entry_close"]),
                    entry_price=float(r["entry_price"]),
                    notional=float(r["notional"]),
                    equity_before=float(r["equity_before"]),
                    signal_close=float(r["signal_close"]),
                    coin_ret_bps=float(r["coin_ret_bps"]),
                    market_ret_bps=float(r["market_ret_bps"]),
                    rel_ret_bps=float(r["rel_ret_bps"]),
                    signal_vol_quote=float(r["signal_vol_quote"]),
                    signal_range_bps=float(r["signal_range_bps"]),
                    entry_vol_quote=float(r["entry_vol_quote"]),
                    entry_range_bps=float(r["entry_range_bps"]),
                    entry_slip_bps=float(r.get("entry_slip_bps", self.args.entry_slip_bps)),
                    exit_slip_bps=float(r.get("exit_slip_bps", self.args.exit_slip_bps)),
                    fee_bps_total=float(r.get("fee_bps_total", self.args.fee_bps_total)),
                    stress_extra_bps=float(r.get("stress_extra_bps", self.args.stress_extra_bps)),
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
            "status", "signal_id", "inst_id", "coin", "strategy", "family_key",
            "signal_time", "target_entry_time", "planned_exit_time",
            "L_hours", "rel_threshold_bps", "coin_threshold_bps", "hold_hours",
            "entry_delay_hours", "signal_close", "coin_ret_bps", "market_ret_bps",
            "rel_ret_bps", "signal_vol_quote", "signal_range_bps", "created_at",
        ])

        open_rows = [asdict(p) for p in self.open_positions.values()]
        write_csv_rows(self.open_path, open_rows, fieldnames=[
            "position_id", "inst_id", "coin", "strategy", "family_key", "signal_id",
            "signal_time", "entry_time", "planned_exit_time",
            "L_hours", "rel_threshold_bps", "coin_threshold_bps", "hold_hours",
            "entry_delay_hours", "raw_entry_close", "entry_price", "notional",
            "equity_before", "signal_close", "coin_ret_bps", "market_ret_bps",
            "rel_ret_bps", "signal_vol_quote", "signal_range_bps",
            "entry_vol_quote", "entry_range_bps",
            "entry_slip_bps", "exit_slip_bps", "fee_bps_total", "stress_extra_bps",
        ])

        state = {
            "updated_at": iso(utc_now()),
            "equity": self.equity,
            "pending_count": len(self.pending),
            "open_count": len(self.open_positions),
            "closed_count": self.closed_count,
            "errors": self.errors,
            "coins": len(self.coins),
            "strategy": self.strategy,
            "last_full_scan_target_time": self.last_full_scan_target_time,
        }
        self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def log_error(self, where: str, inst_id: str, error: Exception) -> None:
        self.errors += 1
        append_csv(self.errors_path, {
            "log_time": iso(utc_now()),
            "where": where,
            "inst_id": inst_id,
            "error_type": type(error).__name__,
            "error": str(error),
        })

    def get_candle_at(self, df: pd.DataFrame, target_time: pd.Timestamp) -> pd.Series | None:
        if df.empty:
            return None
        target_time = pd.Timestamp(target_time).tz_convert("UTC")
        m = df["time"] == target_time
        if not m.any():
            return None
        return df.loc[m].iloc[-1]

    def should_full_scan_now(self) -> bool:
        now = utc_now()
        # 1H bar closes at next hour. Scan after minute N to avoid incomplete exchange updates.
        return int(now.minute) >= int(self.args.scan_after_minute)

    def fetch_all_latest_snapshot(self) -> tuple[pd.Timestamp | None, float | None, pd.DataFrame]:
        rows = []

        for i, coin in enumerate(self.coins, 1):
            inst_id = f"{coin}-USDT-SWAP"
            try:
                df = okx_fetch_1h_candles(inst_id, limit=self.args.candle_limit, sleep_sec=self.args.request_sleep)
            except Exception as e:
                self.log_error("full_scan_fetch", inst_id, e)
                continue

            if df.empty or len(df) < self.args.L_hours + 2:
                continue

            last = df.iloc[-1]
            sig_time = pd.Timestamp(last["time"]).tz_convert("UTC")
            prev_time = sig_time - pd.Timedelta(hours=self.args.L_hours)
            prev = self.get_candle_at(df, prev_time)
            if prev is None:
                continue

            close_now = float(last["close"])
            close_prev = float(prev["close"])
            if close_prev <= 0 or close_now <= 0:
                continue

            coin_ret = (close_now / close_prev - 1.0) * 10000.0

            rows.append({
                "coin": coin,
                "inst_id": inst_id,
                "signal_time": sig_time,
                "signal_close": close_now,
                "coin_ret_bps": coin_ret,
                "signal_vol_quote": float(last.get("volCcyQuote", np.nan)),
                "signal_range_bps": float(last.get("range_bps", np.nan)),
            })

            if i % 25 == 0:
                print(f"  scanned {i}/{len(self.coins)} coins")
            time.sleep(self.args.request_sleep)

        snap = pd.DataFrame(rows)
        if snap.empty:
            return None, None, snap

        # Use the most common/latest confirmed signal_time across the universe.
        mode_time = snap["signal_time"].value_counts().index[0]
        target_time = pd.Timestamp(mode_time).tz_convert("UTC")
        snap = snap.loc[snap["signal_time"] == target_time].copy()

        if len(snap) < self.args.min_market_coins:
            return target_time, None, snap

        market_ret = float(pd.to_numeric(snap["coin_ret_bps"], errors="coerce").median())
        snap["market_ret_bps"] = market_ret
        snap["rel_ret_bps"] = snap["coin_ret_bps"] - market_ret
        return target_time, market_ret, snap

    def scan_signals(self) -> None:
        if not self.should_full_scan_now() and not self.args.force_scan_now:
            return

        target_time, market_ret, snap = self.fetch_all_latest_snapshot()
        if target_time is None or snap.empty:
            return

        target_key = iso(target_time)
        if target_key == self.last_full_scan_target_time and not self.args.force_scan_now:
            return

        self.last_full_scan_target_time = target_key
        self.args.force_scan_now = False

        append_csv(self.snapshot_path, {
            "log_time": iso(utc_now()),
            "signal_time": target_key,
            "coins_in_snapshot": len(snap),
            "market_ret_bps": market_ret if market_ret is not None else np.nan,
            "max_coin_ret_bps": float(pd.to_numeric(snap["coin_ret_bps"], errors="coerce").max()),
            "max_rel_ret_bps": float(pd.to_numeric(snap.get("rel_ret_bps", pd.Series(dtype=float)), errors="coerce").max()) if "rel_ret_bps" in snap.columns else np.nan,
            "threshold_rel_bps": self.args.rel_threshold_bps,
            "threshold_coin_bps": self.args.coin_threshold_bps,
        })

        if market_ret is None:
            return

        candidates = snap.loc[
            (snap["coin_ret_bps"] >= self.args.coin_threshold_bps)
            & (snap["rel_ret_bps"] >= self.args.rel_threshold_bps)
            & (snap["signal_vol_quote"] >= self.args.min_signal_vol_quote)
            & (snap["signal_range_bps"] <= self.args.max_signal_range_bps)
        ].copy()

        if candidates.empty:
            return

        # Prefer high volume signals if many appear.
        candidates = candidates.sort_values("signal_vol_quote", ascending=False)

        for _, sig in candidates.iterrows():
            coin = str(sig["coin"]).upper()
            signal_time = pd.Timestamp(sig["signal_time"]).tz_convert("UTC")
            signal_id = f"{coin}_{self.strategy}_{signal_time.strftime('%Y%m%dT%H%M%SZ')}"

            if signal_id in self.seen_signal_ids:
                continue

            self.seen_signal_ids.add(signal_id)

            target_entry_time = signal_time + pd.Timedelta(hours=self.args.entry_delay_hours)
            planned_exit_time = target_entry_time + pd.Timedelta(hours=self.args.hold_hours)

            p = PendingEntry(
                signal_id=signal_id,
                inst_id=str(sig["inst_id"]),
                coin=coin,
                strategy=self.strategy,
                family_key=self.family_key,
                signal_time=iso(signal_time),
                target_entry_time=iso(target_entry_time),
                planned_exit_time=iso(planned_exit_time),
                L_hours=self.args.L_hours,
                rel_threshold_bps=self.args.rel_threshold_bps,
                coin_threshold_bps=self.args.coin_threshold_bps,
                hold_hours=self.args.hold_hours,
                entry_delay_hours=self.args.entry_delay_hours,
                signal_close=float(sig["signal_close"]),
                coin_ret_bps=float(sig["coin_ret_bps"]),
                market_ret_bps=float(sig["market_ret_bps"]),
                rel_ret_bps=float(sig["rel_ret_bps"]),
                signal_vol_quote=float(sig["signal_vol_quote"]),
                signal_range_bps=float(sig["signal_range_bps"]),
                created_at=iso(utc_now()),
            )

            self.pending[p.signal_id] = p
            append_csv(self.signals_path, {
                "type": "signal_pending_short",
                **asdict(p),
            })

            print(
                f"[SIGNAL] {coin} signal={iso(signal_time)} "
                f"coin_ret={p.coin_ret_bps:.1f} market={p.market_ret_bps:.1f} "
                f"rel={p.rel_ret_bps:.1f} entry_bar={p.target_entry_time}"
            )

    def global_gate_decision(self, signal_id: str) -> tuple[str, str]:
        if not self.args.require_global_gate:
            return "ALLOW", "gate_not_required"

        gate_path = Path(self.args.global_gate_path)
        if not gate_path.exists() or gate_path.stat().st_size == 0:
            return "WAIT", "gate_file_missing"

        try:
            g = pd.read_csv(gate_path)
        except Exception:
            return "WAIT", "gate_file_read_error"

        if g.empty:
            return "WAIT", "gate_empty"

        m = (
            (g.get("family_key", "").astype(str) == self.family_key)
            & (g.get("signal_id", "").astype(str) == signal_id)
        )
        if not m.any():
            return "WAIT", "gate_signal_missing"

        row = g.loc[m].iloc[-1]
        decision = str(row.get("decision", "")).upper()
        reason = str(row.get("reason", ""))

        if decision == "ALLOW":
            return "ALLOW", reason or "gate_allow"
        if decision == "BLOCK":
            return "BLOCK", reason or "gate_block"
        return "WAIT", f"gate_unknown_decision_{decision}"

    def process_pending_entry(self, p: PendingEntry) -> None:
        target_entry_time = pd.Timestamp(p.target_entry_time).tz_convert("UTC")
        now = utc_now()

        # The target 1H candle is available after it closes: bar_start + 1H.
        if now < target_entry_time + pd.Timedelta(hours=1):
            return

        decision, gate_reason = self.global_gate_decision(p.signal_id)
        if decision == "WAIT":
            # Keep pending for manager to update. If too old, reject to avoid eternal pending.
            if now > target_entry_time + pd.Timedelta(hours=1, minutes=self.args.pending_max_wait_minutes):
                append_csv(self.rejected_path, {
                    "type": "entry_reject",
                    "reason": f"global_gate_timeout_{gate_reason}",
                    "log_time": iso(now),
                    **asdict(p),
                })
                self.pending.pop(p.signal_id, None)
            return

        if decision == "BLOCK":
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": f"global_gate_block_{gate_reason}",
                "log_time": iso(now),
                **asdict(p),
            })
            self.pending.pop(p.signal_id, None)
            return

        try:
            df = okx_fetch_1h_candles(p.inst_id, limit=self.args.candle_limit, sleep_sec=self.args.request_sleep)
        except Exception as e:
            self.log_error("pending_entry_fetch", p.inst_id, e)
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "allow_open_failed_fetch_error",
                "log_time": iso(now),
                **asdict(p),
                "gate_reason": gate_reason,
                "error_type": type(e).__name__,
                "error": str(e),
            })
            self.pending.pop(p.signal_id, None)
            return

        entry_row = self.get_candle_at(df, target_entry_time)
        if entry_row is None:
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "allow_open_failed_price_missing",
                "log_time": iso(now),
                **asdict(p),
                "gate_reason": gate_reason,
                "fetched_rows": len(df),
                "target_entry_time_checked": iso(target_entry_time),
            })
            self.pending.pop(p.signal_id, None)
            return

        try:
            raw_entry_close = float(entry_row["close"])
        except Exception as e:
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "allow_open_failed_column_missing",
                "log_time": iso(now),
                **asdict(p),
                "gate_reason": gate_reason,
                "missing_column": "close",
                "error_type": type(e).__name__,
                "error": str(e),
            })
            self.pending.pop(p.signal_id, None)
            return
        if not np.isfinite(raw_entry_close):
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "allow_open_failed_price_missing",
                "log_time": iso(now),
                **asdict(p),
                "gate_reason": gate_reason,
                "raw_entry_close": raw_entry_close,
            })
            self.pending.pop(p.signal_id, None)
            return
        entry_vol = float(entry_row.get("volCcyQuote", np.nan))
        entry_range = float(entry_row.get("range_bps", np.nan))

        if not np.isfinite(entry_vol) or entry_vol < self.args.min_entry_vol_quote:
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "low_entry_vol_quote",
                "log_time": iso(now),
                **asdict(p),
                "raw_entry_close": raw_entry_close,
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
                "raw_entry_close": raw_entry_close,
                "entry_vol_quote": entry_vol,
                "entry_range_bps": entry_range,
            })
            self.pending.pop(p.signal_id, None)
            return

        if len(self.open_positions) >= self.args.max_positions:
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "local_max_positions",
                "log_time": iso(now),
                **asdict(p),
                "raw_entry_close": raw_entry_close,
                "entry_vol_quote": entry_vol,
                "entry_range_bps": entry_range,
            })
            self.pending.pop(p.signal_id, None)
            return

        if any(pos.coin == p.coin for pos in self.open_positions.values()):
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "local_same_coin_overlap",
                "log_time": iso(now),
                **asdict(p),
                "raw_entry_close": raw_entry_close,
                "entry_vol_quote": entry_vol,
                "entry_range_bps": entry_range,
            })
            self.pending.pop(p.signal_id, None)
            return

        entry_price = raw_entry_close * (1.0 - self.args.entry_slip_bps / 10000.0)
        default_notional = self.equity * self.args.paper_fraction
        try:
            notional = resolve_family_notional(
                "market_relative_short",
                default_notional=default_notional,
                sizing_contract_path=self.args.sizing_contract,
                base_equity=self.equity,
            )
        except Exception as e:
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "allow_open_failed_sizing_missing",
                "log_time": iso(now),
                **asdict(p),
                "gate_reason": gate_reason,
                "raw_entry_close": raw_entry_close,
                "error_type": type(e).__name__,
                "error": str(e),
                "sizing_contract": self.args.sizing_contract,
            })
            self.pending.pop(p.signal_id, None)
            return
        if not np.isfinite(notional) or notional <= 0:
            append_csv(self.rejected_path, {
                "type": "entry_reject",
                "reason": "allow_open_failed_sizing_missing",
                "log_time": iso(now),
                **asdict(p),
                "gate_reason": gate_reason,
                "raw_entry_close": raw_entry_close,
                "notional": notional,
                "sizing_contract": self.args.sizing_contract,
            })
            self.pending.pop(p.signal_id, None)
            return
        position_id = f"{p.coin}_{self.strategy}_{target_entry_time.strftime('%Y%m%dT%H%M%SZ')}"

        pos = OpenPosition(
            position_id=position_id,
            inst_id=p.inst_id,
            coin=p.coin,
            strategy=p.strategy,
            family_key=p.family_key,
            signal_id=p.signal_id,
            signal_time=p.signal_time,
            entry_time=iso(target_entry_time),
            planned_exit_time=p.planned_exit_time,
            L_hours=p.L_hours,
            rel_threshold_bps=p.rel_threshold_bps,
            coin_threshold_bps=p.coin_threshold_bps,
            hold_hours=p.hold_hours,
            entry_delay_hours=p.entry_delay_hours,
            raw_entry_close=raw_entry_close,
            entry_price=entry_price,
            notional=notional,
            equity_before=self.equity,
            signal_close=p.signal_close,
            coin_ret_bps=p.coin_ret_bps,
            market_ret_bps=p.market_ret_bps,
            rel_ret_bps=p.rel_ret_bps,
            signal_vol_quote=p.signal_vol_quote,
            signal_range_bps=p.signal_range_bps,
            entry_vol_quote=entry_vol,
            entry_range_bps=entry_range,
            entry_slip_bps=self.args.entry_slip_bps,
            exit_slip_bps=self.args.exit_slip_bps,
            fee_bps_total=self.args.fee_bps_total,
            stress_extra_bps=self.args.stress_extra_bps,
        )

        self.open_positions[pos.position_id] = pos
        self.pending.pop(p.signal_id, None)

        append_csv(self.signals_path, {
            "type": "open_short",
            **asdict(pos),
            "global_gate_reason": gate_reason,
        })

        print(
            f"[OPEN] {p.coin} entry_bar={iso(target_entry_time)} raw={raw_entry_close:.10g} "
            f"entry_price={entry_price:.10g} notional={notional:.2f} exit_bar={p.planned_exit_time}"
        )

    def process_exit(self, pos: OpenPosition) -> None:
        exit_time = pd.Timestamp(pos.planned_exit_time).tz_convert("UTC")
        now = utc_now()

        # Exit candle is available after it closes.
        if now < exit_time + pd.Timedelta(hours=1):
            return

        try:
            df = okx_fetch_1h_candles(pos.inst_id, limit=self.args.candle_limit, sleep_sec=self.args.request_sleep)
        except Exception as e:
            self.log_error("exit_fetch", pos.inst_id, e)
            return

        exit_row = self.get_candle_at(df, exit_time)
        if exit_row is None:
            return

        raw_exit_close = float(exit_row["close"])
        exit_price = raw_exit_close * (1.0 + pos.exit_slip_bps / 10000.0)

        gross_ret = pos.entry_price / exit_price - 1.0
        realistic_net_ret = gross_ret - pos.fee_bps_total / 10000.0
        stress_net_ret = realistic_net_ret - pos.stress_extra_bps / 10000.0

        pnl = pos.notional * realistic_net_ret
        stress_pnl = pos.notional * stress_net_ret
        equity_before = self.equity
        self.equity += pnl
        self.closed_count += 1

        hold_actual_hours = (pd.Timestamp(exit_time) - pd.Timestamp(pos.entry_time)).total_seconds() / 3600.0

        row = {
            "close_id": f"close_{pos.position_id}_{exit_time.strftime('%Y%m%dT%H%M%SZ')}",
            "position_id": pos.position_id,
            "inst_id": pos.inst_id,
            "coin": pos.coin,
            "strategy": pos.strategy,
            "family_key": pos.family_key,
            "side": "short",
            "signal_id": pos.signal_id,
            "signal_time": pos.signal_time,
            "entry_time": pos.entry_time,
            "exit_time": iso(exit_time),
            "planned_exit_time": pos.planned_exit_time,
            "hold_hours_actual": hold_actual_hours,
            "raw_entry_close": pos.raw_entry_close,
            "raw_exit_close": raw_exit_close,
            "entry_price": pos.entry_price,
            "exit_price": exit_price,
            "entry_slip_bps": pos.entry_slip_bps,
            "exit_slip_bps": pos.exit_slip_bps,
            "fee_bps_total": pos.fee_bps_total,
            "stress_extra_bps": pos.stress_extra_bps,
            "gross_ret": gross_ret,
            "realistic_net_ret": realistic_net_ret,
            "stress_net_ret": stress_net_ret,
            "net_ret": realistic_net_ret,
            "notional": pos.notional,
            "pnl": pnl,
            "stress_pnl": stress_pnl,
            "equity_before": equity_before,
            "equity_after": self.equity,
            "L_hours": pos.L_hours,
            "rel_threshold_bps": pos.rel_threshold_bps,
            "coin_threshold_bps": pos.coin_threshold_bps,
            "signal_close": pos.signal_close,
            "coin_ret_bps": pos.coin_ret_bps,
            "market_ret_bps": pos.market_ret_bps,
            "rel_ret_bps": pos.rel_ret_bps,
            "signal_vol_quote": pos.signal_vol_quote,
            "signal_range_bps": pos.signal_range_bps,
            "entry_vol_quote": pos.entry_vol_quote,
            "entry_range_bps": pos.entry_range_bps,
            "exit_vol_quote": float(exit_row.get("volCcyQuote", np.nan)),
            "exit_range_bps": float(exit_row.get("range_bps", np.nan)),
        }

        append_csv(self.closed_path, row)
        self.open_positions.pop(pos.position_id, None)

        print(
            f"[CLOSE] {pos.coin} exit_bar={iso(exit_time)} net={realistic_net_ret:.4f} "
            f"pnl={pnl:.4f} equity={self.equity:.2f}"
        )

    def process_pending_and_open(self) -> None:
        for p in list(self.pending.values()):
            self.process_pending_entry(p)

        for pos in list(self.open_positions.values()):
            self.process_exit(pos)

    def write_heartbeat(self) -> None:
        append_csv(self.heartbeat_path, {
            "log_time": iso(utc_now()),
            "equity": self.equity,
            "open_positions": len(self.open_positions),
            "pending_entries": len(self.pending),
            "closed_count": self.closed_count,
            "errors": self.errors,
            "coins": len(self.coins),
            "strategy": self.strategy,
            "last_full_scan_target_time": self.last_full_scan_target_time,
            "require_global_gate": self.args.require_global_gate,
        })

    def print_status(self) -> None:
        print(
            f"[{iso(utc_now())}] equity={self.equity:.2f} "
            f"open={len(self.open_positions)} pending={len(self.pending)} "
            f"closed={self.closed_count} errors={self.errors} "
            f"last_scan={self.last_full_scan_target_time or 'none'}"
        )

    def run_once(self) -> None:
        self.process_pending_and_open()
        self.scan_signals()
        self.process_pending_and_open()
        self.write_heartbeat()
        self.save_state()
        self.print_status()

    def run_forever(self) -> None:
        print("=" * 100)
        print("MARKET-RELATIVE EXTREME REVERSION SHORT - LIVE PAPER LOGGER")
        print("=" * 100)
        print("REAL ORDERS: NO")
        print("OKX endpoint:", f"{API_BASE}{CANDLES_ENDPOINT}")
        print("out_dir:", self.out_dir)
        print("coins:", len(self.coins), ",".join(self.coins[:20]) + ("..." if len(self.coins) > 20 else ""))
        print("signal:")
        print(f"  1H L={self.args.L_hours} | coin_ret >= {self.args.coin_threshold_bps} bps")
        print(f"  rel_ret = coin_ret - median_market_ret >= {self.args.rel_threshold_bps} bps")
        print(f"  entry_delay={self.args.entry_delay_hours}h hold={self.args.hold_hours}h side=short")
        print("risk:")
        print("  paper_fraction=", self.args.paper_fraction)
        print("  max_positions=", self.args.max_positions)
        print("  min_signal_vol_quote=", self.args.min_signal_vol_quote)
        print("  min_entry_vol_quote=", self.args.min_entry_vol_quote)
        print("  max_signal_range_bps=", self.args.max_signal_range_bps)
        print("  max_entry_range_bps=", self.args.max_entry_range_bps)
        print("  require_global_gate=", self.args.require_global_gate)
        print("=" * 100)

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


def main() -> None:
    ap = argparse.ArgumentParser(description="Live paper logger for market-relative extreme reversion short family.")
    ap.add_argument("--base_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
    ap.add_argument("--out_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\live_market_relative_extreme_reversion_short_paper")
    ap.add_argument("--start", default="2025-04-30")
    ap.add_argument("--end", default="2026-04-30")
    ap.add_argument("--coins", default="AUTO")
    ap.add_argument("--exclude", default="BTC,ETH")

    ap.add_argument("--start_equity", type=float, default=1000.0)
    ap.add_argument("--paper_fraction", type=float, default=0.05)
    ap.add_argument("--sizing_contract", default="", help="Path to position_sizing_contract.json")
    ap.add_argument("--default_notional", type=float, default=50.0, help="Fallback paper notional if sizing contract is missing")
    ap.add_argument("--max_positions", type=int, default=3)

    ap.add_argument("--L_hours", type=int, default=6)
    ap.add_argument("--rel_threshold_bps", type=float, default=600.0)
    ap.add_argument("--coin_threshold_bps", type=float, default=300.0)
    ap.add_argument("--entry_delay_hours", type=int, default=2)
    ap.add_argument("--hold_hours", type=int, default=24)

    ap.add_argument("--min_market_coins", type=int, default=20)
    ap.add_argument("--min_signal_vol_quote", type=float, default=100000.0)
    ap.add_argument("--min_entry_vol_quote", type=float, default=100000.0)
    ap.add_argument("--max_signal_range_bps", type=float, default=2000.0)
    ap.add_argument("--max_entry_range_bps", type=float, default=2000.0)

    ap.add_argument("--entry_slip_bps", type=float, default=25.0)
    ap.add_argument("--exit_slip_bps", type=float, default=25.0)
    ap.add_argument("--fee_bps_total", type=float, default=25.0)
    ap.add_argument("--stress_extra_bps", type=float, default=50.0)

    ap.add_argument("--candle_limit", type=int, default=120)
    ap.add_argument("--scan_after_minute", type=int, default=5)
    ap.add_argument("--pending_max_wait_minutes", type=int, default=30)
    ap.add_argument("--request_sleep", type=float, default=0.03)
    ap.add_argument("--poll_seconds", type=float, default=60.0)
    ap.add_argument("--force_scan_now", action="store_true")

    # EDGE_FACTORY_REQUIRE_GLOBAL_GATE_DEFAULT_TRUE_V1
    ap.add_argument("--require_global_gate", dest="require_global_gate", action="store_true", default=True)
    ap.add_argument("--no_global_gate", dest="require_global_gate", action="store_false")
    ap.add_argument("--global_gate_path", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM\global_gate_decisions.csv")
    args = ap.parse_args()

    logger = MarketRelativePaperLogger(args)
    logger.run_forever()


if __name__ == "__main__":
    main()
