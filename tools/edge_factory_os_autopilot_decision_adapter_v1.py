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
OUT_ROOT = WORKSPACE / "edge_factory_os_autopilot_decision_adapter_v1"

UNIFIED_STATE_PATH = WORKSPACE / "edge_factory_os_unified_state_reader_v1" / "os_unified_state_latest.json"
POLICY_PATH = WORKSPACE / "edge_factory_os_policy_engine_v1" / "os_policy_engine_latest.json"
PLANNER_PATH = WORKSPACE / "edge_factory_os_next_action_planner_v1" / "os_next_action_planner_latest.json"
MEMORY_PATH = WORKSPACE / "edge_factory_os_memory_lesson_index_v1" / "os_memory_lesson_index_latest.json"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e), "__path__": str(path)}

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

def add_reason(reasons: list[dict], key: str, value, severity: str, text: str) -> None:
    reasons.append({
        "key": key,
        "value": value,
        "severity": severity,
        "text": text,
    })

def main() -> int:
    out_dir = OUT_ROOT / f"os_autopilot_decision_adapter_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    unified = read_json(UNIFIED_STATE_PATH)
    policy = read_json(POLICY_PATH)
    planner = read_json(PLANNER_PATH)
    memory = read_json(MEMORY_PATH)

    runtime = unified.get("runtime", {})
    repo_state = unified.get("repo", {})
    safety = unified.get("safety", {})
    memory_state = unified.get("memory", {})

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    runtime_ok = runtime.get("runtime_ok") is True
    process_ok = runtime.get("process_watchdog_pass") is True
    health_ok = runtime.get("health_ok") is True
    errors_acknowledged = runtime.get("errors_acknowledged") is True
    new_errors_since_ack = runtime.get("new_errors_since_ack") is True

    closed = int(runtime.get("closed") or 0)
    open_count = int(runtime.get("open") or 0)
    pending = int(runtime.get("pending") or 0)

    drift_ready = runtime.get("drift_ready") is True
    capital_review_ready = runtime.get("capital_review_ready") is True

    policy_status = policy.get("policy_status")
    unexpected_critical_block_count = int(policy.get("unexpected_critical_block_count") or 0)
    attention_block_count = int(policy.get("attention_block_count") or 0)

    planner_decision = planner.get("decision")
    planner_status = planner.get("planner_status")

    exact_candidate_blocks = memory_state.get("exact_candidate_blocks") or memory.get("exact_candidate_blocks") or []
    family_cooldowns = memory_state.get("family_cooldowns") or memory.get("family_cooldowns") or []

    live_allowed = safety.get("live_allowed") is True
    capital_change_allowed = safety.get("capital_change_allowed") is True
    active_paper_allowed = safety.get("active_paper_allowed") is True
    real_orders_allowed = safety.get("real_orders_allowed") is True

    reasons: list[dict] = []

    add_reason(
        reasons,
        "runtime_health",
        {
            "runtime_ok": runtime_ok,
            "process_ok": process_ok,
            "health_ok": health_ok,
        },
        "OK" if runtime_ok and process_ok and health_ok else "CRITICAL",
        "Runtime health state from Unified State.",
    )

    add_reason(
        reasons,
        "error_state",
        {
            "errors_acknowledged": errors_acknowledged,
            "new_errors_since_ack": new_errors_since_ack,
        },
        "OK" if errors_acknowledged and not new_errors_since_ack else "CRITICAL",
        "Error acknowledgement state.",
    )

    add_reason(
        reasons,
        "sample_state",
        {
            "open": open_count,
            "pending": pending,
            "closed": closed,
            "drift_ready": drift_ready,
            "capital_review_ready": capital_review_ready,
        },
        "INFO",
        "Sample maturity state.",
    )

    add_reason(
        reasons,
        "policy_state",
        {
            "policy_status": policy_status,
            "unexpected_critical_block_count": unexpected_critical_block_count,
            "attention_block_count": attention_block_count,
        },
        "OK" if policy_status == "POLICY_ENGINE_PASS" and unexpected_critical_block_count == 0 else "CRITICAL",
        "Policy Engine state.",
    )

    add_reason(
        reasons,
        "repo_state",
        {
            "git_dirty": git_dirty,
            "git_status_short": git_status["stdout"].strip(),
        },
        "OK" if not git_dirty else "ATTENTION",
        "Repo cleanliness state.",
    )

    add_reason(
        reasons,
        "memory_state",
        {
            "exact_candidate_blocks": exact_candidate_blocks,
            "family_cooldowns": family_cooldowns,
        },
        "INFO",
        "Memory blocks and family cooldowns.",
    )

    add_reason(
        reasons,
        "safety_flags",
        {
            "active_paper_allowed": active_paper_allowed,
            "live_allowed": live_allowed,
            "capital_change_allowed": capital_change_allowed,
            "real_orders_allowed": real_orders_allowed,
        },
        "OK" if not any([active_paper_allowed, live_allowed, capital_change_allowed, real_orders_allowed]) else "CRITICAL",
        "Hard safety flags.",
    )

    # Decision order: safety first, then runtime, then repo, then maturity.
    if live_allowed or capital_change_allowed or active_paper_allowed or real_orders_allowed:
        final_decision = "STOP_AND_INSPECT_SAFETY_FLAGS"
        final_status = "DECISION_CRITICAL_SAFETY_BLOCK"
        allowed_to_execute = False
        allowed_scope = "NONE"
        command = ""
        do_not = [
            "Do not run runtime.",
            "Do not patch.",
            "Do not continue research.",
            "Inspect safety flags immediately.",
        ]
    elif not runtime_ok or not process_ok or not health_ok:
        final_decision = "STOP_AND_INSPECT_RUNTIME"
        final_status = "DECISION_RUNTIME_ATTENTION"
        allowed_to_execute = True
        allowed_scope = "READ_ONLY_DIAGNOSTICS"
        command = r'python -u "C:\Users\alike\edge_factory_os_command_center_v2_overlay.py"'
        do_not = [
            "Do not restart blindly.",
            "Do not launch duplicate processes.",
            "Do not patch runtime until diagnostics identify blocker.",
        ]
    elif new_errors_since_ack or not errors_acknowledged:
        final_decision = "RUN_ERROR_REVIEW"
        final_status = "DECISION_ERROR_REVIEW_REQUIRED"
        allowed_to_execute = True
        allowed_scope = "READ_ONLY_ERROR_CLASSIFICATION"
        command = r'python -u "C:\Users\alike\edge_factory_error_classifier_v1.py"'
        do_not = [
            "Do not delete errors.csv.",
            "Do not ignore new errors.",
            "Do not continue OS changes until errors are classified.",
        ]
    elif unexpected_critical_block_count > 0:
        final_decision = "STOP_AND_REVIEW_POLICY_BLOCKS"
        final_status = "DECISION_POLICY_CRITICAL_BLOCK"
        allowed_to_execute = True
        allowed_scope = "READ_ONLY_POLICY_REVIEW"
        command = r'python -u ".\tools\edge_factory_os_policy_engine_v1.py"'
        do_not = [
            "Do not patch runtime.",
            "Do not proceed until unexpected critical policy blocks are understood.",
        ]
    elif git_dirty:
        final_decision = "COMMIT_OR_REVIEW_REPO_CHANGES_BEFORE_NEXT_STEP"
        final_status = "DECISION_REPO_ATTENTION"
        allowed_to_execute = True
        allowed_scope = "REPO_ONLY"
        command = "git status --short"
        do_not = [
            "Do not apply anything to runtime while repo is dirty.",
            "Do not stack more changes before committing/reviewing current diff.",
        ]
    elif capital_review_ready:
        final_decision = "RUN_CAPITAL_REVIEW_READ_ONLY"
        final_status = "DECISION_CAPITAL_REVIEW_READY"
        allowed_to_execute = True
        allowed_scope = "READ_ONLY_CAPITAL_REVIEW"
        command = r'python -u "C:\Users\alike\edge_factory_active_capital_governor_review_v2.py"'
        do_not = [
            "Do not change capital automatically.",
            "Do not alter sizing contract without explicit approval.",
            "Review only.",
        ]
    elif drift_ready:
        final_decision = "RUN_DRIFT_REVIEW"
        final_status = "DECISION_DRIFT_REVIEW_READY"
        allowed_to_execute = True
        allowed_scope = "READ_ONLY_DRIFT_REVIEW"
        command = r'python -u "C:\Users\alike\edge_factory_active_family_drift_monitor_planner_v1.py"'
        do_not = [
            "Do not change families from drift review automatically.",
            "Review only.",
        ]
    elif planner_decision == "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH":
        final_decision = "DO_NOT_TOUCH_RUNTIME_CONTINUE_REPO_ONLY_OS_INTELLIGENCE"
        final_status = "DECISION_OK_REPO_ONLY"
        allowed_to_execute = True
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        command = r'python -u ".\tools\edge_factory_runtime_regression_guard_v1.py"'
        do_not = [
            "Do not restart MASTER.",
            "Do not run launchers.",
            "Do not patch runtime.",
            "Do not start new active paper family.",
            "Do not run blocked candidates.",
        ]
    else:
        final_decision = "HOLD_AND_REVIEW"
        final_status = "DECISION_AMBIGUOUS_REVIEW_REQUIRED"
        allowed_to_execute = False
        allowed_scope = "NONE"
        command = ""
        do_not = [
            "Do not proceed until planner/policy/unified state agree.",
        ]

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),
        "final_status": final_status,
        "final_decision": final_decision,
        "allowed_to_execute": allowed_to_execute,
        "allowed_scope": allowed_scope,
        "recommended_command": command,
        "do_not": do_not,
        "runtime_ok": runtime_ok,
        "process_ok": process_ok,
        "health_ok": health_ok,
        "errors_acknowledged": errors_acknowledged,
        "new_errors_since_ack": new_errors_since_ack,
        "policy_status": policy_status,
        "planner_status": planner_status,
        "planner_decision": planner_decision,
        "git_dirty": git_dirty,
        "open": open_count,
        "pending": pending,
        "closed": closed,
        "drift_ready": drift_ready,
        "capital_review_ready": capital_review_ready,
        "exact_candidate_blocks": exact_candidate_blocks,
        "family_cooldowns": family_cooldowns,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "real_orders_allowed": False,
        "reasons": reasons,
        "source_paths": {
            "unified": str(UNIFIED_STATE_PATH),
            "policy": str(POLICY_PATH),
            "planner": str(PLANNER_PATH),
            "memory": str(MEMORY_PATH),
        },
    }

    state_path = out_dir / "os_autopilot_decision_adapter_v1_state.json"
    latest_path = OUT_ROOT / "os_autopilot_decision_latest.json"
    reasons_csv = out_dir / "os_autopilot_decision_adapter_v1_reasons.csv"
    report_path = out_dir / "os_autopilot_decision_adapter_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with reasons_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["key", "value", "severity", "text"])
        writer.writeheader()
        for r in reasons:
            rr = dict(r)
            rr["value"] = json.dumps(rr["value"], ensure_ascii=False, default=str)
            writer.writerow(rr)

    md = []
    md.append("# Edge Factory OS Autopilot Decision Adapter v1")
    md.append("")
    md.append(f"final_status: `{final_status}`")
    md.append(f"final_decision: `{final_decision}`")
    md.append(f"allowed_scope: `{allowed_scope}`")
    md.append("")
    md.append("## Recommended command")
    md.append("```powershell")
    md.append(command)
    md.append("```")
    md.append("")
    md.append("## Do not")
    for x in do_not:
        md.append(f"- {x}")
    md.append("")
    md.append("## Safety")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    md.append("- real_orders_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS AUTOPILOT DECISION ADAPTER v1")
    print("=" * 100)
    print(f"final_status   : {final_status}")
    print(f"final_decision : {final_decision}")
    print(f"allowed_execute: {allowed_to_execute}")
    print(f"allowed_scope  : {allowed_scope}")
    print(f"recommended_command: {command}")
    print(f"runtime_ok={runtime_ok} process_ok={process_ok} health_ok={health_ok}")
    print(f"errors_acknowledged={errors_acknowledged} new_errors_since_ack={new_errors_since_ack}")
    print(f"policy_status={policy_status}")
    print(f"planner_decision={planner_decision}")
    print(f"git_dirty={git_dirty}")
    print(f"open={open_count} pending={pending} closed={closed}")
    print(f"drift_ready={drift_ready}")
    print(f"capital_review_ready={capital_review_ready}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print("real_orders_allowed: False")
    print()
    print("DO NOT")
    print("-" * 100)
    for x in do_not:
        print(f"- {x}")
    print()
    print("REASONS")
    print("-" * 100)
    for r in reasons:
        print(f"[{r['severity']}] {r['key']}: {r['text']} -> {r['value']}")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Reason: {reasons_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
