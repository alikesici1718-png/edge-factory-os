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
OUT_ROOT = WORKSPACE / "edge_factory_os_control_tower_v2"

MONITORING_LATEST = WORKSPACE / "edge_factory_os_monitoring_stack_runner_v6" / "monitoring_stack_latest.json"
ACTION_LATEST = WORKSPACE / "edge_factory_os_action_discipline_policy_v1" / "action_discipline_policy_latest.json"
SAMPLE_LATEST = WORKSPACE / "edge_factory_os_sample_maturity_watcher_v1" / "sample_maturity_watcher_latest.json"

STEPS = [
    {
        "step_key": "monitoring_stack_v6",
        "cmd": [sys.executable, "-u", r".\tools\edge_factory_os_monitoring_stack_runner_v6.py"],
        "required_marker_any": ["EDGE FACTORY OS MONITORING STACK RUNNER v6", "monitoring_status:"],
    },
    {
        "step_key": "action_discipline_v1",
        "cmd": [sys.executable, "-u", r".\tools\edge_factory_os_action_discipline_policy_v1.py"],
        "required_marker_any": ["EDGE FACTORY OS ACTION DISCIPLINE POLICY v1", "action_status:"],
    },
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e), "__path__": str(path)}

def run_cmd(cmd: list[str], cwd: Path, timeout: int = 360) -> dict:
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

def marker_any(stdout: str, markers: list[str]) -> bool:
    return any(m in stdout for m in markers)

def git_status() -> tuple[bool, str]:
    r = run_cmd(["git", "status", "--short"], cwd=REPO, timeout=40)
    out = (r.get("stdout") or "").strip()
    return bool(out), out

def as_int(v, default: int = 0) -> int:
    try:
        if v is None or v == "":
            return default
        return int(v)
    except Exception:
        return default

def classify_step(step: dict, result: dict) -> tuple[str, bool, str]:
    stdout = result.get("stdout", "")
    stderr = result.get("stderr", "")
    exception = result.get("exception", "")
    returncode = result.get("returncode")

    marker_seen = marker_any(stdout, step.get("required_marker_any", []))

    if exception:
        return "STEP_EXCEPTION", False, exception

    if returncode == 0 and marker_seen:
        return "PASS", True, "returncode=0 and required marker seen"

    if returncode != 0 and marker_seen:
        return "RETURNCODE_ATTENTION_MARKER_SEEN", True, "non-zero returncode but required marker seen; likely repo-attention workflow or child attention"

    if stdout or stderr:
        return "OUTPUT_WITHOUT_REQUIRED_MARKER", False, "output exists but required marker missing"

    return "NO_OUTPUT_OR_MARKER", False, "no useful output/marker found"


