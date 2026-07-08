#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS SELF-IMPROVEMENT PLANNER v1
===========================================

Purpose
-------
Safe self-improvement / autonomous research planner for the Edge Factory OS.

The control plane is now able to answer:
    - is paper ready?
    - is manual approval present?
    - is paper running?
    - is drift validation ready?
    - is live blocked?

This module is the next OS layer: it decides what the system should research next while
respecting the current control state.

It DOES NOT:
    - start paper
    - start live
    - run loggers
    - run start_edge_factory_MASTER_UPPER_SYSTEM.ps1
    - run --apply
    - mutate active config
    - promote any strategy automatically
    - change sizing automatically

It DOES:
    - read Control Tower v4
    - read Rolling OOS v2 cleanup outputs
    - read lifecycle / capital / execution / kill-switch artifacts if available
    - build a research backlog
    - classify tasks as READY_OFFLINE / WAITING_FOR_PAPER / BLOCKED / FUTURE
    - produce a safe next research queue
    - write reference-only commands, never execute them

Run:
    python "C:\Users\alike\edge_factory_os_self_improvement_planner.py"

Outputs:
    <workspace>\edge_factory_os_self_improvement_planner\self_improve_YYYYMMDD_HHMMSS\
        os_self_improvement_report.md
        os_self_improvement_state.json
        os_self_improvement_queue.csv
        os_self_improvement_queue.json
        os_self_improvement_reference_commands.ps1
        os_self_improvement_evidence.csv

Core principle
--------------
When paper/live are blocked or waiting, the OS should still improve safely via offline
research, validation, cleanup, and planning tasks. This is the beginning of the Edge
Factory's self-improvement brain.
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
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")

ARTIFACTS = {
    "control_tower_v4": ("edge_factory_os_control_tower_v4", "control_tower_v4_", "os_control_tower_v4_state.json"),
    "rolling_oos_v2": ("edge_factory_rolling_oos_validator_v2", "rolling_oos_v2_", "clean_os_family_state_seed.json"),
    "rolling_oos_v2_active": ("edge_factory_rolling_oos_validator_v2", "rolling_oos_v2_", "active_family_decisions.json"),
    "lifecycle": ("edge_factory_family_lifecycle", "lifecycle_", "family_lifecycle_state.json"),
    "capital_governor_v2": ("edge_factory_adaptive_capital_governor_v2", "capital_governor_", "capital_policy_proposal.json"),
    "execution_realism": ("edge_factory_execution_realism_checker", "execution_realism_", "execution_realism_decisions.json"),
    "kill_switch": ("edge_factory_kill_switch_controller", "kill_switch_", "kill_switch_policy.json"),
    "native_bps": ("edge_factory_native_bps_validator", "native_bps_", "native_bps_validation.json"),
    "paper_runtime": ("edge_factory_os_paper_runtime_observer", "paper_runtime_", "os_paper_runtime_observer_state.json"),
    "drift_gate": ("edge_factory_os_drift_gate_controller", "drift_gate_", "os_drift_gate_decision.json"),
    "decision_ledger_snapshot": ("edge_factory_os_decision_ledger", "ledger_run_", "os_decision_ledger_snapshot.json"),
    "decision_ledger_diff": ("edge_factory_os_decision_ledger", "ledger_run_", "os_decision_ledger_diff.json"),
}

# Known scripts. Some may not exist yet. Missing scripts become BUILD_MODULE tasks.
KNOWN_SCRIPTS = {
    "candidate_lab_builder": "edge_factory_candidate_lab_builder.py",
    "research_candidate_validator": "edge_factory_research_candidate_validator.py",
    "coin_subset_validator": "edge_factory_coin_subset_validator.py",
    "rolling_retrain_validator": "edge_factory_rolling_retrain_validator.py",
    "research_result_ledger": "edge_factory_research_result_ledger.py",
    "family_promotion_sandbox": "edge_factory_family_promotion_sandbox.py",
    "paper_drift_response_planner": "edge_factory_paper_drift_response_planner.py",
    "artifact_consistency_auditor": "edge_factory_artifact_consistency_auditor.py",
}

ACTIVE_FAMILIES = ["old_short", "impulse_long", "market_relative_short", "weak_market_short"]
DISABLED_FAMILIES = ["session_short"]

RESEARCH_CANDIDATE_HINTS = [
    "rel_extreme_reversion_short",
    "ret60_reversal_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
]


