#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS ORCHESTRATOR v1
===============================

Purpose
-------
Top-level control-plane brain for the Edge Factory OS.

This is NOT a strategy module.
This is NOT a capital optimizer.
This is NOT a paper/live launcher.

Its job is to inspect the whole Edge Factory workspace and decide what the OS should do next.
It reads the latest outputs from all OS modules, detects missing/stale/inconsistent pieces,
and creates a next-action plan.

Core OS goal
------------
Build a self-improving Edge Factory operating system that can:
    1) inspect its own workspace
    2) detect missing outputs/scripts
    3) understand current paper/live gate status
    4) choose the next OS-level task
    5) keep strategy-family details subordinate to OS-level decisions
    6) queue research/repair/validation tasks
    7) never start paper/live without an explicit supervised command

Run
---
    python "C:\Users\alike\edge_factory_os_orchestrator.py"

Optional strict mode:
    python "C:\Users\alike\edge_factory_os_orchestrator.py" --strict

Optional dry-run command generation:
    python "C:\Users\alike\edge_factory_os_orchestrator.py" --write_command_plan

Outputs
-------
    <workspace>\edge_factory_os_orchestrator\orchestrator_YYYYMMDD_HHMMSS\
        os_orchestrator_report.md
        os_orchestrator_state.json
        os_next_actions.json
        os_artifact_inventory.csv
        os_module_status.csv
        os_command_plan.ps1        only command plan; not executed

Important
---------
This module does not execute child scripts by default.
It only creates a command plan when requested.
It never starts paper/live trading.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")
DEFAULT_PAPER_DIR = DEFAULT_WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
DEFAULT_LAUNCHER = DEFAULT_SCRIPT_DIR / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1"

OS_MODULES = {
    "state_inspector": {
        "script": "edge_factory_os_state_inspector.py",
        "root": "edge_factory_os_state",
        "prefix": "state_inspection_",
        "required_file": "os_state_report.json",
        "stage": "FOUNDATION",
        "must_exist": True,
    },
    "rolling_oos_validator": {
        "script": "edge_factory_rolling_oos_validator.py",
        "root": "edge_factory_rolling_oos_validator",
        "prefix": "rolling_oos_",
        "required_file": "rolling_oos_decisions.json",
        "stage": "VALIDATION",
        "must_exist": True,
    },
    "rolling_oos_validator_v2": {
        "script": "edge_factory_rolling_oos_validator_v2.py",
        "root": "edge_factory_rolling_oos_validator_v2",
        "prefix": "rolling_oos_v2_",
        "required_file": "clean_os_family_state_seed.json",
        "stage": "DATA_HYGIENE",
        "must_exist": True,
    },
    "family_lifecycle_engine": {
        "script": "edge_factory_family_lifecycle_engine.py",
        "root": "edge_factory_family_lifecycle",
        "prefix": "lifecycle_",
        "required_file": "family_lifecycle_state.json",
        "stage": "LIFECYCLE",
        "must_exist": True,
    },
    "adaptive_capital_governor_v2": {
        "script": "edge_factory_adaptive_capital_governor_v2.py",
        "root": "edge_factory_adaptive_capital_governor_v2",
        "prefix": "capital_governor_",
        "required_file": "capital_policy_proposal.json",
        "stage": "RISK_POLICY",
        "must_exist": True,
    },
    "execution_realism_checker": {
        "script": "edge_factory_execution_realism_checker.py",
        "root": "edge_factory_execution_realism_checker",
        "prefix": "execution_realism_",
        "required_file": "execution_realism_decisions.json",
        "stage": "EXECUTION_VALIDATION",
        "must_exist": True,
    },
    "kill_switch_controller": {
        "script": "edge_factory_kill_switch_controller.py",
        "root": "edge_factory_kill_switch_controller",
        "prefix": "kill_switch_",
        "required_file": "kill_switch_policy.json",
        "stage": "SAFETY",
        "must_exist": True,
    },
    "os_preflight_inspector": {
        "script": "edge_factory_os_preflight_inspector.py",
        "root": "edge_factory_os_preflight",
        "prefix": "preflight_",
        "required_file": "paper_boot_decision.json",
        "stage": "BOOT_GATE",
        "must_exist": True,
    },
    "contract_reconciler": {
        "script": "edge_factory_contract_reconciler.py",
        "root": "edge_factory_contract_reconciler",
        "prefix": "contract_reconcile_",
        "required_file": "contract_diff.json",
        "stage": "CONFIG_RECONCILIATION",
        "must_exist": True,
    },
    "autonomous_research_queue": {
        "script": "edge_factory_autonomous_research_queue.py",
        "root": "edge_factory_autonomous_research_queue",
        "prefix": "research_queue_",
        "required_file": "research_queue.json",
        "stage": "SELF_IMPROVEMENT",
        "must_exist": True,
    },
    "native_bps_validator": {
        "script": "edge_factory_native_bps_validator.py",
        "root": "edge_factory_native_bps_validator",
        "prefix": "native_bps_",
        "required_file": "native_bps_validation.json",
        "stage": "DATA_QUALITY",
        "must_exist": True,
    },
    "paper_boot_plan": {
        "script": "edge_factory_paper_boot_plan.py",
        "root": "edge_factory_paper_boot_plan",
        "prefix": "paper_boot_plan_",
        "required_file": "paper_boot_plan.json",
        "stage": "PAPER_PLAN",
        "must_exist": True,
    },
    "live_vs_backtest_drift_monitor": {
        "script": "edge_factory_live_vs_backtest_drift_monitor.py",
        "root": "edge_factory_drift_monitor",
        "prefix": "drift_report_",
        "required_file": "drift_report.json",
        "stage": "AFTER_PAPER",
        "must_exist": False,
    },
}