def derive_clean_repo_preview_from_summary(action: dict, monitoring: dict, sample: dict) -> tuple[str, str, str, str, str]:
    summary = monitoring.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}

    runtime_ok = summary.get("runtime_ok") is True or sample.get("runtime_ok") is True
    process_ok = summary.get("process_ok") is True or sample.get("process_ok") is True
    health_ok = summary.get("health_ok") is True or sample.get("health_ok") is True
    new_errors_since_ack = summary.get("new_errors_since_ack") is True or sample.get("new_errors_since_ack") is True
    snapshot_mismatch = summary.get("snapshot_mismatch") is True

    closed = as_int(summary.get("closed", sample.get("closed")))
    drift_remaining = as_int(summary.get("drift_remaining", sample.get("drift_remaining")))
    capital_remaining = as_int(summary.get("capital_remaining", sample.get("capital_remaining")))

    trend_status = str(summary.get("family_exposure_trend_status") or "")
    profiler_status = str(summary.get("family_exposure_profiler_status") or "")
    balance_status = str(summary.get("family_balance_status") or "")
    aging_status = str(summary.get("aging_status") or "")

    # Real hard blockers survive clean-preview suppression.
    if not runtime_ok or not process_ok or not health_ok:
        return (
            "CONTROL_TOWER_CRITICAL_READ_ONLY",
            "CRITICAL",
            "READ_ONLY_DIAGNOSTICS",
            "RUN_READ_ONLY_RUNTIME_DIAGNOSTICS",
            f"runtime_ok={runtime_ok}, process_ok={process_ok}, health_ok={health_ok}",
        )

    if new_errors_since_ack:
        return (
            "CONTROL_TOWER_ERROR_REVIEW_READ_ONLY",
            "ATTENTION",
            "READ_ONLY_ERROR_REVIEW",
            "RUN_ERROR_CLASSIFIER_AND_ACKNOWLEDGER",
            "New errors appeared since acknowledgement.",
        )

    if snapshot_mismatch:
        return (
            "CONTROL_TOWER_SNAPSHOT_REFRESH_READ_ONLY",
            "ATTENTION",
            "READ_ONLY_SNAPSHOT_REFRESH",
            "REFRESH_SAMPLE_AND_AGING_SNAPSHOT_READ_ONLY",
            "Sample watcher and direct CSV counts disagree.",
        )

    if closed >= 50:
        return (
            "CONTROL_TOWER_CAPITAL_REVIEW_READY_READ_ONLY",
            "INFO",
            "READ_ONLY_CAPITAL_REVIEW",
            "RUN_CAPITAL_REVIEW_READ_ONLY",
            f"closed={closed}/50",
        )

    if closed >= 20:
        return (
            "CONTROL_TOWER_DRIFT_REVIEW_READY_READ_ONLY",
            "INFO",
            "READ_ONLY_DRIFT_REVIEW",
            "RUN_DRIFT_REVIEW_READ_ONLY",
            f"closed={closed}/20",
        )

    # Non-mutating monitoring attentions.
    if trend_status == "FAMILY_EXPOSURE_TREND_ATTENTION":
        return (
            "CONTROL_TOWER_WATCH_ONLY",
            "ATTENTION",
            "WATCH_ONLY",
            "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
            f"family_exposure_trend_status={trend_status}; closed={closed}/20",
        )

    if profiler_status == "FAMILY_EXPOSURE_ATTENTION":
        return (
            "CONTROL_TOWER_WATCH_ONLY",
            "ATTENTION",
            "WATCH_ONLY",
            "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
            f"family_exposure_profiler_status={profiler_status}; closed={closed}/20",
        )

    if balance_status == "FAMILY_SAMPLE_BALANCE_ATTENTION":
        return (
            "CONTROL_TOWER_WATCH_ONLY",
            "ATTENTION",
            "WATCH_ONLY",
            "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
            f"family_balance_status={balance_status}; closed={closed}/20",
        )

    # INFO / collecting states are not intervention signals.
    if (
        trend_status == "FAMILY_EXPOSURE_TREND_INFO"
        or profiler_status == "FAMILY_EXPOSURE_INFO"
        or balance_status == "FAMILY_SAMPLE_BALANCE_COLLECTING"
        or aging_status in {"OPEN_PENDING_AGING_INFO", "OPEN_PENDING_CONSISTENCY_INFO"}
    ):
        return (
            "CONTROL_TOWER_COLLECT_ONLY_WITH_INFO",
            "INFO",
            "COLLECT_ONLY",
            "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
            f"sample still below review thresholds; closed={closed}/20; drift_remaining={drift_remaining}; capital_remaining={capital_remaining}",
        )

    return (
        "CONTROL_TOWER_COLLECT_ONLY",
        "OK",
        "COLLECT_ONLY",
        "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
        f"sample still below review thresholds; closed={closed}/20; drift_remaining={drift_remaining}; capital_remaining={capital_remaining}",
    )


def derive_final_decision(action: dict, monitoring: dict, sample: dict, git_dirty: bool, hard_failed_step_count: int) -> tuple[str, str, str, str, str]:
    action_status = str(action.get("action_status") or "")
    action_severity = str(action.get("severity") or "")
    allowed_scope = str(action.get("allowed_scope") or "")
    recommended_action = str(action.get("recommended_action") or "")
    reason = str(action.get("reason") or "")

    monitoring_status = str(monitoring.get("monitoring_status") or "")

    if hard_failed_step_count > 0:
        return (
            "CONTROL_TOWER_STEP_FAILURE",
            "ATTENTION",
            "NONE",
            "REVIEW_CONTROL_TOWER_STEP_FAILURE",
            "One or more control tower steps lacked required evidence marker.",
        )

    if git_dirty or action_status == "ACTION_DISCIPLINE_REPO_ATTENTION":
        return (
            "CONTROL_TOWER_REPO_ATTENTION",
            "ATTENTION",
            "REPO_ONLY_CLEANUP",
            "COMMIT_OR_REVIEW_REPO_CHANGES",
            "Repo is dirty; checkpoint current code before trusting downstream final decision.",
        )

    if action_severity == "CRITICAL":
        return (
            "CONTROL_TOWER_CRITICAL_READ_ONLY",
            "CRITICAL",
            allowed_scope or "READ_ONLY_DIAGNOSTICS",
            recommended_action or "RUN_READ_ONLY_DIAGNOSTICS",
            reason or "Action discipline returned critical.",
        )

    if "CAPITAL_REVIEW_READY" in action_status:
        return (
            "CONTROL_TOWER_CAPITAL_REVIEW_READY_READ_ONLY",
            "INFO",
            "READ_ONLY_CAPITAL_REVIEW",
            recommended_action or "RUN_CAPITAL_REVIEW_READ_ONLY",
            reason,
        )

    if "DRIFT_REVIEW_READY" in action_status:
        return (
            "CONTROL_TOWER_DRIFT_REVIEW_READY_READ_ONLY",
            "INFO",
            "READ_ONLY_DRIFT_REVIEW",
            recommended_action or "RUN_DRIFT_REVIEW_READ_ONLY",
            reason,
        )

    if allowed_scope == "WATCH_ONLY" or action_status.startswith("ACTION_DISCIPLINE_WATCH_ONLY"):
        return (
            "CONTROL_TOWER_WATCH_ONLY",
            action_severity or "ATTENTION",
            "WATCH_ONLY",
            recommended_action or "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
            reason or "Watch-only attention from action discipline.",
        )

    if allowed_scope == "COLLECT_ONLY" or action_status == "ACTION_DISCIPLINE_OK_COLLECTING":
        return (
            "CONTROL_TOWER_COLLECT_ONLY",
            "OK",
            "COLLECT_ONLY",
            recommended_action or "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
            reason or "Collecting sample below review thresholds.",
        )

    if monitoring_status:
        return (
            "CONTROL_TOWER_MONITORING_ATTENTION",
            action_severity or "ATTENTION",
            allowed_scope or "WATCH_ONLY",
            recommended_action or "CONTINUE_MONITORING",
            reason or f"Monitoring status={monitoring_status}",
        )

    return (
        "CONTROL_TOWER_UNKNOWN_REVIEW",
        "ATTENTION",
        "READ_ONLY_REVIEW",
        "REVIEW_CONTROL_TOWER_OUTPUT",
        "Unable to classify final OS decision.",
    )

