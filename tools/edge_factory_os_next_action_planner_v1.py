#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
RUNTIME = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_next_action_planner_v1"

DRIFT_MIN_CLOSED = 20
CAPITAL_MIN_CLOSED = 50

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def read_csv_count(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                return 0
            return max(0, len(rows) - 1)
    except Exception:
        return -1

def run(cmd: list[str], cwd: Path | None = None, timeout: int = 60) -> dict:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
        }
    except Exception as e:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": repr(e),
        }

def family_counts() -> dict:
    config_path = RUNTIME / "family_config.json"
    config = read_json(config_path)

    out = {
        "config_path": str(config_path),
        "families": {},
        "totals": {
            "open": 0,
            "pending": 0,
            "closed": 0,
            "rejected": 0,
            "errors": 0,
        },
    }

    if not isinstance(config, dict):
        out["error"] = "family_config_not_dict"
        return out

    for family_key, folder_raw in config.items():
        folder = Path(str(folder_raw))
        counts = {
            "folder": str(folder),
            "folder_exists": folder.exists(),
            "open": read_csv_count(folder / "open_positions.csv"),
            "pending": read_csv_count(folder / "pending_entries.csv"),
            "closed": read_csv_count(folder / "closed_trades.csv"),
            "rejected": read_csv_count(folder / "rejected_entries.csv"),
            "errors": read_csv_count(folder / "errors.csv"),
        }

        out["families"][family_key] = counts

        for k in ["open", "pending", "closed", "rejected", "errors"]:
            if isinstance(counts[k], int) and counts[k] > 0:
                out["totals"][k] += counts[k]

    return out