CORE_NON_OS_FILES = {
    "launcher": DEFAULT_LAUNCHER,
    "position_sizing_contract": DEFAULT_WORKSPACE / "edge_factory_position_sizing_contract" / "position_sizing_contract.json",
    "sizing_runtime_helper": DEFAULT_SCRIPT_DIR / "sizing_contract_runtime.py",
}

PAPER_BLOCKED_STATES = {"PAPER_BLOCKED", "PAPER_BLOCKED_BPS_DATA_MISSING", "PAPER_BOOT_BLOCKED_NO_ELIGIBLE_FAMILIES"}
LIVE_ALLOWED_STATES = {"LIVE_ALLOWED", "LIVE_READY"}


@dataclass
class ModuleStatus:
    module_key: str
    stage: str
    script_path: str
    script_exists: bool
    artifact_root: str
    latest_dir: Optional[str]
    required_file: Optional[str]
    required_file_exists: bool
    required_file_path: Optional[str]
    modified_at: Optional[str]
    age_minutes: Optional[float]
    status: str
    severity: str
    message: str


@dataclass
class NextAction:
    priority: int
    action_key: str
    category: str
    title: str
    status: str
    reason: str
    command: Optional[str]
    safe_to_run_offline: bool
    starts_paper_or_live: bool
    blocked_by: List[str]
    expected_outputs: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def iso_mtime(path: Path) -> Optional[str]:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
    except Exception:
        return None


def age_minutes(path: Path) -> Optional[float]:
    try:
        return round((datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)).total_seconds() / 60.0, 3)
    except Exception:
        return None


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def optional_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        obj = load_json(path)
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, list):
            return {"_list": obj}
        return {}
    except Exception as e:
        return {"_load_error": str(e)}


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def module_status(workspace: Path, script_dir: Path, key: str, spec: Dict[str, Any]) -> ModuleStatus:
    script_path = script_dir / spec["script"]
    artifact_root = workspace / spec["root"]
    latest_dir = latest_child_dir(artifact_root, spec["prefix"])
    required_file_path = latest_dir / spec["required_file"] if latest_dir else None
    required_exists = bool(required_file_path and required_file_path.exists() and required_file_path.is_file())
    script_exists = script_path.exists() and script_path.is_file()

    must_exist = bool(spec.get("must_exist", True))
    if script_exists and required_exists:
        status = "PASS"
        severity = "INFO"
        message = "script and latest artifact exist"
    elif not script_exists and must_exist:
        status = "FAIL"
        severity = "BLOCKER"
        message = "required script missing"
    elif script_exists and not required_exists and must_exist:
        status = "FAIL"
        severity = "BLOCKER"
        message = "required artifact missing"
    elif not script_exists and not must_exist:
        status = "WARN"
        severity = "WARNING"
        message = "optional script missing or not built yet"
    else:
        status = "WARN"
        severity = "WARNING"
        message = "optional artifact missing or not produced yet"

    return ModuleStatus(
        module_key=key,
        stage=str(spec["stage"]),
        script_path=str(script_path),
        script_exists=script_exists,
        artifact_root=str(artifact_root),
        latest_dir=str(latest_dir) if latest_dir else None,
        required_file=spec.get("required_file"),
        required_file_exists=required_exists,
        required_file_path=str(required_file_path) if required_file_path else None,
        modified_at=iso_mtime(required_file_path) if required_exists and required_file_path else None,
        age_minutes=age_minutes(required_file_path) if required_exists and required_file_path else None,
        status=status,
        severity=severity,
        message=message,
    )


