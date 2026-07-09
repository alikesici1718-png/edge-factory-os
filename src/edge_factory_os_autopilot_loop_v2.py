#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Top-level safe autopilot control loop (v2) that coordinates the command center, drift monitor, capital governor, and batch planner to produce a consolidated OS mode decision with a persistent JSONL history. Writes timestamped state artifacts to edge_factory_os_autopilot_loop_v2/ in the workspace.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
USERDIR = Path(r"C:\Users\alike")
MASTER_BASE = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

COMMAND_CENTER = USERDIR / "edge_factory_os_command_center_v1.py"
DRIFT_MONITOR = USERDIR / "edge_factory_active_family_drift_monitor_planner_v1.py"
CAPITAL_GOVERNOR = USERDIR / "edge_factory_active_capital_governor_review_v2.py"
BATCH_PLANNER = USERDIR / "edge_factory_batch_family_pipeline_planner.py"

OUT_ROOT = WORKSPACE / "edge_factory_os_autopilot_loop_v2"

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def latest_dir(root: Path, prefix: str) -> Path | None:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda p: p.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

def run_cmd(name: str, cmd: list[str], timeout: int = 180) -> dict[str, Any]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "name": name,
            "cmd": cmd,
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout_tail": p.stdout[-8000:],
            "stderr_tail": p.stderr[-4000:],
            "ran_at": now_iso(),
        }
    except Exception as e:
        return {
            "name": name,
            "cmd": cmd,
            "ok": False,
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": repr(e),
            "ran_at": now_iso(),
        }

def load_latest_command_center_state() -> dict[str, Any]:
    d = latest_dir(WORKSPACE / "edge_factory_os_command_center_v1", "os_command_center_v1_")
    if not d:
        return {}
    state = read_json(d / "edge_factory_os_command_center_v1_state.json")
    state["_state_dir"] = str(d)
    return state

def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")

def append_csv(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    fieldnames = [
        "timestamp",
        "loop",
        "severity",
        "status",
        "open",
        "pending",
        "closed",
        "errors",
        "safe_actions_run",
        "safe_actions_blocked",
        "next_actions",
        "active_paper_allowed",
        "live_allowed",
        "capital_change_allowed",
    ]
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in fieldnames})

