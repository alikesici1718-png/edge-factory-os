#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "ret60_reversal_short"

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
    out_dir = ws / "edge_factory_ret60_sandbox_preflight_gate_v2" / f"ret60_sandbox_preflight_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    audit_dir = latest_dir(ws / "edge_factory_ret60_shadow_runtime_engine_auditor_v2", "ret60_runtime_engine_audit_v2_")
    approval_dir = latest_dir(ws / "edge_factory_ret60_manual_shadow_approval_recorder", "ret60_manual_approval_")

    audit_path = audit_dir / "ret60_shadow_runtime_engine_audit_v2_state.json" if audit_dir else None
    approval_path = approval_dir / "ret60_manual_shadow_approval_record.json" if approval_dir else None

    audit = read_json(audit_path)
    approval_record = read_json(approval_path)
    approval_state = approval_record.get("state", {})

    engine_path = audit.get("engine_path")
    self_test_dir = audit.get("self_test_dir")

    sandbox_root = ws / "paper_run_shadow_ret60_reversal_short"

    gates = []

    def gate(name: str, passed: bool, reason: str = ""):
        gates.append({"gate": name, "passed": bool(passed), "reason": reason})

    gate("runtime_engine_audit_exists", bool(audit_path and audit_path.exists()), str(audit_path))
    gate("runtime_engine_audit_passed", audit.get("runtime_engine_audit_passed") is True, str(audit.get("runtime_engine_audit_passed")))
    gate("runtime_engine_file_exists", bool(engine_path and Path(engine_path).exists()), str(engine_path))
    gate("runtime_engine_self_test_ok", audit.get("self_test_ok") is True, str(audit.get("self_test_ok")))
    gate("native_rows_positive", int(audit.get("native_rows") or 0) > 0, str(audit.get("native_rows")))
    gate("closed_rows_positive", int(audit.get("closed_rows") or 0) > 0, str(audit.get("closed_rows")))
    gate("audit_gates_complete", audit.get("gates_passed") == audit.get("gates_total") and audit.get("gates_total", 0) > 0, f"{audit.get('gates_passed')}/{audit.get('gates_total')}")
    gate("audit_live_blocked", audit.get("live_allowed") is False, str(audit.get("live_allowed")))
    gate("audit_active_paper_blocked", audit.get("active_paper_allowed") is False, str(audit.get("active_paper_allowed")))
    gate("audit_shadow_start_blocked", audit.get("shadow_start_allowed") is False, str(audit.get("shadow_start_allowed")))

    gate("manual_approval_record_exists", bool(approval_path and approval_path.exists()), str(approval_path))
    gate("manual_approval_granted", approval_state.get("manual_approval_granted") is True, str(approval_state.get("manual_approval_granted")))
    gate("approval_allows_shadow_reference", approval_state.get("shadow_start_allowed_by_approval_record") is True, str(approval_state.get("shadow_start_allowed_by_approval_record")))
    gate("approval_live_blocked", approval_state.get("live_allowed") is False, str(approval_state.get("live_allowed")))
    gate("approval_active_paper_blocked", approval_state.get("active_paper_allowed") is False, str(approval_state.get("active_paper_allowed")))

    native_csv = Path(self_test_dir) / "ret60_shadow_native_events.csv" if self_test_dir else None
    closed_csv = Path(self_test_dir) / "ret60_shadow_closed_trades.csv" if self_test_dir else None
    heartbeat_json = Path(self_test_dir) / "ret60_shadow_heartbeat.json" if self_test_dir else None
    state_json = Path(self_test_dir) / "ret60_shadow_runtime_state.json" if self_test_dir else None

    gate("self_test_native_csv_exists", bool(native_csv and native_csv.exists()), str(native_csv))
    gate("self_test_closed_csv_exists", bool(closed_csv and closed_csv.exists()), str(closed_csv))
    gate("self_test_heartbeat_exists", bool(heartbeat_json and heartbeat_json.exists()), str(heartbeat_json))
    gate("self_test_state_exists", bool(state_json and state_json.exists()), str(state_json))

    passed = sum(1 for g in gates if g["passed"])
    total = len(gates)

    preflight_passed = passed == total

    status = (
        "RET60_SANDBOX_PREFLIGHT_V2_PASS_READY_FOR_SHADOW_START_GATE"
        if preflight_passed
        else "RET60_SANDBOX_PREFLIGHT_V2_BLOCKED"
    )

    runtime_plan = {
        "candidate_key": CANDIDATE,
        "runtime_engine_path": engine_path,
        "sandbox_root": str(sandbox_root),
        "expected_native_log_csv": str(sandbox_root / "ret60_shadow_native_events.csv"),
        "expected_closed_trades_csv": str(sandbox_root / "ret60_shadow_closed_trades.csv"),
        "expected_heartbeat_json": str(sandbox_root / "ret60_shadow_heartbeat.json"),
        "expected_state_json": str(sandbox_root / "ret60_shadow_runtime_state.json"),
        "command_is_reference_only": True,
        "reference_command": f'python "{engine_path}" --self_test --out_dir "{sandbox_root}"',
        "note": "v2 preflight still does not start runtime. Shadow start gate v2 must decide next.",
    }

    state = {
        "candidate": CANDIDATE,
        "preflight_status": status,
        "preflight_passed": preflight_passed,
        "ready_for_shadow_start_gate": preflight_passed,
        "runtime_engine_audit_passed": audit.get("runtime_engine_audit_passed") is True,
        "manual_approval_granted": approval_state.get("manual_approval_granted") is True,
        "runtime_engine_path": engine_path,
        "sandbox_root": str(sandbox_root),
        "runtime_plan": runtime_plan,
        "gates_passed": passed,
        "gates_total": total,
        "gates": gates,
        "shadow_start_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "expires_at": (datetime.now() + timedelta(hours=12)).isoformat(timespec="seconds"),
        "next_action": "RUN_RET60_SHADOW_START_GATE_V2" if preflight_passed else "REPAIR_PREFLIGHT_V2_BLOCKERS",
    }

    write_json(out_dir / "ret60_sandbox_preflight_v2_state.json", state)
    write_json(out_dir / "ret60_shadow_runtime_plan_v2_REFERENCE_ONLY.json", runtime_plan)
    pd.DataFrame(gates).to_csv(out_dir / "ret60_sandbox_preflight_v2_gates.csv", index=False)

    ref = "# REFERENCE ONLY - DO NOT RUN FROM PREFLIGHT\n"
    ref += "# Shadow start gate v2 must decide first.\n"
    ref += f'# {runtime_plan["reference_command"]}\n'
    (out_dir / "ret60_shadow_start_v2_REFERENCE_ONLY.ps1").write_text(ref, encoding="utf-8")

    print("EDGE FACTORY RET60 SANDBOX PREFLIGHT GATE v2")
    print("=" * 100)
    print(f"workspace : {ws}")
    print(f"output_dir: {out_dir}")
    print(f"preflight_status: {status}")
    print(f"preflight_passed: {preflight_passed}")
    print(f"ready_for_shadow_start_gate: {preflight_passed}")
    print(f"runtime_engine_path: {engine_path}")
    print(f"sandbox_root: {sandbox_root}")
    print(f"gates: {passed}/{total}")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")

    if not preflight_passed:
        print()
        print("BLOCKERS")
        print("-" * 100)
        for g in gates:
            if not g["passed"]:
                print(f"- {g['gate']}: {g['reason']}")

    print()
    print(f"State: {out_dir / 'ret60_sandbox_preflight_v2_state.json'}")
    print(f"Gates: {out_dir / 'ret60_sandbox_preflight_v2_gates.csv'}")
    print(f"Reference: {out_dir / 'ret60_shadow_start_v2_REFERENCE_ONLY.ps1'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
