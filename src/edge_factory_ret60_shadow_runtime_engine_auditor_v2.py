#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "ret60_reversal_short"

REQUIRED_LOG_FILES = [
    "ret60_shadow_native_events.csv",
    "ret60_shadow_closed_trades.csv",
    "ret60_shadow_heartbeat.json",
    "ret60_shadow_runtime_state.json",
]

REQUIRED_CSV_FIELDS = [
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

FORBIDDEN_STRINGS = [
    "ccxt",
    "create_order",
    "place_order",
    "private_post",
    "private_get",
    "fetch_balance",
    "apiKey",
    "apiSecret",
]

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

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
    ws = WORKSPACE
    out_dir = ws / "edge_factory_ret60_shadow_runtime_engine_auditor_v2" / f"ret60_runtime_engine_audit_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    bdir = latest_dir(ws / "edge_factory_ret60_shadow_runtime_engine_builder_v2", "ret60_runtime_engine_builder_v2_")
    builder_state_path = bdir / "ret60_shadow_runtime_engine_builder_v2_state.json" if bdir else None
    builder = read_json(builder_state_path)

    engine_path = builder.get("runtime_engine_path")
    engine = Path(engine_path) if engine_path else None

    gates = []

    def gate(name: str, passed: bool, reason: str = ""):
        gates.append({"gate": name, "passed": bool(passed), "reason": reason})

    gate("builder_state_exists", bool(builder_state_path and builder_state_path.exists()), str(builder_state_path))
    gate("runtime_engine_written", builder.get("runtime_engine_written") is True, str(builder.get("runtime_engine_written")))
    gate("engine_file_exists", bool(engine and engine.exists()), str(engine))

    compile_ok = False
    compile_error = ""
    if engine and engine.exists():
        try:
            py_compile.compile(str(engine), doraise=True)
            compile_ok = True
        except Exception as e:
            compile_error = repr(e)
    gate("engine_compiles", compile_ok, compile_error)

    dangerous = False
    text = ""
    if engine and engine.exists():
        text = engine.read_text(encoding="utf-8", errors="replace")
        dangerous = any(x in text for x in FORBIDDEN_STRINGS)
    gate("no_forbidden_live_or_api_code", not dangerous, "forbidden marker found" if dangerous else "")

    markers = {
        "shadow_runtime_entrypoint": "--shadow_runtime" in text,
        "self_test_entrypoint": "--self_test" in text,
        "heartbeat_writer": "heartbeat_writer" in text and "ret60_shadow_heartbeat.json" in text,
        "native_log_writer": "ret60_shadow_native_events.csv" in text,
        "closed_trade_writer": "ret60_shadow_closed_trades.csv" in text,
        "live_block_constant": "LIVE_ALLOWED = False" in text,
        "active_block_constant": "ACTIVE_PAPER_ALLOWED = False" in text,
    }
    for k, v in markers.items():
        gate(k, v, "")

    self_test_dir = out_dir / "runtime_engine_self_test"
    self_test_ok = False
    rc = None
    stdout = ""
    stderr = ""
    if engine and engine.exists() and compile_ok and not dangerous:
        try:
            proc = subprocess.run(
                [sys.executable, str(engine), "--self_test", "--out_dir", str(self_test_dir)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            rc = proc.returncode
            stdout = proc.stdout[-4000:]
            stderr = proc.stderr[-4000:]
            self_test_ok = proc.returncode == 0
        except Exception as e:
            stderr = repr(e)

    gate("self_test_return_code_ok", self_test_ok, f"rc={rc} stderr={stderr[:300]}")

    files_ok = True
    for fn in REQUIRED_LOG_FILES:
        exists = (self_test_dir / fn).exists()
        gate(f"self_test_file_{fn}", exists, str(self_test_dir / fn))
        files_ok = files_ok and exists

    native_csv = self_test_dir / "ret60_shadow_native_events.csv"
    closed_csv = self_test_dir / "ret60_shadow_closed_trades.csv"
    native_fields_ok = False
    closed_fields_ok = False
    native_rows = 0
    closed_rows = 0

    if native_csv.exists():
        try:
            df = pd.read_csv(native_csv)
            native_rows = len(df)
            native_fields_ok = all(c in df.columns for c in REQUIRED_CSV_FIELDS)
        except Exception:
            native_fields_ok = False

    if closed_csv.exists():
        try:
            df = pd.read_csv(closed_csv)
            closed_rows = len(df)
            closed_fields_ok = all(c in df.columns for c in REQUIRED_CSV_FIELDS)
        except Exception:
            closed_fields_ok = False

    gate("native_csv_has_rows", native_rows > 0, f"rows={native_rows}")
    gate("closed_csv_has_rows", closed_rows > 0, f"rows={closed_rows}")
    gate("native_csv_required_fields", native_fields_ok, "")
    gate("closed_csv_required_fields", closed_fields_ok, "")

    heartbeat_ok = False
    state_ok = False
    hb = read_json(self_test_dir / "ret60_shadow_heartbeat.json")
    st = read_json(self_test_dir / "ret60_shadow_runtime_state.json")
    heartbeat_ok = hb.get("live_allowed") is False and hb.get("active_paper_allowed") is False
    state_ok = st.get("live_allowed") is False and st.get("active_paper_allowed") is False
    gate("heartbeat_blocks_live_active", heartbeat_ok, "")
    gate("state_blocks_live_active", state_ok, "")

    passed = sum(1 for g in gates if g["passed"])
    total = len(gates)

    audit_passed = passed == total
    status = (
        "RET60_SHADOW_RUNTIME_ENGINE_AUDIT_PASS_SELF_TEST_ONLY"
        if audit_passed
        else "RET60_SHADOW_RUNTIME_ENGINE_AUDIT_FAIL"
    )

    result = {
        "candidate": CANDIDATE,
        "audit_status": status,
        "runtime_engine_audit_passed": audit_passed,
        "engine_path": str(engine) if engine else None,
        "builder_state_path": str(builder_state_path) if builder_state_path else None,
        "self_test_dir": str(self_test_dir),
        "self_test_ok": self_test_ok,
        "native_rows": native_rows,
        "closed_rows": closed_rows,
        "gates_passed": passed,
        "gates_total": total,
        "gates": gates,
        "stdout_tail": stdout,
        "stderr_tail": stderr,
        "shadow_start_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "RUN_RET60_PREFLIGHT_V2_OR_SHADOW_START_GATE_V2" if audit_passed else "REPAIR_RUNTIME_ENGINE",
    }

    write_json(out_dir / "ret60_shadow_runtime_engine_audit_v2_state.json", result)
    pd.DataFrame(gates).to_csv(out_dir / "ret60_shadow_runtime_engine_audit_v2_gates.csv", index=False)

    print("EDGE FACTORY RET60 SHADOW RUNTIME ENGINE AUDITOR v2")
    print("=" * 100)
    print(f"workspace : {ws}")
    print(f"output_dir: {out_dir}")
    print(f"engine_path: {engine}")
    print(f"audit_status: {status}")
    print(f"runtime_engine_audit_passed: {audit_passed}")
    print(f"self_test_ok: {self_test_ok}")
    print(f"native_rows: {native_rows}")
    print(f"closed_rows: {closed_rows}")
    print(f"gates: {passed}/{total}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")

    if not audit_passed:
        print()
        print("BLOCKERS")
        print("-" * 100)
        for g in gates:
            if not g["passed"]:
                print(f"- {g['gate']}: {g['reason']}")

    print()
    print(f"State: {out_dir / 'ret60_shadow_runtime_engine_audit_v2_state.json'}")
    print(f"Gates: {out_dir / 'ret60_shadow_runtime_engine_audit_v2_gates.csv'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
