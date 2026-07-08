#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS DECISION LEDGER v1
==================================

Purpose
-------
Persistent memory / regression detector for the self-improving Edge Factory OS.

The autopilot loop can produce a final OS mode. But a real OS also needs memory:
    - What was the previous OS mode?
    - Did the control plane regress?
    - Did a rebuild requirement appear?
    - Did paper unexpectedly start?
    - Did live_allowed ever become True?
    - Are we repeating the same state without progress?

This module reads the latest:
    edge_factory_os_autopilot_loop\autopilot_loop_*\os_autopilot_loop_state.json

Then appends a compact snapshot into a persistent ledger:
    edge_factory_os_decision_ledger\master_os_decision_ledger.jsonl
    edge_factory_os_decision_ledger\master_os_decision_ledger.csv

It also emits a current report:
    edge_factory_os_decision_ledger\ledger_run_YYYYMMDD_HHMMSS\...

It does NOT start paper/live.
It does NOT mutate contract/loggers.
It does NOT run child scripts.

Run:
    python "C:\Users\alike\edge_factory_os_decision_ledger.py"

Optional:
    python "C:\Users\alike\edge_factory_os_decision_ledger.py" --no_append

Outputs
-------
    <workspace>\edge_factory_os_decision_ledger\ledger_run_YYYYMMDD_HHMMSS\
        os_decision_ledger_report.md
        os_decision_ledger_snapshot.json
        os_decision_ledger_diff.json
        os_decision_ledger_history_tail.csv
        os_decision_ledger_alerts.json

Core principle
--------------
A self-improving OS must remember its own decisions and detect regressions over time.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

MODE_RANK = {
    "CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED": 90,
    "PAPER_RUNNING_READY_FOR_DRIFT_CHECK": 85,
    "PAPER_RUNNING_WAITING_FOR_DRIFT": 75,
    "WAITING_FOR_PAPER": 70,
    "CONTROL_PLANE_REVIEW_REQUIRED": 55,
    "MANUAL_REVIEW_REQUIRED": 45,
    "REBUILD_REQUIRED": 35,
    "OS_REPAIR_REQUIRED": 10,
    "UNKNOWN": 0,
}

BAD_MODES = {"OS_REPAIR_REQUIRED", "REBUILD_REQUIRED", "MANUAL_REVIEW_REQUIRED"}
GOOD_MODES = {"CONTROL_PLANE_CURRENT__PAPER_READY_NOT_STARTED", "PAPER_RUNNING_READY_FOR_DRIFT_CHECK"}


@dataclass
class Snapshot:
    snapshot_id: str
    generated_at: str
    source_autopilot_path: str
    final_os_mode: str
    mode_rank: int
    paper_started: bool
    closed_paper_trades_exist: bool
    live_allowed: bool
    final_reason_text: str
    final_action_count: int
    waiting_action_count: int
    ready_action_count: int
    hard_rule_count: int
    action_keys: str
    artifact_hash: str


