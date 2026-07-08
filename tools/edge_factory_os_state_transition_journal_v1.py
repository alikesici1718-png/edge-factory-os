#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_state_transition_journal_v1"

STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"
UNIFIED_PATH = WORKSPACE / "edge_factory_os_unified_state_reader_v1" / "os_unified_state_latest.json"
POLICY_PATH = WORKSPACE / "edge_factory_os_policy_engine_v1" / "os_policy_engine_latest.json"
PLANNER_PATH = WORKSPACE / "edge_factory_os_self_improvement_planner_v4" / "os_self_improvement_planner_latest.json"
DECISION_PATH = WORKSPACE / "edge_factory_os_autopilot_decision_adapter_v1" / "os_autopilot_decision_latest.json"
ROUTER_PATH = WORKSPACE / "edge_factory_os_execution_router_v1" / "os_execution_router_latest.json"
SAMPLE_PATH = WORKSPACE / "edge_factory_os_sample_maturity_watcher_v1" / "sample_maturity_watcher_latest.json"

MASTER_JOURNAL = OUT_ROOT / "os_state_transition_journal_master.jsonl"

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

def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")

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

def num_delta(current: int, previous: int | None) -> int | None:
    if previous is None:
        return None
    return current - previous

def status_change(current, previous) -> bool:
    if previous is None:
        return False
    return current != previous

def family_map(sample: dict) -> dict:
    rows = sample.get("family_counts", [])
    out = {}
    if isinstance(rows, list):
        for r in rows:
            key = str(r.get("family_key") or "UNKNOWN")
            out[key] = {
                "open": as_int(r.get("open")),
                "pending": as_int(r.get("pending")),
                "closed": as_int(r.get("closed")),
                "rejected": as_int(r.get("rejected")),
                "errors": as_int(r.get("errors")),
                "last_closed_utc": r.get("last_closed_utc", ""),
                "last_error_utc": r.get("last_error_utc", ""),
            }
    return out

def build_family_deltas(current_families: dict, previous_families: dict | None) -> list[dict]:
    previous_families = previous_families or {}
    all_keys = sorted(set(current_families.keys()) | set(previous_families.keys()))
    rows = []

    for key in all_keys:
        cur = current_families.get(key, {})
        prev = previous_families.get(key, {})

        row = {
            "family_key": key,
            "open": as_int(cur.get("open")),
            "pending": as_int(cur.get("pending")),
            "closed": as_int(cur.get("closed")),
            "errors": as_int(cur.get("errors")),
            "open_delta": "",
            "pending_delta": "",
            "closed_delta": "",
            "errors_delta": "",
            "last_closed_utc": cur.get("last_closed_utc", ""),
            "last_error_utc": cur.get("last_error_utc", ""),
            "changed": False,
        }

        if prev:
            for field in ["open", "pending", "closed", "errors"]:
                d = as_int(cur.get(field)) - as_int(prev.get(field))
                row[f"{field}_delta"] = d
                if d != 0:
                    row["changed"] = True
        else:
            row["changed"] = True

        rows.append(row)

    return rows

