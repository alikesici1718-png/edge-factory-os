#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS PAPER START GATE v1
===================================

Purpose
-------
Final pre-paper gate for the self-improving Edge Factory OS.

This module reads the latest:
    - Control Tower state
    - Transition Controller state
    - Manual Approval Packet
    - Manual Approval Recorder
    - Semantic Dependency/Staleness v2
    - Paper Boot Plan
    - Preflight decision

Then emits one final paper-start gate decision:
    PAPER_START_BLOCKED_NO_MANUAL_APPROVAL
    PAPER_START_BLOCKED_APPROVAL_EXPIRED
    PAPER_START_BLOCKED_CONTROL_PLANE_NOT_CURRENT
    PAPER_START_BLOCKED_TRANSITION_NOT_READY
    PAPER_START_BLOCKED_DEPENDENCY_STALE
    PAPER_START_REFERENCE_ALLOWED_MANUAL_ONLY
    PAPER_ALREADY_STARTED_MONITORING_REQUIRED

It does NOT start paper.
It does NOT start live.
It does NOT execute PowerShell.
It does NOT run start_edge_factory_MASTER_UPPER_SYSTEM.ps1.
It does NOT run --apply.
It does NOT mutate active config.

Run:
    python "C:\Users\alike\edge_factory_os_paper_start_gate.py"

Outputs:
    <workspace>\edge_factory_os_paper_start_gate\paper_start_gate_YYYYMMDD_HHMMSS\
        os_paper_start_gate_report.md
        os_paper_start_gate_decision.json
        os_paper_start_gate_checklist.csv
        paper_start_REFERENCE_ONLY.ps1
        paper_start_gate_evidence.csv

Core rule
---------
Even if the gate says PAPER_START_REFERENCE_ALLOWED_MANUAL_ONLY, the command is still
written commented-out. A human must manually start supervised paper outside this module.
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
DEFAULT_LAUNCHER = DEFAULT_SCRIPT_DIR / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1"
DEFAULT_PAPER_DIR = DEFAULT_WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

