#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS CONTROL TOWER v1
================================

Purpose
-------
Single-command command center for the self-improving Edge Factory OS.

This module coordinates the two highest-level OS modules:
    1) edge_factory_os_autopilot_loop.py
    2) edge_factory_os_decision_ledger.py

Then it emits one human-readable and machine-readable control-tower decision:
    GREEN_CONTROL_PLANE_CURRENT
    YELLOW_WAITING_FOR_PAPER
    YELLOW_MANUAL_REVIEW_REQUIRED
    RED_REBUILD_REQUIRED
    RED_OS_REPAIR_REQUIRED
    RED_UNSAFE_LIVE_FLAG

It does NOT start paper/live.
It does NOT run start_edge_factory_MASTER_UPPER_SYSTEM.ps1.
It does NOT run loggers.
It does NOT execute --apply.
It does NOT mutate active config.

Run:
    python "C:\Users\alike\edge_factory_os_control_tower.py"

Read-only mode:
    python "C:\Users\alike\edge_factory_os_control_tower.py" --read_only

Outputs:
    <workspace>\edge_factory_os_control_tower\control_tower_YYYYMMDD_HHMMSS\
        os_control_tower_report.md
        os_control_tower_state.json
        os_control_tower_actions.json
        os_control_tower_run_log.csv

Core principle
--------------
This is the top safe OS command. It answers:
    "What is the whole Edge Factory OS state right now, and what should happen next?"

It never answers by launching paper/live automatically.
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

FORBIDDEN_MARKERS = [
    "start_edge_factory_master_upper_system",
    "start-process",
    "powershell -executionpolicy bypass -file",
    " --apply",
    "--apply ",
    "live_paper_logger",
    "paper_launch",
]


@dataclass
class TowerRunLog:
    module_key: str
    command: str
    executed: bool
    returncode: Optional[int]
    ok: bool
    reason: str
    stdout_tail: str
    stderr_tail: str


@dataclass
class TowerAction:
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


def forbidden_marker(command: str) -> Optional[str]:
    s = command.lower()
    for m in FORBIDDEN_MARKERS:
        if m in s:
            return m
    return None


def run_safe_command(module_key: str, command: str, timeout_sec: int, allowed_returncodes: Sequence[int] = (0,)) -> TowerRunLog:
    marker = forbidden_marker(command)
    if marker:
        return TowerRunLog(
            module_key=module_key,
            command=command,
            executed=False,
            returncode=None,
            ok=False,
            reason=f"blocked forbidden marker: {marker}",
            stdout_tail="",
            stderr_tail="",
        )
    try:
        proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout_sec)
        ok = int(proc.returncode) in {int(x) for x in allowed_returncodes}
        return TowerRunLog(
            module_key=module_key,
            command=command,
            executed=True,
            returncode=int(proc.returncode),
            ok=ok,
            reason="allowed return code" if ok else "unexpected return code",
            stdout_tail="\n".join((proc.stdout or "").splitlines()[-30:]),
            stderr_tail="\n".join((proc.stderr or "").splitlines()[-30:]),
        )
    except subprocess.TimeoutExpired as e:
        return TowerRunLog(
            module_key=module_key,
            command=command,
            executed=True,
            returncode=-999,
            ok=False,
            reason=f"timeout after {timeout_sec} seconds",
            stdout_tail="\n".join((e.stdout or "").splitlines()[-30:]) if e.stdout else "",
            stderr_tail="TIMEOUT",
        )
    except Exception as e:
        return TowerRunLog(
            module_key=module_key,
            command=command,
            executed=True,
            returncode=-998,
            ok=False,
            reason=f"exception: {e}",
            stdout_tail="",
            stderr_tail=repr(e),
        )


