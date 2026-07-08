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
OUT_ROOT = WORKSPACE / "edge_factory_os_sample_maturity_watcher_v1"

UNIFIED_STATE_PATH = WORKSPACE / "edge_factory_os_unified_state_reader_v1" / "os_unified_state_latest.json"
STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"
POLICY_PATH = WORKSPACE / "edge_factory_os_policy_engine_v1" / "os_policy_engine_latest.json"

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

def read_csv_count(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            rows = list(csv.reader(f))
        return max(0, len(rows) - 1)
    except Exception:
        return -1

def latest_timestamp_from_csv(path: Path, candidate_columns: list[str]) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return ""
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            latest = ""
            for row in reader:
                for col in candidate_columns:
                    val = str(row.get(col, "") or "")
                    if val and val > latest:
                        latest = val
            return latest
    except Exception:
        return ""

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
        "totals": {
            "open": 0,
            "pending": 0,
            "closed": 0,
            "rejected": 0,
            "errors": 0,
        },
    }

    if not isinstance(config, dict):
        result["error"] = "family_config_not_dict"
        return result

    for family_key, folder_raw in config.items():
        folder = Path(str(folder_raw))

        open_path = folder / "open_positions.csv"
        pending_path = folder / "pending_entries.csv"
        closed_path = folder / "closed_trades.csv"
        rejected_path = folder / "rejected_entries.csv"
        errors_path = folder / "errors.csv"

        counts = {
            "folder": str(folder),
            "folder_exists": folder.exists(),
            "open": read_csv_count(open_path),
            "pending": read_csv_count(pending_path),
            "closed": read_csv_count(closed_path),
            "rejected": read_csv_count(rejected_path),
            "errors": read_csv_count(errors_path),
            "last_closed_utc": latest_timestamp_from_csv(
                closed_path,
                ["exit_time", "closed_time", "close_time", "timestamp", "time"],
            ),
            "last_error_utc": latest_timestamp_from_csv(
                errors_path,
                ["log_time", "timestamp", "time"],
            ),
        }

        result["families"][family_key] = counts

        for k in ["open", "pending", "closed", "rejected", "errors"]:
            v = counts.get(k)
            if isinstance(v, int) and v > 0:
                result["totals"][k] += v

    return result

def progress_pct(value: int, threshold: int) -> float:
    if threshold <= 0:
        return 0.0
    return round(min(100.0, max(0.0, value / threshold * 100.0)), 2)

