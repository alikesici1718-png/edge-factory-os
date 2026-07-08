#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_standard_stack_runner_v1"

COMMANDS = [
    {
        "key": "regression_guard",
        "cmd": ["python", "-u", r".\tools\edge_factory_runtime_regression_guard_v1.py"],
        "pass_markers": ["status: REGRESSION_GUARD_PASS", "critical_failed: 0"],
    },
    {
        "key": "unified_state",
        "cmd": ["python", "-u", r".\tools\edge_factory_os_unified_state_reader_v1.py"],
        "pass_markers": ["state_level       : OK", "runtime_ok        : True"],
    },
    {
        "key": "policy_engine",
        "cmd": ["python", "-u", r".\tools\edge_factory_os_policy_engine_v1.py"],
        "pass_markers": ["policy_status: POLICY_ENGINE_PASS", "unexpected_critical_block_count=0"],
    },
    {
        "key": "next_action_planner",
        "cmd": ["python", "-u", r".\tools\edge_factory_os_next_action_planner_v1.py"],
        "pass_markers": ["planner_status: NEXT_ACTION_KEEP_RUNNING", "decision      : KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"],
    },
    {
        "key": "autopilot_decision_adapter",
        "cmd": ["python", "-u", r".\tools\edge_factory_os_autopilot_decision_adapter_v1.py"],
        "pass_markers": ["final_status   : DECISION_OK_REPO_ONLY", "final_decision : DO_NOT_TOUCH_RUNTIME_CONTINUE_REPO_ONLY_OS_INTELLIGENCE"],
    },
    {
        "key": "execution_router",
        "cmd": ["python", "-u", r".\tools\edge_factory_os_execution_router_v1.py"],
        "pass_markers": ["router_status     : EXECUTION_ROUTER_READY", "execution_performed: False"],
    },
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def run_cmd(cmd: list[str]) -> dict:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=240,
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

def git_status_short() -> str:
    r = run_cmd(["git", "status", "--short"])
    return (r.get("stdout") or "").strip()

def marker_pass(stdout: str, markers: list[str]) -> tuple[bool, list[str]]:
    missing = [m for m in markers if m not in stdout]
    return len(missing) == 0, missing

def main() -> int:
    out_dir = OUT_ROOT / f"os_standard_stack_runner_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    stop_after_failure = False

    for item in COMMANDS:
        key = item["key"]
        cmd = item["cmd"]

        if stop_after_failure:
            results.append({
                "key": key,
                "cmd": cmd,
                "skipped": True,
                "passed": False,
                "returncode": None,
                "missing_markers": ["SKIPPED_AFTER_PREVIOUS_FAILURE"],
                "stdout": "",
                "stderr": "",
            })
            continue

        r = run_cmd(cmd)
        passed_markers, missing = marker_pass(r["stdout"], item["pass_markers"])
        passed = bool(r["ok"] and passed_markers)

        results.append({
            "key": key,
            "cmd": cmd,
            "skipped": False,
            "passed": passed,
            "returncode": r["returncode"],
            "missing_markers": missing,
            "stdout": r["stdout"],
            "stderr": r["stderr"],
        })

        if not passed:
            stop_after_failure = True

    git_dirty = bool(git_status_short())

    failed = [r for r in results if not r["passed"]]
    passed_count = sum(1 for r in results if r["passed"])

    if failed:
        stack_status = "STACK_FAIL"
        final_decision = "STOP_AND_REVIEW_FAILED_STACK_STEP"
        allowed_scope = "NONE"
        next_safe_command = "Review failed step output."
    elif git_dirty:
        stack_status = "STACK_PASS_WITH_REPO_ATTENTION"
        final_decision = "COMMIT_OR_REVIEW_REPO_CHANGES_BEFORE_NEXT_STEP"
        allowed_scope = "REPO_ONLY"
        next_safe_command = "git status --short"
    else:
        stack_status = "STACK_PASS"
        final_decision = "DO_NOT_TOUCH_RUNTIME_CONTINUE_REPO_ONLY_OS_INTELLIGENCE"
        allowed_scope = "REPO_ONLY_OS_INTELLIGENCE"
        next_safe_command = r'python -u ".\tools\edge_factory_os_standard_stack_runner_v1.py"'

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),
        "stack_status": stack_status,
        "final_decision": final_decision,
        "allowed_scope": allowed_scope,
        "next_safe_command": next_safe_command,
        "passed_count": passed_count,
        "total_count": len(COMMANDS),
        "failed_count": len(failed),
        "git_dirty": git_dirty,
        "git_status_short": git_status_short(),
        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,
        "results": results,
    }

    state_path = out_dir / "os_standard_stack_runner_v1_state.json"
    latest_path = OUT_ROOT / "os_standard_stack_latest.json"
    report_path = out_dir / "os_standard_stack_runner_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory OS Standard Stack Runner v1")
    md.append("")
    md.append(f"stack_status: `{stack_status}`")
    md.append(f"final_decision: `{final_decision}`")
    md.append(f"allowed_scope: `{allowed_scope}`")
    md.append("")
    md.append("## Steps")
    for r in results:
        icon = "PASS" if r["passed"] else "FAIL"
        md.append(f"- `{icon}` {r['key']}")
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

    print("EDGE FACTORY OS STANDARD STACK RUNNER v1")
    print("=" * 100)
    print(f"stack_status  : {stack_status}")
    print(f"final_decision: {final_decision}")
    print(f"allowed_scope : {allowed_scope}")
    print(f"passed        : {passed_count}/{len(COMMANDS)}")
    print(f"git_dirty     : {git_dirty}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("STEPS")
    print("-" * 100)

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"{status} | {r['key']} | returncode={r['returncode']}")
        if r["missing_markers"]:
            print(f"  missing_markers={r['missing_markers']}")

    print()
    print("DO NOT")
    print("-" * 100)
    print("- Do not restart MASTER.")
    print("- Do not run launchers.")
    print("- Do not patch runtime.")
    print("- Do not start new active paper family.")
    print("- Do not run blocked candidates.")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Report: {report_path}")

    return 0 if stack_status in {"STACK_PASS", "STACK_PASS_WITH_REPO_ATTENTION"} else 1

if __name__ == "__main__":
    raise SystemExit(main())
