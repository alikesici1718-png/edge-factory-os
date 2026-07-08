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
OUT_ROOT = WORKSPACE / "edge_factory_os_control_tower_decision_journal_v1"

CONTROL_TOWER_LATEST = WORKSPACE / "edge_factory_os_control_tower_v2" / "control_tower_latest.json"
MASTER_JOURNAL = OUT_ROOT / "control_tower_decision_journal_master.jsonl"

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

def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")

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

def as_int(v, default: int = 0) -> int:
    try:
        if v is None or v == "":
            return default
        return int(v)
    except Exception:
        return default

def event(level: str, key: str, detail: str) -> dict:
    return {
        "level": level,
        "event_key": key,
        "detail": detail,
    }

def build_events(prev: dict | None, cur: dict) -> list[dict]:
    events = []

    if prev is None:
        events.append(event("INFO", "DECISION_JOURNAL_INITIALIZED", "First Control Tower decision journal entry."))
        return events

    fields = [
        ("control_tower_status", "CONTROL_TOWER_STATUS_CHANGED"),
        ("severity", "SEVERITY_CHANGED"),
        ("allowed_scope", "ALLOWED_SCOPE_CHANGED"),
        ("recommended_action", "RECOMMENDED_ACTION_CHANGED"),
        ("stack_status", "STACK_STATUS_CHANGED"),
        ("trigger_status", "TRIGGER_STATUS_CHANGED"),
        ("family_exposure_trend_status", "FAMILY_EXPOSURE_TREND_STATUS_CHANGED"),
        ("family_exposure_profiler_status", "FAMILY_EXPOSURE_PROFILER_STATUS_CHANGED"),
        ("family_balance_status", "FAMILY_BALANCE_STATUS_CHANGED"),
        ("aging_status", "AGING_STATUS_CHANGED"),
    ]

    for field, key in fields:
        old = prev.get(field)
        new = cur.get(field)
        if old != new:
            level = "INFO"
            if field in {"control_tower_status", "severity", "allowed_scope"}:
                level = "ATTENTION" if str(new).endswith("ATTENTION") or new == "ATTENTION" else "INFO"
            events.append(event(level, key, f"{field}: {old} -> {new}"))

    numeric_fields = [
        ("closed", "CLOSED_CHANGED"),
        ("open", "OPEN_CHANGED"),
        ("pending", "PENDING_CHANGED"),
        ("errors", "ERRORS_CHANGED"),
        ("drift_remaining", "DRIFT_REMAINING_CHANGED"),
        ("capital_remaining", "CAPITAL_REMAINING_CHANGED"),
    ]

    for field, key in numeric_fields:
        old = as_int(prev.get(field))
        new = as_int(cur.get(field))
        delta = new - old
        if delta != 0:
            level = "INFO"
            if field == "errors" and delta > 0:
                level = "ATTENTION"
            events.append(event(level, key, f"{field}: {old} -> {new}; delta={delta}"))

    # Threshold transition events.
    old_closed = as_int(prev.get("closed"))
    new_closed = as_int(cur.get("closed"))

    if old_closed < 20 <= new_closed:
        events.append(event("ATTENTION", "DRIFT_REVIEW_THRESHOLD_REACHED", f"closed crossed 20: {old_closed} -> {new_closed}"))

    if old_closed < 50 <= new_closed:
        events.append(event("ATTENTION", "CAPITAL_REVIEW_THRESHOLD_REACHED", f"closed crossed 50: {old_closed} -> {new_closed}"))

    if not events:
        events.append(event("INFO", "NO_DECISION_CHANGE", "Control Tower decision state unchanged."))

    return events

def compact_state(control: dict) -> dict:
    return {
        "generated_at": control.get("generated_at") or now_iso(),

        "control_tower_status": control.get("control_tower_status"),
        "severity": control.get("severity"),
        "allowed_scope": control.get("allowed_scope"),
        "recommended_action": control.get("recommended_action"),
        "reason": control.get("reason"),

        "monitoring_status": control.get("monitoring_status"),
        "action_status": control.get("action_status"),
        "stack_status": control.get("stack_status"),
        "trigger_status": control.get("trigger_status"),
        "primary_trigger": control.get("primary_trigger"),

        "family_exposure_trend_status": control.get("family_exposure_trend_status"),
        "family_exposure_profiler_status": control.get("family_exposure_profiler_status"),
        "family_balance_status": control.get("family_balance_status"),
        "aging_status": control.get("aging_status"),

        "closed": as_int(control.get("closed")),
        "open": as_int(control.get("open")),
        "pending": as_int(control.get("pending")),
        "errors": as_int(control.get("errors")),
        "drift_remaining": as_int(control.get("drift_remaining")),
        "capital_remaining": as_int(control.get("capital_remaining")),

        "runtime_ok": control.get("runtime_ok") is True,
        "process_ok": control.get("process_ok") is True,
        "health_ok": control.get("health_ok") is True,
        "new_errors_since_ack": control.get("new_errors_since_ack") is True,
        "snapshot_mismatch": control.get("snapshot_mismatch") is True,

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,
    }

