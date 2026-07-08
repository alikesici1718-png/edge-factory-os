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
OUT_ROOT = WORKSPACE / "edge_factory_os_cycle_operator_v1"

SCHEDULER_LATEST = WORKSPACE / "edge_factory_os_cycle_scheduler_policy_v1" / "cycle_scheduler_policy_latest.json"
CYCLE_LATEST = WORKSPACE / "edge_factory_os_control_tower_cycle_runner_v1" / "control_tower_cycle_runner_latest.json"

SCHEDULER_CMD = [sys.executable, "-u", r".\tools\edge_factory_os_cycle_scheduler_policy_v1.py"]
CYCLE_RUNNER_CMD = [sys.executable, "-u", r".\tools\edge_factory_os_control_tower_cycle_runner_v1.py"]

MAIN_CYCLE_COMMAND_TEXT = r"python -u .\tools\edge_factory_os_control_tower_cycle_runner_v1.py"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e), "__path__": str(path)}

def run_cmd(cmd: list[str], cwd: Path, timeout: int = 480) -> dict:
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

def as_int(v, default: int = 0) -> int:
    try:
        if v is None or v == "":
            return default
        return int(v)
    except Exception:
        return default

def classify_step(result: dict, markers: list[str]) -> tuple[str, bool, str]:
    stdout = result.get("stdout", "") or ""
    stderr = result.get("stderr", "") or ""
    exception = result.get("exception", "")
    returncode = result.get("returncode")

    marker_seen = marker_any(stdout, markers)

    if exception:
        return "STEP_EXCEPTION", False, exception

    if returncode == 0 and marker_seen:
        return "PASS", True, "returncode=0 and required marker seen"

    if returncode != 0 and marker_seen:
        return "RETURNCODE_ATTENTION_MARKER_SEEN", True, "non-zero returncode but required marker seen"

    if stdout or stderr:
        return "OUTPUT_WITHOUT_REQUIRED_MARKER", False, "output exists but required marker missing"

    return "NO_OUTPUT_OR_MARKER", False, "no useful output/marker found"

def normalize_command(s: str) -> str:
    return " ".join(str(s or "").replace('"', "").replace("'", "").split()).lower()

def scheduler_recommends_cycle_runner(scheduler: dict) -> bool:
    cmd = normalize_command(scheduler.get("recommended_command"))
    target = normalize_command(MAIN_CYCLE_COMMAND_TEXT)
    return cmd == target or "edge_factory_os_control_tower_cycle_runner_v1.py" in cmd

