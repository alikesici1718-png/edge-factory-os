#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS TASK RECONCILER v1
==================================

Purpose
-------
Self-awareness layer for the Edge Factory OS.

The OS Orchestrator can read the research queue, but the first v1 output may still list
old tasks as OPEN even after their artifacts already exist. This module fixes that OS
blind spot.

It reconciles:
    - autonomous research queue tasks
    - orchestrator next actions
    - actual artifact inventory on disk

Then it marks tasks as:
    DONE
    READY
    WAITING_FOR_PAPER
    BLOCKED
    STALE_REBUILD_RECOMMENDED
    FUTURE_RESEARCH

It does NOT start paper/live trading.
It does NOT run child scripts.
It does NOT modify contracts/loggers.

Run:
    python "C:\Users\alike\edge_factory_os_task_reconciler.py"

Outputs:
    <workspace>\edge_factory_os_task_reconciler\task_reconcile_YYYYMMDD_HHMMSS\
        os_task_reconciliation_report.md
        os_task_reconciliation.json
        reconciled_task_queue.csv
        next_os_actions.json
        next_os_actions.csv

Why this matters
----------------
A self-improving OS must not blindly repeat completed work. It must know:
    - what has already been built
    - what is still missing
    - what is blocked until paper data exists
    - what is only future research
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
DEFAULT_PAPER_DIR = DEFAULT_WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

# Artifact roots that prove an OS-level task is already complete.
COMPLETION_ARTIFACTS = {
    "build_native_bps_and_cost_validation": ("edge_factory_native_bps_validator", "native_bps_", "native_bps_validation.json"),
    "paper_runtime_dry_run_plan": ("edge_factory_paper_boot_plan", "paper_boot_plan_", "paper_boot_plan.json"),
    "patch_oos_validator_active_only_and_trade_level_filter": ("edge_factory_rolling_oos_validator_v2", "rolling_oos_v2_", "clean_os_family_state_seed.json"),
    "build_or_refresh_research_queue": ("edge_factory_autonomous_research_queue", "research_queue_", "research_queue.json"),
    "build_preflight_inspector": ("edge_factory_os_preflight", "preflight_", "paper_boot_decision.json"),
    "build_kill_switch_controller": ("edge_factory_kill_switch_controller", "kill_switch_", "kill_switch_policy.json"),
    "build_execution_realism_checker": ("edge_factory_execution_realism_checker", "execution_realism_", "execution_realism_decisions.json"),
    "build_adaptive_capital_governor_v2": ("edge_factory_adaptive_capital_governor_v2", "capital_governor_", "capital_policy_proposal.json"),
    "build_family_lifecycle_engine": ("edge_factory_family_lifecycle", "lifecycle_", "family_lifecycle_state.json"),
    "build_rolling_oos_validator": ("edge_factory_rolling_oos_validator", "rolling_oos_", "rolling_oos_decisions.json"),
}

# Orchestrator actions can use different names. Map them to completion checks.
ACTION_ALIASES = {
    "build_native_bps_and_cost_validation": "build_native_bps_and_cost_validation",
    "paper_runtime_dry_run_plan": "paper_runtime_dry_run_plan",
    "patch_oos_validator_active_only_and_trade_level_filter": "patch_oos_validator_active_only_and_trade_level_filter",
    "enforce_native_bps_fields_in_paper_logs": "enforce_native_bps_fields_in_paper_logs",
    "keep_os_in_paper_ready_state_or_start_supervised_paper_later": "keep_os_in_paper_ready_state_or_start_supervised_paper_later",
    "activate_drift_monitor_after_paper_closed_trades": "activate_drift_monitor_after_paper_closed_trades",
    "run_drift_monitor_after_paper_trades": "activate_drift_monitor_after_paper_closed_trades",
}

AFTER_PAPER_TASK_KEYS = {
    "activate_drift_monitor_after_paper_closed_trades",
    "run_drift_monitor_after_paper_trades",
    "enforce_native_bps_fields_in_paper_logs",
}

FUTURE_RESEARCH_PREFIXES = (
    "research_candidate_",
)


@dataclass
class ArtifactCheck:
    key: str
    root: str
    prefix: str
    required_file: str
    latest_dir: Optional[str]
    required_path: Optional[str]
    exists: bool
    modified_at: Optional[str]
    age_minutes: Optional[float]


