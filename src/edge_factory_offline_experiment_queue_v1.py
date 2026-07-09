#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads the OS recovery manifest, research brain state, candidate lifecycle registry, and contract validator outputs to build a prioritized queue of allowed offline experiment tasks for each candidate.
Outputs the task queue as a JSON file to the edge_factory_offline_experiment_queue_v1 workspace directory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_offline_experiment_queue_v1"

def latest_dir(root: Path, prefix: str) -> Path | None:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    if not ds:
        return None
    return sorted(ds, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

def add_task(tasks, priority, key, candidate, stage, status, reason, allowed_now, blocker="", required_input="", output_expected=""):
    tasks.append({
        "priority": priority,
        "task_key": key,
        "candidate": candidate,
        "stage": stage,
        "status": status,
        "allowed_now": bool(allowed_now),
        "reason": reason,
        "blocker": blocker,
        "required_input": required_input,
        "output_expected": output_expected,
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

def main() -> int:
    out_dir = OUT_ROOT / f"offline_experiment_queue_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = read_json(WORKSPACE / "edge_factory_os_recovery_manifest_v2" / "edge_factory_os_recovery_manifest_latest.json")

    research_dir = latest_dir(WORKSPACE / "edge_factory_os_research_brain_v1", "research_brain_v1_")
    research = read_json(research_dir / "edge_factory_os_research_brain_v1_state.json" if research_dir else None)

    registry_dir = latest_dir(WORKSPACE / "edge_factory_candidate_lifecycle_registry_v1", "candidate_lifecycle_registry_v1_")
    registry = read_json(registry_dir / "candidate_lifecycle_registry_v1_state.json" if registry_dir else None)

    validator_dir = latest_dir(WORKSPACE / "edge_factory_offline_experiment_contract_validator_v1", "contract_validator_v1_")
    validator = read_json(validator_dir / "offline_experiment_contract_validator_v1_state.json" if validator_dir else None)

    current = manifest.get("current_state", {})
    closed = int(current.get("closed") or 0)
    errors = int(current.get("errors") or 0)

    candidates = registry.get("candidates", [])
    validator_status = validator.get("validation_status", "UNKNOWN")
    validator_critical = int(validator.get("critical_failed_count") or 0)

    tasks = []

    # Global operating constraint.
    if errors > 0:
        add_task(
            tasks, 1000,
            "block_all_offline_experiments_errors_present",
            "GLOBAL",
            "safety",
            "BLOCKED",
            f"Runtime errors present: {errors}. Inspect live system first.",
            allowed_now=False,
            blocker="RUNTIME_ERRORS_PRESENT",
        )
    else:
        add_task(
            tasks, 1000,
            "runtime_safe_for_offline_planning",
            "GLOBAL",
            "safety",
            "PASS",
            "No runtime errors. Offline planning may continue. MASTER remains untouched.",
            allowed_now=True,
        )

    # Contract system.
    add_task(
        tasks, 900,
        "validate_contract_template",
        "TEMPLATE",
        "contract_validation",
        "PASS" if validator_status == "TEMPLATE_STRUCTURE_VALID_NOT_A_CANDIDATE" and validator_critical == 0 else "ATTENTION",
        f"Latest validator status: {validator_status}, critical_failed={validator_critical}.",
        allowed_now=validator_critical == 0,
        blocker="" if validator_critical == 0 else "CONTRACT_VALIDATOR_CRITICAL_FAIL",
        required_input=str(validator.get("contract_path", "")),
        output_expected="template structure is valid but not candidate",
    )

    # rel_extreme handling.
    rel = None
    for c in candidates:
        if c.get("candidate") == "rel_extreme_reversion_short":
            rel = c
            break

    if rel:
        add_task(
            tasks, 850,
            "keep_rel_extreme_archived",
            "rel_extreme_reversion_short",
            "candidate_lifecycle",
            "ARCHIVE_WAIT",
            "rel_extreme has no shadow closed sample and duplicate/stale replay pattern. Do not promote.",
            allowed_now=False,
            blocker="ARCHIVE_WAIT_DO_NOT_PROMOTE",
            required_input=str(rel.get("shadow_dir", "")),
            output_expected="none; archival state only",
        )

        add_task(
            tasks, 820,
            "optional_fix_rel_extreme_realtime_shadow_contract",
            "rel_extreme_reversion_short",
            "contract_repair",
            "OPTIONAL_PLANNING_ONLY",
            "Can write a future contract to fix stale/duplicate shadow behavior, but cannot start it while MASTER initial sample is immature.",
            allowed_now=True,
            blocker="NO_RUNTIME_EXECUTION",
            required_input="candidate_validation_gate_policy_v1.json",
            output_expected="future rel_extreme_shadow_repair_contract.json",
        )

    # New candidate pipeline.
    if closed < 20:
        add_task(
            tasks, 750,
            "block_new_candidate_execution_until_master_initial_sample",
            "NEW_CANDIDATES",
            "research_execution",
            "BLOCKED",
            f"MASTER closed sample too small: {closed}/20. Do not execute new family searches.",
            allowed_now=False,
            blocker="MASTER_INITIAL_SAMPLE_NOT_READY",
        )
    else:
        add_task(
            tasks, 750,
            "allow_readonly_new_candidate_planning",
            "NEW_CANDIDATES",
            "research_planning",
            "READY_READ_ONLY",
            f"MASTER closed sample is mature enough for read-only new candidate planning: {closed}.",
            allowed_now=True,
            required_input="offline_experiment_contract_template_v1.json",
            output_expected="candidate contracts only",
        )

    # Always allowed: produce specs/contracts, not experiments.
    add_task(
        tasks, 700,
        "create_candidate_contract_from_template_when_user_selects_idea",
        "NEW_CANDIDATES",
        "contract_creation",
        "READY_OFFLINE_ONLY",
        "When a new idea is selected, create a filled contract before any backtest/replay.",
        allowed_now=True,
        required_input="offline_experiment_contract_template_v1.json",
        output_expected="filled candidate contract JSON",
    )

    add_task(
        tasks, 650,
        "build_contract_to_test_runner_interface_spec",
        "OS_INFRA",
        "interface_spec",
        "READY_OFFLINE_ONLY",
        "Define how a valid contract maps to an offline test runner without touching MASTER.",
        allowed_now=True,
        required_input="offline_experiment_contract_schema_v1.json",
        output_expected="contract_runner_interface_spec.json",
    )

    add_task(
        tasks, 600,
        "build_result_to_lifecycle_adapter_spec",
        "OS_INFRA",
        "interface_spec",
        "READY_OFFLINE_ONLY",
        "Define how offline test results update candidate lifecycle state.",
        allowed_now=True,
        required_input="candidate_validation_gate_policy_v1.json",
        output_expected="result_lifecycle_adapter_spec.json",
    )

    tasks = sorted(tasks, key=lambda x: x["priority"], reverse=True)

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "queue_status": "OFFLINE_EXPERIMENT_QUEUE_READY",
        "closed": closed,
        "errors": errors,
        "validator_status": validator_status,
        "candidate_count": len(candidates),
        "task_count": len(tasks),
        "tasks": tasks,
        "hard_rules": [
            "Queue does not run experiments.",
            "Queue does not touch MASTER_UPPER_SYSTEM.",
            "Queue does not start/stop processes.",
            "Queue does not promote candidates.",
            "Queue does not change capital.",
            "Queue does not enable live trading.",
        ],
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
    }

    state_path = out_dir / "offline_experiment_queue_v1_state.json"
    csv_path = out_dir / "offline_experiment_queue_v1.csv"
    report_path = out_dir / "offline_experiment_queue_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(tasks).to_csv(csv_path, index=False)

    md = []
    md.append("# Edge Factory Offline Experiment Queue v1")
    md.append("")
    md.append(f"Queue status: `{state['queue_status']}`")
    md.append(f"Closed: `{closed}`")
    md.append(f"Errors: `{errors}`")
    md.append(f"Validator: `{validator_status}`")
    md.append("")
    md.append("## Tasks")
    for t in tasks:
        md.append(f"- `{t['status']}` `{t['task_key']}` — {t['reason']}")
    md.append("")
    md.append("## Safety")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OFFLINE EXPERIMENT QUEUE v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print("queue_status: OFFLINE_EXPERIMENT_QUEUE_READY")
    print(f"closed: {closed}")
    print(f"errors: {errors}")
    print(f"validator_status: {validator_status}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("QUEUE")
    print("-" * 100)
    df = pd.DataFrame(tasks)
    print(df[["priority","task_key","candidate","stage","status","allowed_now","blocker"]].to_string(index=False))
    print()
    print(f"State : {state_path}")
    print(f"Queue : {csv_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
