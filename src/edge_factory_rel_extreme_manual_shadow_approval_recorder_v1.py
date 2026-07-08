#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "rel_extreme_reversion_short"
SANDBOX_ROOT = WORKSPACE / "paper_run_shadow_rel_extreme_reversion_short"

MANUAL_CHECKS = [
    "manual_confirm_shadow_only",
    "manual_confirm_no_master_modification",
    "manual_confirm_no_live_no_order_api",
    "manual_confirm_runtime_supervised",
    "manual_confirm_runtime_outputs_only_sandbox",
    "manual_confirm_cap_policy",
]

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
    ap = argparse.ArgumentParser(description="Record manual shadow approval for rel_extreme candidate. Does not start runtime.")
    ap.add_argument("--approve", action="store_true", help="Record all manual checks as approved.")
    ap.add_argument("--approver", default="human_operator", help="Approval record label.")
    args = ap.parse_args()

    out_dir = WORKSPACE / "edge_factory_rel_extreme_manual_shadow_approval_recorder_v1" / f"rel_extreme_manual_approval_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    packet_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_manual_shadow_approval_packet_v1",
        "rel_extreme_approval_packet_",
    )
    preflight_dir = latest_dir(
        WORKSPACE / "edge_factory_rel_extreme_shadow_preflight_gate_v2",
        "rel_extreme_shadow_preflight_v2_",
    )

    packet_path = packet_dir / "rel_extreme_manual_shadow_approval_packet.json" if packet_dir else None
    preflight_path = preflight_dir / "rel_extreme_shadow_preflight_gate_v2_state.json" if preflight_dir else None

    packet = read_json(packet_path)
    preflight = read_json(preflight_path)

    automated_ok = (
        packet.get("packet_status") == "REL_EXTREME_MANUAL_SHADOW_APPROVAL_PACKET_READY_FOR_HUMAN_REVIEW"
        and int(packet.get("automated_required_passed") or 0) == int(packet.get("automated_required_total") or -1)
    )

    preflight_ok = (
        preflight.get("status") == "REL_EXTREME_SHADOW_PREFLIGHT_V2_PASS_READY_FOR_MANUAL_APPROVAL"
        and preflight.get("ready_for_manual_shadow_approval") is True
    )

    reference_command = packet.get("reference_command") or preflight.get("reference_command")

    manual_records = []
    for check in MANUAL_CHECKS:
        manual_records.append({
            "check": check,
            "required": True,
            "passed": bool(args.approve),
            "status": "APPROVED" if args.approve else "PENDING",
            "approved_by": args.approver if args.approve else None,
            "approved_at": datetime.now().isoformat(timespec="seconds") if args.approve else None,
        })

    manual_ok = all(x["passed"] for x in manual_records)

    approval_granted = bool(args.approve and automated_ok and preflight_ok and manual_ok and reference_command)

    if approval_granted:
        record_status = "REL_EXTREME_MANUAL_SHADOW_APPROVAL_RECORDED"
        next_action = "RUN_REL_EXTREME_SHADOW_START_GATE"
    else:
        record_status = "REL_EXTREME_MANUAL_SHADOW_APPROVAL_NOT_GRANTED"
        next_action = "REVIEW_BLOCKERS_OR_RUN_WITH_APPROVE_AFTER_HUMAN_CHECKS"

    blockers = []
    if not args.approve:
        blockers.append("approval flag --approve was not provided")
    if not automated_ok:
        blockers.append("approval packet automated checks are not complete")
    if not preflight_ok:
        blockers.append("preflight v2 is not ready for manual approval")
    if not reference_command:
        blockers.append("reference command missing")
    if not manual_ok:
        blockers.append("manual checks are not all approved")

    approval_record = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "candidate": CANDIDATE,
        "record_status": record_status,
        "approval_granted": approval_granted,
        "approved_by": args.approver if approval_granted else None,
        "packet_path": str(packet_path) if packet_path else None,
        "preflight_path": str(preflight_path) if preflight_path else None,
        "sandbox_root": str(SANDBOX_ROOT),
        "reference_command": reference_command,
        "manual_checks": manual_records,
        "automated_ok": automated_ok,
        "preflight_ok": preflight_ok,
        "manual_ok": manual_ok,
        "blockers": blockers,
        "shadow_start_allowed_by_record": approval_granted,
        "active_paper_allowed": False,
        "live_allowed": False,
        "hard_rules": [
            "This recorder does not start shadow.",
            "This recorder does not start active paper.",
            "This recorder does not start live.",
            "This recorder does not modify MASTER_UPPER_SYSTEM.",
            "This recorder does not modify sizing contract.",
        ],
        "next_action": next_action,
    }

    record_path = out_dir / "rel_extreme_manual_shadow_approval_record.json"
    checks_path = out_dir / "rel_extreme_manual_shadow_approval_record_checks.csv"
    write_json(record_path, approval_record)

    with checks_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["check", "required", "passed", "status", "approved_by", "approved_at"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in manual_records:
            w.writerow(row)

    master_dir = WORKSPACE / "edge_factory_rel_extreme_manual_shadow_approval_recorder_v1"
    master_dir.mkdir(parents=True, exist_ok=True)
    master_ledger = master_dir / "master_rel_extreme_manual_shadow_approval_ledger.jsonl"
    with master_ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "candidate": CANDIDATE,
            "record_status": record_status,
            "approval_granted": approval_granted,
            "approved_by": args.approver if approval_granted else None,
            "record_path": str(record_path),
            "preflight_path": str(preflight_path) if preflight_path else None,
            "active_paper_allowed": False,
            "live_allowed": False,
        }, ensure_ascii=False) + "\n")

    research_ledger_dir = WORKSPACE / "edge_factory_research_result_ledger"
    research_ledger_dir.mkdir(parents=True, exist_ok=True)
    research_ledger = research_ledger_dir / "master_research_result_ledger.jsonl"
    with research_ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "module": "rel_extreme_manual_shadow_approval_recorder_v1",
            "candidate": CANDIDATE,
            "record_status": record_status,
            "approval_granted": approval_granted,
            "shadow_start_allowed_by_record": approval_granted,
            "active_paper_allowed": False,
            "live_allowed": False,
            "record_path": str(record_path),
        }, ensure_ascii=False) + "\n")

    print("EDGE FACTORY REL EXTREME MANUAL SHADOW APPROVAL RECORDER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"candidate : {CANDIDATE}")
    print(f"output_dir: {out_dir}")
    print(f"approve_flag: {args.approve}")
    print(f"record_status: {record_status}")
    print(f"approval_granted: {approval_granted}")
    print(f"automated_ok: {automated_ok}")
    print(f"preflight_ok: {preflight_ok}")
    print(f"manual_ok: {manual_ok}")
    print(f"shadow_start_allowed_by_record: {approval_granted}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()

    if blockers:
        print("BLOCKERS")
        print("-" * 100)
        for b in blockers:
            print("-", b)
        print()

    print("MANUAL CHECK RECORDS")
    print("-" * 100)
    for x in manual_records:
        print(f"{x['check']:45s} passed={x['passed']} status={x['status']} approved_by={x['approved_by']}")

    print()
    print(f"Record : {record_path}")
    print(f"Checks : {checks_path}")
    print(f"Master : {master_ledger}")
    print(f"Ledger : {research_ledger}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
