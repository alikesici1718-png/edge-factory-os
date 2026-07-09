#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_monitoring_stack_runner_v5"

TOOLS = [
    {
        "step_key": "standard_stack",
        "cmd": [sys.executable, "-u", r".\tools\edge_factory_os_standard_stack_runner_v1.py"],
        "required_marker_any": ["EDGE FACTORY OS STANDARD STACK RUNNER v1", "stack_status"],
        "pass_marker": "stack_status  : STACK_PASS",
        "dirty_expected_fail": True,
    },
    {
        "step_key": "sample_maturity",
        "cmd": [sys.executable, "-u", r".\tools\edge_factory_os_sample_maturity_watcher_v1.py"],
        "required_marker_any": ["EDGE FACTORY OS SAMPLE MATURITY WATCHER v1", "maturity_status:"],
        "pass_marker": "maturity_status:",
        "dirty_expected_fail": False,
    },
    {
        "step_key": "open_pending_aging_v2",
        "cmd": [sys.executable, "-u", r".\tools\edge_factory_os_open_pending_aging_watcher_v2.py"],
        "required_marker_any": ["EDGE FACTORY OS OPEN/PENDING AGING WATCHER v2", "aging_status:"],
        "pass_marker": "aging_status:",
        "dirty_expected_fail": False,
    },
    {
        "step_key": "state_transition_journal",
        "cmd": [sys.executable, "-u", r".\tools\edge_factory_os_state_transition_journal_v1.py"],
        "required_marker_any": ["EDGE FACTORY OS STATE TRANSITION JOURNAL v1", "journal_status:"],
        "pass_marker": "journal_status:",
        "dirty_expected_fail": False,
    },
    {
        "step_key": "trigger_engine",
        "cmd": [sys.executable, "-u", r".\tools\edge_factory_os_trigger_engine_v1.py"],
        "required_marker_any": ["EDGE FACTORY OS TRIGGER ENGINE v1", "trigger_status:"],
        "pass_marker": "trigger_status:",
        "dirty_expected_fail": False,
    },
    {
        "step_key": "family_sample_balance",
        "cmd": [sys.executable, "-u", r".\tools\edge_factory_os_family_sample_balance_watcher_v1.py"],
        "required_marker_any": ["EDGE FACTORY OS FAMILY SAMPLE BALANCE WATCHER v1", "balance_status:"],
        "pass_marker": "balance_status:",
        "dirty_expected_fail": False,
    },
    {
        "step_key": "family_exposure_profiler",
        "cmd": [sys.executable, "-u", r".\tools\edge_factory_os_family_exposure_profiler_v1.py"],
        "required_marker_any": ["EDGE FACTORY OS FAMILY EXPOSURE PROFILER v1", "profiler_status:"],
        "pass_marker": "profiler_status:",
        "dirty_expected_fail": False,
    },
]

LATEST_PATHS = {
    "standard_stack": WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json",
    "sample_maturity": WORKSPACE / "edge_factory_os_sample_maturity_watcher_v1" / "sample_maturity_watcher_latest.json",
    "open_pending_aging": WORKSPACE / "edge_factory_os_open_pending_aging_watcher_v2" / "open_pending_aging_watcher_latest.json",
    "state_transition_journal": WORKSPACE / "edge_factory_os_state_transition_journal_v1" / "state_transition_journal_latest.json",
    "trigger_engine": WORKSPACE / "edge_factory_os_trigger_engine_v1" / "os_trigger_engine_latest.json",
    "family_sample_balance": WORKSPACE / "edge_factory_os_family_sample_balance_watcher_v1" / "family_sample_balance_watcher_latest.json",
    "family_exposure_profiler": WORKSPACE / "edge_factory_os_family_exposure_profiler_v1" / "family_exposure_profiler_latest.json",
}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e), "__path__": str(path)}

def run_cmd(cmd: list[str], cwd: Path, timeout: int = 240) -> dict:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
        return {
            "returncode": p.returncode,
            "stdout": p.stdout or "",
            "stderr": p.stderr or "",
            "exception": "",
        }
    except Exception as e:
        return {
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "exception": repr(e),
        }