def derive_operator_decision(
    scheduler: dict,
    cycle: dict,
    git_dirty: bool,
    hard_failed_step_count: int,
    cycle_executed: bool,
    cycle_skipped_reason: str,
) -> tuple[str, str, str, str, str]:
    scheduler_status = str(scheduler.get("scheduler_status") or "")
    scheduler_severity = str(scheduler.get("severity") or "")
    cadence_mode = str(scheduler.get("cadence_mode") or "")
    scheduler_reason = str(scheduler.get("reason") or "")
    recommended_command = str(scheduler.get("recommended_command") or "")

    cycle_status = str(cycle.get("cycle_status") or "")
    cycle_severity = str(cycle.get("severity") or "")
    cycle_scope = str(cycle.get("allowed_scope") or "")
    cycle_action = str(cycle.get("recommended_action") or "")
    cycle_reason = str(cycle.get("reason") or "")

    if hard_failed_step_count > 0:
        return (
            "CYCLE_OPERATOR_STEP_FAILURE",
            "ATTENTION",
            "NONE",
            "REVIEW_CYCLE_OPERATOR_STEP_FAILURE",
            "One or more operator steps lacked required evidence marker.",
        )

    if git_dirty:
        return (
            "CYCLE_OPERATOR_REPO_ATTENTION",
            "ATTENTION",
            "REPO_ONLY_CLEANUP",
            "COMMIT_OR_REVIEW_REPO_CHANGES",
            "Repo is dirty; operator did not run cycle runner to avoid journal noise.",
        )

    if "CRITICAL" in scheduler_status or scheduler_severity == "CRITICAL":
        return (
            "CYCLE_OPERATOR_SCHEDULER_CRITICAL",
            "CRITICAL",
            "READ_ONLY_REVIEW",
            recommended_command or "REVIEW_SCHEDULER_OUTPUT",
            scheduler_reason,
        )

    if cadence_mode.startswith("READ_ONLY_") and not scheduler_recommends_cycle_runner(scheduler):
        return (
            "CYCLE_OPERATOR_READ_ONLY_REVIEW_RECOMMENDED",
            scheduler_severity or "ATTENTION",
            cadence_mode,
            recommended_command,
            scheduler_reason,
        )

    if not scheduler_recommends_cycle_runner(scheduler):
        return (
            "CYCLE_OPERATOR_COMMAND_REVIEW",
            scheduler_severity or "ATTENTION",
            cadence_mode or "READ_ONLY_REVIEW",
            recommended_command or "REVIEW_SCHEDULER_OUTPUT",
            f"Scheduler recommended a non-cycle command: {recommended_command}",
        )

    if not cycle_executed:
        return (
            "CYCLE_OPERATOR_CYCLE_SKIPPED",
            "ATTENTION",
            cadence_mode or "REVIEW",
            recommended_command,
            cycle_skipped_reason,
        )

    if cycle_status == "CONTROL_TOWER_CYCLE_COLLECT_ONLY":
        return (
            "CYCLE_OPERATOR_COLLECT_ONLY",
            "OK",
            "COLLECT_ONLY",
            "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
            cycle_reason,
        )

    if cycle_status == "CONTROL_TOWER_CYCLE_COLLECT_ONLY_WITH_INFO":
        return (
            "CYCLE_OPERATOR_COLLECT_ONLY_WITH_INFO",
            "INFO",
            "COLLECT_ONLY",
            "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
            cycle_reason,
        )

    if cycle_status == "CONTROL_TOWER_CYCLE_WATCH_ONLY":
        return (
            "CYCLE_OPERATOR_WATCH_ONLY",
            "ATTENTION",
            "WATCH_ONLY",
            cycle_action or "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
            cycle_reason,
        )

    if "DRIFT_REVIEW_READY" in cycle_status:
        return (
            "CYCLE_OPERATOR_DRIFT_REVIEW_READY_READ_ONLY",
            "INFO",
            "READ_ONLY_DRIFT_REVIEW",
            cycle_action or "RUN_DRIFT_REVIEW_READ_ONLY",
            cycle_reason,
        )

    if "CAPITAL_REVIEW_READY" in cycle_status:
        return (
            "CYCLE_OPERATOR_CAPITAL_REVIEW_READY_READ_ONLY",
            "INFO",
            "READ_ONLY_CAPITAL_REVIEW",
            cycle_action or "RUN_CAPITAL_REVIEW_READ_ONLY",
            cycle_reason,
        )

    if cycle_severity == "CRITICAL":
        return (
            "CYCLE_OPERATOR_CYCLE_CRITICAL",
            "CRITICAL",
            cycle_scope or "READ_ONLY_REVIEW",
            cycle_action or "REVIEW_CYCLE_OUTPUT",
            cycle_reason,
        )

    return (
        "CYCLE_OPERATOR_REVIEW",
        cycle_severity or scheduler_severity or "ATTENTION",
        cycle_scope or cadence_mode or "READ_ONLY_REVIEW",
        cycle_action or recommended_command or "REVIEW_OPERATOR_OUTPUT",
        cycle_reason or scheduler_reason or "Unable to classify operator decision.",
    )

