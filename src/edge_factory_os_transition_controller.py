#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS TRANSITION CONTROLLER v1
========================================

Purpose
-------
Finite-state transition policy controller for the self-improving Edge Factory OS.

The Control Tower can tell us the current tower_state:
    GREEN_CONTROL_PLANE_CURRENT
    YELLOW_WAITING_FOR_PAPER
    YELLOW_MANUAL_REVIEW_REQUIRED
    RED_REBUILD_REQUIRED
    RED_OS_REPAIR_REQUIRED
    RED_UNSAFE_LIVE_FLAG

But a real OS also needs a transition policy:
    - Which next states are allowed?
    - Which transitions are forbidden?
    - Which transitions require manual approval?
    - What evidence is required before moving from paper-ready to paper-running?
    - What evidence is required before live can ever be considered?

This module reads the latest:
    edge_factory_os_control_tower\control_tower_*\os_control_tower_state.json
    edge_factory_os_decision_ledger\master_os_decision_ledger.jsonl

Then emits:
    - current canonical OS state
    - allowed transitions
    - forbidden transitions
    - manual-approval gates
    - next safe state action

It does NOT start paper/live.
It does NOT execute commands.
It does NOT mutate active config.
It does NOT run --apply.

Run:
    python "C:\Users\alike\edge_factory_os_transition_controller.py"

Outputs:
    <workspace>\edge_factory_os_transition_controller\transition_YYYYMMDD_HHMMSS\
        os_transition_report.md
        os_transition_state.json
        os_transition_policy.json
        os_allowed_transitions.csv
        os_forbidden_transitions.csv
        os_manual_approval_gates.csv

Core principle
--------------
The OS may recommend a transition, but cannot perform unsafe transitions silently.
Paper start and live start are never automatic.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

CANONICAL_STATES = [
    "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED",
    "PAPER_START_MANUAL_APPROVAL_REQUIRED",
    "PAPER_RUNNING_WAITING_FOR_SAMPLE",
    "PAPER_RUNNING_READY_FOR_DRIFT_CHECK",
    "PAPER_DRIFT_VALIDATION_REQUIRED",
    "LIVE_MANUAL_REVIEW_REQUIRED",
    "LIVE_BLOCKED",
    "REBUILD_REQUIRED",
    "MANUAL_REVIEW_REQUIRED",
    "OS_REPAIR_REQUIRED",
    "UNSAFE_STATE_BLOCKED",
]

