#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS AUTOPILOT LOOP v1
=================================

Purpose
-------
Top-level safe control loop for the self-improving Edge Factory OS.

This is NOT a strategy module.
This is NOT a capital allocator.
This is NOT a paper/live launcher.
It does NOT place orders.
It does NOT start loggers.
It does NOT run start_edge_factory_MASTER_UPPER_SYSTEM.ps1.
It does NOT execute --apply contract changes.

It creates one consolidated OS decision by coordinating the safe OS control-plane modules:

    1) task reconciler
    2) orchestrator v2
    3) semantic dependency/staleness checker v2

Then it emits a final OS mode:

    CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED
    REBUILD_REQUIRED
    MANUAL_REVIEW_REQUIRED
    WAITING_FOR_PAPER
    PAPER_RUNNING_WAITING_FOR_DRIFT
    PAPER_RUNNING_READY_FOR_DRIFT_CHECK
    OS_REPAIR_REQUIRED

Default behavior
----------------
By default it runs only safe offline check modules:
    python edge_factory_os_task_reconciler.py
    python edge_factory_os_orchestrator_v2.py
    python edge_factory_os_dependency_staleness_checker_v2.py

No paper/live process is started.
No active config is modified.

Run:
    python "C:\Users\alike\edge_factory_os_autopilot_loop.py"

Read-only mode, run nothing and only inspect latest artifacts:
    python "C:\Users\alike\edge_factory_os_autopilot_loop.py" --read_only

Outputs:
    <workspace>\edge_factory_os_autopilot_loop\autopilot_loop_YYYYMMDD_HHMMSS\
        os_autopilot_loop_report.md
        os_autopilot_loop_state.json
        os_autopilot_next_actions.json
        os_autopilot_run_log.csv
        os_autopilot_final_actions.csv

Core principle
--------------
The OS can decide what should happen next, but it must not silently start paper/live or
silently mutate active configuration. It can only recommend or run safe offline checks.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")
DEFAULT_PAPER_DIR_NAME = "paper_run_gate_MASTER_UPPER_SYSTEM"

SAFE_CHECK_MODULES = [
    {
        "key": "task_reconciler",
        "script": "edge_factory_os_task_reconciler.py",
        "root": "edge_factory_os_task_reconciler",
        "prefix": "task_reconcile_",
        "file": "os_task_reconciliation.json",
        "critical": True,
    },
    {
        "key": "orchestrator_v2",
        "script": "edge_factory_os_orchestrator_v2.py",
        "root": "edge_factory_os_orchestrator_v2",
        "prefix": "orchestrator_v2_",
        "file": "os_orchestrator_v2_state.json",
        "critical": True,
    },
    {
        "key": "dependency_staleness_v2",
        "script": "edge_factory_os_dependency_staleness_checker_v2.py",
        "root": "edge_factory_os_dependency_staleness_v2",
        "prefix": "dependency_staleness_v2_",
        "file": "os_dependency_staleness_v2.json",
        "critical": True,
        # This checker may return 2 when rebuild is required. That is not a Python failure;
        # it is an OS state. So allowed return codes include 0 and 2.
        "allowed_returncodes": [0, 2],
    },
]

FORBIDDEN_COMMAND_MARKERS = [
    "start_edge_factory_master_upper_system",
    "start-process",
    "powershell -executionpolicy bypass -file",
    " --apply",
    "--apply ",
    "live_paper_logger",
    "paper_launch",
]


@dataclass
class RunLog:
    key: str
    command: str
    executed: bool
    returncode: Optional[int]
    ok: bool
    stdout_tail: str
    stderr_tail: str
    reason: str


@dataclass
class FinalAction:
    priority: int
    action_key: str
    status: str
    category: str
    title: str
    reason: str
    command: Optional[str]
    blocked_by: List[str]
    safe_offline: bool
    starts_paper_or_live: bool


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


