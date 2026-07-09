"""
Gate-aware live paper logger for the old_short strategy family that polls OKX 1-minute candles,
checks the global gate decision file before each entry, and logs simulated short trades to the
MASTER_UPPER_SYSTEM paper run directory without placing real orders.
"""
from __future__ import annotations

import argparse, csv, json, time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import numpy as np
import pandas as pd
from sizing_contract_runtime import resolve_family_notional

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

def discover_coins(base: Path, out_dir: Path, coins_arg: str, exclude: set[str]) -> list[str]:
    arg = coins_arg.strip()
    if arg and arg.upper() not in {"AUTO", "AUTO_OLD", "ALL"}:
        return sorted({x.strip().upper() for x in arg.split(",") if x.strip()} - exclude)

    universe_file = out_dir / "old_short_coin_universe.txt"
    if universe_file.exists():
        txt = universe_file.read_text(encoding="utf-8", errors="ignore")
        coins = {x.strip().upper() for x in txt.replace("\n", ",").split(",") if x.strip()}
        return sorted(coins - exclude)

    # Try previous config produced by this or other old logger.
    for name in ["old_short_gate_aware_config.json", "strategy_config.json"]:
        cfg_path = out_dir / name
        if cfg_path.exists():
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                if isinstance(cfg, dict) and isinstance(cfg.get("coins"), list):
                    return sorted({str(c).upper() for c in cfg["coins"]} - exclude)
                if isinstance(cfg, dict):
                    coins = set()
                    for k, v in cfg.items():
                        if isinstance(v, dict):
                            coins.add(str(v.get("coin", k)).upper())
                        else:
                            coins.add(str(k).upper())
                    if coins:
                        return sorted(coins - exclude)
            except Exception:
                pass

    coins = []
    for d in base.iterdir():
        if not d.is_dir() or d.name.startswith("_"):
            continue
        coin = d.name.upper()
        if coin in exclude:
            continue
        inst = f"{coin}-USDT-SWAP"
        if list((d / "raw").glob(f"**/{inst}_1m_*.csv")):
            coins.append(coin)
    return sorted(set(coins) - exclude)

def okx_fetch_1m_candles(inst_id: str, limit: int, retries: int = 3, sleep_sec: float = 0.08) -> pd.DataFrame:
    url = f"{API_BASE}{CANDLES_ENDPOINT}?{urlencode({'instId': inst_id, 'bar': '1m', 'limit': str(limit)})}"
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers={"User-Agent": "edge-lab-old-short-gate-aware/1.0", "Accept": "application/json"})
            with urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
            js = json.loads(raw)
            if str(js.get("code")) != "0":
                raise RuntimeError(f"OKX code={js.get('code')} msg={js.get('msg')}")
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
                df["volCcyQuote"] = (df["volCcy"] if "volCcy" in df.columns else df["vol"]) * df["close"]
            close = df["close"].astype(float)
            df["ret1_bps"] = close.pct_change() * 10000.0
            df["ret3_bps"] = (close / close.shift(3) - 1.0) * 10000.0
            df["ret5_bps"] = (close / close.shift(5) - 1.0) * 10000.0
            df["ret60_bps"] = (close / close.shift(60) - 1.0) * 10000.0
            df["range_bps"] = (df["high"] - df["low"]) / df["open"].replace(0, np.nan) * 10000.0
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
    family_key: str
    family: str
    strategy: str
    side: str
    signal_time: str
    target_entry_time: str
    planned_exit_time: str
    entry_delay_minutes: int
    hold_minutes: int
    signal_close: float
    signal_ret1_bps: float
    signal_ret3_bps: float
    signal_ret5_bps: float
    signal_ret60_bps: float
    signal_vol_quote: float
    signal_range_bps: float
    created_at: str

@dataclass
class OpenPosition:
    position_id: str
    inst_id: str
    coin: str
    family_key: str
    family: str
    strategy: str
    side: str
    signal_id: str
    signal_time: str
    entry_time: str
    planned_exit_time: str
    entry_delay_minutes: int
    hold_minutes: int
    raw_entry_close: float
    entry_price: float
    notional: float
    equity_before: float
    signal_close: float
    signal_ret1_bps: float
    signal_ret3_bps: float
    signal_ret5_bps: float
    signal_ret60_bps: float
    signal_vol_quote: float
    signal_range_bps: float
    entry_vol_quote: float
    entry_range_bps: float
    entry_slip_bps: float
    exit_slip_bps: float
    fee_bps_total: float
    stress_extra_bps: float

