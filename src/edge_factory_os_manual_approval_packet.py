#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS MANUAL APPROVAL PACKET v1
=========================================

Purpose
-------
Manual approval dossier generator for the self-improving Edge Factory OS.

The transition controller can say:
    READY_FOR_MANUAL_PAPER_APPROVAL_ONLY
    current = CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED
    next    = PAPER_START_MANUAL_APPROVAL_REQUIRED

This module prepares the evidence packet needed before a human manually starts supervised paper.

It does NOT start paper/live.
It does NOT execute launch commands.
It does NOT run PowerShell launchers.
It does NOT mutate active config.
It does NOT run --apply.

It reads latest artifacts:
    - control tower state
    - transition controller state
    - paper boot plan
    - preflight decision
    - kill-switch policy
    - native bps validation
    - semantic staleness v2
    - decision ledger snapshot/diff
    - sizing contract

Then emits:
    - approval packet markdown
    - approval checklist json/csv
    - explicit blocked live statement
    - paper-start command reference, commented out only

Run:
    python "C:\Users\alike\edge_factory_os_manual_approval_packet.py"

Outputs:
    <workspace>\edge_factory_os_manual_approval_packet\approval_packet_YYYYMMDD_HHMMSS\
        os_manual_approval_packet.md
        os_manual_approval_packet.json
        os_manual_approval_checklist.csv
        paper_start_command_REFERENCE_ONLY.ps1
        approval_evidence_inventory.csv

Core rule
---------
This module can say "manual approval packet is complete".
It can never start paper or live by itself.
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
DEFAULT_CONTRACT = DEFAULT_WORKSPACE / "edge_factory_position_sizing_contract" / "position_sizing_contract.json"

ARTIFACT_SPECS = {
    "control_tower": ("edge_factory_os_control_tower", "control_tower_", "os_control_tower_state.json"),
    "transition_controller": ("edge_factory_os_transition_controller", "transition_", "os_transition_state.json"),
    "paper_boot_plan": ("edge_factory_paper_boot_plan", "paper_boot_plan_", "paper_boot_plan.json"),
    "preflight": ("edge_factory_os_preflight", "preflight_", "paper_boot_decision.json"),
    "kill_switch": ("edge_factory_kill_switch_controller", "kill_switch_", "kill_switch_policy.json"),
    "native_bps": ("edge_factory_native_bps_validator", "native_bps_", "native_bps_validation.json"),
    "dependency_staleness_v2": ("edge_factory_os_dependency_staleness_v2", "dependency_staleness_v2_", "os_dependency_staleness_v2.json"),
    "decision_ledger_diff": ("edge_factory_os_decision_ledger", "ledger_run_", "os_decision_ledger_diff.json"),
    "decision_ledger_snapshot": ("edge_factory_os_decision_ledger", "ledger_run_", "os_decision_ledger_snapshot.json"),
    "autopilot_loop": ("edge_factory_os_autopilot_loop", "autopilot_loop_", "os_autopilot_loop_state.json"),
}

REQUIRED_NATIVE_FIELDS = [
    "family_key",
    "symbol",
    "side",
    "entry_time",
    "exit_time",
    "entry_price",
    "exit_price",
    "qty",
    "notional_usdt",
    "gross_pnl_usdt",
    "fee_usdt",
    "net_pnl_usdt",
    "gross_bps",
    "net_bps",
    "spread_bps_at_entry",
    "spread_bps_at_exit",
    "slippage_bps_est",
    "hold_seconds",
    "exit_reason",
    "strategy_signal_id",
]


@dataclass
class EvidenceItem:
    key: str
    path: Optional[str]
    exists: bool
    status: str
    message: str
    modified_at: Optional[str]


@dataclass
class ChecklistItem:
    item_key: str
    category: str
    required: bool
    passed: bool
    manual_confirm_required: bool
    description: str
    evidence: str


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
    root_name, prefix, filename = ARTIFACT_SPECS[key]
    d = latest_child_dir(workspace / root_name, prefix)
    if not d:
        return None
    p = d / filename
    return p if p.exists() else None