def main() -> int:
    out_dir = OUT_ROOT / f"control_tower_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    git_dirty_before, git_short_before = git_status()

    step_rows = []

    for step in STEPS:
        result = run_cmd(step["cmd"], cwd=REPO)
        step_class, evidence_ok, class_reason = classify_step(step, result)

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
            "stdout_tail": stdout[-2500:],
            "stderr_tail": stderr[-2500:],
            "exception": result.get("exception", ""),
        })

    git_dirty_after, git_short_after = git_status()

    monitoring = read_json(MONITORING_LATEST)
    action = read_json(ACTION_LATEST)
    sample = read_json(SAMPLE_LATEST)

    hard_failed_step_count = len([s for s in step_rows if not s["evidence_ok"]])
    returncode_attention_step_count = len([s for s in step_rows if s["step_class"] == "RETURNCODE_ATTENTION_MARKER_SEEN"])

    final_status, severity, allowed_scope, recommended_action, reason = derive_final_decision(
        action=action,
        monitoring=monitoring,
        sample=sample,
        git_dirty=git_dirty_after,
        hard_failed_step_count=hard_failed_step_count,
    )

    summary = monitoring.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}

    action_preview = action.get("clean_repo_decision_preview", {})
    if not isinstance(action_preview, dict):
        action_preview = {}

    # v2: repo-dirty can cascade into stack_status=STACK_FAIL and primary_trigger=STACK_REVIEW_REQUIRED.
    # Clean preview must suppress that workflow noise and classify the underlying runtime/sample state.
    if git_dirty_after and str(summary.get("primary_trigger") or "") == "STACK_REVIEW_REQUIRED":
        clean_preview_status, clean_preview_severity, clean_preview_scope, clean_preview_action, clean_preview_reason = derive_clean_repo_preview_from_summary(
            action=action,
            monitoring=monitoring,
            sample=sample,
        )
    else:
        clean_preview_status, clean_preview_severity, clean_preview_scope, clean_preview_action, clean_preview_reason = derive_final_decision(
            action={
                "action_status": action_preview.get("action_status", action.get("action_status")),
                "severity": action_preview.get("severity", action.get("severity")),
                "allowed_scope": action_preview.get("allowed_scope", action.get("allowed_scope")),
                "recommended_action": action_preview.get("recommended_action", action.get("recommended_action")),
                "reason": action_preview.get("reason", action.get("reason")),
            },
            monitoring=monitoring,
            sample=sample,
            git_dirty=False,
            hard_failed_step_count=hard_failed_step_count,
        )

    closed = as_int(summary.get("closed", sample.get("closed")))
    open_count = as_int(summary.get("open", sample.get("open")))
    pending = as_int(summary.get("pending", sample.get("pending")))
    errors = as_int(summary.get("errors", sample.get("errors")))
    drift_remaining = as_int(summary.get("drift_remaining", sample.get("drift_remaining")))
    capital_remaining = as_int(summary.get("capital_remaining", sample.get("capital_remaining")))

    runtime_ok = summary.get("runtime_ok") is True or sample.get("runtime_ok") is True
    process_ok = summary.get("process_ok") is True or sample.get("process_ok") is True
    health_ok = summary.get("health_ok") is True or sample.get("health_ok") is True
    new_errors_since_ack = summary.get("new_errors_since_ack") is True or sample.get("new_errors_since_ack") is True
    snapshot_mismatch = summary.get("snapshot_mismatch") is True

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),

        "control_tower_status": final_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "recommended_action": recommended_action,
        "reason": reason,

        "clean_repo_decision_preview": {
            "control_tower_status": clean_preview_status,
            "severity": clean_preview_severity,
            "allowed_scope": clean_preview_scope,
            "recommended_action": clean_preview_action,
            "reason": clean_preview_reason,
        },

        "monitoring_status": monitoring.get("monitoring_status"),
        "monitoring_severity": monitoring.get("severity"),
        "action_status": action.get("action_status"),
        "action_severity": action.get("severity"),
        "action_allowed_scope": action.get("allowed_scope"),
        "action_recommended_action": action.get("recommended_action"),

        "stack_status": summary.get("stack_status"),
        "trigger_status": summary.get("trigger_status"),
        "primary_trigger": summary.get("primary_trigger"),
        "family_balance_status": summary.get("family_balance_status"),
        "family_exposure_profiler_status": summary.get("family_exposure_profiler_status"),
        "family_exposure_trend_status": summary.get("family_exposure_trend_status"),
        "aging_status": summary.get("aging_status"),

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

        "step_count": len(step_rows),
        "hard_failed_step_count": hard_failed_step_count,
        "returncode_attention_step_count": returncode_attention_step_count,

        "git_dirty_before": git_dirty_before,
        "git_status_short_before": git_short_before,
        "git_dirty": git_dirty_after,
        "git_status_short": git_short_after,

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,

        "steps": step_rows,
    }

    state_path = out_dir / "control_tower_v2_state.json"
    latest_path = OUT_ROOT / "control_tower_latest.json"
    steps_csv = out_dir / "control_tower_v2_steps.csv"
    report_path = out_dir / "control_tower_v2_report.md"

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
        writer.writerows(step_rows)

    md = []
    md.append("# Edge Factory OS Control Tower v1")
    md.append("")
    md.append(f"control_tower_status: `{final_status}`")
    md.append(f"severity: `{severity}`")
    md.append(f"allowed_scope: `{allowed_scope}`")
    md.append(f"recommended_action: `{recommended_action}`")
    md.append(f"reason: `{reason}`")
    md.append("")
    md.append("## Clean repo decision preview")
    md.append(f"- control_tower_status: `{clean_preview_status}`")
    md.append(f"- severity: `{clean_preview_severity}`")
    md.append(f"- allowed_scope: `{clean_preview_scope}`")
    md.append(f"- recommended_action: `{clean_preview_action}`")
    md.append(f"- reason: `{clean_preview_reason}`")
    md.append("")
    md.append("## Summary")
    for k in [
        "monitoring_status", "action_status", "stack_status", "trigger_status",
        "family_exposure_trend_status", "closed", "open", "pending",
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
    md.append("- execution_performed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS CONTROL TOWER v2")
    print("=" * 100)
    print(f"control_tower_status: {final_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"recommended_action: {recommended_action}")
    print(f"reason: {reason}")
    print(f"git_dirty={git_dirty_after}")
    print()
    print("CLEAN REPO DECISION PREVIEW")
    print("-" * 100)
    print(f"control_tower_status: {clean_preview_status}")
    print(f"severity: {clean_preview_severity}")
    print(f"allowed_scope: {clean_preview_scope}")
    print(f"recommended_action: {clean_preview_action}")
    print(f"reason: {clean_preview_reason}")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(f"monitoring_status={monitoring.get('monitoring_status')}")
    print(f"action_status={action.get('action_status')}")
    print(f"stack_status={summary.get('stack_status')}")
    print(f"trigger_status={summary.get('trigger_status')} primary_trigger={summary.get('primary_trigger')}")
    print(f"family_exposure_trend_status={summary.get('family_exposure_trend_status')}")
    print(f"family_exposure_profiler_status={summary.get('family_exposure_profiler_status')}")
    print(f"family_balance_status={summary.get('family_balance_status')}")
    print(f"aging_status={summary.get('aging_status')}")
    print(f"closed={closed} open={open_count} pending={pending} errors={errors}")
    print(f"drift_remaining={drift_remaining} capital_remaining={capital_remaining}")
    print(f"runtime_ok={runtime_ok} process_ok={process_ok} health_ok={health_ok}")
    print(f"new_errors_since_ack={new_errors_since_ack} snapshot_mismatch={snapshot_mismatch}")
    print(f"step_count={len(step_rows)} hard_failed_step_count={hard_failed_step_count} returncode_attention_step_count={returncode_attention_step_count}")
    print()
    print("STEPS")
    print("-" * 100)
    for s in step_rows:
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
    print("execution_performed  : False")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Steps : {steps_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