@dataclass
class LedgerDiff:
    previous_snapshot_id: Optional[str]
    current_snapshot_id: str
    previous_mode: Optional[str]
    current_mode: str
    previous_rank: Optional[int]
    current_rank: int
    mode_delta: Optional[int]
    classification: str
    alerts: List[str]
    notes: List[str]


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


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def discover_latest_autopilot(workspace: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    d = latest_child_dir(workspace / "edge_factory_os_autopilot_loop", "autopilot_loop_")
    if not d:
        return None
    p = d / "os_autopilot_loop_state.json"
    return p if p.exists() else None


def stable_hash(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def safe_bool(x: Any) -> bool:
    if isinstance(x, bool):
        return x
    if isinstance(x, str):
        return x.strip().lower() in {"1", "true", "yes", "y"}
    return bool(x)


def build_snapshot(source_path: Path, obj: Dict[str, Any]) -> Snapshot:
    state = obj.get("state") if isinstance(obj.get("state"), dict) else {}
    actions = obj.get("final_actions") if isinstance(obj.get("final_actions"), list) else []

    final_os_mode = str(state.get("final_os_mode", "UNKNOWN"))
    generated_at = str(state.get("generated_at", datetime.now().isoformat(timespec="seconds")))
    reasons = state.get("final_reasons") if isinstance(state.get("final_reasons"), list) else []
    action_keys = [str(a.get("action_key", "unknown")) for a in actions if isinstance(a, dict)]
    waiting_count = len([a for a in actions if isinstance(a, dict) and "WAITING" in str(a.get("status", ""))])
    ready_count = len([a for a in actions if isinstance(a, dict) and str(a.get("status", "")) == "READY"])
    hard_count = len([a for a in actions if isinstance(a, dict) and str(a.get("status", "")) == "HARD_RULE"])

    snapshot_raw = {
        "source_path": str(source_path),
        "state": state,
        "action_keys": action_keys,
        "action_count": len(actions),
    }
    artifact_hash = stable_hash(snapshot_raw)
    snapshot_id = f"{generated_at.replace(':', '').replace('-', '').replace('T', '_')}_{artifact_hash}"

    return Snapshot(
        snapshot_id=snapshot_id,
        generated_at=generated_at,
        source_autopilot_path=str(source_path),
        final_os_mode=final_os_mode,
        mode_rank=MODE_RANK.get(final_os_mode, 0),
        paper_started=safe_bool(state.get("paper_started", False)),
        closed_paper_trades_exist=safe_bool(state.get("closed_paper_trades_exist", False)),
        live_allowed=safe_bool(state.get("live_allowed", False)),
        final_reason_text=" | ".join(str(r) for r in reasons),
        final_action_count=len(actions),
        waiting_action_count=waiting_count,
        ready_action_count=ready_count,
        hard_rule_count=hard_count,
        action_keys=" | ".join(action_keys),
        artifact_hash=artifact_hash,
    )


def read_ledger_jsonl(path: Path) -> List[Dict[str, Any]]:
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
                continue
    return rows


def append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def write_csv_from_rows(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)


def latest_previous_snapshot(rows: List[Dict[str, Any]], current: Snapshot) -> Optional[Dict[str, Any]]:
    # Exclude exact same snapshot_id/artifact hash to avoid comparing current to duplicate current.
    filtered = [r for r in rows if r.get("snapshot_id") != current.snapshot_id]
    if not filtered:
        return None
    return filtered[-1]


def build_diff(previous: Optional[Dict[str, Any]], current: Snapshot) -> LedgerDiff:
    alerts: List[str] = []
    notes: List[str] = []

    if previous is None:
        return LedgerDiff(
            previous_snapshot_id=None,
            current_snapshot_id=current.snapshot_id,
            previous_mode=None,
            current_mode=current.final_os_mode,
            previous_rank=None,
            current_rank=current.mode_rank,
            mode_delta=None,
            classification="FIRST_SNAPSHOT",
            alerts=[],
            notes=["No previous snapshot in ledger."],
        )

    prev_mode = str(previous.get("final_os_mode", "UNKNOWN"))
    prev_rank = int(previous.get("mode_rank", MODE_RANK.get(prev_mode, 0)))
    delta = current.mode_rank - prev_rank

    if current.live_allowed:
        alerts.append("LIVE_ALLOWED_TRUE_UNSAFE")
    if current.final_os_mode in BAD_MODES and prev_mode not in BAD_MODES:
        alerts.append("MODE_REGRESSED_TO_BAD_STATE")
    if delta < 0:
        alerts.append("MODE_RANK_DECREASED")
    if current.paper_started and not safe_bool(previous.get("paper_started", False)):
        alerts.append("PAPER_STARTED_SINCE_LAST_SNAPSHOT")
    if current.closed_paper_trades_exist and not safe_bool(previous.get("closed_paper_trades_exist", False)):
        alerts.append("CLOSED_PAPER_TRADES_APPEARED")

    if current.artifact_hash == str(previous.get("artifact_hash", "")):
        notes.append("Snapshot content hash unchanged from previous comparable snapshot.")
    if delta > 0:
        notes.append("OS mode improved by rank.")
    elif delta == 0:
        notes.append("OS mode unchanged.")
    else:
        notes.append("OS mode rank decreased.")

    if alerts:
        classification = "REGRESSION_OR_ALERT"
    elif delta > 0:
        classification = "IMPROVED"
    elif delta == 0:
        classification = "UNCHANGED"
    else:
        classification = "REGRESSED"

    return LedgerDiff(
        previous_snapshot_id=str(previous.get("snapshot_id")),
        current_snapshot_id=current.snapshot_id,
        previous_mode=prev_mode,
        current_mode=current.final_os_mode,
        previous_rank=prev_rank,
        current_rank=current.mode_rank,
        mode_delta=delta,
        classification=classification,
        alerts=alerts,
        notes=notes,
    )


def tail_history(rows: List[Dict[str, Any]], n: int = 20) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows[-n:])


def write_report(path: Path, snapshot: Snapshot, diff: LedgerDiff, ledger_rows: List[Dict[str, Any]], appended: bool) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Decision Ledger Report")
    lines.append("")
    lines.append(f"Generated: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"Snapshot ID: `{snapshot.snapshot_id}`")
    lines.append(f"Final OS mode: **{snapshot.final_os_mode}**")
    lines.append(f"Mode rank: **{snapshot.mode_rank}**")
    lines.append(f"Ledger appended: **{appended}**")
    lines.append("")

    lines.append("## Current snapshot")
    lines.append("")
    lines.append(f"- Source: `{snapshot.source_autopilot_path}`")
    lines.append(f"- Paper started: **{snapshot.paper_started}**")
    lines.append(f"- Closed paper trades: **{snapshot.closed_paper_trades_exist}**")
    lines.append(f"- Live allowed: **{snapshot.live_allowed}**")
    lines.append(f"- Final actions: **{snapshot.final_action_count}**")
    lines.append(f"- Waiting actions: **{snapshot.waiting_action_count}**")
    lines.append(f"- Ready actions: **{snapshot.ready_action_count}**")
    lines.append(f"- Hard rules: **{snapshot.hard_rule_count}**")
    lines.append("")

    lines.append("## Diff vs previous")
    lines.append("")
    lines.append(f"- Classification: **{diff.classification}**")
    lines.append(f"- Previous mode: **{diff.previous_mode}**")
    lines.append(f"- Current mode: **{diff.current_mode}**")
    lines.append(f"- Mode delta: **{diff.mode_delta}**")
    lines.append("")

    if diff.alerts:
        lines.append("### Alerts")
        lines.append("")
        for a in diff.alerts:
            lines.append(f"- `{a}`")
        lines.append("")

    if diff.notes:
        lines.append("### Notes")
        lines.append("")
        for n in diff.notes:
            lines.append(f"- {n}")
        lines.append("")

    lines.append("## Final reasons")
    lines.append("")
    if snapshot.final_reason_text:
        for r in snapshot.final_reason_text.split(" | "):
            lines.append(f"- {r}")
    else:
        lines.append("- No final reasons recorded.")
    lines.append("")

    lines.append("## Ledger state")
    lines.append("")
    lines.append(f"Total ledger rows after this run: **{len(ledger_rows)}**")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("The decision ledger gives the OS memory. It can now detect whether the control plane stayed current, improved, regressed, or entered an unsafe state across runs.")
    lines.append("No paper/live process was started and no active config was changed.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS decision ledger")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--autopilot_state", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--no_append", action="store_true", help="do not append to master ledger")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    ledger_root = workspace / "edge_factory_os_decision_ledger"
    out_root = Path(args.out_dir) if args.out_dir else ledger_root
    out_dir = out_root / f"ledger_run_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    source = discover_latest_autopilot(workspace, Path(args.autopilot_state) if args.autopilot_state else None)
    if source is None:
        err = {"error": "No autopilot loop state found", "expected_root": str(workspace / "edge_factory_os_autopilot_loop")}
        write_json(out_dir / "fatal_error.json", err)
        print("EDGE FACTORY OS DECISION LEDGER v1")
        print("No autopilot loop state found. Run edge_factory_os_autopilot_loop.py first.")
        print(f"Details: {out_dir / 'fatal_error.json'}")
        return 2

    autopilot_obj = load_json(source)
    if not isinstance(autopilot_obj, dict):
        print("EDGE FACTORY OS DECISION LEDGER v1")
        print("Autopilot state is not a JSON object.")
        return 2

    snapshot = build_snapshot(source, autopilot_obj)
    ledger_jsonl = ledger_root / "master_os_decision_ledger.jsonl"
    ledger_csv = ledger_root / "master_os_decision_ledger.csv"
    existing_rows = read_ledger_jsonl(ledger_jsonl)
    previous = latest_previous_snapshot(existing_rows, snapshot)
    diff = build_diff(previous, snapshot)

    appended = False
    # Avoid duplicate append if exact snapshot already exists as last row.
    if not args.no_append:
        if not existing_rows or existing_rows[-1].get("snapshot_id") != snapshot.snapshot_id:
            append_jsonl(ledger_jsonl, asdict(snapshot))
            appended = True
        else:
            appended = False

    final_rows = read_ledger_jsonl(ledger_jsonl)
    if args.no_append:
        final_rows = existing_rows
    write_csv_from_rows(ledger_csv, final_rows)

    write_json(out_dir / "os_decision_ledger_snapshot.json", asdict(snapshot))
    write_json(out_dir / "os_decision_ledger_diff.json", asdict(diff))
    write_json(out_dir / "os_decision_ledger_alerts.json", {"alerts": diff.alerts, "classification": diff.classification})
    tail_history(final_rows, 30).to_csv(out_dir / "os_decision_ledger_history_tail.csv", index=False)
    write_report(out_dir / "os_decision_ledger_report.md", snapshot, diff, final_rows, appended)

    print("EDGE FACTORY OS DECISION LEDGER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"source    : {source}")
    print(f"output_dir: {out_dir}")
    print(f"snapshot : {snapshot.snapshot_id}")
    print(f"mode     : {snapshot.final_os_mode} rank={snapshot.mode_rank}")
    print(f"append   : {appended}")
    print(f"ledger_rows: {len(final_rows)}")
    print("")
    print("DIFF")
    print("-" * 100)
    print(f"classification: {diff.classification}")
    print(f"previous_mode : {diff.previous_mode}")
    print(f"current_mode  : {diff.current_mode}")
    print(f"mode_delta    : {diff.mode_delta}")
    if diff.alerts:
        print("alerts:")
        for a in diff.alerts:
            print(f"- {a}")
    else:
        print("alerts: none")
    print("")
    print(f"Report : {out_dir / 'os_decision_ledger_report.md'}")
    print(f"Ledger : {ledger_jsonl}")
    print(f"CSV    : {ledger_csv}")
    return 2 if diff.alerts else 0


if __name__ == "__main__":
    raise SystemExit(main())