def decide_and_run_safe_actions(
    cc_state: dict[str, Any],
    allow_safe_execution: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    status = cc_state.get("command_center_status", "UNKNOWN")
    open_n = int(cc_state.get("open") or 0)
    pending_n = int(cc_state.get("pending") or 0)
    closed_n = int(cc_state.get("closed") or 0)
    errors_n = int(cc_state.get("errors") or 0)

    severity = "OK"
    next_actions: list[str] = []
    safe_actions_to_run: list[tuple[str, list[str], int]] = []
    blocked: list[str] = []

    if errors_n > 0:
        severity = "ATTENTION"
        next_actions.append("INSPECT_ERRORS_MANUALLY")
        blocked.append("ALL_AUTOMATED_OPTIONAL_ACTIONS_BLOCKED_ERRORS_PRESENT")
    else:
        if status == "RUNNING_COLLECTING_SAMPLE_DO_NOT_TOUCH":
            next_actions.append("KEEP_MASTER_RUNNING_COLLECT_SAMPLE")

        if closed_n >= 20:
            next_actions.append("DRIFT_MONITOR_READY")
            safe_actions_to_run.append((
                "drift_monitor_planner",
                [sys.executable, str(DRIFT_MONITOR)],
                180,
            ))
        else:
            next_actions.append(f"DRIFT_MONITOR_BLOCKED_CLOSED_{closed_n}_LT_20")
            blocked.append("DRIFT_MONITOR_MIN_CLOSED_NOT_MET")

        if closed_n >= 50:
            next_actions.append("CAPITAL_GOVERNOR_REVIEW_READY")
            safe_actions_to_run.append((
                "capital_governor_review",
                [sys.executable, str(CAPITAL_GOVERNOR)],
                180,
            ))
        else:
            next_actions.append(f"CAPITAL_GOVERNOR_BLOCKED_CLOSED_{closed_n}_LT_50")
            blocked.append("CAPITAL_GOVERNOR_MIN_CLOSED_NOT_MET")

        if closed_n >= 20:
            next_actions.append("RESEARCH_QUEUE_CAN_RESUME_READ_ONLY_PLANNING")
            safe_actions_to_run.append((
                "batch_family_pipeline_planner",
                [sys.executable, str(BATCH_PLANNER)],
                180,
            ))
        else:
            next_actions.append("PAUSE_NEW_CANDIDATE_RESEARCH_UNTIL_INITIAL_SAMPLE")
            blocked.append("RESEARCH_QUEUE_BLOCKED_INITIAL_SAMPLE_NOT_READY")

    safe_action_results: list[dict[str, Any]] = []

    if allow_safe_execution and errors_n == 0:
        for name, cmd, timeout in safe_actions_to_run:
            safe_action_results.append(run_cmd(name, cmd, timeout=timeout))
    elif not allow_safe_execution:
        blocked.append("SAFE_EXECUTION_DISABLED_BY_FLAG")

    decision = {
        "status": status,
        "severity": severity,
        "open": open_n,
        "pending": pending_n,
        "closed": closed_n,
        "errors": errors_n,
        "next_actions": list(dict.fromkeys(next_actions)),
        "safe_actions_planned": [x[0] for x in safe_actions_to_run],
        "safe_actions_run": [x["name"] for x in safe_action_results],
        "safe_actions_blocked": list(dict.fromkeys(blocked)),
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
    }

    return decision, safe_action_results

def main() -> int:
    ap = argparse.ArgumentParser(description="Edge Factory OS Autopilot Loop v2.")
    ap.add_argument("--interval_seconds", type=int, default=300)
    ap.add_argument("--max_loops", type=int, default=0, help="0 means run forever.")
    ap.add_argument("--safe_execute", action="store_true", help="Run safe read-only modules when thresholds are met.")
    args = ap.parse_args()

    run_dir = OUT_ROOT / f"os_autopilot_loop_v2_{stamp()}"
    run_dir.mkdir(parents=True, exist_ok=True)

    latest_state_path = OUT_ROOT / "edge_factory_os_autopilot_v2_latest_state.json"
    latest_status_path = OUT_ROOT / "edge_factory_os_autopilot_v2_latest_status.txt"
    history_jsonl = OUT_ROOT / "edge_factory_os_autopilot_v2_history.jsonl"
    history_csv = OUT_ROOT / "edge_factory_os_autopilot_v2_history.csv"

    print("EDGE FACTORY OS AUTOPILOT LOOP v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"master    : {MASTER_BASE}")
    print(f"run_dir   : {run_dir}")
    print(f"interval  : {args.interval_seconds}s")
    print(f"safe_execute: {args.safe_execute}")
    print("mode: READ_ONLY_SUPERVISION")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("Ctrl+C ile durdurabilirsin.")
    print()

    loop_i = 0

    while True:
        loop_i += 1
        ts = now_iso()

        command_center_result = run_cmd(
            "command_center",
            [sys.executable, str(COMMAND_CENTER)],
            timeout=240,
        )

        cc_state = load_latest_command_center_state()
        decision, safe_action_results = decide_and_run_safe_actions(
            cc_state,
            allow_safe_execution=args.safe_execute,
        )

        if not command_center_result["ok"]:
            decision["severity"] = "CRITICAL"
            decision["next_actions"].insert(0, "COMMAND_CENTER_FAILED_INSPECT_STDERR")

        record = {
            "timestamp": ts,
            "loop": loop_i,
            "run_dir": str(run_dir),
            "command_center": command_center_result,
            "command_center_state_dir": cc_state.get("_state_dir"),
            "decision": decision,
            "safe_action_results": safe_action_results,
            "hard_rules": [
                "Does not start or stop MASTER processes.",
                "Does not place live orders.",
                "Does not use API keys.",
                "Does not change strategy logic.",
                "Does not change capital.",
                "Only runs read-only planner/monitor modules when safe_execute is enabled.",
            ],
        }

        latest_state_path.write_text(
            json.dumps(record, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        append_jsonl(history_jsonl, record)

        csv_row = {
            "timestamp": ts,
            "loop": loop_i,
            "severity": decision["severity"],
            "status": decision["status"],
            "open": decision["open"],
            "pending": decision["pending"],
            "closed": decision["closed"],
            "errors": decision["errors"],
            "safe_actions_run": " | ".join(decision["safe_actions_run"]),
            "safe_actions_blocked": " | ".join(decision["safe_actions_blocked"]),
            "next_actions": " | ".join(decision["next_actions"]),
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
        }
        append_csv(history_csv, csv_row)

        status_line = (
            f"{ts} | {decision['severity']} | {decision['status']} | "
            f"open={decision['open']} pending={decision['pending']} "
            f"closed={decision['closed']} errors={decision['errors']} | "
            f"run={decision['safe_actions_run']} | blocked={decision['safe_actions_blocked']}"
        )
        latest_status_path.write_text(status_line + "\n", encoding="utf-8")
        print(status_line)

        if decision["severity"] in {"ATTENTION", "CRITICAL"}:
            print("ATTENTION REQUIRED:")
            print(latest_state_path)

        if args.max_loops and loop_i >= args.max_loops:
            print("max_loops reached; exiting.")
            break

        time.sleep(max(30, args.interval_seconds))

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