def git_status() -> tuple[bool, str]:
    r = run_cmd(["git", "status", "--short"], cwd=REPO, timeout=40)
    out = (r.get("stdout") or "").strip()
    return bool(out), out

def marker_any(stdout: str, markers: list[str]) -> bool:
    return any(m in stdout for m in markers)

def marker_one(stdout: str, marker: str) -> bool:
    if not marker:
        return True
    return marker in stdout

def as_int(v, default: int = 0) -> int:
    try:
        if v is None or v == "":
            return default
        return int(v)
    except Exception:
        return default

def classify_step(step: dict, result: dict, repo_dirty_after: bool) -> tuple[str, bool, str]:
    stdout = result.get("stdout", "")
    exception = result.get("exception", "")
    returncode = result.get("returncode")

    required_marker_seen = marker_any(stdout, step.get("required_marker_any", []))
    pass_marker_seen = marker_one(stdout, step.get("pass_marker", ""))

    if exception:
        return "STEP_EXCEPTION", False, exception

    if returncode == 0 and pass_marker_seen:
        return "PASS", True, "returncode=0 and pass marker seen"

    if step.get("dirty_expected_fail") and repo_dirty_after and required_marker_seen:
        return "EXPECTED_REPO_DIRTY_ATTENTION", True, "repo dirty can make this step report non-pass; required marker seen"

    if returncode != 0 and required_marker_seen:
        return "RETURNCODE_ATTENTION_MARKER_SEEN", True, "non-zero returncode but required marker seen; inspect stderr_tail"

    if returncode == 0 and required_marker_seen:
        return "MARKER_ONLY_PASS", True, "returncode=0 and required marker seen"

    if stdout or result.get("stderr", ""):
        return "OUTPUT_WITHOUT_REQUIRED_MARKER", False, "process produced output but required marker was not found"

    return "NO_OUTPUT_OR_MARKER", False, "no useful output/marker found"

def summarize_latest() -> dict:
    stack = read_json(LATEST_PATHS["standard_stack"])
    sample = read_json(LATEST_PATHS["sample_maturity"])
    aging = read_json(LATEST_PATHS["open_pending_aging"])
    journal = read_json(LATEST_PATHS["state_transition_journal"])
    trigger = read_json(LATEST_PATHS["trigger_engine"])
    balance = read_json(LATEST_PATHS["family_sample_balance"])
    profiler = read_json(LATEST_PATHS["family_exposure_profiler"])

    primary_trigger = trigger.get("primary_trigger", {})
    if not isinstance(primary_trigger, dict):
        primary_trigger = {}

    return {
        "stack_status": stack.get("stack_status"),
        "final_decision": stack.get("final_decision"),

        "sample_maturity_status": sample.get("maturity_status"),
        "closed": as_int(sample.get("closed")),
        "open": as_int(sample.get("open")),
        "pending": as_int(sample.get("pending")),
        "errors": as_int(sample.get("errors")),
        "drift_remaining": as_int(sample.get("drift_remaining")),
        "capital_remaining": as_int(sample.get("capital_remaining")),
        "runtime_ok": sample.get("runtime_ok") is True,
        "process_ok": sample.get("process_ok") is True,
        "health_ok": sample.get("health_ok") is True,
        "new_errors_since_ack": sample.get("new_errors_since_ack") is True,

        "aging_status": aging.get("aging_status"),
        "snapshot_mismatch": aging.get("snapshot_mismatch"),
        "direct_total_open": aging.get("direct_total_open"),
        "direct_total_pending": aging.get("direct_total_pending"),
        "attention_queue_count": as_int(aging.get("attention_queue_count")),
        "info_queue_count": as_int(aging.get("info_queue_count")),
        "consistency_attention_count": as_int(aging.get("consistency_attention_count")),
        "consistency_info_count": as_int(aging.get("consistency_info_count")),

        "journal_status": journal.get("journal_status"),
        "journal_event_count": as_int(journal.get("event_count")),
        "journal_attention_event_count": as_int(journal.get("attention_event_count")),
        "journal_critical_event_count": as_int(journal.get("critical_event_count")),

        "trigger_status": trigger.get("trigger_status"),
        "primary_trigger": primary_trigger.get("trigger_key"),
        "primary_trigger_severity": primary_trigger.get("severity"),
        "primary_recommended_action": primary_trigger.get("recommended_action"),
        "primary_recommended_command": primary_trigger.get("recommended_command"),

        "family_balance_status": balance.get("balance_status"),
        "closed_family_count": balance.get("closed_family_count"),
        "zero_closed_with_exposure_count": balance.get("zero_closed_with_exposure_count"),
        "attention_family_count": as_int(balance.get("attention_family_count")),
        "info_family_count": as_int(balance.get("info_family_count")),
        "max_closed_share": balance.get("max_closed_share"),
        "family_exposure_profiler_status": profiler.get("profiler_status"),
        "family_exposure_attention_count": as_int(profiler.get("attention_family_count")),
        "family_exposure_info_count": as_int(profiler.get("info_family_count")),
        "family_exposure_next_action": profiler.get("next_action"),
    }

