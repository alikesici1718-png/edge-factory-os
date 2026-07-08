#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "ret60_reversal_short"

ENGINE_CODE = r"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

CANDIDATE_KEY = "ret60_reversal_short"
ENGINE_VERSION = "ret60_shadow_runtime_engine_v2"
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

NATIVE_LOG = "ret60_shadow_native_events.csv"
CLOSED_LOG = "ret60_shadow_closed_trades.csv"
HEARTBEAT = "ret60_shadow_heartbeat.json"
STATE = "ret60_shadow_runtime_state.json"

FIELDS = [
    "event_id","candidate_key","engine_version","symbol","side","signal_time_utc",
    "hour_utc","signal_ret60_bps","ret60_rule_passed","delay_minutes",
    "planned_entry_time_utc","actual_paper_entry_time_utc","entry_reference_price",
    "hold_minutes","planned_exit_time_utc","actual_paper_exit_time_utc",
    "exit_reference_price","gross_return_bps_native","fee_bps_assumption",
    "spread_bps_at_signal","slippage_bps_assumption","extra_slip_bps",
    "net_return_bps_native","gross_pnl_usdt","net_pnl_usdt","notional_usdt",
    "source_candle_basis","feature_calculation_version","logger_version",
    "runtime_mode","status"
]

def iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def append_csv(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            w.writeheader()
        w.writerow({k: row.get(k) for k in FIELDS})

def heartbeat_writer(out_dir: Path, status: str, counters: Dict[str, Any]) -> None:
    write_json(out_dir / HEARTBEAT, {
        "candidate_key": CANDIDATE_KEY,
        "engine_version": ENGINE_VERSION,
        "status": status,
        "updated_at": iso(datetime.now(timezone.utc)),
        "counters": counters,
        "live_allowed": LIVE_ALLOWED,
        "active_paper_allowed": ACTIVE_PAPER_ALLOWED,
        "order_placement_allowed": ORDER_PLACEMENT_ALLOWED,
    })

def normalize_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    rename = {}
    for c in df.columns:
        low = str(c).lower()
        if low in {"time","timestamp","datetime","open_time"} and "event_time" not in df.columns:
            rename[c] = "event_time"
        if low in {"inst","inst_id","ticker","coin"} and "symbol" not in df.columns:
            rename[c] = "symbol"
        if low in {"c","close_price"} and "close" not in df.columns:
            rename[c] = "close"
    if rename:
        df = df.rename(columns=rename)

    missing = [x for x in ["symbol","event_time","close"] if x not in df.columns]
    if missing:
        raise ValueError(f"missing columns: {missing}")

    df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce", utc=True)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["symbol","event_time","close"])
    df = df[df["close"] > 0]
    return df.sort_values(["symbol","event_time"]).reset_index(drop=True)

def price_at_or_before(g: pd.DataFrame, ts: pd.Timestamp) -> Optional[float]:
    x = g[g["event_time"] <= ts]
    if x.empty:
        return None
    return float(x.iloc[-1]["close"])

def shadow_runtime_loop(input_csv: Path, out_dir: Path, runtime_mode: str, max_rows: Optional[int] = None) -> Dict[str, Any]:
    # markers for start gate: --shadow_runtime, shadow_runtime_loop, heartbeat, ret60_shadow_native_events.csv, closed_trades
    if runtime_mode.lower() == "live":
        raise RuntimeError("live runtime forbidden")

    out_dir.mkdir(parents=True, exist_ok=True)
    df = normalize_csv(input_csv)
    if max_rows:
        df = df.head(int(max_rows)).copy()

    counters = {"rows": int(len(df)), "signals": 0, "closed": 0, "errors": 0}
    heartbeat_writer(out_dir, "RUNNING", counters)

    for symbol, g in df.groupby("symbol", sort=False):
        g = g.sort_values("event_time").reset_index(drop=True)
        for _, r in g.iterrows():
            try:
                t = r["event_time"].to_pydatetime()
                if t.hour != HOUR_UTC:
                    continue

                current = float(r["close"])
                prior = price_at_or_before(g, pd.Timestamp(t) - pd.Timedelta(minutes=60))
                if prior is None:
                    continue

                signal_ret60_bps = (current / prior - 1.0) * 10000.0
                if signal_ret60_bps < M_PARAM:
                    continue

                entry_t = t + timedelta(minutes=DELAY_MINUTES)
                exit_t = entry_t + timedelta(minutes=HOLD_MINUTES)
                entry_price = price_at_or_before(g, pd.Timestamp(entry_t))
                exit_price = price_at_or_before(g, pd.Timestamp(exit_t))
                if entry_price is None or exit_price is None:
                    continue

                gross_bps = (entry_price / exit_price - 1.0) * 10000.0
                fee_bps = 5.0
                spread_bps = 2.0
                slippage_bps = 3.0
                net_bps = gross_bps - fee_bps - spread_bps - slippage_bps - EXTRA_SLIP_BPS
                notional = 50.0

                row = {
                    "event_id": f"{symbol}_{iso(t)}",
                    "candidate_key": CANDIDATE_KEY,
                    "engine_version": ENGINE_VERSION,
                    "symbol": symbol,
                    "side": SIDE,
                    "signal_time_utc": iso(t),
                    "hour_utc": t.hour,
                    "signal_ret60_bps": signal_ret60_bps,
                    "ret60_rule_passed": True,
                    "delay_minutes": DELAY_MINUTES,
                    "planned_entry_time_utc": iso(entry_t),
                    "actual_paper_entry_time_utc": iso(entry_t),
                    "entry_reference_price": entry_price,
                    "hold_minutes": HOLD_MINUTES,
                    "planned_exit_time_utc": iso(exit_t),
                    "actual_paper_exit_time_utc": iso(exit_t),
                    "exit_reference_price": exit_price,
                    "gross_return_bps_native": gross_bps,
                    "fee_bps_assumption": fee_bps,
                    "spread_bps_at_signal": spread_bps,
                    "slippage_bps_assumption": slippage_bps,
                    "extra_slip_bps": EXTRA_SLIP_BPS,
                    "net_return_bps_native": net_bps,
                    "gross_pnl_usdt": notional * gross_bps / 10000.0,
                    "net_pnl_usdt": notional * net_bps / 10000.0,
                    "notional_usdt": notional,
                    "source_candle_basis": "local_csv_close",
                    "feature_calculation_version": "ret60_close_v2",
                    "logger_version": ENGINE_VERSION,
                    "runtime_mode": runtime_mode,
                    "status": "CLOSED",
                }

                append_csv(out_dir / NATIVE_LOG, row)
                append_csv(out_dir / CLOSED_LOG, row)
                counters["signals"] += 1
                counters["closed"] += 1
            except Exception:
                counters["errors"] += 1

        heartbeat_writer(out_dir, "RUNNING", counters)

    heartbeat_writer(out_dir, "DONE", counters)
    state = {
        "candidate_key": CANDIDATE_KEY,
        "engine_version": ENGINE_VERSION,
        "runtime_mode": runtime_mode,
        "native_log_csv": str(out_dir / NATIVE_LOG),
        "closed_trades_csv": str(out_dir / CLOSED_LOG),
        "heartbeat_json": str(out_dir / HEARTBEAT),
        "state_json": str(out_dir / STATE),
        "counters": counters,
        "live_allowed": LIVE_ALLOWED,
        "active_paper_allowed": ACTIVE_PAPER_ALLOWED,
        "finished_at": iso(datetime.now(timezone.utc)),
    }
    write_json(out_dir / STATE, state)
    return state

def make_self_test_csv(path: Path) -> None:
    rows = []
    base = datetime(2026, 5, 10, 6, 0, tzinfo=timezone.utc)
    price = 100.0
    for i in range(16 * 60):
        t = base + timedelta(minutes=i)
        if t.hour == 8:
            price += 0.15
        elif t.hour >= 9:
            price -= 0.03
        rows.append({"symbol": "TEST-USDT-SWAP", "event_time": iso(t), "close": round(price, 6)})
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)

