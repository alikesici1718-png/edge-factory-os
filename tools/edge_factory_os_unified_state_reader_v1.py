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
OUT_ROOT = WORKSPACE / "edge_factory_os_unified_state_reader_v1"

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
        return {"__read_error__": repr(e), "__path__": str(path)}

def latest_json(root: Path, pattern: str) -> Path | None:
    if not root.exists():
        return None
    files = list(root.rglob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_csv_count(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            rows = list(csv.reader(f))
        return max(0, len(rows) - 1)
    except Exception:
        return -1

def run(cmd: list[str], cwd: Path | None = None, timeout: int = 40) -> dict:
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
    config = read_json(RUNTIME / "family_config.json")
    result = {
        "families": {},
        "totals": {"open": 0, "pending": 0, "closed": 0, "rejected": 0, "errors": 0},
    }

    if not isinstance(config, dict):
        result["error"] = "family_config_not_dict"
        return result

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
        result["families"][family_key] = counts

        for k in result["totals"]:
            v = counts.get(k)
            if isinstance(v, int) and v > 0:
                result["totals"][k] += v

    return result

def status_level(unified: dict) -> str:
    if not unified["runtime"]["runtime_ok"]:
        return "RUNTIME_ATTENTION"
    if unified["runtime"]["new_errors_since_ack"]:
        return "NEW_ERRORS_REVIEW_REQUIRED"
    if unified["safety"]["live_allowed"] or unified["safety"]["capital_change_allowed"]:
        return "SAFETY_ATTENTION"
    if unified["repo"]["git_dirty"]:
        return "REPO_ATTENTION"
    return "OK"

def main() -> int:
    out_dir = OUT_ROOT / f"os_unified_state_reader_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    overlay_path = WORKSPACE / "edge_factory_os_command_center_v2_overlay" / "os_command_center_v2_overlay_latest.json"
    ack_path = WORKSPACE / "edge_factory_error_acknowledger_v1" / "error_acknowledger_latest.json"
    planner_path = WORKSPACE / "edge_factory_os_next_action_planner_v1" / "os_next_action_planner_latest.json"
    memory_path = WORKSPACE / "edge_factory_os_memory_lesson_index_v1" / "os_memory_lesson_index_latest.json"
    guard_path = latest_json(WORKSPACE / "edge_factory_runtime_regression_guard_v1", "runtime_regression_guard_v1_state.json")

    overlay = read_json(overlay_path)
    ack = read_json(ack_path)
    planner = read_json(planner_path)
    memory = read_json(memory_path)
    guard = read_json(guard_path) if guard_path else {}

    counts = family_counts()
    totals = counts.get("totals", {})

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    current_errors = int(totals.get("errors", 0) or 0)
    acknowledged_errors = ack.get("total_errors")
    new_errors_since_ack = (
        isinstance(acknowledged_errors, int)
        and current_errors > acknowledged_errors
    )

    closed = int(totals.get("closed", 0) or 0)
    open_count = int(totals.get("open", 0) or 0)
    pending = int(totals.get("pending", 0) or 0)

    exact_blocks = memory.get("exact_candidate_blocks", [])
    family_cooldowns = memory.get("family_cooldowns", [])

    unified = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "runtime_path": str(RUNTIME),
        "repo_path": str(REPO),
        "runtime": {
            "overlay_status": overlay.get("overlay_status"),
            "severity": overlay.get("severity"),
            "runtime_ok": overlay.get("runtime_ok") is True,
            "process_watchdog_pass": overlay.get("process_watchdog_pass") is True,
            "health_ok": overlay.get("health_ok") is True,
            "errors_acknowledged": overlay.get("errors_acknowledged") is True,
            "current_total_errors": current_errors,
            "acknowledged_total_errors": acknowledged_errors,
            "new_errors_since_ack": new_errors_since_ack,
            "next_action": overlay.get("next_action"),
            "open": open_count,
            "pending": pending,
            "closed": closed,
            "drift_ready": closed >= DRIFT_MIN_CLOSED,
            "capital_review_ready": closed >= CAPITAL_MIN_CLOSED,
        },
        "repo": {
            "git_dirty": git_dirty,
            "git_status_short": git_status["stdout"].strip(),
            "guard_status": guard.get("status"),
            "guard_critical_failed": guard.get("critical_failed"),
            "guard_attention_failed": guard.get("attention_failed"),
            "planner_status": planner.get("planner_status"),
            "planner_decision": planner.get("decision"),
        },
        "memory": {
            "memory_status": memory.get("memory_status"),
            "memory_row_count": memory.get("memory_row_count"),
            "candidate_record_count": memory.get("candidate_record_count"),
            "lesson_count": memory.get("lesson_count"),
            "exact_candidate_blocks": exact_blocks,
            "family_cooldowns": family_cooldowns,
            "known_rules": memory.get("known_rules", []),
        },
        "safety": {
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "real_orders_allowed": False,
        },
        "family_counts": counts,
        "source_paths": {
            "overlay": str(overlay_path),
            "acknowledger": str(ack_path),
            "planner": str(planner_path),
            "memory": str(memory_path),
            "guard": str(guard_path) if guard_path else "",
        },
    }

    unified["state_level"] = status_level(unified)

    if unified["state_level"] == "OK":
        unified["recommended_action"] = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH_AND_CONTINUE_REPO_ONLY_OS_INTELLIGENCE"
    elif unified["state_level"] == "REPO_ATTENTION":
        unified["recommended_action"] = "COMMIT_OR_REVIEW_REPO_CHANGES_BEFORE_NEXT_STEP"
    elif unified["state_level"] == "NEW_ERRORS_REVIEW_REQUIRED":
        unified["recommended_action"] = "RUN_ERROR_CLASSIFIER_AND_ACKNOWLEDGER_BEFORE_ANY_OTHER_ACTION"
    else:
        unified["recommended_action"] = "STOP_REPO_WORK_AND_INSPECT_RUNTIME"

    state_path = out_dir / "os_unified_state_reader_v1_state.json"
    latest_path = OUT_ROOT / "os_unified_state_latest.json"
    report_path = out_dir / "os_unified_state_reader_v1_report.md"

    state_path.write_text(json.dumps(unified, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(unified, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory OS Unified State Reader v1")
    md.append("")
    md.append(f"state_level: `{unified['state_level']}`")
    md.append(f"recommended_action: `{unified['recommended_action']}`")
    md.append("")
    md.append("## Runtime")
    md.append(f"- runtime_ok: `{unified['runtime']['runtime_ok']}`")
    md.append(f"- process_watchdog_pass: `{unified['runtime']['process_watchdog_pass']}`")
    md.append(f"- health_ok: `{unified['runtime']['health_ok']}`")
    md.append(f"- new_errors_since_ack: `{new_errors_since_ack}`")
    md.append(f"- open/pending/closed: `{open_count}/{pending}/{closed}`")
    md.append("")
    md.append("## Memory")
    md.append(f"- exact_candidate_blocks: `{exact_blocks}`")
    md.append(f"- family_cooldowns: `{family_cooldowns}`")
    md.append("")
    md.append("## Safety")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS UNIFIED STATE READER v1")
    print("=" * 100)
    print(f"state_level       : {unified['state_level']}")
    print(f"recommended_action: {unified['recommended_action']}")
    print(f"runtime_ok        : {unified['runtime']['runtime_ok']}")
    print(f"process_ok        : {unified['runtime']['process_watchdog_pass']}")
    print(f"health_ok         : {unified['runtime']['health_ok']}")
    print(f"errors_acknowledged: {unified['runtime']['errors_acknowledged']}")
    print(f"new_errors_since_ack: {new_errors_since_ack}")
    print(f"open={open_count} pending={pending} closed={closed}")
    print(f"drift_ready={closed >= DRIFT_MIN_CLOSED}")
    print(f"capital_review_ready={closed >= CAPITAL_MIN_CLOSED}")
    print(f"git_dirty={git_dirty}")
    print(f"memory_blocks={len(exact_blocks)}")
    print(f"family_cooldowns={len(family_cooldowns)}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("BLOCKED CANDIDATES")
    print("-" * 100)
    print("\n".join(f"- {x}" for x in exact_blocks) if exact_blocks else "NONE")
    print()
    print("FAMILY COOLDOWNS")
    print("-" * 100)
    print("\n".join(f"- {x}" for x in family_cooldowns) if family_cooldowns else "NONE")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
