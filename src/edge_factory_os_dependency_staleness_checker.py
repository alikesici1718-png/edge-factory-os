#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS DEPENDENCY / STALENESS CHECKER v1
=================================================

Purpose
-------
OS-level dependency graph and artifact staleness checker for the Edge Factory project.

This is NOT a strategy module.
This is NOT a capital optimizer.
This does NOT start paper/live.
This does NOT modify contracts/loggers.

Problem it solves
-----------------
The OS can now see that modules exist and that completed tasks are DONE. But a real
self-improving operating system also needs to know:

    "If an upstream artifact changed after a downstream artifact was built,
     is the downstream artifact now stale and should it be rebuilt?"

Example:
    rolling_oos_validator output changes
        -> rolling_oos_validator_v2 is stale
        -> lifecycle is stale
        -> capital governor is stale
        -> execution checker is stale
        -> kill-switch is stale
        -> preflight is stale
        -> orchestrator should not trust old downstream decisions blindly

Run
---
    python "C:\Users\alike\edge_factory_os_dependency_staleness_checker.py"

Outputs
-------
    <workspace>\edge_factory_os_dependency_staleness\dependency_staleness_YYYYMMDD_HHMMSS\
        os_dependency_staleness_report.md
        os_dependency_staleness.json
        os_dependency_graph.csv
        stale_rebuild_plan.csv
        stale_rebuild_commands.ps1

Design
------
The checker builds a dependency graph over OS artifacts, compares timestamps, then emits:
    - FRESH
    - MISSING
    - STALE_DIRECT
    - STALE_TRANSITIVE
    - OPTIONAL_MISSING

It never executes rebuild commands. It only writes a plan.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Set

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")