def self_test(out_dir: Path) -> Dict[str, Any]:
    inp = out_dir / "ret60_runtime_self_test_input.csv"
    make_self_test_csv(inp)
    r = shadow_runtime_loop(inp, out_dir, "self_test_shadow_runtime")
    r["ok"] = bool(r["counters"]["closed"] > 0 and Path(r["native_log_csv"]).exists() and Path(r["closed_trades_csv"]).exists() and Path(r["heartbeat_json"]).exists())
    write_json(out_dir / "ret60_shadow_runtime_self_test_result.json", r)
    return r

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self_test", action="store_true")
    ap.add_argument("--replay_csv")
    ap.add_argument("--shadow_runtime")
    ap.add_argument("--out_dir")
    ap.add_argument("--max_rows", type=int)
    args = ap.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else Path.cwd() / "ret60_shadow_runtime_out"

    if args.self_test:
        r = self_test(out_dir)
        print("RET60 SHADOW RUNTIME ENGINE SELF TEST")
        print("=" * 80)
        print(f"ok: {r['ok']}")
        print(f"closed: {r['counters']['closed']}")
        print(f"native_log_csv: {r['native_log_csv']}")
        print(f"closed_trades_csv: {r['closed_trades_csv']}")
        print(f"heartbeat_json: {r['heartbeat_json']}")
        print("live_allowed: False")
        print("active_paper_allowed: False")
        return 0 if r["ok"] else 2

    inp = args.shadow_runtime or args.replay_csv
    if not inp:
        print("RET60 shadow runtime engine generated. No runtime executed.")
        print("Use --self_test or --replay_csv/--shadow_runtime with local CSV.")
        print("live_allowed: False")
        print("active_paper_allowed: False")
        return 0

    mode = "shadow_runtime_file_replay" if args.shadow_runtime else "shadow_replay"
    r = shadow_runtime_loop(Path(inp), out_dir, mode, max_rows=args.max_rows)
    print("RET60 SHADOW RUNTIME ENGINE")
    print("=" * 80)
    print(f"mode: {mode}")
    print(f"rows: {r['counters']['rows']}")
    print(f"signals: {r['counters']['signals']}")
    print(f"closed: {r['counters']['closed']}")
    print(f"errors: {r['counters']['errors']}")
    print(f"native_log_csv: {r['native_log_csv']}")
    print(f"closed_trades_csv: {r['closed_trades_csv']}")
    print(f"heartbeat_json: {r['heartbeat_json']}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
"""

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=str(WORKSPACE))
    args = ap.parse_args()

    ws = Path(args.workspace)
    out_dir = ws / "edge_factory_ret60_shadow_runtime_engine_builder_v2" / f"ret60_runtime_engine_builder_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    sg_dir = latest_dir(ws / "edge_factory_ret60_shadow_start_gate", "ret60_shadow_start_gate_")
    pf_dir = latest_dir(ws / "edge_factory_ret60_sandbox_preflight_gate", "ret60_sandbox_preflight_")
    sg_path = sg_dir / "ret60_shadow_start_gate_state.json" if sg_dir else None
    pf_path = pf_dir / "ret60_sandbox_preflight_state.json" if pf_dir else None

    sg = read_json(sg_path)
    pf = read_json(pf_path)

    sg_state = sg.get("state", {})
    decision = sg.get("decision", {})
    pf_state = pf.get("state", {})
    runtime_plan = pf.get("runtime_plan", {})

    adapter_path = runtime_plan.get("adapter_path")
    sandbox_root = runtime_plan.get("sandbox_root") or str(ws / "paper_run_shadow_ret60_reversal_short")

    gates = [
        {"gate": "start_gate_exists", "passed": bool(sg_path and sg_path.exists()), "reason": str(sg_path)},
        {"gate": "blocked_runtime_missing", "passed": sg_state.get("decision_status") == "RET60_SHADOW_START_BLOCKED_RUNTIME_ENGINE_NOT_IMPLEMENTED", "reason": str(sg_state.get("decision_status"))},
        {"gate": "approval_valid", "passed": decision.get("approval_valid") is True, "reason": str(decision.get("approval_valid"))},
        {"gate": "preflight_valid", "passed": decision.get("preflight_valid") is True, "reason": str(decision.get("preflight_valid"))},
        {"gate": "preflight_exists", "passed": bool(pf_path and pf_path.exists()), "reason": str(pf_path)},
        {"gate": "adapter_exists", "passed": bool(adapter_path and Path(adapter_path).exists()), "reason": str(adapter_path)},
        {"gate": "active_paper_blocked", "passed": decision.get("active_paper_allowed") is False and pf_state.get("active_paper_allowed") is False, "reason": ""},
        {"gate": "live_blocked", "passed": decision.get("live_allowed") is False and pf_state.get("live_allowed") is False, "reason": ""},
    ]

    can_build = all(g["passed"] for g in gates)
    engine_path = out_dir / "ret60_shadow_runtime_engine.py"

    if can_build:
        engine_path.write_text(ENGINE_CODE, encoding="utf-8")
        status = "RET60_SHADOW_RUNTIME_ENGINE_WRITTEN_NOT_APPROVED_TO_RUN"
    else:
        status = "RET60_SHADOW_RUNTIME_ENGINE_BUILD_BLOCKED"

    state = {
        "candidate": CANDIDATE,
        "builder_status": status,
        "runtime_engine_written": can_build,
        "runtime_engine_path": str(engine_path) if can_build else None,
        "adapter_path": adapter_path,
        "sandbox_root": sandbox_root,
        "supports_self_test": True,
        "supports_replay_csv": True,
        "supports_shadow_runtime_entrypoint": True,
        "expected_heartbeat_json": str(Path(sandbox_root) / "ret60_shadow_heartbeat.json"),
        "expected_state_json": str(Path(sandbox_root) / "ret60_shadow_runtime_state.json"),
        "expected_native_log_csv": str(Path(sandbox_root) / "ret60_shadow_native_events.csv"),
        "expected_closed_trades_csv": str(Path(sandbox_root) / "ret60_shadow_closed_trades.csv"),
        "shadow_start_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "gates": gates,
    }

    write_json(out_dir / "ret60_shadow_runtime_engine_builder_v2_state.json", state)
    write_json(out_dir / "ret60_shadow_runtime_engine_manifest.json", state)

    ref = f'# REFERENCE ONLY - self-test only\npython "{engine_path}" --self_test --out_dir "{out_dir / "runtime_engine_self_test"}"\n'
    (out_dir / "ret60_runtime_engine_self_test_REFERENCE_ONLY.ps1").write_text(ref, encoding="utf-8")

    print("EDGE FACTORY RET60 SHADOW RUNTIME ENGINE BUILDER v2")
    print("=" * 100)
    print(f"workspace : {ws}")
    print(f"output_dir: {out_dir}")
    print(f"builder_status: {status}")
    print(f"runtime_engine_written: {can_build}")
    print(f"runtime_engine_path: {engine_path if can_build else None}")
    print(f"adapter_path: {adapter_path}")
    print(f"sandbox_root: {sandbox_root}")
    print(f"build_gates: {sum(1 for g in gates if g['passed'])}/{len(gates)}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")

    if not can_build:
        print()
        print("BLOCKERS")
        print("-" * 100)
        for g in gates:
            if not g["passed"]:
                print(f"- {g['gate']}: {g['reason']}")

    print()
    print(f"State : {out_dir / 'ret60_shadow_runtime_engine_builder_v2_state.json'}")
    print(f"Engine: {engine_path if can_build else None}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