def collect_module_statuses(workspace: Path, script_dir: Path) -> List[ModuleStatus]:
    return [module_status(workspace, script_dir, key, spec) for key, spec in OS_MODULES.items()]


def status_by_key(statuses: List[ModuleStatus]) -> Dict[str, ModuleStatus]:
    return {s.module_key: s for s in statuses}


def load_artifact_data(statuses: List[ModuleStatus]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for s in statuses:
        path = Path(s.required_file_path) if s.required_file_path else None
        out[s.module_key] = optional_json(path)
    return out


def audit_core_files(workspace: Path, script_dir: Path) -> List[Dict[str, Any]]:
    # Rebuild paths from provided workspace/script_dir so defaults can be overridden.
    files = {
        "launcher": script_dir / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1",
        "position_sizing_contract": workspace / "edge_factory_position_sizing_contract" / "position_sizing_contract.json",
        "sizing_runtime_helper": script_dir / "sizing_contract_runtime.py",
    }
    rows: List[Dict[str, Any]] = []
    for key, path in files.items():
        exists = path.exists() and path.is_file()
        rows.append({
            "key": key,
            "path": str(path),
            "exists": exists,
            "status": "PASS" if exists else "FAIL",
            "modified_at": iso_mtime(path) if exists else None,
            "size_bytes": path.stat().st_size if exists else 0,
        })
    return rows


def safe_get(obj: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def derive_os_state(data: Dict[str, Dict[str, Any]], statuses: List[ModuleStatus], core_files: List[Dict[str, Any]], strict: bool) -> Dict[str, Any]:
    preflight = data.get("os_preflight_inspector", {})
    kill = data.get("kill_switch_controller", {})
    native = data.get("native_bps_validator", {})
    research = data.get("autonomous_research_queue", {})
    paper_plan = data.get("paper_boot_plan", {})
    cap = data.get("adaptive_capital_governor_v2", {})
    lifecycle = data.get("family_lifecycle_engine", {})
    oos_v2 = data.get("rolling_oos_validator_v2", {})

    paper_decision = str(
        preflight.get("decision")
        or preflight.get("paper_boot_decision")
        or safe_get(preflight, "context", "paper_boot_decision", default="UNKNOWN")
    )
    # paper_boot_decision.json uses key "decision".
    if paper_decision == "UNKNOWN" and "paper_boot_decision" in preflight:
        paper_decision = str(preflight.get("paper_boot_decision"))

    live_gate = str(
        preflight.get("live_gate")
        or kill.get("live_gate")
        or safe_get(native, "context", "live_quality_gate", default="LIVE_BLOCKED_UNKNOWN")
    )

    paper_eligible = preflight.get("paper_eligible_families") or kill.get("paper_eligible_families") or []
    if not isinstance(paper_eligible, list):
        paper_eligible = []

    native_paper_gate = safe_get(native, "context", "paper_quality_gate", default="UNKNOWN")
    native_live_gate = safe_get(native, "context", "live_quality_gate", default="UNKNOWN")

    research_task_count = safe_get(research, "context", "task_count", default=None)
    watchlist_count = safe_get(research, "context", "watchlist_count", default=None)

    module_failures = [s.module_key for s in statuses if s.status == "FAIL" and s.module_key != "live_vs_backtest_drift_monitor"]
    module_warnings = [s.module_key for s in statuses if s.status == "WARN"]
    core_failures = [r["key"] for r in core_files if r["status"] == "FAIL"]

    paper_started = DEFAULT_PAPER_DIR.exists() and any(DEFAULT_PAPER_DIR.iterdir()) if DEFAULT_PAPER_DIR.exists() else False

    live_allowed = live_gate in LIVE_ALLOWED_STATES or not str(live_gate).startswith("LIVE_BLOCKED") and "BLOCKED" not in str(live_gate)
    if live_allowed:
        # Hard safety override: orchestrator v1 never allows live.
        live_allowed = False
        live_safety_override = True
    else:
        live_safety_override = False

    if module_failures or core_failures:
        os_mode = "OS_REPAIR_REQUIRED"
    elif paper_decision in PAPER_BLOCKED_STATES:
        os_mode = "PAPER_BLOCKED_REPAIR_REQUIRED"
    elif paper_started:
        os_mode = "PAPER_RUNNING_MONITORING_REQUIRED"
    elif str(paper_decision).startswith("PAPER_READY") or str(paper_decision).startswith("PAPER_BOOT_ALLOWED"):
        os_mode = "PAPER_READY_NOT_STARTED"
    else:
        os_mode = "OS_BUILD_CONTINUE"

    if strict and module_warnings:
        os_mode = "OS_REVIEW_WARNINGS_REQUIRED"

    capital_total = cap.get("total_proposed_notional_known_families")
    active_family_seed = safe_get(oos_v2, "families", default={})
    lifecycle_entries = lifecycle.get("entries", []) if isinstance(lifecycle.get("entries"), list) else []

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "os_mode": os_mode,
        "paper_decision": paper_decision,
        "paper_started": paper_started,
        "paper_eligible_families": paper_eligible,
        "live_gate": live_gate,
        "live_allowed": False,
        "live_safety_override_applied": live_safety_override,
        "native_paper_gate": native_paper_gate,
        "native_live_gate": native_live_gate,
        "module_failures": module_failures,
        "module_warnings": module_warnings,
        "core_failures": core_failures,
        "research_task_count": research_task_count,
        "candidate_watchlist_count": watchlist_count,
        "capital_total_proposed": capital_total,
        "lifecycle_entry_count": len(lifecycle_entries),
        "strict": strict,
        "principle": "OS first: strategy/capital details are subordinate to the self-improving Edge Factory operating system.",
    }


def command_for_module(script_dir: Path, module_key: str) -> Optional[str]:
    spec = OS_MODULES.get(module_key)
    if not spec:
        return None
    return f'python "{script_dir / spec["script"]}"'


def build_next_actions(workspace: Path, script_dir: Path, statuses: List[ModuleStatus], data: Dict[str, Dict[str, Any]], os_state: Dict[str, Any]) -> List[NextAction]:
    actions: List[NextAction] = []
    by_key = status_by_key(statuses)

    # 1. Repair missing required modules/artifacts first.
    for s in statuses:
        if s.status == "FAIL" and s.module_key != "live_vs_backtest_drift_monitor":
            actions.append(NextAction(
                priority=1,
                action_key=f"repair_{s.module_key}",
                category="REPAIR",
                title=f"Repair missing or broken module: {s.module_key}",
                status="BLOCKING",
                reason=s.message,
                command=command_for_module(script_dir, s.module_key),
                safe_to_run_offline=True,
                starts_paper_or_live=False,
                blocked_by=[],
                expected_outputs=[s.required_file_path or s.required_file or "required artifact"],
            ))

    # 2. If core files missing, block.
    # This is checked at report level; command usually manual.

    # 3. If paper is ready and not started, OS-level next action should not be a family micro-validator by default.
    if os_state["os_mode"] == "PAPER_READY_NOT_STARTED":
        actions.append(NextAction(
            priority=10,
            action_key="keep_os_in_paper_ready_state_or_start_supervised_paper_later",
            category="BOOT_CONTROL",
            title="Paper is ready but not started; keep supervised gate or start only by explicit user command",
            status="READY_NOT_STARTED",
            reason="The OS has no blockers. Paper can be started later from the generated boot plan, but the orchestrator will not start it automatically.",
            command=None,
            safe_to_run_offline=True,
            starts_paper_or_live=False,
            blocked_by=["explicit user decision to start paper"],
            expected_outputs=[str(workspace / "paper_run_gate_MASTER_UPPER_SYSTEM")],
        ))

    # 4. If paper running, drift monitor becomes top priority.
    if os_state["paper_started"]:
        actions.append(NextAction(
            priority=5,
            action_key="run_drift_monitor_after_paper_trades",
            category="AFTER_PAPER",
            title="Run drift monitor when enough closed paper trades exist",
            status="WAIT_FOR_SAMPLE_OR_RUN_IF_READY",
            reason="Paper directory exists. The OS should compare paper vs backtest after closed trades accumulate.",
            command=f'python "{script_dir / "edge_factory_live_vs_backtest_drift_monitor.py"}" --base_dir "{workspace / "paper_run_gate_MASTER_UPPER_SYSTEM"}" --workspace "{workspace}"',
            safe_to_run_offline=True,
            starts_paper_or_live=False,
            blocked_by=["closed paper trades sample"],
            expected_outputs=[str(workspace / "edge_factory_drift_monitor")],
        ))

    # 5. Self-improvement tasks from research queue.
    research = data.get("autonomous_research_queue", {})
    tasks = research.get("tasks") if isinstance(research.get("tasks"), list) else []
    if tasks:
        # Add top OS-level tasks only; avoid individual family rabbit holes unless category is OS/data quality.
        allowed_categories = {"execution_quality", "paper_readiness", "data_quality", "after_paper_boot", "new_family_research"}
        added = 0
        for t in sorted(tasks, key=lambda x: int(x.get("priority", 999)) if isinstance(x, dict) else 999):
            if not isinstance(t, dict):
                continue
            cat = str(t.get("category", ""))
            if cat not in allowed_categories:
                continue
            # Skip family-specific micro tasks unless there is no OS-level work left.
            if cat == "new_family_research" and added < 3:
                # put candidates lower priority through queue, not immediate focus
                prio = max(70, int(t.get("priority", 70)))
            else:
                prio = int(t.get("priority", 50))
            actions.append(NextAction(
                priority=prio,
                action_key=str(t.get("task_key", "research_task")),
                category=f"RESEARCH_QUEUE:{cat}",
                title=str(t.get("title", "Research task")),
                status=str(t.get("status", "OPEN")),
                reason=str(t.get("reason", "from autonomous research queue")),
                command=str(t.get("suggested_command")) if t.get("suggested_command") else None,
                safe_to_run_offline=bool(t.get("safe_offline", True)),
                starts_paper_or_live=False,
                blocked_by=list(t.get("blocked_by") or []),
                expected_outputs=list(t.get("outputs") or []),
            ))
            added += 1
            if added >= 8:
                break
    else:
        actions.append(NextAction(
            priority=20,
            action_key="build_or_refresh_research_queue",
            category="SELF_IMPROVEMENT",
            title="Build or refresh autonomous research queue",
            status="OPEN",
            reason="No research queue tasks found; the OS needs a self-improvement queue.",
            command=command_for_module(script_dir, "autonomous_research_queue"),
            safe_to_run_offline=True,
            starts_paper_or_live=False,
            blocked_by=[],
            expected_outputs=[str(workspace / "edge_factory_autonomous_research_queue")],
        ))

    # 6. Native bps warning should become paper logging requirement, not endless offline micro-work.
    native = data.get("native_bps_validator", {})
    native_gate = os_state.get("native_live_gate", "")
    if "LIVE_BLOCKED" in str(native_gate):
        actions.append(NextAction(
            priority=30,
            action_key="enforce_native_bps_fields_in_paper_logs",
            category="LOGGING_CONTRACT",
            title="Ensure paper logs contain native execution fields before any drift/live decision",
            status="OPEN",
            reason="Historical BPS quality is enough for paper, not live. Native fields must be collected during paper.",
            command=None,
            safe_to_run_offline=True,
            starts_paper_or_live=False,
            blocked_by=["paper boot and closed paper trades"],
            expected_outputs=["closed paper trades with gross_bps/net_bps/fees/spread/slippage fields"],
        ))

    # 7. Live is blocked as a deliberate hard action.
    actions.append(NextAction(
        priority=999,
        action_key="live_remains_blocked",
        category="SAFETY",
        title="Keep live trading blocked",
        status="HARD_RULE",
        reason="Orchestrator v1 cannot approve live. Live requires paper drift validation and manual live review.",
        command=None,
        safe_to_run_offline=True,
        starts_paper_or_live=False,
        blocked_by=["paper drift validation", "manual live review"],
        expected_outputs=["future drift_decisions.json"],
    ))

    # Sort and de-duplicate by action_key.
    seen = set()
    deduped: List[NextAction] = []
    for a in sorted(actions, key=lambda x: x.priority):
        if a.action_key in seen:
            continue
        seen.add(a.action_key)
        deduped.append(a)
    return deduped


def module_status_df(statuses: List[ModuleStatus]) -> pd.DataFrame:
    return pd.DataFrame([asdict(s) for s in statuses])


def artifact_inventory_df(statuses: List[ModuleStatus], core_files: List[Dict[str, Any]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for s in statuses:
        rows.append({
            "type": "module_artifact",
            "key": s.module_key,
            "stage": s.stage,
            "path": s.required_file_path,
            "exists": s.required_file_exists,
            "status": s.status,
            "modified_at": s.modified_at,
            "age_minutes": s.age_minutes,
        })
    for r in core_files:
        rows.append({
            "type": "core_file",
            "key": r["key"],
            "stage": "CORE",
            "path": r["path"],
            "exists": r["exists"],
            "status": r["status"],
            "modified_at": r["modified_at"],
            "age_minutes": None,
        })
    return pd.DataFrame(rows)


def action_df(actions: List[NextAction]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for a in actions:
        d = asdict(a)
        d["blocked_by"] = " | ".join(a.blocked_by)
        d["expected_outputs"] = " | ".join(a.expected_outputs)
        rows.append(d)
    return pd.DataFrame(rows)


def write_command_plan(path: Path, actions: List[NextAction]) -> None:
    lines: List[str] = []
    lines.append("# EDGE FACTORY OS ORCHESTRATOR COMMAND PLAN")
    lines.append(f"# Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("# This file is a plan only. Review before running.")
    lines.append("# It must not start paper/live unless you manually choose that separately.")
    lines.append("")
    for a in actions:
        if not a.command:
            continue
        if a.starts_paper_or_live:
            lines.append(f"# SKIPPED unsafe paper/live command for {a.action_key}")
            continue
        lines.append(f"# P{a.priority:03d} {a.title}")
        lines.append(a.command)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, os_state: Dict[str, Any], statuses: List[ModuleStatus], core_files: List[Dict[str, Any]], actions: List[NextAction]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Orchestrator Report")
    lines.append("")
    lines.append(f"Generated: `{os_state['generated_at']}`")
    lines.append(f"OS mode: **{os_state['os_mode']}**")
    lines.append(f"Paper decision: **{os_state['paper_decision']}**")
    lines.append(f"Paper started: **{os_state['paper_started']}**")
    lines.append(f"Live gate: **{os_state['live_gate']}**")
    lines.append(f"Live allowed: **{os_state['live_allowed']}**")
    lines.append("")

    lines.append("## Principle")
    lines.append("")
    lines.append(os_state["principle"])
    lines.append("")

    lines.append("## Executive state")
    lines.append("")
    lines.append(f"- Module failures: `{len(os_state['module_failures'])}`")
    lines.append(f"- Module warnings: `{len(os_state['module_warnings'])}`")
    lines.append(f"- Core file failures: `{len(os_state['core_failures'])}`")
    lines.append(f"- Paper eligible families: `{', '.join(os_state['paper_eligible_families']) if os_state['paper_eligible_families'] else 'none'}`")
    lines.append(f"- Research tasks: `{os_state['research_task_count']}`")
    lines.append(f"- Candidate watchlist: `{os_state['candidate_watchlist_count']}`")
    lines.append(f"- Capital total proposed: `{os_state['capital_total_proposed']}`")
    lines.append("")

    if os_state["module_failures"] or os_state["core_failures"]:
        lines.append("## Blockers")
        lines.append("")
        for b in os_state["module_failures"]:
            lines.append(f"- module: `{b}`")
        for b in os_state["core_failures"]:
            lines.append(f"- core file: `{b}`")
        lines.append("")

    lines.append("## Module status")
    lines.append("")
    lines.append("| Module | Stage | Status | Script | Artifact | Message |")
    lines.append("|---|---:|---:|---|---|---|")
    for s in statuses:
        lines.append(f"| {s.module_key} | {s.stage} | {s.status} | `{s.script_path}` | `{s.required_file_path}` | {s.message} |")
    lines.append("")

    lines.append("## Core files")
    lines.append("")
    lines.append("| Key | Status | Path |")
    lines.append("|---|---:|---|")
    for r in core_files:
        lines.append(f"| {r['key']} | {r['status']} | `{r['path']}` |")
    lines.append("")

    lines.append("## Next actions")
    lines.append("")
    lines.append("| Priority | Category | Status | Action | Command | Blocked by |")
    lines.append("|---:|---|---:|---|---|---|")
    for a in actions[:20]:
        blocked = ", ".join(a.blocked_by)
        cmd = f"`{a.command}`" if a.command else ""
        lines.append(f"| {a.priority} | {a.category} | {a.status} | {a.title} | {cmd} | {blocked} |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("The orchestrator is the OS-level brain. It should prevent the project from drifting into one-family micro-work unless that work is required by the operating system itself.")
    lines.append("Paper can remain ready-not-started, while the OS continues self-improvement through research queueing, data hygiene, logging contracts, and drift readiness.")
    lines.append("Live remains blocked.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS Orchestrator")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--script_dir", default=str(DEFAULT_SCRIPT_DIR))
    p.add_argument("--out_dir", default=None)
    p.add_argument("--strict", action="store_true")
    p.add_argument("--write_command_plan", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    script_dir = Path(args.script_dir)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_orchestrator"
    out_dir = out_root / f"orchestrator_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    statuses = collect_module_statuses(workspace, script_dir)
    data = load_artifact_data(statuses)
    core_files = audit_core_files(workspace, script_dir)
    os_state = derive_os_state(data, statuses, core_files, strict=bool(args.strict))
    actions = build_next_actions(workspace, script_dir, statuses, data, os_state)

    state_obj = {
        "os_state": os_state,
        "module_statuses": [asdict(s) for s in statuses],
        "core_files": core_files,
        "next_actions": [asdict(a) for a in actions],
        "hard_rules": [
            "OS-level work first. Family-level work only when required by the OS state machine.",
            "Orchestrator v1 never starts paper or live.",
            "Live remains blocked until paper drift validation and manual live review.",
            "Research candidates are never activated directly from broad scan outputs.",
        ],
    }

    write_json(out_dir / "os_orchestrator_state.json", state_obj)
    write_json(out_dir / "os_next_actions.json", [asdict(a) for a in actions])
    module_status_df(statuses).to_csv(out_dir / "os_module_status.csv", index=False)
    artifact_inventory_df(statuses, core_files).to_csv(out_dir / "os_artifact_inventory.csv", index=False)
    action_df(actions).to_csv(out_dir / "os_next_actions.csv", index=False)
    write_report(out_dir / "os_orchestrator_report.md", os_state, statuses, core_files, actions)

    if args.write_command_plan:
        write_command_plan(out_dir / "os_command_plan.ps1", actions)

    print("EDGE FACTORY OS ORCHESTRATOR v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"script_dir: {script_dir}")
    print(f"output_dir: {out_dir}")
    print(f"os_mode   : {os_state['os_mode']}")
    print(f"paper     : {os_state['paper_decision']} | started={os_state['paper_started']}")
    print(f"live      : {os_state['live_gate']} | allowed={os_state['live_allowed']}")
    print(f"modules   : failures={len(os_state['module_failures'])} warnings={len(os_state['module_warnings'])}")
    print(f"core      : failures={len(os_state['core_failures'])}")
    print("")

    if os_state["module_failures"] or os_state["core_failures"]:
        print("BLOCKERS")
        print("-" * 100)
        for b in os_state["module_failures"]:
            print(f"module: {b}")
        for b in os_state["core_failures"]:
            print(f"core_file: {b}")
        print("")

    print("TOP NEXT ACTIONS")
    print("-" * 100)
    for a in actions[:10]:
        print(f"P{a.priority:03d} [{a.category}] {a.status} -> {a.title}")
        print(f"     safe_offline={a.safe_to_run_offline} starts_paper_or_live={a.starts_paper_or_live}")
        if a.blocked_by:
            print(f"     blocked_by: {', '.join(a.blocked_by)}")
        if a.command:
            print(f"     command: {a.command}")
        print(f"     reason: {a.reason}")
    print("")
    print(f"Report : {out_dir / 'os_orchestrator_report.md'}")
    print(f"State  : {out_dir / 'os_orchestrator_state.json'}")
    print(f"Actions: {out_dir / 'os_next_actions.json'}")
    if args.write_command_plan:
        print(f"CmdPlan: {out_dir / 'os_command_plan.ps1'}")

    return 0 if not os_state["module_failures"] and not os_state["core_failures"] else 2



if __name__ == "__main__":
    raise SystemExit(main())