def main() -> int:
    out_dir = OUT_ROOT / f"cycle_operator_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    steps = []

    git_dirty_before, git_short_before = git_status()

    scheduler_result = run_cmd(SCHEDULER_CMD, cwd=REPO)
    scheduler_class, scheduler_evidence_ok, scheduler_reason = classify_step(
        scheduler_result,
        ["EDGE FACTORY OS CYCLE SCHEDULER POLICY v1", "scheduler_status:"],
    )

    steps.append({
        "step_key": "cycle_scheduler_policy_v1",
        "cmd": " ".join(SCHEDULER_CMD),
        "returncode": scheduler_result.get("returncode"),
        "step_class": scheduler_class,
        "evidence_ok": scheduler_evidence_ok,
        "class_reason": scheduler_reason,
        "required_marker_seen": marker_any(scheduler_result.get("stdout", ""), ["EDGE FACTORY OS CYCLE SCHEDULER POLICY v1", "scheduler_status:"]),
        "stdout_tail": (scheduler_result.get("stdout", "") or "")[-2500:],
        "stderr_tail": (scheduler_result.get("stderr", "") or "")[-2500:],
        "exception": scheduler_result.get("exception", ""),
    })

    git_dirty_after_scheduler, git_short_after_scheduler = git_status()

    scheduler = read_json(SCHEDULER_LATEST)

    cycle_executed = False
    cycle_skipped_reason = ""

    if git_dirty_after_scheduler:
        cycle_skipped_reason = "Skipped cycle runner because repo is dirty after scheduler."
        steps.append({
            "step_key": "control_tower_cycle_runner_v1",
            "cmd": " ".join(CYCLE_RUNNER_CMD),
            "returncode": None,
            "step_class": "SKIPPED_REPO_DIRTY",
            "evidence_ok": True,
            "class_reason": cycle_skipped_reason,
            "required_marker_seen": False,
            "stdout_tail": "",
            "stderr_tail": "",
            "exception": "",
        })
    elif not scheduler_recommends_cycle_runner(scheduler):
        cycle_skipped_reason = f"Scheduler did not recommend cycle runner; recommended_command={scheduler.get('recommended_command')}"
        steps.append({
            "step_key": "control_tower_cycle_runner_v1",
            "cmd": " ".join(CYCLE_RUNNER_CMD),
            "returncode": None,
            "step_class": "SKIPPED_SCHEDULER_RECOMMENDED_OTHER_COMMAND",
            "evidence_ok": True,
            "class_reason": cycle_skipped_reason,
            "required_marker_seen": False,
            "stdout_tail": "",
            "stderr_tail": "",
            "exception": "",
        })
    else:
        cycle_result = run_cmd(CYCLE_RUNNER_CMD, cwd=REPO)
        cycle_class, cycle_evidence_ok, cycle_reason = classify_step(
            cycle_result,
            ["EDGE FACTORY OS CONTROL TOWER CYCLE RUNNER v1", "cycle_status:"],
        )
        cycle_executed = True

        steps.append({
            "step_key": "control_tower_cycle_runner_v1",
            "cmd": " ".join(CYCLE_RUNNER_CMD),
            "returncode": cycle_result.get("returncode"),
            "step_class": cycle_class,
            "evidence_ok": cycle_evidence_ok,
            "class_reason": cycle_reason,
            "required_marker_seen": marker_any(cycle_result.get("stdout", ""), ["EDGE FACTORY OS CONTROL TOWER CYCLE RUNNER v1", "cycle_status:"]),
            "stdout_tail": (cycle_result.get("stdout", "") or "")[-2500:],
            "stderr_tail": (cycle_result.get("stderr", "") or "")[-2500:],
            "exception": cycle_result.get("exception", ""),
        })

    git_dirty_after, git_short_after = git_status()
    cycle = read_json(CYCLE_LATEST)

    hard_failed_step_count = len([s for s in steps if not s["evidence_ok"]])
    returncode_attention_step_count = len([s for s in steps if s["step_class"] == "RETURNCODE_ATTENTION_MARKER_SEEN"])

    operator_status, severity, allowed_scope, recommended_action, reason = derive_operator_decision(
        scheduler=scheduler,
        cycle=cycle,
        git_dirty=git_dirty_after,
        hard_failed_step_count=hard_failed_step_count,
        cycle_executed=cycle_executed,
        cycle_skipped_reason=cycle_skipped_reason,
    )

    closed = as_int(cycle.get("closed", scheduler.get("closed")))
    open_count = as_int(cycle.get("open", scheduler.get("open")))
    pending = as_int(cycle.get("pending", scheduler.get("pending")))
    errors = as_int(cycle.get("errors", scheduler.get("errors")))
    drift_remaining = as_int(cycle.get("drift_remaining", scheduler.get("drift_remaining")))
    capital_remaining = as_int(cycle.get("capital_remaining", scheduler.get("capital_remaining")))

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),

        "operator_status": operator_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "recommended_action": recommended_action,
        "reason": reason,

        "scheduler_status": scheduler.get("scheduler_status"),
        "scheduler_severity": scheduler.get("severity"),
        "cadence_mode": scheduler.get("cadence_mode"),
        "scheduler_recommended_command": scheduler.get("recommended_command"),
        "scheduler_reason": scheduler.get("reason"),

        "cycle_status": cycle.get("cycle_status"),
        "cycle_severity": cycle.get("severity"),
        "cycle_allowed_scope": cycle.get("allowed_scope"),
        "cycle_recommended_action": cycle.get("recommended_action"),

        "cycle_executed": cycle_executed,
        "cycle_skipped_reason": cycle_skipped_reason,

        "closed": closed,
        "open": open_count,
        "pending": pending,
        "errors": errors,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,

        "runtime_ok": cycle.get("runtime_ok") is True or scheduler.get("runtime_ok") is True,
        "process_ok": cycle.get("process_ok") is True or scheduler.get("process_ok") is True,
        "health_ok": cycle.get("health_ok") is True or scheduler.get("health_ok") is True,
        "new_errors_since_ack": cycle.get("new_errors_since_ack") is True or scheduler.get("new_errors_since_ack") is True,
        "snapshot_mismatch": cycle.get("snapshot_mismatch") is True or scheduler.get("snapshot_mismatch") is True,

        "step_count": len(steps),
        "hard_failed_step_count": hard_failed_step_count,
        "returncode_attention_step_count": returncode_attention_step_count,

        "git_dirty_before": git_dirty_before,
        "git_status_short_before": git_short_before,
        "git_dirty_after_scheduler": git_dirty_after_scheduler,
        "git_status_short_after_scheduler": git_short_after_scheduler,
        "git_dirty": git_dirty_after,
        "git_status_short": git_short_after,

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": cycle_executed,

        "steps": steps,
    }

    state_path = out_dir / "cycle_operator_v1_state.json"
    latest_path = OUT_ROOT / "cycle_operator_latest.json"
    steps_csv = out_dir / "cycle_operator_v1_steps.csv"
    report_path = out_dir / "cycle_operator_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with steps_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "step_key", "cmd", "returncode", "step_class", "evidence_ok",
                "class_reason", "required_marker_seen", "stdout_tail",
                "stderr_tail", "exception",
            ],
        )
        writer.writeheader()
        writer.writerows(steps)

    md = []
    md.append("# Edge Factory OS Cycle Operator v1")
    md.append("")
    md.append(f"operator_status: `{operator_status}`")
    md.append(f"severity: `{severity}`")
    md.append(f"allowed_scope: `{allowed_scope}`")
    md.append(f"recommended_action: `{recommended_action}`")
    md.append(f"reason: `{reason}`")
    md.append("")
    md.append("## Summary")
    for k in [
        "scheduler_status", "cadence_mode", "cycle_status",
        "cycle_executed", "closed", "open", "pending",
        "errors", "drift_remaining", "capital_remaining",
    ]:
        md.append(f"- `{k}`: `{state.get(k)}`")
    md.append("")
    md.append("## Safety")
    md.append("- runtime_touch_allowed: `False`")
    md.append("- launcher_allowed: `False`")
    md.append("- patch_runtime_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    md.append("- real_orders_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS CYCLE OPERATOR v1")
    print("=" * 100)
    print(f"operator_status: {operator_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"recommended_action: {recommended_action}")
    print(f"reason: {reason}")
    print(f"git_dirty={git_dirty_after}")
    print(f"cycle_executed={cycle_executed}")
    if cycle_skipped_reason:
        print(f"cycle_skipped_reason: {cycle_skipped_reason}")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(f"scheduler_status={scheduler.get('scheduler_status')}")
    print(f"cadence_mode={scheduler.get('cadence_mode')}")
    print(f"scheduler_recommended_command={scheduler.get('recommended_command')}")
    print(f"cycle_status={cycle.get('cycle_status')}")
    print(f"cycle_allowed_scope={cycle.get('allowed_scope')}")
    print(f"cycle_recommended_action={cycle.get('recommended_action')}")
    print(f"closed={closed} open={open_count} pending={pending} errors={errors}")
    print(f"drift_remaining={drift_remaining} capital_remaining={capital_remaining}")
    print(f"runtime_ok={state['runtime_ok']} process_ok={state['process_ok']} health_ok={state['health_ok']}")
    print(f"new_errors_since_ack={state['new_errors_since_ack']} snapshot_mismatch={state['snapshot_mismatch']}")
    print(f"step_count={len(steps)} hard_failed_step_count={hard_failed_step_count} returncode_attention_step_count={returncode_attention_step_count}")
    print()
    print("STEPS")
    print("-" * 100)
    for s in steps:
        print(f"{s['step_key']} | class={s['step_class']} evidence_ok={s['evidence_ok']} returncode={s['returncode']} required_marker_seen={s['required_marker_seen']}")
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
    print(f"execution_performed  : {cycle_executed}")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Steps : {steps_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