def command_is_forbidden(command: str) -> Optional[str]:
    s = command.lower()
    for marker in FORBIDDEN_COMMAND_MARKERS:
        if marker in s:
            return marker
    return None


def run_command(command: str, key: str, allowed_returncodes: Sequence[int], timeout_sec: int) -> RunLog:
    marker = command_is_forbidden(command)
    if marker:
        return RunLog(
            key=key,
            command=command,
            executed=False,
            returncode=None,
            ok=False,
            stdout_tail="",
            stderr_tail="",
            reason=f"blocked by forbidden command marker: {marker}",
        )
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        out_tail = "\n".join((proc.stdout or "").splitlines()[-25:])
        err_tail = "\n".join((proc.stderr or "").splitlines()[-25:])
        ok = int(proc.returncode) in set(int(x) for x in allowed_returncodes)
        return RunLog(
            key=key,
            command=command,
            executed=True,
            returncode=int(proc.returncode),
            ok=ok,
            stdout_tail=out_tail,
            stderr_tail=err_tail,
            reason="allowed return code" if ok else "unexpected return code",
        )
    except subprocess.TimeoutExpired as e:
        return RunLog(
            key=key,
            command=command,
            executed=True,
            returncode=-999,
            ok=False,
            stdout_tail="\n".join((e.stdout or "").splitlines()[-25:]) if e.stdout else "",
            stderr_tail="TIMEOUT",
            reason=f"timed out after {timeout_sec} seconds",
        )
    except Exception as e:
        return RunLog(
            key=key,
            command=command,
            executed=True,
            returncode=-998,
            ok=False,
            stdout_tail="",
            stderr_tail=repr(e),
            reason=f"execution exception: {e}",
        )


def run_safe_checks(script_dir: Path, timeout_sec: int, read_only: bool) -> List[RunLog]:
    logs: List[RunLog] = []
    for mod in SAFE_CHECK_MODULES:
        key = str(mod["key"])
        script = script_dir / str(mod["script"])
        command = f'python "{script}"'
        allowed = mod.get("allowed_returncodes", [0])
        if read_only:
            logs.append(RunLog(
                key=key,
                command=command,
                executed=False,
                returncode=None,
                ok=True,
                stdout_tail="",
                stderr_tail="",
                reason="read_only mode",
            ))
            continue
        if not script.exists():
            logs.append(RunLog(
                key=key,
                command=command,
                executed=False,
                returncode=None,
                ok=False,
                stdout_tail="",
                stderr_tail="",
                reason="script missing",
            ))
            continue
        log = run_command(command, key, allowed, timeout_sec)
        logs.append(log)
        # Stop after critical failed safe check; downstream state may be invalid.
        if bool(mod.get("critical", True)) and not log.ok:
            break
    return logs


def artifact_path(workspace: Path, mod: Dict[str, Any]) -> Optional[Path]:
    d = latest_child_dir(workspace / str(mod["root"]), str(mod["prefix"]))
    if not d:
        return None
    p = d / str(mod["file"])
    return p if p.exists() else None


def load_latest_artifacts(workspace: Path) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for mod in SAFE_CHECK_MODULES:
        p = artifact_path(workspace, mod)
        out[str(mod["key"])] = optional_json(p)
        out[str(mod["key"]) + "__path"] = {"path": str(p) if p else None}
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
    for pat in ["*closed*trade*.csv", "*paper*trade*.csv", "trades.csv"]:
        for f in p.rglob(pat):
            try:
                if f.exists() and f.stat().st_size > 200:
                    return True
            except Exception:
                pass
    return False


