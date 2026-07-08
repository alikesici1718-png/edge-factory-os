#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 SHADOW RUNTIME ENGINE BUILDER v1
===================================================

Purpose
-------
Build a sandbox-only ret60 shadow runtime engine after the shadow start gate blocked
because the generated adapter only had core/self-test functions.

This builder creates a runtime engine file that contains:
    - real shadow runtime entrypoint marker: --shadow_runtime
    - replay/runtime loop over candle-like CSV input
    - heartbeat JSON writer
    - native runtime log writer: ret60_shadow_native_events.csv
    - closed trade writer: ret60_shadow_closed_trades.csv
    - runtime state JSON writer
    - strict no-live/no-active-paper safety constants

It DOES NOT:
    - start shadow runtime
    - start active paper
    - start live
    - connect to exchange APIs
    - send orders
    - mutate active config
    - edit MASTER_UPPER_SYSTEM
    - edit position sizing contract
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - read latest shadow start gate decision
    - read latest preflight and adapter path
    - write ret60_shadow_runtime_engine.py
    - write manifest and reference-only self-test command

Run:
    python "C:\Users\alike\edge_factory_ret60_shadow_runtime_engine_builder.py"

Next safe step:
    runtime engine implementation audit, then preflight again, then shadow start gate again.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_CANDIDATE = "ret60_reversal_short"
RUNTIME_DIR_NAME = "paper_run_shadow_ret60_reversal_short"


@dataclass
class BuilderSource:
    name: str
    path: Optional[str]
    exists: bool
    status: str
    key_fields: Dict[str, Any]
    warnings: List[str]


@dataclass
class BuilderGate:
    gate_id: str
    category: str
    required_for_build: bool
    required_for_future_start: bool
    passed: bool
    status: str
    reason: str
    details: str


@dataclass
class RuntimeEngineManifest:
    candidate_key: str
    engine_version: str
    runtime_engine_path: str
    adapter_path: str
    sandbox_root: str
    expected_heartbeat_json: str
    expected_state_json: str
    expected_native_log_csv: str
    expected_closed_trades_csv: str
    supports_self_test: bool
    supports_replay_csv: bool
    supports_shadow_runtime_entrypoint: bool
    live_allowed: bool
    active_paper_allowed: bool
    mutates_active_config: bool
    generated_at: str


