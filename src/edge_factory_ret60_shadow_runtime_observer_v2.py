#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "ret60_reversal_short"
SANDBOX_ROOT = WORKSPACE / "paper_run_shadow_ret60_reversal_short"

REQUIRED_FIELDS = [
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

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def csv_info(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "rows": 0,
            "required_fields_ok": False,
            "missing_fields": REQUIRED_FIELDS,
            "candidate_ok": False,
            "live_like_runtime_mode": False,
            "status_values": [],
        }

    try:
        df = pd.read_csv(path)
    except Exception as e:
        return {
            "exists": True,
            "rows": 0,
            "required_fields_ok": False,
            "missing_fields": REQUIRED_FIELDS,
            "candidate_ok": False,
            "live_like_runtime_mode": False,
            "status_values": [],
            "error": repr(e),
        }

    missing = [c for c in REQUIRED_FIELDS if c not in df.columns]
    runtime_modes = df["runtime_mode"].astype(str).unique().tolist() if "runtime_mode" in df.columns else []
    status_values = df["status"].astype(str).unique().tolist() if "status" in df.columns else []
    candidate_ok = bool("candidate_key" in df.columns and (df["candidate_key"].astype(str) == CANDIDATE).all())
    live_like = any("live" in str(x).lower() for x in runtime_modes)

    return {
        "exists": True,
        "rows": int(len(df)),
        "required_fields_ok": len(missing) == 0,
        "missing_fields": missing,
        "candidate_ok": candidate_ok,
        "runtime_modes": runtime_modes,
        "live_like_runtime_mode": live_like,
        "status_values": status_values,
        "net_pnl_sum": float(pd.to_numeric(df.get("net_pnl_usdt", pd.Series(dtype=float)), errors="coerce").sum()) if len(df) else 0.0,
        "net_bps_mean": float(pd.to_numeric(df.get("net_return_bps_native", pd.Series(dtype=float)), errors="coerce").mean()) if len(df) else 0.0,
    }

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_ret60_shadow_runtime_observer_v2" / f"ret60_shadow_runtime_observer_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    native_csv = SANDBOX_ROOT / "ret60_shadow_native_events.csv"
    closed_csv = SANDBOX_ROOT / "ret60_shadow_closed_trades.csv"
    heartbeat_json = SANDBOX_ROOT / "ret60_shadow_heartbeat.json"
    state_json = SANDBOX_ROOT / "ret60_shadow_runtime_state.json"

    native = csv_info(native_csv)
    closed = csv_info(closed_csv)
    heartbeat = read_json(heartbeat_json)
    runtime_state = read_json(state_json)

    gates = []

    def gate(name: str, passed: bool, reason: str = ""):
        gates.append({"gate": name, "passed": bool(passed), "reason": str(reason)})

    gate("sandbox_root_exists", SANDBOX_ROOT.exists(), SANDBOX_ROOT)
    gate("native_csv_exists", native["exists"], native_csv)
    gate("closed_csv_exists", closed["exists"], closed_csv)
    gate("heartbeat_json_exists", heartbeat_json.exists(), heartbeat_json)
    gate("runtime_state_json_exists", state_json.exists(), state_json)

    gate("native_rows_positive", native["rows"] > 0, native["rows"])
    gate("closed_rows_positive", closed["rows"] > 0, closed["rows"])
    gate("native_required_fields_ok", native["required_fields_ok"], native.get("missing_fields"))
    gate("closed_required_fields_ok", closed["required_fields_ok"], closed.get("missing_fields"))
    gate("native_candidate_ok", native["candidate_ok"], "")
    gate("closed_candidate_ok", closed["candidate_ok"], "")

    gate("native_no_live_runtime_mode", not native["live_like_runtime_mode"], native.get("runtime_modes"))
    gate("closed_no_live_runtime_mode", not closed["live_like_runtime_mode"], closed.get("runtime_modes"))

    gate("heartbeat_blocks_live", heartbeat.get("live_allowed") is False, heartbeat.get("live_allowed"))
    gate("heartbeat_blocks_active_paper", heartbeat.get("active_paper_allowed") is False, heartbeat.get("active_paper_allowed"))
    gate("state_blocks_live", runtime_state.get("live_allowed") is False, runtime_state.get("live_allowed"))
    gate("state_blocks_active_paper", runtime_state.get("active_paper_allowed") is False, runtime_state.get("active_paper_allowed"))

    gate("heartbeat_status_done_or_running", heartbeat.get("status") in {"DONE", "RUNNING"}, heartbeat.get("status"))
    gate("runtime_state_has_counters", isinstance(runtime_state.get("counters"), dict), runtime_state.get("counters"))

    passed = sum(1 for g in gates if g["passed"])
    total = len(gates)
    observer_ok = passed == total

    status = (
        "RET60_SHADOW_RUNTIME_OBSERVER_PASS_READY_FOR_DRIFT_MONITOR"
        if observer_ok
        else "RET60_SHADOW_RUNTIME_OBSERVER_BLOCKED"
    )

    result = {
        "candidate": CANDIDATE,
        "observer_status": status,
        "observer_passed": observer_ok,
        "sandbox_root": str(SANDBOX_ROOT),
        "native_csv": str(native_csv),
        "closed_csv": str(closed_csv),
        "heartbeat_json": str(heartbeat_json),
        "runtime_state_json": str(state_json),
        "native": native,
        "closed": closed,
        "heartbeat": heartbeat,
        "runtime_state": runtime_state,
        "gates_passed": passed,
        "gates_total": total,
        "gates": gates,
        "ready_for_shadow_drift_monitor": observer_ok,
        "shadow_start_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "BUILD_RET60_SHADOW_DRIFT_MONITOR_V2" if observer_ok else "REPAIR_SHADOW_RUNTIME_OUTPUTS",
    }

    write_json(out_dir / "ret60_shadow_runtime_observer_v2_state.json", result)
    pd.DataFrame(gates).to_csv(out_dir / "ret60_shadow_runtime_observer_v2_gates.csv", index=False)

    print("EDGE FACTORY RET60 SHADOW RUNTIME OBSERVER v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"sandbox_root: {SANDBOX_ROOT}")
    print(f"output_dir: {out_dir}")
    print(f"observer_status: {status}")
    print(f"observer_passed: {observer_ok}")
    print(f"native_rows: {native['rows']}")
    print(f"closed_rows: {closed['rows']}")
    print(f"native_net_pnl_sum: {native.get('net_pnl_sum')}")
    print(f"native_net_bps_mean: {native.get('net_bps_mean')}")
    print(f"gates: {passed}/{total}")
    print(f"ready_for_shadow_drift_monitor: {observer_ok}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")

    if not observer_ok:
        print()
        print("BLOCKERS")
        print("-" * 100)
        for g in gates:
            if not g["passed"]:
                print(f"- {g['gate']}: {g['reason']}")

    print()
    print(f"State: {out_dir / 'ret60_shadow_runtime_observer_v2_state.json'}")
    print(f"Gates: {out_dir / 'ret60_shadow_runtime_observer_v2_gates.csv'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
