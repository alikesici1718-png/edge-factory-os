#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS CONTROL TOWER v2
================================

Purpose
-------
Integrated top-level command center for the self-improving Edge Factory OS.

v1 Control Tower coordinated:
    - autopilot loop
    - decision ledger

v2 adds the new state-machine / approval-gate layers:
    - transition controller
    - manual approval packet
    - paper start gate
    - latest manual approval recorder state, read-only

It emits one final OS command-center decision:
    GREEN_CONTROL_PLANE_CURRENT__PAPER_BLOCKED_NO_APPROVAL
    GREEN_CONTROL_PLANE_CURRENT__PAPER_REFERENCE_ALLOWED_MANUAL_ONLY
    YELLOW_PAPER_ALREADY_STARTED_MONITORING_REQUIRED
    YELLOW_MANUAL_REVIEW_REQUIRED
    RED_REBUILD_REQUIRED
    RED_OS_REPAIR_REQUIRED
    RED_UNSAFE_LIVE_FLAG

It does NOT start paper/live.
It does NOT execute launchers.
It does NOT run --apply.
It does NOT mutate active config.
It does NOT record manual approval by itself.

Run:
    python "C:\Users\alike\edge_factory_os_control_tower_v2.py"

Read-only:
    python "C:\Users\alike\edge_factory_os_control_tower_v2.py" --read_only

Outputs:
    <workspace>\edge_factory_os_control_tower_v2\control_tower_v2_YYYYMMDD_HHMMSS\
        os_control_tower_v2_report.md
        os_control_tower_v2_state.json
        os_control_tower_v2_actions.json
        os_control_tower_v2_run_log.csv
        os_control_tower_v2_evidence.csv

Core principle
--------------
This is the safe top-level command center. It can say what the OS state is and what
manual gate is next. It never starts paper/live automatically.
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

SAFE_RUN_MODULES = [
    ("autopilot_loop", "edge_factory_os_autopilot_loop.py", (0, 2)),
    ("decision_ledger", "edge_factory_os_decision_ledger.py", (0, 2)),
    ("transition_controller", "edge_factory_os_transition_controller.py", (0, 2)),
    ("manual_approval_packet", "edge_factory_os_manual_approval_packet.py", (0, 2)),
    ("paper_start_gate", "edge_factory_os_paper_start_gate.py", (0, 2)),
]

ARTIFACTS = {
    "autopilot_loop": ("edge_factory_os_autopilot_loop", "autopilot_loop_", "os_autopilot_loop_state.json"),
    "decision_ledger_diff": ("edge_factory_os_decision_ledger", "ledger_run_", "os_decision_ledger_diff.json"),
    "decision_ledger_snapshot": ("edge_factory_os_decision_ledger", "ledger_run_", "os_decision_ledger_snapshot.json"),
    "transition_controller": ("edge_factory_os_transition_controller", "transition_", "os_transition_state.json"),
    "manual_approval_packet": ("edge_factory_os_manual_approval_packet", "approval_packet_", "os_manual_approval_packet.json"),
    "manual_approval_record": ("edge_factory_os_manual_approval_recorder", "manual_approval_", "os_manual_approval_record.json"),
    "paper_start_gate": ("edge_factory_os_paper_start_gate", "paper_start_gate_", "os_paper_start_gate_decision.json"),
    "control_tower_v1": ("edge_factory_os_control_tower", "control_tower_", "os_control_tower_state.json"),
}

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
class RunLog:
    module_key: str
    command: str
    executed: bool
    returncode: Optional[int]
    ok: bool
    reason: str
    stdout_tail: str
    stderr_tail: str


@dataclass
class Evidence:
    key: str
    path: Optional[str]
    exists: bool
    modified_at: Optional[str]
    status: str
    message: str


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
        return obj if isinstance(obj, dict) else {}
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


def run_safe_command(module_key: str, command: str, timeout_sec: int, allowed_returncodes: Sequence[int]) -> RunLog:
    marker = forbidden_marker(command)
    if marker:
        return RunLog(module_key, command, False, None, False, f"blocked forbidden marker: {marker}", "", "")
    try:
        proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout_sec)
        ok = int(proc.returncode) in {int(x) for x in allowed_returncodes}
        return RunLog(
            module_key=module_key,
            command=command,
            executed=True,
            returncode=int(proc.returncode),
            ok=ok,
            reason="allowed return code" if ok else "unexpected return code",
            stdout_tail="\n".join((proc.stdout or "").splitlines()[-25:]),
            stderr_tail="\n".join((proc.stderr or "").splitlines()[-25:]),
        )
    except subprocess.TimeoutExpired as e:
        return RunLog(module_key, command, True, -999, False, f"timeout after {timeout_sec} seconds", "\n".join((e.stdout or "").splitlines()[-25:]) if e.stdout else "", "TIMEOUT")
    except Exception as e:
        return RunLog(module_key, command, True, -998, False, f"exception: {e}", "", repr(e))


