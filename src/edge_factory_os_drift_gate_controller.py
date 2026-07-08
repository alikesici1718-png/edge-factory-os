#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS DRIFT GATE CONTROLLER v1
========================================

Purpose
-------
Safe gate controller for live-vs-backtest drift validation in the self-improving Edge Factory OS.

This module is used after supervised paper has produced enough closed trades. It decides
whether the drift monitor is allowed to be run as an offline validation step.

It DOES NOT:
    - start paper
    - start live
    - run loggers
    - execute PowerShell launchers
    - run --apply
    - mutate active config
    - approve live

Default behavior
----------------
It only inspects latest artifacts and emits a decision.
It does not execute the drift monitor.

Run:
    python "C:\Users\alike\edge_factory_os_drift_gate_controller.py"

Optional reference-only command plan is always commented out.

Outputs:
    <workspace>\edge_factory_os_drift_gate_controller\drift_gate_YYYYMMDD_HHMMSS\
        os_drift_gate_report.md
        os_drift_gate_decision.json
        os_drift_gate_checklist.csv
        os_drift_gate_evidence.csv
        drift_monitor_REFERENCE_ONLY.ps1

Possible gate statuses
----------------------
    DRIFT_BLOCKED_PAPER_NOT_STARTED
    DRIFT_BLOCKED_NO_CLOSED_TRADES
    DRIFT_BLOCKED_NATIVE_FIELDS_MISSING
    DRIFT_BLOCKED_CONTROL_TOWER_NOT_SAFE
    DRIFT_READY_REFERENCE_ONLY
    DRIFT_ALREADY_RAN_REVIEW_REQUIRED

Core rule
---------
Even if DRIFT_READY_REFERENCE_ONLY appears, this module does not run the drift monitor.
It only writes a commented reference command.
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
DEFAULT_DRIFT_SCRIPT = DEFAULT_SCRIPT_DIR / "edge_factory_live_vs_backtest_drift_monitor.py"
DEFAULT_PAPER_DIR = DEFAULT_WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

ARTIFACTS = {
    "control_tower_v3": ("edge_factory_os_control_tower_v3", "control_tower_v3_", "os_control_tower_v3_state.json"),
    "paper_runtime_observer": ("edge_factory_os_paper_runtime_observer", "paper_runtime_", "os_paper_runtime_observer_state.json"),
    "paper_start_gate": ("edge_factory_os_paper_start_gate", "paper_start_gate_", "os_paper_start_gate_decision.json"),
    "manual_approval_record": ("edge_factory_os_manual_approval_recorder", "manual_approval_", "os_manual_approval_record.json"),
    "dependency_staleness_v2": ("edge_factory_os_dependency_staleness_v2", "dependency_staleness_v2_", "os_dependency_staleness_v2.json"),
    "native_bps_validator": ("edge_factory_native_bps_validator", "native_bps_", "native_bps_validation.json"),
    "drift_monitor": ("edge_factory_drift_monitor", "drift_report_", "drift_report.json"),
}


@dataclass
class Evidence:
    key: str
    path: Optional[str]
    exists: bool
    modified_at: Optional[str]
    status: str
    message: str


@dataclass
class GateCheck:
    key: str
    category: str
    required: bool
    passed: bool
    description: str
    evidence: str