@dataclass
class Evidence:
    key: str
    path: Optional[str]
    exists: bool
    modified_at: Optional[str]
    status: str
    message: str


@dataclass
class ResearchTask:
    priority: int
    task_id: str
    category: str
    status: str
    title: str
    reason: str
    target: str
    command: Optional[str]
    safe_offline: bool
    blocked_by: List[str]
    expected_output: str
    promotes_or_trades: bool


@dataclass
class PlannerState:
    generated_at: str
    planner_mode: str
    control_tower_state: str
    paper_started: bool
    closed_paper_trades: bool
    live_allowed: bool
    ready_offline_count: int
    waiting_for_paper_count: int
    blocked_count: int
    future_count: int
    top_next_task: Optional[str]
    reasons: List[str]
    warnings: List[str]
    hard_rules: List[str]


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


def artifact_path(workspace: Path, key: str) -> Optional[Path]:
    root_name, prefix, filename = ARTIFACTS[key]
    d = latest_child_dir(workspace / root_name, prefix)
    if not d:
        return None
    p = d / filename
    return p if p.exists() else None


def collect_evidence(workspace: Path, script_dir: Path) -> Dict[str, Evidence]:
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
    for key, script_name in KNOWN_SCRIPTS.items():
        p = script_dir / script_name
        exists = p.exists() and p.is_file()
        out[f"script_{key}"] = Evidence(
            key=f"script_{key}",
            path=str(p),
            exists=exists,
            modified_at=iso_mtime(p) if exists else None,
            status="PASS" if exists else "MISSING",
            message="script found" if exists else "script missing / not built yet",
        )
    return out


def data_from_evidence(evidence: Dict[str, Evidence]) -> Dict[str, Dict[str, Any]]:
    return {k: optional_json(Path(v.path) if v.path else None) for k, v in evidence.items()}