def run_modules(script_dir: Path, read_only: bool, timeout_sec: int) -> List[RunLog]:
    logs: List[RunLog] = []
    for key, script_name, allowed in SAFE_RUN_MODULES:
        script = script_dir / script_name
        command = f'python "{script}"'
        if read_only:
            logs.append(RunLog(key, command, False, None, True, "read_only mode", "", ""))
            continue
        if not script.exists():
            logs.append(RunLog(key, command, False, None, False, "script missing", "", ""))
            break
        log = run_safe_command(key, command, timeout_sec, allowed)
        logs.append(log)
        if not log.ok:
            break
    return logs


def artifact_path(workspace: Path, key: str) -> Optional[Path]:
    root_name, prefix, filename = ARTIFACTS[key]
    d = latest_child_dir(workspace / root_name, prefix)
    if not d:
        return None
    p = d / filename
    return p if p.exists() else None


def collect_evidence(workspace: Path) -> Dict[str, Evidence]:
    out: Dict[str, Evidence] = {}
    for key in ARTIFACTS:
        p = artifact_path(workspace, key)
        exists = bool(p and p.exists())
        out[key] = Evidence(
            key=key,
            path=str(p) if p else None,
            exists=exists,
            modified_at=iso_mtime(p) if exists and p else None,
            status="PASS" if exists else "MISSING",
            message="artifact found" if exists else "artifact missing",
        )
    return out


def data_from_evidence(evidence: Dict[str, Evidence]) -> Dict[str, Dict[str, Any]]:
    return {k: optional_json(Path(v.path) if v.path else None) for k, v in evidence.items()}