class OldShortGateAwareLogger:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.base_dir = Path(args.base_dir)
        self.out_dir = Path(args.out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.family_key = "old_short"
        exclude = {x.strip().upper() for x in args.exclude.split(",") if x.strip()}
        self.coins = discover_coins(self.base_dir, self.out_dir, args.coins, exclude)

        self.signals_path = self.out_dir / "signals.csv"
        self.pending_path = self.out_dir / "pending_entries.csv"
        self.open_path = self.out_dir / "open_positions.csv"
        self.closed_path = self.out_dir / "closed_trades.csv"
        self.rejected_path = self.out_dir / "rejected_entries.csv"
        self.errors_path = self.out_dir / "errors.csv"
        self.heartbeat_path = self.out_dir / "heartbeat.csv"
        self.state_path = self.out_dir / "state.json"
        self.config_path = self.out_dir / "old_short_gate_aware_config.json"

        self.pending: dict[str, PendingEntry] = {}
        self.open_positions: dict[str, OpenPosition] = {}
        self.seen_signal_ids: set[str] = set()
        self.equity = float(args.start_equity)
        self.closed_count = 0
        self.errors = 0

        self.config_path.write_text(json.dumps({"family_key": self.family_key, "coins": self.coins, "settings": vars(args)}, indent=2), encoding="utf-8")
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
                    signal_id=str(r["signal_id"]), inst_id=str(r["inst_id"]), coin=str(r["coin"]),
                    family_key=str(r.get("family_key", self.family_key)), family=str(r.get("family", "")),
                    strategy=str(r.get("strategy", r.get("family", ""))), side=str(r.get("side", "short")),
                    signal_time=str(r["signal_time"]), target_entry_time=str(r["target_entry_time"]),
                    planned_exit_time=str(r["planned_exit_time"]), entry_delay_minutes=int(r.get("entry_delay_minutes", self.args.entry_delay_minutes)),
                    hold_minutes=int(r.get("hold_minutes", self.args.hold_minutes)), signal_close=float(r["signal_close"]),
                    signal_ret1_bps=float(r.get("signal_ret1_bps", np.nan)), signal_ret3_bps=float(r.get("signal_ret3_bps", np.nan)),
                    signal_ret5_bps=float(r.get("signal_ret5_bps", np.nan)), signal_ret60_bps=float(r.get("signal_ret60_bps", np.nan)),
                    signal_vol_quote=float(r.get("signal_vol_quote", np.nan)), signal_range_bps=float(r.get("signal_range_bps", np.nan)),
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
                    family_key=str(r.get("family_key", self.family_key)), family=str(r.get("family", "")),
                    strategy=str(r.get("strategy", r.get("family", ""))), side=str(r.get("side", "short")),
                    signal_id=str(r["signal_id"]), signal_time=str(r["signal_time"]), entry_time=str(r["entry_time"]),
                    planned_exit_time=str(r["planned_exit_time"]), entry_delay_minutes=int(r.get("entry_delay_minutes", self.args.entry_delay_minutes)),
                    hold_minutes=int(r.get("hold_minutes", self.args.hold_minutes)), raw_entry_close=float(r["raw_entry_close"]),
                    entry_price=float(r["entry_price"]), notional=float(r["notional"]), equity_before=float(r["equity_before"]),
                    signal_close=float(r["signal_close"]), signal_ret1_bps=float(r.get("signal_ret1_bps", np.nan)),
                    signal_ret3_bps=float(r.get("signal_ret3_bps", np.nan)), signal_ret5_bps=float(r.get("signal_ret5_bps", np.nan)),
                    signal_ret60_bps=float(r.get("signal_ret60_bps", np.nan)), signal_vol_quote=float(r.get("signal_vol_quote", np.nan)),
                    signal_range_bps=float(r.get("signal_range_bps", np.nan)), entry_vol_quote=float(r.get("entry_vol_quote", np.nan)),
                    entry_range_bps=float(r.get("entry_range_bps", np.nan)), entry_slip_bps=float(r.get("entry_slip_bps", self.args.entry_slip_bps)),
                    exit_slip_bps=float(r.get("exit_slip_bps", self.args.exit_slip_bps)), fee_bps_total=float(r.get("fee_bps_total", self.args.fee_bps_total)),
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
            row = asdict(p); row["status"] = "pending"; pending_rows.append(row)
        write_csv_rows(self.pending_path, pending_rows, fieldnames=[
            "status", "signal_id", "inst_id", "coin", "family_key", "family", "strategy", "side",
            "signal_time", "target_entry_time", "planned_exit_time", "entry_delay_minutes", "hold_minutes",
            "signal_close", "signal_ret1_bps", "signal_ret3_bps", "signal_ret5_bps", "signal_ret60_bps",
            "signal_vol_quote", "signal_range_bps", "created_at"
        ])
        open_rows = [asdict(p) for p in self.open_positions.values()]
        write_csv_rows(self.open_path, open_rows, fieldnames=[
            "position_id", "inst_id", "coin", "family_key", "family", "strategy", "side", "signal_id",
            "signal_time", "entry_time", "planned_exit_time", "entry_delay_minutes", "hold_minutes",
            "raw_entry_close", "entry_price", "notional", "equity_before", "signal_close",
            "signal_ret1_bps", "signal_ret3_bps", "signal_ret5_bps", "signal_ret60_bps", "signal_vol_quote",
            "signal_range_bps", "entry_vol_quote", "entry_range_bps", "entry_slip_bps", "exit_slip_bps",
            "fee_bps_total", "stress_extra_bps"
        ])
        self.state_path.write_text(json.dumps({
            "updated_at": iso(utc_now()), "equity": self.equity, "open": len(self.open_positions),
            "pending": len(self.pending), "closed_count": self.closed_count, "errors": self.errors,
            "coins": len(self.coins), "require_global_gate": self.args.require_global_gate
        }, indent=2), encoding="utf-8")

    def log_error(self, where: str, inst_id: str, e: Exception) -> None:
        self.errors += 1
        append_csv(self.errors_path, {"log_time": iso(utc_now()), "where": where, "inst_id": inst_id, "error_type": type(e).__name__, "error": str(e)})

    def get_candle_at(self, df: pd.DataFrame, target: pd.Timestamp) -> pd.Series | None:
        target = pd.Timestamp(target).tz_convert("UTC")
        m = df["time"] == target
        if not m.any(): return None
        return df.loc[m].iloc[-1]

    def scan_coin(self, coin: str) -> None:
        inst = f"{coin}-USDT-SWAP"
        try:
            df = okx_fetch_1m_candles(inst, limit=self.args.candle_limit, sleep_sec=self.args.request_sleep)
        except Exception as e:
            self.log_error("scan_fetch", inst, e); return
        if df.empty or len(df) < 70: return

        now = utc_now()
        x = df.loc[df["time"] >= now - pd.Timedelta(minutes=self.args.signal_backfill_minutes)].copy()
        if x.empty: return

        signals = []
        blowoff = x.loc[(x["ret60_bps"] >= self.args.blowoff_ret60_bps) & (x["ret3_bps"] <= self.args.blowoff_ret3_max_bps) & (x["ret1_bps"] <= self.args.ret1_max_bps)].copy()
        if not blowoff.empty:
            blowoff["family"] = "blowoff_short"; signals.append(blowoff)
        meanrev = x.loc[(x["ret5_bps"] >= self.args.meanrev_ret5_bps) & (x["ret1_bps"] <= self.args.ret1_max_bps)].copy()
        if not meanrev.empty:
            meanrev["family"] = "mean_reversion_short"; signals.append(meanrev)
        if not signals: return

        sigs = pd.concat(signals, ignore_index=True).drop_duplicates(["time", "family"]).sort_values("time")
        for _, sig in sigs.iterrows():
            signal_time = pd.Timestamp(sig["time"]).tz_convert("UTC")
            family = str(sig["family"])
            signal_id = f"{coin}_{family}_{signal_time.strftime('%Y%m%dT%H%M%SZ')}"
            if signal_id in self.seen_signal_ids:
                continue
            self.seen_signal_ids.add(signal_id)
            signal_vol = float(sig.get("volCcyQuote", np.nan))
            signal_range = float(sig.get("range_bps", np.nan))
            if not np.isfinite(signal_vol) or signal_vol < self.args.min_signal_vol_quote:
                append_csv(self.rejected_path, {"type": "signal_reject", "reason": "low_signal_vol_quote", "log_time": iso(now), "signal_id": signal_id, "coin": coin, "family": family, "signal_time": iso(signal_time), "signal_vol_quote": signal_vol, "signal_range_bps": signal_range}); continue
            if np.isfinite(signal_range) and signal_range > self.args.max_signal_range_bps:
                append_csv(self.rejected_path, {"type": "signal_reject", "reason": "high_signal_range_bps", "log_time": iso(now), "signal_id": signal_id, "coin": coin, "family": family, "signal_time": iso(signal_time), "signal_vol_quote": signal_vol, "signal_range_bps": signal_range}); continue

            target_entry = signal_time + pd.Timedelta(minutes=self.args.entry_delay_minutes)
            planned_exit = target_entry + pd.Timedelta(minutes=self.args.hold_minutes)
            p = PendingEntry(
                signal_id=signal_id, inst_id=inst, coin=coin, family_key=self.family_key, family=family,
                strategy=family, side="short", signal_time=iso(signal_time), target_entry_time=iso(target_entry),
                planned_exit_time=iso(planned_exit), entry_delay_minutes=self.args.entry_delay_minutes,
                hold_minutes=self.args.hold_minutes, signal_close=float(sig["close"]), signal_ret1_bps=float(sig.get("ret1_bps", np.nan)),
                signal_ret3_bps=float(sig.get("ret3_bps", np.nan)), signal_ret5_bps=float(sig.get("ret5_bps", np.nan)),
                signal_ret60_bps=float(sig.get("ret60_bps", np.nan)), signal_vol_quote=signal_vol,
                signal_range_bps=signal_range, created_at=iso(now)
            )
            self.pending[p.signal_id] = p
            append_csv(self.signals_path, {"type": "signal_pending_short", **asdict(p)})
            print(f"[SIGNAL] {coin} {family} signal={iso(signal_time)} entry={p.target_entry_time}")

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
        m = (g.get("family_key", "").astype(str) == self.family_key) & (g.get("signal_id", "").astype(str) == signal_id)
        if not m.any():
            return "WAIT", "gate_signal_missing"
        row = g.loc[m].iloc[-1]
        decision, reason = str(row.get("decision", "")).upper(), str(row.get("reason", ""))
        if decision == "ALLOW": return "ALLOW", reason or "gate_allow"
        if decision == "BLOCK": return "BLOCK", reason or "gate_block"
        return "WAIT", f"gate_unknown_decision_{decision}"

    def process_pending_entry(self, p: PendingEntry) -> None:
        now = utc_now()
        target = pd.Timestamp(p.target_entry_time).tz_convert("UTC")
        if now < target + pd.Timedelta(minutes=1):
            return

        decision, reason = self.global_gate_decision(p.signal_id)
        if decision == "WAIT":
            if now > target + pd.Timedelta(minutes=self.args.pending_max_wait_minutes):
                append_csv(self.rejected_path, {"type": "entry_reject", "reason": f"global_gate_timeout_{reason}", "log_time": iso(now), **asdict(p)})
                self.pending.pop(p.signal_id, None)
            return
        if decision == "BLOCK":
            append_csv(self.rejected_path, {"type": "entry_reject", "reason": f"global_gate_block_{reason}", "log_time": iso(now), **asdict(p)})
            self.pending.pop(p.signal_id, None)
            return

        try:
            df = okx_fetch_1m_candles(p.inst_id, limit=self.args.candle_limit, sleep_sec=self.args.request_sleep)
        except Exception as e:
            self.log_error("pending_fetch", p.inst_id, e)
            append_csv(self.rejected_path, {"type": "entry_reject", "reason": "allow_open_failed_fetch_error", "log_time": iso(now), **asdict(p), "gate_reason": reason, "error_type": type(e).__name__, "error": str(e)})
            self.pending.pop(p.signal_id, None)
            return
        entry = self.get_candle_at(df, target)
        if entry is None:
            append_csv(self.rejected_path, {"type": "entry_reject", "reason": "allow_open_failed_price_missing", "log_time": iso(now), **asdict(p), "gate_reason": reason, "fetched_rows": len(df), "target_entry_time_checked": iso(target)})
            self.pending.pop(p.signal_id, None)
            return

        try:
            raw_entry = float(entry["close"])
        except Exception as e:
            append_csv(self.rejected_path, {"type": "entry_reject", "reason": "allow_open_failed_column_missing", "log_time": iso(now), **asdict(p), "gate_reason": reason, "missing_column": "close", "error_type": type(e).__name__, "error": str(e)})
            self.pending.pop(p.signal_id, None)
            return
        if not np.isfinite(raw_entry):
            append_csv(self.rejected_path, {"type": "entry_reject", "reason": "allow_open_failed_price_missing", "log_time": iso(now), **asdict(p), "gate_reason": reason, "raw_entry_close": raw_entry})
            self.pending.pop(p.signal_id, None)
            return
        entry_vol = float(entry.get("volCcyQuote", np.nan))
        entry_range = float(entry.get("range_bps", np.nan))
        if not np.isfinite(entry_vol) or entry_vol < self.args.min_entry_vol_quote:
            append_csv(self.rejected_path, {"type": "entry_reject", "reason": "low_entry_vol_quote", "log_time": iso(now), **asdict(p), "raw_entry_close": raw_entry, "entry_vol_quote": entry_vol, "entry_range_bps": entry_range}); self.pending.pop(p.signal_id, None); return
        if np.isfinite(entry_range) and entry_range > self.args.max_entry_range_bps:
            append_csv(self.rejected_path, {"type": "entry_reject", "reason": "high_entry_range_bps", "log_time": iso(now), **asdict(p), "raw_entry_close": raw_entry, "entry_vol_quote": entry_vol, "entry_range_bps": entry_range}); self.pending.pop(p.signal_id, None); return
        if len(self.open_positions) >= self.args.max_positions:
            append_csv(self.rejected_path, {"type": "entry_reject", "reason": "local_max_positions", "log_time": iso(now), **asdict(p), "raw_entry_close": raw_entry}); self.pending.pop(p.signal_id, None); return
        if any(pos.coin == p.coin for pos in self.open_positions.values()):
            append_csv(self.rejected_path, {"type": "entry_reject", "reason": "local_same_coin_overlap", "log_time": iso(now), **asdict(p), "raw_entry_close": raw_entry}); self.pending.pop(p.signal_id, None); return

        entry_price = raw_entry * (1.0 - self.args.entry_slip_bps / 10000.0)
        default_notional = self.equity * self.args.paper_fraction
        try:
            notional = resolve_family_notional(
                "old_short",
                default_notional=default_notional,
                sizing_contract_path=self.args.sizing_contract,
                base_equity=self.equity,
            )
        except Exception as e:
            append_csv(self.rejected_path, {"type": "entry_reject", "reason": "allow_open_failed_sizing_missing", "log_time": iso(now), **asdict(p), "gate_reason": reason, "raw_entry_close": raw_entry, "error_type": type(e).__name__, "error": str(e), "sizing_contract": self.args.sizing_contract})
            self.pending.pop(p.signal_id, None)
            return
        if not np.isfinite(notional) or notional <= 0:
            append_csv(self.rejected_path, {"type": "entry_reject", "reason": "allow_open_failed_sizing_missing", "log_time": iso(now), **asdict(p), "gate_reason": reason, "raw_entry_close": raw_entry, "notional": notional, "sizing_contract": self.args.sizing_contract})
            self.pending.pop(p.signal_id, None)
            return
        position_id = f"{p.coin}_{p.family}_{target.strftime('%Y%m%dT%H%M%SZ')}"
        pos = OpenPosition(
            position_id=position_id, inst_id=p.inst_id, coin=p.coin, family_key=p.family_key, family=p.family,
            strategy=p.strategy, side="short", signal_id=p.signal_id, signal_time=p.signal_time, entry_time=iso(target),
            planned_exit_time=p.planned_exit_time, entry_delay_minutes=p.entry_delay_minutes, hold_minutes=p.hold_minutes,
            raw_entry_close=raw_entry, entry_price=entry_price, notional=notional, equity_before=self.equity,
            signal_close=p.signal_close, signal_ret1_bps=p.signal_ret1_bps, signal_ret3_bps=p.signal_ret3_bps,
            signal_ret5_bps=p.signal_ret5_bps, signal_ret60_bps=p.signal_ret60_bps, signal_vol_quote=p.signal_vol_quote,
            signal_range_bps=p.signal_range_bps, entry_vol_quote=entry_vol, entry_range_bps=entry_range,
            entry_slip_bps=self.args.entry_slip_bps, exit_slip_bps=self.args.exit_slip_bps,
            fee_bps_total=self.args.fee_bps_total, stress_extra_bps=self.args.stress_extra_bps,
        )
        self.open_positions[pos.position_id] = pos
        self.pending.pop(p.signal_id, None)
        append_csv(self.signals_path, {"type": "open_short", **asdict(pos), "global_gate_reason": reason})
        print(f"[OPEN] {p.coin} {p.family} entry={iso(target)} notional={notional:.2f} gate={reason}")

    def process_exit(self, pos: OpenPosition) -> None:
        now = utc_now()
        exit_time = pd.Timestamp(pos.planned_exit_time).tz_convert("UTC")
        if now < exit_time + pd.Timedelta(minutes=1):
            return
        try:
            df = okx_fetch_1m_candles(pos.inst_id, limit=self.args.candle_limit, sleep_sec=self.args.request_sleep)
        except Exception as e:
            self.log_error("exit_fetch", pos.inst_id, e); return
        row = self.get_candle_at(df, exit_time)
        if row is None: return

        raw_exit = float(row["close"])
        exit_price = raw_exit * (1.0 + pos.exit_slip_bps / 10000.0)
        gross_ret = pos.entry_price / exit_price - 1.0
        realistic_net_ret = gross_ret - pos.fee_bps_total / 10000.0
        stress_net_ret = realistic_net_ret - pos.stress_extra_bps / 10000.0
        pnl = pos.notional * realistic_net_ret
        stress_pnl = pos.notional * stress_net_ret
        equity_before = self.equity
        self.equity += pnl
        self.closed_count += 1

        append_csv(self.closed_path, {
            "close_id": f"close_{pos.position_id}_{exit_time.strftime('%Y%m%dT%H%M%SZ')}",
            "position_id": pos.position_id, "inst_id": pos.inst_id, "coin": pos.coin, "family_key": pos.family_key,
            "family": pos.family, "strategy": pos.strategy, "side": "short", "signal_id": pos.signal_id,
            "signal_time": pos.signal_time, "entry_time": pos.entry_time, "exit_time": iso(exit_time),
            "planned_exit_time": pos.planned_exit_time, "hold_minutes_actual": (exit_time - pd.Timestamp(pos.entry_time)).total_seconds() / 60.0,
            "raw_entry_close": pos.raw_entry_close, "raw_exit_close": raw_exit, "entry_price": pos.entry_price,
            "exit_price": exit_price, "entry_slip_bps": pos.entry_slip_bps, "exit_slip_bps": pos.exit_slip_bps,
            "fee_bps_total": pos.fee_bps_total, "stress_extra_bps": pos.stress_extra_bps, "gross_ret": gross_ret,
            "realistic_net_ret": realistic_net_ret, "stress_net_ret": stress_net_ret, "net_ret": realistic_net_ret,
            "notional": pos.notional, "pnl": pnl, "stress_pnl": stress_pnl, "equity_before": equity_before,
            "equity_after": self.equity, "signal_ret1_bps": pos.signal_ret1_bps, "signal_ret3_bps": pos.signal_ret3_bps,
            "signal_ret5_bps": pos.signal_ret5_bps, "signal_ret60_bps": pos.signal_ret60_bps,
            "signal_vol_quote": pos.signal_vol_quote, "signal_range_bps": pos.signal_range_bps,
            "entry_vol_quote": pos.entry_vol_quote, "entry_range_bps": pos.entry_range_bps
        })
        self.open_positions.pop(pos.position_id, None)
        print(f"[CLOSE] {pos.coin} {pos.family} exit={iso(exit_time)} net={realistic_net_ret:.4f} pnl={pnl:.4f} equity={self.equity:.2f}")

    def run_once(self) -> None:
        for p in list(self.pending.values()):
            self.process_pending_entry(p)
        for pos in list(self.open_positions.values()):
            self.process_exit(pos)
        for i, coin in enumerate(self.coins, 1):
            self.scan_coin(coin)
            if i % 25 == 0: print(f"  scanned {i}/{len(self.coins)} coins")
            time.sleep(self.args.request_sleep)
        for p in list(self.pending.values()):
            self.process_pending_entry(p)
        self.write_heartbeat(); self.save_state(); self.print_status()

    def write_heartbeat(self) -> None:
        append_csv(self.heartbeat_path, {
            "log_time": iso(utc_now()), "equity": self.equity, "open_positions": len(self.open_positions),
            "pending_entries": len(self.pending), "closed_count": self.closed_count, "errors": self.errors,
            "coins": len(self.coins), "strategy_family": "old_short_gate_aware", "require_global_gate": self.args.require_global_gate
        })

    def print_status(self) -> None:
        print(f"[{iso(utc_now())}] equity={self.equity:.2f} open={len(self.open_positions)} pending={len(self.pending)} closed={self.closed_count} errors={self.errors}")

    def run_forever(self) -> None:
        print("=" * 100)
        print("OLD SHORT / BLOWOFF + MEAN-REVERSION SHORT - GATE-AWARE LIVE PAPER LOGGER")
        print("=" * 100)
        print("REAL ORDERS: NO")
        print("out_dir:", self.out_dir)
        print("coins:", len(self.coins), ",".join(self.coins[:30]) + ("..." if len(self.coins) > 30 else ""))
        print("require_global_gate:", self.args.require_global_gate)
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
    ap = argparse.ArgumentParser(description="Gate-aware old short live paper logger.")
    ap.add_argument("--base_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
    ap.add_argument("--out_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\live_blowoff_short_paper_realistic")
    ap.add_argument("--coins", default="AUTO_OLD")
    ap.add_argument("--exclude", default="BTC,ETH")
    ap.add_argument("--start_equity", type=float, default=1000.0)
    ap.add_argument("--paper_fraction", type=float, default=0.05)
    ap.add_argument("--sizing_contract", default="", help="Path to position_sizing_contract.json")
    ap.add_argument("--default_notional", type=float, default=50.0, help="Fallback paper notional if sizing contract is missing")
    ap.add_argument("--max_positions", type=int, default=3)
    ap.add_argument("--blowoff_ret60_bps", type=float, default=500.0)
    ap.add_argument("--blowoff_ret3_max_bps", type=float, default=-75.0)
    ap.add_argument("--meanrev_ret5_bps", type=float, default=300.0)
    ap.add_argument("--ret1_max_bps", type=float, default=0.0)
    ap.add_argument("--entry_delay_minutes", type=int, default=2)
    ap.add_argument("--hold_minutes", type=int, default=120)
    ap.add_argument("--min_signal_vol_quote", type=float, default=100000.0)
    ap.add_argument("--min_entry_vol_quote", type=float, default=100000.0)
    ap.add_argument("--max_signal_range_bps", type=float, default=1000.0)
    ap.add_argument("--max_entry_range_bps", type=float, default=1000.0)
    ap.add_argument("--entry_slip_bps", type=float, default=25.0)
    ap.add_argument("--exit_slip_bps", type=float, default=25.0)
    ap.add_argument("--fee_bps_total", type=float, default=25.0)
    ap.add_argument("--stress_extra_bps", type=float, default=50.0)
    ap.add_argument("--candle_limit", type=int, default=220)
    ap.add_argument("--signal_backfill_minutes", type=int, default=8)
    ap.add_argument("--pending_max_wait_minutes", type=int, default=10)
    ap.add_argument("--request_sleep", type=float, default=0.03)
    ap.add_argument("--poll_seconds", type=float, default=60.0)
    # EDGE_FACTORY_REQUIRE_GLOBAL_GATE_DEFAULT_TRUE_V1
    ap.add_argument("--require_global_gate", dest="require_global_gate", action="store_true", default=True)
    ap.add_argument("--no_global_gate", dest="require_global_gate", action="store_false")
    ap.add_argument("--global_gate_path", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM\global_gate_decisions.csv")
    args = ap.parse_args()
    OldShortGateAwareLogger(args).run_forever()

if __name__ == "__main__":
    main()