def build_alerts(summary: dict, step_rows: list[dict], git_dirty: bool) -> list[dict]:
    alerts = []

    def add(priority: int, level: str, key: str, reason: str, action: str) -> None:
        alerts.append({
            "priority": priority,
            "level": level,
            "key": key,
            "reason": reason,
            "action": action,
        })

    hard_failed_steps = [s for s in step_rows if not s["evidence_ok"]]
    returncode_attention_steps = [s for s in step_rows if s["step_class"] == "RETURNCODE_ATTENTION_MARKER_SEEN"]

    if git_dirty:
        add(10000, "ATTENTION", "REPO_DIRTY", "Repo has uncommitted changes.", "COMMIT_OR_REVIEW_REPO_CHANGES")

    if hard_failed_steps:
        add(9500, "ATTENTION", "MONITORING_STEP_EVIDENCE_MISSING", "At least one monitoring step lacked required evidence marker.", "REVIEW_FAILED_MONITORING_STEP")

    if returncode_attention_steps:
        add(9300, "ATTENTION", "MONITORING_STEP_RETURNCODE_ATTENTION", "Some steps emitted expected markers but returned non-zero.", "REVIEW_STEP_STDERR_TAILS")

    if summary.get("stack_status") != "STACK_PASS":
        # If repo dirty, this is usually explained by REPO_DIRTY.
        level = "ATTENTION"
        key = "STANDARD_STACK_NOT_PASS"
        reason = f"stack_status={summary.get('stack_status')}"
        action = "REVIEW_STANDARD_STACK"
        add(9000, level, key, reason, action)

    if not summary.get("runtime_ok") or not summary.get("process_ok") or not summary.get("health_ok"):
        add(
            8500,
            "CRITICAL",
            "RUNTIME_HEALTH_NOT_OK",
            f"runtime_ok={summary.get('runtime_ok')}, process_ok={summary.get('process_ok')}, health_ok={summary.get('health_ok')}",
            "RUN_READ_ONLY_RUNTIME_DIAGNOSTICS",
        )

    if summary.get("new_errors_since_ack"):
        add(8200, "ATTENTION", "NEW_ERRORS_SINCE_ACK", "New errors appeared since acknowledgement.", "RUN_ERROR_CLASSIFIER_AND_ACKNOWLEDGER")

    if summary.get("snapshot_mismatch"):
        add(7900, "ATTENTION", "SNAPSHOT_MISMATCH", "Sample watcher and direct CSV counts do not match.", "REFRESH_SAMPLE_AND_AGING_SNAPSHOT_READ_ONLY")

    if summary.get("journal_critical_event_count", 0) > 0:
        add(7600, "CRITICAL", "JOURNAL_CRITICAL_EVENT", "State transition journal has critical event(s).", "REVIEW_STATE_TRANSITION_JOURNAL")

    if summary.get("journal_attention_event_count", 0) > 0:
        add(7400, "ATTENTION", "JOURNAL_ATTENTION_EVENT", "State transition journal has attention event(s).", "REVIEW_STATE_TRANSITION_JOURNAL")

    if summary.get("trigger_status") == "TRIGGER_ENGINE_CRITICAL":
        add(7200, "CRITICAL", "TRIGGER_ENGINE_CRITICAL", f"primary_trigger={summary.get('primary_trigger')}", "REVIEW_TRIGGER_ENGINE_CRITICAL")

    if summary.get("trigger_status") == "TRIGGER_ENGINE_ATTENTION":
        add(
            7000,
            "ATTENTION",
            "TRIGGER_ENGINE_ATTENTION",
            f"primary_trigger={summary.get('primary_trigger')}",
            summary.get("primary_recommended_action") or "REVIEW_TRIGGER_ENGINE_ATTENTION",
        )

    if summary.get("aging_status") in {"OPEN_PENDING_AGING_ATTENTION", "OPEN_PENDING_CONSISTENCY_ATTENTION"}:
        add(6800, "ATTENTION", "OPEN_PENDING_AGING_OR_CONSISTENCY_ATTENTION", f"aging_status={summary.get('aging_status')}", "REVIEW_OPEN_PENDING_AGE_OR_CONSISTENCY")

    if summary.get("aging_status") in {"OPEN_PENDING_AGING_INFO", "OPEN_PENDING_CONSISTENCY_INFO"}:
        add(5000, "INFO", "OPEN_PENDING_AGING_INFO", f"aging_status={summary.get('aging_status')}", "CONTINUE_MONITORING_OPEN_PENDING_AGE")

    if summary.get("family_balance_status") == "FAMILY_SAMPLE_BALANCE_ATTENTION":
        add(6600, "ATTENTION", "FAMILY_SAMPLE_BALANCE_ATTENTION", "Family balance watcher reports attention.", "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE")

    if summary.get("family_exposure_profiler_status") == "FAMILY_EXPOSURE_ATTENTION":
        add(
            6700,
            "ATTENTION",
            "FAMILY_EXPOSURE_ATTENTION",
            f"attention_family_count={summary.get('family_exposure_attention_count')}",
            summary.get("family_exposure_next_action") or "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
        )

    if summary.get("family_balance_status") == "FAMILY_SAMPLE_BALANCE_COLLECTING":
        add(4500, "INFO", "FAMILY_SAMPLE_BALANCE_COLLECTING", "Family balance is still collecting sample.", "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH")

    if summary.get("closed", 0) >= 50:
        add(6400, "INFO", "CAPITAL_REVIEW_READY_READ_ONLY", "closed >= 50", "RUN_CAPITAL_REVIEW_READ_ONLY")
    elif summary.get("closed", 0) >= 20:
        add(6300, "INFO", "DRIFT_REVIEW_READY_READ_ONLY", "closed >= 20", "RUN_DRIFT_REVIEW_READ_ONLY")
    else:
        add(1000, "INFO", "SAMPLE_BELOW_REVIEW_THRESHOLDS", f"closed={summary.get('closed')}, drift_remaining={summary.get('drift_remaining')}, capital_remaining={summary.get('capital_remaining')}", "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH")

    return sorted(alerts, key=lambda x: x["priority"], reverse=True)