def main() -> int:
    out_dir = OUT_ROOT / f"state_transition_journal_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    stack = read_json(STACK_PATH)
    unified = read_json(UNIFIED_PATH)
    policy = read_json(POLICY_PATH)
    planner = read_json(PLANNER_PATH)
    decision = read_json(DECISION_PATH)
    router = read_json(ROUTER_PATH)
    sample = read_json(SAMPLE_PATH)

    history = read_jsonl(MASTER_JOURNAL)
    previous = history[-1] if history else None

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    current_families = family_map(sample)
    previous_families = previous.get("families", {}) if previous else {}

    closed = as_int(sample.get("closed"))
    open_count = as_int(sample.get("open"))
    pending = as_int(sample.get("pending"))
    errors = as_int(sample.get("errors"))

    previous_closed = as_int(previous.get("closed")) if previous else None
    previous_open = as_int(previous.get("open")) if previous else None
    previous_pending = as_int(previous.get("pending")) if previous else None
    previous_errors = as_int(previous.get("errors")) if previous else None

    stack_status = stack.get("stack_status")
    planner_status = planner.get("planner_status")
    maturity_status = sample.get("maturity_status")
    final_decision = decision.get("final_decision")
    router_status = router.get("router_status")
    policy_status = policy.get("policy_status")

    previous_stack_status = previous.get("stack_status") if previous else None
    previous_planner_status = previous.get("planner_status") if previous else None
    previous_maturity_status = previous.get("maturity_status") if previous else None
    previous_final_decision = previous.get("final_decision") if previous else None
    previous_router_status = previous.get("router_status") if previous else None
    previous_policy_status = previous.get("policy_status") if previous else None

    closed_delta = num_delta(closed, previous_closed)
    open_delta = num_delta(open_count, previous_open)
    pending_delta = num_delta(pending, previous_pending)
    errors_delta = num_delta(errors, previous_errors)

    family_deltas = build_family_deltas(current_families, previous_families)
    changed_families = [r for r in family_deltas if r["changed"]]

    events = []

    if previous is None:
        events.append({
            "event_type": "JOURNAL_INITIALIZED",
            "severity": "INFO",
            "detail": "First state transition journal entry.",
        })

    if closed_delta is not None and closed_delta > 0:
        events.append({
            "event_type": "CLOSED_INCREASED",
            "severity": "INFO",
            "detail": f"closed increased by {closed_delta}: {previous_closed} -> {closed}",
        })

    if errors_delta is not None and errors_delta > 0:
        events.append({
            "event_type": "ERROR_COUNT_INCREASED",
            "severity": "ATTENTION",
            "detail": f"errors increased by {errors_delta}: {previous_errors} -> {errors}",
        })

    if pending_delta is not None and pending_delta > 5:
        events.append({
            "event_type": "PENDING_JUMP",
            "severity": "ATTENTION",
            "detail": f"pending increased by {pending_delta}: {previous_pending} -> {pending}",
        })

    if status_change(stack_status, previous_stack_status):
        events.append({
            "event_type": "STACK_STATUS_CHANGED",
            "severity": "ATTENTION" if stack_status != "STACK_PASS" else "INFO",
            "detail": f"{previous_stack_status} -> {stack_status}",
        })

    if status_change(planner_status, previous_planner_status):
        events.append({
            "event_type": "PLANNER_STATUS_CHANGED",
            "severity": "INFO",
            "detail": f"{previous_planner_status} -> {planner_status}",
        })

    if status_change(maturity_status, previous_maturity_status):
        events.append({
            "event_type": "MATURITY_STATUS_CHANGED",
            "severity": "INFO",
            "detail": f"{previous_maturity_status} -> {maturity_status}",
        })

    if status_change(final_decision, previous_final_decision):
        events.append({
            "event_type": "FINAL_DECISION_CHANGED",
            "severity": "ATTENTION" if final_decision != "DO_NOT_TOUCH_RUNTIME_CONTINUE_REPO_ONLY_OS_INTELLIGENCE" else "INFO",
            "detail": f"{previous_final_decision} -> {final_decision}",
        })

    for r in family_deltas:
        if r["closed_delta"] != "" and r["closed_delta"] > 0:
            events.append({
                "event_type": "FAMILY_CLOSED_INCREASED",
                "severity": "INFO",
                "detail": f"{r['family_key']} closed increased by {r['closed_delta']}",
            })

        if r["errors_delta"] != "" and r["errors_delta"] > 0:
            events.append({
                "event_type": "FAMILY_ERRORS_INCREASED",
                "severity": "ATTENTION",
                "detail": f"{r['family_key']} errors increased by {r['errors_delta']}",
            })

    critical_events = [e for e in events if e["severity"] == "CRITICAL"]
    attention_events = [e for e in events if e["severity"] == "ATTENTION"]

    if critical_events:
        journal_status = "STATE_JOURNAL_CRITICAL_EVENT"
        next_action = "STOP_AND_REVIEW_CRITICAL_TRANSITION"
    elif attention_events:
        journal_status = "STATE_JOURNAL_ATTENTION_EVENT"
        next_action = "REVIEW_ATTENTION_TRANSITIONS"
    else:
        journal_status = "STATE_JOURNAL_READY"
        next_action = "CONTINUE_MONITORING_SAMPLE_TRANSITIONS"

    entry = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),

        "journal_status": journal_status,
        "next_action": next_action,
        "history_count_before_append": len(history),

        "stack_status": stack_status,
        "policy_status": policy_status,
        "planner_status": planner_status,
        "maturity_status": maturity_status,
        "final_decision": final_decision,
        "router_status": router_status,

        "closed": closed,
        "open": open_count,
        "pending": pending,
        "errors": errors,

        "closed_delta": closed_delta,
        "open_delta": open_delta,
        "pending_delta": pending_delta,
        "errors_delta": errors_delta,

        "drift_remaining": as_int(sample.get("drift_remaining")),
        "capital_remaining": as_int(sample.get("capital_remaining")),
        "drift_ready": sample.get("drift_ready") is True,
        "capital_review_ready": sample.get("capital_review_ready") is True,

        "runtime_ok": sample.get("runtime_ok") is True or unified.get("runtime", {}).get("runtime_ok") is True,
        "process_ok": sample.get("process_ok") is True or unified.get("runtime", {}).get("process_watchdog_pass") is True,
        "health_ok": sample.get("health_ok") is True or unified.get("runtime", {}).get("health_ok") is True,
        "errors_acknowledged": sample.get("errors_acknowledged") is True or unified.get("runtime", {}).get("errors_acknowledged") is True,
        "new_errors_since_ack": sample.get("new_errors_since_ack") is True or unified.get("runtime", {}).get("new_errors_since_ack") is True,

        "git_dirty": git_dirty,
        "git_status_short": git_status["stdout"].strip(),

        "event_count": len(events),
        "attention_event_count": len(attention_events),
        "critical_event_count": len(critical_events),
        "events": events,
        "families": current_families,
        "changed_family_count": len(changed_families),

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,
    }

    append_jsonl(MASTER_JOURNAL, entry)

    state_path = out_dir / "state_transition_journal_v1_state.json"
    latest_path = OUT_ROOT / "state_transition_journal_latest.json"
    events_csv = out_dir / "state_transition_journal_v1_events.csv"
    family_csv = out_dir / "state_transition_journal_v1_family_deltas.csv"
    report_path = out_dir / "state_transition_journal_v1_report.md"

    state_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with events_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["event_type", "severity", "detail"])
        writer.writeheader()
        writer.writerows(events)

    with family_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "family_key", "open", "pending", "closed", "errors",
                "open_delta", "pending_delta", "closed_delta", "errors_delta",
                "last_closed_utc", "last_error_utc", "changed",
            ],
        )
        writer.writeheader()
        writer.writerows(family_deltas)

    md = []
    md.append("# Edge Factory OS State Transition Journal v1")
    md.append("")
    md.append(f"journal_status: `{journal_status}`")
    md.append(f"next_action: `{next_action}`")
    md.append(f"history_count_before_append: `{len(history)}`")
    md.append("")
    md.append("## Totals")
    md.append(f"- closed: `{closed}` delta=`{closed_delta}`")
    md.append(f"- open: `{open_count}` delta=`{open_delta}`")
    md.append(f"- pending: `{pending}` delta=`{pending_delta}`")
    md.append(f"- errors: `{errors}` delta=`{errors_delta}`")
    md.append("")
    md.append("## Events")
    if events:
        for e in events:
            md.append(f"- `{e['severity']}` `{e['event_type']}`: {e['detail']}")
    else:
        md.append("- `NONE`")
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

    print("EDGE FACTORY OS STATE TRANSITION JOURNAL v1")
    print("=" * 100)
    print(f"journal_status: {journal_status}")
    print(f"next_action: {next_action}")
    print(f"history_count_before_append: {len(history)}")
    print(f"closed={closed} delta={closed_delta}")
    print(f"open={open_count} delta={open_delta}")
    print(f"pending={pending} delta={pending_delta}")
    print(f"errors={errors} delta={errors_delta}")
    print(f"stack_status={stack_status}")
    print(f"planner_status={planner_status}")
    print(f"maturity_status={maturity_status}")
    print(f"final_decision={final_decision}")
    print(f"router_status={router_status}")
    print(f"event_count={len(events)} attention={len(attention_events)} critical={len(critical_events)}")
    print(f"changed_family_count={len(changed_families)}")
    print(f"git_dirty={git_dirty}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("EVENTS")
    print("-" * 100)
    if events:
        for e in events:
            print(f"[{e['severity']}] {e['event_type']}: {e['detail']}")
    else:
        print("NONE")
    print()
    print("FAMILY DELTAS")
    print("-" * 100)
    for r in family_deltas:
        print(f"{r['family_key']} | openΔ={r['open_delta']} pendingΔ={r['pending_delta']} closedΔ={r['closed_delta']} errorsΔ={r['errors_delta']} changed={r['changed']}")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Master: {MASTER_JOURNAL}")
    print(f"Events: {events_csv}")
    print(f"Family: {family_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