@dataclass
class ReconciledTask:
    priority: int
    task_key: str
    title: str
    category: str
    original_status: str
    reconciled_status: str
    reason: str
    command: Optional[str]
    safe_to_run_offline: bool
    starts_paper_or_live: bool
    blocked_by: List[str]
    completion_artifact: Optional[str]
    source: str


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


def check_artifact(workspace: Path, key: str, spec: Tuple[str, str, str]) -> ArtifactCheck:
    root_name, prefix, required_file = spec
    root = workspace / root_name
    latest = latest_child_dir(root, prefix)
    req = latest / required_file if latest else None
    exists = bool(req and req.exists() and req.is_file())
    return ArtifactCheck(
        key=key,
        root=str(root),
        prefix=prefix,
        required_file=required_file,
        latest_dir=str(latest) if latest else None,
        required_path=str(req) if req else None,
        exists=exists,
        modified_at=iso_mtime(req) if exists and req else None,
        age_minutes=age_minutes(req) if exists and req else None,
    )


def artifact_checks(workspace: Path) -> Dict[str, ArtifactCheck]:
    return {k: check_artifact(workspace, k, spec) for k, spec in COMPLETION_ARTIFACTS.items()}


def discover_latest_json(workspace: Path, root_name: str, prefix: str, filename: str) -> Tuple[Optional[Path], Dict[str, Any]]:
    d = latest_child_dir(workspace / root_name, prefix)
    if not d:
        return None, {}
    path = d / filename
    return path if path.exists() else None, optional_json(path if path.exists() else None)


