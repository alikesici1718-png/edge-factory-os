#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

COMMAND_CENTER = USERDIR / "edge_factory_os_command_center_v1.py"
OUT_ROOT = WORKSPACE / "edge_factory_os_autopilot_loop_v1"

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

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

def run_command_center() -> dict[str, Any]:
    try:
        p = subprocess.run(
            [sys.executable, str(COMMAND_CENTER)],
            capture_output=True,
            text=True,
            timeout=180,
        )
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout_tail": p.stdout[-8000:],
            "stderr_tail": p.stderr[-4000:],
        }
    except Exception as e:
        return {
            "ok": False,
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": repr(e),
        }

def load_latest_command_center_state() -> dict[str, Any]:
    d = latest_dir(WORKSPACE / "edge_factory_os_command_center_v1", "os_command_center_v1_")
    if not d:
        return {}
    state = read_json(d / "edge_factory_os_command_center_v1_state.json")
    state["_state_dir"] = str(d)
    return state

def decide_autopilot(cc_state: dict[str, Any], run_result: dict[str, Any]) -> dict[str, Any]:
    status = cc_state.get("command_center_status", "UNKNOWN")
    open_n = int(cc_state.get("open") or 0)
    pending_n = int(cc_state.get("pending") or 0)
    closed_n = int(cc_state.get("closed") or 0)
    errors_n = int(cc_state.get("errors") or 0)

    actions = []
    severity = "OK"

    if not run_result.get("ok"):
        severity = "CRITICAL"
        actions.append("COMMAND_CENTER_FAILED_INSPECT_STDERR")

    if errors_n > 0:
        severity = "ATTENTION"
        actions.append("INSPECT_ERRORS_BEFORE_ANY_OTHER_ACTION")

    if status == "RUNNING_COLLECTING_SAMPLE_DO_NOT_TOUCH":
        actions.append("KEEP_MASTER_RUNNING_COLLECT_SAMPLE")

    if closed_n < 20:
        actions.append("DRIFT_MONITOR_BLOCKED_UNTIL_CLOSED_20")
    else:
        actions.append("DRIFT_MONITOR_READY")

    if closed_n < 50:
        actions.append("CAPITAL_GOVERNOR_BLOCKED_UNTIL_CLOSED_50")
    else:
        actions.append("CAPITAL_GOVERNOR_REVIEW_READY")

    if open_n == 0 and pending_n == 0 and errors_n == 0:
        actions.append("IDLE_WAIT_FOR_SIGNALS")

    return {
        "autopilot_status": status,
        "severity": severity,
        "open": open_n,
        "pending": pending_n,
        "closed": closed_n,
        "errors": errors_n,
        "actions": list(dict.fromkeys(actions)),
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
    }

def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")

def append_csv(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        fieldnames = [
            "timestamp",
            "autopilot_status",
            "severity",
            "open",
            "pending",
            "closed",
            "errors",
            "actions",
            "command_center_ok",
            "command_center_returncode",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in fieldnames})

def main() -> int:
    ap = argparse.ArgumentParser(description="Edge Factory OS Autopilot Loop v1 - read-only monitor.")
    ap.add_argument("--interval_seconds", type=int, default=300)
    ap.add_argument("--max_loops", type=int, default=0, help="0 means run forever.")
    args = ap.parse_args()

    run_dir = OUT_ROOT / f"os_autopilot_loop_v1_{stamp()}"
    run_dir.mkdir(parents=True, exist_ok=True)

    latest_state = OUT_ROOT / "edge_factory_os_autopilot_latest_state.json"
    history_jsonl = OUT_ROOT / "edge_factory_os_autopilot_history.jsonl"
    history_csv = OUT_ROOT / "edge_factory_os_autopilot_history.csv"
    latest_txt = OUT_ROOT / "edge_factory_os_autopilot_latest_status.txt"

    print("EDGE FACTORY OS AUTOPILOT LOOP v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"run_dir   : {run_dir}")
    print(f"interval  : {args.interval_seconds}s")
    print("mode      : READ_ONLY")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("Ctrl+C ile durdurabilirsin.")
    print()

    loop_i = 0

    while True:
        loop_i += 1
        ts = datetime.now(timezone.utc).isoformat()

        run_result = run_command_center()
        cc_state = load_latest_command_center_state()
        decision = decide_autopilot(cc_state, run_result)

        record = {
            "timestamp": ts,
            "loop": loop_i,
            "run_dir": str(run_dir),
            "command_center_ok": run_result.get("ok"),
            "command_center_returncode": run_result.get("returncode"),
            "command_center_state_dir": cc_state.get("_state_dir"),
            **decision,
            "stdout_tail": run_result.get("stdout_tail", "")[-3000:],
            "stderr_tail": run_result.get("stderr_tail", "")[-2000:],
        }

        latest_state.write_text(
            json.dumps(record, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        append_jsonl(history_jsonl, record)
        append_csv(history_csv, {
            "timestamp": ts,
            "autopilot_status": decision["autopilot_status"],
            "severity": decision["severity"],
            "open": decision["open"],
            "pending": decision["pending"],
            "closed": decision["closed"],
            "errors": decision["errors"],
            "actions": " | ".join(decision["actions"]),
            "command_center_ok": run_result.get("ok"),
            "command_center_returncode": run_result.get("returncode"),
        })

        status_line = (
            f"{ts} | {decision['severity']} | {decision['autopilot_status']} | "
            f"open={decision['open']} pending={decision['pending']} "
            f"closed={decision['closed']} errors={decision['errors']} | "
            f"{' ; '.join(decision['actions'])}"
        )

        latest_txt.write_text(status_line + "\n", encoding="utf-8")

        print(status_line)

        if decision["severity"] in {"CRITICAL", "ATTENTION"}:
            print("ATTENTION REQUIRED. Latest state:")
            print(latest_state)

        if args.max_loops and loop_i >= args.max_loops:
            print("max_loops reached; exiting.")
            break

        time.sleep(max(30, args.interval_seconds))

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
