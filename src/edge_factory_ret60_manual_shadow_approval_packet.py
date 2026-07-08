#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 MANUAL SHADOW APPROVAL PACKET v1
===================================================

Purpose
-------
Create a human/manual approval packet for ret60_reversal_short shadow sandbox start.

This module is the next safe step after:
    edge_factory_ret60_sandbox_preflight_gate.py

It checks that:
    - ret60 sandbox preflight passed
    - implementation audit passed
    - native logging was verified
    - runtime plan exists
    - active paper remains blocked
    - live remains blocked

It DOES NOT:
    - grant approval by itself
    - start shadow paper
    - start active paper
    - start live
    - run logger runtime
    - mutate active config
    - edit MASTER_UPPER_SYSTEM
    - edit position sizing contract
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - write a manual approval packet
    - write a checklist with automated and manual confirmations
    - write a commented reference-only command path
    - keep shadow start blocked until manual approval is explicitly recorded

Run:
    python "C:\Users\alike\edge_factory_ret60_manual_shadow_approval_packet.py"

Core rule
---------
Packet ready is not approval. Approval must be recorded by a separate recorder with explicit flags.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_CANDIDATE = "ret60_reversal_short"


@dataclass
class ApprovalCheck:
    check_id: str
    check_type: str
    required: bool
    passed: bool
    status: str
    reason: str
    evidence: str


@dataclass
class RuntimeReference:
    candidate_key: str
    sandbox_root: Optional[str]
    adapter_path: Optional[str]
    expected_log_csv: Optional[str]
    expected_state_json: Optional[str]
    expected_heartbeat_json: Optional[str]
    expected_closed_trades_csv: Optional[str]
    command_reference_path: Optional[str]
    command_reference_only: bool