# State transition policy. These are policy permissions, not commands.
TRANSITION_POLICY = {
    "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED": {
        "allowed": [
            "PAPER_START_MANUAL_APPROVAL_REQUIRED",
            "REBUILD_REQUIRED",
            "MANUAL_REVIEW_REQUIRED",
            "OS_REPAIR_REQUIRED",
        ],
        "forbidden": [
            "LIVE_MANUAL_REVIEW_REQUIRED",
            "LIVE_ENABLED",
        ],
        "manual_approval_required": ["PAPER_START_MANUAL_APPROVAL_REQUIRED"],
        "evidence_required": [
            "control_tower_state == GREEN_CONTROL_PLANE_CURRENT",
            "semantic dependency chain current",
            "paper_boot_plan exists",
            "kill_switch_policy exists",
            "position_sizing_contract reconciled",
            "live_allowed == False",
        ],
    },
    "PAPER_START_MANUAL_APPROVAL_REQUIRED": {
        "allowed": [
            "PAPER_RUNNING_WAITING_FOR_SAMPLE",
            "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED",
            "REBUILD_REQUIRED",
            "OS_REPAIR_REQUIRED",
        ],
        "forbidden": ["LIVE_ENABLED"],
        "manual_approval_required": ["PAPER_RUNNING_WAITING_FOR_SAMPLE"],
        "evidence_required": [
            "explicit user decision to start supervised paper",
            "paper_launch_commands reviewed manually",
            "no live exchange mode",
            "native execution fields required",
        ],
    },
    "PAPER_RUNNING_WAITING_FOR_SAMPLE": {
        "allowed": [
            "PAPER_RUNNING_READY_FOR_DRIFT_CHECK",
            "PAPER_DRIFT_VALIDATION_REQUIRED",
            "REBUILD_REQUIRED",
            "OS_REPAIR_REQUIRED",
        ],
        "forbidden": ["LIVE_ENABLED"],
        "manual_approval_required": [],
        "evidence_required": [
            "paper folder exists",
            "closed trade sample not enough yet",
            "live_allowed == False",
        ],
    },
    "PAPER_RUNNING_READY_FOR_DRIFT_CHECK": {
        "allowed": [
            "PAPER_DRIFT_VALIDATION_REQUIRED",
            "LIVE_MANUAL_REVIEW_REQUIRED",
            "REBUILD_REQUIRED",
            "OS_REPAIR_REQUIRED",
        ],
        "forbidden": ["LIVE_ENABLED"],
        "manual_approval_required": ["LIVE_MANUAL_REVIEW_REQUIRED"],
        "evidence_required": [
            "closed paper trades exist",
            "native bps fields present",
            "drift monitor has not failed",
            "kill-switch log clean",
        ],
    },
    "PAPER_DRIFT_VALIDATION_REQUIRED": {
        "allowed": [
            "LIVE_MANUAL_REVIEW_REQUIRED",
            "PAPER_RUNNING_WAITING_FOR_SAMPLE",
            "REBUILD_REQUIRED",
            "OS_REPAIR_REQUIRED",
        ],
        "forbidden": ["LIVE_ENABLED"],
        "manual_approval_required": ["LIVE_MANUAL_REVIEW_REQUIRED"],
        "evidence_required": [
            "drift monitor result exists",
            "paper vs backtest drift acceptable",
            "family-level kill-switch state clean",
            "manual review still required before live",
        ],
    },
    "LIVE_MANUAL_REVIEW_REQUIRED": {
        "allowed": [
            "LIVE_BLOCKED",
            "REBUILD_REQUIRED",
            "OS_REPAIR_REQUIRED",
        ],
        "forbidden": ["LIVE_ENABLED"],
        "manual_approval_required": ["LIVE_ENABLED_NOT_IMPLEMENTED_IN_OS_V1"],
        "evidence_required": [
            "paper drift passed",
            "manual human live review completed",
            "real exchange risk limits outside this module",
            "OS v1 still cannot enable live",
        ],
    },
    "REBUILD_REQUIRED": {
        "allowed": [
            "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED",
            "MANUAL_REVIEW_REQUIRED",
            "OS_REPAIR_REQUIRED",
        ],
        "forbidden": ["PAPER_RUNNING_WAITING_FOR_SAMPLE", "LIVE_ENABLED"],
        "manual_approval_required": ["MANUAL_REVIEW_REQUIRED"],
        "evidence_required": ["safe rebuild plan executed or reviewed", "semantic staleness clean after rebuild"],
    },
    "MANUAL_REVIEW_REQUIRED": {
        "allowed": [
            "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED",
            "REBUILD_REQUIRED",
            "OS_REPAIR_REQUIRED",
        ],
        "forbidden": ["PAPER_RUNNING_WAITING_FOR_SAMPLE", "LIVE_ENABLED"],
        "manual_approval_required": ["CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED"],
        "evidence_required": ["manual review completed", "no unresolved config mismatch"],
    },
    "OS_REPAIR_REQUIRED": {
        "allowed": [
            "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED",
            "REBUILD_REQUIRED",
            "MANUAL_REVIEW_REQUIRED"],
        "forbidden": ["PAPER_RUNNING_WAITING_FOR_SAMPLE", "LIVE_ENABLED"],
        "manual_approval_required": [],
        "evidence_required": ["failed module repaired", "control tower returns non-red state"],
    },
    "UNSAFE_STATE_BLOCKED": {
        "allowed": ["OS_REPAIR_REQUIRED"],
        "forbidden": ["PAPER_RUNNING_WAITING_FOR_SAMPLE", "LIVE_ENABLED"],
        "manual_approval_required": ["OS_REPAIR_REQUIRED"],
        "evidence_required": ["unsafe flag cleared", "live_allowed false", "control tower green/yellow"],
    },
}

TOWER_TO_CANONICAL = {
    "GREEN_CONTROL_PLANE_CURRENT": "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED",
    "YELLOW_PAPER_RUNNING_WAITING_FOR_SAMPLE": "PAPER_RUNNING_WAITING_FOR_SAMPLE",
    "YELLOW_PAPER_RUNNING_READY_FOR_DRIFT_CHECK": "PAPER_RUNNING_READY_FOR_DRIFT_CHECK",
    "YELLOW_MANUAL_REVIEW_REQUIRED": "MANUAL_REVIEW_REQUIRED",
    "RED_REBUILD_REQUIRED": "REBUILD_REQUIRED",
    "RED_OS_REPAIR_REQUIRED": "OS_REPAIR_REQUIRED",
    "RED_UNSAFE_LIVE_FLAG": "UNSAFE_STATE_BLOCKED",
    "RED_LEDGER_ALERT": "UNSAFE_STATE_BLOCKED",
}


