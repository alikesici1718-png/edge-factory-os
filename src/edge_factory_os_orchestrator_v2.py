#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS ORCHESTRATOR v2
===============================

Purpose
-------
Second-generation top-level control-plane brain for the Edge Factory OS.

v1 problem
----------
The first orchestrator could read the raw research queue, but it did not know which queued
tasks had already been completed by later artifacts. So it could keep showing completed
jobs as OPEN.

v2 fix
------
This orchestrator consumes the latest OS Task Reconciler output:
    edge_factory_os_task_reconciler\task_reconcile_*\os_task_reconciliation.json

So it can distinguish:
    DONE
    STATE_ACKNOWLEDGED
    READY
    WAITING_FOR_PAPER
    WAITING_FOR_PAPER_SAMPLE
    FUTURE_RESEARCH
    BLOCKED

It then emits a clean OS-level state and next action plan.

It does NOT start paper/live trading.
It does NOT run child scripts.
It DOES NOT place orders.
It DOES NOT modify contracts/loggers.

Run
---
    python "C:\Users\alike\edge_factory_os_orchestrator_v2.py"

Optional command plan:
    python "C:\Users\alike\edge_factory_os_orchestrator_v2.py" --write_command_plan

Outputs
-------
    <workspace>\edge_factory_os_orchestrator_v2\orchestrator_v2_YYYYMMDD_HHMMSS\
        os_orchestrator_v2_report.md
        os_orchestrator_v2_state.json
        os_v2_next_actions.json
        os_v2_next_actions.csv
        os_v2_module_inventory.csv
        os_v2_command_plan.ps1    optional, plan only

Core principle
--------------
Only OS-level work matters here. Strategy-family work is allowed only when it is promoted
by the OS control-plane as a required validation or research task.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")
DEFAULT_PAPER_DIR_NAME = "paper_run_gate_MASTER_UPPER_SYSTEM"

MODULE_ARTIFACTS = {
    "state_inspector": ("edge_factory_os_state", "state_inspection_", "os_state_report.json"),
    "rolling_oos_validator": ("edge_factory_rolling_oos_validator", "rolling_oos_", "rolling_oos_decisions.json"),
    "rolling_oos_validator_v2": ("edge_factory_rolling_oos_validator_v2", "rolling_oos_v2_", "clean_os_family_state_seed.json"),
    "family_lifecycle_engine": ("edge_factory_family_lifecycle", "lifecycle_", "family_lifecycle_state.json"),
    "adaptive_capital_governor_v2": ("edge_factory_adaptive_capital_governor_v2", "capital_governor_", "capital_policy_proposal.json"),
    "execution_realism_checker": ("edge_factory_execution_realism_checker", "execution_realism_", "execution_realism_decisions.json"),
    "kill_switch_controller": ("edge_factory_kill_switch_controller", "kill_switch_", "kill_switch_policy.json"),
    "os_preflight_inspector": ("edge_factory_os_preflight", "preflight_", "paper_boot_decision.json"),
    "contract_reconciler": ("edge_factory_contract_reconciler", "contract_reconcile_", "contract_diff.json"),
    "autonomous_research_queue": ("edge_factory_autonomous_research_queue", "research_queue_", "research_queue.json"),
    "native_bps_validator": ("edge_factory_native_bps_validator", "native_bps_", "native_bps_validation.json"),
    "paper_boot_plan": ("edge_factory_paper_boot_plan", "paper_boot_plan_", "paper_boot_plan.json"),
    "task_reconciler": ("edge_factory_os_task_reconciler", "task_reconcile_", "os_task_reconciliation.json"),
}

REQUIRED_CONTROL_PLANE_MODULES = [
    "state_inspector",
    "rolling_oos_validator",
    "rolling_oos_validator_v2",
    "family_lifecycle_engine",
    "adaptive_capital_governor_v2",
    "execution_realism_checker",
    "kill_switch_controller",
    "os_preflight_inspector",
    "contract_reconciler",
    "autonomous_research_queue",
    "native_bps_validator",
    "paper_boot_plan",
    "task_reconciler",
]

