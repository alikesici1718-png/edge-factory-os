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
OUT_ROOT = WORKSPACE / "edge_factory_os_monitoring_stack_runner_v2"

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
]

LATEST_PATHS = {
    "standard_stack": WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json",
    "sample_maturity": WORKSPACE / "edge_factory_os_sample_maturity_watcher_v1" / "sample_maturity_watcher_latest.json",
    "open_pending_aging": WORKSPACE / "edge_factory_os_open_pending_aging_watcher_v2" / "open_pending_aging_watcher_latest.json",
    "state_transition_journal": WORKSPACE / "edge_factory_os_state_transition_journal_v1" / "state_transition_journal_latest.json",
    "trigger_engine": WORKSPACE / "edge_factory_os_trigger_engine_v1" / "os_trigger_engine_latest.json",
    "family_sample_balance": WORKSPACE / "edge_factory_os_family_sample_balance_watcher_v1" / "family_sample_balance_watcher_latest.json",
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
    stderr = result.get("stderr", "")
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

    if stdout or stderr:
        return "OUTPUT_WITHOUT_REQUIRED_MARKER", False, "process produced output but required marker was not found"

    return "NO_OUTPUT_OR_MARKER", False, "no useful output/marker found"

def summarize_latest() -> dict:
    stack = read_json(LATEST_PATHS["standard_stack"])
    sample = read_json(LATEST_PATHS["sample_maturity"])
    aging = read_json(LATEST_PATHS["open_pending_aging"])
    journal = read_json(LATEST_PATHS["state_transition_journal"])
    trigger = read_json(LATEST_PATHS["trigger_engine"])
    balance = read_json(LATEST_PATHS["family_sample_balance"])

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
        "attention_queue_count": aging.get("attention_queue_count"),
        "consistency_attention_count": aging.get("consistency_attention_count"),

        "journal_status": journal.get("journal_status"),
        "journal_event_count": journal.get("event_count"),
        "journal_attention_event_count": journal.get("attention_event_count"),
        "journal_critical_event_count": journal.get("critical_event_count"),

        "trigger_status": trigger.get("trigger_status"),
        "primary_trigger": primary_trigger.get("trigger_key"),
        "primary_trigger_severity": primary_trigger.get("severity"),
        "primary_recommended_action": primary_trigger.get("recommended_action"),

        "family_balance_status": balance.get("balance_status"),
        "closed_family_count": balance.get("closed_family_count"),
        "zero_closed_with_exposure_count": balance.get("zero_closed_with_exposure_count"),
        "attention_family_count": balance.get("attention_family_count"),
        "max_closed_share": balance.get("max_closed_share"),
    }

def decide(summary: dict, step_rows: list[dict], git_dirty: bool) -> tuple[str, str, str]:
    hard_failed_steps = [s for s in step_rows if not s["evidence_ok"]]
    returncode_attention_steps = [s for s in step_rows if s["step_class"] == "RETURNCODE_ATTENTION_MARKER_SEEN"]

    if git_dirty:
        return (
            "MONITORING_STACK_REPO_ATTENTION",
            "COMMIT_OR_REVIEW_REPO_CHANGES",
            "Repo is dirty; standard stack may report non-pass until committed.",
        )

    if hard_failed_steps:
        return (
            "MONITORING_STACK_STEP_ATTENTION",
            "REVIEW_FAILED_MONITORING_STEP",
            "At least one monitoring step lacked required evidence marker.",
        )

    if returncode_attention_steps:
        return (
            "MONITORING_STACK_RETURNCODE_ATTENTION",
            "REVIEW_STEP_STDERR_TAILS",
            "Some steps emitted expected markers but returned non-zero.",
        )

    if summary.get("stack_status") != "STACK_PASS":
        return (
            "MONITORING_STACK_STANDARD_STACK_ATTENTION",
            "REVIEW_STANDARD_STACK",
            "Standard stack is not PASS.",
        )

    if not summary.get("runtime_ok") or not summary.get("process_ok") or not summary.get("health_ok"):
        return (
            "MONITORING_STACK_RUNTIME_ATTENTION",
            "RUN_READ_ONLY_RUNTIME_DIAGNOSTICS",
            "Runtime/process/health is not fully OK.",
        )

    if summary.get("new_errors_since_ack"):
        return (
            "MONITORING_STACK_NEW_ERRORS_ATTENTION",
            "RUN_ERROR_CLASSIFIER_AND_ACKNOWLEDGER",
            "New errors appeared since acknowledgement.",
        )

    if summary.get("snapshot_mismatch"):
        return (
            "MONITORING_STACK_SNAPSHOT_MISMATCH_ATTENTION",
            "REFRESH_SAMPLE_AND_AGING_SNAPSHOT_READ_ONLY",
            "Sample watcher and direct CSV counts do not match.",
        )

    if summary.get("trigger_status") == "TRIGGER_ENGINE_CRITICAL":
        return (
            "MONITORING_STACK_TRIGGER_CRITICAL",
            "REVIEW_TRIGGER_ENGINE_CRITICAL",
            "Trigger engine returned critical status.",
        )

    if summary.get("closed", 0) >= 50:
        return (
            "MONITORING_STACK_CAPITAL_REVIEW_READY_READ_ONLY",
            "RUN_CAPITAL_REVIEW_READ_ONLY",
            "Closed sample reached capital review threshold.",
        )

    if summary.get("closed", 0) >= 20:
        return (
            "MONITORING_STACK_DRIFT_REVIEW_READY_READ_ONLY",
            "RUN_DRIFT_REVIEW_READ_ONLY",
            "Closed sample reached drift review threshold.",
        )

    if summary.get("family_balance_status") == "FAMILY_SAMPLE_BALANCE_ATTENTION":
        return (
            "MONITORING_STACK_FAMILY_BALANCE_ATTENTION",
            "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
            "Some active/pending family has no closed sample yet.",
        )

    return (
        "MONITORING_STACK_OK_COLLECTING",
        "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
        "All monitoring checks OK; sample still below review thresholds.",
    )

