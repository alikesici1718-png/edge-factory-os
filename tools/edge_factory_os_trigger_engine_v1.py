#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_trigger_engine_v1"

JOURNAL_LATEST_PATH = WORKSPACE / "edge_factory_os_state_transition_journal_v1" / "state_transition_journal_latest.json"
JOURNAL_MASTER_PATH = WORKSPACE / "edge_factory_os_state_transition_journal_v1" / "os_state_transition_journal_master.jsonl"
SAMPLE_PATH = WORKSPACE / "edge_factory_os_sample_maturity_watcher_v1" / "sample_maturity_watcher_latest.json"
STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"
POLICY_PATH = WORKSPACE / "edge_factory_os_policy_engine_v1" / "os_policy_engine_latest.json"
PLANNER_PATH = WORKSPACE / "edge_factory_os_self_improvement_planner_v4" / "os_self_improvement_planner_latest.json"

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

def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            rows.append({"__parse_error__": line[:300]})
    return rows

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

def as_int(value, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except Exception:
        return default

def add_trigger(
    triggers: list[dict],
    priority: int,
    trigger_key: str,
    severity: str,
    allowed: bool,
    reason: str,
    recommended_action: str,
    recommended_command: str = "",
) -> None:
    triggers.append({
        "priority": priority,
        "trigger_key": trigger_key,
        "severity": severity,
        "allowed": bool(allowed),
        "reason": reason,
        "recommended_action": recommended_action,
        "recommended_command": recommended_command,
    })

def latest_family_state(journal: dict) -> dict:
    families = journal.get("families", {})
    return families if isinstance(families, dict) else {}

def family_no_closed_flags(families: dict) -> list[dict]:
    flags = []
    for family_key, row in families.items():
        open_count = as_int(row.get("open"))
        pending = as_int(row.get("pending"))
        closed = as_int(row.get("closed"))
        errors = as_int(row.get("errors"))

        if closed == 0 and (open_count > 0 or pending > 0):
            severity = "ATTENTION" if pending >= 10 or open_count >= 3 else "INFO"
            flags.append({
                "family_key": family_key,
                "open": open_count,
                "pending": pending,
                "closed": closed,
                "errors": errors,
                "severity": severity,
                "reason": "family has exposure/pending but no closed sample yet",
            })
    return flags

def family_error_delta_flags(journal: dict) -> list[dict]:
    flags = []
    events = journal.get("events", [])
    if not isinstance(events, list):
        return flags

    for e in events:
        if e.get("event_type") == "FAMILY_ERRORS_INCREASED":
            flags.append({
                "severity": e.get("severity", "ATTENTION"),
                "detail": e.get("detail", ""),
            })
    return flags

def event_counts(journal: dict) -> Counter:
    events = journal.get("events", [])
    c = Counter()
    if isinstance(events, list):
        for e in events:
            c[e.get("event_type", "UNKNOWN")] += 1
    return c

def choose_primary_trigger(triggers: list[dict]) -> dict:
    if not triggers:
        return {
            "priority": 0,
            "trigger_key": "NO_ACTION_KEEP_COLLECTING",
            "severity": "OK",
            "allowed": True,
            "reason": "No trigger condition matched.",
            "recommended_action": "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
            "recommended_command": r'python -u ".\tools\edge_factory_os_sample_maturity_watcher_v1.py"',
        }

    return sorted(triggers, key=lambda x: x["priority"], reverse=True)[0]

def main() -> int:
    out_dir = OUT_ROOT / f"os_trigger_engine_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    journal = read_json(JOURNAL_LATEST_PATH)
    history = read_jsonl(JOURNAL_MASTER_PATH)
    sample = read_json(SAMPLE_PATH)
    stack = read_json(STACK_PATH)
    policy = read_json(POLICY_PATH)
    planner = read_json(PLANNER_PATH)

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    stack_status = stack.get("stack_status")
    policy_status = policy.get("policy_status")
    planner_status = planner.get("planner_status")
    journal_status = journal.get("journal_status")
    maturity_status = sample.get("maturity_status")

    closed = as_int(sample.get("closed", journal.get("closed")))
    open_count = as_int(sample.get("open", journal.get("open")))
    pending = as_int(sample.get("pending", journal.get("pending")))
    errors = as_int(sample.get("errors", journal.get("errors")))

    closed_delta = journal.get("closed_delta")
    open_delta = journal.get("open_delta")
    pending_delta = journal.get("pending_delta")
    errors_delta = journal.get("errors_delta")

    closed_delta_i = as_int(closed_delta, 0) if closed_delta is not None else 0
    open_delta_i = as_int(open_delta, 0) if open_delta is not None else 0
    pending_delta_i = as_int(pending_delta, 0) if pending_delta is not None else 0
    errors_delta_i = as_int(errors_delta, 0) if errors_delta is not None else 0

    drift_ready = sample.get("drift_ready") is True or closed >= DRIFT_MIN_CLOSED
    capital_ready = sample.get("capital_review_ready") is True or closed >= CAPITAL_MIN_CLOSED

    drift_remaining = max(0, DRIFT_MIN_CLOSED - closed)
    capital_remaining = max(0, CAPITAL_MIN_CLOSED - closed)

    runtime_ok = sample.get("runtime_ok") is True or journal.get("runtime_ok") is True
    process_ok = sample.get("process_ok") is True or journal.get("process_ok") is True
    health_ok = sample.get("health_ok") is True or journal.get("health_ok") is True
    errors_acknowledged = sample.get("errors_acknowledged") is True or journal.get("errors_acknowledged") is True
    new_errors_since_ack = sample.get("new_errors_since_ack") is True or journal.get("new_errors_since_ack") is True

    critical_event_count = as_int(journal.get("critical_event_count"))
    attention_event_count = as_int(journal.get("attention_event_count"))

    families = latest_family_state(journal)
    no_closed_family_flags = family_no_closed_flags(families)
    family_error_flags = family_error_delta_flags(journal)
    event_counter = event_counts(journal)

    triggers: list[dict] = []

    # Hard safety / stop conditions.
    if stack_status != "STACK_PASS":
        add_trigger(
            triggers,
            10000,
            "STACK_REVIEW_REQUIRED",
            "CRITICAL",
            True,
            f"stack_status={stack_status}",
            "REVIEW_STANDARD_STACK_FAILURE",
            r'python -u ".\tools\edge_factory_os_standard_stack_runner_v1.py"',
        )

    if not runtime_ok or not process_ok or not health_ok:
        add_trigger(
            triggers,
            9500,
            "RUNTIME_HEALTH_REVIEW_REQUIRED",
            "CRITICAL",
            True,
            f"runtime_ok={runtime_ok}, process_ok={process_ok}, health_ok={health_ok}",
            "RUN_READ_ONLY_RUNTIME_DIAGNOSTICS",
            r'python -u "C:\Users\alike\edge_factory_os_command_center_v2_overlay.py"',
        )

    if new_errors_since_ack or errors_delta_i > 0:
        add_trigger(
            triggers,
            9000,
            "NEW_ERROR_REVIEW_REQUIRED",
            "ATTENTION",
            True,
            f"new_errors_since_ack={new_errors_since_ack}, errors_delta={errors_delta}",
            "RUN_ERROR_CLASSIFIER_AND_ACKNOWLEDGER",
            r'python -u "C:\Users\alike\edge_factory_error_classifier_v1.py"',
        )

    if critical_event_count > 0:
        add_trigger(
            triggers,
            8500,
            "CRITICAL_JOURNAL_EVENT_REVIEW_REQUIRED",
            "CRITICAL",
            True,
            f"critical_event_count={critical_event_count}",
            "REVIEW_STATE_TRANSITION_JOURNAL",
            r'python -u ".\tools\edge_factory_os_state_transition_journal_v1.py"',
        )

    # Threshold triggers.
    if capital_ready:
        add_trigger(
            triggers,
            8000,
            "CAPITAL_REVIEW_READY_READ_ONLY",
            "INFO",
            True,
            f"closed={closed}/{CAPITAL_MIN_CLOSED}",
            "RUN_CAPITAL_REVIEW_READ_ONLY",
            r'python -u "C:\Users\alike\edge_factory_active_capital_governor_review_v2.py"',
        )

    if drift_ready:
        add_trigger(
            triggers,
            7500,
            "DRIFT_REVIEW_READY_READ_ONLY",
            "INFO",
            True,
            f"closed={closed}/{DRIFT_MIN_CLOSED}",
            "RUN_DRIFT_REVIEW_READ_ONLY",
            r'python -u "C:\Users\alike\edge_factory_active_family_drift_monitor_planner_v1.py"',
        )

    # Soft monitoring triggers.
    if pending_delta_i > 5:
        add_trigger(
            triggers,
            6000,
            "PENDING_JUMP_REVIEW",
            "ATTENTION",
            True,
            f"pending increased by {pending_delta_i}: pending={pending}",
            "REVIEW_PENDING_QUEUE_READ_ONLY",
            r'python -u ".\tools\edge_factory_os_sample_maturity_watcher_v1.py"',
        )

    if open_delta_i > 5:
        add_trigger(
            triggers,
            5900,
            "OPEN_POSITION_JUMP_REVIEW",
            "ATTENTION",
            True,
            f"open increased by {open_delta_i}: open={open_count}",
            "REVIEW_OPEN_POSITION_COUNT_READ_ONLY",
            r'python -u ".\tools\edge_factory_os_sample_maturity_watcher_v1.py"',
        )

    for flag in no_closed_family_flags:
        if flag["severity"] == "ATTENTION":
            add_trigger(
                triggers,
                5000,
                "FAMILY_EXPOSURE_WITH_NO_CLOSED_SAMPLE_REVIEW",
                "ATTENTION",
                True,
                f"{flag['family_key']} open={flag['open']} pending={flag['pending']} closed=0",
                "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
                r'python -u ".\tools\edge_factory_os_sample_maturity_watcher_v1.py"',
            )

    if closed_delta_i > 0 and not drift_ready and not capital_ready:
        add_trigger(
            triggers,
            3000,
            "CLOSED_INCREASED_CONTINUE",
            "INFO",
            True,
            f"closed increased by {closed_delta_i}; closed={closed}; drift_remaining={drift_remaining}; capital_remaining={capital_remaining}",
            "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
            r'python -u ".\tools\edge_factory_os_sample_maturity_watcher_v1.py"',
        )

    if attention_event_count > 0 and not triggers:
        add_trigger(
            triggers,
            2500,
            "ATTENTION_JOURNAL_EVENT_REVIEW",
            "ATTENTION",
            True,
            f"attention_event_count={attention_event_count}",
            "REVIEW_STATE_TRANSITION_JOURNAL",
            r'python -u ".\tools\edge_factory_os_state_transition_journal_v1.py"',
        )

    if not triggers:
        add_trigger(
            triggers,
            1000,
            "NO_ACTION_KEEP_COLLECTING",
            "OK",
            True,
            f"closed={closed}; drift_remaining={drift_remaining}; capital_remaining={capital_remaining}",
            "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
            r'python -u ".\tools\edge_factory_os_sample_maturity_watcher_v1.py"',
        )

    primary = choose_primary_trigger(triggers)

    # If multiple triggers exist, keep all secondary for context.
    secondary = [t for t in sorted(triggers, key=lambda x: x["priority"], reverse=True) if t != primary]

    if primary["severity"] == "CRITICAL":
        trigger_status = "TRIGGER_ENGINE_CRITICAL"
    elif primary["severity"] == "ATTENTION":
        trigger_status = "TRIGGER_ENGINE_ATTENTION"
    else:
        trigger_status = "TRIGGER_ENGINE_READY"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),

        "trigger_status": trigger_status,
        "primary_trigger": primary,
        "secondary_trigger_count": len(secondary),
        "secondary_triggers": secondary,

        "closed": closed,
        "open": open_count,
        "pending": pending,
        "errors": errors,
        "closed_delta": closed_delta,
        "open_delta": open_delta,
        "pending_delta": pending_delta,
        "errors_delta": errors_delta,

        "drift_ready": drift_ready,
        "capital_review_ready": capital_ready,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,

        "runtime_ok": runtime_ok,
        "process_ok": process_ok,
        "health_ok": health_ok,
        "errors_acknowledged": errors_acknowledged,
        "new_errors_since_ack": new_errors_since_ack,

        "stack_status": stack_status,
        "policy_status": policy_status,
        "planner_status": planner_status,
        "journal_status": journal_status,
        "maturity_status": maturity_status,

        "event_counts": dict(event_counter),
        "no_closed_family_flags": no_closed_family_flags,
        "family_error_flags": family_error_flags,

        "history_count": len(history),
        "git_dirty": git_dirty,
        "git_status_short": git_status["stdout"].strip(),

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,
    }

    state_path = out_dir / "os_trigger_engine_v1_state.json"
    latest_path = OUT_ROOT / "os_trigger_engine_latest.json"
    triggers_csv = out_dir / "os_trigger_engine_v1_triggers.csv"
    family_flags_csv = out_dir / "os_trigger_engine_v1_family_flags.csv"
    report_path = out_dir / "os_trigger_engine_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with triggers_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "priority", "trigger_key", "severity", "allowed",
                "reason", "recommended_action", "recommended_command",
            ],
        )
        writer.writeheader()
        writer.writerows(sorted(triggers, key=lambda x: x["priority"], reverse=True))

    with family_flags_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["family_key", "open", "pending", "closed", "errors", "severity", "reason"],
        )
        writer.writeheader()
        writer.writerows(no_closed_family_flags)

    md = []
    md.append("# Edge Factory OS Trigger Engine v1")
    md.append("")
    md.append(f"trigger_status: `{trigger_status}`")
    md.append(f"primary_trigger: `{primary['trigger_key']}`")
    md.append(f"severity: `{primary['severity']}`")
    md.append(f"recommended_action: `{primary['recommended_action']}`")
    md.append("")
    md.append("## Sample")
    md.append(f"- closed: `{closed}` delta=`{closed_delta}`")
    md.append(f"- open: `{open_count}` delta=`{open_delta}`")
    md.append(f"- pending: `{pending}` delta=`{pending_delta}`")
    md.append(f"- errors: `{errors}` delta=`{errors_delta}`")
    md.append(f"- drift_remaining: `{drift_remaining}`")
    md.append(f"- capital_remaining: `{capital_remaining}`")
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

    print("EDGE FACTORY OS TRIGGER ENGINE v1")
    print("=" * 100)
    print(f"trigger_status: {trigger_status}")
    print(f"primary_trigger: {primary['trigger_key']}")
    print(f"primary_severity: {primary['severity']}")
    print(f"recommended_action: {primary['recommended_action']}")
    print(f"recommended_command: {primary['recommended_command']}")
    print(f"secondary_trigger_count: {len(secondary)}")
    print(f"closed={closed} delta={closed_delta}")
    print(f"open={open_count} delta={open_delta}")
    print(f"pending={pending} delta={pending_delta}")
    print(f"errors={errors} delta={errors_delta}")
    print(f"drift_ready={drift_ready} drift_remaining={drift_remaining}")
    print(f"capital_review_ready={capital_ready} capital_remaining={capital_remaining}")
    print(f"runtime_ok={runtime_ok} process_ok={process_ok} health_ok={health_ok}")
    print(f"errors_acknowledged={errors_acknowledged} new_errors_since_ack={new_errors_since_ack}")
    print(f"stack_status={stack_status}")
    print(f"journal_status={journal_status}")
    print(f"git_dirty={git_dirty}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("TRIGGERS")
    print("-" * 100)
    for t in sorted(triggers, key=lambda x: x["priority"], reverse=True):
        print(f"[{t['severity']}] {t['trigger_key']} | {t['recommended_action']} | {t['reason']}")
    print()
    print("FAMILY NO-CLOSED FLAGS")
    print("-" * 100)
    if no_closed_family_flags:
        for f in no_closed_family_flags:
            print(f"[{f['severity']}] {f['family_key']} open={f['open']} pending={f['pending']} closed={f['closed']} | {f['reason']}")
    else:
        print("NONE")
    print()
    print(f"State  : {state_path}")
    print(f"Latest : {latest_path}")
    print(f"Trigger: {triggers_csv}")
    print(f"Family : {family_flags_csv}")
    print(f"Report : {report_path}")

if __name__ == "__main__":
    main()