MODULES: Dict[str, Dict[str, Any]] = {
    "state_inspector": {
        "script": "edge_factory_os_state_inspector.py",
        "root": "edge_factory_os_state",
        "prefix": "state_inspection_",
        "file": "os_state_report.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
    },
    "rolling_oos_validator": {
        "script": "edge_factory_rolling_oos_validator.py",
        "root": "edge_factory_rolling_oos_validator",
        "prefix": "rolling_oos_",
        "file": "rolling_oos_decisions.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
    },
    "rolling_oos_validator_v2": {
        "script": "edge_factory_rolling_oos_validator_v2.py",
        "root": "edge_factory_rolling_oos_validator_v2",
        "prefix": "rolling_oos_v2_",
        "file": "clean_os_family_state_seed.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
        "deps": ["rolling_oos_validator"],
    },
    "family_lifecycle_engine": {
        "script": "edge_factory_family_lifecycle_engine.py",
        "root": "edge_factory_family_lifecycle",
        "prefix": "lifecycle_",
        "file": "family_lifecycle_state.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
        "deps": ["rolling_oos_validator", "rolling_oos_validator_v2"],
    },
    "adaptive_capital_governor_v2": {
        "script": "edge_factory_adaptive_capital_governor_v2.py",
        "root": "edge_factory_adaptive_capital_governor_v2",
        "prefix": "capital_governor_",
        "file": "capital_policy_proposal.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
        "deps": ["family_lifecycle_engine"],
    },
    "contract_reconciler": {
        "script": "edge_factory_contract_reconciler.py",
        "root": "edge_factory_contract_reconciler",
        "prefix": "contract_reconcile_",
        "file": "contract_diff.json",
        "required": True,
        "safe_offline": True,
        "command_args": "--apply",
        "deps": ["adaptive_capital_governor_v2"],
        "note": "This command uses --apply. Review before running manually.",
    },
    "execution_realism_checker": {
        "script": "edge_factory_execution_realism_checker.py",
        "root": "edge_factory_execution_realism_checker",
        "prefix": "execution_realism_",
        "file": "execution_realism_decisions.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
        "deps": ["adaptive_capital_governor_v2", "family_lifecycle_engine", "rolling_oos_validator"],
    },
    "kill_switch_controller": {
        "script": "edge_factory_kill_switch_controller.py",
        "root": "edge_factory_kill_switch_controller",
        "prefix": "kill_switch_",
        "file": "kill_switch_policy.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
        "deps": ["execution_realism_checker"],
    },
    "os_preflight_inspector": {
        "script": "edge_factory_os_preflight_inspector.py",
        "root": "edge_factory_os_preflight",
        "prefix": "preflight_",
        "file": "paper_boot_decision.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
        "deps": ["kill_switch_controller", "contract_reconciler", "native_bps_validator"],
    },
    "autonomous_research_queue": {
        "script": "edge_factory_autonomous_research_queue.py",
        "root": "edge_factory_autonomous_research_queue",
        "prefix": "research_queue_",
        "file": "research_queue.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
        "deps": ["os_preflight_inspector", "kill_switch_controller", "execution_realism_checker", "family_lifecycle_engine"],
    },
    "native_bps_validator": {
        "script": "edge_factory_native_bps_validator.py",
        "root": "edge_factory_native_bps_validator",
        "prefix": "native_bps_",
        "file": "native_bps_validation.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
        "deps": ["rolling_oos_validator", "adaptive_capital_governor_v2"],
    },
    "paper_boot_plan": {
        "script": "edge_factory_paper_boot_plan.py",
        "root": "edge_factory_paper_boot_plan",
        "prefix": "paper_boot_plan_",
        "file": "paper_boot_plan.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
        "deps": ["os_preflight_inspector", "native_bps_validator", "kill_switch_controller", "adaptive_capital_governor_v2"],
    },
    "task_reconciler": {
        "script": "edge_factory_os_task_reconciler.py",
        "root": "edge_factory_os_task_reconciler",
        "prefix": "task_reconcile_",
        "file": "os_task_reconciliation.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
        "deps": ["autonomous_research_queue", "paper_boot_plan", "native_bps_validator", "rolling_oos_validator_v2"],
    },
    "os_orchestrator_v2": {
        "script": "edge_factory_os_orchestrator_v2.py",
        "root": "edge_factory_os_orchestrator_v2",
        "prefix": "orchestrator_v2_",
        "file": "os_orchestrator_v2_state.json",
        "required": True,
        "safe_offline": True,
        "command_args": "",
        "deps": ["task_reconciler", "os_preflight_inspector", "kill_switch_controller", "native_bps_validator"],
    },
    "dependency_staleness_checker": {
        "script": "edge_factory_os_dependency_staleness_checker.py",
        "root": "edge_factory_os_dependency_staleness",
        "prefix": "dependency_staleness_",
        "file": "os_dependency_staleness.json",
        "required": False,
        "safe_offline": True,
        "command_args": "",
        "deps": ["os_orchestrator_v2"],
    },
    "live_vs_backtest_drift_monitor": {
        "script": "edge_factory_live_vs_backtest_drift_monitor.py",
        "root": "edge_factory_drift_monitor",
        "prefix": "drift_report_",
        "file": "drift_report.json",
        "required": False,
        "safe_offline": True,
        "command_args": "",
        "deps": ["paper_boot_plan"],
        "blocked_by": ["supervised paper boot", "closed paper trades"],
    },
}


@dataclass
class ArtifactState:
    module_key: str
    script_path: str
    script_exists: bool
    artifact_root: str
    latest_dir: Optional[str]
    artifact_path: Optional[str]
    artifact_exists: bool
    modified_ts: Optional[float]
    modified_at: Optional[str]
    required: bool
    deps: List[str]
    direct_stale_deps: List[str]
    transitive_stale_deps: List[str]
    status: str
    reason: str
    command: str
    safe_offline: bool
    blocked_by: List[str]