@dataclass
class ApprovalPacketState:
    generated_at: str
    workspace: str
    candidate: str
    output_dir: str
    packet_status: str
    preflight_passed: bool
    ready_for_manual_shadow_approval: bool
    automated_required_passed: int
    automated_required_total: int
    manual_required_passed: int
    manual_required_total: int
    manual_approval_granted: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    expires_at: str
    next_action: str
    reasons: List[str]
    blockers: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_key(x: Any) -> str:
    return str(x or "").strip().lower().replace(" ", "_")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def read_json_optional(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def latest_preflight_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_sandbox_preflight_gate", "ret60_sandbox_preflight_")
    if not d:
        return None
    p = d / "ret60_sandbox_preflight_state.json"
    return p if p.exists() else None


def load_preflight(workspace: Path, explicit_state: Optional[str]) -> Dict[str, Any]:
    p = Path(explicit_state) if explicit_state else latest_preflight_state(workspace)
    obj = read_json_optional(p)
    obj["__path"] = str(p) if p else None
    return obj


def bool_field(obj: Dict[str, Any], key: str, default: bool = False) -> bool:
    return bool(obj.get(key, default))


def build_runtime_reference(preflight: Dict[str, Any]) -> RuntimeReference:
    runtime = preflight.get("runtime_plan", {}) if isinstance(preflight.get("runtime_plan"), dict) else {}
    return RuntimeReference(
        candidate_key=str(runtime.get("candidate_key") or DEFAULT_CANDIDATE),
        sandbox_root=runtime.get("sandbox_root"),
        adapter_path=runtime.get("adapter_path"),
        expected_log_csv=runtime.get("expected_log_csv"),
        expected_state_json=runtime.get("expected_state_json"),
        expected_heartbeat_json=runtime.get("expected_heartbeat_json"),
        expected_closed_trades_csv=runtime.get("expected_closed_trades_csv"),
        command_reference_path=None,
        command_reference_only=bool(runtime.get("command_is_reference_only", True)),
    )


def build_checks(preflight_obj: Dict[str, Any]) -> List[ApprovalCheck]:
    checks: List[ApprovalCheck] = []
    state = preflight_obj.get("state", {}) if isinstance(preflight_obj.get("state"), dict) else {}
    runtime = preflight_obj.get("runtime_plan", {}) if isinstance(preflight_obj.get("runtime_plan"), dict) else {}
    native = preflight_obj.get("native_check", {}) if isinstance(preflight_obj.get("native_check"), dict) else {}
    preflight_path = preflight_obj.get("__path")

    def add(cid: str, ctype: str, required: bool, passed: bool, reason: str, evidence: str = "") -> None:
        checks.append(ApprovalCheck(
            check_id=cid,
            check_type=ctype,
            required=required,
            passed=bool(passed),
            status="PASS" if passed else "PENDING" if ctype == "MANUAL" else "FAIL",
            reason=reason,
            evidence=evidence,
        ))

    add("preflight_state_exists", "AUTO", True, bool(preflight_path and Path(str(preflight_path)).exists()), "ret60 preflight state must exist", str(preflight_path))
    add("preflight_passed", "AUTO", True, bool_field(state, "preflight_passed"), "ret60 sandbox preflight must pass", state.get("preflight_status", ""))
    add("ready_for_manual_shadow_approval", "AUTO", True, bool_field(state, "ready_for_manual_shadow_approval"), "preflight must be ready for manual shadow approval", "")
    add("implementation_audit_passed", "AUTO", True, bool_field(state, "implementation_audit_passed"), "implementation audit must have passed", "")
    add("native_log_verified", "AUTO", True, bool_field(state, "native_log_verified"), "native log must be verified", json.dumps(native, ensure_ascii=False, default=str)[:500])
    add("runtime_plan_created", "AUTO", True, bool_field(state, "runtime_plan_created"), "runtime plan must be created", "")
    add("adapter_path_exists", "AUTO", True, bool(runtime.get("adapter_path") and Path(str(runtime.get("adapter_path"))).exists()), "adapter path must exist", str(runtime.get("adapter_path")))
    add("expected_log_path_defined", "AUTO", True, bool(runtime.get("expected_log_csv")), "expected native log path must be defined", str(runtime.get("expected_log_csv")))
    add("reference_command_only", "AUTO", True, bool(runtime.get("command_is_reference_only", True)), "preflight command must be reference-only", "")
    add("shadow_start_currently_blocked", "AUTO", True, not bool_field(state, "shadow_start_allowed"), "shadow start must still be blocked before manual approval", "")
    add("active_paper_blocked", "AUTO", True, not bool_field(state, "active_paper_allowed"), "active paper must be blocked", "")
    add("live_blocked", "AUTO", True, not bool_field(state, "live_allowed"), "live must be blocked", "")

    add("manual_confirm_shadow_only", "MANUAL", True, False, "Human must confirm this approval is for ret60 shadow sandbox only, not active paper/live.", "")
    add("manual_confirm_no_live_no_active", "MANUAL", True, False, "Human must confirm no live trading and no active paper portfolio inclusion.", "")
    add("manual_confirm_native_logging", "MANUAL", True, False, "Human must confirm native logging fields are required during shadow runtime.", "")
    add("manual_confirm_runtime_supervised", "MANUAL", True, False, "Human must confirm shadow runtime must be supervised and can be stopped manually.", "")
    add("manual_confirm_do_not_modify_master", "MANUAL", True, False, "Human must confirm MASTER_UPPER_SYSTEM and sizing contract will not be modified.", "")
    return checks


def summarize_packet(workspace: Path, out_dir: Path, preflight: Dict[str, Any], checks: List[ApprovalCheck], runtime_ref: RuntimeReference) -> ApprovalPacketState:
    auto_req = [c for c in checks if c.check_type == "AUTO" and c.required]
    auto_pass = [c for c in auto_req if c.passed]
    manual_req = [c for c in checks if c.check_type == "MANUAL" and c.required]
    manual_pass = [c for c in manual_req if c.passed]

    blockers: List[str] = []
    warnings: List[str] = []
    reasons: List[str] = []

    auto_ok = len(auto_pass) == len(auto_req)
    if auto_ok:
        status = "RET60_MANUAL_SHADOW_APPROVAL_PACKET_READY_FOR_HUMAN_REVIEW"
        next_action = "RECORD_RET60_MANUAL_SHADOW_APPROVAL_WITH_EXPLICIT_FLAGS"
        reasons.append("all automated prerequisites passed")
        reasons.append("manual confirmations are still required before shadow start")
    else:
        status = "RET60_MANUAL_SHADOW_APPROVAL_PACKET_BLOCKED"
        next_action = "REPAIR_FAILED_AUTOMATED_APPROVAL_CHECKS"
        blockers.extend([f"{c.check_id}: {c.reason}" for c in auto_req if not c.passed])

    expires_at = (datetime.now() + timedelta(hours=24)).isoformat(timespec="seconds")
    if manual_req:
        warnings.append("manual approval is not granted by this packet; manual checks remain pending")

    return ApprovalPacketState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        candidate=DEFAULT_CANDIDATE,
        output_dir=str(out_dir),
        packet_status=status,
        preflight_passed=bool(preflight.get("state", {}).get("preflight_passed", False)) if isinstance(preflight.get("state"), dict) else False,
        ready_for_manual_shadow_approval=auto_ok,
        automated_required_passed=len(auto_pass),
        automated_required_total=len(auto_req),
        manual_required_passed=len(manual_pass),
        manual_required_total=len(manual_req),
        manual_approval_granted=False,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        expires_at=expires_at,
        next_action=next_action,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
        hard_rules=[
            "Manual approval packet never grants approval by itself.",
            "Manual approval packet never starts shadow/active paper/live.",
            "Manual approval packet never runs logger runtime.",
            "Manual approval packet never mutates active config.",
            "Manual approval packet never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Manual approval must be recorded by a separate recorder with explicit flags.",
            "Live remains blocked.",
        ],
    )