def discover_latest_autopilot(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_os_autopilot_loop", "autopilot_loop_")
    if not d:
        return None
    p = d / "os_autopilot_loop_state.json"
    return p if p.exists() else None


def discover_latest_ledger_run(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_os_decision_ledger", "ledger_run_")
    if not d:
        return None
    p = d / "os_decision_ledger_diff.json"
    return p if p.exists() else None


def discover_latest_ledger_snapshot(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_os_decision_ledger", "ledger_run_")
    if not d:
        return None
    p = d / "os_decision_ledger_snapshot.json"
    return p if p.exists() else None


def run_control_modules(workspace: Path, script_dir: Path, read_only: bool, timeout_sec: int) -> List[TowerRunLog]:
    logs: List[TowerRunLog] = []
    autopilot_script = script_dir / "edge_factory_os_autopilot_loop.py"
    ledger_script = script_dir / "edge_factory_os_decision_ledger.py"

    autopilot_cmd = f'python "{autopilot_script}"'
    ledger_cmd = f'python "{ledger_script}"'

    if read_only:
        logs.append(TowerRunLog("autopilot_loop", autopilot_cmd, False, None, True, "read_only mode", "", ""))
        logs.append(TowerRunLog("decision_ledger", ledger_cmd, False, None, True, "read_only mode", "", ""))
        return logs

    if not autopilot_script.exists():
        logs.append(TowerRunLog("autopilot_loop", autopilot_cmd, False, None, False, "script missing", "", ""))
        return logs

    auto_log = run_safe_command("autopilot_loop", autopilot_cmd, timeout_sec, allowed_returncodes=(0, 2))
    logs.append(auto_log)
    if not auto_log.ok:
        return logs

    if not ledger_script.exists():
        logs.append(TowerRunLog("decision_ledger", ledger_cmd, False, None, False, "script missing", "", ""))
        return logs

    ledger_log = run_safe_command("decision_ledger", ledger_cmd, timeout_sec, allowed_returncodes=(0, 2))
    logs.append(ledger_log)
    return logs


def build_action(row: Dict[str, Any]) -> TowerAction:
    command = row.get("command")
    starts = bool(row.get("starts_paper_or_live", False))
    status = str(row.get("status", row.get("reconciled_status", "OPEN")))
    if command and forbidden_marker(str(command)):
        command = None
        starts = True
        status = "BLOCKED_UNSAFE_AUTOSTART"
    return TowerAction(
        priority=int(row.get("priority", 999)),
        action_key=str(row.get("action_key", row.get("task_key", "unknown"))),
        status=status,
        category=str(row.get("category", "OS")),
        title=str(row.get("title", "")),
        reason=str(row.get("reason", "")),
        command=str(command) if command else None,
        blocked_by=list(row.get("blocked_by") or []),
        safe_offline=bool(row.get("safe_offline", row.get("safe_to_run_offline", True))),
        starts_paper_or_live=starts,
    )


def derive_tower_decision(workspace: Path, run_logs: List[TowerRunLog]) -> Tuple[Dict[str, Any], List[TowerAction]]:
    failed = [x for x in run_logs if not x.ok]
    autopilot_path = discover_latest_autopilot(workspace)
    ledger_diff_path = discover_latest_ledger_run(workspace)
    ledger_snapshot_path = discover_latest_ledger_snapshot(workspace)

    autopilot = optional_json(autopilot_path)
    ledger_diff = optional_json(ledger_diff_path)
    ledger_snapshot = optional_json(ledger_snapshot_path)

    auto_state = autopilot.get("state") if isinstance(autopilot.get("state"), dict) else {}
    final_actions_raw = autopilot.get("final_actions") if isinstance(autopilot.get("final_actions"), list) else []
    actions = [build_action(x) for x in final_actions_raw if isinstance(x, dict)]

    final_os_mode = str(auto_state.get("final_os_mode", "UNKNOWN"))
    paper_started = bool(auto_state.get("paper_started", False))
    closed_trades = bool(auto_state.get("closed_paper_trades_exist", False))
    live_allowed = bool(auto_state.get("live_allowed", False))
    ledger_class = str(ledger_diff.get("classification", "UNKNOWN"))
    ledger_alerts = list(ledger_diff.get("alerts") or [])

    tower_alerts: List[str] = []
    tower_notes: List[str] = []

    if failed:
        tower_state = "RED_OS_REPAIR_REQUIRED"
        tower_alerts.extend([f"control module failed: {x.module_key} ({x.reason})" for x in failed])
    elif live_allowed:
        tower_state = "RED_UNSAFE_LIVE_FLAG"
        tower_alerts.append("autopilot reported live_allowed=True; hard unsafe state")
    elif ledger_alerts:
        tower_state = "RED_LEDGER_ALERT"
        tower_alerts.extend(ledger_alerts)
    elif final_os_mode == "REBUILD_REQUIRED":
        tower_state = "RED_REBUILD_REQUIRED"
        tower_notes.append("autopilot says semantic dependency rebuild is required")
    elif final_os_mode == "MANUAL_REVIEW_REQUIRED":
        tower_state = "YELLOW_MANUAL_REVIEW_REQUIRED"
        tower_notes.append("manual review required by autopilot")
    elif final_os_mode == "PAPER_RUNNING_READY_FOR_DRIFT_CHECK" or (paper_started and closed_trades):
        tower_state = "YELLOW_PAPER_RUNNING_READY_FOR_DRIFT_CHECK"
        tower_notes.append("paper appears to have closed trades; drift monitor is next gate")
    elif final_os_mode == "PAPER_RUNNING_WAITING_FOR_DRIFT" or paper_started:
        tower_state = "YELLOW_PAPER_RUNNING_WAITING_FOR_SAMPLE"
        tower_notes.append("paper appears started but closed trade sample is not ready")
    elif final_os_mode == "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED":
        tower_state = "GREEN_CONTROL_PLANE_CURRENT"
        tower_notes.append("control plane current; paper ready not started; live blocked")
    else:
        tower_state = "YELLOW_CONTROL_PLANE_REVIEW_REQUIRED"
        tower_notes.append(f"unrecognized or review-needed autopilot mode: {final_os_mode}")

    # If no actions came through, create a state action.
    if not actions:
        actions.append(TowerAction(
            priority=10,
            action_key="control_tower_state_acknowledged",
            status="STATE_ACKNOWLEDGED",
            category="OS_STATE",
            title="Control tower state acknowledged",
            reason="No final actions were available from autopilot; inspect report.",
            command=None,
            blocked_by=[] ,
            safe_offline=True,
            starts_paper_or_live=False,
        ))

    # Add hard live block if missing.
    if not any(a.action_key == "live_remains_blocked" for a in actions):
        actions.append(TowerAction(
            priority=999,
            action_key="live_remains_blocked",
            status="HARD_RULE",
            category="SAFETY",
            title="Keep live trading blocked",
            reason="Control tower v1 cannot approve live. Live requires paper drift validation and manual review.",
            command=None,
            blocked_by=["paper drift validation", "manual live review"],
            safe_offline=True,
            starts_paper_or_live=False,
        ))

    actions = sorted(actions, key=lambda x: x.priority)

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "tower_state": tower_state,
        "autopilot_final_os_mode": final_os_mode,
        "ledger_classification": ledger_class,
        "ledger_alerts": ledger_alerts,
        "tower_alerts": tower_alerts,
        "tower_notes": tower_notes,
        "paper_started": paper_started,
        "closed_paper_trades_exist": closed_trades,
        "live_allowed": False,
        "source_autopilot_path": str(autopilot_path) if autopilot_path else None,
        "source_ledger_diff_path": str(ledger_diff_path) if ledger_diff_path else None,
        "source_ledger_snapshot_path": str(ledger_snapshot_path) if ledger_snapshot_path else None,
        "hard_rules": [
            "Control tower never starts paper/live automatically.",
            "Control tower never executes --apply.",
            "Live remains blocked until paper drift validation and manual review.",
            "OS-level work takes priority over family/capital micro-work.",
        ],
    }
    return state, actions


def run_log_df(logs: List[TowerRunLog]) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in logs])