@dataclass
class RebuildStep:
    order: int
    module_key: str
    status: str
    reason: str
    command: str
    safe_offline: bool
    blocked_by: List[str]
    note: Optional[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def mtime(path: Optional[Path]) -> Optional[float]:
    try:
        if path and path.exists():
            return path.stat().st_mtime
    except Exception:
        return None
    return None


def iso_from_ts(ts: Optional[float]) -> Optional[str]:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def command_for(script_dir: Path, module_key: str) -> str:
    spec = MODULES[module_key]
    script = script_dir / spec["script"]
    args = str(spec.get("command_args", "")).strip()
    if args:
        return f'python "{script}" {args}'
    return f'python "{script}"'


def collect_base_states(workspace: Path, script_dir: Path) -> Dict[str, ArtifactState]:
    states: Dict[str, ArtifactState] = {}
    for key, spec in MODULES.items():
        root = workspace / spec["root"]
        latest = latest_child_dir(root, spec["prefix"])
        artifact = latest / spec["file"] if latest else None
        artifact_exists = bool(artifact and artifact.exists() and artifact.is_file())
        ts = mtime(artifact) if artifact_exists else None
        script = script_dir / spec["script"]
        states[key] = ArtifactState(
            module_key=key,
            script_path=str(script),
            script_exists=script.exists() and script.is_file(),
            artifact_root=str(root),
            latest_dir=str(latest) if latest else None,
            artifact_path=str(artifact) if artifact else None,
            artifact_exists=artifact_exists,
            modified_ts=ts,
            modified_at=iso_from_ts(ts),
            required=bool(spec.get("required", True)),
            deps=list(spec.get("deps", [])),
            direct_stale_deps=[],
            transitive_stale_deps=[],
            status="UNKNOWN",
            reason="",
            command=command_for(script_dir, key),
            safe_offline=bool(spec.get("safe_offline", True)),
            blocked_by=list(spec.get("blocked_by", [])),
        )
    return states


def direct_stale_deps(key: str, states: Dict[str, ArtifactState]) -> List[str]:
    cur = states[key]
    if not cur.artifact_exists or cur.modified_ts is None:
        return []
    stale: List[str] = []
    for dep in cur.deps:
        d = states.get(dep)
        if not d or not d.artifact_exists or d.modified_ts is None:
            continue
        if d.modified_ts > cur.modified_ts:
            stale.append(dep)
    return stale


def compute_transitive_stale(key: str, states: Dict[str, ArtifactState], memo: Dict[str, Set[str]]) -> Set[str]:
    if key in memo:
        return memo[key]
    stale: Set[str] = set(states[key].direct_stale_deps)
    for dep in states[key].deps:
        d = states.get(dep)
        if d is None:
            continue
        if d.status in {"MISSING", "REQUIRED_SCRIPT_MISSING", "OPTIONAL_MISSING"}:
            stale.add(dep)
        stale |= compute_transitive_stale(dep, states, memo)
    memo[key] = stale
    return stale


def evaluate_states(states: Dict[str, ArtifactState]) -> Dict[str, ArtifactState]:
    # Direct stale first.
    for key in states:
        states[key].direct_stale_deps = direct_stale_deps(key, states)

    # Initial missing/script status.
    for key, s in states.items():
        if not s.script_exists and s.required:
            s.status = "REQUIRED_SCRIPT_MISSING"
            s.reason = "required script is missing"
        elif not s.artifact_exists and s.required:
            s.status = "MISSING"
            s.reason = "required artifact is missing"
        elif not s.artifact_exists and not s.required:
            s.status = "OPTIONAL_MISSING"
            s.reason = "optional artifact not produced yet"
        elif s.direct_stale_deps:
            s.status = "STALE_DIRECT"
            s.reason = "upstream artifact newer than this artifact: " + ", ".join(s.direct_stale_deps)
        else:
            s.status = "FRESH"
            s.reason = "artifact exists and no direct newer dependency detected"

    # Transitive stale.
    memo: Dict[str, Set[str]] = {}
    for key in states:
        states[key].transitive_stale_deps = sorted(compute_transitive_stale(key, states, memo))

    for key, s in states.items():
        if s.status == "FRESH" and s.transitive_stale_deps:
            # Do not mark optional drift monitor stale just because it waits for paper.
            if key == "live_vs_backtest_drift_monitor" and s.blocked_by:
                s.status = "OPTIONAL_WAITING"
                s.reason = "optional module waiting for: " + ", ".join(s.blocked_by)
            else:
                s.status = "STALE_TRANSITIVE"
                s.reason = "a dependency chain contains stale/missing modules: " + ", ".join(s.transitive_stale_deps)

    return states


def topo_sort_modules(states: Dict[str, ArtifactState]) -> List[str]:
    visited: Set[str] = set()
    temp: Set[str] = set()
    out: List[str] = []

    def visit(k: str) -> None:
        if k in visited:
            return
        if k in temp:
            return
        temp.add(k)
        for d in states[k].deps:
            if d in states:
                visit(d)
        temp.remove(k)
        visited.add(k)
        out.append(k)

    for key in states:
        visit(key)
    return out


def build_rebuild_plan(states: Dict[str, ArtifactState]) -> List[RebuildStep]:
    order = topo_sort_modules(states)
    rebuild_statuses = {"MISSING", "REQUIRED_SCRIPT_MISSING", "STALE_DIRECT", "STALE_TRANSITIVE"}
    steps: List[RebuildStep] = []
    idx = 1
    for key in order:
        s = states[key]
        if s.status not in rebuild_statuses:
            continue
        if key == "live_vs_backtest_drift_monitor":
            continue
        note = MODULES[key].get("note")
        steps.append(RebuildStep(
            order=idx,
            module_key=key,
            status=s.status,
            reason=s.reason,
            command=s.command,
            safe_offline=s.safe_offline,
            blocked_by=s.blocked_by,
            note=note,
        ))
        idx += 1
    return steps


def graph_df(states: Dict[str, ArtifactState]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for key, s in states.items():
        if not s.deps:
            rows.append({"module_key": key, "dependency": None, "status": s.status})
        else:
            for dep in s.deps:
                rows.append({"module_key": key, "dependency": dep, "status": s.status})
    return pd.DataFrame(rows)


def states_df(states: Dict[str, ArtifactState]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for s in states.values():
        d = asdict(s)
        d["deps"] = " | ".join(s.deps)
        d["direct_stale_deps"] = " | ".join(s.direct_stale_deps)
        d["transitive_stale_deps"] = " | ".join(s.transitive_stale_deps)
        d["blocked_by"] = " | ".join(s.blocked_by)
        rows.append(d)
    return pd.DataFrame(rows)


def rebuild_df(steps: List[RebuildStep]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for s in steps:
        d = asdict(s)
        d["blocked_by"] = " | ".join(s.blocked_by)
        rows.append(d)
    return pd.DataFrame(rows)


def write_command_plan(path: Path, steps: List[RebuildStep]) -> None:
    lines: List[str] = []
    lines.append("# EDGE FACTORY OS STALENESS REBUILD PLAN")
    lines.append(f"# Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("# Plan only. Review manually. This file was not executed.")
    lines.append("# No paper/live start command is included.")
    lines.append("")
    if not steps:
        lines.append("# No stale required control-plane artifacts detected.")
    for s in steps:
        lines.append(f"# Step {s.order}: {s.module_key} [{s.status}]")
        lines.append(f"# reason: {s.reason}")
        if s.note:
            lines.append(f"# note: {s.note}")
        if s.blocked_by:
            lines.append(f"# blocked_by: {', '.join(s.blocked_by)}")
        if s.safe_offline:
            lines.append(s.command)
        else:
            lines.append(f"# NOT SAFE OFFLINE: {s.command}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, context: Dict[str, Any], states: Dict[str, ArtifactState], steps: List[RebuildStep]) -> None:
    counts: Dict[str, int] = {}
    for s in states.values():
        counts[s.status] = counts.get(s.status, 0) + 1

    lines: List[str] = []
    lines.append("# Edge Factory OS Dependency / Staleness Report")
    lines.append("")
    lines.append(f"Generated: `{context['generated_at']}`")
    lines.append(f"Workspace: `{context['workspace']}`")
    lines.append(f"Script dir: `{context['script_dir']}`")
    lines.append(f"Overall state: **{context['overall_state']}**")
    lines.append("")

    lines.append("## Status counts")
    lines.append("")
    for k in sorted(counts):
        lines.append(f"- {k}: **{counts[k]}**")
    lines.append("")

    lines.append("## Rebuild plan")
    lines.append("")
    if not steps:
        lines.append("No required stale/missing control-plane artifacts detected. The OS dependency chain is current.")
    else:
        lines.append("| Order | Module | Status | Command | Reason |")
        lines.append("|---:|---|---:|---|---|")
        for s in steps:
            lines.append(f"| {s.order} | {s.module_key} | {s.status} | `{s.command}` | {s.reason} |")
    lines.append("")

    lines.append("## Artifact states")
    lines.append("")
    lines.append("| Module | Status | Modified | Direct stale deps | Transitive stale deps | Artifact |")
    lines.append("|---|---:|---:|---|---|---|")
    for key in topo_sort_modules(states):
        s = states[key]
        lines.append(
            f"| {s.module_key} | {s.status} | {s.modified_at} | {', '.join(s.direct_stale_deps)} | "
            f"{', '.join(s.transitive_stale_deps)} | `{s.artifact_path}` |"
        )
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This module gives the OS a dependency graph. Existence is not enough; downstream artifacts must also be newer than the upstream outputs they depend on. This prevents the control plane from trusting stale decisions after a rebuild.")
    lines.append("No paper/live actions were executed.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS dependency/staleness checker")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--script_dir", default=str(DEFAULT_SCRIPT_DIR))
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    script_dir = Path(args.script_dir)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_dependency_staleness"
    out_dir = out_root / f"dependency_staleness_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    states = collect_base_states(workspace, script_dir)
    states = evaluate_states(states)
    steps = build_rebuild_plan(states)

    required_bad = [s.module_key for s in states.values() if s.required and s.status in {"MISSING", "REQUIRED_SCRIPT_MISSING", "STALE_DIRECT", "STALE_TRANSITIVE"}]
    if required_bad:
        overall = "REBUILD_REQUIRED"
    else:
        overall = "DEPENDENCY_CHAIN_CURRENT"

    context = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "script_dir": str(script_dir),
        "overall_state": overall,
        "rebuild_required_modules": required_bad,
        "rebuild_step_count": len(steps),
    }

    result = {
        "context": context,
        "artifact_states": {k: asdict(v) for k, v in states.items()},
        "rebuild_plan": [asdict(s) for s in steps],
        "hard_rules": [
            "Do not trust downstream artifacts if an upstream dependency is newer.",
            "Do not execute rebuild commands automatically.",
            "Do not start paper/live from staleness checker.",
            "Review --apply commands manually before running them.",
        ],
    }

    write_json(out_dir / "os_dependency_staleness.json", result)
    states_df(states).to_csv(out_dir / "os_artifact_states.csv", index=False)
    graph_df(states).to_csv(out_dir / "os_dependency_graph.csv", index=False)
    rebuild_df(steps).to_csv(out_dir / "stale_rebuild_plan.csv", index=False)
    write_command_plan(out_dir / "stale_rebuild_commands.ps1", steps)
    write_report(out_dir / "os_dependency_staleness_report.md", context, states, steps)

    print("EDGE FACTORY OS DEPENDENCY / STALENESS CHECKER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"script_dir: {script_dir}")
    print(f"output_dir: {out_dir}")
    print(f"overall   : {overall}")
    print(f"rebuild_steps: {len(steps)}")
    print("")
    print("STATUS COUNTS")
    print("-" * 100)
    counts: Dict[str, int] = {}
    for s in states.values():
        counts[s.status] = counts.get(s.status, 0) + 1
    for k in sorted(counts):
        print(f"{k:26s}: {counts[k]}")
    print("")
    print("REBUILD PLAN")
    print("-" * 100)
    if not steps:
        print("No required stale/missing control-plane artifacts detected.")
    else:
        for s in steps:
            print(f"{s.order:02d}. {s.module_key:32s} status={s.status:18s} safe_offline={s.safe_offline}")
            print(f"    reason : {s.reason}")
            print(f"    command: {s.command}")
            if s.note:
                print(f"    note   : {s.note}")
    print("")
    print(f"Report : {out_dir / 'os_dependency_staleness_report.md'}")
    print(f"JSON   : {out_dir / 'os_dependency_staleness.json'}")
    print(f"Plan   : {out_dir / 'stale_rebuild_commands.ps1'}")
    return 0 if not steps else 2


if __name__ == "__main__":
    raise SystemExit(main())