def latest_json(root: Path, pattern: str) -> Path | None:
    if not root.exists():
        return None
    files = list(root.rglob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def add_task(tasks: list[dict], priority: int, key: str, status: str, allowed: bool, reason: str, command: str = "") -> None:
    tasks.append({
        "priority": priority,
        "task_key": key,
        "status": status,
        "allowed": allowed,
        "reason": reason,
        "command": command,
    })

def main() -> int:
    out_dir = OUT_ROOT / f"os_next_action_planner_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    overlay_path = WORKSPACE / "edge_factory_os_command_center_v2_overlay" / "os_command_center_v2_overlay_latest.json"
    ack_path = WORKSPACE / "edge_factory_error_acknowledger_v1" / "error_acknowledger_latest.json"
    guard_path = latest_json(WORKSPACE / "edge_factory_runtime_regression_guard_v1", "runtime_regression_guard_v1_state.json")

    overlay = read_json(overlay_path)
    ack = read_json(ack_path)
    guard = read_json(guard_path) if guard_path else {}

    counts = family_counts()
    totals = counts.get("totals", {})

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    runtime_ok = overlay.get("runtime_ok") is True
    process_ok = overlay.get("process_watchdog_pass") is True
    health_ok = overlay.get("health_ok") is True
    errors_acknowledged = overlay.get("errors_acknowledged") is True

    acknowledged_total_errors = ack.get("total_errors")
    current_total_errors = totals.get("errors", 0)
    new_errors_since_ack = (
        isinstance(acknowledged_total_errors, int)
        and isinstance(current_total_errors, int)
        and current_total_errors > acknowledged_total_errors
    )

    closed = int(totals.get("closed", 0) or 0)
    open_count = int(totals.get("open", 0) or 0)
    pending = int(totals.get("pending", 0) or 0)

    tasks: list[dict] = []

    if not runtime_ok or not process_ok or not health_ok:
        decision = "STOP_AND_INSPECT_RUNTIME"
        planner_status = "NEXT_ACTION_RUNTIME_ATTENTION"
        add_task(
            tasks,
            1000,
            "inspect_runtime_health",
            "READY_REQUIRED",
            True,
            f"runtime_ok={runtime_ok}, process_ok={process_ok}, health_ok={health_ok}",
            r'python -u "C:\Users\alike\edge_factory_os_command_center_v2_overlay.py"',
        )
    elif new_errors_since_ack:
        decision = "REVIEW_NEW_ERRORS"
        planner_status = "NEXT_ACTION_NEW_ERRORS_REVIEW_REQUIRED"
        add_task(
            tasks,
            1000,
            "classify_new_errors",
            "READY_REQUIRED",
            True,
            f"errors increased: current={current_total_errors}, acknowledged={acknowledged_total_errors}",
            r'python -u "C:\Users\alike\edge_factory_error_classifier_v1.py"',
        )
    elif closed >= CAPITAL_MIN_CLOSED:
        decision = "CAPITAL_REVIEW_READY_BUT_NO_AUTO_CHANGE"
        planner_status = "NEXT_ACTION_CAPITAL_REVIEW_READY"
        add_task(
            tasks,
            1000,
            "run_capital_governor_review",
            "READY_REVIEW_ONLY",
            True,
            f"closed sample reached capital threshold: {closed}/{CAPITAL_MIN_CLOSED}",
            r'python -u "C:\Users\alike\edge_factory_active_capital_governor_review_v2.py"',
        )
    elif closed >= DRIFT_MIN_CLOSED:
        decision = "DRIFT_REVIEW_READY"
        planner_status = "NEXT_ACTION_DRIFT_REVIEW_READY"
        add_task(
            tasks,
            1000,
            "run_drift_review",
            "READY_REVIEW_ONLY",
            True,
            f"closed sample reached drift threshold: {closed}/{DRIFT_MIN_CLOSED}",
            r'python -u "C:\Users\alike\edge_factory_active_family_drift_monitor_planner_v1.py"',
        )
    else:
        decision = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"
        planner_status = "NEXT_ACTION_KEEP_RUNNING"
        add_task(
            tasks,
            1000,
            "protect_running_master",
            "ACTIVE_WAIT",
            True,
            f"runtime healthy; sample not mature yet: closed={closed}/{DRIFT_MIN_CLOSED}, open={open_count}, pending={pending}",
            r'python -u "C:\Users\alike\edge_factory_os_command_center_v2_overlay.py"',
        )

    add_task(
        tasks,
        900,
        "defer_drift_until_closed_20",
        "BLOCKED" if closed < DRIFT_MIN_CLOSED else "READY",
        closed >= DRIFT_MIN_CLOSED,
        f"closed={closed}/{DRIFT_MIN_CLOSED}",
    )

    add_task(
        tasks,
        850,
        "defer_capital_until_closed_50",
        "BLOCKED" if closed < CAPITAL_MIN_CLOSED else "READY_REVIEW_ONLY",
        closed >= CAPITAL_MIN_CLOSED,
        f"closed={closed}/{CAPITAL_MIN_CLOSED}; no automatic capital change allowed",
    )

    add_task(
        tasks,
        800,
        "repo_cleanliness",
        "ATTENTION" if git_dirty else "OK",
        not git_dirty,
        git_status["stdout"].strip() if git_dirty else "git working tree clean",
    )

    add_task(
        tasks,
        700,
        "continue_repo_only_os_intelligence_work",
        "READY" if runtime_ok and not new_errors_since_ack else "BLOCKED",
        runtime_ok and not new_errors_since_ack,
        "Allowed only in repo; runtime stays untouched.",
    )

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "runtime": str(RUNTIME),
        "repo": str(REPO),
        "planner_status": planner_status,
        "decision": decision,
        "runtime_ok": runtime_ok,
        "process_watchdog_pass": process_ok,
        "health_ok": health_ok,
        "errors_acknowledged": errors_acknowledged,
        "acknowledged_total_errors": acknowledged_total_errors,
        "current_total_errors": current_total_errors,
        "new_errors_since_ack": new_errors_since_ack,
        "closed": closed,
        "open": open_count,
        "pending": pending,
        "drift_ready": closed >= DRIFT_MIN_CLOSED,
        "capital_review_ready": closed >= CAPITAL_MIN_CLOSED,
        "git_dirty": git_dirty,
        "git_status_short": git_status["stdout"].strip(),
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "family_counts": counts,
        "tasks": sorted(tasks, key=lambda x: x["priority"], reverse=True),
    }

    state_path = out_dir / "os_next_action_planner_v1_state.json"
    latest_path = OUT_ROOT / "os_next_action_planner_latest.json"
    tasks_csv = out_dir / "os_next_action_planner_v1_tasks.csv"
    report_path = out_dir / "os_next_action_planner_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with tasks_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["priority", "task_key", "status", "allowed", "reason", "command"])
        writer.writeheader()
        writer.writerows(state["tasks"])

    md = []
    md.append("# Edge Factory OS Next Action Planner v1")
    md.append("")
    md.append(f"planner_status: `{planner_status}`")
    md.append(f"decision: `{decision}`")
    md.append("")
    md.append("## Runtime")
    md.append(f"- runtime_ok: `{runtime_ok}`")
    md.append(f"- process_watchdog_pass: `{process_ok}`")
    md.append(f"- health_ok: `{health_ok}`")
    md.append(f"- errors_acknowledged: `{errors_acknowledged}`")
    md.append("")
    md.append("## Sample")
    md.append(f"- open: `{open_count}`")
    md.append(f"- pending: `{pending}`")
    md.append(f"- closed: `{closed}`")
    md.append(f"- drift_ready: `{closed >= DRIFT_MIN_CLOSED}`")
    md.append(f"- capital_review_ready: `{closed >= CAPITAL_MIN_CLOSED}`")
    md.append("")
    md.append("## Safety")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS NEXT ACTION PLANNER v1")
    print("=" * 100)
    print(f"planner_status: {planner_status}")
    print(f"decision      : {decision}")
    print(f"runtime_ok    : {runtime_ok}")
    print(f"process_ok    : {process_ok}")
    print(f"health_ok     : {health_ok}")
    print(f"errors_acknowledged: {errors_acknowledged}")
    print(f"current_total_errors: {current_total_errors}")
    print(f"new_errors_since_ack: {new_errors_since_ack}")
    print(f"open={open_count} pending={pending} closed={closed}")
    print(f"drift_ready={closed >= DRIFT_MIN_CLOSED}")
    print(f"capital_review_ready={closed >= CAPITAL_MIN_CLOSED}")
    print(f"git_dirty={git_dirty}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("TASKS")
    print("-" * 100)
    for t in state["tasks"]:
        print(f"{t['priority']} | {t['task_key']} | {t['status']} | allowed={t['allowed']} | {t['reason']}")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Tasks : {tasks_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