def collect_evidence(workspace: Path) -> Dict[str, EvidenceItem]:
    out: Dict[str, EvidenceItem] = {}
    for key in ARTIFACT_SPECS:
        p = artifact_path(workspace, key)
        exists = bool(p and p.exists())
        out[key] = EvidenceItem(
            key=key,
            path=str(p) if p else None,
            exists=exists,
            status="PASS" if exists else "MISSING",
            message="artifact found" if exists else "artifact missing",
            modified_at=iso_mtime(p) if exists and p else None,
        )
    # Core files.
    for key, p in {
        "launcher": DEFAULT_LAUNCHER,
        "sizing_contract": DEFAULT_CONTRACT,
    }.items():
        exists = p.exists() and p.is_file()
        out[key] = EvidenceItem(
            key=key,
            path=str(p),
            exists=exists,
            status="PASS" if exists else "MISSING",
            message="core file found" if exists else "core file missing",
            modified_at=iso_mtime(p) if exists else None,
        )
    return out


def data_from_evidence(evidence: Dict[str, EvidenceItem]) -> Dict[str, Dict[str, Any]]:
    data: Dict[str, Dict[str, Any]] = {}
    for key, ev in evidence.items():
        p = Path(ev.path) if ev.path else None
        data[key] = optional_json(p)
    return data


