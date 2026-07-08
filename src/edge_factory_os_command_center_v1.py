#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

USERDIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
MASTER_BASE = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

SUPERVISOR = USERDIR / "edge_factory_os_supervisor_v1.py"
QUEUE = USERDIR / "edge_factory_os_lifecycle_queue_v1.py"
HEALTH = USERDIR / "edge_factory_live_health_check_v5.py"
PERF = USERDIR / "edge_factory_live_performance_analyzer_v3.py"

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

def read_csv(path: Path | None) -> pd.DataFrame:
    if not path or not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def run_cmd(cmd: list[str], timeout: int = 120) -> dict[str, Any]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "cmd": cmd,
            "returncode": p.returncode,
            "stdout_tail": p.stdout[-6000:],
            "stderr_tail": p.stderr[-3000:],
            "ok": p.returncode == 0,
        }
    except Exception as e:
        return {
            "cmd": cmd,
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": repr(e),
            "ok": False,
        }

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_os_command_center_v1" / f"os_command_center_v1_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    runs = {}

    # Refresh OS state first.
    runs["supervisor"] = run_cmd([sys.executable, str(SUPERVISOR)], timeout=120)
    runs["queue"] = run_cmd([sys.executable, str(QUEUE)], timeout=120)

    # Health/performance are read-only and useful, but do not block the command center.
    runs["health"] = run_cmd([sys.executable, str(HEALTH), "--base_dir", str(MASTER_BASE)], timeout=120)
    runs["performance"] = run_cmd([sys.executable, str(PERF), "--base_dir", str(MASTER_BASE)], timeout=120)

    sup_dir = latest_dir(WORKSPACE / "edge_factory_os_supervisor_v1", "os_supervisor_v1_")
    queue_dir = latest_dir(WORKSPACE / "edge_factory_os_lifecycle_queue_v1", "os_lifecycle_queue_v1_")

    sup_state = read_json(sup_dir / "edge_factory_os_supervisor_v1_state.json" if sup_dir else None)
    queue_state = read_json(queue_dir / "edge_factory_os_lifecycle_queue_v1_state.json" if queue_dir else None)
    queue_df = read_csv(queue_dir / "edge_factory_os_lifecycle_queue_v1.csv" if queue_dir else None)

    decision = sup_state.get("decision", {})
    status = decision.get("status", "UNKNOWN")
    total_open = int(decision.get("total_open") or 0)
    total_pending = int(decision.get("total_pending") or 0)
    total_closed = int(decision.get("total_closed") or 0)
    total_errors = int(decision.get("total_errors") or 0)

    if total_errors > 0:
        command_center_status = "ATTENTION_REQUIRED_ERRORS_PRESENT"
    elif total_open > 0 or total_pending > 0:
        command_center_status = "RUNNING_COLLECTING_SAMPLE_DO_NOT_TOUCH"
    elif status == "UNKNOWN":
        command_center_status = "UNKNOWN_SUPERVISOR_STATE"
    else:
        command_center_status = "IDLE_WAITING_FOR_SIGNALS"

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "master_base": str(MASTER_BASE),
        "command_center_status": command_center_status,
        "supervisor_status": status,
        "open": total_open,
        "pending": total_pending,
        "closed": total_closed,
        "errors": total_errors,
        "supervisor_dir": str(sup_dir) if sup_dir else None,
        "queue_dir": str(queue_dir) if queue_dir else None,
        "runs": runs,
        "queue_tasks": queue_df.to_dict("records") if not queue_df.empty else [],
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Read-only command center.",
            "Does not start or stop trading processes.",
            "Does not change strategy logic.",
            "Does not change capital.",
            "Does not enable live trading.",
            "Does not place orders.",
        ],
    }

    state_path = out_dir / "edge_factory_os_command_center_v1_state.json"
    report_path = out_dir / "edge_factory_os_command_center_v1_report.md"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    report = []
    report.append("# EDGE FACTORY OS COMMAND CENTER v1")
    report.append("")
    report.append(f"status: `{command_center_status}`")
    report.append(f"supervisor: `{status}`")
    report.append(f"open: `{total_open}`")
    report.append(f"pending: `{total_pending}`")
    report.append(f"closed: `{total_closed}`")
    report.append(f"errors: `{total_errors}`")
    report.append("")
    report.append("## Queue")
    if not queue_df.empty:
        for _, row in queue_df.iterrows():
            report.append(f"- `{row.get('status')}` `{row.get('task_key')}` — {row.get('reason')}")
    else:
        report.append("- queue unavailable")
    report.append("")
    report.append("## Verdict")
    if command_center_status == "RUNNING_COLLECTING_SAMPLE_DO_NOT_TOUCH":
        report.append("MASTER is collecting paper sample. Do not debug or modify unless health fails.")
    elif command_center_status == "ATTENTION_REQUIRED_ERRORS_PRESENT":
        report.append("Errors are present. Inspect health/errors before continuing.")
    else:
        report.append("No immediate action.")
    report.append("")
    report.append("## Hard safety")
    report.append("- active_paper_allowed: `False`")
    report.append("- live_allowed: `False`")
    report.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS COMMAND CENTER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"master    : {MASTER_BASE}")
    print(f"output_dir: {out_dir}")
    print(f"status    : {command_center_status}")
    print(f"supervisor: {status}")
    print(f"open      : {total_open}")
    print(f"pending   : {total_pending}")
    print(f"closed    : {total_closed}")
    print(f"errors    : {total_errors}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()

    print("QUEUE")
    print("-" * 100)
    if not queue_df.empty:
        cols = ["priority", "task_key", "task_type", "status", "reason", "blocker"]
        cols = [c for c in cols if c in queue_df.columns]
        print(queue_df[cols].to_string(index=False))
    else:
        print("queue unavailable")
    print()

    print("RUN STATUS")
    print("-" * 100)
    for k, r in runs.items():
        print(f"{k:12s} ok={r['ok']} returncode={r['returncode']}")
        if not r["ok"]:
            print(r["stderr_tail"][-1000:])

    print()
    print(f"State : {state_path}")
    print(f"Report: {report_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
