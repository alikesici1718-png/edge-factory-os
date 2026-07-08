#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS SAFE REBUILD RUNNER v1
======================================

Purpose
-------
Safe rebuild planner/executor for the Edge Factory OS dependency chain.

The dependency staleness checker can produce a rebuild plan. But not every rebuild step
should be blindly executed. Example:
    contract_reconciler.py --apply
changes active configuration, so it must be separated from normal non-mutating rebuilds.

This module reads the latest:
    edge_factory_os_dependency_staleness\dependency_staleness_*\os_dependency_staleness.json

Then separates rebuild steps into:
    1) SAFE_NON_MUTATING_REBUILD
    2) MANUAL_REVIEW_REQUIRED
    3) BLOCKED_OR_UNSAFE

Default behavior
----------------
DRY RUN ONLY. It writes a safer plan and executes nothing.

Run dry-run:
    python "C:\Users\alike\edge_factory_os_safe_rebuild_runner.py"

Execute only non-mutating safe steps:
    python "C:\Users\alike\edge_factory_os_safe_rebuild_runner.py" --execute_non_mutating

Important
---------
This module never starts paper/live.
It never executes commands containing --apply unless a future explicit manual module handles it.
It never executes PowerShell launchers.
It never touches exchange live trading.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")

MUTATING_COMMAND_MARKERS = [
    " --apply",
    "--apply ",
    "contract_reconciler",
    "position_sizing_contract",
]

UNSAFE_COMMAND_MARKERS = [
    "start_edge_factory_MASTER_UPPER_SYSTEM",
    "paper_launch",
    "start-process",
    "powershell -executionpolicy bypass -file",
    "live_paper_logger",
    "paper_run_gate_MASTER_UPPER_SYSTEM",
]

# These are OS/control-plane modules that are safe to rebuild offline.
SAFE_NON_MUTATING_MODULES = {
    "family_lifecycle_engine",
    "adaptive_capital_governor_v2",
    "execution_realism_checker",
    "kill_switch_controller",
    "native_bps_validator",
    "os_preflight_inspector",
    "autonomous_research_queue",
    "paper_boot_plan",
    "task_reconciler",
    "os_orchestrator_v2",
    "dependency_staleness_checker",
}