def get_nested(obj: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def derive_final_mode(workspace: Path, run_logs: List[RunLog], artifacts: Dict[str, Dict[str, Any]]) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    failed_logs = [x for x in run_logs if not x.ok]
    if failed_logs:
        return "OS_REPAIR_REQUIRED", [f"safe check failed: {x.key} ({x.reason})" for x in failed_logs]

    stale = artifacts.get("dependency_staleness_v2", {})
    stale_context = stale.get("context") if isinstance(stale.get("context"), dict) else {}
    stale_overall = str(stale_context.get("overall_state", "UNKNOWN"))

    if stale_overall == "MANUAL_REVIEW_REQUIRED":
        return "MANUAL_REVIEW_REQUIRED", ["semantic staleness checker requires manual review"]
    if stale_overall == "REBUILD_REQUIRED":
        return "REBUILD_REQUIRED", ["semantic dependency chain has stale/missing required artifacts"]

    orch = artifacts.get("orchestrator_v2", {})
    orch_state = orch.get("state") if isinstance(orch.get("state"), dict) else {}
    orch_mode = str(orch_state.get("os_mode", "UNKNOWN"))
    live_allowed = bool(orch_state.get("live_allowed", False))
    live_gate = str(orch_state.get("live_gate", "UNKNOWN"))
    ps = paper_started(workspace)
    closed = closed_paper_trades_exist(workspace)

    if live_allowed:
        return "OS_REPAIR_REQUIRED", ["orchestrator reports live_allowed=True; autopilot v1 treats this as unsafe"]

    if ps and closed:
        return "PAPER_RUNNING_READY_FOR_DRIFT_CHECK", ["paper folder and closed trade files detected"]
    if ps and not closed:
        return "PAPER_RUNNING_WAITING_FOR_DRIFT", ["paper folder exists but closed trade sample not detected"]

    if orch_mode == "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED":
        return "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED", ["control plane current, semantic dependency chain current, paper not started, live blocked"]

    if "PAPER_READY" in orch_mode or "PAPER_READY" in str(orch_state.get("paper_decision", "")):
        return "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED", ["paper-ready state inferred from orchestrator"]

    if "LIVE_BLOCKED" in live_gate:
        reasons.append("live gate is blocked as expected")

    return "CONTROL_PLANE_REVIEW_REQUIRED", [f"unrecognized orchestrator mode: {orch_mode}"] + reasons


def actions_from_artifacts(workspace: Path, final_mode: str, artifacts: Dict[str, Dict[str, Any]]) -> List[FinalAction]:
    actions: List[FinalAction] = []
    orch = artifacts.get("orchestrator_v2", {})
    orch_actions = orch.get("next_actions") if isinstance(orch.get("next_actions"), list) else []
    task_rec = artifacts.get("task_reconciler", {})
    rec_actions = task_rec.get("next_os_actions") if isinstance(task_rec.get("next_os_actions"), list) else []
    stale = artifacts.get("dependency_staleness_v2", {})
    rebuild = stale.get("rebuild_plan") if isinstance(stale.get("rebuild_plan"), list) else []

    if final_mode == "REBUILD_REQUIRED":
        for i, r in enumerate(rebuild[:10], start=1):
            if not isinstance(r, dict):
                continue
            actions.append(FinalAction(
                priority=i,
                action_key=f"rebuild_{r.get('module_key', 'unknown')}",
                status=str(r.get("status", "REBUILD")),
                category="REBUILD_PLAN",
                title=f"Rebuild stale module: {r.get('module_key', 'unknown')}",
                reason=str(r.get("reason", "stale dependency")),
                command=str(r.get("command")) if r.get("command") else None,
                blocked_by=list(r.get("blocked_by") or []),
                safe_offline=bool(r.get("safe_offline", True)),
                starts_paper_or_live=False,
            ))
        return actions

    # Prefer reconciled next actions because they know DONE/WAITING/FUTURE.
    source_actions = rec_actions if rec_actions else orch_actions
    for row in source_actions:
        if not isinstance(row, dict):
            continue
        key = str(row.get("task_key", row.get("action_key", "unknown")))
        status = str(row.get("reconciled_status", row.get("status", "OPEN")))
        command = row.get("command")
        starts = bool(row.get("starts_paper_or_live", False))
        # Never pass through unsafe/paper/live commands.
        if command and command_is_forbidden(str(command)):
            command = None
            starts = True
            status = "BLOCKED_UNSAFE_AUTOSTART"
        actions.append(FinalAction(
            priority=int(row.get("priority", 999)),
            action_key=key,
            status=status,
            category=str(row.get("category", "OS")),
            title=str(row.get("title", "")),
            reason=str(row.get("reason", "")),
            command=str(command) if command else None,
            blocked_by=list(row.get("blocked_by") or []),
            safe_offline=bool(row.get("safe_to_run_offline", row.get("safe_offline", True))),
            starts_paper_or_live=starts,
        ))

    if not actions:
        actions.append(FinalAction(
            priority=10,
            action_key="control_plane_current_no_offline_action",
            status="STATE_ACKNOWLEDGED",
            category="OS_STATE",
            title="Control plane is current; no safe offline rebuild required",
            reason="Semantic dependency chain is current and paper/live are not auto-started.",
            command=None,
            blocked_by=["supervised paper decision or new OS architecture module"],
            safe_offline=True,
            starts_paper_or_live=False,
        ))

    # Always append live hard block unless already present.
    if not any(a.action_key == "live_remains_blocked" for a in actions):
        actions.append(FinalAction(
            priority=999,
            action_key="live_remains_blocked",
            status="HARD_RULE",
            category="SAFETY",
            title="Keep live trading blocked",
            reason="Autopilot loop v1 cannot approve live. Live requires paper drift validation and manual review.",
            command=None,
            blocked_by=["paper drift validation", "manual live review"],
            safe_offline=True,
            starts_paper_or_live=False,
        ))

    # De-dupe.
    seen = set()
    out: List[FinalAction] = []
    for a in sorted(actions, key=lambda x: x.priority):
        if a.action_key in seen:
            continue
        seen.add(a.action_key)
        out.append(a)
    return out


def run_log_df(logs: List[RunLog]) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in logs])