def load_task_sources(workspace: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []
    meta: Dict[str, Any] = {}

    rq_path, rq = discover_latest_json(workspace, "edge_factory_autonomous_research_queue", "research_queue_", "research_queue.json")
    orch_path, orch = discover_latest_json(workspace, "edge_factory_os_orchestrator", "orchestrator_", "os_next_actions.json")
    preflight_path, preflight = discover_latest_json(workspace, "edge_factory_os_preflight", "preflight_", "paper_boot_decision.json")
    paper_plan_path, paper_plan = discover_latest_json(workspace, "edge_factory_paper_boot_plan", "paper_boot_plan_", "paper_boot_plan.json")

    rq_tasks = rq.get("tasks") if isinstance(rq.get("tasks"), list) else []
    for t in rq_tasks:
        if not isinstance(t, dict):
            continue
        tasks.append({
            "priority": int(t.get("priority", 999)),
            "task_key": str(t.get("task_key", "unknown")),
            "title": str(t.get("title", "")),
            "category": str(t.get("category", "research_queue")),
            "status": str(t.get("status", "OPEN")),
            "reason": str(t.get("reason", "")),
            "command": str(t.get("suggested_command")) if t.get("suggested_command") else None,
            "safe_to_run_offline": bool(t.get("safe_offline", True)),
            "starts_paper_or_live": False,
            "blocked_by": list(t.get("blocked_by") or []),
            "source": "research_queue",
        })

    orch_tasks = orch.get("_list") if isinstance(orch.get("_list"), list) else []
    for t in orch_tasks:
        if not isinstance(t, dict):
            continue
        tasks.append({
            "priority": int(t.get("priority", 999)),
            "task_key": str(t.get("action_key", t.get("task_key", "unknown"))),
            "title": str(t.get("title", "")),
            "category": str(t.get("category", "orchestrator")),
            "status": str(t.get("status", "OPEN")),
            "reason": str(t.get("reason", "")),
            "command": str(t.get("command")) if t.get("command") else None,
            "safe_to_run_offline": bool(t.get("safe_to_run_offline", True)),
            "starts_paper_or_live": bool(t.get("starts_paper_or_live", False)),
            "blocked_by": list(t.get("blocked_by") or []),
            "source": "orchestrator",
        })

    meta["research_queue_path"] = str(rq_path) if rq_path else None
    meta["orchestrator_actions_path"] = str(orch_path) if orch_path else None
    meta["preflight_path"] = str(preflight_path) if preflight_path else None
    meta["paper_plan_path"] = str(paper_plan_path) if paper_plan_path else None
    meta["preflight"] = preflight
    meta["paper_plan"] = paper_plan
    return tasks, meta


def paper_has_closed_trades(workspace: Path) -> bool:
    paper_dir = workspace / "paper_run_gate_MASTER_UPPER_SYSTEM"
    if not paper_dir.exists():
        return False
    candidates = list(paper_dir.rglob("*closed*trade*.csv")) + list(paper_dir.rglob("*paper*trade*.csv")) + list(paper_dir.rglob("trades.csv"))
    for p in candidates:
        try:
            if p.exists() and p.stat().st_size > 200:
                return True
        except Exception:
            pass
    return False


def has_paper_started(workspace: Path) -> bool:
    paper_dir = workspace / "paper_run_gate_MASTER_UPPER_SYSTEM"
    return paper_dir.exists() and any(paper_dir.iterdir())


def normalize_task_key(task_key: str) -> str:
    return ACTION_ALIASES.get(task_key, task_key)


def reconcile_one(task: Dict[str, Any], artifacts: Dict[str, ArtifactCheck], workspace: Path, meta: Dict[str, Any]) -> ReconciledTask:
    raw_key = str(task.get("task_key", "unknown"))
    key = normalize_task_key(raw_key)
    title = str(task.get("title", ""))
    category = str(task.get("category", ""))
    original_status = str(task.get("status", "OPEN"))
    command = task.get("command")
    safe = bool(task.get("safe_to_run_offline", True))
    starts = bool(task.get("starts_paper_or_live", False))
    blocked_by = list(task.get("blocked_by") or [])
    source = str(task.get("source", "unknown"))
    priority = int(task.get("priority", 999))

    completion_artifact: Optional[str] = None
    status = "READY"
    reason = str(task.get("reason", ""))

    # Completed OS-level tasks.
    if key in COMPLETION_ARTIFACTS:
        chk = artifacts[key]
        completion_artifact = chk.required_path
        if chk.exists:
            status = "DONE"
            reason = f"Completed artifact exists: {chk.required_path}"
        else:
            status = "READY"
            reason = f"Required artifact missing: {chk.required_path}"

    # Known paper-gated tasks.
    elif key in AFTER_PAPER_TASK_KEYS:
        if not has_paper_started(workspace):
            status = "WAITING_FOR_PAPER"
            reason = "Task is valid only after supervised paper boot starts and logs exist."
            if "paper boot" not in [x.lower() for x in blocked_by]:
                blocked_by.append("paper boot")
        elif not paper_has_closed_trades(workspace):
            status = "WAITING_FOR_PAPER_SAMPLE"
            reason = "Paper appears to exist, but no closed trade sample was detected."
            blocked_by.append("closed paper trades")
        else:
            status = "READY"
            reason = "Paper sample exists; task may be runnable."

    # Boot control is a state, not a task to run.
    elif key == "keep_os_in_paper_ready_state_or_start_supervised_paper_later":
        status = "STATE_ACKNOWLEDGED"
        reason = "OS is paper-ready-not-started. This is a state, not an offline script task."
        blocked_by = ["explicit user decision before paper boot"]
        command = None

    # Future research candidates should not outrank OS control-plane work.
    elif any(key.startswith(prefix) for prefix in FUTURE_RESEARCH_PREFIXES):
        status = "FUTURE_RESEARCH"
        reason = "Candidate research is queued, but it must not distract from OS control-plane self-improvement."

    # Unknown suggested scripts may not exist.
    else:
        status = "READY"

    # Hard safety: never allow task reconciler to mark paper/live command runnable.
    if starts:
        status = "BLOCKED_UNSAFE_AUTOSTART"
        reason = "Task appears to start paper/live; reconciler refuses to run or approve autostart."

    return ReconciledTask(
        priority=priority,
        task_key=key,
        title=title,
        category=category,
        original_status=original_status,
        reconciled_status=status,
        reason=reason,
        command=command,
        safe_to_run_offline=safe,
        starts_paper_or_live=starts,
        blocked_by=blocked_by,
        completion_artifact=completion_artifact,
        source=source,
    )


def reconcile_tasks(tasks: List[Dict[str, Any]], artifacts: Dict[str, ArtifactCheck], workspace: Path, meta: Dict[str, Any]) -> List[ReconciledTask]:
    reconciled = [reconcile_one(t, artifacts, workspace, meta) for t in tasks]

    # De-duplicate: prefer DONE over READY, and lower priority number.
    rank = {
        "DONE": 0,
        "STATE_ACKNOWLEDGED": 1,
        "WAITING_FOR_PAPER": 2,
        "WAITING_FOR_PAPER_SAMPLE": 3,
        "READY": 4,
        "FUTURE_RESEARCH": 5,
        "BLOCKED": 6,
        "BLOCKED_UNSAFE_AUTOSTART": 7,
    }
    best: Dict[str, ReconciledTask] = {}
    for t in reconciled:
        old = best.get(t.task_key)
        if old is None:
            best[t.task_key] = t
        else:
            if (rank.get(t.reconciled_status, 99), t.priority) < (rank.get(old.reconciled_status, 99), old.priority):
                best[t.task_key] = t
    out = list(best.values())
    out.sort(key=lambda x: (x.reconciled_status not in {"READY", "WAITING_FOR_PAPER", "STATE_ACKNOWLEDGED"}, x.priority))
    return out


def choose_next_os_actions(reconciled: List[ReconciledTask], workspace: Path) -> List[ReconciledTask]:
    # The next actions should be OS-level, not family micro-work.
    selected: List[ReconciledTask] = []

    # Always include current state acknowledgement if present.
    for t in reconciled:
        if t.reconciled_status == "STATE_ACKNOWLEDGED":
            selected.append(t)
            break

    # Then include real READY OS-level tasks only.
    os_categories = ("SELF", "DATA", "LOGGING", "BOOT", "REPAIR", "execution_quality", "paper_readiness", "data_quality")
    for t in reconciled:
        if t in selected:
            continue
        if t.reconciled_status != "READY":
            continue
        if any(s.lower() in t.category.lower() for s in ["new_family_research", "known_family_validation"]):
            continue
        selected.append(t)
        if len(selected) >= 5:
            break

    # Add waiting-for-paper drift/logging tasks as future gates.
    for t in reconciled:
        if t in selected:
            continue
        if t.reconciled_status in {"WAITING_FOR_PAPER", "WAITING_FOR_PAPER_SAMPLE"}:
            selected.append(t)
        if len(selected) >= 8:
            break

    # If no executable task remains, create a synthetic OS status task.
    if not selected:
        selected.append(ReconciledTask(
            priority=10,
            task_key="os_control_plane_currently_complete",
            title="OS control plane is current; next meaningful data requires supervised paper or new OS module design",
            category="OS_STATE",
            original_status="SYNTHETIC",
            reconciled_status="STATE_ACKNOWLEDGED",
            reason="All known control-plane build tasks are done or waiting for paper data.",
            command=None,
            safe_to_run_offline=True,
            starts_paper_or_live=False,
            blocked_by=["supervised paper decision or new OS architecture task"],
            completion_artifact=None,
            source="task_reconciler",
        ))
    return selected


def task_df(tasks: List[ReconciledTask]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for t in tasks:
        d = asdict(t)
        d["blocked_by"] = " | ".join(t.blocked_by)
        rows.append(d)
    return pd.DataFrame(rows)


def artifact_df(artifacts: Dict[str, ArtifactCheck]) -> pd.DataFrame:
    return pd.DataFrame([asdict(a) for a in artifacts.values()])


def write_report(path: Path, context: Dict[str, Any], reconciled: List[ReconciledTask], next_actions: List[ReconciledTask], artifacts: Dict[str, ArtifactCheck]) -> None:
    done = [t for t in reconciled if t.reconciled_status == "DONE"]
    ready = [t for t in reconciled if t.reconciled_status == "READY"]
    waiting = [t for t in reconciled if t.reconciled_status.startswith("WAITING")]
    future = [t for t in reconciled if t.reconciled_status == "FUTURE_RESEARCH"]

    lines: List[str] = []
    lines.append("# Edge Factory OS Task Reconciliation Report")
    lines.append("")
    lines.append(f"Generated: `{context['generated_at']}`")
    lines.append(f"Workspace: `{context['workspace']}`")
    lines.append(f"Paper started: **{context['paper_started']}**")
    lines.append(f"Closed paper trades detected: **{context['paper_closed_trades_detected']}**")
    lines.append("")

    lines.append("## Executive summary")
    lines.append("")
    lines.append(f"- Total reconciled tasks: **{len(reconciled)}**")
    lines.append(f"- Done: **{len(done)}**")
    lines.append(f"- Ready: **{len(ready)}**")
    lines.append(f"- Waiting for paper/sample: **{len(waiting)}**")
    lines.append(f"- Future research: **{len(future)}**")
    lines.append("")

    lines.append("## Next OS actions")
    lines.append("")
    lines.append("| Priority | Status | Category | Task | Command | Blocked by |")
    lines.append("|---:|---:|---|---|---|---|")
    for t in next_actions:
        cmd = f"`{t.command}`" if t.command else ""
        blocked = ", ".join(t.blocked_by)
        lines.append(f"| {t.priority} | {t.reconciled_status} | {t.category} | {t.title} | {cmd} | {blocked} |")
    lines.append("")

    lines.append("## Completed tasks detected")
    lines.append("")
    if not done:
        lines.append("No completed tasks detected from artifact map.")
    else:
        for t in done:
            lines.append(f"- `{t.task_key}` → `{t.completion_artifact}`")
    lines.append("")

    lines.append("## Waiting tasks")
    lines.append("")
    if not waiting:
        lines.append("No waiting tasks.")
    else:
        for t in waiting:
            lines.append(f"- `{t.task_key}`: {t.reason}")
    lines.append("")

    lines.append("## Future research candidates")
    lines.append("")
    if not future:
        lines.append("No future research tasks in queue.")
    else:
        for t in future[:20]:
            lines.append(f"- `{t.task_key}`: {t.title}")
    lines.append("")

    lines.append("## Artifact completion map")
    lines.append("")
    lines.append("| Key | Exists | Path | Modified |")
    lines.append("|---|---:|---|---:|")
    for a in artifacts.values():
        lines.append(f"| {a.key} | {a.exists} | `{a.required_path}` | {a.modified_at} |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This module fixes the OS self-awareness gap: completed tasks should not keep appearing as OPEN just because an older research queue listed them. The next orchestrator version should consume this reconciled queue.")
    lines.append("Paper/live are not started by this module.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS task reconciler")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_task_reconciler"
    out_dir = out_root / f"task_reconcile_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    artifacts = artifact_checks(workspace)
    raw_tasks, meta = load_task_sources(workspace)
    reconciled = reconcile_tasks(raw_tasks, artifacts, workspace, meta)
    next_actions = choose_next_os_actions(reconciled, workspace)

    context = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "raw_task_count": len(raw_tasks),
        "reconciled_task_count": len(reconciled),
        "paper_started": has_paper_started(workspace),
        "paper_closed_trades_detected": paper_has_closed_trades(workspace),
        "sources": {k: v for k, v in meta.items() if not isinstance(v, dict)},
    }

    result = {
        "context": context,
        "reconciled_tasks": [asdict(t) for t in reconciled],
        "next_os_actions": [asdict(t) for t in next_actions],
        "artifact_completion_map": {k: asdict(v) for k, v in artifacts.items()},
        "hard_rules": [
            "Do not repeat DONE OS tasks unless their inputs changed.",
            "Do not run paper/live from task reconciliation.",
            "Family research remains FUTURE_RESEARCH unless promoted by an OS-level gate.",
            "Paper drift tasks wait until supervised paper closed trades exist.",
        ],
    }

    write_json(out_dir / "os_task_reconciliation.json", result)
    write_json(out_dir / "next_os_actions.json", [asdict(t) for t in next_actions])
    task_df(reconciled).to_csv(out_dir / "reconciled_task_queue.csv", index=False)
    task_df(next_actions).to_csv(out_dir / "next_os_actions.csv", index=False)
    artifact_df(artifacts).to_csv(out_dir / "artifact_completion_map.csv", index=False)
    write_report(out_dir / "os_task_reconciliation_report.md", context, reconciled, next_actions, artifacts)

    print("EDGE FACTORY OS TASK RECONCILER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"raw_tasks : {len(raw_tasks)}")
    print(f"reconciled: {len(reconciled)}")
    print(f"paper_started: {context['paper_started']}")
    print(f"closed_paper_trades_detected: {context['paper_closed_trades_detected']}")
    print("")
    print("NEXT OS ACTIONS")
    print("-" * 100)
    for t in next_actions[:12]:
        print(f"P{t.priority:03d} [{t.reconciled_status}] {t.category} -> {t.title}")
        if t.blocked_by:
            print(f"     blocked_by: {', '.join(t.blocked_by)}")
        if t.command:
            print(f"     command: {t.command}")
        print(f"     reason: {t.reason}")
    print("")
    done_count = len([t for t in reconciled if t.reconciled_status == "DONE"])
    waiting_count = len([t for t in reconciled if t.reconciled_status.startswith("WAITING")])
    future_count = len([t for t in reconciled if t.reconciled_status == "FUTURE_RESEARCH"])
    print(f"DONE={done_count} WAITING={waiting_count} FUTURE_RESEARCH={future_count}")
    print(f"Report : {out_dir / 'os_task_reconciliation_report.md'}")
    print(f"JSON   : {out_dir / 'os_task_reconciliation.json'}")
    print(f"Actions: {out_dir / 'next_os_actions.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