def control_state(data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    obj = data.get("control_tower_v4", {})
    return obj.get("state") if isinstance(obj.get("state"), dict) else {}


def queue_status_counts(tasks: List[ResearchTask]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for t in tasks:
        out[t.status] = out.get(t.status, 0) + 1
    return out


def script_exists(evidence: Dict[str, Evidence], script_key: str) -> bool:
    return evidence.get(f"script_{script_key}", Evidence("", None, False, None, "", "")).exists


def script_command(script_dir: Path, script_key: str, args: str = "") -> Optional[str]:
    script_name = KNOWN_SCRIPTS.get(script_key)
    if not script_name:
        return None
    cmd = f'python "{script_dir / script_name}"'
    if args.strip():
        cmd += " " + args.strip()
    return cmd


def extract_research_candidates(data: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    seed = data.get("rolling_oos_v2", {})
    candidates: List[Dict[str, Any]] = []

    # Best effort: many generated schemas are possible.
    for key in ["research_candidates", "top_research_candidates", "candidates"]:
        val = seed.get(key)
        if isinstance(val, list):
            for row in val:
                if isinstance(row, dict):
                    candidates.append(row)

    # Fallback: use known names from latest console output.
    if not candidates:
        for name in RESEARCH_CANDIDATE_HINTS:
            candidates.append({"family_key": name, "source": "known_hint_from_oos_v2_console"})
    return candidates


def build_tasks(workspace: Path, script_dir: Path, evidence: Dict[str, Evidence], data: Dict[str, Dict[str, Any]]) -> Tuple[PlannerState, List[ResearchTask]]:
    cstate = control_state(data)
    tower_state = str(cstate.get("tower_state", "UNKNOWN"))
    paper_started = bool(cstate.get("paper_started", False))
    closed_trades = bool(cstate.get("closed_paper_trades_detected", False))
    live_allowed = bool(cstate.get("live_allowed", False))
    drift_gate_status = str(cstate.get("drift_gate_status", "UNKNOWN"))
    paper_runtime_status = str(cstate.get("paper_runtime_status", "UNKNOWN"))

    tasks: List[ResearchTask] = []
    warnings: List[str] = []
    reasons: List[str] = []

    if live_allowed:
        planner_mode = "SELF_IMPROVEMENT_BLOCKED_UNSAFE_LIVE_FLAG"
        reasons.append("live_allowed is true in control tower; self-improvement must halt until repaired")
    elif tower_state.startswith("RED"):
        planner_mode = "SELF_IMPROVEMENT_BLOCKED_CONTROL_TOWER_RED"
        reasons.append("control tower is red; repair control plane before research")
    else:
        planner_mode = "SELF_IMPROVEMENT_OFFLINE_RESEARCH_ALLOWED"
        reasons.append("control tower is safe and live is blocked; offline research planning is allowed")

    def add(priority: int, task_id: str, category: str, status: str, title: str, reason: str, target: str, command: Optional[str], safe: bool, blocked: List[str], expected: str, promotes: bool = False) -> None:
        tasks.append(ResearchTask(priority, task_id, category, status, title, reason, target, command, safe, blocked, expected, promotes))

    # 1. If red/unsafe, only repair task.
    if planner_mode.startswith("SELF_IMPROVEMENT_BLOCKED"):
        add(
            1,
            "repair_control_tower_before_research",
            "OS_REPAIR",
            "BLOCKED",
            "Repair control tower before any research planning",
            "Unsafe/red OS state blocks research automation.",
            "control_tower_v4",
            None,
            True,
            ["control tower safe state"],
            "control tower returns non-red and live_allowed=False",
        )
    else:
        # 2. Build missing research infrastructure modules.
        build_order = [
            ("research_result_ledger", "Create persistent research result memory"),
            ("candidate_lab_builder", "Create isolated candidate lab / sandbox builder"),
            ("research_candidate_validator", "Validate OOS v2 research candidates without promotion"),
            ("coin_subset_validator", "Test coin-family fit / subset robustness"),
            ("rolling_retrain_validator", "Run rolling retrain / time OOS validation"),
            ("family_promotion_sandbox", "Stage promotion simulation without changing active system"),
            ("artifact_consistency_auditor", "Audit artifact schema consistency across OS modules"),
        ]
        p = 10
        for script_key, title in build_order:
            if not script_exists(evidence, script_key):
                add(
                    p,
                    f"build_{script_key}",
                    "BUILD_SELF_IMPROVEMENT_MODULE",
                    "READY_OFFLINE",
                    title,
                    f"Script {KNOWN_SCRIPTS[script_key]} is missing; OS cannot execute this self-improvement capability yet.",
                    script_key,
                    None,
                    True,
                    [],
                    str(script_dir / KNOWN_SCRIPTS[script_key]),
                )
                p += 10

        # 3. Candidate validation queue from OOS v2.
        candidates = extract_research_candidates(data)
        if candidates:
            for i, row in enumerate(candidates[:8], start=1):
                name = str(row.get("family_key", row.get("name", row.get("candidate", f"candidate_{i}"))))
                if script_exists(evidence, "research_candidate_validator"):
                    cmd = script_command(script_dir, "research_candidate_validator", f'--candidate "{name}" --workspace "{workspace}"')
                    status = "READY_OFFLINE"
                    blocked = []
                else:
                    cmd = None
                    status = "WAITING_FOR_MODULE"
                    blocked = ["build_research_candidate_validator"]
                add(
                    100 + i,
                    f"validate_candidate_{name}",
                    "CANDIDATE_VALIDATION",
                    status,
                    f"Validate research candidate: {name}",
                    "OOS v2 cleanup identified this as a non-master research candidate; validate without promotion.",
                    name,
                    cmd,
                    True,
                    blocked,
                    f"candidate_validation_{name}",
                    promotes=False,
                )

        # 4. Active family robustness tasks.
        for i, fam in enumerate(ACTIVE_FAMILIES, start=1):
            if script_exists(evidence, "coin_subset_validator"):
                cmd = script_command(script_dir, "coin_subset_validator", f'--family "{fam}" --workspace "{workspace}"')
                status = "READY_OFFLINE"
                blocked = []
            else:
                cmd = None
                status = "WAITING_FOR_MODULE"
                blocked = ["build_coin_subset_validator"]
            add(
                200 + i,
                f"coin_subset_robustness_{fam}",
                "ACTIVE_FAMILY_ROBUSTNESS",
                status,
                f"Run coin-subset robustness for active family: {fam}",
                "The OS should verify coin-family fit instead of assuming a family works everywhere.",
                fam,
                cmd,
                True,
                blocked,
                f"coin_subset_robustness_{fam}",
                promotes=False,
            )

        # 5. Paper-dependent tasks.
        if closed_trades:
            if script_exists(evidence, "paper_drift_response_planner"):
                cmd = script_command(script_dir, "paper_drift_response_planner", f'--workspace "{workspace}"')
                status = "READY_OFFLINE"
                blocked = []
            else:
                cmd = None
                status = "WAITING_FOR_MODULE"
                blocked = ["build_paper_drift_response_planner"]
            add(
                300,
                "plan_response_to_paper_drift",
                "PAPER_DRIFT_RESPONSE",
                status,
                "Plan response to paper-vs-backtest drift result",
                "Closed paper trades exist; after drift monitor, OS needs response plan.",
                "paper_runtime",
                cmd,
                True,
                blocked,
                "paper_drift_response_plan",
                promotes=False,
            )
        else:
            add(
                300,
                "wait_for_paper_before_drift_response",
                "PAPER_DEPENDENT",
                "WAITING_FOR_PAPER",
                "Wait for paper runtime before drift-response planning",
                f"Current runtime={paper_runtime_status}, drift_gate={drift_gate_status}; no closed paper sample exists.",
                "paper_runtime",
                None,
                True,
                ["manual paper start", "closed paper trades", "drift monitor result"],
                "paper closed trade sample",
                promotes=False,
            )

        # 6. Permanent safety task.
        add(
            999,
            "live_remains_blocked",
            "SAFETY",
            "HARD_RULE",
            "Keep live trading blocked",
            "Self-improvement planner cannot approve live. Live requires paper drift validation and manual review.",
            "live_gate",
            None,
            True,
            ["paper drift validation", "manual live review"],
            "live remains blocked",
            promotes=False,
        )

    counts = queue_status_counts(tasks)
    top_ready = next((t.task_id for t in sorted(tasks, key=lambda x: x.priority) if t.status == "READY_OFFLINE"), None)
    state = PlannerState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        planner_mode=planner_mode,
        control_tower_state=tower_state,
        paper_started=paper_started,
        closed_paper_trades=closed_trades,
        live_allowed=False,
        ready_offline_count=counts.get("READY_OFFLINE", 0),
        waiting_for_paper_count=counts.get("WAITING_FOR_PAPER", 0),
        blocked_count=counts.get("BLOCKED", 0),
        future_count=counts.get("FUTURE", 0) + counts.get("WAITING_FOR_MODULE", 0),
        top_next_task=top_ready,
        reasons=reasons,
        warnings=warnings,
        hard_rules=[
            "Self-improvement planner never starts paper/live.",
            "Self-improvement planner never mutates active config.",
            "Self-improvement planner never promotes a candidate automatically.",
            "Research tasks are offline/reference only unless a future executor explicitly runs safe tasks.",
            "Live remains blocked until paper drift validation and manual review.",
        ],
    )
    return state, sorted(tasks, key=lambda x: x.priority)


def evidence_df(evidence: Dict[str, Evidence]) -> pd.DataFrame:
    return pd.DataFrame([asdict(v) for v in evidence.values()])


def tasks_df(tasks: List[ResearchTask]) -> pd.DataFrame:
    rows = []
    for t in tasks:
        row = asdict(t)
        row["blocked_by"] = " | ".join(t.blocked_by)
        rows.append(row)
    return pd.DataFrame(rows)


def write_reference_commands(path: Path, tasks: List[ResearchTask]) -> None:
    lines: List[str] = []
    lines.append("# EDGE FACTORY OS SELF-IMPROVEMENT REFERENCE COMMANDS")
    lines.append(f"# Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("# Reference only. This file was not executed.")
    lines.append("# No paper/live/start/apply commands are included.")
    lines.append("")
    for t in tasks:
        lines.append(f"# {t.priority:03d} {t.task_id} [{t.status}] {t.category}")
        lines.append(f"# {t.title}")
        lines.append(f"# reason: {t.reason}")
        if t.blocked_by:
            lines.append(f"# blocked_by: {', '.join(t.blocked_by)}")
        if t.command and t.status == "READY_OFFLINE" and not t.promotes_or_trades:
            lines.append(f"# {t.command}")
        else:
            lines.append("# no runnable safe command yet")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, state: PlannerState, tasks: List[ResearchTask], evidence: Dict[str, Evidence]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Self-Improvement Planner Report")
    lines.append("")
    lines.append(f"Generated: `{state.generated_at}`")
    lines.append(f"Planner mode: **{state.planner_mode}**")
    lines.append(f"Control Tower state: **{state.control_tower_state}**")
    lines.append(f"Paper started: **{state.paper_started}**")
    lines.append(f"Closed paper trades: **{state.closed_paper_trades}**")
    lines.append(f"Live allowed: **{state.live_allowed}**")
    lines.append(f"Top next task: **{state.top_next_task}**")
    lines.append("")

    lines.append("## Reasons")
    lines.append("")
    for r in state.reasons:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Queue summary")
    lines.append("")
    lines.append(f"- READY_OFFLINE: **{state.ready_offline_count}**")
    lines.append(f"- WAITING_FOR_PAPER: **{state.waiting_for_paper_count}**")
    lines.append(f"- BLOCKED: **{state.blocked_count}**")
    lines.append(f"- FUTURE/WAITING_FOR_MODULE: **{state.future_count}**")
    lines.append("")

    lines.append("## Research queue")
    lines.append("")
    lines.append("| Priority | Status | Category | Task | Target | Blocked by |")
    lines.append("|---:|---:|---|---|---|---|")
    for t in tasks[:80]:
        lines.append(f"| {t.priority} | {t.status} | {t.category} | {t.title} | {t.target} | {', '.join(t.blocked_by)} |")
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
    for r in state.hard_rules:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This is the first self-improvement brain layer. It does not trade or promote anything. It decides which research infrastructure and validation tasks the OS should build or run next, while respecting the current control-plane and paper/live gates.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Edge Factory OS self-improvement planner")
    parser.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    parser.add_argument("--script_dir", default=str(DEFAULT_SCRIPT_DIR))
    parser.add_argument("--out_dir", default=None)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    script_dir = Path(args.script_dir)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_self_improvement_planner"
    out_dir = out_root / f"self_improve_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    evidence = collect_evidence(workspace, script_dir)
    data = data_from_evidence(evidence)
    state, tasks = build_tasks(workspace, script_dir, evidence, data)

    result = {
        "state": asdict(state),
        "queue": [asdict(t) for t in tasks],
        "evidence": {k: asdict(v) for k, v in evidence.items()},
    }
    write_json(out_dir / "os_self_improvement_state.json", result)
    write_json(out_dir / "os_self_improvement_queue.json", [asdict(t) for t in tasks])
    tasks_df(tasks).to_csv(out_dir / "os_self_improvement_queue.csv", index=False)
    evidence_df(evidence).to_csv(out_dir / "os_self_improvement_evidence.csv", index=False)
    write_reference_commands(out_dir / "os_self_improvement_reference_commands.ps1", tasks)
    write_report(out_dir / "os_self_improvement_report.md", state, tasks, evidence)

    print("EDGE FACTORY OS SELF-IMPROVEMENT PLANNER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"script_dir: {script_dir}")
    print(f"output_dir: {out_dir}")
    print(f"planner_mode: {state.planner_mode}")
    print(f"control_tower_state: {state.control_tower_state}")
    print(f"paper_started: {state.paper_started} closed_trades={state.closed_paper_trades}")
    print("live_allowed: False")
    print(f"ready_offline={state.ready_offline_count} waiting_for_paper={state.waiting_for_paper_count} blocked={state.blocked_count} future_or_waiting_module={state.future_count}")
    print(f"top_next_task: {state.top_next_task}")
    print("")
    print("REASONS")
    print("-" * 100)
    for r in state.reasons:
        print(f"- {r}")
    print("")
    print("TOP QUEUE")
    print("-" * 100)
    for t in tasks[:15]:
        print(f"P{t.priority:03d} [{t.status}] {t.category} -> {t.task_id}")
        print(f"     title : {t.title}")
        if t.blocked_by:
            print(f"     blocked_by: {', '.join(t.blocked_by)}")
        if t.command:
            print(f"     command: {t.command}")
        print(f"     reason: {t.reason}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not mutate config, and did not promote any strategy.")
    print("")
    print(f"Report : {out_dir / 'os_self_improvement_report.md'}")
    print(f"State  : {out_dir / 'os_self_improvement_state.json'}")
    print(f"Queue  : {out_dir / 'os_self_improvement_queue.json'}")
    return 0 if not state.planner_mode.startswith("SELF_IMPROVEMENT_BLOCKED") else 2



if __name__ == "__main__":
    raise SystemExit(main())