ARTIFACTS = {
    "control_tower": ("edge_factory_os_control_tower", "control_tower_", "os_control_tower_state.json"),
    "transition_controller": ("edge_factory_os_transition_controller", "transition_", "os_transition_state.json"),
    "manual_approval_packet": ("edge_factory_os_manual_approval_packet", "approval_packet_", "os_manual_approval_packet.json"),
    "manual_approval_record": ("edge_factory_os_manual_approval_recorder", "manual_approval_", "os_manual_approval_record.json"),
    "dependency_staleness_v2": ("edge_factory_os_dependency_staleness_v2", "dependency_staleness_v2_", "os_dependency_staleness_v2.json"),
    "paper_boot_plan": ("edge_factory_paper_boot_plan", "paper_boot_plan_", "paper_boot_plan.json"),
    "preflight": ("edge_factory_os_preflight", "preflight_", "paper_boot_decision.json"),
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
    required: bool
    passed: bool
    category: str
    description: str
    evidence: str


@dataclass
class GateDecision:
    generated_at: str
    gate_status: str
    paper_start_reference_allowed: bool
    paper_started: bool
    live_allowed: bool
    launcher_path: str
    approval_id: Optional[str]
    approval_status: Optional[str]
    approval_expires_at: Optional[str]
    reasons: List[str]
    blockers: List[str]
    warnings: List[str]
    next_os_action: str
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
    launcher_exists = DEFAULT_LAUNCHER.exists() and DEFAULT_LAUNCHER.is_file()
    out["launcher"] = Evidence(
        key="launcher",
        path=str(DEFAULT_LAUNCHER),
        exists=launcher_exists,
        modified_at=iso_mtime(DEFAULT_LAUNCHER) if launcher_exists else None,
        status="PASS" if launcher_exists else "MISSING",
        message="launcher found" if launcher_exists else "launcher missing",
    )
    return out


def data_from_evidence(evidence: Dict[str, Evidence]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for key, ev in evidence.items():
        out[key] = optional_json(Path(ev.path) if ev.path else None)
    return out


def paper_started(workspace: Path) -> bool:
    p = workspace / "paper_run_gate_MASTER_UPPER_SYSTEM"
    try:
        return p.exists() and any(p.iterdir())
    except Exception:
        return False


def closed_paper_trades_exist(workspace: Path) -> bool:
    p = workspace / "paper_run_gate_MASTER_UPPER_SYSTEM"
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


def parse_dt(x: Any) -> Optional[datetime]:
    try:
        if not x:
            return None
        return datetime.fromisoformat(str(x))
    except Exception:
        return None


def nested(obj: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def build_checks(workspace: Path, evidence: Dict[str, Evidence], data: Dict[str, Dict[str, Any]]) -> List[GateCheck]:
    tower_state = data.get("control_tower", {}).get("state") if isinstance(data.get("control_tower", {}).get("state"), dict) else {}
    transition_decision = data.get("transition_controller", {}).get("decision") if isinstance(data.get("transition_controller", {}).get("decision"), dict) else {}
    approval_record = data.get("manual_approval_record", {})
    packet = data.get("manual_approval_packet", {})
    stale_context = data.get("dependency_staleness_v2", {}).get("context") if isinstance(data.get("dependency_staleness_v2", {}).get("context"), dict) else {}
    preflight = data.get("preflight", {})

    expires = parse_dt(approval_record.get("expires_at"))
    approval_not_expired = bool(expires and expires > datetime.now())

    checks: List[GateCheck] = []

    def add(key: str, required: bool, passed: bool, category: str, description: str, ev: str) -> None:
        checks.append(GateCheck(key, required, passed, category, description, ev))

    add("paper_not_already_started", True, not paper_started(workspace), "runtime", "Paper is not already started.", str(DEFAULT_PAPER_DIR))
    add("control_tower_green", True, str(tower_state.get("tower_state", "")) == "GREEN_CONTROL_PLANE_CURRENT", "control", "Control Tower is green/current.", evidence["control_tower"].path or "missing")
    add("transition_manual_gate", True, str(transition_decision.get("decision", "")) == "READY_FOR_MANUAL_PAPER_APPROVAL_ONLY", "transition", "Transition controller says paper start is manual-gate only.", evidence["transition_controller"].path or "missing")
    add("dependency_chain_current", True, str(stale_context.get("overall_state", "")) == "DEPENDENCY_CHAIN_CURRENT", "dependency", "Semantic dependency chain is current.", evidence["dependency_staleness_v2"].path or "missing")
    add("preflight_ready", True, str(preflight.get("decision", "")).startswith("PAPER_READY") and int(preflight.get("blockers", 0) or 0) == 0, "preflight", "Preflight allows paper with zero blockers.", evidence["preflight"].path or "missing")
    add("approval_packet_ready", True, str(packet.get("approval_status", "")) == "APPROVAL_PACKET_READY_FOR_HUMAN_REVIEW", "approval", "Manual approval packet is ready for human review.", evidence["manual_approval_packet"].path or "missing")
    add("manual_approval_record_granted", True, str(approval_record.get("approval_status", "")) == "MANUAL_PAPER_APPROVED_REFERENCE_ONLY", "approval", "Manual approval record grants supervised paper reference only.", evidence["manual_approval_record"].path or "missing")
    add("approval_not_expired", True, approval_not_expired, "approval", "Manual approval record is not expired.", str(approval_record.get("expires_at")))
    add("approval_paper_only", True, bool(approval_record.get("paper_only_approved", False)), "approval", "Paper-only flag granted.", evidence["manual_approval_record"].path or "missing")
    add("approval_native_logging", True, bool(approval_record.get("native_logging_approved", False)), "approval", "Native logging confirmation granted.", evidence["manual_approval_record"].path or "missing")
    add("approval_no_live", True, bool(approval_record.get("no_live_approved", False)), "approval", "No-live confirmation granted.", evidence["manual_approval_record"].path or "missing")
    add("live_blocked", True, not bool(tower_state.get("live_allowed", False)) and not bool(approval_record.get("live_allowed", False)), "safety", "Live is blocked in tower and approval record.", "control_tower + approval_record")
    add("launcher_exists", True, evidence["launcher"].exists, "launcher", "MASTER_UPPER_SYSTEM launcher exists.", evidence["launcher"].path or "missing")
    add("paper_boot_plan_exists", True, evidence["paper_boot_plan"].exists, "boot_plan", "Paper boot plan exists.", evidence["paper_boot_plan"].path or "missing")
    return checks


def decide_gate(workspace: Path, checks: List[GateCheck], data: Dict[str, Dict[str, Any]]) -> GateDecision:
    approval_record = data.get("manual_approval_record", {})
    blockers: List[str] = []
    warnings: List[str] = []
    reasons: List[str] = []

    failed_required = [c for c in checks if c.required and not c.passed]
    for c in failed_required:
        blockers.append(c.key)

    ps = paper_started(workspace)
    live_allowed = False
    approval_status = str(approval_record.get("approval_status", "UNKNOWN"))
    expires_at = str(approval_record.get("expires_at", "")) if approval_record.get("expires_at") else None
    approval_id = str(approval_record.get("approval_id", "")) if approval_record.get("approval_id") else None

    if ps:
        gate_status = "PAPER_ALREADY_STARTED_MONITORING_REQUIRED"
        reasons.append("Paper directory already appears active; start gate is no longer the correct action.")
        next_action = "RUN_HEALTH_NATIVE_LOGGING_AND_WAIT_FOR_CLOSED_TRADES"
        allowed = False
    elif "manual_approval_record_granted" in blockers:
        gate_status = "PAPER_START_BLOCKED_NO_MANUAL_APPROVAL"
        reasons.append("Manual approval record does not grant supervised paper start reference.")
        next_action = "RECORD_MANUAL_APPROVAL_OR_KEEP_WAITING"
        allowed = False
    elif "approval_not_expired" in blockers:
        gate_status = "PAPER_START_BLOCKED_APPROVAL_EXPIRED"
        reasons.append("Manual approval exists but is expired or invalid.")
        next_action = "REGENERATE_APPROVAL_PACKET_AND_RECORD_APPROVAL"
        allowed = False
    elif "control_tower_green" in blockers:
        gate_status = "PAPER_START_BLOCKED_CONTROL_PLANE_NOT_CURRENT"
        reasons.append("Control Tower is not green/current.")
        next_action = "RUN_CONTROL_TOWER_AND_REPAIR_OS_STATE"
        allowed = False
    elif "transition_manual_gate" in blockers:
        gate_status = "PAPER_START_BLOCKED_TRANSITION_NOT_READY"
        reasons.append("Transition controller is not in manual paper approval state.")
        next_action = "RUN_TRANSITION_CONTROLLER"
        allowed = False
    elif "dependency_chain_current" in blockers:
        gate_status = "PAPER_START_BLOCKED_DEPENDENCY_STALE"
        reasons.append("Semantic dependency chain is not current.")
        next_action = "RUN_SEMANTIC_STALENESS_REBUILD_FLOW"
        allowed = False
    elif failed_required:
        gate_status = "PAPER_START_BLOCKED_REQUIRED_CHECK_FAILED"
        reasons.append("One or more required paper-start checks failed.")
        next_action = "FIX_FAILED_CHECKS"
        allowed = False
    else:
        gate_status = "PAPER_START_REFERENCE_ALLOWED_MANUAL_ONLY"
        reasons.append("All automated and manual approval checks passed. Paper start is allowed only as a manual supervised action.")
        warnings.append("This module did not start paper. Reference command is commented out.")
        warnings.append("Live remains blocked.")
        next_action = "HUMAN_MAY_MANUALLY_START_SUPERVISED_PAPER_USING_REFERENCE_COMMAND"
        allowed = True

    return GateDecision(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        gate_status=gate_status,
        paper_start_reference_allowed=allowed,
        paper_started=ps,
        live_allowed=live_allowed,
        launcher_path=str(DEFAULT_LAUNCHER),
        approval_id=approval_id,
        approval_status=approval_status,
        approval_expires_at=expires_at,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
        next_os_action=next_action,
        hard_rules=[
            "This module does not start paper/live.",
            "Reference command is always commented out.",
            "Live remains blocked.",
            "Manual approval must exist and be unexpired before paper reference is allowed.",
            "If paper is already started, switch to monitoring/drift workflow.",
        ],
    )


def checks_df(checks: List[GateCheck]) -> pd.DataFrame:
    return pd.DataFrame([asdict(c) for c in checks])


def evidence_df(evidence: Dict[str, Evidence]) -> pd.DataFrame:
    return pd.DataFrame([asdict(e) for e in evidence.values()])


def write_reference_ps1(path: Path, decision: GateDecision) -> None:
    lines: List[str] = []
    lines.append("# EDGE FACTORY PAPER START - FINAL GATE REFERENCE ONLY")
    lines.append(f"# Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"# gate_status: {decision.gate_status}")
    lines.append(f"# approval_id: {decision.approval_id}")
    lines.append(f"# approval_expires_at: {decision.approval_expires_at}")
    lines.append("#")
    lines.append("# This file is intentionally commented out.")
    lines.append("# The paper start gate did NOT execute this command.")
    lines.append("# Live remains blocked.")
    lines.append("")
    if decision.paper_start_reference_allowed:
        lines.append("# Manual supervised paper reference command:")
        lines.append(f"# powershell -ExecutionPolicy Bypass -File \"{DEFAULT_LAUNCHER}\"")
    else:
        lines.append("# Paper start is blocked by the current gate decision.")
        lines.append(f"# powershell -ExecutionPolicy Bypass -File \"{DEFAULT_LAUNCHER}\"")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, decision: GateDecision, checks: List[GateCheck]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Paper Start Gate Report")
    lines.append("")
    lines.append(f"Generated: `{decision.generated_at}`")
    lines.append(f"Gate status: **{decision.gate_status}**")
    lines.append(f"Paper reference allowed: **{decision.paper_start_reference_allowed}**")
    lines.append(f"Paper started: **{decision.paper_started}**")
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

    lines.append("## Hard rules")
    lines.append("")
    for r in decision.hard_rules:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    if decision.paper_start_reference_allowed:
        lines.append("The OS gate allows a human to manually start supervised paper using the reference command. The command was not executed. Live remains blocked.")
    else:
        lines.append("The OS gate blocks paper start reference under the current state. Fix blockers or record manual approval first.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS paper start gate")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_paper_start_gate"
    out_dir = out_root / f"paper_start_gate_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    evidence = collect_evidence(workspace)
    data = data_from_evidence(evidence)
    checks = build_checks(workspace, evidence, data)
    decision = decide_gate(workspace, checks, data)

    write_json(out_dir / "os_paper_start_gate_decision.json", {"decision": asdict(decision), "checks": [asdict(c) for c in checks], "evidence": {k: asdict(v) for k, v in evidence.items()}})
    checks_df(checks).to_csv(out_dir / "os_paper_start_gate_checklist.csv", index=False)
    evidence_df(evidence).to_csv(out_dir / "paper_start_gate_evidence.csv", index=False)
    write_reference_ps1(out_dir / "paper_start_REFERENCE_ONLY.ps1", decision)
    write_report(out_dir / "os_paper_start_gate_report.md", decision, checks)

    print("EDGE FACTORY OS PAPER START GATE v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"gate_status: {decision.gate_status}")
    print(f"paper_start_reference_allowed: {decision.paper_start_reference_allowed}")
    print(f"paper_started: {decision.paper_started}")
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
        print(f"{c.key:38s} required={str(c.required):5s} passed={str(c.passed):5s} category={c.category}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live and did not execute the launcher.")
    print("Reference command is commented out only.")
    print("")
    print(f"Report   : {out_dir / 'os_paper_start_gate_report.md'}")
    print(f"Decision : {out_dir / 'os_paper_start_gate_decision.json'}")
    print(f"Reference: {out_dir / 'paper_start_REFERENCE_ONLY.ps1'}")
    return 0 if decision.gate_status != "PAPER_START_BLOCKED_REQUIRED_CHECK_FAILED" else 2



if __name__ == "__main__":
    raise SystemExit(main())
