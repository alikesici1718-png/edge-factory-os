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
OUT_ROOT = WORKSPACE / "edge_factory_os_cycle_scheduler_policy_v1"

CYCLE_LATEST = WORKSPACE / "edge_factory_os_control_tower_cycle_runner_v1" / "control_tower_cycle_runner_latest.json"
CONTROL_LATEST = WORKSPACE / "edge_factory_os_control_tower_v2" / "control_tower_latest.json"
JOURNAL_LATEST = WORKSPACE / "edge_factory_os_control_tower_decision_journal_v1" / "control_tower_decision_journal_latest.json"
JOURNAL_MASTER = WORKSPACE / "edge_factory_os_control_tower_decision_journal_v1" / "control_tower_decision_journal_master.jsonl"

DRIFT_MIN_CLOSED = 20
CAPITAL_MIN_CLOSED = 50

MAIN_CYCLE_COMMAND = r'python -u .\tools\edge_factory_os_control_tower_cycle_runner_v1.py'
CONTROL_TOWER_COMMAND = r'python -u .\tools\edge_factory_os_control_tower_v2.py'
JOURNAL_COMMAND = r'python -u .\tools\edge_factory_os_control_tower_decision_journal_v1.py'

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

def as_int(v, default: int = 0) -> int:
    try:
        if v is None or v == "":
            return default
        return int(v)
    except Exception:
        return default

def recent_closed_delta(history: list[dict], lookback: int = 5) -> int:
    if len(history) < 2:
        return 0
    h = history[-lookback:] if len(history) > lookback else history
    return as_int(h[-1].get("closed")) - as_int(h[0].get("closed"))

def recent_error_delta(history: list[dict], lookback: int = 5) -> int:
    if len(history) < 2:
        return 0
    h = history[-lookback:] if len(history) > lookback else history
    return as_int(h[-1].get("errors")) - as_int(h[0].get("errors"))

def add_rule(rows: list[dict], priority: int, key: str, condition: bool, level: str, cadence_mode: str, recommended_command: str, reason: str) -> None:
    rows.append({
        "priority": priority,
        "rule_key": key,
        "condition_met": bool(condition),
        "level": level,
        "cadence_mode": cadence_mode,
        "recommended_command": recommended_command,
        "reason": reason,
    })

def decide(active_rules: list[dict], git_dirty: bool) -> tuple[str, str, str, str, str]:
    if git_dirty:
        return (
            "CYCLE_SCHEDULER_REPO_ATTENTION",
            "ATTENTION",
            "REPO_CLEANUP_FIRST",
            "git status --short",
            "Repo is dirty; finish checkpoint before relying on cadence policy.",
        )

    active = sorted(active_rules, key=lambda x: x["priority"], reverse=True)

    if not active:
        return (
            "CYCLE_SCHEDULER_COLLECT_ONLY",
            "OK",
            "NORMAL_COLLECT_ONLY",
            MAIN_CYCLE_COMMAND,
            "No active escalation rule; keep collecting sample.",
        )

    top = active[0]

    return (
        f"CYCLE_SCHEDULER_{top['rule_key']}",
        top["level"],
        top["cadence_mode"],
        top["recommended_command"],
        top["reason"],
    )