@dataclass
class BuilderState:
    generated_at: str
    workspace: str
    candidate: str
    output_dir: str
    builder_status: str
    runtime_engine_written: bool
    runtime_engine_path: Optional[str]
    adapter_path: Optional[str]
    sandbox_root: Optional[str]
    gates_passed_for_build: int
    gates_required_for_build: int
    gates_passed_for_future_start: int
    gates_required_for_future_start: int
    implementation_audit_required: bool
    preflight_required: bool
    manual_approval_required: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    next_action: str
    reasons: List[str]
    blockers: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def read_json_optional(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def latest_start_gate_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_shadow_start_gate", "ret60_shadow_start_gate_")
    if not d:
        return None
    p = d / "ret60_shadow_start_gate_state.json"
    return p if p.exists() else None


def latest_preflight_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_sandbox_preflight_gate", "ret60_sandbox_preflight_")
    if not d:
        return None
    p = d / "ret60_sandbox_preflight_state.json"
    return p if p.exists() else None


def latest_adapter_manifest(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_sandbox_logger_adapter_builder", "ret60_adapter_builder_")
    if not d:
        return None
    p = d / "ret60_sandbox_logger_adapter_manifest.json"
    return p if p.exists() else None


def load_sources(workspace: Path, start_gate: Optional[str], preflight: Optional[str], adapter_manifest: Optional[str]) -> List[BuilderSource]:
    sgp = Path(start_gate) if start_gate else latest_start_gate_state(workspace)
    pfp = Path(preflight) if preflight else latest_preflight_state(workspace)
    mfp = Path(adapter_manifest) if adapter_manifest else latest_adapter_manifest(workspace)

    sg = read_json_optional(sgp)
    pf = read_json_optional(pfp)
    mf = read_json_optional(mfp)

    sg_state = sg.get("state", {}) if isinstance(sg.get("state"), dict) else {}
    sg_decision = sg.get("decision", {}) if isinstance(sg.get("decision"), dict) else {}
    pf_state = pf.get("state", {}) if isinstance(pf.get("state"), dict) else {}
    pf_runtime = pf.get("runtime_plan", {}) if isinstance(pf.get("runtime_plan"), dict) else {}
    mf_state = mf.get("state", {}) if isinstance(mf.get("state"), dict) else {}

    return [
        BuilderSource(
            name="shadow_start_gate",
            path=str(sgp) if sgp else None,
            exists=bool(sgp and sgp.exists()),
            status=str(sg_state.get("decision_status") or sg_decision.get("decision_status") or "MISSING"),
            key_fields={
                "decision_status": sg_state.get("decision_status") or sg_decision.get("decision_status"),
                "approval_valid": sg_decision.get("approval_valid"),
                "preflight_valid": sg_decision.get("preflight_valid"),
                "runtime_engine_available": sg_decision.get("shadow_runtime_engine_available"),
                "start_reference_allowed": sg_decision.get("start_reference_allowed"),
                "active_paper_allowed": sg_decision.get("active_paper_allowed"),
                "live_allowed": sg_decision.get("live_allowed"),
            },
            warnings=[] if sgp and sgp.exists() else ["shadow start gate state missing"],
        ),
        BuilderSource(
            name="preflight",
            path=str(pfp) if pfp else None,
            exists=bool(pfp and pfp.exists()),
            status=str(pf_state.get("preflight_status") or "MISSING"),
            key_fields={
                "preflight_passed": pf_state.get("preflight_passed"),
                "implementation_audit_passed": pf_state.get("implementation_audit_passed"),
                "native_log_verified": pf_state.get("native_log_verified"),
                "shadow_start_allowed": pf_state.get("shadow_start_allowed"),
                "active_paper_allowed": pf_state.get("active_paper_allowed"),
                "live_allowed": pf_state.get("live_allowed"),
                "adapter_path": pf_runtime.get("adapter_path"),
                "sandbox_root": pf_runtime.get("sandbox_root"),
            },
            warnings=[] if pfp and pfp.exists() else ["preflight state missing"],
        ),
        BuilderSource(
            name="adapter_manifest",
            path=str(mfp) if mfp else None,
            exists=bool(mfp and mfp.exists()),
            status=str(mf_state.get("builder_status") or "MISSING"),
            key_fields={
                "adapter_written": mf_state.get("adapter_written"),
                "adapter_path": mf_state.get("adapter_path"),
                "shadow_start_allowed": mf_state.get("shadow_start_allowed"),
                "active_paper_allowed": mf_state.get("active_paper_allowed"),
                "live_allowed": mf_state.get("live_allowed"),
            },
            warnings=[] if mfp and mfp.exists() else ["adapter manifest missing"],
        ),
    ]


def src(sources: List[BuilderSource], name: str) -> BuilderSource:
    for s in sources:
        if s.name == name:
            return s
    return BuilderSource(name, None, False, "MISSING", {}, ["source not loaded"])


def engine_code() -> str:
    return r'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
RET60 SHADOW RUNTIME ENGINE v1
==============================

Sandbox-only runtime engine generated by edge_factory_ret60_shadow_runtime_engine_builder.py.

This file supports:
    --self_test
    --replay_csv <csv>
    --shadow_runtime <csv>

Important:
    --shadow_runtime is still file/replay based in v1. It does NOT connect to exchange APIs.
    Live/private API/order placement are forbidden.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


CANDIDATE_KEY = "ret60_reversal_short"
ENGINE_VERSION = "ret60_shadow_runtime_engine_v1"
SIDE = "short"
HOUR_UTC = 8
M_PARAM = 75
DELAY_MINUTES = 1
HOLD_MINUTES = 720
EXTRA_SLIP_BPS = 0

SANDBOX_ONLY = True
LIVE_ALLOWED = False
ACTIVE_PAPER_ALLOWED = False
ORDER_PLACEMENT_ALLOWED = False
PRIVATE_EXCHANGE_API_ALLOWED = False
MUTATES_ACTIVE_CONFIG = False

NATIVE_LOG_NAME = "ret60_shadow_native_events.csv"
CLOSED_TRADES_NAME = "ret60_shadow_closed_trades.csv"
HEARTBEAT_NAME = "ret60_shadow_heartbeat.json"
STATE_NAME = "ret60_shadow_runtime_state.json"

REQUIRED_INPUT_COLUMNS = ["symbol", "event_time", "close"]
REQUIRED_LOG_FIELDS = [
    "event_id", "candidate_key", "engine_version", "symbol", "side", "signal_time_utc",
    "hour_utc", "signal_ret60_bps", "ret60_rule_passed", "delay_minutes",
    "planned_entry_time_utc", "actual_paper_entry_time_utc", "entry_reference_price",
    "hold_minutes", "planned_exit_time_utc", "actual_paper_exit_time_utc", "exit_reference_price",
    "gross_return_bps_native", "fee_bps_assumption", "spread_bps_at_signal",
    "slippage_bps_assumption", "extra_slip_bps", "net_return_bps_native",
    "gross_pnl_usdt", "net_pnl_usdt", "notional_usdt", "source_candle_basis",
    "feature_calculation_version", "logger_version", "runtime_mode", "status"
]


def parse_utc(x: Any) -> datetime:
    if isinstance(x, datetime):
        dt = x
    else:
        s = str(x).strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def event_id(symbol: str, signal_time: datetime) -> str:
    raw = f"{CANDIDATE_KEY}|{symbol}|{iso_utc(signal_time)}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


def signal_ret60_bps(current_price: float, price_60m_ago: float) -> float:
    if current_price <= 0 or price_60m_ago <= 0:
        raise ValueError("prices must be positive")
    return (current_price / price_60m_ago - 1.0) * 10000.0


def short_gross_return_bps(entry_price: float, exit_price: float) -> float:
    if entry_price <= 0 or exit_price <= 0:
        raise ValueError("entry/exit prices must be positive")
    return (entry_price / exit_price - 1.0) * 10000.0


def net_bps(gross_bps: float, fee_bps: float, spread_bps: float, slippage_bps: float, extra_bps: float = EXTRA_SLIP_BPS) -> float:
    return float(gross_bps) - float(fee_bps) - float(spread_bps) - float(slippage_bps) - float(extra_bps)


def pnl_usdt(return_bps: float, notional_usdt: float) -> float:
    return float(notional_usdt) * float(return_bps) / 10000.0


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def append_csv(path: Path, row: Dict[str, Any], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            w.writeheader()
        w.writerow({k: row.get(k) for k in fields})


def write_heartbeat(out_dir: Path, status: str, counters: Dict[str, Any]) -> None:
    write_json(out_dir / HEARTBEAT_NAME, {
        "candidate_key": CANDIDATE_KEY,
        "engine_version": ENGINE_VERSION,
        "generated_at": iso_utc(datetime.now(timezone.utc)),
        "status": status,
        "counters": counters,
        "live_allowed": LIVE_ALLOWED,
        "active_paper_allowed": ACTIVE_PAPER_ALLOWED,
        "order_placement_allowed": ORDER_PLACEMENT_ALLOWED,
    })


def normalize_candles(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Accept common aliases.
    rename = {}
    for c in df.columns:
        low = str(c).lower()
        if low in {"timestamp", "time", "datetime", "open_time"} and "event_time" not in df.columns:
            rename[c] = "event_time"
        if low in {"inst_id", "inst", "ticker", "coin"} and "symbol" not in df.columns:
            rename[c] = "symbol"
        if low in {"close_price", "c"} and "close" not in df.columns:
            rename[c] = "close"
    if rename:
        df = df.rename(columns=rename)
    missing = [c for c in REQUIRED_INPUT_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"missing input columns: {missing}; required={REQUIRED_INPUT_COLUMNS}")
    df = df.copy()
    df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce", utc=True)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["symbol", "event_time", "close"])
    df = df[df["close"] > 0]
    df = df.sort_values(["symbol", "event_time"]).reset_index(drop=True)
    return df


def find_price_at_or_before(group: pd.DataFrame, ts: pd.Timestamp) -> Optional[float]:
    x = group[group["event_time"] <= ts]
    if x.empty:
        return None
    return float(x.iloc[-1]["close"])


def run_replay(
    input_csv: Path,
    out_dir: Path,
    notional_usdt: float = 50.0,
    fee_bps: float = 5.0,
    spread_bps: float = 2.0,
    slippage_bps: float = 3.0,
    runtime_mode: str = "shadow_replay",
    max_rows: Optional[int] = None,
) -> Dict[str, Any]:
    if runtime_mode.lower() == "live":
        raise RuntimeError("live runtime is forbidden")
    out_dir.mkdir(parents=True, exist_ok=True)
    df = normalize_candles(input_csv)
    if max_rows:
        df = df.head(int(max_rows)).copy()

    native_path = out_dir / NATIVE_LOG_NAME
    closed_path = out_dir / CLOSED_TRADES_NAME
    counters = {"rows": int(len(df)), "signals": 0, "closed": 0, "errors": 0}
    write_heartbeat(out_dir, "RUNNING", counters)

    for symbol, group in df.groupby("symbol", sort=False):
        group = group.sort_values("event_time").reset_index(drop=True)
        for _, row in group.iterrows():
            try:
                signal_time = row["event_time"].to_pydatetime()
                if signal_time.hour != HOUR_UTC:
                    continue
                current_price = float(row["close"])
                price_60 = find_price_at_or_before(group, pd.Timestamp(signal_time) - pd.Timedelta(minutes=60))
                if price_60 is None:
                    continue
                ret60 = signal_ret60_bps(current_price, price_60)
                if ret60 < M_PARAM:
                    continue
                entry_time = signal_time + timedelta(minutes=DELAY_MINUTES)
                exit_time = entry_time + timedelta(minutes=HOLD_MINUTES)
                entry_price = find_price_at_or_before(group, pd.Timestamp(entry_time))
                exit_price = find_price_at_or_before(group, pd.Timestamp(exit_time))
                if entry_price is None or exit_price is None:
                    continue
                gross = short_gross_return_bps(entry_price, exit_price)
                net = net_bps(gross, fee_bps, spread_bps, slippage_bps, EXTRA_SLIP_BPS)
                eid = event_id(str(symbol), signal_time)
                base = {
                    "event_id": eid,
                    "candidate_key": CANDIDATE_KEY,
                    "engine_version": ENGINE_VERSION,
                    "symbol": str(symbol),
                    "side": SIDE,
                    "signal_time_utc": iso_utc(signal_time),
                    "hour_utc": signal_time.hour,
                    "signal_ret60_bps": ret60,
                    "ret60_rule_passed": True,
                    "delay_minutes": DELAY_MINUTES,
                    "planned_entry_time_utc": iso_utc(entry_time),
                    "actual_paper_entry_time_utc": iso_utc(entry_time),
                    "entry_reference_price": entry_price,
                    "hold_minutes": HOLD_MINUTES,
                    "planned_exit_time_utc": iso_utc(exit_time),
                    "actual_paper_exit_time_utc": iso_utc(exit_time),
                    "exit_reference_price": exit_price,
                    "gross_return_bps_native": gross,
                    "fee_bps_assumption": fee_bps,
                    "spread_bps_at_signal": spread_bps,
                    "slippage_bps_assumption": slippage_bps,
                    "extra_slip_bps": EXTRA_SLIP_BPS,
                    "net_return_bps_native": net,
                    "gross_pnl_usdt": pnl_usdt(gross, notional_usdt),
                    "net_pnl_usdt": pnl_usdt(net, notional_usdt),
                    "notional_usdt": notional_usdt,
                    "source_candle_basis": "input_csv_close_1m_or_equivalent",
                    "feature_calculation_version": "ret60_bps_from_close_v1",
                    "logger_version": ENGINE_VERSION,
                    "runtime_mode": runtime_mode,
                    "status": "CLOSED",
                }
                append_csv(native_path, base, REQUIRED_LOG_FIELDS)
                append_csv(closed_path, base, REQUIRED_LOG_FIELDS)
                counters["signals"] += 1
                counters["closed"] += 1
            except Exception:
                counters["errors"] += 1
        write_heartbeat(out_dir, "RUNNING", counters)

    write_heartbeat(out_dir, "DONE", counters)
    state = {
        "candidate_key": CANDIDATE_KEY,
        "engine_version": ENGINE_VERSION,
        "runtime_mode": runtime_mode,
        "input_csv": str(input_csv),
        "out_dir": str(out_dir),
        "native_log_csv": str(native_path),
        "closed_trades_csv": str(closed_path),
        "heartbeat_json": str(out_dir / HEARTBEAT_NAME),
        "counters": counters,
        "live_allowed": LIVE_ALLOWED,
        "active_paper_allowed": ACTIVE_PAPER_ALLOWED,
        "order_placement_allowed": ORDER_PLACEMENT_ALLOWED,
        "finished_at": iso_utc(datetime.now(timezone.utc)),
    }
    write_json(out_dir / STATE_NAME, state)
    return state


def make_self_test_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    base = datetime(2026, 5, 10, 6, 0, tzinfo=timezone.utc)
    price = 100.0
    for i in range(16 * 60):
        t = base + timedelta(minutes=i)
        # Pump into hour 8 so ret60 >= 75, then drop later so short can close positive.
        if t.hour == 8:
            price += 0.05
        elif t.hour >= 9:
            price -= 0.02
        rows.append({"symbol": "TEST-USDT-SWAP", "event_time": iso_utc(t), "close": round(price, 6)})
    pd.DataFrame(rows).to_csv(path, index=False)


def self_test(out_dir: Path) -> Dict[str, Any]:
    sample = out_dir / "ret60_shadow_runtime_self_test_input.csv"
    make_self_test_csv(sample)
    result = run_replay(sample, out_dir, runtime_mode="self_test_shadow_runtime")
    ok = result["counters"]["closed"] > 0 and Path(result["native_log_csv"]).exists() and Path(result["closed_trades_csv"]).exists() and Path(result["heartbeat_json"]).exists()
    result["ok"] = bool(ok)
    write_json(out_dir / "ret60_shadow_runtime_self_test_result.json", result)
    return result


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Ret60 shadow runtime engine")
    p.add_argument("--self_test", action="store_true")
    p.add_argument("--replay_csv", default=None)
    p.add_argument("--shadow_runtime", default=None, help="File/replay-based shadow runtime input CSV. No exchange API.")
    p.add_argument("--out_dir", default=None)
    p.add_argument("--max_rows", type=int, default=None)
    p.add_argument("--notional_usdt", type=float, default=50.0)
    p.add_argument("--fee_bps", type=float, default=5.0)
    p.add_argument("--spread_bps", type=float, default=2.0)
    p.add_argument("--slippage_bps", type=float, default=3.0)
    return p


def main() -> int:
    args = build_arg_parser().parse_args()
    out_dir = Path(args.out_dir) if args.out_dir else Path.cwd() / "ret60_shadow_runtime_out"
    if args.self_test:
        result = self_test(out_dir)
        print("RET60 SHADOW RUNTIME ENGINE SELF TEST")
        print("=" * 80)
        print(f"ok: {result['ok']}")
        print(f"closed: {result['counters']['closed']}")
        print(f"native_log_csv: {result['native_log_csv']}")
        print(f"closed_trades_csv: {result['closed_trades_csv']}")
        print(f"heartbeat_json: {result['heartbeat_json']}")
        print("live_allowed: False")
        print("active_paper_allowed: False")
        return 0 if result["ok"] else 2

    input_csv = args.replay_csv or args.shadow_runtime
    if not input_csv:
        print("Runtime engine generated. No runtime executed. Use --self_test or --replay_csv/--shadow_runtime with a local CSV.")
        print("live_allowed: False")
        print("active_paper_allowed: False")
        return 0

    mode = "shadow_runtime_file_replay" if args.shadow_runtime else "shadow_replay"
    result = run_replay(
        Path(input_csv), out_dir,
        notional_usdt=args.notional_usdt,
        fee_bps=args.fee_bps,
        spread_bps=args.spread_bps,
        slippage_bps=args.slippage_bps,
        runtime_mode=mode,
        max_rows=args.max_rows,
    )
    print("RET60 SHADOW RUNTIME ENGINE")
    print("=" * 80)
    print(f"mode: {mode}")
    print(f"rows: {result['counters']['rows']}")
    print(f"signals: {result['counters']['signals']}")
    print(f"closed: {result['counters']['closed']}")
    print(f"errors: {result['counters']['errors']}")
    print(f"native_log_csv: {result['native_log_csv']}")
    print(f"closed_trades_csv: {result['closed_trades_csv']}")
    print(f"heartbeat_json: {result['heartbeat_json']}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def build_gates(sources: List[BuilderSource]) -> List[BuilderGate]:
    gates: List[BuilderGate] = []
    sg = src(sources, "shadow_start_gate")
    pf = src(sources, "preflight")
    mf = src(sources, "adapter_manifest")

    def add(gid: str, cat: str, build_req: bool, future_req: bool, passed: bool, reason: str, details: str = "") -> None:
        gates.append(BuilderGate(gid, cat, build_req, future_req, bool(passed), "PASS" if passed else "FAIL", reason, details))

    adapter_path = pf.key_fields.get("adapter_path") or mf.key_fields.get("adapter_path")
    add("start_gate_exists", "artifact", True, True, sg.exists, "start gate state must exist", str(sg.path))
    add("start_gate_blocked_runtime_missing", "state", True, True, sg.key_fields.get("decision_status") == "RET60_SHADOW_START_BLOCKED_RUNTIME_ENGINE_NOT_IMPLEMENTED", "previous start gate must block specifically because runtime engine is missing")
    add("approval_valid_at_start_gate", "approval", True, True, sg.key_fields.get("approval_valid") is True, "manual approval must be valid at start gate")
    add("preflight_valid_at_start_gate", "preflight", True, True, sg.key_fields.get("preflight_valid") is True, "preflight must be valid at start gate")
    add("preflight_exists", "artifact", True, True, pf.exists, "preflight state must exist")
    add("adapter_manifest_exists", "artifact", True, True, mf.exists, "adapter manifest must exist")
    add("adapter_file_exists", "adapter", True, True, bool(adapter_path and Path(str(adapter_path)).exists()), "adapter file must exist", str(adapter_path))
    add("active_paper_blocked", "safety", True, True, sg.key_fields.get("active_paper_allowed") is False and pf.key_fields.get("active_paper_allowed") is False and mf.key_fields.get("active_paper_allowed") is False, "active paper must remain blocked")
    add("live_blocked", "safety", True, True, sg.key_fields.get("live_allowed") is False and pf.key_fields.get("live_allowed") is False and mf.key_fields.get("live_allowed") is False, "live must remain blocked")
    add("future_engine_audit_not_done", "future", False, True, False, "future start requires runtime engine audit")
    add("future_preflight_not_redone", "future", False, True, False, "future start requires preflight after runtime engine build")
    return gates


def records_df(items: List[Any]) -> pd.DataFrame:
    rows = []
    for x in items:
        d = asdict(x)
        for k, v in list(d.items()):
            if isinstance(v, list):
                d[k] = " | ".join(str(i) for i in v)
            if isinstance(v, dict):
                d[k] = json.dumps(v, ensure_ascii=False, default=str)
        rows.append(d)
    return pd.DataFrame(rows)


def write_outputs(out_dir: Path, state: BuilderState, manifest: Optional[RuntimeEngineManifest], sources: List[BuilderSource], gates: List[BuilderGate], code: Optional[str]) -> None:
    if code and state.runtime_engine_path:
        write_text(Path(state.runtime_engine_path), code)

    payload = {
        "state": asdict(state),
        "manifest": asdict(manifest) if manifest else None,
        "sources": [asdict(s) for s in sources],
        "gates": [asdict(g) for g in gates],
    }
    write_json(out_dir / "ret60_shadow_runtime_engine_builder_state.json", payload)
    if manifest:
        write_json(out_dir / "ret60_shadow_runtime_engine_manifest.json", asdict(manifest))
    records_df(gates).to_csv(out_dir / "ret60_shadow_runtime_engine_builder_gates.csv", index=False)
    records_df(sources).to_csv(out_dir / "ret60_shadow_runtime_engine_builder_sources.csv", index=False)

    if state.runtime_engine_path:
        ref = f'''# REFERENCE ONLY - self-test only, not real shadow start
python "{state.runtime_engine_path}" --self_test --out_dir "{out_dir / 'runtime_engine_self_test'}"
'''
    else:
        ref = "# BLOCKED - runtime engine was not written\n"
    write_text(out_dir / "ret60_runtime_engine_self_test_REFERENCE_ONLY.ps1", ref)

    md = f"""# Ret60 Shadow Runtime Engine Builder

Status: **{state.builder_status}**

- Runtime engine written: `{state.runtime_engine_written}`
- Runtime engine path: `{state.runtime_engine_path}`
- Shadow start allowed: `False`
- Active paper allowed: `False`
- Live allowed: `False`

## Next action

`{state.next_action}`

## Blockers

```text
{chr(10).join(state.blockers) if state.blockers else 'none'}
```

This builder wrote code only. It did not start runtime.
"""
    write_text(out_dir / "ret60_shadow_runtime_engine_builder_report.md", md)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build ret60 shadow runtime engine")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--start_gate_state", default=None)
    p.add_argument("--preflight_state", default=None)
    p.add_argument("--adapter_manifest", default=None)
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_shadow_runtime_engine_builder"
    out_dir = out_root / f"ret60_runtime_engine_builder_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = load_sources(workspace, args.start_gate_state, args.preflight_state, args.adapter_manifest)
    gates = build_gates(sources)
    req_build = [g for g in gates if g.required_for_build]
    pass_build = [g for g in req_build if g.passed]
    req_future = [g for g in gates if g.required_for_future_start]
    pass_future = [g for g in req_future if g.passed]

    pf = src(sources, "preflight")
    mf = src(sources, "adapter_manifest")
    adapter_path = pf.key_fields.get("adapter_path") or mf.key_fields.get("adapter_path")
    sandbox_root = pf.key_fields.get("sandbox_root") or str(workspace / RUNTIME_DIR_NAME)
    warnings: List[str] = []
    for s in sources:
        warnings.extend([f"{s.name}: {w}" for w in s.warnings])

    can_build = len(pass_build) == len(req_build)
    blockers: List[str] = []
    reasons: List[str] = []
    manifest = None
    runtime_path = None
    code = None

    if can_build:
        runtime_path = out_dir / "ret60_shadow_runtime_engine.py"
        code = engine_code()
        manifest = RuntimeEngineManifest(
            candidate_key=DEFAULT_CANDIDATE,
            engine_version="ret60_shadow_runtime_engine_v1",
            runtime_engine_path=str(runtime_path),
            adapter_path=str(adapter_path),
            sandbox_root=str(sandbox_root),
            expected_heartbeat_json=str(Path(str(sandbox_root)) / "ret60_shadow_heartbeat.json"),
            expected_state_json=str(Path(str(sandbox_root)) / "ret60_shadow_runtime_state.json"),
            expected_native_log_csv=str(Path(str(sandbox_root)) / "ret60_shadow_native_events.csv"),
            expected_closed_trades_csv=str(Path(str(sandbox_root)) / "ret60_shadow_closed_trades.csv"),
            supports_self_test=True,
            supports_replay_csv=True,
            supports_shadow_runtime_entrypoint=True,
            live_allowed=False,
            active_paper_allowed=False,
            mutates_active_config=False,
            generated_at=datetime.now().isoformat(timespec="seconds"),
        )
        status = "RET60_SHADOW_RUNTIME_ENGINE_WRITTEN_NOT_APPROVED_TO_RUN"
        next_action = "RUN_RET60_SHADOW_RUNTIME_ENGINE_AUDIT_THEN_PREFLIGHT"
        reasons.append("all runtime-engine build gates passed")
        reasons.append("runtime engine source was written, but not executed")
    else:
        status = "RET60_SHADOW_RUNTIME_ENGINE_BUILD_BLOCKED"
        next_action = "REPAIR_FAILED_RUNTIME_ENGINE_BUILD_GATES"
        blockers.extend([f"{g.gate_id}: {g.reason} {g.details}" for g in req_build if not g.passed])

    missing_future = [g.gate_id for g in req_future if not g.passed]
    if missing_future:
        warnings.append("future start remains blocked by: " + ", ".join(missing_future))

    state = BuilderState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        candidate=DEFAULT_CANDIDATE,
        output_dir=str(out_dir),
        builder_status=status,
        runtime_engine_written=can_build,
        runtime_engine_path=str(runtime_path) if runtime_path else None,
        adapter_path=str(adapter_path) if adapter_path else None,
        sandbox_root=str(sandbox_root) if sandbox_root else None,
        gates_passed_for_build=len(pass_build),
        gates_required_for_build=len(req_build),
        gates_passed_for_future_start=len(pass_future),
        gates_required_for_future_start=len(req_future),
        implementation_audit_required=True,
        preflight_required=True,
        manual_approval_required=True,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        next_action=next_action,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
        hard_rules=[
            "Runtime engine builder never starts runtime.",
            "Runtime engine builder never starts active paper/live.",
            "Runtime engine builder never mutates active config.",
            "Runtime engine builder never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Generated runtime engine is file/replay based and forbids live/private API/order placement.",
            "Runtime engine must pass audit and preflight before any shadow start gate can allow a reference command.",
        ],
    )

    write_outputs(out_dir, state, manifest, sources, gates, code)

    print("EDGE FACTORY RET60 SHADOW RUNTIME ENGINE BUILDER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"candidate : {DEFAULT_CANDIDATE}")
    print(f"output_dir: {out_dir}")
    print(f"builder_status: {state.builder_status}")
    print(f"runtime_engine_written: {state.runtime_engine_written}")
    print(f"runtime_engine_path: {state.runtime_engine_path}")
    print(f"adapter_path: {state.adapter_path}")
    print(f"sandbox_root: {state.sandbox_root}")
    print(f"build_gates: {state.gates_passed_for_build}/{state.gates_required_for_build}")
    print(f"future_start_gates: {state.gates_passed_for_future_start}/{state.gates_required_for_future_start}")
    print("implementation_audit_required: True")
    print("preflight_required: True")
    print("manual_approval_required: True")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    if state.blockers:
        print("\nBLOCKERS\n" + "-" * 100)
        for b in state.blockers:
            print(f"- {b}")
    if state.warnings:
        print("\nWARNINGS\n" + "-" * 100)
        for w in state.warnings:
            print(f"- {w}")
    print("\nIMPORTANT\n" + "-" * 100)
    print("This module did not start shadow/active paper/live, did not run runtime, and did not mutate active config.")
    print("")
    print(f"Report : {out_dir / 'ret60_shadow_runtime_engine_builder_report.md'}")
    print(f"State  : {out_dir / 'ret60_shadow_runtime_engine_builder_state.json'}")
    print(f"Engine : {state.runtime_engine_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit

# ---- FORCED REAL ENTRYPOINT PATCH ----
if __name__ == "__main__":
    raise SystemExit(main())

