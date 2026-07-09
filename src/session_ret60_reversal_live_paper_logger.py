"""
Live paper logger for the session_ret60_reversal strategy family that polls OKX 1-minute candles,
detects 60-minute return reversal signals, and logs simulated short entries and exits to the
MASTER_UPPER_SYSTEM paper run directory without placing real orders.
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

API_BASE = "https://www.okx.com"
CANDLES_ENDPOINT = "/api/v5/market/candles"


def now_utc() -> pd.Timestamp:
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


def okx_fetch_1m_candles(inst_id: str, limit: int = 300, retries: int = 3, sleep_sec: float = 0.35) -> pd.DataFrame:
    params = {"instId": inst_id, "bar": "1m", "limit": str(limit)}
    url = f"{API_BASE}{CANDLES_ENDPOINT}?{urlencode(params)}"
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers={"User-Agent": "edge-lab-session-paper-logger/1.0", "Accept": "application/json"})
            with urlopen(req, timeout=15) as resp:
                js = json.loads(resp.read().decode("utf-8"))
            if str(js.get("code")) != "0":
                raise RuntimeError(f"OKX code={js.get('code')} msg={js.get('msg')} body={js}")
            data = js.get("data", [])
            if not data:
                return pd.DataFrame()
            rows = []
            for r in data:
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
            df = df.dropna(subset=["time", "open", "high", "low", "close"]).drop_duplicates("time").sort_values("time").reset_index(drop=True)
            df = df.loc[df["confirm"].astype(str) == "1"].copy()
            if "volCcyQuote" not in df.columns or df["volCcyQuote"].isna().all():
                if "volCcy" in df.columns and not df["volCcy"].isna().all():
                    df["volCcyQuote"] = df["volCcy"] * df["close"]
                else:
                    df["volCcyQuote"] = df["vol"] * df["close"]
            df["range_bps"] = (df["high"] - df["low"]) / df["open"].replace(0, np.nan) * 10000.0
            df["ret1_bps"] = df["close"].pct_change() * 10000.0
            df["ret60_bps"] = (df["close"] / df["close"].shift(60) - 1.0) * 10000.0
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
    family: str
    signal_time: str
    target_entry_time: str
    planned_exit_time: str
    signal_ret60_bps: float
    signal_ret1_bps: float
    signal_close: float
    signal_vol_quote: float
    signal_range_bps: float
    created_at: str


@dataclass
class OpenPosition:
    position_id: str
    inst_id: str
    coin: str
    strategy: str
    family: str
    signal_time: str
    entry_time: str
    planned_exit_time: str
    raw_entry_close: float
    entry_price: float
    notional: float
    equity_before: float
    signal_ret60_bps: float
    signal_ret1_bps: float
    signal_close: float
    signal_vol_quote: float
    signal_range_bps: float
    entry_vol_quote: float
    entry_range_bps: float
    entry_slip_bps: float
    exit_slip_bps: float
    fee_bps_total: float
    stress_extra_bps: float


class SessionPaperLogger:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.base_dir = Path(args.base_dir)
        self.out_dir = Path(args.out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.strategy = "session_ret60_reversal_short_h8_m100_hold720"
        self.family = "session_ret60_reversal_short"
        self.signals_path = self.out_dir / "signals.csv"
        self.pending_path = self.out_dir / "pending_entries.csv"
        self.open_path = self.out_dir / "open_positions.csv"
        self.closed_path = self.out_dir / "closed_trades.csv"
        self.rejected_path = self.out_dir / "rejected_entries.csv"
        self.heartbeat_path = self.out_dir / "heartbeat.csv"
        self.errors_path = self.out_dir / "errors.csv"
        self.state_path = self.out_dir / "state.json"
        exclude = {x.strip().upper() for x in args.exclude.split(",") if x.strip()}
        self.coins = discover_coins(self.base_dir, args.start, args.end, args.coins, exclude)
        self.pending: dict[str, PendingEntry] = {}
        self.open_positions: dict[str, OpenPosition] = {}
        self.seen_signal_ids: set[str] = set()
        self.equity = float(args.start_equity)
        self.errors = 0
        self.closed_count = 0
        self.load_state()

    def load_state(self) -> None:
        for r in read_csv_records(self.signals_path):
            sid = str(r.get("signal_id", ""))
            if sid:
                self.seen_signal_ids.add(sid)
        for r in read_csv_records(self.pending_path):
            if str(r.get("status", "pending")) not in {"pending", ""}:
                continue
            try:
                p = PendingEntry(
                    signal_id=str(r["signal_id"]), inst_id=str(r["inst_id"]), coin=str(r["coin"]),
                    strategy=str(r.get("strategy", self.strategy)), family=str(r.get("family", self.family)),
                    signal_time=str(r["signal_time"]), target_entry_time=str(r["target_entry_time"]), planned_exit_time=str(r["planned_exit_time"]),
                    signal_ret60_bps=float(r["signal_ret60_bps"]), signal_ret1_bps=float(r.get("signal_ret1_bps", np.nan)),
                    signal_close=float(r["signal_close"]), signal_vol_quote=float(r["signal_vol_quote"]), signal_range_bps=float(r["signal_range_bps"]),
                    created_at=str(r.get("created_at", "")),
                )
                self.pending[p.signal_id] = p
                self.seen_signal_ids.add(p.signal_id)
            except Exception:
                continue
        for r in read_csv_records(self.open_path):
            try:
                pos = OpenPosition(
                    position_id=str(r["position_id"]), inst_id=str(r["inst_id"]), coin=str(r["coin"]),
                    strategy=str(r.get("strategy", self.strategy)), family=str(r.get("family", self.family)),
                    signal_time=str(r["signal_time"]), entry_time=str(r["entry_time"]), planned_exit_time=str(r["planned_exit_time"]),
                    raw_entry_close=float(r["raw_entry_close"]), entry_price=float(r["entry_price"]), notional=float(r["notional"]), equity_before=float(r["equity_before"]),
                    signal_ret60_bps=float(r["signal_ret60_bps"]), signal_ret1_bps=float(r.get("signal_ret1_bps", np.nan)), signal_close=float(r.get("signal_close", np.nan)),
                    signal_vol_quote=float(r["signal_vol_quote"]), signal_range_bps=float(r["signal_range_bps"]), entry_vol_quote=float(r["entry_vol_quote"]), entry_range_bps=float(r["entry_range_bps"]),
                    entry_slip_bps=float(r.get("entry_slip_bps", self.args.entry_slip_bps)), exit_slip_bps=float(r.get("exit_slip_bps", self.args.exit_slip_bps)),
                    fee_bps_total=float(r.get("fee_bps_total", self.args.fee_bps_total)), stress_extra_bps=float(r.get("stress_extra_bps", self.args.stress_extra_bps)),
                )
                self.open_positions[pos.position_id] = pos
            except Exception:
                continue
        closed = read_csv_records(self.closed_path)
        if closed:
            self.closed_count = len(closed)
            try:
                self.equity = float(closed[-1]["equity_after"])
            except Exception:
                pass

    def save_state(self) -> None:
        write_csv_rows(self.pending_path, [{**asdict(p), "status": "pending"} for p in self.pending.values()], [
            "status", "signal_id", "inst_id", "coin", "strategy", "family", "signal_time", "target_entry_time", "planned_exit_time",
            "signal_ret60_bps", "signal_ret1_bps", "signal_close", "signal_vol_quote", "signal_range_bps", "created_at",
        ])
        write_csv_rows(self.open_path, [asdict(p) for p in self.open_positions.values()], [
            "position_id", "inst_id", "coin", "strategy", "family", "signal_time", "entry_time", "planned_exit_time",
            "raw_entry_close", "entry_price", "notional", "equity_before", "signal_ret60_bps", "signal_ret1_bps", "signal_close",
            "signal_vol_quote", "signal_range_bps", "entry_vol_quote", "entry_range_bps", "entry_slip_bps", "exit_slip_bps",
            "fee_bps_total", "stress_extra_bps",
        ])
        self.state_path.write_text(json.dumps({
            "updated_at": iso(now_utc()), "equity": self.equity, "pending_count": len(self.pending),
            "open_count": len(self.open_positions), "closed_count": self.closed_count, "errors": self.errors,
            "strategy": self.strategy,
        }, indent=2), encoding="utf-8")

    def log_error(self, where: str, inst_id: str, error: Exception) -> None:
        self.errors += 1
        append_csv(self.errors_path, {"log_time": iso(now_utc()), "where": where, "inst_id": inst_id, "error_type": type(error).__name__, "error": str(error)})

    @staticmethod
    def get_candle_at(df: pd.DataFrame, target_time: pd.Timestamp) -> pd.Series | None:
        target_time = pd.Timestamp(target_time).tz_convert("UTC")
        if df.empty:
            return None
        m = df["time"] == target_time
        if not m.any():
            return None
        return df.loc[m].iloc[-1]

    def should_scan_all_now(self) -> bool:
        n = now_utc()
        return int(n.hour) == self.args.signal_hour_utc and 1 <= int(n.minute) <= self.args.signal_scan_until_minute

    def scan_signals_for_coin(self, coin: str) -> None:
        inst_id = f"{coin}-USDT-SWAP"
        try:
            df = okx_fetch_1m_candles(inst_id, limit=self.args.candle_limit, sleep_sec=self.args.request_sleep)
        except Exception as e:
            self.log_error("scan_signals_fetch", inst_id, e)
            return
        if df.empty or len(df) < 70:
            return
        n = now_utc()
        min_time = n - pd.Timedelta(hours=self.args.signal_backfill_hours)
        sig_rows = df.loc[(df["time"] >= min_time) & (df["time"].dt.hour == self.args.signal_hour_utc) & (df["time"].dt.minute == 0)].copy()
        for _, sig in sig_rows.iterrows():
            sig_time = pd.Timestamp(sig["time"]).tz_convert("UTC")
            signal_id = f"{coin}_{self.strategy}_{sig_time.strftime('%Y%m%dT%H%M%SZ')}"
            if signal_id in self.seen_signal_ids:
                continue
            self.seen_signal_ids.add(signal_id)
            prev = self.get_candle_at(df, sig_time - pd.Timedelta(minutes=60))
            if prev is None:
                append_csv(self.rejected_path, {"type": "signal_reject", "reason": "missing_ret60_history", "log_time": iso(n), "signal_id": signal_id, "inst_id": inst_id, "coin": coin, "signal_time": iso(sig_time)})
                continue
            signal_close = float(sig["close"])
            prev_close = float(prev["close"])
            if prev_close <= 0 or signal_close <= 0:
                continue
            ret60_bps = (signal_close / prev_close - 1.0) * 10000.0
            ret1_bps = float(sig.get("ret1_bps", np.nan))
            sig_vol = float(sig.get("volCcyQuote", np.nan))
            sig_range = float(sig.get("range_bps", np.nan))
            if ret60_bps < self.args.move_bps:
                continue
            if not np.isfinite(sig_vol) or sig_vol < self.args.min_signal_vol_quote:
                append_csv(self.rejected_path, {"type": "signal_reject", "reason": "low_signal_vol_quote", "log_time": iso(n), "signal_id": signal_id, "inst_id": inst_id, "coin": coin, "signal_time": iso(sig_time), "signal_ret60_bps": ret60_bps, "signal_vol_quote": sig_vol, "signal_range_bps": sig_range})
                continue
            if np.isfinite(sig_range) and sig_range > self.args.max_signal_range_bps:
                append_csv(self.rejected_path, {"type": "signal_reject", "reason": "high_signal_range_bps", "log_time": iso(n), "signal_id": signal_id, "inst_id": inst_id, "coin": coin, "signal_time": iso(sig_time), "signal_ret60_bps": ret60_bps, "signal_vol_quote": sig_vol, "signal_range_bps": sig_range})
                continue
            target_entry_time = sig_time + pd.Timedelta(minutes=self.args.entry_delay_minutes)
            planned_exit_time = target_entry_time + pd.Timedelta(minutes=self.args.hold_minutes)
            p = PendingEntry(signal_id, inst_id, coin, self.strategy, self.family, iso(sig_time), iso(target_entry_time), iso(planned_exit_time), ret60_bps, ret1_bps, signal_close, sig_vol, sig_range, iso(n))
            self.pending[signal_id] = p
            append_csv(self.signals_path, {"type": "signal_pending_short", **asdict(p)})
            print(f"[SIGNAL] {coin} signal={iso(sig_time)} ret60={ret60_bps:.1f} entry={iso(target_entry_time)}")

    def process_pending_entry(self, p: PendingEntry) -> None:
        target_entry_time = pd.Timestamp(p.target_entry_time).tz_convert("UTC")
        n = now_utc()
        if n < target_entry_time + pd.Timedelta(minutes=1):
            return
        try:
            df = okx_fetch_1m_candles(p.inst_id, limit=self.args.candle_limit, sleep_sec=self.args.request_sleep)
        except Exception as e:
            self.log_error("pending_entry_fetch", p.inst_id, e)
            return
        er = self.get_candle_at(df, target_entry_time)
        if er is None:
            return
        raw_entry_close = float(er["close"])
        entry_vol = float(er.get("volCcyQuote", np.nan))
        entry_range = float(er.get("range_bps", np.nan))
        reject_reason = None
        if not np.isfinite(entry_vol) or entry_vol < self.args.min_entry_vol_quote:
            reject_reason = "low_entry_vol_quote"
        elif np.isfinite(entry_range) and entry_range > self.args.max_entry_range_bps:
            reject_reason = "high_entry_range_bps"
        elif len(self.open_positions) >= self.args.max_positions:
            reject_reason = "max_positions"
        elif any(pos.coin == p.coin for pos in self.open_positions.values()):
            reject_reason = "same_coin_overlap"
        if reject_reason:
            append_csv(self.rejected_path, {"type": "entry_reject", "reason": reject_reason, "log_time": iso(n), **asdict(p), "entry_time": iso(target_entry_time), "raw_entry_close": raw_entry_close, "entry_vol_quote": entry_vol, "entry_range_bps": entry_range, "open_positions": len(self.open_positions)})
            self.pending.pop(p.signal_id, None)
            return
        entry_price = raw_entry_close * (1.0 - self.args.entry_slip_bps / 10000.0)
        notional = self.equity * self.args.paper_fraction
        position_id = f"{p.coin}_{self.strategy}_{target_entry_time.strftime('%Y%m%dT%H%M%SZ')}"
        pos = OpenPosition(position_id, p.inst_id, p.coin, p.strategy, p.family, p.signal_time, iso(target_entry_time), p.planned_exit_time, raw_entry_close, entry_price, notional, self.equity, p.signal_ret60_bps, p.signal_ret1_bps, p.signal_close, p.signal_vol_quote, p.signal_range_bps, entry_vol, entry_range, self.args.entry_slip_bps, self.args.exit_slip_bps, self.args.fee_bps_total, self.args.stress_extra_bps)
        self.open_positions[position_id] = pos
        self.pending.pop(p.signal_id, None)
        append_csv(self.signals_path, {"type": "open_short", **asdict(pos)})
        print(f"[OPEN] {p.coin} entry={iso(target_entry_time)} raw={raw_entry_close:.10g} notional={notional:.2f} exit={p.planned_exit_time}")

    def process_exit(self, pos: OpenPosition) -> None:
        exit_time = pd.Timestamp(pos.planned_exit_time).tz_convert("UTC")
        n = now_utc()
        if n < exit_time + pd.Timedelta(minutes=1):
            return
        try:
            df = okx_fetch_1m_candles(pos.inst_id, limit=self.args.candle_limit, sleep_sec=self.args.request_sleep)
        except Exception as e:
            self.log_error("exit_fetch", pos.inst_id, e)
            return
        xr = self.get_candle_at(df, exit_time)
        if xr is None:
            return
        raw_exit_close = float(xr["close"])
        exit_price = raw_exit_close * (1.0 + pos.exit_slip_bps / 10000.0)
        gross_ret = pos.entry_price / exit_price - 1.0
        realistic_net_ret = gross_ret - pos.fee_bps_total / 10000.0
        stress_net_ret = realistic_net_ret - pos.stress_extra_bps / 10000.0
        pnl = pos.notional * realistic_net_ret
        stress_pnl = pos.notional * stress_net_ret
        equity_before = self.equity
        self.equity += pnl
        self.closed_count += 1
        close_id = f"close_{pos.position_id}_{exit_time.strftime('%Y%m%dT%H%M%SZ')}"
        row = {"close_id": close_id, "position_id": pos.position_id, "inst_id": pos.inst_id, "coin": pos.coin, "strategy": pos.strategy, "family": pos.family, "signal_time": pos.signal_time, "entry_time": pos.entry_time, "exit_time": iso(exit_time), "planned_exit_time": pos.planned_exit_time, "hold_minutes_actual": (exit_time - pd.Timestamp(pos.entry_time)).total_seconds()/60.0, "raw_entry_close": pos.raw_entry_close, "raw_exit_close": raw_exit_close, "entry_price": pos.entry_price, "exit_price": exit_price, "entry_slip_bps": pos.entry_slip_bps, "exit_slip_bps": pos.exit_slip_bps, "fee_bps_total": pos.fee_bps_total, "stress_extra_bps": pos.stress_extra_bps, "gross_ret": gross_ret, "realistic_net_ret": realistic_net_ret, "stress_net_ret": stress_net_ret, "notional": pos.notional, "pnl": pnl, "stress_pnl": stress_pnl, "equity_before": equity_before, "equity_after": self.equity, "signal_ret60_bps": pos.signal_ret60_bps, "signal_ret1_bps": pos.signal_ret1_bps, "signal_close": pos.signal_close, "signal_vol_quote": pos.signal_vol_quote, "signal_range_bps": pos.signal_range_bps, "entry_vol_quote": pos.entry_vol_quote, "entry_range_bps": pos.entry_range_bps, "exit_vol_quote": float(xr.get("volCcyQuote", np.nan)), "exit_range_bps": float(xr.get("range_bps", np.nan))}
        append_csv(self.closed_path, row)
        self.open_positions.pop(pos.position_id, None)
        print(f"[CLOSE] {pos.coin} exit={iso(exit_time)} net={realistic_net_ret:.4f} pnl={pnl:.4f} equity={self.equity:.2f}")

    def process_pending_and_open(self) -> None:
        for p in list(self.pending.values()):
            self.process_pending_entry(p)
        for pos in list(self.open_positions.values()):
            self.process_exit(pos)

    def write_heartbeat(self) -> None:
        row = {"log_time": iso(now_utc()), "equity": self.equity, "open_positions": len(self.open_positions), "pending_entries": len(self.pending), "closed_count": self.closed_count, "errors": self.errors, "coins": len(self.coins), "strategy": self.strategy, "scan_window": self.should_scan_all_now()}
        append_csv(self.heartbeat_path, row)

    def run_once(self) -> None:
        self.process_pending_and_open()
        if self.should_scan_all_now() or self.args.force_scan_now:
            for i, coin in enumerate(self.coins, 1):
                self.scan_signals_for_coin(coin)
                if i % 25 == 0:
                    print(f"  scanned {i}/{len(self.coins)} coins")
                time.sleep(self.args.request_sleep)
            self.args.force_scan_now = False
        self.process_pending_and_open()
        self.write_heartbeat()
        self.save_state()
        print(f"[{iso(now_utc())}] equity={self.equity:.2f} open={len(self.open_positions)} pending={len(self.pending)} closed={self.closed_count} errors={self.errors} scan={'YES' if self.should_scan_all_now() else 'no'}")

    def run_forever(self) -> None:
        print("="*90)
        print("SESSION RET60 REVERSAL SHORT - REALISTIC LIVE PAPER LOGGER")
        print("="*90)
        print("REAL ORDERS: NO")
        print("OKX endpoint:", f"{API_BASE}{CANDLES_ENDPOINT}")
        print("out_dir:", self.out_dir)
        print("coins:", len(self.coins), ",".join(self.coins[:20]) + ("..." if len(self.coins) > 20 else ""))
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
        print("  fee_bps_total=", self.args.fee_bps_total)
        print("  stress_extra_bps=", self.args.stress_extra_bps)
        print("signal:")
        print(f"  UTC hour == {self.args.signal_hour_utc:02d}:00 AND ret60 >= {self.args.move_bps} bps")
        print(f"  short, entry_delay={self.args.entry_delay_minutes}m, hold={self.args.hold_minutes}m")
        print("="*90)
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
    ap = argparse.ArgumentParser(description="Live paper logger for session_ret60_reversal_short_h8_m100_hold720.")
    ap.add_argument("--base_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
    ap.add_argument("--out_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\live_session_ret60_reversal_short_paper")
    ap.add_argument("--start", default="2025-04-30")
    ap.add_argument("--end", default="2026-04-30")
    ap.add_argument("--coins", default="AUTO")
    ap.add_argument("--exclude", default="BTC,ETH")
    ap.add_argument("--start_equity", type=float, default=1000.0)
    ap.add_argument("--paper_fraction", type=float, default=0.05)
    ap.add_argument("--max_positions", type=int, default=5)
    ap.add_argument("--signal_hour_utc", type=int, default=8)
    ap.add_argument("--signal_scan_until_minute", type=int, default=20)
    ap.add_argument("--signal_backfill_hours", type=float, default=6.0)
    ap.add_argument("--move_bps", type=float, default=100.0)
    ap.add_argument("--entry_delay_minutes", type=int, default=2)
    ap.add_argument("--hold_minutes", type=int, default=720)
    ap.add_argument("--min_signal_vol_quote", type=float, default=100000.0)
    ap.add_argument("--min_entry_vol_quote", type=float, default=100000.0)
    ap.add_argument("--max_signal_range_bps", type=float, default=1500.0)
    ap.add_argument("--max_entry_range_bps", type=float, default=1500.0)
    ap.add_argument("--entry_slip_bps", type=float, default=25.0)
    ap.add_argument("--exit_slip_bps", type=float, default=25.0)
    ap.add_argument("--fee_bps_total", type=float, default=25.0)
    ap.add_argument("--stress_extra_bps", type=float, default=50.0)
    ap.add_argument("--candle_limit", type=int, default=300)
    ap.add_argument("--request_sleep", type=float, default=0.05)
    ap.add_argument("--poll_seconds", type=float, default=60.0)
    ap.add_argument("--force_scan_now", action="store_true", help="Scan recent candles once even outside UTC 08 window; useful for checking setup.")
    args = ap.parse_args()
    SessionPaperLogger(args).run_forever()


if __name__ == "__main__":
    main()