@dataclass
class ClassifiedStep:
    order: int
    module_key: str
    original_status: str
    classification: str
    command: str
    reason: str
    safe_offline: bool
    will_execute: bool
    blocked_by: List[str]
    note: Optional[str]
    execution_returncode: Optional[int] = None
    execution_stdout_tail: Optional[str] = None
    execution_stderr_tail: Optional[str] = None


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def discover_staleness_json(workspace: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    d = latest_child_dir(workspace / "edge_factory_os_dependency_staleness", "dependency_staleness_")
    if not d:
        return None
    p = d / "os_dependency_staleness.json"
    return p if p.exists() else None


def command_has_marker(command: str, markers: List[str]) -> bool:
    s = command.lower()
    return any(m.lower() in s for m in markers)


def classify_step(step: Dict[str, Any], execute_non_mutating: bool) -> ClassifiedStep:
    module_key = str(step.get("module_key", "unknown"))
    command = str(step.get("command", ""))
    safe_offline = bool(step.get("safe_offline", True))
    blocked_by = list(step.get("blocked_by") or [])
    note = step.get("note")

    if command_has_marker(command, UNSAFE_COMMAND_MARKERS):
        classification = "BLOCKED_OR_UNSAFE"
        reason = "Command contains paper/live/runtime marker; will not execute."
        will_execute = False
    elif command_has_marker(command, MUTATING_COMMAND_MARKERS):
        classification = "MANUAL_REVIEW_REQUIRED"
        reason = "Command mutates active config or uses --apply; review manually."
        will_execute = False
    elif module_key not in SAFE_NON_MUTATING_MODULES:
        classification = "MANUAL_REVIEW_REQUIRED"
        reason = "Module is not in safe non-mutating allowlist."
        will_execute = False
    elif not safe_offline:
        classification = "BLOCKED_OR_UNSAFE"
        reason = "Step is marked not safe_offline."
        will_execute = False
    else:
        classification = "SAFE_NON_MUTATING_REBUILD"
        reason = "Safe offline control-plane rebuild step."
        will_execute = bool(execute_non_mutating)

    return ClassifiedStep(
        order=int(step.get("order", 999)),
        module_key=module_key,
        original_status=str(step.get("status", "UNKNOWN")),
        classification=classification,
        command=command,
        reason=reason,
        safe_offline=safe_offline,
        will_execute=will_execute,
        blocked_by=blocked_by,
        note=str(note) if note else None,
    )


def run_step(step: ClassifiedStep, timeout_sec: int = 180) -> ClassifiedStep:
    if not step.will_execute:
        return step
    try:
        # Commands are generated as: python "path" args...
        # Use shell=True on Windows to respect quoted paths from generated plan.
        proc = subprocess.run(
            step.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        step.execution_returncode = int(proc.returncode)
        step.execution_stdout_tail = "\n".join((proc.stdout or "").splitlines()[-25:])
        step.execution_stderr_tail = "\n".join((proc.stderr or "").splitlines()[-25:])
        if proc.returncode != 0:
            step.classification = "EXECUTED_FAILED"
            step.reason = f"Command executed but failed with return code {proc.returncode}."
        else:
            step.classification = "EXECUTED_OK"
            step.reason = "Command executed successfully."
    except subprocess.TimeoutExpired as e:
        step.execution_returncode = -999
        step.execution_stdout_tail = "\n".join((e.stdout or "").splitlines()[-25:]) if e.stdout else ""
        step.execution_stderr_tail = "TIMEOUT"
        step.classification = "EXECUTED_TIMEOUT"
        step.reason = f"Command timed out after {timeout_sec} seconds."
    except Exception as e:
        step.execution_returncode = -998
        step.execution_stderr_tail = repr(e)
        step.classification = "EXECUTED_EXCEPTION"
        step.reason = f"Command execution raised exception: {e}"
    return step


def steps_df(steps: List[ClassifiedStep]) -> pd.DataFrame:
    rows = []
    for s in steps:
        d = asdict(s)
        d["blocked_by"] = " | ".join(s.blocked_by)
        rows.append(d)
    return pd.DataFrame(rows)


def write_plan_ps1(path: Path, steps: List[ClassifiedStep]) -> None:
    lines: List[str] = []
    lines.append("# EDGE FACTORY OS SAFE REBUILD PLAN")
    lines.append(f"# Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("# Review manually. This file separates safe rebuilds from manual/mutating steps.")
    lines.append("# It contains no paper/live start command.")
    lines.append("")

    lines.append("# SAFE NON-MUTATING REBUILDS")
    for s in steps:
        if s.classification == "SAFE_NON_MUTATING_REBUILD":
            lines.append(f"# Step {s.order}: {s.module_key}")
            lines.append(s.command)
            lines.append("")

    lines.append("# MANUAL REVIEW REQUIRED / MUTATING")
    for s in steps:
        if s.classification == "MANUAL_REVIEW_REQUIRED":
            lines.append(f"# Step {s.order}: {s.module_key}")
            lines.append(f"# reason: {s.reason}")
            if s.note:
                lines.append(f"# note: {s.note}")
            lines.append(f"# {s.command}")
            lines.append("")

    lines.append("# BLOCKED OR UNSAFE")
    for s in steps:
        if s.classification == "BLOCKED_OR_UNSAFE":
            lines.append(f"# Step {s.order}: {s.module_key}")
            lines.append(f"# reason: {s.reason}")
            lines.append(f"# {s.command}")
            lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, context: Dict[str, Any], steps: List[ClassifiedStep]) -> None:
    counts: Dict[str, int] = {}
    for s in steps:
        counts[s.classification] = counts.get(s.classification, 0) + 1

    lines: List[str] = []
    lines.append("# Edge Factory OS Safe Rebuild Runner Report")
    lines.append("")
    lines.append(f"Generated: `{context['generated_at']}`")
    lines.append(f"Mode: **{context['mode']}**")
    lines.append(f"Staleness source: `{context['staleness_json']}`")
    lines.append("")

    lines.append("## Classification counts")
    lines.append("")
    for k in sorted(counts):
        lines.append(f"- {k}: **{counts[k]}**")
    lines.append("")

    lines.append("## Steps")
    lines.append("")
    lines.append("| Order | Module | Classification | Will execute | Return | Command | Reason |")
    lines.append("|---:|---|---:|---:|---:|---|---|")
    for s in steps:
        lines.append(f"| {s.order} | {s.module_key} | {s.classification} | {s.will_execute} | {s.execution_returncode} | `{s.command}` | {s.reason} |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This runner prevents the OS from blindly executing mutating or runtime commands from a stale rebuild plan. Safe non-mutating rebuilds can be executed with `--execute_non_mutating`; mutating config steps stay manual-review only.")
    lines.append("No paper/live start command is executed by this module.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS safe rebuild runner")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--staleness_json", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--execute_non_mutating", action="store_true")
    p.add_argument("--timeout_sec", type=int, default=180)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    staleness_json = discover_staleness_json(workspace, Path(args.staleness_json) if args.staleness_json else None)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_safe_rebuild_runner"
    out_dir = out_root / f"safe_rebuild_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if staleness_json is None:
        print("EDGE FACTORY OS SAFE REBUILD RUNNER v1")
        print("No staleness JSON found. Run dependency staleness checker first.")
        return 2

    obj = load_json(staleness_json)
    plan = obj.get("rebuild_plan") if isinstance(obj, dict) else []
    if not isinstance(plan, list):
        plan = []

    steps = [classify_step(s, bool(args.execute_non_mutating)) for s in plan if isinstance(s, dict)]
    steps.sort(key=lambda s: s.order)

    if args.execute_non_mutating:
        for i, s in enumerate(steps):
            if s.will_execute:
                steps[i] = run_step(s, timeout_sec=args.timeout_sec)
                # Stop on first failed execution to avoid rebuilding downstream from failed upstream.
                if steps[i].classification in {"EXECUTED_FAILED", "EXECUTED_TIMEOUT", "EXECUTED_EXCEPTION"}:
                    for j in range(i + 1, len(steps)):
                        if steps[j].will_execute:
                            steps[j].will_execute = False
                            steps[j].classification = "SKIPPED_AFTER_FAILURE"
                            steps[j].reason = f"Skipped because {steps[i].module_key} failed."
                    break

    context = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "staleness_json": str(staleness_json),
        "mode": "EXECUTE_NON_MUTATING" if args.execute_non_mutating else "DRY_RUN_ONLY",
        "step_count": len(steps),
    }

    result = {
        "context": context,
        "steps": [asdict(s) for s in steps],
        "hard_rules": [
            "Do not execute --apply automatically.",
            "Do not execute paper/live runtime commands.",
            "Stop executing downstream steps after first failed upstream step.",
            "Mutating config steps require manual review.",
        ],
    }

    write_json(out_dir / "safe_rebuild_result.json", result)
    steps_df(steps).to_csv(out_dir / "safe_rebuild_steps.csv", index=False)
    write_plan_ps1(out_dir / "safe_rebuild_plan.ps1", steps)
    write_report(out_dir / "safe_rebuild_report.md", context, steps)

    print("EDGE FACTORY OS SAFE REBUILD RUNNER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"staleness : {staleness_json}")
    print(f"output_dir: {out_dir}")
    print(f"mode      : {context['mode']}")
    print(f"steps     : {len(steps)}")
    print("")
    print("CLASSIFIED STEPS")
    print("-" * 100)
    for s in steps:
        rc = "" if s.execution_returncode is None else f" rc={s.execution_returncode}"
        print(f"{s.order:02d}. {s.module_key:32s} {s.classification:28s} execute={s.will_execute}{rc}")
        print(f"    reason : {s.reason}")
        print(f"    command: {s.command}")
    print("")
    print(f"Report: {out_dir / 'safe_rebuild_report.md'}")
    print(f"JSON  : {out_dir / 'safe_rebuild_result.json'}")
    print(f"Plan  : {out_dir / 'safe_rebuild_plan.ps1'}")

    failed = [s for s in steps if s.classification in {"EXECUTED_FAILED", "EXECUTED_TIMEOUT", "EXECUTED_EXCEPTION"}]
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
