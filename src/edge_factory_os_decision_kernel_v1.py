#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OS decision kernel (v1) that reads the latest state index and recovery manifest to produce a prioritized list of OS decisions (e.g. allowed actions, blockers, required tasks), writing timestamped JSON/CSV/Markdown artifacts to edge_factory_os_decision_kernel_v1/ in the workspace.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_os_decision_kernel_v1"

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def latest_dir(root: Path, prefix: str) -> Path | None:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    if not ds:
        return None
    return sorted(ds, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def add_decision(rows, priority, key, decision_type, status, reason, action, allowed, blocker=""):
    rows.append({
        "priority": priority,
        "decision_key": key,
        "decision_type": decision_type,
        "status": status,
        "allowed": bool(allowed),
        "reason": reason,
        "action": action,
        "blocker": blocker,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
    })

def component(index: dict[str, Any], name: str) -> dict[str, Any]:
    return index.get("components", {}).get(name, {})

def status_values(index: dict[str, Any], name: str) -> dict[str, Any]:
    return component(index, name).get("status_values", {}) or {}

def main() -> int:
    out_dir = OUT_ROOT / f"os_decision_kernel_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    state_index_path = WORKSPACE / "edge_factory_os_state_index_v2" / "edge_factory_os_state_index_v2_latest.json"
    manifest_path = WORKSPACE / "edge_factory_os_recovery_manifest_v2" / "edge_factory_os_recovery_manifest_latest.json"

    state_index = read_json(state_index_path)
    manifest = read_json(manifest_path)

    cc = status_values(state_index, "command_center")
    auto = status_values(state_index, "autopilot_v4")
    inv = status_values(state_index, "invariant_guard")
    proc = status_values(state_index, "process_watchdog")
    validator = status_values(state_index, "offline_contract_validator")
    queue = status_values(state_index, "offline_experiment_queue")
    registry = status_values(state_index, "candidate_lifecycle_registry")

    index_health = state_index.get("index_health", "UNKNOWN")
    attention_count = int(state_index.get("attention_count") or 0)

    open_n = int(auto.get("open") or cc.get("open") or 0)
    pending_n = int(auto.get("pending") or cc.get("pending") or 0)
    closed_n = int(auto.get("closed") or cc.get("closed") or 0)
    errors_n = int(auto.get("errors") or cc.get("errors") or 0)

    invariant_status = auto.get("invariant_status") or inv.get("status")
    process_status = auto.get("process_status") or proc.get("status")
    autopilot_severity = auto.get("severity", "UNKNOWN")
    autopilot_status = auto.get("status", "UNKNOWN")

    decisions = []
    phase = "UNKNOWN"
    kernel_status = "UNKNOWN"

    # Safety first.
    if index_health != "OS_STATE_INDEX_V2_PASS" or attention_count > 0:
        phase = "ATTENTION_STATE"
        kernel_status = "DECISION_KERNEL_ATTENTION_STATE_INDEX_NOT_CLEAN"
        add_decision(
            decisions, 1000,
            "inspect_state_index_attention",
            "safety",
            "REQUIRED",
            f"State index not clean: {index_health}, attention_count={attention_count}.",
            "Run state index and inspect attention components.",
            True,
            "STATE_INDEX_NOT_PASS",
        )
    elif autopilot_severity != "OK":
        phase = "ATTENTION_STATE"
        kernel_status = "DECISION_KERNEL_ATTENTION_AUTOPILOT_NOT_OK"
        add_decision(
            decisions, 1000,
            "inspect_autopilot_attention",
            "safety",
            "REQUIRED",
            f"Autopilot severity is {autopilot_severity}.",
            "Inspect edge_factory_os_autopilot_v4_latest_state.json.",
            True,
            "AUTOPILOT_NOT_OK",
        )
    elif invariant_status != "INVARIANT_GUARD_PASS":
        phase = "ATTENTION_STATE"
        kernel_status = "DECISION_KERNEL_ATTENTION_INVARIANT_NOT_PASS"
        add_decision(
            decisions, 1000,
            "inspect_invariant_guard",
            "safety",
            "REQUIRED",
            f"Invariant status is {invariant_status}.",
            "Run invariant guard and inspect failed gates.",
            True,
            "INVARIANT_NOT_PASS",
        )
    elif process_status != "PROCESS_WATCHDOG_PASS":
        phase = "ATTENTION_STATE"
        kernel_status = "DECISION_KERNEL_ATTENTION_PROCESS_NOT_PASS"
        add_decision(
            decisions, 1000,
            "inspect_process_watchdog",
            "safety",
            "REQUIRED",
            f"Process watchdog status is {process_status}.",
            "Run process watchdog and inspect missing components.",
            True,
            "PROCESS_NOT_PASS",
        )
    elif errors_n > 0:
        phase = "ATTENTION_STATE"
        kernel_status = "DECISION_KERNEL_ATTENTION_RUNTIME_ERRORS"
        add_decision(
            decisions, 1000,
            "inspect_runtime_errors",
            "safety",
            "REQUIRED",
            f"Runtime errors present: {errors_n}.",
            "Inspect errors.csv before any optional work.",
            True,
            "RUNTIME_ERRORS_PRESENT",
        )
    else:
        phase = "RUNNING_COLLECTING_INITIAL_SAMPLE"
        kernel_status = "DECISION_KERNEL_OK"

    # Core runtime decision.
    if kernel_status == "DECISION_KERNEL_OK":
        add_decision(
            decisions, 1000,
            "protect_master_runtime",
            "runtime",
            "ACTIVE",
            f"MASTER is healthy: open={open_n}, pending={pending_n}, closed={closed_n}, errors={errors_n}.",
            "Keep MASTER and Autopilot v4 running. Do not restart or modify.",
            True,
        )

        if closed_n < 20:
            add_decision(
                decisions, 900,
                "block_drift_until_initial_sample",
                "validation",
                "BLOCKED",
                f"Closed sample too small for drift review: {closed_n}/20.",
                "Do not run drift decision. Wait for closed>=20.",
                False,
                "MIN_CLOSED_20_NOT_MET",
            )
        else:
            phase = "INITIAL_SAMPLE_READY_FOR_DRIFT"
            add_decision(
                decisions, 900,
                "run_drift_monitor_readonly",
                "validation",
                "READY",
                f"Closed sample reached drift threshold: {closed_n}.",
                'python -u "C:\\Users\\alike\\edge_factory_active_family_drift_monitor_planner_v1.py"',
                True,
            )

        if closed_n < 50:
            add_decision(
                decisions, 850,
                "block_capital_review_until_larger_sample",
                "capital",
                "BLOCKED",
                f"Closed sample too small for capital review: {closed_n}/50.",
                "Do not change capital. Wait for closed>=50.",
                False,
                "MIN_CLOSED_50_NOT_MET",
            )
        else:
            phase = "SAMPLE_READY_FOR_CAPITAL_REVIEW"
            add_decision(
                decisions, 850,
                "run_capital_governor_readonly",
                "capital",
                "READY",
                f"Closed sample reached capital review threshold: {closed_n}.",
                'python -u "C:\\Users\\alike\\edge_factory_active_capital_governor_review_v2.py"',
                True,
            )

        # Research OS: allowed to continue only as offline/spec/contract work.
        add_decision(
            decisions, 800,
            "continue_offline_os_buildout",
            "research_os",
            "READY",
            "Runtime is stable and offline OS chain exists. Continue building intelligence around contracts, result adapters, and candidate generation.",
            "Build candidate-contract generator and idea intake modules. Do not execute new family searches yet.",
            True,
        )

        if closed_n < 20:
            add_decision(
                decisions, 750,
                "block_new_candidate_execution",
                "research_execution",
                "BLOCKED",
                f"MASTER initial sample immature: closed={closed_n}/20.",
                "Do not run new family search/backtest execution. Specs and contracts only.",
                False,
                "MASTER_INITIAL_SAMPLE_NOT_READY",
            )
        else:
            add_decision(
                decisions, 750,
                "allow_readonly_candidate_planning",
                "research_execution",
                "READY_READONLY",
                "Initial sample is mature enough for read-only planning.",
                "May plan offline candidates, still no active paper/live.",
                True,
            )

        archived = registry.get("archived", [])
        if archived:
            add_decision(
                decisions, 700,
                "keep_archived_candidates_out",
                "candidate_lifecycle",
                "ACTIVE_BLOCK",
                f"Archived candidates: {archived}.",
                "Do not promote archived candidates. Require new contract/result evidence.",
                False,
                "ARCHIVE_WAIT",
            )

        # Next best build target.
        add_decision(
            decisions, 650,
            "build_candidate_contract_generator",
            "next_build",
            "READY",
            "The OS has schema/validator/queue/adapters. Next intelligence layer is converting a human idea into a valid candidate contract draft.",
            "Create edge_factory_candidate_contract_generator_v1.py.",
            True,
        )

    decisions = sorted(decisions, key=lambda x: x["priority"], reverse=True)

    # Next best action is the highest allowed READY/ACTIVE build or runtime action.
    next_allowed = None
    for d in decisions:
        if d["allowed"] and d["status"] in {"READY", "ACTIVE", "REQUIRED", "READY_READONLY"}:
            next_allowed = d
            break

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "kernel_status": kernel_status,
        "phase": phase,
        "index_health": index_health,
        "attention_count": attention_count,
        "autopilot_status": autopilot_status,
        "autopilot_severity": autopilot_severity,
        "invariant_status": invariant_status,
        "process_status": process_status,
        "open": open_n,
        "pending": pending_n,
        "closed": closed_n,
        "errors": errors_n,
        "next_best_action": next_allowed,
        "decisions": decisions,
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Decision kernel only decides; it does not execute.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start or stop processes.",
            "Does not place orders.",
            "Does not enable live trading.",
            "Does not change capital.",
        ],
    }

    state_path = out_dir / "edge_factory_os_decision_kernel_v1_state.json"
    csv_path = out_dir / "edge_factory_os_decision_kernel_v1_decisions.csv"
    latest_path = OUT_ROOT / "edge_factory_os_decision_kernel_latest.json"
    report_path = out_dir / "edge_factory_os_decision_kernel_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(decisions).to_csv(csv_path, index=False)

    md = []
    md.append("# Edge Factory OS Decision Kernel v1")
    md.append("")
    md.append(f"Kernel status: `{kernel_status}`")
    md.append(f"Phase: `{phase}`")
    md.append(f"Open: `{open_n}`")
    md.append(f"Pending: `{pending_n}`")
    md.append(f"Closed: `{closed_n}`")
    md.append(f"Errors: `{errors_n}`")
    md.append("")
    if next_allowed:
        md.append("## Next best action")
        md.append(f"- `{next_allowed['decision_key']}` — {next_allowed['action']}")
        md.append("")
    md.append("## Decisions")
    for d in decisions:
        md.append(f"- `{d['status']}` `{d['decision_key']}` — {d['reason']}")
    md.append("")
    md.append("## Safety")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS DECISION KERNEL v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"kernel_status: {kernel_status}")
    print(f"phase        : {phase}")
    print(f"open         : {open_n}")
    print(f"pending      : {pending_n}")
    print(f"closed       : {closed_n}")
    print(f"errors       : {errors_n}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("NEXT BEST ACTION")
    print("-" * 100)
    if next_allowed:
        print(f"{next_allowed['decision_key']}: {next_allowed['action']}")
    else:
        print("NONE")
    print()
    print("DECISIONS")
    print("-" * 100)
    df = pd.DataFrame(decisions)
    print(df[["priority","decision_key","decision_type","status","allowed","reason","blocker"]].to_string(index=False))
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"CSV   : {csv_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