SCRIPT_MAP = {
    "state_inspector": "edge_factory_os_state_inspector.py",
    "rolling_oos_validator": "edge_factory_rolling_oos_validator.py",
    "rolling_oos_validator_v2": "edge_factory_rolling_oos_validator_v2.py",
    "family_lifecycle_engine": "edge_factory_family_lifecycle_engine.py",
    "adaptive_capital_governor_v2": "edge_factory_adaptive_capital_governor_v2.py",
    "execution_realism_checker": "edge_factory_execution_realism_checker.py",
    "kill_switch_controller": "edge_factory_kill_switch_controller.py",
    "os_preflight_inspector": "edge_factory_os_preflight_inspector.py",
    "contract_reconciler": "edge_factory_contract_reconciler.py",
    "autonomous_research_queue": "edge_factory_autonomous_research_queue.py",
    "native_bps_validator": "edge_factory_native_bps_validator.py",
    "paper_boot_plan": "edge_factory_paper_boot_plan.py",
    "task_reconciler": "edge_factory_os_task_reconciler.py",
    "live_vs_backtest_drift_monitor": "edge_factory_live_vs_backtest_drift_monitor.py",
}

CORE_FILES = {
    "launcher": "start_edge_factory_MASTER_UPPER_SYSTEM.ps1",
    "sizing_runtime_helper": "sizing_contract_runtime.py",
}


@dataclass
class ModuleInventoryRow:
    module_key: str
    artifact_root: str
    latest_dir: Optional[str]
    required_file: str
    required_path: Optional[str]
    artifact_exists: bool
    script_path: Optional[str]
    script_exists: Optional[bool]
    modified_at: Optional[str]
    status: str
    message: str


@dataclass
class V2Action:
    priority: int
    action_key: str
    status: str
    category: str
    title: str
    reason: str
    command: Optional[str]
    safe_offline: bool
    starts_paper_or_live: bool
    blocked_by: List[str]
    source: str


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def iso_mtime(path: Path) -> Optional[str]:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
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


def inventory_modules(workspace: Path, script_dir: Path) -> List[ModuleInventoryRow]:
    rows: List[ModuleInventoryRow] = []
    for key, (root_name, prefix, required_file) in MODULE_ARTIFACTS.items():
        root = workspace / root_name
        latest = latest_child_dir(root, prefix)
        req = latest / required_file if latest else None
        artifact_exists = bool(req and req.exists() and req.is_file())
        script_name = SCRIPT_MAP.get(key)
        script_path = script_dir / script_name if script_name else None
        script_exists = bool(script_path and script_path.exists() and script_path.is_file()) if script_path else None

        if artifact_exists and (script_exists or script_exists is None):
            status = "PASS"
            message = "artifact and script present"
        elif not script_exists and key in REQUIRED_CONTROL_PLANE_MODULES:
            status = "FAIL"
            message = "script missing"
        elif not artifact_exists and key in REQUIRED_CONTROL_PLANE_MODULES:
            status = "FAIL"
            message = "artifact missing"
        else:
            status = "WARN"
            message = "optional artifact/script missing"

        rows.append(ModuleInventoryRow(
            module_key=key,
            artifact_root=str(root),
            latest_dir=str(latest) if latest else None,
            required_file=required_file,
            required_path=str(req) if req else None,
            artifact_exists=artifact_exists,
            script_path=str(script_path) if script_path else None,
            script_exists=script_exists,
            modified_at=iso_mtime(req) if artifact_exists and req else None,
            status=status,
            message=message,
        ))
    return rows


def module_path(inv: List[ModuleInventoryRow], key: str) -> Optional[Path]:
    for r in inv:
        if r.module_key == key and r.required_path:
            p = Path(r.required_path)
            if p.exists():
                return p
    return None