def nested(obj: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def contract_notional_map(contract: Dict[str, Any]) -> Dict[str, Any]:
    # Contract schema varied across generated code. This does best-effort extraction.
    if not isinstance(contract, dict):
        return {}
    for key in ["family_notional_usdt", "notional_by_family", "families", "family_sizing"]:
        val = contract.get(key)
        if isinstance(val, dict):
            return val
    # If top-level family keys exist, collect numeric/dict values.
    fams = {}
    for fam in ["old_short", "impulse_long", "market_relative_short", "weak_market_short", "session_short"]:
        if fam in contract:
            fams[fam] = contract[fam]
    return fams


def build_checklist(workspace: Path, evidence: Dict[str, EvidenceItem], data: Dict[str, Dict[str, Any]]) -> List[ChecklistItem]:
    items: List[ChecklistItem] = []

    transition = data.get("transition_controller", {})
    transition_decision = transition.get("decision") if isinstance(transition.get("decision"), dict) else {}
    tower = data.get("control_tower", {})
    tower_state = tower.get("state") if isinstance(tower.get("state"), dict) else {}
    preflight = data.get("preflight", {})
    stale = data.get("dependency_staleness_v2", {})
    stale_context = stale.get("context") if isinstance(stale.get("context"), dict) else {}
    ledger_diff = data.get("decision_ledger_diff", {})
    native = data.get("native_bps", {})
    native_context = native.get("context") if isinstance(native.get("context"), dict) else {}
    paper_plan = data.get("paper_boot_plan", {})

    def add(key: str, cat: str, required: bool, passed: bool, manual: bool, desc: str, ev: str) -> None:
        items.append(ChecklistItem(key, cat, required, passed, manual, desc, ev))

    add(
        "transition_ready_for_manual_paper",
        "transition",
        True,
        str(transition_decision.get("decision", "")) == "READY_FOR_MANUAL_PAPER_APPROVAL_ONLY",
        False,
        "Transition controller says next step is manual paper approval only.",
        evidence.get("transition_controller", EvidenceItem("", None, False, "", "", None)).path or "missing",
    )
    add(
        "tower_green",
        "control_tower",
        True,
        str(tower_state.get("tower_state", "")) == "GREEN_CONTROL_PLANE_CURRENT",
        False,
        "Control Tower is green/current.",
        evidence.get("control_tower", EvidenceItem("", None, False, "", "", None)).path or "missing",
    )
    add(
        "dependency_chain_current",
        "dependency",
        True,
        str(stale_context.get("overall_state", "")) == "DEPENDENCY_CHAIN_CURRENT",
        False,
        "Semantic dependency chain is current.",
        evidence.get("dependency_staleness_v2", EvidenceItem("", None, False, "", "", None)).path or "missing",
    )
    add(
        "preflight_ready_with_no_blockers",
        "preflight",
        True,
        str(preflight.get("decision", "")).startswith("PAPER_READY") and int(preflight.get("blockers", 0) or 0) == 0,
        False,
        "Preflight allows paper with zero blockers.",
        evidence.get("preflight", EvidenceItem("", None, False, "", "", None)).path or "missing",
    )
    add(
        "live_blocked",
        "safety",
        True,
        bool(tower_state.get("live_allowed", False)) is False and "LIVE_BLOCKED" in str(tower_state.get("autopilot_final_os_mode", "") + " " + str(tower_state.get("live_gate", "")) + " " + str(preflight.get("live_gate", ""))),
        False,
        "Live is blocked. This approval packet is paper-only.",
        "control tower + preflight",
    )
    add(
        "ledger_no_alerts",
        "memory",
        True,
        not bool(ledger_diff.get("alerts")),
        False,
        "Decision ledger has no regression/unsafe alerts.",
        evidence.get("decision_ledger_diff", EvidenceItem("", None, False, "", "", None)).path or "missing",
    )
    add(
        "native_bps_paper_allowed",
        "data_quality",
        True,
        str(native_context.get("paper_quality_gate", "")).startswith("PAPER_ALLOWED"),
        False,
        "Native/BPS data quality is sufficient for paper, not live.",
        evidence.get("native_bps", EvidenceItem("", None, False, "", "", None)).path or "missing",
    )
    add(
        "paper_boot_plan_exists",
        "boot_plan",
        True,
        evidence.get("paper_boot_plan", EvidenceItem("", None, False, "", "", None)).exists,
        False,
        "Paper boot plan artifact exists.",
        evidence.get("paper_boot_plan", EvidenceItem("", None, False, "", "", None)).path or "missing",
    )
    add(
        "kill_switch_exists",
        "safety",
        True,
        evidence.get("kill_switch", EvidenceItem("", None, False, "", "", None)).exists,
        False,
        "Kill-switch policy exists.",
        evidence.get("kill_switch", EvidenceItem("", None, False, "", "", None)).path or "missing",
    )
    add(
        "sizing_contract_exists",
        "config",
        True,
        evidence.get("sizing_contract", EvidenceItem("", None, False, "", "", None)).exists,
        False,
        "Position sizing contract exists.",
        evidence.get("sizing_contract", EvidenceItem("", None, False, "", "", None)).path or "missing",
    )
    add(
        "launcher_exists",
        "boot_plan",
        True,
        evidence.get("launcher", EvidenceItem("", None, False, "", "", None)).exists,
        False,
        "MASTER_UPPER_SYSTEM launcher exists, but must be run manually only if approved.",
        evidence.get("launcher", EvidenceItem("", None, False, "", "", None)).path or "missing",
    )
    add(
        "manual_confirm_paper_only",
        "manual_approval",
        True,
        False,
        True,
        "Human must confirm this is supervised paper only, not real live execution.",
        "manual checkbox",
    )
    add(
        "manual_confirm_native_logging",
        "manual_approval",
        True,
        False,
        True,
        "Human must confirm paper logs will be checked for native execution fields after start.",
        "manual checkbox",
    )
    add(
        "manual_confirm_no_live",
        "manual_approval",
        True,
        False,
        True,
        "Human must confirm live trading remains blocked regardless of paper approval.",
        "manual checkbox",
    )
    return items


def approval_status(items: List[ChecklistItem]) -> Tuple[str, List[str]]:
    failed_required = [x for x in items if x.required and not x.passed and not x.manual_confirm_required]
    manual_required = [x for x in items if x.manual_confirm_required]
    reasons: List[str] = []
    if failed_required:
        reasons.extend([f"failed required check: {x.item_key}" for x in failed_required])
        return "APPROVAL_PACKET_BLOCKED", reasons
    if manual_required:
        reasons.append("all automated checks passed, but manual confirmations are still required")
        return "APPROVAL_PACKET_READY_FOR_HUMAN_REVIEW", reasons
    reasons.append("all automated and manual checks passed")
    return "APPROVAL_PACKET_COMPLETE", reasons


def evidence_df(evidence: Dict[str, EvidenceItem]) -> pd.DataFrame:
    return pd.DataFrame([asdict(v) for v in evidence.values()])


def checklist_df(items: List[ChecklistItem]) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in items])


