#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS MANUAL APPROVAL RECORDER v1
===========================================

Purpose
-------
Manual approval state recorder for the self-improving Edge Factory OS.

The approval packet can say:
    APPROVAL_PACKET_READY_FOR_HUMAN_REVIEW

But the OS needs a separate artifact that records whether the human actually approved:
    - paper-only confirmation
    - native logging confirmation
    - no-live confirmation

This module records that decision.

It does NOT start paper/live.
It does NOT execute launch commands.
It does NOT run PowerShell.
It does NOT mutate active config.
It does NOT run --apply.

Default behavior
----------------
Without approval flags, it records:
    MANUAL_APPROVAL_NOT_GRANTED

To grant supervised paper approval, run explicitly:
    python "C:\Users\alike\edge_factory_os_manual_approval_recorder.py" ^
      --approve_paper_only ^
      --approve_native_logging ^
      --approve_no_live

Optional operator/note:
    --operator "Ali" --note "I approve supervised paper only"

Outputs
-------
    <workspace>\edge_factory_os_manual_approval_recorder\manual_approval_YYYYMMDD_HHMMSS\
        os_manual_approval_record.json
        os_manual_approval_record.md
        os_manual_approval_checklist.csv
        paper_start_command_APPROVED_REFERENCE_ONLY.ps1

Persistent ledger:
    <workspace>\edge_factory_os_manual_approval_recorder\master_manual_approval_ledger.jsonl
    <workspace>\edge_factory_os_manual_approval_recorder\master_manual_approval_ledger.csv

Core rule
---------
Even if approval is granted, this module only records approval. It never starts paper.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")
DEFAULT_LAUNCHER = DEFAULT_SCRIPT_DIR / "start_edge_factory_MASTER_UPPER_SYSTEM.ps1"

APPROVAL_TTL_HOURS = 24


@dataclass
class ApprovalFlag:
    key: str
    required: bool
    granted: bool
    description: str


@dataclass
class ApprovalRecord:
    approval_id: str
    generated_at: str
    expires_at: str
    approval_status: str
    operator: str
    note: str
    source_packet_path: Optional[str]
    source_packet_status: str
    paper_only_approved: bool
    native_logging_approved: bool
    no_live_approved: bool
    all_manual_flags_granted: bool
    automated_packet_ready: bool
    paper_start_allowed_by_approval_record: bool
    live_allowed: bool
    launcher_path: str
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