def load_artifacts(inv: List[ModuleInventoryRow]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for r in inv:
        p = Path(r.required_path) if r.required_path else None
        out[r.module_key] = optional_json(p)
    return out


def paper_started(workspace: Path) -> bool:
    p = workspace / DEFAULT_PAPER_DIR_NAME
    try:
        return p.exists() and any(p.iterdir())
    except Exception:
        return False


def closed_paper_trades_exist(workspace: Path) -> bool:
    p = workspace / DEFAULT_PAPER_DIR_NAME
    if not p.exists():
        return False
    patterns = ["*closed*trade*.csv", "*paper*trade*.csv", "trades.csv"]
    for pat in patterns:
        for f in p.rglob(pat):
            try:
                if f.exists() and f.stat().st_size > 200:
                    return True
            except Exception:
                pass
    return False


def derive_v2_state(workspace: Path, inv: List[ModuleInventoryRow], data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    failures = [r.module_key for r in inv if r.status == "FAIL"]
    warnings = [r.module_key for r in inv if r.status == "WARN"]

    preflight = data.get("os_preflight_inspector", {})
    task_rec = data.get("task_reconciler", {})
    kill = data.get("kill_switch_controller", {})
    native = data.get("native_bps_validator", {})

    # preflight paper_boot_decision.json uses "decision".
    paper_decision = str(preflight.get("decision") or preflight.get("paper_boot_decision") or "UNKNOWN")
    live_gate = str(preflight.get("live_gate") or kill.get("live_gate") or "LIVE_BLOCKED_UNKNOWN")
    paper_families = preflight.get("paper_eligible_families") or kill.get("paper_eligible_families") or []
    if not isinstance(paper_families, list):
        paper_families = []

    task_context = task_rec.get("context") if isinstance(task_rec.get("context"), dict) else {}
    rec_next = task_rec.get("next_os_actions") if isinstance(task_rec.get("next_os_actions"), list) else []
    rec_tasks = task_rec.get("reconciled_tasks") if isinstance(task_rec.get("reconciled_tasks"), list) else []

    done_count = len([t for t in rec_tasks if isinstance(t, dict) and t.get("reconciled_status") == "DONE"])
    waiting_count = len([t for t in rec_tasks if isinstance(t, dict) and str(t.get("reconciled_status", "")).startswith("WAITING")])
    future_count = len([t for t in rec_tasks if isinstance(t, dict) and t.get("reconciled_status") == "FUTURE_RESEARCH"])
    ready_count = len([t for t in rec_tasks if isinstance(t, dict) and t.get("reconciled_status") == "READY"])

    ps = paper_started(workspace)
    closed = closed_paper_trades_exist(workspace)

    if failures:
        os_mode = "CONTROL_PLANE_REPAIR_REQUIRED"
    elif ps and closed:
        os_mode = "PAPER_RUNNING_READY_FOR_DRIFT_CHECK"
    elif ps and not closed:
        os_mode = "PAPER_RUNNING_WAITING_FOR_CLOSED_TRADES"
    elif str(paper_decision).startswith("PAPER_READY"):
        os_mode = "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED"
    else:
        os_mode = "CONTROL_PLANE_BUILD_OR_REVIEW_REQUIRED"

    # v2 live hard override.
    live_allowed = False

    native_paper_gate = "UNKNOWN"
    native_live_gate = "UNKNOWN"
    if isinstance(native.get("context"), dict):
        native_paper_gate = str(native["context"].get("paper_quality_gate", "UNKNOWN"))
        native_live_gate = str(native["context"].get("live_quality_gate", "UNKNOWN"))

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "os_mode": os_mode,
        "paper_decision": paper_decision,
        "paper_started": ps,
        "closed_paper_trades_exist": closed,
        "paper_eligible_families": paper_families,
        "live_gate": live_gate,
        "live_allowed": live_allowed,
        "native_paper_gate": native_paper_gate,
        "native_live_gate": native_live_gate,
        "module_failures": failures,
        "module_warnings": warnings,
        "reconciled_done_count": done_count,
        "reconciled_ready_count": ready_count,
        "reconciled_waiting_count": waiting_count,
        "reconciled_future_research_count": future_count,
        "reconciler_next_action_count": len(rec_next),
        "principle": "Self-improving OS first. Do not drift into family/capital micro-work unless the OS-level state requires it.",
    }


def to_v2_action(row: Dict[str, Any]) -> V2Action:
    return V2Action(
        priority=int(row.get("priority", 999)),
        action_key=str(row.get("task_key", row.get("action_key", "unknown"))),
        status=str(row.get("reconciled_status", row.get("status", "OPEN"))),
        category=str(row.get("category", "UNKNOWN")),
        title=str(row.get("title", "")),
        reason=str(row.get("reason", "")),
        command=str(row.get("command")) if row.get("command") else None,
        safe_offline=bool(row.get("safe_to_run_offline", row.get("safe_offline", True))),
        starts_paper_or_live=bool(row.get("starts_paper_or_live", False)),
        blocked_by=list(row.get("blocked_by") or []),
        source=str(row.get("source", "task_reconciler")),
    )


def build_v2_actions(workspace: Path, script_dir: Path, state: Dict[str, Any], data: Dict[str, Dict[str, Any]]) -> List[V2Action]:
    actions: List[V2Action] = []
    task_rec = data.get("task_reconciler", {})
    rec_next = task_rec.get("next_os_actions") if isinstance(task_rec.get("next_os_actions"), list) else []

    # If control plane has failures, repair comes first.
    if state["module_failures"]:
        for m in state["module_failures"]:
            script = SCRIPT_MAP.get(m)
            cmd = f'python "{script_dir / script}"' if script else None
            actions.append(V2Action(
                priority=1,
                action_key=f"repair_{m}",
                status="BLOCKING",
                category="REPAIR",
                title=f"Repair missing OS module/artifact: {m}",
                reason="A required control-plane module is missing or broken.",
                command=cmd,
                safe_offline=True,
                starts_paper_or_live=False,
                blocked_by=[],
                source="orchestrator_v2",
            ))
        return actions

    # Consume reconciler next actions first.
    for row in rec_next:
        if not isinstance(row, dict):
            continue
        a = to_v2_action(row)
        # v2 hard filter: no autostart commands.
        if a.starts_paper_or_live:
            a.status = "BLOCKED_UNSAFE_AUTOSTART"
            a.command = None
        actions.append(a)

    # If no useful next actions remain, create OS state action.
    if not actions:
        actions.append(V2Action(
            priority=10,
            action_key="control_plane_current_waiting_for_paper_or_new_os_module",
            status="STATE_ACKNOWLEDGED",
            category="OS_STATE",
            title="Control plane is current; waiting for supervised paper data or next OS architecture module",
            reason="Task reconciler found no immediate runnable OS-level tasks.",
            command=None,
            safe_offline=True,
            starts_paper_or_live=False,
            blocked_by=["supervised paper decision or new OS architecture task"],
            source="orchestrator_v2",
        ))

    # Always append live hard block.
    if not any(a.action_key == "live_remains_blocked" for a in actions):
        actions.append(V2Action(
            priority=999,
            action_key="live_remains_blocked",
            status="HARD_RULE",
            category="SAFETY",
            title="Keep live trading blocked",
            reason="v2 cannot approve live. Live requires paper drift validation and manual review.",
            command=None,
            safe_offline=True,
            starts_paper_or_live=False,
            blocked_by=["paper drift validation", "manual live review"],
            source="orchestrator_v2",
        ))

    # Sort, dedupe.
    seen = set()
    out: List[V2Action] = []
    for a in sorted(actions, key=lambda x: x.priority):
        if a.action_key in seen:
            continue
        seen.add(a.action_key)
        out.append(a)
    return out


def inventory_df(rows: List[ModuleInventoryRow]) -> pd.DataFrame:
    return pd.DataFrame([asdict(r) for r in rows])


def action_df(actions: List[V2Action]) -> pd.DataFrame:
    rows = []
    for a in actions:
        d = asdict(a)
        d["blocked_by"] = " | ".join(a.blocked_by)
        rows.append(d)
    return pd.DataFrame(rows)


def write_command_plan(path: Path, actions: List[V2Action]) -> None:
    lines = []
    lines.append("# EDGE FACTORY OS ORCHESTRATOR v2 COMMAND PLAN")
    lines.append(f"# Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("# Plan only. Review manually. No paper/live autostart is included.")
    lines.append("")
    for a in actions:
        if not a.command:
            continue
        if a.starts_paper_or_live:
            lines.append(f"# BLOCKED unsafe autostart: {a.action_key}")
            continue
        lines.append(f"# P{a.priority:03d} {a.title}")
        lines.append(a.command)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, state: Dict[str, Any], inv: List[ModuleInventoryRow], actions: List[V2Action]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Orchestrator v2 Report")
    lines.append("")
    lines.append(f"Generated: `{state['generated_at']}`")
    lines.append(f"OS mode: **{state['os_mode']}**")
    lines.append(f"Paper decision: **{state['paper_decision']}**")
    lines.append(f"Paper started: **{state['paper_started']}**")
    lines.append(f"Closed paper trades: **{state['closed_paper_trades_exist']}**")
    lines.append(f"Live gate: **{state['live_gate']}**")
    lines.append(f"Live allowed: **{state['live_allowed']}**")
    lines.append("")

    lines.append("## Principle")
    lines.append("")
    lines.append(state["principle"])
    lines.append("")

    lines.append("## Reconciled task state")
    lines.append("")
    lines.append(f"- DONE: **{state['reconciled_done_count']}**")
    lines.append(f"- READY: **{state['reconciled_ready_count']}**")
    lines.append(f"- WAITING: **{state['reconciled_waiting_count']}**")
    lines.append(f"- FUTURE_RESEARCH: **{state['reconciled_future_research_count']}**")
    lines.append("")

    lines.append("## Next actions")
    lines.append("")
    lines.append("| Priority | Status | Category | Action | Command | Blocked by |")
    lines.append("|---:|---:|---|---|---|---|")
    for a in actions:
        cmd = f"`{a.command}`" if a.command else ""
        blocked = ", ".join(a.blocked_by)
        lines.append(f"| {a.priority} | {a.status} | {a.category} | {a.title} | {cmd} | {blocked} |")
    lines.append("")

    lines.append("## Module inventory")
    lines.append("")
    lines.append("| Module | Status | Artifact | Script | Message |")
    lines.append("|---|---:|---|---|---|")
    for r in inv:
        lines.append(f"| {r.module_key} | {r.status} | `{r.required_path}` | `{r.script_path}` | {r.message} |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("v2 uses the reconciled queue, so completed OS work should no longer appear as active OPEN work. The system is now closer to a real operating system: it can inspect its own state, avoid repeating completed tasks, and wait for the correct external condition before running paper-dependent checks.")
    lines.append("Live remains blocked.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS Orchestrator v2")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--script_dir", default=str(DEFAULT_SCRIPT_DIR))
    p.add_argument("--out_dir", default=None)
    p.add_argument("--write_command_plan", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    script_dir = Path(args.script_dir)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_orchestrator_v2"
    out_dir = out_root / f"orchestrator_v2_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    inv = inventory_modules(workspace, script_dir)
    data = load_artifacts(inv)
    state = derive_v2_state(workspace, inv, data)
    actions = build_v2_actions(workspace, script_dir, state, data)

    state_obj = {
        "state": state,
        "module_inventory": [asdict(r) for r in inv],
        "next_actions": [asdict(a) for a in actions],
        "hard_rules": [
            "Do not repeat DONE OS tasks.",
            "Do not start paper/live automatically.",
            "Live remains blocked until paper drift validation and manual live review.",
            "Family-level research is future work unless promoted by OS-level gates.",
        ],
    }

    write_json(out_dir / "os_orchestrator_v2_state.json", state_obj)
    write_json(out_dir / "os_v2_next_actions.json", [asdict(a) for a in actions])
    inventory_df(inv).to_csv(out_dir / "os_v2_module_inventory.csv", index=False)
    action_df(actions).to_csv(out_dir / "os_v2_next_actions.csv", index=False)
    write_report(out_dir / "os_orchestrator_v2_report.md", state, inv, actions)
    if args.write_command_plan:
        write_command_plan(out_dir / "os_v2_command_plan.ps1", actions)

    print("EDGE FACTORY OS ORCHESTRATOR v2")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"script_dir: {script_dir}")
    print(f"output_dir: {out_dir}")
    print(f"os_mode   : {state['os_mode']}")
    print(f"paper     : {state['paper_decision']} | started={state['paper_started']} | closed_trades={state['closed_paper_trades_exist']}")
    print(f"live      : {state['live_gate']} | allowed={state['live_allowed']}")
    print(f"modules   : failures={len(state['module_failures'])} warnings={len(state['module_warnings'])}")
    print(f"tasks     : done={state['reconciled_done_count']} ready={state['reconciled_ready_count']} waiting={state['reconciled_waiting_count']} future={state['reconciled_future_research_count']}")
    print("")
    print("NEXT OS ACTIONS")
    print("-" * 100)
    for a in actions[:12]:
        print(f"P{a.priority:03d} [{a.status}] {a.category} -> {a.title}")
        if a.blocked_by:
            print(f"     blocked_by: {', '.join(a.blocked_by)}")
        if a.command:
            print(f"     command: {a.command}")
        print(f"     reason: {a.reason}")
    print("")
    print(f"Report : {out_dir / 'os_orchestrator_v2_report.md'}")
    print(f"State  : {out_dir / 'os_orchestrator_v2_state.json'}")
    print(f"Actions: {out_dir / 'os_v2_next_actions.json'}")
    if args.write_command_plan:
        print(f"CmdPlan: {out_dir / 'os_v2_command_plan.ps1'}")

    return 0 if not state["module_failures"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