def decide_from_alerts(alerts: list[dict], git_dirty: bool) -> tuple[str, str, str, str]:
    if not alerts:
        return "MONITORING_STACK_OK_COLLECTING", "OK", "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH", "No alerts."

    critical_alerts = sorted(
        [a for a in alerts if a["level"] == "CRITICAL"],
        key=lambda x: x["priority"],
        reverse=True,
    )
    attention_alerts = sorted(
        [a for a in alerts if a["level"] == "ATTENTION"],
        key=lambda x: x["priority"],
        reverse=True,
    )
    info_alerts = sorted(
        [a for a in alerts if a["level"] == "INFO"],
        key=lambda x: x["priority"],
        reverse=True,
    )

    # Hard runtime/journal criticals must never be hidden by repo dirtiness.
    hard_critical_keys = {
        "RUNTIME_HEALTH_NOT_OK",
        "JOURNAL_CRITICAL_EVENT",
    }
    hard_criticals = [a for a in critical_alerts if a["key"] in hard_critical_keys]
    if hard_criticals:
        c = hard_criticals[0]
        return f"MONITORING_STACK_{c['key']}", "CRITICAL", c["action"], c["reason"]

    # Repo dirtiness is a workflow blocker, but not a runtime failure.
    if git_dirty:
        return "MONITORING_STACK_REPO_ATTENTION", "ATTENTION", "COMMIT_OR_REVIEW_REPO_CHANGES", "Repo is dirty; commit/review before trusting final monitoring status."

    # After repo is clean, any remaining critical beats all attention/info.
    if critical_alerts:
        c = critical_alerts[0]
        return f"MONITORING_STACK_{c['key']}", "CRITICAL", c["action"], c["reason"]

    # Attention should not be hidden under OK.
    if attention_alerts:
        a = attention_alerts[0]
        return f"MONITORING_STACK_{a['key']}", "ATTENTION", a["action"], a["reason"]

    if info_alerts:
        a = info_alerts[0]
        if a["key"] == "SAMPLE_BELOW_REVIEW_THRESHOLDS":
            return "MONITORING_STACK_OK_COLLECTING", "OK", a["action"], a["reason"]
        return f"MONITORING_STACK_OK_WITH_{a['key']}", "INFO", a["action"], a["reason"]

    return "MONITORING_STACK_OK_COLLECTING", "OK", "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH", "No critical/attention alerts."


