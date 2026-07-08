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
OUT_ROOT = WORKSPACE / "edge_factory_os_control_tower_cycle_runner_v1"

CONTROL_TOWER_LATEST = WORKSPACE / "edge_factory_os_control_tower_v2" / "control_tower_latest.json"
DECISION_JOURNAL_LATEST = WORKSPACE / "edge_factory_os_control_tower_decision_journal_v1" / "control_tower_decision_journal_latest.json"

CONTROL_TOWER_CMD = [sys.executable, "-u", r".\tools\edge_factory_os_control_tower_v2.py"]
DECISION_JOURNAL_CMD = [sys.executable, "-u", r".\tools\edge_factory_os_control_tower_decision_journal_v1.py"]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e), "__path__": str(path)}

def run_cmd(cmd: list[str], cwd: Path, timeout: int = 420) -> dict:
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

def classify_step(step_key: str, result: dict, markers: list[str]) -> tuple[str, bool, str]:
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

def derive_cycle_decision(control: dict, journal: dict, git_dirty: bool, hard_failed: int, journal_skipped: bool) -> tuple[str, str, str, str, str]:
    control_status = str(control.get("control_tower_status") or "")
    control_severity = str(control.get("severity") or "")
    control_scope = str(control.get("allowed_scope") or "")
    control_action = str(control.get("recommended_action") or "")
    control_reason = str(control.get("reason") or "")

    journal_status = str(journal.get("journal_status") or "")
    journal_attention = as_int(journal.get("attention_event_count"))
    journal_critical = as_int(journal.get("critical_event_count"))

    if hard_failed > 0:
        return (
            "CONTROL_TOWER_CYCLE_STEP_FAILURE",
            "ATTENTION",
            "NONE",
            "REVIEW_CONTROL_TOWER_CYCLE_STEP_FAILURE",
            "One or more cycle steps lacked required evidence marker.",
        )

    if git_dirty:
        return (
            "CONTROL_TOWER_CYCLE_REPO_ATTENTION",
            "ATTENTION",
            "REPO_ONLY_CLEANUP",
            "COMMIT_OR_REVIEW_REPO_CHANGES",
            "Repo is dirty; cycle runner skipped journal append to avoid recording transient repo-attention noise." if journal_skipped else "Repo is dirty.",
        )

    if journal_critical > 0 or journal_status == "CONTROL_TOWER_DECISION_JOURNAL_CRITICAL":
        return (
            "CONTROL_TOWER_CYCLE_JOURNAL_CRITICAL",
            "CRITICAL",
            "READ_ONLY_REVIEW",
            "REVIEW_CONTROL_TOWER_DECISION_JOURNAL",
            "Decision journal recorded critical event(s).",
        )

    if control_severity == "CRITICAL":
        return (
            "CONTROL_TOWER_CYCLE_CRITICAL_READ_ONLY",
            "CRITICAL",
            control_scope or "READ_ONLY_DIAGNOSTICS",
            control_action or "RUN_READ_ONLY_DIAGNOSTICS",
            control_reason or "Control Tower returned critical state.",
        )

    if journal_attention > 0 or journal_status == "CONTROL_TOWER_DECISION_JOURNAL_ATTENTION":
        return (
            "CONTROL_TOWER_CYCLE_JOURNAL_ATTENTION",
            "ATTENTION",
            "READ_ONLY_REVIEW",
            "REVIEW_CONTROL_TOWER_DECISION_CHANGE",
            "Decision journal recorded attention event(s).",
        )

    if control_status == "CONTROL_TOWER_COLLECT_ONLY":
        return (
            "CONTROL_TOWER_CYCLE_COLLECT_ONLY",
            "OK",
            "COLLECT_ONLY",
            "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
            control_reason,
        )

    if control_status == "CONTROL_TOWER_COLLECT_ONLY_WITH_INFO":
        return (
            "CONTROL_TOWER_CYCLE_COLLECT_ONLY_WITH_INFO",
            "INFO",
            "COLLECT_ONLY",
            "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
            control_reason,
        )

    if control_status == "CONTROL_TOWER_WATCH_ONLY":
        return (
            "CONTROL_TOWER_CYCLE_WATCH_ONLY",
            "ATTENTION",
            "WATCH_ONLY",
            control_action or "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
            control_reason,
        )

    if "DRIFT_REVIEW_READY" in control_status:
        return (
            "CONTROL_TOWER_CYCLE_DRIFT_REVIEW_READY_READ_ONLY",
            "INFO",
            "READ_ONLY_DRIFT_REVIEW",
            control_action or "RUN_DRIFT_REVIEW_READ_ONLY",
            control_reason,
        )

    if "CAPITAL_REVIEW_READY" in control_status:
        return (
            "CONTROL_TOWER_CYCLE_CAPITAL_REVIEW_READY_READ_ONLY",
            "INFO",
            "READ_ONLY_CAPITAL_REVIEW",
            control_action or "RUN_CAPITAL_REVIEW_READ_ONLY",
            control_reason,
        )

    return (
        "CONTROL_TOWER_CYCLE_REVIEW",
        control_severity or "ATTENTION",
        control_scope or "READ_ONLY_REVIEW",
        control_action or "REVIEW_CONTROL_TOWER_OUTPUT",
        control_reason or "Control Tower returned unclassified state.",
    )