def write_reference_ps1(path: Path) -> None:
    lines = []
    lines.append("# EDGE FACTORY PAPER START COMMAND - REFERENCE ONLY")
    lines.append(f"# Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("# This file is intentionally commented out.")
    lines.append("# The approval packet generator does NOT start paper.")
    lines.append("# Run manually only after human approval and only for supervised paper mode.")
    lines.append("")
    lines.append(f"# powershell -ExecutionPolicy Bypass -File \"{DEFAULT_LAUNCHER}\"")
    lines.append("")
    lines.append("# After manual paper start, run health checks and verify native log fields.")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, status: str, reasons: List[str], items: List[ChecklistItem], evidence: Dict[str, EvidenceItem], data: Dict[str, Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Manual Approval Packet")
    lines.append("")
    lines.append(f"Generated: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"Approval status: **{status}**")
    lines.append("")
    lines.append("## Status reasons")
    lines.append("")
    for r in reasons:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Non-negotiable limits")
    lines.append("")
    lines.append("- This packet is for supervised **paper** approval only.")
    lines.append("- It does not start paper.")
    lines.append("- It does not allow live.")
    lines.append("- It does not run `--apply`.")
    lines.append("- It does not mutate active config.")
    lines.append("- Live remains blocked until paper drift validation and manual live review.")
    lines.append("")

    lines.append("## Required native paper log fields")
    lines.append("")
    for f in REQUIRED_NATIVE_FIELDS:
        lines.append(f"- `{f}`")
    lines.append("")

    lines.append("## Approval checklist")
    lines.append("")
    lines.append("| Category | Check | Required | Auto passed | Manual confirm | Evidence |")
    lines.append("|---|---|---:|---:|---:|---|")
    for item in items:
        box = "[ ]" if item.manual_confirm_required else ""
        lines.append(f"| {item.category} | {box} {item.description} | {item.required} | {item.passed} | {item.manual_confirm_required} | `{item.evidence}` |")
    lines.append("")

    lines.append("## Evidence inventory")
    lines.append("")
    lines.append("| Key | Status | Path | Modified |")
    lines.append("|---|---:|---|---:|")
    for ev in evidence.values():
        lines.append(f"| {ev.key} | {ev.status} | `{ev.path}` | {ev.modified_at} |")
    lines.append("")

    lines.append("## Paper start command reference")
    lines.append("")
    lines.append("The reference command is written commented-out to `paper_start_command_REFERENCE_ONLY.ps1`. This module did not execute it.")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This packet is the formal manual gate between green control plane and supervised paper start. The OS can prepare evidence; a human must approve and manually start paper if desired.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS manual approval packet")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_manual_approval_packet"
    out_dir = out_root / f"approval_packet_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    evidence = collect_evidence(workspace)
    data = data_from_evidence(evidence)
    items = build_checklist(workspace, evidence, data)
    status, reasons = approval_status(items)

    packet = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "approval_status": status,
        "status_reasons": reasons,
        "checklist": [asdict(x) for x in items],
        "evidence": {k: asdict(v) for k, v in evidence.items()},
        "required_native_fields": REQUIRED_NATIVE_FIELDS,
        "paper_start_reference_command": f'powershell -ExecutionPolicy Bypass -File "{DEFAULT_LAUNCHER}"',
        "hard_rules": [
            "This module does not start paper/live.",
            "This packet is paper-only.",
            "Live remains blocked.",
            "Manual confirmations are required before supervised paper start.",
        ],
    }

    write_json(out_dir / "os_manual_approval_packet.json", packet)
    checklist_df(items).to_csv(out_dir / "os_manual_approval_checklist.csv", index=False)
    evidence_df(evidence).to_csv(out_dir / "approval_evidence_inventory.csv", index=False)
    write_reference_ps1(out_dir / "paper_start_command_REFERENCE_ONLY.ps1")
    write_report(out_dir / "os_manual_approval_packet.md", status, reasons, items, evidence, data)

    print("EDGE FACTORY OS MANUAL APPROVAL PACKET v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"approval_status: {status}")
    print("")
    print("STATUS REASONS")
    print("-" * 100)
    for r in reasons:
        print(f"- {r}")
    print("")
    print("CHECKLIST SUMMARY")
    print("-" * 100)
    for x in items:
        flag = "MANUAL" if x.manual_confirm_required else "AUTO"
        print(f"{x.item_key:38s} {flag:6s} required={str(x.required):5s} passed={str(x.passed):5s}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live and did not execute the launcher.")
    print("Paper start command is written as commented reference only.")
    print("")
    print(f"Report   : {out_dir / 'os_manual_approval_packet.md'}")
    print(f"Packet   : {out_dir / 'os_manual_approval_packet.json'}")
    print(f"Checklist: {out_dir / 'os_manual_approval_checklist.csv'}")
    print(f"Reference: {out_dir / 'paper_start_command_REFERENCE_ONLY.ps1'}")
    return 0 if status != "APPROVAL_PACKET_BLOCKED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