@dataclass
class TransitionRow:
    from_state: str
    to_state: str
    transition_type: str
    manual_approval_required: bool
    evidence_required: str
    allowed_now: bool
    reason: str


@dataclass
class TransitionDecision:
    current_tower_state: str
    current_canonical_state: str
    recommended_next_state: str
    recommendation_type: str
    live_allowed: bool
    paper_started: bool
    closed_paper_trades_exist: bool
    decision: str
    reasons: List[str]
    alerts: List[str]


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
        return obj if isinstance(obj, dict) else {}
    except Exception as e:
        return {"_load_error": str(e)}


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def discover_control_tower_state(workspace: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    d = latest_child_dir(workspace / "edge_factory_os_control_tower", "control_tower_")
    if not d:
        return None
    p = d / "os_control_tower_state.json"
    return p if p.exists() else None


def read_ledger_tail(workspace: Path, n: int = 5) -> List[Dict[str, Any]]:
    p = workspace / "edge_factory_os_decision_ledger" / "master_os_decision_ledger.jsonl"
    if not p.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows[-n:]


def extract_tower_state(obj: Dict[str, Any]) -> Dict[str, Any]:
    state = obj.get("state") if isinstance(obj.get("state"), dict) else {}
    return state


def canonical_from_tower(tower_state: str, paper_started: bool, closed_trades: bool, live_allowed: bool) -> str:
    if live_allowed:
        return "UNSAFE_STATE_BLOCKED"
    if tower_state in TOWER_TO_CANONICAL:
        return TOWER_TO_CANONICAL[tower_state]
    if paper_started and closed_trades:
        return "PAPER_RUNNING_READY_FOR_DRIFT_CHECK"
    if paper_started:
        return "PAPER_RUNNING_WAITING_FOR_SAMPLE"
    return "MANUAL_REVIEW_REQUIRED"


def build_transitions(current: str, paper_started: bool, closed_trades: bool, live_allowed: bool) -> List[TransitionRow]:
    spec = TRANSITION_POLICY.get(current, TRANSITION_POLICY["MANUAL_REVIEW_REQUIRED"])
    allowed = list(spec.get("allowed", []))
    forbidden = list(spec.get("forbidden", []))
    manual = set(spec.get("manual_approval_required", []))
    evidence = " | ".join(spec.get("evidence_required", []))

    rows: List[TransitionRow] = []
    for target in allowed:
        allowed_now = True
        reason = "policy allows this transition"
        if target == "PAPER_START_MANUAL_APPROVAL_REQUIRED" and paper_started:
            allowed_now = False
            reason = "paper already appears started"
        if target == "PAPER_RUNNING_WAITING_FOR_SAMPLE" and not paper_started:
            allowed_now = False
            reason = "paper is not started; requires explicit supervised paper start"
        if target == "PAPER_RUNNING_READY_FOR_DRIFT_CHECK" and not closed_trades:
            allowed_now = False
            reason = "closed paper trades not detected"
        rows.append(TransitionRow(
            from_state=current,
            to_state=target,
            transition_type="ALLOWED",
            manual_approval_required=target in manual,
            evidence_required=evidence,
            allowed_now=allowed_now,
            reason=reason,
        ))
    for target in forbidden:
        rows.append(TransitionRow(
            from_state=current,
            to_state=target,
            transition_type="FORBIDDEN",
            manual_approval_required=True,
            evidence_required=evidence,
            allowed_now=False,
            reason="policy forbids this transition in OS v1",
        ))
    return rows


def recommend_next_state(current: str, rows: List[TransitionRow], paper_started: bool, closed_trades: bool) -> Tuple[str, str, List[str]]:
    reasons: List[str] = []
    if current == "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED":
        reasons.append("control plane is current; next state is manual paper-start approval, not automatic paper start")
        return "PAPER_START_MANUAL_APPROVAL_REQUIRED", "MANUAL_GATE", reasons
    if current == "PAPER_RUNNING_WAITING_FOR_SAMPLE":
        reasons.append("paper running but sample incomplete; wait for closed trades")
        return "PAPER_RUNNING_READY_FOR_DRIFT_CHECK", "WAIT_FOR_EVIDENCE", reasons
    if current == "PAPER_RUNNING_READY_FOR_DRIFT_CHECK":
        reasons.append("closed paper trades detected; drift validation is required before any live review")
        return "PAPER_DRIFT_VALIDATION_REQUIRED", "VALIDATION_GATE", reasons
    if current == "REBUILD_REQUIRED":
        reasons.append("semantic dependency rebuild required before paper/live decisions")
        return "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED", "REBUILD_GATE", reasons
    if current == "MANUAL_REVIEW_REQUIRED":
        reasons.append("manual review required before returning to green control plane")
        return "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED", "MANUAL_GATE", reasons
    if current == "OS_REPAIR_REQUIRED":
        reasons.append("OS repair required before any state advancement")
        return "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED", "REPAIR_GATE", reasons
    if current == "UNSAFE_STATE_BLOCKED":
        reasons.append("unsafe state detected; only repair transition is allowed")
        return "OS_REPAIR_REQUIRED", "SAFETY_BLOCK", reasons
    reasons.append("no special recommendation; maintain current state")
    return current, "HOLD", reasons


def build_decision(tower_state_obj: Dict[str, Any], ledger_tail: List[Dict[str, Any]]) -> Tuple[TransitionDecision, List[TransitionRow]]:
    tower_state = str(tower_state_obj.get("tower_state", "UNKNOWN"))
    paper_started = bool(tower_state_obj.get("paper_started", False))
    closed_trades = bool(tower_state_obj.get("closed_paper_trades_exist", False))
    live_allowed = bool(tower_state_obj.get("live_allowed", False))
    tower_alerts = list(tower_state_obj.get("tower_alerts") or [])

    current = canonical_from_tower(tower_state, paper_started, closed_trades, live_allowed)
    rows = build_transitions(current, paper_started, closed_trades, live_allowed)
    recommended, rec_type, reasons = recommend_next_state(current, rows, paper_started, closed_trades)

    alerts: List[str] = []
    if live_allowed:
        alerts.append("LIVE_ALLOWED_TRUE_UNSAFE")
    alerts.extend(str(x) for x in tower_alerts)

    # Check ledger for repeated bad modes in recent tail.
    bad_recent = [r for r in ledger_tail if str(r.get("final_os_mode", "")) in {"REBUILD_REQUIRED", "OS_REPAIR_REQUIRED", "MANUAL_REVIEW_REQUIRED"}]
    if len(bad_recent) >= 3:
        alerts.append("REPEATED_BAD_LEDGER_MODES")

    if alerts:
        decision = "TRANSITION_BLOCKED_BY_ALERTS"
    elif current == "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED":
        decision = "READY_FOR_MANUAL_PAPER_APPROVAL_ONLY"
    elif current.startswith("PAPER_RUNNING"):
        decision = "PAPER_STATE_WAIT_FOR_VALIDATION"
    elif current in {"REBUILD_REQUIRED", "MANUAL_REVIEW_REQUIRED", "OS_REPAIR_REQUIRED"}:
        decision = "REPAIR_OR_REVIEW_REQUIRED"
    else:
        decision = "HOLD_CURRENT_STATE"

    return TransitionDecision(
        current_tower_state=tower_state,
        current_canonical_state=current,
        recommended_next_state=recommended,
        recommendation_type=rec_type,
        live_allowed=False,
        paper_started=paper_started,
        closed_paper_trades_exist=closed_trades,
        decision=decision,
        reasons=reasons,
        alerts=alerts,
    ), rows


def transition_df(rows: List[TransitionRow], kind: Optional[str] = None) -> pd.DataFrame:
    selected = rows if kind is None else [r for r in rows if r.transition_type == kind]
    return pd.DataFrame([asdict(r) for r in selected])


def write_report(path: Path, decision: TransitionDecision, rows: List[TransitionRow], source_path: Optional[Path]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Transition Controller Report")
    lines.append("")
    lines.append(f"Generated: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"Source control tower: `{source_path}`")
    lines.append(f"Decision: **{decision.decision}**")
    lines.append(f"Current canonical state: **{decision.current_canonical_state}**")
    lines.append(f"Recommended next state: **{decision.recommended_next_state}**")
    lines.append(f"Recommendation type: **{decision.recommendation_type}**")
    lines.append(f"Live allowed: **{decision.live_allowed}**")
    lines.append("")

    lines.append("## Reasons")
    lines.append("")
    for r in decision.reasons:
        lines.append(f"- {r}")
    lines.append("")

    if decision.alerts:
        lines.append("## Alerts")
        lines.append("")
        for a in decision.alerts:
            lines.append(f"- `{a}`")
        lines.append("")

    lines.append("## Allowed transitions")
    lines.append("")
    allowed = [r for r in rows if r.transition_type == "ALLOWED"]
    if not allowed:
        lines.append("No allowed transitions.")
    else:
        lines.append("| To state | Allowed now | Manual approval | Reason | Evidence |")
        lines.append("|---|---:|---:|---|---|")
        for r in allowed:
            lines.append(f"| {r.to_state} | {r.allowed_now} | {r.manual_approval_required} | {r.reason} | {r.evidence_required} |")
    lines.append("")

    lines.append("## Forbidden transitions")
    lines.append("")
    forbidden = [r for r in rows if r.transition_type == "FORBIDDEN"]
    if not forbidden:
        lines.append("No forbidden transitions listed for this state.")
    else:
        lines.append("| To state | Reason |")
        lines.append("|---|---|")
        for r in forbidden:
            lines.append(f"| {r.to_state} | {r.reason} |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("The transition controller formalizes the OS state machine. It does not start paper/live; it only says what transition is legal, forbidden, or requires manual approval.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS transition controller")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--control_tower_state", default=None)
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_transition_controller"
    out_dir = out_root / f"transition_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    source = discover_control_tower_state(workspace, Path(args.control_tower_state) if args.control_tower_state else None)
    if source is None:
        err = {"error": "No control tower state found", "expected_root": str(workspace / "edge_factory_os_control_tower")}
        write_json(out_dir / "fatal_error.json", err)
        print("EDGE FACTORY OS TRANSITION CONTROLLER v1")
        print("No control tower state found. Run edge_factory_os_control_tower.py first.")
        print(f"Details: {out_dir / 'fatal_error.json'}")
        return 2

    tower_obj = optional_json(source)
    tower_state_obj = extract_tower_state(tower_obj)
    ledger_tail = read_ledger_tail(workspace, 5)
    decision, rows = build_decision(tower_state_obj, ledger_tail)

    policy_obj = {
        "canonical_states": CANONICAL_STATES,
        "transition_policy": TRANSITION_POLICY,
        "tower_to_canonical": TOWER_TO_CANONICAL,
    }
    result = {
        "decision": asdict(decision),
        "transitions": [asdict(r) for r in rows],
        "source_control_tower_state": str(source),
        "ledger_tail_count": len(ledger_tail),
        "hard_rules": [
            "Transition controller never starts paper/live.",
            "Transition controller never executes commands.",
            "LIVE_ENABLED is forbidden in OS v1.",
            "Paper start requires explicit manual approval.",
        ],
    }

    write_json(out_dir / "os_transition_state.json", result)
    write_json(out_dir / "os_transition_policy.json", policy_obj)
    transition_df(rows).to_csv(out_dir / "os_all_transitions.csv", index=False)
    transition_df(rows, "ALLOWED").to_csv(out_dir / "os_allowed_transitions.csv", index=False)
    transition_df(rows, "FORBIDDEN").to_csv(out_dir / "os_forbidden_transitions.csv", index=False)
    manual_rows = [r for r in rows if r.manual_approval_required]
    pd.DataFrame([asdict(r) for r in manual_rows]).to_csv(out_dir / "os_manual_approval_gates.csv", index=False)
    write_report(out_dir / "os_transition_report.md", decision, rows, source)

    print("EDGE FACTORY OS TRANSITION CONTROLLER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"source    : {source}")
    print(f"output_dir: {out_dir}")
    print(f"decision  : {decision.decision}")
    print(f"current   : {decision.current_canonical_state}")
    print(f"next      : {decision.recommended_next_state}")
    print(f"type      : {decision.recommendation_type}")
    print(f"paper     : started={decision.paper_started} closed_trades={decision.closed_paper_trades_exist}")
    print("live_allowed: False")
    print("")
    print("REASONS")
    print("-" * 100)
    for r in decision.reasons:
        print(f"- {r}")
    if decision.alerts:
        print("")
        print("ALERTS")
        print("-" * 100)
        for a in decision.alerts:
            print(f"- {a}")
    print("")
    print("ALLOWED TRANSITIONS")
    print("-" * 100)
    for r in rows:
        if r.transition_type == "ALLOWED":
            print(f"{r.to_state:45s} allowed_now={str(r.allowed_now):5s} manual={r.manual_approval_required} reason={r.reason}")
    print("")
    print("FORBIDDEN TRANSITIONS")
    print("-" * 100)
    for r in rows:
        if r.transition_type == "FORBIDDEN":
            print(f"{r.to_state:45s} reason={r.reason}")
    print("")
    print(f"Report : {out_dir / 'os_transition_report.md'}")
    print(f"State  : {out_dir / 'os_transition_state.json'}")
    print(f"Policy : {out_dir / 'os_transition_policy.json'}")
    return 2 if decision.alerts else 0



if __name__ == "__main__":
    raise SystemExit(main())
