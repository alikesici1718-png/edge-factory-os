#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 MANUAL SHADOW APPROVAL RECORDER v1
=====================================================

Purpose
-------
Record explicit human/manual approval for ret60_reversal_short shadow sandbox start.

This module is the next safe step after:
    edge_factory_ret60_manual_shadow_approval_packet.py

Default behavior:
    - If approval flags are NOT passed, it records MANUAL_SHADOW_APPROVAL_NOT_GRANTED.
    - If all required flags ARE passed, it records MANUAL_SHADOW_APPROVAL_GRANTED_REFERENCE_ONLY.

It DOES NOT:
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
    - read latest manual approval packet
    - verify packet is ready and not expired
    - require explicit approval flags
    - append an immutable manual approval ledger record
    - write a record that the future shadow start gate may read

Grant command example:
    python "C:\Users\alike\edge_factory_ret60_manual_shadow_approval_recorder.py" `
      --approve_shadow_only `
      --approve_no_live_no_active `
      --approve_native_logging `
      --approve_runtime_supervised `
      --approve_do_not_modify_master

Core rule
---------
Manual approval record still does not start anything. It only lets the next shadow start gate decide.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_CANDIDATE = "ret60_reversal_short"

REQUIRED_FLAGS = [
    "approve_shadow_only",
    "approve_no_live_no_active",
    "approve_native_logging",
    "approve_runtime_supervised",
    "approve_do_not_modify_master",
]


@dataclass
class ManualFlag:
    flag_name: str
    required: bool
    granted: bool
    status: str
    meaning: str


@dataclass
class ApprovalRecorderState:
    generated_at: str
    workspace: str
    candidate: str
    packet_path: Optional[str]
    output_dir: str
    approval_id: str
    approval_status: str
    packet_ready: bool
    packet_expired: bool
    required_flags_granted: int
    required_flags_total: int
    manual_approval_granted: bool
    shadow_start_allowed_by_approval_record: bool
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


def stable_hash(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


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


def latest_packet_path(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_manual_shadow_approval_packet", "ret60_approval_packet_")
    if not d:
        return None
    p = d / "ret60_manual_shadow_approval_packet.json"
    return p if p.exists() else None


def load_packet(workspace: Path, explicit_packet: Optional[str]) -> tuple[Dict[str, Any], Optional[Path], List[str]]:
    warnings: List[str] = []
    p = Path(explicit_packet) if explicit_packet else latest_packet_path(workspace)
    obj = read_json_optional(p)
    if not p or not p.exists():
        warnings.append("manual approval packet missing")
    if not obj:
        warnings.append("manual approval packet unreadable or empty")
    return obj, p, warnings


def parse_time_maybe(s: Any) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


def packet_ready_and_expired(packet: Dict[str, Any]) -> tuple[bool, bool, str, List[str]]:
    warnings: List[str] = []
    state = packet.get("state", {}) if isinstance(packet.get("state"), dict) else {}
    status = str(state.get("packet_status") or "")
    ready = bool(state.get("ready_for_manual_shadow_approval", False)) and "READY_FOR_HUMAN_REVIEW" in status
    expires_at = str(state.get("expires_at") or "")
    exp = parse_time_maybe(expires_at)
    expired = False
    if exp is None:
        warnings.append("packet expiration time missing/unreadable")
    else:
        expired = datetime.now() > exp
    return ready, expired, status, warnings


def build_flags(args: argparse.Namespace) -> List[ManualFlag]:
    meanings = {
        "approve_shadow_only": "Approval is for ret60 shadow sandbox only, not active paper/live.",
        "approve_no_live_no_active": "No live trading and no active paper portfolio inclusion are allowed.",
        "approve_native_logging": "Native logging fields are required during shadow runtime.",
        "approve_runtime_supervised": "Shadow runtime must be supervised and manually stoppable.",
        "approve_do_not_modify_master": "MASTER_UPPER_SYSTEM and sizing contract must not be modified.",
    }
    flags: List[ManualFlag] = []
    for name in REQUIRED_FLAGS:
        granted = bool(getattr(args, name, False))
        flags.append(ManualFlag(
            flag_name=name,
            required=True,
            granted=granted,
            status="GRANTED" if granted else "MISSING",
            meaning=meanings[name],
        ))
    return flags


def append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def jsonl_to_csv(jsonl_path: Path, csv_path: Path) -> None:
    rows: List[Dict[str, Any]] = []
    if jsonl_path.exists():
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    if rows:
        pd.DataFrame(rows).to_csv(csv_path, index=False)


def summarize_state(workspace: Path, out_dir: Path, packet_path: Optional[Path], packet: Dict[str, Any], flags: List[ManualFlag], warnings: List[str]) -> ApprovalRecorderState:
    packet_ready, packet_expired, packet_status, packet_warnings = packet_ready_and_expired(packet)
    warnings.extend(packet_warnings)
    granted_count = len([f for f in flags if f.required and f.granted])
    total_count = len([f for f in flags if f.required])
    all_flags = granted_count == total_count

    blockers: List[str] = []
    reasons: List[str] = []

    if not packet_ready:
        blockers.append("approval packet is not ready for human review")
    if packet_expired:
        blockers.append("approval packet is expired")
    if not all_flags:
        missing = [f.flag_name for f in flags if f.required and not f.granted]
        blockers.append("missing required manual flags: " + ", ".join(missing))

    manual_granted = packet_ready and not packet_expired and all_flags
    if manual_granted:
        status = "RET60_MANUAL_SHADOW_APPROVAL_GRANTED_REFERENCE_ONLY"
        next_action = "RUN_RET60_SHADOW_START_GATE"
        reasons.append("packet was ready and all required manual approval flags were granted")
        reasons.append("approval record permits the next shadow start gate to decide; it does not start runtime")
    else:
        status = "RET60_MANUAL_SHADOW_APPROVAL_NOT_GRANTED"
        next_action = "GRANT_REQUIRED_FLAGS_OR_KEEP_WAITING"
        reasons.append("manual approval was not granted because at least one required condition is missing")

    approval_seed = {
        "candidate": DEFAULT_CANDIDATE,
        "packet_path": str(packet_path) if packet_path else None,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "flags": [asdict(f) for f in flags],
    }
    approval_id = f"{now_stamp()}_{stable_hash(approval_seed)}"
    expires_at = (datetime.now() + timedelta(hours=12)).isoformat(timespec="seconds") if manual_granted else (datetime.now() + timedelta(hours=24)).isoformat(timespec="seconds")

    return ApprovalRecorderState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        candidate=DEFAULT_CANDIDATE,
        packet_path=str(packet_path) if packet_path else None,
        output_dir=str(out_dir),
        approval_id=approval_id,
        approval_status=status,
        packet_ready=packet_ready,
        packet_expired=packet_expired,
        required_flags_granted=granted_count,
        required_flags_total=total_count,
        manual_approval_granted=manual_granted,
        shadow_start_allowed_by_approval_record=manual_granted,
        active_paper_allowed=False,
        live_allowed=False,
        expires_at=expires_at,
        next_action=next_action,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
        hard_rules=[
            "Manual approval recorder never starts shadow/active paper/live.",
            "Manual approval recorder never runs logger runtime.",
            "Manual approval recorder never mutates active config.",
            "Manual approval recorder never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Approval record only permits a future shadow start gate to decide.",
            "Active paper and live remain blocked.",
        ],
    )


def records_df(items: List[Any]) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in items])


def write_outputs(workspace: Path, out_dir: Path, state: ApprovalRecorderState, flags: List[ManualFlag], packet: Dict[str, Any]) -> None:
    record = {
        "state": asdict(state),
        "flags": [asdict(f) for f in flags],
        "packet_path": state.packet_path,
    }
    write_json(out_dir / "ret60_manual_shadow_approval_record.json", record)
    records_df(flags).to_csv(out_dir / "ret60_manual_shadow_approval_flags.csv", index=False)

    ledger_dir = workspace / "edge_factory_ret60_manual_shadow_approval_recorder"
    ledger_jsonl = ledger_dir / "master_ret60_manual_shadow_approval_ledger.jsonl"
    ledger_csv = ledger_dir / "master_ret60_manual_shadow_approval_ledger.csv"
    ledger_row = {
        "approval_id": state.approval_id,
        "generated_at": state.generated_at,
        "candidate": state.candidate,
        "approval_status": state.approval_status,
        "manual_approval_granted": state.manual_approval_granted,
        "shadow_start_allowed_by_approval_record": state.shadow_start_allowed_by_approval_record,
        "active_paper_allowed": state.active_paper_allowed,
        "live_allowed": state.live_allowed,
        "packet_path": state.packet_path,
        "record_path": str(out_dir / "ret60_manual_shadow_approval_record.json"),
        "expires_at": state.expires_at,
        "flags_granted": state.required_flags_granted,
        "flags_total": state.required_flags_total,
    }
    append_jsonl(ledger_jsonl, ledger_row)
    jsonl_to_csv(ledger_jsonl, ledger_csv)

    md = f"""# Ret60 Manual Shadow Approval Record

Status: **{state.approval_status}**

- Approval ID: `{state.approval_id}`
- Packet ready: `{state.packet_ready}`
- Packet expired: `{state.packet_expired}`
- Required flags: `{state.required_flags_granted}/{state.required_flags_total}`
- Manual approval granted: `{state.manual_approval_granted}`
- Shadow start allowed by approval record: `{state.shadow_start_allowed_by_approval_record}`
- Active paper allowed: `False`
- Live allowed: `False`
- Expires at: `{state.expires_at}`

## Blockers

```text
{chr(10).join(state.blockers) if state.blockers else 'none'}
```

## Hard rules

```text
{chr(10).join(state.hard_rules)}
```

This record does not start anything. A separate shadow start gate must read this record.
"""
    write_text(out_dir / "ret60_manual_shadow_approval_record.md", md)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Record explicit manual approval for ret60 shadow sandbox")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--packet", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--approve_shadow_only", action="store_true")
    p.add_argument("--approve_no_live_no_active", action="store_true")
    p.add_argument("--approve_native_logging", action="store_true")
    p.add_argument("--approve_runtime_supervised", action="store_true")
    p.add_argument("--approve_do_not_modify_master", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_manual_shadow_approval_recorder"
    out_dir = out_root / f"ret60_manual_approval_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    packet, packet_path, warnings = load_packet(workspace, args.packet)
    flags = build_flags(args)
    state = summarize_state(workspace, out_dir, packet_path, packet, flags, warnings)
    write_outputs(workspace, out_dir, state, flags, packet)

    print("EDGE FACTORY RET60 MANUAL SHADOW APPROVAL RECORDER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"candidate : {DEFAULT_CANDIDATE}")
    print(f"packet    : {packet_path}")
    print(f"output_dir: {out_dir}")
    print(f"approval_id: {state.approval_id}")
    print(f"approval_status: {state.approval_status}")
    print(f"packet_ready: {state.packet_ready}")
    print(f"packet_expired: {state.packet_expired}")
    print(f"required_flags: {state.required_flags_granted}/{state.required_flags_total}")
    print(f"manual_approval_granted: {state.manual_approval_granted}")
    print(f"shadow_start_allowed_by_approval_record: {state.shadow_start_allowed_by_approval_record}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print(f"expires_at: {state.expires_at}")
    print("")
    print("FLAGS")
    print("-" * 100)
    for f in flags:
        print(f"{f.flag_name:40s} required={f.required} granted={f.granted} status={f.status} meaning={f.meaning}")
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
    print("This module did not start shadow/active paper/live, did not run logger runtime, and did not mutate active config.")
    print("")
    print(f"Report : {out_dir / 'ret60_manual_shadow_approval_record.md'}")
    print(f"Record : {out_dir / 'ret60_manual_shadow_approval_record.json'}")
    print(f"Ledger : {workspace / 'edge_factory_ret60_manual_shadow_approval_recorder' / 'master_ret60_manual_shadow_approval_ledger.jsonl'}")
    print(f"CSV    : {workspace / 'edge_factory_ret60_manual_shadow_approval_recorder' / 'master_ret60_manual_shadow_approval_ledger.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