def main() -> int:
    out_dir = OUT_ROOT / f"cycle_scheduler_policy_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    cycle = read_json(CYCLE_LATEST)
    control = read_json(CONTROL_LATEST)
    journal = read_json(JOURNAL_LATEST)
    history = read_jsonl(JOURNAL_MASTER)

    git = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git["stdout"].strip())

    cycle_status = str(cycle.get("cycle_status") or "")
    cycle_severity = str(cycle.get("severity") or "")
    cycle_scope = str(cycle.get("allowed_scope") or "")
    cycle_action = str(cycle.get("recommended_action") or "")

    control_status = str(control.get("control_tower_status") or "")
    control_severity = str(control.get("severity") or "")
    control_scope = str(control.get("allowed_scope") or "")

    journal_status = str(journal.get("journal_status") or "")
    journal_attention_count = as_int(journal.get("attention_event_count"))
    journal_critical_count = as_int(journal.get("critical_event_count"))

    closed = as_int(cycle.get("closed", control.get("closed")))
    open_count = as_int(cycle.get("open", control.get("open")))
    pending = as_int(cycle.get("pending", control.get("pending")))
    errors = as_int(cycle.get("errors", control.get("errors")))

    drift_remaining = max(0, DRIFT_MIN_CLOSED - closed)
    capital_remaining = max(0, CAPITAL_MIN_CLOSED - closed)

    runtime_ok = cycle.get("runtime_ok") is True or control.get("runtime_ok") is True
    process_ok = cycle.get("process_ok") is True or control.get("process_ok") is True
    health_ok = cycle.get("health_ok") is True or control.get("health_ok") is True
    new_errors_since_ack = cycle.get("new_errors_since_ack") is True or control.get("new_errors_since_ack") is True
    snapshot_mismatch = cycle.get("snapshot_mismatch") is True or control.get("snapshot_mismatch") is True

    trigger_status = str(cycle.get("trigger_status") or control.get("trigger_status") or "")
    primary_trigger = str(cycle.get("primary_trigger") or control.get("primary_trigger") or "")
    family_trend_status = str(cycle.get("family_exposure_trend_status") or control.get("family_exposure_trend_status") or "")
    family_profiler_status = str(cycle.get("family_exposure_profiler_status") or control.get("family_exposure_profiler_status") or "")
    family_balance_status = str(cycle.get("family_balance_status") or control.get("family_balance_status") or "")
    aging_status = str(cycle.get("aging_status") or control.get("aging_status") or "")

    closed_delta_5 = recent_closed_delta(history, 5)
    error_delta_5 = recent_error_delta(history, 5)

    rules: list[dict] = []

    add_rule(
        rules,
        10000,
        "RUNTIME_HEALTH_REVIEW",
        not runtime_ok or not process_ok or not health_ok,
        "CRITICAL",
        "READ_ONLY_IMMEDIATE_REVIEW",
        CONTROL_TOWER_COMMAND,
        f"runtime_ok={runtime_ok}, process_ok={process_ok}, health_ok={health_ok}",
    )

    add_rule(
        rules,
        9500,
        "NEW_ERRORS_REVIEW",
        new_errors_since_ack or error_delta_5 > 0,
        "ATTENTION",
        "READ_ONLY_ERROR_REVIEW",
        MAIN_CYCLE_COMMAND,
        f"new_errors_since_ack={new_errors_since_ack}; recent_error_delta={error_delta_5}",
    )

    add_rule(
        rules,
        9300,
        "SNAPSHOT_REFRESH",
        snapshot_mismatch,
        "ATTENTION",
        "READ_ONLY_REFRESH",
        MAIN_CYCLE_COMMAND,
        "snapshot_mismatch=True",
    )

    add_rule(
        rules,
        9000,
        "JOURNAL_CRITICAL_REVIEW",
        journal_critical_count > 0 or journal_status == "CONTROL_TOWER_DECISION_JOURNAL_CRITICAL",
        "CRITICAL",
        "READ_ONLY_JOURNAL_REVIEW",
        JOURNAL_COMMAND,
        f"journal_status={journal_status}; critical={journal_critical_count}",
    )

    add_rule(
        rules,
        8500,
        "CAPITAL_REVIEW_READY_READ_ONLY",
        closed >= CAPITAL_MIN_CLOSED,
        "INFO",
        "READ_ONLY_CAPITAL_REVIEW",
        MAIN_CYCLE_COMMAND,
        f"closed={closed}/{CAPITAL_MIN_CLOSED}",
    )

    add_rule(
        rules,
        8000,
        "DRIFT_REVIEW_READY_READ_ONLY",
        closed >= DRIFT_MIN_CLOSED and closed < CAPITAL_MIN_CLOSED,
        "INFO",
        "READ_ONLY_DRIFT_REVIEW",
        MAIN_CYCLE_COMMAND,
        f"closed={closed}/{DRIFT_MIN_CLOSED}",
    )

    add_rule(
        rules,
        7000,
        "DRIFT_THRESHOLD_APPROACHING",
        0 < drift_remaining <= 3,
        "INFO",
        "CLOSE_TO_DRIFT_THRESHOLD",
        MAIN_CYCLE_COMMAND,
        f"closed={closed}/20; drift_remaining={drift_remaining}",
    )

    add_rule(
        rules,
        6500,
        "WATCH_ONLY_FAMILY_ATTENTION",
        (
            "ATTENTION" in family_trend_status
            or "ATTENTION" in family_profiler_status
            or "ATTENTION" in family_balance_status
            or trigger_status == "TRIGGER_ENGINE_ATTENTION"
        ),
        "ATTENTION",
        "WATCH_ONLY_FAMILY_BALANCE",
        MAIN_CYCLE_COMMAND,
        f"trigger={trigger_status}/{primary_trigger}; trend={family_trend_status}; profiler={family_profiler_status}; balance={family_balance_status}",
    )

    add_rule(
        rules,
        5000,
        "COLLECTING_WITH_INFO",
        (
            "INFO" in family_trend_status
            or "INFO" in family_profiler_status
            or "COLLECTING" in family_balance_status
            or "INFO" in aging_status
        ),
        "INFO",
        "NORMAL_COLLECT_ONLY_WITH_INFO",
        MAIN_CYCLE_COMMAND,
        f"trend={family_trend_status}; profiler={family_profiler_status}; balance={family_balance_status}; aging={aging_status}",
    )

    add_rule(
        rules,
        1000,
        "SAMPLE_BELOW_THRESHOLDS",
        closed < DRIFT_MIN_CLOSED,
        "INFO",
        "NORMAL_COLLECT_ONLY",
        MAIN_CYCLE_COMMAND,
        f"closed={closed}/20; drift_remaining={drift_remaining}; capital_remaining={capital_remaining}; recent_closed_delta={closed_delta_5}",
    )

    active_rules = [r for r in rules if r["condition_met"]]
    scheduler_status, severity, cadence_mode, recommended_command, reason = decide(active_rules, git_dirty)

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),

        "scheduler_status": scheduler_status,
        "severity": severity,
        "cadence_mode": cadence_mode,
        "recommended_command": recommended_command,
        "reason": reason,

        "cycle_status": cycle_status,
        "cycle_severity": cycle_severity,
        "cycle_allowed_scope": cycle_scope,
        "cycle_recommended_action": cycle_action,

        "control_tower_status": control_status,
        "control_tower_severity": control_severity,
        "control_tower_allowed_scope": control_scope,

        "journal_status": journal_status,
        "journal_attention_event_count": journal_attention_count,
        "journal_critical_event_count": journal_critical_count,
        "history_count": len(history),
        "recent_closed_delta_5": closed_delta_5,
        "recent_error_delta_5": error_delta_5,

        "trigger_status": trigger_status,
        "primary_trigger": primary_trigger,
        "family_exposure_trend_status": family_trend_status,
        "family_exposure_profiler_status": family_profiler_status,
        "family_balance_status": family_balance_status,
        "aging_status": aging_status,

        "closed": closed,
        "open": open_count,
        "pending": pending,
        "errors": errors,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,

        "runtime_ok": runtime_ok,
        "process_ok": process_ok,
        "health_ok": health_ok,
        "new_errors_since_ack": new_errors_since_ack,
        "snapshot_mismatch": snapshot_mismatch,

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

        "rules": sorted(rules, key=lambda x: x["priority"], reverse=True),
        "active_rules": sorted(active_rules, key=lambda x: x["priority"], reverse=True),
    }

    state_path = out_dir / "cycle_scheduler_policy_v1_state.json"
    latest_path = OUT_ROOT / "cycle_scheduler_policy_latest.json"
    rules_csv = out_dir / "cycle_scheduler_policy_v1_rules.csv"
    active_csv = out_dir / "cycle_scheduler_policy_v1_active_rules.csv"
    report_path = out_dir / "cycle_scheduler_policy_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    fieldnames = [
        "priority", "rule_key", "condition_met", "level",
        "cadence_mode", "recommended_command", "reason",
    ]

    with rules_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(state["rules"])

    with active_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(state["active_rules"])

    md = []
    md.append("# Edge Factory OS Cycle Scheduler Policy v1")
    md.append("")
    md.append(f"scheduler_status: `{scheduler_status}`")
    md.append(f"severity: `{severity}`")
    md.append(f"cadence_mode: `{cadence_mode}`")
    md.append(f"recommended_command: `{recommended_command}`")
    md.append(f"reason: `{reason}`")
    md.append("")
    md.append("## Summary")
    for k in [
        "cycle_status", "control_tower_status", "journal_status",
        "closed", "open", "pending", "errors", "drift_remaining",
        "capital_remaining", "recent_closed_delta_5", "recent_error_delta_5",
    ]:
        md.append(f"- `{k}`: `{state.get(k)}`")
    md.append("")
    md.append("## Active rules")
    if active_rules:
        for r in sorted(active_rules, key=lambda x: x["priority"], reverse=True):
            md.append(f"- `{r['level']}` `{r['rule_key']}` mode=`{r['cadence_mode']}` reason=`{r['reason']}`")
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
    md.append("- real_orders_allowed: `False`")
    md.append("- execution_performed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS CYCLE SCHEDULER POLICY v1")
    print("=" * 100)
    print(f"scheduler_status: {scheduler_status}")
    print(f"severity: {severity}")
    print(f"cadence_mode: {cadence_mode}")
    print(f"recommended_command: {recommended_command}")
    print(f"reason: {reason}")
    print(f"git_dirty={git_dirty}")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(f"cycle_status={cycle_status}")
    print(f"control_tower_status={control_status}")
    print(f"journal_status={journal_status}")
    print(f"trigger_status={trigger_status} primary_trigger={primary_trigger}")
    print(f"family_exposure_trend_status={family_trend_status}")
    print(f"family_exposure_profiler_status={family_profiler_status}")
    print(f"family_balance_status={family_balance_status}")
    print(f"aging_status={aging_status}")
    print(f"closed={closed} open={open_count} pending={pending} errors={errors}")
    print(f"drift_remaining={drift_remaining} capital_remaining={capital_remaining}")
    print(f"recent_closed_delta_5={closed_delta_5} recent_error_delta_5={error_delta_5}")
    print(f"runtime_ok={runtime_ok} process_ok={process_ok} health_ok={health_ok}")
    print(f"new_errors_since_ack={new_errors_since_ack} snapshot_mismatch={snapshot_mismatch}")
    print()
    print("ACTIVE RULES")
    print("-" * 100)
    if active_rules:
        for r in sorted(active_rules, key=lambda x: x["priority"], reverse=True):
            print(f"[{r['level']}] {r['rule_key']} | mode={r['cadence_mode']} | command={r['recommended_command']} | reason={r['reason']}")
    else:
        print("NONE")
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
    print(f"Rules : {rules_csv}")
    print(f"Active: {active_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