def action_df(actions: List[FinalAction]) -> pd.DataFrame:
    rows = []
    for a in actions:
        d = asdict(a)
        d["blocked_by"] = " | ".join(a.blocked_by)
        rows.append(d)
    return pd.DataFrame(rows)


def write_report(path: Path, state: Dict[str, Any], run_logs: List[RunLog], actions: List[FinalAction]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Autopilot Loop Report")
    lines.append("")
    lines.append(f"Generated: `{state['generated_at']}`")
    lines.append(f"Final OS mode: **{state['final_os_mode']}**")
    lines.append(f"Paper started: **{state['paper_started']}**")
    lines.append(f"Closed paper trades detected: **{state['closed_paper_trades_exist']}**")
    lines.append(f"Live allowed: **{state['live_allowed']}**")
    lines.append(f"Read-only: **{state['read_only']}**")
    lines.append("")

    lines.append("## Final reasoning")
    lines.append("")
    for r in state["final_reasons"]:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Safe check run log")
    lines.append("")
    lines.append("| Module | Executed | Return | OK | Reason |")
    lines.append("|---|---:|---:|---:|---|")
    for l in run_logs:
        lines.append(f"| {l.key} | {l.executed} | {l.returncode} | {l.ok} | {l.reason} |")
    lines.append("")

    lines.append("## Final next actions")
    lines.append("")
    lines.append("| Priority | Status | Category | Action | Command | Blocked by |")
    lines.append("|---:|---:|---|---|---|---|")
    for a in actions:
        cmd = f"`{a.command}`" if a.command else ""
        blocked = ", ".join(a.blocked_by)
        lines.append(f"| {a.priority} | {a.status} | {a.category} | {a.title} | {cmd} | {blocked} |")
    lines.append("")

    lines.append("## Hard rules")
    lines.append("")
    for r in state["hard_rules"]:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("The autopilot loop is the first unified OS loop: it refreshes safe control-plane checks, reads semantic dependency state, reconciles tasks, and emits one final OS mode. It still cannot start paper/live or mutate active configuration.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS Autopilot Loop")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--script_dir", default=str(DEFAULT_SCRIPT_DIR))
    p.add_argument("--out_dir", default=None)
    p.add_argument("--read_only", action="store_true", help="do not run safe check modules; only inspect latest artifacts")
    p.add_argument("--timeout_sec", type=int, default=240)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    script_dir = Path(args.script_dir)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_autopilot_loop"
    out_dir = out_root / f"autopilot_loop_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    run_logs = run_safe_checks(script_dir, timeout_sec=int(args.timeout_sec), read_only=bool(args.read_only))
    artifacts = load_latest_artifacts(workspace)
    final_mode, final_reasons = derive_final_mode(workspace, run_logs, artifacts)
    actions = actions_from_artifacts(workspace, final_mode, artifacts)

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "script_dir": str(script_dir),
        "output_dir": str(out_dir),
        "read_only": bool(args.read_only),
        "final_os_mode": final_mode,
        "final_reasons": final_reasons,
        "paper_started": paper_started(workspace),
        "closed_paper_trades_exist": closed_paper_trades_exist(workspace),
        "live_allowed": False,
        "artifact_paths": {k: v.get("path") for k, v in artifacts.items() if k.endswith("__path")},
        "hard_rules": [
            "Do not start paper/live from autopilot loop.",
            "Do not execute --apply or active config mutation from autopilot loop.",
            "Do not repeat DONE tasks; consume reconciled task state.",
            "Use semantic dependency state, not blind artifact timestamps.",
            "Live remains blocked until paper drift validation and manual review.",
        ],
    }

    result = {
        "state": state,
        "run_logs": [asdict(x) for x in run_logs],
        "final_actions": [asdict(x) for x in actions],
        "latest_artifact_summaries": artifacts,
    }

    write_json(out_dir / "os_autopilot_loop_state.json", result)
    write_json(out_dir / "os_autopilot_next_actions.json", [asdict(x) for x in actions])
    run_log_df(run_logs).to_csv(out_dir / "os_autopilot_run_log.csv", index=False)
    action_df(actions).to_csv(out_dir / "os_autopilot_final_actions.csv", index=False)
    write_report(out_dir / "os_autopilot_loop_report.md", state, run_logs, actions)

    print("EDGE FACTORY OS AUTOPILOT LOOP v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"script_dir: {script_dir}")
    print(f"output_dir: {out_dir}")
    print(f"mode      : {'READ_ONLY' if args.read_only else 'SAFE_CHECKS_EXECUTED'}")
    print(f"final_os_mode: {final_mode}")
    print(f"paper_started: {state['paper_started']} | closed_trades={state['closed_paper_trades_exist']}")
    print("live_allowed : False")
    print("")
    print("SAFE CHECKS")
    print("-" * 100)
    for l in run_logs:
        print(f"{l.key:28s} executed={str(l.executed):5s} rc={str(l.returncode):>5s} ok={l.ok} reason={l.reason}")
    print("")
    print("FINAL REASONS")
    print("-" * 100)
    for r in final_reasons:
        print(f"- {r}")
    print("")
    print("FINAL NEXT ACTIONS")
    print("-" * 100)
    for a in actions[:12]:
        print(f"P{a.priority:03d} [{a.status}] {a.category} -> {a.title}")
        if a.blocked_by:
            print(f"     blocked_by: {', '.join(a.blocked_by)}")
        if a.command:
            print(f"     command: {a.command}")
        print(f"     reason: {a.reason}")
    print("")
    print(f"Report : {out_dir / 'os_autopilot_loop_report.md'}")
    print(f"State  : {out_dir / 'os_autopilot_loop_state.json'}")
    print(f"Actions: {out_dir / 'os_autopilot_next_actions.json'}")

    return 0 if final_mode not in {"OS_REPAIR_REQUIRED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