@dataclass
class DriftGateDecision:
    generated_at: str
    gate_status: str
    drift_reference_allowed: bool
    drift_monitor_already_exists: bool
    paper_started: bool
    closed_paper_trades_detected: bool
    native_logging_ready: bool
    live_allowed: bool
    next_os_action: str
    blockers: List[str]
    warnings: List[str]
    reasons: List[str]
    drift_script_path: str
    paper_dir: str
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
    drift_exists = DEFAULT_DRIFT_SCRIPT.exists() and DEFAULT_DRIFT_SCRIPT.is_file()
    out["drift_script"] = Evidence(
        key="drift_script",
        path=str(DEFAULT_DRIFT_SCRIPT),
        exists=drift_exists,
        modified_at=iso_mtime(DEFAULT_DRIFT_SCRIPT) if drift_exists else None,
        status="PASS" if drift_exists else "MISSING",
        message="drift script found" if drift_exists else "drift script missing",
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


def runtime_decision(data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    obj = data.get("paper_runtime_observer", {})
    d = obj.get("decision") if isinstance(obj.get("decision"), dict) else {}
    return d


def tower_state(data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    obj = data.get("control_tower_v3", {})
    s = obj.get("state") if isinstance(obj.get("state"), dict) else {}
    return s


def build_checks(evidence: Dict[str, Evidence], data: Dict[str, Dict[str, Any]]) -> List[GateCheck]:
    checks: List[GateCheck] = []
    runtime = runtime_decision(data)
    tower = tower_state(data)
    stale_context = data.get("dependency_staleness_v2", {}).get("context") if isinstance(data.get("dependency_staleness_v2", {}).get("context"), dict) else {}

    runtime_status = str(runtime.get("runtime_status", "UNKNOWN"))
    tower_state_value = str(tower.get("tower_state", "UNKNOWN"))
    live_allowed = bool(tower.get("live_allowed", False)) or bool(runtime.get("live_allowed", False))
    closed = bool(runtime.get("closed_trades_detected", False))
    paper_started = bool(runtime.get("paper_dir_exists", False) and runtime.get("paper_dir_nonempty", False))
    native_ready = int(runtime.get("native_ready_file_count", 0) or 0) > 0 or int(runtime.get("native_partial_file_count", 0) or 0) > 0

    def add(key: str, cat: str, required: bool, passed: bool, desc: str, ev: str) -> None:
        checks.append(GateCheck(key, cat, required, passed, desc, ev))

    add(
        "control_tower_safe",
        "control",
        True,
        not tower_state_value.startswith("RED") and not live_allowed,
        "Control Tower v3 is not red and live is not allowed.",
        evidence["control_tower_v3"].path or "missing",
    )
    add(
        "dependency_chain_current",
        "dependency",
        True,
        str(stale_context.get("overall_state", "")) == "DEPENDENCY_CHAIN_CURRENT",
        "Semantic dependency chain is current.",
        evidence["dependency_staleness_v2"].path or "missing",
    )
    add(
        "paper_started",
        "runtime",
        True,
        paper_started,
        "Paper runtime directory exists and is non-empty.",
        evidence["paper_runtime_observer"].path or "missing",
    )
    add(
        "closed_paper_trades_detected",
        "runtime",
        True,
        closed,
        "Closed paper trade evidence exists.",
        evidence["paper_runtime_observer"].path or "missing",
    )
    add(
        "native_logging_ready",
        "logging",
        True,
        native_ready,
        "Runtime observer found native or partial/alias execution fields.",
        evidence["paper_runtime_observer"].path or "missing",
    )
    add(
        "runtime_ready_for_drift",
        "runtime",
        True,
        runtime_status == "PAPER_RUNNING_READY_FOR_DRIFT_CHECK",
        "Runtime observer explicitly says drift check is ready.",
        evidence["paper_runtime_observer"].path or "missing",
    )
    add(
        "drift_script_exists",
        "script",
        True,
        evidence["drift_script"].exists,
        "Drift monitor script exists.",
        evidence["drift_script"].path or "missing",
    )
    return checks


def decide(evidence: Dict[str, Evidence], data: Dict[str, Dict[str, Any]], checks: List[GateCheck]) -> DriftGateDecision:
    runtime = runtime_decision(data)
    tower = tower_state(data)

    runtime_status = str(runtime.get("runtime_status", "UNKNOWN"))
    paper_started = bool(runtime.get("paper_dir_exists", False) and runtime.get("paper_dir_nonempty", False))
    closed = bool(runtime.get("closed_trades_detected", False))
    native_ready = int(runtime.get("native_ready_file_count", 0) or 0) > 0 or int(runtime.get("native_partial_file_count", 0) or 0) > 0
    live_allowed = bool(tower.get("live_allowed", False)) or bool(runtime.get("live_allowed", False))
    drift_already = evidence.get("drift_monitor", Evidence("", None, False, None, "", "")).exists

    failed = [c for c in checks if c.required and not c.passed]
    blockers = [c.key for c in failed]
    warnings: List[str] = []
    reasons: List[str] = []

    if live_allowed:
        status = "DRIFT_BLOCKED_UNSAFE_LIVE_FLAG"
        reasons.append("Live flag is true in an upstream artifact; drift gate blocks.")
        next_action = "REPAIR_UNSAFE_LIVE_FLAG"
        allowed = False
    elif not paper_started:
        status = "DRIFT_BLOCKED_PAPER_NOT_STARTED"
        reasons.append("Paper runtime has not started, so no drift sample can exist.")
        next_action = "KEEP_WAITING_OR_USE_MANUAL_APPROVAL_GATE"
        allowed = False
    elif not closed:
        status = "DRIFT_BLOCKED_NO_CLOSED_TRADES"
        reasons.append("Paper runtime exists, but closed paper trades are not detected.")
        next_action = "KEEP_OBSERVING_PAPER_RUNTIME"
        allowed = False
    elif not native_ready:
        status = "DRIFT_BLOCKED_NATIVE_FIELDS_MISSING"
        reasons.append("Closed/paper logs are not native-field ready; drift validation would be unreliable.")
        next_action = "PATCH_OR_VERIFY_NATIVE_LOGGING_FIELDS"
        allowed = False
    elif any(c.key == "control_tower_safe" for c in failed):
        status = "DRIFT_BLOCKED_CONTROL_TOWER_NOT_SAFE"
        reasons.append("Control Tower v3 is not in a safe state.")
        next_action = "REPAIR_CONTROL_TOWER_STATE"
        allowed = False
    elif drift_already:
        status = "DRIFT_ALREADY_RAN_REVIEW_REQUIRED"
        reasons.append("A drift monitor artifact already exists; review latest drift report before rerunning.")
        warnings.append("Rerun may be useful after more paper trades, but should be deliberate.")
        next_action = "REVIEW_LATEST_DRIFT_REPORT_OR_WAIT_FOR_MORE_PAPER_TRADES"
        allowed = False
    elif failed:
        status = "DRIFT_BLOCKED_REQUIRED_CHECK_FAILED"
        reasons.append("One or more required drift gate checks failed.")
        next_action = "FIX_DRIFT_GATE_BLOCKERS"
        allowed = False
    else:
        status = "DRIFT_READY_REFERENCE_ONLY"
        reasons.append("Paper closed trade sample and native logging evidence are ready for drift validation.")
        warnings.append("This module does not execute the drift monitor; it only writes a reference command.")
        next_action = "HUMAN_MAY_RUN_DRIFT_MONITOR_REFERENCE_COMMAND"
        allowed = True

    return DriftGateDecision(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        gate_status=status,
        drift_reference_allowed=allowed,
        drift_monitor_already_exists=drift_already,
        paper_started=paper_started,
        closed_paper_trades_detected=closed,
        native_logging_ready=native_ready,
        live_allowed=False,
        next_os_action=next_action,
        blockers=blockers,
        warnings=warnings,
        reasons=reasons,
        drift_script_path=str(DEFAULT_DRIFT_SCRIPT),
        paper_dir=str(DEFAULT_PAPER_DIR),
        hard_rules=[
            "Drift gate never starts paper/live.",
            "Drift gate never executes the drift monitor by itself.",
            "Live remains blocked regardless of drift readiness.",
            "Drift requires closed paper trades and native/partial execution fields.",
            "Drift pass would still require manual review before any live discussion.",
        ],
    )


def checks_df(checks: List[GateCheck]) -> pd.DataFrame:
    return pd.DataFrame([asdict(c) for c in checks])


def evidence_df(evidence: Dict[str, Evidence]) -> pd.DataFrame:
    return pd.DataFrame([asdict(e) for e in evidence.values()])


def write_reference_ps1(path: Path, decision: DriftGateDecision) -> None:
    lines: List[str] = []
    lines.append("# EDGE FACTORY DRIFT MONITOR - REFERENCE ONLY")
    lines.append(f"# Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"# drift_gate_status: {decision.gate_status}")
    lines.append("# This file is intentionally commented out.")
    lines.append("# The drift gate did NOT run this command.")
    lines.append("# Live remains blocked.")
    lines.append("")
    cmd = f'python "{DEFAULT_DRIFT_SCRIPT}" --base_dir "{DEFAULT_PAPER_DIR}" --workspace "{DEFAULT_WORKSPACE}"'
    if decision.drift_reference_allowed:
        lines.append("# Drift monitor reference command:")
        lines.append(f"# {cmd}")
    else:
        lines.append("# Drift monitor is blocked by current gate decision.")
        lines.append(f"# {cmd}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, decision: DriftGateDecision, checks: List[GateCheck], evidence: Dict[str, Evidence]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Drift Gate Report")
    lines.append("")
    lines.append(f"Generated: `{decision.generated_at}`")
    lines.append(f"Gate status: **{decision.gate_status}**")
    lines.append(f"Drift reference allowed: **{decision.drift_reference_allowed}**")
    lines.append(f"Paper started: **{decision.paper_started}**")
    lines.append(f"Closed paper trades: **{decision.closed_paper_trades_detected}**")
    lines.append(f"Native logging ready: **{decision.native_logging_ready}**")
    lines.append(f"Live allowed: **{decision.live_allowed}**")
    lines.append(f"Next OS action: **{decision.next_os_action}**")
    lines.append("")

    lines.append("## Reasons")
    lines.append("")
    for r in decision.reasons:
        lines.append(f"- {r}")
    lines.append("")

    if decision.blockers:
        lines.append("## Blockers")
        lines.append("")
        for b in decision.blockers:
            lines.append(f"- `{b}`")
        lines.append("")

    if decision.warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in decision.warnings:
            lines.append(f"- {w}")
        lines.append("")

    lines.append("## Checklist")
    lines.append("")
    lines.append("| Category | Check | Required | Passed | Evidence |")
    lines.append("|---|---|---:|---:|---|")
    for c in checks:
        lines.append(f"| {c.category} | {c.description} | {c.required} | {c.passed} | `{c.evidence}` |")
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
    for r in decision.hard_rules:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    if decision.gate_status == "DRIFT_BLOCKED_PAPER_NOT_STARTED":
        lines.append("Paper has not started; drift validation is correctly blocked.")
    elif decision.gate_status == "DRIFT_READY_REFERENCE_ONLY":
        lines.append("Drift validation is ready as a manual/offline reference step. This module did not execute it, and live remains blocked.")
    else:
        lines.append("Drift validation is not currently ready. Fix blockers or keep observing paper runtime.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS drift gate controller")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_drift_gate_controller"
    out_dir = out_root / f"drift_gate_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    evidence = collect_evidence(workspace)
    data = data_from_evidence(evidence)
    checks = build_checks(evidence, data)
    decision = decide(evidence, data, checks)

    write_json(out_dir / "os_drift_gate_decision.json", {"decision": asdict(decision), "checks": [asdict(c) for c in checks], "evidence": {k: asdict(v) for k, v in evidence.items()}})
    checks_df(checks).to_csv(out_dir / "os_drift_gate_checklist.csv", index=False)
    evidence_df(evidence).to_csv(out_dir / "os_drift_gate_evidence.csv", index=False)
    write_reference_ps1(out_dir / "drift_monitor_REFERENCE_ONLY.ps1", decision)
    write_report(out_dir / "os_drift_gate_report.md", decision, checks, evidence)

    print("EDGE FACTORY OS DRIFT GATE CONTROLLER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"gate_status: {decision.gate_status}")
    print(f"drift_reference_allowed: {decision.drift_reference_allowed}")
    print(f"paper_started: {decision.paper_started}")
    print(f"closed_paper_trades_detected: {decision.closed_paper_trades_detected}")
    print(f"native_logging_ready: {decision.native_logging_ready}")
    print("live_allowed: False")
    print(f"next_os_action: {decision.next_os_action}")
    print("")
    print("REASONS")
    print("-" * 100)
    for r in decision.reasons:
        print(f"- {r}")
    if decision.blockers:
        print("")
        print("BLOCKERS")
        print("-" * 100)
        for b in decision.blockers:
            print(f"- {b}")
    print("")
    print("CHECKS")
    print("-" * 100)
    for c in checks:
        print(f"{c.key:36s} required={str(c.required):5s} passed={str(c.passed):5s} category={c.category}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not run the drift monitor, did not start paper/live, and did not mutate config.")
    print("")
    print(f"Report   : {out_dir / 'os_drift_gate_report.md'}")
    print(f"Decision : {out_dir / 'os_drift_gate_decision.json'}")
    print(f"Reference: {out_dir / 'drift_monitor_REFERENCE_ONLY.ps1'}")
    return 0 if not decision.gate_status.startswith("DRIFT_BLOCKED_CONTROL") else 2


if __name__ == "__main__":
    raise SystemExit(main())