def main() -> int:
    out_dir = OUT_ROOT / f"monitoring_stack_runner_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Check repo status before steps too. New v2 file is expected to make repo dirty on first run.
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
    monitoring_status, next_action, reason = decide(summary, step_rows, git_dirty_after)

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),
        "monitoring_status": monitoring_status,
        "next_action": next_action,
        "reason": reason,

        "step_count": len(step_rows),
        "hard_failed_step_count": len([s for s in step_rows if not s["evidence_ok"]]),
        "returncode_attention_step_count": len([s for s in step_rows if s["step_class"] == "RETURNCODE_ATTENTION_MARKER_SEEN"]),
        "expected_repo_dirty_attention_step_count": len([s for s in step_rows if s["step_class"] == "EXPECTED_REPO_DIRTY_ATTENTION"]),

        "git_dirty_before": git_dirty_before,
        "git_status_short_before": git_short_before,
        "git_dirty": git_dirty_after,
        "git_status_short": git_short_after,

        "summary": summary,
        "steps": step_rows,

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,
    }

    state_path = out_dir / "monitoring_stack_runner_v2_state.json"
    latest_path = OUT_ROOT / "monitoring_stack_latest.json"
    steps_csv = out_dir / "monitoring_stack_runner_v2_steps.csv"
    report_path = out_dir / "monitoring_stack_runner_v2_report.md"

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

    md = []
    md.append("# Edge Factory OS Monitoring Stack Runner v2")
    md.append("")
    md.append(f"monitoring_status: `{monitoring_status}`")
    md.append(f"next_action: `{next_action}`")
    md.append(f"reason: `{reason}`")
    md.append("")
    md.append("## Summary")
    for k, v in summary.items():
        md.append(f"- `{k}`: `{v}`")
    md.append("")
    md.append("## Steps")
    for s in step_rows:
        md.append(f"- `{s['step_key']}` class=`{s['step_class']}` evidence_ok=`{s['evidence_ok']}` returncode=`{s['returncode']}`")
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

    print("EDGE FACTORY OS MONITORING STACK RUNNER v2")
    print("=" * 100)
    print(f"monitoring_status: {monitoring_status}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print(f"step_count={len(step_rows)}")
    print(f"hard_failed_step_count={state['hard_failed_step_count']}")
    print(f"returncode_attention_step_count={state['returncode_attention_step_count']}")
    print(f"expected_repo_dirty_attention_step_count={state['expected_repo_dirty_attention_step_count']}")
    print(f"git_dirty_before={git_dirty_before}")
    print(f"git_dirty={git_dirty_after}")
    print()
    print("SUMMARY")
    print("-" * 100)
    for k, v in summary.items():
        print(f"{k}: {v}")
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
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