def nested(obj: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


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


def derive_state(workspace: Path, logs: List[RunLog], data: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, Any], List[TowerAction]]:
    failed = [x for x in logs if not x.ok]

    autopilot_state = data.get("autopilot_loop", {}).get("state") if isinstance(data.get("autopilot_loop", {}).get("state"), dict) else {}
    autopilot_mode = str(autopilot_state.get("final_os_mode", "UNKNOWN"))
    autopilot_actions = data.get("autopilot_loop", {}).get("final_actions") if isinstance(data.get("autopilot_loop", {}).get("final_actions"), list) else []

    ledger_diff = data.get("decision_ledger_diff", {})
    ledger_class = str(ledger_diff.get("classification", "UNKNOWN"))
    ledger_alerts = list(ledger_diff.get("alerts") or [])

    transition_decision = data.get("transition_controller", {}).get("decision") if isinstance(data.get("transition_controller", {}).get("decision"), dict) else {}
    transition_status = str(transition_decision.get("decision", "UNKNOWN"))
    transition_current = str(transition_decision.get("current_canonical_state", "UNKNOWN"))
    transition_next = str(transition_decision.get("recommended_next_state", "UNKNOWN"))

    packet_status = str(data.get("manual_approval_packet", {}).get("approval_status", "UNKNOWN"))
    approval_status = str(data.get("manual_approval_record", {}).get("approval_status", "UNKNOWN"))
    approval_allowed = bool(data.get("manual_approval_record", {}).get("paper_start_allowed_by_approval_record", False))

    gate_decision = data.get("paper_start_gate", {}).get("decision") if isinstance(data.get("paper_start_gate", {}).get("decision"), dict) else {}
    gate_status = str(gate_decision.get("gate_status", "UNKNOWN"))
    gate_allowed = bool(gate_decision.get("paper_start_reference_allowed", False))
    paper_started = bool(gate_decision.get("paper_started", autopilot_state.get("paper_started", False)))
    live_allowed = bool(gate_decision.get("live_allowed", False)) or bool(autopilot_state.get("live_allowed", False))

    alerts: List[str] = []
    notes: List[str] = []

    if failed:
        tower_state = "RED_OS_REPAIR_REQUIRED"
        alerts.extend([f"control module failed: {x.module_key} ({x.reason})" for x in failed])
    elif live_allowed:
        tower_state = "RED_UNSAFE_LIVE_FLAG"
        alerts.append("live_allowed true in upstream artifact")
    elif ledger_alerts:
        tower_state = "RED_LEDGER_ALERT"
        alerts.extend(str(x) for x in ledger_alerts)
    elif gate_status == "PAPER_START_REFERENCE_ALLOWED_MANUAL_ONLY":
        tower_state = "GREEN_CONTROL_PLANE_CURRENT__PAPER_REFERENCE_ALLOWED_MANUAL_ONLY"
        notes.append("manual approval exists; paper reference is allowed but not executed")
    elif gate_status == "PAPER_START_BLOCKED_NO_MANUAL_APPROVAL":
        tower_state = "GREEN_CONTROL_PLANE_CURRENT__PAPER_BLOCKED_NO_APPROVAL"
        notes.append("control plane current, but paper start is blocked until manual approval is granted")
    elif gate_status == "PAPER_ALREADY_STARTED_MONITORING_REQUIRED":
        tower_state = "YELLOW_PAPER_ALREADY_STARTED_MONITORING_REQUIRED"
        notes.append("paper appears started; switch to monitoring and drift workflow")
    elif autopilot_mode == "REBUILD_REQUIRED":
        tower_state = "RED_REBUILD_REQUIRED"
        notes.append("autopilot says rebuild is required")
    elif autopilot_mode == "MANUAL_REVIEW_REQUIRED":
        tower_state = "YELLOW_MANUAL_REVIEW_REQUIRED"
        notes.append("autopilot requires manual review")
    elif autopilot_mode == "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED":
        tower_state = "GREEN_CONTROL_PLANE_CURRENT__PAPER_GATE_REVIEW"
        notes.append("control plane current; paper gate requires review")
    else:
        tower_state = "YELLOW_CONTROL_PLANE_REVIEW_REQUIRED"
        notes.append(f"unrecognized combined state: autopilot={autopilot_mode}, gate={gate_status}")

    actions = [build_action(x) for x in autopilot_actions if isinstance(x, dict)]

    # Add paper gate action as the first meaningful gate action.
    if gate_status == "PAPER_START_BLOCKED_NO_MANUAL_APPROVAL":
        actions.insert(0, TowerAction(
            priority=5,
            action_key="record_manual_approval_or_keep_waiting",
            status="BLOCKED_BY_MANUAL_APPROVAL",
            category="PAPER_GATE",
            title="Paper start is blocked until manual approval is recorded",
            reason="Manual approval record does not grant paper-only/native-logging/no-live confirmations.",
            command=None,
            blocked_by=["manual approval flags"],
            safe_offline=True,
            starts_paper_or_live=False,
        ))
    elif gate_status == "PAPER_START_REFERENCE_ALLOWED_MANUAL_ONLY":
        actions.insert(0, TowerAction(
            priority=5,
            action_key="manual_paper_reference_allowed_not_executed",
            status="MANUAL_REFERENCE_ONLY",
            category="PAPER_GATE",
            title="Human may manually start supervised paper using reference command",
            reason="All gate checks passed. This module did not execute the command.",
            command=None,
            blocked_by=["human manual action"],
            safe_offline=True,
            starts_paper_or_live=False,
        ))

    if not any(a.action_key == "live_remains_blocked" for a in actions):
        actions.append(TowerAction(
            priority=999,
            action_key="live_remains_blocked",
            status="HARD_RULE",
            category="SAFETY",
            title="Keep live trading blocked",
            reason="Control Tower v2 cannot approve live. Live requires paper drift validation and manual live review.",
            command=None,
            blocked_by=["paper drift validation", "manual live review"],
            safe_offline=True,
            starts_paper_or_live=False,
        ))

    # Dedupe actions by key, preserving priority sort.
    seen = set()
    clean_actions: List[TowerAction] = []
    for a in sorted(actions, key=lambda x: x.priority):
        if a.action_key in seen:
            continue
        seen.add(a.action_key)
        clean_actions.append(a)

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "tower_state": tower_state,
        "autopilot_final_os_mode": autopilot_mode,
        "ledger_classification": ledger_class,
        "transition_decision": transition_status,
        "transition_current": transition_current,
        "transition_next": transition_next,
        "approval_packet_status": packet_status,
        "manual_approval_status": approval_status,
        "manual_approval_allows_paper_reference": approval_allowed,
        "paper_gate_status": gate_status,
        "paper_gate_reference_allowed": gate_allowed,
        "paper_started": paper_started,
        "live_allowed": False,
        "tower_alerts": alerts,
        "tower_notes": notes,
        "hard_rules": [
            "Control Tower v2 never starts paper/live automatically.",
            "Control Tower v2 never executes --apply.",
            "Control Tower v2 does not record manual approval by itself.",
            "Live remains blocked until paper drift validation and manual review.",
            "Paper start requires explicit manual approval record and remains reference-only.",
        ],
    }
    return state, clean_actions


def evidence_df(evidence: Dict[str, Evidence]) -> pd.DataFrame:
    return pd.DataFrame([asdict(v) for v in evidence.values()])


def run_log_df(logs: List[RunLog]) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in logs])


