#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "rel_extreme_reversion_short"
SANDBOX_ROOT = WORKSPACE / "paper_run_shadow_rel_extreme_reversion_short"

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def command_safety_check(cmd: str) -> list[str]:
    bad = []
    low = cmd.lower()
    forbidden = [
        "--live",
        "--active_paper",
        "--real_orders",
        "--place_orders",
        "api_key",
        "apikey",
        "secret",
    ]
    for x in forbidden:
        if x in low:
            bad.append(x)
    return bad

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_rel_extreme_shadow_start_gate_v1" / f"rel_extreme_shadow_start_gate_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    approval_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_manual_shadow_approval_recorder_v1",
        "rel_extreme_manual_approval_",
    )
    preflight_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_preflight_gate_v2",
        "rel_extreme_shadow_preflight_v2_",
    )
    engine_builder_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_runtime_engine_builder_v2",
        "rel_extreme_runtime_engine_builder_v2_",
    )

    approval_path = approval_dir / "rel_extreme_manual_shadow_approval_record.json" if approval_dir else None
    preflight_path = preflight_dir / "rel_extreme_shadow_preflight_gate_v2_state.json" if preflight_dir else None
    engine_state_path = engine_builder_dir / "rel_extreme_shadow_runtime_engine_builder_v2_state.json" if engine_builder_dir else None

    approval = read_json(approval_path)
    preflight = read_json(preflight_path)
    engine_state = read_json(engine_state_path)

    engine_path = Path(str(engine_state.get("runtime_engine_path", ""))) if engine_state.get("runtime_engine_path") else None
    reference_command = preflight.get("reference_command") or approval.get("reference_command") or ""

    gates = []

    def gate(name: str, required: bool, passed: bool, reason: Any):
        gates.append({
            "gate": name,
            "required": bool(required),
            "passed": bool(passed),
            "reason": str(reason),
        })

    gate("approval_record_exists", True, bool(approval_path and approval_path.exists()), approval_path)
    gate("approval_granted", True, approval.get("approval_granted") is True, approval.get("approval_granted"))
    gate("approval_shadow_allowed_by_record", True, approval.get("shadow_start_allowed_by_record") is True, approval.get("shadow_start_allowed_by_record"))
    gate("approval_no_active_paper", True, approval.get("active_paper_allowed") is False, approval.get("active_paper_allowed"))
    gate("approval_no_live", True, approval.get("live_allowed") is False, approval.get("live_allowed"))

    gate("preflight_record_exists", True, bool(preflight_path and preflight_path.exists()), preflight_path)
    gate("preflight_passed", True, preflight.get("preflight_passed") is True, preflight.get("status"))
    gate("preflight_ready_for_manual_approval", True, preflight.get("ready_for_manual_shadow_approval") is True, preflight.get("ready_for_manual_shadow_approval"))
    gate("preflight_no_active_paper", True, preflight.get("active_paper_allowed") is False, preflight.get("active_paper_allowed"))
    gate("preflight_no_live", True, preflight.get("live_allowed") is False, preflight.get("live_allowed"))

    gate("engine_state_exists", True, bool(engine_state_path and engine_state_path.exists()), engine_state_path)
    gate("engine_path_exists", True, bool(engine_path and engine_path.exists()), engine_path)
    gate("engine_self_test_ok", True, engine_state.get("self_test_ok") is True, engine_state.get("self_test_ok"))
    gate("engine_runtime_once_test_ok", True, engine_state.get("shadow_runtime_once_test_ok") is True, engine_state.get("shadow_runtime_once_test_ok"))
    gate("engine_no_active_paper", True, engine_state.get("active_paper_allowed") is False, engine_state.get("active_paper_allowed"))
    gate("engine_no_live", True, engine_state.get("live_allowed") is False, engine_state.get("live_allowed"))

    bad_cmd = command_safety_check(reference_command)
    gate("reference_command_exists", True, bool(reference_command), reference_command)
    gate("reference_command_points_to_engine", True, bool(engine_path and str(engine_path) in reference_command), reference_command)
    gate("reference_command_points_to_sandbox", True, str(SANDBOX_ROOT) in reference_command, reference_command)
    gate("reference_command_no_forbidden_args", True, not bad_cmd, bad_cmd)

    required_passed = sum(1 for g in gates if g["required"] and g["passed"])
    required_total = sum(1 for g in gates if g["required"])

    start_reference_allowed = required_passed == required_total

    status = (
        "REL_EXTREME_SHADOW_START_REFERENCE_READY_NOT_EXECUTED"
        if start_reference_allowed
        else "REL_EXTREME_SHADOW_START_BLOCKED"
    )

    reference_ps1 = out_dir / "rel_extreme_shadow_start_COMMAND_REFERENCE_ONLY.ps1"
    reference_ps1.write_text(
        "# REFERENCE ONLY - manual supervised shadow start\n"
        "# This is NOT live trading.\n"
        "# active_paper_allowed: False\n"
        "# live_allowed: False\n"
        "# MASTER_UPPER_SYSTEM is not modified.\n\n"
        + (reference_command if reference_command else "# BLOCKED") + "\n",
        encoding="utf-8",
    )

    decision = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "candidate": CANDIDATE,
        "status": status,
        "start_reference_allowed": start_reference_allowed,
        "shadow_runtime_start_executed": False,
        "approval_record": str(approval_path) if approval_path else None,
        "preflight_state": str(preflight_path) if preflight_path else None,
        "engine_state": str(engine_state_path) if engine_state_path else None,
        "engine_path": str(engine_path) if engine_path else None,
        "sandbox_root": str(SANDBOX_ROOT),
        "reference_command": reference_command,
        "reference_ps1": str(reference_ps1),
        "required_gates_passed": required_passed,
        "required_gates_total": required_total,
        "gates": gates,
        "active_paper_allowed": False,
        "live_allowed": False,
        "hard_rules": [
            "This gate does not start shadow.",
            "This gate does not start active paper.",
            "This gate does not start live.",
            "This gate does not modify MASTER_UPPER_SYSTEM.",
            "Use the reference command manually in a supervised PowerShell window only.",
        ],
        "next_action": "MANUALLY_RUN_REFERENCE_COMMAND_IN_SEPARATE_WINDOW" if start_reference_allowed else "FIX_SHADOW_START_BLOCKERS",
    }

    state_path = out_dir / "rel_extreme_shadow_start_gate_state.json"
    gates_path = out_dir / "rel_extreme_shadow_start_gate_gates.csv"
    decision_path = out_dir / "rel_extreme_shadow_start_gate_decision.json"

    write_json(state_path, decision)
    write_json(decision_path, decision)
    pd.DataFrame(gates).to_csv(gates_path, index=False)

    print("EDGE FACTORY REL EXTREME SHADOW START GATE v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"candidate : {CANDIDATE}")
    print(f"output_dir: {out_dir}")
    print(f"status: {status}")
    print(f"required_gates: {required_passed}/{required_total}")
    print(f"start_reference_allowed: {start_reference_allowed}")
    print("shadow_runtime_start_executed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("REFERENCE COMMAND")
    print("-" * 100)
    print(reference_command or "BLOCKED")
    print()
    print("GATES")
    print("-" * 100)
    print(pd.DataFrame(gates).to_string(index=False))
    print()
    print(f"State    : {state_path}")
    print(f"Gates    : {gates_path}")
    print(f"Decision : {decision_path}")
    print(f"Reference: {reference_ps1}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