def main() -> int:
    out_dir = OUT_ROOT / f"sample_maturity_watcher_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    unified = read_json(UNIFIED_STATE_PATH)
    stack = read_json(STACK_PATH)
    policy = read_json(POLICY_PATH)
    counts = family_counts()

    totals = counts.get("totals", {})
    closed = int(totals.get("closed", 0) or 0)
    open_count = int(totals.get("open", 0) or 0)
    pending = int(totals.get("pending", 0) or 0)
    errors = int(totals.get("errors", 0) or 0)

    drift_remaining = max(0, DRIFT_MIN_CLOSED - closed)
    capital_remaining = max(0, CAPITAL_MIN_CLOSED - closed)

    drift_ready = closed >= DRIFT_MIN_CLOSED
    capital_review_ready = closed >= CAPITAL_MIN_CLOSED

    runtime = unified.get("runtime", {})
    runtime_ok = runtime.get("runtime_ok") is True
    process_ok = runtime.get("process_watchdog_pass") is True
    health_ok = runtime.get("health_ok") is True
    new_errors_since_ack = runtime.get("new_errors_since_ack") is True
    errors_acknowledged = runtime.get("errors_acknowledged") is True

    stack_pass = stack.get("stack_status") == "STACK_PASS"
    policy_pass = policy.get("policy_status") == "POLICY_ENGINE_PASS"

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    if not runtime_ok or not process_ok or not health_ok:
        maturity_status = "SAMPLE_MATURITY_RUNTIME_ATTENTION"
        next_action = "RUN_STANDARD_STACK_AND_RUNTIME_DIAGNOSTICS"
    elif new_errors_since_ack:
        maturity_status = "SAMPLE_MATURITY_NEW_ERRORS_REVIEW_REQUIRED"
        next_action = "RUN_ERROR_CLASSIFIER_AND_ACKNOWLEDGER"
    elif capital_review_ready:
        maturity_status = "SAMPLE_MATURITY_CAPITAL_REVIEW_READY_READ_ONLY"
        next_action = "RUN_CAPITAL_REVIEW_READ_ONLY"
    elif drift_ready:
        maturity_status = "SAMPLE_MATURITY_DRIFT_REVIEW_READY"
        next_action = "RUN_DRIFT_REVIEW_READ_ONLY"
    else:
        maturity_status = "SAMPLE_MATURITY_COLLECTING"
        next_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"

    family_rows = []
    for family_key, c in counts.get("families", {}).items():
        family_rows.append({
            "family_key": family_key,
            "folder_exists": c.get("folder_exists"),
            "open": c.get("open"),
            "pending": c.get("pending"),
            "closed": c.get("closed"),
            "rejected": c.get("rejected"),
            "errors": c.get("errors"),
            "last_closed_utc": c.get("last_closed_utc"),
            "last_error_utc": c.get("last_error_utc"),
        })

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "runtime": str(RUNTIME),
        "repo": str(REPO),
        "maturity_status": maturity_status,
        "next_action": next_action,
        "closed": closed,
        "open": open_count,
        "pending": pending,
        "errors": errors,
        "drift_min_closed": DRIFT_MIN_CLOSED,
        "capital_min_closed": CAPITAL_MIN_CLOSED,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_progress_pct": progress_pct(closed, DRIFT_MIN_CLOSED),
        "capital_progress_pct": progress_pct(closed, CAPITAL_MIN_CLOSED),
        "drift_ready": drift_ready,
        "capital_review_ready": capital_review_ready,
        "runtime_ok": runtime_ok,
        "process_ok": process_ok,
        "health_ok": health_ok,
        "errors_acknowledged": errors_acknowledged,
        "new_errors_since_ack": new_errors_since_ack,
        "stack_pass": stack_pass,
        "policy_pass": policy_pass,
        "git_dirty": git_dirty,
        "git_status_short": git_status["stdout"].strip(),
        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,
        "family_counts": family_rows,
    }

    state_path = out_dir / "sample_maturity_watcher_v1_state.json"
    latest_path = OUT_ROOT / "sample_maturity_watcher_latest.json"
    family_csv = out_dir / "sample_maturity_watcher_v1_family_counts.csv"
    report_path = out_dir / "sample_maturity_watcher_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with family_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "family_key", "folder_exists", "open", "pending", "closed",
                "rejected", "errors", "last_closed_utc", "last_error_utc",
            ],
        )
        writer.writeheader()
        writer.writerows(family_rows)

    md = []
    md.append("# Edge Factory OS Sample Maturity Watcher v1")
    md.append("")
    md.append(f"maturity_status: `{maturity_status}`")
    md.append(f"next_action: `{next_action}`")
    md.append("")
    md.append("## Sample")
    md.append(f"- closed: `{closed}`")
    md.append(f"- open: `{open_count}`")
    md.append(f"- pending: `{pending}`")
    md.append(f"- drift_remaining: `{drift_remaining}`")
    md.append(f"- capital_remaining: `{capital_remaining}`")
    md.append(f"- drift_progress_pct: `{state['drift_progress_pct']}`")
    md.append(f"- capital_progress_pct: `{state['capital_progress_pct']}`")
    md.append("")
    md.append("## Safety")
    md.append("- runtime_touch_allowed: `False`")
    md.append("- launcher_allowed: `False`")
    md.append("- patch_runtime_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    md.append("- execution_performed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS SAMPLE MATURITY WATCHER v1")
    print("=" * 100)
    print(f"maturity_status: {maturity_status}")
    print(f"next_action: {next_action}")
    print(f"closed={closed} open={open_count} pending={pending} errors={errors}")
    print(f"drift_remaining={drift_remaining} / progress={state['drift_progress_pct']}%")
    print(f"capital_remaining={capital_remaining} / progress={state['capital_progress_pct']}%")
    print(f"runtime_ok={runtime_ok} process_ok={process_ok} health_ok={health_ok}")
    print(f"errors_acknowledged={errors_acknowledged} new_errors_since_ack={new_errors_since_ack}")
    print(f"stack_pass={stack_pass} policy_pass={policy_pass} git_dirty={git_dirty}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("FAMILY COUNTS")
    print("-" * 100)
    for r in family_rows:
        print(f"{r['family_key']} | open={r['open']} pending={r['pending']} closed={r['closed']} errors={r['errors']}")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Family: {family_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