def discover_latest_packet(workspace: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    d = latest_child_dir(workspace / "edge_factory_os_manual_approval_packet", "approval_packet_")
    if not d:
        return None
    p = d / "os_manual_approval_packet.json"
    return p if p.exists() else None


def stable_hash(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def packet_automated_ready(packet: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
    status = str(packet.get("approval_status", "UNKNOWN"))
    checklist = packet.get("checklist") if isinstance(packet.get("checklist"), list) else []
    failed: List[str] = []
    for item in checklist:
        if not isinstance(item, dict):
            continue
        required = bool(item.get("required", False))
        manual = bool(item.get("manual_confirm_required", False))
        passed = bool(item.get("passed", False))
        key = str(item.get("item_key", "unknown"))
        if required and not manual and not passed:
            failed.append(key)
    ready = status == "APPROVAL_PACKET_READY_FOR_HUMAN_REVIEW" and not failed
    return ready, status, failed


def build_flags(args: argparse.Namespace) -> List[ApprovalFlag]:
    return [
        ApprovalFlag(
            key="approve_paper_only",
            required=True,
            granted=bool(args.approve_paper_only),
            description="I confirm this approval is for supervised paper only, not live trading.",
        ),
        ApprovalFlag(
            key="approve_native_logging",
            required=True,
            granted=bool(args.approve_native_logging),
            description="I confirm native execution fields must be checked after paper starts.",
        ),
        ApprovalFlag(
            key="approve_no_live",
            required=True,
            granted=bool(args.approve_no_live),
            description="I confirm live trading remains blocked regardless of paper approval.",
        ),
    ]


def build_record(args: argparse.Namespace, packet_path: Optional[Path], packet: Dict[str, Any], flags: List[ApprovalFlag]) -> Tuple[ApprovalRecord, List[str]]:
    automated_ready, packet_status, failed_auto = packet_automated_ready(packet)
    all_flags = all(f.granted for f in flags if f.required)
    generated_at = datetime.now()
    expires_at = generated_at + timedelta(hours=int(args.ttl_hours))
    reasons: List[str] = []

    if not packet_path:
        status = "MANUAL_APPROVAL_BLOCKED_NO_PACKET"
        reasons.append("No approval packet found.")
    elif not automated_ready:
        status = "MANUAL_APPROVAL_BLOCKED_PACKET_NOT_READY"
        reasons.append(f"Approval packet is not ready: {packet_status}")
        for f in failed_auto:
            reasons.append(f"failed automated packet check: {f}")
    elif not all_flags:
        status = "MANUAL_APPROVAL_NOT_GRANTED"
        reasons.append("Automated packet is ready, but required manual flags were not all granted.")
    else:
        status = "MANUAL_PAPER_APPROVED_REFERENCE_ONLY"
        reasons.append("All automated checks passed and all manual approval flags were granted.")
        reasons.append("This record permits only manual supervised paper start; it does not start paper.")

    raw = {
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "packet_path": str(packet_path) if packet_path else None,
        "packet_status": packet_status,
        "operator": str(args.operator),
        "note": str(args.note or ""),
        "flags": [asdict(f) for f in flags],
        "status": status,
    }
    approval_id = f"{generated_at.strftime('%Y%m%d_%H%M%S')}_{stable_hash(raw)}"

    return ApprovalRecord(
        approval_id=approval_id,
        generated_at=generated_at.isoformat(timespec="seconds"),
        expires_at=expires_at.isoformat(timespec="seconds"),
        approval_status=status,
        operator=str(args.operator),
        note=str(args.note or ""),
        source_packet_path=str(packet_path) if packet_path else None,
        source_packet_status=packet_status,
        paper_only_approved=bool(args.approve_paper_only),
        native_logging_approved=bool(args.approve_native_logging),
        no_live_approved=bool(args.approve_no_live),
        all_manual_flags_granted=all_flags,
        automated_packet_ready=automated_ready,
        paper_start_allowed_by_approval_record=status == "MANUAL_PAPER_APPROVED_REFERENCE_ONLY",
        live_allowed=False,
        launcher_path=str(DEFAULT_LAUNCHER),
        hard_rules=[
            "This module does not start paper/live.",
            "This approval is paper-only.",
            "Live remains blocked.",
            "Approval expires and should be regenerated if stale.",
            "Launcher command remains reference-only and must be run manually if approved.",
        ],
    ), reasons


def append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def flags_df(flags: List[ApprovalFlag]) -> pd.DataFrame:
    return pd.DataFrame([asdict(f) for f in flags])


def write_reference_ps1(path: Path, record: ApprovalRecord) -> None:
    lines: List[str] = []
    lines.append("# EDGE FACTORY PAPER START COMMAND - APPROVED REFERENCE ONLY")
    lines.append(f"# Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"# approval_id: {record.approval_id}")
    lines.append(f"# approval_status: {record.approval_status}")
    lines.append(f"# expires_at: {record.expires_at}")
    lines.append("#")
    lines.append("# This file is intentionally commented out.")
    lines.append("# This module did NOT start paper.")
    lines.append("# Run manually only if you choose to start supervised paper.")
    lines.append("# Live remains blocked.")
    lines.append("")
    if record.paper_start_allowed_by_approval_record:
        lines.append(f"# powershell -ExecutionPolicy Bypass -File \"{DEFAULT_LAUNCHER}\"")
    else:
        lines.append("# Paper start is NOT approved by this record.")
        lines.append(f"# powershell -ExecutionPolicy Bypass -File \"{DEFAULT_LAUNCHER}\"")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, record: ApprovalRecord, reasons: List[str], flags: List[ApprovalFlag]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Manual Approval Record")
    lines.append("")
    lines.append(f"Generated: `{record.generated_at}`")
    lines.append(f"Approval ID: `{record.approval_id}`")
    lines.append(f"Approval status: **{record.approval_status}**")
    lines.append(f"Expires at: `{record.expires_at}`")
    lines.append(f"Operator: `{record.operator}`")
    lines.append("")

    lines.append("## Decision reasons")
    lines.append("")
    for r in reasons:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Manual flags")
    lines.append("")
    lines.append("| Flag | Required | Granted | Description |")
    lines.append("|---|---:|---:|---|")
    for f in flags:
        lines.append(f"| {f.key} | {f.required} | {f.granted} | {f.description} |")
    lines.append("")

    lines.append("## Source packet")
    lines.append("")
    lines.append(f"- Packet path: `{record.source_packet_path}`")
    lines.append(f"- Packet status: `{record.source_packet_status}`")
    lines.append(f"- Automated packet ready: **{record.automated_packet_ready}**")
    lines.append("")

    lines.append("## Hard rules")
    lines.append("")
    for r in record.hard_rules:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    if record.paper_start_allowed_by_approval_record:
        lines.append("Manual supervised paper approval has been recorded. The launcher was not executed. If paper is started, it must be started manually and followed by health/native logging checks.")
    else:
        lines.append("Manual supervised paper approval has not been granted. Paper should not be started based on this record.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS manual approval recorder")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--packet", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--operator", default="manual_user")
    p.add_argument("--note", default="")
    p.add_argument("--ttl_hours", type=int, default=APPROVAL_TTL_HOURS)
    p.add_argument("--approve_paper_only", action="store_true")
    p.add_argument("--approve_native_logging", action="store_true")
    p.add_argument("--approve_no_live", action="store_true")
    p.add_argument("--no_append", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    root = workspace / "edge_factory_os_manual_approval_recorder"
    out_root = Path(args.out_dir) if args.out_dir else root
    out_dir = out_root / f"manual_approval_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    packet_path = discover_latest_packet(workspace, Path(args.packet) if args.packet else None)
    packet = optional_json(packet_path)
    flags = build_flags(args)
    record, reasons = build_record(args, packet_path, packet, flags)

    ledger_jsonl = root / "master_manual_approval_ledger.jsonl"
    ledger_csv = root / "master_manual_approval_ledger.csv"
    if not args.no_append:
        append_jsonl(ledger_jsonl, asdict(record))
    ledger_rows = read_jsonl(ledger_jsonl)
    pd.DataFrame(ledger_rows).to_csv(ledger_csv, index=False)

    write_json(out_dir / "os_manual_approval_record.json", asdict(record))
    flags_df(flags).to_csv(out_dir / "os_manual_approval_checklist.csv", index=False)
    write_reference_ps1(out_dir / "paper_start_command_APPROVED_REFERENCE_ONLY.ps1", record)
    write_report(out_dir / "os_manual_approval_record.md", record, reasons, flags)

    print("EDGE FACTORY OS MANUAL APPROVAL RECORDER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"packet    : {packet_path}")
    print(f"output_dir: {out_dir}")
    print(f"approval_id    : {record.approval_id}")
    print(f"approval_status: {record.approval_status}")
    print(f"expires_at     : {record.expires_at}")
    print(f"paper_start_allowed_by_approval_record: {record.paper_start_allowed_by_approval_record}")
    print("live_allowed: False")
    print("")
    print("FLAGS")
    print("-" * 100)
    for f in flags:
        print(f"{f.key:30s} required={str(f.required):5s} granted={str(f.granted):5s}")
    print("")
    print("REASONS")
    print("-" * 100)
    for r in reasons:
        print(f"- {r}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live and did not execute the launcher.")
    print("The paper command, if present, is commented reference only.")
    print("")
    print(f"Report : {out_dir / 'os_manual_approval_record.md'}")
    print(f"Record : {out_dir / 'os_manual_approval_record.json'}")
    print(f"Ledger : {ledger_jsonl}")
    print(f"CSV    : {ledger_csv}")
    return 0 if record.approval_status != "MANUAL_APPROVAL_BLOCKED_PACKET_NOT_READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