def records_df(items: List[Any]) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in items])


def write_outputs(out_dir: Path, state: ApprovalPacketState, checks: List[ApprovalCheck], runtime_ref: RuntimeReference, preflight: Dict[str, Any]) -> None:
    runtime_ref.command_reference_path = str(out_dir / "ret60_shadow_start_REFERENCE_ONLY.ps1")

    payload = {
        "state": asdict(state),
        "checks": [asdict(c) for c in checks],
        "runtime_reference": asdict(runtime_ref),
        "preflight_state_path": preflight.get("__path"),
    }
    write_json(out_dir / "ret60_manual_shadow_approval_packet.json", payload)
    records_df(checks).to_csv(out_dir / "ret60_manual_shadow_approval_checklist.csv", index=False)

    reference = f'''# REFERENCE ONLY - DO NOT RUN FROM THIS PACKET
# Candidate: {DEFAULT_CANDIDATE}
# This packet does not grant approval and does not start shadow runtime.
# Shadow start command must be generated later by a shadow start gate after manual approval is recorded.
# Adapter path: {runtime_ref.adapter_path}
# Sandbox root: {runtime_ref.sandbox_root}
# Expected log CSV: {runtime_ref.expected_log_csv}
'''
    write_text(out_dir / "ret60_shadow_start_REFERENCE_ONLY.ps1", reference)

    md = f"""# Ret60 Manual Shadow Approval Packet

Status: **{state.packet_status}**

- Automated checks: `{state.automated_required_passed}/{state.automated_required_total}`
- Manual checks: `{state.manual_required_passed}/{state.manual_required_total}`
- Manual approval granted: `False`
- Shadow start allowed: `False`
- Active paper allowed: `False`
- Live allowed: `False`
- Expires at: `{state.expires_at}`

## Runtime reference

- Sandbox root: `{runtime_ref.sandbox_root}`
- Adapter path: `{runtime_ref.adapter_path}`
- Expected log CSV: `{runtime_ref.expected_log_csv}`

## Manual confirmations still required

```text
{chr(10).join(c.check_id for c in checks if c.check_type == 'MANUAL' and c.required and not c.passed)}
```

## Next action

`{state.next_action}`

## Important

This packet does not approve or start anything. Approval must be recorded separately with explicit flags.
"""
    write_text(out_dir / "ret60_manual_shadow_approval_packet.md", md)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Create ret60 manual shadow approval packet")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--preflight_state", default=None)
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_manual_shadow_approval_packet"
    out_dir = out_root / f"ret60_approval_packet_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    preflight = load_preflight(workspace, args.preflight_state)
    runtime_ref = build_runtime_reference(preflight)
    checks = build_checks(preflight)
    state = summarize_packet(workspace, out_dir, preflight, checks, runtime_ref)
    write_outputs(out_dir, state, checks, runtime_ref, preflight)

    print("EDGE FACTORY RET60 MANUAL SHADOW APPROVAL PACKET v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"candidate : {DEFAULT_CANDIDATE}")
    print(f"output_dir: {out_dir}")
    print(f"packet_status: {state.packet_status}")
    print(f"preflight_passed: {state.preflight_passed}")
    print(f"ready_for_manual_shadow_approval: {state.ready_for_manual_shadow_approval}")
    print(f"automated_required: {state.automated_required_passed}/{state.automated_required_total}")
    print(f"manual_required: {state.manual_required_passed}/{state.manual_required_total}")
    print("manual_approval_granted: False")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print(f"expires_at: {state.expires_at}")
    print("")
    print("MANUAL CHECKS")
    print("-" * 100)
    for c in checks:
        if c.check_type == "MANUAL":
            print(f"{c.check_id:40s} required={c.required} passed={c.passed} status={c.status} reason={c.reason}")
    if state.blockers:
        print("")
        print("BLOCKERS")
        print("-" * 100)
        for b in state.blockers:
            print(f"- {b}")
    if state.warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in state.warnings:
            print(f"- {w}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not grant approval, did not start shadow/active paper/live, and did not mutate active config.")
    print("")
    print(f"Report   : {out_dir / 'ret60_manual_shadow_approval_packet.md'}")
    print(f"Packet   : {out_dir / 'ret60_manual_shadow_approval_packet.json'}")
    print(f"Checklist: {out_dir / 'ret60_manual_shadow_approval_checklist.csv'}")
    print(f"Reference: {out_dir / 'ret60_shadow_start_REFERENCE_ONLY.ps1'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
