#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Assembles a human-review approval packet for the rel_extreme_reversion_short shadow run by aggregating preflight gate v2, spec review, and OOS robustness results into a single structured JSON. Outputs the packet to the edge_factory_rel_extreme_manual_shadow_approval_packet_v1 directory for operator sign-off before any shadow runtime is started.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "rel_extreme_reversion_short"

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_rel_extreme_manual_shadow_approval_packet_v1" / f"rel_extreme_approval_packet_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    preflight_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_preflight_gate_v2",
        "rel_extreme_shadow_preflight_v2_",
    )
    spec_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_spec_review_v1",
        "rel_extreme_shadow_spec_",
    )
    robust_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_oos_robustness_v1",
        "rel_extreme_oos_robust_",
    )

    preflight_path = preflight_dir / "rel_extreme_shadow_preflight_gate_v2_state.json" if preflight_dir else None
    spec_path = spec_dir / "rel_extreme_shadow_spec.json" if spec_dir else None
    robust_path = robust_dir / "rel_extreme_oos_robustness_state.json" if robust_dir else None

    preflight = read_json(preflight_path)
    spec = read_json(spec_path)
    robust = read_json(robust_path)

    preflight_passed = preflight.get("preflight_passed") is True
    reference_command = preflight.get("reference_command")

    automated_checks = [
        {
            "check": "preflight_v2_passed",
            "required": True,
            "passed": preflight_passed,
            "reason": preflight.get("status"),
        },
        {
            "check": "preflight_ready_for_manual_shadow_approval",
            "required": True,
            "passed": preflight.get("ready_for_manual_shadow_approval") is True,
            "reason": preflight.get("ready_for_manual_shadow_approval"),
        },
        {
            "check": "preflight_live_false",
            "required": True,
            "passed": preflight.get("live_allowed") is False,
            "reason": preflight.get("live_allowed"),
        },
        {
            "check": "preflight_active_paper_false",
            "required": True,
            "passed": preflight.get("active_paper_allowed") is False,
            "reason": preflight.get("active_paper_allowed"),
        },
        {
            "check": "reference_command_exists",
            "required": True,
            "passed": bool(reference_command),
            "reason": reference_command,
        },
        {
            "check": "shadow_spec_review_only",
            "required": True,
            "passed": spec.get("mode") == "SHADOW_REVIEW_ONLY",
            "reason": spec.get("mode"),
        },
        {
            "check": "shadow_spec_live_false",
            "required": True,
            "passed": spec.get("live_allowed") is False,
            "reason": spec.get("live_allowed"),
        },
        {
            "check": "shadow_spec_active_paper_false",
            "required": True,
            "passed": spec.get("active_paper_allowed") is False,
            "reason": spec.get("active_paper_allowed"),
        },
        {
            "check": "robustness_passed",
            "required": True,
            "passed": robust.get("status") == "REL_EXTREME_ROBUSTNESS_PASS_READY_FOR_SHADOW_SPEC_REVIEW",
            "reason": robust.get("status"),
        },
        {
            "check": "robustness_gates_all_passed",
            "required": True,
            "passed": int(robust.get("gates_passed") or 0) == int(robust.get("gates_total") or -1),
            "reason": f"{robust.get('gates_passed')}/{robust.get('gates_total')}",
        },
    ]

    manual_checks = [
        {
            "check": "manual_confirm_shadow_only",
            "required": True,
            "passed": False,
            "status": "PENDING",
            "reason": "Human must confirm this approval is for rel_extreme shadow sandbox only, not active paper/live.",
        },
        {
            "check": "manual_confirm_no_master_modification",
            "required": True,
            "passed": False,
            "status": "PENDING",
            "reason": "Human must confirm MASTER_UPPER_SYSTEM launcher/config/sizing contract will not be modified.",
        },
        {
            "check": "manual_confirm_no_live_no_order_api",
            "required": True,
            "passed": False,
            "status": "PENDING",
            "reason": "Human must confirm no exchange API keys, no private API, no order placement.",
        },
        {
            "check": "manual_confirm_runtime_supervised",
            "required": True,
            "passed": False,
            "status": "PENDING",
            "reason": "Human must confirm the shadow runtime is supervised and can be stopped manually.",
        },
        {
            "check": "manual_confirm_runtime_outputs_only_sandbox",
            "required": True,
            "passed": False,
            "status": "PENDING",
            "reason": "Human must confirm outputs go only to paper_run_shadow_rel_extreme_reversion_short.",
        },
        {
            "check": "manual_confirm_cap_policy",
            "required": True,
            "passed": False,
            "status": "PENDING",
            "reason": "Human must confirm cap_signals_per_hour=1 is intentional.",
        },
    ]

    automated_passed = sum(1 for x in automated_checks if x["passed"])
    automated_total = len(automated_checks)
    manual_passed = sum(1 for x in manual_checks if x["passed"])
    manual_total = len(manual_checks)

    packet_status = (
        "REL_EXTREME_MANUAL_SHADOW_APPROVAL_PACKET_READY_FOR_HUMAN_REVIEW"
        if automated_passed == automated_total
        else "REL_EXTREME_MANUAL_SHADOW_APPROVAL_PACKET_BLOCKED"
    )

    packet = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "candidate": CANDIDATE,
        "packet_status": packet_status,
        "workspace": str(WORKSPACE),
        "preflight_state": str(preflight_path) if preflight_path else None,
        "shadow_spec": str(spec_path) if spec_path else None,
        "robustness_state": str(robust_path) if robust_path else None,
        "reference_command": reference_command,
        "automated_required_passed": automated_passed,
        "automated_required_total": automated_total,
        "manual_required_passed": manual_passed,
        "manual_required_total": manual_total,
        "manual_approval_granted": False,
        "shadow_start_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(timespec="seconds"),
        "automated_checks": automated_checks,
        "manual_checks": manual_checks,
        "next_action": "HUMAN_REVIEW_THEN_RUN_APPROVAL_RECORDER_IF_ACCEPTED",
        "hard_rules": [
            "This packet does not grant approval.",
            "This packet does not start shadow.",
            "This packet does not start active paper.",
            "This packet does not start live.",
            "Manual approval must be recorded by a separate recorder module.",
        ],
    }

    packet_json = out_dir / "rel_extreme_manual_shadow_approval_packet.json"
    packet_md = out_dir / "rel_extreme_manual_shadow_approval_packet.md"
    checklist_csv = out_dir / "rel_extreme_manual_shadow_approval_checklist.csv"
    reference_ps1 = out_dir / "rel_extreme_shadow_start_REFERENCE_ONLY.ps1"

    write_json(packet_json, packet)

    with checklist_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["type", "check", "required", "passed", "status", "reason"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for x in automated_checks:
            w.writerow({
                "type": "automated",
                "check": x["check"],
                "required": x["required"],
                "passed": x["passed"],
                "status": "PASS" if x["passed"] else "FAIL",
                "reason": x["reason"],
            })
        for x in manual_checks:
            w.writerow({
                "type": "manual",
                "check": x["check"],
                "required": x["required"],
                "passed": x["passed"],
                "status": x["status"],
                "reason": x["reason"],
            })

    md = []
    md.append("# REL EXTREME MANUAL SHADOW APPROVAL PACKET v1")
    md.append("")
    md.append(f"status: `{packet_status}`")
    md.append(f"candidate: `{CANDIDATE}`")
    md.append(f"automated required: `{automated_passed}/{automated_total}`")
    md.append(f"manual required: `{manual_passed}/{manual_total}`")
    md.append("")
    md.append("## Safety")
    md.append("- manual_approval_granted: `False`")
    md.append("- shadow_start_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("")
    md.append("## Reference command")
    md.append("```powershell")
    md.append(reference_command or "# BLOCKED")
    md.append("```")
    md.append("")
    md.append("## Manual checks")
    for x in manual_checks:
        md.append(f"- [ ] `{x['check']}` — {x['reason']}")
    packet_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    reference_ps1.write_text(
        "# REFERENCE ONLY - DO NOT AUTO-RUN\n"
        "# Requires manual shadow approval record before use.\n"
        "# live_allowed: False\n"
        "# active_paper_allowed: False\n\n"
        + (reference_command or "# BLOCKED") + "\n",
        encoding="utf-8",
    )

    print("EDGE FACTORY REL EXTREME MANUAL SHADOW APPROVAL PACKET v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"candidate : {CANDIDATE}")
    print(f"output_dir: {out_dir}")
    print(f"packet_status: {packet_status}")
    print(f"automated_required: {automated_passed}/{automated_total}")
    print(f"manual_required: {manual_passed}/{manual_total}")
    print("manual_approval_granted: False")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("MANUAL CHECKS")
    print("-" * 100)
    for x in manual_checks:
        print(f"{x['check']:45s} required={x['required']} passed={x['passed']} status={x['status']} reason={x['reason']}")
    print()
    print(f"Report   : {packet_md}")
    print(f"Packet   : {packet_json}")
    print(f"Checklist: {checklist_csv}")
    print(f"Reference: {reference_ps1}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