def main() -> int:
    out_dir = OUT_ROOT / f"control_tower_cycle_runner_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    steps = []

    git_dirty_before, git_short_before = git_status()

    control_result = run_cmd(CONTROL_TOWER_CMD, cwd=REPO)
    control_class, control_evidence_ok, control_reason = classify_step(
        "control_tower_v2",
        control_result,
        ["EDGE FACTORY OS CONTROL TOWER v2", "control_tower_status:"],
    )

    steps.append({
        "step_key": "control_tower_v2",
        "cmd": " ".join(CONTROL_TOWER_CMD),
        "returncode": control_result.get("returncode"),
        "step_class": control_class,
        "evidence_ok": control_evidence_ok,
        "class_reason": control_reason,
        "required_marker_seen": marker_any(control_result.get("stdout", ""), ["EDGE FACTORY OS CONTROL TOWER v2", "control_tower_status:"]),
        "stdout_tail": (control_result.get("stdout", "") or "")[-2500:],
        "stderr_tail": (control_result.get("stderr", "") or "")[-2500:],
        "exception": control_result.get("exception", ""),
    })

    # Important: after control tower, if repo is dirty, do not append journal.
    # This prevents uncommitted tool creation from polluting the decision journal with transient REPO_ATTENTION.
    git_dirty_after_control, git_short_after_control = git_status()

    journal_skipped_due_repo_dirty = False

    if git_dirty_after_control:
        journal_skipped_due_repo_dirty = True
        steps.append({
            "step_key": "decision_journal_v1",
            "cmd": " ".join(DECISION_JOURNAL_CMD),
            "returncode": None,
            "step_class": "SKIPPED_REPO_DIRTY",
            "evidence_ok": True,
            "class_reason": "Skipped journal append because repo is dirty.",
            "required_marker_seen": False,
            "stdout_tail": "",
            "stderr_tail": "",
            "exception": "",
        })
    else:
        journal_result = run_cmd(DECISION_JOURNAL_CMD, cwd=REPO)
        journal_class, journal_evidence_ok, journal_reason = classify_step(
            "decision_journal_v1",
            journal_result,
            ["EDGE FACTORY OS CONTROL TOWER DECISION JOURNAL v1", "journal_status:"],
        )

        steps.append({
            "step_key": "decision_journal_v1",
            "cmd": " ".join(DECISION_JOURNAL_CMD),
            "returncode": journal_result.get("returncode"),
            "step_class": journal_class,
            "evidence_ok": journal_evidence_ok,
            "class_reason": journal_reason,
            "required_marker_seen": marker_any(journal_result.get("stdout", ""), ["EDGE FACTORY OS CONTROL TOWER DECISION JOURNAL v1", "journal_status:"]),
            "stdout_tail": (journal_result.get("stdout", "") or "")[-2500:],
            "stderr_tail": (journal_result.get("stderr", "") or "")[-2500:],
            "exception": journal_result.get("exception", ""),
        })

    git_dirty_after, git_short_after = git_status()

    control = read_json(CONTROL_TOWER_LATEST)
    journal = read_json(DECISION_JOURNAL_LATEST)

    hard_failed_step_count = len([s for s in steps if not s["evidence_ok"]])
    returncode_attention_step_count = len([s for s in steps if s["step_class"] == "RETURNCODE_ATTENTION_MARKER_SEEN"])

    cycle_status, severity, allowed_scope, recommended_action, reason = derive_cycle_decision(
        control=control,
        journal=journal,
        git_dirty=git_dirty_after,
        hard_failed=hard_failed_step_count,
        journal_skipped=journal_skipped_due_repo_dirty,
    )

    clean_preview_status, clean_preview_severity, clean_preview_scope, clean_preview_action, clean_preview_reason = derive_cycle_decision(
        control=control.get("clean_repo_decision_preview", control) if isinstance(control.get("clean_repo_decision_preview"), dict) else control,
        journal=journal,
        git_dirty=False,
        hard_failed=hard_failed_step_count,
        journal_skipped=False,
    )

    closed = as_int(control.get("closed"))
    open_count = as_int(control.get("open"))
    pending = as_int(control.get("pending"))
    errors = as_int(control.get("errors"))
    drift_remaining = as_int(control.get("drift_remaining"))
    capital_remaining = as_int(control.get("capital_remaining"))

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),

        "cycle_status": cycle_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "recommended_action": recommended_action,
        "reason": reason,

        "clean_repo_decision_preview": {
            "cycle_status": clean_preview_status,
            "severity": clean_preview_severity,
            "allowed_scope": clean_preview_scope,
            "recommended_action": clean_preview_action,
            "reason": clean_preview_reason,
        },

        "control_tower_status": control.get("control_tower_status"),
        "control_tower_severity": control.get("severity"),
        "control_tower_allowed_scope": control.get("allowed_scope"),
        "control_tower_recommended_action": control.get("recommended_action"),

        "journal_status": journal.get("journal_status"),
        "journal_event_count": journal.get("event_count"),
        "journal_attention_event_count": journal.get("attention_event_count"),
        "journal_critical_event_count": journal.get("critical_event_count"),
        "journal_skipped_due_repo_dirty": journal_skipped_due_repo_dirty,

        "monitoring_status": control.get("monitoring_status"),
        "action_status": control.get("action_status"),
        "stack_status": control.get("stack_status"),
        "trigger_status": control.get("trigger_status"),
        "primary_trigger": control.get("primary_trigger"),
        "family_exposure_trend_status": control.get("family_exposure_trend_status"),
        "family_exposure_profiler_status": control.get("family_exposure_profiler_status"),
        "family_balance_status": control.get("family_balance_status"),
        "aging_status": control.get("aging_status"),

        "closed": closed,
        "open": open_count,
        "pending": pending,
        "errors": errors,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,

        "runtime_ok": control.get("runtime_ok") is True,
        "process_ok": control.get("process_ok") is True,
        "health_ok": control.get("health_ok") is True,
        "new_errors_since_ack": control.get("new_errors_since_ack") is True,
        "snapshot_mismatch": control.get("snapshot_mismatch") is True,

        "step_count": len(steps),
        "hard_failed_step_count": hard_failed_step_count,
        "returncode_attention_step_count": returncode_attention_step_count,

        "git_dirty_before": git_dirty_before,
        "git_status_short_before": git_short_before,
        "git_dirty_after_control": git_dirty_after_control,
        "git_status_short_after_control": git_short_after_control,
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

        "steps": steps,
    }

    state_path = out_dir / "control_tower_cycle_runner_v1_state.json"
    latest_path = OUT_ROOT / "control_tower_cycle_runner_latest.json"
    steps_csv = out_dir / "control_tower_cycle_runner_v1_steps.csv"
    report_path = out_dir / "control_tower_cycle_runner_v1_report.md"

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
    md.append("# Edge Factory OS Control Tower Cycle Runner v1")
    md.append("")
    md.append(f"cycle_status: `{cycle_status}`")
    md.append(f"severity: `{severity}`")
    md.append(f"allowed_scope: `{allowed_scope}`")
    md.append(f"recommended_action: `{recommended_action}`")
    md.append(f"reason: `{reason}`")
    md.append("")
    md.append("## Clean repo decision preview")
    md.append(f"- cycle_status: `{clean_preview_status}`")
    md.append(f"- severity: `{clean_preview_severity}`")
    md.append(f"- allowed_scope: `{clean_preview_scope}`")
    md.append(f"- recommended_action: `{clean_preview_action}`")
    md.append(f"- reason: `{clean_preview_reason}`")
    md.append("")
    md.append("## Summary")
    for k in [
        "control_tower_status", "journal_status", "closed", "open",
        "pending", "errors", "drift_remaining", "capital_remaining",
        "journal_skipped_due_repo_dirty",
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

    print("EDGE FACTORY OS CONTROL TOWER CYCLE RUNNER v1")
    print("=" * 100)
    print(f"cycle_status: {cycle_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"recommended_action: {recommended_action}")
    print(f"reason: {reason}")
    print(f"git_dirty={git_dirty_after}")
    print(f"journal_skipped_due_repo_dirty={journal_skipped_due_repo_dirty}")
    print()
    print("CLEAN REPO DECISION PREVIEW")
    print("-" * 100)
    print(f"cycle_status: {clean_preview_status}")
    print(f"severity: {clean_preview_severity}")
    print(f"allowed_scope: {clean_preview_scope}")
    print(f"recommended_action: {clean_preview_action}")
    print(f"reason: {clean_preview_reason}")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(f"control_tower_status={control.get('control_tower_status')}")
    print(f"journal_status={journal.get('journal_status')}")
    print(f"monitoring_status={control.get('monitoring_status')}")
    print(f"action_status={control.get('action_status')}")
    print(f"stack_status={control.get('stack_status')}")
    print(f"trigger_status={control.get('trigger_status')} primary_trigger={control.get('primary_trigger')}")
    print(f"family_exposure_trend_status={control.get('family_exposure_trend_status')}")
    print(f"family_exposure_profiler_status={control.get('family_exposure_profiler_status')}")
    print(f"family_balance_status={control.get('family_balance_status')}")
    print(f"aging_status={control.get('aging_status')}")
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
    print("execution_performed  : False")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Steps : {steps_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
