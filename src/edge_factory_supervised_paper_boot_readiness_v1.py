#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
SCRIPT_DIR = Path(r"C:\Users\alike")
PAPER_DIR = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
LAUNCHER = SCRIPT_DIR / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1"
SIZING_CONTRACT = WORKSPACE / "edge_factory_position_sizing_contract" / "position_sizing_contract.json"

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

def find_latest_state(root_name: str, prefix: str, state_file: str) -> tuple[Optional[Path], Dict[str, Any]]:
    d = latest_dir(WORKSPACE / root_name, prefix)
    p = d / state_file if d else None
    return p, read_json(p)

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_supervised_paper_boot_readiness_v1" / f"paper_boot_readiness_v1_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    capital_path, capital_state = find_latest_state(
        "edge_factory_active_capital_governor_review_v2",
        "active_capital_governor_v2_",
        "active_capital_governor_review_v2_state.json",
    )

    drift_path, drift_state = find_latest_state(
        "edge_factory_active_family_drift_monitor_planner_v1",
        "active_family_drift_plan_v1_",
        "active_family_drift_monitor_planner_v1_state.json",
    )

    refresh_path, refresh_state = find_latest_state(
        "edge_factory_active_family_robustness_refresh_v2",
        "active_family_refresh_v2_",
        "active_family_robustness_refresh_v2_state.json",
    )

    damage_path, damage_state = find_latest_state(
        "edge_factory_active_family_damage_decomposition_v1",
        "active_family_damage_v1_",
        "active_family_damage_decomposition_v1_state.json",
    )

    gates = []

    def gate(name: str, passed: bool, reason: str = ""):
        gates.append({"gate": name, "passed": bool(passed), "reason": str(reason)})

    gate("launcher_exists", LAUNCHER.exists(), LAUNCHER)
    gate("sizing_contract_exists", SIZING_CONTRACT.exists(), SIZING_CONTRACT)

    gate("capital_governor_exists", bool(capital_path and capital_path.exists()), capital_path)
    gate("capital_governor_no_live", capital_state.get("live_allowed") is False, capital_state.get("live_allowed"))
    gate("capital_governor_no_change_allowed", capital_state.get("capital_change_allowed") is False, capital_state.get("capital_change_allowed"))
    gate("capital_governor_no_active_change_allowed", capital_state.get("active_paper_change_allowed") is False, capital_state.get("active_paper_change_allowed"))

    gate("drift_planner_exists", bool(drift_path and drift_path.exists()), drift_path)
    gate("drift_blocked_no_sample", drift_state.get("overall_status") == "ACTIVE_FAMILY_DRIFT_BLOCKED_NO_PAPER_SAMPLE", drift_state.get("overall_status"))
    gate("drift_planner_no_live", drift_state.get("live_allowed") is False, drift_state.get("live_allowed"))
    gate("drift_planner_no_active_change_allowed", drift_state.get("active_paper_change_allowed") is False, drift_state.get("active_paper_change_allowed"))

    gate("refresh_exists", bool(refresh_path and refresh_path.exists()), refresh_path)
    gate("refresh_has_4_families", int(refresh_state.get("family_count") or 0) == 4, refresh_state.get("family_count"))
    gate("refresh_no_live", refresh_state.get("live_allowed") is False, refresh_state.get("live_allowed"))

    gate("damage_decomp_exists", bool(damage_path and damage_path.exists()), damage_path)
    gate("damage_decomp_no_live", damage_state.get("live_allowed") is False, damage_state.get("live_allowed"))
    gate("damage_decomp_no_capital_change", damage_state.get("capital_change_allowed") is False, damage_state.get("capital_change_allowed"))

    paper_dir_exists = PAPER_DIR.exists()
    paper_csv_count = len(list(PAPER_DIR.rglob("*.csv"))) if paper_dir_exists else 0

    gate("paper_dir_not_required_yet", True, f"exists={paper_dir_exists} csv_count={paper_csv_count}")
    gate("live_blocked_by_policy", True, "paper-only boot reference; no live command generated")

    passed = sum(1 for g in gates if g["passed"])
    total = len(gates)
    ready = passed == total

    status = (
        "SUPERVISED_PAPER_BOOT_REFERENCE_READY_NOT_EXECUTED"
        if ready
        else "SUPERVISED_PAPER_BOOT_BLOCKED"
    )

    reference_command = f'powershell -ExecutionPolicy Bypass -File "{LAUNCHER}"'

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "script_dir": str(SCRIPT_DIR),
        "paper_dir": str(PAPER_DIR),
        "launcher": str(LAUNCHER),
        "sizing_contract": str(SIZING_CONTRACT),
        "status": status,
        "ready_for_supervised_paper_boot_reference": ready,
        "paper_started_by_this_module": False,
        "active_paper_change_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "reference_command": reference_command if ready else None,
        "gates_passed": passed,
        "gates_total": total,
        "gates": gates,
        "inputs": {
            "capital_state": str(capital_path) if capital_path else None,
            "drift_state": str(drift_path) if drift_path else None,
            "refresh_state": str(refresh_path) if refresh_path else None,
            "damage_state": str(damage_path) if damage_path else None,
        },
        "next_action": "MANUALLY_RUN_SUPERVISED_PAPER_LAUNCHER_THEN_HEALTH_CHECK" if ready else "REPAIR_BOOT_READINESS_BLOCKERS",
        "hard_rules": [
            "This module did not start paper.",
            "This module did not start live.",
            "This module did not mutate sizing contract.",
            "This module did not change capital.",
            "Only supervised paper reference command may be generated.",
            "Live remains blocked.",
        ],
    }

    write_json(out_dir / "supervised_paper_boot_readiness_v1_state.json", state)
    pd.DataFrame(gates).to_csv(out_dir / "supervised_paper_boot_readiness_v1_gates.csv", index=False)

    ref = "# REFERENCE ONLY - SUPERVISED PAPER BOOT\n"
    ref += "# This file is not executed by readiness module.\n"
    ref += "# Live remains blocked.\n"
    if ready:
        ref += reference_command + "\n"
    else:
        ref += "# BLOCKED - readiness gates failed.\n"

    (out_dir / "supervised_paper_boot_REFERENCE_ONLY.ps1").write_text(ref, encoding="utf-8")

    print("EDGE FACTORY SUPERVISED PAPER BOOT READINESS v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"paper_dir : {PAPER_DIR}")
    print(f"output_dir: {out_dir}")
    print(f"status: {status}")
    print(f"ready_for_supervised_paper_boot_reference: {ready}")
    print(f"paper_started_by_this_module: False")
    print(f"launcher: {LAUNCHER}")
    print(f"sizing_contract: {SIZING_CONTRACT}")
    print(f"paper_dir_exists: {paper_dir_exists}")
    print(f"paper_csv_count: {paper_csv_count}")
    print(f"gates: {passed}/{total}")
    print("active_paper_change_allowed: False")
    print("capital_change_allowed: False")
    print("live_allowed: False")

    if not ready:
        print()
        print("BLOCKERS")
        print("-" * 100)
        for g in gates:
            if not g["passed"]:
                print(f"- {g['gate']}: {g['reason']}")
    else:
        print()
        print("REFERENCE COMMAND")
        print("-" * 100)
        print(reference_command)

    print()
    print(f"State    : {out_dir / 'supervised_paper_boot_readiness_v1_state.json'}")
    print(f"Gates    : {out_dir / 'supervised_paper_boot_readiness_v1_gates.csv'}")
    print(f"Reference: {out_dir / 'supervised_paper_boot_REFERENCE_ONLY.ps1'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