def main() -> int:
    out_dir = OUT_ROOT / f"monitoring_stack_runner_v5_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    git_dirty_before, git_short_before = git_status()
    step_rows = []

    for step in TOOLS:
        result = run_cmd(step["cmd"], cwd=REPO)
        git_dirty_after_step, _ = git_status()

        step_class, evidence_ok, class_reason = classify_step(step, result, git_dirty_after_step)
        stdout = result.get("stdout", "") or ""
        stderr = result.get("stderr", "") or ""

        step_rows.append({
            "step_key": step["step_key"],
            "cmd": " ".join(step["cmd"]),
            "returncode": result.get("returncode"),
            "step_class": step_class,
            "evidence_ok": bool(evidence_ok),
            "class_reason": class_reason,
            "required_marker_seen": marker_any(stdout, step.get("required_marker_any", [])),
            "pass_marker_seen": marker_one(stdout, step.get("pass_marker", "")),
            "dirty_expected_fail": bool(step.get("dirty_expected_fail")),
            "stdout_tail": stdout[-2500:],
            "stderr_tail": stderr[-2500:],
            "exception": result.get("exception", ""),
        })

    git_dirty_after, git_short_after = git_status()
    summary = summarize_latest()
    alerts = build_alerts(summary, step_rows, git_dirty_after)
    monitoring_status, severity, next_action, reason = decide_from_alerts(alerts, git_dirty_after)

    # Preview useful on first uncommitted run.
    # Suppress alerts that are clearly caused by repo dirty -> stack fail -> trigger stack review.
    clean_suppressed_keys = {"REPO_DIRTY", "STANDARD_STACK_NOT_PASS"}
    if git_dirty_after and summary.get("primary_trigger") == "STACK_REVIEW_REQUIRED":
        clean_suppressed_keys.add("TRIGGER_ENGINE_CRITICAL")
        clean_suppressed_keys.add("JOURNAL_ATTENTION_EVENT")

    clean_alerts = [a for a in alerts if a["key"] not in clean_suppressed_keys]
    clean_preview_status, clean_preview_severity, clean_preview_action, clean_preview_reason = decide_from_alerts(clean_alerts, False)

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),

        "monitoring_status": monitoring_status,
        "severity": severity,
        "next_action": next_action,
        "reason": reason,

        "clean_repo_decision_preview": {
            "monitoring_status": clean_preview_status,
            "severity": clean_preview_severity,
            "next_action": clean_preview_action,
            "reason": clean_preview_reason,
        },

        "step_count": len(step_rows),
        "hard_failed_step_count": len([s for s in step_rows if not s["evidence_ok"]]),
        "returncode_attention_step_count": len([s for s in step_rows if s["step_class"] == "RETURNCODE_ATTENTION_MARKER_SEEN"]),
        "expected_repo_dirty_attention_step_count": len([s for s in step_rows if s["step_class"] == "EXPECTED_REPO_DIRTY_ATTENTION"]),

        "git_dirty_before": git_dirty_before,
        "git_status_short_before": git_short_before,
        "git_dirty": git_dirty_after,
        "git_status_short": git_short_after,

        "summary": summary,
        "alert_count": len(alerts),
        "alerts": alerts,
        "steps": step_rows,

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,
    }

    state_path = out_dir / "monitoring_stack_runner_v5_state.json"
    latest_path = OUT_ROOT / "monitoring_stack_latest.json"
    steps_csv = out_dir / "monitoring_stack_runner_v5_steps.csv"
    alerts_csv = out_dir / "monitoring_stack_runner_v5_alerts.csv"
    report_path = out_dir / "monitoring_stack_runner_v5_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with steps_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "step_key", "cmd", "returncode", "step_class", "evidence_ok",
                "class_reason", "required_marker_seen", "pass_marker_seen",
                "dirty_expected_fail", "stdout_tail", "stderr_tail", "exception",
            ],
        )
        writer.writeheader()
        writer.writerows(step_rows)

    with alerts_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["priority", "level", "key", "reason", "action"],
        )
        writer.writeheader()
        writer.writerows(alerts)

    md = []
    md.append("# Edge Factory OS Monitoring Stack Runner v3")
    md.append("")
    md.append(f"monitoring_status: `{monitoring_status}`")
    md.append(f"severity: `{severity}`")
    md.append(f"next_action: `{next_action}`")
    md.append(f"reason: `{reason}`")
    md.append("")
    md.append("## Clean repo decision preview")
    md.append(f"- monitoring_status: `{clean_preview_status}`")
    md.append(f"- severity: `{clean_preview_severity}`")
    md.append(f"- next_action: `{clean_preview_action}`")
    md.append(f"- reason: `{clean_preview_reason}`")
    md.append("")
    md.append("## Alerts")
    for a in alerts:
        md.append(f"- `{a['level']}` `{a['key']}` priority=`{a['priority']}` action=`{a['action']}` reason=`{a['reason']}`")
    md.append("")
    md.append("## Summary")
    for k, v in summary.items():
        md.append(f"- `{k}`: `{v}`")
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

    print("EDGE FACTORY OS MONITORING STACK RUNNER v5")
    print("=" * 100)
    print(f"monitoring_status: {monitoring_status}")
    print(f"severity: {severity}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print(f"step_count={len(step_rows)}")
    print(f"hard_failed_step_count={state['hard_failed_step_count']}")
    print(f"returncode_attention_step_count={state['returncode_attention_step_count']}")
    print(f"expected_repo_dirty_attention_step_count={state['expected_repo_dirty_attention_step_count']}")
    print(f"git_dirty_before={git_dirty_before}")
    print(f"git_dirty={git_dirty_after}")
    print()
    print("CLEAN REPO DECISION PREVIEW")
    print("-" * 100)
    print(f"monitoring_status: {clean_preview_status}")
    print(f"severity: {clean_preview_severity}")
    print(f"next_action: {clean_preview_action}")
    print(f"reason: {clean_preview_reason}")
    print()
    print("SUMMARY")
    print("-" * 100)
    for k, v in summary.items():
        print(f"{k}: {v}")
    print()
    print("ALERTS")
    print("-" * 100)
    for a in alerts:
        print(f"[{a['level']}] {a['key']} | action={a['action']} | reason={a['reason']}")
    print()
    print("STEPS")
    print("-" * 100)
    for s in step_rows:
        print(f"{s['step_key']} | class={s['step_class']} evidence_ok={s['evidence_ok']} returncode={s['returncode']} required_marker_seen={s['required_marker_seen']} pass_marker_seen={s['pass_marker_seen']}")
    print()
    print("SAFETY")
    print("-" * 100)
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Steps : {steps_csv}")
    print(f"Alerts: {alerts_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