def action_df(actions: List[TowerAction]) -> pd.DataFrame:
    rows = []
    for a in actions:
        d = asdict(a)
        d["blocked_by"] = " | ".join(a.blocked_by)
        rows.append(d)
    return pd.DataFrame(rows)


def write_report(path: Path, state: Dict[str, Any], logs: List[RunLog], actions: List[TowerAction], evidence: Dict[str, Evidence]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Control Tower v2 Report")
    lines.append("")
    lines.append(f"Generated: `{state['generated_at']}`")
    lines.append(f"Tower state: **{state['tower_state']}**")
    lines.append(f"Autopilot: **{state['autopilot_final_os_mode']}**")
    lines.append(f"Transition: **{state['transition_decision']}**")
    lines.append(f"Approval packet: **{state['approval_packet_status']}**")
    lines.append(f"Manual approval: **{state['manual_approval_status']}**")
    lines.append(f"Paper gate: **{state['paper_gate_status']}**")
    lines.append(f"Paper reference allowed: **{state['paper_gate_reference_allowed']}**")
    lines.append(f"Paper started: **{state['paper_started']}**")
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
        lines.append("## Alerts")
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
        lines.append(f"| {a.priority} | {a.status} | {a.category} | {a.title} | {cmd} | {', '.join(a.blocked_by)} |")
    lines.append("")

    lines.append("## Evidence")
    lines.append("")
    lines.append("| Key | Status | Path | Modified |")
    lines.append("|---|---:|---|---:|")
    for ev in evidence.values():
        lines.append(f"| {ev.key} | {ev.status} | `{ev.path}` | {ev.modified_at} |")
    lines.append("")

    lines.append("## Hard rules")
    lines.append("")
    for r in state["hard_rules"]:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("Control Tower v2 is the integrated safe command center. It sees the control plane, state transition, approval packet, approval record, and final paper-start gate. It does not start paper/live or mutate active configuration.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS Control Tower v2")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--script_dir", default=str(DEFAULT_SCRIPT_DIR))
    p.add_argument("--out_dir", default=None)
    p.add_argument("--read_only", action="store_true")
    p.add_argument("--timeout_sec", type=int, default=420)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    script_dir = Path(args.script_dir)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_control_tower_v2"
    out_dir = out_root / f"control_tower_v2_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    logs = run_modules(script_dir, bool(args.read_only), int(args.timeout_sec))
    evidence = collect_evidence(workspace)
    data = data_from_evidence(evidence)
    state, actions = derive_state(workspace, logs, data)

    result = {
        "state": state,
        "run_logs": [asdict(x) for x in logs],
        "actions": [asdict(x) for x in actions],
        "evidence": {k: asdict(v) for k, v in evidence.items()},
    }
    write_json(out_dir / "os_control_tower_v2_state.json", result)
    write_json(out_dir / "os_control_tower_v2_actions.json", [asdict(x) for x in actions])
    run_log_df(logs).to_csv(out_dir / "os_control_tower_v2_run_log.csv", index=False)
    action_df(actions).to_csv(out_dir / "os_control_tower_v2_actions.csv", index=False)
    evidence_df(evidence).to_csv(out_dir / "os_control_tower_v2_evidence.csv", index=False)
    write_report(out_dir / "os_control_tower_v2_report.md", state, logs, actions, evidence)

    print("EDGE FACTORY OS CONTROL TOWER v2")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"script_dir: {script_dir}")
    print(f"output_dir: {out_dir}")
    print(f"mode      : {'READ_ONLY' if args.read_only else 'RUN_SAFE_CONTROL_MODULES'}")
    print(f"tower_state: {state['tower_state']}")
    print(f"autopilot : {state['autopilot_final_os_mode']}")
    print(f"transition: {state['transition_decision']} -> {state['transition_next']}")
    print(f"approval_packet: {state['approval_packet_status']}")
    print(f"manual_approval: {state['manual_approval_status']} allows_reference={state['manual_approval_allows_paper_reference']}")
    print(f"paper_gate: {state['paper_gate_status']} reference_allowed={state['paper_gate_reference_allowed']}")
    print(f"paper_started: {state['paper_started']}")
    print("live_allowed: False")
    print("")
    print("RUN LOG")
    print("-" * 100)
    for l in logs:
        print(f"{l.module_key:24s} executed={str(l.executed):5s} rc={str(l.returncode):>5s} ok={l.ok} reason={l.reason}")
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
    print(f"Report : {out_dir / 'os_control_tower_v2_report.md'}")
    print(f"State  : {out_dir / 'os_control_tower_v2_state.json'}")
    print(f"Actions: {out_dir / 'os_control_tower_v2_actions.json'}")

    return 2 if str(state["tower_state"]).startswith("RED") else 0



if __name__ == "__main__":
    raise SystemExit(main())