def action_df(actions: List[TowerAction]) -> pd.DataFrame:
    rows = []
    for a in actions:
        d = asdict(a)
        d["blocked_by"] = " | ".join(a.blocked_by)
        rows.append(d)
    return pd.DataFrame(rows)


def write_report(path: Path, state: Dict[str, Any], logs: List[TowerRunLog], actions: List[TowerAction]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Control Tower Report")
    lines.append("")
    lines.append(f"Generated: `{state['generated_at']}`")
    lines.append(f"Tower state: **{state['tower_state']}**")
    lines.append(f"Autopilot final mode: **{state['autopilot_final_os_mode']}**")
    lines.append(f"Ledger classification: **{state['ledger_classification']}**")
    lines.append(f"Paper started: **{state['paper_started']}**")
    lines.append(f"Closed paper trades: **{state['closed_paper_trades_exist']}**")
    lines.append(f"Live allowed: **{state['live_allowed']}**")
    lines.append("")

    lines.append("## Tower notes")
    lines.append("")
    if state["tower_notes"]:
        for n in state["tower_notes"]:
            lines.append(f"- {n}")
    else:
        lines.append("- No notes.")
    lines.append("")

    if state["tower_alerts"]:
        lines.append("## Tower alerts")
        lines.append("")
        for a in state["tower_alerts"]:
            lines.append(f"- `{a}`")
        lines.append("")

    lines.append("## Run log")
    lines.append("")
    lines.append("| Module | Executed | Return | OK | Reason |")
    lines.append("|---|---:|---:|---:|---|")
    for l in logs:
        lines.append(f"| {l.module_key} | {l.executed} | {l.returncode} | {l.ok} | {l.reason} |")
    lines.append("")

    lines.append("## Final actions")
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
    lines.append("Control Tower is the safe top-level command center. It refreshes autopilot and ledger, compares current state with memory, then emits a single tower state. It does not start paper/live or mutate active configuration.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS Control Tower")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--script_dir", default=str(DEFAULT_SCRIPT_DIR))
    p.add_argument("--out_dir", default=None)
    p.add_argument("--read_only", action="store_true")
    p.add_argument("--timeout_sec", type=int, default=360)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    script_dir = Path(args.script_dir)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_control_tower"
    out_dir = out_root / f"control_tower_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    logs = run_control_modules(workspace, script_dir, bool(args.read_only), int(args.timeout_sec))
    state, actions = derive_tower_decision(workspace, logs)

    result = {
        "state": state,
        "run_logs": [asdict(x) for x in logs],
        "actions": [asdict(x) for x in actions],
    }
    write_json(out_dir / "os_control_tower_state.json", result)
    write_json(out_dir / "os_control_tower_actions.json", [asdict(x) for x in actions])
    run_log_df(logs).to_csv(out_dir / "os_control_tower_run_log.csv", index=False)
    action_df(actions).to_csv(out_dir / "os_control_tower_actions.csv", index=False)
    write_report(out_dir / "os_control_tower_report.md", state, logs, actions)

    print("EDGE FACTORY OS CONTROL TOWER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"script_dir: {script_dir}")
    print(f"output_dir: {out_dir}")
    print(f"mode      : {'READ_ONLY' if args.read_only else 'RUN_CONTROL_MODULES'}")
    print(f"tower_state: {state['tower_state']}")
    print(f"autopilot : {state['autopilot_final_os_mode']}")
    print(f"ledger    : {state['ledger_classification']}")
    print(f"paper     : started={state['paper_started']} closed_trades={state['closed_paper_trades_exist']}")
    print("live_allowed: False")
    print("")
    print("RUN LOG")
    print("-" * 100)
    for l in logs:
        print(f"{l.module_key:20s} executed={str(l.executed):5s} rc={str(l.returncode):>5s} ok={l.ok} reason={l.reason}")
    print("")
    if state["tower_alerts"]:
        print("ALERTS")
        print("-" * 100)
        for a in state["tower_alerts"]:
            print(f"- {a}")
        print("")
    print("FINAL ACTIONS")
    print("-" * 100)
    for a in actions[:12]:
        print(f"P{a.priority:03d} [{a.status}] {a.category} -> {a.title}")
        if a.blocked_by:
            print(f"     blocked_by: {', '.join(a.blocked_by)}")
        if a.command:
            print(f"     command: {a.command}")
        print(f"     reason: {a.reason}")
    print("")
    print(f"Report : {out_dir / 'os_control_tower_report.md'}")
    print(f"State  : {out_dir / 'os_control_tower_state.json'}")
    print(f"Actions: {out_dir / 'os_control_tower_actions.json'}")

    red = str(state["tower_state"]).startswith("RED")
    return 2 if red else 0


if __name__ == "__main__":
    raise SystemExit(main())