def main() -> int:
    out_dir = OUT_ROOT / f"control_tower_decision_journal_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    control = read_json(CONTROL_TOWER_LATEST)
    history = read_jsonl(MASTER_JOURNAL)

    git = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git["stdout"].strip())

    cur = compact_state(control)
    prev = history[-1] if history else None

    events = build_events(prev, cur)

    critical_count = len([e for e in events if e["level"] == "CRITICAL"])
    attention_count = len([e for e in events if e["level"] == "ATTENTION"])
    info_count = len([e for e in events if e["level"] == "INFO"])

    if critical_count > 0:
        journal_status = "CONTROL_TOWER_DECISION_JOURNAL_CRITICAL"
        next_action = "REVIEW_CONTROL_TOWER_DECISION_JOURNAL"
    elif attention_count > 0:
        journal_status = "CONTROL_TOWER_DECISION_JOURNAL_ATTENTION"
        next_action = "REVIEW_CONTROL_TOWER_DECISION_CHANGE"
    else:
        journal_status = "CONTROL_TOWER_DECISION_JOURNAL_READY"
        next_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"

    row = dict(cur)
    row["journal_recorded_at"] = now_iso()
    row["journal_status"] = journal_status
    row["event_count"] = len(events)
    row["critical_event_count"] = critical_count
    row["attention_event_count"] = attention_count
    row["info_event_count"] = info_count
    row["events"] = events

    append_jsonl(MASTER_JOURNAL, row)

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),

        "journal_status": journal_status,
        "next_action": next_action,

        "history_count_before_append": len(history),
        "history_count_after_append": len(history) + 1,

        "event_count": len(events),
        "critical_event_count": critical_count,
        "attention_event_count": attention_count,
        "info_event_count": info_count,
        "events": events,

        "current": cur,
        "previous": prev,

        "git_dirty": git_dirty,
        "git_status_short": git["stdout"].strip(),

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,
    }

    state_path = out_dir / "control_tower_decision_journal_v1_state.json"
    latest_path = OUT_ROOT / "control_tower_decision_journal_latest.json"
    events_csv = out_dir / "control_tower_decision_journal_v1_events.csv"
    report_path = out_dir / "control_tower_decision_journal_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with events_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["level", "event_key", "detail"])
        writer.writeheader()
        writer.writerows(events)

    md = []
    md.append("# Edge Factory OS Control Tower Decision Journal v1")
    md.append("")
    md.append(f"journal_status: `{journal_status}`")
    md.append(f"next_action: `{next_action}`")
    md.append(f"history_count_before_append: `{len(history)}`")
    md.append(f"history_count_after_append: `{len(history) + 1}`")
    md.append("")
    md.append("## Current decision")
    for k in [
        "control_tower_status", "severity", "allowed_scope", "recommended_action",
        "closed", "open", "pending", "errors", "drift_remaining", "capital_remaining",
    ]:
        md.append(f"- `{k}`: `{cur.get(k)}`")
    md.append("")
    md.append("## Events")
    for e in events:
        md.append(f"- `{e['level']}` `{e['event_key']}`: {e['detail']}")
    md.append("")
    md.append("## Safety")
    md.append("- runtime_touch_allowed: `False`")
    md.append("- launcher_allowed: `False`")
    md.append("- patch_runtime_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    md.append("- real_orders_allowed: `False`")
    md.append("- execution_performed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS CONTROL TOWER DECISION JOURNAL v1")
    print("=" * 100)
    print(f"journal_status: {journal_status}")
    print(f"next_action: {next_action}")
    print(f"history_count_before_append: {len(history)}")
    print(f"history_count_after_append: {len(history) + 1}")
    print(f"event_count={len(events)} attention={attention_count} critical={critical_count} info={info_count}")
    print(f"git_dirty={git_dirty}")
    print()
    print("CURRENT DECISION")
    print("-" * 100)
    print(f"control_tower_status={cur.get('control_tower_status')}")
    print(f"severity={cur.get('severity')}")
    print(f"allowed_scope={cur.get('allowed_scope')}")
    print(f"recommended_action={cur.get('recommended_action')}")
    print(f"reason={cur.get('reason')}")
    print(f"closed={cur.get('closed')} open={cur.get('open')} pending={cur.get('pending')} errors={cur.get('errors')}")
    print(f"drift_remaining={cur.get('drift_remaining')} capital_remaining={cur.get('capital_remaining')}")
    print(f"runtime_ok={cur.get('runtime_ok')} process_ok={cur.get('process_ok')} health_ok={cur.get('health_ok')}")
    print(f"new_errors_since_ack={cur.get('new_errors_since_ack')} snapshot_mismatch={cur.get('snapshot_mismatch')}")
    print()
    print("EVENTS")
    print("-" * 100)
    for e in events:
        print(f"[{e['level']}] {e['event_key']} | {e['detail']}")
    print()
    print("SAFETY")
    print("-" * 100)
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("real_orders_allowed  : False")
    print("execution_performed  : False")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Master: {MASTER_JOURNAL}")
    print(f"Events: {events_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
